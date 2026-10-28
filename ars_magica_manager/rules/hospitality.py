"""Hospitality: a magus staying as a guest at another covenant.

The Definitive Edition expects magi to host visiting magi, even uninvited
(DE p. 518), and calls a magus copying from a library he doesn't belong
to scribal hospitality, offered for a payment or a service (DE p. 381).
Covenants adds that guests count their stays in seasons and are charged
for their materials (pp. 96-98). None of these sets a fee or a length of
stay: the troupe agrees the terms.

The Rhine Tribunal's Peripheral Code does (Guardians of the Forests p.
20): a guest is guaranteed at least three years and at most seven, and
pays three pawns of vis a year, or a season's service in its place; the
host need not give him a laboratory. Those are the terms a Rhine host's
stay starts from.

House Jerbiton's code of courtesy between guest and host (Houses of
Hermes: Societates p. 51) is etiquette, with no figures, so it is in the
help only.

"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import FEE_SERVICE, FEE_VIS, Character, GuestStay

SOURCE = (
    "Ars Magica Definitive Edition pp. 381, 518; Covenants pp. 96-98; "
    "Guardians of the Forests p. 20; Houses of Hermes: Societates p. 51"
)


@dataclass(frozen=True)
class Terms:
    """A host's usual conditions of hospitality: the yearly fee, how long
    a stay lasts at the least and the most (None: no rule), and whether a
    laboratory comes with it."""

    fee_kind: str
    fee: int
    shortest: int | None
    longest: int | None
    laboratory: bool
    source: str


#: The Rhine's Peripheral Code (Guardians of the Forests p. 20); a
#: season's service a year may stand in for the vis.
RHINE_TERMS = Terms(FEE_VIS, 3, 3, 7, False, "Guardians of the Forests p. 20")


def guest_at(character: Character, covenant_id: str | None) -> bool:
    """Whether the character is staying as a guest at that covenant."""
    stay = character.stay
    return stay is not None and bool(covenant_id) and stay.host_id == covenant_id


def reads_at(character: Character, covenant_id: str | None) -> bool:
    """Whether the character may study and copy from that covenant's
    library as its guest (scribal hospitality, DE p. 381)."""
    stay = character.stay
    return guest_at(character, covenant_id) and stay is not None and stay.library


def length_problem(
    terms: Terms | None, year: int | None, until: int | None
) -> str | None:
    """Why a stay from `year` to the end of `until` breaks the host's
    rule on its length, or None."""
    if terms is None or year is None or until is None:
        return None
    years = until - year + 1
    if years < 1:
        return "The stay must end in or after the year it began."
    if terms.shortest is not None and years < terms.shortest:
        return (
            f"The host's terms guarantee at least {terms.shortest} years "
            f"({terms.source})."
        )
    if terms.longest is not None and years > terms.longest:
        return f"The host's terms allow at most {terms.longest} years ({terms.source})."
    return None


def due(stay: GuestStay, year: int) -> bool:
    """Whether the year's fee is still owed: a fee is asked, the stay ran
    in that year, and it isn't paid."""
    if stay.fee <= 0 or year in stay.paid:
        return False
    if stay.year is not None and year < stay.year:
        return False
    return stay.until_year is None or year <= stay.until_year


def fee_words(stay: GuestStay) -> str:
    """The yearly fee in words: "3 pawns of vis a year"."""
    if stay.fee <= 0:
        return "No fee"
    plural = "" if stay.fee == 1 else "s"
    if stay.fee_kind == FEE_VIS:
        return f"{stay.fee} pawn{plural} of vis a year"
    if stay.fee_kind == FEE_SERVICE:
        return f"{stay.fee} season{plural} of service a year"
    return f"{stay.fee} pound{plural} of silver a year"
