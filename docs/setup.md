# Detailed Setup & Installation Guide

This document provides step-by-step instructions to set up, configure, train, test, and run the **AI-Based Network Intrusion Detection and Threat Monitoring System** on Windows, Linux, and macOS.

---

## Prerequisites

- **Python**: Version 3.11 or higher
- **Git**: For version control
- **Web Browser**: Chrome, Firefox, Edge, or Brave

---

## Step 1: Environment Setup

### 1. Open Terminal / PowerShell
Navigate to your working directory:
```bash
cd cyber_project
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

---

## Step 2: Dependencies Installation

Install backend, database, machine learning, and testing libraries:
```bash
pip install -r requirements.txt
```

---

## Step 3: Environment Configuration

Copy `.env.example` to create your active `.env` configuration file:
```bash
cp .env.example .env
```

Verify your `.env` contains:
```ini
FLASK_APP=backend/run.py
FLASK_ENV=development
SECRET_KEY=nids-dev-secret-key-987654321-cyber-security
DATABASE_URL=sqlite:///cyber_nids.db
MODEL_PATH=ml/saved_models/nids_random_forest.joblib
SCALER_PATH=ml/saved_models/nids_scaler.joblib
METRICS_PATH=ml/saved_models/model_metrics.json
```

---

## Step 4: Machine Learning Model Training

Train the Random Forest model and generate evaluation metrics:
```bash
python ml/train_model.py
```

Expected Output:
```text
[+] Successfully generated synthetic traffic flow samples...
[*] Training Primary Model: Random Forest Classifier...
[+] Saved trained Random Forest model to ml/saved_models/nids_random_forest.joblib
[+] Saved fitted StandardScaler to ml/saved_models/nids_scaler.joblib
[+] Verified metrics saved to ml/saved_models/model_metrics.json
    - Accuracy : 99.80%
    - Precision: 99.80%
    - Recall   : 99.80%
    - F1-Score : 99.80%
```

---

## Step 5: Run Automated Tests

Verify application health, authentication, predictions, alert generation, and RBAC restrictions using Pytest:
```bash
python -m pytest tests/
```

---

## Step 6: Start the Application Server

Launch the Flask development web server:
```bash
python backend/run.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000`

---

## Default Access Credentials

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `Admin@123456` | Full system access, User Management, Alert Triage, Reports |
| **Analyst** | `analyst` | `Analyst@123456` | Traffic Analysis, Single Flow Predictor, Threat Alerts, Reports |
