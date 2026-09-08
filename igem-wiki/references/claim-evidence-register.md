# Claim-Evidence Register

Use this reference for whole-wiki planning, cross-page audits, or any situation where a claim may be repeated, generalized, or overstated.

## Register schema

| Field | Meaning |
|---|---|
| Claim ID | Stable identifier such as `M3-A-01` or `WL-07` |
| Public claim | Exact bounded statement intended for the wiki |
| Owner page | Canonical page containing the full evidence |
| Supporting pages | Pages that summarize and link to the owner |
| Evidence status | Observed, measured, computed, literature-derived, stakeholder-reported, proposed, or future work |
| Maturity | Use the vocabulary below |
| Evidence location | Figure, table, dataset, notebook, code, Registry entry, transcript, or source |
| Conditions | Construct, sequence, sample, parameter range, environment, controls, and date as relevant |
| Applicability | What population, design space, or context the conclusion covers |
| Uncertainty | Statistical, numerical, structural, sampling, or qualitative uncertainty |
| Limitation | What the evidence cannot establish |
| Decision impact | What changed because of the result |
| Human owner | Team member responsible for verification |
| Last verified | Date checked against the source artifact |

## Evidence-maturity vocabulary

Use descriptive labels, not a pseudo-judging score:

- **Illustrative example:** demonstrates a workflow or visualization; not evidence of general behavior.
- **Exploratory analysis:** investigates a pattern without sufficient calibration or validation for a firm conclusion.
- **Literature-parameterized:** uses external values or behavior; applicability to team conditions remains bounded.
- **Calibrated with team data:** parameters or decisions were adjusted using team-generated data.
- **Validated within tested conditions:** an independent comparison supports performance only within stated conditions.
- **Externally validated:** independent data, users, or contexts support transfer beyond the original test, with remaining limits stated.
- **Proposed future work:** not yet built or tested.

Do not automatically move a claim upward because the page is polished, a fit has high R-squared, or a repository exists.

## Generalization check

Before changing a specific result into a broad claim, ask:

1. How many constructs, sequences, samples, users, or conditions were actually tested?
2. Were they selected as representative, convenient, or merely available?
3. Is the variation biological, technical, computational, or absent?
4. Is there an independent validation set or only the data used to fit or choose the method?
5. What is the narrowest truthful public sentence?

Example: a successful run on one 205-aa sequence is an illustrative or exploratory case unless evidence supports representativeness. State the sequence, why it was selected, what the run demonstrates, and what additional sequences are needed. Do not write that the pipeline works generally.

## Cross-page rule

The owner page carries conditions, uncertainty, and limitations. Supporting pages may shorten the claim only if the shortened version preserves its scope. If a headline cannot preserve the limitation, rewrite the headline rather than hiding the limitation behind a link.

