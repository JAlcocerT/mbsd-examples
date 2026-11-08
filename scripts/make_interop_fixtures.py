"""Write the golden transform-handoff fixtures for the reference consumer.

    uv run python scripts/make_interop_fixtures.py

``blender-golden.json`` is a real handoff: a single Cardan shaft simulated by
mbsd (non-trivial rotations), mapped from MBSD's y-up world to Blender's z-up
with a proper axis matrix, with geometry references. Every other fixture is
the golden one with exactly one contract violation (its ``artifact_id`` is
recomputed so that violation is the only problem). ``manifest.json`` lists
what the consumer must do with each.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from mbsd import ConstantSpeed, Mechanism
from mbsd.spatial import Pose3D, Quaternion, build_transform_handoff

OUT = Path(__file__).resolve().parents[1] / "fixtures" / "interop"
Y_UP_TO_Z_UP = [[1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0]]
ROT = Quaternion.from_axis_angle
Z_TO_X = ROT((0.0, 1.0, 0.0), math.pi / 2)
Z_TO_Y = ROT((1.0, 0.0, 0.0), -math.pi / 2)


def _identity(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def _reseal(payload: dict) -> dict:
    payload = copy.deepcopy(payload)
    payload.pop("artifact_id", None)
    payload["artifact_id"] = _identity(payload)
    return payload


def cardan_handoff() -> dict:
    beta = math.radians(30.0)
    m = Mechanism.spatial()
    ground = m.ground("frame")
    shaft_in = m.body("shaft_in", mass=5.0, inertia=(0.04, 0.02, 0.02))
    cross = m.body("cross", mass=0.3, inertia=(0.002, 0.002, 0.002))
    shaft_out = m.body("shaft_out", mass=2.0, inertia=(0.02, 0.02, 0.02))
    z_to_out = ROT((0.0, 0.0, 1.0), beta) * Z_TO_X
    bearing = m.revolute(ground, shaft_in, frame_i=Pose3D(rotation=Z_TO_X), frame_j=Pose3D(rotation=Z_TO_X), name="input_bearing")
    m.revolute(shaft_in, cross, frame_i=Pose3D(rotation=Z_TO_Y), frame_j=Pose3D(rotation=Z_TO_Y), name="yoke_in")
    m.revolute(cross, shaft_out, name="yoke_out")
    m.parallel_axes(ground, shaft_out, frame_i=Pose3D(rotation=z_to_out), frame_j=Pose3D(rotation=z_to_out), name="output_bearing")
    m.revolute_drive(bearing, law=ConstantSpeed(rate=2.0 * math.pi), name="motor")
    result = m.simulate(np.linspace(0.0, 0.5, 31))
    geometry = {
        "body:shaft_in": {"uri": "cardan.step", "object": "ShaftIn", "media_type": "model/step"},
        "body:cross": {"uri": "cardan.step", "object": "Cross", "media_type": "model/step"},
        "body:shaft_out": {"uri": "cardan.step", "object": "ShaftOut", "media_type": "model/step"},
    }
    return build_transform_handoff(m.constrained_result_to_dict(result), target="blender",
                                   axis_matrix=Y_UP_TO_Z_UP, geometry_references=geometry)


def variants(golden: dict) -> dict[str, tuple[dict, str]]:
    def edit(fn):
        payload = copy.deepcopy(golden)
        fn(payload)
        return _reseal(payload)

    corrupted = copy.deepcopy(golden)
    corrupted["tracks"][1]["samples"][3]["translation"][0] += 1e-3  # edited, not resealed
    return {
        "blender-golden.json": (golden, "import"),
        "reject-geometry-loading.json": (edit(lambda p: p["capabilities"].update(geometry_loading=True)), "reject"),
        "reject-force-import.json": (edit(lambda p: p["capabilities"].update(force_import=True)), "reject"),
        "reject-freecad-target.json": (edit(lambda p: p["target"].update(engine="freecad")), "reject"),
        "reject-xyzw-quaternions.json": (edit(lambda p: p["target"].update(quaternion_order="xyzw")), "reject"),
        "reject-left-handed.json": (edit(lambda p: p["target"].update(coordinate_handedness="left_handed")), "reject"),
        "reject-mirror-axes.json": (edit(lambda p: p["target"].update(axis_matrix_source_to_target=[[1, 0, 0], [0, 1, 0], [0, 0, -1]])), "reject"),
        "reject-millimetres.json": (edit(lambda p: p["target"].update(length_unit="mm", length_scale_from_m=1000.0)), "reject"),
        "reject-duplicate-id.json": (edit(lambda p: p["tracks"][2].update(id=p["tracks"][1]["id"])), "reject"),
        "reject-unknown-schema-version.json": (edit(lambda p: p.update(schema_version=2)), "reject"),
        "reject-edited-content.json": (corrupted, "reject"),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    golden = cardan_handoff()
    manifest = {"schema": "mbsd-examples.interop_fixtures", "version": 1, "fixtures": {}}
    for name, (payload, expect) in variants(golden).items():
        (OUT / name).write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        manifest["fixtures"][name] = {"expect": expect}
        print(f"{expect:7s} {name}")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
