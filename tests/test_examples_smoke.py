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


def test_gallery_script_runs():
    output = run_script("scripts/generate_week1_gallery.py")
    assert "Generated gallery" in output
    assert (ROOT / "gallery" / "png" / "driven-slider.png").exists()
    assert (ROOT / "gallery" / "png" / "mass-spring-damper.png").exists()
    assert (ROOT / "gallery" / "png" / "slider-crank-analysis.png").exists()
