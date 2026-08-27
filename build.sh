#!/usr/bin/env bash
#
# Release script. Runs on the VPS, either from the CD workflow or by hand:
#   cd /srv/blog && ./build.sh
#
# It assumes the repository is already checked out with a venv at ./venv and a
# populated .env alongside it.

set -euo pipefail

cd "$(dirname "$0")"

echo "==> Activating virtualenv"
# shellcheck disable=SC1091
source venv/bin/activate

echo "==> Installing dependencies"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Verifying production configuration"
python manage.py check --deploy

echo "==> Restarting the application service"
sudo systemctl restart blog

echo "==> Waiting for the service to answer"
for i in $(seq 1 10); do
    if curl --fail --silent --max-time 3 http://127.0.0.1:8000/healthz/ > /dev/null; then
        echo "==> Deploy OK: health check passed"
        exit 0
    fi
    sleep 1
done

echo "!! Health check failed after restart. Recent logs:" >&2
sudo journalctl -u blog -n 40 --no-pager >&2
exit 1
