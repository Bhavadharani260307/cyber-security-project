"""
Automated Pytest Suite for Security Headers and RBAC Protection
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

            analyst = User(username="analyst_sec", email="sec@test.com", role="Analyst")
            analyst.set_password("Pass123")
            db.session.add(analyst)
            db.session.commit()
            yield client
            db.session.remove()
            db.drop_all()


def test_security_headers(client):
    res = client.get("/api/health")
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"


def test_unauthorized_access_protection(client):
    # Unauthenticated API request
    res = client.get("/api/alerts")
    assert res.status_code == 401


def test_rbac_admin_restriction(client):
    # Login as Analyst
    client.post("/auth/login", json={"username": "analyst_sec", "password": "Pass123"})

    # Analyst trying to access Admin-only user management endpoint
    res = client.get("/auth/users", headers={"Accept": "application/json"})
    assert res.status_code == 403
