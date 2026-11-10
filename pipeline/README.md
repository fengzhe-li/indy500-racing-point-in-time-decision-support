# v1 pipeline

Run from the repository root, in a Python 3 environment with `requirements.txt` installed:

```bash
PYTHONPATH=. python3 -m pipeline.run_pipeline
PYTHONPATH=. python3 -m unittest -v
```

The stages are separated into source registration, source-specific parsing, canonical reconciliation, provenance, validation, target-specific eligibility, materialization, and QA reporting. Raw files under `evidence/` are read-only inputs. Canonical outputs are deterministic UTF-8 CSV files under `data/canonical/v1/`; QA exports are at the repository root.

Phase 3.5A adds `chronology_constraints.csv` at canonical grain and the root-level `2024_chronology_constraints.csv`, `2024_inter_attempt_gap_diagnostics.csv`, and `2024_chronology_reconciliation_report.md`. The constraint table keeps recorder capture, editorial anchor, and timed-run endpoint semantics separate. Empty inter-attempt-gap output means no pair met the required boundary evidence; it is never a queue-wait estimate.

Parquet is not emitted because the frozen Python runtime has no Parquet engine. CSV schemas and enums are frozen in `v1_data_dictionary.csv`; all datetimes are explicit UTC `Z` strings and local session dates retain an IANA timezone field.

Phase 4A reads the frozen `weather/output/hrrr_ims_2020_2024_features.csv` extract. It creates one canonical snapshot per HRRR cycle, lead, and IMS grid point and 17 numeric values beneath each snapshot. Raw-source and deterministic-derived values remain distinct in field provenance. Public availability is null with `UNKNOWN` quality and `POLICY_REQUIRED` extraction status, so these snapshots cannot yet join to decision-time state. `decision_state_features.csv` remains schema-only because Phase 4A performs no weather alignment, feature engineering, or modelling.
