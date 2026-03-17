# 🎾 Neuron48 - テニス情報自動蓄積システム

毎朝、最新のテニス情報を自動収集し、Claude AI がコーチング視点の「心技体」レポートを生成して LINE で配信するシステムです。

## 機能

| 機能 | 内容 |
|---|---|
| **試合結果・ランキング** | ATP/WTA 最新スコア・世界ランキング |
| **テニスニュース** | RSS フィードから最新記事を収集 |
| **論文・研究** | PubMed からテニス科学論文を収集 |
| **YouTube 動画** | 最新のコーチング・試合解説動画 |
| **AI レポート生成** | Claude API が「心技体」視点でコーチング考察を生成 |
| **LINE 配信** | 毎朝6時に LINE Messaging API で自動配信 |

## セットアップ

### 1. GitHub Secrets の設定

リポジトリの `Settings > Secrets and variables > Actions` で以下を設定してください：

| Secret 名 | 説明 | 取得方法 |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API キー（無料） | [Google AI Studio](https://aistudio.google.com/apikey) |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE チャンネルアクセストークン | LINE Developers Console |
| `LINE_USER_ID` | 配信先の LINE ユーザー ID | LINE Developers で Webhook 確認 |
| `YOUTUBE_API_KEY` | YouTube Data API キー（任意） | Google Cloud Console |

### 2. LINE Messaging API の設定

> ⚠️ LINE Notify は2025年4月に廃止されました。LINE Messaging API を使用します。

1. [LINE Developers Console](https://developers.line.biz/console/) でプロバイダーを作成
2. Messaging API チャンネルを作成
3. チャンネルアクセストークン（長期）を発行 → `LINE_CHANNEL_ACCESS_TOKEN` に設定
4. ボットに LINE でメッセージを送信
5. Webhook ログまたは以下で自分の userId を確認:
   ```bash
   curl -X GET https://api.line.me/v2/bot/profile/{userId} \
     -H "Authorization: Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
   ```
6. 確認した userId を `LINE_USER_ID` に設定

### 3. 自動実行の確認

GitHub Actions タブで `🎾 Daily Tennis Morning Report` ワークフローを確認できます。

- **自動実行**: 毎朝6時 (JST)
- **手動実行**: `workflow_dispatch` で任意のタイミングで実行可能

## ローカル実行

```bash
pip install -r requirements.txt

export ANTHROPIC_API_KEY="your_key"
export LINE_CHANNEL_ACCESS_TOKEN="your_token"
export LINE_USER_ID="your_user_id"
export YOUTUBE_API_KEY="your_key"  # オプション

python main.py
```

## ディレクトリ構成

```
Neuron48/
├── .github/workflows/
│   └── daily-tennis-report.yml   # GitHub Actions スケジューラー
├── collectors/
│   ├── atp_wta.py                # ATP/WTA 試合結果・ランキング
│   ├── rss_feeds.py              # テニスニュース RSS
│   ├── scholar.py                # PubMed 論文収集
│   └── youtube.py                # YouTube 動画情報
├── processor/
│   └── summarizer.py             # Claude API でレポート生成
├── notifier/
│   └── line_messaging.py         # LINE Messaging API 配信
├── data/                         # 収集データ蓄積 (JSON)
├── config.py                     # 設定・環境変数
├── main.py                       # メインスクリプト
└── requirements.txt
```

## 生成されるレポートのサンプル

```
🎾 テニス モーニングレポート 2026-03-17
==============================

📊 本日の試合結果・ランキング動向
- ジョコビッチが第1シードとして全仏オープンへ
- アルカラスが2位をキープ

📰 テニス最新ニュース
- ナダル、今季復帰戦でバルセロナ優勝へ意欲
- 次世代選手の台頭: カルロス・アルカラスの練習方法が公開

🔬 研究・論文インサイト
- サーブ速度と勝率の相関: 190km/h 超で勝率が15%向上

🎯 今日のコーチングポイント「心技体」
- 心: 試合中の呼吸法でプレッシャーを管理
- 技: サーブのトスの安定が一貫性につながる
- 体: ヒップローテーションの強化がパワーに直結

💡 今日の一言
「チャンピオンは諦めない人。諦めた人はチャンピオンにならない」
```

## カスタマイズ

`config.py` を編集して情報ソースやクエリを調整できます：

- `RSS_FEEDS`: テニスニュースサイトの RSS URL
- `SCHOLAR_QUERIES`: 論文検索キーワード
- `YOUTUBE_QUERIES`: YouTube 検索キーワード
- `MAX_NEWS_ITEMS`: 収集するニュース件数
