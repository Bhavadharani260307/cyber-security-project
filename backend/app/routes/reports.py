"""
Reports & Analytics API Blueprint
"""

import csv
import io
from flask import Blueprint, jsonify, Response, request
from flask_login import login_required
from sqlalchemy import func
from backend.app.database import db
from backend.app.models.prediction import Prediction
from backend.app.models.alert import Alert
from backend.app.models.audit_log import AuditLog

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports/summary", methods=["GET"])
@login_required
def get_report_summary():
    total_predictions = Prediction.query.count()
    normal_count = Prediction.query.filter_by(status="NORMAL").count()
    suspicious_count = Prediction.query.filter_by(status="SUSPICIOUS").count()
    malicious_count = Prediction.query.filter_by(status="MALICIOUS").count()

    attack_types = (
        db.session.query(Prediction.attack_type, func.count(Prediction.id))
        .group_by(Prediction.attack_type)
        .all()
    )

    severities = (
        db.session.query(Prediction.severity, func.count(Prediction.id))
        .group_by(Prediction.severity)
        .all()
    )

    alert_statuses = (
        db.session.query(Alert.status, func.count(Alert.id))
        .group_by(Alert.status)
        .all()
    )

    return jsonify(
        {
            "total_predictions": total_predictions,
            "normal_traffic": normal_count,
            "suspicious_traffic": suspicious_count,
            "malicious_traffic": malicious_count,
            "attack_distribution": dict(attack_types),
            "severity_distribution": dict(severities),
            "alert_status_distribution": dict(alert_statuses),
        }
    ), 200


@reports_bp.route("/api/reports/export", methods=["GET"])
@login_required
def export_csv_report():
    record_type = request.args.get("type", "predictions")  # 'predictions' or 'alerts'

    output = io.StringIO()
    writer = csv.writer(output)

    if record_type == "alerts":
        writer.writerow(
            ["Alert ID", "Timestamp", "Source IP", "Destination IP", "Protocol", "Attack Type", "Severity", "Status", "Confidence", "Description"]
        )
        alerts = Alert.query.order_by(Alert.created_at.desc()).all()
        for a in alerts:
            p = a.prediction
            writer.writerow(
                [
                    a.id,
                    a.created_at.isoformat(),
                    p.source_ip if p else "",
                    p.destination_ip if p else "",
                    p.protocol if p else "",
                    p.attack_type if p else "",
                    a.severity,
                    a.status,
                    p.confidence if p else 0.0,
                    a.description,
                ]
            )
        filename = "nids_threat_alerts_report.csv"
    else:
        writer.writerow(
            ["Prediction ID", "Timestamp", "Source IP", "Destination IP", "Protocol", "Source Port", "Destination Port", "Attack Type", "Severity", "Confidence", "Status"]
        )
        preds = Prediction.query.order_by(Prediction.timestamp.desc()).all()
        for p in preds:
            writer.writerow(
                [
                    p.id,
                    p.timestamp.isoformat(),
                    p.source_ip,
                    p.destination_ip,
                    p.protocol,
                    p.source_port,
                    p.destination_port,
                    p.attack_type,
                    p.severity,
                    p.confidence,
                    p.status,
                ]
            )
        filename = "nids_traffic_predictions_report.csv"

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
