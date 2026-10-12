"""
Automated Pytest Suite for Alert Management System
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User
from backend.app.models.prediction import Prediction
from backend.app.models.alert import Alert


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            user = User(username="analyst_alerts", email="alert@test.com", role="Analyst")
            user.set_password("Pass123")
            db.session.add(user)
            db.session.commit()

            client.post("/auth/login", json={"username": "analyst_alerts", "password": "Pass123"})
            yield client
            db.session.remove()
            db.drop_all()


def test_alert_creation_and_status_update(client):
    with client.application.app_context():
        pred = Prediction(
            source_ip="192.168.1.99",
            destination_ip="10.0.0.5",
            attack_type="DDoS",
            severity="CRITICAL",
            confidence=0.99,
            status="MALICIOUS",
        )
        db.session.add(pred)
        db.session.commit()

        alert = Alert(prediction_id=pred.id, severity="CRITICAL", status="NEW")
        db.session.add(alert)
        db.session.commit()
        alert_id = alert.id

    # Fetch alert list via API
    res_list = client.get("/api/alerts")
    assert res_list.status_code == 200
    assert len(res_list.get_json()) == 1

    # Update status to RESOLVED
    res_update = client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "RESOLVED"},
    )
    assert res_update.status_code == 200
    assert res_update.get_json()["status"] == "RESOLVED"
