"""Gravity-driven spherical pendulum with constrained rotational dynamics."""

from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Pose3D, Quaternion


def run_analysis(output: Path) -> dict:
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    rotation = Quaternion.from_axis_angle((0.0, 0.0, 1.0), 0.35)
    pivot = np.array([0.0, 1.0, 0.0])
    body = mechanism.body(
        "pendulum", mass=1.0, inertia=(0.2, 0.2, 0.2),
        pose=Pose3D(-rotation.rotate(pivot), rotation),
    )
    mechanism.spherical(ground, body, point_j=pivot, name="pivot")
    result = mechanism.simulate_constrained_rigid_bodies(
        np.linspace(0.0, 1.0, 101), gravity_world=(0.0, -9.81, 0.0),
        stabilization_frequency=10.0, rtol=1e-10, atol=1e-12,
    )
    diagnostics = mechanism.constrained_diagnostics(result)
    mechanism.constrained_result_to_json(result, output)
    return {"result": result, "diagnostics": diagnostics, "output": output}


def main() -> None:
    output = Path(__file__).parents[1] / "artifacts" / "spatial" / "dynamic-pendulum.json"
    metrics = run_analysis(output)
    print("Constrained spherical pendulum")
    print(f"  position residual:      {metrics['diagnostics'].max_position_residual:.3e}")
    print(f"  velocity residual:      {metrics['diagnostics'].max_velocity_residual:.3e}")
    print(f"  acceleration residual:  {metrics['diagnostics'].max_acceleration_residual:.3e}")
    print(f"  result JSON:            {metrics['output']}")


if __name__ == "__main__":
    main()
