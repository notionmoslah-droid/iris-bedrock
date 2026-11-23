import json
import tempfile
import unittest

from pathlib import Path
from src.lirs.manifest import get_pack_info


class ScannerTests(unittest.TestCase):

    def test_valid_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)

            manifest = {
                "header": {
                    "name": "Test Pack",
                    "uuid": "00000000-0000-0000-0000-000000000001",
                    "version": [1, 0, 0]
                }
            }

            (path / "manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8"
            )

            result = get_pack_info(path)

            self.assertTrue(result["valid"])
            self.assertEqual(result["name"], "Test Pack")


if __name__ == "__main__":
    unittest.main()
