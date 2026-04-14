"""Semantic Scholar API からマーケティング関連論文を収集する (無料・APIキー不要)"""
import requests
from datetime import datetime
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MARKETING_RESEARCH_QUERIES, MAX_MARKETING_PAPERS

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,authors,year,abstract,externalIds,publicationVenue,openAccessPdf"
HEADERS = {"User-Agent": "Neuron48-MarketingBot/1.0"}


def fetch_papers(query: str) -> list[dict]:
    """Semantic Scholar から論文を検索する"""
    results = []
    try:
        params = {
            "query": query,
            "limit": MAX_MARKETING_PAPERS,
            "fields": FIELDS,
            "sort": "relevance",
        }
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        for paper in data.get("data", []):
            title = paper.get("title", "")
            if not title:
                continue

            authors = paper.get("authors", [])
            author_str = ", ".join(a.get("name", "") for a in authors[:3])
            year = str(paper.get("year", ""))
            abstract = (paper.get("abstract") or "")[:400]
            venue = (paper.get("publicationVenue") or {}).get("name", "")

            # DOI または Semantic Scholar の URL を使用
            ext_ids = paper.get("externalIds") or {}
            doi = ext_ids.get("DOI", "")
            paper_id = paper.get("paperId", "")
            link = (
                f"https://doi.org/{doi}" if doi
                else f"https://www.semanticscholar.org/paper/{paper_id}"
            )

            # オープンアクセスPDF
            oa = paper.get("openAccessPdf") or {}
            pdf_url = oa.get("url", "")

            results.append({
                "title": title,
                "authors": author_str,
                "journal": venue,
                "published": year,
                "abstract": abstract,
                "link": link,
                "pdf_url": pdf_url,
                "query": query,
            })

    except Exception as e:
        results.append({
            "title": f"Semantic Scholar 取得エラー ({query})",
            "authors": "",
            "journal": "",
            "published": "",
            "abstract": str(e),
            "link": "",
            "pdf_url": "",
            "query": query,
        })

    return results


def collect() -> dict:
    """全クエリでマーケティング論文を収集する"""
    all_papers = []
    seen_titles = set()

    for query in MARKETING_RESEARCH_QUERIES:
        papers = fetch_papers(query)
        for paper in papers:
            title = paper.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_papers.append(paper)
        time.sleep(1)  # API レート制限 (100 req/5min)

    return {
        "category": "マーケティング論文・研究",
        "collected_at": datetime.now().isoformat(),
        "items": all_papers[:MAX_MARKETING_PAPERS * 2],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
