# Indy 500 Dual-Car Performance Explorer

Independent comparison UI with two modes: official historical timing and **SIMULATED V5 dual-car performance**. It imports no V5/V6 implementation code and does not modify frozen scientific assets.

```sh
cd performance_explorer/frontend
npm ci
npm test
npm run build
npm run dev
```

Choose **V5 simulation · SIMULATED** to compare the actual published baseline and low-grip exports, import V5 JSON, or recompute two independent configurations through the existing V5 API. Shared-clock playback, independent finish clamping, speed overlays, equal-distance arrival delta, segment-time dominance, linked hover/seek and numerical engineering insights are available. Bundled exports work offline. They are assumed-model simulations, not official results or calibrated individual-car predictions.

## Connect the V5 API

Until PR #2 is merged, run the service in a separate checkout pinned to its published commit. Do not merge V5 into this feature branch:

```sh
# From the repository root; choose an unused worktree path.
git fetch origin pull/2/head:refs/remotes/origin/published-v5
git worktree add --detach /tmp/indy500-explorer-v5-service 8879c3095cd11215a0d444e5973bc7a37b36342b
cd /tmp/indy500-explorer-v5-service
python3 -m venv /tmp/indy500-explorer-v5-venv
/tmp/indy500-explorer-v5-venv/bin/pip install -r v5_lap_time_simulation/requirements.txt
/tmp/indy500-explorer-v5-venv/bin/python -m uvicorn v5_lap_time_simulation.server:app --host 127.0.0.1 --port 8007
```

Then, in the Explorer frontend:

```sh
V5_API_TARGET=http://127.0.0.1:8007 npm run dev
# Or: V5_API_TARGET=http://127.0.0.1:8007 npx vite preview
```

The default proxy target is `http://127.0.0.1:8005`. Production hosting must route same-origin `/api/v5/baseline` and `/api/v5/simulate` to a compatible V5 service; the static build does not include or start Python. The client never implements a solver. API errors retain the last validated run, and each car independently cancels/ignores superseded responses. Requests time out after 30 seconds. Applied output snapshots are distinct from editable drafts. Unexposed parameters use the service's baseline.

## Evidence and boundaries

Historical mode preserves **196 retained complete Day 1 qualifying attempts**, 2020–2024: **46 / 50 / 39 / 30 / 31**. Official durations drive discrete lap-boundary replay. Unknown chronological attempt numbers remain unknown; no GPS, continuous trajectory or unmatched section advantages are invented.

The **V6 schema-2 adapter** consumes actual published dynamic exports, preserves optional signal availability, interpolates actual pose and holds commands/flags. It validates terminal events and supports V6-vs-V6 common-clock comparison, with distance deltas restricted to common strictly advancing reference-progress coverage. V6 UI is not connected in this version. Its 4527.95 m stadium is never aligned to the V5 4023.36 m oval.

- [Historical audit](docs/DATA_AUDIT.md)
- [Contracts, numerical semantics and integration requirements](docs/DATA_CONTRACT.md)
- [Verification and browser results](docs/VALIDATION.md)
- [Year-by-year audit](audit/historical_audit.csv)
- [Per-attempt inclusion/exclusion ledger](audit/attempt_selection.csv)

```sh
python3 performance_explorer/scripts/export_historical.py --check
python3 -m unittest discover -s performance_explorer/tests -v
python3 performance_explorer/scripts/check_integrity.py
```

The strict integrity check exits **1** for three inherited V3 Phase 4 source-code hash discrepancies. The report preserves their expected and actual hashes and confirms the files remain unchanged. Scientific asset manifests and pinned exports are checked separately.
