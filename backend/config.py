import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of Project
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base Configuration Class"""

    SECRET_KEY = os.getenv(
        "SECRET_KEY", "fallback-dev-secret-key-replace-in-prod"
    )

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'cyber_nids.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Machine Learning Artifact Paths
    MODEL_PATH = BASE_DIR / os.getenv(
        "MODEL_PATH", "ml/saved_models/nids_random_forest.joblib"
    )
    SCALER_PATH = BASE_DIR / os.getenv(
        "SCALER_PATH", "ml/saved_models/nids_scaler.joblib"
    )
    METRICS_PATH = BASE_DIR / os.getenv(
        "METRICS_PATH", "ml/saved_models/model_metrics.json"
    )

    # Security & Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file upload
    UPLOAD_EXTENSIONS = [".csv"]

    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
