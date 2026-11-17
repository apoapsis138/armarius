"""Roll from the sheet (the Virtual Tabletop preview): a character's
Characteristic, with an Ability or none, rolled at the host while a
Session is Under way. The card asks only what the sheet can't know: the
Characteristic, the Ability, whether a Specialty applies, the die, an
Ease Factor, anything beyond the sheet, what it is for and who sees it.
The host adds the scores and the wound and Fatigue penalties itself
(chronicle.sheet_terms), so the card never sends a number from the sheet.

An Ability with no score is offered too, unless the book says it needs
experience (DE p. 157): rolled at 0 with three extra botch dice.

Where the roll goes: into the Chronicle open here on the host's own
copy; at a Remote seat, to the host, through the sender the window sets
(`use_sender`) while the seat's pane is attached.

Pattern: the core Form (a FieldsDialog builder), its apply making a
Command (chronicle.RollRequest with a SheetRoll) for the host to carry out
once, as the Free roll's does."""

from __future__ import annotations

from typing import Any

from .. import catalog, chronicle
from ..commands import Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga, Session
from ..models.definitions import ROLL_CHARACTERISTICS
from ..rules import creation_access, scores
from . import free_roll

HELP_ID = "sheet-roll"

#: The section names whose Roll this is (section_verbs' ids).
ABILITIES = "tab-abilities"
CHARACTERISTICS = "section-char-characteristics"

#: At a Remote seat: hands a request to the host (the seat's connection),
#: set by the window while the seat's Chronicle pane is attached.
_sender: free_roll.Submit | None = None
#: At a Remote seat: the Chronicle as its host sent it.
_seat_book: chronicle.HasEntries | None = None


def use_sender(
    sender: free_roll.Submit | None, book: chronicle.HasEntries | None = None
) -> None:
    """Send rolls from the sheet to the host with `sender`, the seat's
    Chronicle being `book` (a Remote seat), or roll them here (None: the
    host's own copy)."""
    global _sender, _seat_book
    _sender, _seat_book = sender, book


def _book(saga: Saga, session: Session) -> chronicle.HasEntries | None:
    """The Chronicle as this copy holds it: the seat's, or the one open
    here; None if it can't be read."""
    if _sender is not None:
        return _seat_book
    try:
        return chronicle.read(saga, session)
    except OSError, ValueError:
        return None


def _roll_here(saga: Saga, session: Session, who: str) -> free_roll.Submit:
    def submit(request: chronicle.RollRequest) -> str | None:
        try:
            chronicle.free_roll(
                chronicle.read(saga, session), saga, session, request, by=who
            )
        except ValueError as problem:
            return str(problem)
        except OSError:
            return "The roll couldn't be saved."
        return None

    return submit


def last_characteristic(
    book: chronicle.HasEntries, character_id: str, ability: str
) -> str:
    """The Characteristic last rolled with `ability` by `character_id` in
    this Chronicle, else the first of the book's list."""
    for entry in reversed(book.entries):
        if entry.kind != chronicle.ROLL:
            continue
        if entry.body.get("character_id") != character_id:
            continue
        terms = chronicle.terms_of(entry.body)
        names = [term[0] for term in terms]
        if not names or names[0] not in ROLL_CHARACTERISTICS:
            continue
        rolled = names[1] if len(names) > 1 and names[1] not in _PENALTIES else ""
        if rolled.removesuffix(" (no score)") == ability:
            return names[0]
    return ROLL_CHARACTERISTICS[0]


_PENALTIES = frozenset({"Wounds", "Fatigue", "Modifier"})


def ability_options(character: Character) -> list[tuple[str, str]]:
    """The Abilities the card offers: none, the character's own with their
    scores, then those the book lets anyone try with no score."""
    held = {a.name for a in character.abilities}
    shown: list[tuple[str, str]] = [("(none: the Characteristic alone)", "")]
    for ability in sorted(character.abilities, key=lambda a: a.name):
        level, bonus = scores.ability_score(character, ability.name)
        shown.append((escape(f"{ability.name} {level + bonus}"), ability.name))
    for entry in sorted(catalog.load_ability_catalog(), key=lambda a: a.name):
        if entry.parameters or entry.name in held:
            continue
        if creation_access.needs_experience(entry.name):
            continue
        shown.append((escape(f"{entry.name} (no score)"), entry.name))
    return shown


def roll_form(
    saga: Saga,
    character: Character,
    *,
    ability: str = "",
    characteristic: str = "",
) -> Form | Refuse:
    """Roll from `character`'s sheet at the Session Under way, by whoever
    uses this copy of the app."""
    session = chronicle.under_way(saga)
    if session is None:
        return Refuse("Roll", "No Session is under way.")
    who = chronicle.here()
    book = _book(saga, session)
    chosen = characteristic or (
        last_characteristic(book, character.id, ability)
        if book is not None
        else ROLL_CHARACTERISTICS[0]
    )
    storyguide = who == chronicle.storyguide_of(session, saga)
    specialties = ", ".join(
        f"{a.name}: {a.specialty}" for a in character.abilities if a.specialty
    )

    def fields() -> list[DialogField]:
        return [
            DialogField("_who", "", "info", escape(character.name)),
            DialogField(
                "characteristic",
                "Characteristic",
                "select",
                chosen,
                options=[(name, name) for name in ROLL_CHARACTERISTICS],
            ),
            DialogField(
                "ability",
                "Ability",
                "select",
                ability,
                options=ability_options(character),
                hint="An Ability with no score is rolled at 0, with three more "
                "botch dice.",
            ),
            DialogField(
                "specialty",
                "Specialty applies",
                "check",
                False,
                hint=escape(specialties) if specialties else "No Specialties.",
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
                hint="Blank for none; with one, the margin is shown.",
            ),
            DialogField(
                "modifier",
                "Anything else",
                "int",
                0,
                hint="Beyond the sheet: an aura, a tool, the storyguide's call. "
                "The sheet's scores and penalties are added for you.",
            ),
            DialogField("for_what", "For", "text", "", placeholder="Climb the wall"),
            DialogField(
                "visibility",
                "Who sees it",
                "select",
                chronicle.BLIND if storyguide else chronicle.PUBLIC,
                options=free_roll.visibility_options(saga, session, who),
            ),
        ]

    def request_of(values: dict[str, Any]) -> chronicle.RollRequest:
        stress = values.get("die", free_roll.STRESS) == free_roll.STRESS
        return chronicle.RollRequest(
            stress=stress,
            modifier=values.get("modifier") or 0,
            botch_dice=1 if stress else 0,
            ease_factor=values.get("ease_factor"),
            for_what=(values.get("for_what") or "").strip(),
            character_id=character.id,
            visibility=values.get("visibility") or chronicle.PUBLIC,
            sheet=chronicle.SheetRoll(
                values.get("characteristic") or ROLL_CHARACTERISTICS[0],
                values.get("ability") or "",
                bool(values.get("specialty")),
            ),
        )

    def validate(values: dict[str, Any]) -> str | None:
        return chronicle.why_not_roll(saga, session, request_of(values), who)

    def apply(values: dict[str, Any]) -> list[str]:
        send = _sender or _roll_here(saga, session, who)
        refused = send(request_of(values))
        return notes(refused) if refused else []

    return Form(
        f"Roll: {escape(character.name)}",
        fields,
        apply,
        validate=validate,
        save_label="Roll",
        help_id=HELP_ID,
    )


def why_not_roll_here(saga: Saga, character: Character) -> str | None:
    """Why the sheet offers no Roll for `character` now, or None: a Session
    must be Under way, and whoever uses this copy may roll for them (a
    player for a character cast to them tonight)."""
    session = chronicle.under_way(saga)
    if session is None:
        return "No Session is under way."
    who = chronicle.here()
    if who != chronicle.storyguide_of(session, saga):
        plays = {c.character_id for c in session.castings if c.player_id == who}
        if character.id not in plays:
            return "Roll for a character you play tonight."
    return chronicle.why_not_act(character)
