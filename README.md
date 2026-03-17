# monitor

A lightweight deployment monitor. Projects ping a central server on a schedule. If a ping stops coming, you get an SMS.

## How it works

Each deployed project adds one line to its cron job:
```
curl -s https://your-monitor.com/ping/service-name?interval=1800
```

If the service misses its expected interval by 1.5x, an SMS alert fires. When it recovers, another SMS confirms it.

## Stack

- FastAPI — ping endpoint
- SQLite — stores services and last ping times
- Twilio — SMS alerts
- systemd — keeps the server running on the droplet

## Project structure

```
server.py       — FastAPI app, /ping endpoint
checker.py      — background thread, checks for missed pings every minute
db.py           — SQLite helpers
alerts.py       — Twilio SMS (down + recovery)
requirements.txt
deploy.sh       — one-command DigitalOcean setup
```

## Setup

```bash
git clone https://github.com/danielbusnz-lgtm/monitor.git
cd monitor
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env  # fill in Twilio credentials
venv/bin/uvicorn server:app --host 0.0.0.0 --port 80
```

## Deploy to DigitalOcean

```bash
./deploy.sh <droplet_ip>
```

## Environment variables

```
TWILIO_SID=
TWILIO_TOKEN=
TWILIO_FROM=
ALERT_TO=
```
