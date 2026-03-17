"""YouTube からテニス関連動画情報を収集する"""
import requests
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import YOUTUBE_API_KEY, YOUTUBE_QUERIES, MAX_YOUTUBE_VIDEOS


def fetch_youtube_videos(query: str, api_key: str) -> list[dict]:
    """YouTube Data API v3 で動画を検索する"""
    if not api_key:
        return [{"title": "YouTube API キー未設定", "description": "", "url": "", "query": query}]

    results = []
    try:
        # 過去24時間以内の動画に絞る
        published_after = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "publishedAfter": published_after,
            "maxResults": MAX_YOUTUBE_VIDEOS,
            "key": api_key,
            "relevanceLanguage": "ja",
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            results.append({
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:200],
                "channel": snippet.get("channelTitle", ""),
                "published": snippet.get("publishedAt", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "query": query,
            })

    except Exception as e:
        results.append({
            "title": f"YouTube 取得エラー ({query})",
            "description": str(e),
            "url": "",
            "query": query,
        })

    return results


def collect() -> dict:
    """YouTube テニス動画情報を収集する"""
    all_videos = []
    seen_urls = set()

    for query in YOUTUBE_QUERIES:
        videos = fetch_youtube_videos(query, YOUTUBE_API_KEY)
        for video in videos:
            url = video.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_videos.append(video)
            elif not url:
                all_videos.append(video)

    return {
        "category": "YouTube テニス動画",
        "collected_at": datetime.now().isoformat(),
        "items": all_videos[:MAX_YOUTUBE_VIDEOS * 2],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
