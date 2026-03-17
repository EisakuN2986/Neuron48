"""Google Scholar / PubMed からテニス関連論文情報を収集する"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import SCHOLAR_QUERIES, MAX_PAPERS


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_pubmed(query: str) -> list[dict]:
    """PubMed から論文を検索する (無料APIを使用)"""
    results = []
    try:
        # PubMed Entrez API (無料・APIキー不要)
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": MAX_PAPERS,
            "sort": "date",
            "retmode": "json",
        }
        resp = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return results

        # 論文詳細を取得
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        }
        time.sleep(0.5)  # API レート制限
        fetch_resp = requests.get(fetch_url, params=fetch_params, headers=HEADERS, timeout=15)
        fetch_resp.raise_for_status()
        fetch_data = fetch_resp.json()

        for pmid in ids:
            article = fetch_data.get("result", {}).get(pmid, {})
            title = article.get("title", "")
            authors = article.get("authors", [])
            author_str = ", ".join(a.get("name", "") for a in authors[:3])
            pub_date = article.get("pubdate", "")
            source = article.get("source", "")

            if title:
                results.append({
                    "title": title,
                    "authors": author_str,
                    "journal": source,
                    "published": pub_date,
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "query": query,
                })

    except Exception as e:
        results.append({
            "title": f"PubMed 取得エラー ({query})",
            "authors": "",
            "journal": "",
            "published": "",
            "link": "",
            "query": query,
            "error": str(e),
        })

    return results


def collect() -> dict:
    """全クエリで論文情報を収集する"""
    all_papers = []
    seen_titles = set()

    for query in SCHOLAR_QUERIES:
        papers = fetch_pubmed(query)
        for paper in papers:
            title = paper.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_papers.append(paper)
        time.sleep(1)  # API レート制限

    return {
        "category": "テニス論文・研究",
        "collected_at": datetime.now().isoformat(),
        "items": all_papers[:MAX_PAPERS * 2],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
