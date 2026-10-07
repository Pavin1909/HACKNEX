import logging
import re

import numpy as np

from src.embeddings import EmbeddingEngine

logger = logging.getLogger(__name__)


def _extract_terms(text: str):
    return set(re.findall(r"[a-zA-Z0-9]+", (text or "").lower()))


def hybrid_retrieve(question: str, vector_store, top_k: int = 5, model_name: str = "all-MiniLM-L6-v2"):
    if vector_store is None or getattr(vector_store, "index", None) is None or vector_store.index.ntotal == 0:
        return []

    engine = EmbeddingEngine(model_name=model_name)
    query_vector = engine.encode([question])[0]
    search_results = vector_store.search(np.asarray(query_vector, dtype="float32"), top_k=max(top_k * 2, top_k))

    question_terms = _extract_terms(question)
    adjusted = []
    for result in search_results:
        content = str(result.get("content", ""))
        overlap = len(question_terms & _extract_terms(content))
        content_bonus = 0.08 * overlap
        semantic_score = 1.0 / (1.0 + float(result.get("score", 0.0)))
        result["score"] = round(semantic_score + content_bonus, 6)
        result["keyword_overlap"] = overlap
        adjusted.append(result)

    adjusted.sort(key=lambda item: item.get("score", 0.0), reverse=True)
    logger.info("Hybrid retrieval returned %s supporting chunks for the query.", len(adjusted))
    return adjusted[:top_k]


def retrieve_relevant_chunks(question: str, vector_store, top_k: int = 5, model_name: str = "all-MiniLM-L6-v2"):
    return hybrid_retrieve(question, vector_store, top_k=top_k, model_name=model_name)
