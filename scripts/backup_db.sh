#!/usr/bin/env bash
# ==============================================================================
# Database Backup Script for Django Blog Application
# ==============================================================================
# Description: Automatically backs up SQLite db.sqlite3 (or PostgreSQL database)
#              with timestamp, compresses it, and cleans backups older than 30 days.
#
# Cron Installation Example (Run every night at 02:00 AM):
# 0 2 * * * /srv/blog/scripts/backup_db.sh >> /srv/blog/backups/backup.log 2>&1
# ==============================================================================

set -euo pipefail

# Resolve script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP="$(date +'%Y-%m-%d_%H%M%S')"
RETENTION_DAYS=30

mkdir -p "${BACKUP_DIR}"

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Starting Database Backup..."

# Load environment variables if available
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -o allexport
    source "${PROJECT_ROOT}/.env"
    set +o allexport
fi

# Check if using PostgreSQL via DATABASE_URL or POSTGRES_DB
if [ -n "${DATABASE_URL:-}" ] || [ -n "${POSTGRES_DB:-}" ]; then
    BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql.gz"
    echo "Backing up PostgreSQL database..."
    if command -v pg_dump >/dev/null 2>&1; then
        pg_dump "${DATABASE_URL:-}" | gzip > "${BACKUP_FILE}"
        echo "PostgreSQL backup created successfully at ${BACKUP_FILE}"
    else
        echo "Error: pg_dump command not found." >&2
        exit 1
    fi
else
    # Default SQLite Backup
    SQLITE_DB="${PROJECT_ROOT}/db.sqlite3"
    BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sqlite3.gz"

    if [ -f "${SQLITE_DB}" ]; then
        echo "Backing up SQLite database from ${SQLITE_DB}..."

        # Copying the file directly can capture a half-written transaction if
        # the site is serving traffic. SQLite's online backup API takes a
        # consistent snapshot instead.
        TMP_SNAPSHOT="$(mktemp "${BACKUP_DIR}/.snapshot.XXXXXX")"
        trap 'rm -f "${TMP_SNAPSHOT}"' EXIT

        if [ -x "${PROJECT_ROOT}/venv/bin/python" ]; then
            PYTHON="${PROJECT_ROOT}/venv/bin/python"
        else
            PYTHON="python3"
        fi

        "${PYTHON}" - "${SQLITE_DB}" "${TMP_SNAPSHOT}" <<'PY'
import sqlite3
import sys

source, target = sys.argv[1], sys.argv[2]
with sqlite3.connect(f'file:{source}?mode=ro', uri=True) as src, \
        sqlite3.connect(target) as dst:
    src.backup(dst)
PY

        gzip -c "${TMP_SNAPSHOT}" > "${BACKUP_FILE}"
        echo "SQLite backup created successfully at ${BACKUP_FILE}"
    else
        echo "Warning: SQLite database file not found at ${SQLITE_DB}"
        exit 1
    fi
fi

# Remove old backups older than RETENTION_DAYS
echo "Cleaning up backups older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -type f -name "*_backup_*" -mtime "+${RETENTION_DAYS}" -delete

echo "[$(date +'%Y-%m-%d %H:%M:%S')] Database Backup completed successfully!"
