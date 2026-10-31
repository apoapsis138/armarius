"""Character Templates: the book's ready-to-play characters,
offered on New Character by type. Using one fills the new sheet --
Characteristics, age, Virtues and Flaws, Abilities, Arts, spells, gear,
Personality Traits, Reputations and House -- and the character starts In
Play, since the book's templates are "fully generated".

The catalog keeps the book's notation (scores, not xp): an Ability or Art
gets the xp its score needs plus the book's "(Z)" toward the next, and a
Puissant "+Y" is left to the Virtue. Names the book leaves to the player
("Area Lore: {area}", "Living Language: {language}") are asked for when the
template is used, as the sample childhoods do.

Rules: Ars Magica Definitive Edition, Chapter Three: Characters, Character
Templates (SOURCE); each entry's `fixes` say where it differs from the page.
"""

from __future__ import annotations

from dataclasses import replace

from . import catalog, sourcebooks, storage
from . import possessions as pos
from .markup import escape
from .models import (
    GEAR_TYPES_BY_KIND,
    Ability,
    ArtScore,
    Character,
    CharacterTemplateDef,
    KnownSpell,
    Possession,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from .rules import aging, warping
from .rules import creation_access as access
from .rules import creation_xp as cx
from .rules.xp import ability_xp, art_xp

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Character Templates, pp. "
    "30-43"
)


def templates_for(
    character_type: str, saga: Saga | None = None
) -> list[CharacterTemplateDef]:
    """The templates a new character of this type can start from: the
    Definitive Edition's, and with `saga`, those of a book it has in play."""
    return [t for t in _all(saga) if t.type == character_type]


def any_for(character_type: str) -> bool:
    """Whether any book offers this type a template."""
    return bool(templates_for(character_type)) or any(
        t.type == character_type for t in catalog.load_pack_template_catalog()
    )


def _all(saga: Saga | None) -> list[CharacterTemplateDef]:
    found = catalog.load_character_template_catalog()
    if saga is None:
        return found
    books = sourcebooks.saga_books(saga)
    return found + [
        t
        for t in catalog.load_pack_template_catalog()
        if sourcebooks.in_play(t.source, books)
    ]


def find(template_id: str | None) -> CharacterTemplateDef | None:
    if not template_id:
        return None
    found = catalog.load_character_template_catalog_by_id().get(template_id)
    if found is not None:
        return found
    return next(
        (t for t in catalog.load_pack_template_catalog() if t.id == template_id), None
    )


def blanks(template: CharacterTemplateDef) -> list[str]:
    """The names the template leaves to the player ("area", "language"), in
    the order its Abilities first ask for them."""
    return cx.template_blanks(tuple((a["name"], 0) for a in template.abilities))


def _fill(name: str, values: dict[str, str]) -> str:
    return cx.fill_template(((name, 0),), values)[0][0]


def apply(
    saga: Saga,
    character: Character,
    template: CharacterTemplateDef,
    values: dict[str, str] | None = None,
) -> None:
    """Fill `character` from `template` and put it In Play. `values` fills
    the template's blanks (blanks()); a blank left out keeps its
    placeholder, which the sheet shows as typed."""
    values = values or {}
    c = character
    c.characteristics = replace(c.characteristics, **template.characteristics)
    c.aging.aging_points = dict(template.aging_points)
    c.background.size = template.size
    c.background.year_born = saga.current_year - template.age
    if template.apparent_age != template.age:
        c.aging.apparent_age = template.apparent_age
    score, past = template.decrepitude
    c.aging.decrepitude_points = aging.points_for_score(score) + past
    c.aging.decrepitude = score
    warping.set_total(c, warping.points_for(template.warping[0]) + template.warping[1])
    c.background.confidence_score, c.background.confidence_points = template.confidence
    c.virtues_flaws = [
        VirtueFlawInstance(vf["vf_id"], params=dict(vf["params"]))
        for vf in template.virtues_flaws
    ]
    c.personality_traits = [ScoredTrait(n, s) for n, s in template.personality_traits]
    c.reputations = [ScoredTrait(n, s) for n, s in template.reputations]
    c.abilities = [_ability(entry, values) for entry in template.abilities]
    c.arts = {
        art: ArtScore(xp=art_xp(entry["score"]) + entry.get("xp", 0))
        for art, entry in template.arts.items()
    }
    c.spells_known = [_known_spell(saga, entry) for entry in template.spells]
    c.inventory = []
    for entry in template.equipment:
        c.inventory.append(_possession(c, entry))
    if template.house:
        c.hermetic.house = template.house
    c.description.biography = _biography(template)
    c.in_creation = False


def _ability(entry: dict, values: dict[str, str]) -> Ability:
    name = _fill(entry["name"], values)
    return Ability(
        name=name,
        category=access.ability_category(name),
        xp=ability_xp(entry["score"]) + entry.get("xp", 0),
        specialty=entry.get("specialty"),
        xp_table=access.ability_xp_table(name),
    )


def _known_spell(saga: Saga, entry: dict) -> KnownSpell:
    mastery = entry.get("mastery", 0)
    return KnownSpell(
        _spell_id(saga, entry), mastery_score=mastery, mastery_xp=ability_xp(mastery)
    )


def _spell_id(saga: Saga, entry: dict) -> str:
    """The spell's id: a catalog spell's own, or -- for a version the
    catalog lacks, or a book's own printing -- the saga's own copy of it,
    made the first time."""
    if "spell_id" in entry:
        return entry["spell_id"]
    if "spell" in entry:
        return _printed_spell(saga, entry["spell"])
    for spell in saga.spells:
        if spell.name == entry["name"]:
            return spell.id
    base = catalog.load_spell_catalog_by_id()[entry["version_of"]]
    ids = [s.id for s in [*catalog.load_spell_catalog(), *saga.spells]]
    spell = replace(
        base,
        id=storage.generate_unique_id(f"spell {entry['name']}", ids),
        name=entry["name"],
        level=entry["level"],
        source="DE",
        description=(
            f"A version of {base.name} (Character Templates). " + base.description
        ),
    )
    saga.spells.append(spell)
    return spell.id


def _printed_spell(saga: Saga, data: dict) -> str:
    for spell in saga.spells:
        if spell.name == data["name"]:
            return spell.id
    ids = [s.id for s in [*catalog.load_spell_catalog(), *saga.spells]]
    spell = Spell.from_dict(data)
    spell = replace(spell, id=storage.generate_unique_id(f"spell {spell.name}", ids))
    saga.spells.append(spell)
    return spell.id


def _possession(character: Character, entry: dict) -> Possession:
    kind = entry["kind"]
    if kind == "item":
        values: dict = {"name": entry["name"]}
    elif kind == "weapon":
        weapons = {w.id: w for w in catalog.load_weapon_catalog()}
        values = {"gear_id": entry["gear_id"]}
        values |= pos.weapon_fills(values, weapons)
    else:
        armors = {a.id: a for a in catalog.load_armor_catalog()}
        full = bool(entry.get("full"))
        values = {
            "gear_id": entry["gear_id"],
            "gear_type": GEAR_TYPES_BY_KIND["armor"][1 if full else 0],
        }
        values |= pos.armor_fills(values, armors)
        values["name"] = f"{'Full' if full else 'Partial'} {values['name']}"
    return Possession(
        id=storage.generate_unique_id(
            values.get("name") or kind, [item.id for item in character.inventory]
        ),
        kind=kind,
        **values,
    )


def _biography(template: CharacterTemplateDef) -> str:
    """What the sheet's Biography starts as: where the character came
    from, the book's details for Virtues and Flaws that have no parameter
    to hold them, and its notes on customizing the character."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    details = [
        f"{catalog.describe_virtue_flaw(VirtueFlawInstance(vf['vf_id'], dict(vf['params'])), by_id)}"
        f" ({vf['note']})"
        for vf in template.virtues_flaws
        if vf.get("note")
    ]
    free = [
        catalog.describe_virtue_flaw(
            VirtueFlawInstance(vf["vf_id"], dict(vf["params"])), by_id
        )
        for vf in template.virtues_flaws
        if vf.get("free")
    ]
    book = sourcebooks.title_of(template.source)
    parts = [
        f"Built from the {template.name} template (Ars Magica Definitive "
        "Edition, Chapter Three: Characters, Character Templates)."
        if template.source == "ArM5"
        else f"Built from the {template.name} template ({book})."
    ]
    if free:
        parts.append(f"From the House: {', '.join(free)}.")
    if details:
        parts.append(f"Details: {'; '.join(details)}.")
    if template.notes:
        parts.append(f"Customizing: {template.notes}")
    return "\n\n".join(parts)


def summary(template: CharacterTemplateDef) -> str:
    """The New Character form's description of a template (markup): its
    age (and House), Virtues and Flaws, best Arts or Abilities, and the
    book's notes on customizing it."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    house = catalog.load_house_catalog_by_id().get(template.house or "")
    head = f"age {template.age}" + (f", House {house.name}" if house else "")
    vfs = ", ".join(
        catalog.describe_virtue_flaw(
            VirtueFlawInstance(vf["vf_id"], dict(vf["params"])), by_id
        )
        for vf in template.virtues_flaws
    )
    if template.arts:
        label = "Best Arts"
        best = sorted(template.arts.items(), key=lambda kv: -kv[1]["score"])[:4]
        strengths = [f"{art.title()} {entry['score']}" for art, entry in best]
    else:
        label = "Best Abilities"
        ranked = sorted(
            (a for a in template.abilities if "{" not in a["name"]),
            key=lambda a: -a["score"],
        )
        strengths = [f"{a['name']} {a['score']}" for a in ranked[:5]]
    return "\n".join(
        [
            f"[b]{escape(template.name)}[/] ({escape(head)})",
            f"[b]Virtues and Flaws:[/] {escape(vfs)}",
            f"[b]{label}:[/] {escape(', '.join(strengths))}",
            f"[dim]{escape(template.notes)}[/]",
        ]
    )
