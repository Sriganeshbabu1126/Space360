from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials, initialize_app
from app.config import settings
import firebase_admin

bearer_scheme = HTTPBearer()

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    initialize_app(cred, {
        "projectId": settings.FIREBASE_PROJECT_ID
    })

def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:
    try:
        decoded = auth.verify_id_token(token.credentials)
        return decoded
    except Exception as e:
        print(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_google_ai_pro(
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Gate AI features to Google AI Pro account holders.
    Checks for a custom claim 'ai_pro': true set on the 
    Firebase user via Google Cloud Identity.
    """
    if not user.get("ai_pro", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a Google AI Pro account"
        )
    return user

def require_admin(
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Gate site creation to admins only.
    """
    if user.get("email") != "wincadsg@gmail.com":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return user
