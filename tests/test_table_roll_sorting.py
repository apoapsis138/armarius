"""Every module that rolls is sorted into Table rolls, not Table rolls, or
the fights left to their own story (table_rolls.TABLE, NOT_TABLE,
FIGHTS; the glossary's Table roll), so a new rolling form must be sorted
before it ships. A Table roll module takes the Session's die source and
hands its forms to table_rolls.form (or rolls in table_rolls.drawing, for
a roll made outside a form)."""

from __future__ import annotations

import re
from pathlib import Path

from ars_magica_manager import table_rolls

PACKAGE = Path(table_rolls.__file__).parent
#: Where the dice are rolled for the Chronicle itself, the recording die
#: source, and the front-ends'
#: own drawing (a picture's jitter), which roll nothing for the rules.
LEFT_OUT = {"chronicle", "recorded_dice", "table_rolls"}
BUILDS_A_SOURCE = re.compile(
    r"random\.Random\(|SystemRandom\(|table_rolls\.(dice|drawing)\("
)


def _name(path: Path) -> str:
    return ".".join(path.relative_to(PACKAGE).with_suffix("").parts)


def _rolling() -> dict[str, str]:
    """Each core module that builds a source of chance, with its text."""
    found: dict[str, str] = {}
    for path in sorted(PACKAGE.rglob("*.py")):
        name = _name(path)
        if name.split(".")[0] in ("gui", "tui") or name in LEFT_OUT:
            continue
        text = path.read_text(encoding="utf-8")
        if BUILDS_A_SOURCE.search(text):
            found[name] = text
    return found


def test_every_rolling_module_is_sorted_once() -> None:
    lists = {
        "TABLE": table_rolls.TABLE,
        "NOT_TABLE": table_rolls.NOT_TABLE,
        "FIGHTS": table_rolls.FIGHTS,
    }
    problems: list[str] = []
    for name in _rolling():
        holders = [label for label, held in lists.items() if name in held]
        if len(holders) != 1:
            problems.append(f"{name}: in {holders or 'none of the lists'}")
    assert not problems, "Sort each rolling module once:\n" + "\n".join(problems)


def test_the_lists_name_only_modules_that_roll() -> None:
    rolling = _rolling()
    named = table_rolls.TABLE | table_rolls.NOT_TABLE | table_rolls.FIGHTS

    stale = sorted(name for name in named if name not in rolling)

    assert not stale, f"These no longer roll: {stale}"


def test_a_table_roll_module_takes_the_sessions_dice_and_posts() -> None:
    rolling = _rolling()
    problems: list[str] = []
    for name in sorted(table_rolls.TABLE):
        text = rolling.get(name, "")
        drawn = "table_rolls.drawing(" in text
        if "table_rolls.dice(" not in text and not drawn:
            problems.append(f"{name}: builds its own source of chance")
        if "table_rolls.form(" not in text and not drawn:
            problems.append(f"{name}: its rolls never reach the Chronicle")
    assert not problems, "\n".join(problems)


def test_a_module_that_never_posts_takes_no_table_dice() -> None:
    rolling = _rolling()
    others = table_rolls.NOT_TABLE | table_rolls.FIGHTS

    found = sorted(n for n in others if "table_rolls." in rolling.get(n, ""))

    assert not found, f"Not Table rolls, but using table_rolls: {found}"
