import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

def crawl_site(start_url, page_limit=5):

    queue = [start_url]
    base_domain = urlparse(start_url).netloc
    visited = set()
    results = []

    while queue and len(visited) < page_limit:

        current_url = queue.pop(0)

        if current_url in visited:
            continue

        try:
            response = httpx.get(current_url, timeout=10)

            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.title.string if soup.title else ""

            h1 = soup.find("h1")
            h1_text = h1.text.strip() if h1 else ""

            meta = soup.find(
                "meta",
                attrs={"name": "description"}
            )

            meta_desc = (
                meta["content"]
                if meta and "content" in meta.attrs
                else ""
            )

            results.append({
                "url": current_url,
                "title": title,
                "h1": h1_text,
                "meta_description": meta_desc,
                "status_code": response.status_code,
                "timestamp": datetime.utcnow().isoformat()
            })

            visited.add(current_url)

            links = soup.find_all("a")

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                if href.startswith("#"):
                    continue

                if href.startswith("mailto:"):
                    continue

                if href.startswith("javascript:"):
                    continue

                absolute_url = urljoin(current_url, href)

                link_domain = urlparse(
                    absolute_url
                ).netloc

                if link_domain != base_domain:
                    continue

                if absolute_url not in visited:
                    queue.append(absolute_url)

        except Exception:
            pass

    return results