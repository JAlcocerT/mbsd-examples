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
0.4.0: export and CAD bridge
0.5.0: experimental 3D track
```

## Later Batches

Good candidates for future weekly releases:

- larger synthesis batches
- browser/Pyodide examples
- selected historical GIFs
- notebooks
- CAD/render handoff examples
- experimental 3D examples

Historical plots and animations should be curated before import. Do not bulk
copy the old workbench media into this repository without a source script,
caption, and reason for inclusion.
