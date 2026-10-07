import logging
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: Iterable[str]):
        text_list = list(texts)
        embeddings = self.model.encode(text_list, convert_to_numpy=True, show_progress_bar=False)
        return np.asarray(embeddings, dtype="float32")


def generate_embeddings(chunks: list[dict], model_name: str = "all-MiniLM-L6-v2") -> tuple[list[np.ndarray], list[dict]]:
    engine = EmbeddingEngine(model_name=model_name)
    texts = [chunk["content"] for chunk in chunks]
    embeddings = engine.encode(texts)
    logger.info("Generated %s embeddings", len(embeddings))
    return embeddings.tolist(), chunks
