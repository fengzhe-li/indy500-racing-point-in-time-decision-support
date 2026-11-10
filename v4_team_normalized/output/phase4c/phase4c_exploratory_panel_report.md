# V4 Phase 4C — 2025 Exploratory Within-Team Panel Report

**Pre-specification:** `phase4c_prespecified_analysis.md`, committed before any fit as `3e3d2a7`. All definitions were followed exactly; nothing was changed after results were seen.

**Scope:** 2025 only (hybrid-era external regime). This is exploratory falsification and sensitivity, **not validation** of the frozen 2020–2024 coefficients. It is not pooled with any other year, and it makes no causal claim.

**Effective sample for every result below:** 7 teams · 21 cars · 21 drivers · 41 attempts (16 cars informative under car FE; one session/year). Attempts are clustered within cars and teams, and there is one session, so no year-level replication exists.

## 1–2. Analysis population

| population | teams | cars | drivers | attempts | informative_cars |
|---|---|---|---|---|---|
| 2025_PERFORMANCE_TIMELINE_ALL_TEAMS | 12 | 31 | 31 | 55 | 19 |
| P_all | 7 | 21 | 21 | 42 | 16 |
| P_wx | 7 | 21 | 21 | 41 | 16 |

**Teams (eligibility decided once, on P_all):**

| team | eligible | attempts | attempts_p_wx | cars | cars_with_2plus |
|---|---|---|---|---|---|
| AJ_FOYT | True | 4 | 4 | 2 | 2 |
| ANDRETTI | True | 8 | 8 | 4 | 2 |
| ARROW_MCLAREN_SPM | True | 7 | 7 | 4 | 3 |
| CHIP_GANASSI_RACING | False | 2 | 0 | 2 | 0 |
| DALE_COYNE_RACING | False | 3 | 0 | 2 | 1 |
| DREYER_REINBOLD_RACING | True | 4 | 4 | 2 | 2 |
| ED_CARPENTER_RACING | True | 7 | 7 | 3 | 2 |
| JUNCOS_HOLLINGER_RACING | True | 5 | 4 | 2 | 2 |
| MEYER_SHANK_RACING | False | 1 | 0 | 1 | 0 |
| PREMA_RACING | False | 3 | 0 | 2 | 1 |
| RAHAL_LETTERMAN_LANIGAN | True | 7 | 7 | 4 | 3 |
| TEAM_PENSKE | False | 4 | 0 | 3 | 1 |

**Cars in P_all:**

| team | car | driver | attempts | attempts_p_wx | informative_under_car_fe_p_wx | missing_weather_rows |
|---|---|---|---|---|---|---|
| AJ_FOYT | 14 | Santino Ferrucci | 2 | 2 | True | 0 |
| AJ_FOYT | 4 | David Malukas | 2 | 2 | True | 0 |
| ANDRETTI | 26 | Colton Herta | 1 | 1 | False | 0 |
| ANDRETTI | 27 | Kyle Kirkwood | 2 | 2 | True | 0 |
| ANDRETTI | 28 | Marcus Ericsson | 1 | 1 | False | 0 |
| ANDRETTI | 98 | Marco Andretti | 4 | 4 | True | 0 |
| ARROW_MCLAREN_SPM | 17 | Kyle Larson | 2 | 2 | True | 0 |
| ARROW_MCLAREN_SPM | 5 | Pato O'Ward | 1 | 1 | False | 0 |
| ARROW_MCLAREN_SPM | 6 | Nolan Siegel | 2 | 2 | True | 0 |
| ARROW_MCLAREN_SPM | 7 | Christian Lundgaard | 2 | 2 | True | 0 |
| DREYER_REINBOLD_RACING | 23 | Ryan Hunter-Reay | 2 | 2 | True | 0 |
| DREYER_REINBOLD_RACING | 24 | Jack Harvey | 2 | 2 | True | 0 |
| ED_CARPENTER_RACING | 20 | Alexander Rossi | 4 | 4 | True | 0 |
| ED_CARPENTER_RACING | 21 | Christian Rasmussen | 1 | 1 | False | 0 |
| ED_CARPENTER_RACING | 33 | Ed Carpenter | 2 | 2 | True | 0 |
| JUNCOS_HOLLINGER_RACING | 76 | Conor Daly | 3 | 2 | True | 1 |
| JUNCOS_HOLLINGER_RACING | 77 | Sting Ray Robb | 2 | 2 | True | 0 |
| RAHAL_LETTERMAN_LANIGAN | 15 | Graham Rahal | 1 | 1 | False | 0 |
| RAHAL_LETTERMAN_LANIGAN | 30 | Devlin DeFrancesco | 2 | 2 | True | 0 |
| RAHAL_LETTERMAN_LANIGAN | 45 | Louis Foster | 2 | 2 | True | 0 |
| RAHAL_LETTERMAN_LANIGAN | 75 | Takuma Sato | 2 | 2 | True | 0 |

- P_wx drops one attempt with no PTSC weather (outside the PTSC range; not extrapolated, not imputed).
- Excluded variables: solar (unavailable, not fabricated) and wind (units unverified; metadata only).

## 3–4. Identifiability

See `phase4c_identifiability_report.md`. In short:
- **Track vs session time:** r = 0.38, and within cars r = 0.21. Median within-car track range is 3.0 °C. Track is separately identifiable (within VIF 1.75 in M3).
- **Ambient vs session time:** r = 0.95, and **within cars r = 0.967**. Ambient is effectively a monotone function of session time. Its within VIF in M3 is 25.5 (time: 23.2).

## 5–8. Fixed-effects results (car FE; P_wx)

| model | term | beta | se_classical | se_cr1_car | se_cr1_team | boot_car_95 | boot_team_95 | teams | cars | drivers | attempts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | time | 0.001311 | 0.0006276 | 0.0008626 | 0.0006815 | [0.0003, 0.0027] | [0.0003, 0.0027] | 7 | 21 | 21 | 41 |
| M2 | track | -0.05834 | 0.04142 | 0.04636 | 0.02649 | [-0.1404, 0.0092] | [-0.1340, -0.0241] | 7 | 21 | 21 | 41 |
| M2 | ambient | 0.1987 | 0.08493 | 0.1168 | 0.1019 | [0.0662, 0.3847] | [0.0417, 0.3974] | 7 | 21 | 21 | 41 |
| M3 | time | 4.118e-05 | 0.003077 | 0.004576 | 0.004281 | [-0.0071, 0.0071] | [-0.0108, 0.0075] | 7 | 21 | 21 | 41 |
| M3 | track | -0.05793 | 0.05249 | 0.05249 | 0.0288 | [-0.1406, 0.0378] | [-0.1401, -0.0242] | 7 | 21 | 21 | 41 |
| M3 | ambient | 0.1934 | 0.4108 | 0.6334 | 0.6175 | [-0.7584, 1.1258] | [-0.8174, 1.6802] | 7 | 21 | 21 | 41 |

**Model comparison (descriptive; in-sample):**

| model | n | columns | rss | resid_sd | aic | bic | within_r2_vs_M0 | teams | cars | attempts |
|---|---|---|---|---|---|---|---|---|---|---|
| M0 | 41 | 21 | 4.308 | 0.4641 | 67.97 | 105.7 | 0 | 7 | 21 | 41 |
| M1 | 41 | 22 | 3.503 | 0.4294 | 61.5 | 100.9 | 0.1867 | 7 | 21 | 41 |
| M2 | 41 | 23 | 3.254 | 0.4252 | 60.47 | 101.6 | 0.2447 | 7 | 21 | 41 |
| M3 | 41 | 24 | 3.254 | 0.4375 | 62.47 | 105.3 | 0.2447 | 7 | 21 | 41 |

- **M0:** car baseline only. RSS 4.308, residual SD 0.464 mph.
- **M1:** β_time = +0.079 mph per 60 min. Positive, meaning cars are faster later. The car-bootstrap interval excludes 0, and there are no LOTO or LOCO sign flips. Within R² vs M0 is 0.19.
- **M2:**
  - β_track = -0.0583 mph/°C. The car-bootstrap 95% interval [-0.140, 0.009] includes 0.
  - β_ambient = +0.1987 mph/°C, with a car-bootstrap interval that excludes 0.
  - Within R² is 0.24.
- **M3:**
  - β_time ≈ 0 (+0.0025 per 60 min).
  - β_track = -0.0579, essentially unchanged.
  - β_ambient = +0.1934, but its CR1(car) SE jumps from 0.117 to 0.633 and its bootstrap interval spans roughly −0.76 to 1.13.
  - Adding time to M2 reduces RSS by only 0.00003. Time and ambient carry the same information.

## 9. Does physical state survive adjustment for session time?

- **Track:** yes, its point estimate is unchanged and it is not collinear with time. Its uncertainty interval nonetheless includes 0 under car-cluster resampling.
- **Ambient:** no. It cannot be separated from session time: the within-car correlation with time is 0.97, and the M3 VIF is 25.

## 10. M4 (team structure)

- Car fixed effects already absorb team effects, because every car belongs to exactly one team. A design with team dummies plus all car dummies has 30 columns but rank 23, so it was reported `NOT_ESTIMABLE` rather than forced.
- The valid M4 (team intercepts plus effect-coded car-within-team deviations) reproduces M2 exactly: its maximum |fitted difference| is 2.8e-12, with identical slopes.
- Team effects are not separately identified from car effects in a car-FE design.

## 11. Mixed-effects sensitivity (one attempt each; no re-specification)

| model | formula | status | converged | boundary_or_singular_flag | team_intercept_variance | car_within_team_variance | residual_variance | beta_track | se_track | beta_ambient | se_ambient | beta_time | se_time | warnings |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MX1 | speed ~ track + ambient | FITTED | True | True | 0.0006629 | 0.8058 | 0.1842 | -0.06413 | 0.04049 | 0.1765 | 0.08476 |  |  | ConvergenceWarning: Maximum Likelihood optimization failed to converge. Check mle_retvals || ConvergenceWarning: Retrying MixedLM optimization with lbfgs || ConvergenceWarning: The MLE may be on the boundary of the parameter space. |
| MX2 | speed ~ time + track + ambient | FITTED | False | True | 0.0006123 | 0.7852 | 0.1962 | -0.05265 | 0.05028 | 0.02074 | 0.3852 | 0.001191 | 0.002887 | ConvergenceWarning: Gradient optimization failed, |grad| = 0.062934 || ConvergenceWarning: Maximum Likelihood optimization failed to converge. Check mle_retvals || ConvergenceWarning: MixedLM optimization failed, trying a different optimizer may help. || ConvergenceWarning: Retrying MixedLM optimization with cg || ConvergenceWarning: Retrying MixedLM optimization with lbfgs || ConvergenceWarning: The MLE may be on the boundary of the parameter space. |

- **MX1:** reports `converged = True` only after statsmodels' internal optimiser retries. The team random-intercept variance sits at the boundary (≈0.0007), so the model is effectively car-intercept only. Its fixed effects are close to M2.
- **MX2** (adding time) **did not converge.** Its ambient estimate collapses toward 0 with a large SE, which is again consistent with ambient/time non-separability.
- Both results are reported as they came out. No alternative random-effects structure was tried.

## 12. Within-transformation agreement

| model | term | beta_within | beta_car_fe | abs_diff | agrees_1e_8 |
|---|---|---|---|---|---|
| M1 | time | 0.001311 | 0.001311 | 2.234e-13 | True |
| M2 | track | -0.05834 | -0.05834 | 7.87e-14 | True |
| M2 | ambient | 0.1987 | 0.1987 | 1.584e-13 | True |
| M3 | time | 4.118e-05 | 4.118e-05 | 1.617e-14 | True |
| M3 | track | -0.05793 | -0.05793 | 3.768e-14 | True |
| M3 | ambient | 0.1934 | 0.1934 | 1.628e-13 | True |

Every slope agrees with the car-fixed-effects estimate to within 1e-8, so the FE implementation is verified.

## 13–14. Stability

| model | term | full | loto_min | loto_max | loto_sign_flips | loto_max_rel_change | loco_median | loco_min | loco_max | loco_sign_flips | frozen_sign_label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | time | 0.001311 | 0.0009195 | 0.001749 | 0 | 0.3342 | 0.001333 | 0.0009681 | 0.001597 | 0 |  |
| M2 | track | -0.05834 | -0.0788 | -0.04562 | 0 | 0.3508 | -0.05762 | -0.08275 | -0.04326 | 0 | SAME_SIGN |
| M2 | ambient | 0.1987 | 0.1142 | 0.2429 | 0 | 0.4253 | 0.2026 | 0.148 | 0.241 | 0 | SAME_SIGN |
| M3 | time | 4.118e-05 | -0.0024 | 0.003253 | 3 | 78.01 | 8.016e-05 | -0.001882 | 0.001476 | 7 |  |
| M3 | track | -0.05793 | -0.06922 | -0.04492 | 0 | 0.2245 | -0.05786 | -0.07225 | -0.03943 | 0 | SAME_SIGN |
| M3 | ambient | 0.1934 | -0.3168 | 0.4996 | 1 | 2.638 | 0.1988 | -0.0271 | 0.4309 | 1 | UNSTABLE_SIGN |

- **LOTO:** 7 refits per model. **LOCO:** 16 refits per model (cars with ≥2 attempts).
- **Track:** no sign flip in any refit.
- **Ambient:** stable in M2, but flips sign in M3 when Arrow McLaren is removed (−0.32), and the largest single-team change is 264%.
- **Time in M3:** 3 LOTO and 7 LOCO sign flips.

## 15. Strategic re-running sensitivity (S1 = M2 + repeat_attempt; declared, not primary)

- β_repeat = +0.383 mph. The car-bootstrap interval [-0.376, 1.123] includes 0. 16 cars vary in the indicator.
- **Track:** -0.0583 → -0.0545 (change +0.0039). Essentially unchanged.
- **Ambient:** +0.1987 → +0.0080 (change -0.1907). It **collapses to ≈0.** The M2 ambient association cannot be separated from "later / repeat attempt", which is exactly the strategic re-running confound flagged in Phase 4B.

## 16. Sign comparison with the frozen reference era (context only; not validation)

The frozen reference era had β_track < 0 and β_ambient > 0.

| Term | M2 | M3 |
|---|---|---|
| Track | SAME_SIGN | SAME_SIGN |
| Ambient | SAME_SIGN | UNSTABLE_SIGN |

The ambient sign in M2 is not interpretable, given items 9 and 15.

## 17. Driven by one team or car?

- **Track:** no single team or car drives it. The LOTO range is [-0.079, -0.046] and there are no flips.
- **Ambient in M3:** driven by team composition. Removing Arrow McLaren flips the sign.

## 18. Case classification (mechanical, pre-declared precedence D → B → C → A)

| case | satisfied | detail |
|---|---|---|
| D | False | M2 est=True, M3 est=True, VIF_M2 track=1.15, ambient=1.15 |
| B | True | ambient: within VIF in M3 = 25.5 |
| C | True | M3 ambient: 1.0 LOTO sign flip(s); M3 ambient: single-team removal changes beta by 264% |
| A | False | not met |

**Headline: CASE B.**
- Physical state as a *whole* is not separable from session time: the ambient term is not identifiable once time is included.
- CASE C criteria also hold for ambient in M3.
- **Term-level:** the track term alone shows the stability pattern that CASE A describes (same sign in M2/M3, no LOTO or LOCO flips, unchanged under S1). Its car-cluster bootstrap interval nonetheless includes 0, so a shared track effect is *not established*. It is merely not contradicted.

## 19. What can legitimately be concluded

- In the independent 2025 Day 1 data, within cars of the same teams, speed was associated with later session time or repeat attempts, about +0.08 mph per hour in M1.
- Ambient temperature cannot be distinguished from that time/repeat pattern.
- Track temperature varied partly independently of time in 2025. Its within-car association with speed is negative, of similar size whether or not time is included, and stable to leaving out any team or car. But it is imprecise: under 21-car cluster resampling it is not distinguishable from 0.
- The 2025 data are therefore **not inconsistent** with a negative track effect, and **uninformative** about a separate ambient effect.

## 20. What cannot be concluded

- That 2025 validates, corroborates, or recalibrates the frozen 2020–2024 coefficients. The regime is different, and sign agreement is not validation.
- That temperature causally affects speed.
- That the ambient coefficient in M2 reflects air temperature rather than session evolution or strategy.
- That any estimate generalises beyond one session with 7 teams and 21 cars.
- That 2025 should be pooled with 2020–2024.

## 21. Is further modelling justified?

**Not with the current data design.** The single 2025 session cannot separate ambient temperature from session time or repeat attempts, and more model complexity cannot fix that; it would only invite specification searching. Further work is justified only if new observations become available that separate the variables:
- other sessions or years in the same technical regime, with more non-monotone ambient;
- verified wind units;
- a solar record;
- run-level evidence of setup changes.

Any such work would need a new pre-specification.

## 22. Outputs

Required:
- `phase4c_prespecified_analysis.md`, `analysis_population.csv`, `identifiability_diagnostics.csv`, `fixed_effects_results.csv`, `within_transformation_results.csv`, `mixed_effects_results.csv`, `leave_one_team_out.csv`, `leave_one_car_out.csv`, `strategy_sensitivity_results.csv`, `model_comparison.csv`;
- `phase4c_exploratory_panel_report.md`, `phase4c_identifiability_report.md`, `phase4c_stability_report.md`, `phase4c_checks_log.txt`;
- `figures/fig01…fig10`.

Additional: `case_evaluation.csv`.
