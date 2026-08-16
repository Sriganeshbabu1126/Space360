import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

async def send_issue_notification(
    contractor_email: str,
    contractor_name: str,
    issue_id: str,
    issue_title: str,
    issue_description: str,
    issue_type: str,
    issue_status: str,
    location_name: str,
    reporter_email: str,
    created_at: str
) -> bool:
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"Skipping email to {contractor_email} because SMTP credentials are not configured.")
        return False

    subject = f"New Issue Assigned: {issue_title}"
    
    issue_link = f"{FRONTEND_URL}/issues?id={issue_id}"
    
    body = f"""Hi {contractor_name},

You have been assigned to a new issue:

**Issue:** {issue_title}
**Description:** {issue_description or 'No description provided.'}
**Type:** {issue_type}
**Status:** {issue_status}
**Location:** {location_name or 'No location'}
**Created by:** {reporter_email}
**Created at:** {created_at}

View Issue: {issue_link}

---
Comments & Activity, Evidence Photos, Markup, and more details available in the app.

Regards,
Space360 Team
"""

    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = contractor_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
        print(f"Successfully sent email to {contractor_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {contractor_email}: {e}")
        return False
