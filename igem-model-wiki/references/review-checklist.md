# Model page review checklist

Use this checklist after inspecting the team's actual sources. Mark items **present**, **partial**, **missing**, or **not applicable**, and attach evidence such as a file, section, figure, dataset, notebook, or URL. Do not award points by word count.

## Scientific purpose

- The biological question or design decision is explicit.
- The reason a model is needed is distinct from general project background.
- Inputs and outputs are named, and dependencies between model modules are accurate.
- The model's contribution to wet-lab work, design, safety, or interpretation is concrete.

## Scope and assumptions

- Assumptions, boundary conditions, and simplifications are visible.
- Prediction, proxy, annotation, hypothesis, and experimental result are not conflated.
- Applicability range and known failure modes are stated.
- Limitations are specific enough to motivate a next test or improvement.

## Mathematical and computational clarity

- Variables and symbols are defined near first use.
- Dimensional quantities have units and equations are dimensionally plausible.
- Parameters have values, provenance, and a clear relationship to implementation.
- Algorithms, solvers, initial conditions, constraints, random seeds, or software versions are documented when material.
- Intermediate steps are shown when necessary to understand the output.

## Evidence and validation

- Results include appropriate baselines, controls, or comparison conditions.
- Validation is distinguished as experimental, literature-based, numerical, structural, or internal-consistency checking.
- Sensitivity, uncertainty, robustness, missingness, and coverage are addressed where they could change interpretation.
- Negative, partial, and inconclusive outcomes are retained when informative.
- Each key conclusion can be traced to a figure, table, computation, or external source.

## Results and project loop

- Captions explain what is shown, conditions, and supported conclusion.
- Text interprets effect direction and magnitude instead of repeating axes.
- The page says what changed because of the model, or honestly states that the output remains a proposal.
- Feedback between dry lab and wet lab is documented with dates, iterations, or design changes when available.
- Future work names a discriminating experiment or technical improvement rather than a generic aspiration.

## Reproducibility

- Code and data links work and point to the relevant artifact.
- A reader can identify the command, notebook, workflow, or environment needed for key results.
- Generated figures can be mapped to source data or scripts.
- Literature references and parameter sources are complete and stable.
- Repository availability is not treated as sufficient if the execution path is unclear.

## Page experience

- A skim reader can understand the whole model from the opening overview.
- Heading hierarchy matches scientific hierarchy.
- Long pages provide a table of contents or position-aware navigation.
- Hash links, accordions, and tabs reveal the requested target reliably.
- Primary assumptions, results, and limitations are not hidden by default.
- Equations, tables, and figures remain legible on narrow screens.
- Images have useful alternative text; meaning is not color-only or hover-only.
- Decorative motion does not delay access or obscure content.

## Verification

- HTML and JavaScript pass syntax checks.
- Local assets and internal anchors resolve.
- Outbound scientific, code, and data links are sampled in a browser.
- Desktop and mobile renders are visually inspected.
- The top, at least one dense technical section, interactive navigation, and the page ending are checked.
- Final claims are re-audited against source evidence after editing.

## Priority labels

- **P0 — trust blocker:** unsupported claim, wrong equation or unit, missing primary result, broken core navigation, or inaccessible essential content.
- **P1 — judging-impact gap:** unclear purpose, missing assumptions or validation, weak project feedback, or non-reproducible key result.
- **P2 — comprehension gap:** poor hierarchy, weak caption, excessive density, mobile issue, or missing secondary provenance.
- **P3 — polish:** small consistency or presentation improvement with no effect on scientific interpretation.
