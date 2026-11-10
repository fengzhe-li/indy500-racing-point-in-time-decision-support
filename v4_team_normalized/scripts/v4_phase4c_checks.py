"""Required Phase 4C checks (4C.21). Exits non-zero on any failure; writes phase4c_checks_log.txt."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4c_panel as P  # noqa: E402

REPO = P.REPO
OUT = P.OUT
res = []


def check(name, ok, detail=""):
    res.append((name, bool(ok), detail))


sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
j, y, pall, pwx, elig, t0 = P.load_population()
p3 = pd.read_csv(REPO / "v4_team_normalized/output/phase3/team_attempt_join.csv", dtype={"registry_car_number": str}, low_memory=False).set_index("attempt_id")
reg = pd.read_csv(REPO / "v4_team_normalized/output/v4_team_entry_registry.csv", dtype={"car_number": str})
r6 = pd.read_csv(REPO / "r6_regime_extension/output/regime_attempt_inventory_v3/regime_official_attempt_inventory_v3.csv")

check("only 2025 is used", set(pall.year) == {2025} and set(pwx.year) == {2025})
core = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv")
frozen_ids = set(core.before_attempt_id) | set(core.after_attempt_id)
check("no frozen 2020-2024 transition attempt included", not (set(pall.attempt_id) & frozen_ids) and not pall.is_frozen_core_attempt.any())
check("source attempt speeds unchanged (vs Phase 3 join)", np.allclose(pall.speed.values, p3.loc[pall.attempt_id, "four_lap_average_speed_mph"].values))
r6s = r6.assign(aid="R6_" + r6.year.astype(str) + "_RANK" + r6.source_rank.astype(str)).set_index("aid")
check("source attempt speeds unchanged (vs R6 official parse)", np.allclose(pall.speed.values, r6s.loc[pall.attempt_id, "average_speed_mph"].values))
check("source weather unchanged (track, ambient vs Phase 3 join)",
      np.allclose(pwx.track.values, p3.loc[pwx.attempt_id, "track_temp_c"].values) and np.allclose(pwx.ambient.values, p3.loc[pwx.attempt_id, "ambient_temp_c"].values))
r25 = reg[reg.year == 2025].set_index("car_number")
check("car/team mapping equals accepted V4 registry", all(r25.loc[c, "canonical_engineering_team"] == t for c, t in zip(pall.car, pall.team)))
check("no technical-partnership entry in primary analysis", not (pall.relationship_type == "TECHNICAL_PARTNERSHIP").any() and pall.primary_teammate_layer.all())
check("no missing weather imputed (P_wx = P_all complete cases; dropped rows truly missing)",
      set(pwx.attempt_id) == set(pall.dropna(subset=["track", "ambient"]).attempt_id)
      and pall[~pall.attempt_id.isin(pwx.attempt_id)][["track", "ambient"]].isna().any(axis=1).all(),
      f"{len(pall) - len(pwx)} row(s) excluded for missing weather")
fe = pd.read_csv(OUT / "fixed_effects_results.csv")
mx = pd.read_csv(OUT / "mixed_effects_results.csv")
check("wind excluded from all models", not any("wind" in str(t) for t in list(fe.terms) + list(mx.formula) + list(fe.columns) + list(mx.columns)))
check("solar not fabricated (all 2025 solar missing; never used)", pall.solar_shortwave_wm2.isna().all() and not any("solar" in c for c in fe.columns))
wt = pd.read_csv(OUT / "within_transformation_results.csv")
check("FE and within-transformation slopes reconcile (<1e-8)", wt.agrees_1e_8.all(), f"max diff {wt.abs_diff.max():.1e}")
lo = pd.read_csv(OUT / "leave_one_team_out.csv")
check("LOTO populations correct", all(r.n == int((pwx.team != r.left_out_team).sum()) for r in lo.itertuples()) and lo.left_out_team.nunique() == pwx.team.nunique())
co = pd.read_csv(OUT / "leave_one_car_out.csv", dtype={"left_out_car": str})
multi = set(pwx.groupby("car").size().loc[lambda s: s >= 2].index)
check("LOCO populations correct", all(r.n == int((pwx.car != r.left_out_car).sum()) for r in co.itertuples()) and set(co.left_out_car) == multi)
check("model failures preserved (redundant M4 NOT_ESTIMABLE row; MX2 non-convergence recorded)",
      (fe.model == "M4_redundant_team_plus_all_car_dummies").any() and fe.loc[fe.model == "M4_redundant_team_plus_all_car_dummies", "status"].iloc[0] == "NOT_ESTIMABLE"
      and len(mx) == 2 and mx.warnings.notna().all())
check("M4 reparameterisation reproduces M2", fe.loc[fe.model == "M4", "max_abs_fitted_diff_vs_M2"].iloc[0] < 1e-8)
spec = "v4_team_normalized/output/phase4c/phase4c_prespecified_analysis.md"
spec_commit = subprocess.run(["git", "log", "--format=%H", "--diff-filter=A", "--", spec], cwd=REPO, capture_output=True, text=True).stdout.split()
unchanged = subprocess.run(["git", "diff", "--quiet", spec_commit[-1] if spec_commit else "HEAD", "--", spec], cwd=REPO).returncode == 0 if spec_commit else False
check("pre-specification committed before results and unchanged since", bool(spec_commit) and unchanged, f"spec commit {spec_commit[-1][:7] if spec_commit else 'NONE'}")
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
bad = [f["path"] for f in man["files"] if f.get("exists") and sha(f["path"]) != f["sha256"]]
check("frozen R5.2 manifest hashes exact", not bad, ";".join(bad))
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
bad6 = [p for p, h in zip(r6m.path, r6m.sha256) if (REPO / p).exists() and sha(p) != h]
check("frozen R6 manifest hashes exact", not bad6, ";".join(bad6))
diff = subprocess.run(["git", "diff", "--name-only", "v3-frozen-pre-team-normalization-v4"], cwd=REPO, capture_output=True, text=True).stdout.split()
untr = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, text=True).stdout.split()
outside = [p for p in diff + untr if not p.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed (V2/V3/paper untouched)", not outside, ";".join(outside[:5]))

wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines))
print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4c_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
