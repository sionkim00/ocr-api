import io
import pathlib
import uuid
from functools import lru_cache

import pytesseract
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image
from pydantic_settings import BaseSettings

# ---------- Start of .env Settings ----------


class Settings(BaseSettings):
    debug: bool = False
    ECHO_ACTIVE: bool = False
    app_auth_token: str
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
DEBUG = settings.debug

# ---------- End of .env Settings ----------

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploaded"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    # print(settings.debug)
    return templates.TemplateResponse("home.html", {"request": request})


def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    if settings.debug and settings.skip_auth:
        return

    if authorization is None:
        raise HTTPException(detail="Invalid authorization", status_code=401)

    label, token = authorization.split()
    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid authorization", status_code=401)


@app.post("/")
async def prediction_view(
    file: UploadFile = File(...),
    authorization=Header(None),
    settings: Settings = Depends(get_settings),
):
    verify_auth(authorization, settings)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except Exception as e:
        raise HTTPException(detail="Invalid image", status_code=400) from e

    ocr_prediction = pytesseract.image_to_string(img)
    ocr_predictions = [x for x in ocr_prediction.split("\n")]

    return {"result": ocr_predictions}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(
    file: UploadFile = File(...), settings: Settings = Depends(get_settings)
):
    if not settings.ECHO_ACTIVE:
        raise HTTPException(detail="Invalid endpoint", status_code=400)

    fname = pathlib.Path(file.filename)
    fext = fname.suffix

    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except Exception as e:
        raise HTTPException(detail="Invalid image", status_code=400) from e
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"
    img.save(dest)

    return dest
