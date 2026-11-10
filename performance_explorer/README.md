# Indy 500 Dual-Car Performance Explorer

Standalone historical comparison and lap-boundary replay module. It is independent of the V3 frontend and does not import unfinished V5/V6 code.

## Run locally

```sh
cd performance_explorer/frontend
npm install
npm test
npm run build
npm run dev
```

## Scope

The first version compares canonical retained four-lap qualifying attempts from 2020–2024. It supports year/session/driver/attempt selection, observed official average-speed comparison, explicitly converted lap durations, synchronized schematic lap progression, playback controls, cumulative time delta and evidence availability. Historical data has no GPS/continuous position or matched section timing; track dominance is therefore unavailable in historical mode.

Read [the data contract](docs/DATA_CONTRACT.md) for the V1 series schema and V5/V6 adapter requirements. The current 2024 extract contains only three complete attempts; the selector displays per-year attempt coverage.
