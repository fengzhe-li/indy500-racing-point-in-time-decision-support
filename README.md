<div align="center">

# Indy 500 Point-in-Time Probabilistic Decision Support System

### Physics-conditioned probabilistic inference with leakage-controlled historical replay and evidence-aware abstention

**Status: `FINAL_V3_FROZEN`** · **FINAL_V2 frozen scientific core** · **2020–2024 reference era** · **2025 external regime evaluation** · **Human in the loop**

**+ `V4_TEAM_NORMALIZED_FINAL`** — frozen additive team-normalized evidence extension (V2/V3 unchanged)

[![indy500-v3-ci](https://github.com/fengzhe-li/indy500-point-in-time-decision-support/actions/workflows/ci.yml/badge.svg)](https://github.com/fengzhe-li/indy500-point-in-time-decision-support/actions/workflows/ci.yml)
[![repository-integrity](https://github.com/fengzhe-li/indy500-point-in-time-decision-support/actions/workflows/integrity.yml/badge.svg)](https://github.com/fengzhe-li/indy500-point-in-time-decision-support/actions/workflows/integrity.yml)

[Methodology](docs/methodology.md) · [Model card](docs/model-card.md) · [Validation](docs/validation.md) · [Evidence engineering](docs/evidence-engineering.md) · [Full report](docs/paper/physics_conditioned_probabilistic_performance_inference.pdf) · [**FINAL_V3 application →**](v3_point_in_time/README.md) · [**V4 evidence extension →**](v4_team_normalized/output/phase4l/phase4l_final_scientific_synthesis.md)

</div>

![Identifiability-driven system boundary](figures/portfolio/identifiability-system-boundary.svg)

> **The key engineering result is a boundary.** Public historical evidence does not consistently reveal queue entry, Lane 1/Lane 2 state, withdrawals, requeue timing, pit return, live queue position or team intent. The project therefore does not guess an opportunity-time model or imitate historical decisions. It estimates the identifiable conditional performance problem and leaves the final retain/withdraw judgement to the pit wall.

**What this is, in one paragraph.** This repository is `FINAL_V3_FROZEN`: a point-in-time probabilistic
decision-support system built around a frozen physics-conditioned scientific core (`FINAL_V2`). `FINAL_V2`
estimates the conditional physical-performance distribution `p(Δv | H=h)` for a same-car repeat qualifying
attempt; it is never refit or modified by anything described below. `FINAL_V3` adds, on top of that frozen
core, the engineering needed to use it responsibly with real historical or hypothetical data: point-in-time
forecast-vintage provenance, a fail-closed leakage guard, historical shadow replay, evidence-aware abstention,
an isolated hypothetical scenario interface, and a FastAPI + React/TypeScript application, packaged with
Docker, CI, and health/readiness checks. The system is human-in-the-loop by design: it does **not** predict
queue waiting time, does **not** estimate `P(H=h)`, and does **not** issue a retain/withdraw recommendation or
claim automated pit-wall strategy optimisation, at any layer.

**V4 (additive evidence extension).** `V4_TEAM_NORMALIZED_FINAL` asks whether same-team, different-car evidence
could serve as an intermediate control layer between exact-car repeats and unrelated cars. It is a separately
frozen methodological study: it does **not** modify the FINAL_V2 coefficients, the 41-transition same-car core, the
V3 point-in-time inference or the paper. Its main finding is that exact-car control robustly reduces observed
performance dispersion, while shared team identity showed no stable additional benefit. See
[V4 — Team-normalized evidence extension](#v4--team-normalized-evidence-extension).

## The system in one screen

| Evidence / result | Verified value | Meaning |
|---|---:|---|
| Frozen same-car transitions | **41** | Small, high-confidence performance core |
| Section-linked transitions | **39 / 41** | Mechanism evidence; sections are not independent rows |
| Scientific horizons | **15 / 30 / 60 / 90 / 120 min** | Independently fitted/calibrated anchors |
| Stress-test scenarios | **135** | Thermal gap × ambient path × solar state × horizon |
| 2025 external cases | **15** | Hybrid-era realized-weather retrospective evaluation |
| External MAE / RMSE | **0.492 / 0.610 mph** | Point-error scale across all 15 cases |
| External 80% / 90% PI coverage | **80% / 100%** | Empirical rates in a small external sample |
| External directional accuracy | **46.7%** | Weak direction discrimination, reported without concealment |

The model is more useful as a **probabilistic physical-opportunity envelope** than as a binary prediction that the next run will be faster. Of the 15 external cases, **4** lie inside the production boundary of ≤120 minutes; that subset has MAE **0.221 mph**, RMSE **0.269 mph**, 80% coverage **100%**, 90% coverage **100%**, and directional accuracy **50%**. These four cases are too few for a broad calibration claim.

## FINAL_V3: point-in-time application layer

**Status: `FINAL_V3_FROZEN`.** On top of the frozen `FINAL_V2` scientific core above, a second engineering
layer turns the model into an auditable, evidence-aware decision-support application: a point-in-time
historical replay system, a strictly isolated hypothetical scenario mode, a FastAPI + React/TypeScript
application, and Docker/CI packaging. None of it changes a single frozen coefficient, residual pool, or
calibration file — see [`v3_point_in_time/`](v3_point_in_time/) for the full subsystem.

![FINAL_V3 architecture](figures/final_v3/figureA_final_v3_architecture.png)

Two paths share the frozen scientific core and nothing else: a **historical path** that only ever reads
already-frozen, point-in-time-controlled evidence through a read-only API, and a **hypothetical path** that
runs the same frozen adapter on user-supplied hypothetical input and returns an ephemeral result that can
never be written back into historical evidence. Neither path estimates opportunity timing, models a queue,
or issues a retain/withdraw recommendation.

### Historical Shadow Replay

A forecast-vintage store enforces `forecast.issue_time <= decision_time` before any historical inference is
issued; a fail-closed guard independently re-checks the same invariant. The replay engine then separates two
questions that are easy to conflate but must not be:

- **Inference support** — can the frozen model issue a conditional outlook `p(Δv | H=h)` at a calibrated
  horizon, given the current physical state and an available forecast vintage?
- **Historical scoring support** — can a realised historical outcome be defensibly paired with that outlook
  and scored?

| Evidence / result | Value |
|---|---:|
| Same-car transitions in the frozen 2020–2024 core | 41 |
| Excluded / abstained pre-candidates (ambiguous pairing or no usable timestamp) | 31 |
| Genuine point-in-time candidate cases | 10 |
| Cases with full 5-horizon inference support | 9 |
| Cases abstained from historical scoring (realised horizon > 120 min) | 9 |
| Illustrative-only shadow case (2021, car 60) | 1 |
| Cases contributing to formal aggregate historical-scoring validation | **0** |

**Point-in-time architecture and leakage control: demonstrated. Statistically meaningful point-in-time
forecast validation: not established.** This is reported as an evidence/identifiability boundary, the same way
the rest of this project treats unidentifiable quantities — not concealed, not padded with a larger but less
defensible sample. The one near-anchor case (2021, car 60) is retained as `ILLUSTRATIVE_POINT_IN_TIME_SHADOW_CASE`
only, is never counted toward validation, and is featured because it demonstrates a genuine evidence/model
boundary: its forecast-conditioned (+0.0236 mph) and realised-environment (+0.0451 mph) expectations were
close to each other, while the observed change (+4.695 mph) was far larger than either.

### Hypothetical Scenario Mode

A separate, isolated interface (`POST /api/scenario/infer`) runs the identical frozen `FINAL_V2` adapter on
user-supplied hypothetical current-state input, for demonstration and exploration. Every response is labelled
`HYPOTHETICAL_SCENARIO` / `NOT_HISTORICAL_EVIDENCE`, uses a minimum input contract derived directly from what
the frozen adapter requires, and is never written to any historical store or counted in any validation metric.

### Evidence-Aware Abstention

Wherever evidence does not support an inference or a historical score, the system says so explicitly with a
machine-readable reason code (`INSUFFICIENT_ATTEMPT_TIMESTAMP`, `HORIZON_OUT_OF_SUPPORT`,
`NON_ANCHOR_EVALUATION_NOT_APPROVED`, ...) rather than silently dropping the case. Abstention is a first-class,
auditable output, not an application error.

### Application

| Pit-Wall Outlook | Scenario Mode |
|---|---|
| ![Pit-Wall Outlook](v3_point_in_time/output/final_ui_preview/01_pit_wall_outlook.png) | ![Scenario Mode](v3_point_in_time/output/final_ui_preview/02_scenario_mode.png) |
| Conditional physical outlook across all five calibrated horizons for the deterministically selected, non-illustrative default case. | Hypothetical scenario inference, clearly labelled `HYPOTHETICAL SCENARIO — NOT HISTORICAL EVIDENCE`. |

| Historical Shadow Replay | Validation & Abstention |
|---|---|
| ![Historical Shadow Replay](v3_point_in_time/output/final_ui_preview/03_historical_replay.png) | ![Validation and Abstention](v3_point_in_time/output/final_ui_preview/05_validation_abstention.png) |
| Time-ordered replay events with an explicit information-cutoff boundary between what was known at time *t* and what was only observed later. | Authoritative evidence counts and abstention-reason breakdown, read live from the same frozen Phase 3 output as the numbers above. |

### Quick start

```bash
pip install -r v3_point_in_time/requirements.txt
cd v3_point_in_time/frontend && npm install && cd ../..

./v3_point_in_time/scripts/run_v3_app.sh
# API:      http://127.0.0.1:8000  (docs at /docs)
# Frontend: http://127.0.0.1:5173
```

### Docker

```bash
cd v3_point_in_time
./scripts/prepare_docker_context.sh   # stages a minimal (~3.6 MB) build context
docker compose up --build
# API:      http://localhost:8000
# Frontend: http://localhost:8080
```

The API container's filesystem is mounted read-only at runtime and runs as a non-root user, so frozen
scientific assets cannot be modified even by the process serving them.

### Testing

```bash
python3 -m unittest discover -s v3_point_in_time/tests -p 'test_*.py' -v   # 92 tests
cd v3_point_in_time/frontend && npx vitest run                              # 9 tests
python3 v3_point_in_time/scripts/smoke_test.py                              # end-to-end smoke test
```

**`FINAL_V3_FROZEN`** · **101/101 tests PASS** · **V2 immutability PASS (32/32 frozen dependencies byte-identical)**
· **V3↔V2 behavioural regression PASS**. These are engineering-verification results, not the project's
scientific finding — the primary results remain the 41-transition reference core, the 2025 external
physical-layer evaluation, and the qualified cross-regime transferability evidence above. Full detail:
[`v3_point_in_time/README.md`](v3_point_in_time/README.md), [architecture](v3_point_in_time/output/final_documentation/final_v3_architecture.md),
[model card](v3_point_in_time/output/final_documentation/FINAL_V3_MODEL_CARD.md), [scientific limitations](v3_point_in_time/output/final_documentation/scientific_limitations.md).

## The engineering problem

After setting a valid four-lap average, an Indianapolis 500 entrant may retain it and wait in the lower-priority lane, or withdraw it to seek priority for another attempt. That choice combines at least three different processes:

1. **Opportunity:** whether and when another run becomes available.
2. **Physical performance:** how the car's four-lap performance distribution changes as conditions evolve.
3. **Utility:** how rank, bubble position, time remaining and downside risk affect the team decision.

Historical evidence was sufficient for the second process, but not for a consistently labelled first process. That finding changed the estimand from a complete strategy policy to:

> **If another on-track opportunity occurs _h_ minutes from now, what distribution of four-lap qualifying-performance change should be expected relative to the current official result?**

Formally, the project estimates **p(Δv | H = h)**. It does not estimate **P(H = h)**. Physical-performance inference, opportunity-time prediction and strategy recommendation remain separate layers.

![Evidence engineering pipeline](figures/portfolio/evidence-engineering-pipeline.svg)

## Evidence engineering and data archaeology

The analysis began with official results and detailed reports, then reconciled attempts, chronology, section timing, observed track temperature, weather context and source authority. Every usable value carries evidence and eligibility semantics; unresolved joins remain quarantined.

![Evidence products and attrition](figures/portfolio/evidence-products-and-attrition.svg)

The two core datasets use different observational units. The performance response uses **41 same-car transitions**. The future-state layer uses **168 structured track-temperature observations**, transformed into **656 current–future pairs** at the supported horizons. Section evidence links to **39** transitions and contributes **351 dependent within-transition comparisons**, not 351 independent training examples.

![Evidence hierarchy](figures/portfolio/evidence-hierarchy.svg)

![Same-car transition design](figures/portfolio/same-car-transition-design.svg)

See [evidence engineering](docs/evidence-engineering.md), [data dictionary](docs/data-dictionary.md), and [identifiability boundary](docs/identifiability-boundary.md).

## Frozen physical-response model

The robust zero-intercept response model is:

```text
Δvphysical = βtrack ΔTtrack + βambient ΔTambient

βtrack   = −0.034825 mph / °C
βambient = +0.182393 mph / °C
```

The zero intercept encodes a narrow physical constraint: when both measured temperature changes are zero, the modelled thermal contribution is zero. It does **not** claim that realized speed change must be zero; tyre preparation, setup, execution, wind exposure and other latent run state remain in the residual distribution.

![Frozen physical response](figures/portfolio/frozen-physical-response.svg)

The frozen examples below expose both the measured physical-state changes and the gap between observed total performance change and the modelled physical contribution. They make the residual role visible instead of presenting the coefficients in isolation.

![Physical-state transition examples](figures/portfolio/physical-state-transition-examples.png)

![Observed versus frozen physical prediction](figures/portfolio/observed-vs-frozen-physical-prediction.png)

## Future physical state

Future track temperature is estimated separately from the performance response. The retained **M2b** specification conditions on future ambient-temperature change, the current track-to-ambient thermal gap and mean solar elevation. One model is fitted for each scientific horizon, selected through leave-one-year-out comparison.

![Future track model](figures/portfolio/future-track-state-model.svg)

![Candidate-model comparison](figures/portfolio/future-track-model-selection.png)

![Future track-state conformal calibration](figures/portfolio/future-track-conformal-calibration.png)

The solar-state extension is retained in the future track-state pathway. A direct solar performance coefficient is not added to the speed model. Current heating/cooling rate and change in solar elevation were investigated and rejected when their out-of-year evidence did not justify extra complexity.

## Probabilistic inference

FINAL_V2 propagates three sources of uncertainty:

- paired bootstrap uncertainty in the physical-response coefficients;
- horizon-specific future track-state uncertainty;
- empirical unexplained attempt-level performance variation from centered leave-one-year-out residuals.

![Three-source uncertainty architecture](figures/portfolio/three-source-uncertainty.svg)

![Uncertainty-source ablation](figures/portfolio/uncertainty-source-ablation.png)

Removing empirical performance residual uncertainty reduces mean 80% interval width by about **90.4% at 15 minutes** and **72.8% at 120 minutes**. This is an uncertainty-source ablation and sensitivity result, not an orthogonal variance decomposition. It shows why better track-temperature point prediction alone cannot collapse the final outcome interval.

See [uncertainty architecture](docs/uncertainty.md).

The leave-one-year-out coefficient traces below show why cross-year stability was inspected directly rather than inferred from a single full-sample fit.

![Leave-one-year-out track coefficient](figures/portfolio/loyo-track-coefficient-stability.png)

![Leave-one-year-out ambient coefficient](figures/portfolio/loyo-ambient-coefficient-stability.png)

## Calibrated support and operational interpolation

![Calibration boundary](figures/portfolio/calibrated-horizon-boundary.svg)

Scientific support exists at exactly **15, 30, 60, 90 and 120 minutes**. `OPERATIONAL_CURVE_V2` provides a one-minute display between anchors, with every row labelled as `CURRENT_STATE_BOUNDARY`, `CALIBRATED_ANCHOR` or `INTERPOLATED_OPERATIONAL`. The interpolated values are presentation summaries; they are not independently calibrated minute-by-minute forecasts.

## Diagnostics that interrogate rather than inflate the model

### Section-level mechanism evidence

![Section mechanism](figures/portfolio/section-mechanism-coherence.png)

For the 39 linked transitions, mean directional coherence across nine common sections is **0.724** and rises to **0.935** for the 12 transitions with |Δv| ≥ 0.50 mph. Meaningful changes are generally spatially coherent. Large residuals can also be coherent, so section evidence clarifies mechanism without converting dependent section rows into extra training samples.

### Wind diagnostic

![Wind residual diagnostic](figures/portfolio/wind-residual-diagnostic.png)

Wind is physically relevant. The available fixed-point and gridded historical proxies, however, showed weak or unstable out-of-year residual relationships. No deterministic wind coefficient or production residual-scale term was forced into FINAL_V2.

## Scenario stress test

The frozen model was exercised over **3 thermal-gap states × 3 ambient trajectories × 3 solar states × 5 horizons = 135 scenarios**. Every ambient trajectory remained within its corresponding historical support range.

![120-minute scenario stress test](figures/portfolio/scenario-stress-test-120min.png)

![Scenario probability range by horizon](figures/portfolio/scenario-probability-range-by-horizon.png)

![Scenario performance envelope by horizon](figures/portfolio/scenario-performance-envelope-by-horizon.png)

At 120 minutes, P(improvement) ranges from **0.2055 to 0.6704**, while expected Δspeed ranges from **−0.4630 to +0.2248 mph**. Physical state can materially shift the odds without eliminating outcome uncertainty. The grid remains conditional on an opportunity occurring; it contains no queue model.

## 2025 external validation

![2025 external validation](figures/portfolio/external-validation-2025.png)

The frozen 2020–2024 inference core was evaluated on 15 eligible 2025 hybrid-era same-car repeats. The evaluation uses the realized PTSC ambient trajectory retrospectively, so it tests the physical-inference chain under a new technical regime; it is **not** live weather-forecast validation.

| Metric | All external cases ≤180 min | Production-boundary subset ≤120 min |
|---|---:|---:|
| N | 15 | 4 |
| MAE | 0.492 mph | 0.221 mph |
| Median absolute error | 0.425 mph | 0.190 mph |
| RMSE | 0.610 mph | 0.269 mph |
| Directional accuracy | 46.7% | 50.0% |
| 80% PI coverage | 80% | 100% |
| 90% PI coverage | 100% | 100% |

Cases above 120 minutes are marked as extended retrospective validation and are not production-supported outputs. The 100% 90% interval coverage is an observed rate in 15 cases, not proof of perfect long-run calibration. See [validation](docs/validation.md).

## Technical-regime transfer and format boundary

![Technical regime timeline](figures/portfolio/technical-regime-timeline.svg)

![Regime coefficients](figures/portfolio/regime-coefficient-comparison.png)

The 2019 pre-Aeroscreen and 2025 hybrid samples retain the same directional response as the reference core. All reported 90% bootstrap intervals for direct coefficient differences include zero. This is qualified compatibility evidence, not equivalence or causal proof of coefficient invariance. The 2026 format is separately classified as structurally lacking same-day initial-round repeat transitions.

See [regime transfer](docs/regime-transfer.md).

## V4 — Team-normalized evidence extension

**Status: `V4_TEAM_NORMALIZED_FINAL` — frozen, additive.**

- **Unchanged:** FINAL_V2 coefficients, the 41-transition core, V3 inference and the paper.
- **Freeze:** separate pre-registered phases, a SHA-256 manifest of 735 files, and its own freeze tag.

**Question.** Could same-team, different-car evidence be a defensible intermediate control layer between exact-car repeats and unrelated cars?

**1. Team identity.**
- **Normalisation:** 59 official entrant/team labels (2018–2025) normalise to **21 canonical engineering teams**.
- **Old grouping:** it missed **85 of 313** true teammate relationships (27%) and created **no** false pairs. It was high precision with incomplete recall.

**2. Measurement validity.**
- A valid timed practice lap is not automatically a comparable performance observation.
- Only **8.1%** of 2023–24 at-speed practice laps met the frozen, qualifying-calibrated Class-A performance-comparability rule.
- Raw practice therefore cannot be treated as one homogeneous performance population.

![V4 measurement validity: run-state composition of practice laps](v4_team_normalized/output/phase4h/figures/fig06_run_state_by_session_category.png)

*Each bar splits one practice session type into run-state classes:*
- *green (A): performance-comparable;*
- *blue (B): plausibly comparable;*
- *amber (C): ambiguous;*
- *red (D): clearly non-comparable, e.g. pit or non-green laps;*
- *grey (E): too little data to judge.*

*Most timed laps are not clean performance measurements.*

**3. Final pre-registered test (Phase 4J).**
- **Population:** restricted to 2023–24 Class-A 5-minute car-blocks with timing-adjacency common support, over 6 independent sessions.
- **Dispersion:** same car **0.37 mph**, same team **1.23 mph**, different team **1.09 mph**.
- **C1 = same team − same car = +0.70 mph** [+0.09, +1.72]. **Robust:** positive in 5/6 sessions and in every leave-one-session-out and leave-one-team-out estimate.
- **C2 = different team − same team = +0.20 mph** [−0.53, +0.53]. **Not robust:** positive in 4/6 sessions, one team removal flips its sign, and the Tier 2 sensitivity gives −0.09 mph.
- **Conclusion:** the full *same car < same team < different team* hierarchy was **not established** (CASE B). Exact-car identity materially reduces observed dispersion in this high-confidence population. Shared team identity did not show a stable additional reduction versus different-team comparison. This is an empirical control result, not a causal team effect.

![V4 control-evidence summary](figures/portfolio/v4-control-evidence-summary.png)

**4. Teammate prediction (Phase 4K).**
- Of **113** target events, only **8** strict, leakage-free teammate-assisted events survived.
- Teammate predictive value therefore remains **prospectively unidentifiable** from the current retrospective record.
- This is **not** evidence that teammate predictive value is zero.

**What V4 adds.** Relaxing the same-car qualifying-repeat design exposed further layers of heterogeneity and non-identifiability. This supports the methodological value of exact-car control. It does not prove the V2 coefficients correct.

**Read more:**
- [Final V4 scientific synthesis](v4_team_normalized/output/phase4l/phase4l_final_scientific_synthesis.md)
- [Claims matrix](v4_team_normalized/output/phase4l/phase4l_claims_matrix.csv)
- [Evidence chain](v4_team_normalized/output/phase4l/phase4l_evidence_chain.md)
- [V4 workspace README](v4_team_normalized/README.md)

Lap-level V4 evidence is a third-party archived recording of the INDYCAR live timing feed (Timing71), cross-checked against official INDYCAR session records. Only 2023–2025 provide lap-level timing; 2018–2022 contribute identity and context, not equivalent lap-level evidence.

## Operational decision-support layer

![Operational performance outlook](figures/portfolio/operational-performance-outlook.png)

![Operational probability outlook](figures/portfolio/operational-probability-outlook.png)

An externally supplied opportunity window can be overlaid without converting it into a queue prediction. These views show how live operational context and model evidence remain separate layers.

![External opportunity-window performance overlay](figures/portfolio/external-opportunity-window-performance-overlay.png)

![External opportunity-window probability overlay](figures/portfolio/external-opportunity-window-probability-overlay.png)

The model returns expected Δspeed, median Δspeed, 80% and 90% predictive intervals, and P(Δv > 0) for a supplied physical scenario and opportunity horizon. A real pit-wall decision must combine that evidence with live queue position, cars ahead, leaderboard state, session remaining, interruption risk, withdrawal consequences and engineering judgement.

It does not choose Lane 1 or Lane 2, predict an optimal wait, or recommend retain/withdraw actions. See [operational interface](docs/operational-interface.md).

## Evidence-based decisions: rejected or not retained

| Candidate | Decision | Evidence-based reason |
|---|---|---|
| Historical queue-time model | Rejected | Queue/lane/withdrawal states were not consistently observable |
| Direct solar speed term | Not retained | Solar enters through the future track-state mechanism |
| Deterministic wind term | Not retained | Historical proxy relationships were weak and unstable across years |
| Section rows as training observations | Rejected | Nine sections within a transition are dependent |
| Pooling 2025 into the frozen core | Rejected | Would destroy external validation integrity |
| Independent minute-level calibration | Rejected | Intermediate minutes are labelled operational interpolation |
| Unsupported high-capacity models | Rejected | The evidence base does not justify complexity for its own sake |

These are model-risk controls and engineering outputs, not unfinished work.

## Reproducibility and freeze discipline

![Freeze and reproducibility](figures/portfolio/freeze-and-reproducibility.svg)

The repository contains frozen manifests and SHA-256 records for the performance core, FINAL_V2, diagnostics, operational curve and regulation extension. Portfolio scripts read those artefacts without refitting them. Later observations remain external unless a separately versioned research phase explicitly replaces the freeze.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# Recreate only the curated GitHub figures from frozen outputs
make figures

# Verify public claims, figure references and frozen hashes
make portfolio-check

# Run repository smoke/integrity tests
make test
```

Raw public-source evidence is retained for audit where redistribution permits. Derived canonical tables, provenance records, quarantine outputs and freeze manifests are included. Some external services and historical replay resources are not guaranteed to remain available; the repository does not claim that every raw acquisition can be repeated indefinitely. See [reproducibility](docs/reproducibility.md).

## Repository map

```text
pipeline/                 source-specific ingestion and canonical reconciliation
data/canonical/v1/        canonical historical data products
weather/                  observed weather, future-state model and FINAL_V2 outputs
r5_2/                     frozen 2020–2024 physical-response core
r6_regime_extension/      2019/2025 regime evidence and external evaluation
figures/portfolio/        curated GitHub visual narrative
figures/final_v3/         FINAL_V3 architecture/evidence-flow/illustrative-case figures
docs/                     technical documentation and final report
scripts/                  presentation regeneration and integrity checks
tests/                    pipeline and portfolio QA
v3_point_in_time/         FINAL_V3: point-in-time replay, Scenario Mode, FastAPI + React app, Docker, CI
v4_team_normalized/       V4 (frozen, additive): team registry, pre-registered Phases 3–4K, Phase 4L synthesis + freeze manifest
```

For the detailed module and status inventory, open [the repository guide](docs/reproducibility.md) and [figure gallery](figures/GALLERY.md).

## Limitations

- The primary response dataset contains only 41 transitions.
- Exact queue opportunity and team-intent history remains unidentifiable from the public record.
- Latent setup, tyre preparation, execution and vehicle state dominate much of the predictive spread.
- The 2025 external sample is small, with only four cases inside the production horizon.
- Future-state validation uses realized historical ambient paths; end-to-end live forecast validation remains separate.
- 2022 shows a marked thermal-regime shift and future-track interval undercoverage.
- Wind proxies do not represent the spatial aerodynamic exposure around the oval.
- Technical transferability is qualified; qualifying-format applicability must be checked separately.
- FINAL_V3's point-in-time evidence base yields only 10 genuine candidate cases and 0 cases with formal aggregate historical-scoring support; statistically meaningful point-in-time forecast validation is not established (architecture and leakage control are demonstrated in running software; evidence volume is the limitation, not infrastructure).
- The one near-anchor point-in-time case (2021, car 60) is illustrative only and must never be read as validation.
- Neither FINAL_V2 nor FINAL_V3 models opportunity timing, queue state, or a retain/withdraw strategy, historically or hypothetically.
- **V4** (additive) covers a restricted 2023–24 practice population of 6 independent sessions.
  - Its same-team versus different-team contrast is not robust, so the full three-level hierarchy is not established.
  - Teammate predictive value is not prospectively identifiable with current retrospective labels.
  - Run purpose, fuel, tyres, tow and traffic are unobserved.

## Documentation

- [Identifiability boundary](docs/identifiability-boundary.md)
- [Methodology](docs/methodology.md)
- [Model card](docs/model-card.md)
- [Evidence engineering](docs/evidence-engineering.md)
- [Validation](docs/validation.md)
- [Uncertainty](docs/uncertainty.md)
- [Regime transfer](docs/regime-transfer.md)
- [Operational interface](docs/operational-interface.md)
- [Reproducibility](docs/reproducibility.md)
- [Technical challenges](docs/technical_challenges.md)
- [FINAL_V2 system specification](docs/final_v2_system_specification.md)
- [Full research report](docs/paper/physics_conditioned_probabilistic_performance_inference.pdf) (includes FINAL_V3 Section 10, "Point-in-Time Historical Shadow Evaluation")
- [FINAL_V3 application README](v3_point_in_time/README.md)
- [FINAL_V3 architecture](v3_point_in_time/output/final_documentation/final_v3_architecture.md)
- [FINAL_V3 model card](v3_point_in_time/output/final_documentation/FINAL_V3_MODEL_CARD.md)
- [FINAL_V3 system specification](v3_point_in_time/output/final_documentation/FINAL_V3_SYSTEM_SPECIFICATION.md)
- [FINAL_V3 scientific limitations](v3_point_in_time/output/final_documentation/scientific_limitations.md)
- [FINAL_V3 QA report](v3_point_in_time/output/qa/final_v3_qa_report.md)
- **V4 team-normalized evidence extension:**
  - [final scientific synthesis](v4_team_normalized/output/phase4l/phase4l_final_scientific_synthesis.md)
  - [claims matrix](v4_team_normalized/output/phase4l/phase4l_claims_matrix.csv)
  - [evidence chain](v4_team_normalized/output/phase4l/phase4l_evidence_chain.md)
  - [limitations](v4_team_normalized/output/phase4l/phase4l_limitations.md)
  - [future data requirements](v4_team_normalized/output/phase4l/phase4l_future_data_requirements.md)
  - [freeze report](v4_team_normalized/output/phase4l/v4_freeze_report.md)
  - [workspace README](v4_team_normalized/README.md)

  V4 is **not** yet part of the full research report above.

## Author and citation

**Fengzhe Li** · University College London

If this repository informs your work, cite the project and the versioned frozen artefacts used:

| Frozen artefact | Role |
|---|---|
| `FINAL_V2` | scientific model |
| `R6_REGULATION_AWARE_EXTENSION_V1_FROZEN` | regulation-aware evidence extension |
| `FINAL_V3_FROZEN` | point-in-time application layer |
| `V4_TEAM_NORMALIZED_FINAL` (git tag) | additive team-normalized evidence extension |

The full research report describes FINAL_V2/V3 only. V4 findings are currently documented in the repository ([V4 synthesis](v4_team_normalized/output/phase4l/phase4l_final_scientific_synthesis.md)), not in the report.

## Status

| Layer | Status |
|---|---|
| Scientific core | `FINAL_V2` — frozen |
| Regulation-aware evidence extension | `R6_REGULATION_AWARE_EXTENSION_V1_FROZEN` |
| Point-in-time application layer | `FINAL_V3_FROZEN` — 101/101 tests PASS, V2 immutability PASS, V3↔V2 behavioural regression PASS |
| Team-normalized evidence extension | `V4_TEAM_NORMALIZED_FINAL` — frozen additive evidence extension; V2/V3 unchanged; 735-file SHA-256 manifest; Phase 4L checks 17/17 PASS |
