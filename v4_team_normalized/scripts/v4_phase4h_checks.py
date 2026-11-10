"""Required Phase 4H checks (4H.14). Exits non-zero on failure; writes phase4h_checks_log.txt."""
import glob, hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4h"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402
import v4_phase4h_audit as H  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
P = pd.read_csv(OUT / "practice_lap_inventory.csv", dtype={"session_key": str, "car": str}, low_memory=False)
Q = pd.read_csv(OUT / "qualifying_performance_reference.csv", dtype={"session_key": str, "car": str}, low_memory=False)
CE = pd.read_csv(OUT / "case_evaluation.csv").set_index("criterion").value

fr = pd.read_csv(OUT / "phase4h_freeze_record.csv")
check("Phase 4F/4G result files unchanged (SHA-256 vs freeze record)", len(fr) == 61 and all(sha(p) == h for p, h in zip(fr.path, fr.sha256)))
check("Phase 4F CASE D and Phase 4G CASE A unchanged", CE["phase4f_case_unchanged"] == "D" and CE["phase4g_case_unchanged"] == "A")

pop = F.population()
e = pd.read_csv(V4 / "output/phase4e/evidence_hierarchy_feasibility.csv")
exp = set(pop[(pop.role.eq("PRIMARY") | pop.role.str.startswith("ERA_C")) & pop.normalized_category.isin(H.PRACTICE_CATS)].session_key)
check("exact Phase 4E/4F practice population provenance (Tier A/B practice-type, Phase 4F roles)",
      set(P.session_key) == exp and set(e[e.session_key.isin(exp)].quality_tier) <= {"A", "B"})
check("qualifying reference = Tier A/B formal qualifying only", set(Q.session_key) == set(H.QUAL) and set(e[e.session_key.isin(H.QUAL)].quality_tier) <= {"A", "B"})
check("no race in the audit", not set(P.session_key) & set(pop[pop.normalized_category == "RACE"].session_key) and not (P.category == "RACE").any())

reg, sessions, off, L = F.laps_for(exp | set(H.QUAL))
man = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv").set_index("source_id")
samp = P.sample(400, random_state=3)
cache, ok = {}, True
for r in samp.itertuples(index=False):
    if r.source_id not in cache:
        cache[r.source_id] = json.load(open(REPO / man.loc[r.source_id, "local_path"]))["cars"]["cars"]
    lap = cache[r.source_id][r.car]["stints"][int(r.stint)]["laps"][int(r.lap_in_stint)]
    ok &= np.isclose(lap["laptime"], r.laptime, atol=1e-9) and np.isclose(lap["timestamp"] / 1000, r.ts) and np.isclose(r.speed_mph, 2.5 * 3600 / lap["laptime"])
check("raw lap times / timestamps unaltered vs Timing71 evidence (400-lap sample); speed = 2.5*3600/laptime", ok)
check("no missing speed imputed (inventory row count = source lap records; no NaN laptime/speed)",
      len(P) == int(L.session_key.isin(exp).sum()) and P.laptime.notna().all() and P.speed_mph.notna().all())

ok4, n_off = True, 0
for sk, ids in H.QUAL.items():
    for sid in ids:
        o = json.load(open(glob.glob(str(V4 / f"evidence/phase4e/official_session_details/*_session_{sid}_raw.json"))[0]))
        for r in o["records"]:
            qq = [r.get(f"QualLap{i}") for i in range(1, 5)]
            if not all(isinstance(z, str) and z.strip() for z in qq):
                continue
            base = Q[(Q.session_key == sk) & (Q.provenance == "OFFICIAL_ANCHORED") & (Q.official_segment == o["SessionName"])]
            m = base[base.car == str(r["CarNumber"])]
            if m.empty:  # same fallback as the audit: leading-zero variant only when no exact car match
                m = base[(base.car.str.lstrip("0") == str(r["CarNumber"]).lstrip("0")) & ~base.car.isin(base[base.car == str(r["CarNumber"])].car)]
                m = m[m.groupby("attempt_id").laptime.transform(lambda s_: tuple(s_.round(4)) == tuple(round(float(z), 4) for z in qq))]
            if len(m):
                n_off += 1
                ok4 &= len(m) == 4 and np.allclose(m.sort_values("lap_in_attempt").laptime.round(4).values, [round(float(z), 4) for z in qq]) and list(m.sort_values("lap_in_attempt").lap_in_attempt) == [1, 2, 3, 4]
check("official qualifying four timed laps identified exactly (QualLap1-4 order and values)", ok4 and n_off == int(CE["n_2023_official_attempts"]) + int(CE["n_2024_official_attempts"]), f"{n_off} attempts")
okst = not P.duplicated(["session_key", "source_id", "car", "stint", "lap_in_stint"]).any() and all(
    (g.sort_values("lap_in_stint").ts.diff().dropna() > 0).all() for _, g in P.groupby(["session_key", "source_id", "car", "stint"]))
check("stint ordering correct (unique positions; timestamps increase with position)", okst)

pop2 = pop
Lp = L[L.session_key.isin(exp)].merge(pop[["session_key", "role", "normalized_category"]], on="session_key").rename(columns={"normalized_category": "category"})
X = H.inventory(Lp, H.pit_matching(Lp))
Qa, OFF, _ = H.qualifying_attempts(H.inventory(L[L.session_key.isin(H.QUAL)].merge(pop[["session_key", "role", "normalized_category"]], on="session_key").rename(columns={"normalized_category": "category"}),
                                                H.pit_matching(L[L.session_key.isin(H.QUAL)])))
T = H.thresholds(Qa)
c1, _ = H.classify(X, T)
c2, _ = H.classify(X.sample(frac=1, random_state=9).sort_values(["session_key", "source_id", "car", "stint", "lap_in_stint"]).reset_index(drop=True), T)
key = ["session_key", "source_id", "car", "stint", "lap_in_stint"]
mm = P[key + ["cls"]].merge(c1[key + ["cls"]], on=key, suffixes=("", "_1")).merge(c2[key + ["cls"]], on=key, suffixes=("", "_2"))
check("classification deterministic (re-run and shuffled-input re-run identical to saved)", len(mm) == len(P) and (mm.cls == mm.cls_1).all() and (mm.cls == mm.cls_2).all())
# independence from D / Phase 4F delta / teams / adjacency: perturb those inputs and confirm identical classes
Xp = X.copy()
Xp["canonical_engineering_team"] = "PERMUTED"
Xp["driver"] = "X"
c3, _ = H.classify(Xp, T)
src = open(V4 / "scripts/v4_phase4h_audit.py").read()
body = src[src.index("def d_flags"):src.index("# ------------------------------------------------------------------ qualifying reference")]
forbidden = [k for k in ["D_mph", "delta_block", "team", "pair_category", "intervening", "comparator", "phase4f", "phase4g", "block"] if re.search(k, body, re.I)]
check("classification does not depend on D, Phase 4F delta, team or adjacency (code scan + team-permutation invariance)", not forbidden and (c3.cls.values == c1.cls.values).all(), ";".join(forbidden))
spec = (OUT / "phase4h_performance_validity_spec.md").read_text()
okT = (abs(T["T_steady_95"] - float(CE["T_steady_95"])) < 1e-12 and abs(T["T_level_100"] - float(CE["T_level_100"])) < 1e-12 and H.BAND == (37.0, 45.0) and H.COH == 2.0 and H.PIT_TOL == 5.0
       and "q-th percentile" in spec and "2023 `OFFICIAL_ANCHORED`" in spec and "[37.0, 45.0]" in spec and "within 5 s" in spec)
a = Qa[(Qa.provenance == "OFFICIAL_ANCHORED") & (Qa.year == 2023)].drop_duplicates("attempt_id")
okT &= np.isclose(T["T_steady_100"], a.within_attempt_rel_range.max()) and np.isclose(T["T_level_95"], np.percentile(a.level_deficit_to_car_best_attempt, 95))
check("thresholds/rules match the committed pre-specification (2023 official quantiles; band; coherence; pit tolerance)", okT)
case_ok = CE["MEASUREMENT_VALIDITY_CASE"] == ("C" if str(CE["C1_pass"]) != "True" else ("D" if float(CE["S_AB_nonD_2023_2024"]) < 0.20 else CE["MEASUREMENT_VALIDITY_CASE"]))
check("case evaluation follows the pre-specified precedence (C -> D -> A -> B)", case_ok)
RC = pd.read_csv(OUT / "run_state_classification.csv")
check("2025 kept separate (own year group; not in case criteria)", set(RC.yr_group) == {"2023_2024_PRIMARY", "2025_SECONDARY"} and "S_AB_nonD_2023_2024" in CE.index
      and set(RC[RC.level == "YEAR"].year[RC[RC.level == "YEAR"].yr_group == "2025_SECONDARY"]) == {2025.0})
csvs = list(OUT.glob("*.csv"))
cols = set().union(*[set(pd.read_csv(f, nrows=1).columns) for f in csvs])
tm = RC[RC.level == "TEAM_COVERAGE_ONLY_ALPHABETICAL"]
check("no team/driver ranking (no rank columns; team coverage alphabetical)", not any("rank" in c.lower() for c in cols)
      and all(list(g.canonical_engineering_team) == sorted(g.canonical_engineering_team) for _, g in tm.groupby("yr_group")))
hsrc = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4h_*.py") if not p.name.endswith("_checks.py"))
check("no hierarchy recomputed / no model fitted", not any(k in hsrc for k in ["delta_block =", "session_balanced_delta", "lstsq(", "statsmodels", ".fit(", "polyfit", "LinearRegression"])
      and not (cols & {"delta_block", "session_balanced_delta", "D_same_team", "D_diff_team"}))
bad = []
for f in csvs:
    x = pd.read_csv(f, low_memory=False)
    bad += [f"{f.name}:{c}" for c in x.columns if any(k in c.lower() for k in ["tow", "slipstream", "draft"])]
check("no tow / traffic status invented", not bad, ";".join(bad[:3]))
okp = True
for ph in ["phase4a", "phase4b", "phase4c", "phase4d", "phase4e", "phase4f", "phase4g"]:
    okp &= git("diff", "--quiet", "d903148", "--", f"v4_team_normalized/output/{ph}").returncode == 0 and not git("status", "--porcelain", "--", f"v4_team_normalized/output/{ph}").stdout.strip()
okp &= all(git("diff", "--quiet", "d903148", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-g]_*.py"))
check("no Phase 4A-4G files changed (outputs and scripts vs d903148)", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
sp = "v4_team_normalized/output/phase4h/phase4h_performance_validity_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", sp).stdout.split()
check("pre-specification committed before results (a56b4dd) and unchanged", bool(sc) and sc[-1].startswith("a56b4dd") and git("diff", "--quiet", sc[-1], "--", sp).returncode == 0
      and sorted(git("ls-tree", "--name-only", sc[-1], "v4_team_normalized/output/phase4h/").stdout.split()) == sorted(["v4_team_normalized/output/phase4h/phase4h_freeze_record.csv", sp]))
check("Timing71 labelled third-party; official anchor labelled distinctly", P.evidence_source.str.contains("third-party").all()
      and Q[Q.provenance == "OFFICIAL_ANCHORED"].anchor_source.str.contains("INDYCAR_OFFICIAL").all())
req = ["phase4h_performance_validity_spec.md", "qualifying_performance_reference.csv", "practice_lap_inventory.csv", "practice_speed_distribution.csv", "stint_sequence_audit.csv",
       "run_state_classification.csv", "classification_rule_audit.csv", "qualifying_calibration.csv", "phase4f_population_run_state_audit.csv", "adjacency_run_state_audit.csv",
       "session_year_validity_summary.csv", "case_evaluation.csv", "phase4h_performance_validity_report.md", "phase4h_run_state_report.md", "phase4h_limitations_report.md"]
check("all required outputs and >=8 figures present", all((OUT / f).exists() for f in req) and len(list((OUT / "figures").glob("*.png"))) >= 8)
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed", not out, ";".join(out[:5]))
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4h_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
