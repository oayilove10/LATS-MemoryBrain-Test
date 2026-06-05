# LATS P3
# One Click Recheck Room V1
#
# Purpose:
# - Run full Recheck / Repair dry-run pipeline with one command
#
# Flow:
# 1. Recheck Path
# 2. Repair Job Builder
# 3. Duplicate Guard
# 4. Repair Validator
# 5. Backfill Runner DRY RUN
#
# Rules:
# - No Memory update
# - No hit_count update
# - No candidate confirm/promote
# - No write to signal/result
# - No API fetch in V1

import subprocess
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "LATS_PRODUCTION_P3_TEST"

STEPS = [
    {
        "name": "RECHECK_PATH",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "recheck_path.py"),
        ],
        "allow_fail": True,
    },
    {
        "name": "REPAIR_JOB_BUILDER",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "repair" / "repair_job_builder.py"),
        ],
        "allow_fail": False,
    },
    {
        "name": "DUPLICATE_GUARD",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "repair" / "duplicate_guard.py"),
        ],
        "allow_fail": False,
    },
    {
        "name": "REPAIR_VALIDATOR",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "repair" / "repair_validator.py"),
        ],
        "allow_fail": False,
    },
    {
        "name": "BACKFILL_DRY_RUN",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "repair" / "backfill_runner.py"),
        ],
        "allow_fail": False,
    },
    {
        "name": "REPAIR_EXECUTION_PLAN",
        "cmd": [
            "python3",
            str(ROOT / "runtime" / "recheck" / "repair" / "repair_execution_plan.py"),
        ],
        "allow_fail": False,
    },
]


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def run_step(step):
    print("\n" + "=" * 80)
    print(step["name"])
    print("=" * 80)

    result = subprocess.run(
        step["cmd"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("[STDERR]")
        print(result.stderr)

    status = "PASS"

    if result.returncode != 0:
        if step.get("allow_fail"):
            status = "WARN_ALLOWED"
        else:
            status = "FAIL"

    return {
        "name": step["name"],
        "status": status,
        "returncode": result.returncode,
        "allow_fail": step.get("allow_fail", False),
    }


def main():
    print("=" * 80)
    print("LATS P3 ONE CLICK RECHECK ROOM V1")
    print("=" * 80)
    print("time:", now_text())
    print("mode: DRY_RUN")
    print("memory_update: False")
    print("api_fetch: False")
    print("write_signal_result: False")

    results = []

    for step in STEPS:
        item = run_step(step)
        results.append(item)

        if item["status"] == "FAIL":
            break

    final_status = "PASS"

    hard_fail = [
        r for r in results
        if r["status"] == "FAIL"
    ]

    warn_allowed = [
        r for r in results
        if r["status"] == "WARN_ALLOWED"
    ]

    if hard_fail:
        final_status = "FAIL"
    elif warn_allowed:
        final_status = "PASS_WITH_REPAIR_REQUIRED"

    print("\n" + "=" * 80)
    print("ONE CLICK SUMMARY")
    print("=" * 80)

    for r in results:
        print(
            r["status"],
            "|",
            r["name"],
            "| returncode:",
            r["returncode"],
        )

    print("\nfinal_status:", final_status)

    if final_status == "PASS_WITH_REPAIR_REQUIRED":
        print("next_action: RUN_BLOCKED_UNTIL_BACKFILL")
    elif final_status == "PASS":
        print("next_action: RUN_ALLOWED")
    else:
        print("next_action: STOP_AND_REVIEW")

    print("\n[RULE]")
    print("One Click Recheck Room does not update Memory Brain")
    print("Backfill is DRY RUN only in V1")

    if final_status == "FAIL":
        raise SystemExit(1)

    if final_status == "PASS_WITH_REPAIR_REQUIRED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
