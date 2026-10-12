"""
Automated Pytest Suite for Prediction APIs and Alert Generation
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.app.database import db
from backend.app.models.user import User


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            # Seed user and log in
            user = User(username="analyst_test", email="a@test.com", role="Analyst")
            user.set_password("Pass123")
            db.session.add(user)
            db.session.commit()

            client.post("/auth/login", json={"username": "analyst_test", "password": "Pass123"})
            yield client
            db.session.remove()
            db.drop_all()


def test_single_prediction_api(client):
    payload = {
        "source_ip": "192.168.1.50",
        "destination_ip": "10.0.0.5",
        "protocol": "TCP",
        "destination_port": 80,
        "flow_duration": 1500.0,
        "total_fwd_packets": 200,
        "total_backward_packets": 2,
        "fwd_packet_length_max": 1460.0,
        "bwd_packet_length_mean": 10.0,
        "flow_bytes_s": 1500000.0,
        "flow_packets_s": 5000.0,
    }

    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "attack_type" in data
    assert "severity" in data
    assert "confidence" in data
