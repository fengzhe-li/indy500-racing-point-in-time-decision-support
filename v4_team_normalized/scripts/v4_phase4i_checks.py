"""Required Phase 4I checks (4I.17). Exits non-zero on failure; writes phase4i_checks_log.txt."""
import hashlib, itertools, json, re, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4i"
P4H = V4 / "output" / "phase4h"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402
import v4_phase4h_audit as H  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
EO = pd.read_csv(OUT / "eligible_observations.csv", dtype={"session_key": str, "car": str}, low_memory=False)
WB = pd.read_csv(OUT / "within_block_pairs.csv", dtype={"session_key": str}, low_memory=False)
SC = pd.read_csv(OUT / "same_car_pairs.csv", dtype={"session_a": str, "session_b": str}, low_memory=False)
CE = pd.read_csv(OUT / "case_evaluation.csv")
PI = pd.read_csv(P4H / "practice_lap_inventory.csv", dtype={"session_key": str, "car": str}, low_memory=False)
KEY = ["session_key", "source_id", "car", "stint", "lap_in_stint"]

# 1 Phase 4H classes reproduced exactly (re-run frozen classifier)
pop = F.population()
qk = list(H.QUAL)
reg, sessions, off, L = F.laps_for(set(PI.session_key) | set(qk))
Lp = L[L.session_key.isin(set(PI.session_key))].merge(pop[["session_key", "role", "normalized_category"]], on="session_key").rename(columns={"normalized_category": "category"})
Lq = L[L.session_key.isin(qk)].merge(pop[["session_key", "role", "normalized_category"]], on="session_key").rename(columns={"normalized_category": "category"})
X = H.inventory(Lp, H.pit_matching(Lp))
Qa, _, _ = H.qualifying_attempts(H.inventory(Lq, H.pit_matching(Lq)))
T = H.thresholds(Qa)
c1, _ = H.classify(X, T)
X["car"] = X.car.astype(str)
c1["car"] = c1.car.astype(str)
m = EO[KEY + ["cls", "tier"]].merge(c1[KEY + ["cls"]], on=KEY, suffixes=("", "_re"), how="left")
m2 = PI[KEY + ["cls"]].merge(c1[KEY + ["cls"]], on=KEY, suffixes=("", "_re"))
check("Phase 4H classifications reproduced exactly (re-run frozen classifier)", (m.cls == m.cls_re).all() and len(m2) == len(PI) and (m2.cls == m2.cls_re).all())
h4 = pd.read_csv(P4H / "case_evaluation.csv").set_index("criterion").value
check("no Phase 4H threshold changed (recomputed == frozen; Phase 4H scripts unchanged)",
      all(abs(T[k] - float(h4[k])) < 1e-15 for k in ["T_steady_95", "T_steady_100", "T_level_95", "T_level_100"])
      and all(git("diff", "--quiet", "fd266ea", "--", f"v4_team_normalized/scripts/{f}").returncode == 0 for f in ["v4_phase4h_audit.py", "v4_phase4h_reports.py", "v4_phase4h_checks.py"]))
A, B = "A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE"
check("no C/D/E observation enters Tier 1 or Tier 2", EO.cls.isin([A, B]).all())
check("Tier 1 contains A-A only (laps A; pair car-blocks A_ONLY)", (EO[EO.tier == "TIER1_STRICT"].cls == A).all()
      and WB[WB.tier == "TIER1_STRICT"][["comp_a", "comp_b"]].isin(["A_ONLY"]).all().all() and SC[SC.tier == "TIER1_STRICT"][["comp_first", "comp_second"]].isin(["A_ONLY"]).all().all())
check("Tier 2 contains A/B observations only", EO[EO.tier == "TIER2_EXTENDED"].cls.isin([A, B]).all()
      and set(WB[WB.tier == "TIER2_EXTENDED"][["comp_a", "comp_b"]].stack()) <= {"A_ONLY", "B_ONLY", "MIXED_AB"})
cb_car = lambda s: s.str.split("|").str[-2] + "|" + s.str.split("|").str[-1]
check("same-car identity exact", (SC.car == cb_car(SC.cb_a)).all() and (SC.car == cb_car(SC.cb_b)).all() and (SC.cb_a != SC.cb_b).all())
regd = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
tm = {f"{y}|{c}": t for y, c, t in zip(regd.year, regd.car_number, regd.canonical_engineering_team)}
st = WB[WB.layer == "SAME_TEAM"]
check("same-team mapping matches frozen canonical registry", all(tm[a] == ta == tb == tm[b] for a, b, ta, tb in zip(st.car_a, st.car_b, st.team_a, st.team_b)) and (st.car_a != st.car_b).all())
tpc = {f"{y}|{c}" for y, c, r in zip(regd.year, regd.car_number, regd.relationship_type) if r == "TECHNICAL_PARTNERSHIP"}
elig = EO.drop_duplicates("car_id").set_index("car_id")
check("technical partnerships / non-primary-layer excluded from same-team layer",
      not (set(st.car_a) | set(st.car_b)) & tpc and elig.loc[list(set(st.car_a) | set(st.car_b))].primary_layer.astype(bool).all()
      and not elig.loc[list(set(st.car_a) | set(st.car_b))].technical_partnership_only.fillna(False).astype(bool).any())
dt = WB[WB.layer == "DIFF_TEAM"]
check("different-team pairs truly cross canonical teams", (dt.team_a != dt.team_b).all() and all(tm[a] != tm[b] for a, b in zip(dt.car_a, dt.car_b)))
# 10 no nearest-time control selected: every cross-team pair of eligible car-blocks in each block is present
okn = True
for tier, g in EO.groupby("tier"):
    cbs = g.groupby(["session_key", "block", "car_id"]).canonical_engineering_team.first().reset_index()
    exp = 0
    for (s, b), h in cbs.groupby(["session_key", "block"]):
        exp += sum(1 for i, j in itertools.combinations(h.canonical_engineering_team.values, 2) if i != j)
    okn &= exp == int((WB[(WB.tier == tier)].layer == "DIFF_TEAM").sum())
src = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4i_*.py") if not p.name.endswith("_checks.py"))
check("no nearest-time control selected (full candidate universe enumerated; no selection code)", okn and "selected_control" not in src and "min(others" not in src)
cols = set().union(*[set(pd.read_csv(f, nrows=1).columns) for f in OUT.glob("*.csv")])
pair_cols = set(WB.columns) | set(SC.columns)
check("no hierarchy outcome computed or used (no between-car D / speed fields in pair tables; no D columns)",
      not any(k in c for c in pair_cols for k in ["speed", "D_mph", "laptime", "_v"]) and not cols & {"D_mph", "D_same_team", "D_diff_team", "delta_block", "session_balanced_delta"}
      and not re.search(r"abs\(\s*a\.v\s*-|abs\(\s*v\[i\]\s*-\s*v\[", src))
mm = EO[KEY + ["laptime", "ts", "speed_mph"]].merge(PI[KEY + ["laptime", "ts", "speed_mph"]], on=KEY, suffixes=("", "_4h"))
check("raw speeds/timestamps unchanged vs Phase 4H inventory", len(mm) == len(EO) and (mm.laptime == mm.laptime_4h).all() and (mm.ts == mm.ts_4h).all() and (mm.speed_mph == mm.speed_mph_4h).all())
check("2025 remains separately identifiable (yr_group everywhere; case uses 2023-24 levels only)",
      set(EO[EO.year == 2025].yr_group) == {"2025_SECONDARY"} and set(EO[EO.year < 2025].yr_group) == {"2023_2024_PRIMARY"} and set(WB.yr_group) == {"2023_2024_PRIMARY", "2025_SECONDARY"})
era = pd.read_csv(OUT / "year_era_support.csv")
check("lower-resolution years not treated as lap-level evidence", set(EO.year) <= {2023, 2024, 2025}
      and set(era[era.period.isin(["2018-2021", "2022"])].lap_level_hierarchy_support.str[:4]) == {"NONE"} and not era[era.period.isin(["2018-2021", "2022"])].phase4h_classifier_applied.astype(bool).any())
sts = pd.read_csv(OUT / "same_team_support.csv")
tt = sts[sts.layer == "SAME_TEAM_CONCENTRATION_BY_TEAM_ALPHABETICAL"]
check("no team/driver performance ranking (no rank columns; team tables alphabetical)", not any("rank" in c.lower() for c in cols)
      and all(list(g.team) == sorted(g.team) for _, g in tt.groupby(["tier", "yr_group"])))
lv = CE[CE.criterion == "LEVEL"].set_index(["tier", "yr_group"]).value
met = CE[CE.criterion.str.match(r"^M\d$")].pivot_table(index=["tier", "yr_group"], columns="criterion", values="value", aggfunc="first").astype(float)
def level(m):
    if m.M1 >= 6 and m.M2 == 2 and m.M3 >= 30 and m.M4 >= 5 and m.M5 <= .4 and m.M6 <= .4 and m.M7 >= .5 and m.M8 <= .05 and m.M9 >= 6: return "STRONG"
    if m.M1 >= 3 and m.M3 >= 10 and m.M4 >= 3 and m.M5 <= .6 and m.M6 <= .6 and m.M7 >= .25 and m.M9 >= 3: return "ADEQUATE"
    return "MINIMAL" if (m.M1 >= 1 and m.M4 >= 2) else "NONE"
l1, l2 = level(met.loc[("TIER1_STRICT", "2023_2024_PRIMARY")]), level(met.loc[("TIER2_EXTENDED", "2023_2024_PRIMARY")])
r = {"STRONG": 3, "ADEQUATE": 2, "MINIMAL": 1, "NONE": 0}
case = "A" if l1 == l2 == "STRONG" else ("B" if max(r[l1], r[l2]) >= 2 else ("C" if r[l2] >= 1 else "D"))
check("support case follows the pre-specified gate (recomputed from metrics)", case == CE[CE.criterion == "SUPPORT_CASE"].value.iloc[0]
      and lv[("TIER1_STRICT", "2023_2024_PRIMARY")] == l1 and lv[("TIER2_EXTENDED", "2023_2024_PRIMARY")] == l2, f"CASE {case}")
fr = pd.read_csv(OUT / "phase4i_freeze_record.csv")
okp = all(sha(p) == h for p, h in zip(fr.path, fr.sha256)) and len(fr) == 389
okp &= all(git("diff", "--quiet", "fd266ea", "--", f"v4_team_normalized/output/{ph}").returncode == 0 for ph in ["phase4a", "phase4b", "phase4c", "phase4d", "phase4e", "phase4f", "phase4g", "phase4h"])
okp &= all(git("diff", "--quiet", "fd266ea", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-h]_*.py"))
check("no Phase 4A-4H output/script changed (389 hashes; git vs fd266ea)", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
sp = "v4_team_normalized/output/phase4i/phase4i_support_audit_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", sp).stdout.split()
check("pre-specification committed before results (ccb06c6) and unchanged", bool(sc) and sc[-1].startswith("ccb06c6") and git("diff", "--quiet", sc[-1], "--", sp).returncode == 0
      and sorted(git("ls-tree", "--name-only", sc[-1], "v4_team_normalized/output/phase4i/").stdout.split()) == sorted(["v4_team_normalized/output/phase4i/phase4i_freeze_record.csv", sp]))
check("Timing71 labelled as third-party archived live feed", EO.evidence_source.str.contains("third-party").all())
req = ["phase4i_support_audit_spec.md", "eligible_observations.csv", "tier1_strict_support.csv", "tier2_extended_support.csv", "same_car_support.csv", "same_team_support.csv",
       "different_team_candidate_support.csv", "common_support_by_session.csv", "common_support_by_block.csv", "adjacency_support.csv", "reuse_dependence_audit.csv",
       "year_era_support.csv", "performance_scale_reference.csv", "case_evaluation.csv", "phase4i_support_report.md", "phase4i_common_support_report.md",
       "phase4i_dependence_report.md", "phase4i_limitations_report.md"]
check("all required outputs and >=8 figures present", all((OUT / f).exists() for f in req) and len(list((OUT / "figures").glob("*.png"))) >= 8)
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed (paper unchanged)", not out, ";".join(out[:5]))
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4i_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
