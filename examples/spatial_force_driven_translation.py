"""Analytically validated fixed-orientation translational dynamics preview."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mbsd import Mechanism


ARTIFACT = Path(__file__).resolve().parents[1] / "artifacts/spatial/fixed-orientation-force.json"


def run_analysis(path: Path = ARTIFACT) -> dict[str, object]:
    mechanism = Mechanism.spatial()
    body = mechanism.body("payload", mass=2.0)
    thrust = mechanism.force(body, (2.0, 0.0, 0.0), name="constant-thrust")
    times = np.linspace(0.0, 1.0, 51)
    result = mechanism.simulate_fixed_orientation(times, forces=(thrust,))
    diagnostics = mechanism.dynamics_diagnostics(result)
    mechanism.dynamics_result_to_json(result, path)
    exact_position = 0.5 * times**2
    exact_velocity = times
    return {
        "path": path,
        "max_position_error": float(
            np.max(np.abs([pose.translation[0] for pose in result.body_poses(body)] - exact_position))
        ),
        "max_velocity_error": float(
            np.max(np.abs(result.body_linear_velocity(body)[:, 0] - exact_velocity))
        ),
        "diagnostics": diagnostics.as_dict(),
    }


def print_report(metrics: dict[str, object]) -> None:
    diagnostics = metrics["diagnostics"]
    print("Fixed-orientation force-driven translation")
    print(f"  result JSON:             {metrics['path']}")
    print(f"  analytic position error: {metrics['max_position_error']:.3e} m")
    print(f"  analytic velocity error: {metrics['max_velocity_error']:.3e} m/s")
    print(
        "  force-balance residual: "
        f"{diagnostics['max_force_balance_residual_n']:.3e} N"
    )
    print("  rotations/torques:       unsupported by this preview")


if __name__ == "__main__":
    print_report(run_analysis())
