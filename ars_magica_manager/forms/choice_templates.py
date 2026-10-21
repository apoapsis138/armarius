"""The choices form a choice template asks before it is used (New
Character, from one of choice_templates' recipes): its version, each
slot's pick, the Flaw and the Social Status, held to the limits of the
template's character type. The core's choice_templates.py turns the
values into Choices and fills the sheet.

Field keys: "variant"; "flaw"; "status"; per version i, "slot_i_n" for
each slot that asks for something (an Ability, an Art, which Virtue, or
typed text); "virtue_n" and "flaw_n" (other Virtues and Flaws of the
player's own); "abilities" (the book's minimum Abilities, ticked) and
"blank_<name>" for each name they leave blank.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import catalog, creation
from .. import choice_templates as ct
from .. import grog_templates as gt
from ..commands import Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, GrogTemplateDef, Saga, VirtueFlawInstance
from . import grog_templates as grog_forms
from . import virtue as virtue_forms

ShowIf = Callable[[dict[str, Any]], bool] | None

#: Each kind of template's help page.
HELP_IDS: dict[str, str] = {
    "quick": "quick-virtues-flaws",
    "mythic": "mythic-companion-templates",
    "sample": "companion-sample-templates",
}
#: A check's label is cut to the form's label column.
LABEL_WIDTH = 30


def _shown_for(template: ct.ChoiceTemplateDef, index: int) -> ShowIf:
    if len(ct.variants(template)) < 2:
        return None
    return lambda values: values.get("variant") == str(index)


def _select(
    key: str,
    label: str,
    options: list[tuple[str, str]],
    show_if: ShowIf = None,
    hint: str = "",
) -> DialogField:
    return DialogField(
        key,
        label,
        "select",
        None,
        options=options,
        required=True,
        allow_blank=True,
        placeholder="(choose one)",
        hint=hint,
        show_if=show_if,
    )


def _slot_field(
    saga: Saga,
    template: ct.ChoiceTemplateDef,
    key: str,
    slot: dict[str, Any],
    show_if: ShowIf,
) -> DialogField | None:
    kind, hint = slot["kind"], escape(slot.get("hint", ""))
    if kind in ("text",) or (kind == "ability" and slot.get("free")):
        return DialogField(
            key, slot["label"], "text", "", required=True, hint=hint, show_if=show_if
        )
    if kind == "ability":
        options = [(escape(n), n.lower()) for n in ct.ability_options(slot)]
    elif kind == "art":
        options = [(escape(n), n.lower()) for n in ct.ART_GROUPS[slot["group"]]]
    elif kind == "one_of":
        options = [
            (escape(e.name), e.id) for e in ct.one_of_options(saga, slot, template.type)
        ]
    elif kind == "supernatural":
        options = [
            (escape(e.name), e.id) for e in ct.supernatural_options(saga, template.type)
        ]
    elif kind in ("virtue", "flaw"):
        by_id = catalog.load_virtue_flaw_catalog_by_id()
        options = [
            (
                escape(catalog.describe_virtue_flaw(VirtueFlawInstance(e.id), by_id)),
                e.id,
            )
            for e in ct.tier_options(saga, slot, template.type)
        ]
        made = _select(key, slot["label"], options, show_if, hint)
        made.value = slot.get("default")
        return made
    else:
        return None
    return _select(key, slot["label"], options, show_if, hint)


def _more_fields(saga: Saga, template: ct.ChoiceTemplateDef) -> list[DialogField]:
    """Pickers for other Virtues and Flaws of the player's own."""
    who = Character(id="", name="", type=template.type)  # type: ignore[arg-type]
    by_id = catalog.load_virtue_flaw_catalog_by_id()

    def display(instance: VirtueFlawInstance) -> str:
        return catalog.describe_virtue_flaw(instance, by_id)

    def picker(key: str, side: str) -> DialogField:
        return DialogField(
            key,
            f"Another {side}",
            "picker",
            None,
            allow_blank=True,
            placeholder=f"(choose a {side}...)",
            choose=lambda _current: virtue_forms.choose_virtue_flaw(saga, who, side),
            display=display,
        )

    return [picker(f"virtue_{n}", "Virtue") for n in range(template.more_virtues)] + [
        picker(f"flaw_{n}", "Flaw") for n in range(template.more_flaws)
    ]


def _label(text: str) -> str:
    """A check's label, cut to the form's label column."""
    if len(text) > LABEL_WIDTH:
        text = text[: LABEL_WIDTH - 1] + "…"
    return escape(text)


def _book_fields(template: ct.ChoiceTemplateDef) -> list[DialogField]:
    """A sample's own Virtues and Flaws, ticked, and its Characteristics."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    fields: list[DialogField] = []
    if template.virtues_flaws:
        fields.append(
            DialogField(
                "book",
                "",
                "info",
                "The book's Virtues and Flaws (untick one to leave it out)",
            )
        )
        for n, vf in enumerate(template.virtues_flaws):
            name = catalog.describe_virtue_flaw(
                VirtueFlawInstance(vf["vf_id"], dict(vf.get("params", {}))), by_id
            )
            fields.append(DialogField(f"vf_{n}", _label(name), "check", True))
    if template.characteristics:
        figures = ", ".join(
            f"{key[:3].title()} {score:+d}"
            for key, score in template.characteristics.items()
        )
        fields.append(
            DialogField(
                "characteristics",
                "The book's Characteristics",
                "check",
                True,
                hint=escape(figures),
            )
        )
    return fields


def _ability_fields(template: ct.ChoiceTemplateDef) -> list[DialogField]:
    """The book's minimum Abilities, ticked, and a field for each name they
    leave blank."""
    if not template.abilities:
        return []
    if template.kind == "sample":
        total = sum(xp for _, xp in ct.ability_rows(template))
        label, what = (
            "The book's Abilities",
            f"{len(template.abilities)} Abilities ({total} xp)",
        )
    else:
        label, what = "The book's minimum Abilities", ct.abilities_text(template)
    fields = [
        DialogField(
            "abilities",
            label,
            "check",
            True,
            hint=escape(f"{what}, put on the worksheet."),
        )
    ]
    for blank in ct.blanks(template):
        fields.append(
            DialogField(
                f"blank_{blank}",
                blank.replace("_", " ").capitalize(),
                "text",
                "",
                required=True,
                show_if=lambda values: bool(values.get("abilities", True)),
            )
        )
    return fields


def template_fields(saga: Saga, template: ct.ChoiceTemplateDef) -> list[DialogField]:
    """Every choice `template` offers, the first Social Status chosen to
    start with."""
    found = ct.variants(template)
    fields: list[DialogField] = []
    if len(found) > 1:
        fields.append(
            DialogField(
                "variant",
                template.variant_label or "Version",
                "select",
                "0",
                options=[(escape(v["name"]), str(i)) for i, v in enumerate(found)],
            )
        )
    for i in range(len(found)):
        shown = _shown_for(template, i)
        for n, slot in enumerate(ct.slots(template, i)):
            made = _slot_field(saga, template, f"slot_{i}_{n}", slot, shown)
            if made is not None:
                fields.append(made)
    if template.flaw:
        words = ct.flaw_words(template)
        fields.append(
            _select(
                "flaw",
                f"{template.flaw.get('tier', 'Major')} Flaw",
                [(escape(e.name), e.id) for e in ct.flaw_options(saga, template)],
                hint=escape(
                    f"{words[0].upper()}{words[1:]}: how the character is played."
                ),
            )
        )
    fields += _book_fields(template)
    fields += _more_fields(saga, template)
    fields += _ability_fields(template)
    fields.append(
        DialogField(
            "status",
            "Social Status",
            "select",
            ct.default_status(saga, template),
            options=[(escape(e.name), e.id) for e in ct.status_options(saga, template)],
        )
    )
    return fields


def choices_from(template: ct.ChoiceTemplateDef, values: dict[str, Any]) -> ct.Choices:
    """The form's values as the core's Choices."""
    index = int(values.get("variant") or 0)
    picks = [
        values.get(f"slot_{index}_{n}") or ""
        for n, _ in enumerate(ct.slots(template, index))
    ]
    more = [
        values[key]
        for key in [f"virtue_{n}" for n in range(template.more_virtues)]
        + [f"flaw_{n}" for n in range(template.more_flaws)]
        if isinstance(values.get(key), VirtueFlawInstance)
    ]
    return ct.Choices(
        variant=index,
        status=values.get("status") or ct.default_status(None, template),
        flaw=values.get("flaw") or "",
        picks=picks,
        more=more,
        abilities=bool(values.get("abilities", True)),
        blanks={
            blank: values.get(f"blank_{blank}") or ""
            for blank in ct.blanks(template)
            if values.get(f"blank_{blank}")
        },
        dropped={
            n
            for n in range(len(template.virtues_flaws))
            if not values.get(f"vf_{n}", True)
        },
        characteristics=bool(values.get("characteristics", True)),
    )


def template_live(template: ct.ChoiceTemplateDef) -> Callable[[dict[str, Any]], str]:
    """The lines under the form: the template and the Virtue and Flaw
    points so far (a broken limit is the form's own refusal)."""

    def live(values: dict[str, Any]) -> str:
        chosen = ct.chosen(template, choices_from(template, values))
        lines = [
            f"[b]{escape(template.name)}[/] ({escape(ct.where(template))}): "
            + escape(template.concept),
            escape(ct.tally_line(template, chosen)),
        ]
        if template.age and template.abilities:
            listed = sum(xp for _, xp in ct.ability_rows(template))
            lines.append(
                escape(
                    f"At {template.age}: {gt.age_xp(template.age)} xp before "
                    f"Virtues; the book's Abilities come to {listed} xp."
                )
            )
        if template.notes:
            lines.append(f"[dim]{escape(template.notes)}[/]")
        # A book's character lists many small differences: those go in its
        # Biography, not under the form.
        if template.fixes and template.kind != "sample":
            lines.append(f"[dim]{escape(' '.join(template.fixes))}[/]")
        return "\n".join(lines)

    return live


def choice_template_form(
    saga: Saga,
    template: ct.ChoiceTemplateDef,
    then: Callable[[ct.Choices], Any],
) -> Form:
    """Ask for `template`'s choices, then call `then` with them."""
    return Form(
        escape(template.name),
        lambda: template_fields(saga, template),
        lambda values: then(choices_from(template, values)),
        validate=lambda values: ct.limit_problem(
            template, ct.chosen(template, choices_from(template, values))
        ),
        live=template_live(template),
        save_label="Use",
        help_id=HELP_IDS[template.kind],
    )


def choice_template_steps(
    saga: Saga,
    values: dict[str, Any],
    template: ct.ChoiceTemplateDef,
    created: Callable[[Character], Any] = lambda _character: None,
) -> Form:
    """After New Character (`values`) chose a choice template: ask for
    its choices, then make the character and hand it to `created`.
    Cancelling makes nothing."""

    def make(choices: ct.Choices) -> None:
        character = creation.add_character(
            saga,
            values["name"],
            template.type,  # type: ignore[arg-type]
            values["covenant_id"],
        )
        ct.apply(saga, character, template, choices)
        created(character)

    return choice_template_form(saga, template, make)


# -- a Grogs template played as a companion --

#: New Character's Template value for a Grogs template played as a
#: companion: this prefix and the template's id.
GROG_COMPANION = "ctg:"


def grog_companion_options(saga: Saga) -> list[tuple[str, str]]:
    """The Grogs templates, offered for a companion while Grogs is in play."""
    return [
        (escape(f"{t.name} (Grogs, as a companion)"), GROG_COMPANION + t.id)
        for t in gt.templates(saga)
    ]


def grog_companion_find(value: str | None) -> GrogTemplateDef | None:
    if not value or not value.startswith(GROG_COMPANION):
        return None
    return gt.find(value.removeprefix(GROG_COMPANION))


def _grog_companion_fields(saga: Saga, template: GrogTemplateDef) -> list[DialogField]:
    """The Grogs template's own choices form, its Another Virtue and
    Another Flaw pickers choosing as a companion (so a Major Story Flaw
    is offered)."""
    companion = ct.ChoiceTemplateDef(
        id="",
        name="",
        type="companion",
        more_virtues=grog_forms.MORE_VIRTUES,
        more_flaws=grog_forms.MORE_FLAWS,
    )
    pickers = {f.key: f for f in _more_fields(saga, companion)}
    fields = []
    for f in grog_forms.template_fields(saga, template):
        if f.key in pickers:
            picker = pickers[f.key]
            picker.hint = (
                escape("A Story Flaw makes the grog a companion.")
                if (f.key == "flaw_0")
                else f.hint
            )
            fields.append(picker)
        else:
            fields.append(f)
    return fields


def _grog_companion_live(template: GrogTemplateDef, values: dict[str, Any]) -> str:
    """The Grogs template's own lines under the form, its points counted
    against a companion's limits."""
    chosen = grog_forms.choices_from(template, values).all_virtues_flaws()
    companion = ct.ChoiceTemplateDef(id="", name="", type="companion")
    return grog_forms.template_live(template)(values).replace(
        escape(gt.tally_line(chosen)), escape(ct.tally_line(companion, chosen))
    )


def grog_companion_steps(
    saga: Saga,
    values: dict[str, Any],
    template: GrogTemplateDef,
    created: Callable[[Character], Any] = lambda _character: None,
) -> Form:
    """After New Character (`values`) chose a Grogs template for a
    companion: its choices, held to a companion's limits with a Story Flaw
    added, then the names its Ability list leaves blank, then the
    companion. Cancelling either form makes nothing."""

    def chosen(choices: gt.Choices) -> Form | None:
        def make(filled: dict[str, Any] | None = None) -> None:
            character = creation.add_character(
                saga, values["name"], "companion", values["covenant_id"]
            )
            gt.apply(saga, character, template, choices, filled)
            ct.after_grog_apply(character, template)
            created(character)

        wanted = gt.blanks(template, choices)
        if not wanted:
            make()
            return None
        covenant = saga.covenant(values["covenant_id"])
        known = {"covenant": covenant.name} if covenant is not None else {}
        return Form(
            f"{escape(template.name)} template",
            lambda: [
                DialogField(
                    blank,
                    blank.replace("_", " ").capitalize(),
                    "text",
                    known.get(blank, ""),
                    required=True,
                )
                for blank in wanted
            ],
            make,
            save_label="Use",
        )

    return Form(
        f"{escape(template.name)} as a companion",
        lambda: _grog_companion_fields(saga, template),
        lambda form_values: chosen(grog_forms.choices_from(template, form_values)),
        validate=lambda form_values: ct.grog_companion_problem(
            grog_forms.choices_from(template, form_values).all_virtues_flaws()
        ),
        live=lambda form_values: _grog_companion_live(template, form_values),
        save_label="Next",
        help_id="grog-template-companion",
    )
