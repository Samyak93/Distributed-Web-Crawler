from fastapi import FastAPI, Body

app = FastAPI()

ARXIV_URLS = ["https://arxiv.org/search/cs?query=Computer+Network&searchtype=all&abstracts=show&order=-announced_date_first&size=50"]
MIT_URLS = ["https://ocw.mit.edu/courses/6-829-computer-networks-fall-2002/pages/lecture-notes/"]

@app.get("/")
def home():
    return {"status": "I'm up!"}

@app.get("/get_urls/{worker_id}")
def get_urls(worker_id = 'worker0'):
    if worker_id == 'worker1':
        return {"urls": ARXIV_URLS}
    elif worker_id == 'worker2':
        return {"urls": MIT_URLS}
    else:
        return {"error": "Worker not configured!", "urls": []}

@app.post("/post_results/data")
def post_results(data = Body(...)):
    print("\nReceived results:")
    for item in data:
        print(item)