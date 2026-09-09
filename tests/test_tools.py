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
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = load_module(
            "audit_static_wiki", ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"
        )

    def run_audit(self, root: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"),
                str(root),
                "--json",
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

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
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["errors"], 1)
            self.assertIn("escapes audit root", report["findings"][0]["message"])

    def test_heading_jump_and_missing_figure_caption_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "plot.png").write_bytes(b"png")
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1><h3>Results</h3>'
                '<figure><img src="plot.png" alt="response curve"></figure></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            messages = [item["message"] for item in report["findings"]]
            self.assertIn("heading level jumps from h1 to h3", messages)
            self.assertIn("figure contains a visual but no figcaption", messages)

    def test_machine_local_path_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1>'
                '<img src="/Users/example/Desktop/private.png" alt="private"></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any("machine-local path" in item["message"] for item in report["findings"])
            )

    def test_https_url_is_not_treated_as_a_windows_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1>'
                '<script src="https://cdn.example.org/app.js"></script></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            self.assertFalse(
                any("machine-local path" in item["message"] for item in report["findings"])
            )

    def test_required_route_missing_is_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root, "--required-route", "model")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(
                any("required route not found: model" in item["message"] for item in report["findings"])
            )

    def test_excluded_relative_directory_is_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            drafts = root / "drafts"
            drafts.mkdir()
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            (drafts / "broken.html").write_text(
                '<html><a href="missing.html">broken</a></html>', encoding="utf-8"
            )
            result, report = self.run_audit(root, "--exclude", "drafts")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["html_files"], 1)

    def test_markdown_report_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"),
                    str(root),
                    "--markdown",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("# Static Wiki audit", result.stdout)
            self.assertIn("No findings", result.stdout)

    def test_external_evidence_allowlist(self) -> None:
        self.assertTrue(
            self.audit.allowed_external_evidence_url("https://2025.igem.wiki/example/model")
        )
        self.assertTrue(
            self.audit.allowed_external_evidence_url("https://github.com/example/repository")
        )
        self.assertFalse(
            self.audit.allowed_external_evidence_url("http://github.com/example/repository")
        )
        self.assertFalse(
            self.audit.allowed_external_evidence_url("https://example.com/private")
        )


class CorpusQueryTests(unittest.TestCase):
    def test_model_metadata_token_filter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "query_corpus.py"),
                "model-metadata",
                "--model-archetype",
                "stochastic",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        rows = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(rows)
        self.assertTrue(
            all("stochastic" in row["model_archetype"].split(";") for row in rows)
        )


if __name__ == "__main__":
    unittest.main()
