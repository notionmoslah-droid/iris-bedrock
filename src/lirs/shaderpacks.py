from copy import deepcopy
from pathlib import Path

from .scanner import scan_one
from .analyzer import analyze_resource_pack

DEFAULT_SHADERPACKS = Path("shaderpacks")

SUPPORTED_FORMATS = {
    ".mcpack",
    ".mcaddon",
    ".zip",
}


def create_shaderpacks_folder(path=DEFAULT_SHADERPACKS):
    folder = Path(path).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def discover_shaderpacks(path=DEFAULT_SHADERPACKS):
    """Discover packs and attach a detailed static compatibility report."""
    folder = create_shaderpacks_folder(path)

    packs = []
    errors = []

    for item in sorted(folder.iterdir()):
        if item.is_dir():
            result = scan_one(item)
        elif item.is_file() and item.suffix.lower() in SUPPORTED_FORMATS:
            result = scan_one(item)
        else:
            continue

        if not result["success"]:
            errors.append({
                "source": str(item),
                "error": result.get("error", "Unknown error"),
            })
            continue

        pack = result["pack"]

        # Analyze the original folder/archive.
        compatibility_report = analyze_resource_pack(item)

        if not compatibility_report.get("success"):
            errors.append({
                "source": str(item),
                "error": (
                    "Compatibility analysis failed: "
                    + compatibility_report.get(
                        "error", "Unknown error"
                    )
                ),
            })

        if pack.get("type") == "archive_bundle":
            discovered = pack.get("packs", [])
        else:
            discovered = [pack]

        for discovered_pack in discovered:
            discovered_pack = deepcopy(discovered_pack)
            discovered_pack["enabled"] = False
            discovered_pack["compatibility_report"] = deepcopy(
                compatibility_report
            )
            packs.append(discovered_pack)

    return {
        "success": True,
        "directory": str(folder),
        "count": len(packs),
        "packs": packs,
        "errors": errors,
    }


def get_shaderpack_names(path=DEFAULT_SHADERPACKS):
    result = discover_shaderpacks(path)

    names = []

    for pack in result["packs"]:
        name = pack.get("manifest", {}).get(
            "name", "Unknown"
        )

        if isinstance(name, dict):
            name = (
                name.get("en_US")
                or next(iter(name.values()), "Unknown")
            )

        names.append(str(name))

    return names
