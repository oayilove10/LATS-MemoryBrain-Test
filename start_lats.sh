#!/bin/bash

# LATS P3 TEST
# Startup Hook V1
# Recheck first. Runtime starts only if Recheck passes.

cd ~/LATS_PRODUCTION_P3_TEST || exit 1

echo "================================================================================"
echo "LATS P3 TEST STARTUP HOOK V1"
echo "================================================================================"

echo "[STEP 1] Run One Click Recheck Room"
python3 runtime/recheck_room/one_click_recheck.py

RECHECK_STATUS=$?

echo "================================================================================"
echo "Recheck exit code: $RECHECK_STATUS"
echo "================================================================================"

if [ "$RECHECK_STATUS" -ne 0 ]; then
    echo "RUN BLOCKED"
    echo "Reason: Recheck failed or backfill required"
    echo "Action: Review runtime/recheck reports"
    exit 1
fi

echo "RECHECK PASS"
echo "[STEP 2] Start Memory Runtime Runner"
python3 runtime/memory_runtime_runner.py
