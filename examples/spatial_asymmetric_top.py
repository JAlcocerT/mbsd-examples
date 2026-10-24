"""Torque-free asymmetric body with energy and momentum checks."""

import numpy as np

from mbsd import Mechanism


def run_analysis() -> dict:
    mechanism = Mechanism.spatial()
    mechanism.body("asymmetric-top", inertia=(2.0, 3.0, 4.0))
    result = mechanism.simulate_free_body(
        np.linspace(0.0, 5.0, 301), angular_velocity0_body=(0.7, 1.1, -0.4),
        rtol=1e-11, atol=1e-13,
    )
    return {"result": result, "diagnostics": mechanism.rigid_body_diagnostics(result)}


def main() -> None:
    diagnostics = run_analysis()["diagnostics"]
    print("Torque-free asymmetric rigid body")
    print(f"  relative energy change:   {diagnostics.relative_energy_change:.3e}")
    print(f"  angular momentum change:  {diagnostics.relative_angular_momentum_change:.3e}")
    print(f"  rotation orthogonality:   {diagnostics.max_rotation_orthogonality_error:.3e}")
    print("  constraints/joints:       unsupported by this free-body solver")


if __name__ == "__main__":
    main()
