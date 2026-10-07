import re


def rerank_evidence(question: str, evidence: list[dict], top_k: int = 5) -> list[dict]:
    if not evidence:
        return []

    question_terms = set(re.findall(r"[a-zA-Z0-9]+", question.lower()))
    reranked = []
    for item in evidence:
        content = str(item.get("content", "")).lower()
        content_terms = set(re.findall(r"[a-zA-Z0-9]+", content))
        overlap = len(question_terms & content_terms)
        score = float(item.get("score", 0.0))
        score += overlap * 0.12
        if item.get("type") == "table":
            score += 0.08
        if item.get("type") == "ocr":
            score += 0.04
        if item.get("image_path"):
            score += 0.02
        if len(content) > 120:
            score += 0.03
        reranked.append({**item, "rerank_score": round(score, 4)})

    reranked.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
    return reranked[:top_k]
