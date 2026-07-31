from fastapi.testclient import TestClient

from services.ingestion_api.app.main import app


client = TestClient(app)


def test_liveness_endpoint() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ingestion-api",
    }