# Model winner and nominee corpus

Award status was verified from <https://competition.igem.org/results/> on 2026-09-08. Use `benchmark-patterns.md` for cross-year principles and this file for curated interpretation. The canonical record-level inventory is generated from CSV at [generated/award-index.md](generated/award-index.md); use it for counts and award lookup.

## Award pool

### 2025

- Undergrad winner Peking; nominees IZJU-China, NJU-China, PekingHSC, and SUSTech-BIO.
- Overgrad winner Heidelberg; nominees DTU-Denmark, HPI-Potsdam, Munich, TAU-Israel, and Toronto.
- High School winner GreatBay-SCIE; nominees AIS-China, GEMS-Taiwan, HK-Joint-School, and Lambert-GA.

### 2021

- Undergrad winner Ecuador; nominees FCB-UANL, NUS-Singapore, ShanghaiTech-China, Toulouse-INSA-UPS, Vilnius-Lithuania, Warwick, and XMU-China.
- Overgrad winner HZAU-China; nominees Aachen, BOKU-Vienna, DTU-Denmark, Groningen, Humboldt-Berlin, TU-Eindhoven, and Uppsala.
- High School winner TAS-Taipei; nominees Lambert-GA, LINKS-China, Mingdao, SHSBNU-China, and SMS-Shenzhen.

Selected intervening winners are TU-Eindhoven 2022, ZJU-China 2023, and Heidelberg 2024. Together the seed contains more than forty category records and deliberately includes nominees and all classes.

## Deep-read additions

| Team/page | Award relationship | Reusable observation | Caution |
|---|---|---|---|
| <https://2025.igem.wiki/peking/model/> | Best Model winner, UG | Large multi-model page repeats assumptions, methods, sources, parameters, and results in a recognizable hierarchy | One subsection uses simulated demonstration data; label examples as examples and do not imply validation |
| <https://2025.igem.wiki/heidelberg/model> | Best Model winner, OG | Purpose-led modules link optimization to experimental work and expose technical detail | Dense pipelines need a compact dependency map |
| <https://2025.igem.wiki/munich/model> | Best Model nominee, OG | Design goals, methods, results, discussion, code links, and wet-lab consequences are separated clearly | A repository link is not a complete reproduction path |
| <https://2025.igem.wiki/sustech-bio/model> | Best Model nominee, UG | Experimental response-surface data, predictive models, environmental variables, and kill-switch strategy form a decision loop | Strong accuracy claims require dataset split, metric definition, and uncertainty |
| <https://2025.igem.wiki/gems-taiwan/model> | Best Model nominee, HS | Combines rational design, a learned method, kinetics, literature review, and wet-lab candidate comparison | Distinguish computational screening from biochemical confirmation |
| <https://2025.igem.wiki/lambert-ga/model/> | Best Model nominee, HS | Opens with model purposes, data sources, assumptions, distinct outputs, and judging questions; ODE and geospatial models are linked to decisions | Long-range forecasts need explicit generalization and stability limits |
| <https://2024.igem.wiki/heidelberg/model> | Best Model winner, UG | Three-scale pipeline exposes inputs, outputs, calibration, HPC details, and concrete computational limits | Unprocessed data volume is a limitation, not validation |
| <https://2022.igem.wiki/tu-eindhoven/model> | Best Model winner, UG | Literature and experimental validation, parameter units and sources, global sensitivity analysis, and wet-lab repeats are integrated | Make fitted and independently validated parameters distinct |
| <https://2021.igem.org/Team:NUS_Singapore/Model> | Best Model nominee and Best Wiki winner, UG | Sensitivity analysis triggered a three-repeat experiment and documented improvement; calibration limits remain visible | Do not generalize beyond tested conditions |
| <https://2021.igem.org/Team:TAS_Taipei/Model> | Best Model winner and Best Wiki winner, HS | Each model connects to experiment, prototype, or application and openly records an unresolved Q10 issue | Unsupported environmental extrapolation should stay future work |

## Expansion rule

For each new model example, record model purpose, data origin, parameter provenance, assumptions, validation type, sensitivity or uncertainty, wet-lab or design consequence, reproduction path, and a limitation. Add nominees that contradict any emerging winner-only pattern.
