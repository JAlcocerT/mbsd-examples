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
    result = mechanism.simulate(
        np.linspace(0.0, 1.0, 51), interactions=(interaction,), rtol=1e-10, atol=1e-12
    )
    momentum = np.sum(
        np.array([2.0, 3.0])[None, :, None] * result.linear_velocity, axis=1
    )
    net_applied = np.sum(result.applied_force_world, axis=1)
    return {
        "result": result,
        "check": mechanism.check(result),
        "max_momentum": float(np.max(np.abs(momentum))),
        "pair_force_balance_residual_n": float(np.max(np.abs(net_applied))),
    }


def main() -> None:
    metrics = run_analysis()
    print("Coupled equal-and-opposite interaction (simulate, interactions=)")
    print(f"  max total momentum:          {metrics['max_momentum']:.3e} kg*m/s")
    print(f"  pair-force balance residual: {metrics['pair_force_balance_residual_n']:.3e} N")
    print(f"  check passed:                {metrics['check'].passed}")


if __name__ == "__main__":
    main()
