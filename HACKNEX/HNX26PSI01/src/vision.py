import logging

logger = logging.getLogger(__name__)


def requires_visual_analysis(question: str) -> bool:
    question_lower = question.lower()
    keywords = [
        "chart",
        "graph",
        "image",
        "diagram",
        "visual",
        "bar",
        "pie",
        "line",
        "trend",
        "plot",
        "figure",
    ]
    return any(keyword in question_lower for keyword in keywords)


def analyze_visual_question(question: str, evidence: list[dict], image_path: str = "") -> dict:
    if not evidence:
        return {
            "required": True,
            "answer": "Visual analysis is required for this question, but no vision model is configured.",
        }

    config = {"provider": "", "api_key": "", "model": ""}
    if not config["provider"] or not config["api_key"]:
        return {
            "required": True,
            "answer": "Visual analysis is required for this question, but no vision model is configured.",
        }

    logger.info("Visual analysis requested for %s", question)
    return {
        "required": True,
        "answer": "Visual analysis is required for this question, but no vision model is configured.",
    }
