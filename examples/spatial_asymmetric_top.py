"""Torque-free asymmetric body with energy and momentum checks."""

import numpy as np

from mbsd import Mechanism


def run_analysis() -> dict:
    mechanism = Mechanism.spatial()
    mechanism.body("asymmetric-top", inertia=(2.0, 3.0, 4.0))
    result = mechanism.simulate(
        np.linspace(0.0, 5.0, 301), angular_velocity0_body={"asymmetric-top": (0.7, 1.1, -0.4)},
        rtol=1e-11, atol=1e-13,
    )
    inertia = result.inertia_tensor_body[0]
    omega = result.angular_velocity_body[:, 0]
    momentum = np.array([
        step[0].rotation.to_rotation_matrix() @ (inertia @ omega[k])
        for k, step in enumerate(result.poses)
    ])
    momentum_change = float(np.max(np.linalg.norm(momentum - momentum[0], axis=1)))
    rotations = [step[0].rotation.to_rotation_matrix() for step in result.poses]
    orthogonality = max(float(np.max(np.abs(r.T @ r - np.eye(3)))) for r in rotations)
    verdict = mechanism.check(result)
    energy = next(check for check in verdict.checks if check.name == "energy_drift")
    return {
        "result": result,
        "check": verdict,
        "relative_energy_change": energy.value,
        "relative_angular_momentum_change": momentum_change / float(np.linalg.norm(momentum[0])),
        "rotation_orthogonality_error": orthogonality,
    }


def main() -> None:
    metrics = run_analysis()
    print("Torque-free asymmetric rigid body (simulate, no joints)")
    print(f"  relative energy change:   {metrics['relative_energy_change']:.3e}")
    print(f"  angular momentum change:  {metrics['relative_angular_momentum_change']:.3e}")
    print(f"  rotation orthogonality:   {metrics['rotation_orthogonality_error']:.3e}")
    print(f"  check passed:             {metrics['check'].passed}")


if __name__ == "__main__":
    main()
