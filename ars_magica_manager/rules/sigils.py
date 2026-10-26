"""Who holds a Tremere magus's voting sigil (DE p. 16).

A Tremere parens holds his filius's voting sigil until the filius beats him
in certamen or the parens dies. A parens who doesn't hold his own sigil
can't hold his filius's: it passes up the line of parentes to the first who
holds his own. A magus records whether he has won his sigil back
(`HermeticBackground.holds_own_sigil`); one with no parens recorded holds
his own, and a parens who isn't one of the saga's characters holds it.

Promotion by Force (HoH: True Lineages pp. 123-125), below, is how a
Tremere claims his sigil, or a higher role, by certamen.
"""

from __future__ import annotations

from dataclasses import dataclass

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
    _, when = sigil_challenge(magus, saga.current_year)
    return (
        f"Voting sigil: held by {name}, until he beats his parens in certamen "
        f"or the parens dies (DE p. 16). {when}"
    )


# -- Promotion by Force (HoH: True Lineages pp. 123-125) ----------------------
#
# A Tremere may rise by the House's political path or claim his due by
# certamen, which the House accepts except in an emergency. Vis is not used
# in duels between Tremere (p. 123), nor in duels "for love" (p. 134); the
# Definitive Edition lets any duelist spend vis (DE p. 233), so this is the
# House's custom, not a rule of certamen.

PROMOTION_SOURCE = "Houses of Hermes: True Lineages, Promotion by Force, pp. 123-125"
#: The House's Decennials: its council meets every ten years (p. 118); the
#: last was two years before 1220 (p. 122).
DECENNIAL_EVERY, DECENNIAL_YEAR = 10, 1218


@dataclass(frozen=True)
class Promotion:
    """One step a Tremere may claim by certamen."""

    role: str
    claim: str
    challenge: str
    page: int


PROMOTIONS: tuple[Promotion, ...] = (
    Promotion(
        "Magus",
        "Claiming the Name",
        "The Gauntlet is the apprentice's certamen against his master, when "
        "the master or his superiors choose; the most senior Tremere present "
        "judges whether he graduates. An apprentice who wins (all but unheard "
        "of) holds his own sigil at once; one who loses graduates with a new "
        "name.",
        123,
    ),
    Promotion(
        "Experienced magus",
        "Claiming the Sigil",
        "He may challenge his parens for his sigil once, when he chooses, "
        "then at every Decennial of the House; the parens returns it when "
        "beaten, or at death.",
        123,
    ),
    Promotion(
        "Exarch",
        "Claiming the Dragon Banner",
        "Any Tremere may challenge an exarch over his policies or for his "
        "office, the exarch or an ally answering; a magus may challenge for "
        "the office only once, never while the House faces rivals (at "
        "Tribunal, say), and a beaten exarch may not challenge to regain it. "
        "The Primus may still refuse the victor.",
        124,
    ),
    Promotion(
        "Primus",
        "Claiming the Sigil of Tremere",
        "At each Decennial the conciliarii duel to be secutor, who may "
        "challenge the Primus at any time until the next, as may anyone who "
        "beats the secutor, once for each victory.",
        125,
    ),
)


def decennial(year: int) -> bool:
    """Whether House Tremere meets in its Decennial this year."""
    return (year - DECENNIAL_YEAR) % DECENNIAL_EVERY == 0


def next_decennial(year: int) -> int:
    """The year of the House's next Decennial, this year's included."""
    return year + (DECENNIAL_YEAR - year) % DECENNIAL_EVERY


def sigil_challenge(magus: Character, year: int) -> tuple[bool, str]:
    """Whether a Tremere whose parens holds his sigil may challenge for it
    this year, and the sheet's line saying so: his one challenge at a time
    of his choosing, then only at a Decennial (HoH: TL p. 123)."""
    if magus.hermetic.house != TREMERE or magus.hermetic.holds_own_sigil:
        return False, ""
    if not magus.hermetic.sigil_challenged:
        return True, "He may challenge for it when he chooses (HoH: TL p. 123)."
    if decennial(year):
        return True, "He may challenge for it at this year's Decennial."
    return False, (
        f"His next challenge for it waits for the Decennial of "
        f"{next_decennial(year)} (HoH: TL p. 123)."
    )


def challenge_for_sigil(magus: Character, year: int, *, won: bool) -> None:
    """Record a challenge for his sigil: won, he holds his own; either way
    his free challenge is spent. ValueError when he may not challenge."""
    may, why = sigil_challenge(magus, year)
    if not may:
        raise ValueError(why or f"{magus.name} has no sigil to claim")
    magus.hermetic.sigil_challenged = True
    if won:
        magus.hermetic.holds_own_sigil = True


def may_challenge_exarch(
    *, challenged_before: bool, house_faces_rivals: bool, deposed_exarch: bool
) -> bool:
    """Whether a Tremere may challenge an exarch for his office: once in a
    lifetime, never while the House faces rivals, and not to win back an
    office he lost (HoH: TL p. 124)."""
    return not (challenged_before or house_faces_rivals or deposed_exarch)


def vis_honourable(challenger: Character, defender: Character) -> bool:
    """Whether a duelist may spend vis without dishonour: never in a duel
    between two Tremere (HoH: TL p. 123)."""
    return not (
        challenger.hermetic.house == TREMERE and defender.hermetic.house == TREMERE
    )
