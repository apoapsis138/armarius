"""The Roll request form (the Virtual Tabletop preview): the Session's
storyguide calls for chosen characters to roll a Characteristic, with an
Ability or none, saying what for, who sees each answer (Blind unless
chosen otherwise), and an Ease Factor they may keep to themselves. A
shared grog may be handed, for this request only, to a Player other than
its Steward. Then each answer is one click on the player's card, and the
outcome note one more entry.

Pattern: the core Form (a FieldsDialog builder), its apply making a Macro
Command (chronicle.RollCall: a set of rolls sent out and gathered back)
for the host to carry out."""

from __future__ import annotations

from typing import Any

from .. import catalog, chronicle
from ..commands import Form, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Saga, Session
from ..models.definitions import ROLL_CHARACTERISTICS
from . import free_roll

HELP_ID = "roll-requests"
#: The prefix of each character's tick.
TICK = "roll:"


def offered(saga: Saga, session: Session) -> list[tuple[str, str]]:
    """The characters a request may call on, as (name, id): those cast
    tonight, then shared ones (no Players named) whose Steward is coming."""
    cast = [c.character_id for c in session.castings]
    shown = [(c.name, c.id) for c in saga.characters if c.id in cast]
    for character in saga.characters:
        if character.id in cast or character.background.player_ids:
            continue
        steward = character.background.steward_id
        if steward and steward in session.coming:
            shown.append((character.name, character.id))
    return shown


def _shared(saga: Saga, character_id: str) -> bool:
    found = next((c for c in saga.characters if c.id == character_id), None)
    return found is not None and not found.background.player_ids


def ability_names(saga: Saga, session: Session) -> list[tuple[str, str]]:
    """Any Ability a called character holds, then the catalog's (none
    first: the Characteristic alone)."""
    held = sorted(
        {
            a.name
            for c in saga.characters
            if c.id in {cid for _n, cid in offered(saga, session)}
            for a in c.abilities
        }
    )
    others = sorted(
        a.name
        for a in catalog.load_ability_catalog()
        if not a.parameters and a.name not in held
    )
    return [("(none: the Characteristic alone)", "")] + [
        (escape(name), name) for name in held + others
    ]


def call_of(saga: Saga, session: Session, values: dict[str, Any]) -> chronicle.RollCall:
    """The Roll request the form's values ask for."""
    characters = tuple(
        cid for _name, cid in offered(saga, session) if values.get(TICK + cid)
    )
    handed = values.get("hand_to") or ""
    return chronicle.RollCall(
        characters=characters,
        characteristic=values.get("characteristic") or ROLL_CHARACTERISTICS[0],
        ability=values.get("ability") or "",
        ease_factor=values.get("ease_factor"),
        hide_ease=bool(values.get("hide_ease")),
        visibility=values.get("visibility") or chronicle.BLIND,
        for_what=(values.get("for_what") or "").strip(),
        stress=values.get("die", free_roll.STRESS) == free_roll.STRESS,
        rollers={c: handed for c in characters if handed and _shared(saga, c)},
    )


def request_form(
    saga: Saga, session: Session, who: str, book: chronicle.Chronicle
) -> Form:
    """A Roll request by the Session's storyguide `who`."""

    def fields() -> list[DialogField]:
        ticks = [
            DialogField(TICK + cid, escape(name), "check", True)
            for name, cid in offered(saga, session)
        ]
        return [
            *ticks,
            DialogField(
                "characteristic",
                "Characteristic",
                "select",
                ROLL_CHARACTERISTICS[1],
                options=[(n, n) for n in ROLL_CHARACTERISTICS],
            ),
            DialogField(
                "ability",
                "Ability",
                "select",
                "",
                options=ability_names(saga, session),
            ),
            DialogField(
                "die",
                "Die",
                "select",
                free_roll.STRESS,
                options=[
                    ("Stress die", free_roll.STRESS),
                    ("Simple die", free_roll.SIMPLE),
                ],
            ),
            DialogField(
                "ease_factor",
                "Ease Factor",
                "optint",
                None,
                hint="Blank for none.",
            ),
            DialogField(
                "hide_ease",
                "Hide Ease Factor",
                "check",
                False,
                hint="Players see their totals; only you see the Ease Factor "
                "and who succeeded.",
            ),
            DialogField("for_what", "For", "text", "", placeholder="Spot the ambush"),
            DialogField(
                "visibility",
                "Who sees each roll",
                "select",
                chronicle.BLIND,
                options=[
                    ("Blind: the numbers are yours alone", chronicle.BLIND),
                    ("Private: each roller and you", chronicle.PRIVATE),
                    ("Public: everyone at the Session", chronicle.PUBLIC),
                ],
            ),
            DialogField(
                "hand_to",
                "Shared grogs rolled by",
                "select",
                "",
                options=[("(their Steward)", "")]
                + [
                    (escape(p.name), p.id)
                    for p in saga.players
                    if p.id in session.coming
                ],
                hint="For this request only; the evening's casting is unchanged.",
            ),
        ]

    def validate(values: dict[str, Any]) -> str | None:
        return chronicle.why_not_call(
            saga, session, call_of(saga, session, values), who
        )

    def apply(values: dict[str, Any]) -> list[str]:
        try:
            chronicle.request_rolls(
                book, saga, session, call_of(saga, session, values), by=who
            )
        except ValueError as problem:
            return notes(str(problem))
        except OSError:
            return notes("The request couldn't be saved.")
        return []

    return Form(
        "Roll Request",
        fields,
        apply,
        validate=validate,
        save_label="Ask",
        help_id=HELP_ID,
    )


def outcome_form(
    book: chronicle.Chronicle, saga: Saga, session: Session, number: int, who: str
) -> Form:
    """The storyguide's note of what came of Roll request `number`."""

    def apply(values: dict[str, Any]) -> list[str]:
        try:
            chronicle.note_outcome(
                book, session, number, values.get("text") or "", by=who, saga=saga
            )
        except ValueError as problem:
            return notes(str(problem))
        return []

    return Form(
        f"Outcome of Request {number}",
        lambda: [
            DialogField(
                "text",
                "What came of it",
                "text",
                "",
                required=True,
                placeholder="They spot the archers on the ridge.",
            )
        ],
        apply,
        save_label="Note It",
        help_id=HELP_ID,
    )
