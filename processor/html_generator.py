"""Gemini 生成レポートをモバイル対応 HTML に変換する"""
import re

URL_PATTERN = re.compile(r'https?://[^\s<>"]+')

# Gemini形式: ① 📊 ... / フォールバック形式: 📊 ...
SECTION_STARTS = ('①', '②', '③', '④', '⑤', '⑥',
                  '📊', '📰', '🔬', '▶️', '💡', '✅')


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
        if stripped.startswith('🎾') and current_title is None:
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


def _extract_source_badge(text: str) -> tuple[str, str]:
    """【ソース名】を抽出してバッジ用テキストと本文を返す"""
    m = re.search(r'【([^】]+)】', text)
    if m:
        badge = m.group(1)
        clean = text[:m.start()].strip() + text[m.end():].strip()
        return clean.strip(), badge
    return text, ''


def _build_card(title: str, items: list[str]) -> str:
    content_html = ''
    i = 0
    pending_url = ''
    pending_text = ''
    pending_badge = ''
    in_list = False

    def _flush_item() -> str:
        nonlocal pending_text, pending_url, pending_badge
        if not pending_text:
            return ''
        text_html = _linkify(pending_text)
        badge_html = (
            f'<span class="badge">{pending_badge}</span>' if pending_badge else ''
        )
        link_html = (
            f'<a class="read-more" href="{pending_url}" target="_blank">記事を読む →</a>'
            if pending_url else ''
        )
        result = (
            f'<li>'
            f'<div class="item-row">{text_html}{badge_html}</div>'
            f'{link_html}'
            f'</li>'
        )
        pending_text = ''
        pending_url = ''
        pending_badge = ''
        return result

    rows = ''
    items_html = ''

    for item in items:
        if item.startswith('http'):
            # 直前の箇条書き項目の URL として記録
            pending_url = item
            items_html += _flush_item()
        elif item.startswith(('・', '- ', '• ')):
            items_html += _flush_item()
            body = re.sub(r'^[・\-• ]+', '', item).strip()
            pending_text, pending_badge = _extract_source_badge(body)
            pending_url = ''
        else:
            items_html += _flush_item()
            clean, badge = _extract_source_badge(item)
            badge_html = f'<span class="badge">{badge}</span>' if badge else ''
            items_html += f'<p>{_linkify(clean)}{badge_html}</p>'

    items_html += _flush_item()

    if '<li>' in items_html:
        items_html = f'<ul>{items_html}</ul>'

    return f'<div class="card"><h2>{title}</h2>{items_html}</div>'


def generate_html(report_text: str, date_str: str) -> str:
    """レポートテキストから完全な HTML ページを生成する"""
    sections = _parse_sections(report_text)

    if sections:
        cards_html = '\n'.join(_build_card(t, items) for t, items in sections)
    else:
        fallback = _linkify(report_text.replace('\n', '<br>'))
        cards_html = f'<div class="card"><p>{fallback}</p></div>'

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🎾 テニス朝刊 {date_str}</title>
  <style>
    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans',
                   'Noto Sans JP', sans-serif;
      background: #eef2ee;
      color: #1a1a1a;
      line-height: 1.8;
      padding: 14px 12px 32px;
      font-size: 15px;
    }}

    /* ── ヘッダー ── */
    .header {{
      background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
      color: #fff;
      padding: 22px 16px 18px;
      border-radius: 16px;
      margin-bottom: 16px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(27,67,50,0.25);
    }}
    .header h1 {{
      font-size: 1.5em;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .header .date {{
      font-size: 0.82em;
      opacity: 0.8;
      margin-top: 5px;
      letter-spacing: 0.06em;
    }}

    /* ── カード ── */
    .card {{
      background: #fff;
      border-radius: 16px;
      padding: 18px 16px;
      margin-bottom: 14px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }}
    h2 {{
      font-size: 1.0em;
      font-weight: 700;
      color: #1b4332;
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 2px solid #d0e8d8;
      letter-spacing: 0.02em;
    }}

    /* ── リスト項目 ── */
    ul {{
      list-style: none;
      padding: 0;
    }}
    li {{
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;
    }}
    li:last-child {{
      border-bottom: none;
      padding-bottom: 0;
    }}
    li:first-child {{
      padding-top: 0;
    }}
    .item-row {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .item-row::before {{
      content: '▸';
      color: #2d6a4f;
      font-size: 0.85em;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    /* ── バッジ（情報ソース） ── */
    .badge {{
      display: inline-block;
      background: #e8f5e9;
      color: #1b4332;
      font-size: 0.7em;
      font-weight: 600;
      padding: 1px 7px;
      border-radius: 99px;
      white-space: nowrap;
      flex-shrink: 0;
      margin-top: 3px;
    }}

    /* ── 記事リンクボタン ── */
    .read-more {{
      display: inline-block;
      margin-top: 8px;
      padding: 5px 14px;
      background: #1b4332;
      color: #fff;
      font-size: 0.78em;
      font-weight: 600;
      border-radius: 99px;
      text-decoration: none;
      letter-spacing: 0.03em;
    }}
    .read-more:active {{
      opacity: 0.75;
    }}

    /* ── 段落 ── */
    p {{
      font-size: 0.95em;
      margin-bottom: 8px;
      line-height: 1.75;
    }}
    p:last-child {{
      margin-bottom: 0;
    }}
    p a {{
      color: #2d6a4f;
      text-decoration: underline;
    }}

    /* ── フッター ── */
    .footer {{
      text-align: center;
      font-size: 0.75em;
      color: #aaa;
      margin-top: 4px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🎾 テニス朝刊</h1>
    <div class="date">{date_str}</div>
  </div>

  {cards_html}

  <div class="footer">Powered by Gemini AI &nbsp;·&nbsp; 毎朝6時更新</div>
</body>
</html>"""
