import json
from pathlib import Path

def read_manifest(pack_path):
    manifest_path = Path(pack_path) / "manifest.json"

    if not manifest_path.exists():
        return None

    try:
        with manifest_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data

    except (json.JSONDecodeError, OSError):
        return None


def get_pack_info(pack_path):
    data = read_manifest(pack_path)

    if not data:
        return {
            "valid": False,
            "reason": "Invalid or missing manifest"
        }

    header = data.get("header", {})

    return {
        "valid": True,
        "name": header.get("name", "Unknown"),
        "description": header.get("description", ""),
        "uuid": header.get("uuid"),
        "version": header.get("version"),
        "min_engine_version": header.get("min_engine_version")
    }
