import re


def extract_timeline(document_data: list[dict]) -> list[dict]:
    timeline = []
    for item in document_data:
        text = item.get("content", "") or ""
        dates = re.findall(r"\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", text, flags=re.IGNORECASE)
        if dates:
            timeline.append({
                "document": item.get("document"),
                "page": item.get("page"),
                "date": dates[0],
                "event": text[:120],
            })
    return timeline
