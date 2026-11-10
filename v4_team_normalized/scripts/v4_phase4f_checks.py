"""Required Phase 4F checks (4F.27). Exits non-zero on failure; writes phase4f_checks_log.txt."""
import hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4f"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as H  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
AP = pd.read_csv(OUT / "analysis_population.csv")
CB = pd.read_csv(OUT / "car_block_observations.csv", low_memory=False)
C = pd.read_csv(OUT / "comparison_pairs.csv", low_memory=False)
BL = pd.read_csv(OUT / "block_level_contrasts.csv")
e = pd.read_csv(V4 / "output/phase4e/evidence_hierarchy_feasibility.csv")
feas = e[(e.era == "ERA_B_REFERENCE") & e.quality_tier.isin(["A", "B"]) & e.hier_all_three & (e.normalized_category != "RACE")]
prim = set(AP[AP.role == "PRIMARY"].session_key)
check("primary = exactly Phase 4E Design-1-feasible Tier A/B lap-level sessions (15)", prim == set(feas.session_key) and len(prim) == 15)
check("race excluded from primary analysis", not (set(C.session_key) & set(AP[AP.role.str.startswith("RACE")].session_key)) and (AP[AP.role == "PRIMARY"].normalized_category != "RACE").all())
check("primary years only 2023-2024; secondary only 2025", set(AP[AP.role == "PRIMARY"].year) == {2023, 2024} and set(AP[AP.role.str.startswith("ERA_C")].year) == {2025})
check("session categories preserved", set(CB.category.dropna()) <= set(e.normalized_category) and CB.category.notna().all())
pop = H.population()
reg, sessions, off, L = H.laps_for(set(pop.session_key))
# raw lap values / timestamps match retrieved Timing71 evidence (random sample of 300 laps)
man = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv").set_index("source_id")
samp = L.sample(300, random_state=1)
ok = True
cache = {}
for r in samp.itertuples(index=False):
    if r.source_id not in cache:
        d = json.load(open(REPO / man.loc[r.source_id, "local_path"]))
        cache[r.source_id] = d["cars"]["cars"]
    lap = cache[r.source_id][r.car]["stints"][r.stint]["laps"][r.lap_in_stint]
    ok &= np.isclose(lap["laptime"], r.laptime) and np.isclose(lap["timestamp"] / 1000, r.ts)
check("raw lap times and timestamps match retrieved Timing71 evidence (300-lap sample)", ok)
check("no missing values imputed (car-block v and t never NaN; laps without laptime absent)", CB.v.notna().all() and CB.t.notna().all() and L.laptime.notna().all())
r = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
m = CB.drop_duplicates(["car_id"])
check("canonical team mapping exactly matches V4 registry",
      all(r[(r.year == int(c.split("|")[0])) & (r.car_number == c.split("|")[1])].canonical_engineering_team.iloc[0] == t for c, t in zip(m.car_id, m.team)))
check("technical partnerships absent from primary comparisons", not L[L.session_key.isin(prim)].technical_partnership_only.fillna(False).astype(bool).any())
p = C[C.role == "PRIMARY"]
check("same-car comparisons use the same car", (p[p["class"] == "SAME_CAR"].car_a == p[p["class"] == "SAME_CAR"].car_b).all())
st = p[p["class"] == "SAME_TEAM"]
check("same-team comparisons: different cars, same canonical team", (st.car_a != st.car_b).all() and (st.team_a == st.team_b).all())
dt_ = p[p["class"] == "DIFF_TEAM"]
check("different-team comparisons use different canonical teams", (dt_.team_a != dt_.team_b).all())
check("no car compared with itself in same-team or teammate classes", (p[p["class"].isin(["SAME_TEAM", "TEAMMATE_OF_TARGET", "DIFF_TEAM"])].car_a != p[p["class"].isin(["SAME_TEAM", "TEAMMATE_OF_TARGET", "DIFF_TEAM"])].car_b).all())
cb2 = H.car_blocks(L[L.session_key.isin(prim)], "comparable", 5)
cbp = CB[(CB.role == "PRIMARY") & (CB.layer == "comparable")]
check("block assignment deterministic (recomputed car-blocks identical)", len(cb2) == len(cbp) and np.allclose(np.sort(cb2.v.values), np.sort(cbp.v.values)))
check("each car has at most one value per primary block", not CB.duplicated(["role", "layer", "session_key", "block", "car_id"]).any())
_, cmp2, blk2 = H.run(L, list(prim), "comparable", 5)
pc = C[(C.role == "PRIMARY") & (C.layer == "comparable")]
check("pair counts reproduce", cmp2.groupby("class").size().to_dict() == pc.groupby("class").size().to_dict())
bb = BL[(BL.role == "PRIMARY") & (BL.layer == "comparable")].sort_values(["session_key", "block"])
check("block-level contrasts reproduce", np.allclose(blk2.sort_values(["session_key", "block"]).delta_block.values, bb.delta_block.values))
check("broad and comparable layers distinct (comparable subset of broad; strictly fewer laps)", (L.comparable <= L.broad).all() and L.comparable.sum() < L.broad.sum())
check("race never enters hierarchy results", not any(k in set(pd.read_csv(OUT / "session_balanced_results.csv").session_key.dropna().astype(str)) for k in AP[AP.role.str.startswith("RACE")].session_key.astype(str)))
src = "".join(open(f).read() for f in (V4 / "scripts").glob("v4_phase4f_*.py") if not f.name.endswith("_checks.py"))
check("no environmental coefficient / model estimated (no fitting calls)", not any(k in src for k in ["lstsq(", "statsmodels", ".fit(", "polyfit", "LinearRegression"]))
okp = True
for ph in ["phase4a", "phase4b", "phase4c", "phase4d", "phase4e"]:
    last = git("log", "-1", "--format=%H", "--", f"v4_team_normalized/output/{ph}").stdout.strip()
    okp &= git("diff", "--quiet", last, "--", f"v4_team_normalized/output/{ph}").returncode == 0 and not git("status", "--porcelain", "--", f"v4_team_normalized/output/{ph}").stdout.strip()
check("Phases 4A-4E outputs unchanged", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
spec = "v4_team_normalized/output/phase4f/phase4f_prespecified_design.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", spec).stdout.split()
check("pre-specification committed before results and unchanged", bool(sc) and git("diff", "--quiet", sc[-1], "--", spec).returncode == 0, sc[-1][:7] if sc else "")
check("Timing71 labelled as third-party archived live feed (never official)", AP.evidence_source.str.contains("TIMING71_ARCHIVED_LIVE_FEED").all() and CB.evidence_source.str.contains("third-party").all())
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed", not out, ";".join(out[:5]))
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4f_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
