"""Torque-driven revolute joint checked against analytic motion."""

import numpy as np

from mbsd import Mechanism


def run_analysis() -> dict:
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    rotor = mechanism.body("rotor", inertia=(2.0, 3.0, 4.0))
    mechanism.revolute(ground, rotor, name="hinge")
    motor = mechanism.rigid_body_load(rotor, torque=(0.0, 0.0, 4.0), name="motor")
    times = np.linspace(0.0, 1.0, 51)
    result = mechanism.simulate_constrained_rigid_bodies(
        times, loads=(motor,), rtol=1e-10, atol=1e-12
    )
    angles = np.asarray([
        np.arctan2(step[1].rotation.to_rotation_matrix()[1, 0], step[1].rotation.to_rotation_matrix()[0, 0])
        for step in result.poses
    ])
    return {
        "result": result, "diagnostics": mechanism.constrained_diagnostics(result),
        "angle_error": float(np.max(np.abs(angles - 0.5 * times**2))),
        "speed_error": float(np.max(np.abs(result.angular_velocity_body[:, 1, 2] - times))),
    }


def main() -> None:
    metrics = run_analysis()
    print("Torque-driven spatial hinge")
    print(f"  analytic angle error:    {metrics['angle_error']:.3e} rad")
    print(f"  analytic speed error:    {metrics['speed_error']:.3e} rad/s")
    print(f"  degrees of freedom:      {metrics['diagnostics'].degrees_of_freedom}")


if __name__ == "__main__":
    main()
