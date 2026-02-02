import os
import requests
from datetime import datetime, timedelta, timezone

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FEED_URL = os.environ["FEED_URL"]

# Timezones
IST = timezone(timedelta(hours=5, minutes=30))

# Filters
ALLOWED_IMPACT = {"High", "Medium"}
ALLOWED_COUNTRY = {"USD", "CNY"}

# Alert window (minutes before event)
ALERT_MIN = 1200
ALERT_MAX = 1800

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True
        },
        timeout=20
    ).raise_for_status()

events = requests.get(FEED_URL, timeout=20).json()

now_utc = datetime.now(timezone.utc)

for e in events:
    # --- FILTERS ---
    if e.get("impact") not in ALLOWED_IMPACT:
        continue

    if e.get("country") not in ALLOWED_COUNTRY:
        continue

    date_raw = e.get("date")
    time_raw = e.get("time")

    if not date_raw:
        continue

    event_dt_utc = None

    # Case 1: ISO timestamp in date
    try:
        event_dt_utc = datetime.fromisoformat(date_raw)
        if event_dt_utc.tzinfo is None:
            event_dt_utc = event_dt_utc.replace(tzinfo=timezone.utc)
        else:
            event_dt_utc = event_dt_utc.astimezone(timezone.utc)
    except ValueError:
        pass

    # Case 2: date + time
    if event_dt_utc is None and time_raw and time_raw not in ("", "All Day"):
        try:
            event_dt_utc = datetime.strptime(
                f"{date_raw} {time_raw}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    # Skip events without a usable time
    if event_dt_utc is None:
        continue

    minutes_to_event = (event_dt_utc - now_utc).total_seconds() / 60

    # 🔔 15-minute-before window
    if not (ALERT_MIN <= minutes_to_event <= ALERT_MAX):
        continue

    event_dt_ist = event_dt_utc.astimezone(IST)

    message = (
        f"🚨 UPCOMING ECONOMIC EVENT 🚨\n\n"
        f"📊 {e['title']}\n"
        f"🕒 {event_dt_ist.strftime('%d %b %Y, %I:%M %p')} IST\n"
        f"🌍 {e['country']}\n"
        f"⚠️ Impact: {e['impact']}\n\n"
        f"⏰ Releasing in ~15 minutes"
    )

    send(message)
