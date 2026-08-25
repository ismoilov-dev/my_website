#!/bin/bash
set -e

echo "================================================="
echo "   🚀 Django Blog Production Deployment Script   "
echo "================================================="

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "[1/6] 📦 Checking virtual environment and dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "Virtual environment not found! Please create a virtual environment first: python3 -m venv venv"
    exit 1
fi

pip install -q -r requirements.txt

echo "[2/6] 📁 Ensuring media and static directories exist..."
mkdir -p media/certificates
mkdir -p media/feed
mkdir -p staticfiles

echo "[3/6] 🗄️ Running Django Database Migrations..."
python manage.py migrate --noinput

echo "[4/6] 🎨 Collecting Static Files..."
python manage.py collectstatic --noinput

echo "[5/6] 🔒 Setting File Permissions for Nginx & Media Uploads..."
chmod -R 775 media/
chmod -R 775 staticfiles/
if [ -f db.sqlite3 ]; then
    chmod 664 db.sqlite3
fi

# Ensure parent directory permits www-data / Nginx read access
chmod o+rx "$PROJECT_DIR"
chmod o+rx "$PROJECT_DIR/media"
chmod o+rx "$PROJECT_DIR/staticfiles"

echo "[6/6] 🔄 Restarting Services..."
if systemctl is-active --quiet blog 2>/dev/null; then
    echo "  - Restarting blog.service..."
    sudo systemctl restart blog
else
    echo "  - blog.service is not active. (Start manually or run gunicorn)"
fi

if systemctl is-active --quiet nginx 2>/dev/null; then
    echo "  - Reloading Nginx..."
    sudo systemctl reload nginx
else
    echo "  - Nginx service is not active. (Start manually: sudo systemctl start nginx)"
fi

echo "================================================="
echo "   ✅ Deployment & Media Setup Completed!     "
echo "================================================="
