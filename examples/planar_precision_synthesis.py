"""Four-bar three-precision-point synthesis with Freudenstein's equation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd.planar.synthesis import FourBar, freudenstein_3pt, rocker_angles


def build_precision_points() -> tuple[np.ndarray, np.ndarray]:
    reference = FourBar(ground=1.0, crank=0.3, coupler=0.85, rocker=0.7)
    theta = np.radians([70.0, 130.0, 190.0])
    psi = rocker_angles(reference, theta)
    return theta, psi


def run_analysis() -> dict[str, float]:
    theta, psi = build_precision_points()
    synthesized = freudenstein_3pt(zip(theta, psi), ground=1.0)
    recovered = rocker_angles(synthesized, theta)
    error = np.max(np.abs(recovered - psi))

    return {
        "ground": synthesized.ground,
        "crank": synthesized.crank,
        "coupler": synthesized.coupler,
        "rocker": synthesized.rocker,
        "max_precision_error": float(error),
        "grashof": synthesized.grashof_class(),
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Four-bar precision synthesis")
    print(f"  ground:                 {metrics['ground']:.6f} m")
    print(f"  crank:                  {metrics['crank']:.6f} m")
    print(f"  coupler:                {metrics['coupler']:.6f} m")
    print(f"  rocker:                 {metrics['rocker']:.6f} m")
    print(f"  max precision error:    {metrics['max_precision_error']:.3e} rad")
    print(f"  Grashof class:          {metrics['grashof']}")


def save_plot(path: Path) -> None:
    import matplotlib.pyplot as plt

    theta_pp, psi_pp = build_precision_points()
    synthesized = freudenstein_3pt(zip(theta_pp, psi_pp), ground=1.0)
    theta = np.linspace(theta_pp[0], theta_pp[-1], 181)
    psi = rocker_angles(synthesized, theta)

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(np.degrees(theta), np.degrees(psi), label="synthesized rocker")
    ax.scatter(
        np.degrees(theta_pp),
        np.degrees(psi_pp),
        s=70,
        color="#dc2626",
        zorder=5,
        label="precision points",
    )
    ax.set_title("Freudenstein three-point synthesis")
    ax.set_xlabel("crank angle [deg]")
    ax.set_ylabel("rocker angle [deg]")
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()

    metrics = run_analysis()
    print_report(metrics)
    if args.plot is not None:
        save_plot(args.plot)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
