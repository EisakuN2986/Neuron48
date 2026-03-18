"""テニス情報自動収集 & モーニングレポート生成のメインスクリプト"""
import json
import os
import sys
from datetime import datetime

from config import DATA_DIR
from collectors import atp_wta, rss_feeds, scholar, youtube
from processor.summarizer import generate_report
from notifier.line_messaging import send_report


def collect_all() -> dict:
    """全カテゴリの情報を収集する"""
    print("[1/4] ATP/WTA 試合結果・ランキングを収集中...")
    match_data = atp_wta.collect()

    print("[2/4] テニスニュース (RSS) を収集中...")
    news_data = rss_feeds.collect()

    print("[3/4] 論文・研究情報 (PubMed) を収集中...")
    paper_data = scholar.collect()

    print("[4/4] YouTube テニス動画情報を収集中...")
    yt_data = youtube.collect()

    return {
        match_data["category"]: match_data,
        news_data["category"]: news_data,
        paper_data["category"]: paper_data,
        yt_data["category"]: yt_data,
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


def main():
    print("=" * 50)
    print(f"🎾 テニス情報収集 開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 情報収集
    collected_data = collect_all()

    # データ保存
    save_path = save_data(collected_data)

    # Gemini API でレポート生成
    print("\n[Gemini API] モーニングレポートを生成中...")
    report = generate_report(collected_data)

    # レポートをファイルにも保存
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(DATA_DIR, f"{today}_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[保存] レポートを保存しました: {report_path}")

    # LINE で送信
    print("\n[LINE] レポートを送信中...")
    header = f"🎾 テニス モーニングレポート {today}\n{'=' * 30}\n\n"
    send_report(header + report)

    print("\n" + "=" * 50)
    print("✅ 完了!")
    print("=" * 50)

    # コンソールにもレポートを表示
    print("\n--- 生成されたレポート ---\n")
    print(report)


if __name__ == "__main__":
    main()
