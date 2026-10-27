"""Saga Content's Mystery Cults tab, independent of how it is drawn: the
saga's own cults, the chosen cult's facts, its degrees and the chosen
degree's Script, as the terminal's rows and the desktop's entries; their
details; Add, Edit and Delete on each; and More's Experiment on a Script.

Which cult and degree are chosen is the front-end's to keep: the ops take
callables answering it. The rules are mystery_cults.py's; this module
words them and builds the forms (FieldsDialogs, from the `_*_fields`
builders here).
"""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .. import mystery_cults as mc
from ..commands import Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, attr, pairs
from ..markup import escape, fit
from ..models import (
    TRADITION_REALMS,
    Character,
    CultComponent,
    CultDegree,
    CultScript,
    MysteryCult,
    Saga,
)
from ..models.mystery_cults import (
    COMPONENT_KINDS,
    CULT_ANYONE,
    CULT_CHARACTERISTICS,
    CULT_GIFTED,
    FIRST_LORE,
    FLAW_KINDS,
    LATER_LORE,
    ORDEAL_KINDS,
    needs_lore_ability,
)
from ..rules import mysteries
from ..sections import (
    CULT_DEGREES_SECTION,
    CULT_SCRIPT_SECTION,
    CULTS_SECTION,
)

T = mc.TMRE
#: Who-may-join choices.
WHO = {
    CULT_GIFTED: "Hermetic magi",
    CULT_ANYONE: "Anyone (unGifted need an Ordeal)",
}
#: The Script form's Ordeal choices: the component kind, by size.
ORDEALS = {"minor": "ordeal_minor", "medium": "ordeal_medium", "major": "ordeal_major"}
ORDEAL_LABELS = [
    ("Minor: a Minor Flaw (+3)", "minor"),
    ("Medium: a Minor Flaw made Major (+6)", "medium"),
    ("Major: a Major Flaw (+9)", "major"),
]
#: Column widths: the cults list, the degrees list, the Script's.
CULT_WIDTHS = (20, 20, 8, 15)
DEGREE_WIDTHS = (18, 24, 10)
#: The Script's name, last on a degree's row: cut to fit 120 columns.
SCRIPT_WIDTH = 20
COMPONENT_WIDTHS = (44, 23)

EMPTY_PANEL = "[dim]Choose a cult, a degree or a component.[/]"

Chosen = Callable[[], int | None]


def _cell(text: str, width: int) -> str:
    """One column: the text cut to leave a space before the next."""
    return fit(text, width - 1) + " "


def _at[X](items: list[X], index: int | None) -> X | None:
    return items[index] if index is not None and 0 <= index < len(items) else None


def chosen_cult(saga: Saga, cult: Chosen) -> MysteryCult | None:
    """The cult chosen, or the first when none is (a tab opens on it)."""
    found = _at(saga.custom_cults, cult())
    return found or (saga.custom_cults[0] if saga.custom_cults else None)


def chosen_degree(
    saga: Saga, cult: Chosen, degree: Chosen
) -> tuple[MysteryCult, CultDegree] | None:
    """The chosen cult's chosen degree (its first when none is)."""
    found = chosen_cult(saga, cult)
    if found is None or not found.degrees:
        return None
    return found, _at(found.degrees, degree()) or found.degrees[0]


# -- the cults -------------------------------------------------------------------


def cults_title(saga: Saga) -> str:
    return f"The Saga's Mystery Cults ({len(saga.custom_cults)})"


def cults_header() -> str:
    return "  " + "".join(
        _cell(t, w)
        for t, w in zip(("Cult", "Lore", "Realm", "Founder"), CULT_WIDTHS, strict=True)
    )


def _degrees_words(cult: MysteryCult) -> str:
    n = len(cult.degrees)
    return f"{n} degree{'s' if n != 1 else ''}"


def cult_rows(saga: Saga) -> list[tuple[int | None, str]]:
    rows: list[tuple[int | None, str]] = [
        (
            i,
            "".join(
                escape(_cell(text, width))
                for text, width in zip(
                    (c.name, c.lore, c.realm, mc.founder_name(saga, c)),
                    CULT_WIDTHS,
                    strict=True,
                )
            )
            + _degrees_words(c),
        )
        for i, c in enumerate(saga.custom_cults)
    ]
    return rows or [
        (
            None,
            "[dim]None yet: a adds one. A new cult starts with its Lore at 0 for "
            f"its founders ({T} pp. 18-19).[/]",
        )
    ]


def founded_words(saga: Saga, cult: MysteryCult) -> str:
    founder = mc.founder_name(saga, cult)
    if cult.founded is not None and founder:
        return f"{cult.founded}, by {founder}"
    if founder:
        return f"by {founder}"
    return str(cult.founded) if cult.founded is not None else "not recorded"


def cult_facts(saga: Saga, cult: MysteryCult) -> list[tuple[str, str]]:
    """The cult's facts, in order."""
    return [
        ("Lore", cult.lore),
        ("Realm", cult.realm),
        ("Founded", founded_words(saga, cult)),
        ("Initiation", f"{cult.characteristic} + Lore + Script"),
        (
            "Joining",
            f"Lore {FIRST_LORE}; typically {LATER_LORE} from the second Initiation",
        ),
        ("Members", mc.members_text(saga, cult)),
    ]


def cult_title(saga: Saga, cult: Chosen) -> str:
    found = chosen_cult(saga, cult)
    return found.name if found is not None else "The Cult"


def cult_note(saga: Saga, cult: MysteryCult) -> str:
    """The lines under the facts: what the Lore is and where its Scripts
    are offered."""
    lore = (
        "Its Lore is a new Ability the saga adds"
        if needs_lore_ability(cult)
        else "Its Lore is the catalog's Mystery Cult Lore"
    )
    who = (
        ""
        if cult.who == CULT_GIFTED
        else " Anyone may join; an unGifted Initiate needs an Ordeal in every "
        "Initiation (Hedge Magic Revised Edition p. 14)."
    )
    return (
        f"{lore}; the Initiation season offers its Scripts beside the catalog's "
        f"cults.{who}\n[dim]A new cult starts with its Lore at 0 for its "
        f"founders; its first Script comes from experimenting ({T} pp. 18-19).[/]"
    )


def cult_text(saga: Saga, cult: Chosen) -> str:
    """The chosen cult's section on the terminal: its facts in two lines,
    then the note."""
    found = chosen_cult(saga, cult)
    if found is None:
        return "[dim]No cult yet: a on the list above adds one.[/]"
    facts = cult_facts(saga, found)
    line = "  ·  ".join

    def shown(rows: list[tuple[str, str]]) -> str:
        return line(f"[$label]{k}:[/] {escape(v)}" for k, v in rows)

    return (
        f"{shown(facts[:3])}\n{shown(facts[3:5])}\n{shown(facts[5:])}\n\n"
        + cult_note(saga, found)
    )


def cult_info(saga: Saga, cult: MysteryCult) -> str:
    """The chosen cult's details."""
    lines = [
        f"[b]{escape(cult.name)}[/]  ·  {cult.realm}  ·  {escape(cult.lore)}",
        f"[$label]Members:[/] {escape(mc.members_text(saga, cult))}",
        f"[$label]Who may join:[/] {WHO[cult.who]}",
        "[dim]Members are those with the Lore (a founder may have it at 0); "
        f"its Virtues only say which degree each has reached ({T} pp. 11, 13).[/]",
    ]
    if cult.description.strip():
        lines += ["", escape(cult.description.strip())]
    lines += [
        "",
        f"[dim]A probationer needs the Lore at 1 before his first Initiation; "
        "the second and later typically need 3, which the troupe may set "
        f"aside ({T} pp. 11, 13).[/]",
    ]
    return "\n".join(lines)


# -- the degrees ------------------------------------------------------------------


def degrees_title(saga: Saga, cult: Chosen) -> str:
    found = chosen_cult(saga, cult)
    return f"Degrees ({len(found.degrees) if found is not None else 0})"


def degrees_header() -> str:
    return (
        "  "
        + "".join(
            _cell(t, w)
            for t, w in zip(
                ("Degree", "Mystery Virtue", "Bonus/Tgt"), DEGREE_WIDTHS, strict=True
            )
        )
        + "Script"
    )


def _script_words(degree: CultDegree) -> str:
    return degree.script.name if degree.script is not None else "(none: experiment)"


def degree_rows(saga: Saga, cult: Chosen) -> list[tuple[int | None, str]]:
    found = chosen_cult(saga, cult)
    if found is None:
        return [(None, "[dim]Add a cult first.[/]")]
    rows: list[tuple[int | None, str]] = []
    for i, degree in enumerate(found.degrees):
        bonus = degree.script.bonus if degree.script is not None else 0
        cells = (
            f"{mc.numeral(i)} {degree.name}",
            mc.virtue_name(degree),
            f"{bonus:+d} / {mc.degree_target(saga, degree)}",
        )
        rows.append(
            (
                i,
                "".join(
                    escape(_cell(t, w))
                    for t, w in zip(cells, DEGREE_WIDTHS, strict=True)
                )
                + escape(fit(_script_words(degree), SCRIPT_WIDTH)),
            )
        )
    return rows or [
        (None, "[dim]No degree yet: a adds one, each teaching a Mystery Virtue.[/]")
    ]


def degree_note(saga: Saga, degree: CultDegree) -> str:
    """Who holds the degree's Virtue, so knows it as Mystagogue."""
    known = mc.holders(saga, degree)
    target = mc.degree_target(saga, degree)
    if known:
        names = ", ".join(c.name for c in known)
        return f"{names} {'has' if len(known) == 1 else 'have'} it: Target {target}."
    found = f"No one in the cult has it: Target {target}"
    if degree.script is None:
        return found + ", and its Script must be found by experiment."
    return found + "."


def script_extras(script: CultScript) -> list[str]:
    """What an experiment wrote into the Script beyond its components
    (TMRE p. 18): the Virtue it Initiates instead, its added Virtues and
    its Personality Traits, as markup lines."""
    lines = []
    if script.initiates:
        lines.append(
            f"[$label]Initiates instead:[/] {escape(mc.vf_name(script.initiates))} "
            "(a modified effect)"
        )
    if script.virtues:
        names = ", ".join(mc.vf_name(v) for v in script.virtues)
        lines.append(f"[$label]Also gives:[/] {escape(names)}")
    if script.traits:
        lines.append(
            f"[$label]Personality Traits:[/] {escape(', '.join(script.traits))}"
        )
    return lines


@dataclass(frozen=True)
class EntryText:
    """A list entry as the desktop's ledger draws it: the margin's mark,
    its heading, the italic line beside it, a badge, its words and a note
    (markup), and the inspector's title, subtitle and details."""

    rubric: str
    title: str
    meta: str
    badge: str
    body: str
    note: str
    subtitle: str
    info: str


def degree_info(saga: Saga, cult: MysteryCult, index: int) -> str:
    degree = cult.degrees[index]
    tier = mc.tier_of(degree)
    lines = [
        f"[b]{escape(degree.name)}[/]  ·  degree {mc.numeral(index)}  ·  "
        f"{escape(mc.virtue_name(degree))} ({tier})",
    ]
    if degree.script is not None:
        lines.append(
            f"[$label]Script:[/] {escape(degree.script.name)}, {degree.script.bonus:+d}"
        )
        lines += script_extras(degree.script)
    else:
        lines.append("[$label]Script:[/] none yet: More's Experiment on a Script")
    lines += [
        f"[$label]Target Level:[/] {mc.degree_target(saga, degree)}",
        f"[$label]The Initiate needs:[/] {cult.lore} {FIRST_LORE} (typically "
        f"{LATER_LORE} for a second or later Initiation)",
        f"[i]{escape(degree_note(saga, degree))}[/]",
        "",
        "[dim]Target: a Minor Virtue 15, a Major 21; 18 and 30 when the "
        "Mystagogue lacks it. An earlier Ordeal lowers the next three "
        "Initiations: 3/2/1, 6/4/2 or 9/6/3, never below 9 (DE pp. 387-388; "
        f"{T} p. 14).[/]",
    ]
    return "\n".join(lines)


def degree_entries(saga: Saga, cult: Chosen) -> list[EntryText]:
    found = chosen_cult(saga, cult)
    if found is None:
        return []
    entries = []
    for i, degree in enumerate(found.degrees):
        virtue = mc.virtue_name(degree)
        bonus = degree.script.bonus if degree.script is not None else 0
        entries.append(
            EntryText(
                rubric=mc.numeral(i),
                title=f"{degree.name}: {virtue}",
                meta=f"{mc.tier_of(degree)} Virtue",
                badge=f"Script {bonus:+d}",
                body=f"Script: {escape(_script_words(degree))}",
                note=f"[i]{escape(degree_note(saga, degree))}[/]",
                subtitle=f"Degree {mc.numeral(i)}  ·  {mc.tier_of(degree)} Virtue",
                info=degree_info(saga, found, i),
            )
        )
    return entries


# -- the Script -------------------------------------------------------------------


def script_title(saga: Saga, cult: Chosen, degree: Chosen) -> str:
    found = chosen_degree(saga, cult, degree)
    if found is None:
        return "Script"
    _, chosen = found
    if chosen.script is None:
        return f"{chosen.name}: no Script yet"
    return f"{chosen.script.name}: {chosen.script.bonus:+d}"


def script_header() -> str:
    return (
        "  "
        + "".join(
            _cell(t, w)
            for t, w in zip(("Component", "Kind"), COMPONENT_WIDTHS, strict=True)
        )
        + "Bonus"
    )


def _components(saga: Saga, cult: Chosen, degree: Chosen) -> list[CultComponent]:
    found = chosen_degree(saga, cult, degree)
    if found is None or found[1].script is None:
        return []
    return found[1].script.components


def script_rows(
    saga: Saga, cult: Chosen, degree: Chosen
) -> list[tuple[int | None, str]]:
    found = chosen_degree(saga, cult, degree)
    if found is None:
        return [(None, "[dim]Choose a degree.[/]")]
    if found[1].script is None:
        return [
            (
                None,
                "[dim]No Script: a writes one, or More's Experiment on a Script "
                f"finds it ({T} p. 18).[/]",
            )
        ]
    rows: list[tuple[int | None, str]] = [
        (
            i,
            escape(_cell(mc.component_name(c), COMPONENT_WIDTHS[0]))
            + escape(_cell(c.kind, COMPONENT_WIDTHS[1]))
            + f"{c.bonus:+d}",
        )
        for i, c in enumerate(found[1].script.components)
    ]
    return rows or [(None, "[dim]No components: a adds one.[/]")]


def component_info(part: CultComponent) -> str:
    lines = [
        f"[b]{escape(mc.component_name(part))}[/]  ·  {part.kind}  ·  {part.bonus:+d}",
        mc.KIND_NOTES[part.key],
        "",
        "[dim]If any component costs the Initiate nothing (he lives by the "
        f"special place), the whole Script is void ({T} p. 16).[/]",
    ]
    return "\n".join(lines)


def component_entries(saga: Saga, cult: Chosen, degree: Chosen) -> list[EntryText]:
    return [
        EntryText(
            rubric=f"{c.bonus:+d}",
            title=mc.component_name(c),
            meta=c.kind,
            badge=f"{c.bonus:+d}",
            body=mc.KIND_NOTES[c.key],
            note="",
            subtitle=c.kind,
            info=component_info(c),
        )
        for c in _components(saga, cult, degree)
    ]


def panel_text(
    saga: Saga, cult: Chosen, degree: Chosen, section: str, row: int | None
) -> str:
    """The tab's details panel for the row last chosen in `section`."""
    found = chosen_cult(saga, cult)
    if found is None or row is None:
        return EMPTY_PANEL
    if section == CULTS_SECTION:
        chosen = _at(saga.custom_cults, row)
        return cult_info(saga, chosen) if chosen is not None else EMPTY_PANEL
    if section == CULT_DEGREES_SECTION:
        return (
            degree_info(saga, found, row) if row < len(found.degrees) else EMPTY_PANEL
        )
    if section == CULT_SCRIPT_SECTION:
        parts = _components(saga, cult, degree)
        return component_info(parts[row]) if row < len(parts) else EMPTY_PANEL
    return EMPTY_PANEL


# -- Add and Edit a cult ----------------------------------------------------------


def _cult_fields(saga: Saga, existing: MysteryCult | None) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", attr(existing, "name", ""), required=True),
        DialogField(
            "lore",
            "Its Lore (a new Ability)",
            "text",
            attr(existing, "lore", ""),
            placeholder="e.g. Spinner's Thread Lore",
            hint=f"The storyguide creates it; founders may start at 0 ({T} p. 18). "
            'Written as "Mystery Cult Lore: (cult)" it is the catalog\'s own.',
        ),
        DialogField(
            "realm",
            "Realm",
            "select",
            attr(existing, "realm", "Magic"),
            options=pairs(TRADITION_REALMS),
        ),
        DialogField(
            "characteristic",
            "Initiation uses",
            "select",
            attr(existing, "characteristic", "Presence"),
            options=pairs(CULT_CHARACTERISTICS),
            hint=f"Presence + Lore + Script, as a rule ({T} p. 13).",
        ),
        DialogField(
            "who",
            "Who may join",
            "select",
            attr(existing, "who", CULT_GIFTED),
            options=[(label, key) for key, label in WHO.items()],
        ),
        DialogField(
            "founder_id",
            "Founder",
            "select",
            attr(existing, "founder_id", "") or None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            allow_blank=True,
            placeholder="(none named)",
        ),
        DialogField("founded", "Founded in", "optint", attr(existing, "founded", None)),
        DialogField(
            "description", "What it is", "area", attr(existing, "description", "")
        ),
    ]


def cult_problem(
    saga: Saga, existing: MysteryCult | None, values: dict[str, Any]
) -> str | None:
    name = (values.get("name") or "").strip()
    if not name:
        return "Name the cult."
    if any(
        c.name.casefold() == name.casefold()
        for c in saga.custom_cults
        if c is not existing
    ):
        return f"The saga already has a cult named {name}."
    return mc.lore_problem(saga, existing, values.get("lore") or "") or None


def _apply_cult(
    saga: Saga, existing: MysteryCult | None, values: dict[str, Any]
) -> None:
    name = values["name"].strip()
    lore = (values.get("lore") or "").strip()
    cult = existing or MysteryCult(mc.new_cult_id(saga, name), name, lore)
    mc.rename_lore(saga, cult.lore, lore)
    cult.name, cult.lore = name, lore
    cult.realm = values.get("realm") or "Magic"
    cult.characteristic = values.get("characteristic") or "Presence"
    cult.who = values.get("who") or CULT_GIFTED
    cult.founder_id = values.get("founder_id") or ""
    cult.founded = values.get("founded")
    cult.description = values.get("description") or ""
    if existing is None:
        saga.custom_cults.append(cult)
    mc.changed(saga)


def cult_form(saga: Saga, existing: MysteryCult | None) -> Form:
    return Form(
        "Add Mystery Cult" if existing is None else f"Edit {escape(existing.name)}",
        lambda: _cult_fields(saga, existing),
        lambda values: _apply_cult(saga, existing, values),
        validate=lambda values: cult_problem(saga, existing, values),
        save_label="Add" if existing is None else "Save",
        help_id=CULTS_SECTION,
    )


def cults_ops(saga: Saga) -> SectionOps:
    """The list of the saga's cults."""

    def remove(index: int) -> Confirm:
        cult = saga.custom_cults[index]

        def delete() -> None:
            saga.custom_cults.remove(cult)
            mc.changed(saga)

        return Confirm(
            f"Delete {escape(cult.name)}?\n\nIts members keep its Lore and "
            "Virtues; the Initiation season no longer offers its Scripts.",
            delete,
        )

    return SectionOps(
        add=lambda: cult_form(saga, None),
        edit=lambda index: cult_form(saga, saga.custom_cults[index]),
        remove=remove,
        rows=lambda: [c.name for c in saga.custom_cults],
    )


def cult_ops(saga: Saga, cult: Chosen) -> SectionOps:
    """The chosen cult's section: Edit Cult."""

    def edit(_row: int) -> Form | Refuse:
        found = chosen_cult(saga, cult)
        if found is None:
            return Refuse("Edit Cult", "The saga has no cult yet: add one first.")
        return cult_form(saga, found)

    return SectionOps(edit=edit, rows=lambda: [cult_title(saga, cult)])


# -- Add and Edit a degree --------------------------------------------------------


def _virtue_options() -> list[tuple[str, str]]:
    return [(f"{escape(v.name)} ({v.tier})", v.id) for v in mc.mystery_virtues()]


def _parameters(virtue_id: str) -> list[str]:
    found = next((v for v in mc.mystery_virtues() if v.id == virtue_id), None)
    return list(found.parameters) if found is not None else []


def _degree_fields(existing: CultDegree | None) -> list[DialogField]:
    detail = next(iter(existing.virtue_params.values()), "") if existing else ""
    return [
        DialogField(
            "name",
            "Degree",
            "text",
            attr(existing, "name", ""),
            required=True,
            placeholder="e.g. Weaver",
        ),
        DialogField(
            "virtue_id",
            "Mystery Virtue",
            "select",
            attr(existing, "virtue_id", "") or None,
            options=_virtue_options(),
            hint="Almost any Virtue, save those of birth or circumstance "
            f"({T} p. 13); the saga's own Virtues are listed too.",
        ),
        DialogField(
            "virtue_detail",
            "What it names",
            "text",
            detail.title(),
            placeholder="e.g. Imaginem",
            show_if=lambda values: bool(_parameters(values.get("virtue_id") or "")),
            hint="For a Virtue that names something: the Art, the Ability.",
        ),
    ]


def _params(values: dict[str, Any]) -> dict[str, str]:
    names = _parameters(values.get("virtue_id") or "")
    detail = (values.get("virtue_detail") or "").strip().lower()
    return {names[0]: detail} if names and detail else {}


def degree_problem(
    cult: MysteryCult, existing: CultDegree | None, values: dict[str, Any]
) -> str | None:
    if not (values.get("name") or "").strip():
        return "Name the degree."
    virtue = values.get("virtue_id") or ""
    if not virtue:
        return "Choose the Mystery Virtue the degree teaches."
    if _parameters(virtue) and not (values.get("virtue_detail") or "").strip():
        return "Say what the Virtue names (the Art, the Ability)."
    if any(
        d.virtue_id == virtue and d.virtue_params == _params(values)
        for d in cult.degrees
        if d is not existing
    ):
        return "Another degree of the cult already teaches that Virtue."
    return None


def degree_form(saga: Saga, cult: MysteryCult, existing: CultDegree | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        name = values["name"].strip()
        if existing is None:
            cult.degrees.append(
                CultDegree(
                    mc.new_degree_id(cult), name, values["virtue_id"], _params(values)
                )
            )
        else:
            existing.name, existing.virtue_id = name, values["virtue_id"]
            existing.virtue_params = _params(values)
        mc.changed(saga)

    return Form(
        "Add Degree" if existing is None else f"Edit Degree: {escape(existing.name)}",
        lambda: _degree_fields(existing),
        apply,
        validate=lambda values: degree_problem(cult, existing, values),
        save_label="Add" if existing is None else "Save",
        help_id=CULT_DEGREES_SECTION,
    )


def degree_ops(saga: Saga, cult: Chosen) -> SectionOps:
    """The chosen cult's degrees."""

    def add() -> Form | Refuse:
        found = chosen_cult(saga, cult)
        if found is None:
            return Refuse("Add Degree", "Add a cult first.")
        return degree_form(saga, found, None)

    def edit(index: int) -> Form | Refuse:
        found = chosen_cult(saga, cult)
        if found is None or index >= len(found.degrees):
            return Refuse("Edit Degree", "Choose a degree first.")
        return degree_form(saga, found, found.degrees[index])

    def remove(index: int) -> Confirm | Refuse:
        found = chosen_cult(saga, cult)
        if found is None or index >= len(found.degrees):
            return Refuse("Delete Degree", "Choose a degree first.")
        degree = found.degrees[index]

        def delete() -> None:
            found.degrees.remove(degree)
            mc.changed(saga)

        return Confirm(
            f"Delete the degree {escape(degree.name)} and its Script?", delete
        )

    def rows() -> list[str]:
        found = chosen_cult(saga, cult)
        return [d.name for d in found.degrees] if found is not None else []

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- Add and Edit a Script ----------------------------------------------------------


def _mystagogue_label(cult: MysteryCult, degree: CultDegree, c: Character) -> str:
    short = cult.characteristic[:3]
    value = getattr(c.characteristics, cult.characteristic.lower(), 0)
    has = ", has the Virtue" if mc.holds(c, degree) else ""
    return f"{escape(c.name)} ({short} {value:+d}, Lore {mc.lore_score(c, cult)}{has})"


def _flaw_options() -> list[tuple[str, str]]:
    return [(f"{escape(v.name)} ({v.tier})", v.id) for v in mc.ordeal_flaws()]


def _open_degrees(cult: MysteryCult, degree: CultDegree) -> list[tuple[str, str]]:
    """The degrees a Script may Initiate: this one, and those with none."""
    return [
        (f"{escape(mc.virtue_name(d))} ({mc.tier_of(d)}), degree {mc.numeral(i)}", d.id)
        for i, d in enumerate(cult.degrees)
        if d is degree or d.script is None
    ]


def _script_fields(
    saga: Saga, cult: MysteryCult, degree: CultDegree, existing: CultScript | None
) -> list[DialogField]:
    """A Script, as its kinds of component (TMRE pp. 15-16): the form's
    Ordeal is the Script's first; a Mystagogue to test it with."""
    ordeal = mc.first_of(existing, tuple(ORDEAL_KINDS))
    great = mc.first_of(existing, ("great_sacrifice",))
    sympathy = mc.first_of(existing, ("sympathy",))
    rite = mc.first_of(existing, ("rite",))
    size = {v: k for k, v in ORDEALS.items()}
    mystagogues = mc.mystagogues(saga, cult)
    found = [
        DialogField(
            "name", "Script", "text", attr(existing, "name", ""), required=True
        ),
        DialogField(
            "degree",
            "Initiates",
            "select",
            degree.id,
            options=_open_degrees(cult, degree),
        ),
        DialogField(
            "place",
            "Travel to a special place and time (+3)",
            "check",
            bool(mc.count_of(existing, "place")),
        ),
        DialogField(
            "quests", "Quests (+3 each)", "int", mc.count_of(existing, "quest")
        ),
        DialogField(
            "unique",
            "Unique Quests (+6 each)",
            "int",
            mc.count_of(existing, "unique_quest"),
        ),
        DialogField(
            "ordeal",
            "Ordeal",
            "select",
            size.get(ordeal.key) if ordeal is not None else None,
            options=ORDEAL_LABELS,
            allow_blank=True,
            placeholder="None",
        ),
        DialogField(
            "flaw",
            "Its Flaw",
            "select",
            (ordeal.flaw_id if ordeal is not None else "") or None,
            options=_flaw_options(),
            show_if=lambda values: bool(values.get("ordeal")),
            hint="Gaining a Minor or Major Flaw, or a Minor raised to Major "
            f"(Hermetic Flaws too, {T} p. 13).",
        ),
        DialogField(
            "replaces",
            "A Minor Virtue it replaces (+3)",
            "check",
            bool(mc.count_of(existing, "virtue_replaced")),
        ),
        DialogField(
            "goods",
            "Sacrifice of goods (+1)",
            "check",
            bool(mc.count_of(existing, "goods")),
        ),
        DialogField(
            "service",
            "A season serving the cult (+1)",
            "check",
            bool(mc.count_of(existing, "time")),
        ),
        DialogField(
            "great",
            "Something of great value (0, +3 to +6)",
            "int",
            great.bonus if great is not None else 0,
        ),
        DialogField(
            "teaching",
            "The Mystagogue's time (+3)",
            "check",
            bool(mc.count_of(existing, "mystagogue_time")),
        ),
        DialogField(
            "sympathy",
            "Sympathy (−5 to +5)",
            "int",
            sympathy.bonus if sympathy is not None else 0,
            hint="Agreed with the storyguide: how fitting the rite is.",
        ),
    ]
    if rite is not None:
        found.append(
            DialogField(
                "rite",
                "The rite as proposed",
                "int",
                rite.bonus,
                hint="An experiment's rite as a whole: set it to 0 once its "
                "components are written out above.",
            )
        )
    found.append(
        DialogField(
            "mystagogue",
            "Mystagogue",
            "select",
            mystagogues[0].id if mystagogues else None,
            options=[(_mystagogue_label(cult, degree, c), c.id) for c in mystagogues],
            allow_blank=True,
            placeholder="(none to test it with)",
            hint="Only to test the Script against: not saved.",
        )
    )
    return found


def _wanted(values: dict[str, Any]) -> dict[str, list[CultComponent]]:
    """The components the Script form sets, by kind (the Ordeal aside)."""

    def times(key: str, n: int) -> list[CultComponent]:
        return [mc.component(key) for _ in range(max(0, n))]

    great = int(values.get("great") or 0)
    sympathy = int(values.get("sympathy") or 0)
    wanted = {
        "place": times("place", int(bool(values.get("place")))),
        "quest": times("quest", int(values.get("quests") or 0)),
        "unique_quest": times("unique_quest", int(values.get("unique") or 0)),
        "virtue_replaced": times("virtue_replaced", int(bool(values.get("replaces")))),
        "goods": times("goods", int(bool(values.get("goods")))),
        "time": times("time", int(bool(values.get("service")))),
        "mystagogue_time": times("mystagogue_time", int(bool(values.get("teaching")))),
        "great_sacrifice": [mc.component("great_sacrifice", great)] if great else [],
        "sympathy": [mc.component("sympathy", sympathy)] if sympathy else [],
    }
    if "rite" in values:
        rite = int(values.get("rite") or 0)
        wanted["rite"] = [mc.component("rite", rite)] if rite else []
    return wanted


def script_components(
    old: CultScript | None, values: dict[str, Any]
) -> list[CultComponent]:
    """The Script's components after its form: the kinds it sets
    (mc.reconcile keeps their words), and its Ordeal as the first."""
    parts = mc.reconcile(list(old.components) if old else [], _wanted(values))
    first = next((i for i, c in enumerate(parts) if c.key in ORDEAL_KINDS), None)
    chosen = values.get("ordeal") or ""
    if chosen in ORDEALS:
        note = parts[first].note if first is not None else ""
        made = mc.component(
            ORDEALS[chosen], note=note, flaw_id=values.get("flaw") or ""
        )
        if first is None:
            parts.append(made)
        else:
            parts[first] = made
    elif first is not None:
        del parts[first]
    return parts


def script_problem(old: CultScript | None, values: dict[str, Any]) -> str | None:
    if not (values.get("name") or "").strip():
        return "Name the Script."
    for key, label in (("quests", "Quests"), ("unique", "Unique Quests")):
        if not 0 <= int(values.get(key) or 0) <= 9:
            return f"{label}: 0 to 9."
    great = int(values.get("great") or 0)
    if great and not 3 <= great <= 6:
        return "Something of great value is +3 to +6 (or 0 for none)."
    if not -5 <= int(values.get("sympathy") or 0) <= 5:
        return "The sympathy is −5 to +5."
    if values.get("ordeal") and not values.get("flaw"):
        return "Choose the Flaw the Ordeal inflicts."
    return mc.script_problem(script_components(old, values)) or None


def script_live(saga: Saga, cult: MysteryCult) -> Callable[[dict[str, Any]], str]:
    """The Rite: the Script's bonus from the form, and the chosen
    Mystagogue's Initiation Total against his Target."""

    def live(values: dict[str, Any]) -> str:
        parts = script_components(None, values)
        bonus = sum(p.bonus for p in parts)
        words = " + ".join(f"{COMPONENT_KINDS[p.key]} {p.bonus:+d}" for p in parts)
        lines = [f"[b]Script bonus:[/] {escape(words or 'nothing')} = [b]{bonus:+d}[/]"]
        degree = next((d for d in cult.degrees if d.id == values.get("degree")), None)
        mystagogue = saga.character(values.get("mystagogue"))
        if degree is not None and mystagogue is not None:
            total = mc.initiation_total(mystagogue, cult, bonus).total
            target = mc.target_for(mystagogue, degree)
            knows = "has it" if mc.holds(mystagogue, degree) else "lacks it"
            verdict = (
                "[$text-success]succeeds[/]"
                if total >= target
                else f"[$text-error]falls short by {target - total}[/]"
            )
            value = getattr(mystagogue.characteristics, cult.characteristic.lower(), 0)
            lines.append(
                f"[b]{escape(mystagogue.name)}:[/] {cult.characteristic} {value} + Lore "
                f"{mc.lore_score(mystagogue, cult)} + {bonus} = [b]{total}[/] against "
                f"Target {target} ({mc.tier_of(degree)}, {knows}): {verdict}"
            )
        lines += [
            "An earlier Ordeal lowers the Target for the Initiate (−3 after a Minor "
            "one, and so on), never below 9. No die is rolled.",
            f"[dim]DE p. 388; {T} pp. 15-16.[/]",
        ]
        return "\n".join(lines)

    return live


def script_form(
    saga: Saga, cult: MysteryCult, degree: CultDegree, existing: CultScript | None
) -> Form:
    def apply(values: dict[str, Any]) -> None:
        script = CultScript(
            values["name"].strip(),
            script_components(existing, values),
            traits=list(existing.traits) if existing is not None else [],
            virtues=list(existing.virtues) if existing is not None else [],
            initiates=existing.initiates if existing is not None else "",
        )
        target = next((d for d in cult.degrees if d.id == values.get("degree")), degree)
        if target is not degree:
            degree.script = None
        target.script = script
        mc.changed(saga)

    title = (
        "Add Script" if existing is None else f"Edit Script: {escape(existing.name)}"
    )
    return Form(
        title,
        lambda: _script_fields(saga, cult, degree, existing),
        apply,
        validate=lambda values: script_problem(existing, values),
        live=script_live(saga, cult),
        inspector="The Rite",
        save_label="Add" if existing is None else "Save",
        help_id=CULT_SCRIPT_SECTION,
    )


def _component_fields() -> list[DialogField]:
    kinds = [(label, key) for key, label in COMPONENT_KINDS.items() if key != "rite"]
    sized = {"great_sacrifice", "sympathy"}
    return [
        DialogField("kind", "Kind", "select", "quest", options=kinds),
        DialogField(
            "size",
            "Its bonus",
            "int",
            3,
            show_if=lambda values: values.get("kind") in sized,
            hint="Something of great value +3 to +6; the sympathy −5 to +5 "
            f"({T} pp. 15-16).",
        ),
        DialogField(
            "flaw",
            "Its Flaw",
            "select",
            None,
            options=_flaw_options(),
            show_if=lambda values: values.get("kind") in FLAW_KINDS,
        ),
        DialogField(
            "note",
            "What it is",
            "text",
            "",
            placeholder="e.g. bring the Spinner a thread of a faerie's gown",
        ),
    ]


def _component_from(values: dict[str, Any]) -> CultComponent:
    key = values.get("kind") or "quest"
    flaw = values.get("flaw") or "" if key in FLAW_KINDS else ""
    return mc.component(
        key, int(values.get("size") or 0), values.get("note") or "", flaw
    )


def component_form(saga: Saga, script: CultScript) -> Form:
    def problem(values: dict[str, Any]) -> str | None:
        made = _component_from(values)
        return mc.script_problem([*script.components, made]) or None

    def apply(values: dict[str, Any]) -> None:
        script.components.append(_component_from(values))
        mc.changed(saga)

    return Form(
        f"Add Component: {escape(script.name)}",
        _component_fields,
        apply,
        validate=problem,
        save_label="Add",
        help_id=CULT_SCRIPT_SECTION,
    )


def script_ops(saga: Saga, cult: Chosen, degree: Chosen) -> SectionOps:
    """The chosen degree's Script: Add writes a Script for a degree with
    none, else adds a component; Edit edits the whole Script; Delete
    removes the chosen component."""

    def add() -> Form | Refuse:
        found = chosen_degree(saga, cult, degree)
        if found is None:
            return Refuse("Add", "Add a degree first: a Script Initiates its Virtue.")
        chosen_cult_, chosen = found
        if chosen.script is None:
            return script_form(saga, chosen_cult_, chosen, None)
        return component_form(saga, chosen.script)

    def edit(_row: int) -> Form | Refuse:
        found = chosen_degree(saga, cult, degree)
        if found is None or found[1].script is None:
            return Refuse("Edit Script", "The degree has no Script yet: a writes one.")
        return script_form(saga, found[0], found[1], found[1].script)

    def remove(index: int) -> Confirm | Refuse:
        found = chosen_degree(saga, cult, degree)
        script = found[1].script if found is not None else None
        if script is None or index >= len(script.components):
            return Refuse("Delete", "Choose a component first.")
        part = script.components[index]

        def delete() -> None:
            script.components.remove(part)
            mc.changed(saga)

        return Confirm(
            f"Delete {escape(mc.component_name(part))} from the Script?", delete
        )

    return SectionOps(
        add=add,
        edit=edit,
        remove=remove,
        rows=lambda: [mc.component_name(c) for c in _components(saga, cult, degree)],
    )


# -- More: Experiment on a Script -------------------------------------------------


def offers_experiment(saga: Saga, cult: Chosen, row: int | None) -> bool:
    """Whether Experiment on a Script can act on row `row` of the degrees:
    a degree with no Script yet, or one whose Script won't do for one of
    its Mystagogues (TMRE p. 18)."""
    return mc.offers_experiment(saga, cult(), row)


def _open_to_experiment(
    cult: MysteryCult, degree: CultDegree, guides: list[Character]
) -> list[tuple[str, str]]:
    """The degrees an experiment may seek a Script for: this one, those
    with none, and those whose Script won't do for one of the Mystagogues."""
    return [
        (
            f"{escape(mc.virtue_name(d))} ({mc.tier_of(d)}), degree {mc.numeral(i)}"
            + ("" if d.script is None else f": {escape(d.script.name)} falls short"),
            d.id,
        )
        for i, d in enumerate(cult.degrees)
        if d is degree
        or d.script is None
        or any(mc.script_inadequate(cult, d, g) for g in guides)
    ]


def _experiment_fields(
    saga: Saga, cult: MysteryCult, degree: CultDegree, guides: list[Character]
) -> list[DialogField]:
    return [
        DialogField(
            "degree",
            "Initiates",
            "select",
            degree.id,
            options=_open_to_experiment(cult, degree, guides),
        ),
        DialogField(
            "mystagogue",
            "Mystagogue",
            "select",
            guides[0].id,
            options=[
                (
                    f"{escape(c.name)} ({cult.characteristic[:3]} "
                    f"{getattr(c.characteristics, cult.characteristic.lower(), 0):+d}, "
                    f"Int {c.characteristics.intelligence:+d}, Lore "
                    f"{mc.lore_score(c, cult)})",
                    c.id,
                )
                for c in guides
            ],
        ),
        DialogField(
            "initiate",
            "Initiate",
            "select",
            "",
            options=[("The Mystagogue herself", "")]
            + [(escape(c.name), c.id) for c in saga.characters],
            hint="Experimenting on another is harder: the validity roll's Ease "
            "Factor is 15 + the bonus, not 9 + it.",
        ),
        DialogField(
            "proposed",
            "Proposed Script bonus",
            "int",
            6,
            hint="From the rite's components.",
        ),
        DialogField(
            "rite_flaw",
            "Its Ordeal's Flaw",
            "select",
            None,
            options=_flaw_options(),
            allow_blank=True,
            placeholder="(no Ordeal)",
            hint=f"Suffered by the Initiate even if the rite fails ({T} p. 18).",
        ),
        DialogField("risk", "Risk (0 to +3)", "int", 0),
    ]


def experiment_problem(
    saga: Saga, cult: MysteryCult
) -> Callable[[dict[str, Any]], str | None]:
    """The experiment form's checks: the risk 0 to +3, a bonus of 0 or
    more, and a degree whose Script, if it has one, won't do for this
    Mystagogue and Initiate (TMRE p. 18)."""

    def problem(values: dict[str, Any]) -> str | None:
        if not 0 <= int(values.get("risk") or 0) <= mysteries.MAX_SCRIPT_RISK:
            return f"The risk is 0 to +{mysteries.MAX_SCRIPT_RISK}."
        if int(values.get("proposed") or 0) < 0:
            return "The proposed bonus is 0 or more."
        terms = _terms(saga, cult, values)
        if terms is not None:
            degree, guide, initiate = terms
            if degree.script is not None and not mc.script_inadequate(
                cult, degree, guide, initiate
            ):
                return (
                    f"{escape(degree.script.name)} already reaches the Target for "
                    f"{escape(guide.name)}: follow it in an Initiation season."
                )
        return None

    return problem


def _terms(
    saga: Saga, cult: MysteryCult, values: dict[str, Any]
) -> tuple[CultDegree, Character, Character] | None:
    degree = next((d for d in cult.degrees if d.id == values.get("degree")), None)
    guide = saga.character(values.get("mystagogue"))
    if degree is None or guide is None:
        return None
    initiate = saga.character(values.get("initiate")) or guide
    return degree, guide, initiate


def experiment_live(saga: Saga, cult: MysteryCult) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        terms = _terms(saga, cult, values)
        if terms is None:
            return "[dim]Choose the degree and the Mystagogue.[/]"
        degree, guide, initiate = terms
        risk = int(values.get("risk") or 0)
        bonus = int(values.get("proposed") or 0)
        on_self = initiate is guide
        ease = mysteries.validity_ease(bonus, on_self)
        lore = mc.lore_score(guide, cult)
        intelligence = guide.characteristics.intelligence
        value = getattr(guide.characteristics, cult.characteristic.lower(), 0)
        total = mc.initiation_total(guide, cult, bonus, risk).total
        target = mc.target_for(guide, degree, initiate)
        knows = "she has" if mc.holds(guide, degree) else "she lacks"
        verdict = (
            "[$text-success]works[/]"
            if total >= target
            else f"[$text-warning]needs {target - total} more from sympathy or an "
            "Ordeal[/]"
        )
        return "\n".join(
            [
                "The Initiate first carries out the rite: its Quests, Sacrifices "
                "and Ordeals, which stand whatever follows.",
                f"[b]1.[/] Stress die + risk {risk} on the Extraordinary Results "
                "chart: side effects become Personality Traits of the Script; a "
                "major flaw an extra Ordeal with no bonus; a major benefit a "
                "Virtue; a modified effect a different Virtue; a fatal flaw an "
                "Ordeal and no Virtue; Disaster a Major Flaw for both.",
                f"[b]2.[/] Validity: simple die + risk {risk} + Int {intelligence} + "
                f"Lore {lore} = {risk + intelligence + lore} + die against {ease} "
                + ("(9 + the bonus)" if on_self else "(15 + the bonus, on another)"),
                f"[b]3.[/] The storyguide's sympathy joins the Script; then "
                f"{cult.characteristic} {value} + Lore {lore} + {bonus} + risk {risk} = "
                f"[b]{total}[/] against Target {target} ({knows} "
                f"{escape(mc.virtue_name(degree))}; past Ordeals lower it, never "
                f"below 9): {verdict}",
                f"[dim]The risk is not written into the Script ({T} pp. 14, 18).[/]",
            ]
        )

    return live


def _virtue_choices() -> list[tuple[str, str]]:
    return [(f"{escape(v.name)} ({v.tier})", v.id) for v in mc.mystery_virtues()]


def _major_flaw_options() -> list[tuple[str, str]]:
    return [(escape(v.name), v.id) for v in mc.ordeal_flaws() if v.tier == "Major"]


def _findings_fields(rolled: mc.Experiment) -> list[DialogField]:
    """What the chart's results become, asked of the troupe (TMRE p. 18)."""
    fields: list[DialogField] = []
    for i, effect in enumerate(rolled.traits):
        fields.append(
            DialogField(
                f"trait_{i}",
                f"Personality Trait ({effect})",
                "text",
                "",
                required=True,
                placeholder="e.g. Devoted to the cult +1",
                hint="A trait tied to the cult's goals, with its score: it "
                "joins the Script and the Initiate's sheet.",
            )
        )
    for i in range(rolled.major_flaws):
        fields.append(
            DialogField(
                f"flaw_{i}",
                "The major flaw's Ordeal Flaw",
                "select",
                None,
                options=_flaw_options(),
                hint="Usually Minor; it joins the Script with no bonus.",
            )
        )
    for i in range(rolled.major_benefits):
        fields.append(
            DialogField(
                f"virtue_{i}",
                "The major benefit's Virtue",
                "select",
                None,
                options=_virtue_choices(),
                hint="The Virtue raised or stacked, or a second Minor Virtue: "
                "it joins the Script.",
            )
        )
    if rolled.modified:
        fields.append(
            DialogField(
                "instead",
                "The Virtue Initiated instead",
                "select",
                None,
                options=_virtue_choices(),
                hint="A modified effect Initiates a different Virtue, related "
                "to the cult's goals, not the degree's own.",
            )
        )
    return fields


def _findings(
    rolled: mc.Experiment, rite_flaw: str, values: dict[str, Any]
) -> mc.Findings:
    return mc.Findings(
        rite_flaw=rite_flaw,
        traits=[
            str(values.get(f"trait_{i}") or "").strip()
            for i in range(len(rolled.traits))
        ],
        flaws=[str(values.get(f"flaw_{i}") or "") for i in range(rolled.major_flaws)],
        virtues=[
            str(values.get(f"virtue_{i}") or "") for i in range(rolled.major_benefits)
        ],
        instead=str(values.get("instead") or "") if rolled.modified else "",
    )


def findings_problem(rolled: mc.Experiment, values: dict[str, Any]) -> str | None:
    """Each result the chart gave needs the troupe's answer."""
    for i in range(len(rolled.traits)):
        text = str(values.get(f"trait_{i}") or "")
        if mc.parse_trait(text) is None:
            return "Give each Personality Trait a score: e.g. Devoted to the cult +1."
    if any(not values.get(f"flaw_{i}") for i in range(rolled.major_flaws)):
        return "Choose the Ordeal Flaw the major flaw adds."
    if any(not values.get(f"virtue_{i}") for i in range(rolled.major_benefits)):
        return "Choose the Virtue the major benefit adds."
    if rolled.modified and not values.get("instead"):
        return "Choose the Virtue the modified effect Initiates instead."
    return None


def _disaster_form(
    saga: Saga,
    terms: tuple[CultDegree, Character, Character],
    rite_flaw: str,
    rolled: list[str],
) -> Form:
    """A Disaster: the troupe chooses the Major Flaw the Mystagogue and the
    Initiate each gain (TMRE p. 18)."""
    degree, guide, initiate = terms
    same = guide is initiate

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                "guide_flaw",
                f"{escape(guide.name)}'s Major Flaw",
                "select",
                None,
                options=_major_flaw_options(),
            )
        ]
        if not same:
            found.append(
                DialogField(
                    "initiate_flaw",
                    f"{escape(initiate.name)}'s Major Flaw",
                    "select",
                    None,
                    options=_major_flaw_options(),
                )
            )
        return found

    def problem(values: dict[str, Any]) -> str | None:
        if not values.get("guide_flaw") or (
            not same and not values.get("initiate_flaw")
        ):
            return "Choose each one's Major Flaw."
        return None

    def apply(values: dict[str, Any]) -> list[str]:
        guide_flaw = str(values.get("guide_flaw") or "")
        initiate_flaw = guide_flaw if same else str(values.get("initiate_flaw") or "")
        return [
            *rolled,
            *mc.disaster(saga, guide, initiate, guide_flaw, initiate_flaw, rite_flaw),
        ]

    return Form(
        f"Disaster: {escape(degree.name)}",
        fields,
        apply,
        validate=problem,
        live=lambda _values: "\n".join(escape(n) for n in rolled),
        inspector="The Rite",
        save_label="Suffer them",
        help_id=CULT_DEGREES_SECTION,
    )


def _sympathy_form(
    saga: Saga,
    cult: MysteryCult,
    terms: tuple[CultDegree, Character, Character],
    proposed: int,
    risk: int,
    rolled: mc.Experiment,
    rite_flaw: str = "",
) -> Form:
    degree, guide, initiate = terms
    notes = rolled.notes

    def live(values: dict[str, Any]) -> str:
        sympathy = int(values.get("sympathy") or 0)
        total = mc.initiation_total(guide, cult, proposed + sympathy, risk).total
        target = mc.target_for(guide, degree, initiate)
        return "\n".join(
            [*(escape(n) for n in notes), ""]
            + [
                f"[b]Initiation Total:[/] {total} against {target}: "
                + (
                    "[$text-success]the rite works[/]"
                    if total >= target
                    else "[$text-error]the rite fails[/]"
                )
            ]
        )

    def problem(values: dict[str, Any]) -> str | None:
        if not -5 <= int(values.get("sympathy") or 0) <= 5:
            return "The sympathy is −5 to +5."
        return findings_problem(rolled, values)

    return Form(
        f"The Storyguide's Sympathy: {escape(degree.name)}",
        lambda: [
            DialogField(
                "sympathy",
                "Sympathy (−5 to +5)",
                "int",
                0,
                hint="How well the rite matches the Virtue gained; it joins the "
                f"Script ({T} p. 18).",
            ),
            *_findings_fields(rolled),
        ],
        lambda values: [
            *notes,
            *mc.finish_experiment(
                saga,
                cult,
                degree,
                guide,
                initiate,
                proposed,
                int(values.get("sympathy") or 0),
                risk,
                _findings(rolled, rite_flaw, values),
            ),
        ],
        validate=problem,
        live=live,
        inspector="The Rite",
        save_label="Write the Script",
        help_id=CULT_DEGREES_SECTION,
    )


def experiment_form(
    saga: Saga,
    cult: Chosen,
    row: int | None,
    rng: Callable[[], random.Random] = random.Random,
) -> Form | Refuse:
    """More's Experiment on a Script, on the chosen degree (one with no
    Script, or one whose Script won't do for a Mystagogue): the chart and
    the validity are rolled, then the storyguide gives the sympathy and
    the troupe what the chart's results become, and the Initiation Total
    decides (TMRE p. 18)."""
    title = "Experiment on a Script"
    found = chosen_cult(saga, cult)
    degree = _at(found.degrees, row) if found is not None else None
    if found is None or degree is None:
        return Refuse(title, "Choose a degree first.")
    guides = mc.mystagogues(saga, found)
    if not guides:
        return Refuse(
            title,
            f"No one has {escape(found.lore)} at 1 or more: the founders study it "
            f"first ({T} p. 19).",
        )
    if degree.script is not None and not any(
        mc.script_inadequate(found, degree, g) for g in guides
    ):
        return Refuse(
            title,
            f"{escape(degree.script.name)} reaches the Target for every "
            "Mystagogue: follow it, or vary it, in an Initiation season "
            "(DE p. 388).",
        )
    cult_found = found

    def apply(values: dict[str, Any]) -> Any:
        terms = _terms(saga, cult_found, values)
        if terms is None:
            return ["Choose the degree and the Mystagogue."]
        degree_, guide, initiate = terms
        proposed = int(values.get("proposed") or 0)
        risk = int(values.get("risk") or 0)
        rite_flaw = str(values.get("rite_flaw") or "")
        rolled = mc.experiment(
            rng(), saga, cult_found, guide, initiate is guide, proposed, risk
        )
        if rolled.disaster:
            return _disaster_form(
                saga, (degree_, guide, initiate), rite_flaw, rolled.notes
            )
        if not rolled.goes_on:
            suffered = mc.suffer_ordeals(
                initiate, [rite_flaw] if rite_flaw else [], False
            )
            mc.changed(saga)
            return [
                *rolled.notes,
                f"No Virtue is gained; the Ordeals are still suffered ({T} p. 18).",
                *suffered,
            ]
        return _sympathy_form(
            saga,
            cult_found,
            (degree_, guide, initiate),
            proposed,
            risk if rolled.risk_counts else 0,
            rolled,
            rite_flaw,
        )

    return Form(
        f"{title}: {escape(degree.name)}",
        lambda: _experiment_fields(saga, cult_found, degree, guides),
        apply,
        validate=experiment_problem(saga, cult_found),
        live=experiment_live(saga, cult_found),
        inspector="The Experiment",
        save_label="Roll",
        help_id=CULT_DEGREES_SECTION,
    )
