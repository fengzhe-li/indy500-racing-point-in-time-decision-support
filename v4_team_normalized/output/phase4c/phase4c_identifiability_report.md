# V4 Phase 4C — Identifiability Report (2025, P_wx)

Effective sample: 7 teams · 21 cars · 21 drivers · 41 attempts (16 cars informative under car FE; one session/year).

| diagnostic | value | note |
|---|---|---|
| pearson_track_vs_time | 0.3822 |  |
| spearman_track_vs_time | 0.2445 |  |
| pearson_ambient_vs_time | 0.9484 |  |
| spearman_ambient_vs_time | 0.9545 |  |
| pearson_track_vs_ambient | 0.5415 |  |
| spearman_track_vs_ambient | 0.3179 |  |
| distinct_track_values | 35 |  |
| track_min | 34.37 |  |
| track_max | 44.08 |  |
| track_range | 9.71 |  |
| within_car_track_sd_median | 2.135 | cars with >=2 rows: 16 |
| within_car_track_sd_min | 0.5257 |  |
| within_car_track_range_median | 3.019 |  |
| within_car_track_range_min | 0.7434 |  |
| within_team_track_sd_median | 2.461 |  |
| within_team_track_range_median | 6.906 |  |
| share_of_track_variance_within_car | 0.4584 |  |
| distinct_ambient_values | 23 |  |
| ambient_min | 19.68 |  |
| ambient_max | 23.2 |  |
| ambient_range | 3.515 |  |
| within_car_ambient_sd_median | 1.179 | cars with >=2 rows: 16 |
| within_car_ambient_sd_min | 0.08333 |  |
| within_car_ambient_range_median | 1.784 |  |
| within_car_ambient_range_min | 0.1179 |  |
| within_team_ambient_sd_median | 1.104 |  |
| within_team_ambient_range_median | 2.778 |  |
| share_of_ambient_variance_within_car | 0.6312 |  |
| distinct_time_values | 41 |  |
| time_min | 0 |  |
| time_max | 389 |  |
| time_range | 389 |  |
| within_car_time_sd_median | 144.6 | cars with >=2 rows: 16 |
| within_car_time_sd_min | 96.45 |  |
| within_car_time_range_median | 239.7 |  |
| within_car_time_range_min | 136.4 |  |
| within_team_time_sd_median | 135.3 |  |
| within_team_time_range_median | 322.5 |  |
| share_of_time_variance_within_car | 0.7133 |  |
| eta2_time_on_car | 0.2867 | car/time confounding |
| eta2_time_on_team | 0.07122 | team/time confounding |
| within_vif_M2_track | 1.153 | within-car demeaned design; >=10 flags weak identification |
| within_vif_M2_ambient | 1.153 | within-car demeaned design; >=10 flags weak identification |
| within_vif_M3_time | 23.15 | within-car demeaned design; >=10 flags weak identification |
| within_vif_M3_track | 1.749 | within-car demeaned design; >=10 flags weak identification |
| within_vif_M3_ambient | 25.49 | within-car demeaned design; >=10 flags weak identification |
| within_vif_M1_time | 1 | within-car demeaned design; >=10 flags weak identification |
| within_condition_number_M3_standardised | 10.16 |  |
| within_car_pearson_track_vs_time | 0.2135 | after removing car means |
| within_car_pearson_ambient_vs_time | 0.9667 | after removing car means |
| within_car_pearson_track_vs_ambient | 0.3647 | after removing car means |

## Reading

- **Track temperature** has 35 distinct (interpolated) values over a 9.7 °C range, and 46% of its variance is within cars. Within cars it is only weakly related to session time (r = 0.21), so it is identifiable in both M2 and M3 (within VIF ≤ 1.75). Caveat: 2025 values are linear interpolations between 15-minute PTSC observations, not attempt-exact measurements.
- **Ambient temperature** spans only 3.52 °C. Within cars it is almost perfectly collinear with session time (r = 0.967); in M3 its within VIF is 25.5, and time's is 23.2. That makes ambient and time **not separately identifiable**. Some cars have very little within-car ambient variation (minimum within-car range 0.12 °C).
- **Car/time confounding** is η² = 0.29; **team/time confounding** is η² = 0.07. Both are modest in 2025, so within-car time variation is ample (median within-car time range 240 min).
- **Design conditioning:** the standardised within-demeaned M3 design has condition number 10.2.
- **Excluded inputs:** wind (units unverified) and solar (not available). No values were imputed.

Figure: `figures/fig01_02_state_vs_time_and_track_vs_ambient.png`.
