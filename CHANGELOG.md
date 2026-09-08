# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Full 2021–2025 official Results imports for every mapped award family including the four current Part award families.
- Eighteen exact-page reviews covering previously thin Description, Awards, Results, Experiments, Notebook, Parts, Education, Inclusivity, Implementation, and Contribution functions.
- Compact reviewed-page indexes and separate full official award ledgers for progressive loading.
- Dependency-free corpus query and read-only static-wiki audit tools.
- Team intake, judging-readiness, production-board, and browser-QA templates.
- Functional-coverage, structured-award-link, progressive-loading, and static-audit evaluation scenarios.

### Changed

- Page reviews now carry a structured primary official award relationship validated against the award inventory.
- Sampling policy now treats page function as an explicit axis without imposing an every-year-by-function quota.
- The corpus source manifest must cover every maintained benchmark year.
- Team slugs imported from official results are normalized to portable URL-safe identifiers.
- Coordinator routing now handles the current Alternative Platform category and keeps Best Presentation outside wiki-page precedent sampling.

## [0.5.0] - 2026-09-08

### Added

- 128 official Best Wiki and Best Model records for 2022–2024, bringing the corpus to 739 award-category records.
- 14 inspected pages that close domain-year gaps, bringing the page-review corpus to 76 records.
- A portable benchmark sampling policy with explicit domain-year, award-status, competition-class, and cross-year inference rules.
- Generated year-by-year coverage and reviewed-sample balance tables.

### Changed

- Story and Model award inventories now cover every maintained year rather than 2021/2025 bookends plus selected intervening winners.
- Curated benchmark notes now include the newly inspected cross-year winner and nominee contrasts.
- Corpus validation now rejects missing benchmark years, insufficient domain-year review depth, missing winner or nominee coverage, and missing competition classes.
- The generated coordinator index no longer depends on a repository-external relative link when skills are installed project-locally.

## [0.4.0] - 2026-09-08

### Added

- 312 official 2022–2024 award-category records for Wet Lab, Human Practices, and Implementation, bringing the corpus to 611 records.
- 18 inspected winner and nominee pages across the three expanded domains, bringing page reviews to 62.
- Annual Results API importer and a source manifest containing competition identifiers, retrieval dates, endpoints, and response hashes.
- Curated 2022–2024 comparison tables in the three domain benchmark corpora.
- Evaluation scenarios for API-based corpus updates and client-rendered pages.

### Changed

- Generated corpus indexes now expose official machine-source provenance.
- Repository validation now requires and validates the source manifest and importer.

## [0.3.0] - 2026-09-08

### Added

- Machine-readable award and page-review CSV corpus with a documented schema.
- 299 official award-category records across five wiki domains.
- 44 domain-scoped page-review records with reusable observations and explicit limitations.
- Generated award/page indexes for every domain skill.
- Dependency-free corpus generator and stale-output validation.

### Changed

- Domain skills now use generated indexes as the canonical local award inventory while preserving curated interpretive notes.
- Repository validation and CI now check corpus integrity and generated artifacts.

## [0.2.0] - 2026-09-08

### Added

- Dated 2026 judging, Standard URL, eligibility, and freeze snapshot.
- AI use, scientific-integrity, privacy, verification, and attribution protocol.
- Cross-page Claim-Evidence Register and evidence-maturity vocabulary.
- Seven reusable evidence and documentation templates.
- UI metadata for every skill.
- Dependency-free repository validator and GitHub Actions workflow.
- Behavior-oriented evaluation scenarios for routing, evidence boundaries, current-season compliance, and read-only scope.

### Changed

- Extended the coordinator with competition-phase guidance and current-season routing.
- Strengthened domain instructions for single-case generalization, AI-assisted analysis, Registry dependencies, and 2026 Software eligibility.
- Expanded whole-wiki review checks for AI disclosure, Standard URLs, external artifacts, and pre-freeze compliance.

## [0.1.0] - 2026-09-08

### Added

- Initial coordinator and five domain skills.
- Winner and nominee benchmark corpora.
- Whole-wiki, Model, evidence, UX, and reproducibility checklists.
