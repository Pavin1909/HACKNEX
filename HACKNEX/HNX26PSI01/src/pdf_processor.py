import logging
from pathlib import Path

import fitz

from src.config import PAGES_DIR

logger = logging.getLogger(__name__)


def safe_pdf_name(file_name: str) -> str:
    return Path(file_name).stem.replace(" ", "_")


def extract_pdf_pages(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if path.stat().st_size <= 0:
        raise ValueError(f"PDF is empty or unreadable: {file_path}")

    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        raise ValueError(f"Invalid or corrupted PDF: {file_path}") from exc

    if doc.is_encrypted:
        try:
            doc.authenticate("")
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"PDF is encrypted and cannot be opened: {file_path}") from exc

    pdf_name = Path(file_path).name
    base_name = safe_pdf_name(pdf_name)
    page_items = []

    for page_number in range(1, doc.page_count + 1):
        page = doc[page_number - 1]
        page_text = page.get_text("text") or ""
        image_path = PAGES_DIR / f"{base_name}_page_{page_number}.png"

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        pix.save(str(image_path))

        item = {
            "document": pdf_name,
            "page": page_number,
            "type": "text" if page_text.strip() else "visual",
            "content": page_text.strip(),
            "image_path": str(image_path),
            "metadata": {
                "page_width": float(page.rect.width),
                "page_height": float(page.rect.height),
                "section": "",
                "source": "pdf_text",
            },
        }
        page_items.append(item)
        logger.info("Processed page %s of %s", page_number, pdf_name)

    doc.close()

    return {
        "document": pdf_name,
        "pages": len(page_items),
        "items": page_items,
    }
