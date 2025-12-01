
  # Distributed Web Crawler

  This project implements a **Distributed Web Crawler** for **website content integrity verification**.
  It is built using **Python**, **FastAPI**, and **Docker**, with results stored in **MongoDB**.
  The system uses a **coordinator–worker architecture**, allowing multiple crawler nodes to fetch URLs in parallel, compute MD5 hashes of HTML/PDF resources, and report results to a central orchestrator.

  ---

  ## Project Structure

      Orchestrator/
      ├── app.py            # FastAPI orchestrator assigning URLs and collecting results
      └── requirements.txt  # Python dependencies for orchestrator
      Worker/
      ├── worker.py         # Async web crawler computing MD5 hashes
      ├── config.py         # Configuration values for workers
      └── requirements.txt  # Python dependencies for workers
      docker-compose.yml    # Docker orchestration for orchestrator, workers, and MongoDB
      docs/                 # Sphinx-generated documentation
      README.md             # This documentation

  ---

  ## Requirements

  - Python 3.11
  - Docker 24+
  - MongoDB 6.0
  - Python Libraries:
    - fastapi
    - uvicorn
    - pymongo
    - requests
    - beautifulsoup4

  Install dependencies:

      pip install -r Worker/requirements.txt
      pip install -r Orchestrator/requirements.txt

  Start containers:

      docker-compose up --build

  ---

  ## How to Run

NOTE: Add Login Credentials for a Quanta Magazine profile in the config.py file if needed. Currently, an account is already provided. Create an account [here](https://www.quantamagazine.org/) to test with your own custom bookmarks.

  ### Start the System

      docker-compose up --build

  ### Fetch URLs (Worker)

      GET /get_urls/worker1
      GET /get_urls/worker2

  ### Post Crawl Results

      POST /post_results/data
      Body: [{"url": "...", "file": "...", "md5": "...", "status": "success"}]

  ### Verify Results in MongoDB

      docker exec -it mongo mongo
      > use crawler_db
      > db.results.find().pretty()

  ---

  ## How It Works

  1. Orchestrator:
     - Exposes a batch of URLs to each worker node.
     - Receives crawl results from workers via REST API.
     - Stores results in MongoDB for historical comparison.

  2. Workers:
     - Run as Docker containers.
     - Crawl URLs using the request library.
     - Uses beautiful soup to parse the HTML.
     - Logs into websites and fetches user-specific information.
     - Compute MD5 hashes of HTML pages or PDFs.
     - Send results back to the orchestrator.

  ---

  ## Key Features

  - Distributed Crawling: Multiple workers fetch URLs concurrently
  - MD5 Hashing: Detects content changes in HTML/PDF resources
  - REST API Communication: Workers post results to the orchestrator
  - Dockerized Deployment: Orchestrator, workers, and MongoDB run in containers
  - Scalability: Add more workers to increase crawling capacity
  - User authentication: Workers can log into websites using user credentials

  ---

  ## Sample Output

  - Worker crawling Arxiv PDFs – 50 links fetched.
  - Worker crawling MIT lecture notes – 21 PDFs and pages.
  - Worker crawling Quanta Magazine - 15 articles fetched.
  - Orchestrator received 71 total results.
  - MongoDB stores results in crawler_db.results with MD5 hashes:

      {
        _id: ObjectId('...'),
        url: 'https://ocw.mit.edu/.../lecture1.pdf',
        file: 'mit_pdfs/lecture1.pdf',
        md5: 'abc123...',
        status: 'success'
      }

  ---

  ## Conclusion

  The Distributed Web Crawler provides:

  - Parallel crawling using Dockerized worker nodes
  - Login capabilities by using the authentication token
  - Content integrity verification with MD5 hashes
  - REST API orchestration and inter-container communication
  - Persistent storage in MongoDB for historical monitoring

  This modular framework can be extended for **periodic monitoring**, **self-healing**, or **anomaly detection** in web content.
