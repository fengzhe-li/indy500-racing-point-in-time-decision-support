# V4 Phase 3 — Teammate Comparability Report

**Status:** candidate construction and comparability design only.
- No model was fitted, no coefficient estimated, and no weight assigned.
- No eligibility threshold was chosen. The time windows below are descriptive sensitivity counts.
- `beta_track` and `beta_ambient` are untouched. Teammate observations were not combined with the frozen 41 same-car transitions.

## Terminology (§3.4)

| Level | Variable | Meaning |
|---|---|---|
| A | `relationship_pair` / `relationship_pair_id` | An organisational teammate relationship: two entries of one canonical engineering team in one year (Phase 2 strict layer). |
| B | `attempt_pair_candidate` (one row in `teammate_attempt_candidates.csv`) | Any cross-car pair of qualifying attempts within one year × canonical team. `measurable_candidate` = both attempts complete over four laps and both timed. |
| C | `comparable_observation` | **Not yet defined.** It requires the Phase 4 eligibility rules. |

| level | variable | count |
|---|---|---|
| A. organisational teammate relationships (Phase 2 strict, 2018–2025) | relationship_pair | 313 |
| A′. …with ≥1 attempt-pair candidate in the joined attempt data | relationship_pair_id | 313 |
| A″. …with ≥1 measurable attempt-pair candidate | relationship_pair_id | 148 |
| B. all possible cross-car attempt-to-attempt candidates | attempt_pair_candidate | 1173 |
| B′. measurable candidates (both complete four-lap + both timed) | measurable_candidate | 341 |
| C. scientifically comparable observations | comparable_observation | NOT DEFINED — requires Phase 4 eligibility rules |

All 313 Phase 2 relationship pairs have at least one attempt-pair candidate. Only 148 have at least one *measurable* candidate: the rest lose it to missing timestamps (above all in 2018, 2022, 2023 and 2024) or to incomplete attempts.

| tier | all_candidates | both_complete | both_timed | measurable | relationship_pairs |
|---|---|---|---|---|---|
| CORE_2020_2024 | 807 | 488 | 241 | 208 | 202 |
| REGIME_EXT_R6 | 366 | 282 | 133 | 133 | 111 |

| year | A_relationship_pairs | A′_with_candidates | A″_with_measurable | B_attempt_pairs | B′_measurable |
|---|---|---|---|---|---|
| 2018 | 42 | 42 | 7 | 83 | 7 |
| 2019 | 34 | 34 | 23 | 120 | 31 |
| 2020 | 40 | 40 | 26 | 152 | 47 |
| 2021 | 44 | 44 | 41 | 113 | 96 |
| 2022 | 38 | 38 | 1 | 64 | 1 |
| 2023 | 39 | 39 | 15 | 267 | 50 |
| 2024 | 41 | 41 | 5 | 211 | 14 |
| 2025 | 35 | 35 | 30 | 163 | 95 |

## Sign / order convention

- **A** is the earlier attempt by assembled timestamp; ties go to the lower car sort key, then `attempt_id`. If either timestamp is missing, A is the lower car sort key.
- Every `delta_* = value_B − value_A`, so `delta_time_minutes ≥ 0` for timed pairs (checked: 0 negative).
- Speed, temperature, solar and wind deltas follow the same B − A convention.

## §3.5 Distributions of absolute separations — measurable attempt pairs

### Core 2020–2024

| variable | n | q000 | q010 | q025 | q050 | q075 | q090 | q095 | q100 |
|---|---|---|---|---|---|---|---|---|---|
| abs_time_min | 208 | 0 | 13.25 | 42.15 | 92.61 | 173.37 | 246.25 | 280.33 | 314.73 |
| abs_track_temp_c | 203 | 0 | 0 | 1.67 | 3.33 | 7.78 | 11.09 | 12.11 | 13.89 |
| abs_ambient_temp_c | 207 | 0 | 0.18 | 0.68 | 1.39 | 2.64 | 3.44 | 3.9 | 5.01 |
| abs_solar_wm2 | 207 | 0 | 11.59 | 41.13 | 96.71 | 170.73 | 275.61 | 348.61 | 418.53 |
| abs_wind | 207 | 0 | 0.03 | 0.13 | 0.28 | 0.7 | 1.13 | 1.28 | 1.48 |

### R6 extension (2018/2019/2025; different regime and environment basis)

| variable | n | q000 | q010 | q025 | q050 | q075 | q090 | q095 | q100 |
|---|---|---|---|---|---|---|---|---|---|
| abs_time_min | 133 | 4.25 | 13.7 | 43.58 | 107.23 | 215.33 | 278.9 | 317.43 | 388.95 |
| abs_track_temp_c | 124 | 0.12 | 0.38 | 1.15 | 3.26 | 5.59 | 8.08 | 9.42 | 15.75 |
| abs_ambient_temp_c | 124 | 0 | 0.15 | 0.48 | 1.13 | 2.12 | 2.54 | 3.09 | 4.13 |
| abs_solar_wm2 | 0 |  |  |  |  |  |  |  |  |
| abs_wind | 124 | 0 | 0.13 | 0.45 | 1.44 | 2.6 | 4.37 | 4.94 | 10.14 |

Sensitivity check: restricting to point timestamps only (dropping bounded midpoints) changes the core n from 208 to 207. See `comparability_summary.csv`, scope `POINT_TIMES_ONLY`.

**Resolution caveat:** past-safe PTSC track temperature is a step function on a 15-minute grid. Near-simultaneous pairs therefore often show exactly 0 °C track difference; that is a measurement-resolution artefact, not evidence of identical track state.

### Time separation by year (min)

| tier | year | n | q010 | q025 | q050 | q075 | q090 |
|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | 2020 | 47 | 14.8 | 34.6 | 89.2 | 151.7 | 199.4 |
| CORE_2020_2024 | 2021 | 96 | 16.5 | 42.5 | 105.4 | 182.6 | 257 |
| CORE_2020_2024 | 2022 | 1 | 0 | 0 | 0 | 0 | 0 |
| CORE_2020_2024 | 2023 | 50 | 14.1 | 50.6 | 102.3 | 200.6 | 260.6 |
| CORE_2020_2024 | 2024 | 14 | 4 | 40 | 56 | 117.5 | 148.8 |
| REGIME_EXT_R6 | 2018 | 7 | 7.3 | 11.5 | 13.8 | 25.4 | 27.7 |
| REGIME_EXT_R6 | 2019 | 31 | 9.8 | 40.9 | 86.8 | 175.1 | 232.6 |
| REGIME_EXT_R6 | 2025 | 95 | 25.8 | 56.2 | 113.3 | 233.1 | 285.9 |

### Environmental separation by year

| tier | year | variable | n | q025 | q050 | q075 | q090 |
|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | 2020 | abs_track_temp_c | 47 | 2.22 | 5 | 8.61 | 11.11 |
| CORE_2020_2024 | 2020 | abs_ambient_temp_c | 47 | 0.94 | 1.97 | 2.98 | 4 |
| CORE_2020_2024 | 2021 | abs_track_temp_c | 96 | 1.53 | 3.33 | 8.33 | 11.11 |
| CORE_2020_2024 | 2021 | abs_ambient_temp_c | 96 | 0.68 | 1.27 | 2.65 | 3.45 |
| CORE_2020_2024 | 2022 | abs_track_temp_c | 0 |  |  |  |  |
| CORE_2020_2024 | 2022 | abs_ambient_temp_c | 0 |  |  |  |  |
| CORE_2020_2024 | 2023 | abs_track_temp_c | 50 | 2.27 | 4.26 | 7.59 | 10.6 |
| CORE_2020_2024 | 2023 | abs_ambient_temp_c | 50 | 0.55 | 1.05 | 2.17 | 2.83 |
| CORE_2020_2024 | 2024 | abs_track_temp_c | 10 | 0.14 | 1.11 | 1.67 | 2.78 |
| CORE_2020_2024 | 2024 | abs_ambient_temp_c | 14 | 0.92 | 1.46 | 2.69 | 3.15 |
| REGIME_EXT_R6 | 2018 | abs_track_temp_c | 0 |  |  |  |  |
| REGIME_EXT_R6 | 2018 | abs_ambient_temp_c | 0 |  |  |  |  |
| REGIME_EXT_R6 | 2019 | abs_track_temp_c | 31 | 1.89 | 5.15 | 8.16 | 13.82 |
| REGIME_EXT_R6 | 2019 | abs_ambient_temp_c | 31 | 0.37 | 1.22 | 2.06 | 3.39 |
| REGIME_EXT_R6 | 2025 | abs_track_temp_c | 93 | 0.95 | 2.63 | 4.85 | 6.81 |
| REGIME_EXT_R6 | 2025 | abs_ambient_temp_c | 93 | 0.51 | 1.11 | 2.19 | 2.49 |

## Descriptive window counts (no threshold selected)

| max_time_separation_min | CORE: attempt_pair_candidates | CORE: distinct_attempts_involved | CORE: distinct_relationship_pairs | CORE: distinct_team_years | R6: attempt_pair_candidates | R6: distinct_attempts_involved | R6: distinct_relationship_pairs | R6: distinct_team_years |
|---|---|---|---|---|---|---|---|---|
| 5 | 10 | 17 | 10 | 6 | 5 | 10 | 5 | 5 |
| 10 | 18 | 33 | 17 | 12 | 11 | 21 | 11 | 9 |
| 15 | 25 | 45 | 23 | 14 | 17 | 30 | 16 | 12 |
| 20 | 31 | 52 | 29 | 15 | 17 | 30 | 16 | 12 |
| 30 | 42 | 65 | 38 | 19 | 25 | 40 | 23 | 14 |
| 45 | 57 | 77 | 51 | 20 | 37 | 51 | 33 | 15 |
| 60 | 76 | 91 | 62 | 23 | 45 | 57 | 37 | 16 |
| 90 | 103 | 98 | 77 | 24 | 63 | 69 | 47 | 19 |
| 120 | 124 | 105 | 84 | 26 | 74 | 77 | 53 | 20 |

### By year (measurable attempt-pair candidates)

| tier | year | ≤5 | ≤10 | ≤15 | ≤20 | ≤30 | ≤45 | ≤60 | ≤90 | ≤120 |
|---|---|---|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | 2020 | 1 | 4 | 5 | 7 | 11 | 15 | 19 | 25 | 33 |
| CORE_2020_2024 | 2021 | 5 | 7 | 10 | 14 | 18 | 25 | 33 | 45 | 53 |
| CORE_2020_2024 | 2022 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CORE_2020_2024 | 2023 | 0 | 3 | 6 | 6 | 9 | 12 | 15 | 23 | 27 |
| CORE_2020_2024 | 2024 | 3 | 3 | 3 | 3 | 3 | 4 | 8 | 9 | 10 |
| REGIME_EXT_R6 | 2018 | 1 | 2 | 4 | 4 | 7 | 7 | 7 | 7 | 7 |
| REGIME_EXT_R6 | 2019 | 1 | 4 | 6 | 6 | 6 | 10 | 12 | 17 | 19 |
| REGIME_EXT_R6 | 2025 | 3 | 5 | 7 | 7 | 12 | 20 | 26 | 39 | 48 |

### By canonical team

| tier | canonical_engineering_team | ≤5 | ≤10 | ≤15 | ≤20 | ≤30 | ≤45 | ≤60 | ≤90 | ≤120 |
|---|---|---|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | AJ_FOYT | 0 | 1 | 1 | 1 | 2 | 2 | 4 | 7 | 7 |
| CORE_2020_2024 | ANDRETTI | 3 | 5 | 9 | 11 | 13 | 17 | 22 | 29 | 36 |
| CORE_2020_2024 | ARROW_MCLAREN_SPM | 5 | 7 | 7 | 10 | 14 | 18 | 20 | 22 | 24 |
| CORE_2020_2024 | CHIP_GANASSI_RACING | 0 | 2 | 4 | 5 | 5 | 7 | 13 | 18 | 24 |
| CORE_2020_2024 | DALE_COYNE_RACING | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 |
| CORE_2020_2024 | DREYER_REINBOLD_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| CORE_2020_2024 | ED_CARPENTER_RACING | 0 | 0 | 1 | 1 | 3 | 5 | 5 | 10 | 12 |
| CORE_2020_2024 | MEYER_SHANK_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| CORE_2020_2024 | RAHAL_LETTERMAN_LANIGAN | 1 | 1 | 1 | 1 | 2 | 2 | 3 | 4 | 4 |
| CORE_2020_2024 | TEAM_PENSKE | 0 | 1 | 1 | 1 | 2 | 5 | 7 | 11 | 13 |
| REGIME_EXT_R6 | AJ_FOYT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 |
| REGIME_EXT_R6 | ANDRETTI | 1 | 3 | 6 | 6 | 8 | 10 | 11 | 13 | 18 |
| REGIME_EXT_R6 | ARROW_MCLAREN_SPM | 1 | 2 | 2 | 2 | 3 | 6 | 7 | 10 | 10 |
| REGIME_EXT_R6 | CARLIN | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 2 |
| REGIME_EXT_R6 | CHIP_GANASSI_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| REGIME_EXT_R6 | DALE_COYNE_RACING | 0 | 1 | 1 | 1 | 2 | 4 | 5 | 5 | 5 |
| REGIME_EXT_R6 | DREYER_REINBOLD_RACING | 1 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| REGIME_EXT_R6 | ED_CARPENTER_RACING | 0 | 1 | 1 | 1 | 3 | 4 | 5 | 10 | 11 |
| REGIME_EXT_R6 | JUNCOS_HOLLINGER_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 3 |
| REGIME_EXT_R6 | PREMA_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| REGIME_EXT_R6 | RAHAL_LETTERMAN_LANIGAN | 0 | 0 | 1 | 1 | 3 | 4 | 6 | 9 | 10 |
| REGIME_EXT_R6 | TEAM_PENSKE | 1 | 1 | 1 | 1 | 1 | 4 | 6 | 8 | 9 |

## §3.6 Nearest-teammate structure (non-duplicative view)

For each complete, timed attempt in the primary layer, `nearest_teammate_candidates.csv` records:
- the nearest attempt of each teammate car;
- a flag marking the overall nearest one.

| tier | attempts_with_a_timed_teammate | distinct_nearest_attempt_pairs | mutual_nearest_pairs |
|---|---|---|---|
| CORE_2020_2024 | 115 | 73 | 42 |
| REGIME_EXT_R6 | 93 | 61 | 32 |

### Overall nearest-teammate separations

| variable | n | q000 | q010 | q025 | q050 | q075 | q090 | q095 | q100 |
|---|---|---|---|---|---|---|---|---|---|
| abs_time_min | 115 | 0 | 5 | 9.58 | 24.98 | 51.58 | 108.33 | 167.92 | 254.92 |
| abs_track_temp_c | 111 | 0 | 0 | 0.07 | 1.62 | 3.33 | 6.67 | 8.89 | 12.22 |
| abs_ambient_temp_c | 113 | 0 | 0.03 | 0.2 | 0.63 | 1.39 | 2.53 | 2.79 | 3.74 |
| abs_solar_wm2 | 113 | 0 | 5.5 | 17.72 | 43.4 | 102.39 | 274.76 | 345.27 | 389.24 |
| abs_wind | 113 | 0 | 0.02 | 0.04 | 0.15 | 0.3 | 0.72 | 0.91 | 1.04 |

| variable | n | q000 | q010 | q025 | q050 | q075 | q090 | q095 | q100 |
|---|---|---|---|---|---|---|---|---|---|
| abs_time_min | 93 | 4.25 | 4.95 | 12.92 | 42.5 | 107.23 | 146.83 | 219.2 | 328.67 |
| abs_track_temp_c | 86 | 0.12 | 0.26 | 0.38 | 1.73 | 4.67 | 6.42 | 8.95 | 13.82 |
| abs_ambient_temp_c | 86 | 0 | 0.02 | 0.18 | 0.56 | 1.16 | 1.98 | 2.23 | 3.39 |
| abs_solar_wm2 | 0 |  |  |  |  |  |  |  |  |
| abs_wind | 86 | 0 | 0.28 | 0.43 | 1.2 | 2.36 | 3.95 | 4.63 | 10.14 |

### Attempts whose overall nearest teammate attempt lies within each window

| tier | ≤5 | ≤10 | ≤15 | ≤20 | ≤30 | ≤45 | ≤60 | ≤90 | ≤120 |
|---|---|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | 17 | 33 | 45 | 52 | 65 | 77 | 91 | 98 | 105 |
| REGIME_EXT_R6 | 10 | 21 | 30 | 30 | 40 | 51 | 57 | 69 | 77 |

Distinct nearest attempt pairs within each window (de-duplicated when two attempts are each other's nearest):

| tier | ≤5 | ≤10 | ≤15 | ≤20 | ≤30 | ≤45 | ≤60 | ≤90 | ≤120 |
|---|---|---|---|---|---|---|---|---|---|
| CORE_2020_2024 | 9 | 17 | 23 | 27 | 35 | 43 | 53 | 59 | 64 |
| REGIME_EXT_R6 | 5 | 11 | 16 | 16 | 22 | 30 | 35 | 43 | 48 |

These are not yet controls.

## §3.7 Same-session / track-state structure (measurable pairs)

| tier | session_state | pairs |
|---|---|---|
| CORE_2020_2024 | SAME_SESSION_NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION | 207 |
| CORE_2020_2024 | SAME_SESSION_SAME_KNOWN_SEGMENT | 1 |
| REGIME_EXT_R6 | SAME_SESSION_NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION | 133 |

- All measurable pairs are within one Day 1 `session_id`.
- **2022 is the only year with a reconstructed interruption structure,** but only 1 measurable 2022 pair exists (same known segment).
- For all other years, "no interruption record" is a limitation of the reconstruction, not a verified uninterrupted track state.
- 15 core 2020 measurable pairs span the 7m15s recorder data gap. That gap is a data note, not a track interruption.

## §3.8 What the teammate layer does and does not control

- **Controls** (approximately): the team's vehicle platform, engineering group, engine supplier and aero package.
- **Does not control:** setup, driver, tyre preparation/state, car-specific condition, operational execution or run plan.

Raw teammate speed differences therefore mix environment with these car/driver-specific effects. They are **not** environmental effects. The quantities above describe only how contemporaneous the cross-car evidence is.

## §3.9 Overlap with frozen same-car evidence (frozen set not modified)

The frozen 41 transitions come from years [2020, 2021, 2023, 2024].

| year | frozen_transitions | teams | transitions_in_team_years_with_measurable_teammate_pairs | transitions_whose_car_has_measurable_teammate_pairs |
|---|---|---|---|---|
| 2020 | 11 | 8 | 8 | 8 |
| 2021 | 15 | 8 | 14 | 14 |
| 2023 | 13 | 5 | 12 | 12 |
| 2024 | 2 | 2 | 1 | 1 |

| year | canonical_engineering_team | frozen_transitions | primary_layer | team_year_measurable_pairs |
|---|---|---|---|---|
| 2020 | ANDRETTI | 1 | True | 14 |
| 2020 | ARROW_MCLAREN_SPM | 1 | True | 5 |
| 2020 | CARLIN | 1 | True | 0 |
| 2020 | CHIP_GANASSI_RACING | 3 | True | 11 |
| 2020 | DRAGONSPEED | 1 | True | 0 |
| 2020 | ED_CARPENTER_RACING | 2 | True | 8 |
| 2020 | MEYER_SHANK_RACING | 1 | True | 0 |
| 2020 | TEAM_PENSKE | 1 | True | 5 |
| 2021 | AJ_FOYT | 1 | True | 9 |
| 2021 | ANDRETTI | 5 | True | 48 |
| 2021 | ARROW_MCLAREN_SPM | 2 | True | 8 |
| 2021 | DALE_COYNE_RACING | 1 | True | 2 |
| 2021 | ED_CARPENTER_RACING | 2 | True | 8 |
| 2021 | MEYER_SHANK_RACING | 1 | True | 2 |
| 2021 | PARETTA_AUTOSPORT | 1 | False | 0 |
| 2021 | TEAM_PENSKE | 2 | True | 13 |
| 2023 | ANDRETTI | 3 | True | 6 |
| 2023 | ARROW_MCLAREN_SPM | 3 | True | 17 |
| 2023 | CHIP_GANASSI_RACING | 4 | True | 23 |
| 2023 | ED_CARPENTER_RACING | 2 | True | 3 |
| 2023 | JUNCOS_HOLLINGER_RACING | 1 | True | 0 |
| 2024 | ARROW_MCLAREN_SPM | 1 | True | 12 |
| 2024 | ED_CARPENTER_RACING | 1 | True | 0 |

Frozen endpoints with an overall-nearest timed teammate attempt:

| endpoints | with_timed_teammate | median_min |
|---|---|---|
| before | 35 | 23.3 |
| after | 35 | 37.5 |
| both endpoints | 35 |  |

| endpoint | ≤5 | ≤10 | ≤15 | ≤20 | ≤30 | ≤45 | ≤60 | ≤90 | ≤120 |
|---|---|---|---|---|---|---|---|---|---|
| before | 4 | 9 | 15 | 17 | 22 | 26 | 32 | 32 | 34 |
| after | 1 | 5 | 13 | 17 | 17 | 19 | 22 | 25 | 27 |

Per-transition detail: `frozen_same_car_overlap.csv`.

## Assessment for Phase 4 (§3.11 items 10–15)

**Strongest years for contemporaneous teammate evidence**
- Core: **2021** (18 pairs ≤30 min; 33 ≤60 min), then **2020** and **2023**.
- R6: **2025** (26 ≤60 min).

**Weakest years**
- **2022:** 1 measurable pair and no environment. The core data cannot support the teammate layer this year.
- **2024:** 14 measurable pairs; only 14 timed complete attempts.
- **2018:** 7 measurable pairs; no PTSC.

**Strongest teams**
- Core, by measurable pairs ≤60 min: **ANDRETTI** (22), **ARROW_MCLAREN_SPM** (20), **CHIP_GANASSI_RACING** (13), **TEAM_PENSKE** (7).
- The other core teams contribute 0–5 pairs within 60 min each.

**Missing-data limitations**
- Only 138 of 260 complete core attempts are timed. Timing, not team structure, limits the teammate layer.
- Session interruptions are reconstructed only for 2022.
- Environment bases differ across tiers, and 35 core measurable pairs mix bases.
- Past-safe track temperature is quantised at 15 minutes.
- R6 wind units are unverified. There is no solar data outside the core.

**Sufficiency (descriptive judgement, not a threshold decision)**
- Enough contemporaneous core evidence exists to design a formal teammate comparison: 42 measurable pairs within 30 min and 76 within 60 min. The ≤60-min pairs span 62 relationship pairs and 23 team-years.
- That is the same order of magnitude as the 41-transition same-car core.
- The evidence is concentrated in 2020, 2021 and 2023 and in four teams.
- Multiple attempt pairs share the same relationship pair and attempts. Any Phase 4 design must treat these as dependent, for example by clustering on relationship pair and attempt or by using the nearest-teammate view.

## Files

`team_attempt_join.csv`, `teammate_attempt_candidates.csv`, `nearest_teammate_candidates.csv`, `comparability_summary.csv`, `comparability_window_counts.csv`, `comparability_by_year.csv`, `comparability_by_team.csv`, `frozen_same_car_overlap.csv`, `phase3_data_quality_report.md`, `phase3_comparability_report.md`, `figures/fig1…fig6*.png`.
