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

For local development next to `mbsd-core`:

```sh
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

For `v0.3.0`, the gallery remains small and reproducible while adding a first
2D synthesis preview: three-precision-point four-bar synthesis and rocker
function fitting. Larger GIFs, historical media, CAD/render outputs, notebooks,
larger synthesis batches, and 3D animations should arrive in later weekly
releases.

## Agent Samples

Agent-facing sample guidance lives under:

```text
docs/agent-instructions.md
docs/agent-mechanism-analysis.md
```

These files describe how to assemble small MBSD mechanism analyses while keeping
validation metrics visible for human review.

## Relationship To MBSD Core

`mbsd-core` is the installable framework. This repository is a companion
collection of examples, plots, and case-study material.
