# LATS V3 V1
# Trading Brain - Decision Engine


def calc_final_score(similarity: float, weight: float) -> float:
    try:
        return round(float(similarity) * float(weight), 4)
    except Exception:
        return 0.0


def classify_decision(score: float) -> str:
    if score >= 120:
        return "ULTRA_STRONG_MATCH"

    if score >= 90:
        return "STRONG_MATCH"

    if score >= 70:
        return "GOOD_MATCH"

    if score >= 50:
        return "PARTIAL_MATCH"

    return "WEAK_MATCH"


if __name__ == "__main__":
    score = calc_final_score(80, 1.5)
    print(score)
    print(classify_decision(score))
