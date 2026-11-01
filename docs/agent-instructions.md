# Agent Instructions for MBSD

MBSD is a Python framework for inspectable multibody mechanism models. Agents
assemble models; the framework's guardrails report, as data, whether the
physics is consistent; humans review the result. This page describes the
`0.9.7` public surface of `mbsd-core`.

## Scope and Status

| Status | Surface |
|---|---|
| Stable candidate | Planar (2D) mechanisms: `Mechanism.planar()` |
| Experimental (until 1.0) | Spatial (3D) mechanisms: `Mechanism.spatial()` with one `simulate()` |
| Restricted | `simulate_fixed_orientation()` (translation only, centroidal bodies) |
| Deprecated until 1.0 | `simulate_free_body()`, `simulate_coupled_rigid_bodies()`, `simulate_constrained_rigid_bodies()`; use `simulate()` |
| Unsupported | Contact and collision (write a `force(fn)` callback outside core), flexible bodies, FEM/CFD, spatial joints beyond spherical / fixed / revolute / `parallel_axes`, real-time guarantees |

Ask the framework instead of guessing:

```python
import mbsd

mbsd.capabilities()        # joints, drives, solvers, limits per dimension
mbsd.operation_manifest()  # operations, inputs, solver options, error and validation codes
```

## The Workflow

Every analysis follows the same five steps. Do not skip `validate` or `check`.

```text
build (or load) -> validate -> solve -> check -> export
```

- `validate()` runs before any solve and returns a `ValidationReport`
  (`ok`, `portable`, `classification`, `degrees_of_freedom`, `issues`).
  Stop and repair when `ok` is false.
- `check(result)` returns a `CheckReport` with a pass/fail verdict per check
  and the thresholds used. A run that finishes is not validated until
  `check` passes.
- Solver errors are `MechanismSolveError` with a stable `code`, a `context`
  dict, and a `remediation` string. Read all three.

## Planar Workflows

Kinematics of a fully driven mechanism:

```python
import numpy as np
from mbsd import ConstantSpeed, Mechanism

m = Mechanism.planar(gravity=(0.0, -9.81))
ground = m.ground()
crank = m.body("crank", mass=0.6, inertia=2e-4)
m.pin(ground, crank, point_b=(-0.02, 0.0), name="main_bearing")
m.coordinate_drive(crank, "theta", law=ConstantSpeed(rate=10.0), name="motor")
q0 = np.array([0, 0, 0, 0.02, 0, 0], dtype=float)

t = np.linspace(0.0, 1.0, 101)
assert m.validate(q0, t=t).ok
kinematics = m.solve_kinematics(t, q0=q0)
assert m.check(kinematics).passed
```

Inverse dynamics, joint loads, and export (the FEM / sizing handoff):

```python
result = m.inverse_dynamics(t, q0=q0)
assert m.check(result).passed
loads = m.joint_loads(result)
loads.joints["main_bearing"]["force_on_j"]   # world-frame force on the crank
loads.drives["motor"]["effort"]              # motor torque, N*m
m.joint_loads_to_json(result, "loads.json")  # mbsd.planar.joint_loads v2
m.to_json("mechanism.json")                  # portable model
```

Forward dynamics of a mechanism with free degrees of freedom:

```python
pendulum = Mechanism.planar(gravity=(0.0, -9.81))
g = pendulum.ground()
arm = pendulum.body("arm", mass=2.0, inertia=0.03, center_of_mass=(0.4, 0.0))
pendulum.pin(g, arm, name="pivot")
q0 = np.zeros(6)
report = pendulum.validate(q0)              # 'underconstrained' info: 1 DOF
result = pendulum.simulate(np.linspace(0.0, 2.0, 201), q0=q0, allow_underconstrained=True)
assert pendulum.check(result).passed        # includes energy drift
```

Planar building blocks: `pin`, `slider`, `point_on_line`, `motor`,
`coordinate_drive(law=...)`, `distance_drive(law=...)` (linear actuator),
`spring`, `constant_force`, `constant_torque`, `tabulated_force`,
`tabulated_torque`, and `force(fn)` (Python-only escape hatch). Bodies may
have an offset `center_of_mass`. Downstream computations use
`mbsd.planar.analysis` (mass matrix, Jacobians, residuals, point kinematics),
never the internal modules.

## Spatial Workflows

Kinematics: build joints and drives, then `solve_kinematics(t)` and
`check(result)`.

Dynamics always goes through one call, `simulate()`:

```python
import math
import numpy as np
from mbsd import ConstantSpeed, Mechanism
from mbsd.spatial import Pose3D, Quaternion

z_to_x = Quaternion.from_axis_angle((0, 1, 0), math.pi / 2)
m = Mechanism.spatial()
ground = m.ground()
rotor = m.body("rotor", mass=4.0, inertia=(0.08, 0.05, 0.05))
hinge = m.revolute(ground, rotor, frame_i=Pose3D(rotation=z_to_x),
                   frame_j=Pose3D(rotation=z_to_x), name="bearing")
m.revolute_drive(hinge, law=ConstantSpeed(rate=20.0), name="motor")

t = np.linspace(0.0, 0.5, 51)
assert m.validate(t).ok
result = m.simulate(t, gravity_world=(0.0, 0.0, -9.81))
assert m.check(result).passed
m.drive_efforts(result)["motor"]["effort"]   # drive torque, N*m
m.constrained_result_to_json(result, "rotor.json")
```

- Unconstrained bodies: the same `simulate()` with no joints; coupled bodies
  pass `interactions=(m.pair_interaction(...),)`.
- Initial velocities are center-of-mass world velocity and body-frame angular
  velocity. Pass dicts keyed by body name. When only some are known, call
  `m.consistent_velocities(angular_velocity_body={"shaft_in": (w, 0, 0)})`
  and pass its arrays to `simulate()`.
- Spatial joints: `spherical`, `fixed`, `revolute`, and the orientation-only
  `parallel_axes`. Drives: `coordinate_drive(body, "x"|"y"|"z", law=...)` and
  `revolute_drive(joint, law=...)`. Rotation of a body is driven through a
  revolute joint, never through `coordinate_drive`.
- A shaft on two bearings: the first bearing is `revolute`, the second is
  `parallel_axes`. Two revolute bearings are redundant and are rejected.

## Conventions

- SI units: m, kg, s, rad, N, N*m, W. Angles are radians.
- Planar coordinates are `[x, y, theta]` per body, counterclockwise positive;
  body 0 is the ground.
- Spatial world frame is right-handed XYZ; quaternions are `[w, x, y, z]`,
  active body-to-world; angular velocity and inertia are body-frame; the
  ground is a body row in every per-body array.
- The saddle system is `M a + C_q.T λ = Q`; physical reactions are
  `-C_q.T λ`. Joint loads are world-frame forces with moments about the joint
  point. Drive efforts are the force or torque the drive applies (`-λ` of its
  row); a distance drive's effort is positive when it pushes.
- Identities: `model_id` (structure), `excitation_id` (sampled drives and
  loads), `simulation_id` (initial state and solver controls). A result only
  belongs to the mechanism with the same `model_id`.
- Portable models contain descriptors only: motion laws (`ConstantSpeed`,
  `Polynomial`, `Tabulated`) and load descriptors. Python callables make a
  model non-portable; `validate()` reports it and `from_json()` raises
  `NotPortableError`. Portable payloads never execute code.

## Repairing Failures

| Code | Meaning | Repair |
|---|---|---|
| `redundant_constraints` / `rank_deficient` | Constraint rows repeat; `context` names the joints | Replace a second shaft bearing with `parallel_axes`, or remove the duplicated joint or drive |
| `overconstrained` | More constraints than coordinates | Remove redundant joints or drives |
| `underconstrained` (info) | Free degrees of freedom | Fine for `simulate()`; add drives for kinematics or inverse dynamics |
| `not_kinematically_driven` | Inverse dynamics with free DOF | Add drives until DOF is zero |
| `position_solve_failed` | Assembly did not converge | Give an initial guess closer to an assembled pose; check that drives stay within reachable geometry |
| `inconsistent_initial_velocity` / `inconsistent_initial_state` | Initial velocities break the constraints | Prescribe the known velocities and use `consistent_velocities()` |
| `time_outside_table` | A tabulated law or load does not cover `t` | Extend the table or shorten `t` |
| `opaque_drive` / `opaque_load` / `opaque_constraint`, `not_portable` | Python callbacks | Use laws and load descriptors when the model must be exported |
| `unsupported_capability` | Outside this release | Check `mbsd.capabilities()`; do not work around it inside core |
| `resource_limit` | `max_steps` or `max_evaluations` exceeded | Use fewer samples, looser tolerances, or raise the limit deliberately |
| `unsupported_schema_version` / `schema_mismatch` | Payload cannot be read | Re-export with the current release |

## Local Workflow

```sh
uv sync --extra dev
make check
```

If a change touches examples, solver behavior, or docs that claim runnable
behavior, run `make check` before committing.

## Rules

- Use the public API (`mbsd`, `mbsd.planar`, `mbsd.planar.analysis`,
  `mbsd.spatial`). Do not import internal modules.
- Name bodies, joints, and drives with mechanism terms; names appear in
  loads, layouts, and error messages.
- Keep parameters and units explicit near the top of a script.
- Report solver-produced numbers (from `validate`, `check`, `joint_loads`,
  `drive_efforts`) separately from your own interpretation.
- Do not present a simulation as validated because it runs; cite the
  `check()` verdict and its thresholds.
- Do not invent APIs; confirm with `mbsd.operation_manifest()`.
