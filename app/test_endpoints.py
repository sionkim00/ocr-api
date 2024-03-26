import io
import shutil

from fastapi.testclient import TestClient
from PIL import Image, ImageChops

from app.main import BASE_DIR, UPLOAD_DIR, app, get_settings

client = TestClient(app)

valid_image_extensiosn = ["png", "jpg", "jpeg"]


def test_get_home():
    response = client.get("/")
    assert "text/html" in response.headers["content-type"]
    assert response.status_code == 200
    assert response.text != "<h1>Hello World</h1>"


def test_echo_upload():
    img_saved_path = BASE_DIR / "images"

    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except Exception:
            img = None

        response = client.post("/img-echo/", files={"file": open(path, "rb")})

        if img is None:
            # Invalid image
            assert response.status_code == 400
        else:
            # Valid image
            assert response.status_code == 200

            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)

            # compare image
            dif = ImageChops.difference(echo_img, img).getbbox()
            assert dif is None

    # time.sleep(5)
    shutil.rmtree(UPLOAD_DIR)


def test_prediction_upload_missing_auth_header():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()

    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except Exception:
            img = None

        response = client.post("/", files={"file": open(path, "rb")})

        assert response.status_code == 401


def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()

    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except Exception:
            img = None

        response = client.post(
            "/",
            files={"file": open(path, "rb")},
            headers={"Authorization": f"JWT {settings.app_auth_token}"},
        )

        if img is None:
            # Invalid image
            assert response.status_code == 400
        else:
            # Valid image
            assert response.status_code == 200

            data = response.json()
            assert len(data.keys()) == 1
