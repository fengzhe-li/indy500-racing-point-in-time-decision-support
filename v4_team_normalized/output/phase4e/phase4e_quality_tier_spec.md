# V4 Phase 4E — Data-Quality Tier and Audit Specification

**Status:** written and committed together with the pre-retrieval `source_inventory.csv`. That is **before** any new data was retrieved and **before** any opportunity count or tier was computed. The rules are not changed after results are seen. No performance model is fitted; no physical coefficient is estimated; no performance similarity enters any rule.

## 1. Session universe and categories

- **Session universe:** every Indianapolis 500 session in the official INDYCAR session list for 2018–2025 (`season_dropdown_raw.json`). Official names are preserved verbatim.
- **Timing71 replays:** mapped to official sessions by year, date and name.
- **Dates:** the official `SessionDate` (from EventsSessionDetails). The first official qualifying session defines "qualifying day 1" (Q1D).

**Normalized categories** (deterministic, applied in order):

| Category | Rule |
|---|---|
| `AGGREGATE_RESULT` | Official name contains "Combined" (a derived result table, not an on-track session). Excluded from opportunity counts. |
| `RACE` | Name == "Race". |
| `CARB_DAY` | Name contains "Final Practice", "Practice Final" or "Carb Day", or it is the last practice before the race on a later date than all qualifying (e.g. "Practice 9 (Carb Day)"). |
| `QUALIFYING_DAY1` | Name contains "Day 1" or "Day One", or it is the first qualifying session date's main qualifying session. |
| `QUALIFYING_OTHER` | Any other name containing "Qualif" or "Fast". The subtype preserves the official name (Fast 9 / Positions 10-33 / 31-33 / Last Chance / Top-12 / Fast 12 / Fast 6 …). |
| `FAST_FRIDAY` | A practice on the calendar day immediately before Q1D. |
| `POST_QUALIFYING_PRACTICE` | A practice dated after the last qualifying session and before the Carb Day date. |
| `QUALIFYING_WEEKEND_PRACTICE` (subtype of practice; reported separately) | A practice on a qualifying date. |
| `PRACTICE` | Any other practice. |

**Eras (never pooled):** 2018–2019 `ERA_A_PRE_AEROSCREEN`; 2020–2024 `ERA_B_REFERENCE`; 2025 `ERA_C_HYBRID`.

## 2. Observation units and validity (declared data-quality filters, not performance screens)

- **Primary unit for lap-level sources (Timing71 analysis JSON):** the lap. Each lap carries its car, driver, lap number, lap time, completion timestamp, flag and stint (run between pit visits).
- **Valid lap** (all required):
  - (a) flag is green or none (not yellow/red/checkered);
  - (b) the lap is not the first lap of a stint (out-lap);
  - (c) the lap is not the last lap of a stint that ended in the pits (in-lap), where stint-end information exists;
  - (d) 37.0 s ≤ laptime ≤ 45.0 s, the declared at-speed plausibility band (speed ≈ 200–243 mph). Laps outside it (warm-up, cool-down, traffic-lift, timing glitches) are counted separately as `NON_AT_SPEED`.
- **Race:** the same filters. Race laps are **never** combined numerically with any other category.
- **Qualifying:** laps are counted with the same filters. The four-lap qualifying attempt remains the accepted qualifying unit (Phase 3). It is summarised, not re-derived.
- **Sessions without lap-level machine-readable data:** their unit is the session-level record (best lap per car), which cannot support close-time comparisons.

## 3. Identity join

- **Join key:** (year, car number) to the accepted V4 registry (`v4_team_entry_registry.csv`, qualifying participants). A driver surname check is reported.
- **Backup cars:** a "T" suffix is mapped only when the surname matches (the Phase 3 rule).
- **No fuzzy matching.** Unmatched or ambiguous cars are reported and excluded from team-based counts.
- **Primary teammate layer:** registry `strict_teammate_group` non-empty. Technical-partnership entries are counted only in a separately labelled sensitivity column.
- **Raw identities kept:** the raw Timing71 team string and the official entrant label are preserved.

## 4. Opportunity definitions (counts only; no threshold is chosen for science)

All counts are within one session. They use the valid-lap timestamp (lap completion time).

- **Same-team pair:** two valid laps from **different cars** of the same canonical team (primary layer), with |Δt| ≤ w, for w ∈ {1, 2, 5, 10, 15, 30} min.
- **Different-team pair:** the same, with cars of different canonical teams (both mapped).
- **Same-car repeat:** consecutive valid laps of the same car. The gap distribution is reported.

**Every pair count is reported together with its "effective information" companions:**
- distinct car-pairs (relationships);
- distinct stint-pairs (overlapping runs);
- distinct (team, 5-min bin) cells with ≥2 same-team cars at speed;
- distinct cars and distinct teams.

Raw pair counts are never presented as independent observations.

**Team-reference feasibility** (per valid lap; the target is never in its own reference; counts only):
- nearest teammate valid lap within ±w;
- leave-one-car-out team mean (≥1 other same-team car with a valid lap within ±w);
- leave-one-car-out team median (≥2 other same-team cars within ±w);
- temporally weighted reference (≥1 other same-team car within ±30 min).

These are reported at w = 1, 2, 5, 10, 15, 30.

**Evidence-hierarchy coexistence** (per session, at w = 5 min, a data-availability criterion only):
- **A:** ≥1 car with ≥2 valid laps within 5 min;
- **B:** ≥1 same-team different-car pair within 5 min;
- **C:** ≥1 different-team pair within 5 min.

`all_three` = A and B and C.

## 5. Weather availability classes (per session; no imputation)

- **Observed PTSC** (ambient, track, humidity, pressure, wind [units unverified]): the Firestone archive has ≥1 observation inside the session's timing span (or on its date if no span).
- **HRRR forecast:** locally present only for Day 1, 2020–2024.
- **Solar and cloud:** HRRR only.
- **Wind:** always labelled `UNIT_UNVERIFIED`.

## 6. Session state class (a priori, by category)

| Category | State class |
|---|---|
| `QUALIFYING_*` | `SOLO_RUN_FORMAT` (defensible state) |
| `PRACTICE`, `FAST_FRIDAY`, `POST_QUALIFYING_PRACTICE`, `QUALIFYING_WEEKEND_PRACTICE`, `CARB_DAY` | `OPEN_TRACK_UNOBSERVED_RUN_PLAN` (traffic/tow, fuel, tyre, boost/run plan unobserved) — **one important limitation** |
| `RACE` | `RACE_STATE_CONFOUNDED` (traffic, fuel load, tyre age, cautions) — **major confounding** |

## 7. Quality tiers (deterministic; per session)

**Criteria:**
- **T:** lap-level timestamped machine-readable data were retrieved for the session.
- **I:** ≥95% of the cars observed with valid laps are joined to the V4 registry.
- **M:** ≥3 primary-layer canonical teams have ≥2 cars with valid laps.
- **O:** close-time overlap: ≥20 same-team different-car valid-lap pairs within ±5 min, involving ≥3 distinct canonical teams.
- **W:** observed PTSC weather covers the session (§5).
- **P:** the session appears in the official INDYCAR session list, and its lap-level source is documented (URL + SHA-256).

**Tier assignment:**

| Tier | Rule |
|---|---|
| **D** | Not T, **or** not I, **or** fewer than 2 primary-layer teams with ≥2 cars with valid laps, **or** `AGGREGATE_RESULT`. |
| **C** | Not D, and (state class `RACE_STATE_CONFOUNDED`, **or** L ≥ 2), where L = the number of failed items among {state limitation (`OPEN_TRACK_UNOBSERVED_RUN_PLAN`), not M, not O, not W, not P}. |
| **B** | Not D/C, and L = 1. |
| **A** | Not D, and L = 0 (state `SOLO_RUN_FORMAT`, and M, O, W and P all hold). |

The tier depends only on availability, measurement, overlap, state class and provenance. It never depends on observed performance.

## 8. Future-design feasibility labels (evaluated after the audit; no design is run)

Let *Tier-A/B sessions* mean sessions in tiers A or B.

| Design | FEASIBLE NOW | FEASIBLE WITH ADDITIONAL DATA | WEAK / HIGH-CONFOUNDING | NOT IDENTIFIED |
|---|---|---|---|---|
| 1 Evidence hierarchy | ≥10 Tier-A/B sessions with `all_three`, spanning ≥2 years within one era | Criteria met only after retrieving listed sources | `all_three` holds only in C-tier sessions | Otherwise |
| 2 Within-team relative performance | ≥10 Tier-A/B sessions where ≥50% of valid laps of multi-car-team cars have a leave-one-car-out team reference within ±5 min | — | Only C-tier | Otherwise |
| 3 Cross-session persistence | ≥50% of primary-layer cars in some era are linked across ≥3 session categories with valid laps, in Tier-A/B/C sessions | — | Linkage exists but mostly via C-tier race/practice | Otherwise |
| 4 Within-team dispersion | ≥10 Tier-A/B sessions meeting M | — | Only C-tier | Otherwise |
| 5 Race-only teammate structure | — (the race is always C) | — | Race sessions have lap-level data with flags, but fuel, tyre and traffic are unobserved | No lap-level race data |

The "additional data" label applies where local plus planned-retrieved sources are insufficient but a documented external source (e.g. official Section Results PDFs, 2022) would supply the missing criterion.

## 9. Forbidden in Phase 4E

- Fitting any model or estimating any coefficient.
- Computing a preferred team-reference metric or testing the same-team hypothesis.
- Ranking teams or drivers.
- Pooling race with qualifying, or pooling eras.
- Modifying Phases 4C/4D, FINAL_V2, V3 or the paper.
- Pushing or merging.
