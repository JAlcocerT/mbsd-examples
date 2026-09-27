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
git -C mbsd-core checkout v0.6.0
git -C mbsd-examples checkout v0.6.0
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

For `v0.4.0`, the gallery remains small and reproducible. The export-handoff
example writes versioned mechanism and result JSON, a wide body-trajectory CSV,
and named-point JSON/CSV files under:

```text
artifacts/export/
```

The payloads demonstrate explicit units, frame conventions, metadata, and a
portable spring descriptor suitable for PWA prototyping and neutral CAD path
handoffs. Generated files remain ignored because the example reproduces them.

The `v0.5.0` release adds a pendulum-like experimental spatial vocabulary
example with a posed body, body-local frame, spherical world-pivot joint sketch,
and versioned JSON output under:

```text
artifacts/spatial/
```

It demonstrates a geometry/export vocabulary only. It does not solve spatial
constraints, kinematics, or dynamics, and the API may change before `1.0`.

The `v0.6.0` release adds a diagnostics-panel example that compares healthy,
underconstrained, and rank-deficient configurations using residuals, Jacobian
rank, rank-based DOF, and explicit classification fields.

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
