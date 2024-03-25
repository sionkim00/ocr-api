import io
import pathlib
import uuid
from functools import lru_cache

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

# ---------- Start of .env Settings ----------


class Settings(BaseSettings):
    debug: bool = False
    ECHO_ACTIVE: bool = False

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


@app.post("/")
def home_detail_view():
    return {"text": "Hello World"}


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(
    file: UploadFile = File(...), settings: Settings = Depends(get_settings)
):
    if not settings.ECHO_ACTIVE:
        raise HTTPException(detail="Invalid endpoint", status_code=400)

    bytes_str = io.BytesIO(await file.read())

    fname = pathlib.Path(file.filename)
    fext = fname.suffix

    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"

    with open(str(dest), "wb") as out:
        out.write(bytes_str.read())

    return dest
