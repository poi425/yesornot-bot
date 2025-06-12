import os
import random
from mastodon import Mastodon, StreamListener
from dotenv import load_dotenv

# 환경변수 불러오기 (.env용)
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
INSTANCE_URL = os.getenv("INSTANCE_URL")

mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=INSTANCE_URL
)

class MentionListener(StreamListener):
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            acct = notification['account']['acct']
            reply_id = notification['status']['id']
            answer = random.choice(["Y", "N"])
            status = f"@{acct} {answer}"
            mastodon.status_post(status, in_reply_to_id=reply_id)
            print(f"👂 @{acct} → {answer}")

print("🤖 봇 작동 시작!")
mastodon.stream_user(MentionListener())
