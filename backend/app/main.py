from fastapi import FastAPI
from app.crawler import crawl_site

jobs = {}
next_job_id = 1
job_queue = []

app = FastAPI()

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

    job = {
    "job_id": next_job_id,
    "status": "queued",
    "url": url,
    "limit": limit,
    "pages": []
}

    jobs[next_job_id] = job
    job_queue.append(next_job_id)

    next_job_id += 1

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

    pages = crawl_site(
        job["url"],
        page_limit=job["limit"]
    )

    job["status"] = "completed"
    job["pages"] = pages
    job["pages_crawled"] = len(pages)

    return job