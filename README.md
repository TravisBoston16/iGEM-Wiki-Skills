# iGEM Wiki Skills

A modular set of Codex skills for researching, planning, writing, implementing, and auditing iGEM team wikis.

The collection is organized as one coordinator plus five domain skills:

| Skill | Scope |
|---|---|
| `igem-wiki` | Whole-wiki architecture, cross-page consistency, judging readiness, and task routing |
| `igem-wiki-story` | Home, Description, Awards, navigation, and project narrative |
| `igem-wetlab-wiki` | Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, and Notebook |
| `igem-model-wiki` | Modeling, equations, computational evidence, validation, and reproducibility |
| `igem-hp-wiki` | Human Practices, Education, Inclusivity, Sustainability, ethics, and stakeholder integration |
| `igem-implementation-wiki` | Implementation, Safety, Entrepreneurship, Hardware, Software, and Contribution |

## Research basis

The reference corpus distinguishes:

- official winner and nominee records from the [iGEM Annual Results](https://competition.igem.org/results/);
- observations from individual team wiki pages;
- reusable principles, exceptions, limitations, and accessibility risks.

Award-winning pages are treated as precedents to analyze, not templates to copy. Historical patterns are not presented as current judging rules. Current competition criteria should be refreshed from the official iGEM judging pages whenever they affect a decision.

## Installation

### Project-local installation

Copy all six directories into the project's `.agents/skills/` directory:

```bash
mkdir -p .agents/skills
cp -R /path/to/igem-wiki-skills/igem-* .agents/skills/
```

Install the full collection when using `igem-wiki`, because the coordinator routes specialized work to its five sibling skills. A single domain skill can be installed alone when only that domain is needed.

### Personal installation

To make the skills available across projects, copy the desired directories into your personal Codex skills directory instead:

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R /path/to/igem-wiki-skills/igem-* "$CODEX_HOME/skills/"
```

Restart or reload Codex after installation if the new skills are not discovered immediately.

## Usage examples

```text
Use $igem-wiki to audit the whole site for cross-page contradictions.

Use $igem-model-wiki to review our Model page without editing files.

Use $igem-hp-wiki to turn our interview notes into an evidence-backed integration map.

Use $igem-wetlab-wiki to review whether our Results figures support their claims.
```

## Repository structure

Each skill uses `SKILL.md` as its entry point. Larger benchmark corpora and checklists live under `references/` so that instructions can be loaded progressively.

## Scope and attribution

This is an independent community resource and is not affiliated with or endorsed by the iGEM Foundation. Team names and links are included for research attribution. No award status should be reused without checking the live official Results page.

## License

Released under the MIT License. See [LICENSE](LICENSE).

---

## 中文简介

这是一组模块化的 iGEM Wiki Codex skills。`igem-wiki` 负责全站协调，其余五个 skill 分别处理项目叙事、湿实验、建模、Human Practices 和落地实施。样本库会区分官方获奖/提名记录与对队伍页面的观察，避免把获奖 Wiki 的视觉风格误当成评审规则。

