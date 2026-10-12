from datetime import datetime, timezone
from backend.app.database import db


class Prediction(db.Model):
    """Prediction model for storing network traffic classification results"""

    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    source_ip = db.Column(db.String(45), nullable=False)
    destination_ip = db.Column(db.String(45), nullable=False)
    protocol = db.Column(db.String(10), nullable=False, default="TCP")
    source_port = db.Column(db.Integer, nullable=False, default=0)
    destination_port = db.Column(db.Integer, nullable=False, default=80)

    attack_type = db.Column(db.String(50), nullable=False, default="BENIGN")
    severity = db.Column(db.String(20), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = db.Column(db.Float, nullable=False, default=1.0)
    status = db.Column(db.String(20), nullable=False, default="NORMAL")  # NORMAL, SUSPICIOUS, MALICIOUS
    raw_features = db.Column(db.Text, nullable=True)  # JSON string of raw flow metrics

    # Relationship to alerts
    alerts = db.relationship("Alert", backref="prediction", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "protocol": self.protocol,
            "source_port": self.source_port,
            "destination_port": self.destination_port,
            "attack_type": self.attack_type,
            "severity": self.severity,
            "confidence": round(self.confidence, 4),
            "status": self.status,
        }

    def __repr__(self):
        return f"<Prediction #{self.id} {self.attack_type} ({self.severity})>"
