from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.importer = load_module("import_annual_results", ROOT / "scripts" / "import_annual_results.py")

    def test_invalid_verification_date_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.importer.validate_date("2026-9-9")

    def test_missing_expected_award_title_is_rejected(self) -> None:
        titles = self.importer.EXPECTED_TITLES_BY_YEAR[2025] - {"Best Model"}
        data = [{"title": title} for title in titles]
        with self.assertRaisesRegex(ValueError, "Best Model"):
            self.importer.validate_award_titles(2025, data)


class StaticAuditTests(unittest.TestCase):
    def test_local_link_cannot_escape_audit_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = parent / "wiki"
            root.mkdir()
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1><a href="../outside.html#private">x</a></html>',
                encoding="utf-8",
            )
            (parent / "outside.html").write_text(
                '<html lang="en"><title>Outside</title><h1 id="private">Outside</h1></html>',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"),
                    str(root),
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["errors"], 1)
            self.assertIn("escapes audit root", report["findings"][0]["message"])


if __name__ == "__main__":
    unittest.main()
