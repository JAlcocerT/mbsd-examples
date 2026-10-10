"""Fixed spatial attachment with complete position and velocity checks."""

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Pose3D, Quaternion


def run_analysis() -> dict[str, object]:
    target = Pose3D(
        translation=(0.3, -0.2, 0.5),
        rotation=Quaternion.from_axis_angle((1.0, 1.0, 0.0), 0.4),
    )
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    link = mechanism.body("fixed-link", pose=target)
    mechanism.fixed(ground, link, frame_i=target, name="attachment")
    result = mechanism.solve_kinematics(np.array([0.0, 0.1]))
    return {
        "model": mechanism.model_diagnostics().as_dict(),
        "result": mechanism.result_diagnostics(result).as_dict(),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial fixed attachment")
    print(f"  classification:        {metrics['model']['classification']}")
    print(f"  position residual:     {metrics['result']['max_position_residual']:.3e}")
    print(f"  velocity residual:     {metrics['result']['max_velocity_residual']:.3e}")


if __name__ == "__main__":
    print_report(run_analysis())
