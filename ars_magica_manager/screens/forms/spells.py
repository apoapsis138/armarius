"""The spell form (with its Range / Duration / Target choices and level)
and the Spell Mastery editor."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ... import spells as spl
from ...arts import FORMS, TECHNIQUES
from ...markup import escape
from ...models import (
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    KnownSpell,
    Spell,
)
from ...rules import spell_levels
from ..fields import DialogField, FieldsDialog, _attr, _pairs
from ..prompts import _list_field, _mastery_ability_dialog

#: The choice in a Range/Duration/Target select that opens a free-text box.
_OTHER = "__other__"


def _rdt_field(
    key: str,
    label: str,
    standard: tuple[str, ...],
    value: str,
    fills: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> list[DialogField]:
    """A Range/Duration/Target select of the standard values plus "Other...",
    which shows a text box for a supplement's own value."""
    other = bool(value) and value not in standard
    return [
        DialogField(
            key,
            label,
            "select",
            _OTHER if other else value,
            options=_pairs(standard) + [("Other...", _OTHER)],
            required=True,
            allow_blank=True,
            placeholder=f"(choose a {label})",
            fills=fills,
        ),
        DialogField(
            f"{key}_other",
            f"{label} (other)",
            "text",
            value if other else "",
            placeholder="e.g. Road, Special",
            show_if=lambda v, k=key: v.get(k) == _OTHER,
        ),
    ]


def _spell_fields(spell: Spell | None) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", _attr(spell, "name", ""), required=True),
        DialogField(
            "technique",
            "Technique",
            "select",
            _attr(spell, "technique", ""),
            options=_pairs(TECHNIQUES),
            required=True,
            allow_blank=True,
            placeholder="(choose a Technique)",
        ),
        DialogField(
            "form",
            "Form",
            "select",
            _attr(spell, "form", ""),
            options=_pairs(FORMS),
            required=True,
            allow_blank=True,
            placeholder="(choose a Form)",
        ),
        DialogField(
            "level",
            "Level",
            "optint",
            _attr(spell, "level", None),
            hint="Leave blank for a General spell (cast at any level).",
        ),
        DialogField(
            "requisites",
            "Requisites",
            "text",
            ", ".join(_attr(spell, "requisites", [])),
            placeholder="e.g. Rego, Corpus",
        ),
        *_rdt_field(
            "range", "Range", SPELL_RANGES, _attr(spell, "range", ""), _level_fill
        ),
        *_rdt_field(
            "duration",
            "Duration",
            SPELL_DURATIONS,
            _attr(spell, "duration", ""),
            _level_fill,
        ),
        *_rdt_field(
            "target", "Target", SPELL_TARGETS, _attr(spell, "target", ""), _level_fill
        ),
        DialogField("ritual", "Ritual", "check", _attr(spell, "ritual", False)),
        DialogField(
            "base_level",
            "Base level",
            "optint",
            _attr(spell, "base_level", None),
            hint="The guideline's level; with Range, Duration and Target it "
            "fills in Level (add any size or requisite magnitudes yourself).",
            fills=_level_fill,
        ),
        DialogField(
            "source",
            "Source",
            "text",
            _attr(spell, "source", ""),
            placeholder="e.g. a house rule, or a book",
        ),
        DialogField(
            "description", "Description", "area", _attr(spell, "description", "")
        ),
    ]


def _level_fill(values: dict[str, Any]) -> dict[str, Any]:
    """Level worked out from the base and Range/Duration/Target
    (rules.spell_levels), once they are all standard and given."""
    base = values.get("base_level")
    if base is None:
        return {}
    design = spell_levels.spell_level(
        base,
        _spell_rdt(values, "range"),
        _spell_rdt(values, "duration"),
        _spell_rdt(values, "target"),
        ritual=bool(values.get("ritual")),
    )
    return {} if design is None else {"level": design.level}


def _spell_rdt(values: dict[str, Any], key: str) -> str:
    chosen = values.get(key) or ""
    return values.get(f"{key}_other", "").strip() if chosen == _OTHER else chosen


def _spell_from_values(spell: Spell, values: dict[str, Any]) -> None:
    spell.name = values["name"]
    spell.technique = values["technique"]
    spell.form = values["form"]
    spell.level = values.get("level")
    spell.requisites = spl.parse_requisites(values.get("requisites", ""))
    spell.range = _spell_rdt(values, "range")
    spell.duration = _spell_rdt(values, "duration")
    spell.target = _spell_rdt(values, "target")
    spell.ritual = bool(values.get("ritual"))
    spell.base_level = values.get("base_level")
    spell.source = values.get("source", "")
    spell.description = values.get("description", "")
    spell.details_missing = False


def _spell_problem(values: dict[str, Any]) -> str | None:
    if values.get("level") is not None and values["level"] < 1:
        return "Level must be at least 1 (or blank for a General spell)."
    for key, label in (
        ("range", "Range"),
        ("duration", "Duration"),
        ("target", "Target"),
    ):
        if values.get(key) == _OTHER and not values.get(f"{key}_other", "").strip():
            return f"Type the {label}, or choose one of the standard ones."
    unknown = spl.unknown_requisites(values.get("requisites", ""))
    if unknown:
        return f"Requisites must be Arts (e.g. Rego, Corpus), not {', '.join(unknown)}."
    return None


def _spell_live(values: dict[str, Any]) -> str:
    """The form's live line: the spell's shorthand and magnitude."""
    if not values.get("technique") or not values.get("form"):
        return "[dim]Choose a Technique and a Form.[/]"
    probe = Spell(
        id="",
        name="",
        technique=values["technique"],
        form=values["form"],
        level=values.get("level"),
        requisites=spl.parse_requisites(values.get("requisites", "")),
        ritual=bool(values.get("ritual")),
    )
    mag = spl.magnitude(probe)
    text = f"[b]{escape(spl.shorthand(probe))}[/]"
    text += "  General level" if mag is None else f"  magnitude {mag}"
    if probe.ritual and mag is not None:
        text += f"  ({spl.vis_cost(probe)} pawns, {spl.casting_time(probe)})"
    return text


def _mastery_dialog(spell_name: str, existing: KnownSpell) -> FieldsDialog[KnownSpell]:
    """Edits a known spell's Mastery: score, xp, and its Mastery Abilities
    (each with its own name/level/xp, see MasteryAbility). Builds the
    finished KnownSpell."""
    return FieldsDialog(
        f"Mastery: {escape(spell_name)}",
        [
            DialogField("mastery_score", "Score", "int", existing.mastery_score),
            DialogField("mastery_xp", "XP", "int", existing.mastery_xp),
            _list_field(
                "mastery_abilities",
                "Mastery Abilities",
                existing.mastery_abilities,
                f"Mastery Abilities: {escape(spell_name)}",
                lambda ability: f"{ability.name} {ability.level}/{ability.xp}",
                lambda ability: _mastery_ability_dialog(
                    "Add a Mastery Ability"
                    if ability is None
                    else "Edit a Mastery Ability",
                    ability,
                ),
            ),
        ],
        build=lambda values: KnownSpell(spell_id=existing.spell_id, **values),
    )
