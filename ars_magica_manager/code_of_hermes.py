"""The Code of Hermes's crimes as the Traditionalists read them (Houses of
Hermes: True Lineages, The Code of Hermes, pp. 45-61).

A clear breach of the Oath is a high crime, and only a high crime lets the
prosecution call for a Wizard's March; every other offence is a low crime
(an assault short of the life or magic, a broken contract, perjury,
deceiving or not helping a Quaesitor...), whose penalty is set by the
Presiding Quaesitor. A magus who refuses the penalty, three times, is
Marched, since failing to abide by the Tribunal is itself a high crime.

Penalties are damages to the victim, fines (a third to the prosecutor,
two thirds to the Tribunal's coffers) and punishments, in rising
severity: seasons of service, investing items, loss of an apprentice,
banishment from the Tribunal, loss of a familiar, death of a familiar.
They are paid by the next Tribunal (ruling_templates holds a template for
each). In a Wizard's March the victim takes a quarter of the outcast's
estate, the prosecutor a quarter and the heir the rest; the Tribunal's
coffers nothing. The March itself (the hunt) is not worked out here."""

from __future__ import annotations

from typing import NamedTuple

SOURCE = "Houses of Hermes: True Lineages, The Code of Hermes, pp. 45-61"


class Crime(NamedTuple):
    name: str
    #: Lower-case words in a charge that name it.
    words: tuple[str, ...]
    #: For a house only: "Bonisagus", or "not Bonisagus".
    house: str = ""


#: The high crimes (p. 46), the House's own first so their words are
#: matched before the general ones.
HIGH_CRIMES: tuple[Crime, ...] = (
    Crime(
        "Failure to Respect the Rights of Bonisagus",
        ("rights of bonisagus",),
        "not Bonisagus",
    ),
    Crime("Failure to Share Knowledge", ("share knowledge",), "Bonisagus"),
    Crime("Deprivation of Magical Power", ("depriv",)),
    Crime("Slaying a Magus", ("slay", "slew", "killing", "murder")),
    Crime(
        "Failure to Abide by Tribunal Decisions",
        ("abide", "refus", "defy", "defied"),
    ),
    Crime("Abuse of Voting Rights", ("vote", "voting", "sigil", "proxy")),
    Crime("Endangering the Order", ("endanger",)),
    Crime("Interfering with Mundanes", ("mundane",)),
    Crime("Dealing with Devils", ("devil", "demon", "infernal", "diabol")),
    Crime("Molesting the Fay", ("fay", "faerie", "molest")),
    Crime("Scrying on Members of the Order", ("scry", "spying", "spied")),
    Crime(
        "Failure to Perform the Duties of a Parens",
        ("parens", "filius", "outcast"),
    ),
    Crime("Attacking an Ally of the Order", ("ally", "allies")),
    Crime("Aiding an Enemy of the Order", ("enemy", "enemies")),
)

#: The punishments, least first (pp. 60-61).
PUNISHMENTS: tuple[str, ...] = (
    "Seasons of service",
    "Investing items",
    "Loss of an apprentice",
    "Banishment from the Tribunal",
    "Loss of a familiar",
    "Death of a familiar",
)
#: Fines: the prosecutor's share; the rest goes to the Tribunal's coffers.
FINE_TO_PROSECUTOR = 1 / 3
#: Times a convicted magus may refuse a lesser penalty before the Quaesitor
#: declares him Marched.
REFUSALS = 3
#: A March's estate: the victim's, the prosecutor's and the heir's shares.
MARCH_SHARES = {"victim": 1 / 4, "prosecutor": 1 / 4, "heir": 1 / 2}
#: Notice of a charge is due this many months before the Tribunal.
NOTICE_MONTHS = 3


def high_crime(charge: str) -> Crime | None:
    """The high crime a charge's words name, or None (a low crime, or a
    charge the words don't place)."""
    words = charge.casefold()
    return next((c for c in HIGH_CRIMES if any(w in words for w in c.words)), None)


def fine_shares(amount: int) -> tuple[int, int]:
    """A fine split: the prosecutor's third (rounded down) and the
    Tribunal's coffers' rest."""
    prosecutor = int(amount * FINE_TO_PROSECUTOR)
    return prosecutor, amount - prosecutor


def crime_note(charge: str) -> str:
    """What the charge is under the Code, for the case's details."""
    if not charge.strip():
        return ""
    found = high_crime(charge)
    if found is None:
        return (
            "A low crime unless it breaches the Oath: no Wizard's March, unless "
            f"the penalty is refused {REFUSALS} times (HoH: True Lineages p. 46)."
        )
    only = f" ({found.house} only)" if found.house else ""
    return (
        f"A high crime, {found.name}{only}: on conviction the prosecution may "
        "call for a Wizard's March (HoH: True Lineages p. 46)."
    )
