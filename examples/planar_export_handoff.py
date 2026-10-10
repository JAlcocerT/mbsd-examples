"""Generate portable MBSD export artifacts for app/CAD handoff workflows."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mbsd import Mechanism, Spring


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "artifacts" / "export"


def build_mechanism():
    mechanism = Mechanism.planar(gravity=(0.0, 0.0))
    ground = mechanism.ground()
    slider = mechanism.body("slider", mass=1.0, inertia=0.01)
    mechanism.slider(
        ground,
        slider,
        axis=(1.0, 0.0),
        point_rail=(0.1, 0.2),
        point_slider=(-0.2, 0.3),
    )
    mechanism.coordinate_drive(
        slider,
        "x",
        value=lambda t: 0.4 + 0.2 * np.sin(2.0 * np.pi * t),
        velocity=lambda t: 0.4 * np.pi * np.cos(2.0 * np.pi * t),
        acceleration=lambda t: -0.8 * np.pi**2 * np.sin(2.0 * np.pi * t),
    )
    spring = Spring(
        i=int(ground),
        j=int(slider),
        k=25.0,
        c=0.4,
        l0=0.4,
        ri=np.array([0.0, 0.0]),
        rj=np.array([0.0, 0.0]),
    )
    return mechanism, slider, spring


def run_export(output_dir: Path = EXPORT_DIR) -> dict[str, Path | float]:
    mechanism, slider, spring = build_mechanism()
    q0 = np.zeros(mechanism.ncoord)
    q0[3] = 0.4
    q0[4] = -0.1
    result = mechanism.solve_kinematics(np.linspace(0.0, 1.0, 101), q0=q0)
    mechanism.assert_constraints_satisfied(result)

    output_dir.mkdir(parents=True, exist_ok=True)
    mechanism_json = mechanism.to_json(
        output_dir / "planar-slider-mechanism.json",
        springs=[spring],
        metadata={"name": "planar-slider", "consumer": ["pwa", "cad"]},
    )
    result_json = mechanism.result_to_json(
        result,
        output_dir / "planar-slider-result.json",
        metadata={"name": "planar-slider-kinematics"},
    )
    trajectory_csv = mechanism.result_to_csv(result, output_dir / "planar-slider-trajectory.csv")
    point_json = mechanism.point_trace_to_json(
        result,
        slider,
        (0.25, 0.0),
        output_dir / "planar-slider-marker.json",
        name="slider_marker",
        metadata={"purpose": "cad_path"},
    )
    point_csv = mechanism.point_trace_to_csv(
        result,
        slider,
        (0.25, 0.0),
        output_dir / "planar-slider-marker.csv",
        name="slider_marker",
    )

    return {
        "mechanism_json": mechanism_json,
        "result_json": result_json,
        "trajectory_csv": trajectory_csv,
        "point_json": point_json,
        "point_csv": point_csv,
        "max_constraint_residual": mechanism.max_constraint_residual(result),
    }


def print_report(exports: dict[str, Path | float]) -> None:
    print("Planar export handoff")
    print(f"  mechanism JSON:         {exports['mechanism_json']}")
    print(f"  result JSON:            {exports['result_json']}")
    print(f"  trajectory CSV:         {exports['trajectory_csv']}")
    print(f"  point trace JSON:       {exports['point_json']}")
    print(f"  point trace CSV:        {exports['point_csv']}")
    print(f"  max constraint residual: {exports['max_constraint_residual']:.3e}")


if __name__ == "__main__":
    print_report(run_export())
