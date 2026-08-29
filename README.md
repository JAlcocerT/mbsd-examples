# MBSD Examples

Runnable examples and generated gallery assets for
[MBSD Core](https://github.com/JAlcocerT/mbsd-core).

This repository is intentionally separate from `mbsd-core` so generated plots,
notebooks, animations, and richer case studies do not bloat the framework
package history.

## Install

For local development next to `mbsd-core`:

```sh
uv sync --extra dev
```

For a future public install after `mbsd-core` is published:

```sh
pip install -e .[dev]
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

For `v0.2.0`, the gallery remains small and reproducible while adding canonical
planar mechanisms: four-bar linkage, scotch yoke, driven pendulum, and an
undamped mass-spring energy check. Larger GIFs, historical media, CAD/render
outputs, notebooks, synthesis batches, and 3D animations should arrive in
later weekly releases.

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
