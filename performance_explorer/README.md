# Indy 500 Dual-Car Performance Explorer

Independent historical comparison and dual-car V5 simulation replay module. It imports no V5/V6 implementation code and does not modify frozen scientific assets.

```sh
cd performance_explorer/frontend
npm ci
npm test
npm run build
npm run dev
```

The historical UI compares **196 retained complete Day 1 qualifying attempts** from 2020–2024: **46 / 50 / 39 / 30 / 31**. Stable attempt IDs retain records whose chronological attempt number is unknown. Official lap durations drive discrete boundary replay; lap-average speeds are canonical derivations from those times. There is no continuous historical GPS trajectory or section-level spatial advantage.

The isolated V5 adapter consumes published `v5-replay-1` exports and supports common-clock dual-run progression, distance-aligned speed/delta and incremental region advantage. Its separate SIMULATED UI uses real accepted V5 exports, independent A/B selectors and validated local JSON imports. Both cars share one clock and clamp at their own finishes. Linked speed/delta graphs and segment Track Dominance use matched distance coordinates. Input snapshots are read-only; generate parameter changes with V5 and import the resulting JSON. No backend is required. V6 remains disconnected pending a published schema and validated distance coordinate.

- [V5 integration, replay conventions and use](docs/V5_INTEGRATION.md)
- [Historical audit and count reconciliation](docs/DATA_AUDIT.md)
- [Versioned contracts and integration requirements](docs/DATA_CONTRACT.md)
- [Verification results and delivery history](docs/VALIDATION.md)
- [Year-by-year audit](audit/historical_audit.csv)
- [Per-attempt inclusion/exclusion ledger](audit/attempt_selection.csv)

From the repository root:

```sh
python3 performance_explorer/scripts/export_historical.py --check
python3 -m unittest discover -s performance_explorer/tests -v
python3 performance_explorer/scripts/check_integrity.py
```

The integrity check reports three pre-existing V3 Phase 4 source-code hash discrepancies and exits nonzero. Those files are unchanged by Explorer; the detailed report distinguishes them from the matching scientific assets. See the verification report for exact outcomes.
