import os
import random
from mastodon import Mastodon, StreamListener

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = "https://planet.moe"

if not ACCESS_TOKEN:
    raise ValueError("ACCESS_TOKEN 환경변수가 설정되지 않았습니다!")

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

class MentionListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            acct = notification['account']['acct']
            reply_id = notification['status']['id']
            content = notification['status']['content']
            content_text = content.lower()  # 소문자로 변환해 키워드 감지

            # 1. 자기 자신 멘션이면 무시
            if acct == mastodon.account_verify_credentials()["acct"]:
                return

            # 2. [YN] 키워드 없으면 무시
            if "[yn]" not in content_text:
                print(f"⚠️ [YN] 키워드 없음 → 무시: @{acct}")
                return

            # 3. 정상 응답
            answer = random.choice(["Y", "N"])
            status = f"@{acct} {answer}"
            mastodon.status_post(status, in_reply_to_id=reply_id)
            print(f"✅ [YN] 멘션 감지 → @{acct} → 응답: {answer}")

print(f"🤖 봇 작동 시작! 서버: {INSTANCE_URL}")
mastodon.stream_user(MentionListener())
