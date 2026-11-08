"""Blender reference consumer of the MBSD transform-track handoff.

This is the 1.0 reference consumer of the neutral adapter contract. It runs
inside Blender and deliberately does **not** import mbsd: an engine only gets
the JSON handoff, so everything it needs must be in the contract.

    blender -b --factory-startup --python examples/adapters/blender_consumer.py -- \\
        fixtures/interop artifacts/interop/blender-report.json

For every fixture listed in ``manifest.json`` it

1. checks the contract **before** creating anything: schema and version,
   exact capabilities (no geometry loading, no force import), Blender target,
   right-handed axes, ``wxyz`` active body-to-world quaternions, a proper
   orthogonal axis matrix, metres, unique stable track IDs, one shared time
   grid, unit quaternions and the content ``artifact_id``;
2. imports accepted handoffs as one empty per track (named by track, keyed by
   the stable ``mbsd_id`` property, geometry kept as a reference only) with
   location and quaternion keyframes at ``frame = 1 + fps * t``;
3. evaluates the scene at every keyframe and measures the position and
   rotation error of ``matrix_world`` against the samples;
4. writes a JSON report the test suite asserts on.

The contract checks are plain Python (no bpy, no numpy), so the same function
is unit-tested outside Blender.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

EXPECTED_CAPABILITIES = {"transform_tracks": True, "geometry_loading": False, "force_import": False}
GEOMETRY_FIELDS = {"uri", "object", "media_type", "sha256"}


class HandoffRejected(ValueError):
    """The handoff is outside what this consumer supports; nothing was imported."""


def _identity(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def _reject(reason: str):
    raise HandoffRejected(reason)


def check_handoff(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a handoff for Blender import; raise HandoffRejected otherwise."""
    if not isinstance(payload, Mapping):
        _reject("payload must be an object")
    if payload.get("schema") != "mbsd.interop.transform_tracks" or payload.get("schema_version") != 1:
        _reject("unsupported schema or schema_version")
    if payload.get("capabilities") != EXPECTED_CAPABILITIES:
        _reject("unsupported capabilities: only transform tracks can be imported")
    target = payload.get("target") or {}
    if target.get("engine") != "blender":
        _reject(f"handoff targets {target.get('engine')!r}, not blender")
    if target.get("coordinate_handedness") != "right_handed":
        _reject("only right-handed coordinates are supported")
    if target.get("quaternion_order") != "wxyz" or target.get("rotation") != "active_body_to_world":
        _reject("quaternions must be wxyz, active body-to-world")
    if target.get("time_unit") != "s":
        _reject("time must be in seconds")
    if target.get("length_unit") != "m" or target.get("length_scale_from_m") != 1.0:
        _reject("Blender scenes are in metres: length_scale_from_m must be 1")
    axes = target.get("axis_matrix_source_to_target")
    if not (isinstance(axes, list) and len(axes) == 3 and all(isinstance(r, list) and len(r) == 3 for r in axes)):
        _reject("axis matrix must be 3x3")
    for i in range(3):
        for j in range(3):
            dot = sum(axes[i][k] * axes[j][k] for k in range(3))
            if abs(dot - (1.0 if i == j else 0.0)) > 1e-9:
                _reject("axis matrix is not orthogonal")
    det = (axes[0][0] * (axes[1][1] * axes[2][2] - axes[1][2] * axes[2][1])
           - axes[0][1] * (axes[1][0] * axes[2][2] - axes[1][2] * axes[2][0])
           + axes[0][2] * (axes[1][0] * axes[2][1] - axes[1][1] * axes[2][0]))
    if abs(det - 1.0) > 1e-9:
        _reject("axis matrix must be a proper rotation (det = +1)")
    tracks = payload.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        _reject("no tracks")
    ids, grid = set(), None
    for index, track in enumerate(tracks):
        track_id = track.get("id")
        if track.get("index") != index or not isinstance(track_id, str) or not track_id or track_id in ids:
            _reject(f"track {index} has a missing or duplicate id")
        ids.add(track_id)
        reference = track.get("geometry_reference")
        if reference is not None and (not set(reference) <= GEOMETRY_FIELDS or not reference.get("uri")):
            _reject(f"track {track_id} has an invalid geometry reference")
        times = [s.get("time_s") for s in track.get("samples", [])]
        if len(times) < 2 or any(b <= a for a, b in zip(times, times[1:])):
            _reject(f"track {track_id} needs strictly increasing sample times")
        if grid is None:
            grid = times
        elif times != grid:
            _reject("tracks must share one time grid")
        for sample in track["samples"]:
            q = sample.get("rotation_wxyz")
            p = sample.get("translation")
            if not (isinstance(q, list) and len(q) == 4 and isinstance(p, list) and len(p) == 3):
                _reject(f"track {track_id} has a malformed sample")
            if abs(math.sqrt(sum(c * c for c in q)) - 1.0) > 1e-9:
                _reject(f"track {track_id} has a non-unit quaternion")
    detached = json.loads(json.dumps(payload))
    artifact_id = detached.pop("artifact_id", None)
    if artifact_id != _identity(detached):
        _reject("artifact_id does not match the content (edited or corrupted)")
    return {"tracks": len(tracks), "samples": len(grid), "artifact_id": artifact_id}


# --- Blender side ------------------------------------------------------------------------


def import_handoff(payload: Mapping[str, Any], *, fps: int = 60):
    """Create one keyframed empty per track in a fresh collection."""
    import bpy

    scene = bpy.context.scene
    scene.render.fps = fps
    scene.render.fps_base = 1.0
    collection = bpy.data.collections.new(f"MBSD {payload['artifact_id']}")
    scene.collection.children.link(collection)
    objects = {}
    for track in payload["tracks"]:
        obj = bpy.data.objects.new(track["name"], None)
        obj["mbsd_id"] = track["id"]
        obj["mbsd_artifact_id"] = payload["artifact_id"]
        reference = track.get("geometry_reference")
        if reference:
            obj["mbsd_geometry_uri"] = reference["uri"]
            obj["mbsd_geometry_object"] = reference.get("object", "")
        obj.rotation_mode = "QUATERNION"
        collection.objects.link(obj)
        for sample in track["samples"]:
            frame = 1.0 + fps * sample["time_s"]
            obj.location = sample["translation"]
            obj.rotation_quaternion = sample["rotation_wxyz"]
            obj.keyframe_insert("location", frame=frame)
            obj.keyframe_insert("rotation_quaternion", frame=frame)
        objects[track["id"]] = obj
    scene.frame_start = 1
    scene.frame_end = int(math.ceil(1.0 + fps * payload["tracks"][0]["samples"][-1]["time_s"]))
    return objects


def verify_import(payload: Mapping[str, Any], objects, *, fps: int = 60) -> dict[str, float]:
    """Evaluate every keyframe and compare matrix_world with the samples."""
    import bpy

    scene = bpy.context.scene
    position_error = rotation_error = 0.0
    for track in payload["tracks"]:
        obj = objects[track["id"]]
        for sample in track["samples"]:
            frame = 1.0 + fps * sample["time_s"]
            whole = int(math.floor(frame))
            scene.frame_set(whole, subframe=frame - whole)
            world = obj.matrix_world
            location = world.to_translation()
            quaternion = world.to_quaternion()
            position_error = max(position_error, max(abs(location[i] - sample["translation"][i]) for i in range(3)))
            # Chord distance, robust near zero (acos of a dot product near 1
            # amplifies Blender's float32 rounding); q and -q are one rotation.
            target = sample["rotation_wxyz"]
            chord = min(math.sqrt(sum((quaternion[i] - s * target[i]) ** 2 for i in range(4))) for s in (1.0, -1.0))
            rotation_error = max(rotation_error, 4.0 * math.asin(min(1.0, chord / 2.0)))
    return {"max_position_error_m": position_error, "max_rotation_error_rad": rotation_error}


def run(fixtures: Path, report_path: Path) -> dict[str, Any]:
    import bpy

    manifest = json.loads((fixtures / "manifest.json").read_text(encoding="utf-8"))
    report = {"blender": bpy.app.version_string, "fixtures": {}}
    for name, expectation in manifest["fixtures"].items():
        payload = json.loads((fixtures / name).read_text(encoding="utf-8"))
        before = len(bpy.data.objects)
        entry: dict[str, Any] = {"expected": expectation["expect"]}
        try:
            summary = check_handoff(payload)
        except HandoffRejected as exc:
            entry.update(outcome="rejected", reason=str(exc), objects_created=len(bpy.data.objects) - before)
        else:
            objects = import_handoff(payload)
            entry.update(outcome="imported", **summary, objects_created=len(bpy.data.objects) - before,
                         ids=sorted(o["mbsd_id"] for o in objects.values()),
                         geometry_uris=sorted(o.get("mbsd_geometry_uri", "") for o in objects.values()),
                         **verify_import(payload, objects))
        report["fixtures"][name] = entry
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if len(args) != 2:
        raise SystemExit("usage: blender -b --python blender_consumer.py -- FIXTURES_DIR REPORT.json")
    result = run(Path(args[0]), Path(args[1]))
    for fixture, entry in result["fixtures"].items():
        print(f"{fixture:40s} {entry['outcome']:9s} (expected {entry['expected']})")
