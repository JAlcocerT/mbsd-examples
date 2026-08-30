"""Undamped mass-spring energy check using MBSD constrained dynamics."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism, Spring


def build_energy_model() -> tuple[object, np.ndarray, np.ndarray, Spring]:
    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    mass = mechanism.body("mass", mass=1.0, inertia=0.01)
    mechanism.slider(ground, mass, axis=(1.0, 0.0))

    spring = Spring(
        i=int(ground),
        j=int(mass),
        k=10.0,
        c=0.0,
        l0=1.0,
        ri=np.array([0.0, 0.0]),
        rj=np.array([0.0, 0.0]),
    )

    q0 = np.zeros(mechanism.ncoord)
    q0[3] = 1.5
    v0 = np.zeros(mechanism.ncoord)
    return mechanism, q0, v0, spring


def run_analysis(nsteps: int = 301) -> dict[str, float]:
    mechanism, q0, v0, spring = build_energy_model()
    t = np.linspace(0.0, 1.5, nsteps)
    result = mechanism.simulate(
        t,
        q0=q0,
        v0=v0,
        springs=[spring],
        allow_underconstrained=True,
    )
    mechanism.assert_constraints_satisfied(result, tol=1e-7)

    x = result.q[3, :]
    vx = result.v[3, :]
    energy = 0.5 * vx**2 + 0.5 * spring.k * (x - spring.l0) ** 2
    relative_drift = np.ptp(energy) / energy[0]

    return {
        "coordinates": float(mechanism.ncoord),
        "constraints": float(mechanism.nrestr),
        "max_constraint_residual": mechanism.max_constraint_residual(result),
        "energy_initial": float(energy[0]),
        "energy_min": float(np.min(energy)),
        "energy_max": float(np.max(energy)),
        "relative_energy_drift": float(relative_drift),
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Undamped mass-spring energy")
    print(f"  coordinates / constraints: {metrics['coordinates']:.0f} / {metrics['constraints']:.0f}")
    print(f"  max constraint residual:   {metrics['max_constraint_residual']:.3e}")
    print(f"  initial energy:            {metrics['energy_initial']:.6f} J")
    print(f"  min/max energy:            {metrics['energy_min']:.6f} / {metrics['energy_max']:.6f} J")
    print(f"  relative energy drift:     {metrics['relative_energy_drift']:.3e}")


def save_plot(path: Path, nsteps: int = 301) -> None:
    import matplotlib.pyplot as plt

    mechanism, q0, v0, spring = build_energy_model()
    t = np.linspace(0.0, 1.5, nsteps)
    result = mechanism.simulate(
        t,
        q0=q0,
        v0=v0,
        springs=[spring],
        allow_underconstrained=True,
    )
    x = result.q[3, :]
    vx = result.v[3, :]
    energy = 0.5 * vx**2 + 0.5 * spring.k * (x - spring.l0) ** 2

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True)
    axes[0].plot(t, x)
    axes[0].set_title("Undamped mass-spring")
    axes[0].set_ylabel("x [m]")
    axes[0].grid(True, alpha=0.35)
    axes[1].plot(t, energy)
    axes[1].set_xlabel("time [s]")
    axes[1].set_ylabel("energy [J]")
    axes[1].grid(True, alpha=0.35)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nsteps", type=int, default=301)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()

    metrics = run_analysis(nsteps=args.nsteps)
    print_report(metrics)
    if args.plot is not None:
        save_plot(args.plot, nsteps=args.nsteps)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
