"""Prescribed kinematic path for an underdetermined spherical-joint model."""

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
    model_diagnostics = mechanism.model_diagnostics(result.poses[0])
    mechanism.result_to_json(result, path)
    return {
        "path": path,
        "model_id": result.model_id,
        "excitation_id": result.excitation_id,
        "final_x": result.body_poses(link)[-1].translation[0],
        "diagnostics": diagnostics.as_dict(),
        "degrees_of_freedom": model_diagnostics.degrees_of_freedom,
        "classification": model_diagnostics.classification,
    }


def print_report(metrics: dict[str, object]) -> None:
    diagnostics = metrics["diagnostics"]
    print("Spatial spherical-joint kinematic path")
    print(f"  classification:        {metrics['classification']}")
    print(f"  remaining DOF:         {metrics['degrees_of_freedom']}")
    print(f"  model id:              {metrics['model_id']}")
    print(f"  final driven x:        {metrics['final_x']:.6f} m")
    print(
        "  translation residual: "
        f"{diagnostics['max_translation_residual_m']:.3e} m"
    )
    print(
        "  rotation residual:    "
        f"{diagnostics['max_rotation_residual_rad']:.3e} rad"
    )
    print(
        "  linear vel residual:  "
        f"{diagnostics['max_linear_velocity_residual_m_per_s']:.3e} m/s"
    )
    print(
        "  angular vel residual: "
        f"{diagnostics['max_angular_velocity_residual_rad_per_s']:.3e} rad/s"
    )
    print(
        "  trajectory linear FD: "
        f"{diagnostics['max_trajectory_linear_velocity_error']:.3e} m/s"
    )
    print(
        "  trajectory angular FD: "
        f"{diagnostics['max_trajectory_angular_velocity_error']:.3e} rad/s"
    )


if __name__ == "__main__":
    print_report(run_analysis())
