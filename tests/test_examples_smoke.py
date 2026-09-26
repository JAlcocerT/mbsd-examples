import csv
import json
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

import mbsd_examples

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples import planar_energy_conservation
from examples import planar_export_handoff
from examples import planar_diagnostics_panel
from examples import planar_four_bar
from examples import planar_function_fit
from examples import planar_pendulum
from examples import planar_precision_synthesis
from examples import planar_scotch_yoke
from examples import planar_slider_crank_analysis
from examples import spatial_vocabulary


def run_script(path: str) -> str:
    completed = subprocess.run(
        [sys.executable, path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def test_package_version_matches_installed_metadata():
    assert mbsd_examples.__version__ == version("mbsd-examples")


def test_driven_slider_example_runs():
    assert "Driven slider" in run_script("examples/planar_driven_slider.py")


def test_mass_spring_example_runs():
    assert "Mass-spring-damper" in run_script("examples/planar_mass_spring.py")


def test_slider_crank_example_runs():
    output = run_script("examples/planar_slider_crank_analysis.py")
    assert "Slider-crank analysis" in output
    assert "max constraint residual" in output


def test_four_bar_example_runs():
    output = run_script("examples/planar_four_bar.py")
    assert "Four-bar linkage" in output
    assert "max constraint residual" in output


def test_scotch_yoke_example_runs():
    output = run_script("examples/planar_scotch_yoke.py")
    assert "Scotch yoke" in output
    assert "max x tracking error" in output


def test_pendulum_example_runs():
    output = run_script("examples/planar_pendulum.py")
    assert "Driven pendulum" in output
    assert "theta range" in output


def test_energy_conservation_example_runs():
    output = run_script("examples/planar_energy_conservation.py")
    assert "Undamped mass-spring energy" in output
    assert "relative energy drift" in output


def test_precision_synthesis_example_runs():
    output = run_script("examples/planar_precision_synthesis.py")
    assert "Four-bar precision synthesis" in output
    assert "max precision error" in output


def test_function_fit_example_runs():
    output = run_script("examples/planar_function_fit.py")
    assert "Four-bar function fit" in output
    assert "RMS error" in output


def test_export_handoff_example_runs():
    output = run_script("examples/planar_export_handoff.py")
    assert "Planar export handoff" in output
    assert "mechanism JSON" in output
    assert "point trace JSON" in output


def test_spatial_vocabulary_example_runs():
    output = run_script("examples/spatial_vocabulary.py")
    assert "Spatial vocabulary" in output
    assert "rotation det" in output


def test_planar_diagnostics_panel_example_runs():
    output = run_script("examples/planar_diagnostics_panel.py")
    assert "Planar diagnostics panel" in output
    assert "Jacobian rank" in output


def test_gallery_script_runs():
    output = run_script("scripts/generate_gallery.py")
    assert "Generated gallery" in output
    assert (ROOT / "gallery" / "png" / "driven-slider.png").exists()
    assert (ROOT / "gallery" / "png" / "mass-spring-damper.png").exists()
    assert (ROOT / "gallery" / "png" / "slider-crank-analysis.png").exists()
    assert (ROOT / "gallery" / "png" / "four-bar-linkage.png").exists()
    assert (ROOT / "gallery" / "png" / "scotch-yoke.png").exists()
    assert (ROOT / "gallery" / "png" / "driven-pendulum.png").exists()
    assert (ROOT / "gallery" / "png" / "energy-conservation.png").exists()
    assert (ROOT / "gallery" / "png" / "precision-synthesis.png").exists()
    assert (ROOT / "gallery" / "png" / "function-fit.png").exists()


def test_slider_crank_metrics_regression():
    metrics = planar_slider_crank_analysis.run_analysis(nsteps=181)

    assert metrics["max_constraint_residual"] < 1e-8
    assert metrics["max_drive_error"] < 1e-10
    assert metrics["max_slider_y_error"] < 1e-10
    assert metrics["max_slider_theta_error"] < 1e-10
    assert metrics["slider_stroke"] == pytest.approx(0.7, abs=1e-6)
    assert metrics["velocity_fd_error"] < 1e-3
    assert metrics["acceleration_fd_error"] < 1e-2


def test_canonical_mechanism_metrics_regression():
    four_bar = planar_four_bar.run_analysis(nsteps=181)
    scotch_yoke = planar_scotch_yoke.run_analysis(nsteps=181)
    pendulum = planar_pendulum.run_analysis(nsteps=181)

    assert four_bar["max_constraint_residual"] < 1e-9
    assert four_bar["rocker_angle_range"] > 0.8
    assert scotch_yoke["max_constraint_residual"] < 1e-10
    assert scotch_yoke["max_x_error"] < 1e-10
    assert scotch_yoke["stroke"] == pytest.approx(0.7, abs=1e-6)
    assert pendulum["max_constraint_residual"] < 1e-10
    assert pendulum["theta_range"] == pytest.approx(1.3, abs=1e-10)


def test_dynamics_and_synthesis_metrics_regression():
    energy = planar_energy_conservation.run_analysis(nsteps=151)
    precision = planar_precision_synthesis.run_analysis()
    function_fit = planar_function_fit.run_analysis(nsteps=81)

    assert energy["max_constraint_residual"] < 1e-7
    assert energy["relative_energy_drift"] < 1e-5
    assert precision["max_precision_error"] < 1e-12
    assert precision["grashof"] == "crank-rocker"
    assert function_fit["rms_error"] < 0.02
    assert function_fit["max_abs_error"] < 0.06


def test_export_handoff_artifacts_are_created(tmp_path):
    exports = planar_export_handoff.run_export(tmp_path)

    assert exports["max_constraint_residual"] < 1e-9
    assert exports["mechanism_json"].exists()
    assert exports["result_json"].exists()
    assert exports["trajectory_csv"].exists()
    assert exports["point_json"].exists()
    assert exports["point_csv"].exists()

    mechanism = json.loads(exports["mechanism_json"].read_text(encoding="utf-8"))
    result = json.loads(exports["result_json"].read_text(encoding="utf-8"))
    point = json.loads(exports["point_json"].read_text(encoding="utf-8"))
    with exports["trajectory_csv"].open(newline="", encoding="utf-8") as handle:
        trajectory_rows = list(csv.reader(handle))
    with exports["point_csv"].open(newline="", encoding="utf-8") as handle:
        point_rows = list(csv.reader(handle))

    assert mechanism["schema"] == "mbsd.planar.mechanism"
    assert mechanism["schema_version"] == 1
    assert mechanism["units"]["length"] == "m"
    assert mechanism["metadata"]["consumer"] == ["pwa", "cad"]
    assert mechanism["forces"]["springs"][0]["stiffness"] == 25.0
    assert result["schema"] == "mbsd.planar.result"
    assert result["diagnostics"]["max_constraint_residual"] < 1e-9
    assert point["schema"] == "mbsd.planar.point_trace"
    assert point["point"]["name"] == "slider_marker"
    assert len(point["time"]) == 101
    assert trajectory_rows[0][0] == "time_s"
    assert len(trajectory_rows) == 102
    assert point_rows[0][:3] == ["time_s", "x_m", "y_m"]
    assert len(point_rows) == 102


def test_spatial_vocabulary_metrics(tmp_path):
    metrics = spatial_vocabulary.run_example(tmp_path)

    assert metrics["model"]["schema"] == "mbsd.spatial.model"
    assert metrics["model"]["schema_version"] == 1
    assert metrics["model"]["status"] == "experimental"
    assert metrics["model"]["conventions"]["world_frame"] == "right_handed_xyz"
    assert metrics["model"]["bodies"][0]["pose"]["translation"] == [1.0, 2.0, 0.5]
    assert metrics["model"]["frames"][0]["parent_body"] == 0
    assert metrics["model"]["joints"][0]["kind"] == "spherical"
    assert metrics["model"]["joints"][0]["body_i"] is None
    assert metrics["rotation_det"] == pytest.approx(1.0, abs=1e-12)
    assert metrics["model_json"].exists()
    exported = json.loads(metrics["model_json"].read_text(encoding="utf-8"))
    assert exported == metrics["model"]


def test_planar_diagnostics_panel_metrics():
    metrics = planar_diagnostics_panel.run_analysis()

    assert metrics["healthy"]["constraint_norm"] < 1e-10
    assert metrics["healthy"]["velocity_residual_norm"] < 1e-10
    assert metrics["healthy"]["classification"] == "fully_constrained"
    assert metrics["healthy"]["finite"]
    assert metrics["underconstrained"]["classification"] == "underconstrained"
    assert metrics["underconstrained"]["rank_degrees_of_freedom"] == 1
    assert metrics["rank_deficient"]["classification"] == "rank_deficient"
    assert metrics["rank_deficient"]["singular"]
