from firebase_admin import firestore
from datetime import datetime
from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials
import os

# Initialize Firebase if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {'projectId': 'space360-114433'})
    except Exception as e:
        print("AuditLogger Firebase init error:", e)

class AuditLogger:
    def __init__(self):
        try:
            self.db = firestore.client()
        except Exception as e:
            self.db = None
            print(f"Failed to initialize firestore client: {e}")
    
    def log_action(
        self,
        user_id: str,
        user_name: str,
        action: str,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        project_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None
    ):
        """Log an action to Firestore audit_logs collection"""
        if not self.db:
            print("Firestore client not available, skipping audit log")
            return
            
        log_entry = {
            'timestamp': datetime.utcnow(),
            'user_id': user_id,
            'user_name': user_name,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'resource_name': resource_name,
            'project_id': project_id,
            'details': details or {},
            'ip_address': ip_address,
            'status': status,
            'error_message': error_message,
        }
        
        try:
            self.db.collection('audit_logs').add(log_entry)
        except Exception as e:
            print(f"Failed to write audit log: {e}")

audit_logger = AuditLogger()
