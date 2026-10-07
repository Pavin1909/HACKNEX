import logging
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


def table_to_text(table_rows):
    if not table_rows:
        return ""
    rows = []
    for row in table_rows:
        cleaned = ["" if cell is None else str(cell).strip() for cell in row]
        rows.append(" | ".join(cleaned))
    return "\n".join(rows)


def extract_tables_from_pdf(pdf_path: str) -> list[dict]:
    results = []
    if not Path(pdf_path).exists():
        return results

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables()
                    for table_index, table in enumerate(tables or [], start=1):
                        table_text = table_to_text(table)
                        if not table_text.strip():
                            continue
                        rows = len(table)
                        columns = max(len(r) for r in table) if table else 0
                        results.append(
                            {
                                "document": Path(pdf_path).name,
                                "page": page_number,
                                "type": "table",
                                "table_number": table_index,
                                "rows": rows,
                                "columns": columns,
                                "content": table_text,
                                "image_path": "",
                                "metadata": {"table_number": table_index, "rows": rows, "columns": columns},
                            }
                        )
                except Exception as exc:  # pragma: no cover
                    logger.warning("Table extraction failed on page %s of %s: %s", page_number, pdf_path, exc)
    except Exception as exc:  # pragma: no cover
        logger.warning("Table extraction failed for %s: %s", pdf_path, exc)

    return results
