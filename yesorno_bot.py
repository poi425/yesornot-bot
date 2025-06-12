import os
import random
from mastodon import Mastodon, StreamListener

# 환경변수에서 토큰만 불러옴
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = "https://planet.moe"  # 하드코딩된 서버 주소

if not ACCESS_TOKEN:
    raise ValueError("ACCESS_TOKEN 환경변수가 설정되지 않았습니다!")

# 마스토돈 API 초기화
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

# 멘션 이벤트 처리
class MentionListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            acct = notification['account']['acct']
            
            # 자기 자신이면 무시
            if acct == mastodon.account_verify_credentials()["acct"]:
                return

            reply_id = notification['status']['id']
            answer = random.choice(["Y", "N"])
            status = f"@{acct} {answer}"
            mastodon.status_post(status, in_reply_to_id=reply_id)
            print(f"👂 @{acct} → {answer}")


# 실행
print(f"🤖 봇 작동 시작! 서버: {INSTANCE_URL}")
mastodon.stream_user(MentionListener())
