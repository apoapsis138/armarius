"""No module reads data with pickle, marshal or shelve.

Each of them runs code hidden in the bytes it reads, so a saga, pack or
export that came from someone else could take over the computer. Data
comes in as JSON, checked by shapes.py; this keeps it that way.

One module may use pickle to copy a saga in memory (`IN_MEMORY`): the
bytes it reads are the ones it has just made, never a file's. Even there,
reading from a file (`pickle.load`, `Unpickler`) is refused.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: Modules that load code from the data they read.
UNSAFE = frozenset({"pickle", "cPickle", "_pickle", "marshal", "shelve", "dill"})
#: Modules that may pickle in memory, and why.
IN_MEMORY = {
    "ars_magica_manager/seasons/projection.py": (
        "copies the saga to play seasons forward; its bytes never leave the process"
    ),
}
#: What reads pickled bytes from a file: never allowed.
FROM_A_FILE = frozenset({"load", "Unpickler"})


def _problems(path: Path, in_memory: bool = False) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "pickle"
            and node.attr in FROM_A_FILE
        ):
            found.append(f"pickle.{node.attr}")
            continue
        else:
            continue
        found += [
            n
            for n in names
            if n.split(".")[0] in UNSAFE and not (in_memory and n == "pickle")
        ]
    return found


def _sources() -> list[Path]:
    return [
        *(ROOT / "ars_magica_manager").rglob("*.py"),
        *(ROOT / "tools").rglob("*.py"),
        ROOT / "main.py",
    ]


def test_no_module_reads_data_with_pickle() -> None:
    offenders = []
    for path in _sources():
        name = path.relative_to(ROOT).as_posix()
        if names := _problems(path, in_memory=name in IN_MEMORY):
            offenders.append(f"{name}: {', '.join(names)}")
    assert not offenders, (
        "These use a module that runs code from the data it reads: "
        + "; ".join(offenders)
    )


def test_each_in_memory_use_is_still_there() -> None:
    """An entry whose module stopped pickling is dropped from IN_MEMORY."""
    stale = [name for name in IN_MEMORY if not _problems(ROOT / name)]
    assert not stale, f"No longer pickle: {stale}"


def test_the_check_finds_each_kind(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text(
        "import os\nimport pickle\nfrom shelve import open\n"
        "pickle.loads(b'')\npickle.load(f)\n"
    )
    assert _problems(sample) == ["pickle", "shelve", "pickle.load"]
    assert _problems(sample, in_memory=True) == ["shelve", "pickle.load"]
