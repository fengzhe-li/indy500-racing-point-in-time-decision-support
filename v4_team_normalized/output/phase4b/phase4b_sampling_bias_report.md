# V4 Phase 4B — Sampling / Selection-Bias Report

Qualifying attempt times are chosen by teams, not randomised. This report measures how strongly car identity and time are entangled within each team-year.

**Metrics:**
- **η²:** the share of the within-team-year variance of attempt time explained by car identity. It is descriptive only.
- **Overlapping car pairs:** pairs of cars whose [first, last] attempt-time ranges overlap.
- **Dominance:** the largest share one car holds of the early and late tertiles.

**Severity labels are triage only:** SEVERE means η² ≥ 0.5 *or* no two cars overlap in time; MODERATE means 0.25–0.5; LOW means below 0.25. They are not tests.

| era | LOW | MODERATE | NOT_ASSESSABLE | SEVERE |
|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 0 | 0 | 12 | 10 |
| ERA_B_FROZEN_REFERENCE | 5 | 4 | 23 | 10 |
| ERA_C_HYBRID_EXTERNAL | 5 | 1 | 2 | 4 |

| era | year | canonical_engineering_team | cars | attempts | eta2_time_explained_by_car | car_pairs | car_pairs_with_overlapping_time_ranges | early_tertile_dominant_car | early_tertile_dominant_share | late_tertile_dominant_car | late_tertile_dominant_share | max_attempt_share_one_car | confounding_severity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | AJ_FOYT | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | ANDRETTI | 4 | 4 | 1 | 6 | 0 | 25 | 0.5 | 26 | 1 | 0.25 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | ARROW_MCLAREN_SPM | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | CARLIN | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | DALE_COYNE_RACING | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | DREYER_REINBOLD_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | ED_CARPENTER_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2018 | JUNCOS_HOLLINGER_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | AJ_FOYT | 2 | 3 | 0.87 | 1 | 0 | 14 | 1 | 4 | 1 | 0.67 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | ANDRETTI | 3 | 4 | 0.29 | 3 | 0 | 25 | 0.5 | 25 | 1 | 0.5 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | ARROW_MCLAREN_SPM | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | CARLIN | 3 | 3 | 1 | 3 | 0 | 23 | 1 | 31 | 1 | 0.33 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | CHIP_GANASSI_RACING | 2 | 3 | 0.82 | 1 | 0 | 9 | 1 | 10 | 1 | 0.67 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | CLAUSON_MARSHALL_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | DALE_COYNE_RACING | 3 | 3 | 1 | 3 | 0 | 18 | 1 | 33 | 1 | 0.33 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | DRAGONSPEED | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | DREYER_REINBOLD_RACING | 2 | 4 | 0.31 | 1 | 0 | 48 | 1 | 48 | 1 | 0.75 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | ED_CARPENTER_RACING | 3 | 3 | 1 | 3 | 0 | 21 | 1 | 63 | 1 | 0.33 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | JUNCOS_HOLLINGER_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | MEYER_SHANK_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | RAHAL_LETTERMAN_LANIGAN | 2 | 4 | 0.54 | 1 | 0 | 30 | 0.5 | 15 | 1 | 0.75 | SEVERE |
| ERA_A_PRE_AEROSCREEN_EXT | 2019 | TEAM_PENSKE | 4 | 4 | 1 | 6 | 0 | 12 | 0.5 | 2 | 1 | 0.25 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2020 | AJ_FOYT | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | ANDRETTI | 5 | 6 | 0.79 | 10 | 0 | 27 | 0.5 | 88 | 1 | 0.33 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2020 | ARROW_MCLAREN_SPM | 3 | 4 | 0.23 | 3 | 0 | 5 | 0.5 | 5 | 1 | 0.5 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2020 | CARLIN | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | CHIP_GANASSI_RACING | 3 | 6 | 0.1 | 3 | 1 | 9 | 0.5 | 8 | 0.5 | 0.5 | LOW |
| ERA_B_FROZEN_REFERENCE | 2020 | DALE_COYNE_RACING | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | DRAGONSPEED | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | DREYER_REINBOLD_RACING | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | ED_CARPENTER_RACING | 3 | 5 | 0.52 | 3 | 1 | 21 | 0.5 | 20 | 0.5 | 0.4 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2020 | MEYER_SHANK_RACING | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | RAHAL_LETTERMAN_LANIGAN | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2020 | TEAM_PENSKE | 3 | 4 | 0.73 | 3 | 0 | 1 | 0.5 | 3 | 1 | 0.5 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | AJ_FOYT | 4 | 5 | 0.35 | 6 | 0 | 1 | 0.5 | 14 | 0.5 | 0.4 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | ANDRETTI | 6 | 11 | 0.3 | 15 | 3 | 98 | 0.25 | 25 | 0.5 | 0.27 | MODERATE |
| ERA_B_FROZEN_REFERENCE | 2021 | ARROW_MCLAREN_SPM | 3 | 5 | 0.16 | 3 | 1 | 86 | 0.5 | 86 | 0.5 | 0.4 | LOW |
| ERA_B_FROZEN_REFERENCE | 2021 | CARLIN | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2021 | CHIP_GANASSI_RACING | 3 | 3 | 1 | 3 | 0 | 9 | 1 | 8 | 1 | 0.33 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | DALE_COYNE_RACING | 2 | 3 | 0.13 | 1 | 0 | 18 | 1 | 18 | 1 | 0.67 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | ED_CARPENTER_RACING | 3 | 5 | 0.29 | 3 | 1 | 21 | 0.5 | 21 | 0.5 | 0.4 | MODERATE |
| ERA_B_FROZEN_REFERENCE | 2021 | MEYER_SHANK_RACING | 2 | 3 | 0.86 | 1 | 0 | 6 | 1 | 60 | 1 | 0.67 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | RAHAL_LETTERMAN_LANIGAN | 3 | 3 | 1 | 3 | 0 | 30 | 1 | 15 | 1 | 0.33 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2021 | TEAM_PENSKE | 4 | 6 | 0.34 | 6 | 1 | 2 | 0.5 | 2 | 0.5 | 0.33 | MODERATE |
| ERA_B_FROZEN_REFERENCE | 2021 | TOP_GUN_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2022 | ARROW_MCLAREN_SPM | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2022 | ED_CARPENTER_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2022 | TEAM_PENSKE | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | ABEL_MOTORSPORTS | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | AJ_FOYT | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | ANDRETTI | 2 | 5 | 0.17 | 1 | 1 | 29 | 0.5 | 27 | 1 | 0.6 | LOW |
| ERA_B_FROZEN_REFERENCE | 2023 | ARROW_MCLAREN_SPM | 4 | 7 | 0.28 | 6 | 1 | 7 | 0.33 | 66 | 0.5 | 0.43 | MODERATE |
| ERA_B_FROZEN_REFERENCE | 2023 | CHIP_GANASSI_RACING | 4 | 8 | 0.06 | 6 | 3 | 8 | 0.33 | 9 | 0.33 | 0.38 | LOW |
| ERA_B_FROZEN_REFERENCE | 2023 | DALE_COYNE_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | DREYER_REINBOLD_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | ED_CARPENTER_RACING | 2 | 4 | 0.24 | 1 | 0 | 33 | 0.5 | 33 | 1 | 0.75 | SEVERE |
| ERA_B_FROZEN_REFERENCE | 2023 | JUNCOS_HOLLINGER_RACING | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2023 | RAHAL_LETTERMAN_LANIGAN | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2024 | ARROW_MCLAREN_SPM | 3 | 6 | 0.11 | 3 | 3 | 7 | 0.5 | 6 | 0.5 | 0.33 | LOW |
| ERA_B_FROZEN_REFERENCE | 2024 | CHIP_GANASSI_RACING | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2024 | DREYER_REINBOLD_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2024 | ED_CARPENTER_RACING | 1 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2024 | MEYER_SHANK_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_B_FROZEN_REFERENCE | 2024 | TEAM_PENSKE | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_C_HYBRID_EXTERNAL | 2025 | AJ_FOYT | 2 | 4 | 0.05 | 1 | 1 | 4 | 0.5 | 4 | 1 | 0.5 | LOW |
| ERA_C_HYBRID_EXTERNAL | 2025 | ANDRETTI | 4 | 8 | 0.56 | 6 | 1 | 28 | 0.33 | 98 | 0.67 | 0.5 | SEVERE |
| ERA_C_HYBRID_EXTERNAL | 2025 | ARROW_MCLAREN_SPM | 4 | 7 | 0.24 | 6 | 3 | 5 | 0.33 | 17 | 0.5 | 0.29 | LOW |
| ERA_C_HYBRID_EXTERNAL | 2025 | CHIP_GANASSI_RACING | 2 | 2 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_C_HYBRID_EXTERNAL | 2025 | DALE_COYNE_RACING | 2 | 3 | 0.44 | 1 | 0 | 51 | 1 | 18 | 1 | 0.67 | SEVERE |
| ERA_C_HYBRID_EXTERNAL | 2025 | DREYER_REINBOLD_RACING | 2 | 4 | 0 | 1 | 1 | 23 | 0.5 | 24 | 1 | 0.5 | LOW |
| ERA_C_HYBRID_EXTERNAL | 2025 | ED_CARPENTER_RACING | 3 | 7 | 0.06 | 3 | 1 | 20 | 0.67 | 33 | 0.5 | 0.57 | LOW |
| ERA_C_HYBRID_EXTERNAL | 2025 | JUNCOS_HOLLINGER_RACING | 2 | 5 | 0 | 1 | 1 | 76 | 0.5 | 77 | 0.5 | 0.6 | LOW |
| ERA_C_HYBRID_EXTERNAL | 2025 | MEYER_SHANK_RACING | 1 | 1 |  |  |  |  |  |  |  |  | NOT_ASSESSABLE |
| ERA_C_HYBRID_EXTERNAL | 2025 | PREMA_RACING | 2 | 3 | 0.69 | 1 | 0 | 83 | 1 | 90 | 1 | 0.67 | SEVERE |
| ERA_C_HYBRID_EXTERNAL | 2025 | RAHAL_LETTERMAN_LANIGAN | 4 | 7 | 0.3 | 6 | 3 | 15 | 0.33 | 75 | 0.5 | 0.29 | MODERATE |
| ERA_C_HYBRID_EXTERNAL | 2025 | TEAM_PENSKE | 3 | 4 | 0.73 | 3 | 0 | 3 | 0.5 | 12 | 1 | 0.5 | SEVERE |

## Per-car attempt-time distributions (minutes from the session's first timed attempt)

| year | canonical_engineering_team | per_car_time_distribution |
|---|---|---|
| 2018 | ANDRETTI | #25: n=1, t=192–192 min, median 192; #26: n=1, t=219–219 min, median 219; #27: n=1, t=206–206 min, median 206; #98: n=1, t=215–215 min, median 215 |
| 2019 | AJ_FOYT | #4: n=2, t=172–258 min, median 215; #14: n=1, t=25–25 min, median 25 |
| 2019 | ANDRETTI | #25: n=2, t=0–292 min, median 146; #27: n=1, t=10–10 min, median 10; #28: n=1, t=182–182 min, median 182 |
| 2019 | CARLIN | #23: n=1, t=34–34 min, median 34; #31: n=1, t=162–162 min, median 162; #59: n=1, t=49–49 min, median 49 |
| 2019 | CHIP_GANASSI_RACING | #9: n=1, t=136–136 min, median 136; #10: n=2, t=277–383 min, median 330 |
| 2019 | DALE_COYNE_RACING | #18: n=1, t=20–20 min, median 20; #19: n=1, t=58–58 min, median 58; #33: n=1, t=68–68 min, median 68 |
| 2019 | DREYER_REINBOLD_RACING | #24: n=1, t=396–396 min, median 396; #48: n=3, t=177–401 min, median 218 |
| 2019 | ED_CARPENTER_RACING | #20: n=1, t=15–15 min, median 15; #21: n=1, t=5–5 min, median 5; #63: n=1, t=73–73 min, median 73 |
| 2019 | RAHAL_LETTERMAN_LANIGAN | #15: n=3, t=167–406 min, median 297; #30: n=1, t=77–77 min, median 77 |
| 2019 | TEAM_PENSKE | #2: n=1, t=126–126 min, median 126; #3: n=1, t=121–121 min, median 121; #12: n=1, t=39–39 min, median 39; #22: n=1, t=82–82 min, median 82 |
| 2020 | ANDRETTI | #27: n=1, t=53–53 min, median 53; #28: n=1, t=63–63 min, median 63; #29: n=1, t=92–92 min, median 92; #88: n=2, t=143–245 min, median 194; #98: n=1, t=133–133 min, median 133 |
| 2020 | ARROW_MCLAREN_SPM | #5: n=2, t=34–322 min, median 178; #7: n=1, t=78–78 min, median 78; #66: n=1, t=58–58 min, median 58 |
| 2020 | CHIP_GANASSI_RACING | #8: n=2, t=72–196 min, median 134; #9: n=3, t=25–254 min, median 180; #10: n=1, t=82–82 min, median 82 |
| 2020 | ED_CARPENTER_RACING | #20: n=2, t=87–227 min, median 157; #21: n=1, t=16–16 min, median 16; #47: n=2, t=118–240 min, median 179 |
| 2020 | TEAM_PENSKE | #1: n=1, t=39–39 min, median 39; #3: n=2, t=153–278 min, median 216; #22: n=1, t=128–128 min, median 128 |
| 2021 | AJ_FOYT | #1: n=1, t=75–75 min, median 75; #4: n=2, t=103–345 min, median 224; #11: n=1, t=149–149 min, median 149; #14: n=1, t=154–154 min, median 154 |
| 2021 | ANDRETTI | #25: n=3, t=28–311 min, median 185; #26: n=2, t=131–264 min, median 197; #27: n=1, t=136–136 min, median 136; #28: n=1, t=9–9 min, median 9; #29: n=1, t=23–23 min, median 23; #98: n=3, t=4–324 min, median 173 |
| 2021 | ARROW_MCLAREN_SPM | #5: n=1, t=89–89 min, median 89; #7: n=2, t=94–320 min, median 207; #86: n=2, t=70–301 min, median 186 |
| 2021 | CHIP_GANASSI_RACING | #8: n=1, t=140–140 min, median 140; #9: n=1, t=0–0 min, median 0; #48: n=1, t=32–32 min, median 32 |
| 2021 | DALE_COYNE_RACING | #18: n=2, t=18–306 min, median 162; #51: n=1, t=65–65 min, median 65 |
| 2021 | ED_CARPENTER_RACING | #20: n=1, t=84–84 min, median 84; #21: n=2, t=42–168 min, median 105; #47: n=2, t=108–234 min, median 171 |
| 2021 | MEYER_SHANK_RACING | #06: n=1, t=13–13 min, median 13; #60: n=2, t=117–181 min, median 149 |
| 2021 | RAHAL_LETTERMAN_LANIGAN | #15: n=1, t=112–112 min, median 112; #30: n=1, t=51–51 min, median 51; #45: n=1, t=56–56 min, median 56 |
| 2021 | TEAM_PENSKE | #2: n=2, t=38–163 min, median 100; #3: n=1, t=47–47 min, median 47; #12: n=2, t=80–332 min, median 206; #22: n=1, t=126–126 min, median 126 |
| 2023 | ANDRETTI | #27: n=3, t=111–286 min, median 233; #29: n=2, t=59–221 min, median 140 |
| 2023 | ARROW_MCLAREN_SPM | #5: n=1, t=73–73 min, median 73; #6: n=2, t=31–318 min, median 174; #7: n=1, t=9–9 min, median 9; #66: n=3, t=36–309 min, median 214 |
| 2023 | CHIP_GANASSI_RACING | #8: n=3, t=0–274 min, median 170; #9: n=2, t=13–223 min, median 118; #10: n=1, t=101–101 min, median 101; #11: n=2, t=87–265 min, median 176 |
| 2023 | ED_CARPENTER_RACING | #21: n=1, t=68–68 min, median 68; #33: n=3, t=41–323 min, median 241 |
| 2024 | ARROW_MCLAREN_SPM | #5: n=2, t=275–327 min, median 301; #6: n=2, t=206–331 min, median 269; #7: n=2, t=168–331 min, median 250 |
| 2025 | AJ_FOYT | #4: n=2, t=79–372 min, median 226; #14: n=2, t=84–258 min, median 171 |
| 2025 | ANDRETTI | #26: n=1, t=341–341 min, median 341; #27: n=2, t=141–279 min, median 210; #28: n=1, t=0–0 min, median 0; #98: n=4, t=107–389 min, median 292 |
| 2025 | ARROW_MCLAREN_SPM | #5: n=1, t=5–5 min, median 5; #6: n=2, t=42–244 min, median 143; #7: n=2, t=33–288 min, median 160; #17: n=2, t=93–248 min, median 171 |
| 2025 | DALE_COYNE_RACING | #18: n=2, t=155–318 min, median 236; #51: n=1, t=112–112 min, median 112 |
| 2025 | DREYER_REINBOLD_RACING | #23: n=2, t=23–331 min, median 177; #24: n=2, t=28–345 min, median 187 |
| 2025 | ED_CARPENTER_RACING | #20: n=4, t=18–363 min, median 231; #21: n=1, t=297–297 min, median 297; #33: n=2, t=102–336 min, median 219 |
| 2025 | JUNCOS_HOLLINGER_RACING | #76: n=3, t=46–402 min, median 201; #77: n=2, t=131–267 min, median 199 |
| 2025 | PREMA_RACING | #83: n=1, t=14–14 min, median 14; #90: n=2, t=150–322 min, median 236 |
| 2025 | RAHAL_LETTERMAN_LANIGAN | #15: n=1, t=37–37 min, median 37; #30: n=2, t=145–310 min, median 227; #45: n=2, t=122–367 min, median 244; #75: n=2, t=98–354 min, median 226 |
| 2025 | TEAM_PENSKE | #2: n=1, t=181–181 min, median 181; #3: n=1, t=126–126 min, median 126; #12: n=2, t=239–376 min, median 308 |

## Attempt sequence distribution

`car_baseline_summary.csv` gives attempts per car (total, complete, timed, on the timeline). It also gives `timeline_vs_all_mean_gap`, the difference between a car's timed-attempt mean and its all-complete-attempt mean. That gap shows how timestamp coverage itself selects attempts: in 2023 and 2024, recorder coverage misses part of the session.

| era | cars | median_abs_gap_mph | max_abs_gap_mph |
|---|---|---|---|
| ERA_A_PRE_AEROSCREEN_EXT | 42 | 0 | 3.1 |
| ERA_B_FROZEN_REFERENCE | 93 | 0 | 0.76 |
| ERA_C_HYBRID_EXTERNAL | 31 | 0 | 0.59 |

## Flags

- Every **SEVERE** team-year is one where a temporal performance pattern cannot be separated from which car ran. Temporal movement there must not be read as environmental.
- **Era A (2018–19)** is SEVERE or not assessable everywhere: Timing71 matched too few attempts per car.
- **Selection mechanisms** that cannot be observed in these data include:
  - re-running only when an improvement is expected;
  - withdrawing a retained time;
  - queue position and priority-lane rules;
  - setup and trim changes between runs.

Positive within-car time trends are the expected signature of such selection.
