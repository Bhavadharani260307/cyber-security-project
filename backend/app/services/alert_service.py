"""
Alert Service for AI-Based NIDS
Automatically converts malicious/suspicious predictions into actionable threat alerts.
"""

from backend.app.database import db
from backend.app.models.prediction import Prediction
from backend.app.models.alert import Alert


class AlertService:

    @staticmethod
    def process_prediction_alert(prediction: Prediction) -> Alert | None:
        """
        Creates an Alert entry if the prediction is determined to be suspicious or malicious.
        """
        if prediction.status in ["SUSPICIOUS", "MALICIOUS"]:
            alert = Alert(
                prediction_id=prediction.id,
                severity=prediction.severity,
                status="NEW",
                description=f"Automated Alert: {prediction.attack_type} detected from {prediction.source_ip} to {prediction.destination_ip}:{prediction.destination_port} (Confidence: {prediction.confidence*100:.1f}%)",
            )
            db.session.add(alert)
            db.session.commit()
            return alert
        return None

    @staticmethod
    def update_alert_status(alert_id: int, new_status: str) -> Alert:
        """
        Updates the investigation status of an alert (NEW -> INVESTIGATING -> RESOLVED).
        """
        alert = db.session.get(Alert, alert_id)
        if not alert:
            raise ValueError(f"Alert with ID {alert_id} not found.")

        if new_status not in ["NEW", "INVESTIGATING", "RESOLVED"]:
            raise ValueError(f"Invalid alert status: {new_status}")

        alert.status = new_status
        db.session.commit()
        return alert
