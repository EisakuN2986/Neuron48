"""Claude API を使ってテニス情報を要約し、コーチング考察を生成する"""
import anthropic
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL


def _build_prompt(data: dict) -> str:
    """収集データからプロンプトを構築する"""
    today = datetime.now().strftime("%Y年%m月%d日")

    sections = []

    # 試合結果・ランキング
    match_data = data.get("試合結果・ランキング", {})
    if match_data.get("items"):
        content = "\n".join(
            item.get("content", item.get("title", "")) for item in match_data["items"]
        )
        sections.append(f"【試合結果・ランキング】\n{content}")

    # ニュース
    news_data = data.get("テニスニュース", {})
    if news_data.get("items"):
        news_lines = []
        for item in news_data["items"][:5]:
            title = item.get("title", "")
            summary = item.get("summary", "")
            if title:
                news_lines.append(f"- {title}: {summary[:150]}")
        sections.append(f"【テニスニュース】\n" + "\n".join(news_lines))

    # 論文
    paper_data = data.get("テニス論文・研究", {})
    if paper_data.get("items"):
        paper_lines = []
        for item in paper_data["items"][:3]:
            title = item.get("title", "")
            journal = item.get("journal", "")
            authors = item.get("authors", "")
            if title:
                paper_lines.append(f"- {title} ({journal}, {authors})")
        sections.append(f"【最新論文・研究】\n" + "\n".join(paper_lines))

    # YouTube
    youtube_data = data.get("YouTube テニス動画", {})
    if youtube_data.get("items"):
        yt_lines = []
        for item in youtube_data["items"][:3]:
            title = item.get("title", "")
            channel = item.get("channel", "")
            url = item.get("url", "")
            if title and url:
                yt_lines.append(f"- {title} ({channel}) {url}")
        if yt_lines:
            sections.append(f"【注目 YouTube 動画】\n" + "\n".join(yt_lines))

    raw_info = "\n\n".join(sections) if sections else "本日の情報収集データが取得できませんでした。"

    prompt = f"""あなたはプロテニスのコーチング専門家です。
本日({today})のテニス情報を分析し、コーチング視点のモーニングレポートを作成してください。

## 収集データ

{raw_info}

## 作成するレポートの構成

以下の構成で日本語のモーニングレポートを作成してください。LINEで送信するため、簡潔で読みやすいフォーマットにしてください。

1. **📊 本日の試合結果・ランキング動向** (簡潔に2-3行)
2. **📰 テニス最新ニュース** (重要トピック2-3件を箇条書き)
3. **🔬 研究・論文インサイト** (コーチングに活かせる知見を1-2件)
4. **🎯 今日のコーチングポイント「心技体」**
   - 心（メンタル）: 今日の情報から学べるメンタル強化のヒント
   - 技（技術）: 技術向上に活かせるポイント
   - 体（フィジカル）: コンディション・体力強化の観点

5. **💡 今日の一言（コーチング格言）**

情報が不足している項目はスキップし、利用可能な情報のみで生成してください。
全体を簡潔に、LINE メッセージとして読みやすい形式にしてください。"""

    return prompt


def generate_report(collected_data: dict) -> str:
    """Claude API でモーニングレポートを生成する"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = _build_prompt(collected_data)

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    except Exception as e:
        # フォールバック: API エラー時はデータをそのままフォーマット
        today = datetime.now().strftime("%Y年%m月%d日")
        return f"""🎾 テニス モーニングレポート {today}

⚠️ AI 要約の生成中にエラーが発生しました: {e}

収集した情報は data/ フォルダに保存されています。"""


if __name__ == "__main__":
    # テスト実行
    sample_data = {
        "テニスニュース": {
            "items": [
                {"title": "ジョコビッチが全豪オープン優勝", "summary": "圧倒的なパフォーマンスで10度目の優勝を果たした。"},
            ]
        }
    }
    print(generate_report(sample_data))
