"""テニス情報自動収集 & モーニングレポート生成のメインスクリプト"""
import json
import os
from datetime import datetime

from config import DATA_DIR
from collectors import atp_wta, wta, rss_feeds, scholar, youtube, marketing_news, marketing_research
from processor.summarizer import generate_report
from processor.html_generator import generate_html
from notifier.line_messaging import send_report


GITHUB_PAGES_URL = "https://eisakun2986.github.io/Neuron48"
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
REPORTS_DIR = os.path.join(DOCS_DIR, "reports")


def collect_all() -> dict:
    """全カテゴリの情報を収集する"""
    print("[1/7] ATP 試合結果・ランキングを収集中...")
    match_data = atp_wta.collect()

    print("[2/7] WTA 試合結果・ランキングを収集中...")
    wta_data = wta.collect()

    print("[3/7] テニスニュース (RSS) を収集中...")
    news_data = rss_feeds.collect()

    print("[4/7] 論文・研究情報 (PubMed) を収集中...")
    paper_data = scholar.collect()

    print("[5/7] YouTube テニス動画情報を収集中...")
    yt_data = youtube.collect()

    print("[6/7] マーケティングニュース (海外一次情報) を収集中...")
    mkt_news_data = marketing_news.collect()

    print("[7/7] マーケティング論文・研究 (Semantic Scholar) を収集中...")
    mkt_research_data = marketing_research.collect()

    return {
        match_data["category"]: match_data,
        wta_data["category"]: wta_data,
        news_data["category"]: news_data,
        paper_data["category"]: paper_data,
        yt_data["category"]: yt_data,
        mkt_news_data["category"]: mkt_news_data,
        mkt_research_data["category"]: mkt_research_data,
        "collected_at": datetime.now().isoformat(),
    }


def save_data(data: dict) -> str:
    """収集データを JSON ファイルとして保存する"""
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(DATA_DIR, f"{today}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[保存] データを保存しました: {filepath}")
    return filepath


def save_html_report(report_text: str, date_str: str) -> str:
    """HTML レポートを docs/ に保存して GitHub Pages で公開する"""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    date_label = datetime.now().strftime("%Y年%m月%d日")
    html_content = generate_html(report_text, date_label)

    # 日付別アーカイブ
    report_path = os.path.join(REPORTS_DIR, f"{date_str}.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # index.html（常に最新レポートを表示）
    index_path = os.path.join(DOCS_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[HTML] レポートを保存しました: {report_path}")
    print(f"[HTML] index.html を更新しました")
    return f"{GITHUB_PAGES_URL}/reports/{date_str}.html"


def main():
    print("=" * 50)
    print(f"🎾 テニス情報収集 開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    today = datetime.now().strftime("%Y-%m-%d")

    # 情報収集
    collected_data = collect_all()

    # JSON データ保存
    save_data(collected_data)

    # Gemini API でレポート生成
    print("\n[Gemini API] モーニングレポートを生成中...")
    report = generate_report(collected_data)

    # Markdown レポート保存
    report_path = os.path.join(DATA_DIR, f"{today}_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[保存] Markdownレポートを保存しました: {report_path}")

    # HTML レポート生成 & docs/ に保存（GitHub Pages で公開）
    print("\n[HTML] GitHub Pages 用レポートを生成中...")
    save_html_report(report, today)

    # LINE に短い通知 + URL を送信
    print("\n[LINE] 通知を送信中...")
    line_message = (
        f"🎾 テニス朝刊 {today}\n"
        f"今日のレポートが届きました👇\n"
        f"{GITHUB_PAGES_URL}"
    )
    send_report(line_message)

    print("\n" + "=" * 50)
    print("✅ 完了!")
    print(f"📄 レポートURL: {GITHUB_PAGES_URL}")
    print("=" * 50)

    print("\n--- 生成されたレポート ---\n")
    print(report)


if __name__ == "__main__":
    main()
