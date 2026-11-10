# V4 Phase 4H — Limitations Report

1. **Source semantics differ by session type.**
   - In practice, Timing71 stints are pit-bounded for most stints (feed pit messages).
   - In qualifying they are not, and only timed laps are recorded (2023–24). 2025 captures add a yellow warm-up lap.
   - The Phase 4E "first lap of stint = out-lap" rule therefore removes a *timed* lap in qualifying. This is recorded, not corrected; Phase 4E and 4F are unchanged.
2. **Qualifying is a different regime.** It has different boost, trim and single-car running. Only *shape* (steadiness) and *relative level* (vs the car's own best) were calibrated; absolute qualifying speed was never used as a cutoff. Whether qualifying steadiness is the right envelope for practice performance laps is an assumption, and it cannot be verified with these data.
3. **The class A rule is narrow by construction.** T_level comes from attempt-to-attempt variation in qualifying (0.002 at the 95th percentile). The pre-specified thresholds were not re-tuned. A looser rule would retain more practice laps, but no source-independent justification for any looser value exists, and choosing one after seeing practice shares would be outcome-driven.
4. **Run purpose, fuel, tyres, setup, tow and traffic are unobserved.** Even class A laps are only "qualifying-like steady windows near the car's own best". They are not verified push laps.
5. **Car-block labels are coarse.** The modal-lap class of a 5-min car-block collapses mixed blocks. The residual C class is heterogeneous, so "matched C = C" is not run-state matching.
6. **2025:**
   - There is no official anchor.
   - The pre-specified 4-lap attempt definition misses the 2025 warm-up + 4 structure, so C2 fails for structural reasons. A post-hoc description is reported, and it does not enter the case.
   - 2025 practice is reported separately. It agrees in direction (A∪B 14.8% of non-D laps).
7. **Capture gaps** make about 13.8% of at-speed 2023–24 laps input-insufficient (no valid 4-lap window).
8. **The qualifying negative control is not identifiable** (single-car structure).
9. **What this does not do:**
   - no hierarchy recomputation;
   - no team effects;
   - no ranking;
   - no tow or traffic claims;
   - no model;
   - no change to Phase 4A–4G;
   - no pooling of 2025 or race.
