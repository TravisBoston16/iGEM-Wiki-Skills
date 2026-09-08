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
CORE_PAGE_FUNCTIONS = {
    "story": ("home", "description", "awards"),
    "wetlab": ("engineering", "results", "measurement", "experiments", "parts", "notebook"),
    "model": ("model",),
    "hp": ("human-practices", "education", "inclusivity", "sustainability"),
    "implementation": (
        "implementation",
        "safety",
        "hardware",
        "software",
        "entrepreneurship",
        "contribution",
    ),
}
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


def normalized_team(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def canonical_page_function(value: str) -> str:
    aliases = {
        "project-description": "description",
        "human_practices": "human-practices",
    }
    return aliases.get(value, value)


def validate_reviews(
    rows: list[dict[str, str]], awards: list[dict[str, str]]
) -> None:
    seen: set[tuple[str, str]] = set()
    coverage: Counter[tuple[str, str]] = Counter()
    statuses: dict[tuple[str, str], set[str]] = {}
    classes: dict[str, set[str]] = {domain: set() for domain in DOMAINS}
    official = {
        (
            row["domain"],
            row["year"],
            row["section"],
            row["award"],
            row["status"],
            normalized_team(row["team_slug"]),
        )
        for row in awards
    }
    for row in rows:
        if row["domain"] not in DOMAINS:
            raise ValueError(f"unknown domain: {row['domain']}")
        if row["award_domain"] not in DOMAINS:
            raise ValueError(f"unknown linked award domain: {row['award_domain']}")
        if row["award_status"] not in STATUSES:
            raise ValueError(f"unknown linked award status: {row['award_status']}")
        if row["award_section"] not in SECTIONS:
            raise ValueError(f"unknown linked award section: {row['award_section']}")
        if not AWARD.fullmatch(row["award"]):
            raise ValueError(f"invalid linked award identifier: {row['award']}")
        if row["review_depth"] not in DEPTHS:
            raise ValueError(f"unknown review depth: {row['review_depth']}")
        if not row["page_url"].startswith("https://"):
            raise ValueError(f"page URL must use HTTPS: {row['page_url']}")
        if not row["year"].isdigit() or len(row["year"]) != 4:
            raise ValueError(f"invalid review year: {row['year']}")
        if not ISO_DATE.fullmatch(row["last_checked"]):
            raise ValueError(f"invalid review date: {row['last_checked']}")
        award_key = (
            row["award_domain"],
            row["year"],
            row["award_section"],
            row["award"],
            row["award_status"],
            normalized_team(row["team_slug"]),
        )
        if award_key not in official:
            raise ValueError(
                f"page review does not match an official award record: {award_key}"
            )
        key = (row["domain"], row["page_url"])
        if key in seen:
            raise ValueError(f"duplicate page review: {key}")
        seen.add(key)
        stratum = (row["domain"], row["year"])
        coverage[stratum] += 1
        statuses.setdefault(stratum, set())
        statuses[stratum].add(row["award_status"])
        classes[row["domain"]].add(row["award_section"])
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
    missing = set(BENCHMARK_YEARS) - seen
    if missing:
        raise ValueError(
            f"source manifest is missing benchmark years {', '.join(sorted(missing))}"
        )


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
    domain_awards = [row for row in awards if row["domain"] == domain]
    domain_reviews = [row for row in reviews if row["domain"] == domain]
    winners = sum(row["status"] == "winner" for row in domain_awards)
    year_counts = Counter(row["year"] for row in domain_reviews)
    page_types = Counter(canonical_page_function(row["page_type"]) for row in domain_reviews)
    lines = [
        f"# {label} benchmark index",
        "",
        "> Generated by `scripts/build_corpus.py`. Edit the CSV files in `corpus/`, not this file.",
        "",
        "Award records are official Results-page facts. Page-review notes are independent observations. Do not infer page quality from award status alone.",
        "",
        f"Coverage: **{len(domain_awards)} award records** ({winners} winners, {len(domain_awards) - winners} nominees) and **{len(domain_reviews)} reviewed pages**.",
        "",
        "## Load only what the task needs",
        "",
        "- Read [reviewed-pages.md](reviewed-pages.md) for inspected examples, reusable observations, and limitations.",
        "- Read [award-ledger.md](award-ledger.md) only when verifying or listing official winners and nominees.",
        "- Read the curated `../benchmark-corpus.md` for synthesized domain principles.",
        "",
        "## Review coverage",
        "",
        "| Dimension | Coverage |",
        "|---|---|",
        f"| Years | {', '.join(f'{year}: {year_counts[year]}' for year in BENCHMARK_YEARS)} |",
        f"| Page functions | {', '.join(f'{name}: {count}' for name, count in sorted(page_types.items()))} |",
        "",
        "## Use rule",
        "",
        "Select examples by task fit, evidence type, class, year, and page function—not visual prestige. Verify the live page before quoting or relying on a detail, and keep current judging requirements separate from historical precedent.",
        "",
    ]
    return "\n".join(lines)


def reviewed_pages_index(domain: str, reviews: list[dict[str, str]]) -> str:
    _, label = DOMAINS[domain]
    domain_reviews = sorted(
        (row for row in reviews if row["domain"] == domain),
        key=lambda row: (-int(row["year"]), row["page_type"], row["team"].casefold()),
    )
    lines = [
        f"# {label} reviewed pages",
        "",
        "> Generated by `scripts/build_corpus.py` from exact-page inspections.",
        "",
        "Read this compact file for precedent selection. Award relationships are checked against the official ledger, but award status does not prove page quality.",
        "",
        "| Year | Team/page | Depth | Primary award relationship | Reusable observations | Limitation | Checked |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in domain_reviews:
        lines.append(
            f"| {row['year']} | [{md(row['team'])} — {md(row['page_type'])}]({row['page_url']}) | "
            f"{row['review_depth']} | {md(row['award_relationship'])} | {md(row['strengths'])} | "
            f"{md(row['limitations'])} | {row['last_checked']} |"
        )
    lines.append("")
    return "\n".join(lines)


def award_ledger(domain: str, awards: list[dict[str, str]]) -> str:
    _, label = DOMAINS[domain]
    domain_awards = sorted((row for row in awards if row["domain"] == domain), key=award_sort)
    lines = [
        f"# {label} official award ledger",
        "",
        "> Generated by `scripts/build_corpus.py` from `corpus/award_records.csv`.",
        "",
        "Use this file only for award lookup. It does not assert that a linked team page was reviewed or exemplary.",
        "",
        "| Year | Class | Award | Status | Team | Verified |",
        "|---:|---|---|---|---|---|",
    ]
    for row in domain_awards:
        lines.append(
            f"| {row['year']} | {md(row['section'])} | {md(row['award'])} | {row['status']} | "
            f"[{md(row['team'])}]({wiki_url(row)}) | {row['verified_on']} |"
        )
    lines.append("")
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
            "## Page-function coverage",
            "",
            "This table prevents a large sample of one page type from masquerading as domain coverage. One review is marked thin and a dash marks an in-scope function with no exact-page review; both are research signals rather than a claim that every function needs every year.",
            "",
            "| Domain | Function | Reviewed pages | Status |",
            "|---|---|---:|---|",
        ]
    )
    for domain, (skill, _) in DOMAINS.items():
        counts = Counter(
            canonical_page_function(row["page_type"])
            for row in reviews
            if row["domain"] == domain
        )
        for function in CORE_PAGE_FUNCTIONS[domain]:
            count = counts[function]
            status = "covered" if count >= 2 else "thin" if count == 1 else "gap"
            lines.append(
                f"| [`{skill}`](../../{skill}/references/generated/award-index.md) | "
                f"{function} | {count or '—'} | {status} |"
            )
    lines.extend(
        [
            "",
            "Model reviews share one Standard URL, so Model diversity is assessed by archetype and evidence role during precedent selection rather than by page slug alone.",
            "",
            "## Reviewed-page sample balance",
            "",
            "Counts use each review's structured primary award relationship; additional relationships remain in the human-readable note.",
            "",
            "| Domain | Winner-linked | Nominee-linked | Classes represented |",
            "|---|---:|---:|---|",
        ]
    )
    for domain, (skill, _) in DOMAINS.items():
        domain_reviews = [row for row in reviews if row["domain"] == domain]
        winner_linked = sum(row["award_status"] == "winner" for row in domain_reviews)
        nominee_linked = sum(row["award_status"] == "nominee" for row in domain_reviews)
        classes = sorted(
            {row["award_section"] for row in domain_reviews},
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
        generated[ROOT / skill / "references" / "generated" / "award-index.md"] = (
            domain_index(domain, awards, reviews)
        )
        generated[ROOT / skill / "references" / "generated" / "reviewed-pages.md"] = (
            reviewed_pages_index(domain, reviews)
        )
        generated[ROOT / skill / "references" / "generated" / "award-ledger.md"] = (
            award_ledger(domain, awards)
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
            "award_domain",
            "award",
            "award_status",
            "award_section",
            "award_relationship",
            "strengths",
            "limitations",
        ),
    )
    validate_awards(awards)
    validate_reviews(reviews, awards)
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
        f"{action} {len(outputs(awards, reviews, sources))} indexes from {len(awards)} award records, "
        f"{len(reviews)} page-review records, and {len(sources)} official source snapshots."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
