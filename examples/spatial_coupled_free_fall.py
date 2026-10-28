"""Two six-DOF rigid bodies in gravity with analytic translation checks."""

from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Pose3D, Quaternion


def run_analysis(output: Path) -> dict:
    mechanism = Mechanism.spatial()
    mechanism.body(
        "payload-a", mass=2.0, inertia=(2.0, 3.0, 4.0),
        pose=Pose3D((1.0, 0.0, 3.0), Quaternion.from_axis_angle((1.0, 0.0, 0.0), 0.3)),
    )
    mechanism.body(
        "payload-b", mass=5.0, inertia=(3.0, 4.0, 5.0),
        pose=Pose3D((-1.0, 2.0, 5.0), Quaternion.from_axis_angle((0.0, 1.0, 0.0), -0.4)),
    )
    times = np.linspace(0.0, 1.0, 51)
    result = mechanism.simulate_coupled_rigid_bodies(
        times, gravity_world=(0.0, 0.0, -9.81)
    )
    expected_z = np.array([3.0, 5.0])[None, :] - 4.905 * times[:, None] ** 2
    error = float(np.max(np.abs(result.center_of_mass_position[:, :, 2] - expected_z)))
    mechanism.coupled_result_to_json(result, output)
    return {"result": result, "diagnostics": mechanism.coupled_diagnostics(result), "error": error, "output": output}


def main() -> None:
    output = Path(__file__).parents[1] / "artifacts" / "spatial" / "coupled-free-fall.json"
    metrics = run_analysis(output)
    print("Coupled six-DOF free fall")
    print(f"  bodies:                    {metrics['diagnostics'].bodies}")
    print(f"  analytic position error:   {metrics['error']:.3e} m")
    print(f"  quaternion norm error:     {metrics['diagnostics'].max_quaternion_norm_error:.3e}")
    print(f"  result JSON:               {metrics['output']}")
    print("  joints/constraints:        unsupported until v0.9.4")


if __name__ == "__main__":
    main()
