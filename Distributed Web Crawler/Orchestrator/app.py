from fastapi import FastAPI

app = FastAPI()

URLS = [
    "https://example.com",
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://docs.docker.com",
    "https://github.com"
]

@app.get("/")
def home():
    return {"I'm up!"}

@app.get("/get_urls")
def get_urls():
    return {"urls": URLS}