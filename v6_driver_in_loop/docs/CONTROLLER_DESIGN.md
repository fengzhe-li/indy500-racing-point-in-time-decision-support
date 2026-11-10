# Virtual driver and control assumptions

The driver reads the current state and a pre-known reference map. Its permitted
forward map preview is exactly `preview_m` (default 35 m), measured along the
reference centreline. It uses neither future vehicle states nor the lap solver's
future speed envelope. Position localization projects onto known geometry.

Pure pursuit computes the target's body lateral coordinate yt and actual chord
squared `dx²+dy²`: `δ_requested = steering_gain*atan2(2*wheelbase*yt, dx²+dy²)`.
This is a geometric path controller applied at the CG with dynamic sideslip;
it has no dynamic feedforward or compensation for understeer. An optional
first-order steering filter uses exact sampled exponential gain `1−exp(−dt/tau)`.
The engine clamps actual steering using VehicleParams, never a hardcoded wheelbase
or steering limit. Preview and steering gain are independently configurable.

Desired speed is `aggression*min(max_speed, sqrt(ay_limit/abs(preview_curvature)))`;
on straights the curvature cap is absent. Thus `max_speed` is a pre-aggression
profile value, not a hard safety limit. Defaults are 75 m/s on straights and
sqrt(10×402.336)=63.430 m/s in curves, before aggression. Speed PID controls body
u, so plotted speed magnitude hypot(u,v) can differ slightly. The driver uses no
braking-distance planner and can enter a curve above its target. PID integral
is limited to ±20 and conditionally frozen against saturation; there is no
initial derivative kick. Signed PID output is divided by 5 for throttle or 8
for brake; controls are clipped to [0,1]. Brake overrides throttle in every
input mode. These scale factors/gains are illustrative, not identified human behavior.

Reaction delay queues requested commands with their simulation due times; release
occurs on the first tick at/after the due time, so non-grid delays round up by
less than dt. The queue starts with zero commands. This models delayed commands,
not a complete human perception/reaction model. The displayed target-speed trace
is the current undelayed target. `DriverController` is a typed protocol and
`SimulationEngine.run(controller=...)` accepts a fresh interchangeable controller;
`manual_input=` accepts a software callback. Neither supplies verified human hardware.

Telemetry records requested and applied inputs, full body accelerations, signed
path error and flags. Steering/upper pedal saturation time excludes the terminal
zero-duration row; zero throttle or brake is normal coasting, not saturation.
Tyre clipping occupancy is separate. Maximum steering slew is reported as control
smoothness; no physical rate-limited steering actuator has been calibrated.

The 19-scenario one-factor matrix includes conservative/aggressive/delayed drivers,
initial offsets/headings/speeds, grip and lateral/longitudinal gains. Negative
outcomes are retained. See [results](../reports/ROBUSTNESS_RESULTS.md) and
[scenario definitions](../reports/scenario_definitions.json). Success of one
configuration is not a proof of controller stability or human performance.
