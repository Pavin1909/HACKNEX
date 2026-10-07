import logging
from pathlib import Path

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def should_run_ocr(page_text: str, page_number: int = 0, enable_ocr: bool = True) -> bool:
    if not enable_ocr:
        return False
    cleaned = (page_text or "").strip()
    if not cleaned:
        return True
    if len(cleaned) < 25:
        return True
    return False


def extract_ocr_from_image(image_path: str, document: str, page: int) -> dict:
    if not Path(image_path).exists():
        return {}
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        cleaned = (text or "").strip()
        if not cleaned:
            return {"document": document, "page": page, "type": "ocr", "content": "", "image_path": image_path}
    except Exception as exc:  # pragma: no cover
        logger.warning("OCR failed for %s page %s: %s", document, page, exc)
        return {"document": document, "page": page, "type": "ocr", "content": "", "image_path": image_path, "error": str(exc)}

    return {
        "document": document,
        "page": page,
        "type": "ocr",
        "content": cleaned,
        "image_path": image_path,
        "metadata": {"ocr": True},
    }
