from datetime import datetime, timezone
from backend.app.database import db


class Alert(db.Model):
    """Alert model for managing detected threat incidents"""

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(
        db.Integer, db.ForeignKey("predictions.id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    severity = db.Column(db.String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = db.Column(db.String(20), nullable=False, default="NEW")  # NEW, INVESTIGATING, RESOLVED
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        pred = self.prediction
        return {
            "id": self.id,
            "prediction_id": self.prediction_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "severity": self.severity,
            "status": self.status,
            "description": self.description,
            "source_ip": pred.source_ip if pred else "N/A",
            "destination_ip": pred.destination_ip if pred else "N/A",
            "protocol": pred.protocol if pred else "N/A",
            "source_port": pred.source_port if pred else 0,
            "destination_port": pred.destination_port if pred else 0,
            "attack_type": pred.attack_type if pred else "N/A",
            "confidence": round(pred.confidence, 4) if pred else 0.0,
        }

    def __repr__(self):
        return f"<Alert #{self.id} Status:{self.status} Severity:{self.severity}>"
