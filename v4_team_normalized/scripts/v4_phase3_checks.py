"""Independent consistency checks for V4 Phase 3 outputs. Exits non-zero on any failure."""
import hashlib
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
P3 = REPO / "v4_team_normalized" / "output" / "phase3"
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


j = pd.read_csv(P3 / "team_attempt_join.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
c = pd.read_csv(P3 / "teammate_attempt_candidates.csv", dtype={"car_A": str, "car_B": str}, low_memory=False)
n = pd.read_csv(P3 / "nearest_teammate_candidates.csv", dtype={"car_number": str, "teammate_car": str}, low_memory=False)
for col in ["timestamp_A", "timestamp_B"]:
    c[col] = pd.to_datetime(c[col], utc=True, format="mixed")
j["attempt_timestamp_utc"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")

# ---- join
src_core = pd.read_csv(REPO / "r4/output/r4p1_attempt_four_lap_panel_v1.csv")
src_r6 = pd.read_csv(REPO / "r6_regime_extension/output/regime_attempt_inventory_v3/regime_official_attempt_inventory_v3.csv")
check("join: attempt_id unique", j.attempt_id.is_unique)
check("join: all 329 core attempts present", set(src_core.attempt_id) == set(j[j.tier == "CORE_2020_2024"].attempt_id))
check("join: all R6 2018/2019/2025 attempts present", len(j[j.tier == "REGIME_EXT_R6"]) == int(src_r6.year.isin([2018, 2019, 2025]).sum()))
check("join: no unmapped or ambiguous", set(j.map_status) == {"MAPPED"})
check("join: speeds copied unchanged (core)",
      np.allclose(j[j.tier == "CORE_2020_2024"].set_index("attempt_id").four_lap_average_speed_mph.reindex(src_core.attempt_id).values,
                  src_core.four_lap_average_speed_mph.values, equal_nan=True))

# ---- candidates
check("cand: never same entry", (c.car_A != c.car_B).all())
check("cand: never same driver", (c.driver_A != c.driver_B).all())
check("cand: delta_time >= 0 when timed", (c.delta_time_minutes.dropna() >= 0).all())
dt = (c.timestamp_B - c.timestamp_A).dt.total_seconds() / 60
check("cand: delta_time = t_B - t_A", np.allclose(dt.dropna(), c.delta_time_minutes.dropna()))
check("cand: delta_speed = B - A", np.allclose((c.speed_B - c.speed_A).dropna(), c.delta_speed_mph.dropna()))
check("cand: delta_track = B - A", np.allclose((c.track_B - c.track_A).dropna(), c.delta_track_temp_c.dropna()))
prim = j[j.primary_teammate_layer == True]
key = {a: (y, t) for a, y, t in zip(prim.attempt_id, prim.year, prim.canonical_engineering_team)}
check("cand: both attempts in primary layer", c.attempt_A.isin(key).all() and c.attempt_B.isin(key).all())
check("cand: A and B same year x team", all(key[a] == key[b] for a, b in zip(c.attempt_A, c.attempt_B)))
nonprim = set(j[(j.primary_teammate_layer != True)].attempt_id)
check("cand: technical-partnership attempts excluded", not (set(c.attempt_A) | set(c.attempt_B)) & nonprim)
expected = 0
for _, g in prim.groupby(["tier", "year", "canonical_engineering_team"]):
    sizes = g.groupby("registry_car_number").size().values
    expected += sum(a * b for a, b in itertools.combinations(sizes, 2))
check("cand: count = sum over car pairs of n_a*n_b", expected == len(c), f"{expected} vs {len(c)}")
check("cand: no duplicate attempt pairs", not c.duplicated(subset=["attempt_A", "attempt_B"]).any()
      and not pd.Series([frozenset(p) for p in zip(c.attempt_A, c.attempt_B)]).duplicated().any())
check("cand: measurable = complete & timed", (c.measurable_candidate == (c.both_complete_four_lap & c.both_timed)).all())

# ---- nearest
check("near: teammate car differs", (n.car_number != n.teammate_car).all())
ok = True
for r in n.itertuples(index=False):
    h = j[(j.year == r.year) & (j.registry_car_number == r.teammate_car) & j.complete_four_lap & j.attempt_timestamp_utc.notna()
          & (j.canonical_engineering_team == r.canonical_engineering_team)]
    t0 = j.loc[j.attempt_id == r.attempt_id, "attempt_timestamp_utc"].iloc[0]
    if abs(((h.attempt_timestamp_utc - t0).dt.total_seconds() / 60).abs().min() - r.abs_time_separation_min) > 1e-9:
        ok = False
        break
check("near: recorded separation is the true minimum", ok)
check("near: exactly one overall-nearest per attempt", (n.groupby("attempt_id").is_overall_nearest_teammate.sum() == 1).all())

# ---- windows monotone
w = pd.read_csv(P3 / "comparability_window_counts.csv")
check("windows: counts non-decreasing", all((g.sort_values("max_time_separation_min").attempt_pair_candidates.diff().dropna() >= 0).all()
                                           for _, g in w.groupby("scope")))

# ---- frozen core untouched and environment basis reproduced
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
bad = [f["path"] for f in man["files"] if f.get("exists") and hashlib.sha256((REPO / f["path"]).read_bytes()).hexdigest() != f["sha256"]]
check("frozen: every R5.2 manifest file hash matches", not bad, ";".join(bad))
r = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv")
core = r.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"])
check("frozen: 41 transitions", len(core) == 41)
ep = pd.concat([core[["before_attempt_id", "previous_track_temp_c", "previous_air_temp_c"]].set_axis(["id", "t", "a"], axis=1),
                core[["after_attempt_id", "next_track_temp_c", "next_air_temp_c"]].set_axis(["id", "t", "a"], axis=1)]).drop_duplicates("id")
jj = j.set_index("attempt_id")
mt = ep.assign(jt=ep.id.map(jj.track_temp_c), ja=ep.id.map(jj.ambient_temp_c))
check("frozen: join track temp equals core input for every endpoint", np.allclose(mt.t, mt.jt), f"{int((~np.isclose(mt.t, mt.jt)).sum())} differ")
check("frozen: join ambient temp equals core input for every endpoint", np.allclose(mt.a, mt.ja), f"{int((~np.isclose(mt.a, mt.ja)).sum())} differ")
diff = subprocess.run(["git", "diff", "--name-only", "v3-frozen-pre-team-normalization-v4"], cwd=REPO, capture_output=True, text=True).stdout.split()
untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, text=True).stdout.split()
outside = [p for p in diff + untracked if not p.startswith("v4_team_normalized/")]
check("git: nothing outside v4_team_normalized/ changed vs freeze tag", not outside, ";".join(outside[:5]))

w_ = max(len(x[0]) for x in results)
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(w_)}  {detail}")
print(f"\n{sum(ok for _, ok, _ in results)}/{len(results)} checks passed")
(P3 / "phase3_checks_log.txt").write_text("\n".join(f"{'PASS' if ok else 'FAIL'}  {n_}  {d}" for n_, ok, d in results) + "\n")
sys.exit(0 if all(ok for _, ok, _ in results) else 1)
