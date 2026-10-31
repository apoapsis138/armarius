"""The Antagonists' humans and magi as build templates for New Character,
derived from the pack's own records when the packs are built and kept
in data/pack_template_catalog.json, so New Character needn't read the
whole pack. It is Prototype: each template is a copy of the printed
record to start from, and a test checks the file against the pack, so no
stat block is kept twice by hand. A character with several printed
versions gives one template for each. Sketches have no stats to build
from, and are left out."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .. import catalog
from ..models import Character, KnownSpell, Saga
from ..rules import aging as aging_rules
from ..rules import warping
from .builder import Builder

BOOK = "Ant"
ATTRIBUTION = (
    "Antagonists, by Atlas Games: derived from this app's pack. Based on the "
    "material for Ars Magica, ©1993–2024, licensed by Trident, Inc. d/b/a Atlas "
    "Games®, under Creative Commons Attribution-ShareAlike 4.0 International "
    'license 4.0 ("CC-BY-SA 4.0").'
)
PLAYABLE = ("magus", "companion", "mythic companion")


def _spell(known_spell: KnownSpell, character: Character) -> dict[str, Any]:
    entry: dict[str, Any] = {"mastery": known_spell.mastery_score}
    spell_id = known_spell.spell_id
    held = next((s for s in character.invented_spells if s.id == spell_id), None)
    if held is None:
        return {**entry, "spell_id": spell_id}
    return {**entry, "spell": asdict(held)}


def template_of(
    character: Character, saga: Saga, label: str = "", age: int | None = None
) -> dict[str, Any]:
    """One record as a CharacterTemplateDef's data: Abilities and Arts by
    their whole experience, so nothing is lost to the score."""
    aging = character.aging
    born = character.background.year_born or saga.current_year
    years = age if age is not None else saga.current_year - born
    name = f"{character.name}, {label}" if label else character.name
    key = f"ant_{character.id}_{label}".rstrip("_").casefold().replace(" ", "_")
    past_decrepitude = aging.decrepitude_points - aging_rules.points_for_score(
        aging.decrepitude
    )
    past_warping = warping.total_points(character) - warping.points_for(
        aging.warping_score
    )
    return {
        "id": key,
        "name": f"Antagonist - {name}",
        "type": character.type,
        "house": character.hermetic.house,
        "characteristics": asdict(character.characteristics),
        "aging_points": dict(aging.aging_points),
        "size": character.background.size,
        "age": years,
        "apparent_age": aging.apparent_age or years,
        "decrepitude": [aging.decrepitude, past_decrepitude],
        "warping": [aging.warping_score, past_warping],
        "confidence": [
            character.background.confidence_score,
            character.background.confidence_points,
        ],
        "virtues_flaws": [
            {"vf_id": vf.vf_id, "params": dict(vf.params)}
            for vf in character.virtues_flaws
        ],
        "personality_traits": [[t.name, t.score] for t in character.personality_traits],
        "reputations": [[r.name, r.score] for r in character.reputations],
        "abilities": [
            {"name": a.name, "score": 0, "xp": a.xp, "specialty": a.specialty}
            for a in character.abilities
        ],
        "arts": {
            art: {"score": 0, "xp": score.xp}
            for art, score in character.arts.items()
            if score.xp
        },
        "spells": [_spell(s, character) for s in character.spells_known],
        "equipment": [
            {"kind": "item", "name": item.name}
            for item in character.inventory
            if item.name
        ],
        "source": BOOK,
    }


def entries(b: Builder) -> list[dict[str, Any]]:
    """Every template the pack's records give."""
    saga = b.saga
    found = []
    for character in saga.characters:
        versions = b.variants.get(character.id)
        if versions:
            found += [
                template_of(
                    Character.from_dict(v["character"]), saga, v["label"], v["age"]
                )
                for v in versions
            ]
        elif character.abilities and character.type in PLAYABLE:
            found.append(template_of(character, saga))
    return found


def write(b: Builder, path: Path = catalog.PACK_TEMPLATE_CATALOG_PATH) -> Path:
    catalog.write_pack_templates(path, ATTRIBUTION, entries(b))
    return path
