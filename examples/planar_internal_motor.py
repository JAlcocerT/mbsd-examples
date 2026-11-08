"""Internal motor: a reaction wheel on a free-spinning platform.

A platform turns freely on a frictionless pivot and carries a motor that spins
a wheel. Driven *relative* to the platform (``relative_to=``), the motor's
reaction torque stays inside the system: the total angular momentum stays
zero, the platform counter-rotates, and the frame feels no torque. The same
motor driven as an *absolute* angle reacts against ground, which a real
motor mounted on the platform cannot do.

Forward dynamics returns the solved accelerations (``result.a``), so the power
balance ``motor power = dKE/dt`` closes exactly, with no finite differencing.
"""

from __future__ import annotations

import argparse

import numpy as np

from mbsd import Mechanism, Polynomial

PLATFORM_INERTIA, WHEEL_INERTIA = 0.8, 0.05
SPIN_UP = Polynomial((0.0, 0.0, 6.0))  # relative angle 6 t^2 rad


def build(relative: bool = True):
    m = Mechanism.planar(gravity=(0.0, 0.0))
    frame = m.ground("frame")
    platform = m.body("platform", mass=3.0, inertia=PLATFORM_INERTIA)
    wheel = m.body("wheel", mass=0.6, inertia=WHEEL_INERTIA)
    m.pin(frame, platform, name="pivot")
    m.pin(platform, wheel, name="motor_shaft")
    if relative:
        m.coordinate_drive(wheel, "theta", law=SPIN_UP, relative_to=platform, name="motor")
    else:
        m.coordinate_drive(wheel, "theta", law=SPIN_UP, name="motor")
    return m, np.zeros(9)


def _kinetic_energy_rate(result) -> np.ndarray:
    v, a = result.v, result.a
    return PLATFORM_INERTIA * v[5] * a[5] + WHEEL_INERTIA * v[8] * a[8]


def run_analysis(nsteps: int = 101, duration: float = 2.0) -> dict:
    t = np.linspace(0.0, duration, nsteps)
    metrics = {"t": t}
    for label, relative in (("relative", True), ("absolute", False)):
        mechanism, q0 = build(relative)
        result = mechanism.simulate(
            t, q0, v0=np.zeros(9), allow_underconstrained=True, rtol=1e-11, atol=1e-13
        )
        loads = mechanism.joint_loads(result)
        motor = loads.drives["motor"]
        momentum = PLATFORM_INERTIA * result.v[5] + WHEEL_INERTIA * result.v[8]
        metrics[label] = {
            "platform_rate": result.v[5],
            "wheel_rate": result.v[8],
            "momentum": momentum,
            "frame_torque": loads.frame["moment"],
            "motor_torque": motor["effort"],
            "power_balance": float(np.max(np.abs(motor["power"] - _kinetic_energy_rate(result)))),
            "check_passed": mechanism.check(result).passed,
        }
    relative = metrics["relative"]
    ratio = WHEEL_INERTIA / (PLATFORM_INERTIA + WHEEL_INERTIA)
    metrics["platform_rate_error"] = float(
        np.max(np.abs(relative["platform_rate"] + ratio * 12.0 * t))
    )
    return metrics


def print_report(metrics: dict) -> None:
    rel, ab = metrics["relative"], metrics["absolute"]
    print("Internal motor: reaction wheel on a free platform")
    print(f"  relative drive: |H| max      {np.abs(rel['momentum']).max():.1e} N*m*s")
    print(f"                  frame torque {np.abs(rel['frame_torque']).max():.1e} N*m")
    print(f"                  platform     {rel['platform_rate'][-1]:.3f} rad/s "
          f"(closed form error {metrics['platform_rate_error']:.1e})")
    print(f"                  power balance {rel['power_balance']:.1e} W (solved accelerations)")
    print(f"  absolute drive: |H| max      {np.abs(ab['momentum']).max():.3f} N*m*s")
    print(f"                  frame torque {np.abs(ab['frame_torque']).max():.3f} N*m")
    print(f"  check passed:   {rel['check_passed']} / {ab['check_passed']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nsteps", type=int, default=101)
    args = parser.parse_args()
    print_report(run_analysis(nsteps=args.nsteps))


if __name__ == "__main__":
    main()
