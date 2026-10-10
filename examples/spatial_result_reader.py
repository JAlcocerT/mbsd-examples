"""Minimal public reader for the spatial kinematic-result JSON contract."""

from pathlib import Path

from mbsd.spatial import load_spatial_kinematic_result_payload


def read_summary(path: Path) -> dict[str, object]:
    payload = load_spatial_kinematic_result_payload(path)
    return {
        "model_id": payload["model_id"],
        "steps": len(payload["time"]),
        "bodies": [body["name"] for body in payload["bodies"]],
        "success": payload["solver_status"]["success"],
        "max_position_residual": payload["diagnostics"]["max_position_residual"],
    }
