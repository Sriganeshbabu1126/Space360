from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from sqlalchemy.orm import joinedload
from app.models import Issue, IssueAssignment, Contractor, AccessLevelEnum, IssueComment, IssueStatusEnum, LocationPoint
from app.schemas import IssueCreate, IssueUpdate, IssueResponse, IssueAssignmentResponse, IssueCommentCreate, IssueCommentResponse, IssuePhotoResponse
from app.auth import get_current_user
from pydantic import BaseModel
import uuid
import datetime
from fastapi import UploadFile, File
from app.models import IssuePhoto
from app.services.gcs_service import upload_private_file, get_signed_url

router = APIRouter()

def generate_uuid():
    return str(uuid.uuid4())

class AssignContractorRequest(BaseModel):
    contractor_id: str

@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    payload: IssueCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = Issue(
        id=generate_uuid(),
        title=payload.title,
        description=payload.description,
        issue_type=payload.issue_type,
        location_id=payload.location_id,
        session_a_id=payload.session_a_id,
        session_b_id=payload.session_b_id,
        created_by=current_user.get("email", "system")
    )
    db.add(issue)
    
    # Assign contractors if provided
    if payload.contractor_ids:
        for cid in payload.contractor_ids:
            contractor = db.query(Contractor).filter(Contractor.id == cid).first()
            if contractor:
                assignment = IssueAssignment(
                    id=generate_uuid(),
                    issue_id=issue.id,
                    contractor_id=contractor.id,
                    assigned_by=current_user.get("email", "system")
                )
                db.add(assignment)
                
    db.commit()
    db.refresh(issue)
    return issue

@router.get("/", response_model=List[IssueResponse])
def list_issues(
    status: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Issue).options(
        joinedload(Issue.location).joinedload(LocationPoint.floor_plan)
    )
    if status:
        query = query.filter(Issue.status == status)
    if location_id:
        query = query.filter(Issue.location_id == location_id)
        
    return query.order_by(Issue.created_at.desc()).all()

@router.get("/{id}", response_model=IssueResponse)
def get_issue(id: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).options(
        joinedload(Issue.location).joinedload(LocationPoint.floor_plan)
    ).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Generate signed URLs for photos
    for photo in issue.photos:
        try:
            # Assuming photo_url stores the GCS path directly, e.g., "issues/{id}/{filename}"
            # If it's a full URL we need to parse it, but we'll store just the path
            photo.photo_url = get_signed_url(photo.photo_url, expiration_hours=1)
        except Exception as e:
            print(f"Error generating signed URL for photo {photo.id}: {e}")
            
    return issue

@router.post("/{id}/photos", response_model=IssuePhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_issue_photo(
    id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG and PNG files are allowed")

    # Validate file size (max 5MB)
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit")

    # Upload to GCS
    try:
        timestamp = int(datetime.datetime.now().timestamp())
        filename = f"{timestamp}_{file.filename}"
        destination_path = f"issues/{id}/{filename}"
        
        upload_private_file(file_bytes, destination_path, file.content_type)
        
        photo = IssuePhoto(
            id=generate_uuid(),
            issue_id=id,
            photo_url=destination_path,
            uploaded_by=current_user.get("email", "system")
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        
        # Return with signed URL
        photo_copy = IssuePhotoResponse(
            id=photo.id,
            issue_id=photo.issue_id,
            photo_url=get_signed_url(destination_path, expiration_hours=1),
            uploaded_by=photo.uploaded_by,
            created_at=photo.created_at
        )
        return photo_copy
    except Exception as e:
        print(f"Failed to upload photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload photo to storage")


@router.put("/{id}", response_model=IssueResponse)
def update_issue(
    id: str,
    payload: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    user_email = current_user.get("email", "")
    
    # Check authorization for status change
    if payload.status and payload.status != issue.status:
        is_admin = user_email == "wincadsg@gmail.com"
        
        # Only admins can set pending, closed, or critical
        admin_only_statuses = [IssueStatusEnum.pending, IssueStatusEnum.closed, IssueStatusEnum.critical]
        if payload.status in admin_only_statuses and not is_admin:
            raise HTTPException(status_code=403, detail="Only admins can set status to pending/closed/critical")
            
        # Check if user is an assigned contractor with sufficient privileges
        has_access = False
        if not is_admin:
            for assignment in issue.assignments:
                if assignment.contractor.contact == user_email:
                    if assignment.contractor.access_level in [
                        AccessLevelEnum.close_and_review, 
                        AccessLevelEnum.comment_and_change_status
                    ]:
                        has_access = True
                        break
                        
        if not is_admin and not has_access:
            raise HTTPException(
                status_code=403, 
                detail="You do not have permission to change the status of this issue."
            )
            
    # Check authorization for issue_type change
    if payload.issue_type and payload.issue_type != issue.issue_type:
        is_admin = user_email == "wincadsg@gmail.com"
        if not is_admin:
            raise HTTPException(
                status_code=403, 
                detail="Only admins can change the issue type"
            )
            
    # Update fields
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(issue, key, value)
        
    db.commit()
    db.refresh(issue)
    return issue

@router.post("/{id}/assign", response_model=IssueAssignmentResponse)
def assign_contractor(
    id: str,
    payload: AssignContractorRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    contractor = db.query(Contractor).filter(Contractor.id == payload.contractor_id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
        
    # Check if already assigned
    existing = db.query(IssueAssignment).filter(
        IssueAssignment.issue_id == id,
        IssueAssignment.contractor_id == contractor.id
    ).first()
    if existing:
        return existing
        
    assignment = IssueAssignment(
        id=generate_uuid(),
        issue_id=id,
        contractor_id=contractor.id,
        assigned_by=current_user.get("email", "system")
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/{id}/assignments/{contractor_id}", status_code=status.HTTP_204_NO_CONTENT)
def unassign_contractor(
    id: str,
    contractor_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    assignment = db.query(IssueAssignment).filter(
        IssueAssignment.issue_id == id,
        IssueAssignment.contractor_id == contractor_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
        
    db.delete(assignment)
    db.commit()
    return

@router.get("/{id}/comments", response_model=List[IssueCommentResponse])
def get_issue_comments(id: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue.comments

@router.post("/{id}/comments", response_model=IssueCommentResponse, status_code=status.HTTP_201_CREATED)
def add_issue_comment(
    id: str,
    payload: IssueCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = db.query(Issue).filter(Issue.id == id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    comment = IssueComment(
        id=generate_uuid(),
        issue_id=id,
        author=current_user.get("email", "system"),
        comment_text=payload.comment_text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
