# V4 Phase 4D — Evidence-Independence Report

Labels follow spec §3: exclusive, with precedence RECIPROCAL → FROZEN_ENDPOINT → UNKNOWN → OTHER_REUSE → INDEPENDENT.

| obs_type | independence_label | observations |
|---|---|---|
| LEVEL | FROZEN_CORE_ENDPOINT | 73 |
| LEVEL | INDEPENDENT_OF_FROZEN_CORE | 43 |
| LEVEL | OTHER_DEPENDENT_REUSE | 10 |
| LEVEL | UNKNOWN_DEPENDENCE | 9 |
| MOVE | INDEPENDENT_OF_FROZEN_CORE | 1 |
| MOVE | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | 40 |
| MOVE | UNKNOWN_DEPENDENCE | 1 |

**Reuse:** the number of frozen transitions whose session context contains the observation.

| obs_type | max_contexts | median_contexts | used_in_2plus |
|---|---|---|---|
| LEVEL | 5 | 1 | 34 |
| MOVE | 4 | 1 | 12 |

## Findings

- **LEVEL observations:** 73 of 135 teammate attempts are frozen-core endpoints. The frozen-independent ones are mostly single attempts of cars that ran once, so they carry no within-car movement.
- **MOVE observations** (the primary local-movement representation): **40 of 42 are themselves frozen transitions.** Using them as "team context" for another frozen transition would count the frozen core twice. Reciprocity is common: when two teammates both have frozen transitions in a team-year, each serves as the other's context.
- **Link uncertainty:** `UNKNOWN_DEPENDENCE` MOVEs are flagged where a car has untimed attempts, or timed incomplete attempts inside the pair, so the "immediately previous attempt" cannot be confirmed.
- **Conclusion:** there is no body of independent, repeated teammate evidence in 2020–2024 from which to separate a team-level state.
