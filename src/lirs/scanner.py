
import json
import zipfile
from pathlib import Path

from .manifest import read_manifest
from .compatibility import analyze_pack


SUPPORTED_FILES = {".mcpack", ".mcaddon", ".zip"}


def _archive_graphics(names):
    texture_sets = sum(
        name.lower().endswith("texture_set.json")
        for name in names
    )

    return {
        "pbr": texture_sets > 0,
        "vibrant_visuals_indicators": any(
            "vibrant_visuals" in name.lower()
            for name in names
        ),
        "texture_sets": texture_sets,
        "render_controllers": any(
            name.lower().startswith("render_controllers/")
            for name in names
        ),
        "textures": any(
            name.lower().startswith("textures/")
            for name in names
        ),
        "warnings": [
            "Static inspection only; in-game compatibility is unverified."
        ]
    }


def scan_archive(archive_path):
    archive_path = Path(archive_path)

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            names = [
                name for name in archive.namelist()
                if not name.endswith("/")
            ]

            manifest_name = next(
                (
                    name for name in names
                    if name.lower() == "manifest.json"
                    or name.lower().endswith("/manifest.json")
                ),
                None
            )

            if manifest_name is None:
                return {
                    "success": False,
                    "error": "manifest.json not found"
                }

            with archive.open(manifest_name) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return {
                    "success": False,
                    "error": "Manifest must be a JSON object"
                }

            header = data.get("header")

            if not isinstance(header, dict):
                return {
                    "success": False,
                    "error": "Invalid or missing manifest header"
                }

            prefix = manifest_name.rsplit("/", 1)[0]
            if prefix == manifest_name:
                prefix = ""
            else:
                prefix += "/"

            pack_files = [
                name[len(prefix):]
                for name in names
                if name.startswith(prefix)
            ]

            manifest = {
                "valid": True,
                "name": header.get("name", "Unknown"),
                "description": header.get("description", ""),
                "uuid": header.get("uuid"),
                "version": header.get("version"),
                "min_engine_version": header.get("min_engine_version"),
                "format_version": data.get("format_version"),
                "modules": data.get("modules", [])
            }

            return {
                "success": True,
                "pack": {
                    "source": str(archive_path),
                    "type": "archive",
                    "manifest": manifest,
                    "graphics": _archive_graphics(pack_files)
                }
            }

    except (
        zipfile.BadZipFile,
        json.JSONDecodeError,
        OSError,
        ValueError
    ) as error:
        return {
            "success": False,
            "error": str(error)
        }


def scan_one(path):
    path = Path(path).expanduser()

    if path.is_dir():
        manifest = read_manifest(path)

        if not manifest["valid"]:
            return {
                "success": False,
                "error": manifest["reason"],
                "source": str(path)
            }

        return {
            "success": True,
            "pack": {
                "source": str(path),
                "type": "directory",
                "manifest": manifest,
                "graphics": analyze_pack(path)
            }
        }

    if path.is_file() and path.suffix.lower() in SUPPORTED_FILES:
        return scan_archive(path)

    return {
        "success": False,
        "error": "Unsupported pack format",
        "source": str(path)
    }


def scan_directory(directory):
    directory = Path(directory).expanduser()

    if not directory.is_dir():
        return {
            "success": False,
            "error": "Directory does not exist",
            "directory": str(directory),
            "count": 0,
            "packs": [],
            "errors": []
        }

    packs = []
    errors = []

    for item in sorted(directory.iterdir()):
        result = scan_one(item)

        if result["success"]:
            packs.append(result["pack"])
        else:
            errors.append({
                "source": result.get("source", str(item)),
                "error": result["error"]
            })

    return {
        "success": True,
        "directory": str(directory),
        "count": len(packs),
        "packs": packs,
        "errors": errors
    }
