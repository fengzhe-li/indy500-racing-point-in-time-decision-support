# V4 Phase 4E — Session Coverage Report

Every official 2018–2025 Indianapolis 500 session, plus Timing71-only captures, with source, timing resolution, weather and tier. Official names are preserved; categories follow spec §1.

- **Shared captures:** `lap_data_shared_by_n_official_segments > 1` means one Timing71 capture spans several official qualifying segments (e.g. Top-12 / Last Chance / Fast 6). Their lap data are identical, and totals count them once.
- **Qualifying regimes stay separate:** Day 1 vs Fast 9 / Positions 10-33 / 31-33 / Top-12 / Fast 12 / Last Chance / Fast 6 keep their official names in `subtype`, and no qualifying regimes are mixed.

| year | official_session_name | normalized_category | session_date | source_availability | timing_resolution | quality_tier | tier_reason | valid_laps | cars | multi_car_teams | weather_observed_in_span | lap_data_shared_by_n_official_segments |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | Practice 2 | PRACTICE | 2018-05-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 970 | 34 | 10 | True | 1 |
| 2018 | Practice 1 | PRACTICE | 2018-05-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 295 | 22 | 6 | True | 1 |
| 2018 | Practice 3 | PRACTICE | 2018-05-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 2,403 | 35 | 10 | True | 1 |
| 2018 | Practice 4 | PRACTICE | 2018-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,854 | 35 | 10 | True | 1 |
| 2018 | Practice 5 | FAST_FRIDAY | 2018-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 845 | 35 | 10 | True | 1 |
| 2018 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2018-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 73 | 24 | 7 | True | 1 |
| 2018 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2018-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 51 | 10 | 3 | True | 1 |
| 2018 | Qualifications - Fast 9 | QUALIFYING_OTHER | 2018-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 36 | 9 | 2 | True | 1 |
| 2018 | Qualifications - Positions 10-33 | QUALIFYING_OTHER | 2018-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 36 | 9 | 2 | True | 1 |
| 2018 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2018-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 205 | 24 | 7 | True | 1 |
| 2018 | Practice 8 | POST_QUALIFYING_PRACTICE | 2018-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,876 | 32 | 9 | True | 1 |
| 2018 | Final Practice | CARB_DAY | 2018-05-25 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 812 | 33 | 10 | True | 1 |
| 2018 | Race | RACE | 2018-05-27 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 4,031 | 33 | 10 | True | 1 |
| 2019 | Practice 1 | PRACTICE | 2019-05-14 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,710 | 36 | 10 | True | 1 |
| 2019 | Practice 2 | PRACTICE | 2019-05-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 2,344 | 36 | 10 | True | 1 |
| 2019 | Practice 3 | PRACTICE | 2019-05-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,172 | 35 | 10 | True | 1 |
| 2019 | Practice 4 | FAST_FRIDAY | 2019-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 840 | 35 | 10 | True | 1 |
| 2019 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2019-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 405 | 34 | 10 | True | 1 |
| 2019 | Practice 5 | QUALIFYING_WEEKEND_PRACTICE | 2019-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 46 | 6 | 1 | True | 1 |
| 2019 | Qualifications - Fast 9 | QUALIFYING_OTHER | 2019-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 57 | 15 | 3 | True | 2 |
| 2019 | Qualifications - Positions 31-33 | QUALIFYING_OTHER | 2019-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 57 | 15 | 3 | True | 2 |
| 2019 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2019-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 28 | 5 | 1 | True | 1 |
| 2019 | Practice 8 | POST_QUALIFYING_PRACTICE | 2019-05-20 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2019 | Practice Final | CARB_DAY | 2019-05-24 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2019 | Race | RACE | 2019-05-26 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 4,786 | 33 | 9 | True | 1 |
| 2020 | Practice 1 | PRACTICE | 2020-08-12 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,701 | 32 | 9 | True | 1 |
| 2020 | Practice 2 | PRACTICE | 2020-08-13 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 2,606 | 32 | 9 | True | 1 |
| 2020 | Practice 3 (Fast Friday) | FAST_FRIDAY | 2020-08-14 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 756 | 33 | 9 | True | 1 |
| 2020 | Qualifications (Day 1) | QUALIFYING_DAY1 | 2020-08-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 199 | 16 | 4 | True | 1 |
| 2020 | Practice 4 | QUALIFYING_WEEKEND_PRACTICE | 2020-08-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 171 | 33 | 9 | True | 1 |
| 2020 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2020-08-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,828 | 32 | 9 | True | 1 |
| 2020 | Qualifications (Fast 9) | QUALIFYING_OTHER | 2020-08-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 34 | 9 | 2 | True | 1 |
| 2020 | Practice 5 | QUALIFYING_WEEKEND_PRACTICE | 2020-08-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 15 | 2 | 1 | True | 1 |
| 2020 | Final Practice (Carb Day) | CARB_DAY | 2020-08-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,767 | 33 | 9 | True | 1 |
| 2020 | Race | RACE | 2020-08-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 3,573 | 32 | 9 | True | 1 |
| 2021 | Practice 2 | PRACTICE | 2021-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,345 | 35 | 9 | True | 1 |
| 2021 | Practice 1 | PRACTICE | 2021-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 284 | 29 | 7 | True | 1 |
| 2021 | Practice 3 | PRACTICE | 2021-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 2,442 | 34 | 9 | True | 1 |
| 2021 | Practice 4 | PRACTICE | 2021-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,970 | 35 | 9 | True | 1 |
| 2021 | Practice 5 | FAST_FRIDAY | 2021-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 670 | 35 | 9 | True | 1 |
| 2021 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2021-05-22 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 198 | 19 | 7 | True | 1 |
| 2021 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2021-05-22 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 65 | 9 | 2 | True | 1 |
| 2021 | Practice 8 | QUALIFYING_WEEKEND_PRACTICE | 2021-05-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,564 | 33 | 9 | True | 1 |
| 2021 | Qualifications - Fast 9 | QUALIFYING_OTHER | 2021-05-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 65 | 14 | 3 | True | 2 |
| 2021 | Qualifications - Last Row | QUALIFYING_OTHER | 2021-05-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 65 | 14 | 3 | True | 2 |
| 2021 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2021-05-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 34 | 6 | 0 | True | 1 |
| 2021 | Final Practice (Carb Day) | CARB_DAY | 2021-05-28 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 1,754 | 33 | 9 | True | 1 |
| 2021 | Race | RACE | 2021-05-30 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 5,158 | 33 | 9 | True | 1 |
| 2022 | Practice 2 (All Cars) | PRACTICE | 2022-05-17 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Practice 1 (Oval Veterans) | PRACTICE | 2022-05-17 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Practice 4 | PRACTICE | 2022-05-19 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Practice 5 (Fast Friday) | FAST_FRIDAY | 2022-05-20 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2022-05-21 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2022-05-21 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | 2022-05-22 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | False | 0 |
| 2022 | Qualifications - Top 12 | QUALIFYING_OTHER | 2022-05-22 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | False | 0 |
| 2022 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2022-05-22 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | False | 0 |
| 2022 | Practice 8 | POST_QUALIFYING_PRACTICE | 2022-05-23 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Practice 9 (Carb Day) | CARB_DAY | 2022-05-27 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2022 | Race | RACE | 2022-05-29 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2023 | (not in official list) Practice 1 | PRACTICE | 2023-05-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | STINT_TIMESTAMP_ONLY (lap times derived) | D | not T / not I / <2 multi-car teams / aggregate | 0 | 0 | 0 | False | 1 |
| 2023 | Practice 3 | PRACTICE | 2023-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 2,552 | 34 | 11 | True | 1 |
| 2023 | Practice 4 | PRACTICE | 2023-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 2,340 | 34 | 11 | True | 1 |
| 2023 | Practice 5 | FAST_FRIDAY | 2023-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 515 | 34 | 11 | True | 1 |
| 2023 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2023-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | A | all criteria met | 233 | 34 | 11 | True | 1 |
| 2023 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2023-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | limitations: state_open_track,M,O | 48 | 7 | 2 | True | 1 |
| 2023 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | 2023-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: O | 77 | 16 | 4 | True | 3 |
| 2023 | Qualifications - Last Chance | QUALIFYING_OTHER | 2023-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: O | 77 | 16 | 4 | True | 3 |
| 2023 | Qualifications - Top-12 | QUALIFYING_OTHER | 2023-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: O | 77 | 16 | 4 | True | 3 |
| 2023 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2023-05-21 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 94 | 15 | 4 | True | 1 |
| 2023 | Practice 8 | POST_QUALIFYING_PRACTICE | 2023-05-22 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,392 | 33 | 11 | True | 1 |
| 2023 | Final Practice | CARB_DAY | 2023-05-26 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,763 | 33 | 11 | True | 1 |
| 2023 | Race | RACE | 2023-05-28 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | race state confounded; limitations: none | 647 | 33 | 11 | True | 1 |
| 2024 | Practice 1 | PRACTICE | 2024-05-14 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 128 | 24 | 7 | True | 1 |
| 2024 | Practice 3 | PRACTICE | 2024-05-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,577 | 34 | 11 | True | 1 |
| 2024 | Practice 4 | PRACTICE | 2024-05-16 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2024 | Practice 5 | FAST_FRIDAY | 2024-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 164 | 27 | 8 | True | 1 |
| 2024 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2024-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | A | all criteria met | 161 | 27 | 9 | True | 1 |
| 2024 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2024-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | D | not T / not I / <2 multi-car teams / aggregate | 34 | 5 | 1 | True | 1 |
| 2024 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | 2024-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: O | 31 | 10 | 3 | True | 1 |
| 2024 | Qualifications - Last Chance | QUALIFYING_OTHER | 2024-05-19 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2024 | Qualifications - Top-12 | QUALIFYING_OTHER | 2024-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | limitations: M,O | 36 | 12 | 2 | True | 1 |
| 2024 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2024-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | limitations: state_open_track,O | 96 | 15 | 5 | True | 1 |
| 2024 | Practice 8 | POST_QUALIFYING_PRACTICE | 2024-05-20 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,960 | 33 | 10 | True | 1 |
| 2024 | Final Practice (Carb Day) | CARB_DAY | 2024-05-24 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 2,120 | 33 | 10 | True | 1 |
| 2024 | Race | RACE | 2024-05-26 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | race state confounded; limitations: none | 5,104 | 29 | 10 | True | 1 |
| 2025 | Practice 1 | PRACTICE | 2025-05-13 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 596 | 34 | 12 | True | 1 |
| 2025 | Practice 3 | PRACTICE | 2025-05-14 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 730 | 34 | 12 | True | 1 |
| 2025 | Practice 4 | PRACTICE | 2025-05-15 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,714 | 34 | 12 | True | 1 |
| 2025 | Practice 5 | FAST_FRIDAY | 2025-05-16 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 313 | 33 | 12 | True | 1 |
| 2025 | Qualifications - Day 1 | QUALIFYING_DAY1 | 2025-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | A | all criteria met | 263 | 34 | 12 | True | 1 |
| 2025 | Practice 6 | QUALIFYING_WEEKEND_PRACTICE | 2025-05-17 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 108 | 23 | 8 | True | 1 |
| 2025 | Combined Qualifications | AGGREGATE_RESULT | 2025-05-18 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2025 | Qualifications - Firestone Fast 6 | QUALIFYING_OTHER | 2025-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: O | 40 | 10 | 3 | True | 1 |
| 2025 | Qualifications - Last Chance | QUALIFYING_OTHER | 2025-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | limitations: M,O | 29 | 9 | 2 | True | 1 |
| 2025 | Qualifications - Top-12 | QUALIFYING_OTHER | 2025-05-18 | OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested) | SESSION_LEVEL_ONLY | D | not T / not I / <2 multi-car teams / aggregate |  |  |  | True | 0 |
| 2025 | Practice 7 | QUALIFYING_WEEKEND_PRACTICE | 2025-05-18 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 60 | 11 | 3 | True | 1 |
| 2025 | Practice 8 | POST_QUALIFYING_PRACTICE | 2025-05-19 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,548 | 33 | 11 | True | 1 |
| 2025 | Final Practice (Carb Day) | CARB_DAY | 2025-05-23 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | B | limitation: state_open_track | 1,414 | 33 | 11 | True | 1 |
| 2025 | Race | RACE | 2025-05-25 | OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON | OBSERVED_LAP_TIMESTAMP | C | race state confounded; limitations: none | 4,039 | 31 | 11 | True | 1 |
