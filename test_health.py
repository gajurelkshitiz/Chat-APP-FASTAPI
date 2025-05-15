"""Test the api."""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_api():
    """Checks the health api."""
    response = client.get("/health-check")
    assert (
        response.status_code == 200
    ), "Error, make sure the server is running correctly."
    assert response.json() == {
        "status": "OK"
    }
