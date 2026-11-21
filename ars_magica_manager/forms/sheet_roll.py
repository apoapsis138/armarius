"""Roll from the sheet (the Virtual Tabletop preview): a character's
Characteristic, with an Ability or none, rolled at the host while a
Session is Under way. The card asks only what the sheet can't know: the
Characteristic, the Ability, whether a Specialty applies, the die, an
Ease Factor, anything beyond the sheet, what it is for and who sees it.
The host adds the scores and the wound and Fatigue penalties itself
(chronicle.sheet_terms), so the card never sends a number from the sheet.

An Ability with no score is offered too, unless the book says it needs
experience (DE p. 157): rolled at 0 with three extra botch dice.

A Supernatural Ability or hedge Art is rolled in an aura, taken as Magic
(DE p. 411): the playing Scene's to start with, as whoever rolls may know
it (scene_aura), which the roller can change.

Where the roll goes: to the table as this copy acts at it
(host_table.here): the Chronicle open here on the host's own copy, or the
host, from a Remote seat.

Pattern: the core Form (a FieldsDialog builder), its apply making a
Command (chronicle.RollRequest with a SheetRoll) for the host to carry out
once, as the Free roll's does."""

from __future__ import annotations

from typing import Any

from .. import catalog, chronicle, host_table, scene_aura, table_rules
from ..commands import Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, Saga
from ..models.definitions import ROLL_CHARACTERISTICS
from ..rules import creation_access, realms, scores
from . import free_roll

HELP_ID = "sheet-roll"

#: The section names whose Roll this is (section_verbs' ids).
ABILITIES = "tab-abilities"
CHARACTERISTICS = "section-char-characteristics"


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
    table = host_table.here(saga, session, who)
    book = table.held()
    chosen = characteristic or (
        last_characteristic(book, character.id, ability)
        if book is not None
        else ROLL_CHARACTERISTICS[0]
    )
    specialties = ", ".join(
        f"{a.name}: {a.specialty}" for a in character.abilities if a.specialty
    )
    here = scene_aura.for_character(
        saga, session, who, scene_aura.book_of(session, book), character.id
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
                hint="Beyond the sheet: a tool, the storyguide's call. "
                "The sheet's scores and penalties are added for you.",
            ),
            *aura_fields(saga, here),
            DialogField("for_what", "For", "text", "", placeholder="Climb the wall"),
            DialogField(
                "visibility",
                "Who sees it",
                "select",
                table_rules.default_visibility(saga, session, who),
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
                aura=values.get("aura") or 0,
                aura_realm=values.get("aura_realm") or "",
                in_regio=bool(values.get("aura_regio")),
            ),
        )

    def validate(values: dict[str, Any]) -> str | None:
        return chronicle.why_not_roll(saga, session, request_of(values), who)

    def apply(values: dict[str, Any]) -> list[str]:
        refused = table.roll(request_of(values))
        return notes(refused) if refused else []

    return Form(
        f"Roll: {escape(character.name)}",
        fields,
        apply,
        validate=validate,
        save_label="Roll",
        help_id=HELP_ID,
    )


def aura_fields(
    saga: Saga, here: scene_aura.AuraHere | None, ability_key: str = "ability"
) -> list[DialogField]:
    """The aura a supernatural Ability is rolled in, shown while one is
    chosen (in `ability_key`): the playing Scene's to start with."""

    def shown(values: dict[str, Any]) -> bool:
        return chronicle.supernatural(str(values.get(ability_key) or ""))

    start_realm = here.realm if here is not None else ""

    return [
        DialogField(
            "aura",
            "Aura",
            "int",
            here.aura if here is not None else 0,
            show_if=shown,
            hint="The aura it is rolled in, taken as Magic: the Scene's to "
            "start with. A foreign realm's adds a botch die a point.",
        ),
        DialogField(
            "aura_realm",
            "Aura's realm",
            "select",
            start_realm,
            options=[
                ("(no aura)", ""),
                *((r, r) for r in realms.aura_realms(saga, start_realm)),
            ],
            show_if=shown,
        ),
        DialogField(
            "aura_regio",
            "In a regio",
            "check",
            here.in_regio if here is not None else False,
            show_if=shown,
            hint="Twice the botch dice in a regio of another realm.",
        ),
    ]


def why_not_offered(saga: Saga, character: Character) -> str | None:
    """Why the sheet offers no Roll for `character` now, or None: a Session
    must be Under way, and whoever uses this copy may roll for them (a
    player for a character cast to them tonight). One who can't act is
    still offered it, and told why when they try."""
    session = chronicle.under_way(saga)
    if session is None:
        return "No Session is under way."
    who = chronicle.here()
    return table_rules.why_not_roll_for(
        saga, session, who, character.id, table_rules.PUBLIC
    )


def why_not_roll_here(saga: Saga, character: Character) -> str | None:
    """Why `character` can't be rolled for from the sheet now, or None: it
    must be offered (`why_not_offered`) and the character able to act."""
    return why_not_offered(saga, character) or table_rules.why_not_act(character)
