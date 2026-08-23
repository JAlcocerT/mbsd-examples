# Agent Instructions for MBSD

MBSD is a Python framework for inspectable multibody mechanism models. The
project is intended for a workflow where agents can assemble models and humans
can validate the physics.

## Current Public Scope

The `main` branch is the 0.1 public core. Treat it as a planar mechanism
framework first.

Use the public API unless there is a clear reason to inspect the lower-level
kernel:

```python
from mbsd import Mechanism

mechanism = Mechanism.planar()
```

The public 0.1 surface supports:

- planar rigid bodies with `[x, y, theta]` coordinates
- revolute joints through `pin`
- prismatic joints through `slider`
- scalar coordinate drives
- angular motors
- kinematic solves
- constrained dynamics
- spring, damping, gravity, and contact-force helpers

The 3D kernel exists in the historical workbench, but do not expose or document
3D as a stable public API on this branch.

## Local Workflow

Install and verify with:

```sh
uv sync --extra dev
make check
```

Run examples with:

```sh
make examples
```

If a change touches the public API, examples, solver behavior, or docs that
claim runnable behavior, run `make check` before committing.

## Modeling Rules

- Prefer `Mechanism.planar()` for new public examples.
- Give bodies descriptive names such as `crank`, `connecting_rod`, or `slider`.
- Keep geometry parameters explicit near the top of the script.
- Use SI-style units in examples unless a different convention is stated.
- Make initial guesses physically meaningful and easy to inspect.
- Keep generated models ordinary Python that a human can review.

## Physics Guardrails

Every non-trivial analysis should include at least some validation output.
Useful checks for the 0.1 API:

- coordinate and constraint count
- maximum constraint residual
- drive tracking error
- slider rail errors such as max `|y|` and max `|theta|`
- finite-difference consistency checks for velocity or acceleration
- min/max/stroke or other physically interpretable output

Do not present a simulation as physically validated only because it runs. A
running model still needs residuals, assumptions, and result checks.

## Contribution Rules

- Keep the public API small and readable.
- Prefer examples that show the mechanism concepts directly.
- Do not add broad industrial-solver claims.
- Do not invent APIs in documentation unless the implementation exists.
- Do not commit generated caches or local build outputs.
- Keep public docs aligned with the actual 0.1 surface.
