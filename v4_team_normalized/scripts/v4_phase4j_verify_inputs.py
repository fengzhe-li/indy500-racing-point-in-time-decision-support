"""V4 Phase 4J pre-result input verification (NO performance D computed). Writes phase4j_freeze_record.csv and phase4j_input_verification.csv."""
import csv, hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4j"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4g_adjacency as G  # noqa: E402
import v4_phase4i_support as S  # noqa: E402

sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()
rows = []
for ph in ["phase4a", "phase4b", "phase4c", "phase4d", "phase4e", "phase4f", "phase4g", "phase4h", "phase4i"]:
    for p in sorted((V4 / "output" / ph).rglob("*")):
        if p.is_file() and p.name != "_audit_cache.pkl":
            rows.append((ph, str(p.relative_to(REPO)), sha(p.relative_to(REPO))))
with open(OUT / "phase4j_freeze_record.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["phase", "path", "sha256"]); w.writerows(rows)
ver = [("branch", git("rev-parse", "--abbrev-ref", "HEAD")), ("commit", git("rev-parse", "--short", "HEAD")), ("frozen_files", len(rows))]
cases = [("phase4f", "case_evaluation.csv", "CASE"), ("phase4g", "phase4g_case_evaluation.csv", "CASE"), ("phase4h", "case_evaluation.csv", "MEASUREMENT_VALIDITY_CASE")]
for ph, f, k in cases:
    ver.append((f"{ph}_case", pd.read_csv(V4 / "output" / ph / f).set_index("criterion").value[k]))
ce = pd.read_csv(V4 / "output/phase4i/case_evaluation.csv")
ver.append(("phase4i_case", ce[ce.criterion == "SUPPORT_CASE"].value.iloc[0]))
# Phase 4I eligibility reproduced in memory (car-blocks + within-block pair universe + same-car pairs); no speed differences
P, L = S.load()
seqs = {sk: G.Seq(g.ts.values) for sk, g in L.groupby("session_key")}
WB = pd.read_csv(V4 / "output/phase4i/within_block_pairs.csv", dtype={"session_key": str})
SC = pd.read_csv(V4 / "output/phase4i/same_car_pairs.csv", dtype={"session_a": str, "session_b": str})
EO = pd.read_csv(V4 / "output/phase4i/eligible_observations.csv", dtype={"session_key": str, "car": str}, low_memory=False)
ok_all = True
for tier, okc in S.TIERS.items():
    E = P[P.cls.isin(okc) & (P.join_status == "MATCHED")].copy()
    cb = S.carblocks(E)
    laps = {k: g.ts.values for k, g in E.groupby(["session_key", "block", "car_id"])}
    wb = S.within_block_pairs(cb, laps, seqs, {})
    sc = S.same_car_pairs(cb)
    a = set(zip(wb.layer, wb.cb_a, wb.cb_b, wb.adjacency_category)); b = set(zip(*[WB[WB.tier == tier][c] for c in ["layer", "cb_a", "cb_b", "adjacency_category"]]))
    c = set(zip(sc.subtype, sc.cb_a, sc.cb_b)); d = set(zip(*[SC[SC.tier == tier][c_] for c_ in ["subtype", "cb_a", "cb_b"]]))
    e_ = len(E) == int((EO.tier == tier).sum())
    ver += [(f"{tier}_eligible_laps_match", e_), (f"{tier}_within_block_pairs_match", a == b), (f"{tier}_same_car_pairs_match", c == d)]
    ok_all &= e_ and a == b and c == d
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
ver.append(("final_v2_v3_hashes_exact", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists())))
out = [x for x in subprocess.run(["git", "diff", "--name-only", "v3-frozen-pre-team-normalization-v4"], cwd=REPO, capture_output=True, text=True).stdout.split() if not x.startswith("v4_team_normalized/")]
ver.append(("paper_and_outside_v4_unchanged", not out))
ver.append(("phase4i_eligibility_reproduced", ok_all))
pd.DataFrame(ver, columns=["item", "value"]).to_csv(OUT / "phase4j_input_verification.csv", index=False)
print(pd.DataFrame(ver, columns=["item", "value"]).to_string())
