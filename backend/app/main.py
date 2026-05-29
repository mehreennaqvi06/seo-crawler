from fastapi import FastAPI
from app.crawler import crawl_site

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