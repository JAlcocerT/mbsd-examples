"""Small example for the experimental MBSD spatial vocabulary."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mbsd.spatial import (
    Frame3D,
    Pose3D,
    Quaternion,
    SpatialBody,
    SpatialModel,
    SphericalJoint3D,
)


ROOT = Path(__file__).resolve().parents[1]
EXPORT_DIR = ROOT / "artifacts" / "spatial"


def run_example(output_dir: Path | None = None) -> dict[str, object]:
    pose = Pose3D(
        translation=np.array([1.0, 2.0, 0.5]),
        rotation=Quaternion.from_axis_angle((0.0, 0.0, 1.0), np.pi / 4.0),
    )
    model = SpatialModel(metadata={"name": "pendulum-vocabulary", "solver": None}).with_body(
        SpatialBody(
            "spatial-link",
            mass=2.0,
            inertia=(0.1, 0.2, 0.3),
            center_of_mass=(0.0, 0.0, -0.25),
            pose=pose,
        )
    )
    model = model.with_frame(
        Frame3D(
            "link-tip",
            Pose3D(translation=np.array([0.5, 0.0, 0.0])),
            parent_body=0,
        )
    )
    model = model.with_joint(
        SphericalJoint3D(
            "world-pivot",
            body_i=None,
            body_j=0,
            point_i=(1.0, 2.0, 0.5),
            point_j=(0.0, 0.0, 0.0),
        )
    )

    local_tip = np.array([0.5, 0.0, 0.0])
    world_tip = pose.transform_point(local_tip)

    model_json = None
    if output_dir is not None:
        model_json = model.to_json(output_dir / "spatial-pendulum-model.json")

    return {
        "model": model.as_dict(),
        "model_json": model_json,
        "world_tip": world_tip,
        "rotation_det": float(np.linalg.det(pose.rotation.to_rotation_matrix())),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial vocabulary")
    print(f"  schema:              {metrics['model']['schema']}")
    print(f"  body name:           {metrics['model']['bodies'][0]['name']}")
    print(f"  world tip:           {np.array2string(metrics['world_tip'], precision=6)}")
    print(f"  rotation det:        {metrics['rotation_det']:.6f}")
    if metrics["model_json"] is not None:
        print(f"  model JSON:          {metrics['model_json']}")


if __name__ == "__main__":
    print_report(run_example(EXPORT_DIR))
