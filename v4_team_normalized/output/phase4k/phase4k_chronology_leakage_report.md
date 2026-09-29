# V4 Phase 4K — Chronology / Leakage Report

## Information cutoff

**Primary cutoff:**
- `prediction_time` = the timestamp of t1's first eligible lap. Every predictor input must be **strictly earlier**.
- Records in the same feed update as the first outcome lap (equal timestamp) are never treated as prior. No within-update order is invented.

**Conservative cutoff (sensitivity):** `prediction_time` = t0's completion.

## Label leakage (the binding constraint)

**The issue:** Phase 4H class labels are retrospective. They use 4-lap windows that can extend after a lap, and the car's session-best steady level.

**Point-in-time confirmation:**
- Each predictor-side car-block (t0, s0, s1, q0, q1) was **re-confirmed** with the *unchanged* rule and thresholds, using only laps before the cutoff.
- This removes selection leakage for the predictor side.

**F4 events:**
- t0 confirmable: 8 of 22.
- Each of those had at least one fully confirmable teammate/placebo combination.

**Outcome labels (t1) remain retrospective.** The target population is defined ex post, and eligibility depends on t1's level relative to the session best. This applies equally to P0–P3, but it is a real selection on the outcome.

## Horizons

| population | level | quantity | n | p10 | p25 | median | p75 | p90 | max |
|---|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | F0 | target_horizon_s (t1 - prediction_time) | 113 | 0 | 19.97 | 21.193 | 41.352 | 61.134 | 142.319 |
| PRIMARY_TIER1_2023_2024 | F0 | target_baseline_interval_s (t1 - t0) | 113 | 80.303 | 81.143 | 83.707 | 123.679 | 2323.113 | 14316.412 |
| PRIMARY_TIER1_2023_2024 | F0 | teammate_signal_age_s (prediction_time - s1) | 60 | 224.898 | 686.866 | 2529.254 | 5481.587 | 13359.456 | 17094.736 |
| PRIMARY_TIER1_2023_2024 | F0 | teammate_movement_interval_s (s1 - s0) | 60 | 80.321 | 80.4 | 81.871 | 101.596 | 123.044 | 4395.174 |
| PRIMARY_TIER1_2023_2024 | F0 | placebo_signal_age_s | 48 | 211.08 | 636.301 | 1895.289 | 3898.881 | 5636.437 | 11381.494 |
| PRIMARY_TIER1_2023_2024 | F0 | placebo_movement_interval_s | 48 | 81.342 | 81.579 | 101.264 | 102.02 | 132.754 | 182.472 |
| PRIMARY_TIER1_2023_2024 | F3 | target_horizon_s (t1 - prediction_time) | 44 | 0 | 20.091 | 40.088 | 41.44 | 61.131 | 101.939 |
| PRIMARY_TIER1_2023_2024 | F3 | target_baseline_interval_s (t1 - t0) | 44 | 80.182 | 81.037 | 91.502 | 1327.621 | 4110.799 | 14316.412 |
| PRIMARY_TIER1_2023_2024 | F3 | teammate_signal_age_s (prediction_time - s1) | 60 | 224.898 | 686.866 | 2529.254 | 5481.587 | 13359.456 | 17094.736 |
| PRIMARY_TIER1_2023_2024 | F3 | teammate_movement_interval_s (s1 - s0) | 60 | 80.321 | 80.4 | 81.871 | 101.596 | 123.044 | 4395.174 |
| PRIMARY_TIER1_2023_2024 | F3 | placebo_signal_age_s | 48 | 211.08 | 636.301 | 1895.289 | 3898.881 | 5636.437 | 11381.494 |
| PRIMARY_TIER1_2023_2024 | F3 | placebo_movement_interval_s | 48 | 81.342 | 81.579 | 101.264 | 102.02 | 132.754 | 182.472 |
| PRIMARY_TIER1_2023_2024 | F5 | target_horizon_s (t1 - prediction_time) | 8 | 14.043 | 20.532 | 60.434 | 61.117 | 61.151 | 61.177 |
| PRIMARY_TIER1_2023_2024 | F5 | target_baseline_interval_s (t1 - t0) | 8 | 81.952 | 97.895 | 2082.291 | 4710.492 | 7924.751 | 13217.467 |
| PRIMARY_TIER1_2023_2024 | F5 | teammate_signal_age_s (prediction_time - s1) | 13 | 242.319 | 529.609 | 902.92 | 4473.37 | 5601.855 | 11460.159 |
| PRIMARY_TIER1_2023_2024 | F5 | teammate_movement_interval_s (s1 - s0) | 13 | 80.623 | 81.517 | 82.359 | 101.596 | 119.334 | 182.472 |
| PRIMARY_TIER1_2023_2024 | F5 | placebo_signal_age_s | 14 | 285.421 | 784.135 | 902.812 | 5356.427 | 5795.825 | 11381.494 |
| PRIMARY_TIER1_2023_2024 | F5 | placebo_movement_interval_s | 14 | 80.771 | 81.643 | 101.877 | 102.02 | 142.306 | 163.578 |
| TIER2_2023_2024_EXTENDED | F0 | target_horizon_s (t1 - prediction_time) | 258 | 0 | 20.069 | 40.143 | 60.295 | 62.763 | 184.168 |
| TIER2_2023_2024_EXTENDED | F0 | target_baseline_interval_s (t1 - t0) | 258 | 80.307 | 81.885 | 122.066 | 1834.604 | 5983.98 | 20598.891 |
| TIER2_2023_2024_EXTENDED | F0 | teammate_signal_age_s (prediction_time - s1) | 192 | 224.136 | 850.196 | 2130.494 | 5470.734 | 12394.442 | 18897.441 |
| TIER2_2023_2024_EXTENDED | F0 | teammate_movement_interval_s (s1 - s0) | 192 | 80.321 | 81.051 | 101.596 | 1082.998 | 3336.257 | 13217.467 |
| TIER2_2023_2024_EXTENDED | F0 | placebo_signal_age_s | 169 | 218.245 | 890.599 | 1905.407 | 3991.219 | 5771.688 | 18522.505 |
| TIER2_2023_2024_EXTENDED | F0 | placebo_movement_interval_s | 169 | 81.513 | 83.249 | 101.949 | 123.185 | 163.584 | 13285.988 |
| TIER2_2023_2024_EXTENDED | F3 | target_horizon_s (t1 - prediction_time) | 129 | 0 | 20.101 | 40.234 | 61.029 | 80.547 | 123.625 |
| TIER2_2023_2024_EXTENDED | F3 | target_baseline_interval_s (t1 - t0) | 129 | 80.356 | 81.947 | 224.759 | 2331.94 | 7728.285 | 20598.891 |
| TIER2_2023_2024_EXTENDED | F3 | teammate_signal_age_s (prediction_time - s1) | 192 | 224.136 | 850.196 | 2130.494 | 5470.734 | 12394.442 | 18897.441 |
| TIER2_2023_2024_EXTENDED | F3 | teammate_movement_interval_s (s1 - s0) | 192 | 80.321 | 81.051 | 101.596 | 1082.998 | 3336.257 | 13217.467 |
| TIER2_2023_2024_EXTENDED | F3 | placebo_signal_age_s | 169 | 218.245 | 890.599 | 1905.407 | 3991.219 | 5771.688 | 18522.505 |
| TIER2_2023_2024_EXTENDED | F3 | placebo_movement_interval_s | 169 | 81.513 | 83.249 | 101.949 | 123.185 | 163.584 | 13285.988 |
| TIER2_2023_2024_EXTENDED | F5 | target_horizon_s (t1 - prediction_time) | 36 | 0 | 20.537 | 60.192 | 61.047 | 61.935 | 100.846 |
| TIER2_2023_2024_EXTENDED | F5 | target_baseline_interval_s (t1 - t0) | 36 | 350.739 | 1341.996 | 2410.465 | 5591.6 | 10823.256 | 20598.891 |
| TIER2_2023_2024_EXTENDED | F5 | teammate_signal_age_s (prediction_time - s1) | 62 | 317.863 | 862.538 | 1804.184 | 3844.829 | 11287.507 | 18522.505 |
| TIER2_2023_2024_EXTENDED | F5 | teammate_movement_interval_s (s1 - s0) | 62 | 80.401 | 81.7 | 101.878 | 187.325 | 2602.958 | 13217.467 |
| TIER2_2023_2024_EXTENDED | F5 | placebo_signal_age_s | 90 | 741.903 | 1327.102 | 2036.187 | 3938.828 | 5732.525 | 18522.505 |
| TIER2_2023_2024_EXTENDED | F5 | placebo_movement_interval_s | 90 | 81.576 | 99.112 | 101.949 | 123.185 | 163.608 | 426.146 |
| TIER1_2025_SECONDARY | F0 | target_horizon_s (t1 - prediction_time) | 94 | 0 | 0 | 20.99 | 41.644 | 61.174 | 125.894 |
| TIER1_2025_SECONDARY | F0 | target_baseline_interval_s (t1 - t0) | 94 | 80.066 | 81.763 | 83.083 | 103.664 | 2311.473 | 13428.098 |
| TIER1_2025_SECONDARY | F0 | teammate_signal_age_s (prediction_time - s1) | 37 | 232.367 | 549.151 | 2059.416 | 3601.507 | 12077.268 | 15287.955 |
| TIER1_2025_SECONDARY | F0 | teammate_movement_interval_s (s1 - s0) | 37 | 80.566 | 81.839 | 82.287 | 102.368 | 110.613 | 4678.545 |
| TIER1_2025_SECONDARY | F0 | placebo_signal_age_s | 17 | 185.407 | 250.423 | 1384.927 | 2103.999 | 3336.195 | 5404.238 |
| TIER1_2025_SECONDARY | F0 | placebo_movement_interval_s | 17 | 82.212 | 82.245 | 83.36 | 102.76 | 112.295 | 125.13 |
| TIER1_2025_SECONDARY | F3 | target_horizon_s (t1 - prediction_time) | 35 | 0 | 0 | 20.854 | 41.594 | 60.687 | 124.359 |
| TIER1_2025_SECONDARY | F3 | target_baseline_interval_s (t1 - t0) | 35 | 80.904 | 81.647 | 83.492 | 187.355 | 3978.376 | 13428.098 |
| TIER1_2025_SECONDARY | F3 | teammate_signal_age_s (prediction_time - s1) | 37 | 232.367 | 549.151 | 2059.416 | 3601.507 | 12077.268 | 15287.955 |
| TIER1_2025_SECONDARY | F3 | teammate_movement_interval_s (s1 - s0) | 37 | 80.566 | 81.839 | 82.287 | 102.368 | 110.613 | 4678.545 |
| TIER1_2025_SECONDARY | F3 | placebo_signal_age_s | 17 | 185.407 | 250.423 | 1384.927 | 2103.999 | 3336.195 | 5404.238 |
| TIER1_2025_SECONDARY | F3 | placebo_movement_interval_s | 17 | 82.212 | 82.245 | 83.36 | 102.76 | 112.295 | 125.13 |
| TIER1_2025_SECONDARY | F5 | target_horizon_s (t1 - prediction_time) | 3 | 12.088 | 30.221 | 60.442 | 71.093 | 77.484 | 81.744 |
| TIER1_2025_SECONDARY | F5 | target_baseline_interval_s (t1 - t0) | 3 | 210.122 | 372.606 | 643.411 | 666.954 | 681.08 | 690.497 |
| TIER1_2025_SECONDARY | F5 | teammate_signal_age_s (prediction_time - s1) | 3 | 282.021 | 382.195 | 549.151 | 1421.379 | 1944.716 | 2293.607 |
| TIER1_2025_SECONDARY | F5 | teammate_movement_interval_s (s1 - s0) | 3 | 86.389 | 92.696 | 103.209 | 112.464 | 118.018 | 121.72 |
| TIER1_2025_SECONDARY | F5 | placebo_signal_age_s | 4 | 225.575 | 243.595 | 444.987 | 1065.37 | 1837.576 | 2352.38 |
| TIER1_2025_SECONDARY | F5 | placebo_movement_interval_s | 4 | 82.569 | 83.077 | 92.951 | 108.189 | 118.353 | 125.13 |

**Horizon structure:**
- The target horizon (t1 − `prediction_time`) is short by construction: the median F5 value is about 60 s.
- The baseline interval (t1 − t0) is bimodal: adjacent blocks (about 80–100 s) or cross-stint (tens of minutes).
- The teammate signal age has a median of 15–40 min, so teammate movements are often not recent.
