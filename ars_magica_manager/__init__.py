"""Armarius, a saga manager for Ars Magica: tracks characters, covenants,
laboratories, and libraries."""

import sys
import tomllib
from pathlib import Path

#: Whether this copy runs from a Build (the app packed by PyInstaller), not
#: from a checkout with Python.
FROZEN: bool = bool(getattr(sys, "frozen", False))

#: Where the app's own files are: the repo root when it runs from a
#: checkout, or the folder a Build unpacked them into, laid out the same
#: way (pyproject.toml, CHANGELOG.md, NOTICE.md, data/). Every module finds
#: those files from here, so neither layout is known anywhere else.
ROOT = Path(getattr(sys, "_MEIPASS", None) or Path(__file__).resolve().parent.parent)

#: The app's version, MAJOR.MINOR.PATCH. pyproject.toml is the one place
#: it's set (see CHANGELOG.md); a Build carries a copy of it.
__version__: str = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]

#: The app's data/ folder: the shared catalogs, packs and tutorials. The
#: user's own data (sagas, backups, exports, settings) is in
#: paths.data_dir().
DATA_DIR = ROOT / "data"
