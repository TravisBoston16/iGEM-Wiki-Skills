#!/usr/bin/env python3
"""Validate the structure of behavioral evaluation contracts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^## (\d+)\. .+$", re.MULTILINE)


def main() -> int:
    path = ROOT / "evals" / "scenarios.md"
    text = path.read_text(encoding="utf-8")
    matches = list(HEADING.finditer(text))
    failures: list[str] = []
    numbers = [int(match.group(1)) for match in matches]
    if numbers != list(range(1, len(numbers) + 1)):
        failures.append(f"scenario numbering is not continuous: {numbers}")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        if not re.search(r"^Prompt: `.+`$", section, re.MULTILINE):
            failures.append(f"scenario {match.group(1)} lacks one inline-code Prompt")
        if not re.search(r"^Expected invariants: .+", section, re.MULTILINE):
            failures.append(f"scenario {match.group(1)} lacks Expected invariants")
    if not matches:
        failures.append("no behavioral scenarios found")
    if failures:
        print("Behavioral evaluation contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        f"Validated {len(matches)} behavioral evaluation contracts; "
        "this structural check does not run or score a model."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
