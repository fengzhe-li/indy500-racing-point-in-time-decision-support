# V4 Phase 4J — Final Pre-registered Performance-Control Hierarchy (Specification)

**Status:** written and committed **before** any Phase 4J performance D, hierarchy contrast, bootstrap, leave-one-out result or Tier 2 / 2025 value was computed.

**Computed beforehand (verification only; no speed difference):**
- `phase4j_input_verification.csv`: branch/commit; Phase 4F D, 4G A, 4H D and 4I B unchanged;
- Phase 4H classes and Phase 4I eligibility (laps, within-block pair universe, same-car pairs) reproduced exactly;
- FINAL_V2/V3 hashes exact; paper unchanged;
- `phase4j_freeze_record.csv`: 419 Phase 4A–4I files hashed;
- the list of Phase 4I-supported sessions per tier (structure only).

**FINALITY:**
- This is the final hierarchy analysis of V4, and its result is accepted regardless of direction.
- No Phase 4K estimator.
- No redesign, re-tuning of windows, thresholds, weights or exclusions, re-definition of adjacency, or loosening of the Phase 4H classifier after results.

**Scope:** an empirical performance-control hierarchy in a restricted population. It is **not**:
- a causal decomposition or variance decomposition;
- a team effect, or a team or driver ranking;
- pure pace;
- a tow, traffic, strategy or weather model.

**Source:** Timing71 archived recordings of the INDYCAR live timing feed (third-party).

## 1. Population

**Primary:**
- **Years:** 2023–2024.
- **Sessions:** the Phase 4I Tier 1 supported sessions (all three layers at block scale): **6199, 6207, 6208, 6375, 6378, 6380, 6387, 6388** (8). No session is added.
- **Evidence tier:** Tier 1 only; every observation is Phase 4H class A (`A_PERFORMANCE_COMPARABLE`).
- **Excluded:** race, qualifying, 2018–2022, 2025, unsupported sessions, and B/C/D/E laps.

**Tier 2 sensitivity** (only after the Tier 1 result is frozen):
- class A or B laps (Phase 4I);
- the Phase 4I Tier 2 supported 2023–24 sessions: 6198, 6199, 6200, 6207, 6208, 6375, 6378, 6380, 6387, 6388.

**2025 hybrid-era secondary replication** (only after the primary is frozen):
- Tier 1, the Phase 4I Tier 1 supported 2025 sessions: 6651, 6653, 6654, 6655, 6662, 6663;
- never pooled.

## 2. Observational unit and performance summary

- **Unit:** the frozen Phase 4F/4I **car-block** (session, 5-min epoch block ⌊ts/300⌋, car_id). It is built from the tier's eligible laps only, with the Phase 4I `carblocks` function.
- **Performance summary v:** the **median lap speed (mph)** of the car-block's eligible laps. This is the Phase 4F car-block summary applied to eligible laps.
- Laps within a car-block never count as separate observations.
- **D** = |v₁ − v₂| in mph.

## 3. Layers

**SAME_CAR (local repeat; primary same-car rule):**
- the same car_id, the same session, the same stint (Phase 4I `stint_key`), in **consecutive 5-min blocks** (b, b+1), both eligible;
- this is the Phase 4F SAME_CAR structure. It is admissible because Phase 4I shows these local repeats are about 80–100 s apart, the same time scale as the same-team pairs (median about 73 s);
- cross-run, cross-session and days-apart same-car pairs are **excluded** from the hierarchy;
- context value = D of that pair.

**SAME_TEAM context:**
- an **oriented** eligible teammate pair (target i, teammate j): different cars, the same canonical team, both in the primary teammate layer, no technical-partnership-only relationship, the same session and the same 5-min block;
- each unordered pair gives two contexts (i→j and j→i);
- D_st(context) = |v_i − v_j|.

**DIFF_TEAM candidates for a context:**
- every eligible car-block k in the same session and block with a canonical team different from i's (the Phase 4I candidate universe);
- **no nearest-time selection**.

## 4. Adjacency balance (design-balance variable only)

- **Categories:** Phase 4G `pair_metrics` over all Timing71 records of the session, with **i as target**, using the tier's eligible laps. The categories are SAME_UPDATE (tied / order unobserved), CONSECUTIVE, BETWEEN_1_2, BETWEEN_3_5 and BETWEEN_GT5. No new threshold.
- **Exact-stratum rule:** a candidate k is admissible for context (i, j) only if c(i, k) = c(i, j).
- **Strict common support:** a context is in the primary population only if it has **≥ 1 admissible candidate**, the Phase 4I feasibility definition.
- **No substitution:** a nearest stratum is never substituted. Out-of-support contexts, including the Tier 1 same-update contexts with no same-update candidate, are kept in the coverage tables only.
- Counts with ≥ 3 admissible candidates are reported descriptively. That is not a criterion.

## 5. Aggregation and weighting

- **Different-team context value:** D_dt(context) = the **median** over admissible candidates k of |v_i − v_k|. The median is the robust summary used throughout V4. Each context contributes one value, and candidate pairs are never treated as independent.
- **Per session s** (common-support contexts and same-car pairs of that session):
  - D_sc,s = median of same-car local-repeat pair D;
  - D_st,s = median of D_st(context);
  - D_dt,s = median of D_dt(context).
- **Session contrasts:**
  - **C1_s** = D_st,s − D_sc,s;
  - **C2_s** = the median over contexts of [D_dt(context) − D_st(context)] (paired within context: the same target, block and adjacency stratum);
  - **C3_s** = D_dt,s − D_sc,s.
- **Evaluable session:** ≥ 1 common-support context **and** ≥ 1 same-car local pair.
- **Primary estimates** (equal session weight):
  - D_layer = the median over evaluable sessions of D_layer,s;
  - C1, C2 and C3 = the median over evaluable sessions of C1_s, C2_s and C3_s.
- Differences of the layer medians are also reported descriptively.
- **The session is the replication unit.**

## 6. Uncertainty and sensitivity (descriptive; not used to tune)

**Session bootstrap:**
- resample evaluable sessions with replacement, B = 2000, seed 20261001 (the Phase 4F values);
- median of the session contrasts; 95% percentile interval;
- the number of unique sessions is reported, and no p-values.

**Leave-one-session-out:** drop each evaluable session and recompute C1, C2 and C3.

**Leave-one-team-out:**
- remove every car-block of one canonical team from all layers (targets, teammates, candidates, same-car), then recompute the common support and the contrasts;
- teams considered: those present in primary common-support contexts;
- a removal is **feasible** if ≥ 1 evaluable session remains.

**Sign stability:** reported for all of the above.

## 7. Interpretation (mechanical; primary Tier 1 2023–24)

**Contrast status** for k ∈ {1, 2}:

| Status | Rule |
|---|---|
| `POSITIVE_CONSISTENT` | C_k > 0 **and** ≥ 75% of evaluable sessions have C_k,s > 0 **and** every LOSO C_k > 0 **and** every feasible LOTO C_k > 0 |
| `NEGATIVE_CONSISTENT` | the mirror image: < 0, ≥ 75% negative, all LOSO < 0, all feasible LOTO < 0 |
| `INCONSISTENT` | otherwise |

**Cases** (precedence E → D → A → B → C):

| Case | Rule |
|---|---|
| **E** (strict common support too small) | fewer than **5** evaluable sessions, **or** fewer than **20** common-support contexts |
| **D** (opposite / contradictory) | C1 or C2 is `NEGATIVE_CONSISTENT` |
| **A** (full hierarchy) | C1 and C2 are both `POSITIVE_CONSISTENT` |
| **B** (partial) | exactly one of C1, C2 is `POSITIVE_CONSISTENT`, **or** both C1 > 0 and C2 > 0 in aggregate while at least one is not consistent |
| **C** (no clear hierarchy) | otherwise |

**Status of the case label:**
- The label applies to the **primary only**.
- Tier 2 and 2025 get the same mechanical label but are reported only as `EXTENDED MEASUREMENT-VALIDITY SENSITIVITY` and `2025 HYBRID-ERA SECONDARY REPLICATION`.
- They never replace or overturn the primary.
- If they fail the E criteria, they are reported as NOT IDENTIFIABLE / INSUFFICIENT SUPPORT.

## 8. Scale

- All D and contrast values are reported in mph, in % of the median eligible speed, and as a lap-time equivalent at 225 mph (Δt ≈ 40 s × Δ/225).
- **Context** comes from the Phase 4I references: qualifying within-attempt SD, class-A same-car local variation, and recorded precision.
- Empirical separation is distinguished from competitive significance. No universal threshold is imposed.

## 9. Order of computation

1. Tier 1 primary: all outputs, and the case label written to `case_evaluation.csv`.
2. Then Tier 2 sensitivity.
3. Then the 2025 replication.

Nothing in steps 2–3 alters step 1.

## 10. Forbidden

- Nearest-time comparator selection.
- New block widths.
- New adjacency thresholds.
- Loosening the classifier.
- Promoting Tier 2 or 2025.
- Pooling 2025.
- Modelling.
- Ranking.
- Changing Phase 4A–4I files.
- Any post-result redesign.
