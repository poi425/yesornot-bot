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

# 자신의 계정 정보 미리 가져옴
myself = mastodon.account_verify_credentials()["acct"]

# 중복 응답 방지 캐시
already_replied = set()

class MentionListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] != 'mention':
            return

        acct = notification['account']['acct']
        status_id = notification['status']['id']
        content = notification['status']['content']
        content_text = content.lower()

        # 이미 응답한 멘션이면 무시
        if status_id in already_replied:
            return

        # [YN] 키워드 없으면 무시
        if "[yn]" not in content_text:
            return

        # mention 목록 중 나 자신만 들어 있는지 확인
        mention_list = [m["acct"] for m in notification['status']['mentions']]
        if mention_list.count(myself) != 1 or len(mention_list) != 1:
            print(f"⚠️ 멘션이 여러 명에게 보내졌음 → 무시: {mention_list}")
            return

        # 자기 멘션이 맞고, [YN] 키워드 있고, 중복 아니면 응답
        already_replied.add(status_id)
        answer = random.choice(["Y", "N"])
        mastodon.status_post(f"@{acct} {answer}", in_reply_to_id=status_id)
        print(f"✅ 응답 완료 → @{acct} → {answer}")
