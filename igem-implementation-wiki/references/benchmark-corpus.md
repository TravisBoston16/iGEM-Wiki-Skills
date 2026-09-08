# Implementation benchmark corpus

Award status was verified from <https://competition.igem.org/results/> on 2026-09-08. The corpus combines Hardware, Software, Safety and Security, and Entrepreneurship award pools. The canonical record-level inventory is generated from CSV at [generated/award-index.md](generated/award-index.md); use it for counts and award lookup.

## Award pools

The official inventory includes every recorded winner and nominee in the selected Implementation-related award families for 2021–2025. Representative 2025 records are:

- Hardware winners Cornell, TUDarmstadt, and SHSID; nominees include BIT-China, Estonia-TUBI, NUDT-CHINA, Rochester, Brno Czech Republic, ETH-Zurich, GEC-Guangzhou, HongKong-JSS, SHSBNU-China, and UCS-A.
- Software winners BIT-China, EPFL, Marburg, Munich, and Lambert-GA; nominees include Barcelona-UB, Duke, UBC-Vancouver, TU-Dresden, and HK-Joint-School.
- Safety winners include UCalgary, GU-Frankfurt, HPI-Potsdam, and Uprize-I.
- Entrepreneurship winners include SUSTech-BIO, UNILausanne, WageningenUR, and SUIS-PINGHE; nominees span all three classes.

The 2021 Hardware pool is:

- Undergrad winner UPenn; nominees Ecuador, NUS-Singapore, Rochester, ShanghaiTech-China, Vilnius-Lithuania, and ZJU-China.
- Overgrad winner Aachen; nominees Concordia-Montreal, NCKU-Tainan, Paris-Bettencourt, and UNILausanne.
- High School winner SJTang; nominees Lambert-GA, LINKS-China, SHSBNU-China, and TAS-Taipei.

The 2021 Software pool is:

- Undergrad winner ZJU-China; nominees CSMU-Taiwan, CSU-CHINA, Kyoto, Tec-Monterrey, and Vilnius-Lithuania.
- Overgrad winner Marburg; nominees Aachen, Heidelberg, and TU-Darmstadt.

## Deep-read findings

| Team/page | Award relationship | Reusable observation | Caution |
|---|---|---|---|
| <https://2025.igem.wiki/cornell/hardware> | Best Hardware winner, UG | Starts from user need; documents modular variants, dimensions, specifications, energy, costed BOM, operation, and future work | Repeated explanatory text can hide the decisive test results |
| <https://2025.igem.wiki/rochester/hardware> | Best Hardware nominee, UG | Functional extruder connects mechanical, thermal, and control subsystems; reports tested feedstocks and observed diameter inconsistency | Separate demonstrated inputs from proposed microgravity use |
| <https://2025.igem.wiki/bit-china/software> | Best Software winner, UG | Architecture, installation, data pipeline, usage, commands, and visual outputs support reuse | A polished interface still needs tests and explicit limitations |
| <https://2025.igem.wiki/ubc-vancouver/software/> | Best Software nominee, UG | Core page exposes libraries, analysis roles, repository, input/output data, and joint commit history | Overview links should lead to complete per-tool run instructions |
| <https://2025.igem.wiki/hpi-potsdam/safety-and-security> | Best Safety winner, OG; Model nominee | Embeds safety information at the point of design, releases screening data, records ethics review, and admits that intentional misuse is not detected | Approval does not eliminate residual dual-use risk |
| <https://2025.igem.wiki/ucalgary/safety-and-security> | Best Safety winner, UG | Bowtie analysis links hazards, preventive barriers, consequence controls, weaknesses, and implementation timing; reusable tool is provided | Risk diagrams need evidence that controls were tested where possible |
| <https://2025.igem.wiki/sustech-bio/entrepreneurship> | Best Entrepreneurship winner, UG | Covers unmet need, market, commercialization, MVP, finances, and risk as one path | Large market or impact claims require source and boundary checks |
| <https://2025.igem.wiki/aalto-helsinki/sustainability> | Sustainability winner, OG | Demonstrates how implementation boundaries affect environmental claims | Do not substitute SDG labels for lifecycle reasoning |
| <https://2025.igem.wiki/shsid/hardware> | Best Hardware winner, HS | Three design versions, expert feedback, modular subsystems, software control, and component tests expose the design path | Overlapping sensor ranges and module-level tests leave real-wastewater full-cycle reliability and biosafety open |
| <https://2021.igem.org/Team:UPenn/Hardware> | Best Hardware winner, UG | A 96-well device includes source files, assembly time, costed materials, calibration, and biological tests | Some calibration remains unimplemented and broad robustness claims need repeated independent evidence |
| <https://2021.igem.org/Team:Rochester/Hardware> | Best Hardware nominee, UG | Manufacturing attempts, stakeholder advice, COMSOL, and measured flow are tied to design changes | Duplicated passages and inconsistent flow units weaken specification auditability |

## 2022–2024 additions

| Team/page | Award relationship | Reusable observation | Caution |
|---|---|---|---|
| <https://2024.igem.wiki/ubc-vancouver/hardware/> | Best Hardware winner, UG | Three hardware systems are linked to sustainability, stakeholder, and DBTL goals | The overview delegates decisive specifications and tests to subpages, so evidence routes must be precise |
| <https://2024.igem.wiki/munich/software/> | Best Software Tool nominee, OG | Local deployment, architecture, data handling, model choices, evaluation, source code, and contribution routes are documented | The proof of concept uses only 2019 wikis and a small LLM-judged evaluation set |
| <https://2023.igem.wiki/fudan/software/> | Best Software Tool winner, UG | Public source, online and offline documentation, web and API access, Docker, interoperability, and wet-lab validation support reuse | Multiple tools make each reproduction path dense and dataset or validation boundaries need local visibility |
| <https://2023.igem.wiki/rochester/hardware> | Best Hardware nominee, UG | A sub-450-dollar bioprinter is documented through DBTL, firmware, materials tests, and model-hardware integration | Field reliability, representative-user testing, and some material assumptions remain open |
| <https://2022.igem.wiki/insa-lyon1/hardware> | Best Hardware winner, UG | User requirements lead to a tested 386.78-euro imaging chamber with plans, materials, and unfinished requirements visible | Professional-standard performance claims need quantitative benchmarks |
| <https://2022.igem.wiki/mit-mahe/software> | Best Software Tool nominee, OG | The page explains alanine scanning, a delta-delta-G threshold, combinatorial generation, sampling, and FASTA output | Installation, tests, examples, and the reproducible runtime are not sufficiently visible on the inspected page |

## Extracted principles

- Start with a user task and measurable requirements, not the artifact's novelty.
- Report achieved performance next to target performance and remaining failure modes.
- Reuse requires source files, dependencies, license, instructions, example inputs and outputs, and known limitations.
- Safety should cover laboratory hazards, deployment hazards, misuse, governance, and residual risk.
- Entrepreneurship is strongest when customer evidence, regulation, manufacturing, reimbursement, cost, and milestones agree with technical readiness.
