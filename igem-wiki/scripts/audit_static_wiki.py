#!/usr/bin/env python3
"""Read-only checks for a static iGEM wiki tree."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


SKIP_DIRS = {".git", "node_modules", "dist", "build", ".cache", "templates"}
VISUAL_TAGS = {"img", "svg", "canvas", "table", "video"}
MACHINE_PATH = re.compile(r"^(?:file://|~/|/Users/|/home/|/Volumes/|[A-Za-z]:[\\/])")
EXTERNAL_EVIDENCE_HOSTS = {
    "competition.igem.org",
    "github.com",
    "gitlab.igem.org",
    "parts.igem.org",
    "registry.igem.org",
    "static.igem.org",
    "static.igem.wiki",
    "video.igem.org",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[tuple[str, int]] = []
        self.links: list[tuple[str, int]] = []
        self.references: list[tuple[str, str, str, int]] = []
        self.images_without_alt: list[int] = []
        self.images_with_empty_alt: list[int] = []
        self.headings: list[tuple[int, int]] = []
        self.figures: list[dict[str, object]] = []
        self.figures_without_caption: list[int] = []
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
        if len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
            level = int(tag[1])
            if 1 <= level <= 6:
                self.headings.append((level, line))
                if level == 1:
                    self.h1_count += 1
        identifier = data.get("id")
        if identifier:
            self.ids.append((identifier, line))
        href = data.get("href")
        if tag in {"a", "area"} and href:
            self.links.append((href, line))
        if href:
            self.references.append((tag, "href", href, line))
        src = data.get("src")
        if src:
            self.references.append((tag, "src", src, line))
        if tag == "figure":
            self.figures.append({"line": line, "visual": False, "caption": False})
        elif self.figures and tag in VISUAL_TAGS:
            self.figures[-1]["visual"] = True
        elif self.figures and tag == "figcaption":
            self.figures[-1]["caption"] = True
        if tag == "img" and "alt" not in data:
            self.images_without_alt.append(line)
        elif tag == "img" and not (data.get("alt") or "").strip():
            self.images_with_empty_alt.append(line)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.title_depth:
            self.title_depth -= 1
        if tag == "figure" and self.figures:
            figure = self.figures.pop()
            if figure["visual"] and not figure["caption"]:
                self.figures_without_caption.append(int(figure["line"]))

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory containing static HTML files")
    parser.add_argument("--no-fail", action="store_true", help="always return success after reporting")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    output.add_argument("--markdown", action="store_true", help="emit a Markdown audit report")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="exclude a relative file or directory; repeat as needed",
    )
    parser.add_argument(
        "--required-route",
        action="append",
        default=[],
        metavar="ROUTE",
        help="warn when a required Standard URL route is absent; repeat as needed",
    )
    parser.add_argument(
        "--check-external",
        action="store_true",
        help="optionally check allowlisted public evidence links; not intended for deterministic CI",
    )
    parser.add_argument(
        "--external-timeout",
        type=float,
        default=8.0,
        metavar="SECONDS",
        help="timeout per unique external evidence link (default: 8)",
    )
    return parser.parse_args()


def exclusion_prefixes(values: list[str]) -> tuple[tuple[str, ...], ...]:
    prefixes = []
    for value in values:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError(f"exclude path must be a safe relative path: {value}")
        prefixes.append(path.parts)
    return tuple(prefixes)


def html_files(root: Path, excluded: tuple[tuple[str, ...], ...]) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.html")
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        and not any(
            path.relative_to(root).parts[: len(prefix)] == prefix for prefix in excluded
        )
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


def allowed_external_evidence_url(url: str) -> bool:
    split = urlsplit(url)
    hostname = (split.hostname or "").casefold()
    return (
        split.scheme == "https"
        and not split.username
        and not split.password
        and (
            hostname in EXTERNAL_EVIDENCE_HOSTS
            or hostname.endswith(".igem.wiki")
            or hostname.endswith(".igem.org")
        )
    )


class EvidenceRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        if not allowed_external_evidence_url(newurl):
            raise HTTPError(newurl, code, "redirect left the evidence-link allowlist", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def external_link_problem(url: str, timeout: float) -> str | None:
    request = Request(
        url,
        headers={"User-Agent": "igem-wiki-static-audit/0.7", "Range": "bytes=0-0"},
    )
    try:
        with build_opener(EvidenceRedirectHandler()).open(request, timeout=timeout) as response:
            if 200 <= response.status < 400:
                return None
            return f"HTTP {response.status}"
    except HTTPError as exc:
        return f"HTTP {exc.code}: {exc.reason}"
    except (URLError, TimeoutError, OSError) as exc:
        return str(getattr(exc, "reason", exc))


def markdown_report(report: dict[str, object]) -> str:
    lines = [
        "# Static Wiki audit",
        "",
        f"Root: `{report['root']}`",
        "",
        f"Checked **{report['html_files']}** HTML files: **{report['errors']} errors** and **{report['warnings']} warnings**.",
        "",
        "| Level | Location | Finding |",
        "|---|---|---|",
    ]
    for item in report["findings"]:
        location = f"{item['file']}:{item['line']}" if item["line"] else item["file"]
        message = str(item["message"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {str(item['level']).upper()} | `{location}` | {message} |")
    if not report["findings"]:
        lines.append("| — | — | No findings |")
    lines.extend(
        [
            "",
            "> This static report does not replace browser, accessibility, scientific-evidence, or current-season judging review.",
            "",
        ]
    )
    return "\n".join(lines)


def route_exists(root: Path, route: str) -> bool:
    normalized = unquote(urlsplit(route).path).strip("/")
    if not normalized:
        return (root / "index.html").is_file()
    candidate = (root / normalized).resolve()
    if not candidate.is_relative_to(root):
        return False
    return any(
        path.is_file()
        for path in (candidate, candidate.with_suffix(".html"), candidate / "index.html")
    )


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    if args.external_timeout <= 0:
        raise SystemExit("--external-timeout must be greater than zero")
    try:
        excluded = exclusion_prefixes(args.exclude)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    files = html_files(root, excluded)
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
        for (previous_level, _), (level, line) in zip(parser.headings, parser.headings[1:]):
            if level > previous_level + 1:
                findings.append(
                    finding(
                        "warning",
                        relative,
                        line,
                        f"heading level jumps from h{previous_level} to h{level}",
                    )
                )
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
        for line in parser.figures_without_caption:
            findings.append(
                finding("warning", relative, line, "figure contains a visual but no figcaption")
            )
        for tag, attribute, value, line in parser.references:
            if MACHINE_PATH.search(unquote(value)):
                findings.append(
                    finding(
                        "error",
                        relative,
                        line,
                        f"{tag} {attribute} contains a machine-local path: {value}",
                    )
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

        anchor_references = {(href, line) for href, line in parser.links}
        for tag, attribute, value, line in parser.references:
            if attribute == "href" and (value, line) in anchor_references:
                continue
            split = urlsplit(value)
            if split.scheme or split.netloc or value.startswith(("data:", "javascript:")):
                continue
            if not split.path:
                continue
            try:
                target = resolve_page(root, source, split.path)
            except ValueError as exc:
                findings.append(finding("error", relative, line, str(exc)))
                continue
            if target is None:
                findings.append(
                    finding("error", relative, line, f"missing local {tag} {attribute} target: {value}")
                )

    for route in args.required_route:
        if not route_exists(root, route):
            findings.append(
                finding("warning", Path("."), None, f"required route not found: {route}")
            )

    if args.check_external:
        checked_urls: set[str] = set()
        for source, parser in parsed.items():
            relative = source.relative_to(root)
            for href, line in parser.links:
                if href in checked_urls or not allowed_external_evidence_url(href):
                    continue
                checked_urls.add(href)
                problem = external_link_problem(href, args.external_timeout)
                if problem:
                    findings.append(
                        finding(
                            "warning",
                            relative,
                            line,
                            f"external evidence link could not be verified: {href} ({problem})",
                        )
                    )

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
    elif args.markdown:
        print(markdown_report(report), end="")
    else:
        print(f"Checked {len(files)} HTML files: {counts['error']} errors; {counts['warning']} warnings.")
        for item in findings:
            location = f"{item['file']}:{item['line']}" if item["line"] else item["file"]
            print(f"[{str(item['level']).upper()}] {location}: {item['message']}")
    return 0 if args.no_fail or not counts["error"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
