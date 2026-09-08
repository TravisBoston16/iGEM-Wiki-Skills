#!/usr/bin/env python3
"""Import selected official iGEM Annual Results into the benchmark corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API_ROOT = "https://api.igem.org/v1"
AWARDS = {
    "Best Measurement": ("wetlab", "best-measurement"),
    "Best Integrated Human Practices": ("hp", "best-integrated-human-practices"),
    "Best Education": ("hp", "best-education"),
    "Best Sustainable Development Impact": ("hp", "best-sustainable-development-impact"),
    "Inclusivity Award": ("hp", "best-inclusivity"),
    "Best Hardware": ("implementation", "best-hardware"),
    "Best Software Tool": ("implementation", "best-software"),
    "Best Supporting Entrepreneurship": ("implementation", "best-entrepreneurship"),
    "Best Entrepreneurship": ("implementation", "best-entrepreneurship"),
    "Safety and Security Award": ("implementation", "best-safety"),
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
SOURCE_FIELDS = ("year", "competition_uuid", "awards_endpoint", "retrieved_on", "sha256")


def fetch_json(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "igem-wiki-skills-corpus-importer"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def read_competitions(source_dir: Path | None) -> list[dict]:
    if source_dir:
        path = source_dir / "igem-competitions.json"
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))["data"]
    return json.loads(fetch_json(f"{API_ROOT}/competitions"))["data"]


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
    return name.replace("_", "-").lower()


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--verified-on", required=True)
    parser.add_argument("--source-dir", type=Path, help="directory containing igem-results-YEAR.json snapshots")
    parser.add_argument("--write", action="store_true", help="update CSV files; otherwise report only")
    args = parser.parse_args()

    competitions = {item["year"]: item for item in read_competitions(args.source_dir) if item.get("type") == "igem"}
    imported: list[dict[str, str]] = []
    sources: list[dict[str, str]] = []
    for year in sorted(set(args.years)):
        competition = competitions.get(year)
        if not competition:
            raise ValueError(f"official API has no iGEM competition for {year}")
        raw, endpoint = read_results(year, competition["uuid"], args.source_dir)
        data = json.loads(raw)
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
