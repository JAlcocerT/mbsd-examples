"""Two-body spherical-joint rank and degree-of-freedom example."""

from mbsd import Mechanism


def run_analysis() -> dict[str, object]:
    mechanism = Mechanism.spatial()
    ground = mechanism.ground()
    first = mechanism.body("first")
    second = mechanism.body("second")
    mechanism.fixed(ground, first, name="first-fixed")
    mechanism.spherical(first, second, name="coupling")
    return mechanism.model_diagnostics().as_dict()


def print_report(metrics: dict[str, object]) -> None:
    print("Spatial two-body spherical joint")
    print(f"  Jacobian rank:         {metrics['jacobian_rank']}")
    print(f"  degrees of freedom:    {metrics['degrees_of_freedom']}")
    print(f"  classification:        {metrics['classification']}")


if __name__ == "__main__":
    print_report(run_analysis())
