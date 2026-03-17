"""収集したテニス情報をそのままLINE送信用にフォーマットする"""
from datetime import datetime


def generate_report(data: dict) -> str:
    """収集データをLINE送信用テキストにフォーマットする"""
    today = datetime.now().strftime("%Y年%m月%d日")
    lines = [f"🎾 テニス モーニングレポート {today}\n"]

    # 試合結果・ランキング
    match_data = data.get("試合結果・ランキング", {})
    if match_data.get("items"):
        lines.append("📊 試合結果・ランキング")
        seen_urls = set()
        for item in match_data["items"]:
            content = item.get("content") or item.get("title", "")
            url = item.get("url", "")
            if content:
                lines.append(f"・{content[:200]}")
                if url and url not in seen_urls:
                    lines.append(f"  {url}")
                    seen_urls.add(url)
        lines.append("")

    # ニュース
    news_data = data.get("テニスニュース", {})
    if news_data.get("items"):
        lines.append("📰 最新ニュース")
        for item in news_data["items"][:5]:
            title = item.get("title", "")
            url = item.get("link", "") or item.get("url", "")
            if title:
                lines.append(f"・{title}")
                if url:
                    lines.append(f"  {url}")
        lines.append("")

    # 論文
    paper_data = data.get("テニス論文・研究", {})
    if paper_data.get("items"):
        lines.append("🔬 論文・研究")
        for item in paper_data["items"][:3]:
            title = item.get("title", "")
            journal = item.get("journal", "")
            url = item.get("link", "")
            if title:
                lines.append(f"・{title}" + (f" ({journal})" if journal else ""))
                if url:
                    lines.append(f"  {url}")
        lines.append("")

    # YouTube
    youtube_data = data.get("YouTube テニス動画", {})
    if youtube_data.get("items"):
        lines.append("▶️ YouTube 注目動画")
        for item in youtube_data["items"][:3]:
            title = item.get("title", "")
            url = item.get("url", "")
            if title and url:
                lines.append(f"・{title}")
                lines.append(f"  {url}")
        lines.append("")

    if len(lines) == 1:
        lines.append("本日の情報を取得できませんでした。")

    return "\n".join(lines)
