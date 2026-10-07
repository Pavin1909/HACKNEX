import json
import logging
from pathlib import Path

import faiss
import numpy as np

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []

    def add(self, embeddings: np.ndarray, metadata: list[dict]):
        if embeddings.size == 0:
            return
        vectors = np.asarray(embeddings, dtype="float32")
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def save(self, directory: str):
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path / "faiss_index.index"))
        with open(path / "metadata.json", "w", encoding="utf-8") as handle:
            json.dump(self.metadata, handle, ensure_ascii=False, indent=2)

    def load(self, directory: str):
        path = Path(directory)
        if not (path / "faiss_index.index").exists():
            raise FileNotFoundError(f"Vector index not found in {directory}")
        self.index = faiss.read_index(str(path / "faiss_index.index"))
        with open(path / "metadata.json", "r", encoding="utf-8") as handle:
            self.metadata = json.load(handle)
        self.dimension = self.index.d

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        if self.index.ntotal == 0:
            return []
        vector = np.asarray(query_vector, dtype="float32").reshape(1, -1)
        distances, indices = self.index.search(vector, min(top_k, self.index.ntotal))
        results = []
        for rank, idx in enumerate(indices[0]):
            if idx < 0:
                continue
            record = self.metadata[int(idx)]
            results.append({
                "index": int(idx),
                "document": record.get("document"),
                "page": record.get("page"),
                "type": record.get("type"),
                "content": record.get("content"),
                "image_path": record.get("image_path"),
                "score": float(distances[0][rank]),
            })
        return results
