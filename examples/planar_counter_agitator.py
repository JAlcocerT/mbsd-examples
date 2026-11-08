"""Counter-oscillating agitator: crank, rack, pinion and a reverser.

A crank drives a rack through a connecting rod; the rack turns a pinion on the
outer paddle set, and a reverser (idlers on the frame) turns the inner set the
opposite way. The rack and the reverser are portable ``rack()`` / ``gear()``
meshes, so the gear relations are solved and their tooth loads come from the
multipliers. ``joint_loads()`` then shows why the sets swing opposite: their
inertia torques cancel on the frame. A same-direction variant (one sign) and
an unmatched variant (inner set at half inertia) quantify the effect.

Note the rack phase: the in-line slider-crank's true mid-stroke is at
``x = L`` (rod length), not at crank 90 deg, because of rod obliquity.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.planar import PlanarMechanism

CRANK, ROD, PITCH_RADIUS = 0.05, 0.20, 0.04
AXLE = np.array([0.20, -0.04])  # pinion axle; the rack's pitch line is at y = 0


def build_agitator(direction: str = "opposite", inner_inertia: float = 0.06, speed_hz: float = 1.0):
    """Return the mechanism and an assembled ``q0`` (crank at 0 deg)."""
    if direction not in {"opposite", "same"}:
        raise ValueError("direction must be 'opposite' or 'same'")
    m = Mechanism.planar(gravity=(0.0, 0.0))  # top view
    frame = m.ground("frame")
    crank = m.body("crank", mass=0.5, inertia=2e-4, center_of_mass=(CRANK / 2, 0.0))
    rod = m.body("rod", mass=0.2, inertia=8e-4, center_of_mass=(ROD / 2, 0.0))
    rack = m.body("rack", mass=0.6, inertia=1e-3)
    outer = m.body("outer_paddles", mass=2.0, inertia=0.06)
    inner = m.body("inner_paddles", mass=2.0, inertia=inner_inertia)
    m.pin(frame, crank, name="crank_bearing")
    m.pin(crank, rod, point_a=(CRANK, 0.0), name="crank_pin")
    m.pin(rod, rack, point_a=(ROD, 0.0), name="rack_pin")
    m.slider(frame, rack, axis=(1.0, 0.0), name="rack_guide")
    m.pin(frame, outer, point_a=AXLE, name="sleeve_bearing")
    m.pin(frame, inner, point_a=AXLE, name="shaft_bearing")
    # Pinion zero at the true mid-stroke x = ROD.
    m.rack(outer, rack, PITCH_RADIUS, offset=ROD, name="rack_mesh")
    m.gear(outer, inner, -1.0 if direction == "opposite" else 1.0, name="reverser")
    m.motor(crank, omega=2.0 * np.pi * speed_hz, name="motor")

    x0 = CRANK + ROD
    theta_outer = (x0 - ROD) / PITCH_RADIUS
    theta_inner = -theta_outer if direction == "opposite" else theta_outer
    q0 = np.array([
        0, 0, 0,
        0, 0, 0,
        CRANK, 0, 0,
        x0, 0, 0,
        *AXLE, theta_outer,
        *AXLE, theta_inner,
    ], dtype=float)
    return m, q0


def _run(direction: str, inner_inertia: float, t: np.ndarray) -> dict:
    mechanism, q0 = build_agitator(direction, inner_inertia)
    report = mechanism.validate(q0, t=t)
    result = mechanism.inverse_dynamics(t, q0=q0)
    loads = mechanism.joint_loads(result)
    return {
        "mechanism": mechanism,
        "q0": q0,
        "result": result,
        "report": report,
        "frame_torque": loads.frame["moment"],
        "motor_torque": loads.drives["motor"]["effort"],
        "tooth_force": loads.meshes["rack_mesh"]["effort_on_b"],
        "inner_torque": loads.meshes["reverser"]["effort_on_b"],
        "check_passed": mechanism.check(result).passed,
    }


def run_analysis(nsteps: int = 121, duration: float = 2.0) -> dict:
    t = np.linspace(0.0, duration, nsteps)
    opposite = _run("opposite", 0.06, t)
    same = _run("same", 0.06, t)
    unmatched = _run("opposite", 0.03, t)
    result = opposite["result"]
    swing = np.degrees(result.q[14])
    with tempfile.TemporaryDirectory() as tmp:
        replay = PlanarMechanism.from_json(opposite["mechanism"].to_json(Path(tmp) / "agitator.json"))
    replayed = replay.inverse_dynamics(t, q0=opposite["q0"])
    return {
        "t": t,
        "swing_deg": swing,
        "frame_torque_opposite": opposite["frame_torque"],
        "frame_torque_same": same["frame_torque"],
        "frame_torque_unmatched": unmatched["frame_torque"],
        "motor_torque": opposite["motor_torque"],
        "tooth_force": opposite["tooth_force"],
        "inner_torque": opposite["inner_torque"],
        "validation_ok": opposite["report"].ok,
        "portable": opposite["report"].portable,
        "check_passed": all(run["check_passed"] for run in (opposite, same, unmatched)),
        "replay_identical": bool(np.array_equal(replayed.multipliers, result.multipliers)),
        "counter_rotation_error": float(np.max(np.abs(result.q[14] + result.q[17]))),
    }


def print_report(metrics: dict) -> None:
    peak = {k: float(np.max(np.abs(metrics[f"frame_torque_{k}"]))) for k in ("opposite", "same", "unmatched")}
    print("Counter-oscillating agitator: crank, rack, pinion and reverser")
    print(f"  validate ok / portable:      {metrics['validation_ok']} / {metrics['portable']}")
    print(f"  paddle swing:                {metrics['swing_deg'].min():.1f} .. {metrics['swing_deg'].max():.1f} deg")
    print(f"  counter-rotation error:      {metrics['counter_rotation_error']:.1e} rad")
    print(f"  peak rack tooth force:       {np.abs(metrics['tooth_force']).max():.1f} N")
    print(f"  peak motor torque:           {np.abs(metrics['motor_torque']).max():.3f} N*m")
    print(f"  peak frame torque opposite:  {peak['opposite']:.4f} N*m")
    print(f"  peak frame torque same dir:  {peak['same']:.4f} N*m")
    print(f"  peak frame torque unmatched: {peak['unmatched']:.4f} N*m")
    print(f"  check / JSON replay:         {metrics['check_passed']} / {metrics['replay_identical']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nsteps", type=int, default=121)
    args = parser.parse_args()
    print_report(run_analysis(nsteps=args.nsteps))


if __name__ == "__main__":
    main()
