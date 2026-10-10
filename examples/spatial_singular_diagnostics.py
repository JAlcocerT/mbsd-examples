"""Deliberately redundant spatial model and inconsistent-solve failure."""

from mbsd import Mechanism, MechanismSolveError


def run_analysis() -> dict[str, object]:
    singular = Mechanism.spatial()
    ground = singular.ground()
    link = singular.body("link")
    singular.spherical(ground, link, name="pivot-a")
    singular.spherical(ground, link, name="pivot-b")

    inconsistent = Mechanism.spatial()
    fixed_ground = inconsistent.ground()
    inconsistent.coordinate_drive(
        fixed_ground, "x", value=lambda _t: 1.0, velocity=lambda _t: 0.0
    )
    try:
        inconsistent.solve_position()
    except MechanismSolveError as error:
        failure = str(error)
    else:
        raise AssertionError("inconsistent model unexpectedly solved")
    return {"diagnostics": singular.model_diagnostics().as_dict(), "failure": failure}


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial singular diagnostics")
    print(f"  classification:        {metrics['diagnostics']['classification']}")
    print(f"  inconsistent failure:  {metrics['failure']}")


if __name__ == "__main__":
    print_report(run_analysis())
