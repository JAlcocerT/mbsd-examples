"""PWA-friendly diagnostics payload for one planar configuration."""

from __future__ import annotations

from mbsd import Mechanism


def run_analysis() -> dict[str, float | int | bool | None]:
    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    slider = mechanism.body("slider", mass=1.0, inertia=0.01)
    mechanism.slider(ground, slider, axis=(1.0, 0.0))
    mechanism.coordinate_drive(
        slider,
        "x",
        value=lambda t: 0.25 + t,
        velocity=lambda _t: 1.0,
        acceleration=lambda _t: 0.0,
    )

    q = mechanism.solve_position(t=0.5)
    v = mechanism.solve_velocity(q, t=0.5)
    return mechanism.configuration_diagnostics(q, t=0.5, v=v).as_dict()


def print_report(metrics: dict[str, float | int | bool | None]) -> None:
    print("Planar diagnostics panel")
    print(f"  constraint residual:   {metrics['constraint_norm']:.3e}")
    print(f"  velocity residual:     {metrics['velocity_residual_norm']:.3e}")
    print(f"  Jacobian rank:         {metrics['jacobian_rank']}")
    print(f"  rank DOF:              {metrics['rank_degrees_of_freedom']}")
    print(f"  finite:                {metrics['finite']}")


if __name__ == "__main__":
    print_report(run_analysis())
