# V4 Phase 4C — Pre-specified Exploratory Analysis (2025 within-team panel)

**Status:** written and committed **before** any Phase 4C model was fitted or any Phase 4C coefficient was inspected. The primary definitions below are not changed after results are known. Any technical failure (rank deficiency, non-convergence, boundary estimates, too few observations) is reported as a result. No more favourable model is substituted.

**Purpose:** a falsification and sensitivity exercise, *not* validation.

**Question:** within the independent 2025 hybrid-era Day 1 qualifying data, after accounting for persistent car-specific offsets, is there evidence of a shared session-time and/or observed physical-state structure across cars of the same engineering teams?

**Not asked:**
- whether the frozen 2020–2024 coefficients are correct;
- whether teammate data validate V2;
- causality;
- pooling 2025 with 2020–2024;
- replacing FINAL_V2.

## 0. Prior-knowledge disclosure

Before this specification was written, Phase 4B showed the following 2025 *descriptive* results:
- Spearman correlations of within-car centered speed vs track, ambient and time for 4 team-years;
- within-car time-trend signs (13 of 16 cars positive);
- team-year track–time and track–ambient correlations (median 0.31 and 0.50).

No regression on 2025 has been run. The specification below was fixed without reference to any fitted coefficient.

## 1. Data source and population

- **Source:** `v4_team_normalized/output/phase4b/team_timeline_long.csv`, read-only. It derives from the accepted Phase 3 join and V4 registry.
- **Year:** 2025 only (`era == ERA_C_HYBRID_EXTERNAL`). No 2018–2024 row and no frozen-core attempt may enter.
- **Row eligibility (P_all):**
  - `primary_teammate_layer == True`;
  - `on_performance_timeline == True`, meaning a complete four-lap attempt with a usable timestamp;
  - non-missing `four_lap_average_speed_mph`.
- **Team eligibility (determined once, on P_all):** a canonical team is eligible if, among its P_all rows:
  - there are ≥2 distinct cars (by registry car number); and
  - ≥2 of those cars each have ≥2 rows.

  All P_all rows of eligible teams form the analysis population, including rows of cars that have only one attempt. Such single-attempt cars are retained but contribute nothing to within-car slopes under car fixed effects. They are counted, not dropped.
- **Weather complete-case population (P_wx):** P_all-eligible rows with both `track_temp_c` and `ambient_temp_c` observed. No imputation. Team eligibility is **not** re-evaluated after this filter; cars left with one weather-complete row become uninformative and are reported.
- **Primary model comparison (M0–M3, M4, mixed models, S1, LOTO, LOCO):** all on **P_wx**, so every model is fitted to identical rows.
- **Secondary:** M0 and M1 also on P_all, to show the effect of the weather filter.
- **Reported before fitting:** number of teams, cars, drivers and attempts; attempts per car; attempts per team (`analysis_population.csv`).

## 2. Variables

| Symbol | Definition |
|---|---|
| `speed` | `four_lap_average_speed_mph` (outcome, mph) |
| `car` | `registry_car_number` within 2025 (the accepted V4 registry entry) |
| `team` | `canonical_engineering_team` (accepted V4 registry) |
| `session_time` | minutes since the earliest non-missing `attempt_timestamp_utc` among **all** 2025 rows of `v4_team_normalized/output/phase3/team_attempt_join.csv` (any team, complete or not). The origin is fixed by this rule, not by model performance. |
| `track` | `track_temp_c` (°C; 2025 = PTSC linear interpolation between 15-min observations, as reconstructed in Phase 3) |
| `ambient` | `ambient_temp_c` (°C; 2025 = PTSC ambient linear interpolation) |
| `repeat_attempt` | S1 only: 1 if the car has an earlier *timed* 2025 Day 1 attempt (complete or not) in the Phase 4B timeline (`car_timeline_order > 1`), else 0. Untimed earlier attempts cannot be seen; this limitation is reported. |

- **Excluded:**
  - **Solar:** not available for 2025, and not fabricated.
  - **Wind:** raw PTSC units are unverified. It is kept as metadata only and never used as a predictor.
- **Scaling:** no rescaling of predictors. `beta_time` is reported per minute and per 60 minutes.

## 3. Pre-model identifiability diagnostics (computed and reported before regression)

On P_wx:
- Pearson and Spearman correlations: track–time, ambient–time, track–ambient.
- Number of distinct values of track and ambient (rounded to 0.001 °C), plus their ranges.
- Within-car SD and range of track, ambient and time, for cars with ≥2 rows.
- Within-team SD and range of the same.
- Car/time and team/time confounding, measured as η² of session_time on car and on team.
- Variance inflation factors of the *within-car-demeaned* predictors, for the M3 design and for M2. Also the condition number of the within-demeaned, column-standardised M3 design.
- Scatterplots with raw observations: track vs time, ambient vs time, track vs ambient.

**Identifiability flag (pre-declared):** a physical term is "weakly identified" if its within-demeaned VIF is ≥ 10 in the relevant model.

## 4. Models (all OLS unless stated; car fixed effects = one dummy per car, no global intercept)

| Model | Specification |
|---|---|
| M0 | speed = α_car + ε |
| M1 | speed = α_car + β_time·time + ε |
| M2 | speed = α_car + β_track·track + β_ambient·ambient + ε |
| M3 | speed = α_car + β_time·time + β_track·track + β_ambient·ambient + ε |
| M4 | speed = γ_team + Σ_car-within-team δ (effect-coded, sum-to-zero within team) + β_track·track + β_ambient·ambient + ε |
| S1 (strategy sensitivity; not primary) | M2 + β_rep·repeat_attempt |

- **Estimability:** if the design matrix is rank-deficient, the model is recorded as `NOT_ESTIMABLE`, with its rank and column count. No columns are dropped automatically.
- **M4:** each car belongs to exactly one team, so team dummies plus a full set of car dummies are collinear. M4 is therefore the *reparameterisation* with team intercepts plus effect-coded car-within-team deviations. It must reproduce M2's fitted values and slopes exactly. The rank of the redundant "team dummies + all car dummies" design is also reported, to document the collinearity.
- **Uncertainty (reported with every coefficient):**
  1. Classical OLS standard errors.
  2. CR1 cluster-robust standard errors clustered by **car**, with G−1 degrees of freedom.
  3. CR1 clustered by **team**, with G−1 degrees of freedom. This is flagged unreliable because G ≈ 7.
  4. Cluster (pairs) bootstrap resampling **cars** with replacement; each resampled car is a distinct cluster. B = 2000, seed 20250517, percentile 95% interval, plus the fraction of draws that are estimable.
  5. Cluster bootstrap resampling **teams**, with the same B and seed and the same limitations flag.

  p-values, if shown, are exploratory and secondary. The number of clusters limits all inference.

## 5. Mixed-effects sensitivity (statsmodels MixedLM, REML, default optimiser settings, one attempt each)

| Model | Specification |
|---|---|
| MX1 | speed ~ track + ambient; `groups = team`, `re_formula = "1"` (team random intercept), `vc_formula = {"car": "0 + C(car)"}` (car-within-team random intercept) |
| MX2 | MX1 + session_time |

- **Recorded for each:** the converged flag, all warnings (including convergence and boundary/singular warnings), variance components and the fixed effects with standard errors.
- **No refits with altered random-effects structures.**

## 6. Within-transformation check

- **Construction:** within P_wx, demean speed, time, track and ambient by car. Then fit OLS without an intercept for the M1, M2 and M3 equivalents.
- **Expectation:** slopes must equal the corresponding car-fixed-effects slopes to within 1e-8 (absolute).
- **If they disagree:** investigate and report why.

## 7. Stability

- **Leave-one-team-out (LOTO):** for each eligible team, drop all its rows from P_wx and refit M1, M2 and M3. Report β_time, β_track and β_ambient, the population counts, and estimability. Failures are kept in the output.
- **Leave-one-car-out (LOCO):** for each car with ≥2 P_wx rows, drop that car and refit M1, M2 and M3. Dropping a single-row car cannot change the slopes, so it is not repeated; this is stated. Summary per term: median, minimum, maximum, and the number of sign flips relative to the full-sample sign.
- **Use:** neither LOTO nor LOCO is used to choose a coefficient.

## 8. Model comparison (descriptive)

**Measures:**
- residual sum of squares and residual SD;
- within-car R² relative to M0;
- Gaussian log-likelihood, AIC and BIC (parameters = regression columns + 1 variance);
- adjusted increment over M0;
- coefficient stability (LOTO, LOCO, bootstrap).

**Key comparisons:** M0 vs M2 (does physical state add information beyond the car baseline?) and **M2 vs M3** (is physical state still identifiable once session time is included?). There is no winner-by-fit.

## 9. Frozen-model sign reference (context only)

The frozen reference era had β_track < 0 and β_ambient > 0. For M2 and M3, 2025 estimates are labelled:
- SAME_SIGN or OPPOSITE_SIGN, based on the full-sample point estimate;
- UNSTABLE_SIGN if any LOTO fit or more than one LOCO fit flips the sign.

This is not validation, and no numerical agreement is required.

## 10. Pre-declared interpretation rules

These are evaluated mechanically after fitting. Every satisfied criterion is reported. The headline follows the precedence **D → B → C → A**.

| Case | Criterion |
|---|---|
| **D (not identified)** | M2 or M3 NOT_ESTIMABLE, **or** the within-demeaned VIF of track or ambient is ≥ 10 in M2. |
| **B (not separable from session time)** | Not D, and for at least one physical term: its M3 estimate has the opposite sign to M2, **or** its absolute value in M3 is < 50% of M2 while its car-bootstrap 95% interval excludes 0 in M2 but includes 0 in M3, **or** its within-demeaned VIF in M3 is ≥ 10. |
| **C (unstable / dominated by one team or car)** | Not D, and for a physical term in M2 or M3: ≥1 LOTO sign flip, **or** ≥2 LOCO sign flips, **or** removing a single team changes the estimate by more than 100% of the full-sample absolute value. |
| **A (stable shared physical-state structure)** | None of B, C or D; the physical terms keep the same sign in M2 and M3, with no LOTO sign flip and ≤1 LOCO sign flip. Even then, this is still not validation of the 2020–2024 coefficients. |

## 11. Forbidden actions

- Searching windows or alternative time origins.
- Removing teams or cars, except in the declared LOTO/LOCO sensitivity fits.
- Changing predictors after seeing signs.
- Nonlinear terms or interactions.
- Redefining the population.
- Selecting favourable plots.
- Tuning to p < 0.05.
- Using wind or solar.
- Imputing weather.

## 12. Figures

1. Track vs session time.
2. Ambient vs session time.
3. Raw speed vs time by team and car.
4. Within-car centered speed vs time.
5. Centered speed vs centered track.
6. Centered speed vs centered ambient.
7. Coefficients of M1, M2 and M3 with uncertainty.
8. LOTO stability.
9. LOCO stability.
10. Observed vs fitted for M2 and M3.

Raw observations are shown wherever applicable.

## 13. Software

Python 3.14, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, statsmodels 0.15.0 (installed into the local environment for this phase; the repository `requirements.txt` is not modified). Fixed-effects OLS is computed with `numpy.linalg.lstsq` and explicit rank checks. Mixed models use `statsmodels.regression.mixed_linear_model.MixedLM`.
