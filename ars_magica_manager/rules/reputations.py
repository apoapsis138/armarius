"""Reputations: one way of reading them, for every rule that does.

- A Reputation has a score, what it is for, and a type (Local,
  Ecclesiastical, Hermetic, and the supplements' Academic and Noble) that
  says who may have heard of it: a stress die + the score against 0 in the
  same village, parish or covenant, 6 in the same town, diocese or
  Tribunal, 9 in the county, province or whole Order, 12 in the country or
  the whole Church (DE pp. 28-29).
- A noteworthy deed before witnesses who talk starts a Reputation at 1;
  each later one is an experience point in it, as for an Ability (DE p.
  386).
- Good or bad is the troupe's call (the books label Reputations "Good" or
  "Bad", DE p. 28 gives only score, content and type): the app reads a
  negative score as bad and a positive one as good. A covenant loses five
  Loyalty points per point of each bad Reputation its covenfolk know of,
  of any type, and gains five per point of a good local one (Covenants p.
  40).
- A university exam adds the Good Academic Reputations and takes off the
  Bad ones; the candidate needs a net Good Academic Reputation of 1, 2 or
  3 for the baccalaureus, magister or doctor (Art & Academe p. 100).
"""

from __future__ import annotations

from collections.abc import Iterable

from ..models import ScoredTrait

SOURCE = (
    "Ars Magica Definitive Edition, Reputations, pp. 28-29, and Changing "
    "Reputations, p. 386; Covenants, Reputation, p. 40; Art & Academe, "
    "Passing Examinations, p. 100"
)

ACADEMIC = "Academic"
LOCAL = "Local"
#: Ease Factors for a random person to have heard of a Reputation, by how
#: far away they are: (Local, Ecclesiastical, Hermetic) at each Ease.
HEARD_EASE: dict[int, tuple[str, str, str]] = {
    0: ("Same village", "Same parish or monastery", "Same covenant"),
    6: ("Same town", "Same diocese", "Same Tribunal"),
    9: ("Same county", "Same province", "Entire Order"),
    12: ("Same country", "Whole Church", ""),
}


def is_bad(reputation: ScoredTrait) -> bool:
    """A bad Reputation: one typed with a negative score."""
    return reputation.score < 0


def is_academic(reputation: ScoredTrait) -> bool:
    """An Academic Reputation, by its type or its name."""
    return reputation.type == ACADEMIC or "academic" in reputation.name.casefold()


def good(reputations: Iterable[ScoredTrait]) -> list[ScoredTrait]:
    return [r for r in reputations if not is_bad(r) and r.score > 0]


def bad(reputations: Iterable[ScoredTrait]) -> list[ScoredTrait]:
    return [r for r in reputations if is_bad(r)]


def highest_good(reputations: Iterable[ScoredTrait]) -> int:
    """The highest good Reputation's score (0 for none)."""
    return max((r.score for r in good(reputations)), default=0)


def academic_scores(reputations: Iterable[ScoredTrait]) -> tuple[int, int]:
    """The Good and Bad Academic Reputations' scores, each summed."""
    academic = [r for r in reputations if is_academic(r)]
    return (
        sum(r.score for r in good(academic)),
        sum(abs(r.score) for r in bad(academic)),
    )


def net_academic(reputations: Iterable[ScoredTrait]) -> int:
    """Good Academic Reputation less Bad Academic Reputation."""
    gained, lost = academic_scores(reputations)
    return gained - lost


def loyalty_points(reputations: Iterable[ScoredTrait]) -> int:
    """A covenant's Loyalty points from the Reputations its covenfolk know
    of: -5 per point of each bad one, +5 per point of each good local one
    (untyped counts as local)."""
    known = [r for r in reputations if r.known]
    lost = sum(abs(r.score) for r in bad(known))
    gained = sum(r.score for r in good(known) if r.type in ("", LOCAL))
    return 5 * (gained - lost)
