#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/django_user/blockline_app"
VENV="$APP_DIR/venv"
PY="$VENV/bin/python"
PIP="$VENV/bin/pip"
LOG="/var/log/blockline_deploy.log"

exec >>"$LOG" 2>&1

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') Deploy start ====="
cd "$APP_DIR"

echo "[git] fetching/reset..."
git fetch --all
git reset --hard origin/main

echo "[pip] installing..."
$PIP install --upgrade pip
$PIP install -r requirements.txt

echo "[django] migrate & collectstatic..."
$PY manage.py migrate --noinput
$PY manage.py collectstatic --noinput

echo "[systemd] restarting gunicorn..."
sudo systemctl restart gunicorn
sudo systemctl status gunicorn --no-pager -l | sed -n '1,10p'

echo "===== $(date -u +'%Y-%m-%dT%H:%M:%SZ') Deploy end ====="
