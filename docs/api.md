# REST API Specification Document

## Authentication Endpoints

### 1. User Login
- **Endpoint**: `POST /auth/login`
- **Payload**:
```json
{
  "username": "admin",
  "password": "Admin@123456"
}
```
- **Response** (`200 OK`):
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@nids.local",
    "role": "Admin"
  }
}
```

---

## Prediction Endpoints

### 2. Single Flow Prediction
- **Endpoint**: `POST /api/predict`
- **Payload**:
```json
{
  "source_ip": "192.168.1.100",
  "destination_ip": "10.0.0.5",
  "protocol": "TCP",
  "destination_port": 80,
  "flow_duration": 1500,
  "total_fwd_packets": 200,
  "total_backward_packets": 2,
  "fwd_packet_length_max": 1460,
  "bwd_packet_length_mean": 10,
  "flow_bytes_s": 1500000,
  "flow_packets_s": 5000
}
```
- **Response** (`200 OK`):
```json
{
  "id": 15,
  "attack_type": "DoS",
  "severity": "HIGH",
  "confidence": 0.984,
  "status": "MALICIOUS",
  "alert_generated": true,
  "description": "Denial of Service attack detected. High volume of request packets targeting service availability."
}
```

### 3. Batch CSV Prediction
- **Endpoint**: `POST /api/predict/batch`
- **Form Data**: `file` (CSV file)
- **Response** (`200 OK`):
```json
{
  "message": "Successfully processed 250 records.",
  "total_records": 250,
  "alerts_generated": 18,
  "predictions": [...]
}
```

---

## Alert Endpoints

### 4. Get Threat Alerts
- **Endpoint**: `GET /api/alerts?status=NEW&severity=HIGH`
- **Response** (`200 OK`): List of alert objects.

### 5. Update Alert Status
- **Endpoint**: `PATCH /api/alerts/<id>`
- **Payload**: `{"status": "RESOLVED"}`
- **Response** (`200 OK`): Updated alert object.
