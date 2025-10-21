# DefenX Frontend Guide

## Table of Contents

1. [Overview](#overview)
2. [API Base URL](#api-base-url)
3. [Authentication](#authentication) *(Not implemented; open for local use)*
4. [Monitoring](#monitoring)

   * Trigger Scan
   * Last Scan
5. [Incidents](#incidents)

   * List All Incidents
   * Get Incident Details
6. [Alerts](#alerts)

   * Latest Alerts
   * Acknowledge Alert
7. [Logs](#logs)

   * Recent Logs
   * Search Logs
8. [Dashboard](#dashboard)

   * Overview
   * Trends
9. [Config](#config)

   * Get Config
   * Update Config
10. [Health](#health)

    * Health Status
    * Metrics
11. [Phishing Scanner](#phishing-scanner)

    * Scan Email/Text

---

## Overview

DefenX backend exposes **real-time server scanning, alerts, logs, dashboard metrics, and phishing detection** via REST APIs. All endpoints are under `/api`.

Use Swagger docs at `/docs` for interactive testing.

---

## API Base URL

```
http://<SERVER_IP>:8000/api
```

Replace `<SERVER_IP>` with your backend server address.

---

## Authentication

Currently, no authentication. Frontend can call APIs directly.

---

## Monitoring

### Trigger Scan

**Endpoint:** `POST /monitor/scan`

**Request Body:**

```json
{
  "ports": [22, 80, 443]
}
```

* `ports` (optional): list of ports to scan. If omitted, defaults are used.

**Response Example:**

```json
{
  "scan_target": "127.0.0.1",
  "ports": {
    "22": true,
    "80": false,
    "443": true
  },
  "http_info": {
    "status_code": 200,
    "server": "nginx/1.23",
    "security_headers": {}
  },
  "timestamp": "2025-10-21T08:15:00Z"
}
```

---

### Last Scan

**Endpoint:** `GET /monitor/last`

**Response Example:**

```json
{
  "scan_target": "127.0.0.1",
  "ports": {...},
  "http_info": {...},
  "timestamp": "2025-10-21T08:15:00Z"
}
```

---

## Incidents

### List All Incidents

**Endpoint:** `GET /incidents/all`

**Response Example:**

```json
[
  {
    "incident_id": "INC-1",
    "timestamp": "2025-10-21T08:15:00Z",
    "type": "open_ports",
    "severity": "Medium",
    "status": "Open",
    "source": "scanner",
    "details": "Open ports on 127.0.0.1: [22, 443]"
  }
]
```

### Get Incident Details

**Endpoint:** `GET /incidents/{incident_id}`

**Example:** `/incidents/INC-1`

---

## Alerts

### Latest Alerts

**Endpoint:** `GET /alerts/latest?limit=5&severity=High`

**Parameters:**

* `limit` (optional): number of alerts to fetch (default 10)
* `severity` (optional): filter by `Low`, `Medium`, `High`

### Acknowledge Alert

**Endpoint:** `POST /alerts/acknowledge?alert_id=AL-1`

---

## Logs

### Recent Logs

**Endpoint:** `GET /logs/recent?limit=50`

### Search Logs

**Endpoint:** `GET /logs/search?query=scan&start_time=2025-10-21T00:00:00Z&end_time=2025-10-21T12:00:00Z`

---

## Dashboard

### Overview

**Endpoint:** `GET /dashboard/overview`

**Response Example:**

```json
{
  "total_incidents": 3,
  "active_alerts": 1,
  "total_logs": 120,
  "last_scan_time": "2025-10-21T08:15:00Z"
}
```

### Trends

**Endpoint:** `GET /dashboard/trends`

---

## Config

### Get Config

**Endpoint:** `GET /config/`

### Update Config

**Endpoint:** `POST /config/update`

**Example Body:**

```json
{
  "scan_ports_default": [22, 80, 443, 3306],
  "scan_interval_seconds": 120
}
```

---

## Health

### Health Status

**Endpoint:** `GET /health/health`

### Metrics

**Endpoint:** `GET /health/metrics`

---

## Phishing Scanner

### Scan Email/Text

**Endpoint:** `POST /phishing/scan`

**Request Body Example:**

```json
{
  "content": "Please click here to verify your account",
  "custom_keywords": ["verify"],
  "custom_domains": ["malicious.com"]
}
```

**Response Example:**

```json
{
  "risk_score": 3,
  "risk_level": "High",
  "reasons": [
    "Keyword detected: verify",
    "Suspicious domain: malicious.com"
  ]
}
```

---

## Notes for Frontend Developers

1. All routes are prefixed with `/api`.
2. Scanner runs in **real-time** on the server; `/monitor/last` always shows the latest results.
3. Alerts, incidents, and logs are **real-time**.
4. Use Swagger docs at `/docs` for testing.
5. Config can be read/updated at runtime.
