"""Constant-torque free rigid-body rotation with an analytic check."""

from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Quaternion


def run_analysis(output: Path) -> dict:
    mechanism = Mechanism.spatial()
    rotor = mechanism.body("rotor", mass=2.0, inertia=(2.0, 3.0, 4.0))
    motor = mechanism.rigid_body_load(rotor, torque=(2.0, 0.0, 0.0), name="motor")
    times = np.linspace(0.0, 1.0, 101)
    result = mechanism.simulate_free_body(times, loads=(motor,))
    diagnostics = mechanism.rigid_body_diagnostics(result)
    expected = Quaternion.from_axis_angle((1.0, 0.0, 0.0), 0.5)
    orientation_error = float(np.max(np.abs(
        result.poses[-1].rotation.to_rotation_matrix() - expected.to_rotation_matrix()
    )))
    mechanism.rigid_body_result_to_json(result, output)
    return {"result": result, "diagnostics": diagnostics, "orientation_error": orientation_error, "output": output}


def main() -> None:
    output = Path(__file__).parents[1] / "artifacts" / "spatial" / "free-body-rotation.json"
    metrics = run_analysis(output)
    print("Free rigid-body constant-torque rotation")
    print(f"  result JSON:              {metrics['output']}")
    print(f"  final angular speed:      {metrics['result'].angular_velocity_body[-1, 0]:.6f} rad/s")
    print(f"  analytic orientation err: {metrics['orientation_error']:.3e}")
    print(f"  quaternion norm error:    {metrics['diagnostics'].max_quaternion_norm_error:.3e}")
    print("  constraints/joints:       unsupported by this free-body solver")


if __name__ == "__main__":
    main()
