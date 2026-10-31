"""A place marked as a tomb, designed like a covenant (Lands of the Nile
pp. 32-35, 40-46): its kind, aura and Build Points, its curses, its
talismans and wards, and its traps, on the place's Tomb tab, and More's
Overcome It when a trap springs or a talisman or ward stands in the way.
The rules are rules.egyptian_tombs. The tomb is fixed once built; Overcome
It holds only what varies: who is there, what each does and rolls, who
suffers it, and whether the trap stays sprung. A puzzle stays as words on
its place, played by the troupe.

A place is marked a tomb by the Tomb box on its form; only then is the
tab shown. The tomb doesn't set the place's own aura: its burial
ground's tether is shown, for the place's Tethers to name when the aura
change option is on.

Kept in Neighbour.details: "tomb" (the mark), "tomb_kind", "tomb_centuries",
"tomb_decay", "tomb_hooks", "tomb_hook_points", "tomb_boons",
"tomb_other", "tomb_other_bp" and "tomb_description", and the lists
"tomb_curses" (TombCurse), "tomb_wards" (TombWard) and "tomb_traps"
(TombTrap). A place of a book's examples has the "examples" kind, which
has no budget.

Pattern: the tab is one more place kind tab (neighbour_lists.KindTab),
the Strategy the Regio and Roll Tables tabs use: a block and three
KindLists, each with its `_*_fields` builder. Build Points are small
rule functions over the book's two tables, which the lists, the forms'
inspectors and the tomb's total all read. Overcome It is one form a step:
each builds the next from a Springing, which keeps what has been said so
far (Command, as every multi-step action here)."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
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
from .rules.derived import carried_load, encumbrance
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
    #: The Ease Factor printed, where it isn't 6 or 9 + the magnitude (0:
    #: the rule's).
    ease: int


class TombTrap(TypedDict, total=False):
    """A trap: what it does, the Ease Factor to avoid it, and the roll
    and Ease Factor to spot it where the book gives them."""

    name: Required[str]
    harm: str
    ease: int
    text: str
    resets: bool
    #: It works once, and can't be reset.
    once: bool
    #: Build Points of further harms, for a trap treated as several.
    further_bp: int
    #: The roll the book gives for avoiding it ("Qik + Athletics - Encumbrance").
    roll: str
    #: The Ease Factor to spot it, where it isn't the trap's own (0: its own).
    spot: int
    #: It has gone off and isn't reset yet.
    sprung: bool


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
    return et.trap_build_points(harm, ease, whole_number(trap.get("further_bp")))


def ward_ease(ward: TombWard) -> int | None:
    """The Ease Factor to overcome an enchantment without magic: the one
    printed if any, else the rule's; None when it is no obstacle."""
    kind = ward.get("kind") or et.TALISMAN
    if kind == et.NO_OBSTACLE:
        return None
    return whole_number(ward.get("ease")) or et.overcome_ease(
        kind, whole_number(ward.get("level"))
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
    if allowed == 0:
        return f"{total} in all"
    words = f"{total} of the tomb's {allowed} spent"
    if total > allowed:
        return f"[$text-error]{words}: {total - allowed} too many[/]"
    return words


# -- the tomb --


def tomb_facts(_saga: Saga, place: Neighbour) -> list[Fact]:
    d = place.details
    found = _kind(place)
    if found is et.EXAMPLES:
        return [
            Fact("Kind", found.name),
            Fact("Build Points", f"{spent_total(place)} in all"),
        ]
    decay = whole_number(d.get("tomb_decay"))
    aura = et.tomb_aura(found.key, decay)
    own = whole_number(d.get("aura"))
    centuries = whole_number(d.get("tomb_centuries"))
    hook_points = whole_number(d.get("tomb_hook_points"))
    hooks = str(d.get("tomb_hooks") or "").strip()
    return [
        Fact("Kind", found.name),
        Fact("Build Points", f"{spent_total(place)} of {found.build_points}"),
        Fact("Magic aura", _aura_words(aura, found.aura, decay, own)),
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


def _aura_words(aura: int, base: int, decay: int, own: int) -> str:
    """The tomb's Magic aura, or the place's own where Boons or a fine
    site raise it above that (p. 40)."""
    if own > aura:
        return f"{own} (base {base}; raised by Boons or its site)"
    return f"{aura} (base {base}; decayed)" if decay > 0 else str(aura)


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
    kinds = list(et.KINDS.values())
    if d.get("tomb_kind") == et.EXAMPLES.key:
        kinds.append(et.EXAMPLES)
    return [
        DialogField(
            "tomb_kind",
            "Kind",
            "select",
            d.get("tomb_kind") or et.DEFAULT_KIND,
            options=[(k.name, k.key) for k in kinds],
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
        DialogField(
            "tomb_boons",
            "Boons",
            "text",
            d.get("tomb_boons") or "",
            hint="Wealth: its grave goods are intact, perhaps Unknown. A tomb in "
            "Nubia should buy Seclusion (LotN p. 44).",
        ),
        DialogField(
            "tomb_other",
            "Other resources",
            "text",
            d.get("tomb_other") or "",
            placeholder="e.g. inscriptions 21, a guardian ghost 6, vis 20",
            hint="Inscriptions, ghosts and vis at a covenant's costs; a guardian "
            "at its highest Martial Ability or Brawl (LotN p. 42).",
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
    if allowed == 0:
        return f"{total} in all"
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
    lines = [f"[$label]Excoriation:[/] {escape(curse.get('excoriation') or '')}"]
    if curse.get("condition"):
        lines.insert(
            0, f"[$label]Condition:[/] [i]{escape(curse.get('condition', ''))}[/]"
        )
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
                f"{_ward_ease_words(w)}, {ward_points(w)} BP",
            ]
            for w in found
        ],
        list(range(len(found))),
        "No talismans or wards yet.",
        caps=[30, 16, 12, 0],
    )


def _ward_ease_words(ward: TombWard) -> str:
    ease = ward_ease(ward)
    return "no roll" if ease is None else f"EF {ease}"


def _ward_meta(ward: TombWard) -> str:
    return f"{_ward_effect(ward)}, Pen {whole_number(ward.get('penetration'))}"


def wards_ledger(_saga: Saga, place: Neighbour) -> list[LedgerEntry]:
    return [
        LedgerEntry(
            w["name"],
            rubric="¶",
            meta=_ward_meta(w),
            badge=_ward_ease_words(w),
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


def _overcome_line(ward: TombWard, kind: str, level: int, penetration: int) -> str:
    """How an enchantment is overcome, as markup."""
    ease = ward_ease(ward)
    if ease is None:
        return "[$label]To overcome it:[/] it stands in nobody's way."
    why = (
        "as printed"
        if whole_number(ward.get("ease"))
        else f"{et.OVERCOME_BASE.get(kind, 6)} + magnitude {et.magnitude(level)}"
    )
    return (
        f"[$label]To overcome it without magic:[/] Ease Factor {ease} ({why}); "
        + _resistance_line(penetration)
    )


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
        _overcome_line(ward, kind, level, penetration),
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
            hint="A talisman harms or imprisons; a ward repels or hides; some "
            "do neither, and need no defence (LotN p. 42).",
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
        DialogField(
            "ease",
            "Ease Factor, if another",
            "int",
            whole_number(w.get("ease")),
            hint="0 for 6 or 9 + its magnitude; else what the book or the "
            "storyguide sets.",
        ),
    ]


def _ward_problem(values: dict[str, Any]) -> str | None:
    if (values.get("level") or 0) < 1:
        return "An enchantment has a level of at least 1."
    if (values.get("penetration") or 0) < 0:
        return "Penetration can't be below 0."
    if (values.get("ease") or 0) < 0:
        return "An Ease Factor can't be below 0."
    return None


def _ward_live(place: Neighbour, entry: TombWard | None, values: dict[str, Any]) -> str:
    kind = values.get("kind") or et.TALISMAN
    level = values.get("level") or 0
    points = et.enchantment_build_points(level)
    penetration = values.get("penetration") or 0
    tail = (
        f"[b]{points} Build Points[/]; {_others(place, entry, points)}.\n"
        f"[dim]{L} pp. 35, 41-42.[/]"
    )
    if kind == et.NO_OBSTACLE:
        return f"It stands in nobody's way.\n{tail}"
    ease = values.get("ease") or et.overcome_ease(kind, level)
    why = (
        "set by hand"
        if values.get("ease")
        else f"{et.OVERCOME_BASE.get(kind, 6)} + magnitude {et.magnitude(level)}"
    )
    return (
        f"Ease Factor {ease} to overcome it without magic ({why}); "
        f"{_resistance_line(penetration)}\n{tail}"
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
                f"EF {whole_number(t.get('ease'))}"
                + (", sprung" if t.get("sprung") else ""),
                f"{trap_points(t)} BP",
            ]
            for t in found
        ],
        list(range(len(found))),
        "No traps yet.",
        caps=[26, 38, 14, 0],
    )


def _trap_note(trap: TombTrap) -> str:
    if trap.get("sprung"):
        return "[i]Sprung, and not reset.[/]"
    return "[i]Resets itself.[/]" if trap.get("resets") else ""


def traps_ledger(_saga: Saga, place: Neighbour) -> list[LedgerEntry]:
    return [
        LedgerEntry(
            t["name"],
            rubric="!",
            meta=f"EF {whole_number(t.get('ease'))} to avoid",
            badge=f"{trap_points(t)} BP",
            tone="label",
            body=escape(t.get("text") or ""),
            note=_trap_note(t),
            subtitle=_harm_name(t),
        )
        for t in traps(place)
    ]


def _trap_cost_line(harm: str, ease: int, further: int = 0) -> str:
    found = et.HARMS[harm]
    more = f" + {further} for its further harms" if further else ""
    return (
        f"{found.build_points} for the harm{more} + {et.AVOID[ease]} for Ease "
        f"Factor {ease} = {et.trap_build_points(harm, ease, further)}"
    )


TRAP_RULE = (
    "When it springs, each character says one thing he does and rolls for it "
    "against the Ease Factor, adjusted by 3, 6 or more for the action; in "
    "Quickness order, the one in danger first, the trap last. A magus answers "
    "with a Fast-Cast spell. Spotting it first (Per + Awareness) gives time to "
    "deal with it: −3 with perfect light, +3 by a candle, +6 in near darkness "
    f"({L} pp. 32-33, 44). {et.EVASION}"
)


def _resets_words(trap: TombTrap) -> str:
    if trap.get("once"):
        return "works only once"
    return "by itself" if trap.get("resets") else "by hand"


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
    if trap.get("roll"):
        lines.append(f"[$label]Avoided by:[/] {escape(trap.get('roll', ''))}")
    if trap.get("spot"):
        lines.append(f"[$label]To spot it:[/] Ease Factor {trap.get('spot')}")
    if harm in et.HARMS and ease in et.AVOID:
        cost = _trap_cost_line(harm, ease, whole_number(trap.get("further_bp")))
        lines.append(f"[$label]Build Points:[/] {cost}")
    lines.append(f"[$label]Resets:[/] {_resets_words(trap)}")
    if trap.get("sprung"):
        lines.append("[$label]Now:[/] sprung, and not reset")
    lines.append(f"[dim]{TRAP_RULE}[/]")
    return "\n".join(lines)


def _trap_fields(entry: TombTrap | None) -> list[DialogField]:
    t: TombTrap = entry or {"name": ""}
    found = [
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
        DialogField(
            "further_bp",
            "Further harms' Build Points",
            "int",
            whole_number(t.get("further_bp")),
            hint="For a trap treated as several: what its other harms cost.",
        ),
        DialogField(
            "roll",
            "The roll to avoid it",
            "text",
            t.get("roll", ""),
            placeholder="e.g. Qik + Athletics - Encumbrance",
            hint="Offered first when it springs; the troupe may agree another.",
        ),
        DialogField(
            "spot",
            "Ease Factor to spot it",
            "int",
            whole_number(t.get("spot")),
            hint="0 for the trap's own; assumes torches or lanterns.",
        ),
        DialogField("text", "How it works", "area", t.get("text", "")),
        DialogField("resets", "Resets itself", "check", bool(t.get("resets"))),
        DialogField("once", "Works only once", "check", bool(t.get("once"))),
    ]
    if entry is not None:
        found.append(DialogField("sprung", "Sprung", "check", bool(t.get("sprung"))))
    return found


def _trap_values(values: dict[str, Any]) -> dict[str, Any]:
    kept = {**values, "ease": whole_number(values.get("ease")) or 3}
    kept["roll"] = str(kept.get("roll") or "").strip()
    return kept


def _trap_problem(values: dict[str, Any]) -> str | None:
    if values.get("harm") not in et.HARMS:
        return "Choose what the trap does."
    if whole_number(values.get("ease")) not in et.AVOID:
        return "Choose the Ease Factor to avoid it."
    if (values.get("further_bp") or 0) < 0 or (values.get("spot") or 0) < 0:
        return "Build Points and Ease Factors can't be below 0."
    if values.get("resets") and values.get("once"):
        return "A trap that works only once doesn't reset itself."
    return roll_problem(str(values.get("roll") or ""))


def _trap_live(place: Neighbour, entry: TombTrap | None, values: dict[str, Any]) -> str:
    harm = values.get("harm") or "scare"
    ease = whole_number(values.get("ease")) or 3
    if harm not in et.HARMS or ease not in et.AVOID:
        return ""
    further = values.get("further_bp") or 0
    points = et.trap_build_points(harm, ease, further)
    return (
        f"{_trap_cost_line(harm, ease, further).rsplit(' = ', 1)[0]} = [b]{points} "
        f"Build Points[/]; {_others(place, entry, points)}.\n"
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

#: Rolls the book names against traps (pp. 33, 43, 46, 92), for a hint:
#: the troupe agrees each one, and any Characteristic + Ability will do.
ROLLS: tuple[str, ...] = (
    "Qik + Athletics - Encumbrance",
    "Dex + Athletics - Encumbrance",
    "Str + Athletics - Encumbrance",
    "Per + Awareness",
    "Int + Concentration",
    "Com + Leadership",
    "Sta",
)

_ENCUMBRANCE = "encumbrance"

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


def _roll_parts(roll: str) -> tuple[str, str, bool]:
    """A roll's Characteristic, Ability ("" for none) and whether it takes
    off Encumbrance."""
    head, minus, tail = roll.partition(" - ")
    short, _, ability = (part.strip() for part in head.partition("+"))
    return short, ability, bool(minus) and tail.strip().lower() == _ENCUMBRANCE


def roll_problem(roll: str) -> str | None:
    """Why a roll can't be read ("" is no roll, and fine)."""
    text = roll.strip()
    if not text:
        return None
    short, _ability, less = _roll_parts(text)
    if short not in _CHARACTERISTICS:
        names = ", ".join(_CHARACTERISTICS)
        return f"A roll starts with a Characteristic ({names}), as in {ROLLS[0]}."
    if " - " in text and not less:
        return "The only thing a roll here takes off is Encumbrance."
    return None


def roll_score(character: Character, roll: str) -> tuple[int, str]:
    """A character's Characteristic + Ability for `roll` ("Qik + Athletics
    - Encumbrance", or "Sta" alone), and how it reads."""
    short, ability, less = _roll_parts(roll)
    name = _CHARACTERISTICS.get(short)
    if name is None:
        raise ValueError(f"No Characteristic is called {short!r}.")
    value = getattr(character.characteristics, name)
    parts = [f"{name.capitalize()} {value}"]
    if ability:
        score, bonus = ability_score(character, ability)
        value += score + bonus
        parts.append(f"{ability} {score + bonus}")
    words = " + ".join(parts)
    if less:
        load = encumbrance(
            carried_load(character.inventory), character.characteristics.strength
        )
        value -= load
        words += f" - Encumbrance {load}"
    return value, words


@dataclass(frozen=True)
class Obstacle:
    """What Overcome It faces: a trap, or a talisman or ward sprung like
    one (LotN pp. 35, 42)."""

    name: str
    ease: int
    harm: str
    text: str = ""
    #: The roll the book gives, offered first.
    roll: str = ""
    #: The Ease Factor to spot it first; None for one that can't be.
    spot: int | None = None
    #: What Magic Resistance must reach to pass it; None for a trap.
    penetration: int | None = None
    #: The trap itself, to mark sprung or reset.
    trap: TombTrap | None = None


def _trap_obstacle(trap: TombTrap) -> Obstacle:
    ease = whole_number(trap.get("ease"))
    return Obstacle(
        trap["name"],
        ease,
        _harm_name(trap).lower(),
        trap.get("text") or "",
        trap.get("roll") or "",
        whole_number(trap.get("spot")) or ease,
        trap=trap,
    )


def _ward_obstacle(ward: TombWard, ease: int) -> Obstacle:
    return Obstacle(
        ward["name"],
        ease,
        "its effect",
        ward.get("effect") or "",
        penetration=whole_number(ward.get("penetration")),
    )


@dataclass
class Acted:
    """One character's turn: what the diary says of it, and whether it
    took him clear."""

    who: Character
    line: str
    clear: bool


@dataclass
class Springing:
    """Overcome It under way: who is there, in acting order, and what has
    been said so far. Nothing here is kept in the saga."""

    saga: Saga
    place: Neighbour
    obstacle: Obstacle
    party: list[Character]
    rng: random.Random
    acted: list[Acted] = field(default_factory=list)
    #: How the look for it went, as plain lines.
    spotting: list[str] = field(default_factory=list)


def _party(saga: Saga) -> list[Character]:
    """Who might be there: the player covenants' characters, or all of
    them in a saga with none."""
    played = {c.id for c in saga.covenants if c.played}
    return [c for c in saga.characters if c.covenant_id in played] or saga.characters


def _with_key(character: Character) -> str:
    return f"with_{character.id}"


def _chosen(
    saga: Saga, values: dict[str, Any]
) -> tuple[Character | None, list[Character]]:
    """The one in danger, and everyone there, in acting order: he first,
    then by Quickness (the trap acts after them all, p. 33)."""
    danger = saga.character(values.get("who"))
    if danger is None:
        return None, []
    there = {c.id: c for c in _party(saga) if values.get(_with_key(c))}
    there[danger.id] = danger
    order = et.action_order(
        [(key, c.characteristics.quickness, c is danger) for key, c in there.items()]
    )
    return danger, [there[key] for key in order]


def _opening_fields(saga: Saga, obstacle: Obstacle) -> list[DialogField]:
    found = [
        DialogField(
            "who",
            "Who is in danger",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
            hint="The one it is springing on acts first, whatever his Quickness.",
        ),
        *(
            DialogField(_with_key(c), f"With him: {escape(c.name)}", "check", False)
            for c in _party(saga)
        ),
    ]
    if obstacle.spot is None:
        return found
    return [
        *found,
        DialogField(
            "look",
            "They look for it first",
            "check",
            False,
            hint="Per + Awareness for each of them, before it springs.",
        ),
        DialogField(
            "light",
            "Light",
            "select",
            next(iter(et.LIGHT)),
            options=pairs(tuple(et.LIGHT)),
            show_if=lambda values: bool(values.get("look")),
        ),
    ]


def _order_words(party: list[Character]) -> str:
    return ", ".join([*(c.name for c in party), "then it acts"])


def _opening_live(saga: Saga, obstacle: Obstacle, values: dict[str, Any]) -> str:
    lines = [f"[b]{escape(obstacle.name)}[/], Ease Factor {obstacle.ease}."]
    if obstacle.text:
        lines.append(escape(obstacle.text))
    _danger, party = _chosen(saga, values)
    if party:
        lines.append(f"Order: {escape(_order_words(party))}.")
    if obstacle.penetration is not None:
        words = _resistance_line(obstacle.penetration)
        lines.append(words[0].upper() + words[1:])
    if obstacle.spot is not None:
        light = values.get("light") or next(iter(et.LIGHT))
        lines.append(
            f"[dim]Per + Awareness against {et.spot_ease(obstacle.spot, light)} "
            f"to spot it ({escape(light.lower())}; {L} p. 44). {et.AWARE}[/]"
        )
    return "\n".join(lines)


def _opening(
    saga: Saga, place: Neighbour, obstacle: Obstacle, rng: random.Random
) -> Form:
    def apply(values: dict[str, Any]) -> Any:
        danger, party = _chosen(saga, values)
        if danger is None:
            return Refuse("Overcome It", "Choose who is in danger.")
        spring = Springing(saga, place, obstacle, party, rng)
        if not values.get("look") or obstacle.spot is None:
            return action_form(spring)
        ease = et.spot_ease(obstacle.spot, values.get("light") or "")
        seen = [c for c in party if _spots(spring, c, ease)]
        if seen:
            return seen_form(spring, seen)
        return action_form(spring)

    return Form(
        f"Overcome It: {escape(obstacle.name)}",
        lambda: _opening_fields(saga, obstacle),
        apply,
        live=lambda values: _opening_live(saga, obstacle, values),
        inspector="It Stands in the Way",
        save_label="Next",
        help_id="overcome-trap",
    )


def _spots(spring: Springing, who: Character, ease: int) -> bool:
    """Rolls `who`'s Per + Awareness against `ease`, noting how it went."""
    score, words = roll_score(who, "Per + Awareness")
    die = dice.stress_die(spring.rng, saga=spring.saga)
    total = score + die.value
    seen = total >= ease and not die.botched
    spring.spotting.append(
        f"{who.name}: {words} + {'a botch' if die.botched else die.value} = "
        f"{total} against {ease}: {'spots it' if seen else 'sees nothing'}."
    )
    return seen


LEAVE, DEAL, SPRINGS = "leave", "deal", "springs"


def seen_form(spring: Springing, seen: list[Character]) -> Form:
    """Someone spotted it unsprung: there is time to choose what to do."""
    who = ", ".join(c.name for c in seen)
    obstacle = spring.obstacle

    def apply(values: dict[str, Any]) -> Any:
        then = values.get("then")
        if then == SPRINGS:
            return action_form(spring)
        if then == DEAL:
            if obstacle.trap is not None:
                obstacle.trap["sprung"] = True
            line = f"{who} found {obstacle.name} before it sprang, and dealt with it."
        else:
            line = f"{who} found {obstacle.name} before it sprang, and left it be."
        _write(spring, line)
        return notes(line)

    return Form(
        f"Spotted: {escape(obstacle.name)}",
        lambda: [
            DialogField(
                "then",
                "What then",
                "select",
                DEAL,
                options=[
                    ("They deal with it", DEAL),
                    ("They leave it be", LEAVE),
                    ("It springs all the same", SPRINGS),
                ],
            )
        ],
        apply,
        live=lambda _values: "\n".join(
            [*(escape(line) for line in spring.spotting), f"[dim]{et.AWARE}[/]"]
        ),
        inspector="Before It Springs",
        save_label="Go On",
        help_id="overcome-trap",
    )


def _action_fields(spring: Springing) -> list[DialogField]:
    obstacle = spring.obstacle

    def by_roll(values: dict[str, Any]) -> bool:
        return not values.get("fast_cast")

    found = [
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
            hint="A magus's spell is judged on its own, not against this.",
        ),
        DialogField(
            "spell_saved",
            "The spell worked",
            "check",
            False,
            hint="Roll the spell as usual. If it failed, the trap still has him.",
            show_if=lambda values: bool(values.get("fast_cast")),
        ),
        DialogField(
            "roll",
            "His roll",
            "text",
            obstacle.roll or ROLLS[0],
            hint="As the troupe agrees: Characteristic + Ability, - Encumbrance "
            "if it counts. Blank for an action that needs no roll.",
            show_if=by_roll,
        ),
        DialogField(
            "adjust",
            "Harder or easier",
            "int",
            0,
            hint="The storyguide's move for this action: 3, 6 or more either way.",
            show_if=by_roll,
        ),
    ]
    if obstacle.penetration is not None:
        found.append(
            DialogField(
                "resistance",
                "His Magic Resistance",
                "optint",
                None,
                hint="Blank for none: at least its Penetration, and he passes.",
            )
        )
    return found


def _so_far(spring: Springing) -> list[str]:
    """What has happened so far, as markup lines."""
    return [escape(line) for line in spring.spotting] + [
        escape(acted.line) for acted in spring.acted
    ]


def _action_live(spring: Springing, who: Character, values: dict[str, Any]) -> str:
    obstacle = spring.obstacle
    base = obstacle.ease
    lines = _so_far(spring)
    if _passes(obstacle, values):
        lines.append(f"{escape(who.name)} passes it untouched.")
    elif values.get("fast_cast"):
        lines.append(et.FAST_CAST)
    else:
        ease = et.action_ease(base, values.get("adjust") or 0)
        moved = f", adjusted to {ease}" if ease != base else ""
        roll = str(values.get("roll") or "").strip()
        if not roll:
            lines.append("No roll for this action.")
        elif roll_problem(roll) is None:
            _score, words = roll_score(who, roll)
            lines.append(f"{escape(words)} + stress die against {ease}.")
        lines.insert(0, f"[b]{escape(obstacle.name)}[/], Ease Factor {base}{moved}.")
    lines.append(f"Order: {escape(_order_words(spring.party))}.")
    lines.append(f"[dim]{et.PRIORITY}[/]")
    return "\n".join(lines)


def _passes(obstacle: Obstacle, values: dict[str, Any]) -> bool:
    return obstacle.penetration is not None and et.passes_untouched(
        values.get("resistance"), obstacle.penetration
    )


def _acted(spring: Springing, who: Character, values: dict[str, Any]) -> Acted:
    """What `who`'s turn came to: rolled, unless he needs no roll."""
    doing = str(values.get("action") or "").strip()
    name = f"{who.name}, {doing}," if doing else who.name
    obstacle = spring.obstacle
    if _passes(obstacle, values):
        return Acted(who, f"{name} passes untouched.", True)
    if values.get("fast_cast"):
        worked = bool(values.get("spell_saved"))
        ending = "and it works" if worked else "and it fails"
        return Acted(who, f"{name} answers with a Fast-Cast spell, {ending}.", worked)
    roll = str(values.get("roll") or "").strip()
    if not roll:
        return Acted(who, f"{name} makes no roll.", False)
    ease = et.action_ease(obstacle.ease, values.get("adjust") or 0)
    score, words = roll_score(who, roll)
    die = dice.stress_die(spring.rng, saga=spring.saga)
    total = score + die.value
    rolled = f"{words} + {'a botch' if die.botched else die.value}"
    if die.botched:
        return Acted(who, f"{name} botches ({rolled}).", False)
    clear = total >= ease
    verb = "succeeds" if clear else "fails"
    return Acted(who, f"{name} {verb} ({rolled} = {total} against {ease}).", clear)


def action_form(spring: Springing) -> Form:
    """The next character's turn: what he does and rolls; his roll is made
    when he goes on, so those after him see how it went."""
    who = spring.party[len(spring.acted)]

    def apply(values: dict[str, Any]) -> Any:
        spring.acted.append(_acted(spring, who, values))
        if len(spring.acted) < len(spring.party):
            return action_form(spring)
        return it_acts(spring)

    def problem(values: dict[str, Any]) -> str | None:
        if values.get("fast_cast") or _passes(spring.obstacle, values):
            return None
        return roll_problem(str(values.get("roll") or ""))

    return Form(
        f"{escape(who.name)} Acts: {escape(spring.obstacle.name)}",
        lambda: _action_fields(spring),
        apply,
        validate=problem,
        live=lambda values: _action_live(spring, who, values),
        inspector="The Trap Springs",
        save_label="Roll",
        help_id="overcome-trap",
    )


def _spared_key(character: Character) -> str:
    return f"spared_{character.id}"


def _caught(spring: Springing) -> list[Character]:
    return [acted.who for acted in spring.acted if not acted.clear]


def _suffering(spring: Springing, values: dict[str, Any]) -> list[str]:
    caught = _caught(spring)
    spared = {c.name for c in caught if values.get(_spared_key(c))}
    return et.suffering([c.name for c in caught], spared)


#: What a trap is left as.
SPRUNG, RESET = "sprung", "reset"


def _it_acts_fields(spring: Springing) -> list[DialogField]:
    found = [
        DialogField(
            _spared_key(c),
            f"{escape(c.name)} is helped, or out of its reach",
            "check",
            False,
        )
        for c in _caught(spring)
    ]
    found.append(DialogField("outcome", "What came of it", "text", ""))
    trap = spring.obstacle.trap
    if trap is None:
        return found
    left = [("Left sprung", SPRUNG)]
    if not trap.get("once"):
        left.append(("Reset", RESET))
    found.append(
        DialogField(
            "left",
            "The trap is",
            "select",
            RESET if trap.get("resets") else SPRUNG,
            options=left,
            hint="Most mechanical traps are reset by hand (LotN p. 44).",
        )
    )
    return found


def _it_acts_live(spring: Springing, values: dict[str, Any]) -> str:
    obstacle = spring.obstacle
    lines = _so_far(spring)
    hurt = _suffering(spring, values)
    if hurt:
        names = escape(", ".join(hurt))
        lines.append(
            f"[b]{names} suffer{'s' if len(hurt) == 1 else ''} it:[/] {escape(obstacle.harm)}."
        )
        if obstacle.text:
            lines.append(escape(obstacle.text))
    else:
        lines.append("[b]Nobody suffers it.[/]")
    lines.append(f"[dim]{et.LAST_IN_THE_ROUND}[/]")
    return "\n".join(lines)


def it_acts(spring: Springing) -> Form:
    """The last step: it acts on those who failed and weren't helped, and
    the outcome goes in the place's diary."""
    obstacle = spring.obstacle

    def apply(values: dict[str, Any]) -> Any:
        hurt = _suffering(spring, values)
        trap = obstacle.trap
        words = [acted.line for acted in spring.acted]
        words.append(
            f"{', '.join(hurt)} suffered {obstacle.name}."
            if hurt
            else f"Nobody suffered {obstacle.name}."
        )
        outcome = str(values.get("outcome") or "").strip()
        if outcome:
            words.append(outcome)
        if trap is not None:
            if values.get("left") == SPRUNG:
                trap["sprung"] = True
            else:
                trap.pop("sprung", None)
        _write(spring, " ".join(words))
        return notes(words[-2] if outcome else words[-1])

    return Form(
        f"It Acts: {escape(obstacle.name)}",
        lambda: _it_acts_fields(spring),
        apply,
        live=lambda values: _it_acts_live(spring, values),
        inspector="Who Suffers It",
        save_label="Write",
        help_id="overcome-trap",
    )


def _write(spring: Springing, line: str) -> None:
    place_events.diary(spring.place).append(
        {
            "year": spring.saga.current_year,
            "season": spring.saga.current_season,
            "text": line,
        }
    )


def _reset_step(trap: TombTrap) -> Command:
    """A trap already sprung is reset before it can spring again."""
    if trap.get("once"):
        return Refuse("Overcome It", f"{escape(trap['name'])} works only once.")

    def reset() -> Any:
        trap.pop("sprung", None)
        return notes(f"{trap['name']} is reset.")

    return Confirm(
        f"{escape(trap['name'])} has sprung and isn't reset. Reset it?",
        reset,
        yes_label="Reset",
        title="Overcome It",
    )


def overcome_trap(
    saga: Saga, place: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Overcome It on the chosen trap: who is there, whether they
    look for it first, each character's action in order, then who suffers
    it, written in the place's diary."""
    listed = traps(place)
    if index >= len(listed):
        return Refuse("Overcome It", "Choose a trap first.")
    if not saga.characters:
        return Refuse("Overcome It", "The saga has no characters to act.")
    trap = listed[index]
    if trap.get("sprung"):
        return _reset_step(trap)
    return _opening(saga, place, _trap_obstacle(trap), rng or random.Random())


def overcome_ward(
    saga: Saga, place: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Overcome It on the chosen talisman or ward: the same narrative
    rules as a trap (LotN pp. 35, 42), with no sprung state to keep."""
    listed = wards(place)
    if index >= len(listed):
        return Refuse("Overcome It", "Choose a talisman or ward first.")
    if not saga.characters:
        return Refuse("Overcome It", "The saga has no characters to act.")
    ease = ward_ease(listed[index])
    if ease is None:
        return Refuse(
            "Overcome It", f"{escape(listed[index]['name'])} stands in nobody's way."
        )
    return _opening(
        saga, place, _ward_obstacle(listed[index], ease), rng or random.Random()
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
