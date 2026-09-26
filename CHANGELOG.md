# Changelog

## v0.6.0-dev - 2D Diagnostics Panel

Local development branch only.

- Add a planar diagnostics-panel example around
  `PlanarMechanism.configuration_diagnostics()`.
- Move the examples package version to `0.6.0.dev0` and depend on local
  `mbsd>=0.6.0.dev0,<0.7`.
- Keep the example focused on PWA-friendly status metrics rather than UI code.

## v0.5.0 - Experimental 3D Vocabulary

Week 5 companion release for MBSD Core `v0.5.0`.

- Add a pendulum-like spatial vocabulary example with a posed body, body-local
  frame, and spherical world-pivot joint sketch.
- Write and validate a versioned spatial-model JSON handoff artifact.
- Move the examples package version to `0.5.0` and depend on
  `mbsd>=0.5,<0.6`.
- Keep the examples 3D scope to data modeling and pose/frame/joint exports; no
  solved 3D mechanism behavior is claimed yet.

## v0.4.0 - Export Handoff

Week 4 companion release for MBSD Core `v0.4.0`.

- Add a planar export-handoff example that writes mechanism JSON, result JSON,
  trajectory CSV, and named-point JSON/CSV artifacts.
- Demonstrate explicit SI units, coordinate conventions, caller metadata, and
  a portable spring-damper descriptor for PWA/CAD consumers.
- Parse and validate every generated handoff artifact in tests.
- Move the examples package version to `0.4.0` and depend on
  `mbsd>=0.4,<0.5`.
- Expose the installed package version through `mbsd_examples.__version__`.
- Keep generated handoff artifacts under ignored `artifacts/` output.
- Keep public browser/PWA code outside the OSS repositories.

## v0.3.0 - Week 3 Synthesis Preview

Prepared release candidate for MBSD Core `v0.3.0`.

- Add three-precision-point four-bar synthesis example.
- Add rocker function fitting example.
- Refresh the gallery generator and PNG list with synthesis outputs.
- Add numerical regression assertions for example metrics.
- Bound the paired core dependency to the compatible `0.3.x` release line and
  keep CI pinned to `mbsd-core` `v0.3.0`.
- Document the examples repo as repo-first: clone and run from source rather
  than expecting the marker wheel to contain runnable examples and gallery
  assets.
- Keep synthesis scope narrow: no large optimization batches, notebooks, CAD,
  or 3D examples in this release.

## v0.2.0 - Week 2 Examples

Prepared release candidate for MBSD Core `v0.2.0`.

- Add canonical four-bar linkage, scotch-yoke, driven-pendulum, and
  undamped mass-spring energy examples.
- Refresh the gallery generator and PNG list for the Week 2 examples.
- Use the new core validation helpers in the Week 2 examples.
- Make the examples repository buildable by adding a minimal
  `mbsd_examples` package marker.
- Pin CI to the paired `mbsd-core` `v0.2.0` release tag for release
  reproducibility.
- Keep larger media, notebooks, synthesis batches, CAD/render handoffs, and 3D
  examples out of this release.

## v0.1.0 - Week 1 Examples

Initial examples companion release for MBSD Core `v0.1.0`.

- Add runnable driven-slider, mass-spring-damper, and slider-crank examples.
- Add reproducible gallery-generation script.
- Add small PNG gallery for the Week 1 release.
- Keep historical media, GIFs, notebooks, CAD/render assets, synthesis batches,
  and 3D examples out of the first examples release.
