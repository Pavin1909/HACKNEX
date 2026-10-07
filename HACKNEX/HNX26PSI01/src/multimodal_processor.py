import json
import logging
from pathlib import Path

from src.config import OUTPUT_DIR, get_setting
from src.ocr_processor import extract_ocr_from_image, should_run_ocr
from src.pdf_processor import extract_pdf_pages
from src.table_processor import extract_tables_from_pdf

logger = logging.getLogger(__name__)


def process_document(file_path: str, enable_ocr: bool = True) -> dict:
    pdf_info = extract_pdf_pages(file_path)
    document_name = pdf_info["document"]
    page_items = list(pdf_info["items"])

    tables = extract_tables_from_pdf(file_path)
    for table in tables:
        table["image_path"] = next(
            (
                item["image_path"]
                for item in page_items
                if item["document"] == table["document"] and item["page"] == table["page"]
            ),
            "",
        )
        page_items.append(
            {
                "document": table["document"],
                "page": table["page"],
                "type": "table",
                "content": table["content"],
                "image_path": table["image_path"],
                "metadata": table["metadata"],
            }
        )

    for item in page_items:
        if item.get("type") == "visual":
            continue
        if item.get("content", "").strip() and len(item["content"].strip()) > 25:
            continue
        if not enable_ocr:
            continue
        if should_run_ocr(item.get("content", ""), item.get("page", 0), enable_ocr=True):
            ocr_item = extract_ocr_from_image(item["image_path"], item["document"], item["page"])
            if ocr_item and ocr_item.get("content"):
                page_items.append(ocr_item)

    document_data = sorted(page_items, key=lambda x: (x["page"], x["type"]))
    output_path = OUTPUT_DIR / "document_data.json"
    output_path.write_text(json.dumps(document_data, indent=2), encoding="utf-8")

    logger.info("Saved document data for %s to %s", document_name, output_path)
    return {
        "document": document_name,
        "pages": pdf_info["pages"],
        "items": document_data,
        "table_count": len(tables),
        "ocr_enabled": enable_ocr,
    }


def process_documents(file_paths: list[str], enable_ocr: bool = True) -> list[dict]:
    results = []
    for file_path in file_paths:
        try:
            results.append(process_document(file_path, enable_ocr=enable_ocr))
        except Exception as exc:
            logger.warning("Skipping invalid or unreadable document %s: %s", file_path, exc)
    return results
