from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Issue, IssueAssignment, Contractor, IssueStatusEnum

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # 1. Total Issues
    total_issues = db.query(Issue).count()
    
    # 2. Status Breakdown
    status_counts = {
        "open": 0, "in_review": 0, "pending": 0, "closed": 0, "critical": 0
    }
    status_query = db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
    for status, count in status_query:
        if hasattr(status, 'value'):
            status_val = status.value
        else:
            status_val = str(status)
        if status_val in status_counts:
            status_counts[status_val] = count
            
    # 3. Type Breakdown
    type_counts = {}
    type_query = db.query(Issue.issue_type, func.count(Issue.id)).group_by(Issue.issue_type).all()
    for itype, count in type_query:
        if hasattr(itype, 'value'):
            type_val = itype.value
        else:
            type_val = str(itype)
        type_counts[type_val] = count
        
    # 4. Contractor Workload
    contractor_workload = {}
    workload_query = db.query(
        Contractor.name, Contractor.contact, func.count(IssueAssignment.id)
    ).join(
        IssueAssignment, IssueAssignment.contractor_id == Contractor.id
    ).group_by(Contractor.id).all()
    
    for name, email, count in workload_query:
        # User might have asked for email, if no email use name
        key = email if email else name
        contractor_workload[key] = count
        
    # 5. Last 7 Days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    created_last_7 = db.query(Issue).filter(Issue.created_at >= seven_days_ago).count()
    closed_last_7 = db.query(Issue).filter(
        Issue.status == IssueStatusEnum.closed,
        Issue.updated_at >= seven_days_ago
    ).count()
    
    # 6. Avg Resolution Time
    closed_issues = db.query(Issue).filter(Issue.status == IssueStatusEnum.closed).all()
    avg_resolution_hours = 0
    if closed_issues:
        total_hours = sum(
            ((i.updated_at or i.created_at) - i.created_at).total_seconds() / 3600
            for i in closed_issues
        )
        avg_resolution_hours = round(total_hours / len(closed_issues), 1)

    return {
        "total_issues": total_issues,
        "open_issues": status_counts.get("open", 0),
        "in_review": status_counts.get("in_review", 0),
        "pending": status_counts.get("pending", 0),
        "closed": status_counts.get("closed", 0),
        "critical": status_counts.get("critical", 0),
        "by_type": type_counts,
        "by_contractor": contractor_workload,
        "created_last_7_days": created_last_7,
        "closed_last_7_days": closed_last_7,
        "avg_resolution_time_hours": avg_resolution_hours
    }

@router.get("/timeline")
def get_dashboard_timeline(db: Session = Depends(get_db)):
    issues = db.query(Issue).order_by(Issue.created_at.desc()).limit(10).all()
    return [
        {
            "id": i.id,
            "title": i.title,
            "status": i.status.value if hasattr(i.status, 'value') else str(i.status),
            "issue_type": i.issue_type.value if hasattr(i.issue_type, 'value') else str(i.issue_type),
            "created_at": i.created_at,
            "created_by": i.created_by
        }
        for i in issues
    ]
