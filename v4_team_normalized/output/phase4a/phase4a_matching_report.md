# V4 Phase 4A — Frozen-Transition Teammate-Control Matching Design

**Status:** design and diagnostics only.
- No coefficient was fitted or refitted.
- The frozen 41 transitions are read-only anchors, and teammate observations were not added to them.
- No matching rule was implemented as final, and no inferential test was run.

## Anchors (4A.1)

The 41 frozen transitions come from `r5_2/manual/r5_2_repeat_analysis_set_v1.csv`, restricted to rows with non-missing target, track and ambient changes. Every frozen value is carried unaltered into `frozen_transition_anchors.csv`.

**Model values.** Existing frozen LOYO predictions and residuals come from `r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv`, which is in the frozen manifest. Its rows were linked by row order and verified on year, car, driver, Δspeed, Δtrack and Δair for all 41. A second column, `derived_full_data_frozen_prediction_mph`, applies the frozen full-data coefficients; it is labelled as derived.

**Endpoint times.**
- 38 transitions use the frozen repeat-set timestamps.
- The 3 R5.2 public-rescue transitions have no timestamp in the repeat set. They use the Phase 3 rescue timestamp, and the source is recorded in `t1_source` / `t2_source`.

**Eligibility.**
- One transition (2021 Paretta #16) belongs to a technical-partnership entry, so it has no eligible teammates by decision.
- The remaining 40 are eligible.
- Eligible teammate observations: complete four-lap, timed attempts from a different entry of the same canonical team.
- Excluded: the target entry (including backup chassis), technical partnerships, and ambiguous affiliations.

## 1. Endpoint support by window (4A.3)

| window_min | support_t1:ANY | support_t2:ANY | support_both:ANY | support_t1:PRIOR | support_t2:PRIOR | support_both:PRIOR | support_t1:FUTURE | support_t2:FUTURE | support_both:FUTURE |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 9 | 5 | 1 | 4 | 2 | 0 | 5 | 3 | 0 |
| 15 | 15 | 13 | 6 | 7 | 6 | 1 | 8 | 7 | 2 |
| 20 | 17 | 17 | 9 | 7 | 8 | 2 | 10 | 9 | 3 |
| 30 | 22 | 17 | 9 | 11 | 8 | 3 | 12 | 9 | 3 |
| 45 | 26 | 19 | 13 | 14 | 11 | 5 | 15 | 10 | 4 |
| 5 | 4 | 1 | 0 | 2 | 0 | 0 | 2 | 1 | 0 |
| 60 | 32 | 22 | 21 | 16 | 14 | 9 | 22 | 13 | 10 |

Transitions with ≥2 distinct teammate cars inside the window (any direction):

| window_min | multi_car_t1 | multi_car_t2 | multi_car_both |
|---|---|---|---|
| 5 | 0 | 1 | 0 |
| 10 | 0 | 1 | 0 |
| 15 | 0 | 1 | 0 |
| 20 | 2 | 1 | 0 |
| 30 | 6 | 1 | 0 |
| 45 | 11 | 3 | 1 |
| 60 | 17 | 7 | 4 |

## 2. Nearest-match support

| view | endpoints_with_any_eligible_teammate | q00 | q25 | q50 | q75 | q90 | q100 |
|---|---|---|---|---|---|---|---|
| nearest any direction | 70 | 4 | 11.8 | 23.8 | 55.4 | 167.6 | 254.9 |
| nearest prior-only (PIT) | 60 | 5 | 20.9 | 59.6 | 110.4 | 175 | 254.9 |
| nearest future-only | 47 | 4 | 13.2 | 41.3 | 59.6 | 103.2 | 207 |

## 3–4. Strategy comparison, car-balanced support and PIT support (4A.4–4A.7)

**Degenerate** controls use the identical teammate attempts at both endpoints, so the control change is zero by construction. They are excluded from the association columns. **Control = another frozen transition** means the teammate control change is exactly another car's frozen same-car transition, so the pair re-uses same-car evidence.

### Retrospective, any direction

| strategy | window_min | direction | n_supported_both | n_nondegenerate | n_same_teammate_car_set | n_control_equals_other_frozen_transition | n_reciprocal_frozen_pairs | n_independent_of_frozen_transitions | same_direction_n | same_direction_fraction |
|---|---|---|---|---|---|---|---|---|---|---|
| NEAREST | 15 | ANY | 6 | 6 | 3 | 2 | 1 | 4 | 6 | 0.667 |
| NEAREST | 30 | ANY | 9 | 9 | 3 | 2 | 1 | 7 | 9 | 0.667 |
| NEAREST | 45 | ANY | 13 | 13 | 5 | 4 | 2 | 9 | 13 | 0.692 |
| NEAREST | 60 | ANY | 21 | 19 | 9 | 8 | 3 | 11 | 19 | 0.632 |
| NEAREST | UNBOUNDED | ANY | 35 | 25 | 10 | 9 | 3 | 16 | 25 | 0.64 |
| MUTUAL_NEAREST | 15 | ANY | 6 | 6 | 3 | 2 | 1 | 4 | 6 | 0.667 |
| MUTUAL_NEAREST | 30 | ANY | 9 | 9 | 3 | 2 | 1 | 7 | 9 | 0.667 |
| MUTUAL_NEAREST | 45 | ANY | 13 | 13 | 5 | 4 | 2 | 9 | 13 | 0.692 |
| MUTUAL_NEAREST | 60 | ANY | 17 | 17 | 8 | 7 | 3 | 10 | 17 | 0.706 |
| MUTUAL_NEAREST | UNBOUNDED | ANY | 18 | 18 | 8 | 7 | 3 | 11 | 18 | 0.667 |
| WINDOW_MEDIAN | 15 | ANY | 6 | 6 | 3 | 2 | 1 | 4 | 6 | 0.667 |
| WINDOW_MEDIAN | 30 | ANY | 9 | 9 | 2 | 2 | 1 | 7 | 9 | 0.556 |
| WINDOW_MEDIAN | 45 | ANY | 13 | 13 | 3 | 3 | 1 | 10 | 13 | 0.692 |
| WINDOW_MEDIAN | 60 | ANY | 21 | 19 | 5 | 5 | 2 | 14 | 19 | 0.579 |
| WINDOW_MEAN | 15 | ANY | 6 | 6 | 3 | 2 | 1 | 4 | 6 | 0.667 |
| WINDOW_MEAN | 30 | ANY | 9 | 9 | 2 | 2 | 1 | 7 | 9 | 0.556 |
| WINDOW_MEAN | 45 | ANY | 13 | 13 | 3 | 3 | 1 | 10 | 13 | 0.692 |
| WINDOW_MEAN | 60 | ANY | 21 | 19 | 5 | 5 | 2 | 14 | 19 | 0.579 |
| CAR_BALANCED_MEAN | 15 | ANY | 6 | 6 | 3 | 2 | 1 | 4 | 6 | 0.667 |
| CAR_BALANCED_MEAN | 30 | ANY | 9 | 9 | 2 | 2 | 1 | 7 | 9 | 0.556 |
| CAR_BALANCED_MEAN | 45 | ANY | 13 | 13 | 3 | 3 | 1 | 10 | 13 | 0.692 |
| CAR_BALANCED_MEAN | 60 | ANY | 21 | 19 | 5 | 5 | 2 | 14 | 19 | 0.579 |
| CAR_BALANCED_COMMON_CARS | 15 | ANY | 3 | 3 | 3 | 2 | 1 | 1 | 3 | 1 |
| CAR_BALANCED_COMMON_CARS | 30 | ANY | 7 | 7 | 7 | 6 | 3 | 1 | 7 | 0.429 |
| CAR_BALANCED_COMMON_CARS | 45 | ANY | 9 | 9 | 9 | 8 | 4 | 1 | 9 | 0.556 |
| CAR_BALANCED_COMMON_CARS | 60 | ANY | 19 | 16 | 16 | 12 | 4 | 4 | 16 | 0.562 |

### PIT-compatible (prior-only: teammate_timestamp ≤ endpoint)

| strategy | window_min | direction | n_supported_both | n_nondegenerate | n_same_teammate_car_set | n_control_equals_other_frozen_transition | n_reciprocal_frozen_pairs | n_independent_of_frozen_transitions | same_direction_n | same_direction_fraction |
|---|---|---|---|---|---|---|---|---|---|---|
| NEAREST | 15 | PRIOR | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 |
| NEAREST | 30 | PRIOR | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| NEAREST | 45 | PRIOR | 5 | 5 | 1 | 1 | 0 | 4 | 5 | 0.6 |
| NEAREST | 60 | PRIOR | 9 | 9 | 4 | 4 | 0 | 5 | 9 | 0.444 |
| NEAREST | UNBOUNDED | PRIOR | 25 | 18 | 6 | 6 | 0 | 12 | 18 | 0.556 |
| MUTUAL_NEAREST | 15 | PRIOR | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 |
| MUTUAL_NEAREST | 30 | PRIOR | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| MUTUAL_NEAREST | 45 | PRIOR | 5 | 5 | 1 | 1 | 0 | 4 | 5 | 0.6 |
| MUTUAL_NEAREST | 60 | PRIOR | 9 | 9 | 4 | 4 | 0 | 5 | 9 | 0.444 |
| MUTUAL_NEAREST | UNBOUNDED | PRIOR | 11 | 11 | 5 | 5 | 0 | 6 | 11 | 0.455 |
| WINDOW_MEDIAN | 15 | PRIOR | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 |
| WINDOW_MEDIAN | 30 | PRIOR | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| WINDOW_MEDIAN | 45 | PRIOR | 5 | 5 | 1 | 1 | 0 | 4 | 5 | 0.6 |
| WINDOW_MEDIAN | 60 | PRIOR | 9 | 9 | 4 | 4 | 0 | 5 | 9 | 0.444 |
| WINDOW_MEAN | 15 | PRIOR | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 |
| WINDOW_MEAN | 30 | PRIOR | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| WINDOW_MEAN | 45 | PRIOR | 5 | 5 | 1 | 1 | 0 | 4 | 5 | 0.6 |
| WINDOW_MEAN | 60 | PRIOR | 9 | 9 | 4 | 4 | 0 | 5 | 9 | 0.444 |
| CAR_BALANCED_MEAN | 15 | PRIOR | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 1 |
| CAR_BALANCED_MEAN | 30 | PRIOR | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| CAR_BALANCED_MEAN | 45 | PRIOR | 5 | 5 | 1 | 1 | 0 | 4 | 5 | 0.6 |
| CAR_BALANCED_MEAN | 60 | PRIOR | 9 | 9 | 4 | 4 | 0 | 5 | 9 | 0.444 |
| CAR_BALANCED_COMMON_CARS | 15 | PRIOR | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |
| CAR_BALANCED_COMMON_CARS | 30 | PRIOR | 2 | 2 | 2 | 2 | 0 | 0 | 2 | 0 |
| CAR_BALANCED_COMMON_CARS | 45 | PRIOR | 3 | 3 | 3 | 3 | 0 | 0 | 3 | 0.333 |
| CAR_BALANCED_COMMON_CARS | 60 | PRIOR | 7 | 7 | 7 | 7 | 0 | 0 | 7 | 0.429 |

### Future-only (retrospective)

| strategy | window_min | direction | n_supported_both | n_nondegenerate | n_same_teammate_car_set | n_control_equals_other_frozen_transition | n_reciprocal_frozen_pairs | n_independent_of_frozen_transitions | same_direction_n | same_direction_fraction |
|---|---|---|---|---|---|---|---|---|---|---|
| NEAREST | 15 | FUTURE | 2 | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| NEAREST | 30 | FUTURE | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| NEAREST | 45 | FUTURE | 4 | 4 | 1 | 1 | 0 | 3 | 4 | 0.5 |
| NEAREST | 60 | FUTURE | 10 | 9 | 4 | 4 | 0 | 5 | 9 | 0.556 |
| NEAREST | UNBOUNDED | FUTURE | 17 | 15 | 6 | 6 | 0 | 9 | 15 | 0.6 |
| MUTUAL_NEAREST | 15 | FUTURE | 2 | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| MUTUAL_NEAREST | 30 | FUTURE | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0.333 |
| MUTUAL_NEAREST | 45 | FUTURE | 4 | 4 | 1 | 1 | 0 | 3 | 4 | 0.5 |
| MUTUAL_NEAREST | 60 | FUTURE | 8 | 8 | 3 | 3 | 0 | 5 | 8 | 0.625 |
| MUTUAL_NEAREST | UNBOUNDED | FUTURE | 11 | 11 | 4 | 4 | 0 | 7 | 11 | 0.545 |
| WINDOW_MEDIAN | 15 | FUTURE | 2 | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| WINDOW_MEDIAN | 30 | FUTURE | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| WINDOW_MEDIAN | 45 | FUTURE | 4 | 4 | 1 | 1 | 0 | 3 | 4 | 0.25 |
| WINDOW_MEDIAN | 60 | FUTURE | 10 | 9 | 3 | 3 | 0 | 6 | 9 | 0.444 |
| WINDOW_MEAN | 15 | FUTURE | 2 | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| WINDOW_MEAN | 30 | FUTURE | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| WINDOW_MEAN | 45 | FUTURE | 4 | 4 | 1 | 1 | 0 | 3 | 4 | 0.25 |
| WINDOW_MEAN | 60 | FUTURE | 10 | 9 | 3 | 3 | 0 | 6 | 9 | 0.444 |
| CAR_BALANCED_MEAN | 15 | FUTURE | 2 | 2 | 0 | 0 | 0 | 2 | 2 | 0 |
| CAR_BALANCED_MEAN | 30 | FUTURE | 3 | 3 | 0 | 0 | 0 | 3 | 3 | 0 |
| CAR_BALANCED_MEAN | 45 | FUTURE | 4 | 4 | 1 | 1 | 0 | 3 | 4 | 0.25 |
| CAR_BALANCED_MEAN | 60 | FUTURE | 10 | 9 | 3 | 3 | 0 | 6 | 9 | 0.444 |
| CAR_BALANCED_COMMON_CARS | 15 | FUTURE | 0 | 0 | 0 | 0 | 0 | 0 | 0 |  |
| CAR_BALANCED_COMMON_CARS | 30 | FUTURE | 2 | 2 | 2 | 2 | 0 | 0 | 2 | 0 |
| CAR_BALANCED_COMMON_CARS | 45 | FUTURE | 3 | 3 | 3 | 3 | 0 | 0 | 3 | 0.333 |
| CAR_BALANCED_COMMON_CARS | 60 | FUTURE | 8 | 7 | 7 | 7 | 0 | 0 | 7 | 0.429 |

## 5–7. Same direction, association and team-adjusted delta (descriptive; no p-values)

| strategy | window_min | n_nondegenerate | pearson_r | spearman_rho | median_team_adjusted | iqr_team_adjusted | sd_delta_target | sd_team_adjusted | sd_frozen_loyo_residual_same_subset | pearson_team_control_vs_frozen_prediction |
|---|---|---|---|---|---|---|---|---|---|---|
| NEAREST | 15 | 6 | 0.156 | 0.029 | 0.365 | 0.817 | 0.387 | 0.816 | 0.374 | -0.706 |
| NEAREST | 30 | 9 | 0.008 | -0.067 | 0.06 | 0.886 | 0.345 | 0.856 | 0.343 | -0.315 |
| NEAREST | 45 | 13 | 0.103 | 0.148 | 0.06 | 0.861 | 0.303 | 0.756 | 0.333 | -0.171 |
| NEAREST | 60 | 19 | 0.336 | 0.125 | -0.005 | 0.797 | 0.477 | 0.693 | 0.443 | 0.052 |
| NEAREST | UNBOUNDED | 25 | 0.221 | 0.096 | -0.021 | 0.809 | 0.481 | 0.762 | 0.432 | 0.148 |
| MUTUAL_NEAREST | 15 | 6 | 0.156 | 0.029 | 0.365 | 0.817 | 0.387 | 0.816 | 0.374 | -0.706 |
| MUTUAL_NEAREST | 30 | 9 | 0.008 | -0.067 | 0.06 | 0.886 | 0.345 | 0.856 | 0.343 | -0.315 |
| MUTUAL_NEAREST | 45 | 13 | 0.103 | 0.148 | 0.06 | 0.861 | 0.303 | 0.756 | 0.333 | -0.171 |
| MUTUAL_NEAREST | 60 | 17 | 0.402 | 0.235 | -0.005 | 0.797 | 0.478 | 0.681 | 0.436 | 0.067 |
| MUTUAL_NEAREST | UNBOUNDED | 18 | 0.28 | 0.11 | 0.027 | 0.878 | 0.481 | 0.755 | 0.433 | 0.014 |
| WINDOW_MEDIAN | 15 | 6 | 0.156 | 0.029 | 0.365 | 0.817 | 0.387 | 0.816 | 0.374 | -0.706 |
| WINDOW_MEDIAN | 30 | 9 | -0.106 | -0.15 | 0.488 | 0.893 | 0.345 | 0.671 | 0.343 | -0.258 |
| WINDOW_MEDIAN | 45 | 13 | 0.296 | 0.423 | 0.128 | 0.797 | 0.303 | 0.586 | 0.333 | 0.563 |
| WINDOW_MEDIAN | 60 | 19 | 0.146 | 0.12 | 0.128 | 0.935 | 0.477 | 0.647 | 0.443 | 0.705 |
| WINDOW_MEAN | 15 | 6 | 0.156 | 0.029 | 0.365 | 0.817 | 0.387 | 0.816 | 0.374 | -0.706 |
| WINDOW_MEAN | 30 | 9 | -0.132 | -0.2 | 0.429 | 0.893 | 0.345 | 0.643 | 0.343 | -0.186 |
| WINDOW_MEAN | 45 | 13 | 0.3 | 0.363 | 0.287 | 0.702 | 0.303 | 0.523 | 0.333 | 0.544 |
| WINDOW_MEAN | 60 | 19 | 0.272 | 0.075 | 0.147 | 0.892 | 0.477 | 0.57 | 0.443 | 0.723 |
| CAR_BALANCED_MEAN | 15 | 6 | 0.156 | 0.029 | 0.365 | 0.817 | 0.387 | 0.816 | 0.374 | -0.706 |
| CAR_BALANCED_MEAN | 30 | 9 | -0.132 | -0.2 | 0.429 | 0.893 | 0.345 | 0.643 | 0.343 | -0.186 |
| CAR_BALANCED_MEAN | 45 | 13 | 0.3 | 0.363 | 0.287 | 0.702 | 0.303 | 0.523 | 0.333 | 0.544 |
| CAR_BALANCED_MEAN | 60 | 19 | 0.279 | 0.094 | 0.147 | 0.892 | 0.477 | 0.569 | 0.443 | 0.72 |
| CAR_BALANCED_COMMON_CARS | 15 | 3 | 0.993 | 0.5 | -0.053 | 0.06 | 0.509 | 0.067 | 0.386 | 0.985 |
| CAR_BALANCED_COMMON_CARS | 30 | 7 | 0.381 | -0.036 | -0.053 | 0.46 | 0.382 | 0.433 | 0.348 | 0.188 |
| CAR_BALANCED_COMMON_CARS | 45 | 9 | 0.303 | 0.033 | -0.053 | 0.658 | 0.341 | 0.41 | 0.337 | 0.151 |
| CAR_BALANCED_COMMON_CARS | 60 | 16 | 0.225 | -0.015 | 0.003 | 0.693 | 0.495 | 0.543 | 0.434 | 0.276 |

**How to read this:** `sd_team_adjusted > sd_delta_target` means subtracting the teammate control *adds* variance. For comparison, `sd_frozen_loyo_residual_same_subset` is the frozen physics model's out-of-year residual spread on the same transitions.

### Environmental fidelity of the control

Does the teammate control experience the same Δtrack and Δambient as the frozen target? For scale, the frozen |Δtrack| quartiles are [2.3, 5.56, 8.27] °C.

| strategy | window_min | n_nondegenerate | env_fidelity_corr_delta_track | env_fidelity_median_abs_diff_delta_track_c | env_fidelity_corr_delta_ambient | env_fidelity_median_abs_diff_delta_ambient_c |
|---|---|---|---|---|---|---|
| NEAREST | 15 | 6 | 0.24 | 1.667 | 0.995 | 0.125 |
| NEAREST | 30 | 9 | 0.219 | 1.667 | 0.976 | 0.158 |
| NEAREST | 45 | 13 | 0.649 | 1.667 | 0.931 | 0.277 |
| NEAREST | 60 | 19 | 0.735 | 2.105 | 0.862 | 0.329 |
| NEAREST | UNBOUNDED | 25 | 0.589 | 2.222 | 0.586 | 0.507 |
| MUTUAL_NEAREST | 15 | 6 | 0.24 | 1.667 | 0.995 | 0.125 |
| MUTUAL_NEAREST | 30 | 9 | 0.219 | 1.667 | 0.976 | 0.158 |
| MUTUAL_NEAREST | 45 | 13 | 0.649 | 1.667 | 0.931 | 0.277 |
| MUTUAL_NEAREST | 60 | 17 | 0.614 | 2.222 | 0.832 | 0.329 |
| MUTUAL_NEAREST | UNBOUNDED | 18 | 0.618 | 2.222 | 0.782 | 0.41 |
| WINDOW_MEDIAN | 15 | 6 | 0.24 | 1.667 | 0.995 | 0.125 |
| WINDOW_MEDIAN | 30 | 9 | 0.23 | 2.5 | 0.942 | 0.444 |
| WINDOW_MEDIAN | 45 | 13 | 0.688 | 2.222 | 0.849 | 0.494 |
| WINDOW_MEDIAN | 60 | 19 | 0.681 | 2.222 | 0.789 | 0.494 |
| WINDOW_MEAN | 15 | 6 | 0.24 | 1.667 | 0.995 | 0.125 |
| WINDOW_MEAN | 30 | 9 | 0.23 | 2.5 | 0.942 | 0.444 |
| WINDOW_MEAN | 45 | 13 | 0.688 | 2.222 | 0.849 | 0.494 |
| WINDOW_MEAN | 60 | 19 | 0.681 | 2.222 | 0.789 | 0.494 |
| CAR_BALANCED_MEAN | 15 | 6 | 0.24 | 1.667 | 0.995 | 0.125 |
| CAR_BALANCED_MEAN | 30 | 9 | 0.23 | 2.5 | 0.942 | 0.444 |
| CAR_BALANCED_MEAN | 45 | 13 | 0.688 | 2.222 | 0.849 | 0.494 |
| CAR_BALANCED_MEAN | 60 | 19 | 0.681 | 2.222 | 0.789 | 0.494 |
| CAR_BALANCED_COMMON_CARS | 15 | 3 | 0.563 | 1.667 | 1 | 0.006 |
| CAR_BALANCED_COMMON_CARS | 30 | 7 | 0.064 | 3.333 | 0.901 | 0.78 |
| CAR_BALANCED_COMMON_CARS | 45 | 9 | 0.485 | 2.222 | 0.873 | 0.696 |
| CAR_BALANCED_COMMON_CARS | 60 | 16 | 0.461 | 3.333 | 0.751 | 0.75 |

### Case table: same-teammate-car (common-car) control, ±60 min, any direction

| year | canonical_engineering_team | target_driver | cars_t1 | cars_t2 | delta_target | delta_team_control | team_adjusted_delta | frozen_loyo_residual_raw_mph | degenerate_identical_control | control_equals_other_frozen_transition | reciprocal_frozen_pair |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020 | ED_CARPENTER_RACING | Ed Carpenter | 47 | 47 | 0.4 | 0.071 | 0.329 | -0.028 | False | Conor Daly #47 | True |
| 2020 | ED_CARPENTER_RACING | Conor Daly | 20 | 20 | 0.071 | 0.4 | -0.329 | -0.293 | False | Ed Carpenter #20 | True |
| 2020 | CHIP_GANASSI_RACING | Marcus Ericsson | 9 | 9 | 0.094 | 0.01 | 0.084 | -0.18 | False |  | False |
| 2020 | CHIP_GANASSI_RACING | Scott Dixon | 8 | 8 | -0.041 | 0.094 | -0.135 | -0.446 | False | Marcus Ericsson #8 | False |
| 2020 | CHIP_GANASSI_RACING | Scott Dixon | 8 | 8 | 0.102 | 0 | 0.102 | -0.089 | True |  | False |
| 2021 | ANDRETTI | Stefan Wilson | 98 | 98 | -0.02 | 0.611 | -0.631 | -0.29 | False | Marco Andretti #98 | True |
| 2021 | ANDRETTI | Stefan Wilson | 26|98 | 26|98 | -0.062 | -0.71 | 0.648 | 0.08 | False |  | False |
| 2021 | ANDRETTI | Colton Herta | 25 | 25 | -1.419 | -0.062 | -1.357 | -1.193 | False | Stefan Wilson #25 | False |
| 2021 | ARROW_MCLAREN_SPM | Felix Rosenqvist | 86 | 86 | 0.246 | -0.154 | 0.4 | 0.284 | False | Juan Pablo Montoya #86 | True |
| 2021 | ARROW_MCLAREN_SPM | Juan Pablo Montoya | 7 | 7 | -0.154 | 0.246 | -0.4 | -0.137 | False | Felix Rosenqvist #7 | True |
| 2021 | ANDRETTI | Marco Andretti | 25 | 25 | 0.611 | -0.02 | 0.631 | 0.079 | False | Stefan Wilson #25 | True |
| 2021 | ANDRETTI | Marco Andretti | 25 | 25 | -0.002 | -0.062 | 0.06 | 0.198 | False | Stefan Wilson #25 | False |
| 2023 | ANDRETTI | Kyle Kirkwood | 29 | 29 | 0.227 | 0.08 | 0.147 | 0.177 | False | Devlin DeFrancesco #29 | True |
| 2023 | ANDRETTI | Devlin DeFrancesco | 27 | 27 | 0.08 | 0.227 | -0.147 | -0.09 | False | Kyle Kirkwood #27 | True |
| 2023 | CHIP_GANASSI_RACING | Marcus Ericsson | 9 | 9 | -0.314 | 0.461 | -0.775 | -0.404 | False | Scott Dixon #9 | False |
| 2023 | CHIP_GANASSI_RACING | Marcus Ericsson | 9 | 9 | 0.609 | 0 | 0.609 | 0.556 | True |  | False |
| 2023 | CHIP_GANASSI_RACING | Scott Dixon | 8 | 8 | 0.461 | -0.01 | 0.471 | 0.307 | False |  | False |
| 2023 | ARROW_MCLAREN_SPM | Felix Rosenqvist | 66 | 66 | 0.848 | 0.901 | -0.053 | 0.8 | False |  | False |
| 2024 | ARROW_MCLAREN_SPM | Pato O'Ward | 6|7 | 6|7 | 0.601 | 0 | 0.601 | 0.551 | True |  | False |

## 8–9. Sensitivity to strategy and window

- **Nearest, median, mean and car-balanced mean are identical up to ±15 min,** because each supported endpoint then has one teammate attempt. From ±20 min, windows start to hold several attempts and the strategies diverge.
- **Car-balancing is identical to the plain window mean up to ±45 min** (no window yet holds several attempts from one teammate car). At ±60 min it differs only slightly.
- **All strategies except common-car let the teammate car differ between T1 and T2.** Their control change then includes a car-to-car speed offset. This shows up as `sd_team_adjusted` well above `sd_delta_target`.
- **Common-car controls fix composition, but most of them are another frozen transition:** 6 of 7 at ±30 min and 12 of 16 at ±60 min. Many are reciprocal pairs, so they carry no information independent of the frozen core.
- **Window:** support at both endpoints rises from 0 (±5) to 9 (±30) to 21 (±60), and to 35 unbounded (of which 10 are degenerate). The same-direction fraction is unstable at 0.43–1.0 because n is small.

## 10. Dependence / reuse

| strategy | window_min | direction | unique_frozen_transitions | unique_target_cars | unique_teammate_cars | unique_teammate_relationships | unique_teams | unique_canonical_teams | unique_years | teammate_attempt_uses | unique_teammate_attempts_used | teammate_attempts_reused | max_reuse_of_one_teammate_attempt | share_of_uses_that_are_reused | controls_equal_to_another_frozen_transition | reciprocal_frozen_transition_pairs | transitions_sharing_attempt_across_own_endpoints |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NEAREST | 15 | ANY | 6 | 4 | 7 | 7 | 3 | 3 | 2 | 12 | 10 | 2 | 2 | 0.333 | 2 | 1 | 0 |
| NEAREST | 30 | ANY | 9 | 7 | 12 | 13 | 5 | 3 | 3 | 18 | 15 | 3 | 2 | 0.333 | 2 | 1 | 0 |
| NEAREST | 45 | ANY | 13 | 11 | 17 | 19 | 7 | 5 | 3 | 26 | 23 | 3 | 2 | 0.231 | 4 | 2 | 0 |
| NEAREST | 60 | ANY | 21 | 17 | 23 | 27 | 9 | 5 | 4 | 42 | 33 | 8 | 3 | 0.405 | 8 | 3 | 2 |
| NEAREST | UNBOUNDED | ANY | 35 | 28 | 37 | 43 | 17 | 8 | 4 | 70 | 48 | 17 | 4 | 0.557 | 9 | 3 | 10 |
| MUTUAL_NEAREST | 15 | ANY | 6 | 4 | 7 | 7 | 3 | 3 | 2 | 12 | 10 | 2 | 2 | 0.333 | 2 | 1 | 0 |
| MUTUAL_NEAREST | 30 | ANY | 9 | 7 | 12 | 13 | 5 | 3 | 3 | 18 | 15 | 3 | 2 | 0.333 | 2 | 1 | 0 |
| MUTUAL_NEAREST | 45 | ANY | 13 | 11 | 17 | 19 | 7 | 5 | 3 | 26 | 23 | 3 | 2 | 0.231 | 4 | 2 | 0 |
| MUTUAL_NEAREST | 60 | ANY | 17 | 15 | 21 | 24 | 8 | 5 | 3 | 34 | 30 | 4 | 2 | 0.235 | 7 | 3 | 0 |
| MUTUAL_NEAREST | UNBOUNDED | ANY | 18 | 16 | 23 | 26 | 9 | 5 | 3 | 36 | 32 | 4 | 2 | 0.222 | 7 | 3 | 0 |
| WINDOW_MEDIAN | 15 | ANY | 6 | 4 | 7 | 7 | 3 | 3 | 2 | 12 | 10 | 2 | 2 | 0.333 | 2 | 1 | 0 |
| WINDOW_MEDIAN | 30 | ANY | 9 | 7 | 13 | 16 | 5 | 3 | 3 | 25 | 20 | 5 | 2 | 0.4 | 2 | 1 | 0 |
| WINDOW_MEDIAN | 45 | ANY | 13 | 11 | 23 | 27 | 7 | 5 | 3 | 40 | 33 | 7 | 2 | 0.35 | 3 | 1 | 0 |
| WINDOW_MEDIAN | 60 | ANY | 21 | 17 | 28 | 40 | 9 | 5 | 4 | 71 | 46 | 15 | 5 | 0.563 | 5 | 2 | 3 |
| WINDOW_MEAN | 15 | ANY | 6 | 4 | 7 | 7 | 3 | 3 | 2 | 12 | 10 | 2 | 2 | 0.333 | 2 | 1 | 0 |
| WINDOW_MEAN | 30 | ANY | 9 | 7 | 13 | 16 | 5 | 3 | 3 | 25 | 20 | 5 | 2 | 0.4 | 2 | 1 | 0 |
| WINDOW_MEAN | 45 | ANY | 13 | 11 | 23 | 27 | 7 | 5 | 3 | 40 | 33 | 7 | 2 | 0.35 | 3 | 1 | 0 |
| WINDOW_MEAN | 60 | ANY | 21 | 17 | 28 | 40 | 9 | 5 | 4 | 71 | 46 | 15 | 5 | 0.563 | 5 | 2 | 3 |
| CAR_BALANCED_MEAN | 15 | ANY | 6 | 4 | 7 | 7 | 3 | 3 | 2 | 12 | 10 | 2 | 2 | 0.333 | 2 | 1 | 0 |
| CAR_BALANCED_MEAN | 30 | ANY | 9 | 7 | 13 | 16 | 5 | 3 | 3 | 25 | 20 | 5 | 2 | 0.4 | 2 | 1 | 0 |
| CAR_BALANCED_MEAN | 45 | ANY | 13 | 11 | 23 | 27 | 7 | 5 | 3 | 40 | 33 | 7 | 2 | 0.35 | 3 | 1 | 0 |
| CAR_BALANCED_MEAN | 60 | ANY | 21 | 17 | 28 | 40 | 9 | 5 | 4 | 71 | 46 | 15 | 5 | 0.563 | 5 | 2 | 3 |
| CAR_BALANCED_COMMON_CARS | 15 | ANY | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 6 | 6 | 0 | 1 | 0 | 2 | 1 | 0 |
| CAR_BALANCED_COMMON_CARS | 30 | ANY | 7 | 5 | 5 | 5 | 3 | 2 | 2 | 14 | 12 | 2 | 2 | 0.286 | 6 | 3 | 0 |
| CAR_BALANCED_COMMON_CARS | 45 | ANY | 9 | 7 | 7 | 7 | 4 | 3 | 3 | 18 | 16 | 2 | 2 | 0.222 | 8 | 4 | 0 |
| CAR_BALANCED_COMMON_CARS | 60 | ANY | 19 | 15 | 16 | 17 | 8 | 4 | 4 | 44 | 34 | 7 | 3 | 0.386 | 12 | 4 | 3 |

Frozen transitions frequently act as each other's controls, so the frozen core and this layer are not independent.

## 11–12. Strongest years and teams (both-endpoint support, any direction)

| scope | ±10 | ±15 | ±20 | ±30 | ±45 | ±5 | ±60 |
|---|---|---|---|---|---|---|---|
| YEAR=2020 | 0 | 0 | 1 | 1 | 3 | 0 | 5 |
| YEAR=2021 | 0 | 4 | 6 | 6 | 7 | 0 | 8 |
| YEAR=2023 | 1 | 2 | 2 | 2 | 3 | 0 | 7 |
| YEAR=2024 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

| scope | ±10 | ±15 | ±20 | ±30 | ±45 | ±5 | ±60 |
|---|---|---|---|---|---|---|---|
| TEAM=ANDRETTI | 0 | 4 | 4 | 4 | 4 | 0 | 7 |
| TEAM=CHIP_GANASSI_RACING | 0 | 1 | 2 | 2 | 3 | 0 | 7 |
| TEAM=ARROW_MCLAREN_SPM | 1 | 1 | 3 | 3 | 3 | 0 | 4 |
| TEAM=ED_CARPENTER_RACING | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| TEAM=TEAM_PENSKE | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| TEAM=AJ_FOYT | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=CARLIN | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=DALE_COYNE_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=DRAGONSPEED | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=JUNCOS_HOLLINGER_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=MEYER_SHANK_RACING | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| TEAM=PARETTA_AUTOSPORT | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

2022 is absent from the frozen 41, so no 2022 transition can be anchored. It stays visible in the Phase 3 coverage reports. R6 (2018/2019/2025) is excluded from this reference-period analysis.

## 13. Quality limitations

See `phase4a_data_quality_report.md`. In short:
- Track temperature is past-safe PTSC on a 15-minute grid.
- Timestamps are approximate recorder captures. Rescued endpoints have minute-level or tighter-bound times.
- Some controls mix environment bases.
- Session state is unrecorded outside 2022.
- The teammate Δtrack tracks the target Δtrack only weakly within ±30 min.

## 14–15. Can a primary matching rule be selected? Recommendation (not implemented)

**Can a primary rule be selected now? Only in narrow form.**
- **The design is clear.** Only a composition-fixed control (the same teammate car or cars at both endpoints, car-balanced) avoids the car-to-car offset that inflates every other strategy.
- **The support is not.** Under that rule the independent (non-frozen, non-degenerate) evidence is only 1 transition at ±30 min and 4 at ±60 min.
- **The PIT-compatible version is smaller still.**
- **Consequence:** the teammate layer cannot serve as an independent statistical corroboration of the frozen β estimates in the 2020–2024 reference period.

**Recommended rule (for the Phase 4B design, not final):**
1. **Primary retrospective control:** `CAR_BALANCED_COMMON_CARS`, any direction, window **±30 min**. The window is justified physically, not by N: it is two PTSC 15-minute steps, and the median frozen transition spans ≈150 min, so ±30 min is ≲20% of the elapsed interval. Pre-declared sensitivities: ±15, ±45 and ±60.
2. **Explicitly partition** each matched control into:
   - independent of the frozen core;
   - equal to another frozen transition (reciprocal: report once, as a *pair consistency check*, not as corroboration);
   - degenerate (exclude).
3. **Unit of analysis:** the frozen transition, with reuse and reciprocity reported. No per-attempt pooling and no independence-based tests.
4. **PIT:** report prior-only support separately as operational-availability evidence only.
5. **Suggested use:** qualitative, case-level corroboration (sign and magnitude consistency, alongside environmental fidelity) rather than a quantitative coefficient check. Treat R6 2025 (the separate regime) as its own later analysis if broader teammate evidence is wanted.

## 16. Outputs

`frozen_transition_anchors.csv`, `frozen_transition_teammate_candidates.csv`, `endpoint_support_by_window.csv`, `matched_controls_nearest.csv`, `matched_controls_window_median.csv`, `matched_controls_window_mean.csv`, `matched_controls_car_balanced.csv`, `pit_prior_only_controls.csv`, `all_matched_controls.csv`, `strategy_summary.csv`, `dependence_audit.csv`, `phase4a_matching_report.md`, `phase4a_data_quality_report.md`, `phase4a_checks_log.txt`, `figures/fig1…fig8*.png`.
