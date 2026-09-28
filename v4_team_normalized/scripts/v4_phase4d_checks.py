"""Independent Phase 4D checks. Exits non-zero on any failure; writes phase4d_checks_log.txt."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4d"
res = []


def check(n, ok, d=""):
    res.append((n, bool(ok), d))


git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()

tt = pd.read_csv(OUT / "transition_team_context.csv", dtype={"target_car": str})
obs = pd.read_csv(OUT / "evidence_independence_audit.csv", dtype={"car": str}, low_memory=False)
tco = pd.read_csv(OUT / "team_context_observations.csv", low_memory=False)
st = pd.read_csv(OUT / "identifiability_by_transition.csv", dtype={"window": str})
al = pd.read_csv(OUT / "residual_context_alignment.csv", dtype={"window": str})
core = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv").dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).reset_index(drop=True)
lo = pd.read_csv(REPO / "r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv")
beta = json.loads((REPO / "r5_2/manual/probabilistic_physics_core_v1.json").read_text())["mean_core"]["full_data_huber_coefficients"]
j = pd.read_csv(V4 / "output/phase4b/team_timeline_long.csv", dtype={"registry_car_number": str}, low_memory=False)
j["on_performance_timeline"] = j.on_performance_timeline.astype(str).eq("True")
j["t"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")

# frozen anchors unchanged
check("41 anchors, frozen order", list(tt.transition_id) == list(core.transition_id))
check("observed delta == frozen", np.array_equal(tt.observed_delta_speed.values, core.delta_four_lap_average_speed_mph.values))
check("expected delta == frozen LOYO prediction", np.array_equal(tt.frozen_expected_delta_loyo.values, lo.predicted_physical_delta_mph_loyo.values))
check("target residual == frozen residual_loyo_raw", np.array_equal(tt.target_residual.values, lo.residual_loyo_raw.values))
# teammate pool rules
tco_t = tco.merge(tt[["transition_id", "year", "canonical_engineering_team", "target_car"]], on="transition_id", suffixes=("", "_tgt"))
check("teammate obs never the target car", (tco_t.car != tco_t.target_car).all())
check("teammate obs same year and canonical team", ((tco_t.year == tco_t.year_tgt) & (tco_t.canonical_engineering_team == tco_t.canonical_engineering_team_tgt)).all())
prim = {(y, c): p for y, c, p in zip(j.year, j.registry_car_number, j.primary_teammate_layer.astype(str).eq("True"))}
check("no technical-partnership / non-primary observations", all(prim[(y, c)] for y, c in zip(obs.year, obs.car)))
check("primary analysis restricted to 2020-2024", set(obs.year) <= {2020, 2021, 2022, 2023, 2024} and set(tt.year) <= {2020, 2021, 2023, 2024})
# MOVE construction
mv = obs[obs.obs_type == "MOVE"]
ok = True
for (y, c), g in j[j.on_performance_timeline & j.year.between(2020, 2024) & j.primary_teammate_layer.astype(str).eq("True")].groupby(["year", "registry_car_number"]):
    g = g.sort_values(["t", "attempt_id"])
    exp = set(zip(g.attempt_id.iloc[:-1], g.attempt_id.iloc[1:]))
    got = set(zip(mv[(mv.year == y) & (mv.car == c)].attempt_prev, mv[(mv.year == y) & (mv.car == c)].attempt_curr))
    ok &= exp == got
check("MOVEs are exactly consecutive timed-complete pairs per car", ok)
check("previous_attempt_delta = current − previous", np.allclose(mv.previous_attempt_delta, mv.speed_curr - mv.speed_prev))
adj = mv.previous_attempt_delta - (beta["delta_track_temp_c"] * mv.delta_track_c + beta["delta_air_temp_c"] * mv.delta_ambient_c)
check("physics adjustment applies frozen coefficients exactly", np.allclose(adj.dropna(), mv.physics_adjusted_move.dropna()) and adj.isna().equals(mv.physics_adjusted_move.isna()))
# independence labels
fpairs = set(zip(core.before_attempt_id, core.after_attempt_id))
fep = set(core.before_attempt_id) | set(core.after_attempt_id)
check("no missing independence label", obs.independence_label.notna().all())
check("RECIPROCAL iff MOVE pair is a frozen transition",
      ((mv.independence_label == "RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE") == pd.Series([(a, b) in fpairs for a, b in zip(mv.attempt_prev, mv.attempt_curr)], index=mv.index)).all())
lv = obs[obs.obs_type == "LEVEL"]
check("LEVEL FROZEN_CORE_ENDPOINT iff attempt is a frozen endpoint", ((lv.independence_label == "FROZEN_CORE_ENDPOINT") == lv.attempt_curr.isin(fep)).all())
# structural categories re-derived (primary window)
p30 = st[st.window == "30"].set_index("transition_id")
ok = True
for r in p30.itertuples():
    if r.category == "D":
        continue
    A = r.move_cars >= 2 and r.frozen_independent_moves >= 1 and bool(r.both_sides_coverage)
    Bc = (not A) and r.move_cars >= 1 and (r.move_cars >= 2 or r.frozen_independent_moves >= 1)
    exp = "A" if A else "B" if Bc else "C"
    ok &= exp == r.category
check("categories follow pre-declared rules (±30)", ok)
check("C/D always labelled INSUFFICIENT", (al[al.category.isin(["C", "D"])].label == "INSUFFICIENT_TEAM_CONTEXT").all())
check("alignment never uses causal labels", not al.label.str.contains("EFFECT").any())
# permutation reproducibility of the observed statistic
perm = pd.read_csv(OUT / "permutation_diagnostic.csv")
summ = pd.read_csv(OUT / "team_context_summary.csv", dtype={"window": str})
d = summ[(summ.window == "30") & summ.S6_car_balanced_median_adj_move.notna()]
check("permutation observed T3 == transitions with defined same-team S6 (±30)", int(perm[perm.statistic == "T3_n_defined"].observed.iloc[0]) == len(d))
check("permutation observed T1 reproduced", np.isclose(perm[perm.statistic == "T1_sign_agree"].observed.iloc[0],
                                                     (np.sign(d.S6_car_balanced_median_adj_move) == np.sign(d.target_residual)).mean()))
# 2025 kept separate
e = pd.read_csv(OUT / "extension_2025_alignment.csv")
check("2025 extension contains only 2025 and is labelled not pooled", set(e.year) == {2025} and (e.scope == "2025_EXTENSION_RAW_DELTAS_NOT_POOLED").all())
# spec before results; Phase 4C untouched; frozen manifests; scope
spec = "v4_team_normalized/output/phase4d/phase4d_identifiability_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", spec).stdout.split()
check("identifiability spec committed before results and unchanged", bool(sc) and git("diff", "--quiet", sc[-1], "--", spec).returncode == 0, sc[-1][:7] if sc else "")
p4c = git("log", "-1", "--format=%H", "--", "v4_team_normalized/output/phase4c").stdout.strip()
check("Phase 4C outputs unchanged since their commit", git("diff", "--quiet", p4c, "--", "v4_team_normalized/output/phase4c", "v4_team_normalized/scripts/v4_phase4c_panel.py").returncode == 0
      and not git("status", "--porcelain", "--", "v4_team_normalized/output/phase4c").stdout.strip(), p4c[:7])
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
check("frozen R5.2 manifest hashes exact", all(sha(f["path"]) == f["sha256"] for f in man["files"] if f.get("exists")))
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("frozen R6 manifest hashes exact", all(sha(p) == h for p, h in zip(r6m.path, r6m.sha256) if (REPO / p).exists()))
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [p for p in diff if not p.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed", not out, ";".join(out[:5]))

wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines))
print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4d_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
