from fastapi.testclient import TestClient

from app.main import app


def test_health_check_reports_status_without_secrets():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["supabase_configured"], bool)
    assert isinstance(body["auth_enabled"], bool)
    assert "SUPABASE_SERVICE_KEY" not in body
    assert "SUPABASE_JWT_SECRET" not in body
