
import json
from pathlib import Path


def read_manifest_data(data):
    if not isinstance(data, dict):
        return {
            "valid": False,
            "reason": "Manifest must be a JSON object"
        }

    header = data.get("header")

    if not isinstance(header, dict):
        return {
            "valid": False,
            "reason": "Missing or invalid manifest header"
        }

    name = header.get("name")
    if not isinstance(name, (str, dict)):
        name = "Unknown"

    description = header.get("description", "")
    if not isinstance(description, (str, dict)):
        description = ""

    return {
        "valid": True,
        "name": name,
        "description": description,
        "uuid": header.get("uuid"),
        "version": header.get("version"),
        "min_engine_version": header.get("min_engine_version"),
        "format_version": data.get("format_version"),
        "modules": data.get("modules", [])
    }


def read_manifest(pack_path):
    manifest_path = Path(pack_path).expanduser() / "manifest.json"

    if not manifest_path.is_file():
        return {
            "valid": False,
            "reason": "Missing manifest.json"
        }

    try:
        with manifest_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return read_manifest_data(data)

    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
        return {
            "valid": False,
            "reason": f"Invalid or unreadable manifest: {error}"
        }


def get_pack_info(pack_path):
    return read_manifest(pack_path)
