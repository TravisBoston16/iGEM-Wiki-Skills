# Benchmark corpus schema

This directory separates facts about iGEM awards from observations made while reviewing individual wiki pages.

## `award_records.csv`

One row is one team-award-class-year record from the official [iGEM Annual Results](https://competition.igem.org/results/). It does not assert that a particular page was reviewed or that every aspect of the team's wiki is exemplary.

| Field | Meaning |
|---|---|
| `domain` | `story`, `wetlab`, `model`, `hp`, or `implementation` |
| `year` | Competition year |
| `section` | `undergrad`, `overgrad`, or `high-school` |
| `award` | Stable lowercase award identifier |
| `status` | `winner` or `nominee` |
| `team` | Team display name used in this corpus |
| `team_slug` | URL path or legacy 2021 `Team:` identifier |
| `verified_on` | Date on which the award record was checked against the official Results page |

## `page_reviews.csv`

One row is one domain-scoped inspection of an exact page. The same page may have separate rows when it was reviewed for different functions. Observations and limitations are analytical notes, not official iGEM judgments.

| Field | Meaning |
|---|---|
| `domain` | Domain whose skill can reuse the review |
| `year` | Competition year |
| `team` | Team display name |
| `team_slug` | URL identifier used to join records when useful |
| `page_type` | Page function such as `model`, `measurement`, or `home` |
| `page_url` | Exact page inspected |
| `review_depth` | `targeted` or `deep` |
| `last_checked` | Most recent inspection date |
| `award_domain` | Domain of one official award record used as the primary sample link |
| `award` | Stable identifier of that official award |
| `award_status` | `winner` or `nominee` for that official award |
| `award_section` | `undergrad`, `overgrad`, or `high-school` for that official award |
| `award_relationship` | Human-readable reason the page entered the sample; may mention additional relationships |
| `strengths` | Reusable decisions observed on the page |
| `limitations` | A caution, exception, or unresolved weakness |

The four structured award fields act as a foreign-key-like link to `award_records.csv`. The build rejects a page review when its year, normalized team, award domain, award identifier, status, and section do not match an official record. This does not imply that the award was given for the exact page being reviewed; it makes the sampling relationship auditable.

## `source_manifest.csv`

One row records the official machine-readable award-results snapshot used for a competition year. The manifest makes bulk imports auditable without treating an API response as a page review.

| Field | Meaning |
|---|---|
| `year` | Competition year represented by the snapshot |
| `competition_uuid` | Competition identifier returned by the official iGEM API |
| `awards_endpoint` | Exact official API endpoint used for award results |
| `retrieved_on` | Date on which the response was retrieved |
| `sha256` | SHA-256 digest of the raw response bytes |
| `competitions_sha256` | SHA-256 digest of the preserved competitions response |
| `results_snapshot` | Repository-relative path to the exact annual Results JSON whose bytes match `sha256` |
| `competitions_snapshot` | Repository-relative path to the official competitions JSON used to resolve the competition UUID |

## Maintenance contract

1. Verify award rows against the official Results page or its official API before adding or changing them.
2. Do not create a page-review row unless the exact page was opened and inspected.
3. Record a limitation for every review; winner status is not a quality guarantee.
4. Follow the portable [benchmark sampling policy](../igem-wiki/references/sampling-policy.md): for 2021–2025, maintain at least two inspected pages per domain-year, winner and nominee coverage where available, all three competition classes across each domain, and explicit coverage of the domain's core page functions.
5. Treat the sampling floors as minima, not equal-count quotas or a requirement to fill every year-by-function combination; publish year-by-year and function-by-function counts so imbalances remain visible.
6. For a bulk annual-results update, run `python3 scripts/import_annual_results.py --years YEAR ... --verified-on YYYY-MM-DD` first as a dry run, then repeat with `--write`. Live writes preserve the exact official JSON inputs in `corpus/snapshots/`; use that directory with `--source-dir` for an auditable offline import.
7. Run `python3 scripts/build_corpus.py` after editing a corpus CSV.
8. Keep a source-manifest row for every maintained benchmark year and preserve its official endpoint, retrieval date, response hash, and exact raw inputs.
9. Run `python3 scripts/build_corpus.py --check` and `python3 scripts/validate_repository.py` before release.

The corpus is a research seed, not an exhaustive leaderboard. Recheck unstable current-season requirements separately.
