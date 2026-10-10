"""Experimental 3D kinematics residual preview."""

from __future__ import annotations

import numpy as np

from mbsd.spatial import (
    FixedJoint3D,
    Frame3D,
    Pose3D,
    Quaternion,
    SphericalJoint3D,
    fixed_joint_descriptor_residual,
    joint_residual_jacobian,
    max_spatial_residual,
    point_position,
    point_velocity,
    resolve_frame_pose,
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
    tip_velocity = point_velocity(
        poses[0],
        np.array([0.0, 1.0, 0.5]),
        linear_velocity=np.zeros(3),
        angular_velocity_world=np.array([0.0, 0.0, 2.0]),
    )
    tip_frame = Frame3D(
        "tip-frame",
        pose=Pose3D(translation=np.array([0.0, 1.0, 0.5])),
        parent_body=0,
    )
    resolved_tip_frame = resolve_frame_pose(tip_frame, poses)
    fixed_joint = FixedJoint3D(
        "tip-world-check",
        body_i=None,
        body_j=0,
        frame_i=resolved_tip_frame,
        frame_j=tip_frame.pose,
    )
    fixed_residual = fixed_joint_descriptor_residual(fixed_joint, poses)
    spherical_jacobian = joint_residual_jacobian(joint, poses)
    return {
        "joint": joint.as_dict(),
        "residual": residual,
        "tip": tip,
        "tip_velocity": tip_velocity,
        "fixed_residual": fixed_residual,
        "spherical_jacobian_shape": spherical_jacobian.shape,
        "spherical_jacobian_rank": int(np.linalg.matrix_rank(spherical_jacobian)),
        "max_residual": max_spatial_residual([residual, fixed_residual[:3], fixed_residual[3:]]),
    }


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial kinematics preview")
    print(f"  joint kind:           {metrics['joint']['kind']}")
    print(f"  residual:             {np.array2string(metrics['residual'], precision=6)}")
    print(f"  tip:                  {np.array2string(metrics['tip'], precision=6)}")
    print(f"  tip velocity:         {np.array2string(metrics['tip_velocity'], precision=6)}")
    print(f"  joint Jacobian rank:  {metrics['spherical_jacobian_rank']}")
    print(f"  max residual:         {metrics['max_residual']:.3e}")


if __name__ == "__main__":
    print_report(run_analysis())
