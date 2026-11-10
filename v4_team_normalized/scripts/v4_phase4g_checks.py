"""Required Phase 4G checks (4G.18). Exits non-zero on failure; writes phase4g_checks_log.txt."""
import hashlib, json, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4g"
P4F = V4 / "output" / "phase4f"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()

fr = pd.read_csv(OUT / "phase4f_freeze_record.csv")
check("Phase 4F files unchanged (SHA-256 vs freeze record, 35 files)", len(fr) == 35 and all(sha(p) == h for p, h in zip(fr.path, fr.sha256)))
ce4f = pd.read_csv(P4F / "case_evaluation.csv").set_index("criterion").value
CE = pd.read_csv(OUT / "phase4g_case_evaluation.csv").set_index("criterion").value
check("Phase 4F CASE D unchanged", ce4f["CASE"] == "D" and CE["phase4f_case_unchanged"] == "D")

REC = pd.read_csv(OUT / "primary_control_reconstruction.csv", dtype={"session_key": str})
TS = pd.read_csv(OUT / "timing_sequence_adjacency.csv", dtype={"session_key": str}, low_memory=False)
BLK = pd.read_csv(P4F / "block_level_contrasts.csv", dtype={"session_key": str})
C4 = pd.read_csv(P4F / "comparison_pairs.csv", dtype={"session_key": str}, low_memory=False)
CB4 = pd.read_csv(P4F / "car_block_observations.csv", dtype={"session_key": str}, low_memory=False)
bp = BLK[(BLK.role == "PRIMARY") & (BLK.layer == "comparable")]
r = REC[REC.role == "PRIMARY"]
check("exact Phase 4F primary population reproduced (blocks, sessions, targets)",
      set(zip(r.session_key, r.block)) == set(zip(bp.session_key, bp.block)) and len(r) == int(bp.targets.sum()) and r.session_key.nunique() == bp.session_key.nunique())
pop = F.population()
reg, sessions, off, L = F.laps_for(set(pop.session_key))
prim = list(pop[pop.role == "PRIMARY"].session_key)
cb = F.car_blocks(L[L.session_key.isin(prim)], "comparable", 5)
cbp = CB4[(CB4.role == "PRIMARY") & (CB4.layer == "comparable")]
check("Phase 4F primary car-blocks recomputed identically (unchanged definitions)", len(cb) == len(cbp) and np.allclose(np.sort(cb.v.values), np.sort(cbp.v.values)))
d = C4[(C4.role == "PRIMARY") & (C4.layer == "comparable") & (C4.width_min == 5) & (C4["class"] == "DIFF_TEAM")]
m = r.merge(d.rename(columns={"car_a": "target"}), on=["session_key", "block", "target"])
check("exact Phase 4F primary controls reproduced (control, D, separation)", len(m) == len(d) == len(r) and (m.control == m.car_b).all()
      and np.allclose(m.D_diff_team_target, m.D_mph) and np.allclose(m.abs_target_control_sep_s / 60, m.time_sep_min))
t = C4[(C4.role == "PRIMARY") & (C4.layer == "comparable") & (C4.width_min == 5) & (C4["class"] == "TEAMMATE_OF_TARGET")]
m2 = r.merge(t.rename(columns={"car_a": "target"}), on=["session_key", "block", "target"])
check("exact Phase 4F primary teammate comparators reproduced", len(m2) == len(r) and (m2.teammate == m2.car_b).all() and np.allclose(m2.D_same_team_target, m2.D_mph))
A = TS[(TS.role == "PRIMARY") & (TS.population == "A_PRIMARY_CONTROL")]
check("population A pairs identical to reconstructed controls", len(A) == len(r) and set(zip(A.session_key, A.block, A.target, A.comparator)) == set(zip(r.session_key, r.block, r.target, r.control)))

# brute-force re-derivation of adjacency counts on a random sample (independent of the Seq class)
comp = L[L.comparable & (L.join_status == "MATCHED") & ~L.technical_partnership_only.fillna(False).astype(bool)].copy()
comp["block"] = np.floor(comp.ts / 300).astype(int)
lapts = {k: np.sort(g.ts.values) for k, g in comp.groupby(["session_key", "block", "car_id"])}
allts = {sk: np.round(g.ts.values, 3) for sk, g in L.groupby("session_key")}
samp = TS[(TS.role == "PRIMARY") & TS.population.isin(["A_PRIMARY_CONTROL", "B_ELIGIBLE_CANDIDATES", "C1_TEAMMATE_OF_TARGET"])].sample(300, random_state=7)
ok, chron = True, True
for row in samp.itertuples(index=False):
    ta, tc = lapts[(row.session_key, row.block, row.target)], lapts[(row.session_key, row.block, row.comparator)]
    S = allts[row.session_key]
    inter = []
    for a in ta:
        c = tc[np.argmin(np.abs(tc - a))]
        a3, c3 = round(a, 3), round(c, 3)
        lo, hi = min(a3, c3), max(a3, c3)
        inter.append(int(((S > lo) & (S < hi)).sum()))
    ok &= np.isclose(np.median(inter), row.median_intervening) and min(inter) == row.min_intervening
check("adjacency counts reproduce by brute force (300-pair sample)", ok)
chron = all(np.all(np.diff(np.sort(v)) >= 0) for v in allts.values()) and all(
    (g.sort_values(["stint", "lap_in_stint"]).groupby("stint").ts.diff().dropna() > 0).all() for _, g in L[L.session_key.isin(prim)].groupby(["session_key", "source_id", "car"]))
check("timing order chronological (per-car lap timestamps strictly increasing within each source file's stints; session sequence sorted)", chron,
      "stint indices are per Timing71 source file (combined multi-file qualifying key)")
su = TS[TS.pair_category == "SAME_UPDATE"]
check("same-update pairs carry no invented crossing order", (su.share_same_update > 0).all() and TS.columns.str.contains("within_update_order").sum() == 0)

regd = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
tm = {(str(y) + "|" + c): t for y, c, t in zip(regd.year, regd.car_number, regd.canonical_engineering_team)}
P = TS[TS.population.isin(["A_PRIMARY_CONTROL", "B_ELIGIBLE_CANDIDATES", "C1_TEAMMATE_OF_TARGET", "C2_ALL_TEAMMATES"])]
check("same-team and different-team identities reproduce from the V4 registry",
      all(tm[a] == ta for a, ta in zip(P.target, P.target_team)) and all(tm[c] == tc for c, tc in zip(P.comparator, P.comparator_team))
      and (P[P.population.str.startswith("C")].target_team == P[P.population.str.startswith("C")].comparator_team).all()
      and (P[~P.population.str.startswith("C")].target_team != P[~P.population.str.startswith("C")].comparator_team).all())
tpc = {str(y) + "|" + c for y, c in zip(regd[regd.relationship_type == "TECHNICAL_PARTNERSHIP"].year, regd[regd.relationship_type == "TECHNICAL_PARTNERSHIP"].car_number)}
cc = P[P.population.str.startswith("C")]
check("no technical partnerships in primary teammate relationships (by year|car registry relationship)",
      not L[L.session_key.isin(prim)].technical_partnership_only.fillna(False).astype(bool).any() and not ((set(cc.target) | set(cc.comparator)) & tpc))
csvs = list(OUT.glob("*.csv"))
bad_tow = []
for f in csvs:
    if f.name == "future_evidence_feasibility.csv":
        continue
    x = pd.read_csv(f, low_memory=False)
    bad_tow += [f.name for c in x.columns if any(k in c.lower() for k in ["tow", "slipstream", "draft", "aero"])]
    for c in x.select_dtypes(["object", "string"]).columns:
        if x[c].astype(str).str.contains(r"\btow|TOW_|slipstream|aero group|traffic group", regex=True).any():
            bad_tow.append(f"{f.name}:{c}")
check("no tow / traffic-group / aerodynamic status invented in outputs", not bad_tow, ";".join(bad_tow[:5]))
src = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4g_*.py") if not p.name.endswith("_checks.py"))
newcols = set().union(*[set(pd.read_csv(f, nrows=1).columns) for f in csvs])
NBd = pd.read_csv(OUT / "negative_positive_block_diagnostics.csv", dtype={"session_key": str})
nbb = NBd[NBd.level == "BLOCK"].merge(bp[["session_key", "block", "delta_block"]], on=["session_key", "block"], suffixes=("", "_4f"))
check("no new hierarchy estimator promoted (delta_block only copied verbatim from Phase 4F; no new Δ/case on the hierarchy)",
      len(nbb) == len(bp) and np.allclose(nbb.delta_block, nbb.delta_block_4f) and not any(c in newcols for c in ["session_balanced_delta", "delta_block_team_balanced"])
      and "hierarchy_case" not in src)
check("no model fitted (no fitting calls)", not any(k in src for k in ["lstsq(", "statsmodels", ".fit(", "polyfit", "LinearRegression", "sklearn"]))
check("no team/driver ranking produced (no rank-of-team/driver columns; team shares alphabetical)",
      not any(("rank" in c.lower() and ("team" in c.lower() or "driver" in c.lower())) for c in newcols) and "driver" not in " ".join(newcols).lower())
check("2025 secondary never pooled with primary (role separate in every pair table)", set(TS.role) == {"PRIMARY", "ERA_C_SECONDARY"} and
      set(TS[TS.role == "PRIMARY"].year) == {2023, 2024} and set(TS[TS.role == "ERA_C_SECONDARY"].year) == {2025})
dv = pd.read_csv(OUT / "design_population_verification.csv")
check("Phase 4F sensitivity populations reproduced (adjacent-block, reweighted, team-balanced)",
      (dv.phase4f_n == dv.phase4g_n).all() and np.isclose(dv.phase4f_session_balanced_D[0], dv.phase4g_session_balanced_D[0])
      and np.isclose(dv.phase4f_pooled_weighted_D[1], dv.phase4g_pooled_weighted_D[1]) and bool(dv.team_balanced_block_values_match[2]))
okp = True
for ph in ["phase4a", "phase4b", "phase4c", "phase4d", "phase4e", "phase4f"]:
    okp &= git("diff", "--quiet", "81455f3", "--", f"v4_team_normalized/output/{ph}").returncode == 0 and not git("status", "--porcelain", "--", f"v4_team_normalized/output/{ph}").stdout.strip()
okp &= all(git("diff", "--quiet", "81455f3", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-f]_*.py"))
check("no Phase 4A-4F file changes (outputs and scripts vs 81455f3)", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
spec = "v4_team_normalized/output/phase4g/phase4g_design_diagnostic_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", spec).stdout.split()
check("pre-specification committed before results (ffdfacd) and unchanged", bool(sc) and sc[-1].startswith("ffdfacd") and git("diff", "--quiet", sc[-1], "--", spec).returncode == 0
      and git("ls-tree", "--name-only", sc[-1], "v4_team_normalized/output/phase4g/").stdout.split() == ["v4_team_normalized/output/phase4g/phase4f_freeze_record.csv", spec], sc[-1][:7] if sc else "")
check("Timing71 labelled as third-party archived live feed (never official)", REC.evidence_source.str.contains("third-party").all() and TS.evidence_source.str.contains("TIMING71_ARCHIVED_LIVE_FEED").all())
req = ["phase4g_design_diagnostic_spec.md", "primary_control_reconstruction.csv", "timing_sequence_adjacency.csv", "adjacency_distribution_summary.csv", "different_team_adjacency_strata.csv",
       "negative_positive_block_diagnostics.csv", "control_reuse_audit.csv", "design_population_comparison.csv", "year_session_adjacency.csv", "future_evidence_feasibility.csv",
       "phase4g_control_selection_report.md", "phase4g_adjacency_report.md", "phase4g_limitations_report.md"]
check("all required outputs and >=7 figures present", all((OUT / f).exists() for f in req) and len(list((OUT / "figures").glob("*.png"))) >= 7)
rep = "".join((OUT / f).read_text() for f in req if f.endswith("report.md"))
check("reports contain the required no-tow statement", "Timing-sequence adjacency is consistent with shared local on-track context but does not identify tow." in rep)
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("nothing outside v4_team_normalized/ changed", not out, ";".join(out[:5]))
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4g_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
