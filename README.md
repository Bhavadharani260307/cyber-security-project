# AI-Based Network Intrusion Detection & Threat Monitoring System

A production-style, defensive cybersecurity and machine learning application designed to classify network traffic flows, detect malicious intrusions in real-time, generate automated threat alerts, and present visual SOC monitoring analytics.

---

## Key Features

- **Machine Learning Threat Classification**: Multi-class classification of network flow traffic into 8 categories (`BENIGN`, `DoS`, `DDoS`, `Port Scan`, `Brute Force`, `Web Attack`, `Bot`, `Infiltration`).
- **Real-Time SOC Dashboard**: Summary statistics cards, interactive Chart.js widgets (Traffic Status Breakdown, Attack Category Distribution), and live threat alert stream.
- **Batch CSV Analysis**: Upload raw network traffic flow CSV datasets for automated cleaning, feature scaling, model inference, and threat logging.
- **Single Flow Inspector**: Manual entry form for real-time packet feature evaluation with defensive explanations and confidence scores.
- **Incident Response Alert Management**: Filter, search, and manage threat alerts through lifecycle stages (`NEW` → `INVESTIGATING` → `RESOLVED`).
- **Security & RBAC**: Role-Based Access Control (`Admin`, `Analyst`), salted PBKDF2 password hashing, secure session cookies, CSRF protection, and security headers.
- **Model Evaluation Suite**: Visualized confusion matrix heatmap, per-class precision/recall/F1-score breakdown, and model comparisons (`Random Forest` vs `Decision Tree` vs `Logistic Regression`).
- **Reports & Export**: Download historical traffic predictions and threat alerts as standard CSV reports.

---

## Technology Stack

- **Backend**: Python 3.11+, Flask 3.0, SQLAlchemy ORM, Flask-Login, Werkzeug Security, Python-Dotenv
- **Machine Learning**: Scikit-Learn 1.9+, Pandas 3.0+, NumPy 2.4+, Joblib
- **Frontend**: HTML5, Vanilla CSS3 (SOC Dark Theme), JavaScript (ES6+), Bootstrap 5.3, Chart.js
- **Database**: SQLite3 (development) / PostgreSQL ready
- **Testing & Security**: Pytest 9.0+, Role Decorators, Security Headers (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`)

---

## System Architecture

```text
cyber_project/
├── backend/
│   ├── app/
│   │   ├── routes/        # Auth, Dashboard, Predict, Alerts, Reports, Metrics
│   │   ├── models/        # User, Prediction, Alert, AuditLog
│   │   ├── services/      # PredictorService, AlertService, AuditService
│   │   ├── security/      # RBAC Decorators & Input Validators
│   │   └── database.py    # SQLAlchemy DB Instance
│   ├── config.py          # Environment Configurations
│   └── run.py             # Entry Point Script
├── frontend/
│   ├── templates/         # Jinja2 Layout & Page Views
│   └── static/            # SOC Dark Theme CSS & JavaScript
├── ml/
│   ├── data/              # Raw & Processed Datasets (CICIDS2017 Format)
│   ├── preprocessing/     # Data Loading & Scaling Pipeline
│   ├── train_model.py     # Random Forest & Comparison Training Pipeline
│   ├── sample_generator.py# Synthetic Dataset Generator
│   └── saved_models/      # Joblib Models & Metrics JSON
├── tests/                 # Pytest Automated Test Suite
└── docs/                  # Architecture, API & Interview Questions
```

---

## Installation & Setup Guide

### 1. Clone & Environment Setup
```bash
git clone https://github.com/your-username/cyber_project.git
cd cyber_project
python -m venv venv
```

Activate Virtual Environment:
- **Windows (PowerShell)**: `venv\Scripts\activate`
- **Linux / macOS**: `source venv/bin/activate`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Environment File
Copy the example environment configuration:
```bash
cp .env.example .env
```

### 4. Train the ML Model
Run the automated dataset generator and training pipeline:
```bash
python ml/train_model.py
```
*Output*: Saves trained model to `ml/saved_models/nids_random_forest.joblib` and metrics to `ml/saved_models/model_metrics.json`.

### 5. Launch the Application
```bash
python backend/run.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

**Default Login Credentials**:
- **Admin User**: `admin` / `Admin@123456`
- **Analyst User**: `analyst` / `Analyst@123456`

---

## Running Automated Tests

Run the full pytest suite:
```bash
python -m pytest tests/
```

---

## API Documentation Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticates user and establishes secure session |
| `POST` | `/auth/logout` | Terminates user session |
| `GET` | `/api/dashboard/statistics` | Summary metrics & attack distribution for Chart.js |
| `POST` | `/api/predict` | Single packet feature classification |
| `POST` | `/api/predict/batch` | Upload CSV dataset for batch prediction |
| `GET` | `/api/alerts` | Retrieve security threat alerts (filterable) |
| `PATCH` | `/api/alerts/<id>` | Update alert investigation status |
| `GET` | `/api/model/metrics` | Retrieve model confusion matrix & per-class F1-scores |
| `GET` | `/api/reports/export` | Download predictions or alerts as CSV |

---

## Disclaimer

This project is strictly developed for **defensive cybersecurity, education, authorized testing, and academic portfolio demonstration**. It does not contain any offensive attack functionality or unauthorized scanning tools.
