# V4 Phase 4D — Identifiability and Alignment Specification

**Status:** written and committed **before** any Phase 4D team context, structural category, or residual alignment was computed. These rules are not changed after results are seen. Phase 4C is untouched.

**Question:** does the historical observation structure contain enough independent, temporally local, repeated multi-car information to distinguish a shared team-level performance state from car-specific unexplained movement? No latent model is fitted.

## 0. Prior-knowledge disclosure

Earlier phases showed the following:
- Team contexts are sparse (Phase 4A/4B).
- Most repeated Era B teammate attempts are frozen-core endpoints (Phase 4B: 73 of 77).
- Common-car controls are often other frozen transitions (Phase 4A).
- 2025 ambient is collinear with session time (Phase 4C).

No Phase 4D alignment between teammate context and target residuals has been computed.

## 1. Anchors (primary)

- **Transitions:** the 41 frozen same-car transitions, i.e. rows of `r5_2/manual/r5_2_repeat_analysis_set_v1.csv` with non-missing Δspeed, Δtrack and Δair, in frozen row order.
- **Endpoint times:** from Phase 4A `frozen_transition_anchors.csv` (frozen timestamps; 3 rescued transitions use Phase 3 rescue times, labelled).
- **Frozen expected delta:** `predicted_physical_delta_mph_loyo` from `r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv`. This is the only per-transition physics expectation in the frozen manifest. The frozen backtest `predicted_median_mph` (`probabilistic_physics_historical_backtest_v1.csv`, not in the manifest) is carried as secondary context only.
- **Target residual:** `residual_loyo_raw` = observed Δspeed − frozen LOYO expected Δspeed (verified identical). It means only "movement not explained by the frozen physical expectation".
- **Carried unchanged:** all frozen quality and provenance fields (`physical_link_quality`, `analysis_source`, time classes, PTSC/HRRR pair availability, `exclusion_reason`, `in_frozen_39`).

## 2. Teammate observation pool

- **Source:** Phase 4B `team_timeline_long.csv`, Era B (2020–2024).
- **Pool:** primary teammate layer; timed complete four-lap attempts; same year and canonical team as the target; car ≠ target car.
- **Excluded:** technical-partnership entries (they are not in the primary layer). The target in a technical-partnership entry (2021 Paretta #16) gets category D.

Two observation types are built.

- **MOVE observation (primary local-movement representation, per addendum 4D.6A).**
  - **Definition:** for a teammate car with ≥2 timed complete attempts, each consecutive pair (previous → current) in that car's chronological sequence of timed complete attempts.
  - **Columns:** `previous_attempt_delta = speed_current − speed_previous`; previous-attempt time; `delta_time_min`; Δtrack; Δambient; the attempt sequence numbers.
  - **`physics_adjusted_move`** = previous_attempt_delta − (β_track·Δtrack + β_ambient·Δambient), using the **published frozen full-data coefficients**, applied only (β_track = −0.03482533, β_ambient = 0.18239338). Nothing is refitted. If Δtrack or Δambient is missing, it is NaN.
  - **`link_uncertain` = True** if the car has an *untimed* or *incomplete* attempt whose position relative to the pair cannot be excluded: either any untimed attempt of that car exists in the team-year, or a timed incomplete attempt lies strictly between the two.
- **LEVEL observation (secondary):** each teammate timed complete attempt, with `speed_minus_car_mean` and `speed_minus_car_median` (Phase 4B, whole-session, within-car) and raw speed.
- **Offsets:** every observation carries signed offsets from t1 and t2. A MOVE observation is placed on the interval [t_previous, t_current].

## 3. Evidence-independence label (exclusive; precedence top to bottom)

| Label | Rule |
|---|---|
| `RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE` | MOVE: the pair (previous → current) is itself a frozen transition, so its delta is another frozen observed delta. LEVEL: not used. |
| `FROZEN_CORE_ENDPOINT` | MOVE: either attempt is an endpoint of any frozen transition. LEVEL: the attempt is a frozen endpoint. |
| `UNKNOWN_DEPENDENCE` | Not frozen-linked, but the time class is not a recorder point (bounded or rescued), or (MOVE) `link_uncertain`. |
| `OTHER_DEPENDENT_REUSE` | Not frozen-linked and not unknown, but the observation belongs to the context (window ±30 min, §4) of ≥2 different target transitions, so those transitions' contexts are not mutually independent. |
| `INDEPENDENT_OF_FROZEN_CORE` | None of the above. |

**`frozen_independent`** = label ∈ {`INDEPENDENT_OF_FROZEN_CORE`, `OTHER_DEPENDENT_REUSE`, `UNKNOWN_DEPENDENCE`}, i.e. not part of frozen-core evidence. The reuse count is also reported for every observation.

## 4. Windows (declared; not optimised)

- **Windows:** w ∈ {15, 30, 45, 60} min, plus `INTERVAL`.
- **Context span:** [t1 − w, t2 + w]. For `INTERVAL`, it is [t1, t2].
- **In-window MOVE:** both attempts of the MOVE lie inside the context span.
- **In-window LEVEL:** the attempt lies inside the context span.
- **Near t1 / near t2:** |offset| ≤ w. For `INTERVAL`, "near" is not defined; those columns are left blank.
- **Primary window:** **±30 min**. The others are reported as sensitivity only.

## 5. Structural categories (deterministic; computed per transition × window)

Let:
- *MC* = the set of teammate cars with ≥1 in-window MOVE;
- *IMV* = the number of in-window MOVEs that are `frozen_independent`;
- **both-sides coverage** = at least one in-window MOVE whose interval intersects [t1 − w, t1 + w] and at least one whose interval intersects [t2 − w, t2 + w]. For `INTERVAL`: at least one MOVE with its previous attempt ≤ midpoint and at least one with its current attempt ≥ midpoint.

| Category | Rule |
|---|---|
| **D — NOT IDENTIFIABLE** | The target is not in the primary layer, or either target endpoint time is missing, or there is no in-window LEVEL and no in-window MOVE. |
| **A — STRONG** | \|MC\| ≥ 2 **and** IMV ≥ 1 **and** both-sides coverage. |
| **B — MODERATE** | Not A, and \|MC\| ≥ 1 **and** (\|MC\| ≥ 2 **or** IMV ≥ 1). |
| **C — WEAK** | Not A/B/D. Team context exists, but it is only LEVEL observations, or MOVEs from a single car that are all frozen-core-linked. |

Also reported per transition × window:
- the counts of eligible LEVEL and MOVE observations, unique teammate cars, and cars with repeats;
- frozen-independent counts and frozen-core-overlapping counts;
- temporal span and weather span of the in-window observations;
- whether observations lie on both sides of the target's midpoint;
- whether ≥2 cars' MOVE intervals overlap in time.

A transition is **dominated by frozen-core reuse** at a window if it has ≥1 in-window MOVE and all of its in-window MOVEs are `RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE` or `FROZEN_CORE_ENDPOINT`.

## 6. Team-context summaries (all descriptive; computed for categories A–C, every window)

| # | Summary |
|---|---|
| S1 | Median `speed_minus_car_mean` of LEVEL observations near t1 (secondary) |
| S2 | The same near t2 (secondary) |
| S3 | Median `speed_minus_car_mean` of LEVEL observations in [t1, t2] (secondary) |
| S4 | Nearest repeated-teammate change: the in-window MOVE whose interval midpoint is nearest to the target midpoint (t1 + t2)/2, both raw and physics-adjusted, with its Δt |
| S5 | Median physics-adjusted MOVE over all in-window MOVEs (attempt-weighted; the dominance share of the largest car is reported) |
| **S6 (primary)** | **Car-balanced median physics-adjusted MOVE: the median within each car, then the median across cars** |
| S7 | S5 and S6 restricted to `frozen_independent` MOVEs (reported as S5_IND and S6_IND) |
| S8 | Common-car centered change: mean over cars present near both t1 and t2 of (that car's median centered state near t2 − near t1). Only defined when ≥1 car is near both. |

- **No cross-car raw differences:** no summary subtracts raw speeds of two different cars.
- **Car dominance:** the largest single-car share of MOVEs is reported with S5.
- **Interval disclosure:** for S4–S7, the MOVE intervals (Δt) are reported alongside the target Δt.

## 7. Alignment labels (primary: S6 at ±30 min)

Per transition, with r = the target residual:
- **INSUFFICIENT_TEAM_CONTEXT:** category D or C, or S6 is undefined (no in-window MOVE with physics-adjusted value).
- For categories A/B, compute each contributing car's median physics-adjusted MOVE, m_c (cars with MOVE in window):
  - **TEAM_CONTEXT_CONSISTENT:** every m_c has the same sign as r.
  - **TARGET_CAR_ISOLATED:** every m_c has the opposite sign to r.
  - **MIXED_TEAM_CONTEXT:** the m_c signs disagree.
  - Any m_c or r exactly 0 counts as disagreement (MIXED).
  - The number of contributing cars is reported with every label. A label from a single car is flagged `single_car_label = True`.
- **Secondary labels:** the same rule on frozen-independent MOVEs only (`label_IND`); at every other window; and using S4.
- **Magnitude (no threshold):** report |r|, |S6|, S6 / r (only when |r| ≥ 0.001 mph), |S6 − r| and their empirical distributions. No "meaningful magnitude" threshold is declared in this phase.

## 8. Unrelated-team placebo (descriptive; no randomisation claim)

- **For each target transition in categories A/B at ±30:** build the same S6 from MOVE observations of **every other canonical team** in the same year and session, with both attempts in [t1 − 30, t2 + 30] (the same time window, so the environment is matched by construction).
  - Computed per other team (its own car-balanced median) and pooled across all other teams (car-balanced across all their cars).
- **Descriptive comparison (same-team vs unrelated-team):**
  - (i) the sign-agreement rate with r;
  - (ii) the median |S − r|;
  - (iii) per transition, the rank of the same-team |S6 − r| among all teams with a defined summary (1 = closest).
- **Reporting:** transitions where no other team has a defined summary are listed as not identifiable. The frozen-independent-only version is also reported.

## 9. Permutation diagnostic (within-session team-label shuffle)

- **Shuffle:** within each year separately, randomly reassign canonical team labels to cars while preserving the multiset of team sizes (the number of cars per team in the Era B timeline). All attempts, timestamps, speeds and MOVE observations stay attached to their cars.
- **Recompute:** each target's pseudo-teammate context (cars sharing the target's shuffled team label), S6 at ±30, and the alignment statistics.
- **Statistics:**
  - T1 = the fraction of defined transitions with sign(S6) = sign(r);
  - T2 = median |S6 − r|;
  - T3 = the number of transitions with a defined S6.
- **Draws:** 2000 shuffles, seed 20260928. Report where the observed values fall in the permutation distribution (a descriptive percentile). The dependence between transitions is acknowledged.
- **Not meaningful if:** fewer than 5 transitions have a defined observed S6. In that case it is reported as not meaningful and not interpreted.

## 10. Large-residual case studies

The 8 frozen transitions with the largest |r| are selected, by selection rule only, with no importance claim. Each gets a detailed context timeline. 2021 Andretti is a separate dense QA case, regardless of its residual ranks.

## 11. 2025 extension (separate; contextual only)

- **Anchors:** consecutive same-car pairs of timed complete 2025 attempts (Phase 4B timeline).
- **Target movement:** raw Δspeed. No frozen expectation is applied to the hybrid era, and Phase 4C coefficients are not used as truth.
- **Rules:** the same MOVE, LEVEL, category and label rules, with team context from 2025 teammates. Physics adjustment is **not** applied (both target and teammate use raw deltas); this is labelled.
- **Reporting:** structural counts and labels only. It is never pooled with 2020–2024.

## 12. Feasibility case (evaluated mechanically after results; precedence C → D → B → A)

| Case | Criterion |
|---|---|
| **C — NOT IDENTIFIED** | At ±30, fewer than 5 transitions are category A, **or** more than half of the transitions with any MOVE context are dominated by frozen-core reuse. |
| **D — NOT TEAM-SPECIFIC** | Not C, and the same-team sign-agreement rate does not exceed the pooled unrelated-team rate, **or** the same-team median \|S6 − r\| is not smaller than the unrelated-team median. |
| **B — PARTIALLY FEASIBLE** | Not C/D, and fewer than 10 transitions are category A, **or** the permutation percentile of T1 is < 90. |
| **A — FEASIBLE** | None of the above. |

All satisfied criteria are reported, not only the headline.

## 13. Forbidden in Phase 4D

- Any latent, state-space, Kalman, Gaussian-process, factor, HMM, dynamic mixed or spline model.
- Refitting physical coefficients.
- Changing Phase 4C.
- Pooling eras.
- Causal labels (team, driver or setup effect).
- Changing windows, rules or summaries after results.
