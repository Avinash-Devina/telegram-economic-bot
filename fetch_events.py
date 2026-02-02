import os
import requests
import hashlib

BOT_TOKEN = os.environ["8211906927:AAEuqveIbJyinxuWQ_FqLb_KwLqaRXKgyO0"]
CHAT_ID = os.environ["7920132476"]
FEED_URL = os.environ["https://nfs.faireconomy.media/ff_calendar_thisweek.json"]

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

data = requests.get(FEED_URL, timeout=20).json()

sent = set()

for e in data.get("events", [])[:5]:
    uid = hashlib.md5(e["title"].encode()).hexdigest()
    if uid in sent:
        continue

    message = (
        f"📊 {e['title']}\n"
        f"🕒 {e['time']}\n"
        f"🌍 {e['country']}\n"
        f"⚠️ Impact: {e.get('impact', 'N/A')}"
    )

    send(message)
    sent.add(uid)
