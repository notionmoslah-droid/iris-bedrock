
import json
import os
import tempfile
from pathlib import Path

DEFAULT_LIBRARY = Path("lirs_library.json")


def load_library(path=DEFAULT_LIBRARY):
    path = Path(path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
        raise ValueError(
            f"Cannot read library safely: {error}"
        ) from error

    if not isinstance(data, list):
        raise ValueError("Library file must contain a JSON list")

    if not all(isinstance(item, dict) for item in data):
        raise ValueError("Every library entry must be a JSON object")

    return data


def save_library(items, path=DEFAULT_LIBRARY):
    path = Path(path)

    if not isinstance(items, list):
        raise TypeError("Library data must be a list")

    if not all(isinstance(item, dict) for item in items):
        raise TypeError("Every library entry must be a dictionary")

    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            delete=False
        ) as file:
            json.dump(items, file, indent=4, ensure_ascii=False)
            file.write("\n")
            temp_path = Path(file.name)

        os.replace(temp_path, path)

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def add_pack(pack, path=DEFAULT_LIBRARY):
    if not isinstance(pack, dict):
        raise TypeError("Pack must be a dictionary")

    library = load_library(path)
    source = pack.get("source")

    if not source:
        raise ValueError("Pack source is required")

    if any(item.get("source") == source for item in library):
        return False

    library.append(pack)
    save_library(library, path)
    return True


def list_packs(path=DEFAULT_LIBRARY):
    return load_library(path)
