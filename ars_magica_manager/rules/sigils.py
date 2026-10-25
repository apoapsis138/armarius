"""Who holds a Tremere magus's voting sigil (DE p. 16).

A Tremere parens holds his filius's voting sigil until the filius beats him
in certamen or the parens dies. A parens who doesn't hold his own sigil
can't hold his filius's: it passes up the line of parentes to the first who
holds his own. A magus records whether he has won his sigil back
(`HermeticBackground.holds_own_sigil`); one with no parens recorded holds
his own, and a parens who isn't one of the saga's characters holds it.
"""

from __future__ import annotations

from ..models import Character, Saga

SOURCE = "Ars Magica Definitive Edition, House Tremere, p. 16"
TREMERE = "house_tremere"
#: How far up the line of parentes to look (a loop in the records stops).
MAX_GENERATIONS = 50


def _parens(saga: Saga, magus: Character) -> Character | None:
    name = magus.hermetic.parens.strip()
    if not name:
        return None
    return next(
        (c for c in saga.characters if c.type == "magus" and c.name == name), None
    )


def _holds_own(saga: Saga, magus: Character) -> bool:
    """Whether the magus holds his own sigil: not Tremere, won back, no
    parens recorded, or a parens of the saga's who has died."""
    if magus.hermetic.house != TREMERE or magus.hermetic.holds_own_sigil:
        return True
    parens = _parens(saga, magus)
    if not magus.hermetic.parens.strip():
        return True
    return parens is not None and parens.wounds.dead


def sigil_holder(saga: Saga, magus: Character) -> tuple[str, Character | None]:
    """Who holds a Tremere magus's voting sigil: ("", None) when he holds
    his own (or isn't Tremere), else the holder's name and character (None
    for a parens the saga doesn't have)."""
    if magus.type != "magus" or _holds_own(saga, magus):
        return "", None
    name, holder = magus.hermetic.parens.strip(), _parens(saga, magus)
    for _ in range(MAX_GENERATIONS):
        if holder is None or _holds_own(saga, holder):
            break
        name, holder = holder.hermetic.parens.strip(), _parens(saga, holder)
    return name, holder


def sigil_text(saga: Saga, magus: Character) -> str:
    """The sheet's line on a Tremere magus's voting sigil ("" for anyone
    else)."""
    if magus.hermetic.house != TREMERE or magus.type != "magus":
        return ""
    name, _ = sigil_holder(saga, magus)
    if not name:
        return "Voting sigil: his own."
    return (
        f"Voting sigil: held by {name}, until he beats his parens in certamen "
        "or the parens dies (DE p. 16)."
    )
