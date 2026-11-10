# Authentic Application & Simulation Demo Media

This directory contains browser-recorded GIF animations and full-resolution H.264 MP4 recordings captured directly from the repository's verified engineering applications and model exports. Every animation reflects genuine model outputs without fabricated telemetry or synthetic interpolation outside the documented display contracts.

## Media Inventory & Provenance

| File | Format / Dimensions | Size | Label | Source Application & Verified Model Outputs |
|---|---|---:|---|---|
| [`explorer-dual-car.gif`](explorer-dual-car.gif) | GIF (`920×1297`, 51 frames, `loop=0`) | `1,056.7 KiB` | `SIMULATED — V5` | [`performance_explorer/`](../../performance_explorer/README.md) (`V5 simulation · SIMULATED` mode) comparing `v5-baseline.json` (`Car A`: `38.9875 s`, `230.844 mph`, $\mu = 1.80$) vs. `v5-low-grip.json` (`Car B`: `40.9635 s`, `219.708 mph`, $\mu = 1.35$, `+1.9760 s`). Shows shared-clock playback, distance-aligned speed profiles, equal-distance arrival delta $t_B(s) - t_A(s)$, segment-level Track Dominance (`Car A: 100.0% / 4023.4 m`), and independent finish clamping (`A ✓` at `38.9875 s` while `B` completes at `40.9635 s`). |
| [`explorer-dual-car.mp4`](explorer-dual-car.mp4) | MP4 H.264 (`1240×1748`, `yuv420p`) | `530.9 KiB` | `SIMULATED — V5` | Full-resolution MP4 counterpart to `explorer-dual-car.gif`. |
| [`v6-vehicle-dynamics.gif`](v6-vehicle-dynamics.gif) | GIF (`960×974`, 62 frames, `loop=0`) | `538.4 KiB` | `SIMULATED — V6` | [`v6_driver_in_loop/viewer/`](../../v6_driver_in_loop/README.md) sequential replay of (1) `reports/replays/baseline.json` (`COMPLETED`, `72.410 s` lap time on the `4527.95 m` stadium path, max/RMS tracking error `5.187 / 2.769 m`, tyre saturation `4.09%`) and (2) `reports/replays/delay_0.6s.json` (`OFF_TRACK` terminal event at `17.474 s`, `track boundary exceeded`, `-7.500 m` tracking error, `17.40%` tyre saturation). |
| [`v6-vehicle-dynamics.mp4`](v6-vehicle-dynamics.mp4) | MP4 H.264 (`1360×1380`, `yuv420p`) | `295.9 KiB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-vehicle-dynamics.gif`. |
| [`v6-baseline-completed.gif`](v6-baseline-completed.gif) | GIF (`960×974`, 37 frames, `loop=0`) | `347.2 KiB` | `SIMULATED — V6` | Standalone V6 replay of `v6_driver_in_loop/reports/replays/baseline.json` (`COMPLETED` at `72.410 s`). |
| [`v6-baseline-completed.mp4`](v6-baseline-completed.mp4) | MP4 H.264 (`1360×1380`, `yuv420p`) | `199.3 KiB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-baseline-completed.gif`. |
| [`v6-delay-off-track.gif`](v6-delay-off-track.gif) | GIF (`960×974`, 25 frames, `loop=0`) | `249.5 KiB` | `SIMULATED — V6` | Standalone V6 replay of `v6_driver_in_loop/reports/replays/delay_0.6s.json` (`OFF_TRACK` terminal event at `17.474 s`). |
| [`v6-delay-off-track.mp4`](v6-delay-off-track.mp4) | MP4 H.264 (`1360×1380`, `yuv420p`) | `155.8 KiB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-delay-off-track.gif`. |
| [`v5-physics-comparison.gif`](v5-physics-comparison.gif) | GIF (`960×1154`, 40 frames, `loop=0`) | `330.8 KiB` | `SIMULATED — V5` | [`v5_lap_time_simulation/`](../../v5_lap_time_simulation/README.md) interactive engineering replay (`output/replay.json` vs. `output/replay_low_grip.json`), showing `38.9875 s` (`230.844 mph`) vs. `40.9635 s` (`219.708 mph`), `+1.9760 s` (`+5.068%`) delta, speed-regime envelope, and 8-segment contributions. |
| [`v5-physics-comparison.mp4`](v5-physics-comparison.mp4) | MP4 H.264 (`1360×1634`, `yuv420p`) | `233.7 KiB` | `SIMULATED — V5` | Full-resolution MP4 counterpart to `v5-physics-comparison.gif`. |

## Reproducing the Browser Sessions Locally

1. **Dual-Car Performance Explorer (`SIMULATED — V5`):**
   ```bash
   cd performance_explorer/frontend
   npm ci
   npm run dev -- --host 127.0.0.1 --port 5180
   # Open http://127.0.0.1:5180 and select "V5 simulation · SIMULATED"
   ```
2. **V5 Engineering Replay (`SIMULATED — V5`):**
   ```bash
   python3 -m pip install -r v5_lap_time_simulation/requirements.txt
   npm ci --prefix v5_lap_time_simulation/frontend
   npm run build --prefix v5_lap_time_simulation/frontend
   python3 -m v5_lap_time_simulation.server
   # Open http://127.0.0.1:8005
   ```
3. **V6 Vehicle Dynamics & Virtual Driver Replay (`SIMULATED — V6`):**
   ```bash
   python3 -m http.server 8766 --bind 127.0.0.1
   # Open http://127.0.0.1:8766/v6_driver_in_loop/viewer/
   # Select "baseline · completed" or "delay_0.6s · off_track"
   ```

## Integrated Performance Explorer V1.1 — accepted V6 interface

This additional recording is **not** the standalone V6 viewer shown in `v6-vehicle-dynamics.*`. It was captured on 2026-11-10 after PR #8 was accepted, from the production React application under `performance_explorer/frontend/`.

- Accepted main merge: `80344d9581c0bb464036085a141503bdc09358d2`; accepted source head: `66b0dd4e6c8380343008b95f9a6591dcd7378376`.
- Input files: `performance_explorer/frontend/public/v6-replays/baseline.json` and `delay_0.6s.json`, matching the published schema-2 V6 exports. No telemetry or model parameters were edited for the recording.
- Capture: real Chromium browser, 1280×1700 viewport; Playwright records the browser video while operating visible controls. Sequence: select V6, play at 2× through the off-track event, pause, restart, then play at 10× through baseline completion. No fabricated frames, retimed simulation data or extrapolation.
- Verified terminal telemetry: baseline `72.40999667048455 s`; delay run `17.473820515275 s`. No browser page errors were observed.
- [`explorer-v6-integrated.mp4`](explorer-v6-integrated.mp4): H.264, 1280×1700, 25 fps, approximately 26.1 s, 2,192,173 bytes; `yuv420p`, fast-start metadata, no audio.
- [`explorer-v6-integrated.gif`](explorer-v6-integrated.gif): 920×1222, 104 frames at 4 fps, 26.0 s, 6,766,941 bytes, infinite loop. The GIF is a reduced-resolution/sample-rate encoding of the same real browser capture; the MP4 retains the full capture frame rate.

To open the accepted interface from the repository root:

```sh
npm ci --prefix performance_explorer/frontend
npm run build --prefix performance_explorer/frontend
cd performance_explorer/frontend
npx vite preview --host 127.0.0.1 --port 5183
# Open http://127.0.0.1:5183 and select "V6 interactive replay · SIMULATED".
```

Existing media files in this directory are retained byte-for-byte. Repeated README embeds reference these same files; they do not introduce duplicate assets.
