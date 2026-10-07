import re


def extract_entities(text: str) -> dict:
    content = text or ""
    entities = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": [],
        "money": [],
        "percentages": [],
    }

    for match in re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content):
        entities["persons"].append(match)

    for match in re.findall(r"\b(?:Inc|LLC|Ltd|Corp|Company|Group|Department|Bank|University)\b", content, flags=re.IGNORECASE):
        entities["organizations"].append(match)

    for match in re.findall(r"\b(?:USA|UK|Europe|Asia|America|India|Canada|London|New York|Tokyo|Germany|France)\b", content, flags=re.IGNORECASE):
        entities["locations"].append(match)

    for match in re.findall(r"\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", content, flags=re.IGNORECASE):
        entities["dates"].append(match)

    for match in re.findall(r"\$\s?\d+(?:,\d{3})*(?:\.\d+)?|\d+(?:,\d{3})*(?:\.\d+)?\s*(?:USD|EUR|GBP)", content, flags=re.IGNORECASE):
        entities["money"].append(match)

    for match in re.findall(r"\d+(?:\.\d+)?%", content):
        entities["percentages"].append(match)

    return {key: sorted(set(value)) for key, value in entities.items() if value}
