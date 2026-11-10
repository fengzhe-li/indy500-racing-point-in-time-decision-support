# V4 Phase 4E — Limitations Report

1. **Legacy timing (2018–2021).**
   - Timing71 legacy analysis files carry stint start/end timestamps and lap times, but no per-lap timestamps.
   - Reconstructing lap times from stint boundaries is consistent within 15 s for only about 25% of stints.
   - Per the pre-declared criterion (T: observed lap timestamps on ≥80% of valid laps), every 2018–2021 session is Tier D.
   - Derived timestamps are retained in the lap-level cache, labelled, and excluded from tiering.
2. **2022** has no Timing71 capture. Only session-level official records are machine-readable; lap-level data exist as official PDFs (not ingested).
3. **Secondary timing source.** Timing71 is a third-party capture of the INDYCAR feed. Captures can skip laps: about 10% of consecutive in-stint entries skip ≥1 lap. Four archive files were empty, and two archive entries were mislabelled (other series). Content was verified per file (≥80% of cars in the V4 registry and no other-series keywords).
4. **Weather.**
   - PTSC is 15-minute, so close-time teammates almost always share a reading.
   - Wind units are unverified.
   - Solar/cloud are HRRR Day 1 2020–2024 only.
   - Nothing was imputed.
5. **State confounding.**
   - Practice: run plan, tow/traffic, fuel, tyre age and boost are not observed.
   - Race: plus cautions and strategy.
   - The per-lap flag is observed; traffic is not.
6. **Pseudoreplication.**
   - Lap and pair counts are raw. They are dominated by repeated use of the same car pairs and shared run state. Within-stint lag-1 lap-time autocorrelation is low in practice (≈0.0–0.1) but high in the race (≈0.5) and qualifying runs (≈0.8); see `sampling_dependence_audit.csv`.
   - The effective-information proxies (distinct car-pairs, distinct team × 5-min cells) are orders of magnitude smaller.
7. **Validity filter.** The at-speed plausibility band (37–45 s) and the out/in-lap exclusion are declared data-quality filters. Their counts are reported (`non_at_speed_laps`); they were not tuned.

## Implementation notes (clarifications; no tier rule changed)

1. **Fast Friday name.** The spec's "Fast" qualifying keyword was intended for Fast 9 / 12 / 6 / Six segments. Official names containing "Fast Friday" (2020 "Practice 3 (Fast Friday)") are treated as practice; otherwise an official practice would have been labelled qualifying. This affects 2020 categories only, which are Tier D regardless (legacy timing).
2. **File-to-session dates.** Timing71 files are mapped by the modal local date of their laps; one 2020 capture begins with stale data from an earlier day.
3. **Timing71-only sessions.** Captures absent from the official session list (2023 Practice 1) are kept as separate inventory rows with the provenance criterion failed.
4. **Empty files.** Empty analysis files are labelled `EMPTY_ANALYSIS`, not "excluded content".
5. **Shared qualifying captures.** Where one capture spans several official qualifying segments, totals count its laps once (`lap_data_shared_by_n_official_segments`).
6. **Epoch conversion.** A weather-join timestamp conversion bug (microsecond epochs) was fixed before any tier was interpreted.
