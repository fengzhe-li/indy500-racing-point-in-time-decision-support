# V4 Phase 4H — Performance-Lap / Run-State Validity Report

**Pre-specification:** `phase4h_performance_validity_spec.md`, committed as `a56b4dd` before any classification, calibration or population audit. Its rules were applied without change.

**Prior results:** Phase 4F (`81455f3`, CASE **D**) and Phase 4G (`d903148`, CASE **A**) are unchanged and verified against `phase4h_freeze_record.csv`.

**Sources:**
- Lap records: **Timing71 archived recordings of the INDYCAR live timing feed (third-party)**.
- Official INDYCAR session details (2023–2024 only) anchor the official QualLap1–4 values.

**Scope:** a measurement-validity audit. No hierarchy was recomputed.

## Headline

**Measurement-validity CASE D: practice is unsuitable for a performance hierarchy.** Under the committed rules:
- The qualifying-calibrated classifier passes its out-of-year calibration: 91.7% of 2024 official qualifying laps are retained.
- But only **11.6%** of at-speed 2023–24 practice laps (non-D) fall inside the qualifying envelope (class A or B).
- **74.6%** are run-state ambiguous and 13.8% are input-insufficient.

**Gate:** STOP practice-based hierarchy. Phase 4F and 4G stand as evidence that raw practice observations are not clean performance measurements. Phase 4I is not run.

## 1. Qualifying performance reference (4H.2)

**Official attempts matched to Timing71:** 67 of 96 official QualLap1–4 records (2023–2024) matched an exact run of 4 consecutive Timing71 laps (`OFFICIAL_ANCHORED`). The unmatched records correspond to capture gaps.

| year | attempts | laps | speed_min | speed_median | speed_max | within_range_median | within_range_max | dev_fastest_p90 | share_monotone_decline |
|---|---|---|---|---|---|---|---|---|---|
| 2023 | 43 | 172 | 228.751 | 232.868 | 235.131 | 0.006 | 0.013 | 0.007 | 0.907 |
| 2024 | 24 | 96 | 227.854 | 232.333 | 234.526 | 0.004 | 0.008 | 0.005 | 0.833 |

**Structure of the official attempts:**
- Laps decline almost monotonically within an attempt ("---" pattern in most attempts).
- The within-attempt relative range is tiny (median 0.4–0.6%; max 1.3%).

**Timing71 qualifying attempts by length** (a maximal timestamp-coherent run):

| year | session_key | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 2023 | 2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206 | 4 | 3 | 2 | 22 | 0 |
| 2023 | 6202 | 49 | 8 | 8 | 49 | 0 |
| 2024 | 6382 | 36 | 3 | 12 | 33 | 0 |
| 2024 | 6386 | 3 | 0 | 1 | 10 | 0 |
| 2025 | 6656 | 10 | 5 | 12 | 9 | 49 |
| 2025 | 6660 | 14 | 2 | 2 | 3 | 5 |

**Structural findings:**
- **2023–2024:** Timing71 qualifying captures record only timed laps. Warm-up laps are absent. Of the 92 one-lap "attempts", 38% re-post the previous lap time at the start of the next run (a feed artifact); the rest are isolated captured laps or partial captures.
- **2025:** the captures record a **yellow-flag warm-up lap** before each run, so runs appear as 5 laps. The pre-specified exactly-4-lap attempt definition therefore captures only fragments in 2025, and C2 fails mechanically.
- **2025 post-hoc description** (not a criterion): on the green laps 2–5 of these runs, the classifier retains 75.9% as A. The yellow warm-up laps are all D.
- **2025 has no official anchor**; its qualifying reference is inferred only.

## 2. Raw practice speed distribution (4H.4)

| layer | year | n_laps | speed_min | speed_p5 | speed_p25 | speed_p50 | speed_p75 | speed_p95 | speed_max | def_session_best_p50 | def_session_best_p90 | def_stint_best_p50 | def_stint_best_p90 | within_stint_range_median | share_def_session_best_gt_2pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ALL_RECORDS | 2025 | 9297 | 0.516 | 11.689 | 158.746 | 215.473 | 218.636 | 223.706 | 234.176 | 0.036 | 0.893 | 0.022 | 0.848 | 190.776 | 0.729 |
| ALL_RECORDS | 2023 | 12365 | 0.707 | 12.21 | 165.585 | 218.135 | 221.029 | 226.28 | 235.692 | 0.036 | 0.896 | 0.02 | 0.634 | 186.289 | 0.774 |
| ALL_RECORDS | 2024 | 7903 | 0.896 | 15.921 | 209.484 | 217.713 | 220.469 | 223.797 | 233.879 | 0.032 | 0.504 | 0.02 | 0.359 | 170.29 | 0.726 |
| NON_D | 2025 | 6417 | 200.068 | 209.077 | 214.809 | 217.345 | 219.599 | 226.552 | 234.176 | 0.025 | 0.055 | 0.015 | 0.047 | 7.732 | 0.623 |
| NON_D | 2023 | 8621 | 200.012 | 211.394 | 217.428 | 219.713 | 221.89 | 229.184 | 235.692 | 0.028 | 0.055 | 0.014 | 0.044 | 7.905 | 0.692 |
| NON_D | 2024 | 5925 | 200.444 | 211.593 | 216.525 | 219.038 | 221.101 | 224.152 | 233.748 | 0.026 | 0.05 | 0.017 | 0.042 | 8.585 | 0.647 |

**By category** (non-D laps):

| role | category | n_laps | speed_p10 | speed_p50 | speed_p90 | def_session_best_p50 | def_stint_best_p50 | within_stint_range_median | within_car_iqr_median |
|---|---|---|---|---|---|---|---|---|---|
| ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | CARB_DAY | 1414 | 210.622 | 216.745 | 220.818 | 0.029 | 0.02 | 8.173 | 4.83 |
| ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | FAST_FRIDAY | 298 | 213.008 | 228.522 | 231.295 | 0.01 | 0.003 | 13.64 | 5.267 |
| ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | POST_QUALIFYING_PRACTICE | 1545 | 210.06 | 217.122 | 221.455 | 0.031 | 0.021 | 9.764 | 5.519 |
| ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | PRACTICE | 3000 | 212.257 | 217.341 | 220.998 | 0.023 | 0.011 | 5.239 | 3.828 |
| ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | QUALIFYING_WEEKEND_PRACTICE | 160 | 217.037 | 230.741 | 232.813 | 0.003 | 0.002 | 14.031 | 3.791 |
| PRIMARY | CARB_DAY | 3875 | 214.22 | 218.888 | 222.635 | 0.026 | 0.018 | 8.439 | 4.037 |
| PRIMARY | FAST_FRIDAY | 663 | 215.306 | 230.883 | 232.907 | 0.006 | 0.003 | 14.19 | 3.525 |
| PRIMARY | POST_QUALIFYING_PRACTICE | 3347 | 212.705 | 218.676 | 222.519 | 0.028 | 0.018 | 9.237 | 4.612 |
| PRIMARY | PRACTICE | 6563 | 214.395 | 219.792 | 223.54 | 0.028 | 0.013 | 6.749 | 3.88 |
| PRIMARY | QUALIFYING_WEEKEND_PRACTICE | 98 | 220.806 | 233.028 | 234.849 | 0.003 | 0.002 | 11.651 | 0.46 |

**Evidence for multiple run states in practice** (descriptive, not causal):
- **All records:** heavily multimodal. Pit/out/in-laps and slow laps pull the p25 down to about 160–210 mph.
- **Non-D at-speed laps, deficit to the car's session best:** the median is 2.5–2.8% (about 6 mph).
  - 65–69% of at-speed laps are more than 2% below the car's own session best.
  - In official qualifying, the deficit to the attempt's fastest lap has a p90 of about 0.6%.
- **Within one stint:** the at-speed range is typically about 8 mph (median within-stint range of non-D laps).
- **Stint position:** the first lap is the pit-exit lap; lap 2 and the penultimate lap are slower on average (fig05).

## 3. Classifier and calibration (4H.5–4H.7)

**Thresholds** (2023 official attempts, n = 43):
- T_steady: 95th pct 0.009, max 0.013 (relative range of a 4-lap window);
- T_level: 95th pct 0.002, max 0.002 (window median vs the car's best steady window).

| reference_group | in_sample | attempts | laps | retention_A | retention_AB | share_C | share_D | share_E | attempt_coherence_same_class | within_attempt_rel_range_median | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2023_INFERRED_4LAP | False | 28 | 112 | 0.536 | 0.607 | 0.25 | 0.036 | 0.107 | 0.857 | 0.006 |  |
| 2023_OFFICIAL_ANCHORED | True | 43 | 172 | 0.744 | 0.86 | 0 | 0.035 | 0.105 | 0.86 | 0.006 |  |
| 2024_INFERRED_4LAP | False | 19 | 76 | 0.632 | 0.632 | 0.211 | 0.079 | 0.079 | 0.895 | 0.004 |  |
| 2024_OFFICIAL_ANCHORED | False | 24 | 96 | 0.917 | 0.917 | 0 | 0.021 | 0.062 | 0.917 | 0.004 |  |
| 2025_INFERRED_4LAP | False | 12 | 48 | 0.083 | 0.083 | 0 | 0.229 | 0.688 | 0.083 | 0.054 |  |
| QUALIFYING_KNOWN_NON_PERFORMANCE_LAPS |  | 0 | 0 |  |  |  |  |  |  |  | NOT AVAILABLE: Timing71 qualifying captures record only timed laps (no warm-up / cool-down laps) |
| PRACTICE_PROXY_BUILD_LAP_pos2_pitbounded|2023_2024_PRIMARY |  |  | 1926 | 0.029 | 0.043 | 0.593 |  | 0.364 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_PROXY_BUILD_LAP_pos2_pitbounded|2025_SECONDARY |  |  | 967 | 0.042 | 0.056 | 0.566 |  | 0.378 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_PROXY_PRE_INLAP_penultimate|2023_2024_PRIMARY |  |  | 1847 | 0.061 | 0.081 | 0.557 |  | 0.363 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_PROXY_PRE_INLAP_penultimate|2025_SECONDARY |  |  | 903 | 0.086 | 0.112 | 0.514 |  | 0.374 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_PROXY_RESTART_prev_nongreen|2023_2024_PRIMARY |  |  | 336 | 0.033 | 0.045 | 0.595 |  | 0.36 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_PROXY_RESTART_prev_nongreen|2025_SECONDARY |  |  | 179 | 0.028 | 0.034 | 0.603 |  | 0.363 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_REFERENCE_interior_pos3plus|2023_2024_PRIMARY |  |  | 10804 | 0.092 | 0.134 | 0.801 |  | 0.065 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| PRACTICE_REFERENCE_interior_pos3plus|2025_SECONDARY |  |  | 4604 | 0.125 | 0.173 | 0.769 |  | 0.058 |  |  | inferred proxy negative; descriptive only (not a criterion) |
| 2025_WARMUP_PLUS_4|timed laps 2-5 (post-hoc descriptive; not a criterion) |  | 54 | 216 | 0.759 | 0.815 | 0.185 | 0 | 0 |  |  | 2025 Timing71 qualifying captures include a yellow-flag warm-up lap before each timed run; the pre-specified 4-lap attempt definition does not capture these runs |
| 2025_WARMUP_PLUS_4|warm-up lap 1 = observed non-performance qualifying lap (post-hoc descriptive) |  | 54 | 54 | 0 | 0 | 0 | 1 | 0 |  |  | 2025 Timing71 qualifying captures include a yellow-flag warm-up lap before each timed run; the pre-specified 4-lap attempt definition does not capture these runs |

**Calibration criteria:**
- **C1 (2024 official, out-of-year):** A 91.7%, A∪B 91.7% → **PASS**.
- **C2 (2025 inferred 4-lap):** A∪B 8.3% → **FAIL**. The cause is structural (§1).

**Negative references:**
- **Qualifying:** known non-performance laps are **not recorded** in 2023–24 captures, so no qualifying negative reference exists there. In 2025, the observed yellow warm-up laps are all rejected (D), but only through the flag.
- **Practice proxies:** build laps (position 2), pre-in-laps and restart laps are classified A in only 3–9% of cases, vs 9–13% for interior laps.

**Classifier rule audit:**

| item | value |
|---|---|
| n_2023_official_attempts | 43 |
| n_2024_official_attempts | 24 |
| T_steady_95 | 0.009401666311997741 |
| T_steady_100 | 0.01334916816180075 |
| T_level_95 | 0.001673525628209048 |
| T_level_100 | 0.001987874348791996 |
| threshold_source | 2023 OFFICIAL_ANCHORED qualifying attempts only; numpy percentile (linear) |
| official attempts in records (2023-2024) | 96 |
| official attempts matched to Timing71 4-lap runs | 67 |
| reference sufficiency (>=20 2023, >=10 2024) | True |
| 2023_2024_PRIMARY: laps | 20268 |
| 2023_2024_PRIMARY: d1 non-green | 990 |
| 2023_2024_PRIMARY: d2 observed out-lap (pit-exit matched) | 2963 |
| 2023_2024_PRIMARY: d3 observed in-lap (pit-entry matched) | 2961 |
| 2023_2024_PRIMARY: d4 outside 37-45 s band | 5194 |
| 2023_2024_PRIMARY: D total | 5722 |
| 2023_2024_PRIMARY: first laps of UNMATCHED-start stints (inferred out-lap; not D by rule) | 82 |
| 2023_2024_PRIMARY: of those, inside 37-45 s band | 17 |
| 2023_2024_PRIMARY: E (no valid 4-lap window) | 2007 |
| 2023_2024_PRIMARY: windows | 8234 |
| 2025_SECONDARY: laps | 9297 |
| 2025_SECONDARY: d1 non-green | 508 |
| 2025_SECONDARY: d2 observed out-lap (pit-exit matched) | 1436 |
| 2025_SECONDARY: d3 observed in-lap (pit-entry matched) | 1424 |
| 2025_SECONDARY: d4 outside 37-45 s band | 2675 |
| 2025_SECONDARY: D total | 2880 |
| 2025_SECONDARY: first laps of UNMATCHED-start stints (inferred out-lap; not D by rule) | 41 |
| 2025_SECONDARY: of those, inside 37-45 s band | 4 |
| 2025_SECONDARY: E (no valid 4-lap window) | 904 |
| 2025_SECONDARY: windows | 3563 |
| stint start matched to pit-exit message (practice stints) | 0.7111875560873467 |
| stint end matched to pit-entry message (practice stints with endTime) | 0.7545247148288974 |
| qualifying stints start matched to pit-exit message | 0.0 |
| classification SHA-256 (practice) | 29bc8da24499b72091656d2efed3f37d997bf5e7ab7f4014416d7b66aa3fdd14 |
| classification deterministic on re-run | True |
| inputs used by classifier | flag, stint position/provenance, pit-message match, laptime, timestamp coherence (car's own laps only) |
| 2023_2024_PRIMARY: evaluable laps in >=1 steady window (r_w <= T_steady_95), any level | 0.205359279049366 |
| 2023_2024_PRIMARY: evaluable laps in >=1 steady window (r_w <= T_steady_100), any level | 0.3331206635297871 |
| 2023_2024_PRIMARY: evaluable laps steady(95) but failing level(95) -> not A | 0.11189090039078077 |
| 2023_2024_PRIMARY: window r_w median | 0.024439403361601934 |
| 2023_2024_PRIMARY: window level deficit l_100 median (steady windows) | 0.00685577826628897 |
| 2025_SECONDARY: evaluable laps in >=1 steady window (r_w <= T_steady_95), any level | 0.21694177398875386 |
| 2025_SECONDARY: evaluable laps in >=1 steady window (r_w <= T_steady_100), any level | 0.3275893343007437 |
| 2025_SECONDARY: evaluable laps steady(95) but failing level(95) -> not A | 0.0908761110103392 |
| 2025_SECONDARY: window r_w median | 0.026375657614104916 |
| 2025_SECONDARY: window level deficit l_100 median (steady windows) | 0.004424544168080136 |

## 4. Practice run-state composition (4H.8)

| level | yr_group | year | category | lap_position | n_laps | n_nonD | share_all_D | share_nonD_A | share_nonD_B | share_nonD_C | share_nonD_E | share_nonD_AB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| YEAR | 2023_2024_PRIMARY | 2023 |  |  | 12365 | 8621 | 0.303 | 0.08 | 0.033 | 0.728 | 0.159 | 0.113 |
| YEAR | 2023_2024_PRIMARY | 2024 |  |  | 7903 | 5925 | 0.25 | 0.082 | 0.039 | 0.773 | 0.107 | 0.12 |
| YEAR | 2025_SECONDARY | 2025 |  |  | 9297 | 6417 | 0.31 | 0.108 | 0.04 | 0.711 | 0.141 | 0.148 |
| CATEGORY | 2023_2024_PRIMARY |  | CARB_DAY |  | 5091 | 3875 | 0.239 | 0.071 | 0.031 | 0.817 | 0.082 | 0.101 |
| CATEGORY | 2023_2024_PRIMARY |  | FAST_FRIDAY |  | 1352 | 663 | 0.51 | 0.205 | 0.042 | 0.495 | 0.258 | 0.247 |
| CATEGORY | 2023_2024_PRIMARY |  | POST_QUALIFYING_PRACTICE |  | 4377 | 3347 | 0.235 | 0.077 | 0.037 | 0.76 | 0.126 | 0.114 |
| CATEGORY | 2023_2024_PRIMARY |  | PRACTICE |  | 9251 | 6563 | 0.291 | 0.073 | 0.036 | 0.73 | 0.161 | 0.109 |
| CATEGORY | 2023_2024_PRIMARY |  | QUALIFYING_WEEKEND_PRACTICE |  | 197 | 98 | 0.503 | 0.245 | 0.082 | 0.276 | 0.398 | 0.327 |
| CATEGORY | 2025_SECONDARY |  | CARB_DAY |  | 1988 | 1414 | 0.289 | 0.087 | 0.035 | 0.785 | 0.093 | 0.122 |
| CATEGORY | 2025_SECONDARY |  | FAST_FRIDAY |  | 618 | 298 | 0.518 | 0.295 | 0.027 | 0.433 | 0.245 | 0.322 |
| CATEGORY | 2025_SECONDARY |  | POST_QUALIFYING_PRACTICE |  | 2076 | 1545 | 0.256 | 0.068 | 0.043 | 0.806 | 0.083 | 0.111 |
| CATEGORY | 2025_SECONDARY |  | PRACTICE |  | 4295 | 3000 | 0.302 | 0.114 | 0.043 | 0.672 | 0.171 | 0.157 |
| CATEGORY | 2025_SECONDARY |  | QUALIFYING_WEEKEND_PRACTICE |  | 320 | 160 | 0.5 | 0.225 | 0.025 | 0.375 | 0.375 | 0.25 |
| STINT_POSITION | 2023_2024_PRIMARY |  |  | 1 (first) | 3045 | 17 | 0.994 | 0 | 0 | 0.118 | 0.882 | 0 |
| STINT_POSITION | 2023_2024_PRIMARY |  |  | 2 | 2277 | 1948 | 0.144 | 0.028 | 0.014 | 0.59 | 0.368 | 0.042 |
| STINT_POSITION | 2023_2024_PRIMARY |  |  | 3+ interior | 11026 | 10804 | 0.02 | 0.092 | 0.041 | 0.801 | 0.065 | 0.134 |
| STINT_POSITION | 2023_2024_PRIMARY |  |  | last | 2024 | 20 | 0.99 | 0.1 | 0 | 0.65 | 0.25 | 0.1 |
| STINT_POSITION | 2023_2024_PRIMARY |  |  | penultimate | 1896 | 1757 | 0.073 | 0.066 | 0.022 | 0.591 | 0.321 | 0.088 |
| STINT_POSITION | 2025_SECONDARY |  |  | 1 (first) | 1477 | 4 | 0.997 | 0 | 0 | 0 | 1 | 0 |
| STINT_POSITION | 2025_SECONDARY |  |  | 2 | 1162 | 973 | 0.163 | 0.042 | 0.013 | 0.564 | 0.38 | 0.055 |
| STINT_POSITION | 2025_SECONDARY |  |  | 3+ interior | 4728 | 4604 | 0.026 | 0.125 | 0.048 | 0.769 | 0.058 | 0.173 |
| STINT_POSITION | 2025_SECONDARY |  |  | last | 1017 | 11 | 0.989 | 0.091 | 0 | 0.364 | 0.545 | 0.091 |
| STINT_POSITION | 2025_SECONDARY |  |  | penultimate | 913 | 825 | 0.096 | 0.096 | 0.028 | 0.567 | 0.309 | 0.124 |

**Per session:**

| yr_group | session_key | category | n_laps | share_all_D | share_nonD_A | share_nonD_B | share_nonD_C | share_nonD_E | share_nonD_AB |
|---|---|---|---|---|---|---|---|---|---|
| 2023_2024_PRIMARY | 6198 | PRACTICE | 3595 | 0.292 | 0.065 | 0.033 | 0.699 | 0.203 | 0.098 |
| 2023_2024_PRIMARY | 6199 | PRACTICE | 3284 | 0.292 | 0.075 | 0.025 | 0.774 | 0.126 | 0.1 |
| 2023_2024_PRIMARY | 6200 | FAST_FRIDAY | 1051 | 0.518 | 0.174 | 0.047 | 0.533 | 0.247 | 0.221 |
| 2023_2024_PRIMARY | 6203 | QUALIFYING_WEEKEND_PRACTICE | 197 | 0.503 | 0.245 | 0.082 | 0.276 | 0.398 | 0.327 |
| 2023_2024_PRIMARY | 6207 | POST_QUALIFYING_PRACTICE | 1875 | 0.259 | 0.073 | 0.034 | 0.738 | 0.156 | 0.107 |
| 2023_2024_PRIMARY | 6208 | CARB_DAY | 2363 | 0.256 | 0.077 | 0.034 | 0.783 | 0.106 | 0.111 |
| 2023_2024_PRIMARY | 6375 | PRACTICE | 238 | 0.454 | 0.123 | 0.131 | 0.415 | 0.331 | 0.254 |
| 2023_2024_PRIMARY | 6378 | PRACTICE | 2134 | 0.267 | 0.081 | 0.046 | 0.742 | 0.131 | 0.127 |
| 2023_2024_PRIMARY | 6380 | FAST_FRIDAY | 301 | 0.482 | 0.308 | 0.026 | 0.372 | 0.295 | 0.333 |
| 2023_2024_PRIMARY | 6387 | POST_QUALIFYING_PRACTICE | 2502 | 0.217 | 0.08 | 0.039 | 0.776 | 0.106 | 0.118 |
| 2023_2024_PRIMARY | 6388 | CARB_DAY | 2728 | 0.224 | 0.065 | 0.028 | 0.844 | 0.062 | 0.094 |
| 2025_SECONDARY | 6651 | PRACTICE | 863 | 0.323 | 0.146 | 0.055 | 0.599 | 0.2 | 0.2 |
| 2025_SECONDARY | 6653 | PRACTICE | 1033 | 0.308 | 0.145 | 0.049 | 0.608 | 0.197 | 0.194 |
| 2025_SECONDARY | 6654 | PRACTICE | 2399 | 0.291 | 0.091 | 0.036 | 0.724 | 0.149 | 0.127 |
| 2025_SECONDARY | 6655 | FAST_FRIDAY | 618 | 0.518 | 0.295 | 0.027 | 0.433 | 0.245 | 0.322 |
| 2025_SECONDARY | 6657 | QUALIFYING_WEEKEND_PRACTICE | 202 | 0.505 | 0.2 | 0.04 | 0.33 | 0.43 | 0.24 |
| 2025_SECONDARY | 6661 | QUALIFYING_WEEKEND_PRACTICE | 118 | 0.492 | 0.267 | 0 | 0.45 | 0.283 | 0.267 |
| 2025_SECONDARY | 6662 | CARB_DAY | 1988 | 0.289 | 0.087 | 0.035 | 0.785 | 0.093 | 0.122 |
| 2025_SECONDARY | 6663 | POST_QUALIFYING_PRACTICE | 2076 | 0.256 | 0.068 | 0.043 | 0.806 | 0.083 | 0.111 |

**Coverage by team** (alphabetical; not a ranking):

| yr_group | canonical_engineering_team | n_laps | share_nonD_AB | share_nonD_C |
|---|---|---|---|---|
| 2023_2024_PRIMARY | ABEL_MOTORSPORTS | 308 | 0.184 | 0.637 |
| 2023_2024_PRIMARY | AJ_FOYT | 1108 | 0.108 | 0.716 |
| 2023_2024_PRIMARY | ANDRETTI | 2597 | 0.124 | 0.758 |
| 2023_2024_PRIMARY | ARROW_MCLAREN_SPM | 2571 | 0.127 | 0.732 |
| 2023_2024_PRIMARY | CHIP_GANASSI_RACING | 2658 | 0.112 | 0.763 |
| 2023_2024_PRIMARY | DALE_COYNE_RACING | 1105 | 0.11 | 0.775 |
| 2023_2024_PRIMARY | DREYER_REINBOLD_RACING | 1019 | 0.109 | 0.685 |
| 2023_2024_PRIMARY | ED_CARPENTER_RACING | 1952 | 0.091 | 0.785 |
| 2023_2024_PRIMARY | JUNCOS_HOLLINGER_RACING | 1168 | 0.132 | 0.63 |
| 2023_2024_PRIMARY | MEYER_SHANK_RACING | 1627 | 0.107 | 0.775 |
| 2023_2024_PRIMARY | RAHAL_LETTERMAN_LANIGAN | 2252 | 0.116 | 0.766 |
| 2023_2024_PRIMARY | TEAM_PENSKE | 1903 | 0.118 | 0.754 |
| 2025_SECONDARY | AJ_FOYT | 497 | 0.112 | 0.761 |
| 2025_SECONDARY | ANDRETTI | 994 | 0.159 | 0.68 |
| 2025_SECONDARY | ARROW_MCLAREN_SPM | 1174 | 0.163 | 0.75 |
| 2025_SECONDARY | CHIP_GANASSI_RACING | 975 | 0.162 | 0.717 |
| 2025_SECONDARY | DALE_COYNE_RACING | 465 | 0.146 | 0.587 |
| 2025_SECONDARY | DREYER_REINBOLD_RACING | 440 | 0.137 | 0.604 |
| 2025_SECONDARY | ED_CARPENTER_RACING | 801 | 0.129 | 0.686 |
| 2025_SECONDARY | JUNCOS_HOLLINGER_RACING | 514 | 0.159 | 0.648 |
| 2025_SECONDARY | MEYER_SHANK_RACING | 916 | 0.144 | 0.773 |
| 2025_SECONDARY | PREMA_RACING | 622 | 0.147 | 0.672 |
| 2025_SECONDARY | RAHAL_LETTERMAN_LANIGAN | 1028 | 0.15 | 0.701 |
| 2025_SECONDARY | TEAM_PENSKE | 871 | 0.141 | 0.78 |

## 5. Measurement-validity case (spec §9)

| criterion | value |
|---|---|
| phase4f_case_unchanged | D |
| phase4g_case_unchanged | A |
| reference_sufficient | True |
| n_2023_official_attempts | 43 |
| n_2024_official_attempts | 24 |
| T_steady_95 | 0.009401666311997741 |
| T_steady_100 | 0.01334916816180075 |
| T_level_95 | 0.001673525628209048 |
| T_level_100 | 0.001987874348791996 |
| C1_2024_official_retention_A | 0.9166666666666666 |
| C1_2024_official_retention_AB | 0.9166666666666666 |
| C1_pass | True |
| C2_2025_inferred_retention_AB | 0.08333333333333333 |
| C2_pass | False |
| S_AB_nonD_2023_2024 | 0.11570191117833081 |
| S_A_nonD_2023_2024 | 0.08057197855080435 |
| S_A_2023 | 0.07980512701542744 |
| S_A_2024 | 0.08168776371308017 |
| S_C_nonD | 0.7463220129245153 |
| S_E_nonD | 0.13797607589715385 |
| stability_abs_S_AB_minus_S_A | 0.035129932627526464 |
| MEASUREMENT_VALIDITY_CASE | D |
| agreement_2025_S_AB_nonD | 0.14835592956210067 |
| agreement_2025_S_A_nonD | 0.10830606202275206 |
| agreement_2025_S_C_nonD | 0.7107682717780894 |
| phase4i_gate | STOP practice-based hierarchy |
