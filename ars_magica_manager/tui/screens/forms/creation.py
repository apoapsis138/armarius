"""The Create forms: a saga (and its rule options), a covenant, a character
(from a template), a laboratory and a familiar."""

from __future__ import annotations

from typing import Any

from .... import character_templates
from .... import familiars as fam
from ....form_spec import DialogField, attr, covenant_options, pairs
from ....markup import escape
from ....models import REALMS, SEASONS, Saga
from ....rules import options as rule_options
from ..fields import FieldsDialog


def _saga_fields(saga: Saga | None) -> list[DialogField]:
    """The Create Saga form (with the starting date) or, given a saga, its
    Edit Saga form."""
    fields = [
        DialogField(
            "name",
            "Name",
            "text",
            attr(saga, "name", ""),
            required=True,
            placeholder="e.g. Dammerstein",
        ),
        DialogField(
            "storyguide",
            "Storyguide",
            "text",
            attr(saga, "storyguide", ""),
            required=True,
            placeholder="e.g. Alex",
        ),
    ]
    if saga is None:
        fields += [
            DialogField("year", "Start Year", "int", 1220),
            DialogField(
                "season", "Start Season", "select", SEASONS[0], options=pairs(SEASONS)
            ),
        ]
    fields.append(
        DialogField(
            "description",
            "Description",
            "text",
            attr(saga, "description", ""),
            placeholder="A one-line premise for the saga",
        )
    )
    if saga is not None:
        fields.append(
            DialogField(
                "keep_season_records",
                "Keep season records",
                "check",
                saga.keep_season_records,
                hint="A record of each season as it is applied, listed under Seasons in the tree. Off: only the Diaries keep them.",
            )
        )
        fields += [
            DialogField(
                RULE_OPTION_PREFIX + option.key,
                option.label,
                "check",
                rule_options.is_on(saga, option.key),
                hint=f"Optional rule, off by default. {option.effect}",
            )
            for option in rule_options.offered(saga)
        ]
    return fields


#: Saga-form keys for the optional rules: the prefix plus the option's key.
RULE_OPTION_PREFIX = "rule_option__"


def saga_rule_options(
    values: dict[str, Any], kept: dict[str, bool] | None = None
) -> dict[str, bool]:
    """The optional rules chosen on the saga form, taken out of `values` (so
    what's left are plain Saga fields). An option the form didn't offer (its
    book out of play) keeps its value from `kept`, the saga's own."""
    chosen = {
        **(kept or {}),
        **{
            key.removeprefix(RULE_OPTION_PREFIX): bool(values.pop(key))
            for key in list(values)
            if key.startswith(RULE_OPTION_PREFIX)
        },
    }
    return rule_options.normalized(chosen)


def _covenant_create_fields() -> list[DialogField]:
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Fengheld"
        ),
        DialogField(
            "notes",
            "Notes",
            "text",
            "",
            placeholder="A one-line note about the covenant",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            "Spring",
            options=pairs(SEASONS),
            hint="Its stage of life. Spring or Winter, Summer or Autumn set "
            "each inhabitant's points and Living Conditions.",
        ),
        DialogField(
            "aura_realm",
            "Aura realm",
            "select",
            "Magic",
            options=pairs(REALMS),
            hint="The creation rules assume Magic (aura 3); a Faerie aura is a Hook.",
        ),
    ]


#: The kinds of character, as Select options.
_CHARACTER_TYPES: list[tuple[str, str]] = [
    ("Magus", "magus"),
    ("Companion", "companion"),
    ("Mythic Companion", "mythic companion"),
    ("Grog", "grog"),
]


def _covenant_field(saga: Saga, covenant_id: str | None) -> DialogField:
    """An optional choice of covenant."""
    return DialogField(
        "covenant_id",
        "Covenant",
        "select",
        covenant_id,
        options=covenant_options(saga),
        allow_blank=True,
        placeholder="(no covenant)",
    )


def _character_create_fields(saga: Saga, covenant_id: str | None) -> list[DialogField]:
    """Name, Type, a Template of that Type (one field per Type,
    shown while it is chosen) and covenant."""
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Leandro"
        ),
        DialogField("type", "Type", "select", "magus", options=_CHARACTER_TYPES),
        *(_template_field(kind) for _, kind in _CHARACTER_TYPES),
        _covenant_field(saga, covenant_id),
    ]


def template_key(kind: str) -> str:
    """The New Character form's key for a Type's Template field."""
    return "template_" + kind.replace(" ", "_")


def _template_field(kind: str) -> DialogField:
    options = [(escape(t.name), t.id) for t in character_templates.templates_for(kind)]
    return DialogField(
        template_key(kind),
        "Template",
        "select",
        None,
        options=options,
        allow_blank=True,
        placeholder="None",
        show_if=lambda values: values.get("type") == kind,
    )


def _character_create_dialog(
    saga: Saga, covenant_id: str | None
) -> FieldsDialog[dict[str, Any]]:
    """Create a New Character, describing the chosen Template as it is
    picked."""

    def live(values: dict[str, Any]) -> str:
        kind = values.get("type") or ""
        template = character_templates.find(values.get(template_key(kind)))
        if template is not None:
            return character_templates.summary(template)
        if not character_templates.templates_for(kind):
            return "[dim]The book has no templates for this type.[/]"
        return (
            "[dim]None: the character starts In Creation, built step by step. "
            "A template is a ready-to-play character from the book.[/]"
        )

    return FieldsDialog(
        "Create a New Character",
        _character_create_fields(saga, covenant_id),
        live=live,
        save_label="Create",
    )


def _laboratory_create_fields(saga: Saga, covenant_id: str | None) -> list[DialogField]:
    return [
        DialogField(
            "name",
            "Name",
            "text",
            "",
            required=True,
            placeholder="e.g. The Alchemical Tower",
        ),
        DialogField("size", "Size", "int", 0),
        _covenant_field(saga, covenant_id),
        DialogField(
            "starting",
            "One of the covenant's starting labs",
            "check",
            _covenant_in_creation(saga, covenant_id),
            hint="Paid for from the covenant's Build Points (one free per magus).",
        ),
    ]


def _covenant_in_creation(saga: Saga, covenant_id: str | None) -> bool:
    covenant = saga.covenant(covenant_id)
    return covenant is not None and covenant.in_creation


def _familiar_create_fields(saga: Saga, magus_id: str | None) -> list[DialogField]:
    """Name the Familiar and choose its magus (one with no Familiar yet)."""
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Ashwing"
        ),
        DialogField(
            "character_id",
            "Magus Partner",
            "select",
            magus_id,
            options=[(escape(c.name), c.id) for c in fam.unbonded_magi(saga)],
            required=True,
            allow_blank=True,
            placeholder="(choose a magus)",
        ),
    ]
