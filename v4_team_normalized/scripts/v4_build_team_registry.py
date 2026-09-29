"""V4 Phase 1-2: team entry registry and team-normalisation audit.

Inputs (read-only; nothing in the frozen V2/V3 tree is modified):
  v4_team_normalized/output/v4_official_entry_lists_parsed.csv   (from v4_parse_entry_lists.py)
  v4_team_normalized/manual/v4_team_mapping_rules.csv            (explicit, source-backed rules)
  r6_regime_extension/evidence/official_api_v2/regime_extension_all_session_records_v1.csv
  weather/output/official_day1_api_record_inventory_v1.csv
  r5_1/output/team_year_control_inventory_v1.csv                 (existing teammate grouping)

Team identity is assigned ONLY by exact-label rules; no string similarity is used.
"""
import itertools
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output"

SOURCE_URLS = {
    "OFFICIAL_ENTRY_LIST": None,  # per-year URL from parsed entry list
    "OFFICIAL_INDYCAR_NEWS_2018-03-09": "https://www.indycar.com/News/2018/03/03-09-Servia-Scuderia-Corsa-Rahal-Indy-500-entry",
    "OFFICIAL_INDYCAR_NEWS_2018-09-19": "https://www.indycar.com/News/2018/09/09-19-Harding-Steinbrenner-Racing-announcement",
    "OFFICIAL_INDYCAR_NEWS_2019-09-21": "https://www.indycar.com/News/2019/09/09-21-Andretti-Herta",
    "ANDRETTI_PRESS_2019-09": "https://andrettiglobal.com/news/2019/09/andretti-autosport-and-harding-steinbrenner-racing-align-to-field-colton-herta-in-ntt-indycar-series/",
    "OFFICIAL_INDYCAR_NEWS_2019-05-13": "https://www.indycar.com/News/2019/05/05-13-Servia-Stange-Arrow-SPM-Indy-500-entry",
    "OFFICIAL_IMS_NEWS_2019-05-13": "https://www.indianapolismotorspeedway.com/news-multimedia/news/2019/05/13/oriol-servia-livery-indy-500-2019",
    "OFFICIAL_IMS_NEWS_2022": "https://www.indianapolismotorspeedway.com/news-multimedia/news/2022/02/15/02-15-2022-marco-andretti-500-entry",
    "OFFICIAL_INDYCAR_NEWS_2021-01-19": "https://www.indycar.com/news/2021/01/01-19-paretta-autosport-indy-500",
    "SECONDARY_RACER_2021-01-19": "https://racer.com/2021/01/19/de-silvestro-to-make-indy-500-return-in-penske-aligned-paretta-entry",
    "SECONDARY_NBC": "https://motorsports.nbcsports.com/tag/andretti-herta-autosport-with-curb-agajanian/",
    "SECONDARY_WIKIPEDIA": "https://en.wikipedia.org/wiki/Jack_Harvey_(racing_driver)",
    "MSR_TEAM_PRESS_2018-05-19": "http://www.michaelshankracing.com/index.php/2018/05/19/meyer-shank-racing-qualifies-for-the-102nd-indianapolis-500/",
    "SECONDARY_GENERAL_KNOWLEDGE": None,
}

# Driver changes after the entry list was issued (primary-source confirmed).
SUBSTITUTIONS = [
    dict(year=2018, car_number="19", driver="Zachary Claman De Melo", replaces="Pietro Fittipaldi",
         entry_status="SUBSTITUTE_DRIVER",
         source="https://www.indycar.com/News/2018/05/05-15-Claman-De-Melo-replaces-Fittipaldi-in-Indy-500",
         note="Replaced Fittipaldi (leg/ankle fractures, 4 May 2018 Spa crash) before practice; ran all practice and qualifying. Same DCR #19 entry."),
    dict(year=2023, car_number="24", driver="Graham Rahal", replaces="Stefan Wilson",
         entry_status="RACE_ONLY_SUBSTITUTE",
         source="https://www.indycar.com/news/2023/05/05-23-rahal-drrcusick",
         note="Race-day substitute after Wilson's practice injury (22 May 2023). Wilson qualified the car; Rahal did not qualify #24. Excluded from qualifying teammate pairs."),
]

# Technical/affiliation links that are NOT merged into the strict teammate layer.
AFFILIATIONS = [
    (2018, "MEYER_SHANK_RACING", "ARROW_MCLAREN_SPM", "TECHNICAL_PARTNERSHIP", "MEDIUM", "MSR ran #60 with SPM technical partnership (official entry label 'Meyer Shank Racing with SPM')."),
    (2019, "MEYER_SHANK_RACING", "ARROW_MCLAREN_SPM", "TECHNICAL_PARTNERSHIP", "MEDIUM", "Reported as Arrow SPM's partnership with MSR for 2019 Indy 500 (motorsportweek.com 2019-05-13, secondary)."),
    (2019, "HARDING_STEINBRENNER_RACING", "ANDRETTI", "TECHNICAL_PARTNERSHIP", "MEDIUM", "Andretti Technologies engineering support to HSR through 2019 (INDYCAR/Andretti press)."),
    (2019, "MCLAREN_RACING_2019", "CARLIN", "TECHNICAL_PARTNERSHIP", "MEDIUM", "McLaren's 2019 Alonso entry ran with Carlin support (secondary; not verified against a primary document here)."),
    (2020, "MEYER_SHANK_RACING", "ANDRETTI", "TECHNICAL_PARTNERSHIP", "MEDIUM", "MSR-Andretti data-sharing alliance ~1.5 years old as of 2021-06-29 (Autosport, secondary)."),
    (2021, "MEYER_SHANK_RACING", "ANDRETTI", "TECHNICAL_PARTNERSHIP", "MEDIUM", "MSR-Andretti data-sharing alliance active (Autosport 2021-06-29, secondary)."),
    (2022, "MEYER_SHANK_RACING", "ANDRETTI", "UNCERTAIN", "LOW", "Continuation of MSR-Andretti alliance into 2022 not verified."),
    (2021, "PARETTA_AUTOSPORT", "TEAM_PENSKE", "TECHNICAL_PARTNERSHIP", "MEDIUM", "Team Penske technical partnership (INDYCAR 2021-01-19; RACER 2021-01-19)."),
]

# (year, old API label) pairs where the API label is anachronistic: it names an organisation
# or brand that did not exist / did not enter that car in that year per the official entry list.
ANACHRONISTIC_API_LABELS = {
    (2018, "Arrow McLaren"): "Official 2018 entrant: Schmidt Peterson Motorsports / SPM-AFS.",
    (2019, "Arrow McLaren"): "Official 2019 entrant: Arrow Schmidt Peterson Motorsports.",
    (2018, "Juncos Hollinger Racing"): "Official 2018 entrant: Juncos Racing.",
    (2019, "Juncos Hollinger Racing"): "Official 2019 entrant: Juncos Racing.",
    (2018, "Andretti Steinbrenner Autosport"): "Official 2018 entrant for #88: Harding Racing (no Andretti or Steinbrenner involvement).",
    (2019, "Andretti Steinbrenner Autosport"): "Official 2019 entrant for #88: Harding Steinbrenner Racing (independent, Andretti technical support only).",
    (2020, "Andretti Steinbrenner Autosport"): "Official 2020 entrant for #88: Andretti Harding Steinbrenner Autosport.",
    (2020, "Arrow McLaren"): "Official 2020 entrant: Arrow McLaren SP.",
    (2021, "Arrow McLaren"): "Official 2021 entrant: Arrow McLaren SP.",
    (2022, "Arrow McLaren"): "Official 2022 entrant: Arrow McLaren SP.",
    (2021, "Andretti Global w/ Curb-Agajanian"): "Official 2021 entrant: Andretti Autosport w/ Curb-Agajanian (Andretti Global name from 2024).",
    (2022, "Andretti Global w/ Curb-Agajanian"): "Official 2022 entrant: Andretti Autosport w/ Curb-Agajanian.",
    (2023, "Andretti Global w/ Curb-Agajanian"): "Official 2023 entrant: Andretti Autosport w/ Curb-Agajanian.",
    (2021, "Meyer Shank w/ Curb-Agajanian"): "Official 2021 entrant for #06: Meyer Shank Racing.",
    (2022, "Meyer Shank w/ Curb-Agajanian"): "Official 2022 entrant for #06: Meyer Shank Racing.",
    (2023, "Meyer Shank w/ Curb-Agajanian"): "Official 2023 entrant for #06: Meyer Shank Racing.",
    (2019, "Arrow McLaren"): "Official 2019 entrant: Arrow Schmidt Peterson Motorsports.",
    (2019, "Dale Coyne Racing with Rick Ware Racing, BYRD and Belardi Auto Racing"): "Official 2019 entrant for #33: Dale Coyne Racing with Byrd and Belardi (Rick Ware Racing partnership began 2020).",
    (2020, "Dale Coyne Racing with RWR"): "Official 2020 entrant for #55: Dale Coyne Racing with Team Goh (RWR label belongs to later #51 entries).",
    (2018, "Andretti Herta w/ Marco & Curb-Agajanian"): "Official 2018 entrant: Andretti Herta Autosport with Curb-Agajanian (Marco became co-owner in 2019).",
}

# Deliberate non-merges where surface similarity or an API label could suggest equivalence.
NOT_EQUIVALENT = {
    (2018, "88"): "API labels 2018 #88 as 'Andretti Steinbrenner Autosport'; official entrant is Harding Racing. Not Andretti.",
    (2022, "25"): "DragonSpeed / Cusick Motorsports shares partner Cusick with later DRR-Cusick entries but is a different engineering team from DRR.",
}


# Surname used by the INDYCAR API where it differs from the entry-list spelling.
DRIVER_ALIASES = {"Zachary Claman De Melo": "claman"}


def car_key(c):
    # Keep leading zeros: #06 (Castroneves, MSR) and #6 (Montoya, AMSP) are different 2022 entries.
    return str(c).strip()


def car_variants(c):
    c = car_key(c)
    return {c, c.lstrip("0") or "0"}


def surname(name):
    name = str(name).strip()
    if name in DRIVER_ALIASES:
        return DRIVER_ALIASES[name]
    n = re.sub(r"\s*\((R|W)\)", "", name).strip()
    return n.split()[-1].lower().replace("í", "i") if n else ""


def year_in(rule_years, y):
    a, _, b = str(rule_years).partition("-")
    return int(a) <= y <= int(b or a)


def load_entries():
    e = pd.read_csv(OUT / "v4_official_entry_lists_parsed.csv", dtype={"car_number": str})
    e["entry_status"] = "ENTRY_LIST"
    e["substitution_note"] = ""
    e["substitution_source"] = ""
    extra = []
    for s in SUBSTITUTIONS:
        base = e[(e.year == s["year"]) & (e.car_number.map(car_key) == car_key(s["car_number"]))]
        assert len(base) == 1, s
        r = base.iloc[0].copy()
        idx = base.index[0]
        if s["entry_status"] == "SUBSTITUTE_DRIVER":
            e.loc[idx, "entry_status"] = "LISTED_REPLACED_BEFORE_PARTICIPATION"
            e.loc[idx, "substitution_note"] = f"Replaced by {s['driver']}. " + s["note"]
            e.loc[idx, "substitution_source"] = s["source"]
        r["driver"] = r["driver_as_listed"] = s["driver"]
        r["rookie_flag"] = r["past_winner_flag"] = pd.NA
        r["hometown"] = ""
        r["entry_status"] = s["entry_status"]
        r["substitution_note"] = f"Replaces {s['replaces']}. " + s["note"]
        r["substitution_source"] = s["source"]
        extra.append(r)
    return pd.concat([e, pd.DataFrame(extra)], ignore_index=True)


def apply_rules(e):
    rules = pd.read_csv(V4 / "manual" / "v4_team_mapping_rules.csv", dtype=str).fillna("")
    out = []
    for r in e.itertuples(index=False):
        hits = rules[[year_in(ry, r.year) and r.entrant_or_team_as_listed in lbl.split("|")
                      for ry, lbl in zip(rules.years, rules.raw_entry_label)]]
        if len(hits) != 1:
            raise ValueError(f"{r.year} #{r.car_number} '{r.entrant_or_team_as_listed}': {len(hits)} rule matches")
        out.append(hits.iloc[0].to_dict())
    rr = pd.DataFrame(out).drop(columns=["years", "raw_entry_label"])
    return pd.concat([e.reset_index(drop=True), rr], axis=1)


def load_api_labels():
    a = pd.read_csv(REPO / "r6_regime_extension/evidence/official_api_v2/regime_extension_all_session_records_v1.csv", low_memory=False)
    a = a[["year", "session_name", "CarNumber", "DriverName", "TeamName"]]
    w = pd.read_csv(REPO / "weather/output/official_day1_api_record_inventory_v1.csv", low_memory=False)
    w = w.rename(columns=lambda c: c.replace("field__", ""))
    w["session_name"] = "Qualifications - Day 1"
    api = pd.concat([a, w[["year", "session_name", "CarNumber", "DriverName", "TeamName"]]])
    api = api[api.year.between(2018, 2025)].copy()
    api["car_key"] = api.CarNumber.map(car_key)
    api["surname"] = api.DriverName.map(surname)
    return api


def attach_old_labels(reg, api):
    old, anomalies = [], []
    for r in reg.itertuples(index=False):
        g = api[(api.year == r.year) & api.car_key.isin(car_variants(r.car_number))]
        match = g[g.surname == surname(r.driver)]
        labels = sorted(match.TeamName.dropna().unique())
        old.append(" | ".join(labels) if labels else "")
    reg["old_group_identity"] = old
    # API records whose (car, driver) pair does not match any registry row = API artefacts
    keys = {(y, v, surname(d)) for y, c, d in zip(reg.year, reg.car_number, reg.driver) for v in car_variants(c)}
    for (y, c, s), g in api.groupby(["year", "car_key", "surname"]):
        if (y, c, s) not in keys:
            anomalies.append(dict(year=y, api_car_number=c, api_driver=g.DriverName.iloc[0], api_team=g.TeamName.iloc[0],
                                  sessions="; ".join(sorted(g.session_name.unique())), records=len(g)))
    return reg, pd.DataFrame(anomalies)


def attach_r5_1_groups(reg):
    t = pd.read_csv(REPO / "r5_1/output/team_year_control_inventory_v1.csv", dtype={"car_number": str})
    t["car_key"] = t.car_number.map(car_key)
    t["surname"] = t.driver_name.map(surname)
    m = {(y, c, s): tid for y, c, s, tid in zip(t.year, t.car_key, t.surname, t.team_year_id)}
    reg["r5_1_inventory_team_year_id"] = [
        next((m[(y, v, surname(d))] for v in car_variants(c) if (y, v, surname(d)) in m), "") if st != "RACE_ONLY_SUBSTITUTE" else ""
        for y, c, d, st in zip(reg.year, reg.car_number, reg.driver, reg.entry_status)]
    # map r5_1 rows onto registry car keys so pair accounting uses one key space
    back = {(y, v, surname(d)): car_key(c) for y, c, d in zip(reg.year, reg.car_number, reg.driver) for v in car_variants(c)}
    t["car_key"] = [back.get((y, c, s), c) for y, c, s in zip(t.year, t.car_key, t.surname)]
    return reg, t


def pairs(df, group_col):
    s = set()
    for (y, gv), g in df.groupby(["year", group_col]):
        if gv in ("", None) or pd.isna(gv):
            continue
        for a, b in itertools.combinations(sorted(g.car_key), 2):
            s.add((y, a, b))
    return s


def main():
    e = load_entries()
    reg = apply_rules(e)
    api = load_api_labels()
    reg, anomalies = attach_old_labels(reg, api)
    reg, r51 = attach_r5_1_groups(reg)
    reg["car_key"] = reg.car_number.map(car_key)

    # ---------------- registry ----------------
    reg["raw_entry_name"] = reg.entrant_or_team_as_listed
    reg["raw_team_name"] = reg.old_group_identity  # the separately published (INDYCAR API) team label
    reg["display_name"] = reg.car_name_as_listed
    reg["primary_source"] = reg.source_url
    reg["secondary_source"] = [
        "; ".join(filter(None, [SOURCE_URLS.get(tok) for tok in sr.split("+") if tok != "OFFICIAL_ENTRY_LIST"] + [ss]))
        for sr, ss in zip(reg.source_ref, reg.substitution_source)
    ]
    reg["old_label_anachronistic"] = [
        any((y, lbl.strip()) in ANACHRONISTIC_API_LABELS for lbl in old.split("|")) for y, old in zip(reg.year, reg.old_group_identity)
    ]
    reg["evidence_notes"] = [
        " ".join(filter(None, [n, sn,
                               *[ANACHRONISTIC_API_LABELS[(y, l.strip())] for l in old.split("|") if (y, l.strip()) in ANACHRONISTIC_API_LABELS],
                               NOT_EQUIVALENT.get((y, car_key(c)), "")]))
        for n, sn, y, old, c in zip(reg.evidence_notes, reg.substitution_note, reg.year, reg.old_group_identity, reg.car_number)
    ]
    reg["qualifying_participant"] = reg.entry_status.isin(["ENTRY_LIST", "SUBSTITUTE_DRIVER"])
    reg["strict_teammate_group"] = [f"{y}|{c}" if m == "TRUE" and q else "" for y, c, m, q in
                                    zip(reg.year, reg.canonical_engineering_team, reg.merge_into_canonical, reg.qualifying_participant)]
    cols = ["year", "driver", "car_number", "raw_entry_name", "raw_team_name", "display_name",
            "canonical_engineering_team", "parent_organisation", "engine", "relationship_type",
            "normalization_confidence", "primary_source", "secondary_source", "evidence_notes",
            "affiliated_with", "entry_status", "qualifying_participant", "strict_teammate_group",
            "old_group_identity", "old_label_anachronistic", "r5_1_inventory_team_year_id",
            "driver_as_listed", "rookie_flag", "past_winner_flag", "entry_list_issued", "rule_id"]
    reg = reg.sort_values(["year", "canonical_engineering_team", "car_key"]).reset_index(drop=True)
    reg[cols].to_csv(OUT / "v4_team_entry_registry.csv", index=False)

    # ---------------- pair accounting ----------------
    q = reg[reg.qualifying_participant].copy()
    q["old_g"] = q.old_group_identity.replace("", pd.NA)
    old_p = pairs(q.dropna(subset=["old_g"]), "old_g")
    new_p = pairs(q[q.merge_into_canonical == "TRUE"], "canonical_engineering_team")
    lost = new_p - old_p
    spurious_api = old_p - new_p
    q["r51"] = q.r5_1_inventory_team_year_id
    r51_years = sorted(r51.year.unique())
    r51_p = pairs(q[q.year.isin(r51_years) & (q.r51 != "")], "r51")
    new_p_r51yrs = {p for p in new_p if p[0] in r51_years}
    aff_rows = []
    for y, a, b, rel, conf, note in AFFILIATIONS:
        ca = q[(q.year == y) & (q.canonical_engineering_team == a)].car_key.tolist()
        cb = q[(q.year == y) & (q.canonical_engineering_team == b)].car_key.tolist()
        aff_rows.append(dict(year=y, team_a=a, team_b=b, relationship_type=rel, confidence=conf,
                             cars_a="|".join(ca), cars_b="|".join(cb), cross_pairs=len(ca) * len(cb), notes=note))
    aff = pd.DataFrame(aff_rows)
    aff.to_csv(OUT / "v4_team_affiliation_links.csv", index=False)

    pair_rows = []
    drv = {(y, c): d for y, c, d in zip(q.year, q.car_key, q.driver)}
    can = {(y, c): t for y, c, t in zip(q.year, q.car_key, q.canonical_engineering_team)}
    for y, a, b in sorted(new_p | old_p | r51_p):
        pair_rows.append(dict(year=y, car_a=a, driver_a=drv[(y, a)], car_b=b, driver_b=drv[(y, b)],
                              canonical_team=can[(y, a)] if can[(y, a)] == can[(y, b)] else "",
                              in_v4_strict=(y, a, b) in new_p, in_old_api_label_grouping=(y, a, b) in old_p,
                              in_r5_1_inventory=(y, a, b) in r51_p if y in r51_years else pd.NA,
                              status=("RECOVERED_FALSE_SPLIT" if (y, a, b) in lost else
                                      "SPURIOUS_IN_OLD_GROUPING" if (y, a, b) not in new_p else "UNCHANGED")))
    pairs_df = pd.DataFrame(pair_rows)
    pairs_df.to_csv(OUT / "v4_teammate_pair_changes.csv", index=False)

    # ---------------- audit ----------------
    audit = []
    for (y, raw, old), g in reg.groupby(["year", "raw_entry_name", "old_group_identity"], sort=True):
        r = g.iloc[0]
        canon = r.canonical_engineering_team
        cars_new = set(q[(q.year == y) & (q.canonical_engineering_team == canon) & (q.merge_into_canonical == "TRUE")].car_key)
        cars_old = set(q[(q.year == y) & (q.old_group_identity == old)].car_key) if old else set()
        gq = g[g.qualifying_participant]
        if r.relationship_type == "TECHNICAL_PARTNERSHIP":
            status, reason = "POSSIBLE_AFFILIATION", f"Technical partnership ({r.affiliated_with}); kept as separate engineering team."
        elif any((y, c) in NOT_EQUIVALENT for c in g.car_key):
            status, reason = "NOT_EQUIVALENT", NOT_EQUIVALENT[next((y, c) for c in g.car_key if (y, c) in NOT_EQUIVALENT)]
        elif r.normalization_confidence != "HIGH":
            status, reason = "REQUIRES_REVIEW", "Merge proposed at below-HIGH confidence."
        elif gq.empty:
            status, reason = "UNCHANGED", "Entry did not take part in qualifying (listed driver replaced / race-only); no teammate effect."
        elif not old:
            status, reason = "REQUIRES_REVIEW", "No matching API/project label found for this car-driver."
        elif cars_old < cars_new:
            status, reason = "FALSE_SPLIT_CORRECTED", (f"Old label grouped cars {sorted(cars_old)} separately; canonical {canon} "
                                                        f"groups {sorted(cars_new)}.")
        elif cars_old == cars_new:
            status, reason = "UNCHANGED", "Old label group already equals canonical team membership."
        else:
            status, reason = "REQUIRES_REVIEW", f"Old group {sorted(cars_old)} not a subset of canonical {sorted(cars_new)}."
        if r.old_label_anachronistic and status in ("UNCHANGED", "FALSE_SPLIT_CORRECTED"):
            reason += " Old API label is anachronistic for this year (period-correct name restored; grouping effect as stated)."
        audit.append(dict(year=y, raw_team_or_entry=raw, old_group_identity=old or "(none)",
                          new_canonical_team=canon, merge_status=status, reason=reason,
                          confidence=r.normalization_confidence, relationship_type=r.relationship_type,
                          cars="|".join(g.car_key), drivers="|".join(g.driver),
                          source=r.primary_source + ("; " + r.secondary_source if r.secondary_source else ""),
                          rule_id=r.rule_id, audit_scope="API_LABEL_VS_V4"))
    # the r5_1 teammate inventory's own groups (existing project grouping actually used)
    for (y, tid), g in r51.groupby(["year", "team_year_id"]):
        cars = set(g.car_key)
        canon_sets = q[(q.year == y) & q.car_key.isin(cars)].groupby("canonical_engineering_team").car_key.apply(set)
        if tid.endswith("|UNKNOWN"):
            status = "FALSE_MERGE_IN_OLD_GROUPING"
            reason = (f"team_name missing for {y} in r5_1 inputs; team_name.fillna('UNKNOWN') placed all {len(cars)} cars in one group, "
                      f"treating {len(canon_sets)} different canonical teams as teammates.")
        else:
            full = [set(q[(q.year == y) & (q.canonical_engineering_team == c) & (q.merge_into_canonical == 'TRUE')].car_key) for c in canon_sets.index]
            if len(canon_sets) == 1 and cars == full[0]:
                status, reason = "UNCHANGED", "r5_1 group equals canonical team membership."
            elif len(canon_sets) == 1:
                status, reason = "FALSE_SPLIT_CORRECTED", f"r5_1 group {sorted(cars)} is a fragment of {canon_sets.index[0]} {sorted(full[0])}."
            else:
                status, reason = "REQUIRES_REVIEW", "r5_1 group spans several canonical teams."
        audit.append(dict(year=y, raw_team_or_entry=tid.split("|", 1)[1], old_group_identity=tid,
                          new_canonical_team="|".join(canon_sets.index), merge_status=status, reason=reason,
                          confidence="HIGH", relationship_type="", cars="|".join(sorted(cars)), drivers="|".join(g.driver_name),
                          source="r5_1/output/team_year_control_inventory_v1.csv", rule_id="", audit_scope="R5_1_TEAMMATE_INVENTORY"))
    audit = pd.DataFrame(audit)
    audit.to_csv(OUT / "v4_team_normalization_audit.csv", index=False)
    anomalies.to_csv(OUT / "v4_api_record_anomalies.csv", index=False)

    # ---------------- summary numbers for report ----------------
    summ = {
        "registry_rows": len(reg),
        "qualifying_participant_rows": int(q.shape[0]),
        "raw_official_labels_distinct_strings": reg.raw_entry_name.nunique(),
        "raw_official_labels_year_label": reg.groupby(["year", "raw_entry_name"]).ngroups,
        "old_api_labels_distinct_strings": q.old_group_identity.nunique(),
        "old_api_labels_year_label": q.groupby(["year", "old_group_identity"]).ngroups,
        "canonical_teams_distinct": reg.canonical_engineering_team.nunique(),
        "canonical_team_years": reg.groupby(["year", "canonical_engineering_team"]).ngroups,
        "pairs_v4_strict": len(new_p), "pairs_old_api": len(old_p), "pairs_lost_recovered": len(lost),
        "pairs_spurious_old_api": len(spurious_api),
        "r5_1_years": r51_years, "pairs_r5_1": len(r51_p), "pairs_v4_strict_in_r5_1_years": len(new_p_r51yrs),
        "pairs_r5_1_spurious": len(r51_p - new_p), "pairs_r5_1_missing": len(new_p_r51yrs - r51_p),
        "affiliation_cross_pairs": int(aff.cross_pairs.sum()),
    }
    for k, v in summ.items():
        print(f"{k}: {v}")
    print(audit.groupby(["audit_scope", "merge_status"]).size().to_string())
    return reg, audit, pairs_df, aff, anomalies, summ


if __name__ == "__main__":
    main()
