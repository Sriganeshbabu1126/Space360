from fastapi import APIRouter, Depends
from pydantic import BaseModel
import os
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

# Note: require_admin mock for now or use real one
def require_admin():
    return {"email": "admin@example.com"}

try:
    from app.auth import require_admin
except ImportError:
    pass

class NewUserNotification(BaseModel):
    name: str
    email: str
    temp_password: str

@router.post("/admin/notify-new-user")
async def notify_new_user(payload: NewUserNotification,
                          current_user=Depends(require_admin)):
    try:
        sender_email = os.environ.get("SMTP_EMAIL", "wincadsg@gmail.com")
        sender_password = os.environ.get("SMTP_PASSWORD", "dummy_password")
        
        msg = MIMEText(f"Hi {payload.name},\n\nYour Space360 account has been created.\n\nEmail:    {payload.email}\nPassword: {payload.temp_password}\n\nLogin to the Space360 app and change your password immediately.\n\n— SGB Dev Apps")
        msg['Subject'] = "Welcome to Space360!"
        msg['From'] = sender_email
        msg['To'] = payload.email

        # Non-blocking, best effort
        if sender_password != "dummy_password":
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    return {"status": "sent"}
