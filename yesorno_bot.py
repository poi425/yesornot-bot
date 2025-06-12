import os
import random
from mastodon import Mastodon, StreamListener

# 환경변수에서 토큰, 서버 주소 불러오기
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL") or "https://planet.moe"

if not ACCESS_TOKEN or not INSTANCE_URL:
    raise ValueError("ACCESS_TOKEN 또는 INSTANCE_URL 환경변수가 누락되었습니다!")

# 마스토돈 인증
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

# 내 계정 정보
myself = mastodon.account_verify_credentials()["acct"]
already_replied = set()

class UnifiedBotListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] != 'mention':
            return

        acct = notification['account']['acct']
        status_id = notification['status']['id']
        content = notification['status']['content'].lower()

        if acct == myself:
            return
        if status_id in already_replied:
            return

        mentions = [m["acct"] for m in notification['status']['mentions']]
        if mentions.count(myself) != 1:
            return

        reply = None
        if "[yn]" in content:
            reply = random.choice(["Y", "N"])
        elif "[1d20]" in content:
            reply = f"🎲 {random.randint(1, 20)}"

        if reply:
            mastodon.status_post(f"@{acct} {reply}", in_reply_to_id=status_id)
            already_replied.add(status_id)
            print(f"✅ 응답: @{acct} → {reply}")

print(f"🤖 통합 봇 작동 시작! ({myself}) @ {INSTANCE_URL}")
mastodon.stream_user(UnifiedBotListener())
