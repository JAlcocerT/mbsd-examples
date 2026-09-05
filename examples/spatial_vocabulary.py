"""Small example for the experimental MBSD spatial vocabulary."""

from __future__ import annotations

import numpy as np

from mbsd.spatial import Frame3D, Pose3D, Quaternion, SpatialBody, SpatialModel


def run_example() -> dict[str, object]:
    pose = Pose3D(
        translation=np.array([1.0, 2.0, 0.5]),
        rotation=Quaternion.from_axis_angle((0.0, 0.0, 1.0), np.pi / 4.0),
    )
    model = SpatialModel().with_body(
        SpatialBody("spatial-link", mass=2.0, inertia=(0.1, 0.2, 0.3))
    )
    model = model.with_frame(Frame3D("link-frame", pose))

    local_tip = np.array([0.5, 0.0, 0.0])
    world_tip = pose.transform_point(local_tip)

    return {
        "model": model.as_dict(),
        "world_tip": world_tip,
        "rotation_det": float(np.linalg.det(pose.rotation.to_rotation_matrix())),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial vocabulary")
    print(f"  schema:              {metrics['model']['schema']}")
    print(f"  body name:           {metrics['model']['bodies'][0]['name']}")
    print(f"  world tip:           {np.array2string(metrics['world_tip'], precision=6)}")
    print(f"  rotation det:        {metrics['rotation_det']:.6f}")


if __name__ == "__main__":
    print_report(run_example())
