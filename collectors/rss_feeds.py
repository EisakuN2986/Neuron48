"""テニスニュースの RSS フィードを収集する"""
import feedparser
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RSS_FEEDS, MAX_NEWS_ITEMS


def fetch_feed(url: str) -> list[dict]:
    """1つの RSS フィードを取得してパースする"""
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:MAX_NEWS_ITEMS]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")
            published = entry.get("published", "")

            # HTML タグを除去
            import re
            summary = re.sub(r"<[^>]+>", "", summary).strip()
            summary = summary[:300] if summary else ""

            if title:
                items.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published,
                    "source_url": url,
                })
    except Exception as e:
        items.append({
            "title": f"フィード取得エラー ({url})",
            "summary": str(e),
            "link": "",
            "published": "",
            "source_url": url,
        })
    return items


def collect() -> dict:
    """全 RSS フィードを収集する"""
    all_items = []
    for feed_url in RSS_FEEDS:
        all_items.extend(fetch_feed(feed_url))

    # 日付で並べ替え (取得できた場合のみ)
    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)

    return {
        "category": "テニスニュース",
        "collected_at": datetime.now().isoformat(),
        "items": all_items[:MAX_NEWS_ITEMS * 2],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
