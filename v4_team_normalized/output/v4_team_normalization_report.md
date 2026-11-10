# V4 Team Normalisation Report (Phases 1–2)

Branch `v4-team-normalized-evidence`, which starts from the frozen tag `v3-frozen-pre-team-normalization-v4` (`a8bb519`).
Scope: Indianapolis 500 years 2018–2025. No V2/V3 artefact was modified.

## Method in one paragraph

Each year's team identity comes from that year's **official INDYCAR/IMS Indianapolis 500 entry-list PDF** (8/8 years found and archived in `evidence/entry_lists/`). Each exact entrant/team string maps to a canonical engineering team through an explicit rule in `manual/v4_team_mapping_rules.csv` (51 rules). Every rule names its source and its relationship type. No string similarity is used; an unmatched or doubly-matched label stops the build with an error. Where an official label is a partnership, a separate source was checked to find who actually ran the car. Technical partnerships are **never** merged. Driver changes after each list was issued were reconciled against the project's official session records. The "old" identity is the INDYCAR API `TeamName` that the existing project uses as `team_name`.

## Key finding before the numbers: the old labels are not period-correct

The API `TeamName` applies later organisation names to earlier seasons. **28 of 274 qualifying car-entries** carry an anachronistic label (2018–2023). Examples:

| Year | Car | API label (used by project) | Official entry list |
|---|---|---|---|
| 2018 | #88 Chaves | Andretti Steinbrenner Autosport | **Harding Racing** (no Andretti link) |
| 2018 | #5/#6 | Arrow McLaren | Schmidt Peterson Motorsports |
| 2019 | #88 Herta | Andretti Steinbrenner Autosport | **Harding Steinbrenner Racing** (independent; Andretti technical support only) |
| 2020 | #55 Palou | Dale Coyne Racing with RWR | Dale Coyne Racing with Team Goh |
| 2021–23 | #06 Castroneves | Meyer Shank w/ Curb-Agajanian | Meyer Shank Racing |

So normalising *from the API labels* would be unsafe. For example, it would wrongly merge the 2018 Harding car into Andretti. V4 therefore normalises from the period-correct entry lists.

## 1. How many raw entrant/team labels existed?

| Label set | Distinct strings | Distinct (year, label) |
|---|---|---|
| Official entry-list entrant/team labels | **59** | **136** |
| Old API labels used by the project (qualifying participants) | 33 | 135 |

## 2. How many canonical engineering teams after normalisation?

**21** canonical engineering teams (lineage-stable IDs, e.g. SPM → Arrow McLaren SP → Arrow McLaren = `ARROW_MCLAREN_SPM`), giving **101** team-years (11–16 per year).

Relationship types across the 276 registry rows: FULL_TEAM_ENTRY 226, JOINT_ENTRY 46, TECHNICAL_PARTNERSHIP 4. Confidence: HIGH 272, MEDIUM 4.

## 3. How many false organisational splits were found?

**22 canonical team-years** were split across more than one old label, producing **34 extra fragments**. These are the 56 `FALSE_SPLIT_CORRECTED` rows in the audit (each fragment and its core label are both marked).

A second problem, a **false merge**, was found in the existing teammate inventory `r5_1/output/team_year_control_inventory_v1.csv`. `team_name` is missing for 2023 and 2024 there, and `team_name.fillna('UNKNOWN')` put **all 34 cars of each year into one "team"**. That makes 1,122 teammate pairs where V4 finds 80 (**1,042 spurious pairs**). It also left 39 real pairs missing in 2020–2022. This inventory is a data-assembly output; no frozen model reads it. It was not modified.

## 4. Which years were most affected?

| Year | Fragmented team-years | Extra fragments | Teammate pairs recovered | Strict V4 pairs (old API-label pairs) |
|---|---|---|---|---|
| 2018 | 4 | 5 | 14 | 42 (28) |
| 2019 | 3 | 4 | 9 | 34 (25) |
| 2020 | 3 | 5 | 14 | 40 (26) |
| 2021 | 3 | 5 | 14 | 44 (30) |
| 2022 | 3 | 5 | 11 | 38 (27) |
| 2023 | 3 | 5 | 11 | 39 (28) |
| 2024 | 2 | 3 | 7 | 41 (34) |
| 2025 | 1 | 2 | 5 | 35 (30) |

2018, 2020 and 2021 are the most affected. In the r5_1 inventory, 2023 and 2024 are the most affected by far because of the false merge.

## 5. Which teams were most affected?

| Canonical team | Years fragmented | Extra fragments | Pairs recovered | Cause |
|---|---|---|---|---|
| **ANDRETTI** | all 8 (2018–2025) | 17 | 58 | #98 Andretti Herta, #26 w/ Curb-Agajanian, #29 Andretti Steinbrenner, 2020 #88 Andretti Harding Steinbrenner each had its own label |
| **DALE_COYNE_RACING** | 2018–2023 | 9 | 14 | Every co-entry (Vasser-Sullivan, Thom Burns, Byrd/Belardi, RWR, Team Goh, HMD) had its own label |
| MEYER_SHANK_RACING | 2021–2024 | 4 | 5 | #06 labelled "Meyer Shank w/ Curb-Agajanian" |
| RAHAL_LETTERMAN_LANIGAN | 2018, 2020 | 2 | 4 | Scuderia Corsa w/ RLL (2018), RLL w/ Citrone/Buhl (2020) |
| AJ_FOYT | 2018 | 1 | 2 | Foyt with Byrd/Hollinger/Belardi |
| ARROW_MCLAREN_SPM | 2019 | 1 | 2 | MotoGator Team Stange w/ Arrow SPM |

The Herta/Marco example is confirmed: in every year 2020–2025, Colton Herta and Marco Andretti had different labels and were never paired.

## 6. How many potential teammate relationships were previously lost?

- **85 of 313** strict V4 teammate pairs (27%) were missing under the old API-label grouping, 2018–2025. The old grouping had **no spurious** pairs; every old pair is also a V4 pair.
- In the r5_1 teammate inventory (2020–2024): 39 real pairs missing (2020–2022), plus 1,042 spurious pairs (2023–2024).
- Separately, 46 cross-team pairs are linked only through technical partnerships (`v4_team_affiliation_links.csv`). They are **excluded** from the strict layer.

Pair-level detail: `v4_teammate_pair_changes.csv`.

## 7. Which mappings remain uncertain?

**Kept separate (TECHNICAL_PARTNERSHIP, MEDIUM, `POSSIBLE_AFFILIATION`); none is merged:**

| Year | Entry | Possible affiliation | Evidence |
|---|---|---|---|
| 2018 | #60 Meyer Shank Racing with SPM | SPM | Official label + MSR press/secondary |
| 2019 | #88 Harding Steinbrenner Racing | Andretti (engineering support) | INDYCAR 2018-09-19, Andretti press 2019-09 |
| 2019 | #66 McLaren Racing (Alonso) | Carlin | Secondary knowledge only; no primary document retrieved |
| 2021 | #16 Paretta Autosport | Team Penske | INDYCAR 2021-01-19, RACER |

**Affiliation-only links, not assigned to any entry:** MSR↔Arrow SPM 2019 (secondary), MSR↔Andretti 2020–2021 (Autosport 2021-06-29, secondary), MSR↔Andretti 2022 (**unverified, LOW**).

**Merged at HIGH confidence, but most consequential; explicit sign-off requested:**
- **#98 Andretti Herta (2018–2025) → ANDRETTI.** 33 of the 85 recovered pairs depend on this. The support is the official labels (Andretti-led entrant) and IMS/NBC descriptions of an Andretti Herta subsidiary entry. No document states the crew or engineering structure outright.
- **Dale Coyne co-entries → DALE_COYNE_RACING.** This rests on official labels that name DCR as lead entrant ("Dale Coyne Racing with …"). No separate operator document was retrieved for each co-entry.

**Deliberately not equivalent:** 2018 #88 Harding Racing vs Andretti (API anachronism); 2022 DragonSpeed/Cusick vs DRR-Cusick (they share partner Cusick, not an engineering team).

**API record artefacts (not entries):** seven 2019 single-session records put a driver on the wrong car (e.g. Hinchcliffe on #7/#60/#77 in Practice 1). #5T is Hinchcliffe's backup car. Listed in `v4_api_record_anomalies.csv`.

## Gate for modelling

- **Strict layer:** no mapping is unresolved. Every merge is HIGH confidence, and every uncertain case is kept separate.
- **Before Phase 3, confirm:** (a) the #98 → ANDRETTI merge, and (b) that the four technical partnerships stay out of the strict teammate layer. They may later form an optional "affiliated" sensitivity layer.

## Files

| File | Content |
|---|---|
| `v4_team_entry_registry.csv` | 276 rows: 274 qualifying participants + 1 replaced listed driver (2018 Fittipaldi) + 1 race-only substitute (2023 Rahal #24) |
| `v4_team_normalization_audit.csv` | 141 API-label rows + 53 r5_1-inventory-group rows |
| `v4_teammate_pair_changes.csv` | every pair in V4 strict, old grouping or r5_1 inventory, with status |
| `v4_team_affiliation_links.csv` | non-merged technical/affiliation links |
| `v4_api_record_anomalies.csv` | API records not matching any entry |
| `v4_official_entry_lists_parsed.csv` | verbatim parse of the 8 official PDFs |
