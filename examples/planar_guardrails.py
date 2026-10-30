"""Agent-style guardrails: validate before solving, check after, export portably."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import numpy as np

import mbsd
from mbsd import Mechanism, NotPortableError, Tabulated
from mbsd.planar import PlanarMechanism


def build_driven_link(portable: bool = True):
    mechanism = Mechanism.planar(gravity=(0.0, -9.81))
    ground = mechanism.ground()
    link = mechanism.body("link", mass=1.0, inertia=0.02)
    mechanism.pin(ground, link, point_b=(-0.25, 0.0), name="hinge")
    if portable:
        law = Tabulated((0.0, 0.5, 1.0), (0.0, 0.6, 0.0))
        mechanism.coordinate_drive(link, "theta", law=law, name="cam_profile")
    else:
        mechanism.coordinate_drive(
            link,
            "theta",
            value=lambda t: 0.6 * np.sin(np.pi * t),
            velocity=lambda t: 0.6 * np.pi * np.cos(np.pi * t),
            acceleration=lambda t: -0.6 * np.pi**2 * np.sin(np.pi * t),
            name="python_profile",
        )
    q0 = np.array([0.0, 0.0, 0.0, 0.25, 0.0, 0.0])
    return mechanism, q0


def run_analysis() -> dict[str, object]:
    t = np.linspace(0.0, 1.0, 101)
    mechanism, q0 = build_driven_link()
    validation = mechanism.validate(q0, t=t)
    too_long = mechanism.validate(q0, t=np.linspace(0.0, 2.0, 11))

    result = mechanism.inverse_dynamics(t, q0=q0)
    verdict = mechanism.check(result)

    with tempfile.TemporaryDirectory() as tmp:
        rebuilt = PlanarMechanism.from_json(mechanism.to_json(Path(tmp) / "link.json"))
    replay = rebuilt.inverse_dynamics(t, q0=q0)

    opaque, _ = build_driven_link(portable=False)
    opaque_report = opaque.validate(q0, t=t)
    try:
        PlanarMechanism.from_dict(opaque.to_dict())
        import_error = None
    except NotPortableError as exc:
        import_error = exc.as_dict()

    return {
        "validation": validation.as_dict(),
        "out_of_table": [issue.code for issue in too_long.issues],
        "check": verdict.as_dict(),
        "replay_identical": bool(np.array_equal(replay.multipliers, result.multipliers)),
        "opaque_portable": opaque_report.portable,
        "opaque_issues": [issue.code for issue in opaque_report.issues],
        "import_error": import_error,
        "operations": [op["name"] for op in mbsd.operation_manifest()["operations"]],
    }


def print_report(report: dict[str, object]) -> None:
    print("Planar guardrails")
    validation = report["validation"]
    print(f"  validate ok / portable:    {validation['ok']} / {validation['portable']}")
    print(f"  classification / DOF:      {validation['classification']} / "
          f"{validation['degrees_of_freedom']}")
    print(f"  t beyond table:            {report['out_of_table']}")
    check = report["check"]
    print(f"  check passed:              {check['passed']}")
    for item in check["checks"]:
        value = "-" if item["value"] is None else f"{item['value']:.3e}"
        limit = "-" if item["threshold"] is None else f"{item['threshold']:.0e}"
        print(f"    {item['name']:<28} passed={item['passed']!s:<5} value={value:<10} limit={limit}")
    print(f"  JSON round trip identical: {report['replay_identical']}")
    print(f"  callable drive portable:   {report['opaque_portable']} {report['opaque_issues']}")
    print(f"  import error:              {json.dumps(report['import_error'])}")
    print(f"  manifest operations:       {', '.join(report['operations'])}")


def main() -> None:
    print_report(run_analysis())


if __name__ == "__main__":
    main()
