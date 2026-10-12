"""
Alert Management API Blueprint
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from backend.app.database import db
from backend.app.models.alert import Alert
from backend.app.services.alert_service import AlertService
from backend.app.services.audit_service import AuditService

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/api/alerts", methods=["GET"])
@login_required
def get_alerts_api():
    status_filter = request.args.get("status", None)
    severity_filter = request.args.get("severity", None)
    limit = request.args.get("limit", 100, type=int)

    query = Alert.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if severity_filter:
        query = query.filter_by(severity=severity_filter)

    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("/api/alerts/<int:alert_id>", methods=["GET"])
@login_required
def get_alert_detail_api(alert_id):
    alert = db.session.get(Alert, alert_id)
    if not alert:
        return jsonify({"error": f"Alert #{alert_id} not found"}), 404
    return jsonify(alert.to_dict()), 200


@alerts_bp.route("/api/alerts/<int:alert_id>", methods=["PATCH", "PUT"])
@login_required
def update_alert_status_api(alert_id):
    data = request.get_json() or {}
    new_status = data.get("status", "").upper()

    if not new_status or new_status not in ["NEW", "INVESTIGATING", "RESOLVED"]:
        return jsonify({"error": "Invalid status. Must be 'NEW', 'INVESTIGATING', or 'RESOLVED'."}), 400

    try:
        updated_alert = AlertService.update_alert_status(alert_id, new_status)
        AuditService.log_event(
            "ALERT_STATUS_UPDATED",
            f"Alert #{alert_id} status updated to '{new_status}'",
        )
        return jsonify(updated_alert.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update alert: {str(e)}"}), 500
