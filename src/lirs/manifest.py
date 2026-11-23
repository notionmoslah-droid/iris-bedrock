
import json
from pathlib import Path


def read_manifest(pack_path):
    manifest_path = Path(pack_path) / "manifest.json"

    if not manifest_path.exists():
        return {
            "valid": False,
            "reason": "Missing manifest.json"
        }

    try:
        with manifest_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {
                "valid": False,
                "reason": "Manifest must be a JSON object"
            }

        header = data.get("header", {})

        if not isinstance(header, dict):
            return {
                "valid": False,
                "reason": "Invalid manifest header"
            }

        return {
            "valid": True,
            "name": header.get("name", "Unknown"),
            "description": header.get("description", ""),
            "uuid": header.get("uuid"),
            "version": header.get("version"),
            "min_engine_version": header.get("min_engine_version")
        }

    except (json.JSONDecodeError, OSError):
        return {
            "valid": False,
            "reason": "Invalid or unreadable manifest"
        }


def get_pack_info(pack_path):
    return read_manifest(pack_path)
