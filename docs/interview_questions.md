# Cybersecurity & Placement Interview Preparation Guide

This document contains 30+ technically accurate yet easy-to-explain interview questions and answers designed for campus placement interviews in Cybersecurity, Software Engineering, and Machine Learning roles.

---

## Part 1: Project Overview & Core Cybersecurity Concepts

### Q1: Why did you choose an AI-Based Network Intrusion Detection System for your project?
**Answer**: Modern networks handle high-volume, high-speed traffic where traditional signature-based detection systems struggle to identify zero-day attacks and subtle anomaly patterns. By building an ML-based NIDS, I wanted to combine machine learning for pattern recognition with software engineering (Flask, REST APIs, SQLAlchemy) and cybersecurity operations (SOC dashboards, alert triage).

### Q2: What is an Intrusion Detection System (IDS)?
**Answer**: An Intrusion Detection System is a security monitoring tool that inspects network traffic or host activities for policy violations, malicious activity, or abnormal patterns, generating alerts when suspicious activity is detected.

### Q3: What is the difference between an IDS and an IPS?
**Answer**:
- **IDS (Intrusion Detection System)**: Passive monitor. Listens to mirrored traffic, analyzes flows, and sends alerts to SOC analysts without modifying or blocking network packets directly.
- **IPS (Intrusion Prevention System)**: Active inline device. Sits directly in the network traffic path and actively blocks, drops, or resets connections detected as malicious.

### Q4: Compare Signature-Based vs. Anomaly-Based Detection.
**Answer**:
- **Signature-Based**: Compares packet payloads against a database of known threat signatures (like Snort rules or antivirus definitions). Highly accurate for known threats, but completely blind to new (zero-day) attacks.
- **Anomaly-Based**: Learns baseline behavior of normal network traffic using machine learning. Flags deviations from normal behavior as suspicious. Can detect unknown zero-day attacks, but may produce higher false positive rates.

### Q5: What is the CICIDS2017 / UNSW-NB15 dataset?
**Answer**: CICIDS2017 is a widely benchmarked cybersecurity dataset developed by the Canadian Institute for Cybersecurity. It contains realistic network flow features (80+ metrics like Flow Duration, Total Fwd Packets, Flow Bytes/s) covering normal benign traffic and 7 attack categories (DoS, DDoS, Port Scan, Brute Force, Web Attacks, Botnet, Infiltration).

---

## Part 2: Machine Learning & Preprocessing

### Q6: Why did you choose Random Forest as your primary model?
**Answer**:
1. **Handles Non-Linearity & Feature Interaction**: Network traffic features (duration vs packet rate vs port) have complex non-linear interactions.
2. **Robust Against Overfitting**: Ensemble of multiple decision trees using bagging (bootstrap aggregation).
3. **Imbalanced Data Handling**: Supports class weighting (`class_weight="balanced"`).
4. **Feature Importance & Speed**: Provides fast inference suitable for near real-time traffic classification.

### Q7: Why is Accuracy alone not sufficient for Intrusion Detection?
**Answer**: Because network traffic datasets are heavily class-imbalanced (e.g., 99% benign traffic, 1% malicious). A naive model predicting "BENIGN" for every packet gets 99% raw accuracy but misses 100% of attacks! Therefore, **Recall** (Sensitivity) and **F1-Score** are far more critical metrics.

### Q8: Explain Precision, Recall, and F1-Score in the context of NIDS.
**Answer**:
- **Precision**: Out of all flows predicted as attacks, how many were actual attacks? High precision means low false alarms.
- **Recall (Sensitivity)**: Out of all real attacks, how many did the system catch? High recall means low missed attacks (low false negatives).
- **F1-Score**: Harmonic mean of Precision and Recall: `2 * (Precision * Recall) / (Precision + Recall)`.

### Q9: What is a Confusion Matrix?
**Answer**: A tabular representation comparing actual target classes against predicted classes. Diagonal cells represent correct predictions (True Positives, True Negatives), while off-diagonal cells highlight misclassifications (False Positives, False Negatives).

### Q10: How did you handle missing values and infinite numbers in network flow data?
**Answer**: Flow features like `Flow Bytes/s` can produce division-by-zero infinite values when `Flow Duration` is zero. In our preprocessing pipeline (`data_loader.py`), infinite values are replaced with `NaN`, followed by median feature imputation and standard scaling (`StandardScaler`).

---

## Part 3: Backend, Database & REST APIs

### Q11: How does Flask communicate with the Machine Learning model?
**Answer**: The trained Scikit-Learn model and `StandardScaler` are serialized to disk using `joblib` (`.joblib` files). When a REST API request arrives (`POST /api/predict`), Flask calls `PredictorService`, which loads the joblib model, transforms input features using the scaler, runs `model.predict()`, and formats the output into JSON.

### Q12: Why use the Application Factory pattern (`create_app`) in Flask?
**Answer**: It decouples app configuration from initialization, allowing us to easily instantiate separate app contexts for Development, Production, and Pytest automated testing (`TestingConfig` using an in-memory SQLite database).

### Q13: How is the database designed, and how can it migrate to PostgreSQL?
**Answer**: We use SQLAlchemy ORM models (`User`, `Prediction`, `Alert`, `AuditLog`). DB connections are managed via environment variables (`DATABASE_URL`). Switching from SQLite to PostgreSQL only requires changing the connection string to `postgresql://user:pass@localhost/dbname` without modifying ORM code.

---

## Part 4: Web Security & OWASP Best Practices

### Q14: How are passwords protected in your application?
**Answer**: Passwords are never stored in plaintext. We use `werkzeug.security` to hash passwords using PBKDF2 with SHA-256 and unique per-user random salting.

### Q15: How did you secure file uploads for CSV batch analysis?
**Answer**:
1. Extension validation (`.csv` only).
2. Filename sanitization (`secure_filename`).
3. Stream reading via Pandas without invoking `eval()` or executing code.
4. Input schema validation verifying required numeric columns exist before feeding to ML model.

### Q16: How do you enforce Role-Based Access Control (RBAC)?
**Answer**: We implemented custom python decorators `@login_required` and `@role_required('Admin')` wrapping Flask route handlers. If an Analyst tries to access Admin endpoints (like `/auth/users`), the system blocks the request and returns a `403 Forbidden` response.

### Q17: What security headers are implemented in your system?
**Answer**: Every HTTP response includes:
- `X-Content-Type-Options: nosniff` (prevents MIME sniffing)
- `X-Frame-Options: SAMEORIGIN` (prevents Clickjacking)
- `X-XSS-Protection: 1; mode=block` (mitigates Cross-Site Scripting)

---

## Part 5: Production & Limitations

### Q18: What are the main limitations of this project?
**Answer**:
1. Performs offline batch and API packet inspection rather than direct inline promiscuous packet capture (`libpcap`).
2. Synthetic/sample data fallback used for demonstration; real production requires training on multi-gigabyte continuous network taps.

### Q19: How would you scale this application for a real-world enterprise SOC?
**Answer**:
1. **Packet Capture**: Integrate `scapy` or `DPDK` for live network interface sniffing.
2. **Asynchronous Queue**: Use Celery with Redis/RabbitMQ for high-throughput packet processing.
3. **Database**: Migrate to PostgreSQL/TimescaleDB or Elasticsearch for log indexing.
4. **Containerization**: Deploy backend API, ML inference, and DB via Docker & Kubernetes.
