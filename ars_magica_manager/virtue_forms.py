"""Virtues and Flaws, independent of how they are drawn: adding one from
the catalog (choose it, then fill in what it names: "Affinity with
{art}") and deleting one, for a character, a familiar or a laboratory
(commands.SectionOps). They can't be edited, only added and deleted.

A character and a familiar choose from the character catalog, each entry
checked against who is choosing (catalog.VirtueFlawChooser) and what
they hold already; a character's Great or Poor (Characteristic) moves
the Characteristic it names as it is added or deleted. A laboratory
chooses from its own catalog (ArM5 Covenants, Chapter 9); deleting a
Feature Virtue takes its Feature too.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from . import catalog, sourcebooks
from . import laboratories as lab_rules
from .arts import ARTS, FORMS, TECHNIQUES
from .commands import Choice, Choose, Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .markup import escape
from .models import (
    FOCUS_FLAWS,
    Character,
    Familiar,
    Laboratory,
    LabVirtueFlawDef,
    Saga,
    VirtueFlawDef,
    VirtueFlawInstance,
    link_unlinked_features,
    new_instance_id,
)
from .rules import creation_characteristics as cch

Owner = Character | Familiar | Laboratory

#: The eight Characteristics, as a Virtue or Flaw's {characteristic}.
CHARACTERISTIC_NAMES: tuple[str, ...] = (
    "Intelligence",
    "Perception",
    "Strength",
    "Stamina",
    "Presence",
    "Communication",
    "Dexterity",
    "Quickness",
)

#: The four realms, as a Virtue or Flaw's {realm}.
REALM_NAMES: tuple[str, ...] = ("Divine", "Faerie", "Infernal", "Magic")

#: The kinds of Faerie Blood (the Definitive Edition's and Realms of
#: Power: Faerie's), as a {blood}.
BLOOD_NAMES: tuple[str, ...] = (
    "Bee King",
    "Bloodcap",
    "Brownie",
    "Dwarf",
    "Ettin",
    "Faerie God",
    "Ghul",
    "Goblin",
    "Huldra",
    "Nymph",
    "Padfoot",
    "Satyr",
    "Selkie",
    "Sidhe",
    "Spinnen",
    "Undine",
)

#: Parameters that may be left blank: (label, placeholder).
OPTIONAL_PARAMS: dict[str, tuple[str, str]] = {
    "favored": (
        "Favoured Craft or Profession",
        "Dwarf or Brownie Blood only, e.g. Craft: Smith",
    ),
}

#: An Add list's title, by the side it lists (None: both).
ADD_TITLES: dict[str | None, str] = {
    "Virtue": "Add a Virtue",
    "Flaw": "Add a Flaw",
    None: "Add a Virtue or Flaw",
}


def param_choices(
    entry: VirtueFlawDef,
    taken: Sequence[VirtueFlawInstance] = (),
    own_abilities: Sequence[str] = (),
) -> dict[str, list[tuple[str, str]]]:
    """The valid values of each of `entry`'s parameters that name a
    Characteristic, an Ability, an Art, a Technique, a Form, a realm or a
    kind of Faerie Blood,
    as (label, stored value) pairs; other parameters are typed. A value
    the character already holds this entry for, as often as the book
    allows, is left out."""
    named: dict[str, Sequence[str]] = {
        "characteristic": CHARACTERISTIC_NAMES,
        "art": ARTS,
        "technique": TECHNIQUES,
        "form": FORMS,
        "realm": REALM_NAMES,
        "blood": BLOOD_NAMES,
    }
    found: dict[str, list[tuple[str, str]]] = {}
    for param in entry.parameters:
        if param == "ability":
            listed = {
                d.name for d in catalog.load_ability_catalog() if not d.parameters
            }
            choices: Sequence[str] = sorted(listed | set(own_abilities))
        elif param in named:
            choices = named[param]
        else:
            continue
        single = len(entry.parameters) == 1
        found[param] = [
            (escape(name), name.lower())
            for name in choices
            if not single
            or not catalog.virtue_flaw_repeat_refusal(
                entry, taken, {param: name.lower()}
            )
        ]
    return found


def param_fields(
    parameters: Sequence[str],
    choices: dict[str, list[tuple[str, str]]] | None = None,
) -> list[DialogField]:
    """Fill in a catalog entry's {placeholders} ("Affinity with {art}"): a
    parameter with `choices` is picked from them; the rest are typed.
    params_from reads the values."""
    choices = choices or {}

    def field(param: str) -> DialogField:
        if param in choices:
            return DialogField(
                param,
                param.title(),
                "select",
                None,
                options=choices[param],
                required=True,
                allow_blank=True,
                placeholder=f"(choose the {param})",
            )
        if param in OPTIONAL_PARAMS:
            label, hint = OPTIONAL_PARAMS[param]
            return DialogField(param, label, "text", "", placeholder=hint)
        return DialogField(
            param, param.title(), "text", "", required=True, placeholder="e.g. Creo"
        )

    return [field(param) for param in parameters]


def params_from(parameters: Sequence[str], values: dict[str, Any]) -> dict[str, str]:
    """{parameter: value} from param_fields' values, lower-cased."""
    return {param: values[param].lower() for param in parameters}


def lab_choice_fields(entry: LabVirtueFlawDef) -> list[DialogField]:
    """Choose the Specialization a laboratory Virtue or Flaw grants points
    to, from the ones its catalog entry allows."""
    return [
        DialogField(
            param,
            "Specialization",
            "select",
            None,
            options=pairs(options),
            required=True,
            allow_blank=True,
            placeholder="(choose one)",
            hint=f"{entry.name} grants its points to the one you choose.",
        )
        for param, options in entry.choices.items()
    ]


# -- which instances a side lists --


def _catalog_by_id(owner: Owner) -> dict[str, Any]:
    if isinstance(owner, Laboratory):
        return dict(catalog.load_lab_virtue_flaw_catalog_by_id())
    return dict(catalog.load_virtue_flaw_catalog_by_id())


def _side_of(definition: Any) -> str:
    """ "Virtue" or "Flaw": a character entry's side (a Quality is a
    Virtue), a laboratory entry's type."""
    return definition.side if isinstance(definition, VirtueFlawDef) else definition.type


def side_indices(owner: Owner, side: str | None) -> list[int]:
    """The indices into `owner.virtues_flaws` of the side's instances (all
    of them for None), in the order taken; an instance not in the catalog
    is on neither side."""
    by_id = _catalog_by_id(owner)
    found = []
    for index, instance in enumerate(owner.virtues_flaws):
        definition = by_id.get(instance.vf_id)
        if side is None or (definition is not None and _side_of(definition) == side):
            found.append(index)
    return found


def vf_name(owner: Owner, index: int) -> str:
    """The owner's Virtue/Flaw at `index`, named with its parameters."""
    return catalog.describe_virtue_flaw(
        owner.virtues_flaws[index], _catalog_by_id(owner)
    )


# -- adding --


class _Adder:
    """Adding a character or familiar Virtue/Flaw: what is offered, and
    why one is refused."""

    def __init__(self, saga: Saga, owner: Character | Familiar, side: str | None):
        self.saga, self.owner, self.side = saga, owner, side
        books = sourcebooks.saga_books(saga)
        self.chooser = (
            catalog.VirtueFlawChooser.for_familiar(owner, books)
            if isinstance(owner, Familiar)
            else catalog.VirtueFlawChooser.for_character(owner, books)
        )

    def instance_refusal(self, instance: VirtueFlawInstance) -> str:
        """Why the owner can't take `instance`, from their own scores
        ("" if they can): only a character's are checked."""
        if isinstance(self.owner, Character):
            return cch.virtue_refusal(self.saga, self.owner, instance)
        return ""

    def choices(self, entry: VirtueFlawDef) -> dict[str, list[tuple[str, str]]]:
        """The parameter choices offered for `entry`: a lone parameter's
        values the owner's own refusal turns down are left out."""
        found = param_choices(
            entry, self.owner.virtues_flaws, [a.name for a in self.owner.abilities]
        )
        if isinstance(self.owner, Character) and len(entry.parameters) == 1:
            param = entry.parameters[0]
            if param in found:
                found[param] = [
                    (label, value)
                    for label, value in found[param]
                    if not self.instance_refusal(
                        VirtueFlawInstance(entry.id, {param: value})
                    )
                ]
        return found

    def no_choice_left(self, entry: VirtueFlawDef) -> bool:
        """Whether the owner's own refusal turns down every value of the
        entry's lone Characteristic."""
        if not isinstance(self.owner, Character) or list(entry.parameters) != [
            "characteristic"
        ]:
            return False
        return not self.choices(entry).get("characteristic")

    def offered(self) -> list[VirtueFlawDef]:
        """The entries the owner may take, on the side asked for: not taken
        already (unless repeatable), allowed them (catalog.VirtueFlawChooser),
        from a book in play and not hidden."""
        taken = self.owner.virtues_flaws
        return [
            entry
            for entry in catalog.load_virtue_flaw_catalog()
            if self.side in (None, entry.side)
            and catalog.virtue_flaw_offerable(entry, taken)
            and not self.chooser.refusal(entry)
            and not self.no_choice_left(entry)
        ]

    def refusal(self, entry: VirtueFlawDef, params: dict[str, str]) -> str:
        """Why the owner can't take `entry` with `params` ("" if they can):
        a repeat the book doesn't allow, or their own scores."""
        return catalog.virtue_flaw_repeat_refusal(
            entry, self.owner.virtues_flaws, params
        ) or self.instance_refusal(VirtueFlawInstance(entry.id, params))

    def add(self, entry: VirtueFlawDef, params: dict[str, str]) -> None:
        instance = VirtueFlawInstance(vf_id=entry.id, params=params)
        self.owner.virtues_flaws.append(instance)
        if isinstance(self.owner, Character):
            cch.apply_virtue(self.saga, self.owner, instance)

    def chosen(self, entry: VirtueFlawDef) -> Command | None:
        if not entry.parameters:
            if why := self.refusal(entry, {}):
                return Refuse(escape(entry.name), escape(why))
            self.add(entry, {})
            return None

        def problem(values: dict[str, Any]) -> str | None:
            return self.refusal(entry, params_from(entry.parameters, values)) or None

        return Form(
            escape(entry.name),
            lambda: param_fields(entry.parameters, self.choices(entry)),
            lambda values: self.add(entry, params_from(entry.parameters, values)),
            validate=problem,
            save_label="Confirm",
        )


def virtue_flaw_choice(entry: VirtueFlawDef) -> Choice:
    """A character catalog entry as the Add list offers it: its name, tier,
    type and what it needs naming; its book text beside the list."""
    needs = f"  (needs: {', '.join(entry.parameters)})" if entry.parameters else ""
    facts = f"{entry.tier} {entry.type}, {entry.category_label}"
    text = entry.description or entry.summary
    return Choice(
        escape(f"{entry.name}  [{facts}]{needs}"),
        entry,
        f"[dim]{escape('Source: ' + entry.source)}[/]\n{escape(text)}",
        f"{entry.type} {entry.category_label} {entry.tier} {entry.summary}",
    )


def lab_virtue_flaw_choice(entry: LabVirtueFlawDef) -> Choice:
    return Choice(
        escape(f"{entry.name}  [{entry.type}, {entry.tier}, cost {entry.cost}]"),
        entry,
        lab_rules.vf_entry_text(entry),
        f"{entry.type} {entry.category} {entry.tier}",
    )


def _lab_add(saga: Saga, lab: Laboratory, side: str | None) -> Choose:
    books = sourcebooks.saga_books(saga)
    held = {vf.vf_id for vf in lab.virtues_flaws}

    def add(entry: LabVirtueFlawDef, params: dict[str, str]) -> None:
        # A Feature waiting for a Virtue gets a new Feature Virtue.
        lab.virtues_flaws.append(
            VirtueFlawInstance(vf_id=entry.id, params=params, id=new_instance_id())
        )
        link_unlinked_features(lab)

    def chosen(entry: LabVirtueFlawDef) -> Command | None:
        if not entry.choices:
            add(entry, {})
            return None
        return Form(
            escape(entry.name),
            lambda: lab_choice_fields(entry),
            lambda values: add(
                entry, {param: values[param] for param in entry.choices}
            ),
            save_label="Confirm",
        )

    def offered() -> list[Choice]:
        return [
            lab_virtue_flaw_choice(entry)
            for entry in catalog.load_lab_virtue_flaw_catalog()
            if side in (None, entry.type)
            and (entry.repeatable or entry.id not in held)
            and sourcebooks.in_play(entry.source, books)
            and not catalog.hidden(entry)
        ]

    title = {
        "Virtue": "Add a Laboratory Virtue",
        "Flaw": "Add a Laboratory Flaw",
        None: "Add a Laboratory Virtue or Flaw",
    }[side]
    return Choose(title, offered, chosen, empty="(no more Virtues/Flaws available)")


# -- deleting --


def _remove(saga: Saga, owner: Owner, index: int) -> Confirm:
    """Delete the owner's Virtue/Flaw at `index` after confirming, saying
    what goes with it: a character's Characteristic point, a laboratory's
    Feature or Focus."""
    name = vf_name(owner, index)
    instance = owner.virtues_flaws[index]
    if isinstance(owner, Laboratory):
        return _remove_lab(owner, index, name)
    if isinstance(owner, Character):
        change = cch.removal_change(saga, owner, instance)
        if change is not None:
            characteristic, before, after = change

            def stepped() -> None:
                cch.unapply_virtue(saga, owner, instance)
                del owner.virtues_flaws[index]

            return Confirm(
                f"Delete {escape(name)}? {characteristic} goes from {before:+d} "
                f"to {after:+d}.",
                stepped,
            )

    def apply() -> None:
        del owner.virtues_flaws[index]

    return Confirm(f"Delete {escape(name)}?", apply)


def _remove_lab(lab: Laboratory, index: int, name: str) -> Confirm:
    instance = lab.virtues_flaws[index]
    feature = lab_rules.feature_on(lab, instance)
    focus = lab_rules.focus_feature(lab)
    message = f"Delete {escape(name)}?"
    if feature is not None:
        message += f" Its Feature, {escape(feature.name)}, goes too."
    elif instance.vf_id in FOCUS_FLAWS and focus is not None:
        message += (
            f" {escape(focus.name)} stops being the Focus and loses its Focus points."
        )

    def apply() -> None:
        counted = lab_rules.counted_specializations(lab)
        del lab.virtues_flaws[index]
        lab_rules.prune_features(lab)
        lab_rules.reconcile_dropped(lab, counted)

    return Confirm(message, apply)


# -- a section's ops --


def virtue_flaw_ops(saga: Saga, owner: Owner, side: str | None = None) -> SectionOps:
    """Add and Delete for the owner's Virtues or Flaws (`side`: "Virtue"
    or "Flaw"; None: both in one list). Edit and Delete's row is an index
    into the side's own list (side_indices), in the order taken."""

    def add() -> Choose:
        if isinstance(owner, Laboratory):
            return _lab_add(saga, owner, side)
        adder = _Adder(saga, owner, side)
        return Choose(
            ADD_TITLES[side],
            lambda: [virtue_flaw_choice(entry) for entry in adder.offered()],
            adder.chosen,
            empty="(no more Virtues/Flaws available)",
        )

    def remove(row: int) -> Confirm:
        return _remove(saga, owner, side_indices(owner, side)[row])

    return SectionOps(
        add=add,
        remove=remove,
        rows=lambda: [vf_name(owner, index) for index in side_indices(owner, side)],
    )
