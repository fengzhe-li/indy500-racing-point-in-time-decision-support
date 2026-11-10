# V4 Final Scientific Synthesis: Team-Normalized / Teammate-Control Investigation

**Status:** the authoritative interpretation of V4, Phases 1–4K.
- This is a synthesis only. No new estimator, model, classifier or statistic was computed.
- Every number below is read from a frozen output (`phase4l_key_results_table.csv` lists each source file and field).

**Data provenance:**
- Lap data: Timing71 files, a third-party archived recording of the INDYCAR live timing feed.
- Official INDYCAR session-detail records: used as cross-checks and as the qualifying anchor.

## Final case sequence

| Phase | Question | Case |
|---|---|---|
| 4C | exploratory 2025 within-team panel | **B** |
| 4D | latent team state | **C** (NOT IDENTIFIED) |
| 4F | raw-practice hierarchy | **D** |
| 4G | control-selection diagnostic | **A** |
| 4H | raw-practice measurement validity | **D** |
| 4I | post-validity support | **B** |
| 4J | FINAL hierarchy | **B** |
| 4K | teammate prediction feasibility | **C** |

## Q1 — Team identity

**Question:** did sponsor-heavy entrant naming fragment real engineering-team relationships? **Yes.**
- **Normalisation:** 59 distinct official entry-list labels (2018–2025) normalise to 21 canonical engineering teams.
- **Old grouping:** it missed **85 of 313** strict teammate pairs (27%) and created no spurious pairs. It was **high precision, low recall**.
- **Documented cases:** #98 Andretti Herta → Andretti; lineage-stable IDs such as SPM → Arrow McLaren.
- **Technical partnerships** (4 registry rows) stay separate from the primary teammate layer.

This does not affect the frozen same-car V2/V3 core, which never used teammate grouping.

## Q2 — Can qualifying teammates provide an independent control layer?

**Evidence (Phases 4A–4D):**
- Endpoint matching to the 41 frozen transitions was sparse.
- Teammate-attempt reuse was substantial, and most available teammate "moves" are themselves frozen transitions seen from another car.
- Team timelines showed car × time confounding.
- In Eras A and B (the pre-2023 eras), track temperature, ambient temperature and session time were nearly collinear within team-years.
- **Phase 4C** (2025 exploratory panel, CASE B): track temperature kept a comparatively stable negative point estimate (about −0.058 mph/°C). Its car-bootstrap interval nonetheless includes 0. Ambient temperature, time and rerunning effects were not separable or not stable.
- **Phase 4D** (CASE C): latent dynamic team state was **not identified**.

**Conclusion:** team identity and team context are recoverable. Independent dynamic team-state movement is **not** recoverable from the qualifying record.

## Q3 — Does multi-session practice add observational opportunity?

**Yes, but only in 2023–2025.**

| Period | What it provides |
|---|---|
| 2023–2025 | qualitatively new lap-level timing structure (Timing71, observed lap timestamps) |
| 2018–2021 | stint-level timestamps only; **not equivalent lap-level evidence** |
| 2022 | session-level official records only |

- Practice greatly increases contemporaneous same-team opportunity.
- Raw pair counts are highly dependent; the effective replication unit is the session.
- The eight-year dataset is **not** eight years of equivalent lap-level evidence.

## Q4 — Does raw practice support the proposed hierarchy? (Phase 4F, CASE D)

**Pre-registered primary result:**
- The nearest-time different-team estimator gave Δ = 0.046 mph, positive in only 0.5 of sessions.
- **No team-control advantage was established.**

**Design sensitivity:**
- A pre-specified team-balanced construction was more favourable to same-team similarity (0.31 mph). The result was design-sensitive.
- Raw pair counts overstated the evidence; replication was at session level.

Phase 4F neither established nor refuted the final hierarchy. Its CASE D label stands.

## Q5 — Why was Phase 4F design-sensitive? (Phase 4G, CASE A)

**Finding:** nearest-time different-team controls were unusually timing-adjacent.
- Their median car-block separation was 3.35 s.
- 57.7% had no intervening lap record, against 27.7% expected from a random pick in the same pool.
- Timing adjacency was associated with lower D: +0.975 mph between the far and adjacent strata.

**Interpretation (updated by Phase 4H):**
- Adjacency reflects **local contemporaneous running context**. That may include run phase, run purpose, track position, traffic or tow, and other unobserved local state.
- Phase 4G identifies a **control-selection property, not its causal mechanism**. It is not evidence of tow, traffic or aerodynamic interaction.

## Q6 — Were raw practice laps valid performance observations? (Phase 4H, CASE D)

**A timed, valid lap is not the same as a comparable performance observation.**

**Qualifying reference:**
- Attempts are tightly structured.
- The frozen classifier, calibrated on 2023 official attempts, retained 91.7% of 2024 official qualifying laps out of year.

**Raw 2023–24 practice:**

| Class (at-speed laps) | Share |
|---|---|
| Class A | **8.1%** |
| A + B | 11.6% |
| Ambiguous | 74.6% |

- Separately, 28.2% of all practice laps fell into clearly non-comparable structures (pit, non-green, out of band).
- Phase 4F primary-control pairs were 93.3% ambiguity-affected, and only 1.4% were A–A.

**Narrow reading of CASE D:** *the raw practice population is unsuitable for a clean performance hierarchy.* It does **not** mean that practice can never support a hierarchy; Phase 4I tested that separately.

## Q7 — After validity filtering, is enough evidence left? (Phase 4I, CASE B)

**Tier 1, 2023–24:**
- 1172 class-A laps in 374 five-minute car-blocks;
- 68 cars, 12 teams, 11 sessions.

**Layers:**
- **Same team:** 46 pairs (33 distinct car pairs, 9 teams, 8 sessions).
- **Different team:** 422 candidates.
- **All three layers:** 8/11 sessions and 25 blocks.

A minority survival fraction did **not** imply insufficient absolute support. A restricted final test remained feasible.

## Q8 — The final pre-registered hierarchy (Phase 4J, CASE B; spec `28af221`)

**Population:**
- Tier 1, 2023–24, strict timing-adjacency common support.
- 53 of 92 contexts from 26 teammate pairs, 37 cars, 9 teams and 20 blocks.
- **6 evaluable independent sessions**, session-balanced.

**Layer medians:** D_same-car = 0.368, D_same-team = 1.226, D_different-team = 1.093 mph.

**C1 = D_same-team − D_same-car = +0.696 mph** (≈ +0.124 s/lap): `POSITIVE_CONSISTENT`.
- positive in 5/6 sessions;
- session-bootstrap interval [0.087, 1.721], which excludes zero;
- all leave-one-session-out and leave-one-team-out estimates positive;
- Tier 2 +0.369; 2025 replication +0.266.

**C2 (context-paired different-team − same-team) = +0.199 mph: `INCONSISTENT`. Not robust.**
- positive in only 4/6 sessions;
- interval [-0.528, 0.528];
- removing ED_CARPENTER_RACING flips the sign;
- Tier 2 -0.094;
- difference of overall layer medians -0.134;
- the 2025 value 0.743 is highly uncertain ([-0.90, 3.07]).

**C3 = D_different-team − D_same-car = +0.702 mph.**

**Authoritative conclusion:** the full hierarchy *same car < same team < different team* was **not established**.
- Exact-car identity gave a robust reduction in observed performance dispersion relative to same-team different-car comparisons.
- Shared team identity alone showed **no stable additional reduction** relative to different-team comparisons.
- *The V4 evidence supports the methodological value of exact-car control, but does not establish a complete same-car < same-team < different-team performance-control hierarchy.*

**What this does not mean:** that teammates have no value, that team identity is irrelevant, or that same-team cars are physically unrelated.

## Q9 — Can teammate movement provide predictive information? (Phase 4K, CASE C)

This is a distinct question from Q8.

**Primary class-A 2023–24 attrition:**

| Level | Requirement | Events |
|---|---|---|
| F0 | target event | 113 |
| F1 | + physical readings | 113 |
| F2 | + prior teammate observation | 71 |
| F3 | + prior teammate movement | 44 |
| F4 | + comparable different-team placebo | 22 |
| F5 | + no leakage | **8** |

- **F5 coverage:** 8 target cars, 6 teams, 5 sessions, both years.
- **Dependence:** no duplicate future outcomes (0), and teammate-movement reuse at F5 is at most 1. Reuse is not the binding problem; **scarcity is**.
- **Forecast vintages:** 0 events.
- **Measured environmental change:** only 45/113 events at the 15-min archive resolution.
- **Prediction at t0 completion:** F5 = 0, because the retrospective class-A label cannot yet be confirmed.
- **Tier 2** would give 36 F5 events over 8 sessions, but it was pre-specified as secondary and cannot rescue Tier 1.
- **2025** gives 3 F5 events.

**Authoritative conclusion:** the historical record does **not** establish that teammate movement lacks predictive value. *The incremental predictive value of teammate movement is not prospectively identifiable from the current retrospective historical record under the strict Class-A measurement-validity definition.*

**Why:**
- performance-state labels are retrospective;
- leakage-free high-confidence events are sparse;
- archived environment is coarse relative to the horizon;
- no practice forecast vintages exist;
- the surviving events are structurally restricted (mostly cross-stint, long baselines).

## The central methodological result

The original frozen design used same-car formal qualifying repeats. V4 progressively relaxed those controls, and each relaxation exposed another confounding layer:
1. team-identity fragmentation;
2. different-car baseline, setup and driver heterogeneity;
3. car × session-time confounding;
4. environment/time collinearity;
5. dependence and teammate reuse;
6. timing-sequence / local contemporaneous-context selection;
7. heterogeneous practice run states;
8. retrospective performance-state identifiability;
9. insufficient prospective teammate-prediction support.

**The restrictive same-car qualifying-repeat design was not merely conservative.** Relaxing its controls progressively exposed additional sources of performance heterogeneity, measurement ambiguity and prospective non-identifiability.

V4 does **not** mathematically prove that the frozen V2 coefficients are correct.

## What V4 does not change

V4 is an **additive methodological and evidence extension**. It does **not** modify:
- the FINAL_V2 frozen coefficients (β_track −0.03482533, β_ambient +0.18239338);
- the 41-transition same-car core;
- the V2 uncertainty calibration;
- the V3 point-in-time architecture;
- historical evidence labels or the Phase 3 PIT conclusions;
- production inference, scenario-mode inference or the operational curve;
- any frozen manifest.

## What remains unknown

- Whether shared team identity reduces dispersion beyond different-team comparisons, under better run-state information.
- Whether teammate movement carries prospective predictive information.
- Mechanisms of local contemporaneous context (tow, traffic, run purpose).
- Practice-specific physical coefficients.
- Latent team-state dynamics.

See `phase4l_claims_matrix.csv`, `phase4l_evidence_chain.md`, `phase4l_paper_integration_map.md`, `phase4l_future_data_requirements.md` and `phase4l_limitations.md`.
