"""One dice line for every roll the app makes (STORY-2348): the die, each
stress doubling, the botch dice, the modifiers, the total and any Ease
Factor, in the words the Chronicle card uses. The Chronicle, its desktop
pane and terminal, Diary lines, reports and every rolling form's result
call it, so a roll reads the same wherever it shows.

    Stress die 1, 1, 5 → 5 × 4 = 20, Characteristic + Ability +9 = 29

The rules are the Definitive Edition's (Die Rolls, pp. 7-8; rules.dice):
a stress die's 1 re-rolls and doubles, a re-rolled 0 reads as 10, and a
first 0 rolls the botch dice.

Pattern: none; a plain function each module calls (a Template Method in
name, which in Python is just this function).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .rules.dice import DieResult

#: A modifier's name and amount ("Dexterity", 2).
Term = tuple[str, int]


def signed(amount: int) -> str:
    """+3, +0, −2 (a true minus sign)."""
    return f"+{amount}" if amount >= 0 else f"−{abs(amount)}"


def _zeros(count: int) -> str:
    if count == 0:
        return "no zeros"
    return f"{count} zero{'s' if count > 1 else ''}"


def _botch_dice(die: DieResult) -> str:
    """The botch dice and what came of them: "2 botch dice 0, 4: botch,
    1 zero"; "" when none were rolled."""
    if not die.botch_faces:
        return ""
    count = len(die.botch_faces)
    shown = ", ".join(str(face) for face in die.botch_faces)
    said = _zeros(die.botches)
    if die.botches and die.faces:  # a stress die's botch, not a lone roll
        said = f"botch, {said}"
    return f"{count} botch {'die' if count == 1 else 'dice'} {shown}: {said}"


def doubled(die: DieResult) -> str:
    """A die's value with its doubling worked out: "5 × 4 = 20"; just
    the value when it didn't double."""
    if not die.doublings:
        return str(die.value)
    last = die.faces[-1] or 10
    return f"{last} × {2**die.doublings} = {die.value}"


def _die(die: DieResult) -> str:
    """The die alone, without its botch dice."""
    if not die.stress:
        return f"Simple die {die.value}"
    if not die.doublings:
        return f"Stress die {die.value}"
    thrown = ", ".join(
        str(face if i == 0 or face else 10) for i, face in enumerate(die.faces)
    )
    return f"Stress die {thrown} → {doubled(die)}"


def die_text(die: DieResult) -> str:
    """A die and its botch dice, with no modifiers: "Stress die 1, 1, 5
    → 5 × 4 = 20"; "Stress die 0; 1 botch die 7: no zeros"; a lone roll
    of botch dice (an unsafe laboratory's) as "3 botch dice 4, 0, 9:
    1 zero"."""
    if not die.faces:
        return _botch_dice(die)
    botch = _botch_dice(die)
    return f"{_die(die)}; {botch}" if botch else _die(die)


def terms_text(terms: Sequence[Term]) -> str:
    """A roll's terms ("Dexterity +2, Athletics +3, Wounds −1"); a Free
    roll's lone modifier as its amount ("+3")."""
    if len(terms) == 1 and terms[0][0] == "Modifier":
        return signed(terms[0][1])
    return ", ".join(f"{label} {signed(amount)}" for label, amount in terms)


#: A die as a roll has it: rolled (`DieResult`), or typed in by hand.
RolledOrTyped = DieResult | int


def value_of(die: RolledOrTyped) -> int:
    """What the die adds to the roll."""
    return die if isinstance(die, int) else die.value


def dice_line(
    die: RolledOrTyped,
    terms: Sequence[Term],
    total: int,
    ease_factor: int | None = None,
) -> str:
    """A whole roll as a line: the die (each doubling worked out; a typed
    die as typed), the terms, the total, against the Ease Factor what came
    of it, and the botch dice last. A botched total is the book's: no
    higher than 0."""
    rolled = die if isinstance(die, DieResult) else None
    botched = rolled is not None and rolled.botched
    line = _die(rolled) if rolled is not None else f"Die {die} (typed)"
    if terms:
        line += f", {terms_text(terms)}"
    if terms or botched:
        line += f" = {total}"
    if ease_factor is not None:
        margin = total - ease_factor
        if not botched and margin >= 0:
            line += f" vs {ease_factor}: succeeds by {margin}"
        else:
            line += f" vs {ease_factor}: fails by {abs(margin)}"
    botch = _botch_dice(rolled) if rolled is not None else ""
    return f"{line}; {botch}" if botch else line


def already_said(lines: Sequence[str], said: str) -> bool:
    """Whether `lines` already say every part of the dice line `said` (a
    roll that writes its own dice line needs no second)."""
    text = "\n".join(lines)
    return all(part in text for part in said.split("; "))


def _numbers(kept: Mapping[str, Any], key: str) -> tuple[int, ...]:
    """The whole numbers kept under `key` (read from a file: anything
    else is left out)."""
    found = kept.get(key)
    if not isinstance(found, list):
        return ()
    return tuple(n for n in found if isinstance(n, int) and not isinstance(n, bool))


def whole_die(kept: Mapping[str, Any]) -> DieResult:
    """A whole die as a form roll's entry keeps it (recorded_dice.Die:
    stress, faces, botch_faces), with its value worked out again by the
    book's rules (rules.dice; DE p. 7). A missing or odd field reads as
    empty."""
    faces = _numbers(kept, "faces")
    botch_faces = _numbers(kept, "botch_faces")
    stress = kept.get("stress") is True
    if not faces:
        value = 0
    elif not stress:
        value = faces[0] or 10
    elif len(faces) == 1:
        value = faces[0]
    else:
        value = (faces[-1] or 10) * 2 ** (len(faces) - 1)
    return DieResult(value=value, faces=faces, stress=stress, botch_faces=botch_faces)


def whole_dice_text(kept: Sequence[Mapping[str, Any]]) -> str:
    """The whole dice among `kept` (faces drawn outside the die helpers
    left to the roll's own words), as a result's last line says them;
    "" when there are none."""
    wholes = [die for die in kept if "face" not in die]
    return dice_text(wholes) if wholes else ""


def dice_text(kept: Sequence[Mapping[str, Any]]) -> str:
    """A form roll's dice as its entry keeps them: each whole die as
    `die_text` says it, and faces drawn outside the die helpers together
    ("other dice 12 4"; "dice 3 7" when there are only those)."""
    said: list[str] = []
    loose: list[str] = []
    wholes = any("face" not in die for die in kept)
    for die in kept:
        if "face" in die:
            face = die["face"]
            if isinstance(face, int) and not isinstance(face, bool):
                loose.append(str(face))
            continue
        if loose:
            said.append(f"other dice {' '.join(loose)}")
            loose = []
        said.append(die_text(whole_die(die)))
    if loose:
        said.append(f"{'other dice' if wholes else 'dice'} {' '.join(loose)}")
    return "; ".join(said)
