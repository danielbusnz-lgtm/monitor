# monitor

A lightweight deployment monitor. Projects ping a central server on a schedule. If a ping stops coming, you get a Telegram alert with an AI-generated diagnosis of why it failed.

## How it works

Each deployed project adds one line to its cron job:
```
curl -s http://your-server:8888/ping/service-name?interval=1800
```

If the service misses its expected interval by 1.5x, an alert fires. The monitor grabs recent logs, sends them to Claude Haiku, and includes a plain-English diagnosis in the Telegram message. When the service recovers, a follow-up message confirms it.

A daily status report is sent every day at noon (US Eastern) summarising all services.

## Stack

- FastAPI — ping endpoint + status endpoint
- SQLite — stores services and last ping times
- Telegram Bot API — down, recovery, and daily status alerts
- Claude Haiku — diagnoses failures from recent logs
- systemd — keeps the server running on the droplet

## Project structure

```
server.py         — FastAPI app, /ping and /status endpoints
checker.py        — background thread, checks for missed pings every minute
db.py             — SQLite helpers
alerts.py         — Telegram alerts with Haiku diagnosis (down + recovery)
daily_report.py   — daily status report sent at noon ET via cron
deploy.sh         — one-command DigitalOcean setup
```

## Setup

```bash
git clone https://github.com/danielbusnz-lgtm/monitor.git
cd monitor
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env  # fill in credentials
venv/bin/uvicorn server:app --host 0.0.0.0 --port 8888
```

## Deploy to DigitalOcean

```bash
./deploy.sh <droplet_ip>
```

## Environment variables

```
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
ANTHROPIC_API_KEY=
```
