"""
Audit Service for recording security events and administrative actions
"""

from flask import request
from flask_login import current_user
from backend.app.database import db
from backend.app.models.audit_log import AuditLog


class AuditService:

    @staticmethod
    def log_event(action: str, details: str = None, user_id: int = None, ip_address: str = None):
        """Logs a security audit event into database"""
        try:
            resolved_user_id = user_id
            if resolved_user_id is None and current_user and current_user.is_authenticated:
                resolved_user_id = current_user.id

            resolved_ip = ip_address
            if resolved_ip is None and request:
                resolved_ip = request.remote_addr

            log_entry = AuditLog(
                user_id=resolved_user_id,
                action=action,
                ip_address=resolved_ip,
                details=details,
            )
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            print(f"[!] Audit logging error: {e}")
            return None
