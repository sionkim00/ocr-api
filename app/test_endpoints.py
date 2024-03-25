from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_home():
    response = client.get("/")
    assert "text/html" in response.headers["content-type"]
    assert response.status_code == 200
    assert response.text != "<h1>Hello World</h1>"
