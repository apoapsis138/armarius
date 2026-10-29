"""A function that grows past a limit is hard to read and to test. This
measures every function outside the Tribunal packs (long data, not logic) and
fails when a new one passes a limit. The functions already past one are
listed in `KNOWN`; splitting one removes its entry, and the test also fails
for an entry that no longer needs to be there.

Lines are from `def` to the last line. Branches count each if, conditional
expression, loop, except clause, match case and boolean operator, so a long
flat list of fields is not caught for its length alone: length counts
only in a function with at least `LONG_NEEDS` branches."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "ars_magica_manager"
SKIPPED = ("book_packs",)
MAX_LINES = 120
MAX_BRANCHES = 30
MAX_PARAMS = 12
LONG_NEEDS = 8

KNOWN: set[str] = {
    "bestiary_book.py::build",
    "books.py::_book_from_row",
    "casting_text.py::known_spell_casting_lines",
    "economics.py::summarize",
    "fights.py::_magic_fields",
    "forms/acclaim.py::acclaim_fields",
    "forms/lab_plan.py::LabPlanForm._common_fields",
    "forms/lab_plan.py::LabPlanForm._design_fields",
    "forms/scholar_seasons.py::_artwork_fields",
    "forms/season.py::_supplement_plan_values",
    "forms/season.py::study_fields",
    "gui/character_sheet.py::CharacterSheet._description",
    "gui/pages.py::SagaPage.__init__",
    "meeting.py::Hearing.fields",
    "normandy_meeting.py::Library.fields",
    "rules/book_seasons.py::_copy",
    "rules/casting.py::botch_dice",
    "rules/casting.py::casting_score",
    "rules/casting_virtues.py::reminders",
    "rules/creation_later.py::later_life_checks",
    "rules/enchant_seasons.py::_effect_work",
    "rules/familiar_seasons.py::work",
    "rules/fight.py::odds",
    "rules/lab.py::lab_total",
    "rules/lab_seasons.py::_one_season_work",
    "rules/lab_seasons.py::_with_options",
}

_BRANCHES = (
    ast.If,
    ast.IfExp,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.ExceptHandler,
    ast.match_case,
    ast.BoolOp,
)


def _params(function: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    args = function.args
    names = [*args.posonlyargs, *args.args, *args.kwonlyargs]
    names += [a for a in (args.vararg, args.kwarg) if a is not None]
    return len([a for a in names if a.arg not in ("self", "cls")])


def _own_nodes(function: ast.FunctionDef | ast.AsyncFunctionDef):
    """The nodes of a function without those of the functions nested in it
    (each nested function is measured on its own)."""
    stack = list(ast.iter_child_nodes(function))
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack.extend(ast.iter_child_nodes(node))


def _problems(path: Path) -> dict[str, str]:
    """Each function past a limit, by `module::qualified name`."""
    found: dict[str, str] = {}
    rel = path.relative_to(ROOT).as_posix()

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                lines = (child.end_lineno or child.lineno) - child.lineno + 1
                branches = sum(isinstance(n, _BRANCHES) for n in _own_nodes(child))
                params = _params(child)
                over = []
                if lines > MAX_LINES and branches >= LONG_NEEDS:
                    over.append(f"{lines} lines")
                if branches > MAX_BRANCHES:
                    over.append(f"{branches} branches")
                if params > MAX_PARAMS:
                    over.append(f"{params} parameters")
                if over:
                    found[f"{rel}::{name}"] = ", ".join(over)
                walk(child, name + ".")
            elif isinstance(child, ast.ClassDef):
                walk(child, prefix + child.name + ".")
            else:
                walk(child, prefix)

    walk(ast.parse(path.read_text("utf-8")), "")
    return found


def _all_problems() -> dict[str, str]:
    found: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*.py")):
        if any(part in SKIPPED for part in path.relative_to(ROOT).parts):
            continue
        found.update(_problems(path))
    return found


def test_no_new_function_past_the_limits():
    found = _all_problems()
    new = [f"{key} ({why})" for key, why in found.items() if key not in KNOWN]
    assert not new, (
        f"function past {MAX_LINES} lines (with {LONG_NEEDS}+ branches), "
        f"{MAX_BRANCHES} branches or {MAX_PARAMS} parameters (split it): "
        + "; ".join(new)
    )


def test_known_list_has_no_stale_entries():
    found = _all_problems()
    stale = sorted(KNOWN - set(found))
    assert not stale, "remove from KNOWN, now within the limits: " + ", ".join(stale)
