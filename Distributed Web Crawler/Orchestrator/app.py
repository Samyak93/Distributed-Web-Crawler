"""
CSCI-651 Project: Distributed Web Crawler

Implementing a Distributed Web Crawler to crawl different
websites, download all related files, calculate MD5 hash
and send it back to the server.
Uses Docker Container to host the server and MongoDB.
"""

from fastapi import FastAPI, Body
from pymongo import MongoClient
import os

app = FastAPI()

collection = None

ARXIV_URLS = ["https://arxiv.org/search/cs?query=Computer+Network&searchtype=all&abstracts=show&order=-announced_date_first&size=50"]
MIT_URLS = ["https://ocw.mit.edu/courses/6-829-computer-networks-fall-2002/pages/lecture-notes/"]

def connect_db():
    """
    Method to lazily connect to DB, only 1 connection

    :return: DB connection to the collection
    """
    global collection
    if collection is None:
        MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
        client = MongoClient(MONGO_URI)
        db = client["crawler_db"]
        collection = db["results"]


@app.get("/")
def home():
    """
    Basic method to check if server is up during healthcheck

    :return: JSON response indicating server is live.
    """
    return {"status": "I'm up!"}

@app.get("/get_urls/{worker_id}")
def get_urls(worker_id='worker0'):
    """
    Method to distribute URLs to workers based on the worker ids.

    :param worker_id: ID of the worker requesting the URLs to crawl.
    :return: List of URLs for current worker to crawl.
    """
    if worker_id == 'worker1':
        return {"urls": ARXIV_URLS}
    elif worker_id == 'worker2':
        return {"urls": MIT_URLS}
    else:
        return {"error": "Worker not configured!"}

@app.post("/post_results/data")
def post_results(data=Body(...)):
    """
    Method to receive results from worker and post it into MongoDB.

    :param data: JSON dictionary of {url, file, md5, status} of all downloaded files received from workers.
    :return: None
    """
    print(f"Received {len(data)} results")
    # Store in MongoDB
    connect_db()
    if data:
        collection.insert_many(data)
    return {"status": "ok", "inserted_count": len(data)}
