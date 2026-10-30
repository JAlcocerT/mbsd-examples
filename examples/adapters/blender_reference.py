"""Map MBSD transform tracks to Blender animation-keyframe records."""

from typing import Any, Mapping

from mbsd.spatial import validate_transform_handoff


def animation_tracks(handoff: Mapping[str, Any], *, fps: float = 24.0) -> list[dict[str, Any]]:
    payload = validate_transform_handoff(handoff)
    if payload["target"]["engine"] != "blender":
        raise ValueError("Blender adapter requires a blender transform handoff")
    if fps <= 0:
        raise ValueError("fps must be positive")
    return [{
        "object_id": track["id"], "name": track["name"],
        "geometry_reference": track.get("geometry_reference"),
        "rotation_mode": "QUATERNION",
        "keyframes": [{
            "frame": 1.0 + fps * sample["time_s"],
            "location_m": sample["translation"],
            "rotation_quaternion_wxyz": sample["rotation_wxyz"],
        } for sample in track["samples"]],
    } for track in payload["tracks"]]
