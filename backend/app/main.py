import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.crawler import crawl_site, check_sitemap
from collections import Counter
from fastapi.responses import FileResponse
import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from app.database import (
    create_job_db,
    update_job_db,
    save_page_db,
    get_metrics_db,
    get_all_jobs_db,
    get_job_history_db
)

jobs = {}
next_job_id = 1
job_queue = []

crawl_rules = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
   allow_origins=["*"],
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

@app.get("/sitemap")
def get_sitemap(url: str):
    return check_sitemap(url)

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
    
    process_next_job()

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

@app.get("/jobs/{job_id}/seo-score")
def get_seo_score(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    total_score = 0
    issues = []

    for page in job["pages"]:

        score = 0

        if page["title"]:
            score += 25
        else:
            issues.append(f"Missing title: {page['url']}")

        if page["h1"]:
            score += 25
        else:
            issues.append(f"Missing H1: {page['url']}")

        if page["meta_description"]:
            score += 25
        else:
            issues.append(
                f"Missing meta description: {page['url']}"
            )

        if page["status_code"] == 200:
            score += 25

        total_score += score

    average_score = (
        total_score / len(job["pages"])
        if job["pages"]
        else 0
    )

    return {
        "seo_score": round(average_score, 2),
        "issues": issues
    }
    
@app.get("/jobs/{job_id}/broken-links")
def get_broken_links(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    broken_links = []

    for page in job["pages"]:

        if page["status_code"] >= 400:

            broken_links.append({
                "url": page["url"],
                "status_code": page["status_code"]
            })

    return {
        "broken_links": broken_links,
        "count": len(broken_links)
    }
    
@app.get("/jobs/{job_id}/images")
def get_image_analysis(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    image_report = []

    for page in job["pages"]:

        image_report.append({
            "url": page["url"],
            "total_images": page.get("total_images", 0),
            "missing_alt": page.get("missing_alt", 0)
        })

    return {
        "pages": image_report
    }

@app.get("/jobs/{job_id}/keywords")
def get_keywords(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    words = []

    for page in job["pages"]:

        text = (
            page["title"] + " " +
            page["h1"] + " " +
            page["meta_description"]
        )

        for word in text.lower().split():

            word = word.strip(".,!?()[]{}:;\"'")

            if len(word) > 3:
                words.append(word)

    keyword_counts = Counter(words)

    top_keywords = keyword_counts.most_common(20)

    return {
        "keywords": [
            {
                "keyword": keyword,
                "count": count
            }
            for keyword, count in top_keywords
        ]
    }

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

@app.get("/jobs/{job_id}/robots")
def get_robots(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    return {
        "allowed": job["allowed"],
        "disallowed": job["disallowed"]
    }

@app.get("/jobs/{job_id}/sitemap-check")
def sitemap_check(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    return check_sitemap(job["url"])

@app.get("/metrics")
def get_metrics():
    return get_metrics_db()

@app.get("/jobs")
def get_jobs():
    return get_all_jobs_db()

@app.get("/history")
def get_history():
    return get_all_jobs_db()

@app.get("/history/{job_id}")
def get_history_job(job_id: int):

    job = get_job_history_db(job_id)

    if not job:
        return {"error": "Job not found"}

    return job

@app.get("/jobs/{job_id}/export/csv")
def export_csv(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    filename = f"crawl_{job_id}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "URL",
            "Title",
            "H1",
            "Meta Description",
            "Status Code"
        ])

        for page in job["pages"]:
            writer.writerow([
                page["url"],
                page["title"],
                page["h1"],
                page["meta_description"],
                page["status_code"]
            ])

    return FileResponse(
        filename,
        media_type="text/csv",
        filename=filename
    )

@app.get("/jobs/{job_id}/export/pdf")
def export_pdf(job_id: int):

    job = jobs.get(job_id)

    if not job:
        return {"error": "Job not found"}

    filename = f"crawl_{job_id}.pdf"

    pdf = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            f"Crawl Report - Job {job_id}",
            styles["Title"]
        )
    )

    content.append(
        Paragraph(
            f"URL: {job['url']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Pages Crawled: {len(job['pages'])}",
            styles["Normal"]
        )
    )

    for page in job["pages"]:

        content.append(
            Paragraph(
                f"""
                URL: {page['url']}<br/>
                Title: {page['title']}<br/>
                H1: {page['h1']}<br/>
                Status: {page['status_code']}<br/><br/>
                """,
                styles["BodyText"]
            )
        )

    pdf.build(content)

    return FileResponse(
        filename,
        media_type="application/pdf",
        filename=filename
    )