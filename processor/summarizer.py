"""Gemini API を使って収集したテニス情報を要約・レポート生成する"""
import json
from datetime import datetime

import google.generativeai as genai

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_PAPERS


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
    sections.append("\n## 論文・研究（PubMed 1次情報 ※必ずレポートに含めること）")
    if paper_items:
        for item in paper_items[:MAX_PAPERS]:
            title = item.get("title", "")
            journal = item.get("journal", "")
            published = item.get("published", "")
            authors = item.get("authors", "")
            abstract = item.get("abstract", "")
            url = item.get("link", "")
            if title:
                meta = " | ".join(filter(None, [journal, published, authors]))
                line = f"- タイトル: {title}"
                if meta:
                    line += f"\n  掲載情報: {meta}"
                if abstract:
                    line += f"\n  アブストラクト抜粋: {abstract}"
                if url:
                    line += f"\n  URL: {url}"
                sections.append(line)
    else:
        sections.append("- （本日の論文データは取得できませんでした）")

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
以下の収集情報（{today}）をもとに、テニスコーチが朝一番に読むための実用的なレポートを作成してください。

【収集情報】
{raw_info}

【絶対に守るルール】
1. 出力はすべて日本語のみ。英語タイトル・英語文章は一字も英語のまま残さず、すべて自然な日本語に翻訳すること
2. 情報の優先順位：ATP・WTA・BBC・Tennis.com等の海外公式1次情報を最優先とし、日本語メディアの2次情報は補足に留める
3. 各ニュース・論文には情報ソース名を【ATP Tour】【WTA】【BBC Sport】【Tennis World】【PubMed】等の形式で必ず末尾に付けること
4. URLはそのまま記載すること（短縮しない）
5. 前置きや説明文は一切不要。レポート本文のみを出力すること

【セクション構成（この順番で、見出しも含めて必ず出力）】
① 📊 試合結果・ランキング
・主要試合結果と世界ランキング上位10名を日本語で記載
・ATP/WTAの公式情報を優先すること

② 📰 今日のニュース（海外1次情報を優先）
・英語記事タイトルは必ず日本語に翻訳して記載
・各項目末尾に【情報ソース名】を付ける
・URL を記載すること

③ 🔬 研究・論文トピック ★このセクションは絶対に省略しない★
・PubMedから取得した1次情報（英語原著論文）を必ず掲載する
・論文タイトルを自然な日本語に翻訳して記載（原題は不要）
・掲載誌名・発行年・著者名（3名まで）を併記する
・アブストラクトの要点を日本語で2〜3文に要約する
・テニスコーチングへの実践的活用ポイントを1文で明記する
・各項目末尾に【PubMed】を付け、URLを記載する
・取得できた論文はすべて掲載すること（情報が少なくても省略しない）

④ ▶️ 注目YouTube動画
・タイトルを日本語訳して紹介
・URL を記載すること

⑤ 💡 コーチへの示唆
・本日の情報を踏まえたコーチング・指導への具体的な示唆を3〜4文で述べる

⑥ ✅ 本日のまとめ
・1〜2行で締める"""


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
                max_output_tokens=4000,
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
