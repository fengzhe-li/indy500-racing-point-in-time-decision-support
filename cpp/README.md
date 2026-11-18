# C++17 point-in-time performance engine

[Project overview](../README.md) · [V3 application](../v3_point_in_time/README.md)

While the existing Python stack (`pipeline/`, `weather/`, `v3_point_in_time/`) remains the authoritative reference implementation for historical ingestion, replay orchestration and FastAPI serving, the [`cpp/`](../cpp/) directory provides an additive **C++17 computational module** (`indy500_pit_engine`) that reimplements the core point-in-time temporal guards, time-series observation filtering and physical-response calculations in native C++ with optional `pybind11` bindings.

### Why C++ was introduced and what it implements

In live or high-frequency replay motorsport environments, repeated timestamp parsing, point-in-time eligibility filtering over weather/telemetry streams and physical-model evaluation lie on the inner computational loop. The C++17 module (`cpp/include/indy500/pit_engine.hpp`, `cpp/src/pit_engine.cpp`) implements:

1. **ISO-8601 UTC parsing & hard Point-in-Time leakage guard** (`parse_iso8601_utc`, `check_point_in_time`, `enforce_point_in_time`) — proleptic Gregorian calendar conversion supporting `Z` and `±HH:MM` offsets and enforcing `known_at <= decision_time` and `forecast.issue_time <= decision_time` with identical reason codes to [`v3_point_in_time/src/point_in_time_guard.py`](../v3_point_in_time/src/point_in_time_guard.py).
2. **Timestamp-aware racing time-series filtering & thermal rate calculation** (`filter_observations_at_cutoff`, `compute_point_in_time_thermal_rate`) — filters out post-cutoff or unknown-timestamp observations, deterministically sorts unsorted input streams by `(observed_at, known_at, id)`, validates finite numerical values and computes the 10–20 minute lookback track heating/cooling rate (°C/min) matching [`weather/scripts/v2_build_future_track_samples.py`](../weather/scripts/v2_build_future_track_samples.py).
3. **Point-in-time Forecast Vintage Store** (`ForecastVintageStore`) — pre-parses nominal cycle and valid timestamps on insertion, strictly excludes vintages where `issue_time > decision_time`, prefers the freshest eligible model run and breaks ties by smallest `|valid_time - target_time|` and lexicographical `forecast_id`, matching [`v3_point_in_time/src/forecast_vintage_store.py`](../v3_point_in_time/src/forecast_vintage_store.py).
4. **Validated domain calculations (`FINAL_V2` / `FINAL_V3`)** — NOAA-style solar elevation geometry (`solar_elevation_deg`), horizon applicability gating (`evaluate_applicability`), the frozen `M2b_mean_solar` track-temperature model paired with the zero-intercept physical speed response (`evaluate_physical_response`: $\Delta v_{\text{physical}} = \beta_{\text{track}}\Delta T_{\text{track}} + \beta_{\text{ambient}}\Delta T_{\text{ambient}}$) and NumPy-compatible linear quantile summarization (`summarize_draws`, `evaluate_monte_carlo_draws`, `run_monte_carlo_inference`).

### Preserving Point-in-Time correctness

- **Fail-closed temporal boundary:** Any observation or forecast vintage stamped even 1 second after `decision_time` (`> decision_time`) is rejected or excluded; exact boundary equality (`== decision_time`) is permitted.
- **Deterministic unsorted-input handling:** Unsorted observation vectors and forecast vintage lists are explicitly ordered using deterministic tie-breaking rules so arbitrary input permutations yield identical outputs.
- **Strict input validation:** Empty observation series, malformed calendar dates (e.g. non-leap `2021-02-29`), `NaN`/`Inf` numerical values and duplicate `(id, observed_at)` or duplicate timestamps raise `indy500::pit::PitEngineError` (`ValueError` in Python).

### Compiling, testing and Python integration

The C++ engine builds with CMake and uses GoogleTest (`cpp/tests/test_pit_engine.cpp`). When `pybind11` is installed, CMake also compiles `_indy500_pit_cpp` (`cpp/bindings/pybind_module.cpp`). The Python bridge [`v3_point_in_time/src/cpp_pit_bridge.py`](../v3_point_in_time/src/cpp_pit_bridge.py) loads the native extension when present and falls back transparently to the pure-Python implementation when unbuilt, keeping all existing FastAPI and V3 workflows backward-compatible without mandatory native build dependencies.

```bash
# Configure, build C++17 static library + GoogleTest runner + pybind11 module, and run CTest
cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build cpp/build -j4
ctest --test-dir cpp/build --output-on-failure -V   # 16 C++ GoogleTest tests

# Run Python <-> C++ parity and fallback tests
python3 -m unittest discover -s v3_point_in_time/tests -p 'test_cpp_*.py' -v   # 12 parity/regression tests
```

### Verification and benchmark results

- **C++ GoogleTest suite:** **16/16 PASS**, including temporal boundary equality, +1s future leakage rejection, `None` (`std::nullopt`) vs empty/whitespace timestamp validation, unsorted permutation determinism, `NaN`/`Inf`/duplicate/empty error handling and exact numerical parity (`1e-12` tolerance) across all **656** frozen rows in `future_track_samples_with_solar_v1.csv`.
- **Python↔C++ parity suite:** **12/12 PASS** (`test_cpp_engine_parity.py`), verifying exact parity on real 2020–2024 HRRR forecast vintage selection (259 rows), 2020 PTSC track-temperature rate lookback, applicability gating, empty/whitespace/malformed timestamps, non-finite values, structured `PointInTimeViolation` exceptions (`.reasons` and `.code`), API naming compatibility, 5-horizon Monte Carlo draw summarization (`1e-12` agreement with NumPy when given identical draws) and statistical agreement between standalone C++ (`std::mt19937_64`) and Python (`NumPy PCG64`) Monte Carlo streams.
- **Measured component microbenchmarks (macOS arm64, Apple clang 21.0.0 `-O3`, Python 3.14.5, median of 9 warm runs on identical inputs and outputs):**

  `ForecastVintageStore` parses and stores timestamp strings as integer epochs when each C++ record is added (**0.19 ms** one-time initialization for 259 HRRR records), whereas the unmodified Python reference (`ForecastVintageStore.select`) parses timestamp strings during each `select()` call. A pre-parsed Python baseline (pre-parsing the 259 timestamps once in **0.12 ms**) is also reported below for an apples-to-apples algorithmic comparison. These are component-level microbenchmarks, not measurements of FastAPI or end-to-end application acceleration. The C++ engine is an additive computational extension; Python remains the authoritative application implementation, and historical replay and scenario API routes do not execute the C++ engine in their normal request paths.

| Operation | Workload | Python reference | Pre-parsed Python baseline | C++17 (`_indy500_pit_cpp`) | Speedup vs Python ref (vs pre-parsed) |
|---|---|---:|---:|---:|---:|
| `solar_elevation_deg` | 6,560 calls (656 real timestamps × 10) | 10.49 ms | — | 0.87 ms (direct) / 5.04 ms (bridge) | **12.1×** (direct) / **2.1×** (bridge) |
| `ForecastVintageStore.select` (query only) | 100 point-in-time queries over 259 real HRRR rows | 6.68 ms | 0.76 ms | 0.034 ms | **196.5×** (**22.4×**) |
| `ForecastVintageStore` (259-row init + 100 queries) | 1 store build + 100 point-in-time queries | 6.68 ms | 0.88 ms (0.12 + 0.76 ms) | 0.224 ms (0.19 + 0.034 ms) | **29.8×** (**3.9×**) |
| `check_point_in_time` | 10,000 leakage-guard evaluations | 12.01 ms | — | 2.45 ms (direct) | **4.9×** |

