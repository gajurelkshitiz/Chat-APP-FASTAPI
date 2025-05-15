"""Test the api."""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_add_api():
    """Checks the health api."""
    response = client.get("/add/1/2")
    assert (
        response.status_code == 200
    )
    assert response.json() == {
        "result": 3
    }
