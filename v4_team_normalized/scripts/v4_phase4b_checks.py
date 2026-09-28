"""Independent consistency checks for V4 Phase 4B outputs. Exits non-zero on any failure."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
P4 = REPO / "v4_team_normalized" / "output" / "phase4b"
res = []


def check(name, ok, detail=""):
    res.append((name, bool(ok), detail))


j = pd.read_csv(P4 / "team_timeline_long.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
for b in ["on_performance_timeline", "centering_informative", "is_frozen_core_attempt", "complete_four_lap", "on_timeline"]:
    j[b] = j[b].astype(str).eq("True")
j["attempt_timestamp_utc"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")
p3 = pd.read_csv(REPO / "v4_team_normalized/output/phase3/team_attempt_join.csv", dtype={"car_number": str}, low_memory=False)
prim = p3[(p3.primary_teammate_layer == True) & p3.year.between(2018, 2025)]

check("long: exactly the Phase 3 primary-layer attempts 2018-2025", set(j.attempt_id) == set(prim.attempt_id) and j.attempt_id.is_unique)
src = prim.set_index("attempt_id")
check("long: raw speed preserved", np.allclose(j.set_index("attempt_id").four_lap_average_speed_mph.reindex(src.index), src.four_lap_average_speed_mph, equal_nan=True))
check("long: track temp preserved", np.allclose(j.set_index("attempt_id").track_temp_c.reindex(src.index), src.track_temp_c, equal_nan=True))
check("long: eras never mixed within a year", j.groupby("year").era.nunique().max() == 1)
check("long: performance timeline = timed & complete", (j.on_performance_timeline == (j.attempt_timestamp_utc.notna() & j.complete_four_lap)).all())
ok = True
for _, g in j[j.on_timeline].groupby(["year", "canonical_engineering_team"]):
    g = g.sort_values("team_timeline_order")
    if not g.attempt_timestamp_utc.is_monotonic_increasing:
        ok = False
check("long: team_timeline_order is chronological", ok)
pt = j[j.on_performance_timeline]
check("centering: within-car mean of speed_minus_car_mean == 0", (pt.groupby(["year", "registry_car_number"]).speed_minus_car_mean.mean().abs() < 1e-9).all())
check("centering: raw = centered + car mean", np.allclose(pt.four_lap_average_speed_mph, pt.speed_minus_car_mean + pt.car_mean_timeline))
check("centering: undefined off the performance timeline", j[~j.on_performance_timeline].speed_minus_car_mean.isna().all())
check("centering: single-attempt cars flagged uninformative", (pt[pt.car_n_timeline == 1].centering_informative == False).all())

cons = pd.read_csv(P4 / "consecutive_team_observations.csv")
exp = sum(max(len(g) - 1, 0) for _, g in pt.groupby(["year", "canonical_engineering_team"]))
check("consecutive: count = sum(n-1) per team-year", len(cons) == exp, f"{len(cons)} vs {exp}")
check("consecutive: delta_time >= 0", (cons.delta_time_min >= 0).all())
ty = {a: (y, t) for a, y, t in zip(j.attempt_id, j.year, j.canonical_engineering_team)}
check("consecutive: pairs never cross team-years", all(ty[a] == ty[b] == (y, t) for a, b, y, t in
                                                       zip(cons.attempt_prev, cons.attempt_next, cons.year, cons.canonical_engineering_team)))
check("consecutive: SAME_CAR label correct", ((cons.car_prev == cons.car_next) == (cons.pair_type == "SAME_CAR")).all())

samp = pd.read_csv(P4 / "team_timeline_sampling_summary.csv")
check("sampling: same + switch = n-1", ((samp.consecutive_same_car + samp.consecutive_car_switch) == (samp.attempts_on_performance_timeline - 1).clip(lower=0)).all())
check("sampling: team-year count", len(samp) == j[["year", "canonical_engineering_team"]].drop_duplicates().shape[0])
conf = pd.read_csv(P4 / "car_time_confounding_audit.csv")
check("confounding: eta2 in [0,1]", conf.eta2_time_explained_by_car.dropna().between(-1e-9, 1 + 1e-9).all())
fz = pd.read_csv(P4 / "frozen_core_timeline_context.csv")
check("frozen: 41 transitions represented", len(fz) == 41)
fr = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv").dropna(
    subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"])
fr_ids = set(fr.before_attempt_id) | set(fr.after_attempt_id)
check("frozen: flagged attempts == frozen endpoints present in the primary layer",
      set(j[j.is_frozen_core_attempt].attempt_id) == fr_ids & set(j.attempt_id),
      f"{int(j.is_frozen_core_attempt.sum())} flagged; {len(fr_ids - set(j.attempt_id))} endpoints outside layer (technical partnership)")
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
bad = [f["path"] for f in man["files"] if f.get("exists") and hashlib.sha256((REPO / f["path"]).read_bytes()).hexdigest() != f["sha256"]]
check("frozen: every R5.2 manifest file hash matches", not bad, ";".join(bad))
figs = list((P4 / "figures" / "raw_timelines").glob("*.png"))
check("figures: raw and centered timeline per eligible team-year",
      len(figs) == len(list((P4 / "figures" / "centered_timelines").glob("*.png"))) == int((samp.attempts_on_performance_timeline >= 2).sum()))
check("figures: 7 cross-team summaries", len(list((P4 / "figures").glob("summary*.png"))) == 7)
diff = subprocess.run(["git", "diff", "--name-only", "v3-frozen-pre-team-normalization-v4"], cwd=REPO, capture_output=True, text=True).stdout.split()
untr = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=REPO, capture_output=True, text=True).stdout.split()
outside = [p for p in diff + untr if not p.startswith("v4_team_normalized/")]
check("git: nothing outside v4_team_normalized/ changed vs freeze tag", not outside, ";".join(outside[:5]))

wd = max(len(n) for n, _, _ in res)
for n, ok, d in res:
    print(f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}")
print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(P4 / "phase4b_checks_log.txt").write_text("\n".join(f"{'PASS' if o else 'FAIL'}  {n}  {d}" for n, o, d in res) + "\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
