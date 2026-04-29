from fastapi.testclient import TestClient

from app.main import app


def test_health_check_reports_status_without_secrets():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "supabase_configured": True,
        "auth_enabled": None,
    }
