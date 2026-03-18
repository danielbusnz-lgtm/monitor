import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _send(message: str):
    if not TELEGRAM_TOKEN:
        print(f"[ALERT] {message} (Telegram not configured)")
        return
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
    )


def send_alert(service_name: str):
    _send(f"DOWN: {service_name} has stopped checking in.")
    print(f"[ALERT] Telegram sent — {service_name} is DOWN")


def send_recovery(service_name: str):
    _send(f"RECOVERED: {service_name} is back online.")
    print(f"[RECOVERY] Telegram sent — {service_name} is back UP")
