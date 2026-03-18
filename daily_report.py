#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MONITOR_URL = "http://localhost:8888/status"


def format_ago(seconds):
    if seconds is None:
        return "never"
    if seconds < 120:
        return f"{seconds}s ago"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    return f"{seconds // 3600}h ago"


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
    )


services = requests.get(MONITOR_URL).json()

if not services:
    send("Daily Status: no services registered yet.")
else:
    lines = ["Daily Status Report\n"]
    all_up = True
    for s in services:
        icon = "UP" if s["status"] == "up" else "DOWN" if s["status"] == "down" else "?"
        ago = format_ago(s["last_ping_seconds_ago"])
        lines.append(f"[{icon}] {s['name']} — last ping {ago}")
        if s["status"] != "up":
            all_up = False
    lines.append("")
    lines.append("All systems OK" if all_up else "Some services need attention!")
    send("\n".join(lines))
