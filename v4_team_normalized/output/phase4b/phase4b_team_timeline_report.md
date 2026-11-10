# V4 Phase 4B — Team Timeline Report (exploratory)

**Status:** exploratory reconstruction and description.
- No regression, fixed-effects or mixed-effects model was fitted, and no coefficient was estimated.
- The frozen 41 transitions and V2/V3 are untouched.
- Wherever a "frozen reference sign" appears, it comes from *applying* the published frozen coefficients to observed state changes. Nothing was re-estimated.

**Inputs:**
- Phase 3 `team_attempt_join.csv` (accepted registry; primary teammate layer only).
- Eras are never pooled:
  - Era A: 2018–19, pre-Aeroscreen extension.
  - Era B: 2020–24, frozen reference.
  - Era C: 2025, hybrid external.

**Performance timeline:** complete four-lap and timed attempts. Other primary-layer attempts stay in `team_timeline_long.csv`, each with a `timeline_exclusion_reason`.

## 1–4. Coverage (clustered data — attempts are not independent samples)

| scope | unique_years | unique_team_years | unique_teams | unique_cars | unique_drivers | unique_attempts |
|---|---|---|---|---|---|---|
| ALL_PRIMARY_ATTEMPTS | 8 | 97 | 18 | 270 | 74 | 511 |
| PERFORMANCE_TIMELINE | 8 | 76 | 17 | 166 | 63 | 240 |
| PERFORMANCE_TIMELINE|ERA_A_PRE_AEROSCREEN_EXT | 2 | 22 | 14 | 42 | 35 | 50 |
| PERFORMANCE_TIMELINE|ERA_B_FROZEN_REFERENCE | 5 | 42 | 15 | 93 | 47 | 135 |
| PERFORMANCE_TIMELINE|ERA_C_HYBRID_EXTERNAL | 1 | 12 | 12 | 31 | 31 | 55 |

| era | team_years | attempts_total | attempts_performance_timeline | team_years_ge2_cars | team_years_ge3_cars | panel_eligible | median_of_median_gaps_min |
|---|---|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 26 | 112 | 50 | 12 | 6 | 0 | 40.25 |
| ERA_B_FROZEN_REFERENCE | 59 | 326 | 135 | 27 | 15 | 10 | 50.56 |
| ERA_C_HYBRID_EXTERNAL | 12 | 73 | 55 | 11 | 5 | 7 | 60.16 |

- Team-years with ≥2 cars on the performance timeline: **50**. With ≥3 cars: **26**.
- `panel_eligible` means ≥2 cars *each* with ≥2 timed complete attempts. This is the minimum for any within-car/between-car separation. **17** team-years qualify: 10 in Era B, 7 in Era C, and 0 in Era A.

## 5. Densest team-year timelines (≥5 timed complete attempts)

| era | year | canonical_engineering_team | attempts_on_performance_timeline | cars_on_performance_timeline | cars_with_2plus_timeline_attempts | timeline_span_min | median_gap_min | max_gap_min | consecutive_same_car | consecutive_car_switch | frozen_core_attempts_on_timeline | panel_eligible |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | 11 | 6 | 3 | 319.7 | 13.6 | 102.5 | 0 | 10 | 8 | True |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | 8 | 4 | 2 | 389 | 44 | 107.2 | 1 | 6 | 0 | True |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | 8 | 4 | 3 | 273.5 | 41.3 | 73.8 | 0 | 7 | 7 | True |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | 7 | 4 | 3 | 330.1 | 34.5 | 164.3 | 1 | 5 | 0 | True |
| ERA_B_FROZEN_REFERENCE | 2023 | ARROW_MCLAREN_SPM | 7 | 4 | 2 | 308.6 | 29 | 141.4 | 1 | 5 | 5 | True |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | 7 | 3 | 2 | 344.5 | 60.2 | 88.2 | 1 | 5 | 0 | True |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | 7 | 4 | 3 | 283 | 33.8 | 150.6 | 0 | 6 | 0 | True |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | 6 | 3 | 3 | 163 | 38 | 69 | 1 | 4 | 2 | True |
| ERA_B_FROZEN_REFERENCE | 2020 | ANDRETTI | 6 | 5 | 1 | 191.8 | 28.3 | 101.8 | 1 | 4 | 2 | False |
| ERA_B_FROZEN_REFERENCE | 2020 | CHIP_GANASSI_RACING | 6 | 3 | 2 | 229.2 | 47.5 | 98.3 | 0 | 5 | 5 | True |
| ERA_B_FROZEN_REFERENCE | 2021 | TEAM_PENSKE | 6 | 4 | 2 | 294.8 | 37.5 | 169 | 0 | 5 | 4 | True |
| ERA_B_FROZEN_REFERENCE | 2021 | ED_CARPENTER_RACING | 5 | 3 | 2 | 192.6 | 51.7 | 66 | 0 | 4 | 4 | True |
| ERA_B_FROZEN_REFERENCE | 2021 | ARROW_MCLAREN_SPM | 5 | 3 | 2 | 249.9 | 19 | 207 | 0 | 4 | 4 | True |
| ERA_B_FROZEN_REFERENCE | 2021 | AJ_FOYT | 5 | 4 | 1 | 270 | 37.1 | 190.8 | 0 | 4 | 2 | False |
| ERA_B_FROZEN_REFERENCE | 2020 | ED_CARPENTER_RACING | 5 | 3 | 2 | 224.2 | 50.8 | 109.2 | 0 | 4 | 4 | True |
| ERA_C_HYBRID_EXTERNAL | 2025 | JUNCOS_HOLLINGER_RACING | 5 | 2 | 2 | 355.8 | 77.3 | 134.4 | 0 | 4 | 0 | True |
| ERA_B_FROZEN_REFERENCE | 2023 | ANDRETTI | 5 | 2 | 2 | 227 | 52.4 | 109.9 | 1 | 3 | 5 | True |

## 6. Weakest cases

| era | team_years_with_0_timed_complete | team_years_with_1_timed_complete | team_years_single_car_on_timeline |
|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 4 | 9 | 10 |
| ERA_B_FROZEN_REFERENCE | 17 | 10 | 15 |
| ERA_C_HYBRID_EXTERNAL | 0 | 1 | 1 |

2022 (kept visible, not forced; no weather exists for it):

| canonical_engineering_team | attempts_total | attempts_timed | attempts_on_performance_timeline |
|---|---|---|---|
| AJ_FOYT | 3 | 0 | 0 |
| ANDRETTI | 8 | 0 | 0 |
| ARROW_MCLAREN_SPM | 3 | 2 | 2 |
| CHIP_GANASSI_RACING | 5 | 0 | 0 |
| DALE_COYNE_RACING | 4 | 0 | 0 |
| DRAGONSPEED | 1 | 0 | 0 |
| DREYER_REINBOLD_RACING | 4 | 0 | 0 |
| ED_CARPENTER_RACING | 3 | 1 | 1 |
| JUNCOS_HOLLINGER_RACING | 2 | 0 | 0 |
| MEYER_SHANK_RACING | 3 | 0 | 0 |
| RAHAL_LETTERMAN_LANIGAN | 3 | 0 | 0 |
| TEAM_PENSKE | 5 | 2 | 1 |

## 7. Sampling gaps

The median of team-year median gaps is shown per era above. The densest timeline (2021 Andretti, 11 attempts over ≈320 min) has a 14-min median gap but a 103-min maximum gap. Across the 17 panel-eligible team-years, median gaps run 14–113 min, and 12 of them have a maximum gap above 100 min. No team samples the track continuously.

## 9. Car/time confounding summary

See `phase4b_sampling_bias_report.md`.

| era | LOW | MODERATE | NOT_ASSESSABLE | SEVERE |
|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 0 | 0 | 12 | 10 |
| ERA_B_FROZEN_REFERENCE | 5 | 4 | 23 | 10 |
| ERA_C_HYBRID_EXTERNAL | 5 | 1 | 2 | 4 |

## 10–11. What the raw and centered timelines show

**Raw timelines (`figures/raw_timelines/`):**
- The between-car level differences within a team (often 0.5–2 mph) are as large as or larger than any within-session movement.
- Many team-years hold one attempt per car, so the "timeline" is a sequence of *different cars*, and car identity and time cannot be separated.

**Centered timelines (`figures/centered_timelines/`):**
- Only cars with ≥2 timed complete attempts carry information; single-attempt cars center to 0 by construction and are drawn hollow.
- **Circularity:** in Era B, almost every informative centered attempt is a frozen same-car core attempt.

| era | centering_informative_attempts | of_which_frozen_core_attempts | cars | team_years |
|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 14 | 0 | 6 | 6 |
| ERA_B_FROZEN_REFERENCE | 77 | 73 | 35 | 22 |
| ERA_C_HYBRID_EXTERNAL | 43 | 0 | 19 | 10 |

So in 2020–2024 the centered team timeline mostly re-displays the frozen same-car transitions on a shared clock. It adds no new independent within-car information. Era C (2025) is the only era whose centered information is independent of the frozen core, and it is a different technical regime.

## 12–13. Is common movement apparent?

**Within-car time-trend sign** (Spearman of speed vs session time, per car with ≥2 timed complete attempts):

| era | team_years | all_cars_same_sign | cars | cars_positive_trend | cars_negative_trend |
|---|---|---|---|---|---|
| ERA_B_FROZEN_REFERENCE | 10 | 7 | 23 | 19 | 4 |
| ERA_C_HYBRID_EXTERNAL | 7 | 4 | 16 | 13 | 3 |

- In Era B, most cars go *faster* later in the session.
- Track temperature rises over the same period, so the frozen physics would predict slower speeds from the track term; the ambient term works the other way.
- A positive time trend therefore cannot be read as a track-temperature effect. It is equally consistent with deliberate repeat-attempt improvement (setup/trim changes, and the choice to re-run only when an improvement is expected).

**Centered speed vs physical state** (Spearman within team-year; descriptive; n = 5–8, clustered):

| era | year | canonical_engineering_team | n | cars | rho_centered_track | rho_centered_ambient | rho_raw_track | rho_centered_time |
|---|---|---|---|---|---|---|---|---|
| ERA_B_FROZEN_REFERENCE | 2020 | CHIP_GANASSI_RACING | 5 | 2 | 0.56 | 0.6 | 0.15 | 0.6 |
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | 8 | 3 | -0.35 | -0.26 | 0.2 | -0.07 |
| ERA_B_FROZEN_REFERENCE | 2023 | ANDRETTI | 5 | 2 | 0.72 | 0.6 | 0.67 | 0.9 |
| ERA_B_FROZEN_REFERENCE | 2023 | ARROW_MCLAREN_SPM | 5 | 2 | 0.82 | 0.6 | 0.21 | 0.9 |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | 7 | 3 | 0.04 | 0.5 | 0.15 | 0.64 |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | 5 | 3 | 0.56 | 0.67 | 0.97 | 0.5 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | 6 | 2 | -0.6 | -0.2 | -0.03 | 0.03 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | 6 | 3 | 0.49 | 0.85 | 0.09 | 0.83 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | 6 | 2 | -0.2 | 0.54 | -0.26 | 0.54 |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | 6 | 3 | -0.83 | 0.58 | -0.6 | 0.6 |

- **Era B:** the centered–track correlation is mostly *positive* and close to the centered–time correlation, because track temperature, ambient temperature and session time move together there.
- **Era C (2025):** centered speed vs ambient is positive in all 4 assessable team-years, while centered vs track is mixed. Every one of these rests on n = 6 clustered attempts, so it is suggestive at most.

**Session-time tertiles** (mean centered speed with car composition):

| era | year | canonical_engineering_team | tertile | n | cars | mean_centered | mean_track | mean_ambient | dispersion_centered_sd |
|---|---|---|---|---|---|---|---|---|---|
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | EARLY | 3 | 3 | 0.11 | 35.56 | 26.04 | 0.56 |
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | MID | 2 | 2 | 0.11 | 41.11 | 28.68 | 0.13 |
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | LATE | 3 | 3 | -0.19 | 47.04 | 28.74 | 0.47 |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | EARLY | 3 | 3 | -0.15 | 35.56 | 16.34 | 0.14 |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | MID | 2 | 2 | -0.04 | 44.69 | 18.7 | 0.38 |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | LATE | 2 | 2 | 0.27 | 44.44 | 18.66 | 0.05 |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | EARLY | 2 | 2 | -0.15 | 48.89 | 25.4 | 0.14 |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | MID | 2 | 1 | 0 | 50 | 27.56 | 0.42 |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | LATE | 2 | 2 | 0.15 | 50.56 | 27.12 | 0.14 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | EARLY | 2 | 2 | 0.12 | 42.51 | 21.49 | 0.14 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | MID | 2 | 2 | -0.15 | 43.01 | 22.23 | 0.18 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | LATE | 2 | 1 | 0.03 | 39.13 | 22.68 | 0.27 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | EARLY | 2 | 2 | -0.26 | 37.17 | 20.45 | 0.7 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | MID | 2 | 2 | -0.44 | 42.4 | 21.39 | 0.28 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | LATE | 2 | 2 | 0.69 | 42.52 | 22.56 | 0.08 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | EARLY | 2 | 2 | -0.08 | 38.8 | 20.35 | 0.05 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | MID | 2 | 1 | -0.03 | 42.92 | 21.94 | 0.25 |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | LATE | 2 | 2 | 0.12 | 39.94 | 22.73 | 0 |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | EARLY | 2 | 2 | -0.18 | 41.84 | 20.99 | 0.09 |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | MID | 2 | 1 | -0 | 42.58 | 22.48 | 0.82 |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | LATE | 2 | 2 | 0.18 | 39.46 | 22.78 | 0.09 |

**Consecutive team observations, sign agreement with the frozen reference sign** (the frozen coefficients applied to Δtrack/Δambient; not a test):

| summary | era | n | pair_type | fraction_same_sign | unique_years | unique_team_years | unique_teams | unique_cars | unique_attempts |
|---|---|---|---|---|---|---|---|---|---|
| consecutive_sign_vs_frozen_reference | ERA_A_PRE_AEROSCREEN_EXT | 6 | SAME_CAR | 0.67 | 1 | 5 | 5 | 5 | 11 |
| consecutive_sign_vs_frozen_reference | ERA_B_FROZEN_REFERENCE | 28 | DIFFERENT_CAR | 0.57 | 4 | 10 | 5 | 23 | 43 |
| consecutive_sign_vs_frozen_reference | ERA_B_FROZEN_REFERENCE | 12 | SAME_CAR | 0.67 | 4 | 12 | 8 | 12 | 24 |
| consecutive_sign_vs_frozen_reference | ERA_C_HYBRID_EXTERNAL | 23 | DIFFERENT_CAR | 0.52 | 1 | 7 | 7 | 16 | 33 |
| consecutive_sign_vs_frozen_reference | ERA_C_HYBRID_EXTERNAL | 7 | SAME_CAR | 0.86 | 1 | 7 | 7 | 7 | 14 |

- Different-car consecutive changes agree with the frozen reference sign about as often as a coin flip (≈0.5–0.6).
- Same-car pairs agree more often, but in Era B they are frozen-core transitions themselves.

**Assessment:** there is no clear, consistent common movement across cars.
- Where cars move together (e.g. 2023 Chip Ganassi, 2024 Arrow McLaren, 2025 Rahal: all cars trending up), the pattern is inseparable from session time and from repeat-attempt selection.
- Where the data are densest (2021 Andretti), cars disagree in direction.
- The pattern is concentrated in a few team-years and is not consistent across teams or years.

## 14. Frozen same-car transitions in team context

| year | NONE (no timed teammate attempts) | OUTSIDE_ONLY (teammates only before/after) | RICH (>=2 teammate cars between endpoints) | SOME (1 teammate car between endpoints) |
|---|---|---|---|---|
| 2020 | 3 | 2 | 3 | 3 |
| 2021 | 0 | 1 | 9 | 4 |
| 2023 | 1 | 3 | 5 | 4 |
| 2024 | 1 | 1 | 0 | 0 |

The frozen transitions do sit inside team timelines, and many have teammate attempts between their endpoints. That gives useful *visual context* (see `figures/priority_cases/`). But most of those teammate attempts are themselves frozen-core endpoints, so the context is largely the frozen core seen from another car, not independent corroboration.

## 15–17. Does the representation justify formal panel modelling in Phase 4C?

**Not as a primary corroboration of the frozen reference-era coefficients.** Only a narrow, explicitly exploratory Phase 4C is defensible. The reasons:
1. **Too few usable clusters.** Era B has 10 panel-eligible team-years and Era A has none.
2. **Circularity.** Era B's within-car variation is ≈95% the frozen same-car data.
3. **Collinear environment in Eras A and B.** Within team-years there, track temperature is almost collinear with session time and with ambient (median correlations: Era B 0.95 and 0.95). Era C (2025) is the exception (0.31 and 0.50): within 2025 team-years, track temperature moved much less monotonically with session time.
4. **Coarse track temperature.** Track temperature is quantised on 15-minute PTSC steps.
5. **Confounding.** Car identity and time are confounded (SEVERE in about half of the assessable team-years).
6. **Selection.** Attempt timing is strategic, not random.

**If Phase 4C proceeds**, plausible model families are:
- (a) a within-team-year car fixed-effects panel with a common session-time or state term and team-year-clustered uncertainty;
- (b) a hierarchical/mixed model with car-in-team-year random intercepts and possibly team-year random slopes;
- (c) a common latent session trend (state-space or dynamic factor) with car offsets.

Every one of these must be estimated **separately per era**, with Era C (2025, independent of the frozen core) as the only genuinely out-of-sample setting. They should be framed as *descriptions of within-team co-movement*, not as environmental coefficients.

**Remaining identification problems:**
- time vs environment collinearity;
- track vs ambient collinearity;
- car–time confounding;
- strategic selection of when and whether to re-run, including withdrawals of retained times;
- unobserved setup, tyre and fuel changes between attempts;
- 15-minute track quantisation;
- approximate timestamps;
- unreconstructed interruptions outside 2022;
- small numbers of clusters;
- circular re-use of the frozen core in Era B.

## Priority visual review (4B.16)

The cases were selected by pre-declared rules (`priority_case_selection.csv`), not by appearance. They include negative and messy cases.

| year | canonical_engineering_team | selection_rule | attempts_on_performance_timeline | cars_with_2plus_timeline_attempts | weather_coverage | frozen_core_attempts_on_timeline | confounding_severity |
|---|---|---|---|---|---|---|---|
| 2021 | ANDRETTI | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_B_FROZEN_REFERENCE | 11 | 3 | 1 | 8 | MODERATE |
| 2023 | CHIP_GANASSI_RACING | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_B_FROZEN_REFERENCE | 8 | 3 | 1 | 7 | LOW |
| 2023 | ARROW_MCLAREN_SPM | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_B_FROZEN_REFERENCE | 7 | 2 | 1 | 5 | MODERATE |
| 2024 | ARROW_MCLAREN_SPM | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_B_FROZEN_REFERENCE | 6 | 3 | 0.83 | 2 | LOW |
| 2025 | ANDRETTI | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_C_HYBRID_EXTERNAL | 8 | 2 | 1 | 0 | SEVERE |
| 2025 | ARROW_MCLAREN_SPM | RULE1_DENSEST_PANEL_ELIGIBLE_ERA_C_HYBRID_EXTERNAL | 7 | 3 | 1 | 0 | LOW |
| 2020 | ANDRETTI | RULE2_DENSEST_SEVERE_CONFOUNDING_NEGATIVE_CASE | 6 | 1 | 1 | 2 | SEVERE |
| 2022 | ARROW_MCLAREN_SPM | RULE3_2022_WEATHER_TIMING_GAP_CASE | 2 | 0 | 0 | 0 | NOT_ASSESSABLE |
| 2019 | ANDRETTI | RULE3_DENSEST_ERA_A_CASE | 4 | 1 | 1 | 0 | SEVERE |
