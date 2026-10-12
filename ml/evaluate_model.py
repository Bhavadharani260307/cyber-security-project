"""
Model Evaluation and Metrics Generation Module
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SAVED_MODELS_DIR = BASE_DIR / "ml" / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
METRICS_FILE = SAVED_MODELS_DIR / "model_metrics.json"


def evaluate_and_save_metrics(
    model, X_test, y_test, model_name="Random Forest", extra_models_metrics=None
):
    """
    Calculates comprehensive classification metrics, confusion matrix,
    and saves JSON payload for dashboard display.
    """
    y_pred = model.predict(X_test)
    classes = sorted(list(set(y_test)))

    # Overall metrics
    acc = float(accuracy_score(y_test, y_pred))
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted", zero_division=0
    )

    # Per-class metrics
    p_class, r_class, f1_class, support_class = precision_recall_fscore_support(
        y_test, y_pred, labels=classes, zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=classes)

    class_metrics = {}
    for idx, cls in enumerate(classes):
        class_metrics[cls] = {
            "precision": float(round(p_class[idx], 4)),
            "recall": float(round(r_class[idx], 4)),
            "f1_score": float(round(f1_class[idx], 4)),
            "support": int(support_class[idx]),
        }

    metrics_payload = {
        "primary_model": model_name,
        "overall_metrics": {
            "accuracy": round(acc, 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
        },
        "classes": classes,
        "confusion_matrix": cm.tolist(),
        "class_metrics": class_metrics,
        "compared_models": extra_models_metrics or {},
    }

    with open(METRICS_FILE, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"[+] Verified metrics saved to {METRICS_FILE}")
    print(f"    - Accuracy : {acc * 100:.2f}%")
    print(f"    - Precision: {precision * 100:.2f}%")
    print(f"    - Recall   : {recall * 100:.2f}%")
    print(f"    - F1-Score : {f1 * 100:.2f}%")

    return metrics_payload
