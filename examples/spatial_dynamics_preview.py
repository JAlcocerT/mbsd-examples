"""Limited experimental 3D free-body dynamics preview."""

from __future__ import annotations

import numpy as np

from mbsd.spatial import Pose3D, SpatialState, simulate_free_body


def run_analysis() -> dict[str, object]:
    state = SpatialState(
        pose=Pose3D.identity(),
        linear_velocity=np.array([1.0, 0.0, 0.0]),
        angular_velocity=np.array([0.0, 0.0, 0.5]),
    )
    t = np.linspace(0.0, 1.0, 11)
    history = simulate_free_body(
        state,
        force=np.array([0.2, 0.0, 0.0]),
        torque=np.array([0.0, 0.0, 0.1]),
        mass=2.0,
        inertia=np.array([1.0, 1.0, 0.5]),
        t=t,
    )
    final_state = history[-1]
    return {
        "steps": len(history),
        "final_translation": final_state.pose.translation,
        "final_velocity": final_state.linear_velocity,
        "final_angular_velocity": final_state.angular_velocity,
        "final_state": final_state.as_dict(),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial dynamics preview")
    print(f"  steps:                {metrics['steps']}")
    print(f"  final translation:    {np.array2string(metrics['final_translation'], precision=6)}")
    print(f"  final velocity:       {np.array2string(metrics['final_velocity'], precision=6)}")
    print(
        "  final angular vel:    "
        f"{np.array2string(metrics['final_angular_velocity'], precision=6)}"
    )


if __name__ == "__main__":
    print_report(run_analysis())
