"""海外マーケティング専門メディアの RSS フィードを収集する"""
import feedparser
import re
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MARKETING_RSS_FEEDS, MAX_MARKETING_NEWS_ITEMS


def fetch_feed(url: str) -> list[dict]:
    """1つの RSS フィードを取得してパースする"""
    items = []
    try:
        feed = feedparser.parse(url)
        source_name = feed.feed.get("title", url)
        for entry in feed.entries[:MAX_MARKETING_NEWS_ITEMS]:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            link = entry.get("link", "")
            published = entry.get("published", "")

            summary = re.sub(r"<[^>]+>", "", summary).strip()
            summary = summary[:300] if summary else ""

            if title:
                items.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published,
                    "source": source_name,
                    "source_url": url,
                })
    except Exception as e:
        items.append({
            "title": f"フィード取得エラー ({url})",
            "summary": str(e),
            "link": "",
            "published": "",
            "source": url,
            "source_url": url,
        })
    return items


def collect() -> dict:
    """全マーケティング RSS フィードを収集する"""
    all_items = []
    seen_titles = set()

    for feed_url in MARKETING_RSS_FEEDS:
        for item in fetch_feed(feed_url):
            title = item.get("title", "")
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_items.append(item)

    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)

    return {
        "category": "マーケティングニュース",
        "collected_at": datetime.now().isoformat(),
        "items": all_items[:MAX_MARKETING_NEWS_ITEMS * 2],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
