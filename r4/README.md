# R4 Stochastic Strategic Decision Simulator

## Status

This directory is an engineering scaffold. It defines state, configuration, component interfaces, orchestration, provenance-safe R3C1 input access, and reproducibility checks. It contains no research-approved stochastic parameter values and must not be used for substantive strategy simulation yet.

R4A adds a validated pit-wall scenario layer. [`observable_scenario.schema.json`](state/observable_scenario.schema.json) and `ObservableScenario` require field-level availability and provenance. `ScenarioLoader` accepts manual JSON or overlays only temporally admissible fields from the frozen R3C1 state asset. It returns `ObservablePitWallState`, a read-only extension of `PitWallState` that carries the full decision context, target, and provenance into later plugins.

The three supported actions are:

- `STOP_RETAIN_CURRENT_RESULT`
- `REPEAT_LANE2_RETAIN_CURRENT_RESULT`
- `REPEAT_LANE1_WITHDRAW_CURRENT_RESULT`

## Module boundaries

- `state/` owns the canonical `PitWallState` dataclass and matching JSON Schema. Unknown state remains explicit; queue observations are never inferred from time gaps or result order.
- `queue/` defines the queue-evolution and wait-time model interface.
- `environment/` defines the future-environment model interface. It does not construct track temperature from air temperature.
- `performance/` defines the repeat-performance model interface and the hash-verifying, read-only R3C1 adapter.
- `competitors/` defines the competitor action/performance interface.
- `simulator/` defines actions, shared sampled-result types, interruption, leaderboard, utility interfaces, deterministic component seed streams, and the top-level Monte Carlo runner.
- `config/` contains the configuration loader and an intentionally unconfigured JSON template.
- `output/` is reserved for additive R4 outputs. It must never be used to overwrite R3C1 assets.
- `tests/` exercises schema completeness, explicit unconfigured failures, deterministic seeding, orchestration order, and R3C1 hash verification with interface-only test doubles.

## Orchestration contract

For every requested action and trial, `MonteCarloRunner` invokes the configured components in this order:

1. queue evolution;
2. waiting time;
3. interruption/random shock;
4. future environment;
5. repeat performance;
6. competitor actions/performance;
7. future leaderboard update;
8. utility and risk-profile evaluation.

The trial record exposes final rank, final speed, success, and downside fields. Their values may remain `None` until the responsible research definitions and models are configured.

Each action/trial/component receives an independent random stream derived from the master seed with SHA256. This makes results repeatable and prevents action iteration order from changing a component stream.

## Configuration policy

[`stochastic_parameters.template.json`](config/stochastic_parameters.template.json) deliberately sets every model implementation to `NOT_CONFIGURED`, every stochastic parameter object to `null`, and the trial count, seed, success/downside definitions, utility function, risk profiles, and decision thresholds to `null`. Default component implementations raise `NotConfiguredError` with the missing component name.

Stochastic parameter values, distributions, competitor policies, queue behavior, weather effects, tire effects, utility definitions, risk profiles, and decision thresholds will be supplied in a later research-design step. Existing R3C1 Monte Carlo values are reference outputs and are not automatically imported as R4 assumptions.

## R4A information classes

- **Observable state** is directly available by the decision moment or deterministically derived from such information. It uses `OBSERVED` or `DERIVED_FROM_OBSERVABLES`, and its availability timestamp cannot be later than the decision timestamp.
- **Forecast state** was issued and available by the decision moment. It uses `FORECAST_AVAILABLE_AT_DECISION_TIME`; a later forecast-valid time remains explicit and must never be replaced by realized future weather.
- **Stochastic future state** is produced after the decision by configured R4 plugins. It does not belong in an R4A scenario input, and no stochastic future model is configured in this phase.
- **Latent/unobservable state** includes unrecovered queue wait, future competitor actions, track-grip truth, tire-temperature truth, and other information unavailable at the decision moment. It stays `UNKNOWN` and is never silently imputed.

Every R4A data field uses the same provenance envelope: `value`, `availability`, `available_at_utc`, `valid_at_utc`, `source_reference`, and `derivation`. `UNKNOWN` requires a null value and null timestamps. Observed or derived values with a future validity timestamp are rejected; a decision-time-available forecast is the only input allowed to carry a later forecast-valid time.

The primary comparison reference is `current_result_reference`: the driver's current valid speed, rank, and validity. An `advancement_benchmark` is a separately provenanced, qualifying-format-regime boundary such as Fast Nine, Top 12, or Fast Six. It is not a fixed team objective, and no rank is universal or hard-coded. The old `target_rank`, `IMPROVE_CURRENT_SPEED`, and `REACH_TARGET_RANK` terms are rejected with explicit deprecation errors rather than silently reinterpreted.

The corrected target definitions are `BEAT_CURRENT_RESULT`, `CROSS_ADVANCEMENT_BENCHMARK`, `IMPROVE_RANK`, `REMAIN_ABOVE_CUTOFF`, and `MAXIMIZE_EXPECTED_RANK`. The reserved later output names are `P_BEAT_CURRENT_RESULT`, `P_CROSS_ADVANCEMENT_BENCHMARK`, `P_IMPROVE_RANK`, `P_FINISH_WORSE_THAN_CURRENT_RESULT`, and `P_COMPLETE_BEFORE_SESSION_END`. R4P0 defines names and references only; it computes none of these probabilities.

## R4P0 bounded data audit

`run_r4p0_audit.py` reads existing canonical, timing, HRRR, PTSC, and frozen R3C1 summary assets and writes five compact audit files to `output/`. Fixed 5/10/15/20-minute bins use only existing performance-grade point timestamps and complete four-lap speeds. Bounded intervals remain separate and are never converted to midpoint timestamps. Result-row order is not treated as chronology, and the audit does not infer queue state or track evolution.

[`observable_scenario.template.json`](config/observable_scenario.template.json) is a human-readable placeholder template. Every angle-bracket placeholder must be replaced with a correctly typed value and provenance before loading; the untouched template is intentionally not executable.

## R3C1 read-only inputs

`R3C1ReadOnlyAdapter` reads the active project's [`final_results_freeze_manifest_v1.csv`](../weather/output/final_results_freeze_manifest_v1.csv) and accepts only assets listed there. Before use, it verifies all 13 declared SHA256 hashes. The current manifest references:

- `decision_time_observable_state_v4_1_final.csv`
- `r3c_action_historical_applicability_v1.csv`
- `r3c_final_monte_carlo_action_envelope_v2.csv`
- `r3b4_monte_carlo_performance_decision_envelope_v1.json`
- `r3b3_performance_environment_sensitivity_v1.json`
- `repeat_performance_recovery_probability_v1.csv`
- `r3b3_repeat_pair_environment_dataset_v1.csv`
- `r3b_timed_subset_coverage_v1.csv`
- `final_supported_claims_v1.csv`
- `final_limitations_v1.csv`
- `final_core_results_v1.csv`
- `final_capability_summary_v1.json`
- `final_results_freeze_v1_qa.csv`

The adapter opens these inputs only in read mode. Future R4 development remains inside the active project. The separate `indy500删圈_R3C1_FROZEN_BASELINE` snapshot is outside this package and must remain untouched.

R4A does not use `historical_action_label` or `historical_lane_label` to set eligibility. A blank or generic historical result status also cannot set Lane 1 or Lane 2 eligibility. Unknown eligibility remains unknown in the source scenario and conservatively blocks that action until the team supplies an observable value.

## Verification

Run the engineering checks without creating bytecode outside `r4/`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 r4/run_scaffold_qa.py
PYTHONDONTWRITEBYTECODE=1 python3 r4/run_r4a_qa.py
```

The QA run uses synthetic interface traces only. It does not estimate a probability, make a recommendation, or produce a substantive strategy simulation.
