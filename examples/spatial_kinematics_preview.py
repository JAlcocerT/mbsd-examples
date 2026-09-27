"""Experimental 3D kinematics residual preview."""

from __future__ import annotations

import numpy as np

from mbsd.spatial import (
    Pose3D,
    Quaternion,
    SphericalJoint3D,
    max_spatial_residual,
    point_position,
)


def run_analysis() -> dict[str, object]:
    poses = [
        Pose3D(
            translation=np.array([1.0, 0.0, 0.0]),
            rotation=Quaternion.from_axis_angle((0.0, 0.0, 1.0), np.pi / 2.0),
        ),
        Pose3D(translation=np.array([0.0, 1.0, 0.0])),
    ]
    joint = SphericalJoint3D(
        name="coincident-points",
        body_i=0,
        body_j=1,
        point_i=np.array([1.0, 0.0, 0.0]),
        point_j=np.array([1.0, 0.0, 0.0]),
    )
    residual = joint.residual(poses)
    tip = point_position(poses[0], np.array([0.0, 1.0, 0.5]))
    return {
        "joint": joint.as_dict(),
        "residual": residual,
        "tip": tip,
        "max_residual": max_spatial_residual([residual]),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial kinematics preview")
    print(f"  joint kind:           {metrics['joint']['kind']}")
    print(f"  residual:             {np.array2string(metrics['residual'], precision=6)}")
    print(f"  tip:                  {np.array2string(metrics['tip'], precision=6)}")
    print(f"  max residual:         {metrics['max_residual']:.3e}")


if __name__ == "__main__":
    print_report(run_analysis())
