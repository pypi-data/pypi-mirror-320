from fastapi.testclient import TestClient
from app import app


def test_index():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    # assert response.json() == {"detail": "division by zero"}