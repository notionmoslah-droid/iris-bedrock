
import argparse
import json

from src.lirs import VERSION, NAME
from src.lirs.shaderpacks import (
    create_shaderpacks_folder,
    discover_shaderpacks
)


def main():
    parser = argparse.ArgumentParser(
        description="LIRS - Lightweight Iris Resource System"
    )

    parser.add_argument(
        "--scan",
        default="shaderpacks",
        help="Shaderpacks directory"
    )

    parser.add_argument(
        "--init",
        action="store_true",
        help="Create shaderpacks directory"
    )

    args = parser.parse_args()

    print(f"{NAME} v{VERSION}")

    if args.init:
        folder = create_shaderpacks_folder(args.scan)
        print(f"Created: {folder}")
        return

    print("Scanning shaderpacks...")

    result = discover_shaderpacks(args.scan)

    print(json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()
