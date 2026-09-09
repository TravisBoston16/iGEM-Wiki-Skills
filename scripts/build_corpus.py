#!/usr/bin/env python3
"""Validate the research corpus and generate per-domain Markdown indexes."""

from __future__ import annotations

import argparse
import csv
import hashlib
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
MODEL_ARCHETYPES = {
    "mechanistic-kinetic",
    "stochastic",
    "structural-sequence",
    "data-driven-ml",
    "spatial-multiscale",
    "hybrid",
    "unclear",
}
MODEL_VALIDATION_TYPES = {
    "experimental-comparison",
    "literature-benchmark",
    "internal-consistency",
    "sensitivity-analysis",
    "cross-validation",
    "illustrative-only",
    "none-or-unclear",
}
MODEL_DATA_SOURCES = {
    "team-experiment",
    "public-database",
    "literature",
    "simulated",
    "assumed",
    "manually-constructed",
    "unclear",
}
MODEL_PROJECT_DECISIONS = {
    "design-selection",
    "parameter-estimation",
    "construct-selection",
    "stopping-policy",
    "experimental-prioritization",
    "hardware-design",
    "interpretation",
    "future-work",
    "no-demonstrated-decision",
}
MODEL_PARAMETER_PROVENANCE = {
    "team-fitted",
    "team-measured",
    "literature-derived",
    "assumed",
    "tool-default",
    "derived",
    "unclear",
    "not-applicable",
}
MODEL_EVIDENCE_SCOPES = {
    "validated-with-team-data",
    "partially-validated",
    "literature-benchmarked",
    "internally-checked",
    "illustrative",
    "proposed",
    "unclear",
}
MODEL_REPRODUCTION_PATHS = {
    "code-linked",
    "method-described",
    "interactive-tool",
    "data-linked",
    "page-only",
}


def read_csv(name: str, required: tuple[str, ...]) -> list[dict[str, str]]:
    path = CORPUS / name
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != required:
            raise ValueError(f"{name}: expected columns {required}, got {reader.fieldnames}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{name}:{line_number}: too many CSV fields")
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
        if not SHA256.fullmatch(row["competitions_sha256"]):
            raise ValueError(f"invalid competitions SHA-256: {row['competitions_sha256']}")
        results_snapshot = ROOT / row["results_snapshot"]
        competitions_snapshot = ROOT / row["competitions_snapshot"]
        for label, path in (
            ("results snapshot", results_snapshot),
            ("competitions snapshot", competitions_snapshot),
        ):
            if not path.is_file() or not path.resolve().is_relative_to(ROOT):
                raise ValueError(f"missing or out-of-repository {label}: {path}")
        snapshot_hash = hashlib.sha256(results_snapshot.read_bytes()).hexdigest()
        if snapshot_hash != row["sha256"]:
            raise ValueError(f"results snapshot hash mismatch for {row['year']}")
        competitions_hash = hashlib.sha256(competitions_snapshot.read_bytes()).hexdigest()
        if competitions_hash != row["competitions_sha256"]:
            raise ValueError(f"competitions snapshot hash mismatch for {row['year']}")
    missing = set(BENCHMARK_YEARS) - seen
    if missing:
        raise ValueError(
            f"source manifest is missing benchmark years {', '.join(sorted(missing))}"
        )


def split_tokens(value: str) -> list[str]:
    return [token.strip() for token in value.split(";") if token.strip()]


def validate_model_metadata(
    rows: list[dict[str, str]], reviews: list[dict[str, str]]
) -> None:
    model_reviews = {
        (row["year"], row["team_slug"], row["page_url"]): row["team"]
        for row in reviews
        if row["domain"] == "model"
    }
    seen: set[tuple[str, str, str]] = set()
    vocabularies = {
        "model_archetype": MODEL_ARCHETYPES,
        "validation_type": MODEL_VALIDATION_TYPES,
        "data_source": MODEL_DATA_SOURCES,
        "project_decision": MODEL_PROJECT_DECISIONS,
    }
    for row in rows:
        key = (row["year"], row["team_slug"], row["page_url"])
        if key in seen:
            raise ValueError(f"duplicate Model metadata row: {key}")
        seen.add(key)
        if key not in model_reviews:
            raise ValueError(f"Model metadata has no matching reviewed page: {key}")
        if row["team"] != model_reviews[key]:
            raise ValueError(
                f"Model metadata team does not match reviewed page for {key}: {row['team']}"
            )
        for field, allowed in vocabularies.items():
            tokens = split_tokens(row[field])
            if len(tokens) != len(set(tokens)):
                raise ValueError(f"duplicate {field} token for {row['team']}: {row[field]}")
            unknown = set(tokens) - allowed
            if unknown:
                raise ValueError(
                    f"unknown {field} token for {row['team']}: {', '.join(sorted(unknown))}"
                )
    missing = set(model_reviews) - seen
    if missing:
        raise ValueError(f"Model metadata is missing reviewed pages: {sorted(missing)}")


def validate_model_modules(
    rows: list[dict[str, str]],
    reviews: list[dict[str, str]],
    model_metadata: list[dict[str, str]],
) -> None:
    model_reviews = {
        (row["year"], row["team_slug"], row["page_url"]): row["team"]
        for row in reviews
        if row["domain"] == "model"
    }
    parent_metadata = {
        (row["year"], row["team_slug"], row["page_url"]): row
        for row in model_metadata
    }
    token_vocabularies = {
        "model_archetype": MODEL_ARCHETYPES,
        "validation_type": MODEL_VALIDATION_TYPES,
        "data_source": MODEL_DATA_SOURCES,
        "project_decision": MODEL_PROJECT_DECISIONS,
        "parameter_provenance": MODEL_PARAMETER_PROVENANCE,
        "reproduction_path": MODEL_REPRODUCTION_PATHS,
    }
    parent_fields = (
        "model_archetype",
        "validation_type",
        "data_source",
        "project_decision",
    )
    seen: set[tuple[str, str, str, str]] = set()
    for row in rows:
        page_key = (row["year"], row["team_slug"], row["page_url"])
        module_key = (*page_key, row["module_id"])
        if module_key in seen:
            raise ValueError(f"duplicate Model module row: {module_key}")
        seen.add(module_key)
        if page_key not in model_reviews:
            raise ValueError(f"Model module has no matching reviewed page: {page_key}")
        if row["team"] != model_reviews[page_key]:
            raise ValueError(
                f"Model module team does not match reviewed page for {page_key}: {row['team']}"
            )
        if not AWARD.fullmatch(row["module_id"]):
            raise ValueError(f"invalid Model module identifier: {row['module_id']}")
        if row["page_anchor"] != "page-root" and not re.fullmatch(r"#[^\s#]+", row["page_anchor"]):
            raise ValueError(
                f"invalid Model module anchor for {row['team']} {row['module_id']}: {row['page_anchor']}"
            )
        if not ISO_DATE.fullmatch(row["last_checked"]):
            raise ValueError(f"invalid Model module review date: {row['last_checked']}")
        if row["evidence_scope"] not in MODEL_EVIDENCE_SCOPES:
            raise ValueError(
                f"unknown evidence_scope for {row['team']} {row['module_id']}: {row['evidence_scope']}"
            )
        for field, allowed in token_vocabularies.items():
            tokens = split_tokens(row[field])
            if len(tokens) != len(set(tokens)):
                raise ValueError(
                    f"duplicate {field} token for {row['team']} {row['module_id']}: {row[field]}"
                )
            unknown = set(tokens) - allowed
            if unknown:
                raise ValueError(
                    f"unknown {field} token for {row['team']} {row['module_id']}: "
                    f"{', '.join(sorted(unknown))}"
                )
        if "page-only" in split_tokens(row["reproduction_path"]) and len(
            split_tokens(row["reproduction_path"])
        ) > 1:
            raise ValueError(
                f"page-only cannot be combined with another reproduction path for "
                f"{row['team']} {row['module_id']}"
            )
        parent = parent_metadata[page_key]
        for field in parent_fields:
            child_tokens = set(split_tokens(row[field]))
            parent_tokens = set(split_tokens(parent[field]))
            if not child_tokens <= parent_tokens:
                raise ValueError(
                    f"Model module {field} exceeds its page taxonomy for "
                    f"{row['team']} {row['module_id']}: {', '.join(sorted(child_tokens - parent_tokens))}"
                )
    missing_years = set(BENCHMARK_YEARS) - {row["year"] for row in rows}
    if missing_years:
        raise ValueError(
            "Model module corpus is missing benchmark years "
            f"{', '.join(sorted(missing_years))}"
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


def model_taxonomy_index(rows: list[dict[str, str]]) -> str:
    ordered = sorted(rows, key=lambda row: (-int(row["year"]), row["team"].casefold()))
    archetypes = Counter(
        token for row in rows for token in split_tokens(row["model_archetype"])
    )
    validations = Counter(
        token for row in rows for token in split_tokens(row["validation_type"])
    )
    lines = [
        "# Model precedent taxonomy",
        "",
        "> Generated by `scripts/build_corpus.py` from exact-page review metadata.",
        "",
        "Use these labels to select scientifically relevant precedents rather than defaulting to the newest winner. Labels are bounded research annotations, not iGEM award categories or claims that every method on a page was exhaustively classified.",
        "",
        "## Coverage summary",
        "",
        f"Reviewed Model pages: **{len(rows)}**.",
        "",
        f"Archetypes: {', '.join(f'`{name}`: {count}' for name, count in sorted(archetypes.items()))}.",
        "",
        f"Validation types: {', '.join(f'`{name}`: {count}' for name, count in sorted(validations.items()))}.",
        "",
        "## Page-level labels",
        "",
        "| Year | Team | Model archetype | Validation | Data source | Project decision |",
        "|---:|---|---|---|---|---|",
    ]
    for row in ordered:
        lines.append(
            f"| {row['year']} | [{md(row['team'])}]({row['page_url']}) | "
            f"{md(row['model_archetype'])} | {md(row['validation_type'])} | "
            f"{md(row['data_source'])} | {md(row['project_decision'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A label records that the inspected page visibly uses that role or evidence type; it does not certify correctness, independent validation, or completeness. Read the reviewed-page limitation and verify the live page before relying on a detail.",
            "",
        ]
    )
    return "\n".join(lines)


def model_modules_index(rows: list[dict[str, str]]) -> str:
    ordered = sorted(
        rows,
        key=lambda row: (-int(row["year"]), row["team"].casefold(), row["module_id"]),
    )
    archetypes = Counter(
        token for row in rows for token in split_tokens(row["model_archetype"])
    )
    scopes = Counter(row["evidence_scope"] for row in rows)
    years = Counter(row["year"] for row in rows)
    lines = [
        "# Model module evidence index",
        "",
        "> Generated by `scripts/build_corpus.py` from module-level exact-page inspections.",
        "",
        "Use this index to retrieve a comparable model module by biological question, method, evidence scope, and project decision. A module row is a bounded research annotation, not an endorsement of correctness or an official iGEM category.",
        "",
        "## Coverage summary",
        "",
        f"Inspected modules: **{len(rows)}** across **{len({(row['year'], row['team_slug'], row['page_url']) for row in rows})} Model pages**.",
        "",
        f"Modules by year: {', '.join(f'{year}: {years[year]}' for year in BENCHMARK_YEARS)}.",
        "",
        f"Archetypes: {', '.join(f'`{name}`: {count}' for name, count in sorted(archetypes.items()))}.",
        "",
        f"Evidence scope: {', '.join(f'`{name}`: {count}' for name, count in sorted(scopes.items()))}.",
        "",
        "## Module-level evidence",
        "",
        "| Year | Team/module | Biological question | Archetype | Validation and evidence scope | Project decision | Reproduction path | Limitation |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in ordered:
        target = row["page_url"]
        if row["page_anchor"] != "page-root":
            target += row["page_anchor"]
        lines.append(
            f"| {row['year']} | [{md(row['team'])} — {md(row['module_name'])}]({target}) | "
            f"{md(row['biological_question'])} | {md(row['model_archetype'])} | "
            f"{md(row['validation_type'])}; **{md(row['evidence_scope'])}** | "
            f"{md(row['project_decision'])} | {md(row['reproduction_path'])} | "
            f"{md(row['limitations'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "Read the method summary, parameter provenance, and data source in `corpus/model_modules.csv` or query them with `scripts/query_corpus.py`. Verify the live page before relying on a consequential detail. `page-root` means a stable module anchor was not established; do not invent one.",
            "",
        ]
    )
    return "\n".join(lines)


def corpus_index(
    awards: list[dict[str, str]],
    reviews: list[dict[str, str]],
    sources: list[dict[str, str]],
    model_metadata: list[dict[str, str]],
    model_modules: list[dict[str, str]],
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
            f"Model reviews share one Standard URL, so diversity is assessed through both the generated [Model taxonomy](../../igem-model-wiki/references/generated/model-taxonomy.md) and **{len(model_modules)}** inspected entries in the [module evidence index](../../igem-model-wiki/references/generated/model-modules.md). The module layer records biological question, method, parameter provenance, validation, project decision, reproduction path, evidence scope, and limitations.",
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
            "| Year | Official endpoint | Preserved input | Retrieved | SHA-256 |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in sorted(sources, key=lambda item: -int(item["year"])):
        lines.append(
            f"| {row['year']} | [award results]({row['awards_endpoint']}) | "
            f"`{row['results_snapshot']}` | "
            f"{row['retrieved_on']} | `{row['sha256']}` |"
        )
    competition_source = sources[0]
    lines.extend(
        [
            "",
            f"Competition UUID resolution input: `{competition_source['competitions_snapshot']}` "
            f"(`{competition_source['competitions_sha256']}`).",
            "",
            "## Expansion rule",
            "",
            "Add an official award record before using award status. Add a page-review record only after inspecting the exact page. Record both a reusable decision and a limitation. Follow the [sampling policy](sampling-policy.md), and add class, year, and nominee counterexamples before treating a presentation pattern as universal.",
            "",
        ]
    )
    return "\n".join(lines)


def outputs(
    awards: list[dict[str, str]],
    reviews: list[dict[str, str]],
    sources: list[dict[str, str]],
    model_metadata: list[dict[str, str]],
    model_modules: list[dict[str, str]],
) -> dict[Path, str]:
    generated = {
        ROOT / "igem-wiki" / "references" / "corpus-index.md": corpus_index(
            awards, reviews, sources, model_metadata, model_modules
        ),
        ROOT / "igem-model-wiki" / "references" / "generated" / "model-taxonomy.md": (
            model_taxonomy_index(model_metadata)
        ),
        ROOT / "igem-model-wiki" / "references" / "generated" / "model-modules.md": (
            model_modules_index(model_modules)
        ),
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
    model_metadata = read_csv(
        "model_review_metadata.csv",
        (
            "year",
            "team",
            "team_slug",
            "page_url",
            "model_archetype",
            "validation_type",
            "data_source",
            "project_decision",
        ),
    )
    validate_model_metadata(model_metadata, reviews)
    model_modules = read_csv(
        "model_modules.csv",
        (
            "year",
            "team",
            "team_slug",
            "page_url",
            "module_id",
            "module_name",
            "page_anchor",
            "biological_question",
            "model_archetype",
            "method_summary",
            "data_source",
            "parameter_provenance",
            "validation_type",
            "project_decision",
            "evidence_scope",
            "reproduction_path",
            "limitations",
            "last_checked",
        ),
    )
    validate_model_modules(model_modules, reviews, model_metadata)
    sources = read_csv(
        "source_manifest.csv",
        (
            "year",
            "competition_uuid",
            "awards_endpoint",
            "retrieved_on",
            "sha256",
            "competitions_sha256",
            "results_snapshot",
            "competitions_snapshot",
        ),
    )
    validate_sources(sources)
    stale: list[str] = []
    generated = outputs(awards, reviews, sources, model_metadata, model_modules)
    for path, content in generated.items():
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
        f"{action} {len(generated)} indexes from {len(awards)} award records, "
        f"{len(reviews)} page-review records, {len(model_metadata)} Model taxonomy records, "
        f"{len(model_modules)} Model module records, and {len(sources)} official source snapshots."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
