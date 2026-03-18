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


def _fetch_abstracts(pmids: list[str]) -> dict[str, str]:
    """MEDLINE 形式でアブストラクトを一括取得する (PubMed 無料API)"""
    if not pmids:
        return {}
    try:
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db": "pubmed", "id": ",".join(pmids),
                    "rettype": "medline", "retmode": "text"},
            headers=HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        abstracts: dict[str, str] = {}
        current_pmid = ""
        ab_lines: list[str] = []
        in_ab = False
        for line in resp.text.splitlines():
            if line.startswith("PMID- "):
                if current_pmid and ab_lines:
                    abstracts[current_pmid] = " ".join(ab_lines)[:400]
                current_pmid = line[6:].strip()
                ab_lines = []
                in_ab = False
            elif line.startswith("AB  - "):
                in_ab = True
                ab_lines.append(line[6:].strip())
            elif in_ab and line.startswith("      "):
                ab_lines.append(line.strip())
            elif in_ab:
                in_ab = False
        if current_pmid and ab_lines:
            abstracts[current_pmid] = " ".join(ab_lines)[:400]
        return abstracts
    except Exception:
        return {}


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

        # 論文メタデータを取得
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

        # アブストラクトを一括取得
        time.sleep(0.5)
        abstracts = _fetch_abstracts(ids)

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
                    "abstract": abstracts.get(pmid, ""),
                    "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "query": query,
                })

    except Exception as e:
        results.append({
            "title": f"PubMed 取得エラー ({query})",
            "authors": "",
            "journal": "",
            "published": "",
            "abstract": "",
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
