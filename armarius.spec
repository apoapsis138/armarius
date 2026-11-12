# PyInstaller spec for a Build of Armarius: one folder holding two programs
# over one set of files. `Armarius` is the desktop (no console window);
# `armarius-terminal` is the terminal version, which hosting also runs with
# a word (host, seats, play) in place of Python (docs/adr/0017).
#
#     uv run --group build pyinstaller armarius.spec --noconfirm
#
# makes dist/Armarius/. The files the app reads from its own folder are
# listed in APP_FILES; tests/test_build_spec.py fails if the app reads one
# that isn't.

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

#: The app's own files outside the package, kept at the same place in the
#: Build as in the repo (ars_magica_manager.ROOT finds them in either).
APP_FILES = [
    ("pyproject.toml", "."),
    ("CHANGELOG.md", "."),
    ("NOTICE.md", "."),
    ("LICENSE", "."),
    ("README.md", "."),
]
#: data/ whole, but for sagas/: saves were once kept there, and a Build
#: never has any.
DATA_FOLDERS = ["book_packages", "packs", "saga_starters", "tutorials"]

import glob
import os
import sys

# The package is found from the repo, not installed: put the repo first on
# the path the hooks below search, or they find nothing and say only a
# warning.
sys.path.insert(0, SPECPATH)

datas = list(APP_FILES)
datas += [(os.path.join("data", name), os.path.join("data", name)) for name in DATA_FOLDERS]
datas += [(path, "data") for path in glob.glob(os.path.join("data", "*.json"))]
# The package's own files: help pages, fonts, art, sounds, word lists and
# their licences.
package_files = collect_data_files("ars_magica_manager")

binaries = []
# The packs' builders import their parts by name, so every module is listed.
hiddenimports = collect_submodules("ars_magica_manager")
if not package_files or not hiddenimports:
    raise SystemExit("armarius.spec: the ars_magica_manager package wasn't found")
datas += package_files
# Textual loads its widgets by name, and textual-serve its page and scripts.
for package in ("textual", "textual_serve", "rich"):
    found = collect_all(package)
    datas += found[0]
    binaries += found[1]
    hiddenimports += found[2]

#: What neither program needs: the tests' and tools' libraries.
EXCLUDES = ["pytest", "pyright", "ruff", "_pytest", "tkinter"]


def analysis(script):
    return Analysis(
        [script],
        pathex=["."],
        binaries=binaries,
        datas=datas,
        hiddenimports=hiddenimports,
        excludes=EXCLUDES,
        noarchive=False,
    )


desktop = analysis("gui.py")
terminal = analysis("main.py")

desktop_exe = EXE(
    PYZ(desktop.pure),
    desktop.scripts,
    [],
    exclude_binaries=True,
    name="Armarius",
    console=False,
    upx=False,
)
terminal_exe = EXE(
    PYZ(terminal.pure),
    terminal.scripts,
    [],
    exclude_binaries=True,
    name="armarius-terminal",
    console=True,
    upx=False,
)

COLLECT(
    desktop_exe,
    desktop.binaries,
    desktop.datas,
    terminal_exe,
    terminal.binaries,
    terminal.datas,
    name="Armarius",
    upx=False,
)
