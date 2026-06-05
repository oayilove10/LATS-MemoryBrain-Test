#!/bin/bash
set -e

BASE="$HOME/LATS_PRODUCTION"

echo "========================================"
echo "LATS AUTO CLEANUP"
echo "BASE: $BASE"
echo "========================================"

echo "[1] Remove Python cache"
find "$BASE" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$BASE" -name "*.pyc" -delete 2>/dev/null || true

echo "[2] Remove temp/save files"
find "$BASE" -name "*.tmp" -delete 2>/dev/null || true
find "$BASE" -name "*.bak" -delete 2>/dev/null || true
find "$BASE" -name "*.save" -delete 2>/dev/null || true

echo "[3] Remove generated Memory V3 runtime outputs"
rm -rf "$BASE/data/memory_v3/full_brain_logs"
rm -rf "$BASE/data/memory_v3/full_brain_exports"

echo "========================================"
echo "CLEANUP DONE"
echo "========================================"
