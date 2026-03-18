"""Gemini 生成レポートをモバイル対応 HTML に変換する"""
import re

URL_PATTERN = re.compile(r'https?://[^\s<>"]+')

# Gemini形式: ① 📊 ... / フォールバック形式: 📊 ...
SECTION_STARTS = ('①', '②', '③', '④', '⑤', '⑥',
                  '📊', '📰', '🔬', '▶️', '💡', '✅')

# タイトル行として無視するパターン
TITLE_PREFIXES = ('🎾',)


def _linkify(text: str) -> str:
    return URL_PATTERN.sub(
        lambda m: f'<a href="{m.group()}" target="_blank">{m.group()}</a>',
        text,
    )


def _parse_sections(report_text: str) -> list[tuple[str, list[str]]]:
    """レポートテキストをセクションのリストに分割する（両フォーマット対応）"""
    sections = []
    current_title = None
    current_items: list[str] = []

    for line in report_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        # メインタイトル行（🎾 テニス朝刊...）はスキップ
        if stripped.startswith(TITLE_PREFIXES) and current_title is None and not stripped.startswith('🎾 テニスの'):
            continue
        if stripped.startswith(SECTION_STARTS):
            if current_title is not None:
                sections.append((current_title, current_items[:]))
            current_title = stripped
            current_items = []
        else:
            if current_title is not None:
                current_items.append(stripped)

    if current_title is not None:
        sections.append((current_title, current_items[:]))

    return sections


def _build_card(title: str, items: list[str]) -> str:
    content_html = ''
    i = 0
    list_open = False

    while i < len(items):
        item = items[i]

        # URL 単独行（直前のリスト項目に紐づく）
        if item.startswith('http'):
            if list_open:
                # 直前の <li> に URL を付加
                content_html = content_html.rstrip('</li>') + (
                    f'<br><a class="url" href="{item}" target="_blank">{item}</a></li>'
                )
            else:
                content_html += f'<p><a class="url" href="{item}" target="_blank">{item}</a></p>'
            i += 1
            continue

        # 箇条書き
        if item.startswith(('・', '- ', '• ')):
            if not list_open:
                content_html += '<ul>'
                list_open = True
            body = re.sub(r'^[・\-• ]+', '', item).strip()
            content_html += f'<li>{_linkify(body)}</li>'
        else:
            if list_open:
                content_html += '</ul>'
                list_open = False
            content_html += f'<p>{_linkify(item)}</p>'

        i += 1

    if list_open:
        content_html += '</ul>'

    return f'<div class="card"><h2>{title}</h2>{content_html}</div>'


def generate_html(report_text: str, date_str: str) -> str:
    """レポートテキストから完全な HTML ページを生成する"""
    sections = _parse_sections(report_text)

    if sections:
        cards_html = '\n'.join(_build_card(t, items) for t, items in sections)
    else:
        # セクション分割できなかった場合はそのまま表示
        fallback = _linkify(report_text.replace('\n', '<br>'))
        cards_html = f'<div class="card"><p>{fallback}</p></div>'

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🎾 テニス朝刊 {date_str}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Noto Sans JP', sans-serif;
      background: #f0f4f0;
      color: #1a1a1a;
      line-height: 1.75;
      padding: 12px;
    }}
    .header {{
      background: linear-gradient(135deg, #1b4332, #2d6a4f);
      color: #fff;
      padding: 20px 16px;
      border-radius: 14px;
      margin-bottom: 14px;
      text-align: center;
    }}
    .header h1 {{ font-size: 1.4em; letter-spacing: 0.02em; }}
    .header .date {{ font-size: 0.88em; opacity: 0.8; margin-top: 4px; }}
    .card {{
      background: #fff;
      border-radius: 14px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }}
    h2 {{
      font-size: 1.05em;
      color: #1b4332;
      margin-bottom: 10px;
      padding-bottom: 7px;
      border-bottom: 2px solid #d8eedd;
    }}
    ul {{
      padding-left: 18px;
    }}
    li {{
      margin-bottom: 10px;
      font-size: 0.94em;
    }}
    p {{
      font-size: 0.94em;
      margin-bottom: 8px;
    }}
    a {{
      color: #2d6a4f;
    }}
    a.url {{
      font-size: 0.8em;
      color: #888;
      word-break: break-all;
    }}
    .footer {{
      text-align: center;
      font-size: 0.78em;
      color: #aaa;
      margin-top: 8px;
      padding-bottom: 20px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🎾 テニス朝刊</h1>
    <div class="date">{date_str}</div>
  </div>

  {cards_html}

  <div class="footer">Powered by Gemini AI · 毎朝6時更新</div>
</body>
</html>"""
