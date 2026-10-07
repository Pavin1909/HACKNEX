import re


def classify_question(question: str) -> str:
    if not question:
        return "GENERAL"

    text = question.lower().strip()
    tokens = re.findall(r"[a-z0-9]+", text)

    if any(word in text for word in ["compare", "comparison", "versus", "between", "across", "difference", "contrast"]):
        return "COMPARISON"
    if any(word in text for word in ["chart", "graph", "bar", "pie", "line", "trend", "visual", "diagram", "according to the chart"]):
        return "CHART"
    if any(word in text for word in ["image", "picture", "photo", "diagram", "figure", "logo", "screenshot"]):
        return "IMAGE"
    if any(word in text for word in ["percentage", "increase", "decrease", "average", "median", "ratio", "sum", "total", "growth", "difference", "calculate"]):
        return "CALCULATION"
    if any(word in text for word in ["table", "row", "column", "quarter", "product", "sales", "revenue", "profit"]):
        return "TABLE"
    if any(word in text for word in ["summarize", "summary", "overview", "key points"]):
        return "SUMMARY"
    if any(word in text for word in ["timeline", "when", "date", "event", "month", "year", "march", "january", "april"]):
        return "TIMELINE"
    if any(word in text for word in ["who", "person", "organization", "company", "location", "where", "which company", "which person"]):
        return "ENTITY"
    if any(word in text for word in ["which page", "page contains", "where is", "page number", "located on page"]):
        return "TEXT"
    if any(word in text for word in ["document a", "document b", "another document", "across documents", "multi-document"]):
        return "MULTI_DOCUMENT"

    if len(tokens) <= 4:
        return "TEXT"
    return "TEXT"
