"""Charter Strength, an optional rule (Transforming Mythic Europe p. 36):
More's Draft the Charter and Seek a Loophole on a charter lord, the lords
of a town's charter or of a covenant's own (town_charter.py). Each
charter between a lord and the town or covenant has two scores, the
lord's (the superior signatory's) and the other side's (the
subordinate's), kept on the lord's entry with whether the charter is
English (its notaries then use Common Law). The rules are
rules.polemic's."""

from __future__ import annotations

import random
from typing import Any

from .. import town_charter
from ..commands import Command, Form, Refuse
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import SEASONS, Character, Neighbour, Saga
from ..rules import dice, options
from ..rules import polemic as rules
from ..town_charter import CharterLord

DRAFT_TITLE = "Draft the Charter"
LOOPHOLE_TITLE = "Seek a Loophole"
#: The forms' own help pages.
DRAFT_HELP = "draft-charter"
LOOPHOLE_HELP = "seek-loophole"

TME = "TME p. 36"

SUPERIOR, SUBORDINATE = "superior", "subordinate"

IN_ENGLAND = ", in England"


def offered(saga: Saga) -> bool:
    """Whether the saga uses the optional rule."""
    return options.is_on(saga, options.CHARTER_STRENGTH)


def strength_of(entry: CharterLord, side: str) -> int | None:
    """One side's Charter Strength (None until drafted)."""
    value = (
        entry.get("superior_strength")
        if side == SUPERIOR
        else entry.get("subordinate_strength")
    )
    return value if isinstance(value, int) else None


def _set_strength(entry: CharterLord, side: str, strength: int) -> None:
    if side == SUPERIOR:
        entry["superior_strength"] = strength
    else:
        entry["subordinate_strength"] = strength


def in_england(entry: CharterLord) -> bool:
    """Whether the charter is English: its notaries use Common Law, not
    Civil and Canon Law (TME p. 36)."""
    return bool(entry.get("in_england"))


def _other(side: str) -> str:
    return SUBORDINATE if side == SUPERIOR else SUPERIOR


def charter_name(neighbour: Neighbour, entry: CharterLord) -> str:
    """ "Freiburg's charter to Dammërstein"."""
    return f"{entry['lord']}'s charter to {neighbour.name}"


def _side_options(neighbour: Neighbour, entry: CharterLord) -> list[tuple[str, str]]:
    return [
        (escape(f"{neighbour.name} (subordinate)"), SUBORDINATE),
        (escape(f"{entry['lord']} (superior)"), SUPERIOR),
    ]


def _notary_words(character: Character, england: bool) -> str:
    law, score = rules.law_score(character, england)
    intelligence = character.characteristics.intelligence
    sign = "+" if intelligence > 0 else ""
    return f"{character.name} (Int {sign}{intelligence}, {law} {score})"


def _notaries(saga: Saga, england: bool) -> list[Character]:
    """The saga's characters, those with the charter's law first."""
    return sorted(saga.characters, key=lambda c: -rules.law_score(c, england)[1])


def _notary_options(saga: Saga, england: bool) -> list[tuple[str, str]]:
    return [(escape(_notary_words(c, england)), c.id) for c in _notaries(saga, england)]


def _entry(neighbour: Neighbour, row: int | None) -> CharterLord | None:
    lords = town_charter.charter_lords(neighbour)
    return lords[row] if row is not None and 0 <= row < len(lords) else None


def _refused(
    title: str, saga: Saga, neighbour: Neighbour, row: int | None
) -> Refuse | None:
    if not offered(saga):
        return Refuse(title, "The saga doesn't use the Charter Strength rule.")
    if _entry(neighbour, row) is None:
        return Refuse(title, "Choose a charter lord first.")
    if not saga.characters:
        return Refuse(title, "The saga has no one to act as notary yet.")
    return None


# -- Draft the Charter --


def draft_fields(
    saga: Saga, neighbour: Neighbour, entry: CharterLord
) -> list[DialogField]:
    england = in_england(entry)
    notaries = _notaries(saga, england)
    return [
        DialogField(
            "charter", "Charter", "info", escape(charter_name(neighbour, entry))
        ),
        DialogField(
            "in_england",
            "In England",
            "check",
            england,
            hint="Its notaries use Common Law, not Civil and Canon Law (p. 36).",
        ),
        DialogField(
            "side",
            "Drawn up for",
            "select",
            SUBORDINATE,
            options=_side_options(neighbour, entry),
            required=True,
        ),
        DialogField(
            "notary",
            "Principal notary",
            "select",
            notaries[0].id if notaries else None,
            options=_notary_options(saga, england),
            required=True,
        ),
        DialogField("helpers", "Other notaries (−1 botch die each)", "int", 0),
    ]


def draft_live(saga: Saga, values: dict[str, Any]) -> str:
    notary = saga.character(values.get("notary"))
    law, score = rules.law_score(notary, bool(values.get("in_england")))
    intelligence = notary.characteristics.intelligence if notary is not None else 0
    botch = rules.draft_botch_dice(1 + max(0, values.get("helpers") or 0))
    return "\n".join(
        [
            f"Charter Strength: Int {intelligence} + {law} {score} + stress die, "
            f"[b]{botch} botch dice[/] (3, less one for each notary beyond the "
            "first).",
            "A botch leaves this side's strength at 0: no legal defence.",
            "A season's work. Once signed, it binds; each side may later look "
            "for a loophole against the other's strength.",
            f"[dim]An optional rule ({TME}).[/]",
        ]
    )


def draft(
    saga: Saga,
    neighbour: Neighbour,
    entry: CharterLord,
    values: dict[str, Any],
    die: dice.DieResult,
) -> str:
    """Set one side's Charter Strength from the notary's roll with `die`
    (a botch makes it 0); what happened, in words."""
    side = values.get("side") or SUBORDINATE
    notary = saga.character(values.get("notary"))
    entry["in_england"] = bool(values.get("in_england"))
    total = rules.charter_total(notary, in_england(entry))
    strength = 0 if die.botched else total + die.value
    _set_strength(entry, side, strength)
    whose = entry["lord"] if side == SUPERIOR else neighbour.name
    if die.botched:
        return escape(f"A botch: {whose}'s Charter Strength is 0, no legal defence.")
    return escape(
        f"{total} + {die.value} = {strength}: {whose}'s Charter Strength is {strength}."
    )


def draft_form(
    saga: Saga, neighbour: Neighbour, row: int | None, rng: random.Random | None = None
) -> Command:
    """More's Draft the Charter on the chosen charter lord."""
    refused = _refused(DRAFT_TITLE, saga, neighbour, row)
    entry = _entry(neighbour, row)
    if refused is not None or entry is None:
        return refused or Refuse(DRAFT_TITLE, "Choose a charter lord first.")
    chance = rng or random.Random()
    found = entry

    def apply(values: dict[str, Any]) -> str:
        botch = rules.draft_botch_dice(1 + max(0, values.get("helpers") or 0))
        return draft(
            saga, neighbour, found, values, dice.stress_die(chance, botch, saga=saga)
        )

    return Form(
        f"{DRAFT_TITLE}: Charter Strength",
        lambda: draft_fields(saga, neighbour, found),
        apply,
        validate=lambda values: (
            "Other notaries are 0 or more."
            if (values.get("helpers") or 0) < 0
            else None
        ),
        live=lambda values: draft_live(saga, values),
        save_label="Roll",
        help_id=DRAFT_HELP,
        inspector="Charter Strength",
    )


# -- Seek a Loophole --


def loophole_fields(
    saga: Saga, neighbour: Neighbour, entry: CharterLord
) -> list[DialogField]:
    england = in_england(entry)
    notaries = _notaries(saga, england)

    def shown(side: str) -> str:
        value = strength_of(entry, side)
        return "not drafted" if value is None else str(value)

    return [
        DialogField(
            "charter",
            "Charter",
            "info",
            escape(
                f"{charter_name(neighbour, entry)} (the lord's strength "
                f"{shown(SUPERIOR)}, the town's {shown(SUBORDINATE)}; "
                f"{rules.law_of(england)}{IN_ENGLAND if england else ''})"
            ),
        ),
        DialogField(
            "side",
            "Searching for",
            "select",
            SUBORDINATE,
            options=_side_options(neighbour, entry),
            required=True,
            hint="The side looking for grounds to break the other's provisions.",
        ),
        DialogField(
            "who",
            "Searching",
            "select",
            notaries[0].id if notaries else None,
            options=_notary_options(saga, england),
            required=True,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season or "Spring",
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def _against(entry: CharterLord, side: str) -> int | None:
    return strength_of(entry, _other(side))


def loophole_live(
    saga: Saga, neighbour: Neighbour, entry: CharterLord, values: dict[str, Any]
) -> str:
    side = values.get("side") or SUBORDINATE
    who = saga.character(values.get("who"))
    law, score = rules.law_score(who, in_england(entry))
    intelligence = who.characteristics.intelligence if who is not None else 0
    strength = _against(entry, side)
    whose = "the lord's" if side == SUBORDINATE else f"{neighbour.name}'s"
    if strength is None:
        against = f"{escape(whose)} Charter Strength, [b]not drafted yet[/]"
        need = ""
    else:
        total = intelligence + score
        against = f"{escape(whose)} Charter Strength [b]{strength}[/]"
        need = f": the die must show {max(1, strength + 1 - total)} or more"
    return "\n".join(
        [
            f"A season with the charter and the law books, then Int {intelligence} "
            f"+ {law} {score} + stress die against {against}{need}.",
            "Higher: a loophole, and legal grounds to break one or more of its "
            "provisions. One botch die: a botch is a total of 0, and some ill "
            "the storyguide decides.",
            f"[dim]{TME}; a botch, DE p. 7.[/]",
        ]
    )


def seek(
    saga: Saga,
    neighbour: Neighbour,
    entry: CharterLord,
    values: dict[str, Any],
    die: dice.DieResult,
) -> str:
    """A season's search with `die`: a loophole when the total beats the
    other side's Charter Strength (kept on the entry); what happened."""
    side = values.get("side") or SUBORDINATE
    who = saga.character(values.get("who"))
    strength = _against(entry, side) or 0
    total = (
        0 if die.botched else rules.charter_total(who, in_england(entry)) + die.value
    )
    name = who.name if who is not None else "The search"
    when = f"{values.get('season') or saga.current_season} {values.get('year') or saga.current_year}"
    if die.botched:
        return escape(
            "A botch: a total of 0, and something goes wrong, as the "
            f"storyguide decides: {name} may believe in a loophole that isn't "
            "there, or the other side may learn of the search (DE p. 7)."
        )
    if not rules.finds_loophole(total, strength):
        return escape(f"{total} against {strength}: no loophole this season.")
    whose = "the lord's" if side == SUBORDINATE else f"{neighbour.name}'s"
    entry["loophole"] = f"{when}: {name} found grounds against {whose} provisions"
    return escape(
        f"{total} against {strength}: a loophole. {name} has legal grounds to "
        f"break one or more of {whose} provisions."
    )


def loophole_form(
    saga: Saga, neighbour: Neighbour, row: int | None, rng: random.Random | None = None
) -> Command:
    """More's Seek a Loophole on the chosen charter lord."""
    refused = _refused(LOOPHOLE_TITLE, saga, neighbour, row)
    entry = _entry(neighbour, row)
    if refused is not None or entry is None:
        return refused or Refuse(LOOPHOLE_TITLE, "Choose a charter lord first.")
    chance = rng or random.Random()
    found = entry

    def problem(values: dict[str, Any]) -> str | None:
        if _against(found, values.get("side") or SUBORDINATE) is None:
            return (
                "The other side's Charter Strength isn't drafted yet: Draft the "
                "Charter first, or type it on the lord."
            )
        return None

    return Form(
        LOOPHOLE_TITLE,
        lambda: loophole_fields(saga, neighbour, found),
        lambda values: seek(
            saga, neighbour, found, values, dice.stress_die(chance, saga=saga)
        ),
        validate=problem,
        live=lambda values: loophole_live(saga, neighbour, found, values),
        save_label="Roll",
        help_id=LOOPHOLE_HELP,
        inspector="The Fine Print",
    )
