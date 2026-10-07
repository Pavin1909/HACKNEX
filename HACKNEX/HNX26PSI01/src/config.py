import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
PROCESSED_DIR = PROJECT_ROOT / "processed"
PAGES_DIR = PROCESSED_DIR / "pages"
IMAGES_DIR = PROCESSED_DIR / "images"
TABLES_DIR = PROCESSED_DIR / "tables"
OUTPUT_DIR = PROJECT_ROOT / "output"
VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"


def ensure_directories() -> None:
    for directory in [DOCUMENTS_DIR, PROCESSED_DIR, PAGES_DIR, IMAGES_DIR, TABLES_DIR, OUTPUT_DIR, VECTOR_STORE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def get_setting(name: str, default: Any = None) -> Any:
    value = os.getenv(name, default)
    if value is None:
        return default
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if isinstance(value, str) and value.strip() == "":
        return default
    return value


def get_llm_config() -> dict:
    return {
        "provider": get_setting("LLM_PROVIDER", "openai"),
        "api_key": get_setting("API_KEY"),
        "model_name": get_setting("MODEL_NAME", "gpt-4o-mini"),
    }


def get_vision_config() -> dict:
    return {
        "provider": get_setting("VISION_PROVIDER", ""),
        "api_key": get_setting("VISION_API_KEY"),
        "model": get_setting("VISION_MODEL", ""),
    }


ensure_directories()
