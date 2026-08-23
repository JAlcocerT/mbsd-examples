# MBSD Mechanism Analysis Playbook

Use this playbook when creating an MBSD mechanism analysis for the 0.1 public
API.

## Goal

Create a runnable Python analysis that an agent can assemble and a human can
validate.

## Required Shape

1. Build the model through `Mechanism.planar()`.
2. Declare parameters explicitly: lengths, masses, inertias, drive speed, and
   time span.
3. Name bodies and joints with mechanism terms.
4. Provide a physically meaningful initial guess.
5. Solve with the public kinematic or dynamic API.
6. Print validation metrics before interpretation.
7. Keep any plotting optional so the example remains fast in `make check`.

## Minimum Guardrails

Print or compute:

- number of coordinates
- number of constraints
- maximum constraint residual
- drive tracking error, if driven
- relevant joint or rail errors
- at least one interpretable motion metric such as stroke, peak velocity, or
  final displacement

## Avoid

- hidden parameters
- undocumented units
- claims about 3D stability on the 0.1 branch
- generated scripts that bypass the public API
- plots or files created during the default example run

