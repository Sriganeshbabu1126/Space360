from sqlalchemy.orm import joinedload, Query
from sqlalchemy import desc, asc, func
from typing import List, Optional, Tuple
from app.models import Issue, IssueAssignment, Contractor, IssueComment, LocationPoint, FloorPlan, Site
import datetime

class IssueFilterQuery:
    def __init__(
        self,
        db_session,
        statuses: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        sites: Optional[List[str]] = None,
        contractors: Optional[List[str]] = None,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
        search_text: Optional[str] = None,
        sort_by: str = "created_at",
        sort_direction: str = "desc",
        limit: int = 20,
        offset: int = 0,
        current_user: str = "system"
    ):
        self.db = db_session
        self.statuses = statuses
        self.types = types
        self.sites = sites
        self.contractors = contractors
        self.date_start = date_start
        self.date_end = date_end
        self.search_text = search_text
        self.sort_by = sort_by
        self.sort_direction = sort_direction
        self.limit = limit
        self.offset = offset
        self.current_user = current_user

    def build_query(self) -> Query:
        query = self.db.query(Issue).options(
            joinedload(Issue.assignments).joinedload(IssueAssignment.contractor),
            joinedload(Issue.comments),
            joinedload(Issue.location).joinedload(LocationPoint.floor_plan)
        )
        
        # User Access Control
        if self.current_user != "wincadsg@gmail.com":  # Not admin
            contractor = self.db.query(Contractor).filter(Contractor.contact == self.current_user).first()
            if contractor:
                assigned_site_ids = [assign.site_id for assign in contractor.site_assignments]
                
                query = query.join(LocationPoint, Issue.location_id == LocationPoint.id) \
                             .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id) \
                             .filter(FloorPlan.site_id.in_(assigned_site_ids))
            else:
                return query.filter(Issue.id == 'none') # Return nothing

        if self.statuses:
            query = query.filter(Issue.status.in_(self.statuses))
            
        if self.types:
            query = query.filter(Issue.issue_type.in_(self.types))
            
        if self.sites:
            # If not already joined LocationPoint and FloorPlan above
            if self.current_user == "wincadsg@gmail.com":
                query = query.join(LocationPoint, Issue.location_id == LocationPoint.id) \
                             .join(FloorPlan, LocationPoint.floor_plan_id == FloorPlan.id)
            query = query.filter(FloorPlan.site_id.in_(self.sites))
            
        if self.contractors:
            query = query.join(IssueAssignment, Issue.id == IssueAssignment.issue_id).filter(
                IssueAssignment.contractor_id.in_(self.contractors)
            )
            
        if self.date_start:
            query = query.filter(Issue.created_at >= self.date_start)
            
        if self.date_end:
            query = query.filter(Issue.created_at <= self.date_end)
            
        if self.search_text:
            search_query = func.plainto_tsquery('english', self.search_text)
            
            # Combine title and description for TS Vector
            issue_vector = func.to_tsvector('english', func.coalesce(Issue.title, '') + ' ' + func.coalesce(Issue.description, ''))
            
            # We also want to search comments
            # To do this correctly in SQL without messing up the main query rows, an EXISTS subquery is often better.
            comment_vector = func.to_tsvector('english', func.coalesce(IssueComment.comment_text, ''))
            
            has_comment_match = self.db.query(IssueComment).filter(
                IssueComment.issue_id == Issue.id,
                comment_vector.op('@@')(search_query)
            ).exists()
            
            query = query.filter(
                issue_vector.op('@@')(search_query) | has_comment_match
            )

        direction = desc if self.sort_direction.lower() == 'desc' else asc

        if self.sort_by == 'title':
            query = query.order_by(direction(Issue.title))
        elif self.sort_by == 'status':
            query = query.order_by(direction(Issue.status))
        elif self.sort_by in ('priority', 'issue_type', 'type'):
            query = query.order_by(direction(Issue.issue_type))
        elif self.sort_by == 'updated_at':
            query = query.order_by(direction(Issue.updated_at))
        elif self.sort_by == 'assignee':
            first_assignee = self.db.query(func.min(Contractor.name)) \
                .join(IssueAssignment, Contractor.id == IssueAssignment.contractor_id) \
                .filter(IssueAssignment.issue_id == Issue.id) \
                .correlate(Issue) \
                .scalar_subquery()
            query = query.order_by(direction(first_assignee))
        else:
            query = query.order_by(direction(Issue.created_at))

        return query

    def execute(self) -> Tuple[List[Issue], int]:
        query = self.build_query()
        total = query.count()
        results = query.limit(self.limit).offset(self.offset).all()
        return results, total
