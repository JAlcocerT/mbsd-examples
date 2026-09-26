# MBSD Examples Release Plan

This is the practical companion roadmap for `mbsd-core` and `mbsd-examples`.
Keep `mbsd-core` small and technical; use this repo and the website docs to
explain the weekly release story.

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
0.8.0: 3D dynamics preview
0.9.0: integration and case-study track
0.9.1+: additional curated examples, integrations, and case studies
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
PWA and neutral CAD-path consumers. Arbitrary Python force callbacks remain
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
- offset center-of-mass dynamics support or a narrower documented boundary
- optional stabilization/projection controls for constrained dynamics
- stronger energy, residual, and regression tests

Examples target:

- examples that expose solver diagnostics
- validation-heavy 2D mechanisms
- comparison plots for residuals, energy, and solver behavior

## v0.7.0

Week 7 should introduce a 3D kinematics preview.

Core target:

- basic spatial constraints and Jacobian structure
- one or two solved 3D kinematic mechanisms
- explicit experimental namespace and warnings
- no broad contact, collision, or multiphysics claims

Examples target:

- simple spatial kinematics examples
- validation metrics for 3D position-level and velocity-level constraints

## v0.8.0

Week 8 should introduce a limited 3D dynamics preview only if the kinematic track
is stable enough.

Core target:

- spatial mass/inertia use in constrained acceleration solves
- basic 3D time integration for very small systems
- clear limitations around contact, collision, and complex joints

Examples target:

- one or two minimal 3D dynamics examples
- conservative validation metrics and failure-mode notes

## v0.9.x

The `0.9.x` line should be the public integration and case-study track. Use it to
show credible applications without bloating `mbsd-core`.

Core target:

- only small API additions discovered through examples and integrations
- compatibility fixes, diagnostics, export refinements, and performance cleanups
- no notebook, media, website, or private-app code

Examples target:

- curated case studies
- integration examples with CAD/render/data tools
- notebooks where they add durable explanation
- selected historical GIFs and plots with source scripts, captions, and
  provenance
- larger synthesis batches when they are reproducible

Public browser/PWA work is intentionally not part of the OSS roadmap. A private
PWA can build on top of `mbsd-core` and consume the same export/result schemas
without becoming part of the public repos.

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
