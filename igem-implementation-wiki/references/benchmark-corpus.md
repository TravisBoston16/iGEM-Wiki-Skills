# Implementation benchmark corpus

Award status was verified from <https://competition.igem.org/results/> on 2026-09-08. The corpus combines Hardware, Software, Safety and Security, and Entrepreneurship award pools.

## Award pools

Representative 2025 records:

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

## Extracted principles

- Start with a user task and measurable requirements, not the artifact's novelty.
- Report achieved performance next to target performance and remaining failure modes.
- Reuse requires source files, dependencies, license, instructions, example inputs and outputs, and known limitations.
- Safety should cover laboratory hazards, deployment hazards, misuse, governance, and residual risk.
- Entrepreneurship is strongest when customer evidence, regulation, manufacturing, reimbursement, cost, and milestones agree with technical readiness.
