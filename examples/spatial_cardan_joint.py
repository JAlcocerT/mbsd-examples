"""Single and double Cardan (U-joint) shafts checked against the closed form.

A shaft on two bearings is redundant when both bearings are revolute joints:
the second bearing re-constrains a point that the first already fixes. The
second bearing is modelled with ``parallel_axes`` instead, which keeps only the
axis direction. ``validate()`` names the redundant joint if you do not.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

from mbsd import ConstantSpeed, Mechanism
from mbsd.spatial import Pose3D, Quaternion

ROT = Quaternion.from_axis_angle
Z_TO_X = ROT((0.0, 1.0, 0.0), math.pi / 2)
Z_TO_Y = ROT((1.0, 0.0, 0.0), -math.pi / 2)


def build_single(beta: float, omega: float, *, redundant: bool = False):
    """Input shaft along x, output shaft at ``beta`` in the xy plane."""
    m = Mechanism.spatial()
    ground = m.ground("frame")
    shaft_in = m.body("shaft_in", mass=5.0, inertia=(0.04, 0.02, 0.02))
    cross = m.body("cross", mass=0.3, inertia=(0.002, 0.002, 0.002))
    shaft_out = m.body("shaft_out", mass=2.0, inertia=(0.02, 0.02, 0.02))
    z_to_out = ROT((0.0, 0.0, 1.0), beta) * Z_TO_X
    bearing = m.revolute(ground, shaft_in, frame_i=Pose3D(rotation=Z_TO_X),
                         frame_j=Pose3D(rotation=Z_TO_X), name="input_bearing")
    m.revolute(shaft_in, cross, frame_i=Pose3D(rotation=Z_TO_Y),
               frame_j=Pose3D(rotation=Z_TO_Y), name="yoke_in")
    m.revolute(cross, shaft_out, name="yoke_out")
    second_bearing = m.revolute if redundant else m.parallel_axes
    second_bearing(ground, shaft_out, frame_i=Pose3D(rotation=z_to_out),
                   frame_j=Pose3D(rotation=z_to_out), name="output_bearing")
    m.revolute_drive(bearing, law=ConstantSpeed(rate=omega), name="motor")
    return m


def build_double(beta: float, omega: float, length: float = 0.3):
    """Z-arrangement: input and output parallel, in-phase yokes, equal angles."""
    direction = np.array([math.cos(beta), math.sin(beta), 0.0])
    z_to_mid = ROT((0.0, 0.0, 1.0), beta) * Z_TO_X
    m = Mechanism.spatial()
    ground = m.ground("frame")
    shaft_in = m.body("shaft_in", mass=2.0, inertia=(0.02, 0.01, 0.01))
    cross_1 = m.body("cross_1", mass=0.2, inertia=(0.001, 0.001, 0.001))
    mid = m.body("intermediate", mass=1.0, inertia=(0.01, 0.01, 0.01))
    cross_2 = m.body("cross_2", mass=0.2, inertia=(0.001, 0.001, 0.001),
                     pose=Pose3D(translation=length * direction))
    shaft_out = m.body("shaft_out", mass=2.0, inertia=(0.02, 0.01, 0.01),
                       pose=Pose3D(translation=length * direction))
    bearing = m.revolute(ground, shaft_in, frame_i=Pose3D(rotation=Z_TO_X),
                         frame_j=Pose3D(rotation=Z_TO_X), name="input_bearing")
    m.revolute(shaft_in, cross_1, frame_i=Pose3D(rotation=Z_TO_Y),
               frame_j=Pose3D(rotation=Z_TO_Y), name="yoke_1a")
    m.revolute(cross_1, mid, name="yoke_1b")
    m.parallel_axes(ground, mid, frame_i=Pose3D(rotation=z_to_mid),
                    frame_j=Pose3D(rotation=z_to_mid), name="intermediate_axis")
    m.revolute(mid, cross_2, frame_i=Pose3D(translation=length * direction), name="yoke_2a")
    m.revolute(cross_2, shaft_out, frame_i=Pose3D(rotation=Z_TO_Y),
               frame_j=Pose3D(rotation=Z_TO_Y), name="yoke_2b")
    m.parallel_axes(ground, shaft_out, frame_i=Pose3D(rotation=Z_TO_X),
                    frame_j=Pose3D(rotation=Z_TO_X), name="output_bearing")
    m.revolute_drive(bearing, law=ConstantSpeed(rate=omega), name="motor")
    return m, direction


def axial_speed(result, body: int, axis) -> np.ndarray:
    return np.array([
        step[body].rotation.to_rotation_matrix() @ result.angular_velocity_body[k, body]
        for k, step in enumerate(result.poses)
    ]) @ np.asarray(axis)


def closed_form_ratio(beta: float, theta: np.ndarray) -> np.ndarray:
    return math.cos(beta) / (1.0 - math.sin(beta) ** 2 * np.cos(theta) ** 2)


def run_analysis(nsteps: int = 33, beta_deg: float = 30.0, omega: float = 4.0 * math.pi) -> dict:
    beta = math.radians(beta_deg)
    t = np.linspace(0.0, math.pi / omega, nsteps)  # half an input turn: two speed cycles

    redundant = build_single(beta, omega, redundant=True).validate()
    single = build_single(beta, omega)
    report = single.validate(t)
    result = single.simulate(t)
    ratio = axial_speed(result, 3, (math.cos(beta), math.sin(beta), 0.0)) / omega
    torque = single.drive_efforts(result)["motor"]["effort"]

    double, direction = build_double(beta, omega)
    double_result = double.simulate(t)
    double_out = axial_speed(double_result, 5, (1.0, 0.0, 0.0)) / omega
    intermediate = axial_speed(double_result, 3, direction) / omega

    return {
        "t": t,
        "input_angle": omega * t,
        "single_ratio": ratio,
        "closed_form_ratio": closed_form_ratio(beta, omega * t),
        "double_ratio": double_out,
        "intermediate_ratio": intermediate,
        "validation_ok": report.ok,
        "degrees_of_freedom": report.degrees_of_freedom,
        "redundant_issue": next(i for i in redundant.issues if i.code == "redundant_constraints").message,
        "max_ratio_error": float(np.max(np.abs(ratio - closed_form_ratio(beta, omega * t)))),
        "double_output_error": float(np.max(np.abs(double_out - 1.0))),
        "intermediate_ratio_range": float(np.ptp(intermediate)),
        "peak_input_torque": float(np.max(np.abs(torque))),
        "check_passed": bool(single.check(result).passed and double.check(double_result).passed),
    }


def print_report(metrics: dict) -> None:
    print("Cardan shafts (beta = 30 deg, 2 rev/s input)")
    print(f"  validate ok / DOF:          {metrics['validation_ok']} / {metrics['degrees_of_freedom']}")
    print(f"  two revolute bearings:      {metrics['redundant_issue'][:72]}...")
    print(f"  single: max |ratio-closed|: {metrics['max_ratio_error']:.3e}")
    print(f"  single: ratio range:        {metrics['single_ratio'].min():.4f} .. {metrics['single_ratio'].max():.4f}")
    print(f"  double: max |out/in - 1|:   {metrics['double_output_error']:.3e}")
    print(f"  double: intermediate swing: {metrics['intermediate_ratio_range']:.4f}")
    print(f"  peak input torque:          {metrics['peak_input_torque']:.4f} N*m")
    print(f"  check passed:               {metrics['check_passed']}")


def save_plot(path: Path, nsteps: int = 61) -> None:
    import matplotlib.pyplot as plt

    metrics = run_analysis(nsteps=nsteps)
    angle = np.degrees(metrics["input_angle"])
    fig, ax = plt.subplots(figsize=(8.0, 4.5))
    ax.plot(angle, metrics["closed_form_ratio"], color="#94a3b8", linewidth=4, label="closed form")
    ax.plot(angle, metrics["single_ratio"], "--", color="#dc2626", label="single Cardan (MBSD)")
    ax.plot(angle, metrics["intermediate_ratio"], color="#f59e0b", label="double: intermediate shaft")
    ax.plot(angle, metrics["double_ratio"], color="#16a34a", label="double: output shaft")
    ax.set_xlabel("input angle [deg]")
    ax.set_ylabel("output / input speed")
    ax.set_title("Cardan joint speed ratio, beta = 30 deg")
    ax.grid(True, alpha=0.35)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nsteps", type=int, default=33)
    parser.add_argument("--plot", type=Path, default=None)
    args = parser.parse_args()
    print_report(run_analysis(nsteps=args.nsteps))
    if args.plot is not None:
        save_plot(args.plot)
        print(f"  plot: {args.plot}")


if __name__ == "__main__":
    main()
