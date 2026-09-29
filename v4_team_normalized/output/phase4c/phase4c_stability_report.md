# V4 Phase 4C — Stability Report (2025, P_wx)

Effective sample: 7 teams · 21 cars · 21 drivers · 41 attempts (16 cars informative under car FE; one session/year). LOTO: 7 refits per model. LOCO: 16 refits per model (single-attempt cars cannot change within-car slopes, so they are not refitted). Neither LOTO nor LOCO is used to select a coefficient.

## Summary

| model | term | full | loto_min | loto_max | loto_sign_flips | loto_max_rel_change | loco_median | loco_min | loco_max | loco_sign_flips | frozen_sign_label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 | time | 0.001311 | 0.0009195 | 0.001749 | 0 | 0.3342 | 0.001333 | 0.0009681 | 0.001597 | 0 |  |
| M2 | track | -0.05834 | -0.0788 | -0.04562 | 0 | 0.3508 | -0.05762 | -0.08275 | -0.04326 | 0 | SAME_SIGN |
| M2 | ambient | 0.1987 | 0.1142 | 0.2429 | 0 | 0.4253 | 0.2026 | 0.148 | 0.241 | 0 | SAME_SIGN |
| M3 | time | 4.118e-05 | -0.0024 | 0.003253 | 3 | 78.01 | 8.016e-05 | -0.001882 | 0.001476 | 7 |  |
| M3 | track | -0.05793 | -0.06922 | -0.04492 | 0 | 0.2245 | -0.05786 | -0.07225 | -0.03943 | 0 | SAME_SIGN |
| M3 | ambient | 0.1934 | -0.3168 | 0.4996 | 1 | 2.638 | 0.1988 | -0.0271 | 0.4309 | 1 | UNSTABLE_SIGN |

## Leave-one-team-out (all refits)

| left_out_team | model | n | teams | cars | informative_cars | estimable | beta_time | beta_track | beta_ambient |
|---|---|---|---|---|---|---|---|---|---|
| AJ_FOYT | M1 | 37 | 6 | 19 | 14 | True | 0.00121 |  |  |
| AJ_FOYT | M2 | 37 | 6 | 19 | 14 | True |  | -0.06094 | 0.194 |
| AJ_FOYT | M3 | 37 | 6 | 19 | 14 | True | 0.0004668 | -0.0562 | 0.1324 |
| ANDRETTI | M1 | 33 | 6 | 17 | 14 | True | 0.001534 |  |  |
| ANDRETTI | M2 | 33 | 6 | 17 | 14 | True |  | -0.07127 | 0.2429 |
| ANDRETTI | M3 | 33 | 6 | 17 | 14 | True | 0.0003427 | -0.06875 | 0.199 |
| ARROW_MCLAREN_SPM | M1 | 34 | 6 | 17 | 13 | True | 0.0009195 |  |  |
| ARROW_MCLAREN_SPM | M2 | 34 | 6 | 17 | 13 | True |  | -0.0788 | 0.1142 |
| ARROW_MCLAREN_SPM | M3 | 34 | 6 | 17 | 13 | True | 0.003253 | -0.04492 | -0.3168 |
| DREYER_REINBOLD_RACING | M1 | 37 | 6 | 19 | 14 | True | 0.001749 |  |  |
| DREYER_REINBOLD_RACING | M2 | 37 | 6 | 19 | 14 | True |  | -0.04991 | 0.2403 |
| DREYER_REINBOLD_RACING | M3 | 37 | 6 | 19 | 14 | True | 0.0003906 | -0.04587 | 0.19 |
| ED_CARPENTER_RACING | M1 | 34 | 6 | 18 | 14 | True | 0.00145 |  |  |
| ED_CARPENTER_RACING | M2 | 34 | 6 | 18 | 14 | True |  | -0.06602 | 0.2206 |
| ED_CARPENTER_RACING | M3 | 34 | 6 | 18 | 14 | True | -0.0002678 | -0.06922 | 0.2559 |
| JUNCOS_HOLLINGER_RACING | M1 | 37 | 6 | 19 | 14 | True | 0.001266 |  |  |
| JUNCOS_HOLLINGER_RACING | M2 | 37 | 6 | 19 | 14 | True |  | -0.04652 | 0.189 |
| JUNCOS_HOLLINGER_RACING | M3 | 37 | 6 | 19 | 14 | True | -0.001446 | -0.06195 | 0.376 |
| RAHAL_LETTERMAN_LANIGAN | M1 | 34 | 6 | 17 | 13 | True | 0.001089 |  |  |
| RAHAL_LETTERMAN_LANIGAN | M2 | 34 | 6 | 17 | 13 | True |  | -0.04562 | 0.1883 |
| RAHAL_LETTERMAN_LANIGAN | M3 | 34 | 6 | 17 | 13 | True | -0.0024 | -0.06663 | 0.4996 |

## Leave-one-car-out (all refits)

| left_out_car | team | model | n | cars | estimable | beta_time | beta_track | beta_ambient |
|---|---|---|---|---|---|---|---|---|
| 4 | AJ_FOYT | M1 | 39 | 20 | True | 0.001321 |  |  |
| 4 | AJ_FOYT | M2 | 39 | 20 | True |  | -0.06281 | 0.2106 |
| 4 | AJ_FOYT | M3 | 39 | 20 | True | 2.969e-05 | -0.06251 | 0.2067 |
| 6 | ARROW_MCLAREN_SPM | M1 | 39 | 20 | True | 0.001477 |  |  |
| 6 | ARROW_MCLAREN_SPM | M2 | 39 | 20 | True |  | -0.04655 | 0.2056 |
| 6 | ARROW_MCLAREN_SPM | M3 | 39 | 20 | True | 0.0006462 | -0.03943 | 0.1217 |
| 7 | ARROW_MCLAREN_SPM | M1 | 39 | 20 | True | 0.0009681 |  |  |
| 7 | ARROW_MCLAREN_SPM | M2 | 39 | 20 | True |  | -0.08275 | 0.148 |
| 7 | ARROW_MCLAREN_SPM | M3 | 39 | 20 | True | 0.001111 | -0.07225 | 0.001813 |
| 14 | AJ_FOYT | M1 | 39 | 20 | True | 0.001209 |  |  |
| 14 | AJ_FOYT | M2 | 39 | 20 | True |  | -0.05717 | 0.1837 |
| 14 | AJ_FOYT | M3 | 39 | 20 | True | 0.0004895 | -0.05225 | 0.1192 |
| 17 | ARROW_MCLAREN_SPM | M1 | 39 | 20 | True | 0.001129 |  |  |
| 17 | ARROW_MCLAREN_SPM | M2 | 39 | 20 | True |  | -0.05785 | 0.1678 |
| 17 | ARROW_MCLAREN_SPM | M3 | 39 | 20 | True | 0.001476 | -0.04311 | -0.0271 |
| 20 | ED_CARPENTER_RACING | M1 | 37 | 20 | True | 0.001421 |  |  |
| 20 | ED_CARPENTER_RACING | M2 | 37 | 20 | True |  | -0.06244 | 0.2078 |
| 20 | ED_CARPENTER_RACING | M3 | 37 | 20 | True | -9.513e-06 | -0.06255 | 0.209 |
| 23 | DREYER_REINBOLD_RACING | M1 | 39 | 20 | True | 0.001412 |  |  |
| 23 | DREYER_REINBOLD_RACING | M2 | 39 | 20 | True |  | -0.05678 | 0.2043 |
| 23 | DREYER_REINBOLD_RACING | M3 | 39 | 20 | True | 0.0001306 | -0.05545 | 0.1874 |
| 24 | DREYER_REINBOLD_RACING | M1 | 39 | 20 | True | 0.001597 |  |  |
| 24 | DREYER_REINBOLD_RACING | M2 | 39 | 20 | True |  | -0.05291 | 0.2289 |
| 24 | DREYER_REINBOLD_RACING | M3 | 39 | 20 | True | 0.0002214 | -0.05069 | 0.2002 |
| 27 | ANDRETTI | M1 | 39 | 20 | True | 0.001345 |  |  |
| 27 | ANDRETTI | M2 | 39 | 20 | True |  | -0.05949 | 0.1999 |
| 27 | ANDRETTI | M3 | 39 | 20 | True | 0.0006594 | -0.05345 | 0.1144 |
| 30 | RAHAL_LETTERMAN_LANIGAN | M1 | 39 | 20 | True | 0.00114 |  |  |
| 30 | RAHAL_LETTERMAN_LANIGAN | M2 | 39 | 20 | True |  | -0.04326 | 0.179 |
| 30 | RAHAL_LETTERMAN_LANIGAN | M3 | 39 | 20 | True | -0.001705 | -0.05828 | 0.3989 |
| 33 | ED_CARPENTER_RACING | M1 | 39 | 20 | True | 0.001328 |  |  |
| 33 | ED_CARPENTER_RACING | M2 | 39 | 20 | True |  | -0.06109 | 0.2089 |
| 33 | ED_CARPENTER_RACING | M3 | 39 | 20 | True | -0.0001746 | -0.06291 | 0.232 |
| 45 | RAHAL_LETTERMAN_LANIGAN | M1 | 39 | 20 | True | 0.001263 |  |  |
| 45 | RAHAL_LETTERMAN_LANIGAN | M2 | 39 | 20 | True |  | -0.05739 | 0.1969 |
| 45 | RAHAL_LETTERMAN_LANIGAN | M3 | 39 | 20 | True | -4.73e-06 | -0.05743 | 0.1975 |
| 75 | RAHAL_LETTERMAN_LANIGAN | M1 | 39 | 20 | True | 0.001338 |  |  |
| 75 | RAHAL_LETTERMAN_LANIGAN | M2 | 39 | 20 | True |  | -0.06387 | 0.2161 |
| 75 | RAHAL_LETTERMAN_LANIGAN | M3 | 39 | 20 | True | -0.0004174 | -0.06842 | 0.2718 |
| 76 | JUNCOS_HOLLINGER_RACING | M1 | 39 | 20 | True | 0.001409 |  |  |
| 76 | JUNCOS_HOLLINGER_RACING | M2 | 39 | 20 | True |  | -0.05192 | 0.2009 |
| 76 | JUNCOS_HOLLINGER_RACING | M3 | 39 | 20 | True | 0.0005823 | -0.04549 | 0.1251 |
| 77 | JUNCOS_HOLLINGER_RACING | M1 | 39 | 20 | True | 0.00117 |  |  |
| 77 | JUNCOS_HOLLINGER_RACING | M2 | 39 | 20 | True |  | -0.05317 | 0.1869 |
| 77 | JUNCOS_HOLLINGER_RACING | M3 | 39 | 20 | True | -0.001882 | -0.07123 | 0.4309 |
| 98 | ANDRETTI | M1 | 37 | 20 | True | 0.001491 |  |  |
| 98 | ANDRETTI | M2 | 37 | 20 | True |  | -0.0696 | 0.241 |
| 98 | ANDRETTI | M3 | 37 | 20 | True | -0.0003159 | -0.07224 | 0.2818 |

## Bootstrap limitations

- The car-cluster bootstrap resamples 21 cars; the team-cluster bootstrap resamples 7 teams (B = 2000, seed 20250517). Percentile intervals from so few clusters are unreliable. The team bootstrap in particular can look narrower than the car bootstrap simply because 7 clusters give very few distinct resamples.
- None of these intervals is strong frequentist evidence. They are shown to indicate fragility, not to test hypotheses.
- CR1 cluster-robust SEs (car: G = 21; team: G = 7) have the same small-G caveat.

## Reading

- **Track:** stable in sign and moderately stable in size across every LOTO and LOCO refit, in both M2 and M3.
- **Ambient:** stable only in M2, where time is omitted. In M3 it flips sign when Arrow McLaren is removed, and it collapses under S1.
- **Time in M3:** sign-unstable (3 LOTO and 7 LOCO flips), as expected when it competes with a near-collinear ambient.
