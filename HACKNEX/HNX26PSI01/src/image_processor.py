from pathlib import Path


def build_visual_item(document: str, page: int, image_path: str) -> dict:
    return {
        "document": document,
        "page": page,
        "type": "visual",
        "content": "",
        "image_path": image_path,
        "metadata": {
            "visual_reasoning_required": True,
            "preserved_page_image": True,
        },
    }


def persist_visual_reference(document: str, page: int, image_path: str) -> dict:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    return build_visual_item(document, page, str(path))
