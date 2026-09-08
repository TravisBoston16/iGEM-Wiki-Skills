---
name: igem-wiki
description: Plan, write, implement, or audit an entire iGEM team wiki by coordinating project story, wet-lab evidence, modeling, Human Practices, implementation, and site-wide usability. Use for whole-wiki architecture, cross-page consistency, judging readiness, or work spanning multiple iGEM wiki sections; use a domain subskill for a single specialized section.
---

# iGEM Wiki

Build one coherent, evidence-traceable project record. Treat award-winning wikis as precedents to analyze, not visual templates to copy.

## Route the task

Load only the domain instructions needed for the request:

- **Home, Description, Awards, information architecture, navigation, or visual language:** read `../igem-wiki-story/SKILL.md`.
- **Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, or Notebook:** read `../igem-wetlab-wiki/SKILL.md`.
- **Model, dry-lab analysis, equations, computational figures, or reproducibility:** read `../igem-model-wiki/SKILL.md`.
- **Human Practices, Education, Inclusivity, Sustainability, or stakeholder integration:** read `../igem-hp-wiki/SKILL.md`.
- **Implementation, Safety, Entrepreneurship, Hardware, Software, or Contribution:** read `../igem-implementation-wiki/SKILL.md`.

For a whole-site plan or audit, read [references/current-judging.md](references/current-judging.md), [references/cross-page-contract.md](references/cross-page-contract.md), and [references/review-checklist.md](references/review-checklist.md). Read [references/claim-evidence-register.md](references/claim-evidence-register.md) when claims span pages or risk overgeneralization. Read [references/ai-integrity.md](references/ai-integrity.md) whenever AI materially assists submitted work. For precedent research, also read [references/corpus-index.md](references/corpus-index.md) and [references/sampling-policy.md](references/sampling-policy.md).

When the 2026 Competition is in scope, read [references/seasons/2026-judging.md](references/seasons/2026-judging.md) and verify unstable requirements live. Do not silently apply a 2026 snapshot to another season.

## Choose the mode

- **Research:** verify official awards and current judging guidance, then extract recurring decisions from several contrasting wikis.
- **Plan:** inspect the team's live files and evidence, then propose page ownership, cross-links, and priorities without editing.
- **Write:** draft evidence-bounded content using the domain skill and the site's established voice.
- **Implement:** change only the requested scope, preserve unrelated work, and verify the rendered site.
- **Audit:** attach every finding to a page, source, or browser observation and prioritize trust before polish.

## Establish the evidence map

Before substantial writing or restructuring:

1. Inspect the live wiki, repositories, notebooks, datasets, figures, protocols, Registry entries, forms, and citations. Do not assume paths or current asset versions.
2. List the project's main claims. For each claim, record its evidence, status, owner page, supporting pages, limitations, and next decision.
3. Label statements as observed, experimentally measured, computed, literature-derived, stakeholder-reported, proposed, or future work.
4. Keep one canonical owner for each detailed result. Other pages should summarize and link rather than copy divergent versions.
5. If evidence is missing, weaken the claim or mark the gap. Never invent results, iterations, stakeholder influence, validation, citations, or award eligibility.

For a reusable planning artifact, adapt [assets/templates/whole-wiki-evidence-map.md](assets/templates/whole-wiki-evidence-map.md). For a new or substantially revised page, adapt [assets/templates/page-brief.md](assets/templates/page-brief.md). For an important figure, adapt [assets/templates/figure-evidence-card.md](assets/templates/figure-evidence-card.md).

## Build a judge-readable project path

The whole wiki should support this path without forcing it into identical page layouts:

`problem → users and context → proposed system → design choices → build/test evidence → model or measurement insight → iteration → responsible implementation → reusable contribution`

The Home page orients. Description defines the problem and solution. Technical pages prove what was attempted and learned. Human Practices shows how outside perspectives changed the work. Implementation and Safety bound real-world use. Contribution and Attributions preserve what others can reuse and who did the work.

## Check cross-page consistency

- Project name, problem, intended users, biological mechanism, success criteria, and maturity level agree everywhere.
- Description promises only evidence that Results, Model, Measurement, Hardware, or Software can support.
- Engineering links each design change to a test or reason; Results links back to the relevant method and forward to the conclusion.
- Human Practices records concrete changes and unresolved tensions, not merely meetings.
- Implementation, Safety, Sustainability, and Entrepreneurship use compatible assumptions about scale, users, regulation, containment, cost, and readiness.
- Awards or medal summaries point to evidence pages and never replace them.

## Refresh unstable facts

When judging criteria, competition rules, deadlines, standard URLs, or award status matter, verify the current official iGEM Competition site. Record year, section, prize, winner versus nominee, team, and exact URL. Do not present historical patterns as current rules.

## Match the competition phase

- **Early season:** define users, success criteria, evidence ownership, attribution capture, data provenance, and selected award hypotheses before pages become urgent.
- **Mid season:** audit experiments, modeling, Human Practices integration, Registry work, software or hardware artifacts, and negative results while another iteration is still possible.
- **Pre-freeze:** verify Standard URLs, Judging Form claims, Attributions, Registry and repository links, AI disclosures, external assets, browser behavior, and current deadlines.
- **Post-Jamboree:** add awards and final amendments without rewriting the historical record or erasing limitations.

## Verify implementation

For edits, check syntax and references, then render the real pages at desktop and mobile widths. Test global navigation, local table of contents, anchors, collapsed content, figures, equations, tables, media fallbacks, and outbound evidence links. Essential meaning must remain available without hover, animation, or a particular browser.

Deliver the outcome with the evidence inventory, key gaps, prioritized changes, files changed if any, and verification performed.
