"""Python/JSON contract. Regenerate: python3 -m v5_lap_time_simulation.schema."""
import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict


class Segment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    distance_m: float
    radius_m: float | None
    banking_deg: float
    evidence_class: str
    start_m: float
    time_s: float
    label_xy_m: tuple[float, float]


class ReplayResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    schema_version: Literal["v5-replay-1"]
    units: dict[str, str]
    provenance: dict[str, str]
    origin: str
    vehicle: dict[str, float]
    environment: dict[str, float | None]
    lap_time_s: float
    track_length_m: float
    average_speed_mph: float
    segments: list[Segment]
    distance_m: list[float]
    elapsed_s: list[float]
    speed_mps: list[float]
    speed_cap_mps: list[float]
    acceleration_mps2: list[float]
    mode: list[Literal["acceleration", "braking", "corner_cap", "steady_or_transition"]]
    xy_m: list[tuple[float, float]]


if __name__ == "__main__":
    target = Path(__file__).parent / "schema" / "replay.schema.json"
    target.write_text(json.dumps(ReplayResponse.model_json_schema(), indent=2) + "\n")
