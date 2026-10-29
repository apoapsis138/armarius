"""An import inside a function hides a cycle: the module that needs another
and is imported by it. The shared code goes into a lower module instead. A
function-level import of the app's own modules stays only with a
`# start-up:` or `# cycle:` comment above it saying why."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"
MARKERS = ("# start-up:", "# cycle:")


def _lazy_imports(path: Path) -> list[int]:
    """Line numbers of the app's own modules imported inside a function."""
    source = path.read_text("utf-8")
    found: set[int] = set()
    for function in ast.walk(ast.parse(source)):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(function):
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                found.add(node.lineno)
    return sorted(found)


def _explained(path: Path, lineno: int) -> bool:
    """A marker comment on the import's line, or in the lines just above it
    (or above the run of imports it belongs to)."""
    lines = path.read_text("utf-8").splitlines()
    index = lineno - 1
    while index > 0 and lines[index - 1].lstrip().startswith(("from ", "import ")):
        index -= 1
    nearby = lines[max(0, index - 3) : lineno]
    return any(marker in line for line in nearby for marker in MARKERS)


def test_function_level_imports_say_why():
    unexplained = [
        f"{path.relative_to(ROOT).as_posix()}:{lineno}"
        for path in sorted(ROOT.rglob("*.py"))
        for lineno in _lazy_imports(path)
        if not _explained(path, lineno)
    ]
    assert not unexplained, (
        "import inside a function without a '# start-up:' or '# cycle:' "
        "comment (move the shared code down instead): " + ", ".join(unexplained)
    )
