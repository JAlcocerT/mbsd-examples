"""Excavator boom and stick driven by two hydraulic cylinders.

Each cylinder is a portable ``distance_drive`` between its two pin points, so
the model round-trips through JSON. ``joint_loads()`` reports the cylinder
forces (positive = pushing), the pivot loads, and the load on the chassis,
including both cylinder base reactions. The stick carries a bucket, modelled as
an offset center of mass.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np

from mbsd import Mechanism, Polynomial
from mbsd.planar import PlanarMechanism, analysis


def build_excavator(boom_rate: float = 0.04, stick_rate: float = 0.03):
    m = Mechanism.planar(gravity=(0.0, -9.81))
    chassis = m.ground("chassis")
    boom = m.body("boom", mass=420.0, inertia=180.0)                     # 2.4 m, reference at COM
    stick = m.body("stick", mass=260.0, inertia=60.0, center_of_mass=(1.1, -0.1))
    m.pin(chassis, boom, point_b=(-1.2, 0.0), name="boom_pivot")
    m.pin(boom, stick, point_a=(1.2, 0.0), name="stick_pivot")

    boom_base, boom_eye = np.array([0.6, -0.8]), np.array([-0.4, -0.15])
    stick_base, stick_eye = np.array([0.2, 0.25]), np.array([-0.35, 0.2])
    q0 = np.array([0, 0, 0, 1.2, 0, 0, 2.4, 0, 0], dtype=float)
    boom_len = float(np.linalg.norm(analysis.point_position(q0, boom, boom_eye) - boom_base))
    stick_len = float(np.linalg.norm(
        analysis.point_position(q0, stick, stick_eye) - analysis.point_position(q0, boom, stick_base)
    ))
    m.distance_drive(chassis, boom, law=Polynomial((boom_len, boom_rate)),
                     point_a=boom_base, point_b=boom_eye, name="boom_cylinder")
    m.distance_drive(boom, stick, law=Polynomial((stick_len, stick_rate)),
                     point_a=stick_base, point_b=stick_eye, name="stick_cylinder")
    return m, q0


def run_analysis(nsteps: int = 41, duration: float = 4.0) -> dict:
    mechanism, q0 = build_excavator()
    t = np.linspace(0.0, duration, nsteps)
    report = mechanism.validate(q0, t=t)
    result = mechanism.inverse_dynamics(t, q0=q0)
    loads = mechanism.joint_loads(result)
    with tempfile.TemporaryDirectory() as tmp:
        replay = PlanarMechanism.from_json(mechanism.to_json(Path(tmp) / "excavator.json"))
    replayed = replay.inverse_dynamics(t, q0=q0)
    boom_force = loads.drives["boom_cylinder"]["effort"]
    stick_force = loads.drives["stick_cylinder"]["effort"]
    return {
        "t": t,
        "boom_force": boom_force,
        "stick_force": stick_force,
        "boom_power": loads.drives["boom_cylinder"]["power"],
        "chassis_force": loads.frame["force"],
        "boom_pivot_force": np.linalg.norm(loads.joints["boom_pivot"]["force_on_j"], axis=0),
        "validation_ok": report.ok,
        "portable": report.portable,
        "check_passed": mechanism.check(result).passed,
        "replay_identical": bool(np.array_equal(replayed.multipliers, result.multipliers)),
        "boom_angle_change_deg": float(np.degrees(result.q[5, -1] - result.q[5, 0])),
        "total_weight": float(9.81 * (420.0 + 260.0)),
    }


def print_report(metrics: dict) -> None:
    print("Excavator boom and stick with two hydraulic cylinders")
    print(f"  validate ok / portable:    {metrics['validation_ok']} / {metrics['portable']}")
    print(f"  boom rotation:             {metrics['boom_angle_change_deg']:.2f} deg")
    print(f"  boom cylinder force:       {metrics['boom_force'].min():.0f} .. {metrics['boom_force'].max():.0f} N")
    print(f"  stick cylinder force:      {metrics['stick_force'].min():.0f} .. {metrics['stick_force'].max():.0f} N")
    print(f"  peak boom cylinder power:  {np.abs(metrics['boom_power']).max():.0f} W")
    print(f"  peak boom pivot load:      {metrics['boom_pivot_force'].max():.0f} N")
    print(f"  chassis vertical load:     {metrics['chassis_force'][1].mean():.0f} N "
          f"(weight {metrics['total_weight']:.0f} N)")
    print(f"  check / JSON replay:       {metrics['check_passed']} / {metrics['replay_identical']}")


def save_plot(path: Path, nsteps: int = 81) -> None:
    import matplotlib.pyplot as plt

    metrics = run_analysis(nsteps=nsteps)
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.0), sharex=True)
    axes[0].plot(metrics["t"], metrics["boom_force"] / 1e3, label="boom cylinder")
    axes[0].plot(metrics["t"], metrics["stick_force"] / 1e3, label="stick cylinder")
    axes[0].set_ylabel("cylinder force [kN] (+ push)")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].plot(metrics["t"], metrics["boom_pivot_force"] / 1e3, color="#7c3aed", label="|boom pivot|")
    axes[1].plot(metrics["t"], -metrics["chassis_force"][1] / 1e3, color="#0f766e", label="chassis vertical")
    axes[1].set_ylabel("load [kN]")
    axes[1].set_xlabel("time [s]")
    axes[1].legend(loc="upper right", fontsize=8)
    for ax in axes:
        ax.grid(True, alpha=0.35)
    fig.suptitle("Excavator cylinders as portable distance drives")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nsteps", type=int, default=41)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()
    print_report(run_analysis(nsteps=args.nsteps))
    if args.plot is not None:
        save_plot(args.plot)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
