"""Portable diagnostics payloads for healthy and problematic models."""

from __future__ import annotations

from mbsd import Mechanism


DiagnosticPayload = dict[str, float | int | bool | str | None]


def _add_zero_x_drive(mechanism, body) -> None:
    mechanism.coordinate_drive(
        body,
        "x",
        value=lambda _t: 0.0,
        velocity=lambda _t: 0.0,
        acceleration=lambda _t: 0.0,
    )


def run_analysis() -> dict[str, DiagnosticPayload]:
    healthy = Mechanism.planar(gravity=(0.0, 0.0))
    ground = healthy.ground()
    slider = healthy.body("slider", mass=1.0, inertia=0.01)
    healthy.slider(ground, slider, axis=(1.0, 0.0))
    healthy.coordinate_drive(
        slider,
        "x",
        value=lambda t: 0.25 + t,
        velocity=lambda _t: 1.0,
        acceleration=lambda _t: 0.0,
    )

    q = healthy.solve_position(t=0.5)
    v = healthy.solve_velocity(q, t=0.5)

    underconstrained = Mechanism.planar(gravity=(0.0, 0.0))
    ground = underconstrained.ground()
    slider = underconstrained.body("undriven-slider")
    underconstrained.slider(ground, slider, axis=(1.0, 0.0))

    rank_deficient = Mechanism.planar(gravity=(0.0, 0.0))
    ground = rank_deficient.ground()
    body = rank_deficient.body("redundantly-constrained")
    rank_deficient.pin(ground, body)
    _add_zero_x_drive(rank_deficient, body)

    return {
        "healthy": healthy.configuration_diagnostics(q, t=0.5, v=v).as_dict(),
        "underconstrained": underconstrained.configuration_diagnostics(
            q=[0.0] * underconstrained.ncoord
        ).as_dict(),
        "rank_deficient": rank_deficient.configuration_diagnostics(
            q=[0.0] * rank_deficient.ncoord
        ).as_dict(),
    }


def print_report(metrics: dict[str, DiagnosticPayload]) -> None:
    print("Planar diagnostics panel")
    for name, diagnostics in metrics.items():
        print(f"  {name}:")
        print(f"    classification:      {diagnostics['classification']}")
        print(f"    constraint residual: {diagnostics['constraint_norm']:.3e}")
        print(f"    Jacobian rank:       {diagnostics['jacobian_rank']}")
        print(f"    rank DOF:            {diagnostics['rank_degrees_of_freedom']}")


if __name__ == "__main__":
    print_report(run_analysis())
