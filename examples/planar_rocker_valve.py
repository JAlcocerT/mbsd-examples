"""Rocker arm on a valve stem: a point-on-line contact and its separation check.

The rocker tip rides on the flat top of the valve stem (``point_on_line``).
The bilateral joint reports the contact force a real, unilateral contact would
need; a negative value means the valve would float (separate). Simulating the
separation itself needs a unilateral contact model, which is outside core.
"""

from __future__ import annotations

import numpy as np

from mbsd import Mechanism, Tabulated


def build_valvetrain(spring_preload: float = 250.0, speed: float = 1.0):
    m = Mechanism.planar(gravity=(0.0, -9.81))
    head = m.ground("cylinder_head")
    rocker = m.body("rocker", mass=0.15, inertia=8e-5)
    valve = m.body("valve", mass=0.05, inertia=1e-6)
    m.pin(head, rocker, point_b=(-0.02, 0.0), name="rocker_shaft")
    m.slider(head, valve, axis=(0.0, 1.0), point_rail=(0.04, 0.0), name="valve_guide")
    m.point_on_line(rocker, valve, point_a=(0.02, 0.0), direction_b=(1.0, 0.0), name="tip")
    # Lift profile of the rocker angle (rad): a smooth bump, scaled by speed.
    duration = 0.02 / speed
    times = np.linspace(0.0, duration, 21)
    lift = -0.12 * np.sin(np.pi * times / duration) ** 2
    m.coordinate_drive(rocker, "theta", law=Tabulated(tuple(times), tuple(lift)), name="cam")
    m.constant_force(valve, (0.0, spring_preload), name="valve_spring")
    q0 = np.array([0, 0, 0, 0.02, 0, 0, 0.04, 0, 0], dtype=float)
    return m, q0, duration


def run_analysis(speed: float = 1.0, nsteps: int = 81) -> dict:
    mechanism, q0, duration = build_valvetrain(speed=speed)
    t = np.linspace(0.0, duration, nsteps)
    report = mechanism.validate(q0, t=t)
    result = mechanism.inverse_dynamics(t, q0=q0)
    contact = -mechanism.joint_loads(result).joints["tip"]["force_on_j"][1]  # push-down on valve
    return {
        "t": t,
        "contact_force": contact,
        "validation_ok": report.ok,
        "portable": report.portable,
        "check_passed": mechanism.check(result).passed,
        "min_contact_force": float(contact.min()),
        "floats": bool(contact.min() < 0.0),
    }


def main() -> None:
    print("Rocker on valve stem (point_on_line)")
    for speed in (1.0, 4.0, 6.0):
        metrics = run_analysis(speed=speed)
        print(f"  speed x{speed:.0f}: min tip force {metrics['min_contact_force']:8.1f} N  "
              f"valve floats: {metrics['floats']}  check: {metrics['check_passed']}")


if __name__ == "__main__":
    main()
