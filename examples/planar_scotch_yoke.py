"""Scotch-yoke kinematics using pins, sliders, and a crank drive."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism


def build_scotch_yoke() -> tuple[object, np.ndarray, dict[str, float]]:
    radius = 0.35
    angular_speed = 2.0 * np.pi

    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    crank = mechanism.body("crank", mass=0.4, inertia=0.01)
    pin = mechanism.body("crank_pin", mass=0.1, inertia=0.005)
    yoke = mechanism.body("yoke", mass=1.0, inertia=0.02)

    mechanism.pin(ground, crank, point_a=(0.0, 0.0), point_b=(0.0, 0.0))
    mechanism.pin(crank, pin, point_a=(radius, 0.0), point_b=(0.0, 0.0))
    mechanism.slider(ground, yoke, axis=(1.0, 0.0))
    mechanism.slider(yoke, pin, axis=(0.0, 1.0))
    mechanism.motor(crank, omega=angular_speed)

    q0 = np.zeros(mechanism.ncoord)
    q0[6:9] = [radius, 0.0, 0.0]
    q0[9:12] = [radius, 0.0, 0.0]

    params = {"radius": radius, "angular_speed": angular_speed}
    return mechanism, q0, params


def run_analysis(nsteps: int = 361) -> dict[str, float]:
    mechanism, q0, params = build_scotch_yoke()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)
    mechanism.assert_constraints_satisfied(result)

    yoke_x = result.q[9, :]
    expected_x = params["radius"] * np.cos(params["angular_speed"] * t)

    return {
        "coordinates": float(mechanism.ncoord),
        "constraints": float(mechanism.nrestr),
        "max_constraint_residual": mechanism.max_constraint_residual(result),
        "max_x_error": float(np.max(np.abs(yoke_x - expected_x))),
        "stroke": float(np.ptp(yoke_x)),
        **params,
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Scotch yoke")
    print(f"  coordinates / constraints: {metrics['coordinates']:.0f} / {metrics['constraints']:.0f}")
    print(f"  crank radius:              {metrics['radius']:.3f} m")
    print(f"  max constraint residual:   {metrics['max_constraint_residual']:.3e}")
    print(f"  max x tracking error:      {metrics['max_x_error']:.3e}")
    print(f"  yoke stroke:               {metrics['stroke']:.6f} m")


def save_plot(path: Path, nsteps: int = 361) -> None:
    import matplotlib.pyplot as plt

    mechanism, q0, params = build_scotch_yoke()
    t = np.linspace(0.0, 1.0, nsteps)
    result = mechanism.solve_kinematics(t, q0=q0)
    expected_x = params["radius"] * np.cos(params["angular_speed"] * t)

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(t, result.q[9, :], label="MBSD yoke x")
    ax.plot(t, expected_x, "--", label="r cos(theta)")
    ax.set_title("Scotch yoke")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("x [m]")
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
