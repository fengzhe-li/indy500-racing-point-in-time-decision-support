# Operational scope and future hardware DIL

| Mode | Current status |
| --- | --- |
| Software-in-the-Loop | Operational deterministic offline vehicle/control simulation |
| Virtual driver | Pure-pursuit/PID driver and reproducible parameter sweeps |
| Interactive replay | Read-only saved telemetry with play/pause/seek/rate/experiment selection |
| Manual interactive driving | No live driving UI; optional Python callback is a software input extension only |
| Real hardware Driver-in-the-Loop | Not implemented or validated |

`hardware.py` is a typed future adapter boundary, not a device driver. The current
simulation runs as quickly as the process can execute; replay uses a browser wall
clock solely to present recorded simulation time. CPU/wall duration benchmarks do
not establish deterministic deadlines, latency bounds or real-time capability.
There is no steering wheel, pedal rig, motion platform, human-driver measurement,
manufacturer validation or hardware safety certification.

Future integration needs input/output sampling units and calibration; timestamped
hardware commands; latency/jitter instrumentation; a monotonic fixed-rate scheduler;
stale-data watchdogs; bounded actuation and emergency stop; disconnect/fault handling;
force-feedback and motion cue validation if used; target-computer worst-case timing;
and supervised hardware-in-the-loop commissioning. The current approximate low-speed
and tyre/actuator models need application-specific validation before such integration.
The replay must remain read-only and outside the physical control loop.
