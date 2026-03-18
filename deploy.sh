#!/bin/bash
# deploy.sh — push and start the monitor service on the DigitalOcean droplet
# Usage: ./deploy.sh <droplet_ip>

set -e

IP=${1:-45.55.121.238}
REMOTE_DIR="/opt/monitor"
SERVICE_FILE="monitor.service"

echo "==> Deploying monitor to $IP"

# Copy files (excludes venv, __pycache__, *.db)
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.db' \
    -e "ssh -o StrictHostKeyChecking=no" \
    ./ root@$IP:$REMOTE_DIR/

ssh -o StrictHostKeyChecking=no root@$IP bash <<EOF
set -e

cd $REMOTE_DIR

# Install Python deps
python3 -m venv venv
venv/bin/pip install -q -r requirements.txt

# Write .env if it doesn't exist
if [ ! -f .env ]; then
    echo "ERROR: .env not found on server — copy it manually to $REMOTE_DIR/.env"
    exit 1
fi

# Install systemd service
cat > /etc/systemd/system/$SERVICE_FILE <<UNIT
[Unit]
Description=Deployment Monitor
After=network.target

[Service]
WorkingDirectory=$REMOTE_DIR
ExecStart=$REMOTE_DIR/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8888
Restart=always
RestartSec=5
EnvironmentFile=$REMOTE_DIR/.env

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable $SERVICE_FILE
systemctl restart $SERVICE_FILE
systemctl status $SERVICE_FILE --no-pager
EOF

echo "==> Done. Monitor running at http://$IP:8888"
echo "==> Test: curl http://$IP:8888/ping/test?interval=60"
