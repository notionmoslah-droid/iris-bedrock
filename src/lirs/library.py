import json
from pathlib import Path

DEFAULT_LIBRARY = Path("lirs_library.json")


def load_library(path=DEFAULT_LIBRARY):
    path = Path(path)

    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def save_library(items, path=DEFAULT_LIBRARY):
    path = Path(path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(items, file, indent=4, ensure_ascii=False)


def add_pack(pack, path=DEFAULT_LIBRARY):
    library = load_library(path)

    if any(item.get("source") == pack.get("source") for item in library):
        return False

    library.append(pack)
    save_library(library, path)

    return True


def list_packs(path=DEFAULT_LIBRARY):
    return load_library(path)
