# MBSD Examples

Runnable examples and generated gallery assets for
[MBSD Core](https://github.com/JAlcocerT/mbsd-core).

This repository is intentionally separate from `mbsd-core` so generated plots,
notebooks, animations, and richer case studies do not bloat the framework
package history.

## Install

The supported way to use this release is to clone the repository and run the
examples from source. The lightweight `mbsd_examples` package marker exists only
for repository metadata and local release checks; the wheel is not the user-facing
distribution for the examples, gallery images, or scripts.

Clone both repositories as siblings because examples resolves the paired core
checkout directly:

```bash
mkdir mbsd-framework
cd mbsd-framework
git clone https://github.com/JAlcocerT/mbsd-core.git
git clone https://github.com/JAlcocerT/mbsd-examples.git
git -C mbsd-core checkout v0.7.0
git -C mbsd-examples checkout v0.7.0
cd mbsd-examples
uv sync --extra dev
```

## Examples

```sh
uv run python examples/planar_driven_slider.py
uv run python examples/planar_mass_spring.py
uv run python examples/planar_slider_crank_analysis.py
uv run python examples/planar_four_bar.py
uv run python examples/planar_scotch_yoke.py
uv run python examples/planar_pendulum.py
uv run python examples/planar_energy_conservation.py
uv run python examples/planar_precision_synthesis.py
uv run python examples/planar_function_fit.py
uv run python examples/planar_export_handoff.py
uv run python examples/spatial_vocabulary.py
uv run python examples/planar_diagnostics_panel.py
uv run python examples/spatial_kinematics_preview.py
```

Generate the gallery:

```sh
make gallery
```

Run the full local check:

```sh
make check
```

## Gallery

Generated images live under:

```text
gallery/png/
```

The source scripts live under:

```text
examples/
scripts/
```

Generated export artifacts are written under:

```text
artifacts/export/
```

Spatial model artifacts are written under:

```text
artifacts/spatial/
```

Generated files remain ignored because their source examples reproduce them.

## What The Examples Show

| Example | Focus |
| --- | --- |
| `planar_driven_slider.py` | Prescribed planar motion and residual checks |
| `planar_mass_spring.py` | Constrained forward dynamics with damping |
| `planar_slider_crank_analysis.py` | Kinematic guardrails and finite-difference checks |
| `planar_four_bar.py` | Closed-loop linkage kinematics |
| `planar_scotch_yoke.py` | Slider tracking and stroke validation |
| `planar_pendulum.py` | Driven angular motion |
| `planar_energy_conservation.py` | Undamped energy-drift measurement |
| `planar_precision_synthesis.py` | Three-position four-bar synthesis |
| `planar_function_fit.py` | Rocker-function affine fitting |
| `planar_export_handoff.py` | Versioned JSON/CSV engineering handoff |
| `planar_diagnostics_panel.py` | Healthy, underconstrained, and singular diagnostics |
| `spatial_vocabulary.py` | Posed bodies, frames, joints, and spatial-model JSON |
| `spatial_kinematics_preview.py` | Point motion, frame resolution, joint residuals, and Jacobians |

The spatial examples remain experimental. They evaluate supplied poses and do
not claim a general spatial position, velocity, acceleration, or dynamics
solver.

The local `v0.8.0-dev` branch adds a limited experimental free-body dynamics
preview for simple 3D state propagation.

## Agent Samples

Agent-facing sample guidance lives under:

```text
docs/agent-instructions.md
docs/agent-mechanism-analysis.md
```

These files describe how to assemble small MBSD mechanism analyses while keeping
validation metrics visible for human review.

## Relationship To MBSD Core

[MBSD Core](https://github.com/JAlcocerT/mbsd-core) is the installable framework.
This repository is its companion collection of runnable examples, plots, and
case-study material.
