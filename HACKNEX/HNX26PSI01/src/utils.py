import hashlib
import json
from pathlib import Path


def compute_file_hash(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(path: str):
    file = Path(path)
    if not file.exists():
        return []
    with open(file, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, payload):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def clean_text(value: str) -> str:
    return (value or "").replace("\r", " ").replace("\n", " ").strip()
