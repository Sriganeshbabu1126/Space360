from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.issue_filter import IssueFilterQuery
from app.services.export_service import generate_csv, generate_excel, generate_pdf
from app.services.gcs_service import upload_private_file
import datetime

@celery_app.task(bind=True)
def generate_large_export_task(self, format: str, is_admin: bool, user_email: str, filters: dict):
    db = SessionLocal()
    try:
        # Reconstruct the query
        filter_query = IssueFilterQuery(
            db_session=db,
            statuses=filters.get("statuses"),
            types=filters.get("types"),
            sites=filters.get("sites"),
            contractors=filters.get("contractors"),
            date_start=filters.get("date_start"),
            date_end=filters.get("date_end"),
            search_text=filters.get("search_text"),
            sort_by=filters.get("sort_by", "created_at"),
            sort_direction=filters.get("sort_dir", "desc"),
            limit=100000, # Large limit for export
            offset=0,
            current_user=user_email
        )
        
        issues, _ = filter_query.execute()
        
        if format == "csv":
            file_bytes = generate_csv(issues, is_admin)
            content_type = "text/csv"
            ext = "csv"
        elif format == "excel":
            file_bytes = generate_excel(issues, is_admin)
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ext = "xlsx"
        elif format == "pdf":
            file_bytes = generate_pdf(issues, is_admin)
            content_type = "application/pdf"
            ext = "pdf"
        else:
            raise ValueError(f"Unsupported format: {format}")
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        job_id = self.request.id
        # The prompt mentioned putting it in exports/{user_id}/{job_id}.{ext}
        # But we only have user_email. Let's use user_email replacing @ and . with _
        safe_email = user_email.replace("@", "_").replace(".", "_")
        filename = f"space360_issues_{timestamp}.{ext}"
        destination_path = f"exports/{safe_email}/{job_id}/{filename}"
        
        upload_private_file(file_bytes, destination_path, content_type)
        
        return {
            "status": "complete",
            "destination_path": destination_path,
            "filename": filename
        }
    except Exception as e:
        print(f"Export task failed: {e}")
        raise e
    finally:
        db.close()
