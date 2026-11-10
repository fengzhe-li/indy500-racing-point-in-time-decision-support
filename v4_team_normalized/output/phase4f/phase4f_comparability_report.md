# V4 Phase 4F — Comparability Report

## Layers

- **BROAD:** the Phase 4E valid lap (green or none flag; not an out-lap or in-lap; 37–45 s).
- **COMPARABLE:** BROAD plus all of the following:
  - explicit green flag, and the previous lap also green;
  - not the 2nd lap of a stint;
  - not the last or penultimate lap of a stint that ended in the pits (`endTime` present);
  - timestamp coherence (|Δts − laptime| ≤ 2 s).
- **Not identifiable from the Timing71 archived feed:** fuel load, tyre age, tow/slipstream state, boost, run purpose, qualifying or race simulations. No lap was removed for slowness beyond the Phase 4E band.

| session_key | role | broad_laps | comparable_laps |
|---|---|---|---|
| 2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206 | PRIMARY | 77 | 18 |
| 6198 | PRIMARY | 2552 | 1688 |
| 6199 | PRIMARY | 2340 | 1625 |
| 6200 | PRIMARY | 515 | 262 |
| 6202 | PRIMARY | 233 | 123 |
| 6203 | PRIMARY | 94 | 42 |
| 6207 | PRIMARY | 1392 | 997 |
| 6208 | PRIMARY | 1763 | 1330 |
| 6375 | PRIMARY | 128 | 74 |
| 6378 | PRIMARY | 1577 | 1096 |
| 6380 | PRIMARY | 164 | 79 |
| 6382 | PRIMARY | 161 | 98 |
| 6386 | PRIMARY | 31 | 20 |
| 6387 | PRIMARY | 1960 | 1510 |
| 6388 | PRIMARY | 2120 | 1703 |
| 6651 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 596 | 382 |
| 6653 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 730 | 447 |
| 6654 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 1714 | 1165 |
| 6655 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 313 | 166 |
| 6656 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 263 | 184 |
| 6657 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 108 | 48 |
| 6660 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 40 | 26 |
| 6661 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 60 | 31 |
| 6662 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 1414 | 1098 |
| 6663 | ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE | 1548 | 1176 |
| 6135 | RACE_APPENDIX_STRUCTURAL_ONLY | 647 | 0 |
| 6309 | RACE_APPENDIX_STRUCTURAL_ONLY | 5104 | 1539 |
| 6460 | RACE_APPENDIX_STRUCTURAL_ONLY | 4039 | 3346 |

## Car-block validity

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

- **Stated limit:** car-block values in practice-type sessions are observed local performance summaries, not pure pace.
- **Multimodality:** wide within-block spreads (a 3–6 mph median in practice/Carb Day) indicate towed and un-towed laps inside one 5-minute block.
- **Pit adjacency:** removed in the comparable layer wherever identifiable (`with_pit_adjacent_laps_share` = 0 in that layer).

## Primary-control comparability problem

The time-nearest different-team control is usually adjacent on track (median separation of seconds). The primary contrast therefore compares teammates to drafting partners (see the hierarchy report).

## Official cross-check (sources kept distinct)

| session_key | timing71_cars | official_cars | timing71_cars_in_official | best_speed_compared | best_speed_agree_within_0p01mph | lap_source | crosscheck_source |
|---|---|---|---|---|---|---|---|
| 2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206 | 16 | 16 | 16 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6198 | 34 | 34 | 34 | 34 | 34 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6199 | 34 | 34 | 34 | 34 | 34 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6200 | 34 | 34 | 34 | 34 | 34 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6202 | 34 | 34 | 34 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6203 | 15 | 15 | 15 | 15 | 15 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6207 | 33 | 33 | 33 | 33 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6208 | 33 | 33 | 33 | 33 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6375 | 28 | 29 | 27 | 27 | 27 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6378 | 34 | 34 | 34 | 34 | 34 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6380 | 29 | 34 | 29 | 29 | 14 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6382 | 34 | 34 | 34 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6386 | 10 | 6 | 6 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6387 | 33 | 33 | 33 | 33 | 32 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6388 | 33 | 33 | 33 | 33 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6651 | 34 | 34 | 34 | 34 | 21 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6653 | 34 | 34 | 34 | 34 | 14 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6654 | 34 | 34 | 34 | 34 | 34 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6655 | 34 | 34 | 34 | 34 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6656 | 34 | 34 | 34 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6657 | 23 | 23 | 23 | 23 | 23 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6660 | 10 | 6 | 6 | 0 | 0 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6661 | 13 | 14 | 13 | 13 | 10 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6662 | 33 | 33 | 33 | 33 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |
| 6663 | 33 | 33 | 33 | 33 | 33 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | INDYCAR_OFFICIAL_SESSION_DETAILS |

- **Where it's missing:** the best-lap comparison is 0 for qualifying sessions, because the official qualifying records carry no single-lap `BestSpeed` (only the four-lap `SpeedAvg` and per-lap `QualLap` fields).
- **Where it disagrees:** Fast Friday 2024 (6380: 14/29) and some 2025 practices (6651: 21/34; 6653: 14/34). The cause is not diagnosed; plausible explanations include laps missing from the Timing71 capture.
- **Car presence** agrees except where Timing71 captured fewer cars.
