"""A character's deep covers and personae (Houses of Hermes: Societates
pp. 87-90): the Covers section's rows and details, and the form that
adds or edits one, with its inspector. Both front-ends draw them.

A deep cover is an identity built in a community: a name, a role, and a
Reputation in it that rises as an Ability does (rules.house_magic.
COVER_XP each season, kept at Advance) and eases The Gift with those who
know it. A persona (the Persona Supernatural Ability) is a whole
different person; the character has one for each point of Persona."""

from __future__ import annotations

import random
from typing import Any

from ..commands import Form, Refuse, SectionOps, delete, notes
from ..form_spec import DialogField, pairs
from ..markup import escape, problem
from ..models import COVER, PERSONA_KIND, Character, DeepCover, Saga
from ..rules import dice
from ..rules import house_magic as hm
from ..rules.scores import ability_level
from ..sections import COVERS_SECTION
from ..tables import Table

SOURCE = "Houses of Hermes: Societates, House Tytalus, pp. 87-90"
#: The Social Status a role needs, as its form asks it.
STATUS_TIERS: list[tuple[str, str]] = [
    ("None (an ordinary role)", ""),
    ("A Minor Social Status Virtue (a priest)", "Minor"),
    ("A Major Social Status Virtue (a landed noble)", "Major"),
]
EMPTY = (
    "[dim]None: a magus builds a deep cover in a community, or adopts a "
    "persona with the Persona Ability (HoH:S pp. 87-89).[/]"
)


#: The House whose magi keep deep covers (HoH:S pp. 87-89).
TYTALUS = "house_tytalus"


def shown(character: Character) -> bool:
    """Whether the sheet shows the Covers section: a Tytalus magus, one with
    the Persona Ability, or anyone with a cover recorded."""
    return bool(
        character.covers
        or character.hermetic.house == TYTALUS
        or ability_level(character, hm.PERSONA)
        or any(a.name == hm.PERSONA for a in character.abilities)
    )


def title(character: Character) -> str:
    return f"Covers ({len(character.covers)})"


def reputation(character: Character, cover: DeepCover) -> int:
    return hm.cover_reputation(cover, character)


def table(character: Character) -> Table:
    return Table(
        ["Identity", "Role", "Where", "Reputation"],
        [
            [
                escape(c.name or "(unnamed)"),
                escape(c.role),
                escape(c.community),
                str(reputation(character, c))
                + ("" if c.kind == COVER else " (persona)"),
            ]
            for c in character.covers
        ],
        markup=True,
    )


def rows(character: Character) -> list[tuple[int | None, str]]:
    if not character.covers:
        return [(None, EMPTY)]
    return [
        (
            n,
            f"{escape(c.name or '(unnamed)')} [dim]({escape(c.role or c.kind)}"
            + (f", {escape(c.community)}" if c.community else "")
            + ")[/]"
            + f"  ·  Reputation {reputation(character, c)}",
        )
        for n, c in enumerate(character.covers)
    ]


def personae_line(character: Character) -> str:
    """How many personae the Persona Ability allows, and how many are kept."""
    score = ability_level(character, hm.PERSONA)
    kept = sum(1 for c in character.covers if c.kind == PERSONA_KIND)
    if not score and not kept:
        return ""
    return (
        f"Persona {score}: one identity for each point (HoH:S p. 89); {kept} recorded."
    )


def info(character: Character, index: int | None) -> str:
    if index is None or not 0 <= index < len(character.covers):
        return EMPTY
    return _inspect(character, character.covers[index])


def _inspect(character: Character, cover: DeepCover) -> str:
    lines = [f"[b]{escape(cover.name or 'This identity')}[/]  [dim]{cover.kind}[/]"]
    if cover.kind == PERSONA_KIND:
        lines.append(
            f"[$label]Reputation[/] {reputation(character, cover)} "
            f"({hm.cover_reputation_xp(cover, character)} xp: 1 when made, and "
            "every xp put into Persona since, p. 90)"
        )
        lines.append(
            "[i]A whole different person: changing into it is a round's "
            "concentration and Stamina + Persona against 9, and no Disguise "
            "roll is needed (HoH:S p. 89).[/]"
        )
    else:
        score = reputation(character, cover)
        xp, suspicious = hm.cover_xp(cover.contact)
        lines.append(
            f"[$label]Reputation[/] {score} ({cover.reputation_xp} xp)  ·  "
            f"[$label]Keeping it[/] {escape(cover.contact)}: +{xp} xp a season "
            "at Advance"
        )
        lines.append(
            f"[i]Its role costs {hm.cover_burden(cover.status or None)} (p. 88). "
            f"Questioned, its Disguise roll's Ease Factor falls by {score}; with "
            f"those it sees regularly, The Gift's penalty falls by {score} "
            "(p. 89).[/]"
        )
        if suspicious:
            lines.append(problem("More than 2 xp a season arouses suspicion (p. 89)."))
        if cover.last_used is not None:
            lines.append(
                f"Unused since {cover.last_used}: it keeps its Reputation as many "
                "years as its score, then loses a point a year, and The Gift's "
                "penalty returns in full (p. 90)."
            )
    if cover.notes:
        lines.append(escape(cover.notes))
    return "\n".join(lines)


def fields(existing: DeepCover | None) -> list[DialogField]:
    c = existing or DeepCover(reputation_xp=hm.PERSONA_START_XP)

    def is_cover(values: dict[str, Any]) -> bool:
        return (values.get("kind") or COVER) == COVER

    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            c.kind,
            options=[
                ("A deep cover", COVER),
                ("A persona (the Ability)", PERSONA_KIND),
            ],
        ),
        DialogField(
            "name",
            "Name",
            "text",
            c.name,
            required=True,
            placeholder='e.g. "Reynard the Mercenary"',
        ),
        DialogField("role", "Role", "text", c.role, placeholder="e.g. a mercenary"),
        DialogField(
            "community",
            "Where",
            "text",
            c.community,
            show_if=is_cover,
            placeholder="e.g. the village of Hollin",
        ),
        DialogField(
            "status",
            "The role needs",
            "select",
            c.status,
            options=STATUS_TIERS,
            show_if=is_cover,
            hint="A role needing other Virtues (Wealthy, Temporal Influence) "
            "can't be built (p. 88).",
        ),
        DialogField(
            "contact",
            "Keeping it up",
            "select",
            c.contact,
            options=pairs(tuple(hm.COVER_XP)),
            show_if=is_cover,
            hint="Living there 2 xp a season, regular visits 1; a brief visit "
            "each season is 2 a year: choose away and add them by hand.",
        ),
        DialogField(
            "reputation_xp",
            "Reputation xp",
            "int",
            c.reputation_xp,
            hint="A cover starts at 1 (5 xp) with a noteworthy act before "
            "witnesses; each staged event or tie (marriage, children, an "
            "office) adds 1. A persona starts at 1, and gains every xp put "
            "into Persona after it is made (p. 90).",
        ),
        DialogField(
            "last_used",
            "Unused since (year)",
            "optint",
            c.last_used,
            show_if=is_cover,
            hint="Blank while it is kept up.",
        ),
        DialogField("notes", "Notes", "text", c.notes),
    ]


def _made(
    character: Character, values: dict[str, Any], existing: DeepCover | None
) -> DeepCover:
    typed: int | None = values.get("reputation_xp")
    made = DeepCover(
        name=values.get("name") or "",
        kind=values.get("kind") or COVER,
        role=values.get("role") or "",
        community=values.get("community") or "",
        status=values.get("status") or "",
        contact=values.get("contact") or "visits regularly",
        reputation_xp=max(0, typed if typed is not None else hm.PERSONA_START_XP),
        last_used=values.get("last_used"),
        notes=values.get("notes") or "",
        persona_from_xp=hm.persona_xp(character),
    )
    if existing is not None:
        made.id = existing.id
        made.persona_from_xp = existing.persona_from_xp
    return made


def ops(character: Character) -> SectionOps:
    """Add, Edit and Delete on the Covers section; a row is the cover's
    index."""

    def form(index: int | None) -> Form:
        existing = character.covers[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _made(character, values, existing)
            if index is not None:
                character.covers[index] = made
            else:
                character.covers.append(made)

        return Form(
            "Add a Cover" if index is None else "Edit a Cover",
            lambda: fields(existing),
            apply,
            live=lambda values: _inspect(character, _made(character, values, existing)),
            save_label="Add" if index is None else "Save",
            help_id=COVERS_SECTION,
            inspector="The Identity",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            character.covers, index, character.covers[index].name or "this cover"
        ),
        rows=lambda: [c.name or "(unnamed)" for c in character.covers],
    )


# -- the Disguise roll --------------------------------------------------------

DISGUISE_TITLE = "Disguise Roll"
DISGUISE_HELP = "disguise-roll"
#: The two rolls of a disguise (HoH:S p. 87): the Disguise roll itself,
#: and fooling someone he talks with.
LOOKS, TALKS = "looks", "talks"
ROLLS: list[tuple[str, str]] = [
    ("The Disguise roll (Int + Guile against 9 + modifiers)", LOOKS),
    ("Talking with someone (Pre + Guile against Int + Folk Ken)", TALKS),
]


def _covers_kept(character: Character) -> list[tuple[str, str]]:
    return [
        (escape(c.name or "(unnamed)"), c.id)
        for c in character.covers
        if c.kind == COVER
    ]


def _looks(values: dict[str, Any]) -> bool:
    return values.get("roll", LOOKS) == LOOKS


def _talks(values: dict[str, Any]) -> bool:
    return values.get("roll") == TALKS


def _disguise_fields(character: Character) -> list[DialogField]:
    kept = _covers_kept(character)
    return [
        DialogField(
            "cover",
            "The cover",
            "select",
            kept[0][1] if kept else None,
            options=kept,
        ),
        DialogField("roll", "Roll", "select", LOOKS, options=ROLLS),
        DialogField(
            "questioned",
            "Convincing someone of it",
            "check",
            True,
            hint="Questioned by a suspicious priest, or covering a comrade's "
            "slip: the Ease Factor falls by the cover's Reputation. Unticked: "
            "establishing it, with no help from a Reputation (HoH:S p. 88).",
            show_if=_looks,
        ),
        *(
            DialogField(
                f"mod_{index}", f"{name} (+{amount})", "check", False, show_if=_looks
            )
            for index, (name, amount) in enumerate(hm.DISGUISE_MODIFIERS.items())
        ),
        DialogField(
            "against",
            "Their Intelligence + Folk Ken",
            "int",
            0,
            hint="They add a stress die (HoH:S p. 87).",
            show_if=_talks,
        ),
        DialogField("die", "Stress die", "optint", None, hint="Blank: rolled."),
        DialogField(
            "their_die",
            "Their stress die",
            "optint",
            None,
            hint="Blank: rolled.",
            show_if=_talks,
        ),
    ]


def _reputation_off(character: Character, values: dict[str, Any]) -> int:
    cover = next((c for c in character.covers if c.id == values.get("cover")), None)
    if cover is None or not values.get("questioned"):
        return 0
    return reputation(character, cover)


def _ease(character: Character, values: dict[str, Any]) -> int:
    chosen = [
        name
        for index, name in enumerate(hm.DISGUISE_MODIFIERS)
        if values.get(f"mod_{index}")
    ]
    return int(hm.disguise_ease(chosen, _reputation_off(character, values)).total)


def _disguise_live(character: Character, values: dict[str, Any]) -> str:
    if _talks(values):
        own = int(hm.deceive_total(character).total)
        return (
            f"[$label]Presence + Guile[/] {own} + stress die  ·  "
            f"[$label]against[/] {values.get('against') or 0} + stress die "
            "(The Gift's penalty counts: it is a social roll; HoH:S p. 87)"
        )
    own = int(hm.disguise_total(character).total)
    return (
        f"[$label]Intelligence + Guile[/] {own} + stress die  ·  "
        f"[$label]Ease Factor[/] {_ease(character, values)} (HoH:S pp. 87-88)"
    )


def disguise_form(
    saga: Saga, character: Character, rng: random.Random | None = None
) -> Form | Refuse:
    """More's Disguise Roll on Covers: the Disguise roll, Intelligence +
    Guile + stress die against 9 + the modifiers that apply, less the
    cover's Reputation when it is defended rather than established; or
    talking with someone, Presence + Guile + stress die against their
    Intelligence + Folk Ken + stress die (HoH:S pp. 87-88). Shown, not
    kept."""
    if not _covers_kept(character):
        return Refuse(DISGUISE_TITLE, "Add a deep cover first.")
    dice_ = rng or random.Random()

    def roll(typed: Any) -> int:
        return (
            typed if typed is not None else dice.stress_die(dice_, 1, saga=saga).value
        )

    def apply(values: dict[str, Any]) -> list[str]:
        if _talks(values):
            own = int(hm.deceive_total(character).total) + roll(values.get("die"))
            theirs = (values.get("against") or 0) + roll(values.get("their_die"))
            return notes(
                f"Presence + Guile {own} against {theirs}"
                + (": they are fooled." if own > theirs else ": they see through it.")
            )
        own = int(hm.disguise_total(character).total) + roll(values.get("die"))
        ease = _ease(character, values)
        return notes(
            f"Disguise {own} against {ease}"
            + (": the disguise holds." if own >= ease else ": the disguise fails.")
        )

    return Form(
        DISGUISE_TITLE,
        lambda: _disguise_fields(character),
        apply,
        live=lambda values: _disguise_live(character, values),
        save_label="Roll",
        help_id=DISGUISE_HELP,
    )
