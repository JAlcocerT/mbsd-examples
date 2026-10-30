"""Penalty contact as a Python force callback: a ball bouncing on the floor.

Contact is deliberately not part of MBSD core. ``force(fn)`` lets a workflow
add its own contact model; the mechanism then reports itself as non-portable,
because the callback cannot be serialized.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism


def build_ball(stiffness: float = 2e4, damping: float = 15.0):
    radius, mass = 0.05, 0.2
    mechanism = Mechanism.planar(gravity=(0.0, -9.81))
    ground = mechanism.ground()
    ball = mechanism.body("ball", mass=mass, inertia=0.4 * mass * radius**2)
    mechanism.slider(ground, ball, axis=(0.0, 1.0), name="guide")
    col = 3 * int(ball) + 1

    def floor_contact(t, q, v):
        Q = np.zeros(mechanism.ncoord)
        penetration = radius - q[col]
        if penetration > 0.0:
            Q[col] = max(0.0, stiffness * penetration - damping * v[col])
        return Q

    mechanism.force(floor_contact, name="floor_contact")
    q0 = np.zeros(mechanism.ncoord)
    q0[col] = 0.5
    params = {"radius": radius, "mass": mass, "drop_height": 0.5, "col": col,
              "stiffness": stiffness, "damping": damping}
    return mechanism, q0, params


def simulate(nsteps: int = 1201, t_end: float = 1.2):
    mechanism, q0, params = build_ball()
    t = np.linspace(0.0, t_end, nsteps)
    result = mechanism.simulate(t, q0, allow_underconstrained=True, method="LSODA",
                                rtol=1e-8, atol=1e-10, max_evaluations=2_000_000)
    return mechanism, result, params


def run_analysis(nsteps: int = 1201) -> dict[str, float]:
    mechanism, result, params = simulate(nsteps)
    y = result.q[params["col"]]
    first_impact = int(np.argmax(y <= params["radius"]))
    rebound = float(np.max(y[first_impact:]))
    report = mechanism.validate(result.q[:, 0])
    return {
        "drop_height": params["drop_height"],
        "rebound_height": rebound,
        "restitution_estimate": float(
            np.sqrt((rebound - params["radius"]) / (params["drop_height"] - params["radius"]))
        ),
        "max_penetration": float(params["radius"] - np.min(y)),
        "portable": float(report.portable),
        "max_constraint_residual": mechanism.max_constraint_residual(result),
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Penalty contact (force callback)")
    print(f"  drop / rebound height:     {metrics['drop_height']:.3f} / "
          f"{metrics['rebound_height']:.3f} m")
    print(f"  restitution estimate:      {metrics['restitution_estimate']:.3f}")
    print(f"  max penetration:           {metrics['max_penetration'] * 1e3:.2f} mm")
    print(f"  model portable:            {bool(metrics['portable'])}")
    print(f"  max constraint residual:   {metrics['max_constraint_residual']:.3e}")


def save_plot(path: Path, nsteps: int = 1201) -> None:
    import matplotlib.pyplot as plt

    _, result, params = simulate(nsteps)
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    ax.plot(result.t, result.q[params["col"]], color="#2563eb", label="ball centre")
    ax.axhline(params["radius"], color="0.4", linestyle="--", label="contact height")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("height [m]")
    ax.set_title("Penalty contact via force(fn): non-portable by design")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nsteps", type=int, default=1201)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()
    print_report(run_analysis(nsteps=args.nsteps))
    if args.plot is not None:
        save_plot(args.plot, nsteps=args.nsteps)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
