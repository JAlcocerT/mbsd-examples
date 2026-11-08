"""The Blender reference consumer against the golden interop fixtures.

The contract checks run everywhere (they are plain Python). The full import
runs inside a real Blender when one is found (``blender`` on PATH or
``MBSD_BLENDER``); CI without Blender skips only that test.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from mbsd.spatial import validate_transform_handoff

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from examples.adapters.blender_consumer import HandoffRejected, check_handoff  # noqa: E402

FIXTURES = ROOT / "fixtures" / "interop"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text())["fixtures"]


def _load(name):
    return json.loads((FIXTURES / name).read_text())


@pytest.mark.parametrize("name", sorted(MANIFEST))
def test_contract_verdict_matches_manifest(name):
    payload = _load(name)
    if MANIFEST[name]["expect"] == "import":
        assert check_handoff(payload)["tracks"] == 4
    else:
        with pytest.raises(HandoffRejected):
            check_handoff(payload)


def test_core_validator_accepts_the_golden_handoff():
    golden = _load("blender-golden.json")
    assert validate_transform_handoff(golden)["artifact_id"] == golden["artifact_id"]
    for name in ("reject-geometry-loading.json", "reject-xyzw-quaternions.json", "reject-edited-content.json",
                 "reject-mirror-axes.json", "reject-duplicate-id.json", "reject-unknown-schema-version.json"):
        with pytest.raises(ValueError):
            validate_transform_handoff(_load(name))


def test_golden_fixture_is_reproducible():
    from make_interop_fixtures import cardan_handoff

    fresh, golden = cardan_handoff(), _load("blender-golden.json")
    assert [t["id"] for t in fresh["tracks"]] == [t["id"] for t in golden["tracks"]]
    for a, b in zip(fresh["tracks"], golden["tracks"]):
        for sa, sb in zip(a["samples"], b["samples"]):
            assert np.allclose(sa["translation"], sb["translation"], atol=1e-9)
            # q and -q are the same rotation; at a half turn (w ~ 0) the sign is set by round-off.
            qa, qb = np.asarray(sa["rotation_wxyz"]), np.asarray(sb["rotation_wxyz"])
            assert min(np.max(np.abs(qa - qb)), np.max(np.abs(qa + qb))) < 1e-9


def _blender():
    return os.environ.get("MBSD_BLENDER") or shutil.which("blender")


@pytest.mark.skipif(_blender() is None, reason="Blender is not installed")
def test_blender_imports_golden_and_rejects_the_rest(tmp_path):
    report_path = tmp_path / "report.json"
    completed = subprocess.run(
        [_blender(), "-b", "--factory-startup", "--python", str(ROOT / "examples/adapters/blender_consumer.py"),
         "--", str(FIXTURES), str(report_path)],
        capture_output=True, text=True, timeout=300,
    )
    assert completed.returncode == 0, completed.stderr[-2000:]
    report = json.loads(report_path.read_text())
    for name, entry in report["fixtures"].items():
        assert entry["outcome"] == ("imported" if MANIFEST[name]["expect"] == "import" else "rejected"), name
        if entry["outcome"] == "rejected":
            assert entry["objects_created"] == 0, name
    golden = report["fixtures"]["blender-golden.json"]
    assert golden["objects_created"] == 4
    assert golden["ids"] == ["body:cross", "body:frame", "body:shaft_in", "body:shaft_out"]
    assert golden["geometry_uris"].count("cardan.step") == 3
    assert golden["max_position_error_m"] < 1e-6       # float32 keyframes
    assert golden["max_rotation_error_rad"] < 1e-5
