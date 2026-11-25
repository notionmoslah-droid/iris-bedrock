import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.lirs.analyzer import analyze_resource_pack


class AnalyzerTests(unittest.TestCase):

    def manifest(self):
        return {
            "format_version": 2,
            "header": {
                "name": "Analyzer Test",
                "uuid": "00000000-0000-0000-0000-000000000001",
                "version": [1, 0, 0],
            },
            "modules": [],
        }

    def test_directory_with_valid_pbr_texture_set(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "textures").mkdir()
            (root / "manifest.json").write_text(
                json.dumps(self.manifest()), encoding="utf-8"
            )
            (root / "textures" / "stone_texture_set.json").write_text(
                json.dumps({
                    "minecraft:texture_set": {
                        "color": "stone",
                        "normal": "stone_normal",
                    }
                }),
                encoding="utf-8",
            )

            report = analyze_resource_pack(root)

            self.assertTrue(report["success"])
            self.assertEqual(report["pack_type"], "resource_pack")
            self.assertTrue(report["features"]["pbr_indicators"])
            self.assertEqual(report["texture_sets"]["valid"], 1)

    def test_archive_with_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "sample.mcpack"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("manifest.json", json.dumps(self.manifest()))
                archive.writestr("textures/stone.png", b"fake-image-data")

            report = analyze_resource_pack(archive_path)

            self.assertTrue(report["success"])
            self.assertEqual(report["manifest_count"], 1)
            self.assertTrue(report["features"]["textures"])

    def test_invalid_texture_set_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manifest.json").write_text(
                json.dumps(self.manifest()), encoding="utf-8"
            )
            (root / "texture_set.json").write_text(
                "{broken", encoding="utf-8"
            )

            report = analyze_resource_pack(root)

            self.assertEqual(report["texture_sets"]["valid"], 0)
            self.assertEqual(len(report["texture_sets"]["invalid"]), 1)

    def test_unknown_file_type_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "sample.txt"
            file_path.write_text("not a pack", encoding="utf-8")

            report = analyze_resource_pack(file_path)

            self.assertFalse(report["success"])


if __name__ == "__main__":
    unittest.main()
