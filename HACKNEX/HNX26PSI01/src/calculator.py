import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def extract_numbers(text: str):
    numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
    return [float(value) for value in numbers]


def detect_calculation(question: str, evidence: list[dict]) -> bool:
    if not evidence:
        return False
    text = " ".join(item.get("content", "") for item in evidence).lower()
    keywords = [
        "percentage",
        "increase",
        "decrease",
        "average",
        "ratio",
        "sum",
        "total",
        "difference",
        "multiply",
        "divide",
        "plus",
        "minus",
        "profit",
        "revenue",
    ]
    lower_question = question.lower()
    return any(keyword in lower_question for keyword in keywords) or any(keyword in text for keyword in keywords)


def calculate_percentage_increase(start_value: float, end_value: float) -> float:
    if start_value == 0:
        return 0.0
    return ((end_value - start_value) / start_value) * 100


def calculate_percentage_decrease(start_value: float, end_value: float) -> float:
    if start_value == 0:
        return 0.0
    return ((start_value - end_value) / start_value) * 100


def calculate_average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def evaluate_calculation(question: str, evidence: list[dict]) -> dict:
    if not detect_calculation(question, evidence):
        return {"used": False, "formula": "", "result": None}

    numbers = []
    for item in evidence:
        numbers.extend(extract_numbers(item.get("content", "")))
    if len(numbers) < 2:
        return {"used": False, "formula": "", "result": None}

    q = question.lower()
    if "percentage increase" in q or "increase from" in q:
        start, end = numbers[0], numbers[-1]
        result = calculate_percentage_increase(start, end)
        return {
            "used": True,
            "formula": "((end - start) / start) * 100",
            "values": {"start": start, "end": end},
            "result": result,
        }

    if "percentage decrease" in q or "decrease from" in q:
        start, end = numbers[0], numbers[-1]
        result = calculate_percentage_decrease(start, end)
        return {
            "used": True,
            "formula": "((start - end) / start) * 100",
            "values": {"start": start, "end": end},
            "result": result,
        }

    if "average" in q:
        avg = calculate_average(numbers)
        return {"used": True, "formula": "sum(values) / count(values)", "values": {"values": numbers}, "result": avg}

    if "difference" in q:
        result = numbers[0] - numbers[-1]
        return {"used": True, "formula": "first - last", "values": {"a": numbers[0], "b": numbers[-1]}, "result": result}

    if "total" in q or "sum" in q:
        result = sum(numbers)
        return {"used": True, "formula": "sum(values)", "values": {"values": numbers}, "result": result}

    return {"used": True, "formula": "manual calculation", "values": {"numbers": numbers}, "result": numbers[0] if numbers else None}
