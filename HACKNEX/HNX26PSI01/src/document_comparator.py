from collections import defaultdict


def compare_documents(document_a: dict, document_b: dict) -> dict:
    a_items = document_a.get("items", [])
    b_items = document_b.get("items", [])

    def collect_numbers(items):
        numbers = []
        for item in items:
            text = str(item.get("content", ""))
            for token in text.replace(",", "").split():
                try:
                    numbers.append(float(token))
                except ValueError:
                    pass
        return numbers

    a_numbers = collect_numbers(a_items)
    b_numbers = collect_numbers(b_items)

    return {
        "document_a": document_a.get("document"),
        "document_b": document_b.get("document"),
        "page_count_a": document_a.get("pages", 0),
        "page_count_b": document_b.get("pages", 0),
        "numeric_values_a": a_numbers[:10],
        "numeric_values_b": b_numbers[:10],
        "summary": "Comparison prepared from the two documents. Review source evidence in the page previews.",
    }
