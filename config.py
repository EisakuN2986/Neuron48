import os

# --- Google Gemini API (無料枠: 1日1,500リクエスト) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"

# --- LINE Messaging API ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_USER_ID = os.environ.get("LINE_USER_ID", "")

# --- YouTube Data API ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# --- RSS Feeds (テニスニュースサイト) ---
# ★ 海外1次情報を優先して配置 ★
RSS_FEEDS = [
    # 海外公式・1次情報（優先）
    "https://www.atptour.com/en/media/rss-feed/xml-feed",       # ATP Tour 公式
    "https://www.wtatennis.com/rss",                             # WTA Tour 公式
    "https://feeds.bbci.co.uk/sport/tennis/rss.xml",            # BBC Sport Tennis
    "https://www.espn.com/espn/rss/tennis/news",                 # ESPN Tennis
    "https://www.eurosport.com/tennis/rss.xml",                  # Eurosport Tennis
    "https://www.tennisworldusa.org/rss/news.xml",               # Tennis World USA
    "https://www.tennis.com/rss/",                               # Tennis.com
    # 日本語ソース（補足）
    "https://news.google.com/rss/search?q=テニス&hl=ja&gl=JP&ceid=JP:ja",
]

# --- Google Scholar / PubMed 検索クエリ ---
SCHOLAR_QUERIES = [
    "tennis coaching performance",
    "tennis biomechanics technique",
    "tennis mental performance sports psychology",
    "tennis training methodology",
]

# --- YouTube 検索クエリ ---
YOUTUBE_QUERIES = [
    "テニス 技術解説",
    "テニス コーチング",
    "ATP テニス 試合",
]

# --- データ保存先 ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --- レポート設定 ---
MAX_NEWS_ITEMS = 8
MAX_PAPERS = 5
MAX_YOUTUBE_VIDEOS = 5
MAX_MATCH_RESULTS = 5
