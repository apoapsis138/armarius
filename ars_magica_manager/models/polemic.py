"""A Tribunal's arguments: positions a magus means to win at a coming
meeting, and the texts written for and against each (Transforming Mythic
Europe pp. 27-35).

An argument names its reach (the Prevailing Wisdom it moves), its
proponent, the Ability its texts are written on, the case or motion it
goes to, and how its last debate ended. Each text is a polemic, a
diatribe or an apologia: a link to a summa or tractatus in the saga's
library (not a copy of it), its author, who circulates it, to what
audience and how far it has got. The Argument Total and the debate bonus
it buys are worked out (rules.polemic), never kept.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields
from .traits import new_instance_id

#: What a text is (TME p. 28): the polemic sets out the position, a
#: diatribe attacks it, an apologia defends it.
POLEMIC = "polemic"
DIATRIBE = "diatribe"
APOLOGIA = "apologia"
TEXT_KINDS: tuple[str, ...] = (POLEMIC, DIATRIBE, APOLOGIA)

#: Whom an argument concerns: its reach on the Prevailing Wisdom Table
#: (TME p. 29).
REACHES: tuple[str, ...] = ("magus", "covenant", "tribunal", "house", "order")

#: Whom a text is circulated to (TME p. 29).
AUDIENCES: tuple[str, ...] = ("tribunal", "house", "order")

#: The side of a hearing an argument backs: the case or motion (its
#: prosecutor or proposer), or the defence against it.
FOR, AGAINST = "for", "against"
SIDES: tuple[str, ...] = (FOR, AGAINST)

#: How an argument's last debate went (TME p. 35): not yet debated, won
#: (its bonus carries to later Tribunals) or lost (its bonus is gone).
WON, LOST = "won", "lost"
OUTCOMES: tuple[str, ...] = ("", WON, LOST)


def _one_of(value: Any, allowed: tuple[str, ...], what: str) -> str:
    text = "" if value is None else str(value)
    if text not in allowed:
        raise ValueError(f"{what}: {text!r} is not one of {', '.join(allowed)}.")
    return text


def _count(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{what} should be a whole number of at least 0.")
    return value


@dataclass
class PolemicText:
    """A polemic, diatribe or apologia: the book in the saga's library it
    is, its author, who circulates it (None: the author), the audience it
    goes to, the seasons spent circulating it so far, the new works bound
    into every copy, whether it is out (and when), for a diatribe or
    apologia whether its author spent the season studying the work it
    answers (TME pp. 31, 35), and the characters it has given its
    Reputation (on writing or circulating it), so none gains it twice."""

    kind: str = POLEMIC
    book_id: str | None = None
    author_id: str | None = None
    circulated_by_id: str | None = None
    audience: str = "tribunal"
    seasons_spent: int = 0
    bundled: int = 0
    circulated: bool = False
    circulated_year: int | None = None
    circulated_season: str = ""
    studied: bool = False
    reputation_given: list[str] = field(default_factory=list)
    note: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], where: str = "A text") -> PolemicText:
        text = cls(**known_fields(cls, data))
        text.kind = _one_of(text.kind, TEXT_KINDS, f"{where}: its kind")
        text.audience = _one_of(text.audience, AUDIENCES, f"{where}: its audience")
        text.seasons_spent = _count(text.seasons_spent, f"{where}: its seasons spent")
        text.bundled = _count(text.bundled, f"{where}: the works bound with it")
        given = text.reputation_given
        if not isinstance(given, list) or not all(isinstance(g, str) for g in given):
            raise ValueError(
                f"{where}: those it gave its Reputation should be a list of ids."
            )
        return text


@dataclass
class Argument:
    """A position someone means to win at a coming meeting: its topic,
    the ideal its Reputations name (Supporter of / Opposed to ...), its
    reach and, for one concerning a magus, his Reputation, its proponent,
    the Ability its texts are written on, the case or motion on the
    docket it goes to and the side it backs there, how its last debate
    went, and its texts."""

    topic: str
    ideal: str = ""
    reach: str = "tribunal"
    magus_reputation: int = 0
    proponent_id: str | None = None
    ability: str = "Code of Hermes"
    case_id: str = ""
    side: str = FOR
    outcome: str = ""
    texts: list[PolemicText] = field(default_factory=list)
    id: str = field(default_factory=new_instance_id, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Argument:
        d = known_fields(cls, data)
        where = f"The argument {d.get('topic', '')!r}"
        texts = d.get("texts") or []
        if not isinstance(texts, list):
            raise ValueError(f"{where}: its texts should be a list.")
        d["texts"] = [
            PolemicText.from_dict(t, f"{where}, text {n + 1}")
            for n, t in enumerate(texts)
        ]
        argument = cls(**d)
        argument.reach = _one_of(argument.reach, REACHES, f"{where}: its reach")
        argument.side = _one_of(argument.side, SIDES, f"{where}: its side")
        argument.outcome = _one_of(argument.outcome, OUTCOMES, f"{where}: its outcome")
        argument.magus_reputation = _count(
            argument.magus_reputation, f"{where}: the magus's Reputation"
        )
        return argument
