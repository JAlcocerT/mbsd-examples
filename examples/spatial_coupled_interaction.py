"""Equal-and-opposite interaction between two free rigid bodies."""

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import Pose3D


def run_analysis() -> dict:
    mechanism = Mechanism.spatial()
    first = mechanism.body("first", mass=2.0, pose=Pose3D((-1.0, 0.0, 0.0)))
    second = mechanism.body("second", mass=3.0, pose=Pose3D((1.0, 0.0, 0.0)))
    interaction = mechanism.pair_interaction(
        first, second, (6.0, 0.0, 0.0), name="equal-opposite-pair"
    )
    result = mechanism.simulate_coupled_rigid_bodies(
        np.linspace(0.0, 1.0, 51), interactions=(interaction,)
    )
    momentum = np.sum(
        np.array([2.0, 3.0])[None, :, None] * result.linear_velocity, axis=1
    )
    return {
        "result": result,
        "diagnostics": mechanism.coupled_diagnostics(result),
        "max_momentum": float(np.max(np.abs(momentum))),
    }


def main() -> None:
    metrics = run_analysis()
    print("Coupled equal-and-opposite interaction")
    print(f"  max total momentum:        {metrics['max_momentum']:.3e} kg*m/s")
    print(f"  internal force imbalance:  {metrics['diagnostics'].max_internal_force_imbalance_n:.3e} N")
    print("  joints/constraints:        unsupported until v0.9.4")


if __name__ == "__main__":
    main()
