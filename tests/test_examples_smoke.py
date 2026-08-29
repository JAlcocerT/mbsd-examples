import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(path: str) -> str:
    completed = subprocess.run(
        [sys.executable, path],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


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
