"""Required Phase 4J checks (4J.20). Exits non-zero on failure; writes phase4j_checks_log.txt."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4j"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4g_adjacency as G  # noqa: E402
import v4_phase4i_support as S  # noqa: E402
import v4_phase4j_hierarchy as J  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
IV = pd.read_csv(OUT / "phase4j_input_verification.csv").set_index("item").value
CX = pd.read_csv(OUT / "primary_common_support.csv", dtype={"session_key": str})
SC = pd.read_csv(OUT / "same_car_primary.csv", dtype={"session_key": str})
CA = pd.read_csv(OUT / "different_team_candidates.csv", dtype={"session_key": str})
SL = pd.read_csv(OUT / "session_level_hierarchy.csv", dtype={"session_key": str})
HS = pd.read_csv(OUT / "hierarchy_summary_all_analyses.csv")
CE = pd.read_csv(OUT / "case_evaluation.csv").set_index("criterion").value

check("Phase 4H classifications reproduced exactly (Phase 4I checks re-run 4H classifier; recorded pre-spec)", str(IV["TIER1_STRICT_eligible_laps_match"]) == "True"
      and "22/22" in (V4 / "output/phase4i/phase4i_checks_log.txt").read_text())
check("Phase 4I eligibility reproduced exactly (laps, pair universe, same-car pairs; both tiers)", str(IV["phase4i_eligibility_reproduced"]) == "True")
P, L = S.load()
A_, B_ = "A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE"
# every lap in primary car-blocks must be class A: rebuild from spec definitions
tier, sess = J.SESS["PRIMARY_TIER1_2023_2024"]
E1 = P[P.cls.isin(S.TIERS[tier]) & (P.join_status == "MATCHED") & P.session_key.isin(sess)]
used = set(CX.target_cb) | set(CX.teammate_cb) | set(SC.cb_a) | set(SC.cb_b) | {f"{s}|{b}|{c}" for s, b, c in zip(CA.session_key, CA.block, CA.candidate)}
cb1 = set(E1.session_key + "|" + E1.block.astype(str) + "|" + E1.car_id)
check("Tier 1 uses class A only (every primary car-block built only from A laps)", (E1.cls == A_).all() and used <= cb1)
t2 = pd.read_csv(OUT / "tier2_sensitivity.csv", low_memory=False)
check("Tier 2 uses only A/B (composition labels limited to A_ONLY/B_ONLY/MIXED_AB)", set(t2[t2.table == "COMPOSITION"].composition.str.split("|").explode()) <= {"A_ONLY", "B_ONLY", "MIXED_AB"})
check("no C/D/E enters any hierarchy population", set(S.TIERS["TIER1_STRICT"]) == {A_} and set(S.TIERS["TIER2_EXTENDED"]) == {A_, B_})
yrs = {k: set(P[P.session_key.isin(v[1])].year) for k, v in J.SESS.items()}
check("primary years 2023-2024 only; 2025 separate", yrs["PRIMARY_TIER1_2023_2024"] <= {2023, 2024} and yrs["TIER2_SENSITIVITY_2023_2024"] <= {2023, 2024}
      and yrs["REPLICATION_2025_TIER1"] == {2025} and set(CX.year) <= {2023, 2024})
check("no 2018-2022 lap-level projection; race excluded", set(P.year) <= {2023, 2024, 2025} and "RACE" not in set(P.category))
c4i = pd.read_csv(V4 / "output/phase4i/common_support_by_session.csv", dtype={"session_key": str})
sup = lambda t, y: sorted(c4i[(c4i.tier == t) & (c4i.yr_group == y) & c4i.all_three_layers_block_scale].session_key)
check("sessions = exactly the Phase 4I-supported sessions (no additions)", sorted(J.SESS["PRIMARY_TIER1_2023_2024"][1]) == sup("TIER1_STRICT", "2023_2024_PRIMARY")
      and sorted(J.SESS["TIER2_SENSITIVITY_2023_2024"][1]) == sup("TIER2_EXTENDED", "2023_2024_PRIMARY") and sorted(J.SESS["REPLICATION_2025_TIER1"][1]) == sup("TIER1_STRICT", "2025_SECONDARY"))
check("frozen 5-minute blocks unchanged (block = floor(ts/300))", (P.block == np.floor(P.ts / 300).astype(int)).all() and all(int(c.split("|")[1]) == b for c, b in zip(CX.target_cb, CX.block)))
check("same-car identities exact (same car, same stint, consecutive blocks)", all(a.split("|")[-2:] == b.split("|")[-2:] and int(b.split("|")[1]) == int(a.split("|")[1]) + 1
                                                                                for a, b in zip(SC.cb_a, SC.cb_b)))
regd = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
tm = {f"{y}|{c}": t for y, c, t in zip(regd.year, regd.car_number, regd.canonical_engineering_team)}
check("same-team registry mapping exact", all(tm[a] == tm[b] == t for a, b, t in zip(CX.target, CX.teammate, CX.team)) and (CX.target != CX.teammate).all())
tpc = {f"{y}|{c}" for y, c, r in zip(regd.year, regd.car_number, regd.relationship_type) if r == "TECHNICAL_PARTNERSHIP"}
pe = P.drop_duplicates("car_id").set_index("car_id")
cars = list(set(CX.target) | set(CX.teammate))
check("technical partnerships / non-primary-layer excluded", not set(cars) & tpc and pe.loc[cars].primary_layer.astype(bool).all() and not pe.loc[cars].technical_partnership_only.fillna(False).astype(bool).any())
check("different-team candidates truly different canonical teams", all(tm[c] != tm[t] for c, t in zip(CA.candidate, CA.target)))
src = open(V4 / "scripts/v4_phase4j_hierarchy.py").read()
nct = CA.groupby("context_id").size()
check("no nearest-time control selection (all candidates retained per context; no time-minimising selection)",
      (CX.set_index("context_id").n_candidates == nct.reindex(CX.context_id).fillna(0).values).all() and not re.search(r"min\([^)]*key=", src) and "argmin" not in src)
# adjacency re-derivation (sample): categories equal Phase 4G pair_metrics on eligible laps, target orientation
seqs = {sk: G.Seq(g.ts.values) for sk, g in L.groupby("session_key")}
laps = {k: g.ts.values for k, g in E1.groupby(["session_key", "block", "car_id"])}
smp = CA.sample(min(200, len(CA)), random_state=5)
okadj = all(G.CATS[G.pair_metrics(seqs[r.session_key], laps[(r.session_key, r.block, r.target)], laps[(r.session_key, r.block, r.candidate)])["pair_category_code"]] == r.candidate_category
            for r in smp.itertuples(index=False))
check("adjacency descriptors match Phase 4G definitions (200-candidate re-derivation)", okadj and set(CA.candidate_category) <= set(G.CATS))
check("tied timestamps never receive invented order (same-update handled only as its own stratum)", set(CX.adjacency_category) <= set(G.CATS) and "within_update_order" not in src)
CX2, SC2, CA2 = J.build(P, seqs, tier, sess)
check("strict common-support exclusions deterministic (rebuild identical)", (CX2.in_common_support.values == CX.in_common_support.values).all() and np.allclose(CX2.D_same_team, CX.D_same_team))
agg = CA[CA.admissible].groupby("context_id").D_mph.median()
cs = CX[CX.in_common_support].set_index("context_id")
check("different-team aggregation = median over admissible (same-stratum) candidates, per spec",
      np.allclose(cs.D_diff_team_ctx.values, agg.reindex(cs.index).values) and (CX[~CX.in_common_support].D_diff_team_ctx.isna()).all()
      and ((CA.admissible) == (CA.candidate_category == CA.context_category)).all())
ps = SL[(SL.analysis == "PRIMARY_TIER1_2023_2024") & SL.evaluable]
okw = np.isclose(ps.C1.median(), HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].C1.iloc[0]) and np.isclose(ps.C2.median(), HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].C2.iloc[0])
for s, g in cs.groupby("session_key"):
    r = ps[ps.session_key == s]
    if len(r):
        okw &= np.isclose(r.D_same_team.iloc[0], g.D_same_team.median()) and np.isclose(r.C2.iloc[0], g.paired_C2.median())
check("session weighting = equal-session medians of session medians (per spec)", okw)
check("no raw pair treated as an independent session (bootstrap/LOSO over sessions only)", "rng.choice(v, len(v)" in src and int(HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].evaluable_sessions.iloc[0]) == len(ps)
      and len(pd.read_csv(OUT / "leave_one_session_out.csv").query("analysis == 'PRIMARY_TIER1_2023_2024'")) == len(ps))
sp = "v4_team_normalized/output/phase4j/phase4j_final_hierarchy_spec.md"
sc = git("log", "--format=%H", "--diff-filter=A", "--", sp).stdout.split()
tree = sorted(git("ls-tree", "--name-only", sc[-1], "v4_team_normalized/output/phase4j/").stdout.split()) if sc else []
check("no hierarchy result computed before the spec commit (28af221 contains only spec + verification; spec unchanged)",
      bool(sc) and sc[-1].startswith("28af221") and git("diff", "--quiet", sc[-1], "--", sp).returncode == 0
      and tree == sorted([sp, "v4_team_normalized/output/phase4j/phase4j_freeze_record.csv", "v4_team_normalized/output/phase4j/phase4j_input_verification.csv"])
      and git("cat-file", "-e", f"{sc[-1]}:v4_team_normalized/scripts/v4_phase4j_hierarchy.py").returncode != 0)
fr = pd.read_csv(OUT / "phase4j_freeze_record.csv")
okp = len(fr) == 419 and all(sha(p) == h for p, h in zip(fr.path, fr.sha256))
okp &= all(git("diff", "--quiet", "12a660d", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-i]_*.py"))
check("no Phase 4A-4I output/script changed (419 hashes; scripts vs 12a660d)", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("paper unchanged; nothing outside V4 changed", not out, ";".join(out[:5]))
check("primary case recorded before sensitivity labels and unchanged by them", list(CE.index[:10]).index("PRIMARY_CASE") == 9 and CE["PRIMARY_CASE"] == HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].case.iloc[0]
      and "never replaces primary" in CE["TIER2_SENSITIVITY_LABEL"] and "never replaces primary" in CE["REPLICATION_2025_LABEL"])
req = ["phase4j_final_hierarchy_spec.md", "primary_common_support.csv", "same_car_primary.csv", "same_team_primary.csv", "different_team_candidates.csv", "different_team_context_aggregate.csv",
       "session_level_hierarchy.csv", "primary_hierarchy_summary.csv", "hierarchy_contrasts.csv", "leave_one_session_out.csv", "leave_one_team_out.csv", "tier2_sensitivity.csv",
       "replication_2025.csv", "performance_scale_context.csv", "case_evaluation.csv", "phase4j_final_hierarchy_report.md", "phase4j_common_support_report.md",
       "phase4j_robustness_report.md", "phase4j_limitations_report.md"]
check("all required outputs and >=8 figures present", all((OUT / f).exists() for f in req) and len(list((OUT / "figures").glob("*.png"))) >= 8)
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4j_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
