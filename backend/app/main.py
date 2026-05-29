from fastapi import FastAPI
from app.crawler import crawl_site

jobs = {}
next_job_id = 1

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

    pages = crawl_site(url, page_limit=limit)

    job = {
        "job_id": next_job_id,
        "status": "completed",
        "pages_crawled": len(pages),
        "pages": pages
    }

    jobs[next_job_id] = job

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