"""
Data Loader & Preprocessing Pipeline for Network Intrusion Detection System
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Standard feature set required by model
FEATURE_COLUMNS = [
    "Destination Port",
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Fwd Packet Length Max",
    "Bwd Packet Length Mean",
    "Flow Bytes/s",
    "Flow Packets/s",
]

STANDARD_ATTACK_MAP = {
    "BENIGN": "BENIGN",
    "NORMAL": "BENIGN",
    "DOS": "DoS",
    "DOS HULK": "DoS",
    "DOS GOLDENEYE": "DoS",
    "DOS SLOWLORIS": "DoS",
    "DOS SLOWHTTPTEST": "DoS",
    "DDOS": "DDoS",
    "PORT SCAN": "Port Scan",
    "PORTSCAN": "Port Scan",
    "FTP-PATATOR": "Brute Force",
    "SSH-PATATOR": "Brute Force",
    "BRUTE FORCE": "Brute Force",
    "WEB ATTACK": "Web Attack",
    "WEB ATTACK - XSS": "Web Attack",
    "WEB ATTACK - SQL INJECTION": "Web Attack",
    "WEB ATTACK - BRUTE FORCE": "Web Attack",
    "BOT": "Bot",
    "INFILTRATION": "Infiltration",
}


def preprocess_data(df: pd.DataFrame, is_training: bool = True):
    """
    Cleans raw dataframe, handles infinite/NaN values, standardizes column names,
    maps labels, and extracts feature matrix.
    """
    # 1. Clean column names
    df = df.copy()
    df.columns = df.columns.str.strip()

    # 2. Map labels if present
    if "Label" in df.columns:
        df["Label"] = df["Label"].astype(str).str.strip().str.upper()
        df["Label"] = df["Label"].map(
            lambda val: STANDARD_ATTACK_MAP.get(val, "BENIGN" if "BENIGN" in val else val.title())
        )

    # 3. Ensure required numerical feature columns exist
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Input dataframe missing required features: {missing_cols}")

    # 4. Handle Infinite & Missing Values
    X = df[FEATURE_COLUMNS].copy()
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(X.median(numeric_only=True), inplace=True)
    X.fillna(0, inplace=True)

    y = df["Label"] if "Label" in df.columns else None

    return X, y


def load_and_prepare_dataset(file_path: str, test_size=0.2, random_state=42):
    """
    Full pipeline to load CSV dataset, preprocess, scale, and split into train/test sets.
    """
    df = pd.read_csv(file_path)

    # Clean & preprocess
    X, y = preprocess_data(df, is_training=True)

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Standard Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return (
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
        scaler,
        X.columns.tolist(),
    )
