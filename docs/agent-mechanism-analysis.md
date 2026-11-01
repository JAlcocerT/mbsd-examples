# MBSD Mechanism Analysis Playbook

Use this playbook when writing an MBSD analysis script against the `0.9.7`
public API. See `agent-instructions.md` for the API surface, conventions, and
the failure-repair table.

## Goal

A runnable Python analysis that an agent can assemble and a human can verify
from the printed guardrail data alone.

## Required Shape

1. Build the model with `Mechanism.planar()` or `Mechanism.spatial()`.
2. Declare parameters explicitly at the top: lengths, masses, inertias,
   drive laws, loads, and the time grid, with units.
3. Name every body, joint, and drive with mechanism terms.
4. Prefer portable inputs: motion laws (`ConstantSpeed`, `Polynomial`,
   `Tabulated`) and load descriptors. Use `force(fn)` or callables only for
   behavior core does not model (for example penalty contact), and say so.
5. Call `validate()` and stop if `ok` is false; print the issues.
6. Solve with one public call: `solve_kinematics`, `simulate`, or (planar,
   fully driven) `inverse_dynamics`.
7. Call `check(result)` and print every check with its value and threshold.
8. Derive engineering outputs from public results: `joint_loads()` (planar),
   `drive_efforts()` (spatial), `mbsd.planar.analysis` primitives.
9. Export with `to_json`, `result_to_json` / `constrained_result_to_json`,
   or `joint_loads_to_json` when another tool needs the data.
10. Keep plotting optional so the default run stays fast in `make check`.

## Minimum Guardrails to Print

- `validate()`: `ok`, `portable`, `classification`, `degrees_of_freedom`,
  and every issue code
- `check()`: `passed`, and each check's name, value, and threshold
- for drives: the effort and power range, units included
- at least one physically interpretable metric (stroke, peak force, speed
  ratio, energy drift) compared against an independent estimate where one
  exists (closed form, static balance, momentum)

## Example Skeleton

```python
import numpy as np
from mbsd import ConstantSpeed, Mechanism

# Parameters (SI)
CRANK_RADIUS = 0.04
OMEGA = 150.0

def build():
    m = Mechanism.planar(gravity=(0.0, -9.81))
    ground = m.ground()
    crank = m.body("crank", mass=0.6, inertia=2e-4)
    m.pin(ground, crank, point_b=(-CRANK_RADIUS / 2, 0.0), name="main_bearing")
    m.coordinate_drive(crank, "theta", law=ConstantSpeed(rate=OMEGA), name="motor")
    return m, np.array([0, 0, 0, CRANK_RADIUS / 2, 0, 0], dtype=float)

def run_analysis(nsteps=181):
    m, q0 = build()
    t = np.linspace(0.0, 2 * np.pi / OMEGA, nsteps)
    report = m.validate(q0, t=t)
    if not report.ok:
        raise SystemExit(report.as_dict())
    result = m.inverse_dynamics(t, q0=q0)
    verdict = m.check(result)
    loads = m.joint_loads(result)
    return {"validation": report.as_dict(), "check": verdict.as_dict(),
            "peak_torque": float(np.abs(loads.drives["motor"]["effort"]).max())}
```

## Avoid

- hidden parameters or undocumented units
- imports from internal modules such as `mbsd.planar.jacobians`
- deprecated spatial entry points (`simulate_free_body`,
  `simulate_coupled_rigid_bodies`, `simulate_constrained_rigid_bodies`)
- two revolute bearings on one shaft (use `revolute` + `parallel_axes`)
- claims beyond `mbsd.capabilities()` (contact, flexible bodies, joints that
  are not listed)
- plots or files created during the default example run
