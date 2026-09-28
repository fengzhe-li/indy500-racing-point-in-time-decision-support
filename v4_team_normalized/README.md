# V4 — Team-normalised / teammate-controlled evidence layer

An additive extension. The frozen V2/V3 system (same-car core, future-state model, inference engine, regulation-aware extension, validation outputs, paper) is not modified; everything V4 produces lives under this directory.

## Freeze record (Phase 0, 2026-09-28)

| Item | Value |
|---|---|
| Frozen branch | `main` |
| Frozen commit | `a8bb519b586b329f0c61eca8be31c5960abeccf8` |
| Freeze tag | `v3-frozen-pre-team-normalization-v4` (annotated, pushed to origin) |
| Working tree at freeze | clean; `main` was 1 commit ahead of origin (docs-only `a8bb519`) and was pushed |
| V4 branch | `v4-team-normalized-evidence`, created from the freeze tag |
| V4 working copy | sibling clone `indy500-point-in-time-decision-support-v4/` |

## Reproduce

```bash
python3 v4_team_normalized/scripts/v4_parse_entry_lists.py     # needs pdftotext (poppler)
python3 v4_team_normalized/scripts/v4_build_team_registry.py
```

## Layout

- `evidence/entry_lists/`: official INDYCAR/IMS Indianapolis 500 entry-list PDFs, 2018–2025, with layout text
- `manual/v4_team_mapping_rules.csv`: explicit exact-label → canonical-team rules with sources (the only place team identity is decided)
- `scripts/`: parser and registry/audit builder
- `output/`: registry, audit, pair changes, affiliation links, API anomalies, report

See `output/v4_team_normalization_report.md` for findings and the modelling gate.
