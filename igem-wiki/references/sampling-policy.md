# Benchmark sampling policy

Use this policy whenever the benchmark corpus is expanded or cross-year principles are inferred from it. The goal is auditable coverage, not equal-sized samples or a ranking of teams.

## Keep two evidence layers separate

1. **Official award inventory:** import every winner and nominee in the selected award families for every year in the benchmark interval from the official iGEM Results page or API.
2. **Reviewed-page sample:** inspect exact pages and record the reusable decision, evidence boundary, and at least one limitation. Award status alone is not a page review.

The maintained historical interval is **2021–2025**. Current-season requirements are verified separately and are never inferred from the historical sample.

## Minimum review strata

For each domain and each year in the maintained interval:

- review at least two exact pages;
- include at least one award winner and at least one nominee where both exist;
- across the full five-year domain sample, include Undergrad, Overgrad, and High School teams;
- for broad domains, cover more than one relevant page function or award family rather than treating one page type as representative of the whole domain;
- record a concrete limitation, counterexample, or unresolved evidence boundary for every page.

These are minimum floors, not quotas. Some domains legitimately contain more award families or more useful page types, so raw counts need not be equal. Report year-by-year counts so readers can see remaining imbalance.

## Functional coverage

Use page function as a separate sampling axis. Do not demand every function in every year; that would reward mechanical volume and may be impossible when categories or Standard URLs change. Instead maintain at least one or two useful reviews for each in-scope core function across the interval, include contrasting evidence where possible, and report gaps explicitly.

- **Story:** Home; Description or Project Description; Awards or Judging; site-level navigation and accessibility.
- **Wet lab:** Engineering; Results; Measurement; Experiments or Protocols; Parts and Registry handoff; Notebook.
- **Model:** vary model archetype and decision role rather than page slug—for example mechanistic or kinetic; stochastic; structural or sequence; data-driven or machine-learning; spatial or multiscale when relevant. Use the controlled Model metadata rather than inferring diversity from team names or years.
- **Human Practices:** Human Practices or IHP; Education; Inclusivity; Sustainability.
- **Implementation:** Implementation; Safety and Security; Hardware; Software; Entrepreneurship; Contribution.

Record page type in the corpus. For Model reviews, maintain the dedicated archetype, validation, data-source, and project-decision metadata. A missing function is a research backlog item, not permission to generalize from a different page type.

## Cross-year inference rule

Call a pattern "recurring" or "cross-year" only when it is supported by reviewed pages from at least three competition years and at least two competition classes, with at least one limitation or counterexample considered. Otherwise label it as an example, a provisional pattern, or a year-specific observation.

Do not infer scientific quality, judging causality, or a current rule from award status. Prefer decisions that can be tied to visible evidence: page structure, claim qualification, validation, reproducibility, stakeholder influence, accessibility, or navigation.

## Unavailable or client-rendered pages

- Do not create a page-review row unless the exact page was opened and inspected.
- If essential content cannot be read because rendering failed, retain the observation only as an accessibility or robustness caution; do not treat unseen scientific content as reviewed.
- Record the inspection date and recheck a page before relying on details that may have changed.

## Maintenance sequence

1. Import or verify award records.
2. Inspect pages against the missing domain-year, award-status, class, and page-function strata; prioritize a real user or judging need over equal counts.
3. Add review rows with strengths and limitations.
4. Rebuild the generated indexes.
5. Run repository validation and inspect the year-by-year coverage table before release.

Official starting points: [iGEM Annual Results](https://competition.igem.org/results/) and [iGEM Special Prizes](https://competition.igem.org/judging/special-prizes).
