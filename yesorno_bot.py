import os
import random
import time
from mastodon import Mastodon
from html.parser import HTMLParser

# HTML 태그 제거 도구
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
    return s.get_data().strip().lower()

# 환경 변수에서 토큰과 서버 주소 불러오기
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL") or "https://planet.moe"

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

myself = mastodon.account_verify_credentials()["acct"]
seen_notifications = set()

print(f"🤖 폴링 봇 작동 시작! @{myself} on {INSTANCE_URL}")

# 메인 루프
while True:
    try:
        notifications = mastodon.notifications()
        for note in notifications:
            if note["type"] != "mention":
                continue

            note_id = note["id"]
            if note_id in seen_notifications:
                continue

            acct = note["account"]["acct"]
            if acct == myself:
                continue

            content_html = note["status"]["content"]
            content = strip_html(content_html)
            status_id = note["status"]["id"]

            reply = None
            if "[yn]" in content:
                reply = random.choice(["Y", "N"])
            elif "[1d20]" in content:
                reply = f"🎲 {random.randint(1, 20)}"

            if reply:
                mastodon.status_post(f"@{acct} {reply}", in_reply_to_id=status_id)
                print(f"✅ @{acct} → {reply}")

            seen_notifications.add(note_id)

        time.sleep(10)  # 10초에 한 번 알림 확인

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        time.sleep(30)
