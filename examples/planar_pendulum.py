"""Driven planar pendulum kinematics using the public MBSD API."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism


def build_pendulum() -> tuple[object, np.ndarray, dict[str, float]]:
    length = 0.75
    amplitude = 0.65
    angular_speed = 2.0 * np.pi

    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    link = mechanism.body("pendulum", mass=1.0, inertia=0.04)

    mechanism.pin(ground, link, point_a=(0.0, 0.0), point_b=(0.0, 0.0))
    mechanism.coordinate_drive(
        link,
        "theta",
        value=lambda t: amplitude * np.sin(angular_speed * t),
        velocity=lambda t: amplitude * angular_speed * np.cos(angular_speed * t),
        acceleration=lambda t: -(amplitude * angular_speed**2) * np.sin(angular_speed * t),
    )

    q0 = np.zeros(mechanism.ncoord)
    params = {"length": length, "amplitude": amplitude, "angular_speed": angular_speed}
    return mechanism, q0, params


def run_analysis(nsteps: int = 361) -> dict[str, float]:
    mechanism, q0, params = build_pendulum()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)
    mechanism.assert_constraints_satisfied(result)

    theta = result.q[5, :]
    bob_x = params["length"] * np.cos(theta)
    bob_y = params["length"] * np.sin(theta)

    return {
        "coordinates": float(mechanism.ncoord),
        "constraints": float(mechanism.nrestr),
        "max_constraint_residual": mechanism.max_constraint_residual(result),
        "theta_range": float(np.ptp(theta)),
        "bob_x_range": float(np.ptp(bob_x)),
        "bob_y_range": float(np.ptp(bob_y)),
        **params,
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Driven pendulum")
    print(f"  coordinates / constraints: {metrics['coordinates']:.0f} / {metrics['constraints']:.0f}")
    print(f"  length:                    {metrics['length']:.3f} m")
    print(f"  amplitude:                 {metrics['amplitude']:.3f} rad")
    print(f"  max constraint residual:   {metrics['max_constraint_residual']:.3e}")
    print(f"  theta range:               {metrics['theta_range']:.6f} rad")
    print(f"  bob x/y range:             {metrics['bob_x_range']:.6f} / {metrics['bob_y_range']:.6f} m")


def save_plot(path: Path, nsteps: int = 361) -> None:
    import matplotlib.pyplot as plt

    mechanism, q0, params = build_pendulum()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)
    theta = result.q[5, :]
    bob_x = params["length"] * np.cos(theta)
    bob_y = params["length"] * np.sin(theta)

    fig, axes = plt.subplots(1, 2, figsize=(8.0, 4.0))
    axes[0].plot(t, theta)
    axes[0].set_title("Pendulum angle")
    axes[0].set_xlabel("time [s]")
    axes[0].set_ylabel("theta [rad]")
    axes[0].grid(True, alpha=0.35)
    axes[1].plot(bob_x, bob_y)
    axes[1].plot([0.0], [0.0], "ko")
    axes[1].set_title("Bob path")
    axes[1].set_xlabel("x [m]")
    axes[1].set_ylabel("y [m]")
    axes[1].axis("equal")
    axes[1].grid(True, alpha=0.35)
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
