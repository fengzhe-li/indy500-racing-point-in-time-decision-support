"""Isolated local V5 API and production viewer; no V3 routes or stored mutations."""
from dataclasses import replace
from functools import lru_cache
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .model import Environment, Vehicle, build_ims_oval_approximation, simulate_lap
from .replay import replay_payload
from .schema import ReplayResponse

MODULE = Path(__file__).parent


class VehicleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    mass_kg: float | None = Field(None, ge=600, le=1100)
    cd_a_m2: float | None = Field(None, ge=.6, le=1.6)
    cl_a_m2: float | None = Field(None, ge=.5, le=2.5)
    tire_mu: float | None = Field(None, ge=1.1, le=2.2)
    power_w: float | None = Field(None, ge=400000, le=1100000)


class EnvironmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    air_temperature_c: float | None = Field(None, ge=5, le=45)
    track_temperature_c: float | None = Field(None, ge=15, le=65)


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vehicle: VehicleUpdate = Field(default_factory=VehicleUpdate)
    environment: EnvironmentUpdate = Field(default_factory=EnvironmentUpdate)


def create_app(baseline_path: Path = MODULE / "output" / "baseline.json") -> FastAPI:
    # Read only the explicit generated configuration, then recompute with Python.
    config = json.loads(baseline_path.read_text())
    base_vehicle = Vehicle(**config["vehicle"])
    base_environment = Environment(**config["environment"])
    track = build_ims_oval_approximation()
    app = FastAPI(title="V5 engineering replay", version="1")

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, exc):
        # Validation inputs can contain NaN/Infinity after JSON number overflow.
        # Do not echo those values into a strict JSON error response (which 500s).
        detail = [{key: error[key] for key in ("type", "loc", "msg")}
                  for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detail})

    @lru_cache(maxsize=32)
    def compute(request_json: str):
        request = SimulationRequest.model_validate_json(request_json)
        vehicle = replace(base_vehicle, **request.vehicle.model_dump(exclude_none=True))
        environment = replace(base_environment, **request.environment.model_dump(exclude_none=True))
        result = simulate_lap(track, vehicle, environment, ds_m=10)
        return ReplayResponse.model_validate(replay_payload(track, vehicle, environment, result))

    @app.get("/api/v5/baseline", response_model=ReplayResponse)
    def baseline():
        return compute(SimulationRequest().model_dump_json())

    @app.post("/api/v5/simulate", response_model=ReplayResponse)
    def scenario(request: SimulationRequest):
        try:
            return compute(request.model_dump_json())
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    dist = MODULE / "frontend" / "dist"
    if dist.exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="v5-assets")

    @app.get("/", include_in_schema=False)
    def viewer():
        if not (dist / "index.html").exists():
            raise HTTPException(status_code=503, detail="Build frontend first: npm ci && npm run build in v5_lap_time_simulation/frontend")
        return FileResponse(dist / "index.html")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
