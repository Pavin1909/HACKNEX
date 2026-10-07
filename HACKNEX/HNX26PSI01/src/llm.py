import json
import logging
import re
from typing import Any

import requests

from src.config import get_llm_config

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "You are a document question-answering system. "
    "Answer ONLY using the supplied evidence. "
    "If the evidence does not contain enough information to answer the question, say: "
    "'I could not determine the answer from the provided documents.' "
    "Do not invent numbers. Do not invent page numbers. Do not invent document names. "
    "Do not assume missing values."
)


def format_evidence_for_llm(evidence: list[dict]) -> str:
    if not evidence:
        return "No evidence provided."
    blocks = []
    for idx, item in enumerate(evidence, start=1):
        if not item.get("content"):
            continue
        blocks.append(
            f"{idx}. Document: {item.get('document', 'unknown')} | Page: {item.get('page', 'unknown')} | "
            f"Type: {item.get('type', 'unknown')} | Evidence: {item.get('content', '')}"
        )
    return "\n".join(blocks)


def call_llm(prompt: str, model_name: str = "gpt-4o-mini") -> str:
    config = get_llm_config()
    provider = (config.get("provider") or "").lower()
    api_key = config.get("api_key")

    if not provider or not api_key or provider == "mock":
        return ""

    if provider != "openai":
        return ""

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # pragma: no cover
        logger.warning("LLM call failed: %s", exc)
        return ""


def fallback_answer_from_evidence(question: str, evidence: list[dict]) -> str:
    if not evidence:
        return "I could not determine the answer from the provided documents."

    q = question.lower()
    blocks = []
    for item in evidence:
        text = str(item.get("content") or "").strip()
        if text:
            blocks.append(text)

    evidence_text = " ".join(blocks)
    evidence_text = re.sub(r"\s+", " ", evidence_text).strip()

    if any(token in q for token in ["revenue", "sales", "profit", "margin", "income"]):
        match = re.search(r"(revenue|sales|profit|income|margin)[^\.]{0,120}(\$\s?\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?%)", evidence_text, flags=re.IGNORECASE)
        if match:
            return f"The evidence states: {match.group(0).strip()}"

    if any(token in q for token in ["increase", "decrease", "change", "growth", "up", "down"]):
        match = re.search(r"(increased|decreased|rose|fell|grew|dropped)[^\.]{0,120}(\d+(?:\.\d+)?%)", evidence_text, flags=re.IGNORECASE)
        if match:
            return f"The supporting evidence says: {match.group(0).strip()}"

    if any(token in q for token in ["page", "location", "where"]):
        page_info = []
        for item in evidence:
            page = item.get("page")
            doc = item.get("document")
            if page is not None:
                page_info.append(f"{doc} page {page}")
        if page_info:
            return "The most relevant evidence appears in: " + "; ".join(page_info[:3]) + "."

    if any(token in q for token in ["summarize", "summary", "overview", "key points"]):
        return "The document highlights the main findings in the extracted evidence: " + evidence_text[:300] + ("..." if len(evidence_text) > 300 else "")

    if evidence_text:
        return evidence_text[:500] + ("..." if len(evidence_text) > 500 else "")

    return "I could not determine the answer from the provided documents."


def generate_grounded_answer(question: str, evidence: list[dict], model_name: str = "gpt-4o-mini") -> dict:
    evidence_text = format_evidence_for_llm(evidence)
    prompt = (
        f"Question: {question}\n\n"
        f"Evidence:\n{evidence_text}\n\n"
        "Answer using only the provided evidence and cite the relevant document/page information in your response."
    )

    llm_answer = call_llm(prompt, model_name=model_name)
    if llm_answer:
        return {"answer": llm_answer, "source": "llm", "grounded": True}

    fallback = fallback_answer_from_evidence(question, evidence)
    return {
        "answer": fallback,
        "source": "fallback",
        "grounded": False,
    }
