"""ATP/WTA の最新試合結果・ランキングを収集する"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MAX_MATCH_RESULTS


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_atp_results() -> list[dict]:
    """ATP の最新試合結果を取得する"""
    results = []
    try:
        url = "https://www.atptour.com/en/scores/current"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # 試合結果を抽出
        match_cards = soup.select(".match-cta, .scores-item, [class*='score']")[:MAX_MATCH_RESULTS]
        for card in match_cards:
            text = card.get_text(separator=" ", strip=True)
            if text:
                results.append({"source": "ATP", "content": text[:300], "url": url})

        if not results:
            # フォールバック: ページの主要テキストから抽出
            main = soup.select_one("main, #scores, .scores")
            if main:
                text = main.get_text(separator="\n", strip=True)
                lines = [l for l in text.split("\n") if l.strip()][:MAX_MATCH_RESULTS * 3]
                results.append({"source": "ATP", "content": "\n".join(lines)[:500], "url": url})

    except Exception as e:
        results.append({"source": "ATP", "content": f"取得エラー: {e}"})

    return results


def get_atp_rankings() -> list[dict]:
    """ATP ランキング Top 10 を取得する"""
    results = []
    try:
        url = "https://www.atptour.com/en/rankings/singles"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # ランキングテーブル行を抽出
        rows = soup.select("table tbody tr, .rankings-table tr")[:10]
        ranking_lines = []
        for row in rows:
            cols = row.find_all(["td", "th"])
            if cols:
                line = " | ".join(c.get_text(strip=True) for c in cols[:4])
                if line.strip():
                    ranking_lines.append(line)

        if ranking_lines:
            results.append({
                "source": "ATP Rankings",
                "content": "\n".join(ranking_lines)
            })
        else:
            results.append({"source": "ATP Rankings", "content": "ランキング情報を取得できませんでした"})

    except Exception as e:
        results.append({"source": "ATP Rankings", "content": f"取得エラー: {e}"})

    return results


def collect() -> dict:
    """ATP/WTA 情報をまとめて収集する"""
    return {
        "category": "試合結果・ランキング",
        "collected_at": datetime.now().isoformat(),
        "items": get_atp_results() + get_atp_rankings(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
