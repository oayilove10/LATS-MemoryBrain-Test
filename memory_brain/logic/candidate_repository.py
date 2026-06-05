# LATS P3
# Candidate Repository V2
#
# Purpose:
# - Store waiting_confirm memory candidates separately
# - Support Candidate Workflow before promotion
# - Write candidate.log via memory_logger
# - TEST first, no MAIN changes
#
# Status:
# - Safe JSON repository
# - No AI
# - No Risk Brain
# - No Execution Brain

import json
from pathlib import Path
from datetime import datetime

from memory_logger import log_candidate


BASE = Path.home() / "LATS_PRODUCTION_P3_TEST"

DATA_DIR = (
    BASE
    / "memory_brain"
    / "data"
)

CANDIDATE_DIR = (
    DATA_DIR
    / "candidates"
)

CANDIDATE_FILE = (
    CANDIDATE_DIR
    / "candidate_index.json"
)


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_candidate_dir():
    CANDIDATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def load_candidates():
    ensure_candidate_dir()

    if not CANDIDATE_FILE.exists():
        return []

    try:
        with CANDIDATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get("candidates", [])

        return []

    except Exception:
        return []


def save_candidates(candidates):
    ensure_candidate_dir()

    payload = {
        "schema": "candidate_repository_v2",
        "updated_at": now_text(),
        "total_candidates": len(candidates),
        "candidates": candidates,
    }

    with CANDIDATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return CANDIDATE_FILE


def make_candidate_id(memory):
    base = memory.get("memory_id") or ""
    symbol = memory.get("symbol") or "UNKNOWN"
    trend = memory.get("trend") or "NA"
    cycle = memory.get("cycle") or "NA"

    if base:
        return f"CAND_{base}"

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"CAND_{symbol}_{trend}_{cycle}_{stamp}"


def normalize_candidate(memory):
    item = dict(memory)

    item["candidate_id"] = (
        item.get("candidate_id")
        or make_candidate_id(item)
    )

    item["status"] = item.get(
        "status",
        "waiting_confirm",
    )

    item["created_at"] = item.get(
        "created_at",
        now_text(),
    )

    item["updated_at"] = now_text()

    item["evidence_count"] = int(
        item.get("evidence_count", 0) or 0
    )

    item["hit_count"] = int(
        item.get("hit_count", 0) or 0
    )

    item["confirmed_count"] = int(
        item.get("confirmed_count", 0) or 0
    )

    item["examples"] = item.get("examples", [])

    item["example_count"] = len(
        item.get("examples", [])
    )

    return item


def candidate_log_payload(item):
    return {
        "candidate_id": item.get("candidate_id"),
        "memory_id": item.get("memory_id"),
        "symbol": item.get("symbol"),
        "trend": item.get("trend"),
        "cycle": item.get("cycle"),
        "status": item.get("status"),
        "evidence_count": item.get("evidence_count", 0),
        "hit_count": item.get("hit_count", 0),
        "example_count": item.get("example_count", 0),
    }


def find_candidate(candidate_id):
    candidates = load_candidates()

    for item in candidates:
        if item.get("candidate_id") == candidate_id:
            return item

    return None


def upsert_candidate(memory):
    candidate = normalize_candidate(memory)
    candidate_id = candidate.get("candidate_id")

    candidates = load_candidates()
    updated = False
    saved_item = candidate

    for i, old in enumerate(candidates):
        if old.get("candidate_id") == candidate_id:
            merged = dict(old)
            merged.update(candidate)

            old_examples = old.get("examples", [])
            new_examples = candidate.get("examples", [])
            merged_examples = []

            for ex in old_examples + new_examples:
                if ex not in merged_examples:
                    merged_examples.append(ex)

            merged["examples"] = merged_examples[-10:]
            merged["example_count"] = len(merged["examples"])

            merged["hit_count"] = int(
                old.get("hit_count", 0) or 0
            ) + int(
                candidate.get("hit_count", 0) or 0
            )

            merged["evidence_count"] = int(
                old.get("evidence_count", 0) or 0
            ) + int(
                candidate.get("evidence_count", 0) or 0
            )

            merged["updated_at"] = now_text()

            candidates[i] = merged
            updated = True
            saved_item = merged
            break

    if not updated:
        candidates.append(candidate)
        saved_item = candidate

    save_candidates(candidates)

    if updated:
        log_candidate(
            "UPSERT_CANDIDATE_UPDATE",
            candidate_log_payload(saved_item),
        )
    else:
        log_candidate(
            "UPSERT_CANDIDATE_NEW",
            candidate_log_payload(saved_item),
        )

    return saved_item


def list_candidates(status=None):
    candidates = load_candidates()

    if status is None:
        return candidates

    return [
        item
        for item in candidates
        if item.get("status") == status
    ]


def mark_candidate_confirmed(candidate_id):
    candidates = load_candidates()

    for item in candidates:
        if item.get("candidate_id") == candidate_id:
            item["status"] = "confirmed"
            item["confirmed_at"] = now_text()
            item["updated_at"] = now_text()

            save_candidates(candidates)

            log_candidate(
                "CONFIRM_CANDIDATE",
                candidate_log_payload(item),
            )

            return item

    return None


def mark_candidate_rejected(candidate_id, reason=""):
    candidates = load_candidates()

    for item in candidates:
        if item.get("candidate_id") == candidate_id:
            item["status"] = "rejected"
            item["rejected_at"] = now_text()
            item["reject_reason"] = reason
            item["updated_at"] = now_text()

            save_candidates(candidates)

            payload = candidate_log_payload(item)
            payload["reject_reason"] = reason

            log_candidate(
                "REJECT_CANDIDATE",
                payload,
            )

            return item

    return None


def candidate_repository_stats():
    candidates = load_candidates()

    waiting = [
        c for c in candidates
        if c.get("status") == "waiting_confirm"
    ]

    confirmed = [
        c for c in candidates
        if c.get("status") == "confirmed"
    ]

    rejected = [
        c for c in candidates
        if c.get("status") == "rejected"
    ]

    return {
        "status": "OK",
        "file": str(CANDIDATE_FILE),
        "total_candidates": len(candidates),
        "waiting_confirm": len(waiting),
        "confirmed": len(confirmed),
        "rejected": len(rejected),
        "updated_at": now_text(),
    }


if __name__ == "__main__":
    sample = {
        "memory_id": "MEM_CAND_LOG_TEST_001",
        "symbol": "BTCUSDT",
        "trend": "up",
        "cycle": "continue_up",
        "status": "waiting_confirm",
        "examples": ["EVENT_CAND_LOG_TEST_001"],
        "evidence_count": 1,
        "hit_count": 1,
    }

    saved = upsert_candidate(sample)

    print("[SAVED]")
    print(saved)

    confirmed = mark_candidate_confirmed(
        saved.get("candidate_id")
    )

    print("[CONFIRMED]")
    print(confirmed)

    print("[STATS]")
    print(candidate_repository_stats())
