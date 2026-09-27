"""Ars Magica Manager: tracks characters, covenants, laboratories, and libraries."""

import tomllib
from pathlib import Path

#: The repo root: the app runs from a checkout, next to its pyproject.toml.
ROOT = Path(__file__).resolve().parent.parent

#: The app's version, 0.MINOR.PATCH. pyproject.toml is the one place it's
#: set (see CHANGELOG.md, and CLAUDE.md for when it goes up).
__version__: str = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]

#: The repo's data/ folder: the shared catalogs, and (git-ignored) the saga
#: files and app settings.
DATA_DIR = ROOT / "data"
