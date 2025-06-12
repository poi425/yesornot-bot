import os
import random
from mastodon import Mastodon, StreamListener

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL") or "https://planet.moe"

if not ACCESS_TOKEN or not INSTANCE_URL:
    raise ValueError("ACCESS_TOKEN 또는 INSTANCE_URL 환경변수가 설정되지 않았습니다!")

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

myself = mastodon.account_verify_credentials()["acct"]
already_replied = set()

class MentionListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] != 'mention':
            return

        acct = notification['account']['acct']
        status_id = notification['status']['id']
        content_html = notification['status']['content']
        content = content_html.lower()

        # 조건: 자기 자신이 보낸 툿이면 무시
        if acct == myself:
            return

        # 조건: 이미 응답했으면 무시
        if status_id in already_replied:
            return

        # 조건: [YN] 키워드 없으면 무시
        if "[yn]" not in content:
            return

        # 조건: 나만 멘션됐는지 확인
        mentions = [m["acct"] for m in notification['status']['mentions']]
        if mentions.count(myself) != 1:
            return

        answer = random.choice(["Y", "N"])
        mastodon.status_post(f"@{acct} {answer}", in_reply_to_id=status_id)
        already_replied.add(status_id)
        print(f"✅ @{acct} → {answer}")

print(f"🤖 봇 작동 시작! ({myself}) 서버: {INSTANCE_URL}")
mastodon.stream_user(MentionListener())
