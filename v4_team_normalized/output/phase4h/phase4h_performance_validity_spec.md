# V4 Phase 4H — Pre-specified Performance-Lap / Run-State Validity Audit

**Status:** written and committed **before** any run-state classification, calibration, filtered distribution, adjacency or Phase 4F/4G population audit was computed.

**What was inspected beforehand (source structure only):**
- which qualifying sessions exist;
- whether official QualLap1–4 values appear as consecutive Timing71 laps;
- what Timing71 records around qualifying attempts;
- whether practice stint boundaries coincide with feed pit messages;
- raw quantiles of lap time by stint position in 4 practice sessions.

No D, team, adjacency or hierarchy quantity was looked at. The rules below are not changed after results are seen.

**Nature:** a measurement-validity / data-quality audit. It is **not**:
- a hierarchy test, team-effect test, traffic or tow analysis, or causal analysis;
- a model refit or strategy model;
- a ranking.

**No filtered same-team vs different-team hierarchy is computed in Phase 4H.**

## 0. Freeze

**Phase 4F:** commit `81455f3`, CASE **D**. **Phase 4G:** commit `d903148`, CASE **A**.
- Neither is reinterpreted.
- The SHA-256 of all 61 Phase 4F and 4G files are in `phase4h_freeze_record.csv`.
- FINAL_V2/V3 frozen manifests were verified exact at the start of Phase 4H.

**Source label:** lap records are **Timing71 archived recordings of the INDYCAR live timing feed (third-party)**. The official INDYCAR session details (2023–2024 only; no 2025 official details were retrieved in Phase 4E) are used only to anchor the official qualifying laps. The two sources are labelled distinctly.

Phase 4E and 4F functions are imported read-only. New work is written only to `output/phase4h/`.

## 1. Structural facts established before this spec

**Qualifying (Timing71):**
- Only the timed laps are recorded; warm-up laps are **not** recorded as laps.
- A car's several attempts appear inside one Timing71 "stint", separated by timestamp gaps of hours.
- **Timing71 "stint" in qualifying is not pit-bounded.** The Phase 4E out-lap rule ("first lap of stint") therefore removes a *timed* qualifying lap. This is recorded as a finding. Phase 4E and 4F are not modified.

**Official qualifying records:**
- They give QualLap1–4 (the counting attempt) for 2023–2024.
- These appear as an exact run of 4 consecutive Timing71 laps (4-dp lap times) for:
  - 26/34 cars on 2023 Day 1;
  - 22/22 in 2023 Top-12, Last Chance and Fast 6;
  - 19/34 on 2024 Day 1;
  - 6/6 in the 2024 Fast 6.

**Practice (Timing71):**
- About 90% of stint starts and ends coincide within 5 s with a feed message "has left the pits" / "has entered the pits".
- In the sessions inspected, the first lap of a stint (median 64–71 s) and the last lap of a stint with an end (median 64–80 s) include pit-lane time.

## 2. Populations

**Qualifying reference sessions (Tier A/B formal qualifying):**

| Year | Sessions |
|---|---|
| 2023 | Day 1 (6202); Top-12 / Last Chance / Fast 6 combined capture (6204+6205+6206) |
| 2024 | Day 1 (6382); Fast 6 (6386) |
| 2025 | Day 1 (6656); Fast 6 (6660) — separate |

The Tier C qualifying captures (6384, 6659) are excluded, as they were in Phase 4E.

**Qualifying attempt:**
- A maximal run of a car's consecutive Timing71 laps in one source file, each timestamp-coherent with its predecessor (|Δts − laptime| ≤ 2 s).
- Attempt provenance:

| Label | Definition |
|---|---|
| `OFFICIAL_ANCHORED` | an attempt of exactly 4 laps whose 4-dp lap times equal the official QualLap1–4 of that car in the matching official segment (2023–2024) |
| `INFERRED_4LAP` | any other attempt of exactly 4 laps (all years; the only kind available for 2025) |
| `OTHER_LENGTH` | attempts of ≠ 4 laps: reported, never used as reference |

**Practice population:** every Timing71 Tier A/B **practice-type** session admitted in Phase 4F. That is, Phase 4F roles PRIMARY (2023–2024) and ERA_C_SECONDARY (2025), with categories PRACTICE, FAST_FRIDAY, QUALIFYING_WEEKEND_PRACTICE, POST_QUALIFYING_PRACTICE and CARB_DAY. **2025 is reported separately and never pooled.** The race is excluded.

**Lap records:** all Timing71 lap records (after the Phase 4F de-duplication), every flag. Raw laptime and timestamp are kept unaltered; speed = 2.5 × 3600 / laptime. Nothing is imputed.

## 3. Lap inventory fields (4H.3)

**Per lap:**
- source file, session, category, year, role;
- car, driver, canonical team (V4 registry);
- stint id, with **stint provenance**:
  - `PIT_MESSAGE_MATCHED_START/END` if the stint start/end lies within 5 s of a feed pit-exit/pit-entry message for that car;
  - otherwise `TIMING71_ANALYSIS_STINT_UNMATCHED`;
- timestamp; lap speed; position in stint;
- previous/next-lap speed and the deltas to them (within the stint, else missing);
- the car's fastest lap in the stint and in the session;
- relative deficits: 1 − v / stint-best, and 1 − v / session-best;
- `ts_tied` (another record in the session has the identical ms timestamp);
- `coherent_prev` (|Δts − laptime| ≤ 2 s with the previous lap in the stint);
- flag;
- Phase 4F `broad` / `comparable` flags (copied, for audit only).

## 4. Evidence tiers (4H.5)

| Tier | Contents |
|---|---|
| **DIRECTLY OBSERVED** | lap flag (green / yellow / red); pit exit and pit entry (feed messages matched to stint boundaries); lap time; feed-update timestamp |
| **INFERRED PROXY** | out-lap / in-lap for unmatched stint boundaries; restart lap (previous lap non-green); build lap (2nd in a pit-bounded stint); pre-in-lap (penultimate); capture gap (incoherent timestamp); steady-state window; level relative to own best |
| **UNKNOWN** | fuel load, tyre age, setup, boost level within a session, run purpose (qualifying vs race simulation), tow / traffic state, driver intent |

## 5. Deterministic classifier (4H.6)

**Inputs:** only a car's **own** laps in one session: flag, stint structure, pit-message match, lap time and timestamp coherence. It never uses D, team identity, other cars, timing adjacency, or the Phase 4F/4G Δ or case.

**Step 1 — `D_CLEARLY_NON_COMPARABLE`** if any of the following holds:
- (d1) flag ≠ green (observed);
- (d2) first lap of a stint whose start is `PIT_MESSAGE_MATCHED` (observed out-lap);
- (d3) last lap of a stint whose end is `PIT_MESSAGE_MATCHED` (observed in-lap);
- (d4) laptime outside the Phase 4E plausibility band [37.0, 45.0] s (pre-existing rule; not at speed).

**Step 2 — windows.** A *window* is 4 laps with consecutive positions in the same stint and source file, where:
- none of the 4 is D;
- each of laps 2–4 is timestamp-coherent with its predecessor.

A lap that belongs to no window is **`E_INPUT_INSUFFICIENT`**.

**Step 3 — window statistics:**
- relative range r_w = (max v − min v) / max v;
- median speed m_w.

For threshold level q ∈ {95, 100}:
- M*_q(car, session) = max m_w over that car's windows in the session with r_w ≤ T_steady(q);
- level deficit ℓ_w,q = 1 − m_w / M*_q.

**Step 4 — classes:**

| Class | Rule |
|---|---|
| `A_PERFORMANCE_COMPARABLE` | the lap belongs to ≥1 window with r_w ≤ T_steady(95) **and** ℓ_w,95 ≤ T_level(95) |
| `B_PLAUSIBLY_PERFORMANCE_COMPARABLE` | not A, and the lap belongs to ≥1 window with r_w ≤ T_steady(100) **and** ℓ_w,100 ≤ T_level(100) |
| `C_RUN_STATE_AMBIGUOUS` | in ≥1 window, but neither A nor B |

**Thresholds** come only from the **2023 `OFFICIAL_ANCHORED` qualifying attempts**, by pre-declared quantile rules:
- **T_steady(q)** = the q-th percentile (95th, 100th = max) of the within-attempt relative range (max − min)/max.
- **T_level(q)** = the q-th percentile, over the same attempts, of 1 − (official attempt median speed) / (the car's best median over all its `OFFICIAL_ANCHORED` or `INFERRED_4LAP` attempts in that qualifying session capture). The value is 0 when the official attempt is the car's best.
- Quantiles use numpy's default linear interpolation.
- The same classifier (Steps 1–4) is applied to qualifying sessions for calibration.
- **Minimum reference:** at least 20 attempts in 2023.

**Interpretation limit (declared now):** class A means "a steady 4-lap window within the qualifying envelope of steadiness and near the car's own best steady level in that session". It does **not** observe run purpose, fuel, tyres, tow or traffic. It is not called a "push lap".

## 6. Calibration (4H.7)

The frozen thresholds are applied to the qualifying reference laps. Reported:
- **Retention** (share classified A, and A∪B) of the laps of:
  - 2023 `OFFICIAL_ANCHORED` (in-sample; labelled);
  - **2024 `OFFICIAL_ANCHORED` (out-of-year: primary calibration)**;
  - 2023–2024 `INFERRED_4LAP`;
  - 2025 `INFERRED_4LAP` (separate).
- **Attempt coherence:** the share of official attempts whose 4 laps all receive the same class.
- **Known non-performance structures in qualifying:** NOT AVAILABLE, because warm-up and in-laps are not recorded. This is stated, not manufactured.

**Practice proxy negatives** (inferred; not used as criteria): the A share among build laps (position 2 of pit-bounded stints), pre-in-laps and restart laps, vs laps at positions ≥ 3.

**No re-tuning.** The thresholds are computed once. No alternative quantile family is tried.

## 7. Practice structure and Phase 4F/4G audit (4H.8–4H.9)

**Practice class shares:**
- by year, session, category, stint position and team (coverage only, alphabetical, never ranked);
- over three denominators: all laps, non-D laps, and evaluable laps.

**Car-block run-state label** (Phase 4F comparable layer, 5-min blocks): the **modal class** of the block's laps; ties go to the later letter (less comparable).

**Pair run-state match:**
- Pairs are **matched** if both car-blocks have the same label.
- Pairs are also flagged as **involving C** (ambiguous) and **involving D or E**.

**Populations audited** (from Phase 4F/4G outputs, read-only):
- Phase 4F targets with their teammate (C1) and their primary control (A);
- all teammates (C2);
- the different-team pool (B);
- the team-balanced population.

**Adjacency** (Phase 4G strata, read-only pair labels):
- the matched-share by stratum;
- descriptive D by adjacency stratum **within both-A pairs** and **within mismatched pairs**, for **different-team pool pairs only**. This asks whether the adjacency → lower-D gradient persists when run-state class is held equal.
- No same-team vs different-team contrast is computed. No mediation is claimed.

## 8. Qualifying negative control (4H.10)

**Construction:** the Phase 4F car-block and Phase 4G sequence machinery is applied to the qualifying reference sessions. Different-team pairs within 5-min blocks are counted.

**Rule:**
- If fewer than 30 pairs exist in **both** the no-intervening stratum and the >5-between stratum → **NOT IDENTIFIABLE**. No comparison is made.
- Otherwise, descriptive D by stratum is reported.

## 9. Measurement-validity cases (4H.11; 2023–2024 primary practice; mechanical)

**Denominator:** non-D practice laps (at-speed green laps outside observed pit laps).

**Calibration criteria:**
- **C1 (out-of-year retention):** 2024 official retention of A∪B ≥ 0.90 **and** of A ≥ 0.80.
- **C2 (2025 consistency, secondary):** 2025 inferred retention of A∪B ≥ 0.80.

**Share criteria:**
- **S_AB** = share of non-D practice laps in A∪B.
- **S_A_year** = share of non-D practice laps in A, each year.
- **S_C** = share in C.
- **Stability** = |S_AB − S_A|.

**Cases** (precedence C → D → A → B):

| Case | Rule |
|---|---|
| **C** | fewer than 20 2023 or fewer than 10 2024 official attempts, **or** C1 fails |
| **D** | C1 passes **and** S_AB < 0.20 |
| **A** | C1 **and** C2 pass, S_A_year ≥ 0.50 in both 2023 and 2024, S_C ≤ 0.25, and stability ≤ 0.15 |
| **B** | otherwise |

2025 is reported as agreeing or disagreeing, and never enters the case. These labels concern measurement validity only. They do not overwrite Phase 4F CASE D or Phase 4G CASE A.

## 10. Gate (4H.12)

| Case | Outcome |
|---|---|
| **A** | Design principles only for a possible Phase 4I, not run. Even then, run purpose, tow and traffic remain unobserved (§5 limit). |
| **B** | State whether only a restricted sensitivity analysis would be defensible (not confirmatory); not run. |
| **C or D** | Stop pursuing the practice-based hierarchy; Phases 4F and 4G stand as evidence that raw practice observations are not clean performance measurements. |

**Stop after the gate.**

## 11. Forbidden

- Hierarchy recomputation of any kind (same team vs different team).
- Team effects.
- Ranking.
- Tow or traffic claims.
- Model fitting.
- Tuning thresholds against Phase 4F/4G outcomes or re-tuning against qualifying.
- Pooling 2025 or the race.
- Changing Phase 4A–4G files.
