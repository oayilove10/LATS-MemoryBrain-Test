#!/bin/bash

while true
do
    echo "========================================"
    echo "LATS RUNTIME BACKUP"
    date
    echo "========================================"

    rsync -av \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.tmp' \
    --exclude='*.bak' \
    --exclude='.cache' \
    ~/LATS_PRODUCTION/data/ \
    ~/LATS_PRODUCTION_BACKUP/data/

    rsync -av \
    ~/LATS_PRODUCTION/logs/ \
    ~/LATS_PRODUCTION_BACKUP/logs/

    rsync -av \
    ~/LATS_PRODUCTION/memory_v3/ \
    ~/LATS_PRODUCTION_BACKUP/memory_v3/

    rsync -av \
    ~/LATS_PRODUCTION/config/ \
    ~/LATS_PRODUCTION_BACKUP/config/

    echo "========================================"
    echo "[BACKUP OK]"
    echo "sleep 30 minutes..."
    echo "========================================"

    sleep 1800

done
