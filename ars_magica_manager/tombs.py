"""A place marked as a tomb, designed like a covenant (Lands of the Nile
pp. 32-35, 40-46): its kind, aura and Build Points, its curses, its
talismans and wards, and its traps, on the place's Tomb tab, and More's
Overcome It when a trap springs. The rules are rules.egyptian_tombs.

A place is marked a tomb by the Tomb box on its form; only then is the
tab shown. The tomb doesn't set the place's own aura: its burial
ground's tether is shown, for the place's Tethers to name when the aura
change option is on.

Kept in Neighbour.details: "tomb" (the mark), "tomb_kind", "tomb_centuries",
"tomb_decay", "tomb_hooks", "tomb_hook_points", "tomb_boons",
"tomb_other", "tomb_other_bp" and "tomb_description", and the lists
"tomb_curses" (TombCurse), "tomb_wards" (TombWard) and "tomb_traps"
(TombTrap).

Pattern: the tab is one more place kind tab (neighbour_lists.KindTab),
the Strategy the Regio and Roll Tables tabs use: a block and three
KindLists, each with its `_*_fields` builder. Build Points are small
rule functions over the book's two tables, which the lists, the forms'
inspectors and the tomb's total all read."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any, Required, TypedDict, cast

from . import place_events, sourcebooks
from .commands import Command, Confirm, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import Character, Neighbour, Saga, details_list
from .neighbour_lists import KindBlock, KindList, KindTab, LedgerEntry
from .references import Fact
from .rules import dice
from .rules import egyptian_tombs as et
from .rules.lab import ability_score
from .rules.sites import whole_number
from .sections import (
    TOMB_CURSES_SECTION,
    TOMB_SECTION,
    TOMB_TRAPS_SECTION,
    TOMB_WARDS_SECTION,
)

L = et.L

#: The detail that marks a place as a tomb.
TOMB = "tomb"
CURSES, WARDS, TRAPS = "tomb_curses", "tomb_wards", "tomb_traps"


class TombCurse(TypedDict, total=False):
    """A curse written in the tomb: its condition and its excoriation."""

    name: Required[str]
    kind: str
    art: str
    level: int
    rdt: str
    uses: int
    penetration: int
    condition: str
    excoriation: str


class TombWard(TypedDict, total=False):
    """A talisman or ward: its effect, and how it is made inert."""

    name: Required[str]
    kind: str
    art: str
    level: int
    penetration: int
    uses: str
    effect: str
    deactivation: str


class TombTrap(TypedDict, total=False):
    """A trap: what it does, and the Ease Factor to avoid it."""

    name: Required[str]
    harm: str
    ease: int
    text: str
    resets: bool


def is_tomb(place: Neighbour) -> bool:
    return bool(place.details.get(TOMB))


def curses(place: Neighbour) -> list[TombCurse]:
    return cast(list[TombCurse], details_list(place, CURSES))


def wards(place: Neighbour) -> list[TombWard]:
    return cast(list[TombWard], details_list(place, WARDS))


def traps(place: Neighbour) -> list[TombTrap]:
    return cast(list[TombTrap], details_list(place, TRAPS))


def _kind(place: Neighbour) -> et.TombKind:
    return et.kind(str(place.details.get("tomb_kind") or et.DEFAULT_KIND))


# -- Build Points --


def curse_points(curse: TombCurse) -> int:
    return et.curse_build_points(
        curse.get("kind") or et.EFFECT, whole_number(curse.get("level"))
    )


def ward_points(ward: TombWard) -> int:
    return et.enchantment_build_points(whole_number(ward.get("level")))


def trap_points(trap: TombTrap) -> int:
    harm = trap.get("harm") or "scare"
    ease = whole_number(trap.get("ease")) or 3
    if harm not in et.HARMS or ease not in et.AVOID:
        return 0
    return et.trap_build_points(harm, ease)


def ward_ease(ward: TombWard) -> int:
    return et.overcome_ease(
        ward.get("kind") or et.TALISMAN, whole_number(ward.get("level"))
    )


def spent(place: Neighbour) -> dict[str, int]:
    """The Build Points spent, by what on."""
    return {
        "curses": sum(curse_points(c) for c in curses(place)),
        "talismans and wards": sum(ward_points(w) for w in wards(place)),
        "traps": sum(trap_points(t) for t in traps(place)),
        "other resources": whole_number(place.details.get("tomb_other_bp")),
    }


def spent_total(place: Neighbour) -> int:
    return sum(spent(place).values())


def _spent_line(place: Neighbour) -> str:
    """How many of the tomb's Build Points are spent, as markup."""
    total, allowed = spent_total(place), _kind(place).build_points
    words = f"{total} of the tomb's {allowed} spent"
    if total > allowed:
        return f"[$text-error]{words}: {total - allowed} too many[/]"
    return words


# -- the tomb --


def tomb_facts(_saga: Saga, place: Neighbour) -> list[Fact]:
    d = place.details
    found = _kind(place)
    decay = whole_number(d.get("tomb_decay"))
    aura = et.tomb_aura(found.key, decay)
    centuries = whole_number(d.get("tomb_centuries"))
    hook_points = whole_number(d.get("tomb_hook_points"))
    hooks = str(d.get("tomb_hooks") or "").strip()
    return [
        Fact("Kind", found.name),
        Fact("Build Points", f"{spent_total(place)} of {found.build_points}"),
        Fact(
            "Magic aura",
            f"{aura} (base {found.aura}; decayed)" if decay > 0 else str(aura),
        ),
        Fact(
            "Tethers",
            f"a burial ground {centuries} centur{'y' if centuries == 1 else 'ies'} "
            f"in use: {et.tether_score(centuries)}"
            if centuries
            else "",
        ),
        Fact(
            "Hooks",
            ": ".join(
                p for p in (f"{hook_points} points" if hook_points else "", hooks) if p
            ),
        ),
        Fact("Boons", str(d.get("tomb_boons") or "").strip()),
    ]


def tomb_text(_saga: Saga, place: Neighbour) -> str:
    """What the Build Points went on, and how the tomb is designed."""
    parts = [f"{what} {points}" for what, points in spent(place).items() if points]
    other = str(place.details.get("tomb_other") or "").strip()
    lines = [
        "[$label]Build Points:[/] "
        + (", ".join(parts) if parts else "none spent yet")
        + f"; {_spent_line(place)}.",
    ]
    if other:
        lines.append(f"[$label]Other resources:[/] {escape(other)}")
    lines.append(
        "[dim]Designed like a covenant: Build Points, up to 10 points of Hooks "
        "for Boons; inscriptions, guardians, ghosts and vis cost what a "
        f"covenant's do ({L} pp. 40, 42, 44).[/]"
    )
    return "\n\n".join(["\n".join(lines[:-1]), lines[-1]])


def tomb_prose(_saga: Saga, place: Neighbour) -> str:
    return str(place.details.get("tomb_description") or "").strip()


def _tomb_fields(_saga: Saga, place: Neighbour) -> list[DialogField]:
    d = place.details
    return [
        DialogField(
            "tomb_kind",
            "Kind",
            "select",
            d.get("tomb_kind") or et.DEFAULT_KIND,
            options=[(k.name, k.key) for k in et.KINDS.values()],
            hint="Its base Magic aura and Build Points (LotN p. 40).",
        ),
        DialogField(
            "tomb_centuries",
            "Centuries the burial ground was used",
            "int",
            whole_number(d.get("tomb_centuries")),
            hint="A tether of 1 a century, at most 5.",
        ),
        DialogField(
            "tomb_decay",
            "Aura lost to decay",
            "int",
            whole_number(d.get("tomb_decay")),
        ),
        DialogField(
            "tomb_hook_points",
            "Points of Hooks",
            "int",
            whole_number(d.get("tomb_hook_points")),
            hint="At most 10, spent on Boons.",
        ),
        DialogField("tomb_hooks", "Hooks", "text", d.get("tomb_hooks") or ""),
        DialogField("tomb_boons", "Boons", "text", d.get("tomb_boons") or ""),
        DialogField(
            "tomb_other",
            "Other resources",
            "text",
            d.get("tomb_other") or "",
            placeholder="e.g. inscriptions 21, a guardian ghost 6, vis 20",
            hint="Inscriptions, guardians, ghosts and vis, at a covenant's costs.",
        ),
        DialogField(
            "tomb_other_bp",
            "Their Build Points",
            "int",
            whole_number(d.get("tomb_other_bp")),
        ),
        DialogField(
            "tomb_description",
            "Description",
            "area",
            d.get("tomb_description") or "",
        ),
    ]


def tomb_problem(values: dict[str, Any]) -> str | None:
    if not 0 <= (values.get("tomb_hook_points") or 0) <= et.MOST_HOOKS:
        return f"A tomb has 0 to {et.MOST_HOOKS} points of Hooks (LotN p. 40)."
    for key, words in (
        ("tomb_centuries", "Centuries"),
        ("tomb_decay", "The aura lost to decay"),
        ("tomb_other_bp", "Build Points"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{words} can't be below 0."
    return None


def edit_tomb(saga: Saga, place: Neighbour) -> Form:
    def apply(values: dict[str, Any]) -> None:
        place.details.update(values)

    return Form(
        "Edit Tomb",
        lambda: _tomb_fields(saga, place),
        apply,
        validate=tomb_problem,
        live=lambda values: _tomb_live(place, values),
        inspector="The Tomb",
    )


def _tomb_live(place: Neighbour, values: dict[str, Any]) -> str:
    found = et.kind(str(values.get("tomb_kind") or et.DEFAULT_KIND))
    aura = et.tomb_aura(found.key, values.get("tomb_decay") or 0)
    tether = et.tether_score(values.get("tomb_centuries") or 0)
    return (
        f"Magic aura {aura} (base {found.aura}); a burial ground's tether {tether}; "
        f"[b]{found.build_points} Build Points[/], {spent_total(place)} spent.\n"
        f"[dim]{L} p. 40. The place keeps its own aura: name the tether in its "
        f"Tethers, as (preternatural {tether}), for the aura change option.[/]"
    )


# -- the lists' shared Add, Edit and Delete --


def _ops[E: Any](
    entries: Callable[[], list[E]],
    noun: str,
    fields: Callable[[E | None], list[DialogField]],
    describe: Callable[[E], str],
    convert: Callable[[dict[str, Any]], dict[str, Any]],
    validate: Callable[[dict[str, Any]], str | None],
    live: Callable[[E | None, dict[str, Any]], str],
    inspector: str,
) -> SectionOps:
    """Add, Edit and Delete on a tomb's list: a form of `fields` whose
    values `convert` makes ready to keep, with `live` as its inspector."""

    def form(entry: E | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            kept = convert(values)
            if entry is None:
                entries().append(cast(E, kept))
            else:
                cast(dict[str, Any], entry).update(kept)

        return Form(
            f"Add a {noun}" if entry is None else f"Edit a {noun}",
            lambda: fields(entry),
            apply,
            validate=validate,
            live=lambda values: live(entry, values),
            inspector=inspector,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = entries()[index]

        def delete() -> None:
            entries().remove(entry)

        return Confirm(f"Delete {escape(describe(entry))}?", delete)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(entries()[index]),
        remove=remove,
        rows=lambda: [describe(e) for e in entries()],
    )


def _others(place: Neighbour, entry: object, own: int) -> str:
    """The tomb's Build Points with `entry` costing `own`, as markup."""
    total = spent_total(place) - _points_of(place, entry) + own
    allowed = _kind(place).build_points
    words = f"{total} of the tomb's {allowed} spent"
    return f"[$text-error]{words}[/]" if total > allowed else words


def _points_of(place: Neighbour, entry: object) -> int:
    """What `entry`, already in one of the tomb's lists, costs (0 for a
    new one)."""
    if entry is None:
        return 0
    if any(entry is c for c in curses(place)):
        return curse_points(cast(TombCurse, entry))
    if any(entry is w for w in wards(place)):
        return ward_points(cast(TombWard, entry))
    if any(entry is t for t in traps(place)):
        return trap_points(cast(TombTrap, entry))
    return 0


# -- curses --


def _curse_cost(curse: TombCurse) -> str:
    return f"{curse_points(curse)} BP"


def _curse_effect(curse: TombCurse) -> str:
    if (curse.get("kind") or et.EFFECT) == et.HOLLOW:
        return "no force"
    return f"{curse.get('art') or ''} {whole_number(curse.get('level'))}".strip()


def curses_title(_saga: Saga, place: Neighbour) -> str:
    return f"Curses ({sum(curse_points(c) for c in curses(place))} BP)"


def curses_grid(_saga: Saga, place: Neighbour) -> Grid:
    found = curses(place)
    return Grid(
        ["Curse", "Effect", "Condition", "Cost"],
        [
            [c["name"], _curse_effect(c), c.get("condition") or "", _curse_cost(c)]
            for c in found
        ],
        list(range(len(found))),
        "No curses yet: most tombs have at least one (LotN p. 34).",
        caps=[32, 12, 38, 0],
    )


def _curse_meta(curse: TombCurse) -> str:
    if (curse.get("kind") or et.EFFECT) == et.HOLLOW:
        return "written, without force"
    uses = whole_number(curse.get("uses")) or 1
    return (
        f"{_curse_effect(curse)}, {uses}/day, "
        f"Pen {whole_number(curse.get('penetration'))}"
    )


def curses_ledger(_saga: Saga, place: Neighbour) -> list[LedgerEntry]:
    found: list[LedgerEntry] = []
    for curse in curses(place):
        kind = curse.get("kind") or et.EFFECT
        hollow = kind == et.HOLLOW
        badge = "Hollow" if hollow else kind if kind != et.EFFECT else ""
        found.append(
            LedgerEntry(
                curse["name"],
                rubric="§",
                meta=_curse_meta(curse),
                badge=badge or str(curse.get("rdt") or ""),
                tone="label" if hollow else "text-error",
                body=f"[i]{escape(curse.get('condition') or '')}[/]",
                note=escape(curse.get("excoriation") or ""),
                subtitle="A hollow curse"
                if hollow
                else ", ".join(p for p in (_curse_effect(curse), kind) if p),
            )
        )
    return found


def curse_info(_saga: Saga, place: Neighbour, index: int) -> str:
    found = curses(place)
    if index >= len(found):
        return ""
    curse = found[index]
    hollow = (curse.get("kind") or et.EFFECT) == et.HOLLOW
    points = curse_points(curse)
    lines = [
        f"[$label]Condition:[/] [i]{escape(curse.get('condition') or '')}[/]",
        f"[$label]Excoriation:[/] {escape(curse.get('excoriation') or '')}",
    ]
    if not hollow:
        lines.append(f"[$label]Effect:[/] {escape(_curse_meta(curse))}")
        if curse.get("rdt"):
            lines.append(f"[$label]R / D / T:[/] {escape(str(curse.get('rdt')))}")
    lines += [
        f"[$label]Build Points:[/] {points}"
        + (
            " (a curse without force costs nothing)"
            if hollow
            else " (2 for every 5 levels)"
        ),
        "",
        "[dim]A curse triggers when its condition is broken, or when its text is "
        "defaced; once it has struck as many times as its uses a day, the text "
        "can be destroyed safely. A Malediction (Lesser, base 10; Greater, base "
        f"30) lasts until dispelled, and Warps ({L} pp. 34, 40-41).[/]",
    ]
    return "\n".join(lines)


def _not_hollow(values: dict[str, Any]) -> bool:
    return values.get("kind") != et.HOLLOW


def _curse_fields(entry: TombCurse | None) -> list[DialogField]:
    c: TombCurse = entry or {"name": ""}
    return [
        DialogField("name", "Name", "text", c.get("name", ""), required=True),
        DialogField(
            "kind",
            "Kind",
            "select",
            c.get("kind") or et.EFFECT,
            options=pairs(et.CURSE_KINDS),
            hint="A Malediction is beyond Hermetic magic: Lesser base 10, "
            "Greater base 30, until dispelled (LotN p. 41).",
        ),
        DialogField(
            "art",
            "Art",
            "text",
            c.get("art", ""),
            placeholder="e.g. CrMe",
            show_if=_not_hollow,
        ),
        DialogField(
            "level",
            "Level",
            "int",
            whole_number(c.get("level")),
            show_if=_not_hollow,
        ),
        DialogField(
            "rdt",
            "Range, Duration, Target",
            "text",
            c.get("rdt", ""),
            placeholder="e.g. Touch, Sun, Room",
            show_if=_not_hollow,
        ),
        DialogField(
            "uses",
            "Uses a day",
            "int",
            whole_number(c.get("uses")) or 1,
            show_if=_not_hollow,
        ),
        DialogField(
            "penetration",
            "Penetration",
            "int",
            whole_number(c.get("penetration")),
            hint="Rare: curses were meant for mundane robbers.",
            show_if=_not_hollow,
        ),
        DialogField(
            "condition",
            "Condition",
            "text",
            c.get("condition", ""),
            required=True,
            placeholder="e.g. Whoever breaks the seal of this tomb",
        ),
        DialogField("excoriation", "Excoriation", "area", c.get("excoriation", "")),
    ]


def _curse_values(values: dict[str, Any]) -> dict[str, Any]:
    kept = dict(values)
    if kept.get("kind") == et.HOLLOW:
        for key in ("art", "level", "rdt", "uses", "penetration"):
            kept.pop(key, None)
    return kept


def _curse_problem(values: dict[str, Any]) -> str | None:
    kind = values.get("kind") or et.EFFECT
    if (values.get("uses") or 1) < 1 and kind != et.HOLLOW:
        return "A curse strikes at least once a day."
    if (values.get("penetration") or 0) < 0:
        return "Penetration can't be below 0."
    return et.curse_problem(kind, values.get("level") or 0)


def _curse_live(
    place: Neighbour, entry: TombCurse | None, values: dict[str, Any]
) -> str:
    kind = values.get("kind") or et.EFFECT
    level = values.get("level") or 0
    points = et.curse_build_points(kind, level)
    why = (
        "a curse without force costs nothing"
        if kind == et.HOLLOW
        else f"2 for every 5 levels of {level}"
    )
    return (
        f"[b]{points} Build Points[/] ({why}); {_others(place, entry, points)}.\n"
        f"[dim]{L} pp. 40-41. Most curses are Touch and Room, one use a day.[/]"
    )


def curse_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return _ops(
        lambda: curses(place),
        "Curse",
        _curse_fields,
        lambda c: c["name"],
        _curse_values,
        _curse_problem,
        lambda entry, values: _curse_live(place, entry, values),
        "The Curse",
    )


# -- talismans and wards --


def wards_title(_saga: Saga, place: Neighbour) -> str:
    return f"Talismans and Wards ({sum(ward_points(w) for w in wards(place))} BP)"


def _ward_effect(ward: TombWard) -> str:
    return f"{ward.get('art') or ''} {whole_number(ward.get('level'))}".strip()


def wards_grid(_saga: Saga, place: Neighbour) -> Grid:
    found = wards(place)
    return Grid(
        ["Enchantment", "Effect", "Kind", "Overcome"],
        [
            [
                w["name"],
                _ward_effect(w),
                w.get("kind") or et.TALISMAN,
                f"EF {ward_ease(w)}, {ward_points(w)} BP",
            ]
            for w in found
        ],
        list(range(len(found))),
        "No talismans or wards yet.",
        caps=[30, 16, 12, 0],
    )


def _ward_meta(ward: TombWard) -> str:
    return f"{_ward_effect(ward)}, Pen {whole_number(ward.get('penetration'))}"


def wards_ledger(_saga: Saga, place: Neighbour) -> list[LedgerEntry]:
    return [
        LedgerEntry(
            w["name"],
            rubric="¶",
            meta=_ward_meta(w),
            badge=f"EF {ward_ease(w)}",
            tone="text-warning",
            body=escape(w.get("effect") or ""),
            note=f"[i]{escape(w.get('deactivation') or '')}[/]"
            if w.get("deactivation")
            else "",
            subtitle=f"{w.get('kind') or et.TALISMAN} · {_ward_effect(w)}",
        )
        for w in wards(place)
    ]


def _resistance_line(penetration: int) -> str:
    if penetration == 0:
        return "anyone with Magic Resistance passes untouched (Penetration 0)."
    return f"anyone whose Magic Resistance is at least {penetration} passes untouched."


def ward_info(_saga: Saga, place: Neighbour, index: int) -> str:
    found = wards(place)
    if index >= len(found):
        return ""
    ward = found[index]
    kind = ward.get("kind") or et.TALISMAN
    level = whole_number(ward.get("level"))
    penetration = whole_number(ward.get("penetration"))
    lines = [
        f"{escape(kind)}  ·  {escape(_ward_effect(ward))}, Penetration {penetration}"
        + (f", {escape(ward.get('uses', ''))}" if ward.get("uses") else ""),
        escape(ward.get("effect") or ""),
        "",
        f"[$label]To overcome it without magic:[/] Ease Factor {ward_ease(ward)} "
        f"({et.OVERCOME_BASE.get(kind, 6)} + magnitude {et.magnitude(level)}); "
        + _resistance_line(penetration),
    ]
    if ward.get("deactivation"):
        lines.append(f"[$label]Deactivated:[/] {escape(ward.get('deactivation', ''))}")
    lines += [
        f"[$label]Build Points:[/] {ward_points(ward)}",
        "",
        "[dim]Talismans harm or imprison: 6 + magnitude. Wards repel or hide: "
        "9 + magnitude. Ancient enchantments need not follow Hermetic rules: a "
        f"fire can be dodged ({L} pp. 35, 41-42).[/]",
    ]
    return "\n".join(lines)


def _ward_fields(entry: TombWard | None) -> list[DialogField]:
    w: TombWard = entry or {"name": ""}
    return [
        DialogField("name", "Name", "text", w.get("name", ""), required=True),
        DialogField(
            "kind",
            "Kind",
            "select",
            w.get("kind") or et.TALISMAN,
            options=pairs(et.ENCHANTMENT_KINDS),
            hint="A talisman harms or imprisons; a ward repels or hides.",
        ),
        DialogField("art", "Art", "text", w.get("art", ""), placeholder="e.g. ReCo"),
        DialogField("level", "Level", "int", whole_number(w.get("level"))),
        DialogField(
            "penetration",
            "Penetration",
            "int",
            whole_number(w.get("penetration")),
            hint="Most talismans have none; wards against spirits may.",
        ),
        DialogField(
            "uses",
            "Uses",
            "text",
            w.get("uses", ""),
            placeholder="e.g. 1/day, unlimited, constant",
        ),
        DialogField("effect", "What it does", "area", w.get("effect", "")),
        DialogField(
            "deactivation",
            "How it is made inert",
            "text",
            w.get("deactivation", ""),
            placeholder="e.g. Struck by a Rego Terram effect, inert until sunset",
            hint="A talisman, by a spell effect; a ward, by a deed at a place "
            "and time (LotN p. 35).",
        ),
    ]


def _ward_problem(values: dict[str, Any]) -> str | None:
    if (values.get("level") or 0) < 1:
        return "An enchantment has a level of at least 1."
    if (values.get("penetration") or 0) < 0:
        return "Penetration can't be below 0."
    return None


def _ward_live(place: Neighbour, entry: TombWard | None, values: dict[str, Any]) -> str:
    kind = values.get("kind") or et.TALISMAN
    level = values.get("level") or 0
    points = et.enchantment_build_points(level)
    penetration = values.get("penetration") or 0
    return (
        f"Ease Factor {et.overcome_ease(kind, level)} to overcome it without magic "
        f"({et.OVERCOME_BASE.get(kind, 6)} + magnitude {et.magnitude(level)}); "
        f"{_resistance_line(penetration)}\n"
        f"[b]{points} Build Points[/]; {_others(place, entry, points)}.\n"
        f"[dim]{L} pp. 35, 41-42.[/]"
    )


def ward_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return _ops(
        lambda: wards(place),
        "Talisman or Ward",
        _ward_fields,
        lambda w: w["name"],
        dict,
        _ward_problem,
        lambda entry, values: _ward_live(place, entry, values),
        "The Enchantment",
    )


# -- traps --


def _harm_name(trap: TombTrap) -> str:
    found = et.HARMS.get(trap.get("harm") or "")
    return found.name if found is not None else ""


def traps_title(_saga: Saga, place: Neighbour) -> str:
    return f"Traps ({sum(trap_points(t) for t in traps(place))} BP)"


def traps_grid(_saga: Saga, place: Neighbour) -> Grid:
    found = traps(place)
    return Grid(
        ["Trap", "Harm", "Avoid", "Cost"],
        [
            [
                t["name"],
                _harm_name(t),
                f"EF {whole_number(t.get('ease'))}",
                f"{trap_points(t)} BP",
            ]
            for t in found
        ],
        list(range(len(found))),
        "No traps yet.",
        caps=[26, 38, 8, 0],
    )


def traps_ledger(_saga: Saga, place: Neighbour) -> list[LedgerEntry]:
    return [
        LedgerEntry(
            t["name"],
            rubric="!",
            meta=f"EF {whole_number(t.get('ease'))} to avoid",
            badge=f"{trap_points(t)} BP",
            tone="label",
            body=escape(t.get("text") or ""),
            note="[i]Resets itself.[/]" if t.get("resets") else "",
            subtitle=_harm_name(t),
        )
        for t in traps(place)
    ]


def _trap_cost_line(harm: str, ease: int) -> str:
    found = et.HARMS[harm]
    return (
        f"{found.build_points} for the harm + {et.AVOID[ease]} for Ease Factor "
        f"{ease} = {et.trap_build_points(harm, ease)}"
    )


TRAP_RULE = (
    "When it springs, each character says one thing he does and rolls for it "
    "against the Ease Factor, adjusted by 3 or 6 for the action; in Quickness "
    "order, the one in danger first, the trap last. A magus answers with a "
    "Fast-Cast spell. Spotting it first (Per + Awareness) gives time to deal "
    "with it: −3 with perfect light, +3 by a candle, +6 in near darkness "
    f"({L} pp. 32-33, 44)."
)


def trap_info(_saga: Saga, place: Neighbour, index: int) -> str:
    found = traps(place)
    if index >= len(found):
        return ""
    trap = found[index]
    harm = trap.get("harm") or "scare"
    ease = whole_number(trap.get("ease"))
    lines = [
        f"{escape(_harm_name(trap))}  ·  Ease Factor {ease}",
        escape(trap.get("text") or ""),
        "",
    ]
    if harm in et.HARMS and ease in et.AVOID:
        lines.append(f"[$label]Build Points:[/] {_trap_cost_line(harm, ease)}")
    lines.append(
        "[$label]Resets:[/] "
        + ("by itself" if trap.get("resets") else "by hand, or works only once")
    )
    lines.append(f"[dim]{TRAP_RULE}[/]")
    return "\n".join(lines)


def _trap_fields(entry: TombTrap | None) -> list[DialogField]:
    t: TombTrap = entry or {"name": ""}
    return [
        DialogField("name", "Name", "text", t.get("name", ""), required=True),
        DialogField(
            "harm",
            "What it does",
            "select",
            t.get("harm") or "scare",
            options=[(h.name, h.key) for h in et.HARMS.values()],
        ),
        DialogField(
            "ease",
            "Ease Factor to avoid",
            "select",
            str(whole_number(t.get("ease")) or 3),
            options=[
                (f"{ease}: {words}", str(ease))
                for ease, words in et.AVOID_WORDS.items()
            ],
        ),
        DialogField("text", "How it works", "area", t.get("text", "")),
        DialogField("resets", "Resets itself", "check", bool(t.get("resets"))),
    ]


def _trap_values(values: dict[str, Any]) -> dict[str, Any]:
    return {**values, "ease": whole_number(values.get("ease")) or 3}


def _trap_problem(values: dict[str, Any]) -> str | None:
    if values.get("harm") not in et.HARMS:
        return "Choose what the trap does."
    if whole_number(values.get("ease")) not in et.AVOID:
        return "Choose the Ease Factor to avoid it."
    return None


def _trap_live(place: Neighbour, entry: TombTrap | None, values: dict[str, Any]) -> str:
    harm = values.get("harm") or "scare"
    ease = whole_number(values.get("ease")) or 3
    if harm not in et.HARMS or ease not in et.AVOID:
        return ""
    points = et.trap_build_points(harm, ease)
    return (
        f"{_trap_cost_line(harm, ease).rsplit(' = ', 1)[0]} = [b]{points} Build "
        f"Points[/]; {_others(place, entry, points)}.\n"
        f"[dim]{L} p. 44. Most mechanical traps must be reset by hand.[/]"
    )


def trap_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return _ops(
        lambda: traps(place),
        "Trap",
        _trap_fields,
        lambda t: t["name"],
        _trap_values,
        _trap_problem,
        lambda entry, values: _trap_live(place, entry, values),
        "The Trap",
    )


# -- Overcome It --

#: The rolls a character most often makes against a trap (pp. 33, 43):
#: a Characteristic and an Ability, or a Characteristic alone.
ROLLS: tuple[str, ...] = (
    "Qik + Athletics",
    "Dex + Athletics",
    "Str + Athletics",
    "Str + Brawl",
    "Per + Awareness",
    "Int + Concentration",
    "Com + Leadership",
    "Sta",
    "Str",
)

_CHARACTERISTICS: dict[str, str] = {
    "Int": "intelligence",
    "Per": "perception",
    "Str": "strength",
    "Sta": "stamina",
    "Pre": "presence",
    "Com": "communication",
    "Dex": "dexterity",
    "Qik": "quickness",
}


def roll_score(character: Character, roll: str) -> tuple[int, str]:
    """A character's Characteristic + Ability for `roll` ("Qik +
    Athletics", or "Sta" alone), and how it reads."""
    short, _, ability = (part.strip() for part in roll.partition("+"))
    name = _CHARACTERISTICS.get(short)
    if name is None:
        raise ValueError(f"No Characteristic is called {short!r}.")
    value = getattr(character.characteristics, name)
    parts = [f"{name.capitalize()} {value}"]
    if ability:
        score, bonus = ability_score(character, ability)
        value += score + bonus
        parts.append(f"{ability} {score + bonus}")
    return value, " + ".join(parts)


def _overcome_fields(saga: Saga) -> list[DialogField]:
    return [
        DialogField(
            "who",
            "Who acts",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
        ),
        DialogField(
            "in_danger",
            "In danger",
            "check",
            False,
            hint="The one the trap is springing on acts first.",
        ),
        DialogField(
            "action",
            "What he does",
            "text",
            "",
            placeholder="e.g. Hears the stone shift and throws himself back",
        ),
        DialogField(
            "fast_cast",
            "A Fast-Cast spell",
            "check",
            False,
            hint="A magus's spell is judged on its own, not against the trap.",
        ),
        DialogField(
            "roll",
            "His roll",
            "select",
            ROLLS[0],
            options=pairs(ROLLS),
            show_if=lambda values: not values.get("fast_cast"),
        ),
        DialogField(
            "adjust",
            "Harder or easier",
            "int",
            0,
            hint="The storyguide's adjustment for this action: 3 or 6 either way.",
            show_if=lambda values: not values.get("fast_cast"),
        ),
        DialogField(
            "light",
            "Light",
            "select",
            next(iter(et.LIGHT)),
            options=pairs(tuple(et.LIGHT)),
            hint="For spotting its trigger first (Per + Awareness).",
        ),
    ]


def _order(saga: Saga, values: dict[str, Any]) -> str:
    """Who acts in what order, with the one acting in danger: the player
    covenants' characters by Quickness."""
    who = saga.character(values.get("who"))
    if who is None:
        return ""
    played = {c.id for c in saga.covenants if c.played}
    party = [c for c in saga.characters if c.covenant_id in played or c is who]
    order = et.action_order(
        [
            (
                c.name,
                c.characteristics.quickness,
                c is who and bool(values.get("in_danger")),
            )
            for c in party
        ]
    )
    return ", ".join(order) + ", then the trap"


def _overcome_live(saga: Saga, trap: TombTrap, values: dict[str, Any]) -> str:
    base = whole_number(trap.get("ease"))
    lines = [f"[b]{escape(trap['name'])}[/], Ease Factor {base}"]
    who = saga.character(values.get("who"))
    if values.get("fast_cast"):
        lines[0] += "."
        lines.append(et.FAST_CAST)
    else:
        ease = et.action_ease(base, values.get("adjust") or 0)
        lines[0] += f", adjusted to {ease}." if ease != base else "."
        if who is not None:
            _score, words = roll_score(who, values.get("roll") or ROLLS[0])
            lines.append(f"{escape(words)} + stress die against {ease}.")
    order = _order(saga, values)
    if order:
        lines.append(f"Order: {escape(order)}.")
    lines.append(
        f"Those who fail and aren't helped suffer it: {escape(_harm_name(trap).lower())}."
    )
    light = values.get("light") or next(iter(et.LIGHT))
    lines.append(
        f"[dim]Spotting its trigger first: Per + Awareness against "
        f"{et.spot_ease(base, light)} ({escape(light.lower())}; {L} pp. 32-33, 44).[/]"
    )
    return "\n".join(lines)


def overcome_trap(
    saga: Saga, place: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Overcome It on the chosen trap: who acts, what he does and
    his roll; Roll rolls a stress die against the trap's Ease Factor and
    offers to write the outcome in the place's diary."""
    listed = traps(place)
    if index >= len(listed):
        return Refuse("Overcome It", "Choose a trap first.")
    trap = listed[index]
    if not saga.characters:
        return Refuse("Overcome It", "The saga has no characters to act.")

    def apply(values: dict[str, Any]) -> Any:
        who = saga.character(values.get("who"))
        if who is None:
            return Refuse("Overcome It", "Choose who acts.")
        doing = str(values.get("action") or "").strip()
        if values.get("fast_cast"):
            return notes(
                f"{escape(who.name)} answers {escape(trap['name'])} with a "
                "Fast-Cast spell: cast it from his sheet. It is judged on its "
                f"own, not against the trap's Ease Factor ({L} p. 33)."
            )
        ease = et.action_ease(whole_number(trap.get("ease")), values.get("adjust") or 0)
        score, words = roll_score(who, values.get("roll") or ROLLS[0])
        die = dice.stress_die(rng or random.Random(), saga=saga)
        total = score + die.value
        if die.botched:
            outcome = "botches"
        elif total >= ease:
            outcome = f"succeeds ({total} against {ease})"
        else:
            outcome = f"fails ({total} against {ease})"
        line = (
            f"{who.name}{f', {doing},' if doing else ''} {outcome} against "
            f"{trap['name']}."
        )

        def write() -> None:
            place_events.diary(place).append(
                {
                    "year": saga.current_year,
                    "season": saga.current_season,
                    "text": line,
                }
            )

        return Confirm(
            f"{escape(words)} + {'a botch' if die.botched else die.value} "
            f"= {total}.\n\n[b]{escape(line)}[/]\n\nWrite it in "
            f"{escape(place.name)}'s diary?",
            write,
            yes_label="Write",
            title="Overcome It",
        )

    return Form(
        f"Overcome It: {escape(trap['name'])}",
        lambda: _overcome_fields(saga),
        apply,
        live=lambda values: _overcome_live(saga, trap, values),
        inspector="The Trap Springs",
        save_label="Roll",
        help_id="overcome-trap",
    )


# -- marking a place as a tomb, and its tab --


def mark_fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """The Tomb box on a place's form: offered with Lands of the Nile in
    play, or on a place already marked (and always to New Place's list
    of the keys its details keep)."""
    marked = place is not None and is_tomb(place)
    offered = (
        place is None
        or marked
        or sourcebooks.in_play("LotN", sourcebooks.saga_books(saga))
    )
    if not offered:
        return []
    return [
        DialogField(
            TOMB,
            "A tomb",
            "check",
            marked,
            hint="Shows its Tomb tab: designed like a covenant, with its curses, "
            "talismans, wards and traps (Lands of the Nile pp. 32-46).",
        )
    ]


TOMB_BLOCK = KindBlock(
    TOMB_SECTION,
    "The Tomb",
    text=tomb_text,
    edit=edit_tomb,
    edit_label="Edit Tomb",
    facts=tomb_facts,
    prose=tomb_prose,
    facts_inline=True,
)

TOMB_TAB = KindTab(
    "Tomb",
    "tab-nb-tomb",
    (
        KindList(
            TOMB_CURSES_SECTION,
            curses_title,
            curses_grid,
            curse_ops,
            curse_info,
            ledger=curses_ledger,
        ),
        KindList(
            TOMB_WARDS_SECTION,
            wards_title,
            wards_grid,
            ward_ops,
            ward_info,
            ledger=wards_ledger,
        ),
        KindList(
            TOMB_TRAPS_SECTION,
            traps_title,
            traps_grid,
            trap_ops,
            trap_info,
            ledger=traps_ledger,
        ),
    ),
    blocks=(TOMB_BLOCK,),
    icon="place",
    panel="[dim]Choose a curse, a talisman or a trap.[/]",
    shown=is_tomb,
)
