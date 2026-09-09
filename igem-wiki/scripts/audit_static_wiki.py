#!/usr/bin/env python3
"""Read-only checks for a static iGEM wiki tree."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKIP_DIRS = {".git", "node_modules", "dist", "build", ".cache"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.images_without_alt: list[int] = []
        self.images_with_empty_alt: list[int] = []
        self.html_lang = False
        self.title_depth = 0
        self.title_text: list[str] = []
        self.h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        line = self.getpos()[0]
        if tag == "html" and (data.get("lang") or "").strip():
            self.html_lang = True
        if tag == "title":
            self.title_depth += 1
        if tag == "h1":
            self.h1_count += 1
        identifier = data.get("id")
        if identifier:
            self.ids.append((identifier, line))
        href = data.get("href")
        if tag in {"a", "area"} and href:
            self.links.append((href, line))
        if tag == "img" and "alt" not in data:
            self.images_without_alt.append(line)
        elif tag == "img" and not (data.get("alt") or "").strip():
            self.images_with_empty_alt.append(line)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory containing static HTML files")
    parser.add_argument("--no-fail", action="store_true", help="always return success after reporting")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser.parse_args()


def html_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.html")
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        and path.resolve().is_relative_to(root)
    )


def resolve_page(root: Path, source: Path, raw_path: str) -> Path | None:
    decoded = unquote(raw_path)
    candidate = (root / decoded.lstrip("/")) if decoded.startswith("/") else (source.parent / decoded)
    candidate = candidate.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"local link escapes audit root: {raw_path}")
    options = [candidate]
    if candidate.suffix == "":
        options.extend((candidate.with_suffix(".html"), candidate / "index.html"))
    if candidate.is_dir():
        options.append(candidate / "index.html")
    return next((path for path in options if path.is_file()), None)


def finding(level: str, path: Path, line: int | None, message: str) -> dict[str, object]:
    return {"level": level, "file": str(path), "line": line, "message": message}


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    files = html_files(root)
    if not files:
        raise SystemExit(f"no HTML files found under {root}")

    parsed: dict[Path, PageParser] = {}
    findings: list[dict[str, object]] = []
    for path in files:
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(finding("error", path.relative_to(root), None, f"cannot parse: {exc}"))
            continue
        parsed[path] = parser
        relative = path.relative_to(root)
        if not parser.html_lang:
            findings.append(finding("warning", relative, None, "missing non-empty html lang attribute"))
        if not "".join(parser.title_text).strip():
            findings.append(finding("warning", relative, None, "missing non-empty title"))
        if parser.h1_count != 1:
            findings.append(finding("warning", relative, None, f"expected one h1; found {parser.h1_count}"))
        counts = Counter(value for value, _ in parser.ids)
        duplicate_ids = {value for value, count in counts.items() if count > 1}
        for value in sorted(duplicate_ids):
            lines = [line for identifier, line in parser.ids if identifier == value]
            findings.append(
                finding("error", relative, lines[0], f"duplicate id #{value} on lines {', '.join(map(str, lines))}")
            )
        for line in parser.images_without_alt:
            findings.append(finding("error", relative, line, "image lacks an alt attribute"))
        for line in parser.images_with_empty_alt:
            findings.append(
                finding("warning", relative, line, "empty alt text; confirm that the image is decorative")
            )

    for source, parser in parsed.items():
        relative = source.relative_to(root)
        for href, line in parser.links:
            split = urlsplit(href)
            if split.scheme or split.netloc or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            try:
                target = source if not split.path else resolve_page(root, source, split.path)
            except ValueError as exc:
                findings.append(finding("error", relative, line, str(exc)))
                continue
            if target is None:
                findings.append(finding("error", relative, line, f"missing local link target: {href}"))
                continue
            if split.fragment and target.suffix.lower() in {".html", ".htm"}:
                target_parser = parsed.get(target)
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                identifiers = {value for value, _ in target_parser.ids}
                if unquote(split.fragment) not in identifiers:
                    findings.append(finding("error", relative, line, f"missing fragment target: {href}"))

    counts = Counter(item["level"] for item in findings)
    report = {
        "root": str(root),
        "html_files": len(files),
        "errors": counts["error"],
        "warnings": counts["warning"],
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Checked {len(files)} HTML files: {counts['error']} errors; {counts['warning']} warnings.")
        for item in findings:
            location = f"{item['file']}:{item['line']}" if item["line"] else item["file"]
            print(f"[{str(item['level']).upper()}] {location}: {item['message']}")
    return 0 if args.no_fail or not counts["error"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
