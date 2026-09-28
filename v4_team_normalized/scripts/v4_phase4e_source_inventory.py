"""V4 Phase 4E step 1: source inventory (written BEFORE any new retrieval).

Enumerates (a) sources already preserved in the repository and (b) externally recoverable
sources for 2018-2025 Indianapolis 500 sessions. Nothing is downloaded here; header-only size
probes for Timing71 analysis files were done beforehand and are passed in as a CSV.
"""
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "v4_team_normalized" / "output" / "phase4e"
TODAY = "2026-09-28"
YEARS = range(2018, 2026)


def official_sessions():
    d = json.load(open(REPO / "r6_regime_extension/evidence/official_api_v2/season_dropdown_raw.json"))
    rows = []
    for yb in d:
        y = int(yb["Year"])
        if y not in YEARS:
            continue
        for ev in yb["Events"]:
            if "Indianapolis 500" not in ev["EventName"]:
                continue
            for s in ev["Sessions"]:
                rows.append(dict(year=y, event_id=ev["EventID"], event_name=ev["EventName"], session_id=int(s["EventsSessionID"]),
                                 official_session_name=s["SessionName"]))
    return pd.DataFrame(rows)


def main(t71_csv):
    OUT.mkdir(parents=True, exist_ok=True)
    sess = official_sessions()
    local_api = {int(p.stem.split("_")[2]) for p in (REPO / "r6_regime_extension/evidence/official_api_v2").glob("*_session_*_raw.json")}
    rows = []
    # (1) INDYCAR official session list (local)
    rows.append(dict(source_id="INDYCAR_SEASON_DROPDOWN", source_url="https://www.indycar.com/api/results (season dropdown; archived locally)",
                     source_org="INDYCAR", authority="PRIMARY_OFFICIAL", year="2018-2025", session="ALL (session list)", retrieval_date="pre-existing (R6)",
                     local_path="r6_regime_extension/evidence/official_api_v2/season_dropdown_raw.json", local=True, data_format="JSON",
                     machine_readable=True, lap_level=False, timestamped=False, complete="session names/IDs for every event",
                     known_limitations="no dates, no results; list only"))
    # (2) INDYCAR official per-session details
    for r in sess.itertuples(index=False):
        loc_ = r.session_id in local_api
        rows.append(dict(source_id=f"INDYCAR_SESSION_DETAILS_{r.session_id}", source_url=f"https://www.indycar.com/api/results/EventsSessionDetails?id={r.session_id}",
                         source_org="INDYCAR", authority="PRIMARY_OFFICIAL", year=r.year, session=r.official_session_name,
                         retrieval_date="pre-existing (R6)" if loc_ else "NOT YET RETRIEVED", official_session_id=r.session_id,
                         local_path=(f"r6_regime_extension/evidence/official_api_v2/{r.year}_session_{r.session_id}_raw.json" if loc_ else ""),
                         local=loc_, data_format="JSON", machine_readable=True, lap_level=False, timestamped=False,
                         complete="one record per car: best lap/speed, laps complete, status; session date; report links",
                         known_limitations="session-level only; no lap timestamps; DriverName/TeamName fields can be retroactive (Phase 1)"))
        rows.append(dict(source_id=f"INDYCAR_SECTION_RESULTS_PDF_{r.session_id}", source_url="https://www.imscdn.com/INDYCAR/Documents/<id>/... (URL in SessionReports of the session JSON)",
                         source_org="INDYCAR", authority="PRIMARY_OFFICIAL", year=r.year, session=r.official_session_name,
                         retrieval_date="local only for Day 1 2018/2019/2025 and 2020-2024 Day 1 section PDFs" if "Day 1" in r.official_session_name else "NOT RETRIEVED",
                         official_session_id=r.session_id, local_path="", local="Day 1" in r.official_session_name, data_format="PDF",
                         machine_readable=False, lap_level=True, timestamped="session elapsed time per lap (qualifying top-section parse proven in R6)",
                         complete="every car, every timed lap, section times", known_limitations="PDF parsing required (large); not ingested in Phase 4E"))
    # (3) Official Day-1 JSON 2020-2024 (evidence/)
    for y in range(2020, 2025):
        rows.append(dict(source_id=f"INDYCAR_DAY1_JSON_{y}", source_url="INDYCAR results API (archived)", source_org="INDYCAR", authority="PRIMARY_OFFICIAL",
                         year=y, session="Qualifications - Day 1", retrieval_date="pre-existing", local_path=f"evidence/official_session_{y}.json", local=True,
                         data_format="JSON", machine_readable=True, lap_level=False, timestamped=False, complete="per-car records",
                         known_limitations="session-level"))
    # (4) Curated V1-V4 Day-1 attempt layer
    rows.append(dict(source_id="PROJECT_DAY1_ATTEMPT_LAYER", source_url="(derived) data/canonical/v1 + r4p1 + V4 Phase 3 join", source_org="PROJECT (derived from official + Timing71)",
                     authority="DERIVED", year="2020-2024 (+R6 2018/2019/2025)", session="Qualifications - Day 1", retrieval_date="pre-existing",
                     local_path="v4_team_normalized/output/phase3/team_attempt_join.csv", local=True, data_format="CSV", machine_readable=True,
                     lap_level="four-lap attempt + lap speeds", timestamped="partial (approximate recorder capture / Timing71 match)",
                     complete="all Day-1 attempts; timestamps missing for many", known_limitations="accepted Phase 3 layer; not re-derived here"))
    # (5) Timing71 local captures
    for p, y, note in [("evidence/timing71_2020_part1.zip", 2020, "Day 1 snapshot capture"), ("evidence/timing71_2020_part2.zip", 2020, "Day 1 snapshot capture"),
                       ("evidence/timing71_2021_sample.zip", 2021, "Day 1 snapshot capture"), ("evidence/timing71_2023.zip", 2023, "Day 1 snapshot capture"),
                       ("evidence/timing71_2024.zip", 2024, "Day 1 snapshot capture")]:
        rows.append(dict(source_id=f"T71_LOCAL_{Path(p).stem}", source_url="Timing71 live snapshots (archived)", source_org="Timing71 (third-party capture of INDYCAR live timing)",
                         authority="SECONDARY_TIMING_CAPTURE", year=y, session="Qualifications - Day 1", retrieval_date="pre-existing", local_path=p, local=True,
                         data_format="ZIP of JSON snapshots", machine_readable=True, lap_level=True, timestamped=True, complete=note,
                         known_limitations="Day 1 only; snapshot cadence"))
    for p in sorted((REPO / "r6_regime_extension/evidence/timing71_indy500_v2").glob("*_analysis.json")):
        rows.append(dict(source_id=f"T71_R6_{p.stem}", source_url="https://s3.us-east-005.backblazeb2.com/t71-archive/ (R6 download)", source_org="Timing71",
                         authority="SECONDARY_TIMING_CAPTURE", year=int(p.name[:4]), session="qualifying (R6 selection)", retrieval_date="pre-existing (R6)",
                         local_path=str(p.relative_to(REPO)), local=True, data_format="JSON", machine_readable=True, lap_level=True, timestamped=True,
                         complete="per-car laps/stints", known_limitations="R6 selection only"))
    # (6) Timing71 archive: every Indy 500 session 2018-2025 (external)
    t71 = pd.read_csv(t71_csv)
    for r in t71.itertuples(index=False):
        rows.append(dict(source_id=f"T71_ARCHIVE_{r.id}", source_url=r.analysisFilename, source_org="Timing71 (third-party capture of INDYCAR live timing)",
                         authority="SECONDARY_TIMING_CAPTURE", year=int(r.year), session=r.description, retrieval_date="NOT YET RETRIEVED (HEAD probe only)",
                         local_path="", local=False, data_format="JSON (analysis)", machine_readable=True, lap_level=True, timestamped=True,
                         complete=f"expected: all cars, laps, stints, flags; {int(r.analysis_bytes)} bytes; start {r.start_utc}; duration {int(r.duration)} s",
                         known_limitations="secondary capture; capture gaps possible; team labels are live-feed strings (join by car number to V4 registry)"))
    rows.append(dict(source_id="T71_ARCHIVE_2022", source_url="(none found in Timing71 archive listing)", source_org="Timing71", authority="SECONDARY_TIMING_CAPTURE",
                     year=2022, session="ALL", retrieval_date="probe only", local=False, data_format="", machine_readable=False, lap_level=False, timestamped=False,
                     complete="NO 2022 Indy 500 replays in the archive listing", known_limitations="2022 lap-level data only via official PDFs"))
    # (7) Weather
    rows.append(dict(source_id="FIRESTONE_PTSC_ARCHIVE", source_url="Firestone / IMS track-temperature archive workbook (archived)", source_org="Firestone (PTSC)",
                     authority="PRIMARY_OBSERVATION", year="2007-2026", session="event days", retrieval_date="pre-existing",
                     local_path="weather/evidence/ptsc/FirestoneTemperatures_current.xlsx", local=True, data_format="XLSX", machine_readable=True, lap_level=False,
                     timestamped="~15-min observations", complete="Indy 500 event days present for 2018-2025 (practice/qual/carb/race dates)",
                     known_limitations="only Day 1 extracted so far; 2021+ sheets are block-formatted; wind units unverified"))
    rows.append(dict(source_id="HRRR_ISSUE_GATED", source_url="NOAA HRRR archive (project HRRR pipeline)", source_org="NOAA", authority="MODEL_FORECAST",
                     year="2020-2024", session="Day 1 only (local)", retrieval_date="pre-existing", local_path="weather/output/ (HRRR joins)", local=True,
                     data_format="GRIB2 idx / CSV", machine_readable=True, lap_level=False, timestamped=True, complete="Day 1 only",
                     known_limitations="other days recoverable externally, not retrieved"))
    # (8) Fast Friday material
    for p in sorted((REPO / "r4/evidence/fast_friday").glob("*.*")):
        rows.append(dict(source_id=f"FASTFRIDAY_{p.stem}", source_url="INDYCAR/IMS (archived)", source_org="INDYCAR", authority="PRIMARY_OFFICIAL",
                         year=int(p.name[:4]), session="Fast Friday practice", retrieval_date="pre-existing", local_path=str(p.relative_to(REPO)), local=True,
                         data_format=p.suffix[1:].upper(), machine_readable=p.suffix == ".html", lap_level=p.suffix == ".pdf", timestamped=False,
                         complete="results/editorial", known_limitations="session results; lap-level only in PDFs"))
    inv = pd.DataFrame(rows)
    inv.to_csv(OUT / "source_inventory.csv", index=False)
    print(inv.groupby(["authority", "local"]).size().to_string())


if __name__ == "__main__":
    main(sys.argv[1])
