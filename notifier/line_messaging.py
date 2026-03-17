"""LINE Messaging API でレポートを送信する

LINE Notify は 2025年4月に廃止されたため、LINE Messaging API を使用します。
設定方法: LINE Developers Console でチャンネルを作成し、
  - LINE_CHANNEL_ACCESS_TOKEN: チャンネルアクセストークン
  - LINE_USER_ID: 送信先のユーザーID (自分の LINE UID)
を GitHub Secrets に設定してください。

LINE UID の確認方法:
  https://developers.line.biz/console/ → チャンネル → Messaging API設定
  → Webhook URL を設定後、ボットに任意のメッセージを送ると
    Webhook で userId が確認できます。
"""
import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_USER_ID

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
MAX_MESSAGE_LENGTH = 5000  # LINE の1メッセージ上限


def send_report(report_text: str) -> bool:
    """LINE Messaging API でレポートを送信する"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("[LINE] LINE_CHANNEL_ACCESS_TOKEN が設定されていません。スキップします。")
        return False

    if not LINE_USER_ID:
        print("[LINE] LINE_USER_ID が設定されていません。スキップします。")
        return False

    # 5000文字を超える場合は分割送信
    chunks = _split_message(report_text, MAX_MESSAGE_LENGTH)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    success = True

    for chunk in chunks:
        payload = {
            "to": LINE_USER_ID,
            "messages": [{"type": "text", "text": chunk}],
        }
        try:
            resp = requests.post(LINE_API_URL, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            print(f"[LINE] 送信成功: {resp.status_code}")
        except requests.HTTPError as e:
            print(f"[LINE] 送信エラー: {e} | レスポンス: {resp.text}")
            success = False
        except Exception as e:
            print(f"[LINE] 予期しないエラー: {e}")
            success = False

    return success


def _split_message(text: str, max_len: int) -> list[str]:
    """長いメッセージを指定文字数で分割する"""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # 改行で分割を試みる
        split_pos = text.rfind("\n", 0, max_len)
        if split_pos == -1:
            split_pos = max_len
        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip("\n")

    return chunks


if __name__ == "__main__":
    test_msg = "🎾 テニス モーニングレポート テスト送信"
    result = send_report(test_msg)
    print(f"送信結果: {'成功' if result else '失敗'}")
