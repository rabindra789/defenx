from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "DefenX Backend"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_monitor_last():
    response = client.get("/api/monitor/last")
    assert response.status_code == 200


def test_dashboard_overview():
    response = client.get("/api/dashboard/overview")
    assert response.status_code == 200


def test_alerts_latest():
    response = client.get("/api/alerts/latest")
    assert response.status_code == 200


def test_incidents_all():
    response = client.get("/api/incidents/all")
    assert response.status_code == 200


def test_logs_recent():
    response = client.get("/api/logs/recent")
    assert response.status_code == 200


def test_config_get():
    response = client.get("/api/config")
    assert response.status_code == 200
