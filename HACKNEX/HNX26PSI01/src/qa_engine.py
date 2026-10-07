import logging

from src.calculator import detect_calculation, evaluate_calculation
from src.evidence import verify_evidence
from src.llm import generate_grounded_answer
from src.query_classifier import classify_question
from src.vision import requires_visual_analysis

logger = logging.getLogger(__name__)


def detect_question_type(question: str) -> str:
    lower = question.lower()
    if any(token in lower for token in ["chart", "graph", "image", "visual", "pie", "bar", "trend", "diagram"]):
        return "chart_question"
    if any(token in lower for token in ["compare", "difference", "versus", "between", "across"]):
        return "comparison"
    if any(token in lower for token in ["percentage", "increase", "decrease", "average", "ratio", "total", "sum", "difference"]):
        return "calculation"
    if any(token in lower for token in ["table", "row", "column", "quarter", "sales", "revenue"]):
        return "table_question"
    if any(token in lower for token in ["which page", "page contains", "where is"]):
        return "page_lookup"
    return "factual_text_question"


def answer_question(question: str, evidence: list[dict], model_name: str = "gpt-4o-mini", query_type: str | None = None) -> dict:
    if not evidence:
        return {
            "answer": "I could not determine the answer from the provided documents.",
            "sources": [],
            "question_type": "no_evidence",
            "calculation": {"used": False},
            "confidence": "Low",
            "confidence_value": 0.0,
        }

    question_type = query_type or classify_question(question) or detect_question_type(question)
    evidence_check = verify_evidence(question, evidence, question_type)
    calculation = evaluate_calculation(question, evidence) if detect_calculation(question, evidence) else {"used": False}
    visual_required = requires_visual_analysis(question)

    if visual_required:
        visual_result = {
            "required": True,
            "answer": "Visual analysis is required for this question, but no vision model is configured.",
        }
        return {
            "answer": visual_result["answer"],
            "sources": evidence,
            "question_type": question_type,
            "calculation": calculation,
            "visual": visual_result,
            "confidence": evidence_check["confidence_label"],
            "confidence_value": evidence_check["confidence_value"],
            "evidence_verified": evidence_check["supported"],
        }

    llm_result = generate_grounded_answer(question, evidence, model_name=model_name)
    answer = llm_result["answer"]
    return {
        "answer": answer,
        "sources": evidence,
        "question_type": question_type,
        "calculation": calculation,
        "visual": {"required": False, "answer": ""},
        "confidence": evidence_check["confidence_label"],
        "confidence_value": evidence_check["confidence_value"],
        "evidence_verified": evidence_check["supported"],
    }
