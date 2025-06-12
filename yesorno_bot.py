import os
import random
from mastodon import Mastodon, StreamListener
from html.parser import HTMLParser

# 🔧 HTML 태그 제거용 파서 클래스
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

# 🔧 환경변수 불러오기
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL") or "https://planet.moe"

if not ACCESS_TOKEN or not INSTANCE_URL:
    raise ValueError("ACCESS_TOKEN 또는 INSTANCE_URL 환경변수가 누락되었습니다!")

# ✅ 마스토돈 인증
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

myself = mastodon.account_verify_credentials()["acct"]
already_replied = set()

# ✅ 봇 리스너 클래스
class UnifiedBotListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] != 'mention':
            return

        acct = notification['account']['acct']
        status_id = notification['status']['id']
        content_html = notification['status']['content']
        content = strip_html(content_html).lower()

        # 조건들
        if acct == myself:
            return
        if status_id in already_replied:
            return
        mentions = [m["acct"] for m in notification['status']['mentions']]
        if mentions.count(myself) != 1:
            return

        # 키워드 판별 및 응답
        reply = None
        if "[yn]" in content:
            reply = random.choice(["Y", "N"])
        elif "[1d20]" in content:
            reply = f"🎲 {random.randint(1, 20)}"

        if reply:
            mastodon.status_post(f"@{acct} {reply}", in_reply_to_id=status_id)
            already_replied.add(status_id)
            print(f"✅ 응답 완료: @{acct} → {reply}")

print(f"🤖 통합 봇 작동 시작! ({myself}) 서버: {INSTANCE_URL}")
mastodon.stream_user(UnifiedBotListener())
