.PHONY: help sync examples gallery test check clean

UV ?= uv

help:
	@echo "Targets:"
	@echo "  make sync      Install dependencies with uv"
	@echo "  make examples  Run example scripts"
	@echo "  make gallery   Generate gallery assets"
	@echo "  make test      Run pytest"
	@echo "  make check     Run tests, examples, gallery, and ruff"
	@echo "  make clean     Remove generated local outputs"

sync:
	$(UV) sync --extra dev

examples:
	$(UV) run python examples/planar_driven_slider.py
	$(UV) run python examples/planar_mass_spring.py
	$(UV) run python examples/planar_slider_crank_analysis.py

gallery:
	$(UV) run python scripts/generate_week1_gallery.py

test:
	$(UV) run pytest -q

check: test examples gallery
	$(UV) run ruff check .

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	rm -f gallery/png/*.png
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
