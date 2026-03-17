import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID   = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM  = os.getenv("TWILIO_FROM")
ALERT_TO     = os.getenv("ALERT_TO")


def send_alert(service_name: str):
    if not TWILIO_SID:
        print(f"[ALERT] {service_name} is DOWN (Twilio not configured)")
        return

    from twilio.rest import Client
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=f"[monitor] DOWN: {service_name} has stopped checking in.",
        from_=TWILIO_FROM,
        to=ALERT_TO,
    )
    print(f"[ALERT] SMS sent — {service_name} is DOWN")

def send_recovery(service_name: str):
    if not TWILIO_SID:
        print(f"[RECOVERY] {service_name} is back UP (Twilio not configured)")
        return 
    from twilio.rest import Client
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(
        body=f"[monitor] RECOVERED: {service_name} is back online.",
        from_=TWILIO_FROM,
        to=ALERT_TO,
    )
    print(f"[RECOVERY] SMS sent — {service_name} is back UP")
