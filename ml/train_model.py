"""
Main Training Pipeline Script for AI-Based NIDS
"""

import sys
from pathlib import Path
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.sample_generator import generate_synthetic_dataset
from ml.preprocessing.data_loader import load_and_prepare_dataset
from ml.evaluate_model import evaluate_and_save_metrics

SAVED_MODELS_DIR = PROJECT_ROOT / "ml" / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = SAVED_MODELS_DIR / "nids_random_forest.joblib"
SCALER_PATH = SAVED_MODELS_DIR / "nids_scaler.joblib"


def train_nids_models(data_file_path=None):
    """Full pipeline: load data, train baseline + comparison models, save model & metrics"""
    if data_file_path is None or not Path(data_file_path).exists():
        print("[!] No dataset path provided or file missing. Generating synthetic sample dataset...")
        data_file_path = generate_synthetic_dataset()

    print(f"[*] Loading and preprocessing dataset from {data_file_path}...")
    (
        X_train,
        X_test,
        y_train,
        y_test,
        scaler,
        feature_names,
    ) = load_and_prepare_dataset(data_file_path)

    print(f"[+] Training dataset prepared: {X_train.shape[0]} train samples, {X_test.shape[0]} test samples.")

    # 1. Primary Model: Random Forest
    print("[*] Training Primary Model: Random Forest Classifier...")
    rf_model = RandomForestClassifier(
        n_estimators=100, max_depth=15, random_state=42, class_weight="balanced"
    )
    rf_model.fit(X_train, y_train)

    # 2. Comparison Models
    print("[*] Training Comparison Model 1: Decision Tree Classifier...")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_train, y_train)

    print("[*] Training Comparison Model 2: Logistic Regression...")
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)

    # Evaluate comparison models
    compared_metrics = {}
    for name, m in [("Decision Tree", dt_model), ("Logistic Regression", lr_model)]:
        y_p = m.predict(X_test)
        acc = accuracy_score(y_test, y_p)
        p, r, f1, _ = precision_recall_fscore_support(
            y_test, y_p, average="weighted", zero_division=0
        )
        compared_metrics[name] = {
            "accuracy": round(float(acc), 4),
            "precision": round(float(p), 4),
            "recall": round(float(r), 4),
            "f1_score": round(float(f1), 4),
        }

    # Save primary model & scaler via joblib
    joblib.dump(rf_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"[+] Saved trained Random Forest model to {MODEL_PATH}")
    print(f"[+] Saved fitted StandardScaler to {SCALER_PATH}")

    # Evaluate Primary Model and generate model_metrics.json
    metrics_payload = evaluate_and_save_metrics(
        rf_model, X_test, y_test, model_name="Random Forest", extra_models_metrics=compared_metrics
    )

    return rf_model, scaler, metrics_payload


if __name__ == "__main__":
    train_nids_models()
