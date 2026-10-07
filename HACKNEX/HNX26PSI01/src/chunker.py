import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


def split_text_into_chunks(text: str, chunk_size: int = 400, chunk_overlap: int = 60):
    if not text:
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - chunk_overlap

    return [chunk for chunk in chunks if chunk.strip()]


def build_chunks(document_data: list[dict], chunk_size: int = 400, chunk_overlap: int = 60) -> list[dict]:
    chunks = []
    for item in document_data:
        content = (item.get("content") or "").strip()
        if not content:
            if item.get("type") == "visual":
                content = "Visual page requires chart or image analysis."
            else:
                continue

        section = item.get("metadata", {}).get("section", "") or "general"
        split_chunks = split_text_into_chunks(content, chunk_size, chunk_overlap)
        for index, chunk_text in enumerate(split_chunks):
            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "document": item.get("document"),
                    "page": item.get("page"),
                    "type": item.get("type"),
                    "content": chunk_text,
                    "image_path": item.get("image_path"),
                    "section": section,
                    "metadata": {"chunk_index": index, "original_type": item.get("type")},
                }
            )

    logger.info("Created %s chunks", len(chunks))
    return chunks
