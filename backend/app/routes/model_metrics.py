"""
Model Performance & Evaluation Metrics API Blueprint
"""

import json
from pathlib import Path
from flask import Blueprint, jsonify
from flask_login import login_required
from backend.config import Config

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/api/model/metrics", methods=["GET"])
@login_required
def get_model_metrics():
    metrics_path = Path(Config.METRICS_PATH)

    if not metrics_path.exists():
        # Trigger training to generate metrics if missing
        from ml.train_model import train_nids_models

        train_nids_models()

    try:
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": f"Failed to load model metrics: {str(e)}"}), 500
