"""V4 Phase 4E: 2018-2025 multi-session team-comparison DATA-OPPORTUNITY audit.

Implements output/phase4e/phase4e_quality_tier_spec.md (committed before retrieval/counting).
Counts and characterises observational opportunities only. No model, coefficient, preferred
team reference, performance ranking or hypothesis test is computed. Race observations are
never combined numerically with other categories. Eras are never pooled.
"""
import datetime as dt
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4e"
EVID = V4 / "evidence" / "phase4e"
TZ = "America/Indiana/Indianapolis"
YEARS = list(range(2018, 2026))
WINDOWS = [1, 2, 5, 10, 15, 30]
AT_SPEED = (37.0, 45.0)
ERA = {2018: "ERA_A_PRE_AEROSCREEN", 2019: "ERA_A_PRE_AEROSCREEN", 2025: "ERA_C_HYBRID", **{y: "ERA_B_REFERENCE" for y in range(2020, 2025)}}
LEGACY_FLAG_GREEN = {1}
NON_INDYCAR_WORDS = ["Lights", "Freedom 100", "NXT", "Pro 2000", "Open Test", "USF", "Road to Indy"]
STATE = {"RACE": "RACE_STATE_CONFOUNDED", "QUALIFYING_DAY1": "SOLO_RUN_FORMAT", "QUALIFYING_OTHER": "SOLO_RUN_FORMAT",
         "AGGREGATE_RESULT": "NOT_A_SESSION"}


# ------------------------------------------------------------------ registry
def registry():
    r = pd.read_csv(V4 / "output/v4_team_entry_registry.csv", dtype={"car_number": str})
    r = r[r.year.isin(YEARS)].copy()
    r["primary"] = r.strict_teammate_group.notna() & (r.strict_teammate_group != "")
    r["surname"] = r.driver.str.split().str[-1].str.lower()
    return r


def join_car(reg, year, car, driver):
    """Exact (year, car) join; 'T' backup only with surname agreement; never fuzzy."""
    car = str(car).strip()
    g = reg[(reg.year == year) & (reg.car_number == car)]
    method = "EXACT_CAR"
    if g.empty and car.endswith("T"):
        g = reg[(reg.year == year) & (reg.car_number == car[:-1])]
        method = "BACKUP_T_CAR"
    if g.empty and car.isdigit():
        for v in {car.lstrip("0") or "0", "0" + car}:
            gg = reg[(reg.year == year) & (reg.car_number == v)]
            if len(gg):
                g, method = gg, "CAR_06_6_VARIANT"
    if g.empty:
        return dict(join_status="UNMATCHED")
    sn = str(driver).split()[-1].lower() if isinstance(driver, str) and driver.strip() else ""
    part = g[g.qualifying_participant] if g.qualifying_participant.any() else g
    row = part.iloc[0]
    if method != "EXACT_CAR" and sn and sn not in set(g.surname):
        return dict(join_status="UNMATCHED", join_note=f"{method} without surname agreement")
    return dict(join_status="MATCHED", join_method=method, canonical_engineering_team=row.canonical_engineering_team,
                raw_entry_name=row.raw_entry_name, relationship_type=row.relationship_type, primary_layer=bool(row.primary),
                technical_partnership_only=row.relationship_type == "TECHNICAL_PARTNERSHIP", registry_car=row.car_number,
                registry_driver=row.driver, driver_matches_registry=(sn in set(g.surname)) if sn else None)


# ------------------------------------------------------------------ official sessions
def official_sessions():
    rows = []
    d = json.load(open(REPO / "r6_regime_extension/evidence/official_api_v2/season_dropdown_raw.json"))
    lst = {}
    for yb in d:
        for ev in yb["Events"]:
            if int(yb["Year"]) in YEARS and "Indianapolis 500" in ev["EventName"]:
                for s in ev["Sessions"]:
                    lst[int(s["EventsSessionID"])] = (int(yb["Year"]), ev["EventName"], s["SessionName"])
    files = {int(Path(p).stem.split("_")[2]): p for p in glob.glob(str(REPO / "r6_regime_extension/evidence/official_api_v2/*_session_*_raw.json"))
             + glob.glob(str(EVID / "official_session_details/*_session_*_raw.json"))}
    recs = []
    for sid, (y, ev, name) in lst.items():
        p = files.get(sid)
        dd = json.load(open(p)) if p else {}
        date = pd.to_datetime(dd.get("SessionDate"), format="%m/%d/%Y").date() if dd.get("SessionDate") else None
        rows.append(dict(year=y, event=ev, official_session_id=sid, official_session_name=name, session_date=date,
                         session_type_code=dd.get("SessionType"), official_records=len(dd.get("records", [])),
                         official_json=str(Path(p).relative_to(REPO)) if p else "",
                         official_reports="|".join(r.get("Name", "") for r in (dd.get("SessionReports") or []))))
        for r in dd.get("records", []):
            recs.append(dict(year=y, official_session_id=sid, car_number=str(r.get("CarNumber")), driver=r.get("DriverName") or f"{r.get('FirstName','')} {r.get('LastName','')}",
                             official_team_label=r.get("TeamName"), laps_complete=r.get("LapsComplete"), best_speed=r.get("BestSpeed")))
    s = pd.DataFrame(rows)
    return categorize(s), pd.DataFrame(recs)


def categorize(s):
    out = []
    for y, g in s.groupby("year"):
        isq = lambda n: bool(re.search("Qualif|Fast", n, re.I)) and not re.search("Fast Friday", n, re.I)   # impl. note 1
        q = g[g.official_session_name.map(isq) & ~g.official_session_name.str.contains("Combined", case=False)]
        q1d = q.session_date.dropna().min()
        qlast = q.session_date.dropna().max()
        carb_dates = g[g.official_session_name.str.contains("Final Practice|Practice Final|Carb", case=False)].session_date.dropna()
        carb = carb_dates.min() if len(carb_dates) else None
        for r in g.itertuples(index=False):
            n = r.official_session_name
            if "Combined" in n:
                c, sub = "AGGREGATE_RESULT", "combined result table"
            elif n.strip() == "Race":
                c, sub = "RACE", ""
            elif re.search("Final Practice|Practice Final|Carb", n, re.I):
                c, sub = "CARB_DAY", ""
            elif re.search("Day 1|Day One", n, re.I):
                c, sub = "QUALIFYING_DAY1", n
            elif isq(n):
                c, sub = "QUALIFYING_OTHER", n
            elif r.session_date is not None and q1d is not None and r.session_date == q1d - dt.timedelta(days=1):
                c, sub = "FAST_FRIDAY", n
            elif r.session_date is not None and qlast is not None and r.session_date > qlast and (carb is None or r.session_date < carb):
                c, sub = "POST_QUALIFYING_PRACTICE", n
            elif r.session_date is not None and q1d is not None and q1d <= r.session_date <= qlast:
                c, sub = "QUALIFYING_WEEKEND_PRACTICE", n
            else:
                c, sub = "PRACTICE", n
            out.append({**r._asdict(), "normalized_category": c, "subtype": sub, "era": ERA[y],
                        "state_class": STATE.get(c, "OPEN_TRACK_UNOBSERVED_RUN_PLAN")})
    return pd.DataFrame(out)


# ------------------------------------------------------------------ Timing71 laps
def parse_t71(path, year, reg):
    d = json.load(open(path))
    laps = []
    if "cars" in d:  # modern
        desc = d["manifest"]["description"]
        cars_obj = d["cars"]["cars"] if isinstance(d["cars"], dict) and "cars" in d["cars"] else d["cars"]  # modern schema nests cars once more
        for car, c in cars_obj.items():
            team_raw = c.get("teamName")
            drivers = {x["idx"]: x["name"] for x in c.get("drivers", [])}
            sts = c.get("stints", [])
            for si, st in enumerate(sts):
                L = st.get("laps", [])
                ended = bool(st.get("inPit")) or si < len(sts) - 1
                for k, lp in enumerate(L):
                    laps.append(dict(car=car, driver=drivers.get(lp.get("driver"), ""), team_raw=team_raw, stint=si, lap_in_stint=k,
                                     laps_in_stint=len(L), lap_number=lp.get("lapNumber"), laptime=lp.get("laptime"), flag=lp.get("flag") or "none",
                                     ts=(lp.get("timestamp") or np.nan) / 1000.0, ts_quality="OBSERVED_LAP_TIMESTAMP",
                                     is_out_lap=k == 0, is_in_lap=(k == len(L) - 1) and ended))
        fmt = "MODERN"
    else:  # legacy
        desc = d.get("service", {}).get("description", "")
        drv = d.get("driver", {})
        for car, sts in (d.get("stint") or {}).items():
            for si, s in enumerate(sts):
                if not s or len(s) < 10:
                    continue
                L = [x for x in s[9] if x and x[0]]
                if len(L) >= 2 and abs(L[0][0] - L[1][0]) < 1e-6:
                    L = L[1:]
                trailing_pit = bool(L and L[-1][0] > 120)
                chain = L[:-1] if trailing_pit else L
                cons = (s[3] - s[1]) - sum(x[0] for x in chain) if s[1] and s[3] else np.nan
                ok = bool(abs(cons) <= 15) if cons == cons else False
                # derived lap-completion times, backward from the stint end (labelled DERIVED)
                t_end = s[3]
                cum = np.cumsum([x[0] for x in chain][::-1])[::-1] if chain else []
                for k, x in enumerate(L):
                    tsd = (t_end - (cum[k + 1] if k + 1 < len(cum) else 0.0)) if (k < len(chain) and t_end) else np.nan
                    laps.append(dict(car=car, driver=(drv.get(car) or [""])[0], team_raw=None, stint=si, lap_in_stint=k, laps_in_stint=len(L),
                                     lap_number=None, laptime=x[0], flag="green" if x[1] in LEGACY_FLAG_GREEN else f"code_{x[1]}",
                                     ts=tsd, ts_quality="DERIVED_FROM_STINT_CONSISTENT" if ok else "DERIVED_FROM_STINT_INCONSISTENT",
                                     stint_start_ts=s[1], stint_end_ts=s[3], stint_consistency_s=cons,
                                     is_out_lap=k == 0, is_in_lap=(k == len(L) - 1) and trailing_pit))
        fmt = "LEGACY"
    df = pd.DataFrame(laps)
    return desc, fmt, df


def build_laps(reg, sessions):
    man = pd.read_csv(EVID / "retrieval_manifest.csv")
    man = man[(man.source_set == "TIMING71_ANALYSIS") & (man.error.fillna("") == "")]
    files, all_laps = [], []
    regy = {y: set(reg[reg.year == y].car_number) for y in YEARS}
    for r in man.itertuples(index=False):
        desc, fmt, df = parse_t71(REPO / r.local_path, int(r.year), reg)
        cars = set(df.car) if len(df) else set()
        match = len([c for c in cars if c in regy[int(r.year)] or c.rstrip("T") in regy[int(r.year)] or c.lstrip("0") in regy[int(r.year)]]) / max(len(cars), 1)
        bad_word = any(w.lower() in desc.lower() for w in NON_INDYCAR_WORDS)
        content_ok = (match >= 0.8) and not bad_word
        tsrc = df.ts if len(df) and df.ts.notna().any() else (df.stint_start_ts if len(df) and "stint_start_ts" in df else pd.Series(dtype=float))
        t0 = pd.to_datetime(tsrc.dropna(), unit="s", utc=True).dt.tz_convert(TZ).dt.date.mode().iloc[0] if tsrc.notna().any() else pd.NaT  # impl. note 2
        files.append(dict(source_id=r.source_id, local_path=r.local_path, year=int(r.year), listing_description=r.session, content_description=desc,
                          format=fmt, cars=len(cars), car_registry_match=round(match, 3), content_is_indy500_indycar=content_ok,
                          modal_lap_date_local=t0, laps=len(df), empty_analysis=len(df) == 0))
        if content_ok and len(df):
            df["source_id"], df["year"], df["content_description"], df["format"] = r.source_id, int(r.year), desc, fmt
            all_laps.append(df)
    files = pd.DataFrame(files)
    laps = pd.concat(all_laps, ignore_index=True)
    return files, laps


def map_files(files, sessions):
    out = []
    for f in files.itertuples(index=False):
        if f.empty_analysis:
            out.append(dict(source_id=f.source_id, session_key="", map_status="EMPTY_ANALYSIS"))
            continue
        if not f.content_is_indy500_indycar or pd.isna(f.modal_lap_date_local):
            out.append(dict(source_id=f.source_id, session_key="", map_status="EXCLUDED_CONTENT_NOT_INDY500_INDYCAR" if not f.content_is_indy500_indycar else "NO_TIME"))
            continue
        date = f.modal_lap_date_local
        cand = sessions[(sessions.year == f.year) & (sessions.session_date == date) & (sessions.normalized_category != "AGGREGATE_RESULT")]
        dsc = f.content_description
        pick = cand.iloc[0:0]
        if re.search(r"\bRace\b", dsc):
            pick = cand[cand.normalized_category == "RACE"]
        elif re.search("Final Practice|Practice Final|Carb", dsc, re.I):
            pick = cand[cand.normalized_category == "CARB_DAY"]
        elif m := re.search(r"Practice (\d+)", dsc):
            pick = cand[cand.official_session_name.str.fullmatch(fr"Practice {m.group(1)}.*", case=False)]
            if pick.empty:
                pick = cand[cand.official_session_name.str.contains("Practice", case=False) & ~cand.normalized_category.isin(["CARB_DAY"])]
        elif re.search("ROP", dsc):
            pick = cand[cand.official_session_name.str.contains("Practice", case=False)]
        elif re.search("Qualif|Fast|Top", dsc, re.I):
            qc = cand[cand.normalized_category.isin(["QUALIFYING_DAY1", "QUALIFYING_OTHER"])]
            for kw, pat in [("Day One|Day 1", "Day 1|Day One"), ("Top 12|Top-12", "Top-12|Top 12|Fast 12"), ("Fast 6", "Fast 6"),
                            ("Last Chance", "Last Chance"), ("Fast 9", "Fast 9")]:
                if re.search(kw, dsc, re.I):
                    pick = qc[qc.official_session_name.str.contains(pat, case=False)]
                    break
            else:
                pick = qc
        if len(pick) == 1:
            p = pick.iloc[0]
            out.append(dict(source_id=f.source_id, session_key=str(p.official_session_id), map_status="UNIQUE_OFFICIAL_SESSION"))
        elif len(pick) > 1 and pick.normalized_category.nunique() == 1:
            key = f"{f.year}|{date}|{pick.normalized_category.iloc[0]}|" + "+".join(map(str, sorted(pick.official_session_id)))
            out.append(dict(source_id=f.source_id, session_key=key, map_status="MULTIPLE_OFFICIAL_SEGMENTS_SAME_CATEGORY"))
        elif cand.empty:   # impl. note 3: on-track session captured by Timing71 but absent from the official session list
            c = ("RACE" if re.search(r"\bRace\b", dsc) else "CARB_DAY" if re.search("Final Practice|Practice Final|Carb", dsc, re.I)
                 else "QUALIFYING_OTHER" if re.search("Qualif|Top|Fast (6|9|12)", dsc, re.I) else "PRACTICE")
            out.append(dict(source_id=f.source_id, session_key=f"{f.year}|{date}|{c}|T71_ONLY:{dsc.split(' - ')[-1].strip()}", map_status="TIMING71_ONLY_NOT_IN_OFFICIAL_LIST"))
        else:
            out.append(dict(source_id=f.source_id, session_key="", map_status=f"UNMAPPED ({len(pick)} candidates)"))
    return pd.DataFrame(out)


# ------------------------------------------------------------------ weather (Firestone PTSC archive)
def ptsc_observations():
    x = pd.ExcelFile(REPO / "weather/evidence/ptsc/FirestoneTemperatures_current.xlsx")
    rows = []
    for y in YEARS:
        sheet = [n for n in x.sheet_names if n.startswith(str(y)) and "Temp" in n][0]
        d = pd.read_excel(x, sheet, header=None)
        cur = None
        for v in d.itertuples(index=False):
            c0, c1 = v[0], v[1]
            if isinstance(c0, (dt.datetime, pd.Timestamp)):
                cur = pd.Timestamp(c0).date()
            elif isinstance(c0, str) and c0.strip():
                cur = None if not re.match(r"^\s*$", c0) and not isinstance(c1, dt.time) else cur
            t = c1 if isinstance(c1, dt.time) else (c1.time() if isinstance(c1, (dt.datetime, pd.Timestamp)) else None)
            if cur is None or t is None or cur.year != y:
                continue
            amb, trk = pd.to_numeric(v[2], errors="coerce"), pd.to_numeric(v[3], errors="coerce")
            if pd.isna(amb) and pd.isna(trk):
                continue
            ts = pd.Timestamp(dt.datetime.combine(cur, t)).tz_localize(TZ)
            rows.append(dict(year=y, local_ts=ts, ambient_f=amb, track_f=trk, humidity=pd.to_numeric(v[4], errors="coerce"),
                             wind_raw=pd.to_numeric(v[5], errors="coerce"), pressure=pd.to_numeric(v[7], errors="coerce") if len(v) > 7 else np.nan))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ opportunity counting
def pair_counts(t, car, team, w_s):
    """Count unordered valid-lap pairs with |dt| <= w_s: same car / same team different car / different team."""
    o = np.argsort(t)
    t, car, team = t[o], car[o], team[o]
    hi = np.searchsorted(t, t + w_s, side="right")
    total = int((hi - np.arange(len(t)) - 1).sum())

    def within(groups):
        n = 0
        for g in np.unique(groups):
            tt = t[groups == g]
            n += int((np.searchsorted(tt, tt + w_s, side="right") - np.arange(len(tt)) - 1).sum())
        return n
    same_car = within(car)
    same_team_any = within(team)
    return total, same_car, same_team_any - same_car, total - same_team_any


def session_metrics(key, L, cat, weather):
    """L: valid laps of one session (with team fields). Returns dict of counts (race kept in its own rows)."""
    r = dict(session_key=key)
    t = L.ts.values.astype(float)
    car = L.car_id.values
    teamv = np.where(L.primary_layer.fillna(False).values.astype(bool), L.canonical_engineering_team.fillna("").values, "")
    matched = L.join_status == "MATCHED"
    r.update(raw_laps_all=int(L.attrs.get("raw_laps", len(L))), valid_laps=len(L), cars=L.car_id.nunique(),
             drivers=L.driver.nunique(), canonical_teams=L[matched].canonical_engineering_team.nunique())
    tc = L[L.primary_layer.fillna(False).astype(bool)].groupby("canonical_engineering_team").car_id.nunique()
    r.update(multi_car_teams=int((tc >= 2).sum()), teams_3plus=int((tc >= 3).sum()),
             valid_laps_multi_car_teams=int(L.canonical_engineering_team.isin(tc[tc >= 2].index).sum()))
    has_t = ~np.isnan(t)
    tt, cc, tm = t[has_t], car[has_t], teamv[has_t]
    # team code: unique id per team, but primary-layer-unmatched cars get their own singleton code (never teammates)
    tm_code = np.array([f"T:{x}" if x else f"C:{c}" for x, c in zip(tm, cc)])
    for w in WINDOWS:
        tot, sc, st, dteam = pair_counts(tt, cc, tm_code, w * 60.0) if len(tt) else (0, 0, 0, 0)
        r[f"same_car_pairs_le{w}"], r[f"same_team_pairs_le{w}"], r[f"diff_team_pairs_le{w}"] = sc, st, dteam
    # effective-information companions at 5 min
    Lt = L[has_t].assign(team_code=pd.Series(tm_code, index=L[has_t].index, dtype=object))
    pairs_cars, team_bins = set(), set()
    for team, g in Lt[Lt.team_code.str.startswith("T:")].groupby("team_code"):
        cars = sorted(g.car_id.unique())
        times = {c: np.sort(g[g.car_id == c].ts.values) for c in cars}
        for i in range(len(cars)):
            for k in range(i + 1, len(cars)):
                a, b = times[cars[i]], times[cars[k]]
                j = np.searchsorted(b, a)
                d1 = np.abs(a - b[np.clip(j, 0, len(b) - 1)])
                d2 = np.abs(a - b[np.clip(j - 1, 0, len(b) - 1)])
                if np.minimum(d1, d2).min() <= 300:
                    pairs_cars.add((team, cars[i], cars[k]))
        bins = (g.ts // 300).astype(int)
        for b, gb in g.groupby(bins):
            if gb.car_id.nunique() >= 2:
                team_bins.add((team, b))
    r.update(distinct_same_team_car_pairs_le5=len(pairs_cars), distinct_team_5min_cells_2plus_cars=len(team_bins),
             teams_with_same_team_overlap_le5=len({p[0] for p in pairs_cars}))
    # same-car repeats and gaps
    per_car = Lt.groupby("car_id").size()
    r.update(cars_ge2=int((per_car >= 2).sum()), cars_ge3=int((per_car >= 3).sum()), cars_ge5=int((per_car >= 5).sum()), cars_ge10=int((per_car >= 10).sum()))
    gaps = Lt.sort_values("ts").groupby("car_id").ts.diff().dropna() / 60
    r.update(same_car_gap_min_p10=gaps.quantile(.1) if len(gaps) else np.nan, same_car_gap_min_median=gaps.median() if len(gaps) else np.nan,
             same_car_gap_min_p90=gaps.quantile(.9) if len(gaps) else np.nan)
    # nearest-teammate separation distribution + weather difference
    near, dtr, dam = [], [], []
    for team, g in Lt[Lt.team_code.str.startswith("T:")].groupby("team_code"):
        if g.car_id.nunique() < 2:
            continue
        for c, h in g.groupby("car_id"):
            other = np.sort(g[g.car_id != c].ts.values)
            j = np.searchsorted(other, h.ts.values)
            cand = np.stack([other[np.clip(j, 0, len(other) - 1)], other[np.clip(j - 1, 0, len(other) - 1)]])
            best = cand[np.argmin(np.abs(cand - h.ts.values), axis=0), np.arange(len(h))]
            near.extend(np.abs(best - h.ts.values) / 60)
            if weather is not None and len(weather):
                wt = weather.ts.values
                def wx(tsv, col):
                    k = np.clip(np.searchsorted(wt, tsv, side="right") - 1, 0, len(wt) - 1)   # most recent observation (past-safe)
                    v = weather[col].values[k]
                    return np.where((tsv - wt[k] <= 1800) & (tsv >= wt[k]), v, np.nan)
                dtr.extend(np.abs(wx(best, "track_c") - wx(h.ts.values, "track_c")))
                dam.extend(np.abs(wx(best, "ambient_c") - wx(h.ts.values, "ambient_c")))
    for nm, arr in [("nearest_teammate_min", near), ("teammate_abs_dtrack_c", dtr), ("teammate_abs_dambient_c", dam)]:
        a = pd.Series(arr, dtype=float).dropna()
        for q in [.1, .25, .5, .75, .9, 1.0]:
            r[f"{nm}_p{int(q*100):03d}"] = a.quantile(q) if len(a) else np.nan
        r[f"{nm}_n"] = len(a)
    # team-reference feasibility (target excluded from its own reference)
    for w in WINDOWS:
        ws = w * 60.0
        n1 = n2 = 0
        for team, g in Lt[Lt.team_code.str.startswith("T:")].groupby("team_code"):
            cars = g.car_id.unique()
            if len(cars) < 2:
                continue
            ct = {c: np.sort(g[g.car_id == c].ts.values) for c in cars}
            for c in cars:
                others = [ct[o] for o in cars if o != c]
                x = ct[c]
                cnt = np.zeros(len(x), int)
                for ot in others:
                    cnt += (np.searchsorted(ot, x + ws, side="right") - np.searchsorted(ot, x - ws, side="left")) > 0
                n1 += int((cnt >= 1).sum())
                n2 += int((cnt >= 2).sum())
        r[f"ref_nearest_or_loo_mean_le{w}"] = n1
        r[f"ref_loo_median_le{w}"] = n2
    r["ref_temporally_weighted_le30"] = r["ref_nearest_or_loo_mean_le30"]
    r["valid_laps_in_multi_car_team_timed"] = int(Lt.team_code.str.startswith("T:").sum())
    # sampling / dependence
    lag1 = []
    for (c, s), g in Lt.sort_values("ts").groupby(["car_id", "stint"]):
        x = g.laptime.values
        if len(x) >= 5 and np.std(x[:-1]) > 0 and np.std(x[1:]) > 0:
            lag1.append(np.corrcoef(x[:-1], x[1:])[0, 1])
    r.update(valid_laps_per_car_median=float(per_car.median()) if len(per_car) else np.nan,
             stints_with_valid_laps=int(Lt.groupby(["car_id", "stint"]).ngroups), valid_laps_per_stint_median=float(Lt.groupby(["car_id", "stint"]).size().median()) if len(Lt) else np.nan,
             within_stint_lag1_autocorr_median=float(np.median(lag1)) if lag1 else np.nan, stints_for_autocorr=len(lag1))
    # hierarchy coexistence at 5 min
    r.update(hier_A_same_car=r["same_car_pairs_le5"] > 0, hier_B_same_team=r["same_team_pairs_le5"] > 0, hier_C_diff_team=r["diff_team_pairs_le5"] > 0)
    r["hier_all_three"] = r["hier_A_same_car"] and r["hier_B_same_team"] and r["hier_C_diff_team"]
    return r


# ------------------------------------------------------------------ tiers (spec §7)
def tier(row):
    T = bool(row.get("T_lap_timestamps"))
    I = (row.get("identity_match_share") or 0) >= 0.95
    two_teams = (row.get("multi_car_teams") or 0) >= 2
    if (row["normalized_category"] == "AGGREGATE_RESULT") or not T or not I or not two_teams:
        return "D", "not T / not I / <2 multi-car teams / aggregate"
    M = (row.get("multi_car_teams") or 0) >= 3
    O = (row.get("same_team_pairs_le5") or 0) >= 20 and (row.get("teams_with_same_team_overlap_le5") or 0) >= 3
    W = bool(row.get("weather_observed_in_span"))
    P = bool(row.get("P_provenance"))
    lims = [n for n, ok in [("state_open_track", row["state_class"] != "OPEN_TRACK_UNOBSERVED_RUN_PLAN"), ("M", M), ("O", O), ("W", W), ("P", P)] if not ok]
    if row["state_class"] == "RACE_STATE_CONFOUNDED" or len(lims) >= 2:
        return "C", ("race state confounded; " if row["state_class"] == "RACE_STATE_CONFOUNDED" else "") + "limitations: " + (",".join(lims) or "none")
    return ("B", "limitation: " + lims[0]) if len(lims) == 1 else ("A", "all criteria met")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    reg = registry()
    sessions, off_recs = official_sessions()
    files, laps = build_laps(reg, sessions)
    fmap = map_files(files, sessions)
    files = files.merge(fmap, on="source_id", how="left")
    laps = laps.merge(fmap, on="source_id", how="left")
    laps = laps[laps.session_key.fillna("") != ""].copy()
    # identity join (no fuzzy)
    jc = {}
    for (y, c), g in laps.groupby(["year", "car"]):
        jc[(y, c)] = join_car(reg, y, c, g.driver.mode().iloc[0] if g.driver.notna().any() else "")
    J = pd.DataFrame([dict(year=y, car=c, **v) for (y, c), v in jc.items()])
    laps = laps.merge(J, on=["year", "car"], how="left")
    laps["car_id"] = laps.year.astype(str) + "|" + laps.car.astype(str)
    # dedupe laps across split / duplicate replay files of the same session
    laps["_k"] = laps.ts.round(0).astype("Int64").astype(str) + "|" + laps.laptime.round(4).astype(str)
    laps = laps.sort_values("source_id").drop_duplicates(["session_key", "car", "_k"])
    lo, hi = AT_SPEED
    flag_ok = laps.flag.astype(str).str.lower().isin(["green", "none"])
    laps["valid_lap"] = flag_ok & ~laps.is_out_lap & ~laps.is_in_lap & laps.laptime.between(lo, hi)
    laps["at_speed"] = laps.laptime.between(lo, hi)
    # session categories on laps
    cat_of = {str(r.official_session_id): (r.normalized_category, r.state_class) for r in sessions.itertuples(index=False)}
    def key_cat(k):
        if "|" in k:
            parts = k.split("|")
            return parts[2], STATE.get(parts[2], "OPEN_TRACK_UNOBSERVED_RUN_PLAN")
        return cat_of.get(k, ("UNKNOWN", "UNKNOWN"))
    laps["normalized_category"] = [key_cat(k)[0] for k in laps.session_key]
    # weather
    wx = ptsc_observations()
    wx["ts"] = (wx.local_ts.dt.tz_convert("UTC") - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(seconds=1)   # unit-safe epoch seconds
    wx["track_c"], wx["ambient_c"] = (wx.track_f - 32) * 5 / 9, (wx.ambient_f - 32) * 5 / 9
    wx = wx.sort_values("ts")
    wx.to_csv(OUT / "inputs" / "ptsc_event_observations_extracted.csv", index=False)

    # per-session metrics
    rows = []
    for key, g in laps.groupby("session_key"):
        cat, state = key_cat(key)
        y = int(g.year.iloc[0])
        v = g[g.valid_lap].copy()
        v.attrs["raw_laps"] = len(g)
        ww = wx[wx.year == y]
        tmin, tmax = np.nanmin(g.ts) if g.ts.notna().any() else np.nan, np.nanmax(g.ts) if g.ts.notna().any() else np.nan
        if np.isnan(tmin) and "stint_start_ts" in g:
            tmin, tmax = np.nanmin(g.stint_start_ts), np.nanmax(g.stint_end_ts)
        wspan = ww[(ww.ts >= tmin - 900) & (ww.ts <= tmax + 900)] if not np.isnan(tmin) else ww.iloc[0:0]
        m = session_metrics(key, v, cat, wspan if len(wspan) else None)
        ts_obs_share = float((v.ts_quality == "OBSERVED_LAP_TIMESTAMP").mean()) if len(v) else 0.0
        m.update(year=y, era=ERA[y], normalized_category=cat, state_class=state, source_files=g.source_id.nunique(),
                 formats="|".join(sorted(g.format.unique())), timing_span_start_utc=pd.to_datetime(tmin, unit="s", utc=True) if tmin == tmin else pd.NaT,
                 timing_span_min=(tmax - tmin) / 60 if tmin == tmin else np.nan, observed_lap_timestamp_share=ts_obs_share,
                 derived_consistent_share=float((v.ts_quality == "DERIVED_FROM_STINT_CONSISTENT").mean()) if len(v) else 0.0,
                 T_lap_timestamps=ts_obs_share >= 0.8,
                 identity_match_share=float(v.drop_duplicates("car_id").join_status.eq("MATCHED").mean()) if len(v) else 0.0,
                 unmatched_cars="|".join(sorted(v[v.join_status != "MATCHED"].car.unique())),
                 ptsc_obs_in_span=len(wspan), weather_observed_in_span=len(wspan) > 0,
                 P_provenance="T71_ONLY" not in key, non_at_speed_laps=int((~g.at_speed).sum()),
                 technical_partnership_valid_laps=int(v.technical_partnership_only.fillna(False).astype(bool).sum()))
        rows.append(m)
    S = pd.DataFrame(rows)
    # session inventory (official universe + lap-level coverage)
    key_of_off = {}
    for k in S.session_key:
        if "T71_ONLY" in k:
            continue
        for sid in (k.split("|")[-1].split("+") if "|" in k else [k]):
            key_of_off[int(sid)] = k
    sessions["lap_level_session_key"] = sessions.official_session_id.map(key_of_off).fillna("")
    sessions = sessions.merge(S.drop(columns=["normalized_category", "state_class", "era", "year"]), left_on="lap_level_session_key",
                              right_on="session_key", how="left")
    # Timing71-only sessions (absent from the official list) get their own inventory rows (impl. note 3)
    extra = []
    for k in S.session_key:
        if "T71_ONLY" in k:
            y, d, c, nm = k.split("|")
            extra.append(dict(year=int(y), event="Indianapolis 500", official_session_id=np.nan, official_session_name=f"(not in official list) {nm.replace('T71_ONLY:', '')}",
                              session_date=pd.Timestamp(d).date(), session_type_code=None, official_records=0, official_json="", official_reports="",
                              normalized_category=c, subtype=nm, era=ERA[int(y)], state_class=STATE.get(c, "OPEN_TRACK_UNOBSERVED_RUN_PLAN"), lap_level_session_key=k))
    if extra:
        ex = pd.DataFrame(extra).merge(S.drop(columns=["normalized_category", "state_class", "era", "year"]), left_on="lap_level_session_key", right_on="session_key", how="left")
        sessions = pd.concat([sessions, ex], ignore_index=True)
    sessions["weather_ptsc_on_date"] = [bool(len(wx[(wx.year == y) & (wx.local_ts.dt.date == d)])) if d is not None else False
                                        for y, d in zip(sessions.year, sessions.session_date)]
    # spec §5: PTSC inside the timing span; for sessions with no lap-level span, PTSC on the session date
    sessions["weather_observed_in_span"] = np.where(sessions.lap_level_session_key != "", sessions.weather_observed_in_span.astype("boolean").fillna(False),
                                                    sessions.weather_ptsc_on_date)
    sessions["T_lap_timestamps"] = sessions.T_lap_timestamps.astype("boolean").fillna(False)
    tiers = [tier(r._asdict()) for r in sessions.itertuples(index=False)]
    sessions["quality_tier"], sessions["tier_reason"] = [t[0] for t in tiers], [t[1] for t in tiers]
    sessions["source_availability"] = np.where(sessions.lap_level_session_key != "", "OFFICIAL_SESSION_JSON+TIMING71_LAP_JSON",
                                               np.where(sessions.official_json != "", "OFFICIAL_SESSION_JSON_ONLY(+official PDFs not ingested)", "LIST_ONLY"))
    sessions["timing_resolution"] = np.where(sessions.T_lap_timestamps, "OBSERVED_LAP_TIMESTAMP",
                                             np.where(sessions.lap_level_session_key != "", "STINT_TIMESTAMP_ONLY (lap times derived)", "SESSION_LEVEL_ONLY"))
    # one lap-level capture can cover several official segments: flag sharing so totals count each session_key once
    share = sessions[sessions.lap_level_session_key != ""].groupby("lap_level_session_key").size()
    sessions["lap_data_shared_by_n_official_segments"] = sessions.lap_level_session_key.map(share).fillna(0).astype(int)
    sessions.to_csv(OUT / "session_quality_tiers_full.csv", index=False)
    return reg, sessions, off_recs, files, laps, S, wx


if __name__ == "__main__":
    import pickle
    res = main()
    pickle.dump(res, open(OUT / "inputs" / "_audit_cache.pkl", "wb"))
    reg, sessions, off_recs, files, laps, S, wx = res
    print(files[["year", "content_description", "format", "content_is_indy500_indycar", "map_status"]].to_string())
    print(sessions.groupby(["year", "quality_tier"]).size().unstack(fill_value=0))
