"""Ars Magica Manager: tracks characters, covenants, laboratories, and libraries."""

from pathlib import Path

__version__ = "0.1.0"

#: The repo's data/ folder: the shared catalogs, and (git-ignored) the saga
#: files and app settings.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
