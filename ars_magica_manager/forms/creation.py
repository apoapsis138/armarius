"""The Create forms, independent of how they are drawn: a saga (and its
rule options), a covenant, a character (from a template), a laboratory and
a familiar, plus Edit Saga. Each builder returns form_spec.DialogFields;
the `*_form` functions bundle them with what saving does as the
commands.Form a New menu entry runs.

Saving a New form adds the record and nothing else: the front-end then
shows it (the terminal also opens its Creation Worksheet).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .. import (
    character_templates,
    choice_templates,
    creation,
    medallions,
    packs,
    ruling_templates,
    storage,
)
from .. import familiars as fam
from .. import grog_templates as gt
from ..commands import Form
from ..form_spec import DialogField, attr, covenant_options, pairs
from ..markup import escape
from ..models import (
    REALMS,
    SEASONS,
    Character,
    CharacterTemplateDef,
    GrogTemplateDef,
    Saga,
)
from ..models.saga import assign_laboratory_owner
from ..rules import options as rule_options
from ..seasons import defaults
from . import choice_templates as choice_forms
from . import grog_templates as grog_forms
from . import tribunal as tribunal_forms
from .character import CHARACTER_TYPE_OPTIONS

#: Saga-form keys for the optional rules: the prefix plus the option's key.
RULE_OPTION_PREFIX = "rule_option__"
#: What Edit Saga asks on the desktop.
SAGA_DETAILS = ("name", "storyguide", "description")


def saga_fields(saga: Saga | None) -> list[DialogField]:
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
    # Each pack file is read once, for both the list and its supplements.
    read = (
        packs.read_packs(packs.SHIPPED_DIR, packs.STARTERS_DIR, storage.exports_dir())
        if saga is None
        else []
    )
    found = packs.choices(read)
    if found:
        fields.append(
            DialogField(
                "pack",
                "Start from a pack",
                "select",
                "",
                options=[("None", ""), *((label, path) for label, path, _ in found)],
                hint="Its Tribunals, covenants, characters, places, neighbours "
                "and calendar are added to the new saga.",
            )
        )
        fields += packs.start_base_fields(found)
        fields += packs.start_intro_fields(found)
        fields += packs.start_story_fields(found)
        fields += packs.start_overlay_fields(found, packs.overlays(read))
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
                setting,
                f"{who} with nothing planned",
                "select",
                getattr(saga, setting),
                options=defaults.OPTIONS,
                hint=hint,
            )
            for setting, who, hint in (
                (
                    "unplanned_magi",
                    "Magi",
                    "When the season is advanced: Work / Exposure (2 xp) in "
                    "their profession, else Magic Theory, else their highest "
                    "Ability that isn't a language; marked (default) in the "
                    "Diary.",
                ),
                (
                    "unplanned_companions",
                    "Companions",
                    "Work / Exposure (2 xp) in their profession, else their "
                    "highest Ability that isn't a language.",
                ),
                (
                    "unplanned_grogs",
                    "Grogs",
                    "A grog with no yearly update: 2 xp of Exposure a season "
                    "in their highest Ability, 8 at the year's end.",
                ),
            )
        ]
        fields.append(
            DialogField(
                "medallions",
                "Medallion style",
                "select",
                medallions.chosen(saga),
                options=medallions.options(),
                hint="How the desktop draws every medallion, the seasons' and "
                "figures' such as an aura: stained glass, an illuminated letter's adornment, a wax "
                "seal, Limoges enamel, a Book of Hours roundel, or pen and wash.",
            )
        )
        fields.append(
            DialogField(
                "notify_npc_unplanned",
                "Be notified when and which non-player characters do not "
                "have seasonal activity",
                "check",
                saga.notify_npc_unplanned,
                hint="Off: Advance Season names only player characters with "
                "nothing planned; the others take the default above.",
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
        fields.append(ruling_templates.saga_field(saga))
    return fields


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


def apply_saga(saga: Saga, values: dict[str, Any]) -> None:
    """Save the Edit Saga form."""
    values = dict(values)
    saga.rule_options = saga_rule_options(values, kept=saga.rule_options)
    for field, value in values.items():
        setattr(saga, field, value)


def edit_saga_form(saga: Saga) -> Form:
    return Form(
        "Edit Saga", lambda: saga_fields(saga), lambda values: apply_saga(saga, values)
    )


def saga_details_form(saga: Saga) -> Form:
    """Edit Saga on the desktop, whose Saga Settings chapter has the rest."""
    return Form(
        "Edit Saga",
        lambda: [f for f in saga_fields(saga) if f.key in SAGA_DETAILS],
        lambda values: apply_saga(saga, values),
    )


# -- New Covenant --


def covenant_create_fields() -> list[DialogField]:
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


def new_covenant_fields(saga: Saga) -> list[DialogField]:
    """New Covenant: covenant_create_fields(), and, once the saga has
    Tribunals, which it belongs to and what its customs ask (the Rhine's
    gilds)."""
    if not saga.tribunals:
        return covenant_create_fields()
    return [
        *covenant_create_fields(),
        tribunal_forms.tribunal_field(saga, None),
        *tribunal_forms.package_fields(saga, None),
    ]


def new_covenant_form(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> None:
        values = dict(values)
        covenant = creation.add_covenant(
            saga,
            values["name"],
            values["notes"],
            season=values["season"] or "Spring",
            aura_realm=values["aura_realm"] or "Magic",
        )
        covenant.tribunal_id = values.get("tribunal_id")
        tribunal_forms.save_package_fields(saga, covenant, values)

    return Form(
        "Create a New Covenant",
        lambda: new_covenant_fields(saga),
        apply,
        save_label="Create",
    )


# -- New Character --

#: The kinds of character, as Select options.
CHARACTER_TYPES = CHARACTER_TYPE_OPTIONS


def covenant_field(saga: Saga, covenant_id: str | None) -> DialogField:
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


def character_create_fields(
    saga: Saga, covenant_id: str | None, kind: str = "magus"
) -> list[DialogField]:
    """Name, Type (`kind` to start with), a Template of that Type (one
    field per Type, shown while it is chosen; a grog's include Grogs'
    templates while that book is in play) and covenant."""
    return [
        DialogField(
            "name", "Name", "text", "", required=True, placeholder="e.g. Leandro"
        ),
        DialogField("type", "Type", "select", kind, options=CHARACTER_TYPES),
        *(_template_field(saga, kind) for _, kind in CHARACTER_TYPES),
        covenant_field(saga, covenant_id),
    ]


def template_key(kind: str) -> str:
    """The New Character form's key for a Type's Template field."""
    return "template_" + kind.replace(" ", "_")


def _template_field(saga: Saga, kind: str) -> DialogField:
    options = [
        (escape(t.name), t.id) for t in character_templates.templates_for(kind, saga)
    ]
    if kind == "grog":
        options += [(escape(f"{t.name} (Grogs)"), t.id) for t in gt.templates(saga)]
        options += [
            (escape(f"{t.name} (Grogs, an animal)"), t.id)
            for t in gt.animal_templates(saga)
        ]
    options += [
        (escape(choice_templates.option_label(t)), t.id)
        for t in choice_templates.templates(saga, kind)
    ]
    if kind == "companion":
        options += choice_forms.grog_companion_options(saga)
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


def character_create_live(values: dict[str, Any]) -> str:
    """The New Character form's line under its fields: the chosen
    Template described as it is picked."""
    kind = values.get("type") or ""
    template = character_templates.find(values.get(template_key(kind)))
    if template is not None:
        return character_templates.summary(template)
    grog = gt.find(values.get(template_key(kind)))
    if grog is not None:
        return (
            gt.summary(grog) + "\n[dim]Its choices come next: the character "
            "starts In Creation, built from them on the worksheet.[/]"
        )
    chosen = choice_templates.find(values.get(template_key(kind)))
    if chosen is not None:
        return (
            choice_templates.summary(chosen) + "\n[dim]Its choices come next: the "
            "character starts In Creation with those Virtues and Flaws, finished "
            "on the worksheet.[/]"
        )
    as_companion = choice_forms.grog_companion_find(values.get(template_key(kind)))
    if as_companion is not None:
        return (
            gt.summary(as_companion) + "\n[dim]Played as a companion: its choices "
            "come next, held to a companion's limits, with a Story Flaw added "
            "(Grogs, page 95).[/]"
        )
    if not character_templates.templates_for(kind) and choice_templates.templates(
        None, kind
    ):
        return (
            "[dim]None: the character starts In Creation, built step by step. "
            "A template asks for the book's choices first.[/]"
        )
    if not character_templates.any_for(kind):
        return "[dim]The book has no templates for this type.[/]"
    return (
        "[dim]None: the character starts In Creation, built step by step. "
        "A template is a ready-to-play character from the book.[/]"
    )


def blanks_fields(
    blanks: Sequence[str], filled: dict[str, str] | None = None
) -> list[DialogField]:
    """The names a sample childhood or training package leaves blank
    ("area", "second_area", "language"), one text field each, starting
    as `filled` says."""
    return [
        DialogField(
            blank,
            blank.replace("_", " ").capitalize(),
            "text",
            (filled or {}).get(blank, ""),
            required=True,
        )
        for blank in blanks
    ]


def grog_template_steps(
    saga: Saga,
    values: dict[str, Any],
    template: GrogTemplateDef,
    created: Callable[[Character], Any] = lambda _character: None,
) -> Form:
    """After New Character (`values`) chose a Grogs template: ask for its
    choices, then the names its Ability list leaves blank (the covenant's
    filled in), then make the grog and hand it to `created`."""

    def chosen(choices: gt.Choices) -> Form | None:
        def make(filled: dict[str, Any] | None = None) -> None:
            character = creation.add_character(
                saga, values["name"], "grog", values["covenant_id"]
            )
            gt.apply(saga, character, template, choices, filled)
            created(character)

        wanted = gt.blanks(template, choices)
        if not wanted:
            make()
            return None
        covenant = saga.covenant(values["covenant_id"])
        known = {"covenant": covenant.name} if covenant is not None else {}
        return Form(
            f"{escape(template.name)} template",
            lambda: blanks_fields(wanted, known),
            make,
            save_label="Use",
        )

    return grog_forms.grog_template_form(saga, template, chosen)


def new_character_form(
    saga: Saga, covenant_id: str | None, kind: str = "magus"
) -> Form:
    """Create a New Character, a `kind` to start with; a Template that
    leaves names blank asks for them next, and a Grogs template its
    choices first (cancelling either cancels the new character)."""

    def create(
        values: dict[str, Any],
        template: CharacterTemplateDef | None,
        filled: dict[str, Any] | None = None,
    ) -> None:
        character = creation.add_character(
            saga, values["name"], values["type"], values["covenant_id"]
        )
        if template is not None:
            character_templates.apply(saga, character, template, filled)

    def apply(values: dict[str, Any]) -> Form | None:
        grog = gt.find(values.get(template_key(values["type"])))
        if grog is not None:
            return grog_template_steps(saga, values, grog)
        chosen = choice_templates.find(values.get(template_key(values["type"])))
        if chosen is not None:
            return choice_forms.choice_template_steps(saga, values, chosen)
        as_companion = choice_forms.grog_companion_find(
            values.get(template_key(values["type"]))
        )
        if as_companion is not None:
            return choice_forms.grog_companion_steps(saga, values, as_companion)
        template = character_templates.find(values.get(template_key(values["type"])))
        wanted = character_templates.blanks(template) if template else []
        if template is None or not wanted:
            create(values, template)
            return None
        return Form(
            f"{escape(template.name)} template",
            lambda: blanks_fields(wanted),
            lambda filled: create(values, template, filled),
            save_label="Use",
        )

    return Form(
        "Create a New Character",
        lambda: character_create_fields(saga, covenant_id, kind),
        apply,
        live=character_create_live,
        save_label="Create",
    )


# -- New Laboratory --


def laboratory_create_fields(saga: Saga, covenant_id: str | None) -> list[DialogField]:
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
        covenant_field(saga, covenant_id),
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


def new_laboratory_form(
    saga: Saga, covenant_id: str | None, owner_id: str | None = None
) -> Form:
    """Create a laboratory; given `owner_id`, as that magus's sanctum."""
    owner = saga.character(owner_id)

    def apply(values: dict[str, Any]) -> None:
        lab = creation.add_laboratory(
            saga,
            values["name"],
            values["size"],
            values["covenant_id"],
            starting=values.get("starting", False),
        )
        if owner is not None:
            assign_laboratory_owner(saga, lab, owner.id)

    return Form(
        f"Create {escape(owner.name)}'s Sanctum"
        if owner is not None
        else "Create a New Laboratory",
        lambda: laboratory_create_fields(saga, covenant_id),
        apply,
        save_label="Create",
    )


# -- Bind Familiar --


def familiar_create_fields(saga: Saga, magus_id: str | None) -> list[DialogField]:
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
        DialogField(
            "bound",
            "Bound already",
            "check",
            True,
            hint="Untick to bind it by lab work: the bond's True Friend and "
            "Loyal (Partner) +3 come when that season is played (DE p. 267).",
        ),
    ]


def bind_familiar_form(saga: Saga, magus_id: str | None) -> Form:
    """Bind a New Familiar; `magus_id` the magus chosen to start with (one
    without a Familiar, or None)."""

    def apply(values: dict[str, Any]) -> None:
        magus = saga.character(values["character_id"])
        if magus is not None:
            fam.bind_familiar(
                saga, magus, values["name"], bound=bool(values.get("bound", True))
            )

    return Form(
        "Bind a New Familiar",
        lambda: familiar_create_fields(saga, magus_id),
        apply,
        save_label="Create",
    )
