import os

# --- Anthropic Claude API ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

# --- LINE Messaging API ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_USER_ID = os.environ.get("LINE_USER_ID", "")

# --- YouTube Data API ---
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# --- RSS Feeds (テニスニュースサイト) ---
RSS_FEEDS = [
    "https://www.tennisabstract.com/blog/feed/",
    "https://www.tennisworld.net/feed/",
    "https://www.tennisworldusa.org/rss/news.xml",
    "https://www.atptour.com/en/media/rss-feed/xml-feed",
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
    "tennis coaching tips",
    "tennis technique analysis",
    "ATP tennis match highlights",
]

# --- データ保存先 ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# --- レポート設定 ---
MAX_NEWS_ITEMS = 5
MAX_PAPERS = 3
MAX_YOUTUBE_VIDEOS = 3
MAX_MATCH_RESULTS = 5
