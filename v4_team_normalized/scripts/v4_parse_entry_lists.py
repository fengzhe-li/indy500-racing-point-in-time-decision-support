"""Parse official INDYCAR/IMS Indianapolis 500 entry-list PDFs (layout text) into rows.

Raw strings are preserved exactly as printed; no normalisation happens here.
"""
import re
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence" / "entry_lists"
OUT = ROOT / "output"

SOURCES = {
    2018: ("http://www.imscdn.com/indycar_media/documents/2018-05-04/Indy%20500%20Entry%20List%205-3.pdf", "5/3/2018"),
    2019: ("http://www.imscdn.com/indycar_media/documents/2019-05-13/Indy%20500%20Entry%20List%205-13.pdf", "5/13/2019"),
    2020: ("http://www.imscdn.com/indycar_media/documents/2020-08-10/indycar-entrylist-indianapolis%20500.pdf", "8/10/2020"),
    2021: ("http://www.imscdn.com/indycar_media/documents/2021-05-12/indycar-entrylist-indianapolis%20500.pdf", "5/10/2021"),
    2022: ("https://digbza2f4g9qo.cloudfront.net/-/media/Files/2022/INDYCAR/06-500/indycar-entrylist", None),
    2023: ("https://www.indycar.com/-/media/Files/2023/NICS/06-500/indycar-entrylist.pdf", "5/15/2023"),
    2024: ("https://www.indycar.com/-/media/Files/2024/NICS/06-500/indycar-entrylist-V1-2024Indy500.pdf", None),
    2025: ("https://www.indycar.com/-/media/Files/2025/NICS/06-500/indycar-entrylist-2025Indy500.pdf", None),
}
# 2018/2019 layout: CarName, Engine, Entrant. 2020+: CarName, Team, Engine.
ENGINE_FIRST = {2018, 2019}
ENGINES = {"Chevrolet", "Honda", "Hond"}


def parse_year(year):
    pdf = EVID / f"{year}_indy500_entry_list.pdf"
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    issued = re.search(r"Issued:\s*([0-9/]+)", txt)
    rows = []
    for line in txt.splitlines():
        m = re.match(r"^\s*(\d{1,2})\s+(0?\d{1,2})\s+(\S.*)$", line)
        if not m:
            continue
        rank, car, rest = m.groups()
        parts = [p.strip() for p in re.split(r"\s{2,}", rest.strip()) if p.strip()]
        if len(parts) != 5:
            raise ValueError(f"{year}: unexpected field count {len(parts)} in line: {line!r}")
        driver, hometown, car_name, a, b = parts
        engine, team = (a, b) if year in ENGINE_FIRST else (b, a)
        if engine not in ENGINES:
            raise ValueError(f"{year}: engine column parse failed: {line!r}")
        rookie = "(R)" in driver
        winner = "(W)" in driver
        rows.append({
            "year": year,
            "entry_list_rank": int(rank),
            "car_number": car,
            "driver_as_listed": driver,
            "driver": re.sub(r"\s*\((R|W)\)", "", driver).replace('"Matt" ', "").strip(),
            "hometown": hometown,
            "car_name_as_listed": car_name,
            "entrant_or_team_as_listed": team,
            "engine": "Honda" if engine.startswith("Hond") else engine,
            "rookie_flag": rookie,
            "past_winner_flag": winner,
            "entry_list_issued": issued.group(1) if issued else SOURCES[year][1],
            "entry_list_column_label": "Entrant" if year in ENGINE_FIRST else "TEAM",
            "source_url": SOURCES[year][0],
            "source_file": f"v4_team_normalized/evidence/entry_lists/{pdf.name}",
        })
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    df = pd.DataFrame([r for y in sorted(SOURCES) for r in parse_year(y)])
    df.to_csv(OUT / "v4_official_entry_lists_parsed.csv", index=False)
    print(df.groupby("year").size().to_string())
    return df


if __name__ == "__main__":
    main()
