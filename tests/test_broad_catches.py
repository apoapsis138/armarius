"""No new `except` that catches TypeError or AttributeError.

Those are what a renamed field or a wrong argument raise, so catching them
turns a bug into a silent no-op (CLAUDE.md, "Catch only the error you
expect"). Data from outside (a file, another computer) should be checked
for shape where it comes in, and refused with a ValueError naming the
field; STORY-2223 brings that check for the Remote seat and import paths.

KNOWN lists the catches that were there when this test came (by file and
function, so moving lines doesn't matter). Remove an entry when its catch
goes; never add one without saying why beside it.
"""

from __future__ import annotations

import ast
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"
BROAD = {"TypeError", "AttributeError"}

KNOWN = {
    # Untrusted data from another computer turned into models: until the
    # shape check (STORY-2223).
    "remote/client.py::RemoteClient.read_saga",
    "seat_changes.py::apply_change",
    # Files read from disk: the shape check is to cover these too.
    "remote/audit.py::AuditLog.entries",
    "remote/devices.py::DeviceBook._load",
    "remote/invites.py::InviteBook._load",
    "remote/passcodes.py::RemotePasscodes._load",
    "storage.py::reload_into",
    "storage.py::_normalized",
    "title_page.py::_saga_name",
    "forms/importing.py::_import_pack",
    "forms/importing.py::_import_record",
    "forms/importing.py::update_record",
    # Numbers typed or saved that may be None or text.
    "hosting.py::last_plan",
    "forms/ships.py::_float",
    "forms/ships.py::_int",
    "rules/sites.py::whole_number",
}


@cache
def _catches() -> frozenset[str]:
    found: set[str] = set()
    for path in sorted(ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        where = path.relative_to(ROOT).as_posix()
        for scope in ast.walk(tree):
            if not isinstance(scope, ast.ClassDef | ast.Module):
                continue
            for node in scope.body:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    _in_function(node, where, scope, found)
    return frozenset(found)


def _in_function(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    where: str,
    scope: ast.ClassDef | ast.Module,
    found: set[str],
) -> None:
    name = function.name
    if isinstance(scope, ast.ClassDef):
        name = f"{scope.name}.{name}"
    for node in ast.walk(function):
        if isinstance(node, ast.ExceptHandler) and node.type is not None:
            caught = node.type.elts if isinstance(node.type, ast.Tuple) else [node.type]
            if any(isinstance(c, ast.Name) and c.id in BROAD for c in caught):
                found.add(f"{where}::{name}")


def test_no_new_catch_of_type_or_attribute_errors():
    found = _catches()
    new = sorted(found - KNOWN)
    assert not new, (
        "catches TypeError or AttributeError (check the data's shape where it "
        "comes in instead, CLAUDE.md): " + "; ".join(new)
    )


def test_every_known_catch_is_still_there():
    gone = sorted(KNOWN - _catches())
    assert not gone, f"no longer there, so take out of KNOWN: {'; '.join(gone)}"
