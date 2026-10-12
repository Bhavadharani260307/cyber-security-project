"""
Dashboard Analytics API Blueprint
"""

from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify
from flask_login import login_required
from sqlalchemy import func
from backend.app.database import db
from backend.app.models.prediction import Prediction
from backend.app.models.alert import Alert

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/statistics", methods=["GET"])
@login_required
def get_dashboard_stats():
    total_traffic = Prediction.query.count()
    normal_traffic = Prediction.query.filter_by(status="NORMAL").count()
    suspicious_traffic = Prediction.query.filter_by(status="SUSPICIOUS").count()
    malicious_traffic = Prediction.query.filter_by(status="MALICIOUS").count()

    attacks_detected = suspicious_traffic + malicious_traffic
    detection_rate = round((attacks_detected / total_traffic * 100), 2) if total_traffic > 0 else 0.0

    # Attack Category Distribution
    attack_counts = (
        db.session.query(Prediction.attack_type, func.count(Prediction.id))
        .group_by(Prediction.attack_type)
        .all()
    )
    attack_distribution = {cat: count for cat, count in attack_counts}

    # Severity breakdown for alerts
    alert_severity_counts = (
        db.session.query(Alert.severity, func.count(Alert.id))
        .group_by(Alert.severity)
        .all()
    )
    severity_distribution = {sev: count for sev, count in alert_severity_counts}

    # Recent Alerts (top 10)
    recent_alerts = Alert.query.order_by(Alert.created_at.desc()).limit(10).all()

    return jsonify(
        {
            "total_traffic": total_traffic,
            "normal_traffic": normal_traffic,
            "suspicious_traffic": suspicious_traffic,
            "malicious_traffic": malicious_traffic,
            "attacks_detected": attacks_detected,
            "detection_rate": detection_rate,
            "attack_distribution": attack_distribution,
            "severity_distribution": severity_distribution,
            "recent_alerts": [a.to_dict() for a in recent_alerts],
        }
    ), 200
