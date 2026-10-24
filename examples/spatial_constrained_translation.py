"""Acceleration-driven constrained translation with reaction-force output."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mbsd import Mechanism


ARTIFACT = Path(__file__).resolve().parents[1] / "artifacts/spatial/constrained-translation.json"


def run_analysis(path: Path = ARTIFACT) -> dict[str, object]:
    mechanism = Mechanism.spatial()
    body = mechanism.body("driven-mass", mass=2.0)
    mechanism.coordinate_drive(
        body,
        "x",
        value=lambda t: t * t,
        velocity=lambda t: 2.0 * t,
        acceleration=lambda _t: 2.0,
    )
    result = mechanism.simulate_fixed_orientation(np.linspace(0.0, 1.0, 51))
    diagnostics = mechanism.dynamics_diagnostics(result)
    mechanism.dynamics_result_to_json(result, path)
    return {
        "path": path,
        "final_x": result.body_poses(body)[-1].translation[0],
        "final_velocity": result.body_linear_velocity(body)[-1, 0],
        "drive_reaction": result.reaction_force[-1, int(body), 0],
        "diagnostics": diagnostics.as_dict(),
    }


def print_report(metrics: dict[str, object]) -> None:
    diagnostics = metrics["diagnostics"]
    print("Fixed-orientation constrained translation")
    print(f"  result JSON:          {metrics['path']}")
    print(f"  final x:              {metrics['final_x']:.6f} m")
    print(f"  final velocity:       {metrics['final_velocity']:.6f} m/s")
    print(f"  drive reaction:       {metrics['drive_reaction']:.6f} N")
    print(
        "  acceleration residual: "
        f"{diagnostics['max_acceleration_residual_m_per_s2']:.3e} m/s^2"
    )


if __name__ == "__main__":
    print_report(run_analysis())
