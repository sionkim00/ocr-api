from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home_view():
    return {"text": "Hello World"}


@app.get("/")
def home_detail_view():
    return {"text": "Hello World"}
