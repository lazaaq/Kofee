#!/usr/bin/env bash
# Build Kofee on this Mac (linux/arm64) and ship it to the pi4 home server.
# The Pi never builds anything: the image is streamed over SSH with `docker load`.
#
#   ./deploy/deploy.sh [path/to/kofee_resnet.tflite]
set -euo pipefail

HOST="${KOFEE_HOST:-lazaaq@100.123.135.38}"
APP_DIR="${KOFEE_APP_DIR:-apps/kofee.lanasa.web.id}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MODEL="${1:-$ROOT/model/kofee_resnet.tflite}"

cd "$ROOT"

echo "==> Building image (linux/arm64)"
docker build --platform linux/arm64 -t kofee:latest .

echo "==> Preparing $HOST:~/$APP_DIR"
ssh "$HOST" "mkdir -p ~/$APP_DIR/data/model && free -h | head -2"
scp docker-compose.yml .env.example "$HOST:~/$APP_DIR/"
ssh "$HOST" "cd ~/$APP_DIR && if [ ! -f .env ]; then echo DJANGO_SECRET_KEY=\$(openssl rand -hex 32) > .env && chmod 600 .env; fi"

if [ -f "$MODEL" ]; then
    echo "==> Uploading model $(du -h "$MODEL" | cut -f1)"
    rsync -az --progress "$MODEL" "$HOST:~/$APP_DIR/data/model/kofee_resnet.tflite"
else
    echo "WARNING: no model at $MODEL - diagnosis will be unavailable on the server" >&2
fi

echo "==> Shipping image"
docker save kofee:latest | gzip | ssh "$HOST" "gunzip | docker load"

echo "==> Starting container"
ssh "$HOST" "cd ~/$APP_DIR && docker compose up -d --no-build && sleep 5 && docker compose ps && curl -s -o /dev/null -w 'local check: %{http_code}\n' -H 'Host: kofee.lanasa.web.id' http://127.0.0.1:3005/accounts/login/"
