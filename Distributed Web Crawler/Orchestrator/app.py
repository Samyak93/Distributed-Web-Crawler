from fastapi import FastAPI, Body
from pymongo import MongoClient
import os

app = FastAPI()

collection = None

ARXIV_URLS = ["https://arxiv.org/search/cs?query=Computer+Network&searchtype=all&abstracts=show&order=-announced_date_first&size=50"]
MIT_URLS = ["https://ocw.mit.edu/courses/6-829-computer-networks-fall-2002/pages/lecture-notes/"]

def connect_db():
    global collection
    if collection is None:
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        client = MongoClient(MONGO_URI)
        db = client["crawler_db"]
        collection = db["results"]


@app.get("/")
def home():
    return {"status": "I'm up!"}

@app.get("/get_urls/{worker_id}")
def get_urls(worker_id='worker0'):
    if worker_id == 'worker1':
        return {"urls": ARXIV_URLS}
    elif worker_id == 'worker2':
        return {"urls": MIT_URLS}
    else:
        return {"error": "Worker not configured!"}

@app.post("/post_results/data")
def post_results(data=Body(...)):
    print(f"Received {len(data)} results")
    # Store in MongoDB
    connect_db()
    if data:
        collection.insert_many(data)
    return {"status": "ok", "inserted_count": len(data)}
