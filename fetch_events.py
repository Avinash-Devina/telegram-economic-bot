import os
import requests
import hashlib

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FEED_URL = os.environ["FEED_URL"]

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
