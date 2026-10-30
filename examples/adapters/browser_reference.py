"""Map MBSD transform tracks to a compact browser/PWA record."""

from typing import Any, Mapping

from mbsd.spatial import validate_transform_handoff


def scene_tracks(handoff: Mapping[str, Any]) -> dict[str, Any]:
    payload = validate_transform_handoff(handoff)
    if payload["target"]["engine"] != "browser":
        raise ValueError("browser adapter requires a browser transform handoff")
    return {
        "artifact_id": payload["artifact_id"],
        "time_s": [sample["time_s"] for sample in payload["tracks"][0]["samples"]],
        "objects": [{
            "id": track["id"], "name": track["name"],
            "geometry_reference": track.get("geometry_reference"),
            "translation_m": [sample["translation"] for sample in track["samples"]],
            "rotation_wxyz": [sample["rotation_wxyz"] for sample in track["samples"]],
        } for track in payload["tracks"]],
    }
