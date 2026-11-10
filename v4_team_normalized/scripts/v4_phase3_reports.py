"""V4 Phase 3 reporting: diagnostic figures, frozen-core overlap, and the two Markdown reports.

Reads only Phase 3 outputs, the Phase 2 registry/pair table, and (read-only) the frozen
R5.2 repeat analysis set. Descriptive; no model, threshold, or weight.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase3"
FIG = OUT / "figures"
WINDOWS = [5, 10, 15, 20, 30, 45, 60, 90, 120]

# reference palette (dataviz skill, light mode)
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
TIER_COLOR = {"CORE_2020_2024": BLUE, "REGIME_EXT_R6": ORANGE}
TIER_LABEL = {"CORE_2020_2024": "Core 2020–2024 (past-safe PTSC track, HRRR ambient)",
              "REGIME_EXT_R6": "R6 extension 2018/2019/2025 (interpolated PTSC)"}

plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})

def md(df, index=True):
    """Minimal GitHub Markdown table (avoids an extra 'tabulate' dependency)."""
    d = df.reset_index() if index else df
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    head = "| " + " | ".join(map(str, d.columns)) + " |"
    sep = "|" + "|".join("---" for _ in d.columns) + "|"
    return "\n".join([head, sep] + ["| " + " | ".join(fmt(v) for v in row) + " |" for row in d.itertuples(index=False)])


DIAG = "Diagnostic figure — descriptive; not a threshold choice or a publication result."


def save(fig, name):
    # reserve a bottom strip for the diagnostic footer and a top strip for the figure title
    fig.tight_layout(rect=(0, 0.06, 1, 0.9 if fig._suptitle is not None else 1))
    fig.text(0.01, 0.01, DIAG, fontsize=7, color=INK2)
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figures(c):
    m = c[c.measurable_candidate].copy()
    m["adt"] = m.delta_time_minutes.abs()
    tiers = [t for t in TIER_COLOR if t in set(m.tier)]

    # 1 distribution of time separation
    fig, axes = plt.subplots(1, len(tiers), figsize=(10, 3.4), sharey=True)
    for ax, t in zip(np.atleast_1d(axes), tiers):
        x = m[m.tier == t].adt
        ax.hist(x, bins=np.arange(0, x.max() + 15, 15), color=TIER_COLOR[t], edgecolor=SURFACE, linewidth=1)
        ax.set_title(f"{TIER_LABEL[t]}\n(n = {len(x)} measurable attempt pairs)", fontsize=8.5)
        ax.set_xlabel("|time separation| between teammate attempts (min)")
    np.atleast_1d(axes)[0].set_ylabel("attempt-pair candidates")
    fig.suptitle("1. Teammate attempt-pair time separation", x=0.01, ha="left", fontsize=11)
    save(fig, "fig1_teammate_time_separation_distribution.png")

    # 2 cumulative count vs max separation
    fig, ax = plt.subplots(figsize=(7.5, 4))
    grid = np.arange(0, 400, 1)
    for t in tiers:
        x = np.sort(m[m.tier == t].adt.values)
        ax.plot(grid, np.searchsorted(x, grid, side="right"), color=TIER_COLOR[t], lw=2, label=TIER_LABEL[t])
        for w in WINDOWS:
            ax.plot(w, np.searchsorted(x, w, side="right"), "o", ms=4, color=TIER_COLOR[t])
    for w in WINDOWS:
        ax.axvline(w, color=GRID, lw=0.8, zorder=0)
    ax.set_xlabel("maximum |time separation| allowed (min); markers at descriptive windows 5–120")
    ax.set_ylabel("measurable attempt-pair candidates")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("2. Candidate count vs maximum time separation", loc="left", fontsize=11)
    save(fig, "fig2_candidate_count_vs_max_time_separation.png")

    # 3/4 temperature separation vs time separation
    for num, col, lab, fname in [(3, "delta_track_temp_c", "|track-temperature difference| (°C)", "fig3_track_temp_diff_vs_time_separation.png"),
                                 (4, "delta_ambient_temp_c", "|ambient-temperature difference| (°C)", "fig4_ambient_temp_diff_vs_time_separation.png")]:
        fig, axes = plt.subplots(1, len(tiers), figsize=(10, 3.6), sharey=True)
        for ax, t in zip(np.atleast_1d(axes), tiers):
            s = m[(m.tier == t) & m[col].notna()]
            mixed = s.env_basis_consistent == False
            ax.scatter(s.adt[~mixed], s[col].abs()[~mixed], s=16, color=TIER_COLOR[t], edgecolor=SURFACE, linewidth=0.6,
                       label="same environment basis")
            if mixed.any():
                ax.scatter(s.adt[mixed], s[col].abs()[mixed], s=18, facecolor="none", edgecolor=INK2, linewidth=0.9,
                           label="mixed basis (flagged)")
            ax.set_title(f"{TIER_LABEL[t]}  (n = {len(s)})", fontsize=8.5)
            ax.set_xlabel("|time separation| (min)")
            ax.legend(fontsize=7, loc="upper left", framealpha=0.9, frameon=True, edgecolor=SURFACE)
        np.atleast_1d(axes)[0].set_ylabel(lab)
        fig.suptitle(f"{num}. {lab.split('|')[1].strip().capitalize()} vs time separation (measurable teammate pairs)",
                     x=0.01, ha="left", fontsize=11)
        save(fig, fname)

    # 5/6 availability heatmaps (year, team) x window
    def heat(group_col, fname, title, num):
        rows = []
        for (t, g), s in m.groupby(["tier", group_col]):
            rows.append([f"{'core' if t.startswith('CORE') else 'R6'} | {g}"] + [(s.adt <= w).sum() for w in WINDOWS] + [len(s)])
        h = pd.DataFrame(rows, columns=["row"] + [f"≤{w}" for w in WINDOWS] + ["all timed"]).set_index("row")
        fig, ax = plt.subplots(figsize=(9, 0.32 * len(h) + 1.4))
        vals = h.values.astype(float)
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", BLUE, "#0f3f7a"])
        ax.imshow(vals, aspect="auto", cmap=cmap, vmin=0, vmax=max(vals.max(), 1))
        for (i, k), v in np.ndenumerate(vals):
            ax.text(k, i, int(v), ha="center", va="center", fontsize=7.5, color="white" if v > vals.max() * 0.55 else INK)
        ax.set_xticks(range(len(h.columns)), h.columns)
        ax.set_yticks(range(len(h)), h.index)
        ax.grid(False)
        ax.set_xlabel("maximum |time separation| (min) — descriptive windows")
        ax.set_title(f"{num}. {title} (measurable attempt-pair candidates)", loc="left", fontsize=11)
        save(fig, fname)

    heat("year", "fig5_candidate_availability_by_year.png", "Candidate availability by year", 5)
    heat("canonical_engineering_team", "fig6_candidate_availability_by_team.png", "Candidate availability by canonical team", 6)


def frozen_overlap(j, c, n):
    r = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv", dtype={"car_number": str})
    core = r.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).copy()
    assert len(core) == 41
    team = {(y, car): t for y, car, t in zip(j.year, j.registry_car_number, j.canonical_engineering_team)}
    prim = {(y, car): p for y, car, p in zip(j.year, j.registry_car_number, j.primary_teammate_layer)}
    core["canonical_engineering_team"] = [team.get((y, car), "") for y, car in zip(core.year, core.car_number)]
    core["primary_teammate_layer"] = [prim.get((y, car), False) for y, car in zip(core.year, core.car_number)]
    m = c[c.measurable_candidate]
    ov = n[n.is_overall_nearest_teammate].set_index("attempt_id")
    rows = []
    for x in core.itertuples(index=False):
        tm = m[(m.year == x.year) & (m.canonical_engineering_team == x.canonical_engineering_team)]
        own = tm[(tm.car_A == x.car_number) | (tm.car_B == x.car_number)]
        rows.append(dict(transition_id=x.transition_id, year=x.year, car_number=x.car_number, driver_name=x.driver_name,
                         canonical_engineering_team=x.canonical_engineering_team, primary_teammate_layer=x.primary_teammate_layer,
                         team_year_measurable_teammate_pairs=len(tm), car_measurable_teammate_pairs=len(own),
                         before_nearest_teammate_abs_min=ov.abs_time_separation_min.get(x.before_attempt_id, np.nan),
                         after_nearest_teammate_abs_min=ov.abs_time_separation_min.get(x.after_attempt_id, np.nan)))
    fo = pd.DataFrame(rows)
    fo.to_csv(OUT / "frozen_same_car_overlap.csv", index=False)
    return fo


def qtable(df, scope_prefix):
    d = df[df.scope.str.startswith(scope_prefix)]
    cols = ["variable", "n", "q000", "q010", "q025", "q050", "q075", "q090", "q095", "q100"]
    return md(d[cols].round(2), index=False)


def reports(j, c, n, fo):
    qs = pd.read_csv(OUT / "comparability_summary.csv")
    ws = pd.read_csv(OUT / "comparability_window_counts.csv")
    by_y = pd.read_csv(OUT / "comparability_by_year.csv")
    by_t = pd.read_csv(OUT / "comparability_by_team.csv")
    pc = pd.read_csv(V4 / "output" / "v4_teammate_pair_changes.csv", dtype={"car_a": str, "car_b": str})
    strict = pc[pc.in_v4_strict]
    m = c[c.measurable_candidate]

    # ---------------- data-quality report ----------------
    g = j.groupby(["tier", "year"])
    cov = g.apply(lambda d: pd.Series({
        "attempts": len(d), "mapped": int((d.map_status == "MAPPED").sum()),
        "unmapped": int((d.map_status == "UNMAPPED").sum()), "ambiguous": int((d.map_status == "AMBIGUOUS").sum()),
        "primary_layer": int((d.primary_teammate_layer == True).sum()),
        "driver_car_mismatch": int((d.driver_car_consistent == False).sum()),
        "missing_timestamp": int(d.attempt_timestamp_utc.isna().sum()),
        "missing_four_lap_speed": int(d.four_lap_average_speed_mph.isna().sum()),
        "missing_track_temp": int(d.track_temp_c.isna().sum()), "missing_ambient_temp": int(d.ambient_temp_c.isna().sum()),
        "missing_solar": int(d.solar_shortwave_wm2.isna().sum()), "missing_wind": int(d.wind_speed_ms.isna().sum()),
        "complete_and_timed": int((d.complete_four_lap & d.attempt_timestamp_utc.notna()).sum()),
        "complete_timed_with_track_and_ambient": int((d.complete_four_lap & d.attempt_timestamp_utc.notna() & d.track_temp_c.notna() & d.ambient_temp_c.notna()).sum()),
    })).reset_index()
    cov.loc[len(cov)] = ["ALL", "ALL"] + cov.iloc[:, 2:].sum().tolist()
    miss_time = j[j.attempt_timestamp_utc.isna()].groupby(["tier", "year", "attempt_class"]).size().rename("attempts").reset_index()
    non_primary = j[(j.map_status == "MAPPED") & (j.primary_teammate_layer != True)][
        ["tier", "year", "car_number", "driver_name", "canonical_engineering_team", "relationship_type"]].drop_duplicates()
    non_primary = non_primary.assign(attempts=non_primary.apply(lambda r: int(((j.year == r.year) & (j.car_number == r.car_number)).sum()), axis=1))
    mism = j[j.driver_car_consistent == False][["tier", "year", "car_number", "driver_name", "registry_driver"]].drop_duplicates()
    tcls = j.groupby(["tier", "time_class"]).size().rename("attempts").reset_index()
    tb = j.groupby(["tier", "track_basis"]).size().rename("attempts").reset_index()
    ab = j.groupby(["tier", "ambient_basis"]).size().rename("attempts").reset_index()
    backup = j[j.map_method.fillna("").str.startswith("BACKUP")][["year", "car_number", "driver_name", "registry_car_number", "result_status", "four_lap_average_speed_mph"]]
    dq = f"""# V4 Phase 3 — Data-Quality Report (team registry ⨝ qualifying attempts)

Generated by `v4_team_normalized/scripts/v4_phase3_candidates.py` and `v4_phase3_reports.py`.
Descriptive audit only. No original dataset was modified; every input was read-only.

## Inputs and tiers

| Tier | Years | Attempt source | Timestamp source | Environment basis |
|---|---|---|---|---|
| `CORE_2020_2024` | 2020–2024 Day 1 | `r4/output/r4p1_attempt_four_lap_panel_v1.csv` (the canonical attempt panel, 329 rows) | r4p1 `time_point_utc` (recorder capture ≈ performance time) → R5.2 public-rescue times (`r5_2/manual/rescued_attempt_environment_states_v1.csv`, matched on year + car + exact speed) → r4p1 bounded-interval midpoint | **Same as the frozen same-car core.** Track = past-safe PTSC; ambient/solar/wind = issue-gated HRRR (`r5_1/.../day1_within_run_fade_physics_v1.csv`, then `weather/output/performance_context_features.csv`, then the rescue file). Interpolated PTSC is kept as secondary columns `ptsc_interp_*`. |
| `REGIME_EXT_R6` | 2018, 2019, 2025 Day 1 | `r6_regime_extension/.../regime_official_attempt_inventory_v3.csv` (official results parse) | Timing71 lap-matched attempt midpoint; only `EXACT_OR_NEAR_EXACT` matches with a resolved timestamp are accepted | Linearly interpolated PTSC (`r6_ptsc_2019_2025_canonical_v1.csv`); bracket ≤ 30 min; no extrapolation; no HRRR; wind in raw PTSC units |

The two tiers belong to different technical regimes and use different environment bases, so they are **never pooled** in any summary.

Verification checks:
- The frozen-core track and ambient inputs were reproduced exactly: 69/69 non-rescued endpoints match `r5_1` to within 1e-6.
- Every frozen-core timestamp equals r4p1 `time_point_utc`.

## 3.2 Join verification

{md(cov, index=False)}

- **Unmapped attempts: 0. Ambiguous mappings: 0. Duplicate joins: 0** (`attempt_id` is unique, and each attempt matches exactly one registry row on exact year + car number).
- **Backup-chassis mapping (explicit rule, flagged):** 2019 #5T James Hinchcliffe is the backup car on the #5 Arrow SPM entry. It maps to entry #5 with `map_method = BACKUP_T_CAR_TO_SAME_ENTRY_WITH_SURNAME`. Pairing uses the entry car number, so #5T is never compared with #5.

{md(backup, index=False)}

- **Driver/car mismatches (kept, flagged, not dropped):**

{md(mism, index=False)}

  The name "ZacharyHarvey, Jack" is a text-merge artefact of the R6 PDF parse. Car #60 is Jack Harvey in the 2018 official entry list and the Phase 1 registry.

- **Mapped but outside the primary teammate layer:** the technical-partnership entries (Phase 1–2 decision 2). They are retained in the join and absent from the candidates. One-car teams (e.g. 2020 DragonSpeed) stay in the primary layer but produce no pairs.

{md(non_primary, index=False)}

### Missing timestamps by attempt class

{md(miss_time, index=False)}

Why timestamps are missing:
- **Core tier:** no attempt-level time exists in the existing reconstruction, because the r4p1 time-evidence class is `UNKNOWN`. 2022 has only 5 bounded or point times, since recorder data was unavailable and weather stops interrupted the day. 2023 and 2024 recorder capture covers only part of each session.
- **R6 tier:** Timing71 archives cover only some cars or periods. 2018 has only 12 matched attempts (R6 marks 2018 `PARTIAL_SOURCE_COVERAGE`). 20 matches were rejected on quality (`WEAK`, `PLAUSIBLE` or `UNRESOLVED`); their candidate times are kept in `rejected_time_candidate_utc`.

### Timestamp classes

{md(tcls, index=False)}

The 6 bounded-interval midpoints carry `time_half_width_min`. Every pair records `time_uncertainty_min` (the sum of both half-widths).

### Environment basis

{md(tb, index=False)}

{md(ab, index=False)}

- **Missing environment:** 2022 has none, because it has no performance-grade timing. 2018 has no PTSC archive in R6. Other gaps are untimed attempts, plus one 2025 attempt after the last PTSC observation, which is not extrapolated.
- **Mixed bases:** 35 core measurable pairs mix environment bases (past-safe vs realized-interpolated track, or rescue-matched vs issue-gated HRRR). They are flagged `env_basis_consistent = False`.
- **Wind:** the core uses HRRR 10 m wind (m/s). R6 uses raw PTSC wind, whose units are unverified. Wind separations are therefore tier-specific.
- **Solar:** core only (HRRR downward shortwave).

## Weather observation timestamps

- `track_obs_time_utc`: the PTSC observation used. For R6 this is the bracketing pair `before|after`.
- `hrrr_valid_before_utc` / `hrrr_valid_after_utc`: the HRRR valid times that bracket the attempt (core).

## Session / track-state evidence available (§3.7)

| Year | Evidence in the existing reconstruction | Pair classification used |
|---|---|---|
| 2022 | Weather stop 18:14–19:34 UTC; second stop ≈20:00–20:02 UTC, then session called 20:50 UTC (secondary sources, preserved from `weather/output/chronology_rescue_2022_weather_interruption_windows_v1.csv`) | same segment / crosses interruption / bounded time straddles a stop |
| 2020 | 7m15s recorder **data** gap 18:35:15–18:42:30 UTC (not a track interruption) | `SAME_SESSION_NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION` + `data_coverage_note` |
| 2023 | Terminal ≈58-minute recorder data gap (untimed) | as above |
| 2021, 2024, 2018, 2019, 2025 | No interruption record (2024: session start/cutoff only) | `SAME_SESSION_NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION` |

**Absence of an interruption record is not evidence of uninterrupted running.** Session equivalence was not inferred from the calendar date. Every attempt comes from a Day 1 session identified by `session_id`, and every timed attempt's local date matches that year's Day 1 date.
"""
    (OUT / "phase3_data_quality_report.md").write_text(dq)

    # ---------------- comparability report ----------------
    rel_years = strict[strict.year.isin(j.year.unique())]
    rel_with_any = c.relationship_pair_id.nunique()
    rel_with_meas = m.relationship_pair_id.nunique()
    abc = pd.DataFrame([
        dict(level="A. organisational teammate relationships (Phase 2 strict, 2018–2025)", variable="relationship_pair",
             count=len(strict)),
        dict(level="A′. …with ≥1 attempt-pair candidate in the joined attempt data", variable="relationship_pair_id", count=rel_with_any),
        dict(level="A″. …with ≥1 measurable attempt-pair candidate", variable="relationship_pair_id", count=rel_with_meas),
        dict(level="B. all possible cross-car attempt-to-attempt candidates", variable="attempt_pair_candidate", count=len(c)),
        dict(level="B′. measurable candidates (both complete four-lap + both timed)", variable="measurable_candidate", count=len(m)),
        dict(level="C. scientifically comparable observations", variable="comparable_observation",
             count="NOT DEFINED — requires Phase 4 eligibility rules"),
    ])
    by_tier = c.groupby("tier").agg(all_candidates=("attempt_A", "size"), both_complete=("both_complete_four_lap", "sum"),
                                     both_timed=("both_timed", "sum"), measurable=("measurable_candidate", "sum"),
                                     relationship_pairs=("relationship_pair_id", "nunique")).reset_index()
    rel_by_year = strict.groupby("year").size().rename("A_relationship_pairs").to_frame().join(
        c.groupby("year").relationship_pair_id.nunique().rename("A′_with_candidates")).join(
        m.groupby("year").relationship_pair_id.nunique().rename("A″_with_measurable")).join(
        c.groupby("year").size().rename("B_attempt_pairs")).join(m.groupby("year").size().rename("B′_measurable")).fillna(0).astype(int).reset_index()

    wtab = ws.pivot_table(index="max_time_separation_min", columns="scope",
                          values=["attempt_pair_candidates", "distinct_relationship_pairs", "distinct_attempts_involved", "distinct_team_years"]).astype(int)
    wtab.columns = [f"{s.split('|')[0].replace('_2020_2024', '').replace('REGIME_EXT_R6', 'R6')}: {v}" for v, s in wtab.columns]
    wtab = wtab[[c_ for c_ in wtab.columns if c_.startswith("CORE")] + [c_ for c_ in wtab.columns if c_.startswith("R6")]]

    yw = by_y[by_y.table == "WINDOW_COUNTS"].pivot_table(index=["tier", "year"], columns="max_time_separation_min",
                                                        values="attempt_pair_candidates").astype(int)
    yw.columns = [f"≤{int(x)}" for x in yw.columns]
    yq = by_y[(by_y.table == "QUANTILES") & (by_y.variable == "abs_time_min")][["tier", "year", "n", "q010", "q025", "q050", "q075", "q090"]].round(1)
    yenv = by_y[(by_y.table == "QUANTILES") & (by_y.variable.isin(["abs_track_temp_c", "abs_ambient_temp_c"]))][["tier", "year", "variable", "n", "q025", "q050", "q075", "q090"]].round(2)
    tw = by_t[by_t.table == "WINDOW_COUNTS"].pivot_table(index=["tier", "canonical_engineering_team"], columns="max_time_separation_min",
                                                        values="attempt_pair_candidates").astype(int)
    tw.columns = [f"≤{int(x)}" for x in tw.columns]

    ovn = n[n.is_overall_nearest_teammate]
    near_counts = ovn.groupby("tier").agg(attempts_with_a_timed_teammate=("attempt_id", "size"),
                                         distinct_nearest_attempt_pairs=("attempt_pair_key", "nunique"),
                                         mutual_nearest_pairs=("overall_nearest_is_mutual", lambda s: int(s.sum() // 2))).reset_index()
    near_w = pd.DataFrame([dict(tier=t, **{f"≤{w}": int((g.abs_time_separation_min <= w).sum()) for w in WINDOWS})
                           for t, g in ovn.groupby("tier")])
    near_w_pairs = pd.DataFrame([dict(tier=t, **{f"≤{w}": int(g[g.abs_time_separation_min <= w].attempt_pair_key.nunique()) for w in WINDOWS})
                                 for t, g in ovn.groupby("tier")])

    fo_year = fo.groupby("year").agg(frozen_transitions=("transition_id", "size"), teams=("canonical_engineering_team", "nunique"),
                                     transitions_in_team_years_with_measurable_teammate_pairs=("team_year_measurable_teammate_pairs", lambda s: int((s > 0).sum())),
                                     transitions_whose_car_has_measurable_teammate_pairs=("car_measurable_teammate_pairs", lambda s: int((s > 0).sum()))).reset_index()
    fo_team = fo.groupby(["year", "canonical_engineering_team"]).agg(frozen_transitions=("transition_id", "size"),
                                                                     primary_layer=("primary_teammate_layer", "first"),
                                                                     team_year_measurable_pairs=("team_year_measurable_teammate_pairs", "first")).reset_index()
    fo_near = fo[["before_nearest_teammate_abs_min", "after_nearest_teammate_abs_min"]]
    both_ep = fo_near.notna().all(axis=1)
    fo_near_desc = pd.DataFrame([dict(endpoints="before", with_timed_teammate=int(fo_near.iloc[:, 0].notna().sum()), median_min=round(fo_near.iloc[:, 0].median(), 1)),
                                 dict(endpoints="after", with_timed_teammate=int(fo_near.iloc[:, 1].notna().sum()), median_min=round(fo_near.iloc[:, 1].median(), 1)),
                                 dict(endpoints="both endpoints", with_timed_teammate=int(both_ep.sum()), median_min=np.nan)])
    fo_near_w = pd.DataFrame([dict(endpoint=e, **{f"≤{w}": int((fo_near[col] <= w).sum()) for w in WINDOWS})
                              for e, col in [("before", "before_nearest_teammate_abs_min"), ("after", "after_nearest_teammate_abs_min")]])

    core_m = m[m.tier == "CORE_2020_2024"]
    cr = f"""# V4 Phase 3 — Teammate Comparability Report

**Status:** candidate construction and comparability design only.
- No model was fitted, no coefficient estimated, and no weight assigned.
- No eligibility threshold was chosen. The time windows below are descriptive sensitivity counts.
- `beta_track` and `beta_ambient` are untouched. Teammate observations were not combined with the frozen 41 same-car transitions.

## Terminology (§3.4)

| Level | Variable | Meaning |
|---|---|---|
| A | `relationship_pair` / `relationship_pair_id` | An organisational teammate relationship: two entries of one canonical engineering team in one year (Phase 2 strict layer). |
| B | `attempt_pair_candidate` (one row in `teammate_attempt_candidates.csv`) | Any cross-car pair of qualifying attempts within one year × canonical team. `measurable_candidate` = both attempts complete over four laps and both timed. |
| C | `comparable_observation` | **Not yet defined.** It requires the Phase 4 eligibility rules. |

{md(abc, index=False)}

All 313 Phase 2 relationship pairs have at least one attempt-pair candidate. Only 148 have at least one *measurable* candidate: the rest lose it to missing timestamps (above all in 2018, 2022, 2023 and 2024) or to incomplete attempts.

{md(by_tier, index=False)}

{md(rel_by_year, index=False)}

## Sign / order convention

- **A** is the earlier attempt by assembled timestamp; ties go to the lower car sort key, then `attempt_id`. If either timestamp is missing, A is the lower car sort key.
- Every `delta_* = value_B − value_A`, so `delta_time_minutes ≥ 0` for timed pairs (checked: 0 negative).
- Speed, temperature, solar and wind deltas follow the same B − A convention.

## §3.5 Distributions of absolute separations — measurable attempt pairs

### Core 2020–2024

{qtable(qs, 'CORE_2020_2024|ALL_MEASURABLE')}

### R6 extension (2018/2019/2025; different regime and environment basis)

{qtable(qs, 'REGIME_EXT_R6|ALL_MEASURABLE')}

Sensitivity check: restricting to point timestamps only (dropping bounded midpoints) changes the core n from {len(core_m)} to {int((core_m.time_uncertainty_min.fillna(0) == 0).sum())}. See `comparability_summary.csv`, scope `POINT_TIMES_ONLY`.

**Resolution caveat:** past-safe PTSC track temperature is a step function on a 15-minute grid. Near-simultaneous pairs therefore often show exactly 0 °C track difference; that is a measurement-resolution artefact, not evidence of identical track state.

### Time separation by year (min)

{md(yq, index=False)}

### Environmental separation by year

{md(yenv, index=False)}

## Descriptive window counts (no threshold selected)

{md(wtab)}

### By year (measurable attempt-pair candidates)

{md(yw)}

### By canonical team

{md(tw)}

## §3.6 Nearest-teammate structure (non-duplicative view)

For each complete, timed attempt in the primary layer, `nearest_teammate_candidates.csv` records:
- the nearest attempt of each teammate car;
- a flag marking the overall nearest one.

{md(near_counts, index=False)}

### Overall nearest-teammate separations

{qtable(qs, 'CORE_2020_2024|OVERALL_NEAREST')}

{qtable(qs, 'REGIME_EXT_R6|OVERALL_NEAREST')}

### Attempts whose overall nearest teammate attempt lies within each window

{md(near_w, index=False)}

Distinct nearest attempt pairs within each window (de-duplicated when two attempts are each other's nearest):

{md(near_w_pairs, index=False)}

These are not yet controls.

## §3.7 Same-session / track-state structure (measurable pairs)

{md(m.groupby(['tier', 'session_state']).size().rename('pairs').reset_index(), index=False)}

- All measurable pairs are within one Day 1 `session_id`.
- **2022 is the only year with a reconstructed interruption structure,** but only 1 measurable 2022 pair exists (same known segment).
- For all other years, "no interruption record" is a limitation of the reconstruction, not a verified uninterrupted track state.
- {int(m.data_coverage_note.fillna('').astype(str).str.len().gt(0).sum())} core 2020 measurable pairs span the 7m15s recorder data gap. That gap is a data note, not a track interruption.

## §3.8 What the teammate layer does and does not control

- **Controls** (approximately): the team's vehicle platform, engineering group, engine supplier and aero package.
- **Does not control:** setup, driver, tyre preparation/state, car-specific condition, operational execution or run plan.

Raw teammate speed differences therefore mix environment with these car/driver-specific effects. They are **not** environmental effects. The quantities above describe only how contemporaneous the cross-car evidence is.

## §3.9 Overlap with frozen same-car evidence (frozen set not modified)

The frozen 41 transitions come from years {sorted(fo.year.unique().tolist())}.

{md(fo_year, index=False)}

{md(fo_team, index=False)}

Frozen endpoints with an overall-nearest timed teammate attempt:

{md(fo_near_desc, index=False)}

{md(fo_near_w, index=False)}

Per-transition detail: `frozen_same_car_overlap.csv`.

## Assessment for Phase 4 (§3.11 items 10–15)

**Strongest years for contemporaneous teammate evidence**
- Core: **2021** ({int(yw.loc[('CORE_2020_2024', 2021)]['≤30'])} pairs ≤30 min; {int(yw.loc[('CORE_2020_2024', 2021)]['≤60'])} ≤60 min), then **2020** and **2023**.
- R6: **2025** ({int(yw.loc[('REGIME_EXT_R6', 2025)]['≤60'])} ≤60 min).

**Weakest years**
- **2022:** 1 measurable pair and no environment. The core data cannot support the teammate layer this year.
- **2024:** {int((m.year == 2024).sum())} measurable pairs; only {int(((j.year == 2024) & j.complete_four_lap & j.attempt_timestamp_utc.notna()).sum())} timed complete attempts.
- **2018:** {int((m.year == 2018).sum())} measurable pairs; no PTSC.

**Strongest teams**
- Core, by measurable pairs ≤60 min: {', '.join(f'**{t}** ({int(v)})' for t, v in tw.loc['CORE_2020_2024']['≤60'].sort_values(ascending=False).head(4).items())}.
- The other core teams contribute {int(tw.loc['CORE_2020_2024']['≤60'].sort_values(ascending=False).iloc[4:].min())}–{int(tw.loc['CORE_2020_2024']['≤60'].sort_values(ascending=False).iloc[4:].max())} pairs within 60 min each.

**Missing-data limitations**
- Only {int((j.tier.eq('CORE_2020_2024') & j.complete_four_lap & j.attempt_timestamp_utc.notna()).sum())} of {int((j.tier.eq('CORE_2020_2024') & j.complete_four_lap).sum())} complete core attempts are timed. Timing, not team structure, limits the teammate layer.
- Session interruptions are reconstructed only for 2022.
- Environment bases differ across tiers, and {int((m.env_basis_consistent.astype(str) == 'False').sum())} core measurable pairs mix bases.
- Past-safe track temperature is quantised at 15 minutes.
- R6 wind units are unverified. There is no solar data outside the core.

**Sufficiency (descriptive judgement, not a threshold decision)**
- Enough contemporaneous core evidence exists to design a formal teammate comparison: {int(ws[(ws.scope.str.startswith('CORE')) & (ws.max_time_separation_min == 30)].attempt_pair_candidates.iloc[0])} measurable pairs within 30 min and {int(ws[(ws.scope.str.startswith('CORE')) & (ws.max_time_separation_min == 60)].attempt_pair_candidates.iloc[0])} within 60 min. The ≤60-min pairs span {int(ws[(ws.scope.str.startswith('CORE')) & (ws.max_time_separation_min == 60)].distinct_relationship_pairs.iloc[0])} relationship pairs and {int(ws[(ws.scope.str.startswith('CORE')) & (ws.max_time_separation_min == 60)].distinct_team_years.iloc[0])} team-years.
- That is the same order of magnitude as the 41-transition same-car core.
- The evidence is concentrated in 2020, 2021 and 2023 and in four teams.
- Multiple attempt pairs share the same relationship pair and attempts. Any Phase 4 design must treat these as dependent, for example by clustering on relationship pair and attempt or by using the nearest-teammate view.

## Files

`team_attempt_join.csv`, `teammate_attempt_candidates.csv`, `nearest_teammate_candidates.csv`, `comparability_summary.csv`, `comparability_window_counts.csv`, `comparability_by_year.csv`, `comparability_by_team.csv`, `frozen_same_car_overlap.csv`, `phase3_data_quality_report.md`, `phase3_comparability_report.md`, `figures/fig1…fig6*.png`.
"""
    (OUT / "phase3_comparability_report.md").write_text(cr)
    return cov, abc, fo_year


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    j = pd.read_csv(OUT / "team_attempt_join.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    j["attempt_timestamp_utc"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")
    c = pd.read_csv(OUT / "teammate_attempt_candidates.csv", dtype={"car_A": str, "car_B": str}, low_memory=False)
    n = pd.read_csv(OUT / "nearest_teammate_candidates.csv", dtype={"car_number": str, "teammate_car": str}, low_memory=False)
    figures(c)
    fo = frozen_overlap(j, c, n)
    cov, abc, fo_year = reports(j, c, n, fo)
    print(cov.to_string()); print(abc.to_string()); print(fo_year.to_string())


if __name__ == "__main__":
    main()
