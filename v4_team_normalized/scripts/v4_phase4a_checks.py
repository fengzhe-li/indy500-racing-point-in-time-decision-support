"""Independent consistency checks for V4 Phase 4A outputs. Exits non-zero on any failure."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
P4 = REPO / "v4_team_normalized" / "output" / "phase4a"
res = []


def check(name, ok, detail=""):
    res.append((name, bool(ok), detail))


anch = pd.read_csv(P4 / "frozen_transition_anchors.csv", dtype={"target_car": str})
cand = pd.read_csv(P4 / "frozen_transition_teammate_candidates.csv", dtype={"teammate_car": str, "target_car": str}, low_memory=False)
ctrl = pd.read_csv(P4 / "all_matched_controls.csv", dtype={"window_min": str, "target_car": str, "cars_t1": str, "cars_t2": str}, low_memory=False)
j = pd.read_csv(REPO / "v4_team_normalized/output/phase3/team_attempt_join.csv", dtype={"registry_car_number": str, "car_number": str}, low_memory=False)
frozen = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv", dtype={"car_number": str})
core = frozen.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).reset_index(drop=True)

# anchors preserve frozen values exactly
check("anchors: 41 rows, same ids and order", list(anch.transition_id) == list(core.transition_id))
for a_col, f_col in [("speed_t1", "before_four_lap_average_speed_mph"), ("speed_t2", "after_four_lap_average_speed_mph"),
                     ("observed_delta_speed", "delta_four_lap_average_speed_mph"), ("track_temp_t1", "previous_track_temp_c"),
                     ("track_temp_t2", "next_track_temp_c"), ("ambient_temp_t1", "previous_air_temp_c"), ("ambient_temp_t2", "next_air_temp_c")]:
    check(f"anchors: {a_col} == frozen {f_col}", np.array_equal(anch[a_col].values, core[f_col].values))
lo = pd.read_csv(REPO / "r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv")
check("anchors: LOYO residual carried unchanged", np.array_equal(anch.frozen_loyo_residual_raw_mph.values, lo.residual_loyo_raw.values))
ft = pd.to_datetime(core.before_time_utc, utc=True, format="mixed")
check("anchors: frozen t1 used wherever frozen t1 exists",
      (pd.to_datetime(anch.t1, utc=True)[ft.notna()].values == ft[ft.notna()].values).all())

# candidate eligibility rules
prim = {(y, c): (t, p) for y, c, t, p in zip(j.year, j.registry_car_number, j.canonical_engineering_team, j.primary_teammate_layer)}
check("cand: never the target entry", (cand.teammate_car != cand.target_car).all())
check("cand: same year x canonical team as target",
      all(prim[(y, c)][0] == t for y, c, t in zip(cand.year, cand.teammate_car, cand.canonical_engineering_team)))
check("cand: teammates all in primary layer (no technical partnerships)",
      all(bool(prim[(y, c)][1]) for y, c in zip(cand.year, cand.teammate_car)))
check("cand: technical-partnership target has no candidates", not cand.transition_id.isin(anch[~anch.target_team_in_primary_layer].transition_id).any())
off = (pd.to_datetime(cand.teammate_timestamp, utc=True, format="mixed") - pd.to_datetime(cand.endpoint_time_utc, utc=True, format="mixed")).dt.total_seconds() / 60
check("cand: signed offset = teammate - endpoint", np.allclose(off.dropna(), cand.signed_offset_min.dropna()))
check("cand: PIT availability == offset <= 0", (cand.pit_available == (cand.signed_offset_min <= 0)).all())

# controls
b = ctrl[ctrl.supported_both]
check("ctrl: delta_team_control = t2 - t1", np.allclose(b.delta_team_control, b.team_control_t2 - b.team_control_t1))
check("ctrl: team_adjusted = delta_target - delta_team_control", np.allclose(b.team_adjusted_delta, b.delta_target - b.delta_team_control))
check("ctrl: delta_target equals frozen delta", np.allclose(b.delta_target, b.transition_id.map(anch.set_index("transition_id").observed_delta_speed)))
c = cand[cand.eligible_control]
ok = True
for r in ctrl[(ctrl.direction == "PRIOR")].itertuples(index=False):
    for tag in ("t1", "t2"):
        att = getattr(r, f"attempts_{tag}")
        if isinstance(att, str):
            ep = "T1" if tag == "t1" else "T2"
            used = c[(c.transition_id == r.transition_id) & (c.endpoint == ep) & c.teammate_attempt.isin(att.split("|"))]
            if (used.signed_offset_min > 0).any():
                ok = False
check("PIT: prior-only controls never use a future teammate attempt", ok)
ok = True
for r in ctrl[ctrl.direction == "FUTURE"].itertuples(index=False):
    for tag in ("t1", "t2"):
        att = getattr(r, f"attempts_{tag}")
        if isinstance(att, str):
            used = c[(c.transition_id == r.transition_id) & (c.endpoint == tag.upper()) & c.teammate_attempt.isin(att.split("|"))]
            if (used.signed_offset_min <= 0).any():
                ok = False
check("future-only controls never use a prior attempt", ok)
w = ctrl[(ctrl.window_min != "UNBOUNDED") & ctrl.supported_both]
check("ctrl: used attempts lie inside the window",
      ((w[["max_abs_offset_t1", "max_abs_offset_t2"]].max(axis=1) <= w.window_min.astype(float) + 1e-9)).all())
nb = ctrl[(ctrl.strategy == "CAR_BALANCED_COMMON_CARS") & ctrl.supported_both]
check("common-cars: same teammate car set at both endpoints", (nb.cars_t1 == nb.cars_t2).all())
# car-balanced recomputation for one window
ok = True
cb = ctrl[(ctrl.strategy == "CAR_BALANCED_MEAN") & (ctrl.window_min == "60") & (ctrl.direction == "ANY") & ctrl.supported_t1]
for r in cb.itertuples(index=False):
    u = c[(c.transition_id == r.transition_id) & (c.endpoint == "T1") & (c.abs_offset_min <= 60)]
    if not np.isclose(u.groupby("teammate_car").teammate_speed.mean().mean(), r.team_control_t1):
        ok = False
check("car-balanced: recomputed mean-of-car-means matches (±60, T1)", ok)
sup = pd.read_csv(P4 / "endpoint_support_by_window.csv", dtype={"window_min": str})
s = sup[(sup.scope == "ALL")]
check("support: both <= min(T1, T2)", (s.support_both <= s[["support_t1", "support_t2"]].min(axis=1)).all())
ok = all((g.sort_values("window_min", key=lambda x: x.astype(int)).support_both.diff().dropna() >= 0).all() for _, g in s.groupby("direction"))
check("support: non-decreasing with window", ok)

# frozen artefacts and repository untouched
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
bad = [f["path"] for f in man["files"] if f.get("exists") and hashlib.sha256((REPO / f["path"]).read_bytes()).hexdigest() != f["sha256"]]
check("frozen: every R5.2 manifest file hash matches", not bad, ";".join(bad))
diff = subprocess.run(["git", "diff", "--name-only", "v3-frozen-pre-team-normalization-v4"], cwd=REPO, capture_output=True, text=True).stdout.split()
untr = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, text=True).stdout.split()
outside = [p for p in diff + untr if not p.startswith("v4_team_normalized/")]
check("git: nothing outside v4_team_normalized/ changed vs freeze tag", not outside, ";".join(outside[:5]))

wd = max(len(n) for n, _, _ in res)
for n, ok, d in res:
    print(f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}")
print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(P4 / "phase4a_checks_log.txt").write_text("\n".join(f"{'PASS' if o else 'FAIL'}  {n}  {d}" for n, o, d in res) + "\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
