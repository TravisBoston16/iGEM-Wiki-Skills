#!/usr/bin/env python3
"""Validate the research corpus and generate per-domain Markdown indexes."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
DOMAINS = {
    "story": ("igem-wiki-story", "Narrative and Best Wiki"),
    "wetlab": ("igem-wetlab-wiki", "Wet-lab and Measurement"),
    "model": ("igem-model-wiki", "Model"),
    "hp": ("igem-hp-wiki", "Human Practices"),
    "implementation": ("igem-implementation-wiki", "Implementation"),
}
SECTIONS = {"undergrad", "overgrad", "high-school"}
STATUSES = {"winner", "nominee"}
DEPTHS = {"targeted", "deep"}
BENCHMARK_YEARS = tuple(str(year) for year in range(2021, 2026))
MIN_REVIEWS_PER_DOMAIN_YEAR = 2
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG = re.compile(r"^[A-Za-z0-9_-]+$")
AWARD = re.compile(r"^[a-z0-9-]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def read_csv(name: str, required: tuple[str, ...]) -> list[dict[str, str]]:
    path = CORPUS / name
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{name}: expected columns {required}, got {reader.fieldnames}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            cleaned = {key: (value or "").strip() for key, value in row.items()}
            missing = [key for key, value in cleaned.items() if not value]
            if missing:
                raise ValueError(f"{name}:{line_number}: empty fields {missing}")
            rows.append(cleaned)
        return rows


def validate_awards(rows: list[dict[str, str]]) -> None:
    seen: set[tuple[str, ...]] = set()
    coverage: Counter[tuple[str, str]] = Counter()
    for row in rows:
        if row["domain"] not in DOMAINS:
            raise ValueError(f"unknown domain: {row['domain']}")
        if row["section"] not in SECTIONS:
            raise ValueError(f"unknown section: {row['section']}")
        if row["status"] not in STATUSES:
            raise ValueError(f"unknown award status: {row['status']}")
        if not row["year"].isdigit() or len(row["year"]) != 4:
            raise ValueError(f"invalid year: {row['year']}")
        if not AWARD.fullmatch(row["award"]):
            raise ValueError(f"invalid award identifier: {row['award']}")
        if not SLUG.fullmatch(row["team_slug"]):
            raise ValueError(f"invalid team slug: {row['team_slug']}")
        if not ISO_DATE.fullmatch(row["verified_on"]):
            raise ValueError(f"invalid verification date: {row['verified_on']}")
        key = tuple(row[field] for field in ("domain", "year", "section", "award", "status", "team"))
        if key in seen:
            raise ValueError(f"duplicate award row: {key}")
        seen.add(key)
        coverage[(row["domain"], row["year"])] += 1
    for domain in DOMAINS:
        missing = [year for year in BENCHMARK_YEARS if not coverage[(domain, year)]]
        if missing:
            raise ValueError(
                f"{domain}: official award inventory is missing benchmark years {', '.join(missing)}"
            )


def review_classes(relationship: str) -> set[str]:
    return {
        section
        for token, section in (("UG", "undergrad"), ("OG", "overgrad"), ("HS", "high-school"))
        if re.search(rf"(?:^|[\s;,]){token}(?:$|[\s;,])", relationship)
    }


def validate_reviews(rows: list[dict[str, str]]) -> None:
    seen: set[tuple[str, str]] = set()
    coverage: Counter[tuple[str, str]] = Counter()
    statuses: dict[tuple[str, str], set[str]] = {}
    classes: dict[str, set[str]] = {domain: set() for domain in DOMAINS}
    for row in rows:
        if row["domain"] not in DOMAINS:
            raise ValueError(f"unknown domain: {row['domain']}")
        if row["review_depth"] not in DEPTHS:
            raise ValueError(f"unknown review depth: {row['review_depth']}")
        if not row["page_url"].startswith("https://"):
            raise ValueError(f"page URL must use HTTPS: {row['page_url']}")
        if not row["year"].isdigit() or len(row["year"]) != 4:
            raise ValueError(f"invalid review year: {row['year']}")
        if not ISO_DATE.fullmatch(row["last_checked"]):
            raise ValueError(f"invalid review date: {row['last_checked']}")
        key = (row["domain"], row["page_url"])
        if key in seen:
            raise ValueError(f"duplicate page review: {key}")
        seen.add(key)
        stratum = (row["domain"], row["year"])
        coverage[stratum] += 1
        relationship = row["award_relationship"].casefold()
        statuses.setdefault(stratum, set())
        for status in STATUSES:
            if status in relationship:
                statuses[stratum].add(status)
        classes[row["domain"]].update(review_classes(row["award_relationship"]))
    for domain in DOMAINS:
        for year in BENCHMARK_YEARS:
            count = coverage[(domain, year)]
            if count < MIN_REVIEWS_PER_DOMAIN_YEAR:
                raise ValueError(
                    f"{domain} {year}: needs at least {MIN_REVIEWS_PER_DOMAIN_YEAR} reviewed pages; found {count}"
                )
            missing_statuses = STATUSES - statuses.get((domain, year), set())
            if missing_statuses:
                raise ValueError(
                    f"{domain} {year}: reviewed-page sample lacks {', '.join(sorted(missing_statuses))} coverage"
                )
        missing_classes = SECTIONS - classes[domain]
        if missing_classes:
            raise ValueError(
                f"{domain}: reviewed-page sample lacks competition classes {', '.join(sorted(missing_classes))}"
            )


def validate_sources(rows: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    for row in rows:
        if not row["year"].isdigit() or len(row["year"]) != 4:
            raise ValueError(f"invalid source year: {row['year']}")
        if row["year"] in seen:
            raise ValueError(f"duplicate source year: {row['year']}")
        seen.add(row["year"])
        if not row["awards_endpoint"].startswith("https://api.igem.org/"):
            raise ValueError(f"source endpoint must use the official iGEM API: {row['awards_endpoint']}")
        if not ISO_DATE.fullmatch(row["retrieved_on"]):
            raise ValueError(f"invalid source retrieval date: {row['retrieved_on']}")
        if not SHA256.fullmatch(row["sha256"]):
            raise ValueError(f"invalid source SHA-256: {row['sha256']}")


def md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def wiki_url(row: dict[str, str]) -> str:
    if row["year"] == "2021":
        return f"https://2021.igem.org/Team:{row['team_slug']}"
    return f"https://{row['year']}.igem.wiki/{row['team_slug']}/"


def award_sort(row: dict[str, str]) -> tuple[object, ...]:
    return (
        -int(row["year"]),
        row["award"],
        row["section"],
        0 if row["status"] == "winner" else 1,
        row["team"].casefold(),
    )


def domain_index(domain: str, awards: list[dict[str, str]], reviews: list[dict[str, str]]) -> str:
    _, label = DOMAINS[domain]
    domain_awards = sorted((row for row in awards if row["domain"] == domain), key=award_sort)
    domain_reviews = sorted(
        (row for row in reviews if row["domain"] == domain),
        key=lambda row: (-int(row["year"]), row["team"].casefold(), row["page_type"]),
    )
    winners = sum(row["status"] == "winner" for row in domain_awards)
    lines = [
        f"# {label} award and page-review index",
        "",
        "> Generated by `scripts/build_corpus.py`. Edit the CSV files in `corpus/`, not this file.",
        "",
        "Award records are official Results-page facts. Page-review notes are independent observations. Do not infer page quality from award status alone.",
        "",
        f"Coverage: **{len(domain_awards)} award records** ({winners} winners, {len(domain_awards) - winners} nominees) and **{len(domain_reviews)} reviewed pages**.",
        "",
        "## Award records",
        "",
        "| Year | Class | Award | Status | Team | Verified |",
        "|---:|---|---|---|---|---|",
    ]
    for row in domain_awards:
        lines.append(
            f"| {row['year']} | {md(row['section'])} | {md(row['award'])} | {row['status']} | "
            f"[{md(row['team'])}]({wiki_url(row)}) | {row['verified_on']} |"
        )
    lines.extend(
        [
            "",
            "## Reviewed pages",
            "",
            "| Year | Team/page | Depth | Award relationship | Reusable observations | Limitation | Checked |",
            "|---:|---|---|---|---|---|---|",
        ]
    )
    for row in domain_reviews:
        lines.append(
            f"| {row['year']} | [{md(row['team'])} — {md(row['page_type'])}]({row['page_url']}) | "
            f"{row['review_depth']} | {md(row['award_relationship'])} | {md(row['strengths'])} | "
            f"{md(row['limitations'])} | {row['last_checked']} |"
        )
    lines.extend(
        [
            "",
            "## Use rule",
            "",
            "Select examples by task fit, evidence type, class, and year—not visual prestige. Verify the live page before quoting or relying on a detail, and keep current judging requirements separate from historical precedent.",
            "",
        ]
    )
    return "\n".join(lines)


def corpus_index(
    awards: list[dict[str, str]], reviews: list[dict[str, str]], sources: list[dict[str, str]]
) -> str:
    lines = [
        "# Benchmark corpus index",
        "",
        "> Generated by `scripts/build_corpus.py`. Edit the CSV files in `corpus/`, not this file.",
        "",
        "This is a dated research corpus, not a leaderboard and not a substitute for current judging guidance.",
        "",
        "## Collection method",
        "",
        "Each domain uses two deliberately separate layers:",
        "",
        "1. **Award records:** winners and nominees verified against the official [iGEM Annual Results](https://competition.igem.org/results/).",
        "2. **Page reviews:** exact pages inspected for structure, evidence, limitations, navigation, and reproducibility.",
        "",
        "An award record does not prove that a page was reviewed or that every claim is exemplary. The corpus is a non-exhaustive research seed and includes contrasting nominees and competition classes.",
        "",
        "## Domain coverage",
        "",
        "| Domain skill | Award records | Winners | Nominees | Reviewed pages | Years represented |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for domain, (skill, _) in DOMAINS.items():
        domain_awards = [row for row in awards if row["domain"] == domain]
        domain_reviews = [row for row in reviews if row["domain"] == domain]
        counts = Counter(row["status"] for row in domain_awards)
        years = ", ".join(sorted({row["year"] for row in domain_awards}, reverse=True))
        lines.append(
            f"| [`{skill}`](../../{skill}/references/generated/award-index.md) | {len(domain_awards)} | "
            f"{counts['winner']} | {counts['nominee']} | {len(domain_reviews)} | {years} |"
        )
    lines.extend(
        [
            "",
            "Counts are award-category records; a team may appear in multiple categories. Review coverage follows the portable [sampling policy](sampling-policy.md).",
            "",
            "## Year-by-year coverage",
            "",
            "Each cell reports `official award records / inspected pages`. The policy enforces a review floor, not equal-sized samples.",
            "",
            "| Domain | 2021 | 2022 | 2023 | 2024 | 2025 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for domain, (skill, _) in DOMAINS.items():
        cells = []
        for year in BENCHMARK_YEARS:
            award_count = sum(
                row["domain"] == domain and row["year"] == year for row in awards
            )
            review_count = sum(
                row["domain"] == domain and row["year"] == year for row in reviews
            )
            cells.append(f"{award_count} / {review_count}")
        lines.append(f"| [`{skill}`](../../{skill}/references/generated/award-index.md) | " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "## Reviewed-page sample balance",
            "",
            "Winner-linked and nominee-linked counts may overlap when one page has both relationships.",
            "",
            "| Domain | Winner-linked | Nominee-linked | Classes represented |",
            "|---|---:|---:|---|",
        ]
    )
    for domain, (skill, _) in DOMAINS.items():
        domain_reviews = [row for row in reviews if row["domain"] == domain]
        winner_linked = sum("winner" in row["award_relationship"].casefold() for row in domain_reviews)
        nominee_linked = sum("nominee" in row["award_relationship"].casefold() for row in domain_reviews)
        classes = sorted(
            {item for row in domain_reviews for item in review_classes(row["award_relationship"])},
            key=("undergrad", "overgrad", "high-school").index,
        )
        lines.append(
            f"| [`{skill}`](../../{skill}/references/generated/award-index.md) | {winner_linked} | "
            f"{nominee_linked} | {', '.join(classes)} |"
        )
    lines.extend(
        [
            "",
            "## Official machine-source snapshots",
            "",
            "| Year | Official endpoint | Retrieved | SHA-256 |",
            "|---:|---|---|---|",
        ]
    )
    for row in sorted(sources, key=lambda item: -int(item["year"])):
        lines.append(
            f"| {row['year']} | [award results]({row['awards_endpoint']}) | "
            f"{row['retrieved_on']} | `{row['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Expansion rule",
            "",
            "Add an official award record before using award status. Add a page-review record only after inspecting the exact page. Record both a reusable decision and a limitation. Follow the [sampling policy](sampling-policy.md), and add class, year, and nominee counterexamples before treating a presentation pattern as universal.",
            "",
        ]
    )
    return "\n".join(lines)


def outputs(
    awards: list[dict[str, str]], reviews: list[dict[str, str]], sources: list[dict[str, str]]
) -> dict[Path, str]:
    generated = {
        ROOT / "igem-wiki" / "references" / "corpus-index.md": corpus_index(
            awards, reviews, sources
        )
    }
    for domain, (skill, _) in DOMAINS.items():
        generated[ROOT / skill / "references" / "generated" / "award-index.md"] = domain_index(
            domain, awards, reviews
        )
    return generated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated indexes are stale")
    args = parser.parse_args()
    awards = read_csv(
        "award_records.csv",
        ("domain", "year", "section", "award", "status", "team", "team_slug", "verified_on"),
    )
    reviews = read_csv(
        "page_reviews.csv",
        (
            "domain",
            "year",
            "team",
            "team_slug",
            "page_type",
            "page_url",
            "review_depth",
            "last_checked",
            "award_relationship",
            "strengths",
            "limitations",
        ),
    )
    validate_awards(awards)
    validate_reviews(reviews)
    sources = read_csv(
        "source_manifest.csv",
        ("year", "competition_uuid", "awards_endpoint", "retrieved_on", "sha256"),
    )
    validate_sources(sources)
    stale: list[str] = []
    for path, content in outputs(awards, reviews, sources).items():
        expected = content.rstrip() + "\n"
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
    if stale:
        print("Generated corpus indexes are stale:")
        for path in stale:
            print(f"- {path}")
        return 1
    action = "Checked" if args.check else "Generated"
    print(
        f"{action} {len(DOMAINS) + 1} indexes from {len(awards)} award records, "
        f"{len(reviews)} page-review records, and {len(sources)} official source snapshots."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
