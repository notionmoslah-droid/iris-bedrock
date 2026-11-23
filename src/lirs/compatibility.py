from pathlib import Path


def analyze_pack(pack_path):
    root = Path(pack_path)

    result = {
        "pbr": False,
        "vibrant_visuals_indicators": False,
        "texture_sets": 0,
        "render_controllers": False,
        "textures": False,
        "warnings": []
    }

    if not root.is_dir():
        result["warnings"].append("Pack directory not found")
        return result

    for file in root.rglob("*"):
        if not file.is_file():
            continue

        relative = file.relative_to(root).as_posix().lower()

        if file.name.lower() == "texture_set.json":
            result["pbr"] = True
            result["texture_sets"] += 1

        if relative.startswith("textures/"):
            result["textures"] = True

        if relative.startswith("render_controllers/"):
            result["render_controllers"] = True

        if "vibrant_visuals" in relative:
            result["vibrant_visuals_indicators"] = True

    if not result["textures"]:
        result["warnings"].append("No textures directory found")

    if not result["pbr"]:
        result["warnings"].append("No texture_set.json found")

    result["warnings"].append(
        "File detection does not guarantee in-game compatibility"
    )

    return result
