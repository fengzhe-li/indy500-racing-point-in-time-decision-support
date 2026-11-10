"""Required Phase 4L checks (4L.10). Exits non-zero on failure; writes phase4l_checks_log.txt."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
O = V4 / "output"
OUT = O / "phase4l"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4l_synthesis as SY  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a, cwd=REPO: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
K = pd.read_csv(OUT / "phase4l_key_results_table.csv")
syn = (OUT / "phase4l_final_scientific_synthesis.md").read_text()
docs = {n: (OUT / n).read_text() for n in ["phase4l_final_scientific_synthesis.md", "phase4l_evidence_chain.md", "phase4l_paper_integration_map.md",
                                         "phase4l_future_data_requirements.md", "phase4l_limitations.md"]}
cl = pd.read_csv(OUT / "phase4l_claims_matrix.csv")
PO = pd.read_csv(OUT / "phase4l_phase_outcomes.csv")

# 1 case labels vs frozen sources (independent reads)
src_cases = {"4C": pd.read_csv(O / "phase4c/case_evaluation.csv").headline_by_precedence_D_B_C_A.iloc[0],
             "4D": pd.read_csv(O / "phase4d/feasibility_case_evaluation.csv").headline_by_precedence_C_D_B_A.iloc[0],
             "4F": pd.read_csv(O / "phase4f/case_evaluation.csv").set_index("criterion").value["CASE"],
             "4G": pd.read_csv(O / "phase4g/phase4g_case_evaluation.csv").set_index("criterion").value["CASE"],
             "4H": pd.read_csv(O / "phase4h/case_evaluation.csv").set_index("criterion").value["MEASUREMENT_VALIDITY_CASE"],
             "4I": pd.read_csv(O / "phase4i/case_evaluation.csv").query("criterion == 'SUPPORT_CASE'").value.iloc[0],
             "4J": pd.read_csv(O / "phase4j/case_evaluation.csv").set_index("criterion").value["PRIMARY_CASE"],
             "4K": pd.read_csv(O / "phase4k/case_evaluation.csv").set_index("criterion").value["PRIMARY_FEASIBILITY_CASE"]}
exp = {"4C": "B", "4D": "C", "4F": "D", "4G": "A", "4H": "D", "4I": "B", "4J": "B", "4K": "C"}
check("every final case label matches its frozen source and the accepted sequence", src_cases == exp and all(PO.set_index("phase").case_label[p] == c for p, c in exp.items())
      and all(f"**{c}**" in syn for c in exp.values()), str(src_cases))
# 2 key numbers: regenerate from sources and compare; spot-check against the user-quoted values
K2 = SY.extract()
check("all key numbers reproduce from source outputs (re-extraction identical)", K2.astype(str).equals(K.astype(str)))
kv = {(r.phase, r.item): str(r.value) for r in K.itertuples(index=False)}
quoted = {("P1-2", "official_entry_list_labels"): "59", ("P1-2", "canonical_engineering_teams"): "21", ("P1-2", "teammate_pairs_missed_by_old_grouping"): "85",
          ("P1-2", "strict_v4_teammate_pairs"): "313", ("4G", "primary_control_share_no_intervening"): "0.577", ("4H", "share_A_of_at_speed_2023_24_pct"): "8.1",
          ("4H", "share_AB_of_at_speed_2023_24_pct"): "11.6", ("4H", "share_C_ambiguous_of_at_speed_2023_24_pct"): "74.6", ("4H", "phase4f_primary_control_pairs_both_A_pct"): "1.4",
          ("4I", "tier1_eligible_laps"): "1172", ("4I", "tier1_eligible_carblocks"): "374", ("4I", "tier1_same_team_pairs"): "46", ("4I", "tier1_diff_team_candidates"): "422",
          ("4I", "tier1_blocks_all_three_layers"): "25", ("4J", "contexts_common_support"): "53", ("4J", "evaluable_sessions"): "6", ("4J", "C1"): "0.696",
          ("4J", "C2"): "0.199", ("4J", "tier2_C2"): "-0.094", ("4K", "F0"): "113", ("4K", "F2"): "71", ("4K", "F3"): "44", ("4K", "F4"): "22", ("4K", "F5"): "8",
          ("4K", "events_with_measured_env_change"): "45", ("4K", "tier2_F5"): "36", ("4K", "rep2025_F5"): "3"}
bad = [k for k, v in quoted.items() if kv.get(k) != v]
check("quoted key counts/numbers match source outputs", not bad, str(bad))
regen = {}
SY.write_docs(lambda ph, it: K2.set_index(["phase", "item"]).value[(ph, it)])
check("synthesis documents are exactly the rendering of the source-extracted values", all((OUT / n).read_text() == t for n, t in docs.items()))
# 3 C1/C2 interpretation
c2_para = syn[syn.index("**C2 (context-paired"):syn.index("**C3 =")]
check("Phase 4J C1/C2 interpretation matches pre-registered result (C1 POSITIVE_CONSISTENT; C2 INCONSISTENT; full hierarchy not established)",
      kv[("4J", "C1_status")] == "POSITIVE_CONSISTENT" and kv[("4J", "C2_status")] == "INCONSISTENT" and "was **not established**" in syn
      and "The V4 evidence supports the methodological value of exact-car control, but does not establish a complete same-car < same-team < different-team performance-control hierarchy." in syn)
check("C2 not presented as robust support", "Not robust" in c2_para and "POSITIVE_CONSISTENT" not in c2_para
      and cl[cl.claim.str.startswith("Same-team similarity")].status.iloc[0] == "PARTIALLY_SUPPORTED"
      and not cl[(cl.status == "SUPPORTED") & cl.claim.str.contains("different-team", case=False) & ~cl.claim.str.contains("same-team different-car")].shape[0])
check("Phase 4K CASE C not presented as zero teammate predictive value",
      "not prospectively identifiable" in syn and "does **not** establish that teammate movement lacks predictive value" in syn
      and all("does not mean" in line or "What this does not mean" in line for line in " ".join(docs.values()).splitlines()
              if re.search(r"teammate(s| movement)? (has|have) no (predictive )?value", line, re.I)))
check("Timing71 provenance wording correct", all(SY.TIMING71 in docs[n] for n in ["phase4l_final_scientific_synthesis.md", "phase4l_paper_integration_map.md", "phase4l_limitations.md"])
      and SY.TIMING71 == "third-party archived recording of the INDYCAR live timing feed" and not re.search(r"official (INDYCAR )?lap(-level)? data", " ".join(docs.values()), re.I))
check("2018-2022 not presented as equivalent lap-level evidence", "**not equivalent lap-level evidence**" in syn and "not** eight years of equivalent lap-level evidence" in syn
      and "2022 | session-level" in syn)
check("2025 not pooled with 2023-24", "2025 replication" in syn and "2025 is always analysed separately" in docs["phase4l_limitations.md"].replace("It is always analysed separately", "2025 is always analysed separately")
      and "pooled" not in re.sub(r"not pooled|never pooled", "", syn))
src = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4l_*.py") if not p.name.endswith("_checks.py"))
check("no new estimator/model/classifier in Phase 4L", not re.search(r"\.fit\(|lstsq|statsmodels|polyfit|LinearRegression|classify\(|speed_mph|bootstrap\(", src))
fr = pd.read_csv(O / "phase4k/phase4k_freeze_record.csv")
okp = all(sha(p) == h for p, h in zip(fr.path, fr.sha256)) and len(fr) == 451
okp &= git("diff", "--quiet", "c74e892", "--", "v4_team_normalized/output/phase4k").returncode == 0
okp &= all(git("diff", "--quiet", "c74e892", "--", str(p.relative_to(REPO))).returncode == 0 for p in (V4 / "scripts").glob("v4_phase4[a-k]_*.py"))
okp &= all(git("diff", "--quiet", "c74e892", "--", f"v4_team_normalized/{d}").returncode == 0 for d in ["evidence", "manual"]) and \
    all(git("diff", "--quiet", "c74e892", "--", str(p.relative_to(REPO))).returncode == 0 for p in O.glob("*.*"))
check("no Phase 1-4K artifact changed (451 hashes 4A-4J; 4K, evidence, registry, scripts vs c74e892)", okp)
man5 = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("FINAL_V2/V3 frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man5["files"] if f.get("exists")) and all(sha(pp) == h for pp, h in zip(r6m.path, r6m.sha256) if (REPO / pp).exists()))
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [x for x in diff if not x.startswith("v4_team_normalized/")]
check("paper unchanged; nothing outside V4 changed", not out, ";".join(out[:5]))
orig = REPO.parent / "indy500-point-in-time-decision-support"
check("original main unchanged (main == a8bb519; original worktree clean)", git("rev-parse", "--short", "main").stdout.strip() == "a8bb519"
      and git("status", "--porcelain", cwd=orig).stdout.strip() == "" and git("rev-parse", "--short", "HEAD", cwd=orig).stdout.strip() == "a8bb519")
M = pd.read_csv(OUT / "v4_final_manifest.csv")
msha = (OUT / "v4_final_manifest.sha256").read_text().split()[0]
okm = hashlib.sha256((OUT / "v4_final_manifest.csv").read_bytes()).hexdigest() == msha
okm &= all(sha(p) == h and (REPO / p).stat().st_size == s for p, h, s in zip(M.relative_path, M.sha256, M.size_bytes))
allf = {str(p.relative_to(REPO)) for p in V4.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store" and not p.name.endswith(".pkl")}
excl = {f"v4_team_normalized/output/phase4l/{n}" for n in ["v4_final_manifest.csv", "v4_final_manifest.sha256", "v4_freeze_report.md", "phase4l_checks_log.txt"]}
okm &= set(M.relative_path) == allf - excl and not M.relative_path.duplicated().any()
check("manifest self-consistent; all hashes and sizes reproduce; complete coverage", okm, f"{len(M)} files")
req = ["phase4l_final_scientific_synthesis.md", "phase4l_claims_matrix.csv", "phase4l_evidence_chain.md", "phase4l_paper_integration_map.md", "phase4l_future_data_requirements.md",
       "phase4l_limitations.md", "v4_final_manifest.csv", "v4_final_manifest.sha256", "v4_freeze_report.md", "phase4l_key_results_table.csv", "phase4l_phase_outcomes.csv"]
check("all required outputs present", all((OUT / f).exists() for f in req))
wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4l_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
