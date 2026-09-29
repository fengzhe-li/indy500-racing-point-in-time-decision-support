# V4 Phase 4E — 2018–2025 Multi-Session Team-Comparison Data-Opportunity Audit

**Scope:** audit only.
- No model was fitted, no coefficient estimated, no team-reference metric chosen, and no performance hypothesis tested.
- No team or driver was ranked.
- Race is never pooled with other sessions, and eras are never pooled.

**Specification:** `phase4e_quality_tier_spec.md` was committed with the pre-retrieval `source_inventory.csv` (`d2d65e4`) before any retrieval or counting. Implementation clarifications made during coding are listed in `phase4e_limitations_report.md` §Implementation notes; none changes a tier rule.

**Retrieval (documented, small):**
- 101 Timing71 lap-level analysis JSONs (11.0 MB);
- 60 official INDYCAR session-detail JSONs for 2020–2024 (1.3 MB).

Every file is listed with its SHA-256 in `v4_team_normalized/evidence/phase4e/retrieval_manifest.csv`. Timing71 replay ZIPs and official lap-level PDFs were **not** ingested (documented as recoverable).

## 1. Session data by year (official session list; normalized categories)

| year | AGGREGATE_RESULT | CARB_DAY | FAST_FRIDAY | POST_QUALIFYING_PRACTICE | PRACTICE | QUALIFYING_DAY1 | QUALIFYING_OTHER | QUALIFYING_WEEKEND_PRACTICE | RACE |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 0 | 1 | 1 | 1 | 4 | 1 | 2 | 2 | 1 |
| 2019 | 0 | 1 | 1 | 1 | 3 | 1 | 2 | 2 | 1 |
| 2020 | 0 | 1 | 1 | 0 | 2 | 1 | 1 | 3 | 1 |
| 2021 | 0 | 1 | 1 | 0 | 4 | 1 | 2 | 3 | 1 |
| 2022 | 0 | 1 | 1 | 1 | 3 | 1 | 2 | 2 | 1 |
| 2023 | 0 | 1 | 1 | 1 | 3 | 1 | 3 | 2 | 1 |
| 2024 | 0 | 1 | 1 | 1 | 3 | 1 | 3 | 2 | 1 |
| 2025 | 1 | 1 | 1 | 1 | 3 | 1 | 3 | 2 | 1 |

## 2. Local vs requiring retrieval

| authority | local | sources |
|---|---|---|
| DERIVED | True | 1 |
| MODEL_FORECAST | True | 1 |
| PRIMARY_OBSERVATION | True | 1 |
| PRIMARY_OFFICIAL | False | 91 |
| PRIMARY_OFFICIAL | True | 124 |
| SECONDARY_TIMING_CAPTURE | False | 1 |
| SECONDARY_TIMING_CAPTURE | True | 111 |

Timing71 file-to-session mapping outcome:

| year | EMPTY_ANALYSIS | EXCLUDED_CONTENT_NOT_INDY500_INDYCAR | MULTIPLE_OFFICIAL_SEGMENTS_SAME_CATEGORY | TIMING71_ONLY_NOT_IN_OFFICIAL_LIST | UNIQUE_OFFICIAL_SESSION |
|---|---|---|---|---|---|
| 2018 | 1 | 0 | 1 | 0 | 12 |
| 2019 | 0 | 2 | 1 | 0 | 11 |
| 2020 | 0 | 0 | 0 | 0 | 12 |
| 2021 | 1 | 0 | 2 | 0 | 11 |
| 2023 | 1 | 0 | 3 | 1 | 12 |
| 2024 | 1 | 0 | 0 | 0 | 13 |
| 2025 | 0 | 0 | 0 | 0 | 16 |

- **Excluded as not Indy 500 IndyCar content:** the archive listing mislabelled an Indy Lights open-test practice and the Freedom 100 (2019).
- **Empty captures:** four analysis files.
- **No lap-level capture:** 2022 has no Timing71 capture; its lap-level data exist only as official PDFs.
- **Other missing captures:** 2024 Practice 4 and Last Chance, and 2025 Top-12.

## 3. Finest reliable observation unit

| normalized_category | finest_unit | sessions |
|---|---|---|
| AGGREGATE_RESULT | session-level best lap per car | 1 |
| CARB_DAY | lap (observed timestamp) | 3 |
| CARB_DAY | lap (stint-level timestamps; lap times derived) | 3 |
| CARB_DAY | session-level best lap per car | 2 |
| FAST_FRIDAY | lap (observed timestamp) | 3 |
| FAST_FRIDAY | lap (stint-level timestamps; lap times derived) | 4 |
| FAST_FRIDAY | session-level best lap per car | 1 |
| POST_QUALIFYING_PRACTICE | lap (observed timestamp) | 3 |
| POST_QUALIFYING_PRACTICE | lap (stint-level timestamps; lap times derived) | 1 |
| POST_QUALIFYING_PRACTICE | session-level best lap per car | 2 |
| PRACTICE | lap (observed timestamp) | 8 |
| PRACTICE | lap (stint-level timestamps; lap times derived) | 13 |
| PRACTICE | session-level best lap per car | 4 |
| QUALIFYING_DAY1 | lap (observed timestamp) | 3 |
| QUALIFYING_DAY1 | lap (stint-level timestamps; lap times derived) | 4 |
| QUALIFYING_DAY1 | session-level best lap per car | 1 |
| QUALIFYING_OTHER | lap (observed timestamp) | 7 |
| QUALIFYING_OTHER | lap (stint-level timestamps; lap times derived) | 7 |
| QUALIFYING_OTHER | session-level best lap per car | 4 |
| QUALIFYING_WEEKEND_PRACTICE | lap (observed timestamp) | 6 |
| QUALIFYING_WEEKEND_PRACTICE | lap (stint-level timestamps; lap times derived) | 10 |
| QUALIFYING_WEEKEND_PRACTICE | session-level best lap per car | 2 |
| RACE | lap (observed timestamp) | 3 |
| RACE | lap (stint-level timestamps; lap times derived) | 4 |
| RACE | session-level best lap per car | 1 |

- **2023–2025:** lap-level with **observed** timestamps (±~1 s feed latency; median |Δtimestamp − laptime| = 0.78 s).
- **2018–2021:** the Timing71 legacy format stores stint-level start/end times plus lap times. Lap times reconstructed from stints are consistent within 15 s for only about 25% of stints, so those years do **not** meet the pre-declared "observed lap timestamp" criterion.
- **Exact legacy lap times:** would require the replay ZIPs (not retrieved).

## 4–5. Raw observations and identity

| era | timestamp_basis | normalized_category | sessions | raw_laps | valid_laps |
|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 1 | 1171 | 812 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 2 | 2716 | 1685 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | POST_QUALIFYING_PRACTICE | 1 | 2416 | 1876 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 7 | 14955 | 10748 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 2 | 888 | 478 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 3 | 167 | 129 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 4 | 559 | 330 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 2 | 11900 | 8817 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 2 | 4545 | 3521 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 2 | 2452 | 1426 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 7 | 13605 | 10348 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 2 | 1246 | 397 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 2 | 131 | 99 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 6 | 4735 | 3677 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 2 | 11677 | 8731 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 2 | 5091 | 3883 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 2 | 1352 | 679 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 2 | 4377 | 3352 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 4 | 9251 | 6597 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 2 | 495 | 394 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 3 | 198 | 144 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 4 | 554 | 272 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | RACE | 2 | 8670 | 5751 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 1 | 1988 | 1414 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 1 | 618 | 313 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 1 | 2076 | 1548 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 3 | 4295 | 3040 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 1 | 337 | 263 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 2 | 101 | 69 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 2 | 320 | 168 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | RACE | 1 | 5672 | 4039 |

| era | cars | drivers | teams | team_years |
|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | 68 | 41 | 15 | 26 |
| ERA_B_REFERENCE | 168 | 59 | 15 | 59 |
| ERA_C_HYBRID | 34 | 34 | 12 | 12 |

Identity joins to the V4 registry (exact car number, no fuzzy matching) match 100% of cars in every lap-level session.

## 6–9. Opportunity counts by window (raw valid-lap pairs; NOT independent)

| era | timestamp_basis | normalized_category | same_car_pairs_le1 | same_car_pairs_le2 | same_car_pairs_le5 | same_car_pairs_le10 | same_car_pairs_le15 | same_car_pairs_le30 | same_team_pairs_le1 | same_team_pairs_le2 | same_team_pairs_le5 | same_team_pairs_le10 | same_team_pairs_le15 | same_team_pairs_le30 | diff_team_pairs_le1 | diff_team_pairs_le2 | diff_team_pairs_le5 | diff_team_pairs_le10 | diff_team_pairs_le15 | diff_team_pairs_le30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 659 | 1195 | 2826 | 4073 | 5329 | 8462 | 1055 | 1972 | 4475 | 7627 | 10448 | 17226 | 12538 | 24365 | 56283 | 100602 | 139345 | 231349 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 1204 | 2394 | 2758 | 2954 | 3452 | 5323 | 185 | 392 | 1191 | 2738 | 4048 | 7313 | 3665 | 7311 | 18837 | 36487 | 52342 | 95433 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | POST_QUALIFYING_PRACTICE | 1636 | 3062 | 7756 | 11258 | 14051 | 22581 | 2556 | 4819 | 11253 | 18695 | 24034 | 41063 | 26132 | 51474 | 116976 | 198630 | 263679 | 491847 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 8520 | 15150 | 31520 | 41750 | 52582 | 82005 | 9962 | 18439 | 42438 | 67253 | 87368 | 145815 | 75855 | 149497 | 353035 | 622841 | 864526 | 1572004 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 328 | 689 | 1007 | 1626 | 2035 | 3021 | 44 | 81 | 184 | 343 | 478 | 760 | 1020 | 1853 | 3384 | 6315 | 8889 | 16530 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 96 | 188 | 190 | 190 | 190 | 190 | 0 | 0 | 59 | 133 | 196 | 320 | 76 | 122 | 337 | 754 | 1075 | 1875 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 229 | 454 | 548 | 670 | 931 | 1286 | 81 | 182 | 566 | 1195 | 1635 | 2619 | 607 | 1240 | 3074 | 5824 | 7993 | 12526 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 8775 | 17221 | 53714 | 98489 | 138854 | 236291 | 24023 | 47031 | 113899 | 210129 | 294594 | 497403 | 313456 | 611100 | 1493734 | 2764642 | 3883147 | 6569325 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 3082 | 5787 | 14964 | 22335 | 30094 | 51822 | 5221 | 9695 | 23929 | 43810 | 63572 | 116097 | 55775 | 110454 | 270607 | 519795 | 756346 | 1375244 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 959 | 1878 | 2122 | 2403 | 2748 | 3779 | 411 | 703 | 1493 | 2777 | 3732 | 6652 | 4326 | 8568 | 17819 | 30457 | 41722 | 73434 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 8561 | 15551 | 36015 | 51499 | 65723 | 99012 | 12468 | 22696 | 53811 | 90794 | 121414 | 203447 | 97920 | 193029 | 454271 | 830602 | 1187087 | 2129868 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 295 | 664 | 1078 | 1873 | 2348 | 3515 | 71 | 131 | 274 | 607 | 866 | 1542 | 617 | 1131 | 2124 | 3683 | 5113 | 8544 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 73 | 146 | 149 | 149 | 149 | 149 | 0 | 3 | 37 | 111 | 139 | 216 | 0 | 0 | 151 | 380 | 601 | 959 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 3174 | 5967 | 14611 | 21212 | 27145 | 45076 | 4292 | 8406 | 20480 | 37174 | 51752 | 93387 | 46132 | 90020 | 216800 | 392975 | 548450 | 1030399 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 8543 | 16810 | 52813 | 93925 | 128288 | 220973 | 25333 | 48710 | 119295 | 214464 | 293952 | 502851 | 306976 | 600093 | 1453508 | 2633915 | 3616314 | 6188266 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 3480 | 6622 | 17907 | 27318 | 36155 | 63117 | 6513 | 11535 | 30111 | 53632 | 76572 | 140051 | 78290 | 141715 | 358866 | 635064 | 918800 | 1710939 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 476 | 965 | 1032 | 1070 | 1181 | 1488 | 45 | 97 | 423 | 1049 | 1582 | 2736 | 868 | 1824 | 5019 | 10296 | 15236 | 28261 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 2933 | 5529 | 14408 | 20903 | 26149 | 41978 | 5276 | 9325 | 23438 | 40229 | 54323 | 92169 | 61999 | 112294 | 281155 | 484512 | 653758 | 1112182 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 5569 | 10243 | 23798 | 32486 | 40353 | 64486 | 8873 | 15450 | 38619 | 62970 | 80884 | 129301 | 74194 | 136706 | 342459 | 588459 | 796546 | 1385564 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 239 | 391 | 395 | 395 | 395 | 418 | 35 | 38 | 96 | 200 | 327 | 519 | 476 | 571 | 1208 | 2162 | 3049 | 5990 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 104 | 160 | 160 | 187 | 188 | 188 | 0 | 0 | 46 | 127 | 153 | 234 | 0 | 0 | 170 | 428 | 669 | 1146 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 227 | 436 | 468 | 515 | 577 | 780 | 56 | 85 | 224 | 491 | 754 | 1148 | 180 | 369 | 1152 | 2038 | 2703 | 4348 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | RACE | 45530 | 85058 | 176086 | 237887 | 262285 | 530681 | 17452 | 30433 | 68099 | 103323 | 123556 | 247278 | 273525 | 487094 | 1075432 | 1598725 | 1888018 | 3944746 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 1235 | 2322 | 6069 | 9107 | 11118 | 16307 | 2135 | 3706 | 9200 | 16096 | 21174 | 31170 | 27743 | 48843 | 121251 | 212941 | 282052 | 440045 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 212 | 438 | 488 | 518 | 548 | 672 | 8 | 13 | 94 | 264 | 408 | 730 | 289 | 562 | 1460 | 2803 | 4264 | 7865 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 1346 | 2524 | 6456 | 9095 | 11568 | 20790 | 1913 | 3401 | 8500 | 14025 | 19035 | 35375 | 26607 | 46926 | 116730 | 196517 | 277197 | 521837 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 2503 | 4537 | 10061 | 13017 | 15858 | 24742 | 2616 | 4470 | 11501 | 18030 | 23134 | 39533 | 22577 | 40952 | 104929 | 181844 | 245277 | 429378 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 191 | 368 | 368 | 368 | 368 | 368 | 0 | 0 | 30 | 85 | 139 | 270 | 0 | 0 | 506 | 1411 | 2243 | 4431 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 45 | 84 | 84 | 84 | 84 | 84 | 0 | 0 | 17 | 34 | 36 | 36 | 0 | 0 | 77 | 232 | 368 | 624 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 117 | 227 | 236 | 249 | 265 | 301 | 18 | 33 | 104 | 172 | 186 | 289 | 310 | 599 | 1418 | 2259 | 2972 | 4052 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | RACE | 4561 | 8908 | 26171 | 47840 | 66351 | 111291 | 10291 | 19047 | 46872 | 84115 | 115921 | 191536 | 149890 | 276040 | 675813 | 1212346 | 1667216 | 2744994 |

**Effective-information companions (±5 min):**

| era | timestamp_basis | normalized_category | distinct_same_team_car_pairs_le5 | distinct_team_5min_cells_2plus_cars | cars_ge2 | cars_ge10 |
|---|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 37 | 71 | 33 | 31 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 62 | 71 | 70 | 67 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | POST_QUALIFYING_PRACTICE | 36 | 125 | 32 | 32 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 236 | 721 | 232 | 221 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 8 | 8 | 57 | 12 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 7 | 3 | 33 | 0 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 29 | 20 | 44 | 12 |
| ERA_A_PRE_AEROSCREEN | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 68 | 438 | 66 | 65 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | CARB_DAY | 81 | 247 | 66 | 66 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | FAST_FRIDAY | 76 | 94 | 68 | 68 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | PRACTICE | 241 | 766 | 197 | 183 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_DAY1 | 9 | 17 | 33 | 8 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_OTHER | 5 | 4 | 23 | 0 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | QUALIFYING_WEEKEND_PRACTICE | 88 | 245 | 115 | 69 |
| ERA_B_REFERENCE | DERIVED_FROM_STINTS (indicative only; fails spec criterion T) | RACE | 79 | 424 | 64 | 64 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 76 | 263 | 66 | 66 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 43 | 26 | 60 | 34 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 76 | 241 | 66 | 66 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 136 | 498 | 124 | 105 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 39 | 15 | 61 | 11 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 8 | 2 | 37 | 1 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 17 | 9 | 42 | 4 |
| ERA_B_REFERENCE | OBSERVED_LAP_TIMESTAMPS | RACE | 64 | 366 | 62 | 61 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | CARB_DAY | 33 | 110 | 33 | 32 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | FAST_FRIDAY | 9 | 6 | 32 | 16 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | POST_QUALIFYING_PRACTICE | 34 | 132 | 33 | 31 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | PRACTICE | 95 | 237 | 101 | 87 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_DAY1 | 3 | 2 | 34 | 6 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_OTHER | 2 | 0 | 19 | 0 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | QUALIFYING_WEEKEND_PRACTICE | 11 | 6 | 33 | 0 |
| ERA_C_HYBRID | OBSERVED_LAP_TIMESTAMPS | RACE | 29 | 221 | 31 | 31 |

## 10–11. Strongest coverage

- **Contemporaneous teammate coverage:** strongest in open practice (Practice 3/4, Post-Qualifying Practice 8, Carb Day) and the race.
  - In practice, thousands of raw same-team pairs per session fall within ±5 min, spread over every multi-car team.
  - Qualifying (Day 1 and other segments) has tens.
- **Same-car repeat coverage:** strongest in practice and the race (every car has dozens of valid laps). In qualifying, laps come in 4-lap runs.

**Teammate time-gap quantiles** (session medians by category; minutes; weather differences are |Δ| of the most recent PTSC reading, 15-min resolution):

| normalized_category | nearest_teammate_min_p010 | nearest_teammate_min_p025 | nearest_teammate_min_p050 | nearest_teammate_min_p075 | nearest_teammate_min_p090 | nearest_teammate_min_p100 | teammate_abs_dtrack_c_p050 | teammate_abs_dambient_c_p050 |
|---|---|---|---|---|---|---|---|---|
| CARB_DAY | 0.01 | 0.03 | 0.1 | 0.7 | 3.28 | 30.35 | 0 | 0 |
| FAST_FRIDAY | 0.48 | 2.38 | 5.65 | 16.9 | 33.09 | 159.84 | 0 | 0 |
| POST_QUALIFYING_PRACTICE | 0.01 | 0.04 | 0.08 | 1.38 | 3.73 | 68.94 | 0 | 0 |
| PRACTICE | 0.01 | 0.04 | 0.33 | 3.25 | 10.38 | 83.76 | 0 | 0 |
| QUALIFYING_DAY1 | 3.28 | 8.1 | 26.27 | 58.24 | 128.63 | 213.67 | 1.11 | 0 |
| QUALIFYING_OTHER | 3.46 | 4.14 | 5.44 | 8.04 | 24.78 | 26.09 | 0 | 0 |
| QUALIFYING_WEEKEND_PRACTICE | 2.33 | 3.26 | 4.62 | 6.32 | 15.49 | 24.66 | 0 | 0 |
| RACE | 0.01 | 0.03 | 0.08 | 0.15 | 0.3 | 77.91 | 0 | 0 |

## 12–13. Weather and state confounding

- **Observed PTSC weather:** ambient, track, humidity and pressure; wind is unit-unverified.
  - Present for essentially every event day 2018–2025 in the local Firestone archive. It is now extracted for all event days and validated against the R6 canonical 2019/2025 Day 1 values (exact match).
  - Its resolution is 15 minutes, so nearly all close-time teammates share the same reading (median |Δtrack| = 0).
- **HRRR solar/cloud forecasts:** local only for Day 1, 2020–2024.
- **Major state confounding:** the race (traffic, fuel, tyres, cautions) is always Tier C.
- **One important limitation:** every practice-type session (unobserved run plan, tow, fuel, boost).

## 14. Cross-session linkage (primary-layer cars)

| era | lap_level_ge2 | lap_level_ge3 | lap_level_ge4 | lap_level_all_available | official_ge2 | official_ge3 | official_ge4 | cars |
|---|---|---|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | 0 | 0 | 0 | 0 | 68 | 64 | 64 | 68 |
| ERA_B_REFERENCE | 68 | 68 | 67 | 123 | 168 | 164 | 163 | 168 |
| ERA_C_HYBRID | 34 | 34 | 34 | 11 | 34 | 33 | 33 | 34 |

## 15. Longitudinal team coverage (top 10 by years × non-race same-team 5-min cells)

| era | canonical_engineering_team | years | cars | drivers | valid_laps_non_race | valid_laps_race | same_team_5min_cells_non_race |
|---|---|---|---|---|---|---|---|
| ERA_B_REFERENCE | ANDRETTI | 2020|2021|2022|2023|2024 | 26 | 11 | 5709 | 2041 | 418 |
| ERA_B_REFERENCE | TEAM_PENSKE | 2020|2021|2022|2023|2024 | 17 | 5 | 4004 | 1633 | 304 |
| ERA_B_REFERENCE | CHIP_GANASSI_RACING | 2020|2021|2022|2023|2024 | 21 | 10 | 4013 | 1457 | 303 |
| ERA_B_REFERENCE | ARROW_MCLAREN_SPM | 2020|2021|2022|2023|2024 | 17 | 9 | 3747 | 1530 | 287 |
| ERA_B_REFERENCE | ED_CARPENTER_RACING | 2020|2021|2022|2023|2024 | 15 | 4 | 3283 | 1329 | 274 |
| ERA_B_REFERENCE | RAHAL_LETTERMAN_LANIGAN | 2020|2021|2022|2023|2024 | 17 | 8 | 3539 | 1329 | 270 |
| ERA_B_REFERENCE | AJ_FOYT | 2020|2021|2022|2023|2024 | 14 | 9 | 2357 | 1156 | 164 |
| ERA_B_REFERENCE | DALE_COYNE_RACING | 2020|2021|2022|2023|2024 | 11 | 10 | 2352 | 608 | 142 |
| ERA_B_REFERENCE | MEYER_SHANK_RACING | 2020|2021|2022|2023|2024 | 10 | 5 | 2184 | 685 | 122 |
| ERA_B_REFERENCE | DREYER_REINBOLD_RACING | 2020|2021|2022|2023|2024 | 9 | 6 | 1453 | 1767 | 82 |

## 16. Quality tiers

| era | A | B | C | D |
|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN | 0 | 0 | 0 | 25 |
| ERA_B_REFERENCE | 2 | 15 | 5 | 39 |
| ERA_C_HYBRID | 1 | 9 | 2 | 2 |

**Tier A/B sessions:**

| year | official_session_name | normalized_category | quality_tier | tier_reason |
|---|---|---|---|---|
| 2023 | Final Practice | CARB_DAY | B | limitation: state_open_track |
| 2023 | Practice 8 | POST_QUALIFYING_PRACTICE | B | limitation: state_open_track |
| 2023 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | B | limitation: O |
| 2023 | Qualifications - Last Chance | QUALIFYING_OTHER | B | limitation: O |
| 2023 | Qualifications - Top-12 | QUALIFYING_OTHER | B | limitation: O |
| 2023 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | B | limitation: state_open_track |
| 2023 | Qualifications - Day 1 | QUALIFYING_DAY1 | A | all criteria met |
| 2023 | Practice 5 | FAST_FRIDAY | B | limitation: state_open_track |
| 2023 | Practice 4 | PRACTICE | B | limitation: state_open_track |
| 2023 | Practice 3 | PRACTICE | B | limitation: state_open_track |
| 2024 | Final Practice (Carb Day) | CARB_DAY | B | limitation: state_open_track |
| 2024 | Practice 8 | POST_QUALIFYING_PRACTICE | B | limitation: state_open_track |
| 2024 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | B | limitation: O |
| 2024 | Qualifications - Day 1 | QUALIFYING_DAY1 | A | all criteria met |
| 2024 | Practice 5 | FAST_FRIDAY | B | limitation: state_open_track |
| 2024 | Practice 3 | PRACTICE | B | limitation: state_open_track |
| 2024 | Practice 1 | PRACTICE | B | limitation: state_open_track |
| 2025 | Final Practice (Carb Day) | CARB_DAY | B | limitation: state_open_track |
| 2025 | Practice 8 | POST_QUALIFYING_PRACTICE | B | limitation: state_open_track |
| 2025 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | B | limitation: O |
| 2025 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | B | limitation: state_open_track |
| 2025 | Qualifications - Day 1 | QUALIFYING_DAY1 | A | all criteria met |
| 2025 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | B | limitation: state_open_track |
| 2025 | Practice 5 | FAST_FRIDAY | B | limitation: state_open_track |
| 2025 | Practice 4 | PRACTICE | B | limitation: state_open_track |
| 2025 | Practice 3 | PRACTICE | B | limitation: state_open_track |
| 2025 | Practice 1 | PRACTICE | B | limitation: state_open_track |

## 17. Does the broader dataset improve on Day 1 qualifying?

Day 1 qualifying at lap level:

| year | valid_laps | same_team_pairs_le5 | distinct_same_team_car_pairs_le5 | distinct_team_5min_cells_2plus_cars | quality_tier |
|---|---|---|---|---|---|
| 2018 | 73 | 20 | 2 | 1 | D |
| 2019 | 405 | 164 | 6 | 7 | D |
| 2020 | 199 | 272 | 8 | 16 | D |
| 2021 | 198 | 2 | 1 | 1 | D |
| 2023 | 233 | 61 | 34 | 12 | A |
| 2024 | 161 | 35 | 5 | 3 | A |
| 2025 | 263 | 30 | 3 | 2 | A |

Practice-type sessions (practice, Fast Friday, post-qualifying, Carb Day) at lap level:

| year | valid_laps | same_team_pairs_le5 | distinct_same_team_car_pairs_le5 | distinct_team_5min_cells_2plus_cars |
|---|---|---|---|---|
| 2018 | 9055 | 43792 | 248 | 633 |
| 2019 | 6066 | 15565 | 123 | 355 |
| 2020 | 6830 | 34925 | 159 | 527 |
| 2021 | 8465 | 44308 | 239 | 580 |
| 2023 | 8562 | 48437 | 176 | 610 |
| 2024 | 5949 | 44154 | 155 | 418 |
| 2025 | 6315 | 29295 | 171 | 485 |

**Materially, yes, for contemporaneous same-team coverage, and only in 2023–2025.**
- **Scale:** practice-type sessions give ≈50–250× more distinct same-team 5-minute cells than Day 1 qualifying (2023: 616 vs 12; 2024: 421 vs 3; 2025: 491 vs 2), across all multi-car teams, with simultaneous same-car, same-team and different-team comparisons.
- **The price:** unobserved run plan, tow and fuel state (Tier B at best).
- **Dependence, measured:** the within-stint lag-1 autocorrelation of valid lap times is low in practice (session medians ≈0.0–0.1) but high in the race (≈0.5) and in 4-lap qualifying runs (≈0.8). Practice dependence comes mainly from shared run state (fuel, tyre, traffic, run plan) and from repeated car pairs, not lap-to-lap correlation; the raw-to-effective ratios (same-team pairs per distinct team × 5-min cell ≈ 60–90 in practice, ≈250 in the race) show how much raw counts overstate information.
- **2018–2022:** no improvement without additional data (exact legacy lap timestamps; 2022 lap data).
- **Accepted Day 1 attempt layer (Phase 3):** unchanged; its 2020–2024 counts are in `output/phase3/`.

## 18–22. Future designs (mechanical, spec §8; not run)

| design | ERA_A_PRE_AEROSCREEN | ERA_B_REFERENCE | ERA_C_HYBRID |
|---|---|---|---|
| DESIGN_1_evidence_hierarchy | FEASIBLE WITH ADDITIONAL DATA | FEASIBLE NOW | FEASIBLE WITH ADDITIONAL DATA |
| DESIGN_2_within_team_relative | FEASIBLE WITH ADDITIONAL DATA | FEASIBLE NOW | FEASIBLE WITH ADDITIONAL DATA |
| DESIGN_3_cross_session_persistence | FEASIBLE WITH ADDITIONAL DATA | FEASIBLE WITH ADDITIONAL DATA | FEASIBLE NOW |
| DESIGN_4_within_team_dispersion | FEASIBLE WITH ADDITIONAL DATA | FEASIBLE NOW | FEASIBLE NOW |
| DESIGN_5_race_teammate_pace | WEAK / HIGH-CONFOUNDING | WEAK / HIGH-CONFOUNDING | WEAK / HIGH-CONFOUNDING |

| era | design | feasibility | evidence |
|---|---|---|---|
| ERA_B_REFERENCE | DESIGN_1_evidence_hierarchy | FEASIBLE NOW | Tier A/B sessions with all_three: 15 over 2 year(s); 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs) |
| ERA_B_REFERENCE | DESIGN_2_within_team_relative | FEASIBLE NOW | Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 10; 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs) |
| ERA_B_REFERENCE | DESIGN_3_cross_session_persistence | FEASIBLE WITH ADDITIONAL DATA | share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 0.40; official-record linkage >=3 categories: 0.98 |
| ERA_B_REFERENCE | DESIGN_4_within_team_dispersion | FEASIBLE NOW | Tier A/B sessions with >=3 multi-car teams: 15; 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs) |
| ERA_B_REFERENCE | DESIGN_5_race_teammate_pace | WEAK / HIGH-CONFOUNDING | lap-level race sessions: 4 (tiers: C/D; race is at best Tier C by rule; fuel/tyre/traffic unobserved) |
| ERA_C_HYBRID | DESIGN_1_evidence_hierarchy | FEASIBLE WITH ADDITIONAL DATA | Tier A/B sessions with all_three: 10 over 1 year(s); only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope) |
| ERA_C_HYBRID | DESIGN_2_within_team_relative | FEASIBLE WITH ADDITIONAL DATA | Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 5; only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope) |
| ERA_C_HYBRID | DESIGN_3_cross_session_persistence | FEASIBLE NOW | share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 1.00; official-record linkage >=3 categories: 0.97 |
| ERA_C_HYBRID | DESIGN_4_within_team_dispersion | FEASIBLE NOW | Tier A/B sessions with >=3 multi-car teams: 10; only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope) |
| ERA_C_HYBRID | DESIGN_5_race_teammate_pace | WEAK / HIGH-CONFOUNDING | lap-level race sessions: 1 (tiers: C; race is at best Tier C by rule; fuel/tyre/traffic unobserved) |
| ERA_A_PRE_AEROSCREEN | DESIGN_1_evidence_hierarchy | FEASIBLE WITH ADDITIONAL DATA | Tier A/B sessions with all_three: 0 over 0 year(s); 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them |
| ERA_A_PRE_AEROSCREEN | DESIGN_2_within_team_relative | FEASIBLE WITH ADDITIONAL DATA | Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 0; 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them |
| ERA_A_PRE_AEROSCREEN | DESIGN_3_cross_session_persistence | FEASIBLE WITH ADDITIONAL DATA | share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 0.00; official-record linkage >=3 categories: 0.94 |
| ERA_A_PRE_AEROSCREEN | DESIGN_4_within_team_dispersion | FEASIBLE WITH ADDITIONAL DATA | Tier A/B sessions with >=3 multi-car teams: 0; 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them |
| ERA_A_PRE_AEROSCREEN | DESIGN_5_race_teammate_pace | WEAK / HIGH-CONFOUNDING | lap-level race sessions: 2 (tiers: D; race is at best Tier C by rule; fuel/tyre/traffic unobserved) |

- **Design 1 (evidence hierarchy):** feasible now for 2023–2024 (Era B) and 2025 (Era C, which has only one year and so fails the ≥2-year rule). Limited to the lap-level Tier A/B sessions.
- **Design 2 (leave-one-out team reference):** structurally supported in the same sessions.
- **Design 3 (cross-session persistence):** counted in Tier A/B/C sessions only. Linkage is strong in 2023–2025; 2018–2022 linkage exists only in official session-level records.
- **Design 4 (within-team dispersion):** feasible in 2023–2025 Tier A/B sessions.
- **Design 5 (race-only teammate pace):** weak / high-confounding by construction (fuel, tyre and traffic are not observed).

## 23. Most valuable additional data (for the strongest currently infeasible design: the hierarchy in 2018–2022)

1. **Timing71 replay ZIPs for 2018–2021** (already listed in the archive): exact lap timestamps would lift those sessions from D to B, adding four more years to Design 1 and 2 in Eras A and B.
2. **Official Section Results PDFs for 2022** (all sessions, primary source): the only lap-level route for 2022.
3. **HRRR for non-Day-1 event days:** solar/cloud context. Observed PTSC is already local.
4. **Run-plan context** (no-tow speed column, boost/fuel annotations) from the Timing71 feed columns, to narrow practice state confounding.

## 24. Recommended next scientific phase

A **pre-registered Design 1 descriptive comparison in 2023–2024 practice-type Tier A/B sessions** (Era B), with 2025 as a separate replication:
- **Question:** under matched close-time windows, how large are |Δ lap time| distances for same car vs same team/different car vs different team?
- **Units and dependence:** run-level units (stints), not laps, with cluster-aware summaries by car and team.
- **Scope:** qualifying (Day 1, Tier A) as a separate small-n stratum; race excluded or run only as a separately labelled, high-confounding sensitivity.
- **What it tests:** whether engineering-team identity removes variance beyond session matching, before any physics or latent modelling.

## 25–27

See the final summary and `phase4e_checks_log.txt`.
