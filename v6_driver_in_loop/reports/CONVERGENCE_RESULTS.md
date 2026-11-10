# SIMULATED timestep refinement

Baseline, conservative and boundary-sensitive aggressive drivers; fixed external control/record steps of 20, 10, 5, 2.5 ms. Deterministic internal substeps bound low-speed stiffness. Finest run is a numerical reference, not ground truth. Compare same-time states on the shared [0, min(end times)] interval at 0.1 s plus endpoint using linear interpolation. RMS position difference is over this comparison grid; tracking RMS in the CSV is time-weighted.

| name | dt_s | status | lap_time_s | max_path_error_m | rms_path_error_m | max_lateral_accel_m_s2 | max_yaw_rate_rad_s | position_max_difference_m | position_rms_difference_m | velocity_max_difference_m_s | cpu_time_s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.02 | completed | 72.4132 | 5.19559 | 2.76943 | 12.849 | 0.211099 | 0.406319 | 0.202227 | 0.160926 | 0.18098 |
| baseline | 0.01 | completed | 72.41 | 5.18681 | 2.76899 | 12.8275 | 0.210641 | 0.201859 | 0.117387 | 0.103726 | 0.356852 |
| baseline | 0.005 | completed | 72.4077 | 5.18452 | 2.76897 | 12.8219 | 0.210466 | 0.057314 | 0.0293881 | 0.0174316 | 0.712478 |
| baseline | 0.0025 | completed | 72.4068 | 5.18225 | 2.76887 | 12.8164 | 0.210351 | 0 | 0 | 0 | 1.44492 |
| conservative | 0.02 | completed | 90.3735 | 3.13415 | 1.82281 | 7.93986 | 0.159273 | 0.0961234 | 0.0660127 | 0.0376982 | 0.222978 |
| conservative | 0.01 | completed | 90.3739 | 3.12874 | 1.82252 | 7.92556 | 0.158961 | 0.0776609 | 0.048733 | 0.0344886 | 0.449007 |
| conservative | 0.005 | completed | 90.3751 | 3.12601 | 1.82233 | 7.91839 | 0.158806 | 0.0200211 | 0.011733 | 0.0133324 | 1.00674 |
| conservative | 0.0025 | completed | 90.3754 | 3.12494 | 1.82228 | 7.91553 | 0.158737 | 0 | 0 | 0 | 1.87645 |
| aggressive | 0.02 | completed | 63.2272 | 7.4944 | 3.69365 | 18.0932 | 0.257976 | 0.615767 | 0.398229 | 0.176224 | 0.157478 |
| aggressive | 0.01 | completed | 63.2211 | 7.48895 | 3.69339 | 18.0807 | 0.25753 | 0.216696 | 0.131308 | 0.0843737 | 0.319678 |
| aggressive | 0.005 | completed | 63.2202 | 7.47351 | 3.69261 | 18.0458 | 0.257054 | 0.119171 | 0.0650522 | 0.0289926 | 0.640666 |
| aggressive | 0.0025 | completed | 63.2185 | 7.47205 | 3.69254 | 18.0424 | 0.256942 | 0 | 0 | 0 | 1.41466 |

See convergence.csv for all actuator/tyre saturation fractions, heading/yaw differences and wall time. The study refines both sampled control and dynamics, so RK4 order cannot be inferred from these laps. Curvature steps, PID derivative response, clipping and event localization are nonsmooth. Timing is a single local process measurement, excludes exports and is not a real-time guarantee.
