"""Compatibility wrapper for the original Week 1 gallery command."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_gallery import main


if __name__ == "__main__":
    main()
