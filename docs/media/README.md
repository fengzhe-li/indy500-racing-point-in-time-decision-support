# Authentic Application & Simulation Demo Media

This directory contains browser-recorded GIF animations and full-resolution H.264 MP4 recordings captured directly from the repository's verified engineering applications and model exports. Every animation reflects genuine model outputs without fabricated telemetry or synthetic interpolation outside the documented display contracts.

## Media Inventory & Provenance

| File | Format / Dimensions | Size | Label | Source Application & Verified Model Outputs |
|---|---|---:|---|---|
| [`explorer-dual-car.gif`](explorer-dual-car.gif) | GIF (`920×1297`, 51 frames, `loop=0`) | `1,056.7 KB` | `SIMULATED — V5` | [`performance_explorer/`](../../performance_explorer/README.md) (`V5 simulation · SIMULATED` mode) comparing `v5-baseline.json` (`Car A`: `38.9875 s`, `230.844 mph`, $\mu = 1.80$) vs. `v5-low-grip.json` (`Car B`: `40.9635 s`, `219.708 mph`, $\mu = 1.35$, `+1.9760 s`). Shows shared-clock playback, distance-aligned speed profiles, equal-distance arrival delta $t_B(s) - t_A(s)$, segment-level Track Dominance (`Car A: 100.0% / 4023.4 m`), and independent finish clamping (`A ✓` at `38.9875 s` while `B` completes at `40.9635 s`). |
| [`explorer-dual-car.mp4`](explorer-dual-car.mp4) | MP4 H.264 (`1240×1748`, `yuv420p`) | `530.9 KB` | `SIMULATED — V5` | Full-resolution MP4 counterpart to `explorer-dual-car.gif`. |
| [`v6-vehicle-dynamics.gif`](v6-vehicle-dynamics.gif) | GIF (`960×974`, 62 frames, `loop=0`) | `538.4 KB` | `SIMULATED — V6` | [`v6_driver_in_loop/viewer/`](../../v6_driver_in_loop/README.md) sequential replay of (1) `reports/replays/baseline.json` (`COMPLETED`, `72.410 s` lap time on the `4527.95 m` stadium path, max/RMS tracking error `5.187 / 2.769 m`, tyre saturation `4.09%`) and (2) `reports/replays/delay_0.6s.json` (`OFF_TRACK` terminal event at `17.474 s`, `track boundary exceeded`, `-7.500 m` tracking error, `17.40%` tyre saturation). |
| [`v6-vehicle-dynamics.mp4`](v6-vehicle-dynamics.mp4) | MP4 H.264 (`1280×1298`, `yuv420p`) | `295.9 KB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-vehicle-dynamics.gif`. |
| [`v6-baseline-completed.gif`](v6-baseline-completed.gif) | GIF (`960×974`, 37 frames, `loop=0`) | `347.2 KB` | `SIMULATED — V6` | Standalone V6 replay of `v6_driver_in_loop/reports/replays/baseline.json` (`COMPLETED` at `72.410 s`). |
| [`v6-baseline-completed.mp4`](v6-baseline-completed.mp4) | MP4 H.264 (`1280×1298`, `yuv420p`) | `199.3 KB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-baseline-completed.gif`. |
| [`v6-delay-off-track.gif`](v6-delay-off-track.gif) | GIF (`960×974`, 25 frames, `loop=0`) | `249.5 KB` | `SIMULATED — V6` | Standalone V6 replay of `v6_driver_in_loop/reports/replays/delay_0.6s.json` (`OFF_TRACK` terminal event at `17.474 s`). |
| [`v6-delay-off-track.mp4`](v6-delay-off-track.mp4) | MP4 H.264 (`1280×1298`, `yuv420p`) | `155.8 KB` | `SIMULATED — V6` | Full-resolution MP4 counterpart to `v6-delay-off-track.gif`. |
| [`v5-physics-comparison.gif`](v5-physics-comparison.gif) | GIF (`960×1154`, 40 frames, `loop=0`) | `330.8 KB` | `SIMULATED — V5` | [`v5_lap_time_simulation/`](../../v5_lap_time_simulation/README.md) interactive engineering replay (`output/replay.json` vs. `output/replay_low_grip.json`), showing `38.9875 s` (`230.844 mph`) vs. `40.9635 s` (`219.708 mph`), `+1.9760 s` (`+5.068%`) delta, speed-regime envelope, and 8-segment contributions. |
| [`v5-physics-comparison.mp4`](v5-physics-comparison.mp4) | MP4 H.264 (`1280×1538`, `yuv420p`) | `233.7 KB` | `SIMULATED — V5` | Full-resolution MP4 counterpart to `v5-physics-comparison.gif`. |

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
