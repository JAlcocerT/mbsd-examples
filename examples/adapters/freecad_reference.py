"""Map MBSD transform tracks to FreeCAD Placement-compatible records."""

from typing import Any, Mapping

from mbsd.spatial import validate_transform_handoff


def placements(handoff: Mapping[str, Any]) -> list[dict[str, Any]]:
    payload = validate_transform_handoff(handoff)
    if payload["target"]["engine"] != "freecad":
        raise ValueError("FreeCAD adapter requires a freecad transform handoff")
    return [{
        "object_id": track["id"], "label": track["name"],
        "geometry_reference": track.get("geometry_reference"),
        "placements": [{
            "time_s": sample["time_s"], "base_mm": sample["translation"],
            "rotation_quaternion_wxyz": sample["rotation_wxyz"],
        } for sample in track["samples"]],
    } for track in payload["tracks"]]
