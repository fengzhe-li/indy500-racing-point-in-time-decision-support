# V4 Phase 4F — Pre-specified Design: Empirical Performance-Control Hierarchy

**Status:** written and committed **before** any car-block value, comparison, contrast or hierarchy result was computed. Primary rules are not modified after results are seen. Phase 4E is frozen and is only read.

**Hypothesis under test, not assumed:** same car > same canonical engineering team (different car) > different team, where ">" means smaller local performance difference.

## 0. Source labelling (addendum 2)

- **Lap data** are **Timing71 archived recordings of the INDYCAR live timing feed**, a third-party capture. They are labelled `TIMING71_ARCHIVED_LIVE_FEED` everywhere and are never called official INDYCAR lap data.
- **Official INDYCAR session-detail records** are used **only as a cross-check**: car presence per session and best-lap agreement. They are labelled `INDYCAR_OFFICIAL_SESSION_DETAILS`.

## 1. Inclusion (addendum 1: exactly the Phase 4E Design-1-feasible combinations)

- **Phase 4E Design 1 result:** "FEASIBLE NOW" **only for Era B (2023–2024)**. 2025 (Era C) was "FEASIBLE WITH ADDITIONAL DATA" because it is the only in-scope year of its regime, even though its sessions are Tier A/B. This distinction is preserved.
- **PRIMARY:** the 15 Phase 4E lap-level session keys with era = ERA_B_REFERENCE, quality tier A or B, `hier_all_three` = True, and category ≠ RACE (read from `output/phase4e/evidence_hierarchy_feasibility.csv`).
  - **2023:** Practice 3 (6198), Practice 4 (6199), Fast Friday / Practice 5 (6200), Qualifications Day 1 (6202), Practice 7 (6203), the combined Top-12 / Last Chance / Fast 6 capture (6204+6205+6206, one key), Practice 8 (6207), Final Practice (6208).
  - **2024:** Practice 1 (6375), Practice 3 (6378), Fast Friday / Practice 5 (6380), Qualifications Day 1 (6382), Fast 6 (6386), Practice 8 (6387), Carb Day (6388).
- **SECONDARY, separately labelled `ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE`:** the 10 Era C 2025 Tier A/B `hier_all_three` non-race keys (6651, 6653, 6654, 6655, 6656, 6657, 6660, 6661, 6662, 6663). Reported as a replication and never pooled with the primary.
- **Race appendix:** the 2023–2025 race keys, structural counts only; no performance differences.

## 2. Exclusion

- **Out of scope:** the race (appendix only); 2018–2022 (failed the Phase 4E timestamp criterion; not reconstructed); every Tier C/D session; sessions not Design-1-flagged.
- **Cars:** cars not joined to the V4 registry, and technical-partnership-only entries (none are expected in 2023–2025; checked).

## 3. Laps, layers and the car-block validity check (addendum 3)

**Lap assembly:** laps are built from the retrieved Timing71 files with the Phase 4E parsing and join functions (imported and read-only; Phase 4E outputs are not rewritten).

- **Speed:** `speed_mph = 2.5 × 3600 / laptime_s`.
- **Timestamp:** the Timing71 lap timestamp (UTC).

**Layer 1 — BROAD:** exactly the Phase 4E `valid_lap`. That is:
- flag green or none;
- not the first lap of a stint (out-lap);
- not the in-lap as defined in Phase 4E;
- 37.0 s ≤ laptime ≤ 45.0 s.

**Layer 2 — COMPARABLE:** Layer 1 **and** all of the following, which are structural and derivable from stint and flag fields only:
- (a) flag explicitly `green` (excludes `none`);
- (b) the previous lap of the same stint exists and is flagged green (not the first lap after a restart or caution);
- (c) not the 2nd lap of a stint (the pit-exit-adjacent lap);
- (d) not the last lap of a stint that has an `endTime` (pit entry), and not the lap immediately before it (pit-approach-adjacent);
- (e) timestamp coherence with the previous lap: |Δtimestamp − laptime| ≤ 2 s. A larger gap indicates a missing capture, so the lap sequence is uncertain.

**What cannot be filtered:** fuel load, tyre age, tow/slipstream state, run purpose, boost, and qualifying/race simulations. No lap is removed for being slow beyond the Phase 4E plausibility band.

**Car-block validity check** (reported before any hierarchy result):
- per car-block: laps contributing; min, max, median, spread (max − min) of lap speed;
- positions in the stint;
- whether it contains pit-adjacent laps (Layer 1 only);
- a descriptive `WIDE_SPREAD` flag for spread > 3 mph (descriptive only, not used for exclusion);
- the lap-count distribution.

**Stated limit:** a car-block value is an **observed local performance summary**, not pure pace.

## 4. Blocks, unit and representative value

- **Block (primary):** 5 minutes, fixed and epoch-aligned: `block = floor(timestamp_utc_seconds / 300)`. It is never slid.
- **Block sensitivities:** 1, 2 and 10 min (the same alignment rule).
- **Unit:** session_key × block × car ("car-block").
- **Representative value:** the **median lap speed (mph)** of that layer's laps in the car-block. Each car has at most one value per block.
- **Also kept:** n laps, min, max, spread, and the median lap timestamp (the car-block time).
- **Minimum laps:** 1 (primary); ≥2 (sensitivity).

## 5. Comparison classes (primary metric D = |Δ representative speed| in mph; lap time is not used in the primary)

1. **SAME_CAR:** the same car in block k vs the same car in the **next** block k + 1 (adjacent blocks only), within the same session. Time separation = the difference of car-block times.
2. **SAME_TEAM:** within the same session and block, every unordered pair of **different** cars in the same canonical engineering team (V4 registry, primary layer).
3. **DIFF_TEAM (primary, balanced):** within the same session and block, for each **target car** that has ≥1 same-team partner in the block:
   - one control is chosen: the different-team car whose car-block time is nearest to the target's (ties go to the lower car number, then lexicographic);
   - the target's teammate comparator is its nearest-in-time same-team car;
   - both comparisons are recorded with their time separations.
   - **Sensitivity (`DIFF_TEAM_TEAM_BALANCED`):** per block, all cross-team car pairs are summarised with equal weight per team pair (the median within each team pair, then the median across team pairs).

## 6. Weighting and reuse

- **Weights:**
  - SAME_TEAM pairs are weighted 1 / (number of pairs of that team in that block), so each block-team counts once.
  - SAME_CAR and DIFF_TEAM comparisons have weight 1 each.
- **Balanced summaries:** the per-block median, then the per-session median, then the median across sessions with **equal session weight**.
- **Reuse:** it is audited but not prevented. A car-block appears in at most 2 SAME_CAR comparisons, in SAME_TEAM pairs with all of its teammates, and as a control for several targets. The maximum reuse is reported.

## 7. Primary metric and within-block contrast

- **Per target i in block b:**
  - D_st(i) = |v_i − v_nearest teammate|;
  - D_dt(i) = |v_i − v_matched different-team control|.
- **Delta_block** = median_i D_dt(i) − median_i D_st(i), over the targets in that block. Positive means same-team cars were more similar.
- **Primary statistic:** the **session-balanced median of Delta_block** (median within each session, then the median across the 15 primary sessions), Layer 2 (COMPARABLE), 5-min blocks.
- **Uncertainty:** a cluster bootstrap over **sessions** (B = 2000, seed 20261001). The percentile interval is reported with the explicit caveat that there are only 15 sessions. No pair-level bootstrap. p-values are not reported.

**Hierarchy descriptions:**
- median(D_same_team) − median(D_same_car) and median(D_diff_team) − median(D_same_team), pooled-weighted and session-balanced;
- ratios where the denominator is ≥ 0.01 mph.

## 8. Sensitivity and stability (all pre-declared)

- **Layer:** BROAD vs COMPARABLE.
- **Block width:** 1, 2, 5 and 10 min.
- **Minimum laps:** ≥2 laps per car-block.
- **Different-team definition:** DIFF_TEAM_TEAM_BALANCED.
- **Year:** 2023 and 2024 separately.
- **Session category:** PRACTICE, FAST_FRIDAY, QUALIFYING_WEEKEND_PRACTICE, QUALIFYING_DAY1, QUALIFYING_OTHER, POST_QUALIFYING_PRACTICE and CARB_DAY, each separately where it has ≥1 eligible block.
- **Leave one team out:** remove every car of one canonical team (as target, teammate and control) and recompute the primary statistic. No team is ranked.
- **Same-car fairness** (two constructions):
  - (i) **adjacent-block design for all three classes:** SAME_CAR (k, k + 1); SAME_TEAM_ADJ (car i in block k vs its nearest-time teammate in block k + 1); DIFF_TEAM_ADJ (car i in block k vs its nearest-time different-team car in block k + 1). Session-balanced medians are compared.
  - (ii) **time-separation reweighting:** within-block SAME_TEAM and DIFF_TEAM comparisons are reweighted to the SAME_CAR time-separation histogram (1-min bins, 0–10 min).
- **Era C (2025) secondary replication:** the full primary pipeline on the 2025 keys, reported separately.

## 9. Secondary analyses

- **Leave-one-out team reference:** for car-blocks with ≥1 same-team car in the block, ref₋ᵢ = the median of the other same-team car-block values, and dev_i = v_i − ref₋ᵢ. |dev| is reported. It is not called a team effect.
- **Cross-session persistence** (exploratory):
  - **Per car and session:** the median over blocks of the signed dev_i (Layer 2, 5 min). Multiple sessions of the same category within a year are combined per car by the median.
  - **Linked category pairs, within year:** PRACTICE→FAST_FRIDAY, FAST_FRIDAY→QUALIFYING_DAY1, QUALIFYING_DAY1→POST_QUALIFYING_PRACTICE, QUALIFYING_DAY1→CARB_DAY, PRACTICE→CARB_DAY, POST_QUALIFYING_PRACTICE→CARB_DAY.
  - **Reported:** the number of linked cars, Spearman ρ, and the sign-persistence rate (shown only for pairs with ≥8 cars).
  - **Interpretation limit:** not driver skill, not a car effect.
- **Weather diagnostic only** (PTSC from the Phase 4E extraction, read-only): per block, the number of PTSC readings in [block start − 15 min, block end] and the track/ambient range. No coefficients.
- **Official cross-check:**
  - Timing71 cars vs INDYCAR official records per session;
  - Timing71 best lap vs official best lap (agreement is reported, and the sources are kept distinct).
- **Race appendix:** car-blocks, blocks with ≥2 same-team cars, and blocks with all three classes. **No D values.**

## 10. Interpretation rules (mechanical; primary = Layer 2, 5 min, 2023–2024)

- **Team advantage "consistent"** requires all of the following:
  - the session-balanced median Delta_block > 0;
  - ≥75% of eligible primary sessions have a positive session-median Delta;
  - both 2023 and 2024 are positive;
  - no leave-one-team-out removal makes it ≤ 0;
  - the BROAD layer is also > 0;
  - 5 min and at least 2 of {1, 2, 10} min are > 0.
- **Same-car ordering "established":** in the fair adjacent-block design (§8 i), the session-balanced median D_SAME_CAR < D_SAME_TEAM_ADJ < D_DIFF_TEAM_ADJ.
- **Cases (precedence D → A → B → C):**

| Case | Rule |
|---|---|
| **D** | The session-balanced median Delta ≤ 0, **or** ≤50% of sessions have a positive session-median Delta. |
| **A** | The team advantage is consistent **and** the same-car ordering is established. |
| **B** | The team advantage is consistent, and the same-car ordering is not established. |
| **C** | Otherwise (positive, but it fails at least one consistency criterion). |

All satisfied criteria are reported. 2025 does not enter the case evaluation; it is reported as agreeing or disagreeing.

## 11. Forbidden

- Fitting any variance, latent or regression model.
- Estimating weather coefficients.
- Ranking teams or drivers.
- Pooling race with other sessions, pooling 2025 with 2023–2024, or using 2018–2022.
- Changing Phase 4E tiers.
- Changing these rules after seeing results.
