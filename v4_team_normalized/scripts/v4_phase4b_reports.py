"""V4 Phase 4B: timeline figures, cross-team summary figures, priority-case selection and reports.

Exploratory and descriptive only. No model is fitted. Any connecting line between attempts is a
labelled visual connection between discrete observations, never an interpolation.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "v4_team_normalized" / "output" / "phase4b"
FIG = OUT / "figures"
LOCAL_TZ = "America/Indiana/Indianapolis"

CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "h"]
BLUE, ORANGE = CAT[0], CAT[1]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "legend.frameon": False})
DIAG = "Exploratory diagnostic — discrete attempts; dotted lines are visual connections only (no interpolation); no model fitted."
ERA_SHORT = {"ERA_A_PRE_AEROSCREEN_EXT": "Era A 2018–19 (pre-Aeroscreen ext.)", "ERA_B_FROZEN_REFERENCE": "Era B 2020–24 (frozen reference)",
             "ERA_C_HYBRID_EXTERNAL": "Era C 2025 (hybrid external)"}
INTERRUPTIONS = {2022: [("2022-05-21T18:14:00Z", "2022-05-21T19:34:00Z"), ("2022-05-21T20:00:00Z", "2022-05-21T20:50:00Z")]}
DATA_GAPS = {2020: [("2020-08-15T18:35:15Z", "2020-08-15T18:42:30Z")]}


def md(df, index=False):
    d = df.reset_index() if index else df
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(fmt(v) for v in row) + " |" for row in d.itertuples(index=False)])


def car_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


def save(fig, path, top=0.9):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.5, color=INK2)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ per team-year timeline figure
def timeline_figure(g_all, y, team, mode, path, samp_row, conf_row, wx_row, note=""):
    g = g_all[g_all.on_performance_timeline].sort_values("attempt_timestamp_utc")
    cars = sorted(g.registry_car_number.unique(), key=car_key)
    style = {c: (CAT[i % 8], MARKERS[i % 8]) for i, c in enumerate(cars)}
    tloc = g.attempt_timestamp_utc.dt.tz_convert(LOCAL_TZ).dt.tz_localize(None)
    panels = {"raw": ["four_lap_average_speed_mph"], "centered": ["speed_minus_car_mean", "speed_minus_car_median"]}[mode]
    ylab = {"four_lap_average_speed_mph": "four-lap average (mph)", "speed_minus_car_mean": "− car mean (mph)",
            "speed_minus_car_median": "− car median (mph)"}
    fig, axes = plt.subplots(len(panels) + 1, 1, figsize=(10, 2.7 * len(panels) + 2.3), sharex=True,
                             gridspec_kw=dict(height_ratios=[3] * len(panels) + [1.6]))
    for ax, col in zip(axes[:-1], panels):
        for c in cars:
            h = g[g.registry_car_number == c]
            col_, mk = style[c]
            x = tloc[h.index]
            if len(h) >= 2:
                ax.plot(x, h[col], ":", color=col_, lw=1, alpha=0.7)
            informative = h.centering_informative.astype(bool) if mode == "centered" else pd.Series(True, index=h.index)
            if informative.any():
                ax.scatter(x[informative], h[col][informative], s=46, marker=mk, color=col_, edgecolor=SURFACE, linewidth=0.8, zorder=3,
                           label=f"#{c} {h.registry_driver.iloc[0]} (n={len(h)})")
            if (~informative).any():
                ax.scatter(x[~informative], h[col][~informative], s=46, marker=mk, facecolor="none", edgecolor=col_, linewidth=1.1, zorder=3,
                           label=f"#{c} {h.registry_driver.iloc[0]} (n=1: centered ≡ 0)")
            fz = h[h.is_frozen_core_attempt.astype(bool)]
            if len(fz):
                ax.scatter(tloc[fz.index], fz[col], s=150, facecolor="none", edgecolor=INK, linewidth=1.2, zorder=4)
        if mode == "centered":
            ax.axhline(0, color=INK2, lw=0.8)
        ax.set_ylabel(ylab[col])
    axes[0].scatter([], [], s=150, facecolor="none", edgecolor=INK, label="frozen same-car core attempt")
    axes[0].plot([], [], ":", color=INK2, label="visual connection only (not interpolation)")
    axes[0].legend(fontsize=6.8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    ax = axes[-1]
    tr = g.dropna(subset=["track_temp_c"])
    am = g.dropna(subset=["ambient_temp_c"])
    ax.scatter(tloc[tr.index], tr.track_temp_c, s=18, color=INK, marker="o", label="track temp at attempt (°C)")
    ax.scatter(tloc[am.index], am.ambient_temp_c, s=18, color=INK2, marker="x", label="ambient temp at attempt (°C)")
    if len(tr) == 0 and len(am) == 0:
        ax.text(0.5, 0.5, "no weather available for these attempts (not manufactured)", transform=ax.transAxes, ha="center", color=INK2)
    ax.set_ylabel("°C")
    ax.legend(fontsize=6.8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    for a in axes:
        for lo, hi in INTERRUPTIONS.get(y, []):
            a.axvspan(pd.Timestamp(lo).tz_convert(LOCAL_TZ).tz_localize(None), pd.Timestamp(hi).tz_convert(LOCAL_TZ).tz_localize(None),
                      color=GRID, alpha=0.8, zorder=0)
        for lo, hi in DATA_GAPS.get(y, []):
            a.axvspan(pd.Timestamp(lo).tz_convert(LOCAL_TZ).tz_localize(None), pd.Timestamp(hi).tz_convert(LOCAL_TZ).tz_localize(None),
                      color="#f3e6d6", alpha=0.9, zorder=0)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.set_xlabel("local time (Indianapolis), Day 1 qualifying" + ("; grey = known weather stops" if y in INTERRUPTIONS else "")
                  + ("; tan = recorder data gap" if y in DATA_GAPS else ""))
    untimed = int((~g_all.on_performance_timeline).sum())
    sub = (f"{ERA_SHORT[g_all.era.iloc[0]]} | {len(g)} timed complete attempts, {len(cars)} cars; {untimed} other primary attempts not placeable "
           f"(untimed or incomplete) | median gap {samp_row.median_gap_min:.0f} min | car/time confounding: {conf_row.confounding_severity} | "
           f"weather: {str(wx_row['flags']).replace('|', ', ')}")
    fig.suptitle(f"{y} {team} — {'raw speed' if mode == 'raw' else 'within-car centered speed (descriptive location shift, not adjustment)'}"
                 + (f"\n[{note}]" if note else ""), x=0.01, y=0.995, ha="left", va="top", fontsize=10.5)
    fig.tight_layout(rect=(0, 0.05, 1, 0.84 if note else 0.87))
    fig.text(0.01, 0.855 if note else 0.885, sub, fontsize=6.8, color=INK2, wrap=True, va="bottom")
    fig.text(0.01, 0.01, DIAG, fontsize=6.5, color=INK2)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ cross-team grid figures
def grid_heat(samp, value, title, fname, fmt="{:.0f}", cmap_max=None, note=""):
    teams = sorted(samp.canonical_engineering_team.unique())
    years = list(range(2018, 2026))
    M = np.full((len(teams), len(years)), np.nan)
    for r in samp.itertuples(index=False):
        v = getattr(r, value)
        M[teams.index(r.canonical_engineering_team), years.index(r.year)] = v if v is not None else np.nan
    fig, ax = plt.subplots(figsize=(8.8, 0.36 * len(teams) + 1.8))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", BLUE, "#0f3f7a"])
    cmap.set_bad(SURFACE)
    vmax = cmap_max or np.nanmax(M) if np.isfinite(np.nanmax(M)) else 1
    ax.imshow(np.ma.masked_invalid(M), aspect="auto", cmap=cmap, vmin=0, vmax=vmax)
    for (i, k), v in np.ndenumerate(M):
        if not np.isnan(v):
            ax.text(k, i, fmt.format(v), ha="center", va="center", fontsize=7, color="white" if v > vmax * 0.55 else INK)
    ax.set_xticks(range(len(years)), years)
    ax.set_yticks(range(len(teams)), teams, fontsize=7.5)
    for xline in (1.5, 6.5):
        ax.axvline(xline, color=INK, lw=1.2)
    ax.set_xlabel("Era A (2018–19)  |  Era B frozen reference (2020–24)  |  Era C (2025) — eras separated by vertical lines, never pooled", fontsize=7.5)
    ax.grid(False)
    ax.set_title(title + (f"\n{note}" if note else ""), loc="left", fontsize=10.5)
    save(fig, FIG / fname, top=0.97)


def summary_figures(samp, conf, wx, fctx):
    grid_heat(samp, "attempts_on_performance_timeline", "1. Timed complete attempts per team-year (primary teammate layer)", "summary1_attempts_per_team_year.png")
    grid_heat(samp, "cars_on_performance_timeline", "2. Cars on the performance timeline per team-year", "summary2_cars_per_team_year.png")
    grid_heat(samp, "median_gap_min", "3. Median gap between consecutive team attempts (min)", "summary3_median_gap_per_team_year.png",
              note="blank = fewer than 2 timed complete attempts")
    grid_heat(samp, "timeline_span_min", "4. Team timeline span (min, first→last timed complete attempt)", "summary4_span_per_team_year.png")
    wx2 = wx.copy()
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax, col, lab in zip(axes, ["track_range_c", "ambient_range_c"], ["track-temperature range (°C)", "ambient-temperature range (°C)"]):
        for i, (era, g) in enumerate(wx2.groupby("era")):
            g = g[g.attempts_on_performance_timeline >= 2]
            ax.scatter(g[col], g.attempts_on_performance_timeline + (i - 1) * 0.12, s=24, color=CAT[i], edgecolor=SURFACE, label=ERA_SHORT[era])
        ax.set_xlabel(lab)
    axes[0].set_ylabel("timed complete attempts in team-year")
    axes[0].legend(fontsize=7)
    fig.suptitle("5. Weather range covered by each team-year timeline (≥2 timed complete attempts; 2018 and 2022 have none)", x=0.01, ha="left", fontsize=10.5)
    save(fig, FIG / "summary5_weather_range_per_team_year.png")
    c = conf[conf.confounding_severity != "NOT_ASSESSABLE"].copy()
    c["label"] = c.year.astype(str) + " " + c.canonical_engineering_team
    c = c.sort_values(["era", "eta2_time_explained_by_car"])
    sev_col = {"LOW": CAT[2], "MODERATE": CAT[3], "SEVERE": CAT[7]}
    fig, ax = plt.subplots(figsize=(8, 0.24 * len(c) + 1.6))
    ax.barh(range(len(c)), c.eta2_time_explained_by_car, color=[sev_col[s] for s in c.confounding_severity], height=0.7)
    for i, (v, s, ov, pr) in enumerate(zip(c.eta2_time_explained_by_car, c.confounding_severity, c.car_pairs_with_overlapping_time_ranges, c.car_pairs)):
        ax.text(v + 0.01, i, f"{s} · overlapping car pairs {int(ov)}/{int(pr)}", va="center", fontsize=6.5, color=INK2)
    ax.set_yticks(range(len(c)), c.label, fontsize=7)
    ax.set_xlim(0, 1.45)
    ax.set_xlabel("η² = share of attempt-time variance explained by car identity (descriptive)")
    ax.set_title("6. Car/time confounding severity by team-year (labels are triage, not tests)", loc="left", fontsize=10.5)
    save(fig, FIG / "summary6_car_time_confounding.png", top=0.97)
    f = fctx[fctx.canonical_engineering_team != ""].copy()
    order = ["RICH (>=2 teammate cars between endpoints)", "SOME (1 teammate car between endpoints)",
             "OUTSIDE_ONLY (teammates only before/after)", "NONE (no timed teammate attempts)"]
    tab = f.groupby(["year", "context_class"]).size().unstack(fill_value=0).reindex(columns=order, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    left = np.zeros(len(tab))
    for k, col in enumerate(order):
        ax.barh(tab.index.astype(str), tab[col], left=left, color=CAT[k], edgecolor=SURFACE, linewidth=2, label=col, height=0.6)
        left += tab[col].values
    ax.set_xlabel("frozen same-car transitions (41 total; 1 technical-partnership target excluded)")
    ax.legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax.set_title("7. Frozen-core transitions: teammate context on the team timeline", loc="left", fontsize=10.5)
    save(fig, FIG / "summary7_frozen_core_context.png", top=0.97)


def priority_selection(samp, conf, wx):
    s = samp.merge(conf[["year", "canonical_engineering_team", "confounding_severity", "eta2_time_explained_by_car"]], how="left").merge(
        wx[["year", "canonical_engineering_team", "missing_track_fraction", "flags"]], how="left")
    s["weather_coverage"] = 1 - s.missing_track_fraction.fillna(1)
    picks = []
    # Rule 1: panel-eligible team-years, ranked by (timed complete attempts, cars with >=2 attempts, weather coverage, frozen overlap)
    elig = s[s.panel_eligible].sort_values(["attempts_on_performance_timeline", "cars_with_2plus_timeline_attempts", "weather_coverage",
                                            "frozen_core_attempts_on_timeline"], ascending=False)
    for era, k in [("ERA_B_FROZEN_REFERENCE", 4), ("ERA_C_HYBRID_EXTERNAL", 2)]:
        for r in elig[elig.era == era].head(k).itertuples(index=False):
            picks.append((r.year, r.canonical_engineering_team, f"RULE1_DENSEST_PANEL_ELIGIBLE_{era}"))
    # Rule 2: densest SEVERE-confounded team-year (negative case) in the reference era
    sev = s[(s.confounding_severity == "SEVERE") & (s.era == "ERA_B_FROZEN_REFERENCE")].sort_values("attempts_on_performance_timeline", ascending=False)
    if len(sev):
        picks.append((sev.iloc[0].year, sev.iloc[0].canonical_engineering_team, "RULE2_DENSEST_SEVERE_CONFOUNDING_NEGATIVE_CASE"))
    # Rule 3: densest 2022 team-year (weather/timing gap case) and densest Era A team-year
    for yrs, lab in [([2022], "RULE3_2022_WEATHER_TIMING_GAP_CASE"), ([2018, 2019], "RULE3_DENSEST_ERA_A_CASE")]:
        t = s[s.year.isin(yrs)].sort_values(["attempts_on_performance_timeline", "attempts_total"], ascending=False)
        if len(t):
            picks.append((t.iloc[0].year, t.iloc[0].canonical_engineering_team, lab))
    out = []
    seen = set()
    for y, t, why in picks:
        if (y, t) in seen:
            continue
        seen.add((y, t))
        r = s[(s.year == y) & (s.canonical_engineering_team == t)].iloc[0]
        out.append(dict(year=y, canonical_engineering_team=t, selection_rule=why, attempts_on_performance_timeline=r.attempts_on_performance_timeline,
                        cars_with_2plus_timeline_attempts=r.cars_with_2plus_timeline_attempts, weather_coverage=r.weather_coverage,
                        frozen_core_attempts_on_timeline=r.frozen_core_attempts_on_timeline, confounding_severity=r.confounding_severity))
    return pd.DataFrame(out)


def reports(j, base, samp, cons, conf, wx, fctx, cm, cl, pri):
    perf = j[j.on_performance_timeline]
    era_tab = samp.groupby("era").agg(team_years=("year", "size"), attempts_total=("attempts_total", "sum"),
                                      attempts_performance_timeline=("attempts_on_performance_timeline", "sum"),
                                      team_years_ge2_cars=("cars_on_performance_timeline", lambda s: int((s >= 2).sum())),
                                      team_years_ge3_cars=("cars_on_performance_timeline", lambda s: int((s >= 3).sum())),
                                      panel_eligible=("panel_eligible", "sum"),
                                      median_of_median_gaps_min=("median_gap_min", "median")).reset_index()
    dense = samp[samp.attempts_on_performance_timeline >= 5].sort_values("attempts_on_performance_timeline", ascending=False)[
        ["era", "year", "canonical_engineering_team", "attempts_on_performance_timeline", "cars_on_performance_timeline",
         "cars_with_2plus_timeline_attempts", "timeline_span_min", "median_gap_min", "max_gap_min", "consecutive_same_car",
         "consecutive_car_switch", "frozen_core_attempts_on_timeline", "panel_eligible"]].round(1)
    weak = samp.groupby("era").apply(lambda d: pd.Series({
        "team_years_with_0_timed_complete": int((d.attempts_on_performance_timeline == 0).sum()),
        "team_years_with_1_timed_complete": int((d.attempts_on_performance_timeline == 1).sum()),
        "team_years_single_car_on_timeline": int((d.cars_on_performance_timeline == 1).sum())}), include_groups=False).reset_index()
    y22 = samp[samp.year == 2022][["canonical_engineering_team", "attempts_total", "attempts_timed", "attempts_on_performance_timeline"]]
    cq = cons.groupby(["era", "pair_type"]).agg(pairs=("delta_time_min", "size"), median_dt_min=("delta_time_min", "median"),
                                                 median_abs_d_raw=("delta_raw_speed", lambda s: s.abs().median()),
                                                 median_abs_d_centered=("delta_centered_mean", lambda s: s.abs().median()),
                                                 median_abs_d_track=("delta_track_temp_c", lambda s: s.abs().median()),
                                                 share_same_track_obs=("same_track_observation", lambda s: s.astype(str).eq("True").mean())).reset_index().round(3)
    cqu = pd.DataFrame([dict(era=e, pair_type=p, unique_team_years=g[["year", "canonical_engineering_team"]].drop_duplicates().shape[0],
                             unique_teams=g.canonical_engineering_team.nunique(), unique_cars=len(set(zip(g.year, g.car_prev)) | set(zip(g.year, g.car_next))),
                             unique_attempts=len(set(g.attempt_prev) | set(g.attempt_next)))
                        for (e, p), g in cons.groupby(["era", "pair_type"])])
    ci = j[j.centering_informative.astype(bool)]
    circ = ci.groupby("era").apply(lambda d: pd.Series({"centering_informative_attempts": len(d),
                                                        "of_which_frozen_core_attempts": int(d.is_frozen_core_attempt.sum()),
                                                        "cars": d[["year", "registry_car_number"]].drop_duplicates().shape[0],
                                                        "team_years": d[["year", "canonical_engineering_team"]].drop_duplicates().shape[0]}),
                                   include_groups=False).reset_index()
    trend = cm[cm.summary == "within_car_time_trend_sign"]
    trend_tab = trend.groupby("era").agg(team_years=("year", "size"), all_cars_same_sign=("all_same_sign", "sum"),
                                         cars=("cars", "sum"), cars_positive_trend=("n_positive", "sum"), cars_negative_trend=("n_negative", "sum")).reset_index()
    rho = cm[cm.summary == "centered_vs_state_spearman"][["era", "year", "canonical_engineering_team", "n", "cars", "rho_centered_track",
                                                         "rho_centered_ambient", "rho_raw_track", "rho_centered_time"]].round(2)
    tert = cm[cm.summary == "tertile_centered_mean"][["era", "year", "canonical_engineering_team", "tertile", "n", "cars", "mean_centered",
                                                     "mean_track", "mean_ambient", "dispersion_centered_sd"]].round(2)
    signref = cm[cm.summary == "consecutive_sign_vs_frozen_reference"].dropna(axis=1, how="all").round(2)
    fz = fctx[fctx.canonical_engineering_team != ""]
    fz_tab = fz.groupby(["year", "context_class"]).size().unstack(fill_value=0).reset_index()
    conf_tab = conf.groupby(["era", "confounding_severity"]).size().unstack(fill_value=0).reset_index()
    wx_era = wx[wx.attempts_on_performance_timeline >= 2].groupby("era").agg(
        team_years=("year", "size"), median_track_range_c=("track_range_c", "median"), median_ambient_range_c=("ambient_range_c", "median"),
        median_distinct_track_values=("distinct_track_values", "median"), median_corr_track_ambient=("corr_track_ambient", "median"),
        median_corr_track_time=("corr_track_session_time", "median"),
        method_inconsistent_team_years=("method_consistent", lambda s: int((~s.astype(bool)).sum()))).reset_index().round(2)

    tr = f"""# V4 Phase 4B — Team Timeline Report (exploratory)

**Status:** exploratory reconstruction and description.
- No regression, fixed-effects or mixed-effects model was fitted, and no coefficient was estimated.
- The frozen 41 transitions and V2/V3 are untouched.
- Wherever a "frozen reference sign" appears, it comes from *applying* the published frozen coefficients to observed state changes. Nothing was re-estimated.

**Inputs:**
- Phase 3 `team_attempt_join.csv` (accepted registry; primary teammate layer only).
- Eras are never pooled:
  - Era A: 2018–19, pre-Aeroscreen extension.
  - Era B: 2020–24, frozen reference.
  - Era C: 2025, hybrid external.

**Performance timeline:** complete four-lap and timed attempts. Other primary-layer attempts stay in `team_timeline_long.csv`, each with a `timeline_exclusion_reason`.

## 1–4. Coverage (clustered data — attempts are not independent samples)

{md(cl)}

{md(era_tab)}

- Team-years with ≥2 cars on the performance timeline: **{int((samp.cars_on_performance_timeline >= 2).sum())}**. With ≥3 cars: **{int((samp.cars_on_performance_timeline >= 3).sum())}**.
- `panel_eligible` means ≥2 cars *each* with ≥2 timed complete attempts. This is the minimum for any within-car/between-car separation. **{int(samp.panel_eligible.sum())}** team-years qualify: {int(samp[samp.era=='ERA_B_FROZEN_REFERENCE'].panel_eligible.sum())} in Era B, {int(samp[samp.era=='ERA_C_HYBRID_EXTERNAL'].panel_eligible.sum())} in Era C, and 0 in Era A.

## 5. Densest team-year timelines (≥5 timed complete attempts)

{md(dense)}

## 6. Weakest cases

{md(weak)}

2022 (kept visible, not forced; no weather exists for it):

{md(y22)}

## 7. Sampling gaps

The median of team-year median gaps is shown per era above. The densest timeline (2021 Andretti, 11 attempts over ≈320 min) has a 14-min median gap but a 103-min maximum gap. Across the {int(samp.panel_eligible.sum())} panel-eligible team-years, median gaps run {samp[samp.panel_eligible].median_gap_min.min():.0f}–{samp[samp.panel_eligible].median_gap_min.max():.0f} min, and {int((samp[samp.panel_eligible].max_gap_min > 100).sum())} of them have a maximum gap above 100 min. No team samples the track continuously.

## 9. Car/time confounding summary

See `phase4b_sampling_bias_report.md`.

{md(conf_tab)}

## 10–11. What the raw and centered timelines show

**Raw timelines (`figures/raw_timelines/`):**
- The between-car level differences within a team (often 0.5–2 mph) are as large as or larger than any within-session movement.
- Many team-years hold one attempt per car, so the "timeline" is a sequence of *different cars*, and car identity and time cannot be separated.

**Centered timelines (`figures/centered_timelines/`):**
- Only cars with ≥2 timed complete attempts carry information; single-attempt cars center to 0 by construction and are drawn hollow.
- **Circularity:** in Era B, almost every informative centered attempt is a frozen same-car core attempt.

{md(circ)}

So in 2020–2024 the centered team timeline mostly re-displays the frozen same-car transitions on a shared clock. It adds no new independent within-car information. Era C (2025) is the only era whose centered information is independent of the frozen core, and it is a different technical regime.

## 12–13. Is common movement apparent?

**Within-car time-trend sign** (Spearman of speed vs session time, per car with ≥2 timed complete attempts):

{md(trend_tab)}

- In Era B, most cars go *faster* later in the session.
- Track temperature rises over the same period, so the frozen physics would predict slower speeds from the track term; the ambient term works the other way.
- A positive time trend therefore cannot be read as a track-temperature effect. It is equally consistent with deliberate repeat-attempt improvement (setup/trim changes, and the choice to re-run only when an improvement is expected).

**Centered speed vs physical state** (Spearman within team-year; descriptive; n = 5–8, clustered):

{md(rho)}

- **Era B:** the centered–track correlation is mostly *positive* and close to the centered–time correlation, because track temperature, ambient temperature and session time move together there.
- **Era C (2025):** centered speed vs ambient is positive in all 4 assessable team-years, while centered vs track is mixed. Every one of these rests on n = 6 clustered attempts, so it is suggestive at most.

**Session-time tertiles** (mean centered speed with car composition):

{md(tert)}

**Consecutive team observations, sign agreement with the frozen reference sign** (the frozen coefficients applied to Δtrack/Δambient; not a test):

{md(signref)}

- Different-car consecutive changes agree with the frozen reference sign about as often as a coin flip (≈0.5–0.6).
- Same-car pairs agree more often, but in Era B they are frozen-core transitions themselves.

**Assessment:** there is no clear, consistent common movement across cars.
- Where cars move together (e.g. 2023 Chip Ganassi, 2024 Arrow McLaren, 2025 Rahal: all cars trending up), the pattern is inseparable from session time and from repeat-attempt selection.
- Where the data are densest (2021 Andretti), cars disagree in direction.
- The pattern is concentrated in a few team-years and is not consistent across teams or years.

## 14. Frozen same-car transitions in team context

{md(fz_tab)}

The frozen transitions do sit inside team timelines, and many have teammate attempts between their endpoints. That gives useful *visual context* (see `figures/priority_cases/`). But most of those teammate attempts are themselves frozen-core endpoints, so the context is largely the frozen core seen from another car, not independent corroboration.

## 15–17. Does the representation justify formal panel modelling in Phase 4C?

**Not as a primary corroboration of the frozen reference-era coefficients.** Only a narrow, explicitly exploratory Phase 4C is defensible. The reasons:
1. **Too few usable clusters.** Era B has {int(samp[samp.era=='ERA_B_FROZEN_REFERENCE'].panel_eligible.sum())} panel-eligible team-years and Era A has none.
2. **Circularity.** Era B's within-car variation is ≈95% the frozen same-car data.
3. **Collinear environment in Eras A and B.** Within team-years there, track temperature is almost collinear with session time and with ambient (median correlations: Era B {wx_era.set_index('era').median_corr_track_time.get('ERA_B_FROZEN_REFERENCE', float('nan')):.2f} and {wx_era.set_index('era').median_corr_track_ambient.get('ERA_B_FROZEN_REFERENCE', float('nan')):.2f}). Era C (2025) is the exception ({wx_era.set_index('era').median_corr_track_time.get('ERA_C_HYBRID_EXTERNAL', float('nan')):.2f} and {wx_era.set_index('era').median_corr_track_ambient.get('ERA_C_HYBRID_EXTERNAL', float('nan')):.2f}): within 2025 team-years, track temperature moved much less monotonically with session time.
4. **Coarse track temperature.** Track temperature is quantised on 15-minute PTSC steps.
5. **Confounding.** Car identity and time are confounded (SEVERE in about half of the assessable team-years).
6. **Selection.** Attempt timing is strategic, not random.

**If Phase 4C proceeds**, plausible model families are:
- (a) a within-team-year car fixed-effects panel with a common session-time or state term and team-year-clustered uncertainty;
- (b) a hierarchical/mixed model with car-in-team-year random intercepts and possibly team-year random slopes;
- (c) a common latent session trend (state-space or dynamic factor) with car offsets.

Every one of these must be estimated **separately per era**, with Era C (2025, independent of the frozen core) as the only genuinely out-of-sample setting. They should be framed as *descriptions of within-team co-movement*, not as environmental coefficients.

**Remaining identification problems:**
- time vs environment collinearity;
- track vs ambient collinearity;
- car–time confounding;
- strategic selection of when and whether to re-run, including withdrawals of retained times;
- unobserved setup, tyre and fuel changes between attempts;
- 15-minute track quantisation;
- approximate timestamps;
- unreconstructed interruptions outside 2022;
- small numbers of clusters;
- circular re-use of the frozen core in Era B.

## Priority visual review (4B.16)

The cases were selected by pre-declared rules (`priority_case_selection.csv`), not by appearance. They include negative and messy cases.

{md(pri)}
"""
    (OUT / "phase4b_team_timeline_report.md").write_text(tr)

    sb = f"""# V4 Phase 4B — Sampling / Selection-Bias Report

Qualifying attempt times are chosen by teams, not randomised. This report measures how strongly car identity and time are entangled within each team-year.

**Metrics:**
- **η²:** the share of the within-team-year variance of attempt time explained by car identity. It is descriptive only.
- **Overlapping car pairs:** pairs of cars whose [first, last] attempt-time ranges overlap.
- **Dominance:** the largest share one car holds of the early and late tertiles.

**Severity labels are triage only:** SEVERE means η² ≥ 0.5 *or* no two cars overlap in time; MODERATE means 0.25–0.5; LOW means below 0.25. They are not tests.

{md(conf_tab)}

{md(conf[['era','year','canonical_engineering_team','cars','attempts','eta2_time_explained_by_car','car_pairs','car_pairs_with_overlapping_time_ranges','early_tertile_dominant_car','early_tertile_dominant_share','late_tertile_dominant_car','late_tertile_dominant_share','max_attempt_share_one_car','confounding_severity']].round(2))}

## Per-car attempt-time distributions (minutes from the session's first timed attempt)

{md(conf[conf.confounding_severity!='NOT_ASSESSABLE'][['year','canonical_engineering_team','per_car_time_distribution']])}

## Attempt sequence distribution

`car_baseline_summary.csv` gives attempts per car (total, complete, timed, on the timeline). It also gives `timeline_vs_all_mean_gap`, the difference between a car's timed-attempt mean and its all-complete-attempt mean. That gap shows how timestamp coverage itself selects attempts: in 2023 and 2024, recorder coverage misses part of the session.

{md(base.assign(gap=base.timeline_vs_all_mean_gap.round(3))[base.attempts_on_performance_timeline >= 1].groupby('era').agg(cars=('car_number','size'), median_abs_gap_mph=('gap', lambda s: s.abs().median()), max_abs_gap_mph=('gap', lambda s: s.abs().max())).reset_index())}

## Flags

- Every **SEVERE** team-year is one where a temporal performance pattern cannot be separated from which car ran. Temporal movement there must not be read as environmental.
- **Era A (2018–19)** is SEVERE or not assessable everywhere: Timing71 matched too few attempts per car.
- **Selection mechanisms** that cannot be observed in these data include:
  - re-running only when an improvement is expected;
  - withdrawing a retained time;
  - queue position and priority-lane rules;
  - setup and trim changes between runs.

Positive within-car time trends are the expected signature of such selection.
"""
    (OUT / "phase4b_sampling_bias_report.md").write_text(sb)

    wr = f"""# V4 Phase 4B — Weather Identifiability Report

A dense team timeline supports environmental interpretation only if the physical-state data vary enough, are measured consistently, and are not collinear with time.

## Era summary (team-years with ≥2 timed complete attempts)

{md(wx_era)}

## Per team-year

{md(wx[wx.attempts_on_performance_timeline >= 2][['era','year','canonical_engineering_team','attempts_on_performance_timeline','track_range_c','ambient_range_c','distinct_track_values','distinct_ambient_values','distinct_track_observation_times','track_resolution','method_consistent','missing_track_fraction','missing_ambient_fraction','corr_track_ambient','corr_track_session_time','flags']].round(2))}

## Findings

- **Quantisation:** Era B track temperature is the past-safe PTSC value on a 15-minute grid. A team-year with 6–11 attempts typically has only 4–7 distinct track values; attempts within one 15-minute bin share a value. Era A/C track values are linear interpolations between 15-minute observations, which adds smoothness, not information.
- **Collinearity (era-specific; see the table above):** in Eras A and B, track temperature within team-years is nearly collinear with session time and with ambient temperature. A within-team panel there cannot separate a track effect from an ambient effect or from a session-time trend. Era C (2025) has much weaker collinearity, so it is the only era where within-team variation could, in principle, separate state from time.
- **Mixed methods:** in 2023–24 the core tier mixes past-safe and realized-interpolated PTSC, or issue-gated and rescue-matched HRRR, within the same team-year (`method_consistent = False`).
- **Missing:** 2018 has no PTSC archive, and 2022 has no weather at all (it was not manufactured). Era A/C have no solar data, and their wind is in raw PTSC units, unverified.
- **Interruptions:** they are reconstructed only for 2022, which has no performance-timeline attempts with weather. For every other year, having no interruption record doesn't mean there was no interruption.
"""
    (OUT / "phase4b_weather_identifiability_report.md").write_text(wr)


def main():
    for d in ["raw_timelines", "centered_timelines", "priority_cases"]:
        (FIG / d).mkdir(parents=True, exist_ok=True)
    j = pd.read_csv(OUT / "team_timeline_long.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    j["attempt_timestamp_utc"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")
    for b in ["on_performance_timeline", "centering_informative", "is_frozen_core_attempt", "complete_four_lap"]:
        j[b] = j[b].astype(str).eq("True")
    base = pd.read_csv(OUT / "car_baseline_summary.csv", dtype={"car_number": str})
    samp = pd.read_csv(OUT / "team_timeline_sampling_summary.csv")
    cons = pd.read_csv(OUT / "consecutive_team_observations.csv")
    conf = pd.read_csv(OUT / "car_time_confounding_audit.csv")
    wx = pd.read_csv(OUT / "weather_identifiability_audit.csv")
    fctx = pd.read_csv(OUT / "frozen_core_timeline_context.csv").fillna({"canonical_engineering_team": ""})
    cm = pd.read_csv(OUT / "common_movement_exploration.csv")
    cl = pd.read_csv(OUT / "cluster_counts.csv")
    ix = lambda df, y, t: df[(df.year == y) & (df.canonical_engineering_team == t)].iloc[0]
    made = 0
    for (y, t), g in j.groupby(["year", "canonical_engineering_team"]):
        if g.on_performance_timeline.sum() < 2:
            continue  # "sufficient attempts": at least two timed complete attempts to form a timeline
        confr = ix(conf, y, t)
        for mode, d in [("raw", "raw_timelines"), ("centered", "centered_timelines")]:
            timeline_figure(g, y, t, mode, FIG / d / f"{y}_{t}_{mode}.png", ix(samp, y, t), confr, ix(wx, y, t))
        made += 1
    pri = priority_selection(samp, conf, wx)
    pri.to_csv(OUT / "priority_case_selection.csv", index=False)
    for r in pri.itertuples(index=False):
        g = j[(j.year == r.year) & (j.canonical_engineering_team == r.canonical_engineering_team)]
        if g.on_performance_timeline.sum() >= 1:
            for mode in ["raw", "centered"]:
                timeline_figure(g, r.year, r.canonical_engineering_team, mode,
                                FIG / "priority_cases" / f"{r.year}_{r.canonical_engineering_team}_{mode}.png",
                                ix(samp, r.year, r.canonical_engineering_team), ix(conf, r.year, r.canonical_engineering_team),
                                ix(wx, r.year, r.canonical_engineering_team), note=r.selection_rule)
    summary_figures(samp, conf, wx, fctx)
    reports(j, base, samp, cons, conf, wx, fctx, cm, cl, pri)
    print("team-year timelines drawn:", made)
    print(pri.to_string())


if __name__ == "__main__":
    main()
