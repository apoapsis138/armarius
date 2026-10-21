"""The choices form a Grogs template asks before it is used (New
Character, a grog from one of Grogs' Chapter 7 templates): its version,
age, Social Status, Virtues and Flaws, Characteristics and Personality
Traits, held to a grog's limits. The core's grog_templates.py turns the
values into Choices and fills the sheet.

Field keys: "variant"; per version i, "status_i", "age_i" and "vf_i_n"
(the book's own Virtues and Flaws, ticked); "pool_n" (a suggestion: a tick,
or a pick for the book's "X or Y"); "virtue_n" and "flaw_n" (any other
Minor Virtue or Flaw a grog may take); "characteristics"; "trait_n".
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import catalog
from .. import grog_templates as gt
from ..commands import Form
from ..form_spec import DialogField
from ..markup import escape
from ..models import Character, GrogTemplateDef, Saga, VirtueFlawInstance
from . import virtue as virtue_forms

#: How many other Virtues and Flaws the form offers beyond the book's.
MORE_VIRTUES, MORE_FLAWS = 2, 3
#: A check's label is cut to the form's label column.
LABEL_WIDTH = 30

ShowIf = Callable[[dict[str, Any]], bool] | None


def _shown_for(template: GrogTemplateDef, index: int) -> ShowIf:
    if len(gt.variants(template)) < 2:
        return None
    return lambda values: values.get("variant") == str(index)


def _label(text: str) -> str:
    if len(text) > LABEL_WIDTH:
        text = text[: LABEL_WIDTH - 1] + "…"
    return escape(text)


def _name(entry: dict[str, Any]) -> str:
    return catalog.describe_virtue_flaw(
        gt.instance(entry), catalog.load_virtue_flaw_catalog_by_id()
    )


def _note(key: str, text: str, show_if: ShowIf = None) -> DialogField:
    return DialogField(key, "", "info", text, show_if=show_if)


def template_fields(saga: Saga, template: GrogTemplateDef) -> list[DialogField]:
    """Every choice `template` offers, its book's own set ticked."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    found = list(gt.variants(template))
    fields: list[DialogField] = []
    if len(found) > 1:
        fields.append(
            DialogField(
                "variant",
                template.variant_label or "Version",
                "select",
                "0",
                options=[(escape(v.name), str(i)) for i, v in enumerate(found)],
            )
        )
    for i, variant in enumerate(found):
        shown = _shown_for(template, i)
        fields.append(
            DialogField(
                f"age_{i}",
                "Age",
                "select",
                "0",
                options=[
                    (escape(gt.age_label(entry)), str(j))
                    for j, entry in enumerate(variant.ages)
                ],
                hint="Sets the year born and the book's Ability list for that age.",
                show_if=shown,
            )
        )
        fields.append(
            DialogField(
                f"status_{i}",
                "Social Status",
                "select",
                variant.statuses[0],
                options=[(escape(by_id[s].name), s) for s in variant.statuses],
                show_if=shown,
            )
        )
    for i, variant in enumerate(found):
        if not variant.virtues_flaws:
            continue
        shown = _shown_for(template, i)
        fields.append(
            _note(
                f"book_{i}",
                "The book's Virtues and Flaws (untick one to leave it out)",
                shown,
            )
        )
        fields += [
            DialogField(
                f"vf_{i}_{n}", _label(_name(entry)), "check", True, show_if=shown
            )
            for n, entry in enumerate(variant.virtues_flaws)
        ]
    if template.pool:
        fields.append(_note("suggested", "The book also suggests"))
        for n, entry in enumerate(template.pool):
            if "one_of" in entry:
                fields.append(
                    DialogField(
                        f"pool_{n}",
                        _label(entry["label"]),
                        "select",
                        None,
                        options=[
                            (escape(_name(option)), str(k))
                            for k, option in enumerate(entry["one_of"])
                        ],
                        allow_blank=True,
                        placeholder="(none)",
                    )
                )
            else:
                fields.append(
                    DialogField(f"pool_{n}", _label(_name(entry)), "check", False)
                )
    fields += _more_fields(saga, template)
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
    for k, choice in enumerate(template.trait_choices):
        fields.append(
            DialogField(
                f"trait_{k}",
                "Personality Trait",
                "select",
                choice["options"][0],
                options=[(escape(o), o) for o in choice["options"]],
                hint=f"At {choice['score']:+d}.",
            )
        )
    return fields


def _more_fields(saga: Saga, template: GrogTemplateDef) -> list[DialogField]:
    """Pickers for any other Minor Virtue or Flaw a grog may take."""
    grog = Character(id="", name="", type="grog")
    by_id = catalog.load_virtue_flaw_catalog_by_id()

    def display(instance: VirtueFlawInstance) -> str:
        return catalog.describe_virtue_flaw(instance, by_id)

    def picker(key: str, side: str, hint: str = "") -> DialogField:
        return DialogField(
            key,
            f"Another {side}",
            "picker",
            None,
            allow_blank=True,
            placeholder=f"(choose a {side}...)",
            hint=hint,
            choose=lambda _current: virtue_forms.choose_virtue_flaw(saga, grog, side),
            display=display,
        )

    found = [picker(f"virtue_{n}", "Virtue") for n in range(MORE_VIRTUES)]
    hints = {v.flaw_hint for v in gt.variants(template) if v.flaw_hint}
    for n in range(MORE_FLAWS):
        hint = ""
        if n == 0:
            hint = (
                " ".join(sorted(hints)) or "A Minor Personality Flaw suits most grogs."
            )
        found.append(picker(f"flaw_{n}", "Flaw", escape(hint)))
    return found


def choices_from(template: GrogTemplateDef, values: dict[str, Any]) -> gt.Choices:
    """The form's values as the core's Choices."""
    found = gt.variants(template)
    index = int(values.get("variant") or 0)
    variant = found[index]
    chosen = [
        gt.instance(entry)
        for n, entry in enumerate(variant.virtues_flaws)
        if values.get(f"vf_{index}_{n}", True)
    ]
    for n, entry in enumerate(template.pool):
        value = values.get(f"pool_{n}")
        if "one_of" in entry:
            if value not in (None, ""):
                chosen.append(gt.instance(entry["one_of"][int(value)]))
        elif value:
            chosen.append(gt.instance(entry))
    for key in [f"virtue_{n}" for n in range(MORE_VIRTUES)] + [
        f"flaw_{n}" for n in range(MORE_FLAWS)
    ]:
        if isinstance(values.get(key), VirtueFlawInstance):
            chosen.append(values[key])
    traits = [(name, score) for name, score in template.traits]
    for k, choice in enumerate(template.trait_choices):
        traits.append(
            (values.get(f"trait_{k}") or choice["options"][0], choice["score"])
        )
    traits.sort(key=lambda trait: -trait[1])
    return gt.Choices(
        variant=index,
        age=int(values.get(f"age_{index}") or 0),
        status=values.get(f"status_{index}") or variant.statuses[0],
        virtues_flaws=chosen,
        characteristics=bool(values.get("characteristics", False)),
        traits=traits,
    )


def template_live(template: GrogTemplateDef) -> Callable[[dict[str, Any]], str]:
    """The lines under the form: the template, the age's xp against its
    Ability list, the Virtue and Flaw points so far, and the book's
    notes (a broken limit is the form's own refusal)."""

    def live(values: dict[str, Any]) -> str:
        choices = choices_from(template, values)
        variant = gt.variants(template)[choices.variant]
        age = variant.ages[choices.age]["age"]
        lines = [
            f"[b]{escape(template.name)}[/] (Grogs, page {template.page}): "
            + escape(template.concept),
            escape(
                f"At {age}: {gt.age_xp(age)} xp before Virtues; the book's list "
                f"comes to {gt.list_xp(template, choices)} xp."
            ),
            escape(gt.tally_line(choices.all_virtues_flaws())),
        ]
        if template.notes:
            lines.append(f"[dim]{escape(template.notes)}[/]")
        return "\n".join(lines)

    return live


def grog_template_form(
    saga: Saga,
    template: GrogTemplateDef,
    then: Callable[[gt.Choices], Any],
) -> Form:
    """Ask for `template`'s choices, then call `then` with them."""
    return Form(
        f"{escape(template.name)} template",
        lambda: template_fields(saga, template),
        lambda values: then(choices_from(template, values)),
        validate=lambda values: gt.limit_problem(
            choices_from(template, values).all_virtues_flaws()
        ),
        live=template_live(template),
        save_label="Next",
        help_id="grog-templates",
    )
