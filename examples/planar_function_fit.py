"""Four-bar rocker function fitting preview."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd.planar.synthesis import FourBar, affine_fit, rocker_angles


def target_function(x: np.ndarray) -> np.ndarray:
    return np.log(x)


def run_analysis(nsteps: int = 121) -> dict[str, float]:
    four_bar = FourBar(ground=1.0, crank=0.3, coupler=0.85, rocker=0.7)
    theta = np.linspace(np.radians(70.0), np.radians(190.0), nsteps)
    x_domain = 1.0 + (theta - theta[0]) / (theta[-1] - theta[0])
    target = target_function(x_domain)
    rocker = rocker_angles(four_bar, theta)
    fit = affine_fit(rocker, target)
    residual = fit.transform(rocker) - target

    return {
        "ground": four_bar.ground,
        "crank": four_bar.crank,
        "coupler": four_bar.coupler,
        "rocker": four_bar.rocker,
        "fit_scale": fit.scale,
        "fit_offset": fit.offset,
        "rms_error": fit.rms_error,
        "max_abs_error": float(np.max(np.abs(residual))),
    }


def print_report(metrics: dict[str, float]) -> None:
    print("Four-bar function fit")
    print(f"  links:              {metrics['ground']:.3f}, {metrics['crank']:.3f}, "
          f"{metrics['coupler']:.3f}, {metrics['rocker']:.3f} m")
    print(f"  affine scale:       {metrics['fit_scale']:.6f}")
    print(f"  affine offset:      {metrics['fit_offset']:.6f}")
    print(f"  RMS error:          {metrics['rms_error']:.3e}")
    print(f"  max abs error:      {metrics['max_abs_error']:.3e}")


def save_plot(path: Path, nsteps: int = 121) -> None:
    import matplotlib.pyplot as plt

    four_bar = FourBar(ground=1.0, crank=0.3, coupler=0.85, rocker=0.7)
    theta = np.linspace(np.radians(70.0), np.radians(190.0), nsteps)
    x_domain = 1.0 + (theta - theta[0]) / (theta[-1] - theta[0])
    target = target_function(x_domain)
    rocker = rocker_angles(four_bar, theta)
    fit = affine_fit(rocker, target)
    fitted = fit.transform(rocker)
    residual = fitted - target

    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.2), sharex=True)
    axes[0].plot(x_domain, target, color="black", label="target log(x)")
    axes[0].plot(x_domain, fitted, color="#0ea5e9", label="affine-fitted rocker")
    axes[0].set_ylabel("output")
    axes[0].set_title("Four-bar rocker function fit")
    axes[0].grid(True, alpha=0.35)
    axes[0].legend()
    axes[1].plot(x_domain, residual, color="#dc2626")
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_xlabel("input domain")
    axes[1].set_ylabel("residual")
    axes[1].grid(True, alpha=0.35)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nsteps", type=int, default=121)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()

    metrics = run_analysis(nsteps=args.nsteps)
    print_report(metrics)
    if args.plot is not None:
        save_plot(args.plot, nsteps=args.nsteps)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
