# V4 Phase 4G — Pre-specified Design Diagnostic: Different-Team Control Selection / Timing-Sequence Adjacency

**Status:** written and committed **before** any adjacency metric, adjacency-stratified D summary or block diagnostic was computed. The only thing inspected beforehand was the timestamp *structure* of the Timing71 records (resolution and ties; §3). No D values were looked at. The rules below are not changed after results are seen.

**Nature:** DIAGNOSTIC. Phase 4G does not retest the hierarchy, does not change the Phase 4F CASE D label, does not optimise a new control rule, fits no model, estimates no team effects, and ranks no teams or drivers.

## 0. Phase 4F freeze

- **Phase 4F results commit:** `81455f3` (pre-specification `fa480ed`). Working tree clean at the start of Phase 4G.
- **Phase 4F CASE:** `D` (`output/phase4f/case_evaluation.csv`). It is not relabelled, overwritten or reinterpreted.
- **SHA-256 of all 35 Phase 4F files:** `phase4f_freeze_record.csv`. These are re-verified by the Phase 4G checks.
- Phase 4G reads Phase 4F outputs and imports Phase 4F/4E pure functions read-only. It writes only to `output/phase4g/`.

## 1. Terminology (4G.1, 4G.13)

- **Neutral terms only:** TIMING-SEQUENCE ADJACENCY, ON-TRACK TEMPORAL ADJACENCY PROXY, NEAR-CONSECUTIVE TIMING OBSERVATIONS.
- **Never used for timing-adjacent cars:** "tow partner", "tow group", "traffic group", "aerodynamic group". No tow status exists in the data, and none is created.
- **Source label:** lap records are **Timing71 archived recordings of the INDYCAR live timing feed (third-party)**, never official INDYCAR lap data.

## 2. Population (4G.3)

- **PRIMARY:** exactly the Phase 4F primary population. That is:
  - the 15 Era B (2023–2024) sessions;
  - the COMPARABLE layer;
  - 5-min epoch-aligned blocks;
  - min 1 lap;
  - the Phase 4F car-block definition, canonical team mapping and performance filtering, all reused by importing `v4_phase4f_hierarchy`.
- **SECONDARY:** 2025 (Era C, `ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE`), the same pipeline as the Phase 4F secondary. It is reported in the year breakdown (4G.7) **separately**, never pooled with the primary, and never enters the case evaluation.
- **Race:** excluded.

## 3. Timing-sequence reconstruction (4G.5)

**Structural facts observed before this spec (no D inspected):**
- Timing71 lap timestamps are **feed-update times**. Distinct timestamps within a session are never closer than about 1.6 s; the modal spacing is about 1.67 s.
- Within one car, (Δtimestamp − laptime) spreads about ±1.3 s.
- In the long practice sessions, 54–78% of lap records share an identical timestamp with at least one other car's record.
- The line-crossing order **within one feed update is therefore not observed**. Order *between* updates is observed, at update resolution.

**Sequence definition (primary, OBSERVED):**
- **Record set:** every Timing71 lap record in the session, including all flags and all laps, not only comparable ones. Records are taken after the Phase 4F de-duplication, sorted by timestamp.
- **Feed-update index `u`:** the dense rank of the distinct timestamp, rounded to 1 ms.

**Lap-to-lap pairing:** for a target lap *a* and a comparator lap *c*:
- `abs_ts_sep_s` = |ts_c − ts_a|;
- `update_sep` = |u_c − u_a|;
- `intervening` = the number of **other** records (not *a*, not *c*) whose timestamp lies strictly between ts_a and ts_c;
- `order`:
  - `CONTROL_AFTER` if ts_c > ts_a;
  - `CONTROL_BEFORE` if ts_c < ts_a;
  - `SAME_UPDATE_ORDER_UNOBSERVED` if they are equal.

**Adjacency category of a lap pair (ordinal):**

| Category | Definition |
|---|---|
| `SAME_UPDATE` | update_sep = 0: same feed update; order unobserved |
| `CONSECUTIVE` | update_sep ≥ 1 and intervening = 0 |
| `BETWEEN_1_2` | 1 ≤ intervening ≤ 2 |
| `BETWEEN_3_5` | 3 ≤ intervening ≤ 5 |
| `BETWEEN_GT5` | intervening > 5 |

"No intervening observation" = SAME_UPDATE ∪ CONSECUTIVE.

**Car-block pair (target i, comparator j, as used in Phase 4F):**
- For **each** comparable lap of i in its block, take the lap of j in j's car-block that is nearest in timestamp (ties go to the earlier lap), and compute the lap-pair metrics.
- **Pair-level summaries:**
  - `median_intervening`, `median_update_sep`, `median_abs_ts_sep_s`;
  - `min_intervening` (closest approach);
  - `pair_category` = the **ordinal lower median** of the lap-pair categories across i's laps (**primary adjacency label**);
  - `share_control_after`, `share_same_update`.
- **Selection time:** `carblock_time_sep_s` = |t_i − t_j| on the Phase 4F car-block median times (the quantity nearest-time selection minimised).

**Cumulative adjacency shares** (by pair_category): ≤0 intervening (same update or consecutive), ≤1, ≤2, ≤3 and ≤5. Here "≤k" means SAME_UPDATE, or intervening ≤ k computed on the lower-median target lap.

**Sequence completeness:** per session, the share of lap records whose predecessor in the same car's stint is timestamp-incoherent (|Δts − laptime| > 2 s, the Phase 4F rule) is reported as missing-capture risk. Missing records would **understate** `intervening`.

**Derived sensitivity (labelled `DERIVED_LAPTIME_CHAIN_ESTIMATE`, not observed):**
- **Chains:** within each car and stint, a run of timestamp-coherent laps (|Δts − laptime| ≤ 2 s) forms a chain.
- **Estimated crossing time:** anchor + cumulative laptime, where anchor = min_k(ts_k − C_k) over the chain.
- The sequence metrics are recomputed on these estimated times.
- **Use:** only to ask whether conclusions depend on within-update ties. It is never presented as observed crossing order and never used in the case rule.

## 4. Reconstruction (4G.4)

The Phase 4F nearest-time selection is re-implemented, **keeping the full candidate pools**, with the same key: |t_k − t_i|, then the lower numeric car number, then lexicographic order.

**Reproduction requirement:** for every primary target, (target, teammate, control, D_st, D_dt, time separations) must equal the Phase 4F `comparison_pairs.csv` rows exactly (PRIMARY, comparable, width 5).

## 5. Populations compared (4G.6)

| Label | Definition |
|---|---|
| **A_PRIMARY_CONTROL** | the selected different-team control for each target (weight 1) |
| **B_ELIGIBLE_CANDIDATES** | every different-team car-block in the target's block (the pool A was drawn from) |
| **C1_TEAMMATE_OF_TARGET** | the target's nearest-time teammate |
| **C2_ALL_TEAMMATES** | all teammates of the target in the block |

**How B is summarised:**
- pooled over all target–candidate pairs;
- **as the random-pick expectation:** per target, the share of its pool in each category, averaged over targets. This is the expected share if the control had been drawn uniformly from the same pool;
- the selected control's **pool percentile rank**: the share of pool candidates with strictly smaller `median_intervening`, plus half of the ties.

**Reported for all four populations:** car-block time separation, lap-level |Δts|, median intervening, update separation, cumulative adjacency shares, median, IQR, and p10/p25/p75/p90.

## 6. Year and session category (4G.7)

- **Breakdowns:** A, B-expectation and C1 adjacency by year (2023, 2024 primary; 2025 secondary, separate) and by session category.
- **Descriptive link:** alongside each, the Phase 4F session-balanced primary Delta for that year/category (read from Phase 4F outputs) is shown. No correlation is interpreted causally.

## 7. D by adjacency stratum (4G.8)

- **Population:** different-team candidate pairs only (population B), PRIMARY.
- **Sequence strata** (fixed here, before any D is seen): SAME_UPDATE, CONSECUTIVE, BETWEEN_1_2, BETWEEN_3_5, BETWEEN_GT5 (on `pair_category`). Also the combined NO_INTERVENING = SAME_UPDATE ∪ CONSECUTIVE.
- **Timestamp strata:** the Phase 4F diagnostic bins on car-block time separation: ≤5 s, 5–15 s, 15–60 s, 60–300 s.
- **Per stratum:**
  - n pairs, sessions and blocks;
  - pooled median, IQR and p10/p90 of D;
  - the session-balanced median (the median within session, then across sessions);
  - by year.
- **Within-target paired diagnostic:** for targets whose pool has ≥1 NO_INTERVENING candidate and ≥1 BETWEEN_GT5 candidate, take the median D(GT5) − median D(NO_INTERVENING) per target, then the session-balanced median. This holds the block and target fixed.

## 8. Negative vs positive blocks (4G.9)

**Groups:** Phase 4F primary blocks split by `delta_block` < 0, = 0 and > 0. The groups are **not** redefined or discarded.

**Per block:**
- the median control car-block time separation;
- median lap-level |Δts|;
- median intervening;
- the share of controls with NO_INTERVENING;
- the median candidate-pool size;
- control reuse (targets ÷ unique control car-blocks);
- the median random-pick expectation of NO_INTERVENING.

**Comparison:** the group medians, plus the within-block excess adjacency (the control NO_INTERVENING share minus the pool expectation).

## 9. Control reuse (4G.10)

**Reported:**
- unique control car-blocks and cars;
- the distribution of targets per control car-block;
- the maximum;
- reuse by year and by session;
- the adjacency of high-reuse controls (reused ≥3 times) vs the rest.

Repeated controls are not treated as independent.

## 10. Design-population comparison (4G.11, 4G.12)

These are diagnostics only; nothing is promoted to primary.

| Population | Definition | Weight |
|---|---|---|
| **TEAM_BALANCED_DIFF** | every cross-team car-block pair in the same 209 eligible primary blocks | 1 / (pairs in that team pair in the block), as in Phase 4F |
| **ADJACENT_BLOCK_DIFF** (Phase 4F §8 i) | car i in block k vs its nearest-time different-team car in block k+1 | 1 |
| **REWEIGHTED_DIFF** (Phase 4F §8 ii) | the Phase 4F within-block DIFF_TEAM pairs with the Phase 4F same-car time-separation weights | as in Phase 4F |
| **A_PRIMARY_CONTROL** | as in §5 | 1 |

**Compared across populations:**
- time separation;
- sequence adjacency, using the same lap-pair rule; for ADJACENT_BLOCK, comparator laps come from block k+1;
- team representation: the number of distinct control teams and the largest single-team share. Shares are listed alphabetically, as a descriptive count, not a ranking;
- observation reuse: the maximum and median appearances of a car-block;
- block coverage.

## 11. Mechanical interpretation (primary only; §15 of the request)

**Gate G (identifiability):** `pair_category` must be defined for ≥ 90% of A_PRIMARY_CONTROL pairs **and** ≥ 90% of B candidate pairs.
- If G fails → **CASE D**.
- Same-update ties do not fail G: they are adjacency at feed-update resolution with order unobserved.

**S1 — selection adjacency:** the share of A with NO_INTERVENING, compared with the B random-pick expectation E.

| Level | Rule |
|---|---|
| SUBSTANTIAL | A − E ≥ 0.20 **and** A / E ≥ 2 |
| MATERIAL | A − E ≥ 0.05 (and not substantial) |
| NOT_MATERIAL | otherwise |

**S2 — adjacency–D association** (population B, PRIMARY). Δ_S2 = session-balanced median D(BETWEEN_GT5) − session-balanced median D(NO_INTERVENING).

| Level | Rule |
|---|---|
| CONSISTENT | Δ_S2 ≥ 0.25 mph **and** positive in 2023 and in 2024 separately **and** positive in ≥ 2/3 of primary sessions that have ≥ 3 candidate pairs in both strata **and** the within-target paired session-balanced median > 0 |
| MODEST_OR_INCONSISTENT | Δ_S2 > 0 but not CONSISTENT |
| NONE | Δ_S2 ≤ 0 |

The 0.25 mph threshold is fixed here on the scale of the Phase 4F discrepancy (primary +0.05 vs team-balanced +0.31 mph).

**Cases** (precedence D → A → C → B):

| Case | Rule |
|---|---|
| **D** | Gate G fails |
| **A** | S1 = SUBSTANTIAL **and** S2 = CONSISTENT |
| **C** | S1 = NOT_MATERIAL **or** S2 = NONE |
| **B** | Otherwise |

**Additional reporting:** the derived laptime-chain sensitivity and the 2025 secondary are reported as agreeing or disagreeing. They do not change the case.

## 12. Phase 4H decision rule (4G.16)

- **YES** only if the case is A or B, i.e. a concrete, mechanically defined control-selection property (timing-sequence adjacency) has been identified that a future rule can avoid **without reference to team-performance results**.
- **Otherwise NO.**
- If yes, only design **principles** are written. No thresholds are tuned, and Phase 4H is not run.

## 13. Forbidden

- Model fitting.
- Team-effect estimation.
- Team or driver ranking.
- A new hierarchy estimator.
- Tow claims.
- Pooling 2025 or race with the primary.
- Changing Phase 4A–4F files.
- Changing these rules after results.
- Ingesting substantial new data (4G.14 is feasibility documentation only).
