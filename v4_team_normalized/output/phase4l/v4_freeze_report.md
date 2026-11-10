# V4 Freeze Report

**Freeze record:**
- **Manifest:** `v4_final_manifest.csv`, 735 files, 103,277,282 bytes.
- **Manifest SHA-256:** `3a3529eedbf0dc2ac706364eeeb13de7062d0b7e80e05e1607e19808157fef2c` (in `v4_final_manifest.sha256`).
- **Pre-freeze V4 HEAD:** `c74e892`. The final commit is the "V4 final synthesis and freeze" commit that adds this manifest.

**Coverage:**
- **Included:** every file under `v4_team_normalized/` (evidence, manual rules, scripts, Phase 1–4L outputs, figures, README).
- **Excluded:** `__pycache__`, `.DS_Store`, the regenerable `_audit_cache.pkl`, and the four self-referential freeze files (`v4_final_manifest.csv`, `v4_final_manifest.sha256`, `v4_freeze_report.md`, `phase4l_checks_log.txt`).

## By role

| artifact_role | files | bytes |
|---|---|---|
| CHECK_LOG | 12 | 27408 |
| CODE | 44 | 898807 |
| FIGURE | 271 | 27490078 |
| FREEZE_RECORD | 6 | 205018 |
| MANUAL_RULES | 1 | 11175 |
| PRE_REGISTRATION | 10 | 195550 |
| REPORT | 41 | 437672 |
| RESULT_TABLE | 164 | 60922207 |
| SOURCE_EVIDENCE | 178 | 13059185 |
| SYNTHESIS | 8 | 30182 |

## By phase

| phase | files | bytes |
|---|---|---|
| phase1_2 | 26 | 1164314 |
| phase3 | 20 | 1841184 |
| phase4a | 25 | 5904852 |
| phase4b | 154 | 15400142 |
| phase4c | 27 | 1116384 |
| phase4d | 73 | 6759995 |
| phase4e | 203 | 14837456 |
| phase4f | 38 | 7671537 |
| phase4g | 29 | 24561582 |
| phase4h | 28 | 17895787 |
| phase4i | 33 | 4376204 |
| phase4j | 36 | 845657 |
| phase4k | 31 | 804718 |
| phase4l | 11 | 87533 |
| v4 | 1 | 9937 |

## Verification

`scripts/v4_phase4l_checks.py` recomputes every manifest hash. It also verifies:
- case labels and quoted numbers against their sources;
- FINAL_V2/V3 hashes, Phase 4A–4K immutability, and that the paper and original main are unchanged.

The results are in `phase4l_checks_log.txt`.

## Status

**Frozen:**
- V4 is an additive extension. It does not modify FINAL_V2/V3, the 41-transition core, V2 calibration, the V3 PIT architecture, production or scenario inference, the operational curve, or any existing frozen manifest.

**Not done:**
- No merge, no push, paper untouched.
