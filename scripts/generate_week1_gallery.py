"""Generate the MBSD Examples v0.1.0 gallery."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

from mbsd import Mechanism, Spring


ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "gallery" / "png"
sys.path.insert(0, str(ROOT))

from examples.planar_slider_crank_analysis import build_slider_crank, run_analysis  # noqa: E402


def save_driven_slider() -> None:
    omega = 2.0 * np.pi
    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    slider = mechanism.body("slider", mass=1.0, inertia=0.01)

    mechanism.slider(ground, slider, axis=(1.0, 0.0))
    mechanism.coordinate_drive(
        slider,
        "x",
        value=lambda t: np.sin(omega * t),
        velocity=lambda t: omega * np.cos(omega * t),
        acceleration=lambda t: -(omega**2) * np.sin(omega * t),
    )

    t = np.linspace(0.0, 1.0, 201)
    result = mechanism.solve_kinematics(t)

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(result.t, result.q[3, :], label="x")
    ax.plot(result.t, result.v[3, :], label="vx")
    ax.set_title("Driven slider")
    ax.set_xlabel("time [s]")
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(GALLERY / "driven-slider.png", dpi=160)
    plt.close(fig)


def save_mass_spring() -> None:
    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    mass = mechanism.body("mass", mass=1.0, inertia=0.01)
    mechanism.slider(ground, mass, axis=(1.0, 0.0))

    spring = Spring(
        i=int(ground),
        j=int(mass),
        k=10.0,
        c=0.5,
        l0=1.0,
        ri=np.array([0.0, 0.0]),
        rj=np.array([0.0, 0.0]),
    )

    q0 = np.zeros(mechanism.ncoord)
    q0[3] = 1.5
    v0 = np.zeros(mechanism.ncoord)
    t = np.linspace(0.0, 1.0, 201)
    result = mechanism.simulate(t, q0=q0, v0=v0, springs=[spring])

    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(result.t, result.q[3, :], color="#2563eb")
    ax.set_title("Mass-spring-damper")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("x [m]")
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(GALLERY / "mass-spring-damper.png", dpi=160)
    plt.close(fig)


def save_slider_crank() -> None:
    mechanism, q0, params = build_slider_crank()
    t = np.linspace(0.0, 1.0, 361)
    result = mechanism.solve_kinematics(t, q0=q0)
    metrics = run_analysis(nsteps=361)

    fig, axes = plt.subplots(3, 1, figsize=(8.0, 7.0), sharex=True)
    fig.suptitle(
        "Slider-crank analysis "
        f"(max residual {metrics['max_constraint_residual']:.1e})"
    )
    axes[0].plot(t, result.q[9, :], color="#2563eb")
    axes[0].set_ylabel("slider x [m]")
    axes[1].plot(t, result.v[9, :], color="#dc2626")
    axes[1].set_ylabel("slider vx [m/s]")
    axes[2].plot(t, result.a[9, :], color="#16a34a")
    axes[2].set_ylabel("slider ax [m/s^2]")
    axes[2].set_xlabel("time [s]")
    for ax in axes:
        ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(GALLERY / "slider-crank-analysis.png", dpi=160)
    plt.close(fig)


def main() -> None:
    GALLERY.mkdir(parents=True, exist_ok=True)
    save_driven_slider()
    save_mass_spring()
    save_slider_crank()
    print(f"Generated gallery in {GALLERY}")


if __name__ == "__main__":
    main()
