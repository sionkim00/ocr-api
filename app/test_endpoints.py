import shutil
import time

from fastapi.testclient import TestClient

from app.main import BASE_DIR, UPLOAD_DIR, app

client = TestClient(app)


def test_get_home():
    response = client.get("/")
    assert "text/html" in response.headers["content-type"]
    assert response.status_code == 200
    assert response.text != "<h1>Hello World</h1>"


def test_echo_upload():
    img_saved_path = BASE_DIR / "images"

    for path in img_saved_path.glob("*.png"):
        response = client.post("/img-echo/", files={"file": open(path, "rb")})
        assert response.status_code == 200

        fext = str(path.suffix).replace(".", "")
        assert fext in response.headers["content-type"]

    time.sleep(5)
    shutil.rmtree(UPLOAD_DIR)
