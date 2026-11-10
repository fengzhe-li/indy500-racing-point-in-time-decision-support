# Historical completeness and numerical audit

The corrected Explorer population is **196 retained, complete four-lap Day 1 qualifying attempts**. The previous 168-row export silently lost 28 valid 2024 attempts because `car_attempt_index` was blank. Missing chronological order is not missing lap timing. Records are now selected by stable `attempt_id`, with `attempt: null` and an explicit “Order unknown” label where appropriate. No chronological ordinal is fabricated.

## Population reconciliation

| Year | Canonical / r4p1 source rows | V5 complete timing population | Original Explorer | Corrected retained Explorer | Recovered unknown order | Excluded by retained-result policy |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 63 | 46 | 46 | 46 | 0 | 17 |
| 2021 | 60 | 51 | 50 | 50 | 0 | 10 |
| 2022 | 44 | 40 | 39 | 39 | 0 | 5 |
| 2023 | 85 | 69 | 30 | 30 | 0 | 55 |
| 2024 | 77 | 54 | 3 | 31 | 28 | 46 |
| Total | 329 | 260 | 168 | 196 | 28 | 133 |

The V5 loader's 2020–2023 count is 206 and its 2024 count is 54. These reproduce exactly against the same canonical files. They are **different populations**, not competing estimates of the number of retained results. V5 requires four COMPLETE lap rows and positive finite aggregate time/speed, without filtering result status. The additional complete records are:

| Year | Complete records present in V5 but excluded by Explorer |
|---|---|
| 2020 | None |
| 2021 | 1 WITHDRAWN |
| 2022 | 1 DISALLOWED |
| 2023 | 17 RETIRED, 13 FAILED, 8 VALID_SUPERSEDED, 1 WITHDRAWN |
| 2024 | 9 RETIRED, 9 FAILED, 4 VALID_SUPERSEDED, 1 WITHDRAWN |

For all source rows (including incomplete observations), the exhaustive mutually exclusive exclusions are:

| Year | Exclusion reasons |
|---|---|
| 2020 | UNKNOWN: 17 |
| 2021 | UNKNOWN: 9; WITHDRAWN: 1 |
| 2022 | UNKNOWN: 4; DISALLOWED: 1 |
| 2023 | FAILED: 13; RETIRED: 17; UNKNOWN: 1; VALID_SUPERSEDED: 8; WAVED_OFF: 15; WITHDRAWN: 1 |
| 2024 | FAILED: 9; RETIRED: 9; UNKNOWN: 3; VALID_SUPERSEDED: 4; WAVED_OFF: 20; WITHDRAWN: 1 |

Status exclusions are evaluated first. No additional retained record fails the stricter lap identity, finite-value, or timing consistency checks. The row-level ledger in `audit/attempt_selection.csv` records every source attempt, inclusion in both populations, original Explorer membership, missing order and the first exclusion reason. `audit/historical_audit.csv` and `.json` contain the year summaries.

## Sources, versions and joins

- Original Explorer: derived `r4/output/r4p1_attempt_four_lap_panel_v1.csv`, generated from `data/canonical/v1/attempts.csv` and `attempt_laps.csv` by `r4/build_r4p1_four_lap_panels_v1.py`. It carries lap speeds but omits original lap durations.
- Corrected Explorer: directly joins the canonical V1 attempts and laps; uses `qualifying_events.csv` for year/session semantics, `field_evidence_links.csv` and `evidence_items.csv` for recorded timing provenance, and `sources.csv` for source URIs and hashes. The generator reads these inputs only.
- Official primary results are the 2020–2022 session JSONs and 2023–2024 results PDFs identified by the canonical source catalogue. Section-report evidence also corroborates some lap durations. The export includes source IDs and native locators per attempt and source URIs/hashes at dataset level.
- At inspected V5 commit `81674ea7d27e1a0f7305c215da8b4c049c8fbbfe`, both canonical input files are byte-for-byte identical to this checkout. No newer dataset version explains the discrepancy. Target main `fe65ddf` also leaves these inputs unchanged relative to the Explorer base.
- Canonical and r4p1 have identical sets of 329 attempt IDs; no duplicate attempt IDs, duplicate lap IDs, or orphan lap joins occur. Grouping uses attempt IDs, not entry keys or nullable attempt ordinals.
- All five event IDs are `INDY500_DAY1_YYYY`: qualifying Day 1 only. Race, practice, Fast Six and Last Chance sessions are not included. A new session type requires explicit policy review.
- The original export's IDs and SHA-256 are pinned in `contracts/historical-selection-f15a323.json`. Regeneration proves its selection exactly equals corrected retained rows with a known attempt ordinal, isolating the 28-row loss.

## Inclusion and numerical rules

Retain `VALID_RETAINED` and `A_COMPLETE`; require exactly four uniquely numbered laps 1–4, all COMPLETE; require positive finite lap durations, derived lap speeds and aggregate values. Confirm raw observed timing provenance for each duration and aggregate field. Reject missing values, duplicated laps, invalid numbers and inconsistent totals. Canonical lap numbering is used, not the source report's global lap index. A missing attempt ordinal remains null and has no effect on selection.

Recorded lap durations sum to the official four-lap total to floating-point precision: maximum discrepancy is approximately `2.84e-14 s`. Comparison deltas now use these durations. Canonical lap-average speed is a **rounded deterministic derivation** (`9000 / lap_seconds`), not an independent speed sensor measurement. The official four-lap speed is preserved as a separate recorded result. Rounding tolerances are `0.0005 s` for the sum and `0.001 mph` for speed consistency; no timing values are adjusted to fit those tolerances.

The previous UI inverted rounded speed to approximate duration, used four times the slowest lap as total duration, and moved both map markers with a fixed arbitrary offset. Those errors are removed. Replay now uses one elapsed-time clock, the maximum of the two cumulative durations, and independent discrete boundary markers. No between-boundary trajectory, time delta or GPS position is invented. Both markers remain complete at finish. Seeking to lap N uses the time at which both cars have reached boundary N; the delta uses each car's own time at that boundary.

Positive B − A time means B is behind; negative means B is ahead. Zero is a tie. Cumulative and incremental lap deltas are separate. Historical cross-session comparisons are rejected; unequal lap sequences in the domain helper compare only their shared boundaries. Production export rejects partial four-lap attempts instead of padding them.

Canonical section observations do exist, with different section-set versions and blank spatial timing-point mappings. The current adapter deliberately reports section comparison unavailable; it does not claim those records are absent from the repository or infer corner-level advantages. A future section adapter must validate section-set identity, ordering, coverage and matching boundaries explicitly.

## Reproduce

```sh
python3 performance_explorer/scripts/export_historical.py --check
python3 -m unittest discover -s performance_explorer/tests -v
```

Without `--check`, the generator rewrites only Explorer's export and audit files. It does not modify canonical or frozen data. All rejection reasons are preserved in the audit; broadening the result-status policy would be a separate deliberate change.
