import os
import subprocess
import requests
import anthropic
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Known log paths for cron-based services
CRON_LOG_PATHS = {
    "twitter-bot":  "/root/twitter-bot/cron.log",
    "invoice-flow": "/opt/invoice-flow/logs/cron.log",
}


def _get_logs(service_name: str) -> str:
    # Try systemd journal first
    try:
        result = subprocess.run(
            ["journalctl", "-u", service_name, "-n", "40", "--no-pager", "--no-hostname", "-o", "short"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip() and "No entries" not in result.stdout:
            return result.stdout.strip()
    except Exception:
        pass

    # Fall back to known cron log file
    log_path = CRON_LOG_PATHS.get(service_name)
    if log_path and os.path.exists(log_path):
        try:
            result = subprocess.run(["tail", "-n", "40", log_path], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            pass

    return ""


def _get_diagnosis(service_name: str, logs: str) -> str:
    if not ANTHROPIC_API_KEY or not logs:
        return ""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"A deployment called '{service_name}' has gone down. "
                    f"Here are its recent logs:\n\n{logs}\n\n"
                    "In 2-3 sentences, explain what likely caused it to fail. Be specific and direct."
                )
            }]
        )
        return message.content[0].text.strip()
    except Exception:
        return ""


def _send(message: str):
    if not TELEGRAM_TOKEN:
        print(f"[ALERT] {message} (Telegram not configured)")
        return
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
    )


def send_alert(service_name: str):
    logs = _get_logs(service_name)
    diagnosis = _get_diagnosis(service_name, logs)

    message = f"DOWN: {service_name} has stopped checking in."
    if diagnosis:
        message += f"\n\nDiagnosis: {diagnosis}"

    _send(message)
    print(f"[ALERT] Telegram sent — {service_name} is DOWN")


def send_recovery(service_name: str):
    _send(f"RECOVERED: {service_name} is back online.")
    print(f"[RECOVERY] Telegram sent — {service_name} is back UP")
