"""
Automated Pytest Suite for Authentication and User Authorization
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
            yield client
            db.session.remove()
            db.drop_all()


def test_user_password_hashing():
    u = User(username="testuser", email="test@local.com", role="Analyst")
    u.set_password("SecretPassword123")
    assert u.password_hash != "SecretPassword123"
    assert u.check_password("SecretPassword123") is True
    assert u.check_password("WrongPassword") is False


def test_login_success_and_failure(client):
    # Register user
    client.post(
        "/auth/register",
        json={"username": "analyst1", "email": "a1@test.com", "password": "Password123"},
    )

    # Valid Login
    res_valid = client.post(
        "/auth/login",
        json={"username": "analyst1", "password": "Password123"},
    )
    assert res_valid.status_code == 200

    # Logout before testing invalid login
    client.get("/auth/logout")

    # Invalid Login
    res_invalid = client.post(
        "/auth/login",
        json={"username": "analyst1", "password": "WrongPassword"},
    )
    assert res_invalid.status_code == 401
