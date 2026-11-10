# Read-only SIMULATED replay

Serve the repository root: `python3 -m http.server 8766 --bind 127.0.0.1`.
Open `http://127.0.0.1:8766/v6_driver_in_loop/viewer/`. Direct `file://` opening is
unsupported because browser fetch restrictions prevent JSON reads. The server
only needs to serve static files; no simulation API or remote dependency is used.

Select a saved scenario, play/pause, reset to zero, seek any simulated time or
change playback rate. The arrow position and unwrapped heading interpolate between
recorded states; actuator commands and boolean flags hold their left-hand sample.
All charts share the same simulation-time cursor. Reset and selection pause playback.
The run summary is the final outcome even when the cursor is early in the run.
Yellow chart bands indicate an upper actuator limit or tyre-circle clipping; the
cursor panel names active limits. Red marks identify recorded off-track events.

The seek slider accepts arbitrary precision so an off-grid terminal event is
reachable. Playback clamps to the exact last recorded time. An initial off-track
state produces a valid single-row, zero-duration replay and no running animation.
Browser frame time and playback multiplier affect display only; they do not change
physics, telemetry or reported lap duration.

## Export contract

`reports/index.json` lists runs. Each referenced schema-2 JSON has SIMULATED label,
name, SI metadata, metrics, events, explicit `fields` and aligned `rows`. The
exporter selects **existing** samples approximately every 50 ms, retaining all
flag transitions (and their preceding samples), first and final samples. No
synthetic state is stored. The full baseline CSV and in-memory simulation retain
the original control grid plus terminal event; metrics use the full data, not the
reduced display rows. Non-flag peaks between display samples can be absent from
traces; max values in the summary remain full-resolution metrics.

`viewer/replay.mjs` validates finite numeric fields, booleans, increasing timestamps,
schema, track geometry, terminal time and event intervals. It implements binary
search interpolation and clamped playback time. Browser tests use **actual generated
run files**. Invalid/missing data produces an error with regeneration instructions.

## Verification

Automated: `node --test v6_driver_in_loop/viewer/replay.test.mjs` checks all 19
exports, interpolation/held inputs, time clamping/rate, nonfinite/incompatible data,
zero duration and terminal events. Python checks exports against original samples.

Browser smoke (2026-11-10): page loaded all 19 runs; Play advanced time/vehicle;
Pause froze replay; seek to 30 s updated baseline speed to ~60.01 m/s and tracking
error to −3.544 m; 2× was selectable; reset restored zero; selecting 600 ms delay
showed off-track at 17.473820515275 s; End seek showed the final −7.500 m error
and OFF TRACK terminal flag. This is UI verification, not human driving validation.
