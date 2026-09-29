# V4 Phase 4F — Empirical Performance-Control Hierarchy Report

**Pre-specification:** `phase4f_prespecified_design.md`, committed as `fa480ed` before any hierarchy computation. Primary rules were not changed after results were seen.

**Evidence and scope:**
- Lap data are **Timing71 archived recordings of the INDYCAR live timing feed** (third-party). Official INDYCAR session details are used only as a cross-check (§Cross-check).
- No model was fitted, no coefficient estimated, and no team or driver ranked.

## Population (addendum 1)

- **Primary:** exactly the 15 Phase 4E Design-1-feasible sessions (Era B, 2023–2024; Tier A/B; all three comparison classes present; race excluded).
- **2025:** Tier A/B, but its Phase 4E Design-1 label is "feasible with additional data" (only one in-scope year of the hybrid regime). It is analysed identically, reported separately, and does not enter the case evaluation.
- **Race:** structural appendix only.

| session_key | role | normalized_category | raw_laps | broad_laps | comparable_laps | cars | teams |
|---|---|---|---|---|---|---|---|
| 2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206 | PRIMARY | QUALIFYING_OTHER | 104 | 77 | 18 | 16 | 7 |
| 6198 | PRIMARY | PRACTICE | 3595 | 2552 | 1688 | 34 | 12 |
| 6199 | PRIMARY | PRACTICE | 3284 | 2340 | 1625 | 34 | 12 |
| 6200 | PRIMARY | FAST_FRIDAY | 1051 | 515 | 262 | 34 | 12 |
| 6202 | PRIMARY | QUALIFYING_DAY1 | 285 | 233 | 123 | 34 | 12 |
| 6203 | PRIMARY | QUALIFYING_WEEKEND_PRACTICE | 197 | 94 | 42 | 15 | 7 |
| 6207 | PRIMARY | POST_QUALIFYING_PRACTICE | 1875 | 1392 | 997 | 33 | 12 |
| 6208 | PRIMARY | CARB_DAY | 2363 | 1763 | 1330 | 33 | 12 |
| 6375 | PRIMARY | PRACTICE | 238 | 128 | 74 | 28 | 11 |
| 6378 | PRIMARY | PRACTICE | 2134 | 1577 | 1096 | 34 | 11 |
| 6380 | PRIMARY | FAST_FRIDAY | 301 | 164 | 79 | 29 | 10 |
| 6382 | PRIMARY | QUALIFYING_DAY1 | 210 | 161 | 98 | 34 | 11 |
| 6386 | PRIMARY | QUALIFYING_OTHER | 46 | 31 | 20 | 10 | 6 |
| 6387 | PRIMARY | POST_QUALIFYING_PRACTICE | 2502 | 1960 | 1510 | 33 | 11 |
| 6388 | PRIMARY | CARB_DAY | 2728 | 2120 | 1703 | 33 | 11 |
| 6651 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | PRACTICE | 863 | 596 | 382 | 34 | 12 |
| 6653 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | PRACTICE | 1033 | 730 | 447 | 34 | 12 |
| 6654 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | PRACTICE | 2399 | 1714 | 1165 | 34 | 12 |
| 6655 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | FAST_FRIDAY | 618 | 313 | 166 | 34 | 12 |
| 6656 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | QUALIFYING_DAY1 | 337 | 263 | 184 | 34 | 12 |
| 6657 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | QUALIFYING_WEEKEND_PRACTICE | 202 | 108 | 48 | 23 | 11 |
| 6660 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | QUALIFYING_OTHER | 61 | 40 | 26 | 10 | 7 |
| 6661 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | QUALIFYING_WEEKEND_PRACTICE | 118 | 60 | 31 | 13 | 7 |
| 6662 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | CARB_DAY | 1988 | 1414 | 1098 | 33 | 12 |
| 6663 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | POST_QUALIFYING_PRACTICE | 2076 | 1548 | 1176 | 33 | 12 |
| 6135 | RACE_APPENDIX_STRUCTURAL_ONLY | RACE | 1196 | 647 | 0 | 33 | 12 |
| 6309 | RACE_APPENDIX_STRUCTURAL_ONLY | RACE | 7474 | 5104 | 1539 | 30 | 11 |
| 6460 | RACE_APPENDIX_STRUCTURAL_ONLY | RACE | 5672 | 4039 | 3346 | 32 | 12 |

## Car-block validity (addendum 3; reported before the hierarchy)

| role | layer | category | car_blocks | laps_median | laps_p90 | single_lap_share | spread_median | spread_p90 | wide_spread_share | with_pit_adjacent_laps_share |
|---|---|---|---|---|---|---|---|---|---|---|
| ERA_C_SECONDARY | broad | CARB_DAY | 330 | 4 | 7 | 0.15 | 5.9 | 12.85 | 0.7 | 0.78 |
| ERA_C_SECONDARY | broad | FAST_FRIDAY | 127 | 2 | 5 | 0.38 | 1.44 | 17.71 | 0.47 | 0.92 |
| ERA_C_SECONDARY | broad | POST_QUALIFYING_PRACTICE | 392 | 4 | 7 | 0.17 | 6.32 | 12.99 | 0.7 | 0.82 |
| ERA_C_SECONDARY | broad | PRACTICE | 910 | 3 | 7 | 0.25 | 2.63 | 10.54 | 0.47 | 0.88 |
| ERA_C_SECONDARY | broad | QUALIFYING_DAY1 | 100 | 3 | 4 | 0.22 | 0.4 | 1.72 | 0.02 | 0.73 |
| ERA_C_SECONDARY | broad | QUALIFYING_OTHER | 15 | 3 | 4 | 0.2 | 0.59 | 0.94 | 0 | 0.87 |
| ERA_C_SECONDARY | broad | QUALIFYING_WEEKEND_PRACTICE | 61 | 3 | 4 | 0.23 | 12.63 | 16.25 | 0.57 | 0.93 |
| ERA_C_SECONDARY | comparable | CARB_DAY | 261 | 4 | 7 | 0.16 | 5.81 | 12.69 | 0.7 | 0 |
| ERA_C_SECONDARY | comparable | FAST_FRIDAY | 76 | 2 | 3 | 0.29 | 0.38 | 2.32 | 0.05 | 0 |
| ERA_C_SECONDARY | comparable | POST_QUALIFYING_PRACTICE | 311 | 3 | 7 | 0.21 | 5.48 | 12.35 | 0.66 | 0 |
| ERA_C_SECONDARY | comparable | PRACTICE | 630 | 3 | 7 | 0.27 | 2.25 | 10.24 | 0.45 | 0 |
| ERA_C_SECONDARY | comparable | QUALIFYING_DAY1 | 91 | 2 | 3 | 0.34 | 0.17 | 1.21 | 0 | 0 |
| ERA_C_SECONDARY | comparable | QUALIFYING_OTHER | 12 | 2 | 3 | 0.17 | 0.24 | 0.62 | 0 | 0 |
| ERA_C_SECONDARY | comparable | QUALIFYING_WEEKEND_PRACTICE | 45 | 2 | 3 | 0.47 | 0.15 | 1.02 | 0 | 0 |
| PRIMARY | broad | CARB_DAY | 857 | 4 | 7 | 0.13 | 5.44 | 11.8 | 0.7 | 0.79 |
| PRIMARY | broad | FAST_FRIDAY | 262 | 2.5 | 5 | 0.32 | 8.02 | 20.38 | 0.53 | 0.94 |
| PRIMARY | broad | POST_QUALIFYING_PRACTICE | 803 | 4 | 7 | 0.14 | 5.8 | 12.4 | 0.69 | 0.8 |
| PRIMARY | broad | PRACTICE | 1820 | 3 | 7 | 0.21 | 3.57 | 11.85 | 0.53 | 0.88 |
| PRIMARY | broad | QUALIFYING_DAY1 | 182 | 2 | 3 | 0.37 | 0.38 | 1.34 | 0.03 | 0.87 |
| PRIMARY | broad | QUALIFYING_OTHER | 39 | 3 | 3 | 0.13 | 0.56 | 1.36 | 0 | 0.97 |
| PRIMARY | broad | QUALIFYING_WEEKEND_PRACTICE | 25 | 4 | 5 | 0.16 | 0.68 | 14.02 | 0.32 | 0.96 |
| PRIMARY | comparable | CARB_DAY | 718 | 4 | 7 | 0.19 | 4.53 | 11.19 | 0.64 | 0 |
| PRIMARY | comparable | FAST_FRIDAY | 171 | 2 | 3 | 0.34 | 0.36 | 1.75 | 0.06 | 0 |
| PRIMARY | comparable | POST_QUALIFYING_PRACTICE | 654 | 3 | 7 | 0.17 | 5.23 | 11.54 | 0.63 | 0 |
| PRIMARY | comparable | PRACTICE | 1330 | 3 | 7 | 0.25 | 2.58 | 10.96 | 0.48 | 0 |
| PRIMARY | comparable | QUALIFYING_DAY1 | 121 | 2 | 3 | 0.31 | 0.19 | 0.8 | 0.01 | 0 |
| PRIMARY | comparable | QUALIFYING_OTHER | 21 | 2 | 2 | 0.24 | 0.24 | 1.16 | 0 | 0 |
| PRIMARY | comparable | QUALIFYING_WEEKEND_PRACTICE | 17 | 2 | 4 | 0.29 | 0.38 | 2.02 | 0.12 | 0 |

- **Practice-type sessions:** car-blocks typically hold 3–4 laps with a within-block speed spread of several mph. Roughly half to two-thirds exceed 3 mph (`wide_spread_share`), even in the comparable layer. The spread reflects towed vs un-towed laps and run-plan variation that the data cannot identify.
- **Qualifying sessions:** spreads are tight (≈0.2–0.4 mph).
- **Consequence:** the car-block median speed is an **observed local performance summary, not pure pace**.

## Primary hierarchy (2023–2024, session-balanced; D in mph)

| layer | width_min | sessions_with_eligible_blocks | eligible_blocks | session_balanced_delta | boot_session_lo | boot_session_hi | share_sessions_positive | session_balanced_delta_team_balanced | sb_D_same_car | sb_D_same_team | sb_D_diff_team |
|---|---|---|---|---|---|---|---|---|---|---|---|
| comparable | 1 | 9 | 694 | -0.148 | -0.639 | 0.098 | 0.222 | 0.222 | 1.863 | 2.012 | 1.684 |
| comparable | 2 | 10 | 389 | -0.101 | -0.344 | 1.039 | 0.5 | 0.272 | 1.591 | 1.797 | 1.644 |
| comparable | 5 | 10 | 209 | 0.046 | -0.208 | 0.709 | 0.5 | 0.31 | 1.697 | 1.606 | 1.801 |
| comparable | 10 | 12 | 148 | 0.074 | -0.128 | 0.277 | 0.5 | 0.273 | 1.72 | 1.519 | 1.529 |
| broad | 1 | 13 | 854 | -0.367 | -0.571 | 0.178 | 0.308 | 0.219 | 2.114 | 2.097 | 1.694 |
| broad | 2 | 13 | 488 | -0.056 | -0.435 | 0.411 | 0.462 | 0.256 | 1.939 | 1.935 | 1.571 |
| broad | 5 | 13 | 249 | -0.046 | -0.133 | 0.564 | 0.385 | 0.285 | 1.918 | 1.882 | 1.515 |
| broad | 10 | 13 | 166 | -0.026 | -0.129 | 0.313 | 0.462 | 0.486 | 1.825 | 1.501 | 1.512 |

**Class distributions (5 min):**

| scope | class | n_raw_comparisons | n_unique_cars | n_unique_teams | n_unique_sessions | n_unique_blocks | weighted_median | mean | sd | iqr | p10 | p25 | p75 | p90 | block_balanced_median | session_balanced_median | time_sep_median_min |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERA_C_SECONDARY|broad|5min | DIFF_TEAM | 1129 | 34 | 12 | 7 | 134 | 1.931 | 2.732 | 2.807 | 3.14 | 0.295 | 0.725 | 3.864 | 5.991 | 1.923 | 2.153 | 0.056 |
| ERA_C_SECONDARY|broad|5min | SAME_CAR | 894 | 34 | 12 | 10 | 193 | 1.977 | 2.944 | 3.112 | 3.406 | 0.272 | 0.736 | 4.141 | 6.784 | 1.473 | 2.182 | 3.147 |
| ERA_C_SECONDARY|broad|5min | SAME_TEAM | 815 | 34 | 12 | 8 | 138 | 2.182 | 3.004 | 2.842 | 3.215 | 0.386 | 0.977 | 4.192 | 6.842 | 2.116 | 2.029 | 0.812 |
| ERA_C_SECONDARY|comparable|5min | DIFF_TEAM | 762 | 34 | 12 | 7 | 107 | 1.937 | 2.523 | 2.549 | 2.631 | 0.24 | 0.721 | 3.352 | 5.428 | 1.802 | 1.787 | 0.056 |
| ERA_C_SECONDARY|comparable|5min | SAME_CAR | 575 | 34 | 12 | 10 | 141 | 2.008 | 2.614 | 2.632 | 2.876 | 0.284 | 0.746 | 3.622 | 5.778 | 1.417 | 0.94 | 3.115 |
| ERA_C_SECONDARY|comparable|5min | SAME_TEAM | 548 | 34 | 12 | 8 | 112 | 1.919 | 2.788 | 2.664 | 2.86 | 0.414 | 0.999 | 3.859 | 6.084 | 1.963 | 1.713 | 0.751 |
| PRIMARY|broad|5min | DIFF_TEAM | 2674 | 68 | 12 | 13 | 249 | 1.582 | 2.466 | 2.761 | 2.634 | 0.268 | 0.696 | 3.33 | 5.592 | 1.769 | 1.515 | 0.054 |
| PRIMARY|broad|5min | SAME_CAR | 1950 | 68 | 12 | 14 | 288 | 1.98 | 2.759 | 2.766 | 2.836 | 0.334 | 0.865 | 3.702 | 6.096 | 1.925 | 1.918 | 3.427 |
| PRIMARY|broad|5min | SAME_TEAM | 2400 | 67 | 11 | 13 | 253 | 1.718 | 2.472 | 2.473 | 2.525 | 0.274 | 0.725 | 3.25 | 5.413 | 1.826 | 1.882 | 0.717 |
| PRIMARY|comparable|5min | DIFF_TEAM | 1937 | 68 | 12 | 10 | 209 | 1.714 | 2.422 | 2.455 | 2.639 | 0.295 | 0.692 | 3.331 | 5.331 | 1.931 | 1.801 | 0.056 |
| PRIMARY|comparable|5min | SAME_CAR | 1356 | 68 | 12 | 13 | 218 | 1.749 | 2.518 | 2.491 | 2.712 | 0.294 | 0.81 | 3.523 | 5.562 | 1.52 | 1.697 | 3.411 |
| PRIMARY|comparable|5min | SAME_TEAM | 1648 | 67 | 11 | 13 | 218 | 1.793 | 2.498 | 2.404 | 2.579 | 0.306 | 0.778 | 3.357 | 5.384 | 1.649 | 1.606 | 0.73 |

**Minimum-laps ≥2 sensitivity:**

| role | layer | width_min | session_balanced_delta | share_sessions_positive | session_balanced_delta_team_balanced |
|---|---|---|---|---|---|
| PRIMARY | comparable | 5 | 0.138 | 0.5 | 0.32 |
| PRIMARY | broad | 5 | -0.046 | 0.455 | 0.197 |
| ERA_C_SECONDARY | comparable | 5 | 0.044 | 0.667 | 0.188 |
| ERA_C_SECONDARY | broad | 5 | -0.367 | 0 | 0.049 |

**2025 secondary (separate; not pooled):**

| layer | width_min | sessions_with_eligible_blocks | eligible_blocks | session_balanced_delta | boot_session_lo | boot_session_hi | share_sessions_positive | session_balanced_delta_team_balanced | sb_D_same_car | sb_D_same_team | sb_D_diff_team |
|---|---|---|---|---|---|---|---|---|---|---|---|
| comparable | 1 | 6 | 314 | -0.086 | -0.748 | 0.518 | 0.333 | -0.049 | 1.209 | 2.062 | 1.595 |
| comparable | 2 | 6 | 186 | -0.238 | -0.52 | 0.457 | 0.333 | 0.394 | 1.1 | 1.823 | 1.665 |
| comparable | 5 | 7 | 107 | -0.387 | -0.461 | -0.031 | 0.143 | 0.121 | 0.94 | 1.713 | 1.787 |
| comparable | 10 | 9 | 77 | -0.194 | -0.301 | 0.294 | 0.444 | 0.294 | 1.251 | 1.639 | 1.661 |
| broad | 1 | 7 | 404 | -0.045 | -0.731 | 0.188 | 0.429 | 0.156 | 1.953 | 1.945 | 1.72 |
| broad | 2 | 7 | 236 | -0.224 | -0.553 | 0.285 | 0.429 | 0.243 | 1.954 | 1.972 | 1.656 |
| broad | 5 | 7 | 134 | -0.023 | -0.43 | 0.262 | 0.429 | 0.24 | 2.182 | 2.029 | 2.153 |
| broad | 10 | 9 | 90 | -0.171 | -0.466 | 0.201 | 0.444 | 0.11 | 1.67 | 2.033 | 1.889 |

## The pre-registered primary control is confounded by on-track adjacency

| class | median_sep_s | share_le_10s | share_le_30s |
|---|---|---|---|
| DIFF_TEAM | 3.345 | 0.659 | 0.885 |
| TEAMMATE_OF_TARGET | 37.671 | 0.274 | 0.473 |

D of the time-nearest different-team control, by how close it ran:

| sep | size | median |
|---|---|---|
| <=5s | 1080 | 1.294 |
| 5-15s | 307 | 2.89 |
| 15-60s | 467 | 1.987 |
| 60-300s | 83 | 2.738 |

- **What the primary control is:** the pre-registered control is the different-team car nearest in time within the block. It is within 10 s of the target in about two-thirds of cases, far more often than the nearest teammate. That means it is typically the car running directly ahead of or behind the target, in the same tow group.
- **Why that matters:** such adjacent cars have markedly smaller D (≈1.3 mph within 5 s vs 2–2.9 mph farther away). The primary contrast therefore compares teammates against drafting partners.
- **This is a design limitation discovered after pre-specification.** The primary rule is **not** changed. The pre-declared sensitivity designs that do not select controls by track adjacency (team-balanced within-block pairs, the adjacent-block design and time-separation reweighting) are reported alongside.

## Year, category, leave-one-team-out

| role | layer | year | sessions | session_balanced_delta | share_sessions_positive | blocks |
|---|---|---|---|---|---|---|
| PRIMARY | comparable | 2023 | 5 | 0.103 | 0.6 | 136 |
| PRIMARY | comparable | 2024 | 5 | -0.208 | 0.4 | 73 |
| ERA_C_SECONDARY | comparable | 2025 | 7 | -0.387 | 0.143 | 107 |
| PRIMARY | broad | 2023 | 7 | -0.046 | 0.429 | 166 |
| PRIMARY | broad | 2024 | 6 | -0.075 | 0.333 | 83 |
| ERA_C_SECONDARY | broad | 2025 | 7 | -0.023 | 0.429 | 134 |

| role | layer | category | sessions | session_balanced_delta | share_sessions_positive | blocks | pooled_block_median_delta |
|---|---|---|---|---|---|---|---|
| PRIMARY | comparable | CARB_DAY | 2 | -0.001 | 0.5 | 41 | -0.015 |
| PRIMARY | comparable | FAST_FRIDAY | 2 | 0.772 | 1 | 7 | 0.709 |
| PRIMARY | comparable | POST_QUALIFYING_PRACTICE | 2 | -0.173 | 0 | 40 | -0.163 |
| PRIMARY | comparable | PRACTICE | 4 | 0.024 | 0.5 | 121 | -0.114 |
| PRIMARY | broad | CARB_DAY | 2 | 0.019 | 0.5 | 42 | 0.035 |
| PRIMARY | broad | FAST_FRIDAY | 2 | -0.752 | 0 | 20 | -0.478 |
| PRIMARY | broad | POST_QUALIFYING_PRACTICE | 2 | -0.203 | 0 | 40 | -0.175 |
| PRIMARY | broad | PRACTICE | 4 | 0.273 | 0.5 | 141 | 0.24 |
| PRIMARY | broad | QUALIFYING_DAY1 | 2 | 0.937 | 1 | 2 | 0.937 |
| PRIMARY | broad | QUALIFYING_WEEKEND_PRACTICE | 1 | -0.521 | 0 | 4 | -0.521 |

**Leave-one-team-out** (primary; teams are listed only to show stability, not ranked):

| dropped_team | sessions | blocks | session_balanced_delta | share_sessions_positive |
|---|---|---|---|---|
| ABEL_MOTORSPORTS | 10 | 209 | 0.046 | 0.5 |
| AJ_FOYT | 10 | 208 | 0.093 | 0.5 |
| ANDRETTI | 10 | 199 | -0.048 | 0.4 |
| ARROW_MCLAREN_SPM | 10 | 202 | 0.023 | 0.6 |
| CHIP_GANASSI_RACING | 10 | 198 | 0.065 | 0.5 |
| DALE_COYNE_RACING | 10 | 207 | -0.005 | 0.5 |
| DREYER_REINBOLD_RACING | 10 | 208 | 0.029 | 0.5 |
| ED_CARPENTER_RACING | 10 | 205 | 0.153 | 0.7 |
| JUNCOS_HOLLINGER_RACING | 10 | 206 | 0.026 | 0.5 |
| MEYER_SHANK_RACING | 10 | 207 | 0.151 | 0.6 |
| RAHAL_LETTERMAN_LANIGAN | 10 | 203 | -0.047 | 0.4 |
| TEAM_PENSKE | 10 | 203 | -0.027 | 0.4 |

## Same-car fairness

| construction | layer | class | n | sessions | session_balanced_median | pooled_median | time_sep_median_min | same_car_separation_mass_covered |
|---|---|---|---|---|---|---|---|---|
| ADJACENT_BLOCK_ALL_CLASSES | comparable | DIFF_TEAM_ADJ | 1006 | 10 | 2.617 | 2.591 | 2.451 |  |
| ADJACENT_BLOCK_ALL_CLASSES | comparable | SAME_CAR_ADJ | 1006 | 10 | 1.737 | 1.803 | 3.452 |  |
| ADJACENT_BLOCK_ALL_CLASSES | comparable | SAME_TEAM_ADJ | 1006 | 10 | 2.004 | 2.039 | 3.749 |  |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | comparable | SAME_TEAM | 1648 | 13 | 1.726 | 1.771 | 0.73 | 0.87 |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | comparable | DIFF_TEAM | 1937 | 10 | 2.507 | 2.384 | 0.056 | 0.87 |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | comparable | SAME_CAR | 1356 | 13 | 1.707 | 1.751 | 3.411 | 1 |
| ADJACENT_BLOCK_ALL_CLASSES | broad | DIFF_TEAM_ADJ | 1459 | 12 | 2.616 | 2.44 | 2.596 |  |
| ADJACENT_BLOCK_ALL_CLASSES | broad | SAME_CAR_ADJ | 1459 | 12 | 2.017 | 1.947 | 3.656 |  |
| ADJACENT_BLOCK_ALL_CLASSES | broad | SAME_TEAM_ADJ | 1459 | 12 | 2.011 | 2.153 | 3.787 |  |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | broad | SAME_TEAM | 2400 | 13 | 2.799 | 2.554 | 0.717 | 0.821 |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | broad | DIFF_TEAM | 2674 | 13 | 1.383 | 4.443 | 0.054 | 0.821 |
| TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR | broad | SAME_CAR | 1950 | 14 | 1.982 | 1.984 | 3.427 | 1 |

- **At matched time separation:**
  - In the adjacent-block design (k → k+1 for every class), the comparable layer orders same car < same team < different team.
  - In the broad layer, same car ≈ same team < different team.
  - With within-block comparisons reweighted to the same-car time-separation distribution (comparable layer), the order is same car ≤ same team < different team.
  - **Contradictory broad-layer reweighting:** in the broad layer the reweighted result is unstable. The session-balanced different-team median (1.38) falls *below* same-team (2.80), while the pooled median points the other way (4.44 vs 2.55). The reweighting covers only 82% of the same-car separation mass there.
- **The same-car advantage is small:** in the comparable layer it is about 0.27 mph over same-team in the adjacent-block design, and it vanishes in the broad layer.

## Leave-one-out team-relative deviation

| role | count | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|---|
| ERA_C_SECONDARY | 772 | 2.663 | 2.568 | 0.017 | 0.932 | 1.862 | 3.709 | 16.06 |
| PRIMARY | 1955 | 2.298 | 2.296 | 0.002 | 0.761 | 1.662 | 3.189 | 20.4 |

## Weather inside blocks (diagnostic only)

| index | ptsc_readings | track_range_c | ambient_range_c |
|---|---|---|---|
| count | 209 | 209 | 209 |
| mean | 1.67 | 0.64 | 0.3 |
| std | 0.47 | 0.71 | 0.4 |
| min | 1 | 0 | 0 |
| 25% | 1 | 0 | 0 |
| 50% | 2 | 0.56 | 0 |
| 75% | 2 | 1.11 | 0.56 |
| max | 2 | 2.78 | 2.22 |

PTSC is 15-minute resolution. The median block spans ≤2 readings, with a median track range of 0.56 °C and ambient 0 °C. Local blocks remove most measurable environmental mismatch, within that resolution.

## Dependence

| item | count |
|---|---|
| primary laps (comparable layer) | 10665 |
| car-block observations | 3032 |
| unique cars | 68 |
| unique canonical teams | 12 |
| unique sessions (independent clusters) | 15 |
| unique session-blocks | 454 |
| eligible within-block contrast blocks | 209 |
| comparisons DIFF_TEAM | 1937 |
| comparisons SAME_CAR | 1356 |
| comparisons SAME_TEAM | 1648 |
| comparisons TEAMMATE_OF_TARGET | 1937 |
| max appearances of one car across comparisons | 415 |
| median appearances per car | 203.5 |
| Phase 4E raw same-team lap pairs ±5 min in these sessions | 92893 |
| car-block reuse: max comparisons involving one car-block | 13 |

The Phase 4E raw same-team pair count for these sessions (92,893) compresses to 1,648 same-team block-pair comparisons, 209 eligible contrast blocks, and **15 independent sessions**. The raw pair counts exaggerate the effective sample by roughly two to three orders of magnitude.

## Case evaluation (pre-declared, mechanical)

| criterion | value |
|---|---|
| delta_positive | True |
| share_ge_075 | False |
| both_years_positive | False |
| loto_all_positive | False |
| broad_positive | False |
| windows_ge2_positive | False |
| team_advantage_consistent | False |
| same_car_ordering_established | True |
| CASE | D |

**Headline: CASE D.**

**Why it is D:** the pre-registered primary contrast (time-nearest different-team control, comparable layer, 5 min) is:
- only +0.046 mph session-balanced, with a session-bootstrap interval of −0.21 to +0.71;
- positive in only 50% of sessions;
- negative in 2024;
- sign-unstable across block widths and leave-one-team-out removals;
- negative in the broad layer.

**What the pre-declared sensitivities show instead:** a **consistent** same-team advantage.
- The team-balanced within-block contrast is +0.22 to +0.49 mph in every primary layer and width, and mostly positive in 2025.
- The adjacent-block design gives different team 2.62 > same team 2.00 > same car 1.74 mph (comparable layer).
- Time-separation reweighting (comparable layer) gives different team 2.51 > same team 1.73 ≈ same car 1.71. The broad-layer reweighting is unstable and contradictory (see Same-car fairness).

**What this means:** the evidence is mixed. By the committed rule it is CASE D. The documented adjacency confound means that result is plausibly an artefact of how the primary control was defined, not evidence against team control. This report does not re-label the case.
