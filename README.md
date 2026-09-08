# iGEM Wiki Skills

A modular Codex skill collection for researching, planning, writing, implementing, and auditing evidence-led iGEM team wikis.

Current release: **v0.4.0**

## Skills

| Skill | Scope |
|---|---|
| `igem-wiki` | Whole-wiki architecture, current-season compliance, cross-page claims, AI integrity, and task routing |
| `igem-wiki-story` | Home, Description, Awards, navigation, and project narrative |
| `igem-wetlab-wiki` | Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, and Notebook |
| `igem-model-wiki` | Modeling, equations, computational evidence, validation, and reproducibility |
| `igem-hp-wiki` | Human Practices, Education, Inclusivity, Sustainability, ethics, and stakeholder integration |
| `igem-implementation-wiki` | Implementation, Safety, Entrepreneurship, Hardware, Software, and Contribution |

## What v0.4.0 adds

- a machine-readable benchmark corpus with **611 official award records** and **62 domain-scoped page-review records**;
- complete 2022–2024 official Results coverage for the selected Wet Lab, Human Practices, and Implementation award families;
- 18 newly inspected winner and nominee pages across three years, three competition classes, and six page functions;
- a reproducible annual-results importer plus an official API source manifest with retrieval dates and response hashes;
- a strict separation between official award facts and independent page observations;
- generated award/page indexes for Story, Wet Lab, Model, Human Practices, and Implementation;
- a dependency-free corpus generator with stale-output checks in local validation and GitHub Actions;
- schema and maintenance rules for expanding the research base without turning winners into unquestioned templates.

The v0.2 evidence templates, 2026 judging snapshot, AI-integrity protocol, and Claim-Evidence Register remain included.

## Research basis

The reference corpus distinguishes:

- official winner and nominee records from the [iGEM Annual Results](https://competition.igem.org/results/);
- observations from individual team wiki pages;
- reusable principles, meaningful exceptions, limitations, and accessibility risks.

Award-winning pages are precedents to analyze, not templates to copy. Historical patterns are not judging rules. Current criteria, eligibility, policies, Standard URLs, and deadlines must be refreshed from official iGEM sources when they affect a decision.

Machine-readable sources live in `corpus/award_records.csv`, `corpus/page_reviews.csv`, and `corpus/source_manifest.csv`. Use `scripts/import_annual_results.py` for reproducible annual imports, then run `python3 scripts/build_corpus.py`. The generated per-domain indexes are committed so a skill can use them without running code.

## Installation

### Project-local

Copy all six directories into the project's `.agents/skills/` directory:

```bash
mkdir -p .agents/skills
cp -R /path/to/igem-wiki-skills/igem-* .agents/skills/
```

Install the full collection when using `igem-wiki`, because the coordinator routes specialized work to its five sibling skills. A single domain skill can be installed alone when only that domain is needed.

### Personal

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R /path/to/igem-wiki-skills/igem-* "$CODEX_HOME/skills/"
```

Restart or reload Codex if the new skills are not discovered immediately.

## Usage examples

```text
Use $igem-wiki to build a Claim-Evidence Register and audit our full wiki against current judging requirements.

Use $igem-model-wiki to review whether a single-sequence demonstration has been generalized beyond its evidence.

Use $igem-hp-wiki to turn our engagement records into an evidence-backed integration log.

Use $igem-wetlab-wiki to review whether our Results figures support their claims and document a complete DBTL cycle.
```

## Templates

- `igem-wiki/assets/templates/whole-wiki-evidence-map.md`
- `igem-wiki/assets/templates/page-brief.md`
- `igem-wiki/assets/templates/figure-evidence-card.md`
- `igem-wetlab-wiki/assets/templates/dbtl-cycle.md`
- `igem-model-wiki/assets/templates/model-card.md`
- `igem-hp-wiki/assets/templates/integration-log.md`
- `igem-implementation-wiki/assets/templates/readiness-matrix.md`

## Validation

Run the dependency-free repository validator:

```bash
python3 scripts/build_corpus.py --check
python3 scripts/validate_repository.py
```

The checks validate corpus schema, duplicate records, generated-index freshness, skill entrypoints, names, UI metadata, local Markdown references, required resources, and unfinished placeholders. GitHub Actions runs both checks on pushes and pull requests. Behavioral scenarios live in `evals/scenarios.md`; they test decision invariants rather than exact wording.

## Scope and attribution

This is an independent community resource and is not affiliated with or endorsed by the iGEM Foundation. Team names and links are included for research attribution. The repository summarizes public examples without copying their branding or scientific assets. Recheck official award status before reuse.

## License and citation

Released under the MIT License. See [LICENSE](LICENSE). Citation metadata is provided in [CITATION.cff](CITATION.cff).

---

## 中文简介

这是一组模块化的 iGEM Wiki Codex skills。`igem-wiki` 负责全站证据、赛季合规与跨页面协调，其余五个 skill 分别处理项目叙事、湿实验、建模、Human Practices 和落地实施。v0.4.0 收录 611 条官方奖项记录与 62 条按领域记录的页面审阅，并为 2022–2024 年湿实验、Human Practices 和落地实施奖项建立可复现的官方 API 导入与来源哈希，避免把“获奖”误当成“页面每一点都值得照搬”。
