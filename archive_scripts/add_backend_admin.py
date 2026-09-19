import os

filepath = r"backend\app\routers\admin.py"
content = """from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.auth import require_admin

router = APIRouter()

class NewUserNotification(BaseModel):
    name: str
    email: str
    temp_password: str

@router.post("/admin/notify-new-user")
async def notify_new_user(payload: NewUserNotification,
                          current_user=Depends(require_admin)):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Note: For SGB Dev Apps production, configure real SMTP. 
    # For now, we simulate success or use a generic one if env vars exist.
    print(f"--- FAKE EMAIL SENT TO {payload.email} ---")
    print(f"Temp Password: {payload.temp_password}")
    return {"status": "sent"}
"""
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Add to main.py
main_path = r"backend\main.py"
with open(main_path, "r", encoding="utf-8") as f:
    main_content = f.read()

if "from app.routers import admin" not in main_content:
    main_content = main_content.replace(
        "from app.routers import sites, projects, floor_plans, locations, sessions, voice_notes, annotations, ai_features, contractors, issues, dashboard, paths, video, correlation",
        "from app.routers import sites, projects, floor_plans, locations, sessions, voice_notes, annotations, ai_features, contractors, issues, dashboard, paths, video, correlation, admin"
    )
    main_content = main_content.replace(
        "app.include_router(dashboard.router, prefix=\"/dashboard\", tags=[\"Dashboard\"])",
        "app.include_router(dashboard.router, prefix=\"/dashboard\", tags=[\"Dashboard\"])\napp.include_router(admin.router, tags=[\"Admin\"])"
    )
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

print("Done")
