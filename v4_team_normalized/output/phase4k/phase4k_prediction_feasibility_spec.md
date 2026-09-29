# V4 Phase 4K — Pre-specified Point-in-Time Teammate Prediction Feasibility Audit

**Status:** written and committed **before** any prediction-event count was enumerated.

**Inspected beforehand (verification only):**
- git state; Phase 4J CASE B;
- FINAL_V2/V3 hashes; the paper is unchanged;
- the column list and cadence of the Phase 4E PTSC extraction (15-min readings of track and ambient °C);
- the Phase 4E note that forecast vintages are MISSING;
- the frozen R5.2 physics file.

**Scope:** support and identifiability only. The following are **not** computed:
- predictions, MAE, RMSE, directional accuracy, or correlation with outcomes;
- which predictor wins;
- a teammate coefficient, λ, or any fitting;
- Δv_target (future target movement), which is never used to select events.

This phase does not revisit Phase 4J (**FINAL, CASE B**), and does not concern the hierarchy question.

## 0. Freeze

| Item | Value |
|---|---|
| Branch / commit at start | `v4-team-normalized-evidence` @ `04c39f8` |
| Phase 4F | D |
| Phase 4G | A |
| Phase 4H | D |
| Phase 4I | B |
| Phase 4J | B |

- SHA-256 of all 451 Phase 4A–4J output files: `phase4k_freeze_record.csv`.
- FINAL_V2/V3 exact; nothing outside V4 changed.
- The Phase 4H classifier and the Phase 4I eligibility are re-verified by the checks.
- New work only under `output/phase4k/`.

## 1. Populations

**PRIMARY:**
- 2023–2024, Tier 1 (Phase 4H class A);
- the Phase 4I Tier 1 supported practice-type sessions **6199, 6207, 6208, 6375, 6378, 6380, 6387, 6388**;
- race, qualifying, 2018–2022 (no classifier projection) and unsupported sessions are excluded.

**SECONDARY** (after the primary counts are written; never pooled; never rescue the primary):

| Label | Tier | Sessions |
|---|---|---|
| `2025_SECONDARY_FEASIBILITY` | Tier 1 | 6651, 6653, 6654, 6655, 6662, 6663 |
| `EXTENDED MEASUREMENT-VALIDITY FEASIBILITY` (2023–24) | Tier 2 (A or B) | 6198, 6199, 6200, 6207, 6208, 6375, 6378, 6380, 6387, 6388 |

## 2. Observation and time stamps

- **Observation:** the frozen Phase 4I car-block (session, ⌊ts/300⌋, car) built from the tier's eligible laps.
- **Value:** v = median eligible-lap speed (mph). It is *recorded* for later use and **never used in any Phase 4K selection or statistic**, beyond confirming it is non-missing.

Per observation:
- **first_ts:** the earliest eligible lap timestamp;
- **source_ts:** the median eligible lap timestamp (the Phase 4F car-block time);
- **avail_ts:** the latest eligible lap timestamp. The observation is fully known only after this feed update.

## 3. Prediction events (target-centric; one per future outcome)

**Definitions:**
- **t1:** an eligible target car-block in a primary session.
- **t0:** the **immediately preceding eligible car-block of the same car in the same session**. The first eligible car-block of a car in a session has no event.
- **Canonical:** each t1 belongs to exactly one event.
- **Chronological only:** no speed values are used.

**Prediction time (primary):**
- `prediction_time` = t1.first_ts. Information must have timestamp **strictly <** `prediction_time`.
- Anything in the same unresolved feed update as the first outcome lap (equal timestamp) is therefore never treated as prior. No within-update order is invented.

**Conservative variant** (sensitivity counts only): `prediction_time_cons` = t0.avail_ts. Teammate or placebo information must then be complete strictly before the target's own latest observation completed.

**Recorded per event:**
- target car and team; t0 and t1 times and block IDs;
- horizon h = t1.source_ts − prediction_time; baseline interval t1.source_ts − t0.source_ts;
- same or different stint (Phase 4I `stint_key`);
- the timing-adjacency descriptor is not needed across blocks and is not computed.

## 4. Point-in-time label confirmation (leakage control; classifier unchanged)

**The issue:** the frozen Phase 4H class-A label is **retrospective**. It uses 4-lap windows that can extend after a lap, and the car's session-best steady level M*.

**Confirmation rule:** a frozen class-A lap is **point-in-time confirmed at τ** if, using only laps with timestamp < τ, the *unchanged* Phase 4H rule (same thresholds T_steady_95 = 0.0094017 and T_level_95 = 0.0016735) labels it A:
- there is a window containing the lap, fully completed before τ (its last lap timestamp < τ);
- the window has r_w ≤ T_steady_95;
- the window median is ≥ (1 − T_level_95) × M*_95(τ), where M*_95(τ) is the max median of that car's steady windows completed before τ.

**Other points:**
- The class definition is unchanged; only the information set is restricted.
- A car-block observation is **PIT-confirmed at τ** if **all** of its frozen-A laps are PIT-confirmed at τ.
- **Outcome labels (t1) are retrospective by definition.** This is recorded as a limitation: eligibility of the outcome depends on its level relative to the session best. It applies equally to all future predictors.

## 5. Physical inputs (no imputation)

**Physical state at time x:** the **latest PTSC reading at or before x**, with age ≤ 15 min (the archive cadence), for both track_c and ambient_c. Otherwise the input is missing. Values are never interpolated or imputed.

**Other fields:**
- wind: unit unverified (Phase 4E), so not used;
- humidity and pressure: recorded as available, not required.

**Coverage reported:**

| Type | Definition |
|---|---|
| **REALIZED-ENVIRONMENT** | readings exist for t0 and t1 (x = t0.source_ts, t1.source_ts). The t1 reading may lie after `prediction_time` |
| **POINT-IN-TIME-KNOWN** | the reading assigned to t1 is timestamped < `prediction_time` |
| **Resolved change** | t0 and t1 map to different readings (vs the same reading, so Δ = 0 at 15-min resolution) |
| **GENUINE FORECAST VINTAGE** | none exist in the frozen evidence (Phase 4E: HRRR not retrieved), so **0** |

**Frozen physics reference** (β_track = −0.03482533, β_ambient = +0.18239338): mechanically applicable where t0 and t1 both have track and ambient readings. It is never refit and never assumed to be correct for practice.

## 6. Teammate and placebo signals

**Teammate movement for teammate car j:**
- j is a different car, the same canonical team, primary teammate layer, not technical-partnership-only, the same session;
- **s1** = j's latest eligible car-block with avail_ts < `prediction_time`;
- **s0** = j's immediately preceding eligible car-block (same session);
- every teammate with such an (s0, s1) is enumerated, and none is chosen;
- s0 < s1 is guaranteed chronologically.

**Recorded per teammate signal:**
- age = `prediction_time` − s1.avail_ts;
- movement interval = s1.source_ts − s0.source_ts;
- block gap = s1.block − s0.block;
- same or different stint;
- overlap with the target interval [t0.source_ts, t1.source_ts];
- physical readings at s0 and s1.

**Prior teammate observation (F2):** ≥ 1 teammate car-block with avail_ts < `prediction_time`.

**Placebo movement:** the same construction for **different-team** cars.

**Structural comparability of placebo q to teammate signal j** (no performance criterion):
- q.s1 is in the **same 5-min block** as j.s1, which gives a comparable age;
- the **same block gap** s1 − s0;
- the **same same/different-stint status**.

The Phase 4G adjacency category between j.s1 and q.s1 (same block) is recorded descriptively.

## 7. Nested feasibility populations (primary definitions; fixed)

| Level | Definition |
|---|---|
| **F0** | an event (t0, t1) exists |
| **F1** | F0 + track and ambient readings at t0 and t1 (realized) |
| **F2** | F1 + ≥ 1 prior teammate observation |
| **F3** | F2 + ≥ 1 prior teammate movement (s0, s1) |
| **F4** | F3 + ≥ 1 structurally comparable placebo movement for at least one teammate movement |
| **F5** | F4 + no leakage and unambiguous chronology (all conditions below) |

**F5 conditions:**
- t0 is PIT-confirmed at `prediction_time`;
- for **at least one** (teammate signal, comparable placebo) combination, s0, s1, q.s0 and q.s1 are all PIT-confirmed at `prediction_time`;
- every used lap timestamp is < `prediction_time` (strict; ties excluded);
- the physical readings for t0, s0, s1, q.s0 and q.s1 are timestamped < `prediction_time`.

**F5 counting:** F5 events are counted per canonical t1. The teammate and placebo signals are not reduced to one choice here; aggregation is left to a future Phase 4L specification. The conservative-cutoff F5 is reported separately.

**Model-free support** (within F4 / F5):

| Label | Definition |
|---|---|
| `MODEL_FREE_EXACT` | the target t0/t1, teammate s0/s1 and placebo q.s0/q.s1 each map to a single PTSC reading within the interval (no measured change) |
| `MODEL_FREE_MATCHED` | the target interval and the teammate and placebo intervals map to the *same pair* of PTSC readings (identical measured change) |

## 8. Dependence and coverage

**Dependence:**
- total events, unique t1 (equal by construction), cars, teams, sessions, teammate cars, target–teammate pairs;
- teammate-movement reuse (the same (j, s0, s1) across events) and placebo reuse (maximum and median);
- events per car-session trajectory and per stint.

**Coverage:** by year, session, category, target team (alphabetical; coverage only) and target car.

**Horizons:** p10, p25, median, p75, p90 and max of the target horizon, baseline interval, teammate age and interval, and placebo age and interval. No horizon cutoff is imposed.

## 9. Feasibility cases (primary F5; mechanical; no prediction outcomes)

**Metrics:**
- **N5:** F5 events (unique future outcomes);
- **S5:** sessions; **K5:** target teams; **C5:** target cars; **Y5:** years;
- **MS:** max single-session share; **MT:** max single-target-team share;
- **MP:** max single target–teammate-car-pair share among F5 teammate signals.

**Cases:**

| Case | Rule |
|---|---|
| **A** (strong) | N5 ≥ 100, S5 ≥ 6, K5 ≥ 6, C5 ≥ 20, Y5 = 2, MS ≤ 0.35, MT ≤ 0.35, MP ≤ 0.15 |
| **B** (partial) | not A, and N5 ≥ 30, S5 ≥ 4, K5 ≥ 4, C5 ≥ 10, MS ≤ 0.50, MT ≤ 0.50 |
| **C** (weak) | N5 ≥ 1, not A or B |
| **D** (not identifiable) | N5 = 0 |

**Rationale:** the scale follows Phase 4J, whose strict primary was 53 contexts in 6 sessions (CASE B support).

The secondary populations get the same metrics as labels. They never change the primary case.

## 10. Phase 4L gate

| Case | Outcome |
|---|---|
| **A** | one pre-registered Phase 4L experiment |
| **B** | only within the explicitly supported restricted population |
| **C or D** | no Phase 4L |

**Phase 4L is not run here.**

## 11. Forbidden

- Using Δv_target or any speed difference to select events.
- Computing prediction errors or predictor comparisons.
- Fitting any coefficient or λ.
- Choosing a teammate by resemblance to the outcome.
- Inventing within-update order.
- Imputing physics.
- Pooling 2025.
- Using Tier 2 to rescue Tier 1.
- Changing Phase 4A–4J files.
- Changing these rules after counts.
