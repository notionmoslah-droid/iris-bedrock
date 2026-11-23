import argparse
import json

from src.lirs.scanner import scan_directory
from src.lirs import VERSION, NAME


def main():
    parser = argparse.ArgumentParser(
        description="LIRS Bedrock Resource Pack Scanner"
    )

    parser.add_argument(
        "--scan",
        default="resource_packs",
        help="Directory containing resource packs"
    )

    parser.add_argument(
        "--bedrock-version",
        default=None
    )

    args = parser.parse_args()

    print(f"{NAME} v{VERSION}")
    print("Scanning resource packs...\n")

    results = scan_directory(
        args.scan,
        args.bedrock_version
    )

    print(json.dumps(
        results,
        indent=4,
        ensure_ascii=False
    ))


if __name__ == "__main__":
    main()
