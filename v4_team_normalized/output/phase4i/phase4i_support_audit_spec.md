# V4 Phase 4I — Pre-specified Post-Validity Eligibility / Support Audit

**Status:** written and committed **before** any support count was computed. The only checks run beforehand verified inputs:
- the git state, the Phase 4F/4G/4H case labels and the Phase 4H thresholds;
- the FINAL_V2/V3 hashes;
- the Phase 4E era/resolution labels.

The rules below are not changed after counts are seen.

**Question:** after the frozen Phase 4H measurement-validity filter, is there enough overlapping, independent and appropriately structured evidence to support a *future* comparison of the three layers (same car; same engineering team, different car; different engineering team)?

**Not in this phase:**
- no D (speed difference between observations) is computed for any same-team or different-team pair;
- no hierarchy direction or hierarchy estimator;
- no control selection;
- no model;
- no ranking.

The only speed dispersions computed are the pre-declared **measurement-scale references** in §9: qualifying and same-car only.

## 0. Freeze

| Item | Value |
|---|---|
| Branch / commit at start | `v4-team-normalized-evidence` @ `fd266ea` |
| Phase 4F | CASE **D** |
| Phase 4G | CASE **A** |
| Phase 4H | CASE **D** |

**Phase 4H thresholds** (unchanged):
- T_steady_95 = 0.0094017, T_steady_100 = 0.0133492;
- T_level_95 = 0.0016735, T_level_100 = 0.0019879.

**Other verification at the start:**
- SHA-256 of all 389 Phase 4A–4H output files: `phase4i_freeze_record.csv`;
- FINAL_V2/V3 hashes exact;
- nothing outside V4 changed (the paper is unchanged).

All new work is written only under `output/phase4i/`.

## 1. Inputs (frozen)

- **Eligible laps** come from `output/phase4h/practice_lap_inventory.csv`, class column `cls`, used **exactly**. The checks re-derive the classes by re-running the Phase 4H classifier with the frozen thresholds and require identity.
- **Classes** are never loosened, redefined or converted, and no new mph cutoff or performance rule is introduced.
- **Session population:** the Phase 4H practice population.
  - **Primary:** 2023–2024 practice-type Tier A/B sessions.
  - **Secondary:** 2025 (Era C), reported separately and never pooled.
  - Race and qualifying sessions are excluded.
- **Identity:**
  - car_id = year|car (leading zeros kept);
  - canonical team from the V4 registry, joined by Phase 4F (`join_status == MATCHED` required);
  - same-team requires `primary_layer == True` and not `technical_partnership_only` (technical partnerships and affiliation-only are excluded).

## 2. Evidence tiers (separate; never mixed)

| Tier | Eligible laps | Eligible pair |
|---|---|---|
| **Tier 1 — STRICT** | class A only | A ↔ A |
| **Tier 2 — EXTENDED** | class A or B | (A or B) ↔ (A or B) |

Classes C, D and E are not eligible for either tier. Exclusion means "does not meet the frozen measurement-validity requirement", not "bad lap".

**Observation unit:** the eligible **car-block** = (session, Phase 4F 5-min epoch-aligned block ⌊ts/300⌋, car_id), built separately per tier from that tier's eligible laps only.
- **Car-block time** = the median timestamp of its eligible laps.
- **Stint** = the stint of its earliest eligible lap (the (source_id, stint) key); car-blocks with eligible laps in >1 stint are flagged.
- **Tier 2 composition label:** `A_ONLY` / `B_ONLY` / `MIXED_AB`.

Lap-level counts are also reported.

## 3. Comparison layers (per tier)

All pairs are unordered pairs of distinct eligible car-blocks. **No D is computed.**

**SAME_CAR** (same car_id):
- `WITHIN_CARBLOCK_LAP_REPEAT`: a car-block with ≥2 eligible laps (the count of such car-blocks and of their lap pairs);
- `SAME_CAR_LOCAL_REPEAT`: the same session and the same stint, different car-blocks;
- `SAME_CAR_CROSS_RUN`: the same session, different stints;
- `SAME_CAR_CROSS_SESSION`: different sessions of the same year, split into the same vs different session category;
- the four are reported separately and never pooled.

**SAME_TEAM:** the same session and the same 5-min block, different car_id, the same canonical team, with both cars in the primary teammate layer.

**DIFF_TEAM:** the same session and the same 5-min block, different canonical team labels. This is **the candidate universe only; no comparator is selected** (no nearest-time rule).

**Block-scale "same-car support" at block b** (for common support): ≥1 car with an eligible car-block at b that either has ≥2 eligible laps, or has an eligible car-block of the same car at b+1 in the same session and stint (the Phase 4F SAME_CAR structure).

## 4. Descriptors per pair (no outcome)

- time separation (s) between car-block times;
- for same-car pairs: same/different stint, stint separation (number of stints apart), session and category difference;
- for within-block pairs:
  - the **Phase 4G timing-sequence category**, computed with the Phase 4G functions (`Seq`, `pair_metrics`) over **all** Timing71 lap records of the session, using the pair's eligible laps (target = the lexicographically smaller car_id);
  - categories: SAME_UPDATE (tied / order unobserved), CONSECUTIVE, BETWEEN_1_2, BETWEEN_3_5, BETWEEN_GT5. No new adjacency threshold is defined;
- PTSC weather availability: the number of Phase 4E PTSC readings in [block start − 15 min, block end] (availability only; no coefficients);
- reuse: the number of pairs each car-block participates in.

## 5. Common support (4I.5)

Reported at these scales: year, session, category, team-year, car, car-session, 5-min block, and session-scale.

**Session with all three layers (block scale):**
- ≥1 block with a SAME_TEAM pair;
- ≥1 block with a DIFF_TEAM pair;
- ≥1 block with same-car support.

**Session-scale variant:** ≥1 SAME_CAR (any subtype), ≥1 SAME_TEAM and ≥1 DIFF_TEAM pair anywhere in the session.

**Blocks** are counted with ST∧DT, SC∧ST, and all three.

## 6. Adjacency-balance feasibility (4I.9)

- Each SAME_TEAM pair is considered in both orientations (i target, j teammate), with the category c(i, j).
- **Feasible** means ≥1 DIFF_TEAM eligible candidate k in the same block with c(i, k) = c(i, j), exactly the same Phase 4G stratum.
- Reported: the shares with ≥1 and ≥3 such candidates, overall and by stratum.
- No matching algorithm is chosen.

## 7. Tier 2 composition (4I.10)

Pairs are classified by the two car-blocks' composition labels:
- **unordered:** A_ONLY–A_ONLY, A_ONLY–B_ONLY, B_ONLY–B_ONLY, and pairs involving MIXED_AB;
- **ordered:** A–B vs B–A, where the orientation is time order for same-car pairs and target = the smaller car_id otherwise.

## 8. Dependence (4I.11)

Reported per tier and layer:
- raw pairs;
- unique laps, car-blocks, cars, car-pairs, teams, team-years, sessions (the independent clusters);
- maximum and median car-block reuse;
- the fraction of pairs involving a car-block used in ≥2 pairs.

**Graph** (nodes = car-blocks, edges = within-block ST+DT pairs):
- the degree distribution;
- the share of edges touching the top 5% highest-degree nodes;
- connected components (union-find);
- the largest-component share.

No "effective N" formula is used.

## 9. Era coverage (4I.12) and measurement scale (4I.13; descriptive)

**Periods reported separately:**

| Period | Source and resolution | Classifier |
|---|---|---|
| 2018–2021 | Timing71 legacy, stint-level timestamps, Tier D | not applied |
| 2022 | official session-level records only | not applied |
| 2023 | lap-level Timing71 | applied |
| 2024 | lap-level Timing71 | applied |
| 2025 | lap-level Timing71; secondary | applied |

The Phase 4H classifier is calibrated on 2023 official qualifying and applied only to 2023–2025. It is **not projected backwards**.

**Scale references:**
- **Qualifying:** within-attempt SD and range (Phase 4H `OFFICIAL_ANCHORED`), in mph and %.
- **Same car, class A:** within-car-block SD and range of eligible A laps, and |Δ| between consecutive eligible A laps in the same stint.
- **Same car, across sessions:** the SD of the per-car median eligible-A speed across same-year sessions (same car only).
- **Precision:** lap-time precision (1e-4 s) as mph at 225 mph, and the feed-update timestamp resolution.
- **Lap-time equivalent** at 225 mph: Δt ≈ 40 s × Δv/v.

**Not done:** no power calculation; no minimum meaningful difference imposed.

## 10. Support gate (4I.14; mechanical; 2023–2024 primary, per tier)

**Metrics:**

| Metric | Definition |
|---|---|
| M1 | sessions with all three layers (block scale) |
| M2 | years (2023, 2024) with ≥1 such session |
| M3 | blocks with all three layers |
| M4 | distinct teams with ≥1 SAME_TEAM pair |
| M5 | max single-team share of SAME_TEAM pairs |
| M6 | max single-session share of SAME_TEAM pairs |
| M7 | adjacency-balance feasibility share (≥1 same-stratum candidate) |
| M8 | max share of within-block (ST+DT) pairs touching one car-block |
| M9 | sessions with SAME_CAR_LOCAL_REPEAT or within-car-block repeat support |

**Levels:**

| Level | Rule |
|---|---|
| **STRONG** | M1 ≥ 6, M2 = 2, M3 ≥ 30, M4 ≥ 5, M5 ≤ 0.40, M6 ≤ 0.40, M7 ≥ 0.50, M8 ≤ 0.05, M9 ≥ 6 |
| **ADEQUATE** | M1 ≥ 3, M3 ≥ 10, M4 ≥ 3, M5 ≤ 0.60, M6 ≤ 0.60, M7 ≥ 0.25, M9 ≥ 3 |
| **MINIMAL** | M1 ≥ 1 and M4 ≥ 2 |
| **NONE** | otherwise |

**Rationale (fixed now):** the reference scale is Phase 4F, whose primary had 10 sessions with eligible blocks and 209 eligible blocks. STRONG asks for most of those sessions (≥6), both years, and ≥15% of the Phase 4F block count. It also requires broad, non-dominated team and session coverage and no single car-block driving the pair set.

**Cases:**

| Case | Rule |
|---|---|
| **A** | Tier 1 STRONG **and** Tier 2 STRONG |
| **B** | not A, and at least one tier is ≥ ADEQUATE. A future analysis is restricted to the tier(s) and sessions meeting ADEQUATE |
| **C** | not B, and Tier 2 is MINIMAL |
| **D** | otherwise |

2025 is evaluated with the same metrics and reported as agreeing or disagreeing; it never enters the case. The case uses no D and no hierarchy direction.

## 11. Gate for Phase 4J (4I.15)

| Case | Outcome |
|---|---|
| **A** | a Phase 4J may pre-specify one confirmatory analysis |
| **B** | only within the supported restricted population |
| **C or D** | no hierarchy test |

**Phase 4J is not run here.**

## 12. Forbidden

- Computing or inspecting same-team or different-team D.
- A hierarchy direction or estimator.
- Selecting nearest-time controls.
- Retuning the classifier.
- Modelling or power calculations built on unjustified assumptions.
- Ranking.
- Pooling 2025.
- Using 2018–2022 as lap-level evidence.
- Changing Phase 4A–4H files.
