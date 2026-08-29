"""Four-bar linkage kinematics using the public MBSD API."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism


def build_four_bar() -> tuple[object, np.ndarray, dict[str, float]]:
    crank_length = 0.30
    coupler_length = 0.85
    rocker_length = 0.70
    ground_length = 0.90
    angular_speed = 2.0 * np.pi

    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    crank = mechanism.body("crank", mass=0.4, inertia=0.01)
    coupler = mechanism.body("coupler", mass=0.8, inertia=0.03)
    rocker = mechanism.body("rocker", mass=0.5, inertia=0.02)

    mechanism.pin(ground, crank, point_a=(0.0, 0.0), point_b=(0.0, 0.0))
    mechanism.pin(crank, coupler, point_a=(crank_length, 0.0), point_b=(0.0, 0.0))
    mechanism.pin(coupler, rocker, point_a=(coupler_length, 0.0), point_b=(rocker_length, 0.0))
    mechanism.pin(ground, rocker, point_a=(ground_length, 0.0), point_b=(0.0, 0.0))
    mechanism.motor(crank, omega=angular_speed)

    coupler_origin = np.array([crank_length, 0.0])
    pivot_distance = ground_length - crank_length
    x = (
        coupler_length**2
        - rocker_length**2
        + pivot_distance**2
    ) / (2.0 * pivot_distance)
    y = np.sqrt(coupler_length**2 - x**2)
    coupler_rocker_pin = coupler_origin + np.array([x, y])

    coupler_angle = np.arctan2(y, x)
    rocker_angle = np.arctan2(
        coupler_rocker_pin[1],
        coupler_rocker_pin[0] - ground_length,
    )

    q0 = np.zeros(mechanism.ncoord)
    q0[3:6] = [0.0, 0.0, 0.0]
    q0[6:9] = [coupler_origin[0], coupler_origin[1], coupler_angle]
    q0[9:12] = [ground_length, 0.0, rocker_angle]

    params = {
        "crank_length": crank_length,
        "coupler_length": coupler_length,
        "rocker_length": rocker_length,
        "ground_length": ground_length,
        "angular_speed": angular_speed,
    }
    return mechanism, q0, params


def run_analysis(nsteps: int = 361) -> dict[str, float]:
    mechanism, q0, params = build_four_bar()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)
    mechanism.assert_constraints_satisfied(result)
    diagnostics = mechanism.diagnostics(result)

    coupler_angle = result.q[8, :]
    rocker_angle = result.q[11, :]

    return {
        "coordinates": float(diagnostics.coordinates),
        "constraints": float(diagnostics.constraints),
        "max_constraint_residual": diagnostics.max_constraint_residual,
        "coupler_angle_range": float(np.ptp(coupler_angle)),
        "rocker_angle_range": float(np.ptp(rocker_angle)),
        **params,
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Four-bar linkage")
    print(f"  coordinates / constraints: {metrics['coordinates']:.0f} / {metrics['constraints']:.0f}")
    print(f"  crank length:              {metrics['crank_length']:.3f} m")
    print(f"  coupler length:            {metrics['coupler_length']:.3f} m")
    print(f"  rocker length:             {metrics['rocker_length']:.3f} m")
    print(f"  ground length:             {metrics['ground_length']:.3f} m")
    print(f"  max constraint residual:   {metrics['max_constraint_residual']:.3e}")
    print(f"  coupler angle range:       {metrics['coupler_angle_range']:.6f} rad")
    print(f"  rocker angle range:        {metrics['rocker_angle_range']:.6f} rad")


def save_plot(path: Path, nsteps: int = 361) -> None:
    import matplotlib.pyplot as plt

    mechanism, q0, params = build_four_bar()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)

    crank_pin = np.column_stack(
        (
            params["crank_length"] * np.cos(result.q[5, :]),
            params["crank_length"] * np.sin(result.q[5, :]),
        )
    )
    coupler_pin = np.column_stack(
        (
            result.q[6, :] + params["coupler_length"] * np.cos(result.q[8, :]),
            result.q[7, :] + params["coupler_length"] * np.sin(result.q[8, :]),
        )
    )

    fig, ax = plt.subplots(figsize=(7.0, 4.5))
    ax.plot(crank_pin[:, 0], crank_pin[:, 1], label="crank pin")
    ax.plot(coupler_pin[:, 0], coupler_pin[:, 1], label="coupler-rocker pin")
    ax.plot([0.0, params["ground_length"]], [0.0, 0.0], "k--", label="ground")
    ax.set_title("Four-bar linkage")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nsteps", type=int, default=361)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()

    metrics = run_analysis(nsteps=args.nsteps)
    print_report(metrics)
    if args.plot is not None:
        save_plot(args.plot, nsteps=args.nsteps)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
