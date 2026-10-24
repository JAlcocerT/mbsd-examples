# MBSD Examples Release Plan

This is the practical companion roadmap for `mbsd-core` and `mbsd-examples`.
Keep `mbsd-core` small and technical; use this repo and the website docs to
explain the weekly release story.

The framework-root `roadmap.md` is canonical. This file summarizes examples
work and must be updated whenever that version ladder changes.

## v0.1.0

Week 1 stays deliberately small:

- driven slider
- mass-spring-damper
- slider-crank analysis with guardrails
- generated PNG gallery
- agent-facing sample guidance

## v0.2.0

Week 2 should make the first release easier to inspect and compare.

Core target:

- validation and diagnostics helpers for simulation results
- stable helpers for constraint residual checks
- explicit tests for invalid models and singular solves
- additional physics regression tests, especially energy behavior
- no new heavy runtime dependencies

Examples target:

- four-bar linkage
- scotch yoke
- driven pendulum
- energy-conservation mass-spring example
- refreshed PNG gallery with source scripts
- buildable source release artifacts for repository hygiene

Release order:

1. tag and release `mbsd-core` `v0.2.0`
2. pin `mbsd-examples` CI to `mbsd-core` `v0.2.0`
3. tag and release `mbsd-examples` `v0.2.0`
4. update the website/docs with the new examples and release notes

## v0.3.0

Week 3 should add the first small 2D synthesis preview.

Core target:

- four-bar geometry helper
- Grashof classification
- closed-form Freudenstein three-precision-point synthesis
- rocker-angle sweep and affine fitting helpers
- no top-level API expansion

Examples target:

- precision-point synthesis example
- rocker function fitting example
- refreshed PNG gallery with synthesis plots
- numerical regression assertions for example metrics
- repo-first distribution notes so users clone and run the examples from source
- keep optimization-heavy and notebook-style synthesis batches for later

Release order:

1. tag and release `mbsd-core` `v0.3.0`
2. pin `mbsd-examples` CI to `mbsd-core` `v0.3.0`
3. tag and release `mbsd-examples` `v0.3.0`
4. update the website/docs with synthesis preview notes

## Planned Ladder

Use this ladder as the public version story unless the implementation reality
forces a change:

```text
0.1.0: lean planar core and first runnable examples
0.2.0: validation helpers and canonical planar example gallery
0.3.0: 2D synthesis preview
0.4.0: export schema and CAD handoff bridge
0.5.0: experimental 3D model vocabulary
0.6.0: 2D solver hardening and API maturity
0.7.0: 3D kinematics preview
0.8.0: Mechanism.spatial() and constrained spatial kinematics
0.9.0: empty release (tag accidentally matched 0.8.1)
0.9.1: fixed-orientation spatial translational dynamics preview
0.9.2: free-body rotational dynamics foundation
0.9.3: coupled six-DOF rigid-body dynamics
0.9.4: constrained rotational dynamics and reactions
0.9.5: interoperability and reference adapters
0.9.6: agent-ready workflows
0.9.7: 1.0 release candidate and compatibility freeze
1.0.0: stable planar and coupled rotational 3D rigid-body framework
```

## v0.4.0

Week 4 should make solved mechanisms portable without turning `mbsd-core` into a
CAD package.

Core target:

- mechanism export schema for bodies, joints, drives, supported force
  descriptors, metadata, and units
- solved-result export schema for time histories, body poses, traces, and
  validation summaries
- JSON-first helpers such as `to_dict()` / `to_json()` style APIs
- optional CSV helpers for trajectories and point traces
- no FreeCAD, CadQuery, Blender, STEP, or heavy CAD dependencies in core runtime

Examples target:

- one mechanism JSON export example
- one trajectory/point-trace CSV export example
- one CAD-handoff example that produces neutral data a CAD/render tool could
  consume later
- small generated artifacts committed only when they are reproducible from source

The `v0.4.0` release provides versioned planar mechanism and result schemas,
explicit SI units and coordinate conventions, portable spring-damper
descriptors, caller metadata, wide trajectory CSV, and named body-point traces.
The handoff example writes and validates each JSON/CSV artifact for downstream
browser and neutral CAD-path consumers. Arbitrary Python force callbacks remain
outside the portable schema.

## v0.5.0

Week 5 should start the 3D track as vocabulary and data modeling, not as a full
3D solver claim.

Core target:

- experimental spatial namespace
- body pose and rotation representation decision
- coordinate and frame conventions
- mass/inertia containers suitable for later spatial dynamics
- basic joint data structures or sketches, clearly marked experimental
- no promise of solved 3D kinematics or 3D dynamics yet

Examples target:

- a pendulum-like posed-body, body-local-frame, and spherical-joint sketch
- a versioned JSON spatial-model artifact for geometry handoff
- explicit notes that the 3D API can change before `1.0`

The implemented vocabulary uses right-handed XYZ coordinates, active
body-to-world quaternions ordered `[w, x, y, z]`, SI units, and principal body
inertia values about the center of mass. It remains data-only in this release.

## v0.6.0

Week 6 should strengthen the existing 2D foundation before deeper 3D work.

Core target:

- cleaner internal constraint APIs
- improved solver diagnostics and failure reports
- consistent offset center-of-mass rejection at every unsupported dynamics API
- genuine RK45 integration with caller initial velocities preserved
- optional stabilization/projection controls for constrained dynamics
- stronger energy, residual, and regression tests
- hardened spatial value/export contracts before downstream solver work
- distribution builds and installed-wheel smoke tests in CI

Examples target:

- examples that expose solver diagnostics
- healthy, underconstrained, and rank-deficient diagnostic states
- comparison metrics for residuals, energy, and solver behavior

This release is a readiness gate for later spatial solvers rather than a
calendar-only milestone.

## v0.7.0

Week 7 should introduce a 3D kinematics preview.

Core target:

- spatial point-position, pose-composition, and inverse-transform helpers
- spherical-joint point-coincidence residual evaluation
- compact maximum-residual summaries
- explicit experimental namespace and warnings
- no general 3D position, velocity, or acceleration solver claim
- no broad contact, collision, or multiphysics claims

Examples target:

- a spatial transform and spherical-joint residual example
- an analytic geometry assertion and numerical residual metric

## v0.8.0

This release introduces the public spatial builder and constrained spatial
kinematics without claiming spatial dynamics.

Core target:

- `Mechanism.spatial()` with stable body/frame handles
- position and velocity constraint solves with rank diagnostics
- spatial kinematic results, provenance, diagnostics, and JSON exports
- clear limitations around dynamics, contact, collision, and complex joints

Examples target:

- spherical, fixed-attachment, and deliberately singular examples
- conservative residual metrics and failure-mode notes

## v0.8.1

This patch release hardens the constrained-spatial-kinematics interchange
contract without adding dynamics or changing schema versions.

Core target:

- validate complete pose, quaternion, diagnostics, units, conventions, and
  capability records in spatial kinematic-result payloads
- reject non-finite JSON values during validation and export
- preserve valid `0.8.0` result compatibility

Examples target:

- exercise the strict public reader using a complete paired result artifact
- keep the dynamics boundary explicit until `0.9.0`

## v0.9.1

The first functional `0.9.x` release is the fixed-orientation translational
dynamics preview. It keeps orientations constant and exposes no torque input.
The published `v0.9.0` tag accidentally matched `v0.8.1`; `v0.9.1` preserves
that public history while delivering the intended implementation.

Core target:

- fixed-orientation translation with force inputs and translation constraints
- acceleration-level drive laws, multipliers, physical reaction loads, and
  three-level residuals
- bounded integration settings and versioned dynamic-result JSON
- explicit rejection of rotational dynamics, torque, and offset-force claims

Examples target:

- analytic constant-force and constrained-drive validation cases
- diagnostics-rich JSON artifacts and explicit limitation reporting
- integration examples with CAD/render/data tools from `0.9.5`
- notebooks where they add durable explanation
- selected historical GIFs and plots with source scripts, captions, and
  provenance
- larger synthesis batches when they are reproducible

Browser application code is intentionally not part of the OSS roadmap. External
applications can consume the same public export and result schemas without
becoming part of these repositories.

## v0.9.2

Free-body rotational dynamics is limited to one unconstrained rigid body. The
solver uses active body-to-world quaternions, body-frame angular velocity and
inertia, Euler's gyroscopic term, and explicit world/body load frames.

Core acceptance thresholds:

- principal-axis constant-torque angular velocity and orientation error below
  `2e-9`;
- torque-free asymmetric-body relative energy error below `2e-10`;
- torque-free inertial angular-momentum error below `2e-10`;
- quaternion norm and rotation orthogonality error below `1e-12`;
- tightened integration tolerances reduce error against a high-accuracy
  reference trajectory;
- invalid inertia tensors, non-finite runtime loads, constraints, ground, and
  multiple bodies fail before a result is returned.

Fixed-orientation hardening carried into this release:

- the independent `a=sin(t)`, `v=1-cos(t)`, `x=t-sin(t)` reference case must
  match position and velocity within `1e-9`;
- tightened translational integration tolerances must reduce trajectory error,
  with the tight velocity error below `1e-8`;
- force balance and unconstrained energy/momentum checks retain their existing
  `1e-12` to `1e-13` thresholds;
- inconsistent position/velocity states, redundant constraints, and non-finite
  runtime forces must fail explicitly;
- schema rows must carry validated names, kinds, components, body references,
  residual units, and multiplier units.

Examples target:

- constant principal-axis torque with an analytic orientation check;
- torque-free asymmetric rotation with conservation metrics;
- versioned JSON output with explicit orientation, angular-velocity, inertia,
  force, and torque conventions;
- an explicit statement that coupled and constrained rotation remain future
  milestones.

## Later Batches

Good candidates for future weekly releases:

- larger synthesis batches
- selected historical GIFs
- notebooks
- CAD/render handoff examples
- experimental 3D examples

Historical plots and animations should be curated before import. Do not bulk
copy the old workbench media into this repository without a source script,
caption, and reason for inclusion.
