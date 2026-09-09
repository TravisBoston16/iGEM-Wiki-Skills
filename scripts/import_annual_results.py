#!/usr/bin/env python3
"""Import selected official iGEM Annual Results into the benchmark corpus."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = "https://api.igem.org/v1"
AWARDS = {
    "Best Wiki": ("story", "best-wiki"),
    "Best Model": ("model", "best-model"),
    "Best Measurement": ("wetlab", "best-measurement"),
    "Best New Basic Part": ("wetlab", "best-new-basic-part"),
    "Best New Composite Part": ("wetlab", "best-new-composite-part"),
    "Best New Improved Part": ("wetlab", "best-new-improved-part"),
    "Best Part Collection": ("wetlab", "best-part-collection"),
    "Best Integrated Human Practices": ("hp", "best-integrated-human-practices"),
    "Best Education": ("hp", "best-education"),
    "Best Sustainable Development Impact": ("hp", "best-sustainable-development-impact"),
    "Best Sustainability": ("hp", "best-sustainable-development-impact"),
    "Inclusivity Award": ("hp", "best-inclusivity"),
    "Best Inclusivity": ("hp", "best-inclusivity"),
    "Best Hardware": ("implementation", "best-hardware"),
    "Best Software Tool": ("implementation", "best-software"),
    "Best Supporting Entrepreneurship": ("implementation", "best-entrepreneurship"),
    "Best Entrepreneurship": ("implementation", "best-entrepreneurship"),
    "Safety and Security Award": ("implementation", "best-safety"),
    "Best Safety & Security": ("implementation", "best-safety"),
}
BASE_EXPECTED_TITLES = {
    "Best Wiki",
    "Best Model",
    "Best Measurement",
    "Best New Basic Part",
    "Best New Composite Part",
    "Best Part Collection",
    "Best Integrated Human Practices",
    "Best Education",
    "Best Hardware",
    "Best Software Tool",
}
EXPECTED_TITLES_BY_YEAR = {
    2021: BASE_EXPECTED_TITLES
    | {"Best Sustainability", "Best Inclusivity", "Best Supporting Entrepreneurship", "Best Safety & Security"},
    2022: BASE_EXPECTED_TITLES
    | {
        "Best Sustainable Development Impact",
        "Inclusivity Award",
        "Best Supporting Entrepreneurship",
        "Safety and Security Award",
    },
    2023: BASE_EXPECTED_TITLES
    | {
        "Best New Improved Part",
        "Best Sustainable Development Impact",
        "Inclusivity Award",
        "Best Entrepreneurship",
        "Safety and Security Award",
    },
    2024: BASE_EXPECTED_TITLES
    | {
        "Best New Improved Part",
        "Best Sustainable Development Impact",
        "Inclusivity Award",
        "Best Entrepreneurship",
        "Safety and Security Award",
    },
    2025: BASE_EXPECTED_TITLES
    | {
        "Best New Improved Part",
        "Best Sustainable Development Impact",
        "Inclusivity Award",
        "Best Entrepreneurship",
        "Safety and Security Award",
    },
}
AWARD_FIELDS = (
    "domain",
    "year",
    "section",
    "award",
    "status",
    "team",
    "team_slug",
    "verified_on",
)
SOURCE_FIELDS = (
    "year",
    "competition_uuid",
    "awards_endpoint",
    "retrieved_on",
    "sha256",
    "competitions_sha256",
    "results_snapshot",
    "competitions_snapshot",
)


def fetch_json(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "igem-wiki-skills-corpus-importer"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def read_competitions(source_dir: Path | None) -> tuple[list[dict], bytes]:
    if source_dir:
        path = source_dir / "igem-competitions.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        raw = path.read_bytes()
    else:
        raw = fetch_json(f"{API_ROOT}/competitions")
    return json.loads(raw)["data"], raw


def read_results(year: int, uuid: str, source_dir: Path | None) -> tuple[bytes, str]:
    endpoint = f"{API_ROOT}/competitions/{uuid}/awards/results"
    if source_dir:
        path = source_dir / f"igem-results-{year}.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        return path.read_bytes(), endpoint
    return fetch_json(endpoint), endpoint


def normalize_name(name: str) -> str:
    return name.replace("_", "-")


def normalize_slug(name: str) -> str:
    simplified = re.sub(r"[^a-z0-9_-]+", "-", name.casefold()).replace("_", "-")
    return re.sub(r"-+", "-", simplified).strip("-")


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8", dir=path.parent, delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    temporary.replace(path)


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def validate_date(value: str) -> None:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("--verified-on must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise ValueError("--verified-on must use YYYY-MM-DD")


def validate_award_titles(year: int, data: list[dict]) -> None:
    expected = EXPECTED_TITLES_BY_YEAR.get(year)
    if expected is None:
        raise ValueError(
            f"no expected award-title contract for {year}; review the official categories before importing"
        )
    available = {award.get("title") for award in data}
    missing = sorted(expected - available)
    if missing:
        raise ValueError(
            f"official results for {year} are missing expected mapped titles: {', '.join(missing)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--verified-on", required=True)
    parser.add_argument("--source-dir", type=Path, help="directory containing igem-results-YEAR.json snapshots")
    parser.add_argument(
        "--snapshot-dir",
        type=Path,
        default=ROOT / "corpus" / "snapshots",
        help="directory in which --write preserves the exact JSON inputs",
    )
    parser.add_argument("--write", action="store_true", help="update CSV files; otherwise report only")
    args = parser.parse_args()

    validate_date(args.verified_on)
    snapshot_dir = args.snapshot_dir.resolve()
    if not snapshot_dir.is_relative_to(ROOT):
        raise ValueError("--snapshot-dir must remain inside the repository")
    snapshot_relative = snapshot_dir.relative_to(ROOT)
    competition_items, competition_raw = read_competitions(args.source_dir)
    competitions = {item["year"]: item for item in competition_items if item.get("type") == "igem"}
    imported: list[dict[str, str]] = []
    sources: list[dict[str, str]] = []
    result_snapshots: dict[int, bytes] = {}
    for year in sorted(set(args.years)):
        competition = competitions.get(year)
        if not competition:
            raise ValueError(f"official API has no iGEM competition for {year}")
        raw, endpoint = read_results(year, competition["uuid"], args.source_dir)
        result_snapshots[year] = raw
        data = json.loads(raw)
        validate_award_titles(year, data)
        for award in data:
            mapped = AWARDS.get(award.get("title"))
            if not mapped:
                continue
            domain, award_id = mapped
            for record in award.get("teamAwards", []):
                team = record["team"]["name"]
                imported.append(
                    {
                        "domain": domain,
                        "year": str(year),
                        "section": record["group"],
                        "award": award_id,
                        "status": record["decision"],
                        "team": normalize_name(team),
                        "team_slug": normalize_slug(team),
                        "verified_on": args.verified_on,
                    }
                )
        sources.append(
            {
                "year": str(year),
                "competition_uuid": competition["uuid"],
                "awards_endpoint": endpoint,
                "retrieved_on": args.verified_on,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "competitions_sha256": hashlib.sha256(competition_raw).hexdigest(),
                "results_snapshot": str(snapshot_relative / f"igem-results-{year}.json"),
                "competitions_snapshot": str(snapshot_relative / "igem-competitions.json"),
            }
        )

    unique = {
        (row["domain"], row["year"], row["section"], row["award"], row["status"], row["team"])
        for row in imported
    }
    if len(unique) != len(imported):
        raise ValueError("official results produced duplicate normalized award rows")
    print(f"Prepared {len(imported)} records for years {', '.join(map(str, sorted(set(args.years))))}.")
    if not args.write:
        return 0

    write_bytes(snapshot_dir / "igem-competitions.json", competition_raw)
    for year, raw in result_snapshots.items():
        write_bytes(snapshot_dir / f"igem-results-{year}.json", raw)

    award_path = ROOT / "corpus" / "award_records.csv"
    existing = read_rows(award_path)
    replacement_keys = {(row["domain"], row["year"], row["award"]) for row in imported}
    merged = [
        row for row in existing if (row["domain"], row["year"], row["award"]) not in replacement_keys
    ] + imported
    merged.sort(
        key=lambda row: (
            row["domain"],
            -int(row["year"]),
            row["award"],
            row["section"],
            0 if row["status"] == "winner" else 1,
            row["team"].casefold(),
        )
    )
    write_rows(award_path, AWARD_FIELDS, merged)

    source_path = ROOT / "corpus" / "source_manifest.csv"
    old_sources = read_rows(source_path)
    years = {str(year) for year in args.years}
    merged_sources = [row for row in old_sources if row["year"] not in years] + sources
    merged_sources.sort(key=lambda row: -int(row["year"]))
    write_rows(source_path, SOURCE_FIELDS, merged_sources)
    print(f"Wrote {len(merged)} total award records and {len(merged_sources)} source records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
