"""Gemini API を使って収集したテニス情報を要約・レポート生成する"""
import json
from datetime import datetime

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL


def _build_prompt(data: dict) -> str:
    """収集データを Gemini へのプロンプトに変換する"""
    today = datetime.now().strftime("%Y年%m月%d日")

    sections = []

    match_items = data.get("試合結果・ランキング", {}).get("items", [])
    if match_items:
        sections.append("## 試合結果・ランキング情報")
        for item in match_items[:10]:
            content = item.get("content") or item.get("title", "")
            url = item.get("url", "")
            if content:
                line = f"- {content[:300]}"
                if url:
                    line += f"\n  URL: {url}"
                sections.append(line)

    news_items = data.get("テニスニュース", {}).get("items", [])
    if news_items:
        sections.append("\n## 最新ニュース")
        for item in news_items[:8]:
            title = item.get("title", "")
            url = item.get("link", "") or item.get("url", "")
            if title:
                line = f"- {title}"
                if url:
                    line += f"\n  URL: {url}"
                sections.append(line)

    paper_items = data.get("テニス論文・研究", {}).get("items", [])
    if paper_items:
        sections.append("\n## 論文・研究")
        for item in paper_items[:5]:
            title = item.get("title", "")
            journal = item.get("journal", "")
            url = item.get("link", "")
            if title:
                line = f"- {title}" + (f" ({journal})" if journal else "")
                if url:
                    line += f"\n  URL: {url}"
                sections.append(line)

    yt_items = data.get("YouTube テニス動画", {}).get("items", [])
    if yt_items:
        sections.append("\n## YouTube 動画")
        for item in yt_items[:5]:
            title = item.get("title", "")
            url = item.get("url", "")
            if title:
                line = f"- {title}"
                if url:
                    line += f"\n  URL: {url}"
                sections.append(line)

    raw_info = "\n".join(sections) if sections else "本日の情報を取得できませんでした。"

    return f"""あなたはプロのテニスコーチ向けモーニングレポートを作成するアシスタントです。
以下の収集情報（{today}）をもとに、テニスコーチが朝一番に読むための簡潔で実用的なレポートを日本語で作成してください。

【収集情報】
{raw_info}

【レポート作成の要件】
- LINEで送信するため、合計1500文字以内に収めること
- 絵文字を適度に使い読みやすくすること
- 各セクションは箇条書きで簡潔にまとめること
- URLはそのまま記載すること（短縮しない）
- コーチとして特に注目すべき情報にはコメントを添えること
- セクション構成: 試合結果・ランキング → ニュース → 研究トピック → YouTube → 本日のまとめ（1〜2行）

レポート本文のみを出力してください（前置きや説明は不要）。"""


def generate_report(data: dict) -> str:
    """Gemini API を使ってレポートを生成する。失敗時はフォールバック。"""
    if not GEMINI_API_KEY:
        print("[警告] GEMINI_API_KEY が未設定のためフォールバックを使用します")
        return _fallback_report(data)

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        prompt = _build_prompt(data)
        print(f"[Gemini] {GEMINI_MODEL} でレポートを生成中...")

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1200,
            ),
        )

        report = response.text.strip()
        print("[Gemini] レポート生成完了")
        return report

    except Exception as e:
        print(f"[Gemini] エラーが発生したためフォールバックを使用します: {e}")
        return _fallback_report(data)


def _fallback_report(data: dict) -> str:
    """Gemini が使えない場合のシンプルなフォーマッタ"""
    today = datetime.now().strftime("%Y年%m月%d日")
    lines = [f"🎾 テニス モーニングレポート {today}\n"]

    match_items = data.get("試合結果・ランキング", {}).get("items", [])
    if match_items:
        lines.append("📊 試合結果・ランキング")
        for item in match_items[:5]:
            content = item.get("content") or item.get("title", "")
            url = item.get("url", "")
            if content:
                lines.append(f"・{content[:200]}")
                if url:
                    lines.append(f"  {url}")
        lines.append("")

    news_items = data.get("テニスニュース", {}).get("items", [])
    if news_items:
        lines.append("📰 最新ニュース")
        for item in news_items[:5]:
            title = item.get("title", "")
            url = item.get("link", "") or item.get("url", "")
            if title:
                lines.append(f"・{title}")
                if url:
                    lines.append(f"  {url}")
        lines.append("")

    paper_items = data.get("テニス論文・研究", {}).get("items", [])
    if paper_items:
        lines.append("🔬 論文・研究")
        for item in paper_items[:3]:
            title = item.get("title", "")
            journal = item.get("journal", "")
            url = item.get("link", "")
            if title:
                lines.append(f"・{title}" + (f" ({journal})" if journal else ""))
                if url:
                    lines.append(f"  {url}")
        lines.append("")

    yt_items = data.get("YouTube テニス動画", {}).get("items", [])
    if yt_items:
        lines.append("▶️ YouTube 注目動画")
        for item in yt_items[:3]:
            title = item.get("title", "")
            url = item.get("url", "")
            if title and url:
                lines.append(f"・{title}")
                lines.append(f"  {url}")
        lines.append("")

    if len(lines) == 1:
        lines.append("本日の情報を取得できませんでした。")

    return "\n".join(lines)
