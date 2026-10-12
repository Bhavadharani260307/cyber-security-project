"""
Prediction APIs Blueprint (Single Packet Form & Batch CSV Upload)
"""

from datetime import datetime, timezone
import json
import pandas as pd
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from backend.app.database import db
from backend.app.models.prediction import Prediction
from backend.app.services.predictor import PredictorService
from backend.app.services.alert_service import AlertService
from backend.app.services.audit_service import AuditService
from backend.app.security.validators import validate_predict_payload, validate_allowed_file

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/api/predict", methods=["POST"])
@login_required
def predict_single_api():
    data = request.get_json() or {}

    is_valid, err_msg = validate_predict_payload(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    # Extract meta IP & protocol info or default
    src_ip = data.get("source_ip", "192.168.1.105")
    dst_ip = data.get("destination_ip", "10.0.0.5")
    protocol = data.get("protocol", "TCP")
    src_port = int(data.get("source_port", 49152))
    dst_port = int(data.get("destination_port", 80))

    # Feature dict matching dataset columns
    feature_dict = {
        "Destination Port": dst_port,
        "Flow Duration": float(data["flow_duration"]),
        "Total Fwd Packets": int(data["total_fwd_packets"]),
        "Total Backward Packets": int(data["total_backward_packets"]),
        "Fwd Packet Length Max": float(data["fwd_packet_length_max"]),
        "Bwd Packet Length Mean": float(data["bwd_packet_length_mean"]),
        "Flow Bytes/s": float(data["flow_bytes_s"]),
        "Flow Packets/s": float(data["flow_packets_s"]),
    }

    try:
        res = PredictorService.predict_single(feature_dict)

        # Persist prediction
        pred_record = Prediction(
            source_ip=src_ip,
            destination_ip=dst_ip,
            protocol=protocol,
            source_port=src_port,
            destination_port=dst_port,
            attack_type=res["attack_type"],
            severity=res["severity"],
            confidence=res["confidence"],
            status=res["status"],
            raw_features=json.dumps(feature_dict),
        )
        db.session.add(pred_record)
        db.session.commit()

        # Trigger automatic threat alert if malicious/suspicious
        alert = AlertService.process_prediction_alert(pred_record)

        AuditService.log_event(
            "SINGLE_PREDICTION_EXECUTED",
            f"Classified {pred_record.attack_type} ({pred_record.severity}) for {src_ip}",
        )

        response_payload = pred_record.to_dict()
        response_payload["description"] = res["description"]
        response_payload["alert_generated"] = bool(alert)

        return jsonify(response_payload), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Prediction pipeline failure: {str(e)}"}), 500


@predict_bp.route("/api/predict/batch", methods=["POST"])
@login_required
def predict_batch_api():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Selected file is empty."}), 400

    if not validate_allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only CSV files are allowed."}), 400

    try:
        df = pd.read_csv(file)
        results = PredictorService.predict_batch(df)

        persisted_records = []
        alert_count = 0

        for r in results:
            pred = Prediction(
                source_ip=r["source_ip"],
                destination_ip=r["destination_ip"],
                protocol=r["protocol"],
                source_port=r["source_port"],
                destination_port=r["destination_port"],
                attack_type=r["attack_type"],
                severity=r["severity"],
                confidence=r["confidence"],
                status=r["status"],
            )
            db.session.add(pred)
            db.session.flush()

            alert = AlertService.process_prediction_alert(pred)
            if alert:
                alert_count += 1

            persisted_records.append(pred.to_dict())

        db.session.commit()

        AuditService.log_event(
            "BATCH_PREDICTION_EXECUTED",
            f"Analyzed {len(results)} network traffic records from CSV. Alerts generated: {alert_count}",
        )

        return jsonify(
            {
                "message": f"Successfully processed {len(results)} records.",
                "total_records": len(results),
                "alerts_generated": alert_count,
                "predictions": persisted_records,
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error parsing CSV dataset: {str(e)}"}), 500


@predict_bp.route("/api/predictions", methods=["GET"])
@login_required
def get_predictions_api():
    limit = request.args.get("limit", 100, type=int)
    attack_filter = request.args.get("attack_type", None)

    query = Prediction.query

    if attack_filter:
        query = query.filter_by(attack_type=attack_filter)

    records = query.order_by(Prediction.timestamp.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in records]), 200
