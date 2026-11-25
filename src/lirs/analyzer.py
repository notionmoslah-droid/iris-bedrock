import json
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILES = 10000
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_TOTAL_BYTES = 64 * 1024 * 1024

PBR_CHANNELS = {
    "color",
    "normal",
    "height",
    "metalness_emissive_roughness",
}


def _safe_name(name):
    path = PurePosixPath(name.replace("\\", "/"))
    return not path.is_absolute() and ".." not in path.parts


def _empty_report(source):
    return {
        "success": True,
        "source": str(source),
        "pack_type": "unknown",
        "manifest_count": 0,
        "valid_manifests": [],
        "invalid_manifests": [],
        "texture_sets": {
            "count": 0,
            "valid": 0,
            "invalid": [],
            "channels_found": [],
        },
        "features": {
            "textures": False,
            "render_controllers": False,
            "materials": False,
            "vibrant_visuals_indicators": [],
            "pbr_indicators": False,
        },
        "compatibility": {
            "classification": "unknown",
            "confidence": "low",
            "notes": [
                "Static file analysis only; this is not an in-game compatibility test."
            ],
        },
        "warnings": [],
    }


def _read_json(raw, label):
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError(f"{label}: JSON file exceeds size limit")
    return json.loads(raw.decode("utf-8-sig"))


def _inspect(entries, read_bytes, source):
    report = _empty_report(source)
    names = list(entries)

    if len(names) > MAX_FILES:
        return {
            "success": False,
            "source": str(source),
            "error": f"Pack contains more than {MAX_FILES} files",
        }

    lower_names = [name.lower() for name in names]

    report["features"]["textures"] = any(
        name.startswith("textures/") for name in lower_names
    )
    report["features"]["render_controllers"] = any(
        name.startswith("render_controllers/") for name in lower_names
    )
    report["features"]["materials"] = any(
        name.startswith("materials/") for name in lower_names
    )

    visual_tokens = (
        "atmospherics",
        "point_lights",
        "vibrant_visuals",
        "water_settings",
    )
    report["features"]["vibrant_visuals_indicators"] = sorted({
        token
        for name in lower_names
        for token in visual_tokens
        if token in name
    })

    manifests = [
        name for name in names
        if PurePosixPath(name).name.lower() == "manifest.json"
    ]
    report["manifest_count"] = len(manifests)

    for name in manifests:
        try:
            data = _read_json(read_bytes(name), name)
            header = data.get("header") if isinstance(data, dict) else None
            if not isinstance(header, dict) or not header.get("uuid"):
                raise ValueError("Missing valid header or header UUID")

            modules = data.get("modules", [])
            report["valid_manifests"].append({
                "path": name,
                "name": header.get("name", "Unknown"),
                "version": header.get("version"),
                "min_engine_version": header.get("min_engine_version"),
                "modules_count": len(modules) if isinstance(modules, list) else 0,
                "capabilities": data.get("capabilities", []),
            })
        except (ValueError, UnicodeDecodeError, OSError, AttributeError) as error:
            report["invalid_manifests"].append({
                "path": name,
                "reason": str(error),
            })

    texture_sets = [
        name for name in names
        if PurePosixPath(name).name.lower().endswith("texture_set.json")
    ]
    report["texture_sets"]["count"] = len(texture_sets)

    channels = set()
    for name in texture_sets:
        try:
            data = _read_json(read_bytes(name), name)
            texture_set = (
                data.get("minecraft:texture_set")
                if isinstance(data, dict) else None
            )
            if not isinstance(texture_set, dict):
                raise ValueError("Missing minecraft:texture_set object")

            found = PBR_CHANNELS.intersection(texture_set.keys())
            if not found:
                raise ValueError("No recognized PBR texture channels")

            channels.update(found)
            report["texture_sets"]["valid"] += 1
        except (ValueError, UnicodeDecodeError, OSError, AttributeError) as error:
            report["texture_sets"]["invalid"].append({
                "path": name,
                "reason": str(error),
            })

    report["texture_sets"]["channels_found"] = sorted(channels)
    report["features"]["pbr_indicators"] = report["texture_sets"]["valid"] > 0

    if report["valid_manifests"] and not report["invalid_manifests"]:
        report["pack_type"] = "resource_pack"
    elif report["valid_manifests"]:
        report["pack_type"] = "mixed_or_multi_pack"
    elif report["manifest_count"]:
        report["pack_type"] = "invalid"
    else:
        report["pack_type"] = "unknown"
        report["warnings"].append("No manifest.json was found")

    if report["features"]["pbr_indicators"]:
        report["compatibility"]["classification"] = "pbr_indicators_found"
        report["compatibility"]["confidence"] = "medium"
    elif report["features"]["vibrant_visuals_indicators"]:
        report["compatibility"]["classification"] = "possible_vibrant_visuals_pack"
        report["compatibility"]["confidence"] = "low"
    elif report["valid_manifests"]:
        report["compatibility"]["classification"] = "resource_pack_no_pbr_detected"
        report["compatibility"]["confidence"] = "medium"

    if not report["features"]["textures"]:
        report["warnings"].append("No textures/ directory detected")
    if report["texture_sets"]["invalid"]:
        report["warnings"].append("One or more texture_set.json files are invalid")
    if not report["features"]["pbr_indicators"]:
        report["warnings"].append("No valid PBR texture set was detected")
    if report["features"]["vibrant_visuals_indicators"]:
        report["compatibility"]["notes"].append(
            "Vibrant Visuals-related filenames were found; this does not prove support."
        )
    report["compatibility"]["notes"].append(
        "Device support, game version, rendering mode, and actual visuals must be tested in Minecraft."
    )
    return report


def analyze_resource_pack(path):
    """Analyze a Bedrock pack directory or .mcpack/.mcaddon/.zip archive."""
    path = Path(path).expanduser()

    if path.is_dir():
        files = [
            item for item in path.rglob("*")
            if item.is_file() and not item.is_symlink()
        ]
        if len(files) > MAX_FILES:
            return {
                "success": False,
                "source": str(path),
                "error": f"Pack contains more than {MAX_FILES} files",
            }

        names = [item.relative_to(path).as_posix() for item in files]

        def read_bytes(name):
            target = path.joinpath(*PurePosixPath(name).parts)
            if target.stat().st_size > MAX_JSON_BYTES:
                raise ValueError(f"{name}: file exceeds size limit")
            return target.read_bytes()

        return _inspect(names, read_bytes, path)

    if not path.is_file() or path.suffix.lower() not in {".mcpack", ".mcaddon", ".zip"}:
        return {
            "success": False,
            "source": str(path),
            "error": "Expected a pack directory or .mcpack/.mcaddon/.zip file",
        }

    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = [
                info for info in archive.infolist()
                if not info.is_dir() and _safe_name(info.filename)
            ]
            if len(infos) > MAX_FILES:
                raise ValueError(f"Archive contains more than {MAX_FILES} files")

            total_size = sum(info.file_size for info in infos)
            if total_size > MAX_ARCHIVE_TOTAL_BYTES:
                raise ValueError("Archive uncompressed size exceeds safety limit")

            info_by_name = {info.filename: info for info in infos}
            names = list(info_by_name)

            def read_bytes(name):
                info = info_by_name[name]
                if info.file_size > MAX_JSON_BYTES:
                    raise ValueError(f"{name}: file exceeds size limit")
                return archive.read(info)

            return _inspect(names, read_bytes, path)

    except (zipfile.BadZipFile, OSError, ValueError, RuntimeError) as error:
        return {
            "success": False,
            "source": str(path),
            "error": str(error),
        }
