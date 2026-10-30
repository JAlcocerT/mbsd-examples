"""Slider-crank joint reactions, drive torque, and shaking force for one revolution."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from mbsd import Mechanism


def build_engine(omega: float = 150.0, piston_force: float = 400.0):
    crank_radius, rod_length = 0.04, 0.14
    mechanism = Mechanism.planar(gravity=(0.0, -9.81))
    ground = mechanism.ground()
    crank = mechanism.body("crank", mass=0.6, inertia=2e-4)
    rod = mechanism.body("rod", mass=0.5, inertia=1.2e-3)
    piston = mechanism.body("piston", mass=0.35, inertia=1e-4)

    mechanism.pin(ground, crank, point_b=(-crank_radius / 2, 0.0), name="main_bearing")
    mechanism.pin(
        crank,
        rod,
        point_a=(crank_radius / 2, 0.0),
        point_b=(-rod_length / 2, 0.0),
        name="crank_pin",
    )
    mechanism.pin(rod, piston, point_a=(rod_length / 2, 0.0), name="wrist_pin")
    mechanism.slider(ground, piston, axis=(1.0, 0.0), name="bore")
    mechanism.motor(crank, omega=omega, name="crankshaft")
    mechanism.constant_force(piston, (-piston_force, 0.0), name="piston_load")

    q0 = np.array(
        [0, 0, 0, crank_radius / 2, 0, 0, crank_radius + rod_length / 2, 0, 0,
         crank_radius + rod_length, 0, 0],
        dtype=float,
    )
    params = {"crank_radius": crank_radius, "rod_length": rod_length, "omega": omega}
    return mechanism, q0, params


def run_analysis(nsteps: int = 361, output_dir: Path | None = None) -> dict[str, float]:
    mechanism, q0, params = build_engine()
    t = np.linspace(0.0, 2.0 * np.pi / params["omega"], nsteps)
    report = mechanism.validate(q0, t=t)
    result = mechanism.inverse_dynamics(t, q0=q0)
    verdict = mechanism.check(result)
    loads = mechanism.joint_loads(result)

    torque = loads.drives["crankshaft"]["effort"]
    power = loads.drives["crankshaft"]["power"]
    metrics = {
        "validation_ok": float(report.ok),
        "check_passed": float(verdict.passed),
        "peak_main_bearing_force": float(
            np.linalg.norm(loads.joints["main_bearing"]["force_on_j"], axis=0).max()
        ),
        "peak_crank_pin_force": float(
            np.linalg.norm(loads.joints["crank_pin"]["force_on_j"], axis=0).max()
        ),
        "peak_wrist_pin_force": float(
            np.linalg.norm(loads.joints["wrist_pin"]["force_on_j"], axis=0).max()
        ),
        "peak_torque": float(np.abs(torque).max()),
        "rms_torque": float(np.sqrt(np.mean(torque**2))),
        "mean_power": float(np.mean(power[:-1])),
        "peak_shaking_x": float(np.abs(loads.frame["force"][0]).max()),
        "peak_shaking_y": float(np.abs(loads.frame["force"][1]).max()),
        "action_reaction_residual": loads.max_action_reaction_residual,
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        mechanism.to_json(output_dir / "slider-crank-mechanism.json")
        mechanism.joint_loads_to_json(result, output_dir / "slider-crank-joint-loads.json")
    return metrics


def print_report(metrics: dict[str, float]) -> None:
    print("Slider-crank joint loads (one revolution)")
    print(f"  validate / check:          {bool(metrics['validation_ok'])} / "
          f"{bool(metrics['check_passed'])}")
    print(f"  peak main bearing force:   {metrics['peak_main_bearing_force']:.2f} N")
    print(f"  peak crank pin force:      {metrics['peak_crank_pin_force']:.2f} N")
    print(f"  peak wrist pin force:      {metrics['peak_wrist_pin_force']:.2f} N")
    print(f"  peak / RMS drive torque:   {metrics['peak_torque']:.3f} / "
          f"{metrics['rms_torque']:.3f} N*m")
    print(f"  mean drive power:          {metrics['mean_power']:.3f} W")
    print(f"  peak shaking force x / y:  {metrics['peak_shaking_x']:.2f} / "
          f"{metrics['peak_shaking_y']:.2f} N")
    print(f"  action-reaction residual:  {metrics['action_reaction_residual']:.3e}")


def save_plot(path: Path, nsteps: int = 361) -> None:
    import matplotlib.pyplot as plt

    mechanism, q0, params = build_engine()
    t = np.linspace(0.0, 2.0 * np.pi / params["omega"], nsteps)
    loads = mechanism.joint_loads(mechanism.inverse_dynamics(t, q0=q0))
    angle = np.degrees(params["omega"] * t)

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 7.5), sharex=True)
    for name in ("main_bearing", "crank_pin", "wrist_pin"):
        axes[0].plot(angle, np.linalg.norm(loads.joints[name]["force_on_j"], axis=0), label=name)
    axes[0].set_ylabel("|pin force| [N]")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].plot(angle, loads.drives["crankshaft"]["effort"], color="#dc2626")
    axes[1].set_ylabel("drive torque [N*m]")
    axes[2].plot(angle, loads.frame["force"][0], label="x")
    axes[2].plot(angle, loads.frame["force"][1], label="y")
    axes[2].set_ylabel("shaking force [N]")
    axes[2].set_xlabel("crank angle [deg]")
    axes[2].legend(loc="upper right", fontsize=8)
    for ax in axes:
        ax.grid(True, alpha=0.35)
    fig.suptitle("Slider-crank joint loads (inverse dynamics)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nsteps", type=int, default=361)
    parser.add_argument("--export", type=Path, default=None)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()

    print_report(run_analysis(nsteps=args.nsteps, output_dir=args.export))
    if args.plot is not None:
        save_plot(args.plot, nsteps=args.nsteps)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
