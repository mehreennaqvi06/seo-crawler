import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from crawler import crawl_site
from database import (
    create_job_db,
    update_job_db,
    save_page_db,
    get_metrics_db,
    get_all_jobs_db
)

jobs = {}
next_job_id = 1
job_queue = []

crawl_rules = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Crawler API running"}

@app.get("/test")
def test():
    return crawl_site(
        "https://example.com",
        page_limit=5
    )

@app.get("/crawl")
def crawl(url: str, limit: int = 5):
    return crawl_site(
        url,
        page_limit=limit
    )

@app.post("/jobs")
def create_job(url: str, limit: int = 5):

    global next_job_id

    db_job_id = create_job_db(url, "queued")

    job = {
        "job_id": db_job_id,
        "status": "queued",
        "url": url,
        "limit": limit,
        "pages": [],
        "allowed": [],
        "disallowed": []
    }

    jobs[db_job_id] = job
    job_queue.append(db_job_id)

    return job

@app.get("/jobs/{job_id}")
def get_job(job_id: int):
    return jobs.get(job_id)


@app.get("/jobs/{job_id}/pages")
def get_pages(job_id: int):
    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    return job["pages"]


@app.post("/process-next-job")
def process_next_job():

    if not job_queue:
        return {"message": "No jobs in queue"}

    job_id = job_queue.pop(0)

    job = jobs[job_id]
    
    job["status"] = "running"

    start_time = time.time()
    
    pages = crawl_site(
        job["url"],
        page_limit=job["limit"]
    )

    job["status"] = "completed"
    
    for page in pages["pages"]:

        save_page_db(
            job_id,
            page["url"],
            page["title"],
            page["h1"],
            page["meta_description"],
            page["status_code"]
        )
    job["allowed"] = pages["allowed"]
    job["disallowed"] = pages["disallowed"]
    
    job["pages"] = pages["pages"]
    
    job["pages_crawled"] = len(pages["pages"])
    
    crawl_duration = time.time() - start_time
    
    update_job_db(
        job_id,
        "completed",
        len(pages["pages"]),
        crawl_duration,
        pages["error_count"],
        pages["retry_count"]
    )

    return job

@app.get("/robots-rules")
def robots_rules(url: str):

    from app.crawler import get_disallowed_paths

    return get_disallowed_paths(url)

@app.get("/metrics")
def get_metrics():
    return get_metrics_db()

@app.get("/jobs")
def get_jobs():
    return get_all_jobs_db()