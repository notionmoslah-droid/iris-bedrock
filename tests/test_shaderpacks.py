
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.lirs.shaderpacks import discover_shaderpacks


class ShaderpackIntegrationTests(unittest.TestCase):

    def manifest(self, name="Integration Test"):
        return {
            "format_version": 2,
            "header": {
                "name": name,
                "uuid": "00000000-0000-0000-0000-000000000002",
                "version": [1, 0, 0],
            },
            "modules": [],
        }

    def test_discovery_attaches_directory_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pack = root / "ExamplePack"
            (pack / "textures").mkdir(parents=True)

            (pack / "manifest.json").write_text(
                json.dumps(self.manifest()),
                encoding="utf-8",
            )

            (pack / "textures" /
             "stone_texture_set.json").write_text(
                json.dumps({
                    "minecraft:texture_set": {
                        "color": "stone",
                        "normal": "stone_normal",
                    }
                }),
                encoding="utf-8",
            )

            result = discover_shaderpacks(root)

            self.assertEqual(result["count"], 1)

            report = result["packs"][0][
                "compatibility_report"
            ]

            self.assertTrue(report["success"])
            self.assertTrue(
                report["features"]["pbr_indicators"]
            )
            self.assertEqual(
                report["texture_sets"]["valid"], 1
            )
            self.assertFalse(result["packs"][0]["enabled"])

    def test_discovery_attaches_archive_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "Example.mcpack"

            with zipfile.ZipFile(
                archive_path, "w"
            ) as archive:

                archive.writestr(
                    "manifest.json",
                    json.dumps(self.manifest("Archive Pack")),
                )

                archive.writestr(
                    "textures/stone_texture_set.json",
                    json.dumps({
                        "minecraft:texture_set": {
                            "color": "stone",
                        }
                    }),
                )

            result = discover_shaderpacks(root)

            self.assertEqual(result["count"], 1)

            report = result["packs"][0][
                "compatibility_report"
            ]

            self.assertTrue(report["success"])
            self.assertEqual(report["manifest_count"], 1)
            self.assertTrue(
                report["features"]["pbr_indicators"]
            )

    def test_invalid_archive_analysis_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive_path = root / "Bad.mcpack"

            with zipfile.ZipFile(
                archive_path, "w"
            ) as archive:
                archive.writestr(
                    "manifest.json",
                    "{invalid json",
                )

            result = discover_shaderpacks(root)

            self.assertEqual(result["count"], 0)
            self.assertEqual(len(result["errors"]), 1)


if __name__ == "__main__":
    unittest.main()
