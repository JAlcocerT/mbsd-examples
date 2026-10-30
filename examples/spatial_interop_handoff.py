"""One constrained result consumed by FreeCAD, Blender, and browser mappings."""

from pathlib import Path

import numpy as np

from mbsd import Mechanism
from mbsd.spatial import build_transform_handoff, transform_handoff_to_json

try:
    from examples.adapters.blender_reference import animation_tracks
    from examples.adapters.browser_reference import scene_tracks
    from examples.adapters.freecad_reference import placements
except ModuleNotFoundError:  # Direct execution adds examples/, not its parent.
    from adapters.blender_reference import animation_tracks
    from adapters.browser_reference import scene_tracks
    from adapters.freecad_reference import placements


def run_analysis(output_directory: Path) -> dict:
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    rotor = mechanism.body("rotor", inertia=(2.0, 3.0, 4.0))
    mechanism.revolute(ground, rotor, name="hinge")
    motor = mechanism.rigid_body_load(rotor, torque=(0.0, 0.0, 4.0))
    result = mechanism.simulate_constrained_rigid_bodies(
        np.linspace(0.0, 1.0, 11), loads=(motor,)
    )
    result_payload = mechanism.constrained_result_to_dict(result)
    geometry = {
        "body:ground": {"uri": "assembly.step", "object": "Ground"},
        "body:rotor": {"uri": "assembly.step", "object": "Rotor"},
    }
    handoffs = {
        target: build_transform_handoff(
            result_payload, target=target, geometry_references=geometry
        )
        for target in ("freecad", "blender", "browser")
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    for target, payload in handoffs.items():
        transform_handoff_to_json(payload, output_directory / f"{target}-tracks.json")
    return {
        "handoffs": handoffs,
        "freecad": placements(handoffs["freecad"]),
        "blender": animation_tracks(handoffs["blender"]),
        "browser": scene_tracks(handoffs["browser"]),
    }


def main() -> None:
    output = Path(__file__).parents[1] / "artifacts" / "interop"
    metrics = run_analysis(output)
    print("Spatial interoperability handoff")
    print(f"  FreeCAD objects: {len(metrics['freecad'])}")
    print(f"  Blender tracks:  {len(metrics['blender'])}")
    print(f"  Browser objects: {len(metrics['browser']['objects'])}")
    print(f"  artifacts:       {output}")


if __name__ == "__main__":
    main()
