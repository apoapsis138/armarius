"""A magus's Known Spells, independent of how they are drawn: adding a
spell from every spell there is, editing its Spell Mastery, and deleting
it (commands.SectionOps)."""

from __future__ import annotations

from typing import Any

from .. import sourcebooks
from .. import spells as spl
from ..commands import Choice, Choose, Form, SectionOps, delete, not_offered, picked
from ..form_spec import DialogField, ListEditor, attr
from ..markup import escape
from ..models import Character, KnownSpell, MasteryAbility, Saga, Spell


def known_spell_name(saga: Saga, known: KnownSpell) -> str:
    """A known spell's name (plain text; its id if it's missing)."""
    spell = spl.find_spell(saga, known.spell_id)
    return spell.name if spell else f"{known.spell_id} (unknown spell)"


def mastery_ability_row(ability: MasteryAbility) -> str:
    """A Mastery Ability as its list shows it (plain text)."""
    return f"{ability.name} {ability.level}/{ability.xp}"


def mastery_ability_fields(existing: MasteryAbility | None) -> list[DialogField]:
    """One Mastery Ability: its name, level and xp."""
    return [
        DialogField(
            "name",
            "Name",
            "text",
            attr(existing, "name", ""),
            required=True,
            placeholder="e.g. Fast Casting",
        ),
        DialogField("level", "Level", "int", attr(existing, "level", 0)),
        DialogField("xp", "XP", "int", attr(existing, "xp", 0)),
    ]


def mastery_ability_title(existing: MasteryAbility | None) -> str:
    return "Add a Mastery Ability" if existing is None else "Edit a Mastery Ability"


def mastery_ability_form(existing: MasteryAbility | None) -> Form:
    """Add or edit one Mastery Ability, picked as a MasteryAbility."""
    return Form(
        mastery_ability_title(existing),
        lambda: mastery_ability_fields(existing),
        picked(lambda values: MasteryAbility(**values)),
        save_label="Add" if existing is None else "Save",
    )


def mastery_fields(
    known: KnownSpell,
    abilities: DialogField | None = None,
    *,
    spell_name: str = "",
) -> list[DialogField]:
    """A known spell's Mastery: its score, its xp and its Mastery
    Abilities. `abilities` is the front-end's own field for the list
    (one that opens a list to add to); by default the list is shown as it
    stands and kept as it is."""
    if abilities is None:
        abilities = DialogField(
            "mastery_abilities",
            "Mastery Abilities",
            "picker",
            list(known.mastery_abilities),
            display=lambda items: (
                "; ".join(mastery_ability_row(a) for a in items) or "(none)"
            ),
            items=ListEditor(
                mastery_ability_row,
                mastery_ability_form,
                f"Mastery Abilities: {escape(spell_name)}"
                if spell_name
                else "Mastery Abilities",
            ),
        )
    return [
        DialogField("mastery_score", "Score", "int", known.mastery_score),
        DialogField("mastery_xp", "XP", "int", known.mastery_xp),
        abilities,
    ]


def known_spell_from(known: KnownSpell, values: dict[str, Any]) -> KnownSpell:
    return KnownSpell(
        spell_id=known.spell_id,
        mastery_score=values["mastery_score"],
        mastery_xp=values["mastery_xp"],
        mastery_abilities=list(
            values.get("mastery_abilities", known.mastery_abilities)
        ),
    )


def mastery_title(spell_name: str) -> str:
    return f"Mastery: {escape(spell_name)}"


def spell_choices(
    saga: Saga, exclude: set[str], *, in_play: bool = True
) -> list[Choice]:
    """Every spell there is (the catalog, the saga's own, any magus's
    invented spells) but those in `exclude`, from books in play: its name,
    Arts and where it is from, with its details beside the list.
    `in_play` False: those from books not in play instead, marked so (for
    Show everything)."""
    books = sourcebooks.saga_books(saga)
    found = []
    for spell, origin in spl.pickable_spells(saga):
        if spell.id in exclude:
            continue
        # A catalog spell's book; the saga's own and invented spells are
        # always in play.
        source = spell.source if origin == spell.source else ""
        if sourcebooks.in_play(source, books) != in_play:
            continue
        choice = _spell_choice(saga, spell, origin)
        found.append(choice if in_play else not_offered(choice, "book not in play"))
    return found


def _spell_choice(saga: Saga, spell: Spell, origin: str) -> Choice:
    shorthand = spl.shorthand(spell)
    return Choice(
        f"{escape(spell.name)}  [dim]{escape(shorthand)}  {escape(origin)}[/]",
        spell.id,
        spl.detail_text(saga, spell),
        shorthand,
    )


def shared_fields(
    saga: Saga, character: Character, spell: Spell | None
) -> list[DialogField]:
    """A spell the magus invented: the Shared tick, which puts it in the
    saga's Spells for anyone to learn; once shared it stays shared."""
    if spell is None:
        return []
    own = spl.invention(saga, character, spell.id)
    if own == "Shared":
        return [DialogField("_shared", "Shared", "info", "Yes, with the whole saga")]
    if own == "Own":
        return [
            DialogField(
                "shared",
                "Shared",
                "check",
                False,
                hint="Puts it in the saga's Spells, where anyone can learn it "
                "or write it up. Once shared, it stays shared.",
            )
        ]
    return []


def known_spell_ops(saga: Saga, character: Character) -> SectionOps:
    """Add, Edit (its Mastery) and Delete for the magus's Known Spells."""
    known = character.spells_known

    def add() -> Choose:
        def apply(spell_id: str) -> None:
            known.append(KnownSpell(spell_id=spell_id))

        return Choose(
            f"Add a spell {escape(character.name)} knows",
            lambda: spell_choices(saga, {k.spell_id for k in known}),
            apply,
            empty="(no spells)",
            others=lambda: spell_choices(
                saga, {k.spell_id for k in known}, in_play=False
            ),
        )

    def edit(index: int) -> Form:
        existing = known[index]
        spell = spl.find_spell(saga, existing.spell_id)
        name = spell.name if spell else existing.spell_id

        def apply(values: dict[str, Any]) -> None:
            known[index] = known_spell_from(existing, values)
            if values.get("shared") and spell in character.invented_spells:
                spl.share_invented_spell(saga, character, spell)

        return Form(
            mastery_title(name),
            lambda: mastery_fields(existing) + shared_fields(saga, character, spell),
            apply,
        )

    return SectionOps(
        add=add,
        edit=edit,
        remove=lambda index: delete(known, index, known_spell_name(saga, known[index])),
        rows=lambda: [known_spell_name(saga, k) for k in known],
    )
