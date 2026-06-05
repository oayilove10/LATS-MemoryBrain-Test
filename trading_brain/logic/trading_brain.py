# LATS V3 V1
# Trading Brain

from pattern import build_pattern
from similarity import (
    score_similarity_detail,
)
from weight import get_weight
from decision import (
    calc_final_score,
    classify_decision,
)
from play_skip import classify_play_skip
from execution import classify_execution


def run_trading_brain(
    signal,
    memory,
    weights,
):

    pattern = build_pattern(signal)

    similarity, score_detail = score_similarity_detail(
        signal,
        memory,
    )

    weight = get_weight(
        memory["memory_id"],
        weights,
    )

    final_score = calc_final_score(
        similarity,
        weight,
    )

    decision = classify_decision(
        final_score,
    )

    play_action = classify_play_skip(
        decision,
    )

    execution_mode = classify_execution(
        play_action,
    )

    return {
        "pattern": pattern,
        "similarity": similarity,
        "score_detail": score_detail,
        "weight": weight,
        "final_score": final_score,
        "decision": decision,
        "play_action": play_action,
        "execution_mode": execution_mode,
    }


if __name__ == "__main__":

    signal = {
        "cycle": "continue_up",
        "trend": "up",
        "zone": "support",
        "direction": "long",
        "symbol": "BTCUSDT",
        "pattern": "pullback",
    }

    memory = {
        "memory_id": "MEM001",
        "symbol": "BTCUSDT",
        "cycle": "continue_up",
        "trend": "up",
        "pattern": "pullback",
        "direction": "long",
        "zone": "support",
    }

    weights = {
        "MEM001": 1.5
    }

    result = run_trading_brain(
        signal,
        memory,
        weights,
    )

    print(result)
