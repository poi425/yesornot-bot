import os
import random
import time
from mastodon import Mastodon, StreamListener
from html.parser import HTMLParser

# HTML 제거 도우미
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, d):
        self.text_parts.append(d)

    def get_data(self):
        return ''.join(self.text_parts)

def strip_html(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

# 기본 설정
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL") or "https://planet.moe"

if not ACCESS_TOKEN or not INSTANCE_URL:
    raise ValueError("ACCESS_TOKEN 또는 INSTANCE_URL 환경변수가 누락되었습니다!")

mastodon = Mastodon(access_token=ACCESS_TOKEN, api_base_url=INSTANCE_URL)
myself = mastodon.account_verify_credentials()["acct"]

# 최근 응답 캐시: { (acct + content): timestamp }
reply_cache = {}

class UnifiedBotListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] != 'mention':
            return

        acct = notification['account']['acct']
        status_id = notification['status']['id']
        content_html = notification['status']['content']
        content = strip_html(content_html).lower().strip()
        mentions = [m["acct"] for m in notification['status']['mentions']]

        if acct == myself or mentions.count(myself) != 1:
            return

        cache_key = f"{acct}:{content}"
        now = time.time()

        # 15초 이내 중복 응답 방지
        if cache_key in reply_cache and now - reply_cache[cache_key] < 15:
            return

        reply = None
        if "[yn]" in content:
            reply = random.choice(["Y", "N"])
        elif "[1d20]" in content:
            reply = f"{random.randint(1, 20)}"

        if reply:
            mastodon.status_post(f"@{acct} {reply}", in_reply_to_id=status_id)
            reply_cache[cache_key] = now
            print(f"✅ @{acct} → {reply}")

print(f"🤖 통합 봇 작동 시작! ({myself}) on {INSTANCE_URL}")
mastodon.stream_user(UnifiedBotListener())
