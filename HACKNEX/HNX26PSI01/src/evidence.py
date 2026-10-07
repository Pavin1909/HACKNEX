import statistics


def verify_evidence(question: str, evidence: list[dict], question_type: str = "TEXT") -> dict:
    if not evidence:
        return {
            "supported": False,
            "confidence_value": 0.0,
            "confidence_label": "Low",
            "reason": "No relevant evidence found.",
        }

    scores = []
    for item in evidence:
        score = float(item.get("rerank_score", item.get("score", 0.0)))
        scores.append(score)

    avg_score = statistics.mean(scores) if scores else 0.0
    evidence_count = len(evidence)
    base = 0.35 + min(0.45, avg_score / 2.0)
    support_bonus = min(0.2, evidence_count * 0.05)
    confidence_value = min(0.99, max(0.12, base + support_bonus))

    if confidence_value >= 0.75:
        label = "High"
    elif confidence_value >= 0.45:
        label = "Medium"
    else:
        label = "Low"

    supported = confidence_value >= 0.45 and evidence_count > 0
    return {
        "supported": supported,
        "confidence_value": round(confidence_value, 2),
        "confidence_label": label,
        "reason": "Evidence is present and supports the answer." if supported else "Evidence is insufficient or weak.",
    }
