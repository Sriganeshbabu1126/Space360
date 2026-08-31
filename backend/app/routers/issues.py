from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, SessionLocal
from sqlalchemy.orm import joinedload
from app.models import Issue, IssueAssignment, Contractor, AccessLevelEnum, IssueComment, IssueStatusEnum, LocationPoint, IssueNotification, FloorPlan
from app.schemas import IssueCreate, IssueUpdate, IssueResponse, IssueAssignmentResponse, IssueCommentCreate, IssueCommentResponse, IssuePhotoResponse, IssueNotificationResponse
from app.auth import get_current_user
from pydantic import BaseModel
import uuid
import datetime
from fastapi import UploadFile, File
from app.models import IssuePhoto
from app.services.gcs_service import upload_private_file, get_signed_url
from app.utils.email import send_issue_notification
import time
from app.services.issue_filter import IssueFilterQuery
from fastapi.responses import StreamingResponse
from app.services.export_service import generate_csv, generate_excel, generate_pdf
from app.celery_app import celery_app
from celery.result import AsyncResult
from app.worker import generate_large_export_task
import io

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
        frame_a_id=payload.frame_a_id,
        frame_b_id=payload.frame_b_id,
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
    site_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Issue).options(
        joinedload(Issue.location).joinedload(LocationPoint.floor_plan)
    )
    
    user_email = current_user.get("email")
    is_admin = user_email == "wincadsg@gmail.com"
    
    if not is_admin:
        from sqlalchemy import func
        contractor = db.query(Contractor).filter(func.lower(Contractor.contact) == func.lower(user_email)).first()
        if contractor:
            assigned_site_ids = [assign.site_id for assign in contractor.site_assignments]
            query = query.join(LocationPoint, Issue.location_id == LocationPoint.id) \
                         .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id) \
                         .filter(FloorPlan.site_id.in_(assigned_site_ids))
        else:
            return []
            
    if site_id and is_admin:
        # If admin and specific site selected
        query = query.join(LocationPoint, Issue.location_id == LocationPoint.id) \
                     .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id) \
                     .filter(FloorPlan.site_id == site_id)
    elif site_id and not is_admin:
        # User already joined FloorPlan above
        query = query.filter(FloorPlan.site_id == site_id)
            
    if status:
        query = query.filter(Issue.status == status)
    if location_id:
        query = query.filter(Issue.location_id == location_id)
        
    return query.order_by(Issue.created_at.desc()).all()


@router.get("/search")
async def search_issues(
    statuses: Optional[str] = Query(None),
    types: Optional[str] = Query(None),
    sites: Optional[str] = Query(None),
    contractors: Optional[str] = Query(None),
    date_start: Optional[datetime.datetime] = None,
    date_end: Optional[datetime.datetime] = None,
    search_text: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Parse comma separated strings to lists
    status_list = statuses.split(",") if statuses else None
    type_list = types.split(",") if types else None
    site_list = sites.split(",") if sites else None
    contractor_list = contractors.split(",") if contractors else None

    filter_query = IssueFilterQuery(
        db_session=db,
        statuses=status_list,
        types=type_list,
        sites=site_list,
        contractors=contractor_list,
        date_start=date_start,
        date_end=date_end,
        search_text=search_text,
        sort_by=sort_by,
        sort_direction=sort_dir,
        limit=limit,
        offset=offset,
        current_user=current_user.get("email")
    )

    start_time = time.time()
    results, total = filter_query.execute()
    query_time = (time.time() - start_time) * 1000

    return {
        "total": total,
        "results": [IssueResponse.from_orm(r) for r in results],
        "query_time_ms": int(query_time)
    }


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

async def send_and_log_notification(c_email, c_name, i_id, i_title, i_desc, i_type, i_status, loc_name, rep_email, c_at):
    success = await send_issue_notification(
        contractor_email=c_email,
        contractor_name=c_name,
        issue_id=i_id,
        issue_title=i_title,
        issue_description=i_desc,
        issue_type=i_type,
        issue_status=i_status,
        location_name=loc_name,
        reporter_email=rep_email,
        created_at=c_at
    )
    db_bg = SessionLocal()
    try:
        notif = IssueNotification(
            id=generate_uuid(),
            issue_id=i_id,
            sent_to=c_email,
            status="success" if success else "failed"
        )
        db_bg.add(notif)
        db_bg.commit()
    except Exception as e:
        print(f"Error logging notification: {e}")
    finally:
        db_bg.close()

@router.post("/{id}/send-notification", status_code=status.HTTP_202_ACCEPTED)
async def trigger_issue_notification(
    id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    issue = db.query(Issue).options(
        joinedload(Issue.location).joinedload(LocationPoint.floor_plan),
        joinedload(Issue.assignments).joinedload(IssueAssignment.contractor)
    ).filter(Issue.id == id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
        
    if not issue.assignments:
        return {"message": "No contractors assigned to this issue."}
        
    queued_count = 0
    for assignment in issue.assignments:
        contractor = assignment.contractor
        if not contractor.contact or "@" not in contractor.contact:
            continue
            
        background_tasks.add_task(
            send_and_log_notification,
            contractor.contact,
            contractor.name,
            issue.id,
            issue.title,
            issue.description or "",
            issue.issue_type.value if hasattr(issue.issue_type, 'value') else str(issue.issue_type),
            issue.status.value if hasattr(issue.status, 'value') else str(issue.status),
            issue.location_name,
            issue.created_by,
            issue.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        queued_count += 1

    return {"message": f"Notifications queued for {queued_count} contractors."}
class ExportRequest(BaseModel):
    format: str
    filters: dict = {}

@router.post("/export")
def export_issues(
    payload: ExportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    format_type = payload.format.lower()
    if format_type not in ["csv", "excel", "pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported format")
        
    filters = payload.filters
    # Extract filter logic, similar to /search
    status_list = filters.get("statuses").split(",") if filters.get("statuses") else None
    type_list = filters.get("types").split(",") if filters.get("types") else None
    site_list = filters.get("sites").split(",") if filters.get("sites") else None
    contractor_list = filters.get("contractors").split(",") if filters.get("contractors") else None
    
    # We need to construct filter query to know the count
    user_email = current_user.get("email")
    is_admin = user_email == "wincadsg@gmail.com"
    
    filter_query = IssueFilterQuery(
        db_session=db,
        statuses=status_list,
        types=type_list,
        sites=site_list,
        contractors=contractor_list,
        search_text=filters.get("search_text"),
        current_user=user_email,
        limit=100000,
        offset=0
    )
    
    query = filter_query.build_query()
    total = query.count()
    
    if total > 500:
        # Kick off background job
        safe_filters = {
            "statuses": status_list,
            "types": type_list,
            "sites": site_list,
            "contractors": contractor_list,
            "search_text": filters.get("search_text")
        }
        task = generate_large_export_task.delay(format_type, is_admin, user_email, safe_filters)
        return {"job_id": task.id, "status": "processing"}
    else:
        # Return directly
        issues = query.all()
        if format_type == "csv":
            file_bytes = generate_csv(issues, is_admin)
            media_type = "text/csv"
            filename = f"space360_issues_{datetime.datetime.now().strftime('%Y-%m-%d')}.csv"
        elif format_type == "excel":
            file_bytes = generate_excel(issues, is_admin)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"space360_issues_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        else: # pdf
            file_bytes = generate_pdf(issues, is_admin)
            media_type = "application/pdf"
            filename = f"space360_issues_{datetime.datetime.now().strftime('%Y-%m-%d')}.pdf"
            
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )

@router.get("/export/{job_id}")
def get_export_status(job_id: str):
    res = AsyncResult(job_id, app=celery_app)
    if res.state == 'PENDING' or res.state == 'STARTED':
        return {"status": "processing"}
    elif res.state == 'SUCCESS':
        result_data = res.result
        # Generate a signed URL for the destination path
        signed_url = get_signed_url(result_data["destination_path"], expiration_hours=1)
        return {
            "status": "complete",
            "download_url": signed_url
        }
    else:
        return {"status": "failed", "error": str(res.result)}
