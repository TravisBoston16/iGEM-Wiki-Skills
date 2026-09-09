#!/usr/bin/env python3
"""Query the iGEM wiki benchmark corpus without third-party dependencies."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "awards": ROOT / "corpus" / "award_records.csv",
    "reviews": ROOT / "corpus" / "page_reviews.csv",
    "model-metadata": ROOT / "corpus" / "model_review_metadata.csv",
    "model-modules": ROOT / "corpus" / "model_modules.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=FILES, help="records to query")
    parser.add_argument("--domain")
    parser.add_argument("--year")
    parser.add_argument("--team", help="case-insensitive team-name or slug substring")
    parser.add_argument("--award")
    parser.add_argument("--status", choices=("winner", "nominee"))
    parser.add_argument("--section", choices=("undergrad", "overgrad", "high-school"))
    parser.add_argument("--page-type")
    parser.add_argument("--depth", choices=("targeted", "deep"))
    parser.add_argument("--model-archetype")
    parser.add_argument("--validation-type")
    parser.add_argument("--data-source")
    parser.add_argument("--project-decision")
    parser.add_argument(
        "--module",
        help="case-insensitive module identifier, name, question, or method substring",
    )
    parser.add_argument("--parameter-provenance", "--parameter-source")
    parser.add_argument("--evidence-scope")
    parser.add_argument("--reproduction-path")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--format", choices=("markdown", "json", "csv"), default="markdown")
    return parser.parse_args()


def matches(row: dict[str, str], args: argparse.Namespace) -> bool:
    exact = {
        "domain": args.domain,
        "year": args.year,
        "award": args.award,
        "status": args.status,
        "section": args.section,
        "page_type": args.page_type,
        "review_depth": args.depth,
    }
    for field, wanted in exact.items():
        if wanted and row.get(field) != wanted:
            return False
    if args.team:
        needle = args.team.casefold()
        haystack = f"{row.get('team', '')} {row.get('team_slug', '')}".casefold()
        if needle not in haystack:
            return False
    if args.module:
        needle = args.module.casefold()
        haystack = " ".join(
            row.get(field, "")
            for field in ("module_id", "module_name", "biological_question", "method_summary")
        ).casefold()
        if needle not in haystack:
            return False
    token_filters = {
        "model_archetype": args.model_archetype,
        "validation_type": args.validation_type,
        "data_source": args.data_source,
        "project_decision": args.project_decision,
        "parameter_provenance": args.parameter_provenance,
        "evidence_scope": args.evidence_scope,
        "reproduction_path": args.reproduction_path,
    }
    for field, wanted in token_filters.items():
        if wanted and wanted not in {token.strip() for token in row.get(field, "").split(";")}:
            return False
    return True


def markdown(rows: list[dict[str, str]], kind: str) -> str:
    if not rows:
        return "No matching records.\n"
    if kind == "awards":
        fields = ("year", "domain", "section", "award", "status", "team", "verified_on")
    elif kind == "reviews":
        fields = (
            "year",
            "domain",
            "team",
            "page_type",
            "review_depth",
            "award_relationship",
            "page_url",
            "last_checked",
        )
    elif kind == "model-metadata":
        fields = (
            "year",
            "team",
            "model_archetype",
            "validation_type",
            "data_source",
            "project_decision",
            "page_url",
        )
    else:
        fields = (
            "year",
            "team",
            "module_name",
            "biological_question",
            "model_archetype",
            "validation_type",
            "evidence_scope",
            "project_decision",
            "parameter_provenance",
            "reproduction_path",
            "page_url",
            "page_anchor",
        )
    escape = lambda value: value.replace("|", "\\|").replace("\n", " ")
    lines = ["| " + " | ".join(fields) + " |", "|" + "---|" * len(fields)]
    for row in rows:
        lines.append("| " + " | ".join(escape(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")
    with FILES[args.kind].open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if matches(row, args)]
    rows = rows[: args.limit]
    if args.format == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    elif args.format == "csv":
        if rows:
            writer = csv.DictWriter(__import__("sys").stdout, fieldnames=rows[0])
            writer.writeheader()
            writer.writerows(rows)
    else:
        print(markdown(rows, args.kind), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
