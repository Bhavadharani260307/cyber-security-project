"""
Security Decorators for RBAC (Role-Based Access Control)
"""

from functools import wraps
from flask import jsonify, redirect, url_for, flash, request
from flask_login import current_user


def role_required(*roles):
    """Decorator to enforce specific user roles (e.g. Admin, Analyst)"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"error": "Unauthorized access. Authentication required."}), 401
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))

            is_api = request.is_json or request.path.startswith("/api/") or request.headers.get("Accept") == "application/json"
            if current_user.role not in roles:
                if is_api:
                    return jsonify({"error": "Forbidden. Insufficient permissions."}), 403
                flash("You do not have permission to access this resource.", "danger")
                return redirect(url_for("views.dashboard_view"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    """Shortcut decorator for Admin-only routes"""
    return role_required("Admin")(f)
