
import json
from pathlib import Path, PurePosixPath


def _empty_result():
    return {
        "pbr": False,
        "vibrant_visuals_indicators": False,
        "texture_sets": 0,
        "valid_texture_sets": 0,
        "render_controllers": False,
        "textures": False,
        "warnings": []
    }


def _check_texture_set_files(file_paths, read_text):
    result = _empty_result()

    for file_path in file_paths:
        relative = file_path.replace("\\", "/").lower()
        name = PurePosixPath(relative).name

        if name == "texture_set.json":
            result["texture_sets"] += 1

            try:
                data = json.loads(read_text(file_path))
                if isinstance(data, dict):
                    result["valid_texture_sets"] += 1
            except (ValueError, OSError, UnicodeDecodeError):
                pass

        if relative.startswith("textures/"):
            result["textures"] = True

        if relative.startswith("render_controllers/"):
            result["render_controllers"] = True

        if "vibrant_visuals" in relative:
            result["vibrant_visuals_indicators"] = True

    result["pbr"] = result["valid_texture_sets"] > 0

    if result["texture_sets"] == 0:
        result["warnings"].append("No texture_set.json found")
    elif result["valid_texture_sets"] < result["texture_sets"]:
        result["warnings"].append("Some texture_set.json files are invalid")

    if not result["textures"]:
        result["warnings"].append("No textures directory found")

    result["warnings"].append(
        "Static inspection only; in-game compatibility is unverified."
    )

    return result


def analyze_pack(pack_path):
    root = Path(pack_path).expanduser()

    if not root.is_dir():
        result = _empty_result()
        result["warnings"].append("Pack directory not found")
        return result

    files = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    ]

    def read_text(relative):
        return (root / relative).read_text(encoding="utf-8")

    return _check_texture_set_files(files, read_text)


def analyze_archive_files(file_paths):
    # Archive contents are inspected separately by the scanner.
    # This function reports indicators, not verified game support.
    result = _empty_result()

    for name in file_paths:
        relative = name.replace("\\", "/").lower()

        if PurePosixPath(relative).name == "texture_set.json":
            result["texture_sets"] += 1

        if relative.startswith("textures/"):
            result["textures"] = True

        if relative.startswith("render_controllers/"):
            result["render_controllers"] = True

        if "vibrant_visuals" in relative:
            result["vibrant_visuals_indicators"] = True

    if result["texture_sets"]:
        result["warnings"].append(
            "PBR files detected by name; JSON content was not validated."
        )
    else:
        result["warnings"].append("No texture_set.json found")

    result["warnings"].append(
        "Static inspection only; in-game compatibility is unverified."
    )

    return result
