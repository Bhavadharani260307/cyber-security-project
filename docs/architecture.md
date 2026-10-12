# System Architecture & Technical Design Document

## System Overview

The **AI-Based Network Intrusion Detection & Threat Monitoring System** is designed as a modular 3-tier enterprise architecture.

```text
[ Network Packets / CSV Upload ]
               │
               ▼
┌──────────────────────────────┐
│  Presentation Layer (UI)     │
│  HTML5 / CSS / JS / Chart.js │
└──────────────┬───────────────┘
               │ REST API / JSON
               ▼
┌──────────────────────────────┐
│  Application Layer (Flask)   │
│  - Auth & RBAC Decorators    │
│  - Predictor Service         │
│  - Alert Triage Service      │
│  - Audit Log Service         │
└──────────────┬───────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐ ┌──────────────┐
│ Joblib ML    │ │ SQLAlchemy   │
│ Model Engine │ │ Database     │
└──────────────┘ └──────────────┘
```

---

## Data Flow Diagram

1. **Traffic Acquisition**: Packets are provided via single form entry or CSV batch file upload.
2. **Sanitization & Preprocessing**: `validators.py` and `data_loader.py` clean inputs, replace infinite values, fill missing metrics, and standardize feature order.
3. **Model Inference**: `PredictorService` passes feature matrix through `StandardScaler` and runs `RandomForestClassifier.predict()`.
4. **Threat Classification & Thresholding**: Predicted class mapped to severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and status (`NORMAL`, `SUSPICIOUS`, `MALICIOUS`).
5. **Persistence & Alerting**: Record saved in `predictions` table. If status is malicious or suspicious, an `Alert` record is automatically pushed to the alert queue.
6. **SOC Presentation**: Dashboard charts and alert queues poll endpoints (`/api/dashboard/statistics`, `/api/alerts`) to render real-time UI updates.
