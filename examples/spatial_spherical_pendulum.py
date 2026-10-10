"""Constrained spatial pendulum-like pose sequence."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Pose3D


ARTIFACT = Path(__file__).resolve().parents[1] / "artifacts/spatial/kinematic-result.json"


def run_analysis(path: Path = ARTIFACT) -> dict[str, object]:
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    link = mechanism.body("pendulum", pose=Pose3D(translation=(0.0, -1.0, 0.0)))
    mechanism.spherical(ground, link, point_j=(0.0, 1.0, 0.0), name="pivot")
    mechanism.coordinate_drive(
        link, "x", value=lambda t: 0.2 * t, velocity=lambda _t: 0.2
    )
    result = mechanism.solve_kinematics(np.linspace(0.0, 0.5, 6), tol=1e-8)
    diagnostics = mechanism.result_diagnostics(result)
    mechanism.result_to_json(result, path)
    return {
        "path": path,
        "model_id": result.model_id,
        "final_x": result.body_poses(link)[-1].translation[0],
        "diagnostics": diagnostics.as_dict(),
    }


def print_report(metrics: dict[str, object]) -> None:
    diagnostics = metrics["diagnostics"]
    print("Spatial spherical pendulum")
    print(f"  model id:              {metrics['model_id']}")
    print(f"  final driven x:        {metrics['final_x']:.6f} m")
    print(f"  position residual:     {diagnostics['max_position_residual']:.3e}")
    print(f"  velocity residual:     {diagnostics['max_velocity_residual']:.3e}")


if __name__ == "__main__":
    print_report(run_analysis())
