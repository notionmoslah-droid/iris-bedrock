
import json
import tempfile
import unittest
import zipfile

from pathlib import Path

from src.lirs.manifest import read_manifest
from src.lirs.scanner import scan_one
from src.lirs.library import load_library, save_library, add_pack


class LIRSTests(unittest.TestCase):

    def make_manifest(self, name="Test Pack"):
        return {
            "format_version": 2,
            "header": {
                "name": name,
                "description": "Test pack",
                "uuid": "00000000-0000-0000-0000-000000000001",
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
            },
            "modules": []
        }

    def test_valid_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "manifest.json").write_text(
                json.dumps(self.make_manifest()),
                encoding="utf-8"
            )

            result = read_manifest(folder)

            self.assertTrue(result["valid"])
            self.assertEqual(result["name"], "Test Pack")

    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            result = read_manifest(temp)
            self.assertFalse(result["valid"])

    def test_invalid_manifest_json(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "manifest.json").write_text(
                "{broken json",
                encoding="utf-8"
            )

            result = read_manifest(folder)
            self.assertFalse(result["valid"])

    def test_scan_directory_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "manifest.json").write_text(
                json.dumps(self.make_manifest()),
                encoding="utf-8"
            )

            result = scan_one(folder)

            self.assertTrue(result["success"])
            self.assertEqual(
                result["pack"]["manifest"]["name"],
                "Test Pack"
            )

    def test_scan_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "test.mcpack"

            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "manifest.json",
                    json.dumps(self.make_manifest())
                )

            result = scan_one(archive_path)

            self.assertTrue(result["success"])
            self.assertEqual(
                result["pack"]["manifest"]["name"],
                "Test Pack"
            )

    def test_multiple_manifests_in_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "test.mcaddon"

            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(
                    "resource_pack/manifest.json",
                    json.dumps(self.make_manifest("Resource Pack"))
                )
                archive.writestr(
                    "behavior_pack/manifest.json",
                    json.dumps(self.make_manifest("Behavior Pack"))
                )

            result = scan_one(archive_path)

            self.assertTrue(result["success"])
            self.assertEqual(result["pack"]["type"], "archive_bundle")
            self.assertEqual(len(result["pack"]["packs"]), 2)

    def test_library_save_and_load(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            items = [{"source": "test.mcpack"}]

            save_library(items, path)

            self.assertEqual(load_library(path), items)

    def test_add_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            pack = {"source": "test.mcpack"}

            self.assertTrue(add_pack(pack, path))
            self.assertFalse(add_pack(pack, path))

    def test_corrupt_library_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "library.json"
            path.write_text("{broken", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_library(path)


if __name__ == "__main__":
    unittest.main()
