"""
ML Predictor Service for AI-Based NIDS
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from backend.config import Config
from ml.preprocessing.data_loader import FEATURE_COLUMNS, preprocess_data

# Threat Severity & Status Mapping based on attack categories
ATTACK_SEVERITY_MAP = {
    "BENIGN": {"severity": "LOW", "status": "NORMAL"},
    "DoS": {"severity": "HIGH", "status": "MALICIOUS"},
    "DDoS": {"severity": "CRITICAL", "status": "MALICIOUS"},
    "Port Scan": {"severity": "MEDIUM", "status": "SUSPICIOUS"},
    "Brute Force": {"severity": "HIGH", "status": "MALICIOUS"},
    "Web Attack": {"severity": "HIGH", "status": "MALICIOUS"},
    "Bot": {"severity": "CRITICAL", "status": "MALICIOUS"},
    "Infiltration": {"severity": "CRITICAL", "status": "MALICIOUS"},
}

ATTACK_DESCRIPTIONS = {
    "BENIGN": "Normal network traffic behavior with standard flow rate and packet size distribution.",
    "DoS": "Denial of Service attack detected. High volume of request packets targeting service availability.",
    "DDoS": "Distributed Denial of Service attack detected. Massive flood of malicious packets from multiple sources.",
    "Port Scan": "Reconnaissance activity detected. Sequential probing of open network ports.",
    "Brute Force": "Credential brute-forcing attempt detected against authentication service.",
    "Web Attack": "Malicious HTTP payload injection (SQLi/XSS/Command Injection) detected.",
    "Bot": "Automated botnet Command & Control (C2) communication detected.",
    "Infiltration": "Unauthorized network intrusion and internal compromise activity detected.",
}


class PredictorService:
    """Wrapper service for model loading, feature validation, scaling, and inference"""

    _model = None
    _scaler = None

    @classmethod
    def load_artifacts(cls):
        """Lazy load joblib model and scaler"""
        if cls._model is None or cls._scaler is None:
            model_path = Path(Config.MODEL_PATH)
            scaler_path = Path(Config.SCALER_PATH)

            if not model_path.exists() or not scaler_path.exists():
                # Train model on the fly if artifacts missing
                from ml.train_model import train_nids_models

                print("[!] ML artifacts missing. Running training pipeline on demand...")
                train_nids_models()

            cls._model = joblib.load(model_path)
            cls._scaler = joblib.load(scaler_path)

    @classmethod
    def predict_single(cls, feature_dict: dict) -> dict:
        """
        Runs prediction for a single network flow packet dictionary.
        Returns prediction details including class, probability, severity, and description.
        """
        cls.load_artifacts()

        # Build single row dataframe
        df_row = pd.DataFrame([feature_dict])
        X_df, _ = preprocess_data(df_row, is_training=False)

        # Scale features
        X_scaled = cls._scaler.transform(X_df)

        # Prediction
        prediction_class = cls._model.predict(X_scaled)[0]

        # Confidence / Probabilities
        confidence = 1.0
        if hasattr(cls._model, "predict_proba"):
            probs = cls._model.predict_proba(X_scaled)[0]
            confidence = float(np.max(probs))

        meta = ATTACK_SEVERITY_MAP.get(
            prediction_class, {"severity": "MEDIUM", "status": "SUSPICIOUS"}
        )

        description = ATTACK_DESCRIPTIONS.get(
            prediction_class, f"Suspicious activity detected: {prediction_class}"
        )

        return {
            "attack_type": prediction_class,
            "severity": meta["severity"],
            "status": meta["status"],
            "confidence": float(round(confidence, 4)),
            "description": description,
            "features_used": feature_dict,
        }

    @classmethod
    def predict_batch(cls, df: pd.DataFrame) -> list:
        """
        Runs prediction for a batch dataframe (e.g. uploaded CSV).
        """
        cls.load_artifacts()

        X_df, _ = preprocess_data(df, is_training=False)
        X_scaled = cls._scaler.transform(X_df)

        preds = cls._model.predict(X_scaled)

        probabilities = None
        if hasattr(cls._model, "predict_proba"):
            probabilities = np.max(cls._model.predict_proba(X_scaled), axis=1)

        results = []
        for idx in range(len(df)):
            attack = preds[idx]
            conf = float(probabilities[idx]) if probabilities is not None else 1.0
            meta = ATTACK_SEVERITY_MAP.get(
                attack, {"severity": "MEDIUM", "status": "SUSPICIOUS"}
            )

            row_dict = df.iloc[idx].to_dict()
            src_ip = str(row_dict.get("Source IP", row_dict.get("source_ip", f"192.168.1.{10+idx%200}")))
            dst_ip = str(row_dict.get("Destination IP", row_dict.get("destination_ip", "10.0.0.5")))
            protocol = str(row_dict.get("Protocol", row_dict.get("protocol", "TCP")))
            src_port = int(row_dict.get("Source Port", row_dict.get("source_port", 1024 + idx)))
            dst_port = int(row_dict.get("Destination Port", row_dict.get("destination_port", 80)))

            results.append(
                {
                    "source_ip": src_ip,
                    "destination_ip": dst_ip,
                    "protocol": protocol,
                    "source_port": src_port,
                    "destination_port": dst_port,
                    "attack_type": attack,
                    "severity": meta["severity"],
                    "status": meta["status"],
                    "confidence": float(round(conf, 4)),
                    "description": ATTACK_DESCRIPTIONS.get(attack, f"Incident: {attack}"),
                }
            )

        return results
