# Follow-up verification record

Executed locally on 2026-11-10 after the banked-force corrections. Counts below
are actual successful executions, not inferred from missing CI runs.

| Check | Result |
|---|---|
| V5 Python unittest suite | 20 passed |
| Root repository unittest suite | 33 passed |
| V3 Python scientific/API suite | 92 passed |
| V5 React/Vitest suite | 10 passed |
| Existing V3 frontend suite | 9 passed |
| V5 TypeScript/Vite production build | Passed |
| Existing V3 TypeScript/Vite production build | Passed |
| V2 frozen-dependency hash check | 32 files matched |
| V3 vs V2 behavioral regression | Passed at all five supported horizons |
| V3 application/scenario smoke checks | 10/10 passed |
| Portfolio integrity validator | Passed |
| Frozen V2/V3/V4/data trees vs initial V5 commit | No tracked changes |
| Corrected numerical analysis and replay regeneration | Passed |

## Coverage

V5 tests cover ordered segment lengths and geometric closure, banked force
balance against an independent analytic no-aero result, periodic acceleration
and braking bounds, tire-circle feasibility, rotated lap-origin invariance,
mesh refinement independent of iteration tolerance, year-separated scalar
fitting, median benchmark equivalence, schema generation, exact time integration,
API reproducibility and invalid input rejection. Frontend tests consume Python
fixtures and cover endpoint geometry, schema drift, kinematic round trips,
playback rate/wrap, timeline seeking, graph dragging, car/cursor synchronization,
parameter submission, reset and failed-recompute behavior.

Manual browser inspection of the production build confirmed play/pause,
timeline seeking, keyboard and pointer graph seeking, and a live mass change
from 800 to 900 kg (keeping μ=1.35), which recomputed the scenario from
40.9635 to 42.3287 s. The course marker and graph use shared elapsed time.

## Commands

Run from the repository root:

```bash
python3 -m unittest discover -s v5_lap_time_simulation/tests -v
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s v3_point_in_time/tests -v
python3 v3_point_in_time/scripts/run_v2_immutability_check.py
python3 v3_point_in_time/scripts/run_v3_v2_behavioral_regression.py
python3 v3_point_in_time/scripts/smoke_test.py
python3 scripts/validate_portfolio.py
npm test --prefix v5_lap_time_simulation/frontend
npm run build --prefix v5_lap_time_simulation/frontend
npm test --prefix v3_point_in_time/frontend
npm run build --prefix v3_point_in_time/frontend
python3 -m v5_lap_time_simulation.cli
```

## GitHub Actions

The existing PR #2 head `18b8623` had an actual successful
[V3 CI run](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42829679521),
including Python, frontend and Docker jobs. This was verified in GitHub's run
page, not inferred from absent checks. It does not establish follow-up-head
success. The follow-up adds `.github/workflows/v5.yml` for V5 physics/API tests,
analysis regeneration and frontend tests/build. The latest pushed head's actual
status is reported separately in the PR/delivery; queued, missing or inaccessible
runs must not be reported as passed.

Local Docker builds were not rerun in this follow-up; the existing remote Docker
job and the latest-head remote status are distinguished from local verification.
Untracked V6 and concurrent C++ files were neither edited nor staged.
