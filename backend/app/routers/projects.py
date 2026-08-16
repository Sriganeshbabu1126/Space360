from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models import Site, FloorPlan, LocationPoint, Issue, ContractorSiteAssignment, Contractor
from app.schemas import ProjectResponse, ProjectDetailResponse, ProjectUpdate, ProjectCreate, ProjectStats
from app.auth import get_current_user, require_admin

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email")
    is_admin = user_email == "wincadsg@gmail.com"
    
    if is_admin:
        sites = db.query(Site).order_by(Site.last_activity_at.desc()).all()
    else:
        contractor = db.query(Contractor).filter(Contractor.contact == user_email).first()
        if not contractor:
            return []
        assigned_site_ids = [assign.site_id for assign in contractor.site_assignments]
        sites = db.query(Site).filter(Site.id.in_(assigned_site_ids)).order_by(Site.last_activity_at.desc()).all()
        
    projects = []
    for site in sites:
        # Calculate simple stats
        floor_plans = db.query(FloorPlan).filter(FloorPlan.site_id == site.id).all()
        fp_ids = [fp.id for fp in floor_plans]
        
        issues = []
        if fp_ids:
            loc_ids = [loc.id for loc in db.query(LocationPoint).filter(LocationPoint.floor_plan_id.in_(fp_ids)).all()]
            if loc_ids:
                issues = db.query(Issue).filter(Issue.location_id.in_(loc_ids)).all()
                
        contractor_count = db.query(ContractorSiteAssignment).filter(ContractorSiteAssignment.site_id == site.id).count()
        
        stats = ProjectStats(
            total_issues=len(issues),
            open_issues=sum(1 for i in issues if i.status == 'open'),
            critical_issues=sum(1 for i in issues if i.status == 'critical'),
            closed_issues=sum(1 for i in issues if i.status == 'closed'),
            total_floor_plans=len(fp_ids),
            total_captures=0,
            assigned_contractors=contractor_count
        )
        
        projects.append(ProjectResponse(
            id=site.id,
            name=site.name,
            location=site.address,
            status=site.status,
            description=site.description,
            stats=stats,
            last_activity_at=site.last_activity_at,
            created_at=site.created_at
        ))
        
    return projects

@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email")
    is_admin = user_email == "wincadsg@gmail.com"
    
    site = db.query(Site).filter(Site.id == project_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if not is_admin:
        contractor = db.query(Contractor).filter(Contractor.contact == user_email).first()
        if not contractor or project_id not in [assign.site_id for assign in contractor.site_assignments]:
            raise HTTPException(status_code=403, detail="Not authorized to access this project")

    # Simple eager load for details
    floor_plans = db.query(FloorPlan).filter(FloorPlan.site_id == site.id).all()
    fp_ids = [fp.id for fp in floor_plans]
    
    issues = []
    if fp_ids:
        loc_ids = [loc.id for loc in db.query(LocationPoint).filter(LocationPoint.floor_plan_id.in_(fp_ids)).all()]
        if loc_ids:
            issues = db.query(Issue).filter(Issue.location_id.in_(loc_ids)).order_by(Issue.created_at.desc()).all()
            
    # Contractors assigned
    assignments = db.query(ContractorSiteAssignment).filter(ContractorSiteAssignment.site_id == site.id).all()
    contractor_ids = [a.contractor_id for a in assignments]
    contractors = db.query(Contractor).filter(Contractor.id.in_(contractor_ids)).all() if contractor_ids else []

    stats = ProjectStats(
        total_issues=len(issues),
        open_issues=sum(1 for i in issues if i.status == 'open'),
        critical_issues=sum(1 for i in issues if i.status == 'critical'),
        closed_issues=sum(1 for i in issues if i.status == 'closed'),
        total_floor_plans=len(fp_ids),
        total_captures=0,
        assigned_contractors=len(contractors)
    )

    return ProjectDetailResponse(
        id=site.id,
        name=site.name,
        location=site.address,
        status=site.status,
        description=site.description,
        stats=stats,
        last_activity_at=site.last_activity_at,
        created_at=site.created_at,
        floor_plans=floor_plans,
        recent_issues=issues[:5],
        contractors=contractors
    )

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    site = db.query(Site).filter(Site.id == project_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if payload.name is not None:
        site.name = payload.name
    if payload.location is not None:
        site.address = payload.location
    if payload.description is not None:
        site.description = payload.description
    if payload.status is not None:
        site.status = payload.status
        
    db.commit()
    db.refresh(site)
    
    return ProjectResponse(
        id=site.id,
        name=site.name,
        location=site.address,
        status=site.status,
        description=site.description,
        last_activity_at=site.last_activity_at,
        created_at=site.created_at
    )
