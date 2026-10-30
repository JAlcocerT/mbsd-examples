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
git -C mbsd-core checkout v0.9.6
git -C mbsd-examples checkout v0.9.6
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
uv run python examples/spatial_spherical_pendulum.py
uv run python examples/spatial_two_body_joint.py
uv run python examples/spatial_fixed_attachment.py
uv run python examples/spatial_singular_diagnostics.py
uv run python examples/spatial_force_driven_translation.py
uv run python examples/spatial_constrained_translation.py
uv run python examples/spatial_free_body_rotation.py
uv run python examples/spatial_asymmetric_top.py
uv run python examples/spatial_coupled_free_fall.py
uv run python examples/spatial_coupled_interaction.py
uv run python examples/spatial_dynamic_pendulum.py
uv run python examples/spatial_driven_hinge.py
uv run python examples/spatial_interop_handoff.py
uv run python examples/planar_joint_loads.py
uv run python examples/planar_guardrails.py
uv run python examples/planar_penalty_contact.py
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
| `spatial_spherical_pendulum.py` | Prescribed underdetermined spherical-joint path with kinematic metrics and JSON; not a dynamics simulation |
| `spatial_two_body_joint.py` | Two-body spherical-joint rank and degrees of freedom |
| `spatial_fixed_attachment.py` | Fully constrained fixed-orientation attachment |
| `spatial_singular_diagnostics.py` | Redundant constraints and actionable failure reporting |
| `spatial_result_reader.py` | Minimal consumer for spatial kinematic-result JSON |
| `spatial_force_driven_translation.py` | Constant-force case checked against its analytic trajectory and exported to JSON |
| `spatial_constrained_translation.py` | Acceleration-driven translation with constraint reactions and three-level residuals |
| `spatial_free_body_rotation.py` | Constant principal-axis torque checked against analytic rotation |
| `spatial_asymmetric_top.py` | Torque-free asymmetric body with energy and angular-momentum checks |
| `spatial_coupled_free_fall.py` | Two arbitrary-orientation rigid bodies under gravity with analytic checks |
| `spatial_coupled_interaction.py` | Equal-and-opposite pair force with total-momentum validation |
| `spatial_dynamic_pendulum.py` | Gravity-driven spherical pendulum with reaction and residual export |
| `spatial_driven_hinge.py` | Torque-driven revolute joint checked against analytic motion |
| `spatial_interop_handoff.py` | One result consumed by FreeCAD, Blender, and browser reference mappings |

The spatial examples remain experimental. Version `0.9.1` adds only
fixed-orientation translational dynamics: world-frame forces at coincident body
reference points/centers of mass, translation constraints, multipliers,
physical reactions, diagnostics, and JSON export. It does not integrate
orientation, accept torque, provide spatial inertia dynamics, contact, or a
broad joint catalog.

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

The paired `0.9.1` release demonstrates fixed-orientation translational
dynamics only. The examples expose world-frame center-of-mass forces,
constraint reactions, three-level residuals, and JSON handoffs while clearly
excluding quaternion integration, torque response, contact, and coupled
rotational dynamics.

The paired `0.9.2` release adds quaternion integration and torque response for
one unconstrained rigid body. It demonstrates principal-axis constant torque
and asymmetric torque-free motion. Multi-body coupling, joints, contact, and
constrained rotational reactions remain outside this solver.

The paired `0.9.3` release adds unconstrained multi-body six-DOF motion,
gravity, offset centers of mass, external loads, and equal-and-opposite pair
interactions. Joints, constraint reactions, and contact remain outside the
solver and are not implied by these examples.

The paired `0.9.4` release adds constrained rotational dynamics for spherical,
fixed, and revolute joints. It exposes multipliers, physical reaction forces
and moments, projection controls, stabilization, and mixed-unit constraint-row
identities. Contact and collision remain unsupported.

The paired `0.9.5` release hardens constrained identities and schemas, fixes
hinge motion through 180 degrees and multiple turns, and demonstrates a shared
engine-neutral transform contract through dependency-free FreeCAD-, Blender-,
and browser/PWA-oriented mappings.

The paired `0.9.6` release adds planar inverse dynamics and named joint loads
(`planar_joint_loads.py`: pin forces, drive torque, shaking force, and the
`mbsd.planar.joint_loads` handoff), the `validate` / `check` guardrails and an
exact JSON round trip (`planar_guardrails.py`), and penalty contact written as
a `force(fn)` callback outside core (`planar_penalty_contact.py`). Contact
stays an example-level model: the callback makes the mechanism non-portable by
design.
