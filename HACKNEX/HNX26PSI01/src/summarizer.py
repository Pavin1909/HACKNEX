def summarize_document_data(document_data: list[dict]) -> dict:
    if not document_data:
        return {
            "document": "unknown",
            "page_count": 0,
            "text_pages": 0,
            "table_count": 0,
            "visual_pages": 0,
            "topics": [],
            "summary": "No document data available for summary.",
        }

    pages = {item.get("page") for item in document_data}
    text_pages = sum(1 for item in document_data if item.get("type") in {"text", "ocr"})
    table_count = sum(1 for item in document_data if item.get("type") == "table")
    visual_pages = sum(1 for item in document_data if item.get("type") in {"visual"})

    topics = []
    for item in document_data[:10]:
        content = str(item.get("content", ""))
        if content and len(content) > 15:
            topics.append(content[:80])

    return {
        "document": document_data[0].get("document", "unknown"),
        "page_count": len(pages),
        "text_pages": text_pages,
        "table_count": table_count,
        "visual_pages": visual_pages,
        "topics": topics,
        "summary": "Document processed. Key evidence extracted from text and table content. Review source pages for deeper analysis.",
    }
