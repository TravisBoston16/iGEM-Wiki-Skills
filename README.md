# iGEM Wiki Skills

A modular Codex skill collection for researching, planning, writing, implementing, and auditing evidence-led iGEM team wikis.

Current release: **v0.2.0**

## Skills

| Skill | Scope |
|---|---|
| `igem-wiki` | Whole-wiki architecture, current-season compliance, cross-page claims, AI integrity, and task routing |
| `igem-wiki-story` | Home, Description, Awards, navigation, and project narrative |
| `igem-wetlab-wiki` | Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, and Notebook |
| `igem-model-wiki` | Modeling, equations, computational evidence, validation, and reproducibility |
| `igem-hp-wiki` | Human Practices, Education, Inclusivity, Sustainability, ethics, and stakeholder integration |
| `igem-implementation-wiki` | Implementation, Safety, Entrepreneurship, Hardware, Software, and Contribution |

## What v0.2.0 adds

- a dated iGEM 2026 judging, Standard URL, eligibility, and freeze snapshot;
- an AI use, scientific-integrity, verification, privacy, and attribution protocol;
- a Claim-Evidence Register with evidence-status and maturity vocabulary;
- seven reusable templates for whole-wiki evidence, pages, figures, DBTL, models, Human Practices, and implementation readiness;
- UI metadata for all six skills;
- repository validation and behavior-oriented evaluation scenarios.

## Research basis

The reference corpus distinguishes:

- official winner and nominee records from the [iGEM Annual Results](https://competition.igem.org/results/);
- observations from individual team wiki pages;
- reusable principles, meaningful exceptions, limitations, and accessibility risks.

Award-winning pages are precedents to analyze, not templates to copy. Historical patterns are not judging rules. Current criteria, eligibility, policies, Standard URLs, and deadlines must be refreshed from official iGEM sources when they affect a decision.

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
python3 scripts/validate_repository.py
```

The validator checks skill entrypoints, names, UI metadata, local Markdown references, required v0.2 resources, and unfinished placeholders. GitHub Actions runs the same check on pushes and pull requests. Behavioral scenarios live in `evals/scenarios.md`; they test decision invariants rather than exact wording.

## Scope and attribution

This is an independent community resource and is not affiliated with or endorsed by the iGEM Foundation. Team names and links are included for research attribution. The repository summarizes public examples without copying their branding or scientific assets. Recheck official award status before reuse.

## License and citation

Released under the MIT License. See [LICENSE](LICENSE). Citation metadata is provided in [CITATION.cff](CITATION.cff).

---

## 中文简介

这是一组模块化的 iGEM Wiki Codex skills。`igem-wiki` 负责全站证据、赛季合规与跨页面协调，其余五个 skill 分别处理项目叙事、湿实验、建模、Human Practices 和落地实施。v0.2.0 新增 AI 使用与科研诚信协议、Claim-Evidence Register、2026 评审快照和七类可复用模板。

