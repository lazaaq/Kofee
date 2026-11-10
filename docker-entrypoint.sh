#!/bin/sh
set -e

mkdir -p "$(dirname "$DATABASE_PATH")" "$MEDIA_ROOT/images" "$(dirname "$MODEL_PATH")"

# First run: start from the database and sample images shipped with the repo
if [ ! -f "$DATABASE_PATH" ] && [ -f /app/db.sqlite3 ]; then
    cp /app/db.sqlite3 "$DATABASE_PATH"
fi
if [ ! -d "$MEDIA_ROOT/sample_image" ]; then
    cp -r /app/media/. "$MEDIA_ROOT/"
fi

python manage.py migrate --noinput
python manage.py loaddata seed/label.json

if [ ! -f "$MODEL_PATH" ]; then
    echo "WARNING: model not found at $MODEL_PATH - diagnosis will be unavailable" >&2
fi

exec "$@"
