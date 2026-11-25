
import json
import zipfile
from pathlib import Path, PurePosixPath

from .manifest import read_manifest_data
from .compatibility import analyze_archive_files, analyze_pack

SUPPORTED_FILES = {".mcpack", ".mcaddon", ".zip"}


def _safe_member(name):
    """Reject absolute paths and path traversal entries."""
    path = PurePosixPath(name.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts


def _read_archive_manifests(archive):
    names = [
        name for name in archive.namelist()
        if not name.endswith("/") and _safe_member(name)
    ]

    manifests = [
        name for name in names
        if PurePosixPath(name).name.lower() == "manifest.json"
    ]

    results = []

    for manifest_name in manifests:
        try:
            with archive.open(manifest_name) as file:
                data = json.load(file)

            manifest = read_manifest_data(data)
            if not manifest["valid"]:
                continue

            parent = str(PurePosixPath(manifest_name).parent)
            prefix = "" if parent == "." else parent + "/"

            pack_files = [
                name[len(prefix):]
                for name in names
                if name.startswith(prefix)
            ]

            results.append({
                "source": manifest_name,
                "manifest": manifest,
                "graphics": analyze_archive_files(pack_files)
            })

        except (json.JSONDecodeError, OSError, ValueError):
            continue

    return results


def scan_archive(archive_path):
    archive_path = Path(archive_path).expanduser()

    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            found = _read_archive_manifests(archive)

        if not found:
            return {
                "success": False,
                "error": "No valid manifest.json found in archive",
                "source": str(archive_path)
            }

        packs = [
            {
                "source": f"{archive_path}!/{item['source']}",
                "type": "archive",
                "manifest": item["manifest"],
                "graphics": item["graphics"]
            }
            for item in found
        ]

        return {
            "success": True,
            "pack": packs[0] if len(packs) == 1 else {
                "source": str(archive_path),
                "type": "archive_bundle",
                "manifest": {
                    "valid": True,
                    "name": archive_path.stem,
                    "description": "Multiple packs found in this archive"
                },
                "graphics": {},
                "packs": packs
            }
        }

    except (zipfile.BadZipFile, OSError, ValueError) as error:
        return {
            "success": False,
            "error": str(error),
            "source": str(archive_path)
        }


def scan_one(path):
    path = Path(path).expanduser()

    if path.is_dir():
        manifest = read_manifest_data_from_folder(path)

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


def read_manifest_data_from_folder(path):
    from .manifest import read_manifest
    return read_manifest(path)


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
            pack = result["pack"]
            if pack.get("type") == "archive_bundle":
                packs.extend(pack["packs"])
            else:
                packs.append(pack)
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
