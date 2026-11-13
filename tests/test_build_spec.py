"""A Build carries every file the app reads from its own folder.

armarius.spec lists them (APP_FILES, DATA_FOLDERS, data/*.json); a file
the app reads that the spec leaves out would only show as a crash in a
Build, so this checks the spec against the code and data/ instead.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import main
from ars_magica_manager import DATA_DIR, ROOT, launch

PACKAGE = ROOT / "ars_magica_manager"
#: data/ folders a Build leaves out: where saves were once kept.
NOT_SHIPPED = {"sagas"}
#: Files under ROOT this test leaves to others: data/ (checked against
#: DATA_FOLDERS below) and main.py, which launch runs only from a checkout
#: (a Build's terminal program is main.py itself).
CHECKED_ELSEWHERE = {"data", "main.py"}


def _spec_list(name: str) -> set[str]:
    """The names in the spec's list `name`: each entry itself, or the
    first of each pair."""
    tree = ast.parse((ROOT / "armarius.spec").read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            entries = ast.literal_eval(node.value)
            return {str(e[0] if isinstance(e, tuple) else e) for e in entries}
    raise AssertionError(f"armarius.spec has no {name}")


def test_the_spec_carries_every_file_the_app_reads_beside_its_package() -> None:
    shipped = _spec_list("APP_FILES")
    read: set[str] = set()
    for path in PACKAGE.rglob("*.py"):
        read |= set(re.findall(r'ROOT / "([^"]+)"', path.read_text(encoding="utf-8")))
    missing = sorted(read - shipped - CHECKED_ELSEWHERE)
    assert not missing, f"armarius.spec's APP_FILES leaves out {missing}"


def test_the_spec_carries_all_of_data() -> None:
    folders = _spec_list("DATA_FOLDERS")
    present = {p.name for p in DATA_DIR.iterdir() if p.is_dir()} - NOT_SHIPPED
    loose = [p.name for p in DATA_DIR.iterdir() if p.is_file() and p.suffix != ".json"]
    problems = sorted(present - folders) + sorted(folders - present) + loose
    assert not problems, (
        "armarius.spec's DATA_FOLDERS doesn't match data/ (or data/ holds a "
        f"file that isn't .json): {problems}"
    )


def test_the_terminal_program_runs_every_word_hosting_asks_for() -> None:
    assert set(main.WORDS) == set(launch.WORDS)


def test_from_a_checkout_each_word_is_a_python_command() -> None:
    host = launch.command(launch.HOST, "--port", "8001")
    assert host[1:] == ["-m", "ars_magica_manager.tui.serve", "--port", "8001"]
    assert Path(launch.command(launch.PLAY)[1]).name == "main.py"


def test_in_a_build_each_word_runs_the_terminal_program(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(launch, "FROZEN", True)
    monkeypatch.setattr(launch.sys, "executable", str(Path("app") / "Armarius.exe"))
    assert launch.command(launch.SEATS, "--saga", "s1") == [
        str(Path("app") / "armarius-terminal.exe"),
        "seats",
        "--saga",
        "s1",
    ]
