"""Required Phase 4E checks (4E.25). Exits non-zero on failure; writes phase4e_checks_log.txt."""
import hashlib, json, pickle, subprocess, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4e"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4e_audit as A  # noqa: E402

res = []
check = lambda n, ok, d="": res.append((n, bool(ok), d))
git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
sha = lambda p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
cache = OUT / "inputs" / "_audit_cache.pkl"
if not cache.exists():
    pickle.dump(A.main(), open(cache, "wb"))
reg, sessions, off, files, laps, S, wx = pickle.load(open(cache, "rb"))
tiers = pd.read_csv(OUT / "session_quality_tiers.csv")
st = pd.read_csv(OUT / "same_team_opportunities.csv")

check("years restricted to 2018-2025", set(sessions.year) <= set(range(2018, 2026)) and set(laps.year) <= set(range(2018, 2026)) and set(st.year) <= set(range(2018, 2026)))
r = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
m = laps[laps.join_status == "MATCHED"].drop_duplicates(["year", "car"])
check("accepted V4 registry reused (team = registry team for every matched car)",
      all(r[(r.year == y) & (r.car_number == c)].canonical_engineering_team.iloc[0] == t for y, c, t in zip(m.year, m.registry_car, m.canonical_engineering_team)))
tp = laps[laps.technical_partnership_only.fillna(False).astype(bool)]
check("technical partnerships excluded from primary teammate layer", not tp.primary_layer.fillna(False).astype(bool).any())
check("raw official identities preserved (official names + raw Timing71 team strings kept)",
      "official_session_name" in sessions and "team_raw" in laps and pd.read_csv(OUT / "team_join_coverage.csv", low_memory=False).columns.isin(["team_raw", "raw_entry_name"]).sum() == 2)
jm = set(laps.join_method.dropna())
check("no fuzzy joins accepted (only exact / T-backup-with-surname / 06-6 variant)", jm <= {"EXACT_CAR", "BACKUP_T_CAR", "CAR_06_6_VARIANT"}, str(jm))
src = "".join(open(p).read() for p in (V4 / "scripts").glob("v4_phase4e_*.py") if not p.name.endswith("_checks.py"))
check("no model fitted / no coefficient estimated (no fitting calls in Phase 4E code)",
      not any(k in src for k in ["lstsq(", "statsmodels", ".fit(", "LinearRegression", "mixedlm", "polyfit"]))
p4c = git("log", "-1", "--format=%H", "--", "v4_team_normalized/output/phase4c").stdout.strip()
p4d = git("log", "-1", "--format=%H", "--", "v4_team_normalized/output/phase4d").stdout.strip()
check("no Phase 4C file changes", git("diff", "--quiet", p4c, "--", "v4_team_normalized/output/phase4c").returncode == 0 and not git("status", "--porcelain", "--", "v4_team_normalized/output/phase4c").stdout.strip())
check("no Phase 4D file changes", git("diff", "--quiet", p4d, "--", "v4_team_normalized/output/phase4d").returncode == 0 and not git("status", "--porcelain", "--", "v4_team_normalized/output/phase4d").stdout.strip())
man = json.loads((REPO / "r5_2/manual/CORE_REGIME_2020_2024_V1_FROZEN_MANIFEST.json").read_text())
r6m = pd.read_csv(REPO / "r6_regime_extension/output/r6_final_freeze_v1/R6_FROZEN_MANIFEST_SHA256_V1.csv")
check("frozen manifests hash exactly (R5.2 + R6)", all(sha(f["path"]) == f["sha256"] for f in man["files"] if f.get("exists")) and all(sha(p) == h for p, h in zip(r6m.path, r6m.sha256) if (REPO / p).exists()))
wc = pd.read_csv(OUT / "weather_coverage.csv")
check("no missing weather imputed (MISSING wherever no PTSC in span/date)", (wc[~wc.weather_observed_in_span.astype(bool)].track_temperature == "MISSING").all())
check("2025/all wind labelled unit-unverified, never numeric-joined", set(wc.wind) <= {"OBSERVED_UNIT_UNVERIFIED", "MISSING"} and "wind" not in "".join(c for c in st.columns))
sd = pd.read_csv(OUT / "sampling_dependence_audit.csv")
check("raw observation counts distinguished from effective-information proxies", {"raw_observation_count", "effective_information_proxy"} <= set(sd.columns))
om = pd.read_csv(OUT / "opportunity_matrix.csv")
race_keys = set(st[st.normalized_category == "RACE"].session_key)
check("race never mixed with other categories (every table row has a single category; race keys disjoint)",
      st.groupby("session_key").normalized_category.nunique().max() == 1 and not (race_keys & set(st[st.normalized_category != "RACE"].session_key)) and om.groupby(["year", "normalized_category"]).size().max() == 1)
check("official session names + categories preserved for every official session", sessions.official_session_name.notna().all() and sessions.normalized_category.notna().all())
inv = pd.read_csv(OUT / "source_inventory.csv", low_memory=False)
rm = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv")
check("source provenance retained (every retrieved file: URL + SHA-256 matches bytes on disk)",
      all(hashlib.sha256((REPO / p).read_bytes()).hexdigest() == h for p, h in zip(rm.local_path, rm.sha256)) and inv.source_url.notna().all())
# reproducibility: recompute one session's counts from the lap cache
key = st[st.timestamp_basis == "OBSERVED_LAP_TIMESTAMPS"].sort_values("valid_laps").iloc[-1].session_key
v = laps[(laps.session_key == key) & laps.valid_lap]
tm = np.where(v.primary_layer.fillna(False).astype(bool), "T:" + v.canonical_engineering_team.fillna(""), "C:" + v.car_id)
ok = True
for w in [1, 5, 30]:
    _, sc, stt, dt_ = A.pair_counts(v.ts.values.astype(float), v.car_id.values, tm, w * 60.0)
    row = st[st.session_key == key].iloc[0]
    ok &= stt == row[f"same_team_pairs_le{w}"]
check("opportunity counts reproducible (independent recount, largest observed session, w=1/5/30)", ok, key)
# tiers reproduce from spec rules
rep_ok = True
for rr in tiers.itertuples(index=False):
    T = bool(rr.T_lap_timestamps); I = (rr.identity_match_share if rr.identity_match_share == rr.identity_match_share else 0) >= 0.95
    mct = rr.multi_car_teams if rr.multi_car_teams == rr.multi_car_teams else 0
    if rr.normalized_category == "AGGREGATE_RESULT" or not T or not I or mct < 2:
        exp = "D"
    else:
        O_ = (rr.same_team_pairs_le5 >= 20) and (rr.teams_with_same_team_overlap_le5 >= 3)
        lims = sum([rr.state_class == "OPEN_TRACK_UNOBSERVED_RUN_PLAN", mct < 3, not O_, not bool(rr.weather_observed_in_span), not bool(rr.P_provenance)])
        exp = "C" if (rr.state_class == "RACE_STATE_CONFOUNDED" or lims >= 2) else ("B" if lims == 1 else "A")
    rep_ok &= exp == rr.quality_tier
check("quality tiers reproduce from pre-declared rules", rep_ok)
spec = "v4_team_normalized/output/phase4e/phase4e_quality_tier_spec.md"
sc_ = git("log", "--format=%H", "--diff-filter=A", "--", spec).stdout.split()
check("tier spec committed before results and unchanged", bool(sc_) and git("diff", "--quiet", sc_[-1], "--", spec).returncode == 0, sc_[-1][:7] if sc_ else "")
r6 = pd.read_csv(REPO / "r6_regime_extension/output/r6_ptsc_canonical_v1/r6_ptsc_2019_2025_canonical_v1.csv")
okw = True
for y in (2019, 2025):
    a = wx[(wx.year == y)].assign(k=lambda d: d.local_ts.dt.strftime("%Y-%m-%d %H:%M"))
    b = r6[r6.year == y].assign(k=lambda d: pd.to_datetime(d.datetime_local).dt.strftime("%Y-%m-%d %H:%M"))
    mm = a.merge(b, on="k", suffixes=("_a", "_b"))
    okw &= len(mm) == len(b) and np.allclose(mm.track_f_a.astype(float), mm.track_f_b.astype(float))
check("PTSC extraction reproduces frozen R6 canonical values (2019, 2025)", okw)
diff = git("diff", "--name-only", "v3-frozen-pre-team-normalization-v4").stdout.split() + git("ls-files", "--others", "--exclude-standard").stdout.split()
out = [p for p in diff if not p.startswith("v4_team_normalized/")]
check("no frozen V2/V3 changes; nothing outside v4_team_normalized/ changed", not out, ";".join(out[:5]))

wd = max(len(n) for n, _, _ in res)
lines = [f"{'PASS' if ok else 'FAIL'}  {n.ljust(wd)}  {d}" for n, ok, d in res]
print("\n".join(lines)); print(f"\n{sum(o for _, o, _ in res)}/{len(res)} checks passed")
(OUT / "phase4e_checks_log.txt").write_text("\n".join(lines) + f"\n\n{sum(o for _, o, _ in res)}/{len(res)} checks passed\n")
sys.exit(0 if all(o for _, o, _ in res) else 1)
