"""`# type: ignore` hides an error from pyright. The few left each carry a
reason; a new one is a deliberate change to this list, not a convenience."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"

#: The ignores kept, as "path:count": Qt's stub asks for a QGraphicsEffect
#: where setGraphicsEffect(None) removes one.
ALLOWED = {"gui/title.py": 1}


def test_type_ignores_are_only_the_listed_ones():
    found: dict[str, int] = {}
    for path in ROOT.rglob("*.py"):
        count = len(re.findall(r"#\s*type:\s*ignore", path.read_text("utf-8")))
        if count:
            found[path.relative_to(ROOT).as_posix()] = count
    assert found == ALLOWED, f"type: ignore found {found}, allowed {ALLOWED}"
