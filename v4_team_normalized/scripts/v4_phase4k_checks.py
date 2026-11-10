"""Required Phase 4K checks (4K.23). Exits non-zero on failure; writes phase4k_checks_log.txt."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4k"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4i_support as S  # noqa: E402
import v4_phase4k_feasibility as K  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
EV = pd.read_csv(OUT / "target_prediction_events.csv", dtype={"session_key": str})
TS = pd.read_csv(OUT / "teammate_signal_support.csv", dtype={"session_key": str})
PS = pd.read_csv(OUT / "placebo_signal_support.csv", dtype={"session_key": str})
P, L = S.load()
P["car"] = P.car.astype(str)
mach = K.pit_machinery(P)
Xc, W, T, lapwin, steady, pos = mach
m = P[K.KEY + ["cls"]].merge(Xc[K.KEY + ["cls"]], on=K.KEY, suffixes=("", "_re"))
check("Phase 4H class-A eligibility reproduced exactly (re-run frozen classifier)", len(m) == len(P) and (m.cls == m.cls_re).all())
h4 = pd.read_csv(V4 / "output/phase4h/case_evaluation.csv").set_index("criterion").value
check("Phase 4H thresholds unchanged", all(abs(T[k] - float(h4[k])) < 1e-15 for k in ["T_steady_95", "T_steady_100", "T_level_95", "T_level_100"]))
fr = pd.read_csv(OUT / "phase4k_freeze_record.csv")
ok = lambda ph: all(sha(p) == h for p, h in zip(fr[fr.phase == ph].path, fr[fr.phase == ph].sha256))
check("Phase 4I populations unchanged (hashes)", ok("phase4i"))
check("Phase 4J unchanged (hashes; CASE B)", ok("phase4j") and pd.read_csv(V4 / "output/phase4j/case_evaluation.csv").set_index("criterion").value["PRIMARY_CASE"] == "B")
pr = EV[EV.population == "PRIMARY_TIER1_2023_2024"]
att = pd.read_csv(OUT / "event_attrition.csv")
r25 = pd.read_csv(OUT / "replication_2025_feasibility.csv")
check("primary years 2023-2024 only; 2025 separate (own population/file; sessions all 2025)", set(EV.population) == {"PRIMARY_TIER1_2023_2024"} and set(pr.year) <= {2023, 2024}
      and set(P[P.session_key.isin(K.POPS["TIER1_2025_SECONDARY"][1])].year) == {2025} and "2025 SECONDARY" in " ".join(r25.value.astype(str))
      and not set(K.POPS["TIER1_2025_SECONDARY"][1]) & set(K.POPS["PRIMARY_TIER1_2023_2024"][1]))
check("race excluded; no 2018-2022 classifier projection", set(EV.year) <= {2023, 2024, 2025} and "RACE" not in set(EV.category))
check("t0 < t1 (blocks and timestamps)", (EV.t0_block < EV.t1_block).all() and (EV.t0_avail_ts < EV.t1_first_ts).all() and (EV.t0_source_ts < EV.t1_source_ts).all())
sig = TS.merge(EV[EV.cutoff == "PRIMARY"][["event_id", "t1_first_ts", "t1_source_ts"]], on="event_id")
check("s0 < s1", (TS.s0_source_ts < TS.s1_source_ts).all())
check("s1 availability < prediction_time <= t1 first eligible lap <= t1 observation time (strict information cutoff)",
      (sig.s1_avail_ts < sig.prediction_time).all() and (sig.prediction_time <= sig.t1_first_ts).all() and (sig.t1_first_ts <= sig.t1_source_ts).all()
      and (EV[EV.cutoff == "PRIMARY"].prediction_time == EV[EV.cutoff == "PRIMARY"].t1_first_ts).all())
check("no tied/unordered observation treated as safely prior (strict < on feed-update timestamps; placebo too)",
      (TS.avail_before_cutoff).all() and (PS.q_avail_before_cutoff).all() and "within_update_order" not in open(V4 / "scripts/v4_phase4k_feasibility.py").read())
regd = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
tm = {f"{y}|{c}": t for y, c, t in zip(regd.year, regd.car_number, regd.canonical_engineering_team)}
tpc = {f"{y}|{c}" for y, c, r in zip(regd.year, regd.car_number, regd.relationship_type) if r == "TECHNICAL_PARTNERSHIP"}
check("teammate differs from target; same canonical team", (TS.teammate_car != TS.target_car).all() and all(tm[a] == tm[b] for a, b in zip(TS.target_car, TS.teammate_car)))
check("placebo canonical team differs", all(tm[a] != tm[b] for a, b in zip(PS.target_car, PS.placebo_car)) and all(tm[b] == t for b, t in zip(PS.placebo_car, PS.placebo_team)))
pe = P.drop_duplicates("car_id").set_index("car_id")
cars = list(set(TS.teammate_car) | set(TS.target_car))
check("technical partnerships excluded from teammate relationships", not set(TS.teammate_car) & tpc and pe.loc[cars].primary_layer.astype(bool).all()
      and not pe.loc[cars].technical_partnership_only.fillna(False).astype(bool).any())
src = open(V4 / "scripts/v4_phase4k_feasibility.py").read()
body = src[src.index("def enumerate_pop"):src.index("def qtab")]
check("no future target speed used in event selection (no v / dv in enumeration logic beyond the recorded median)",
      not re.search(r"\.v\b|\bdv\b|delta_v|speed_mph\)", body.replace('v=("speed_mph", "median")', "")) and not {"dv", "delta_v_target", "D_mph"} & set(EV.columns))
allsrc = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4k_*.py") if not p.name.endswith("_checks.py"))
check("no prediction error computed; no lambda fitted; no predictor ranked",
      not re.search(r"\bmae\b|\brmse\b|lambda_|\.fit\(|lstsq|statsmodels|\.corr\(|argmin|\.rank\(", allsrc, re.I)
      and not any(k in c.lower() for f in OUT.glob("*.csv") for c in pd.read_csv(f, nrows=1).columns for k in ["mae", "rmse", "error", "lambda", "rank"]))
wx = K.ptsc()
wts = wx.ts_s.values
pp = EV[EV.cutoff == "PRIMARY"]
okr = all((r < 0) or (wts[r] <= t and t - wts[r] <= K.PTSC_MAX_AGE) for r, t in zip(pp.t0_reading, pp.t0_source_ts)) and all((r < 0) or (wts[r] <= t and t - wts[r] <= K.PTSC_MAX_AGE) for r, t in zip(pp.t1_reading, pp.t1_source_ts))
check("no missing physical input imputed (readings are observed PTSC at/before time, age <= 15 min; F1 requires both)", okr and (pp.F1 == ((pp.t0_reading >= 0) & (pp.t1_reading >= 0))).all())
cbt = P[P.cls.isin(S.TIERS["TIER1_STRICT"]) & (P.join_status == "MATCHED")].groupby(P.session_key + "|" + P.block.astype(str) + "|" + P.car_id).ts.agg(["min", "max"])
q = pr[pr.cutoff == "PRIMARY"]
check("no raw timestamp altered (t1 first / t0 availability equal raw eligible-lap timestamps)",
      np.allclose(cbt.loc[q.t1_cb]["min"].values, q.t1_first_ts.values) and np.allclose(cbt.loc[q.t0_cb]["max"].values, q.t0_avail_ts.values))
check("one canonical event per future target outcome (per population and cutoff)", not EV.duplicated(["population", "cutoff", "t1_cb"]).any())
# PIT confirmation re-verification for F5 events (t0 and all laps)
f5 = pr[(pr.cutoff == "PRIMARY") & pr.F5]
okc = True
E1 = P[P.cls.isin(S.TIERS["TIER1_STRICT"]) & (P.join_status == "MATCHED")].copy()
E1["xpos"] = pos.reindex(pd.MultiIndex.from_frame(E1[K.KEY])).values
E1["cb_id"] = E1.session_key + "|" + E1.block.astype(str) + "|" + E1.car_id
for r in f5.itertuples(index=False):
    laps = E1[E1.cb_id == r.t0_cb]
    okc &= all(K.lap_confirmed(int(p), r.prediction_time, c, W, T, lapwin, steady) for p, c in zip(laps.xpos, laps.cls))
nf4 = pr[(pr.cutoff == "PRIMARY") & pr.F4 & ~pr.F5]
check("point-in-time label confirmation reproduces (F5 t0 confirmed; conservative-cutoff F5 empty)", okc and len(f5) == int(pr[pr.cutoff == 'PRIMARY'].F5.sum())
      and EV[EV.cutoff == "CONSERVATIVE"].F5.sum() == 0)
check("nested populations monotone F0>=...>=F5", all((EV[f"F{i}"] >= EV[f"F{i+1}"]).all() for i in range(5)))
fr_ok = len(fr) == 451 and all(sha(p) == h for p, h in zip(fr.path, fr.sha256))
fr_ok &= all(git("diff", "--quiet", "04c39f8", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-j]_*.py"))
check("no Phase 4A-4J output/script changed (451 hashes; scripts vs 04c39f8)", fr_ok)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp_) == h for pp_, h in zip(r6m.path, r6m.sha256) if (REPO / pp_).exists()))
sp = "v4_team_normalized/output/phase4k/phase4k_prediction_feasibility_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", sp).stdout.split()
check("spec committed before counts (dae6856) and unchanged", bool(sc) and sc[-1].startswith("dae6856") and git("diff", "--quiet", sc[-1], "--", sp).returncode == 0
      and sorted(git("ls-tree", "--name-only", sc[-1], "v4_team_normalized/output/phase4k/").stdout.split()) == sorted([sp, "v4_team_normalized/output/phase4k/phase4k_freeze_record.csv"]))
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("paper unchanged; nothing outside V4 changed", not out, ";".join(out[:5]))
req = ["phase4k_prediction_feasibility_spec.md", "target_prediction_events.csv", "physical_input_support.csv", "teammate_signal_support.csv", "placebo_signal_support.csv",
       "fully_comparable_events.csv", "event_attrition.csv", "event_overlap_dependence.csv", "horizon_structure.csv", "session_team_coverage.csv", "model_free_support.csv",
       "tier2_feasibility.csv", "replication_2025_feasibility.csv", "case_evaluation.csv", "phase4k_prediction_feasibility_report.md", "phase4k_chronology_leakage_report.md",
       "phase4k_dependence_report.md", "phase4k_limitations_report.md"]
check("all required outputs and >=8 figures present", all((OUT / f).exists() for f in req) and len(list((OUT / "figures").glob("*.png"))) >= 8)
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok_ else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok_, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4k_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
