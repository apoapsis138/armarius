"""Logic behind enchanted devices and talismans -- no UI in here.

The item-side arithmetic of ArM5 Definitive Edition ch. 8 (Enchantments
through Investigating Enchantments): capacity from Material and Size, a
talisman's capacity from its magus's Arts, each effect's modified level and
vis, a Charged Item's charges, and the warnings shown (never blocking) when
something doesn't add up. Every worked-out figure can be overridden on the
record. Lab Totals and seasons to finish stay with the Rules Engine and
Seasonal Activities. Also the text of the device lists and details panels
on the character, laboratory and covenant sheets.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from . import experiment_text
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .markup import PROBLEM_GLYPH, escape, fit, markdown_text, problem
from .models import (
    CHARGED,
    EFFECT_EXPIRIES,
    EFFECT_FREQUENCIES,
    ENCHANT_MATERIALS,
    ENCHANT_SIZES,
    INVESTED,
    LESSER,
    PAY_HIGHEST,
    SEASONS,
    Character,
    DeviceComponent,
    EnchantedDevice,
    InstilledEffect,
    Saga,
    ShapeMaterialBonus,
)
from .rules.rounding import round_down, round_up
from .tables import Table

#: Level additions for the effect modifications (DE ch. 8, Effect
#: Modifications), as (InstilledEffect flag, label, levels).
MODIFICATIONS: tuple[tuple[str, str, int], ...] = (
    ("maintains_concentration", "Item maintains concentration", 5),
    ("restricted_use", "Restricted use", 3),
    ("environmental_trigger", "Environmental trigger", 3),
    ("fast_trigger", "Fast trigger", 5),
    ("linked_trigger", "Linked trigger", 3),
)

#: How each type is named in a list row.
TYPE_WORDS: dict[str, str] = {
    INVESTED: "Invested",
    LESSER: "Lesser",
    CHARGED: "Charged",
}

#: The details panel with nothing chosen, where devices share a sheet's panel.
PANEL_HINT = "[dim]Select an enchanted device or effect to see its details.[/]"

#: The rules the app doesn't apply, said where they matter (help text).
TALISMAN_HINT = (
    "Its magus's Technique + Form sets its capacity. Instilling into one's own "
    "talisman is at +5 Lab Total; its casting bonus and Arcane Connection "
    "aren't applied yet."
)
BONUS_HINT = (
    "Bonuses for one effect add up to at most the maker's Magic Theory (not checked)."
)
LEVEL_HINT = (
    "No Ritual-equivalent effect can be enchanted, unless it is a Ritual only "
    "because its level is over 50 (not checked)."
)


def _plural(count: int, noun: str) -> str:
    return f"{count} {noun}{'' if count == 1 else 's'}"


# ------------------------------------------------------------------- lookups


def maker(saga: Saga, device: EnchantedDevice) -> Character | None:
    """The character who made `device`, if it's one of the saga's."""
    return saga.character(device.maker_id)


def maker_label(saga: Saga, device: EnchantedDevice) -> str:
    made_by = maker(saga, device)
    if made_by is not None:
        return made_by.name
    return device.maker_name or "(unknown: found or bought)"


def holder_label(saga: Saga, kind: str | None, holder_id: str | None) -> str:
    """ "Leandro (character)" -- the holder's name and kind, or "(nobody)"."""
    record = {
        "character": saga.character,
        "laboratory": saga.laboratory,
        "covenant": saga.covenant,
    }.get(kind or "", lambda _id: None)(holder_id)
    if record is None:
        return "(nobody)"
    return f"{record.name} ({kind})"


def held_by(saga: Saga, kind: str, holder_id: str) -> list[EnchantedDevice]:
    """The devices `kind` `holder_id` holds, its talismans first, then in the
    order they were added."""
    held = [
        d
        for d in saga.enchanted_devices
        if d.holder_kind == kind and d.holder_id == holder_id
    ]
    return sorted(held, key=lambda d: not is_talisman(d))


def is_talisman(device: EnchantedDevice) -> bool:
    return device.type == INVESTED and device.talisman


def talisman_magus_id(device: EnchantedDevice) -> str | None:
    """Whose talisman `device` is: its maker, else the character holding it."""
    if device.maker_id:
        return device.maker_id
    return device.holder_id if device.holder_kind == "character" else None


def talisman_of(saga: Saga, character: Character) -> EnchantedDevice | None:
    """The character's talisman, if they have one."""
    return next(
        (
            d
            for d in saga.enchanted_devices
            if is_talisman(d) and talisman_magus_id(d) == character.id
        ),
        None,
    )


def magic_theory(character: Character) -> int | None:
    """The character's Magic Theory score, or None if they don't have it."""
    return next(
        (a.level for a in character.abilities if a.name == "Magic Theory"), None
    )


def device_of(saga: Saga, effect: InstilledEffect) -> EnchantedDevice | None:
    return next((d for d in saga.enchanted_devices if effect in d.effects), None)


# ------------------------------------------------------------------ capacity


def component_capacity(component: DeviceComponent) -> int:
    """Material base x size multiplier (DE ch. 8, Material and Size Tables)."""
    return ENCHANT_MATERIALS.get(component.material, 0) * ENCHANT_SIZES.get(
        component.size, 0
    )


def talisman_capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The magus's highest Technique + highest Form (DE ch. 8, Talisman
    Attunement), or None with no magus to take them from."""
    magus = saga.character(talisman_magus_id(device))
    if magus is None:
        return None

    def highest(arts: Sequence[str]) -> int:
        return max(
            (magus.arts[a.lower()].level for a in arts if a.lower() in magus.arts),
            default=0,
        )

    return highest(TECHNIQUES) + highest(FORMS)


def material_capacity(device: EnchantedDevice) -> int | None:
    """What the components' Material and Size give: their sum, or the highest
    one for a compound invested item paid that way (DE ch. 8, Preparation
    for Enchantment); None with no components."""
    if not device.components:
        return None
    capacities = [component_capacity(c) for c in device.components]
    if device.type == INVESTED and device.payment == PAY_HIGHEST:
        return max(capacities)
    return sum(capacities)


def computed_capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The capacity in pawns as the rules give it (None: nothing to work it
    out from, or a Charged Item, which has none)."""
    if device.type == CHARGED:
        return None
    if is_talisman(device):
        return talisman_capacity(saga, device)
    return material_capacity(device)


def capacity(saga: Saga, device: EnchantedDevice) -> int | None:
    """The capacity in pawns: the override if set, else worked out."""
    if device.capacity_override is not None:
        return device.capacity_override
    return computed_capacity(saga, device)


def capacity_text(saga: Saga, device: EnchantedDevice) -> str:
    """ "8 pawns (wood x large = 2 x 4)", or how a talisman's or an
    overridden capacity comes about."""
    value = capacity(saga, device)
    if value is None:
        return "(not worked out: add a component, or type a capacity)"
    worked = computed_capacity(saga, device)
    if device.capacity_override is not None:
        note = f"worked out: {worked}" if worked is not None else "not worked out"
        return f"{_plural(value, 'pawn')} (typed; {note})"
    if is_talisman(device):
        magus = saga.character(talisman_magus_id(device))
        whose = f"{magus.name}'s" if magus is not None else "the magus's"
        return f"{_plural(value, 'pawn')} ({escape(whose)} highest Technique + Form)"
    if len(device.components) == 1:
        c = device.components[0]
        return (
            f"{_plural(value, 'pawn')} ({c.material} x {c.size} = "
            f"{ENCHANT_MATERIALS.get(c.material, 0)} x {ENCHANT_SIZES.get(c.size, 0)})"
        )
    how = (
        "the highest component"
        if device.type == INVESTED and device.payment == PAY_HIGHEST
        else "the sum of its components"
    )
    return f"{_plural(value, 'pawn')} ({how})"


def is_opened(saga: Saga, device: EnchantedDevice) -> bool:
    total = capacity(saga, device)
    return total is not None and device.pawns_opened >= total


def opening_text(saga: Saga, device: EnchantedDevice) -> str:
    """ "Opened 4/4", or "Opening 2/8" while pawns are still to open."""
    total = capacity(saga, device)
    shown = "?" if total is None else str(total)
    word = "Opened" if is_opened(saga, device) else "Opening"
    return f"{word} {device.pawns_opened}/{shown}"


# ------------------------------------------------------------------- effects


def level_breakdown(
    device: EnchantedDevice, effect: InstilledEffect
) -> list[tuple[str, int]]:
    """What makes up the modified level (DE ch. 8, Designing the Effect):
    the effect level, the uses-per-day addition (not on a Charged Item),
    Penetration (+1 per 2 points) and each modification."""
    parts = [("level", effect.level)]
    if device.type != CHARGED:
        uses = EFFECT_FREQUENCIES.get(effect.uses_per_day, 0)
        if uses:
            parts.append((f"{uses_text(effect.uses_per_day)}", uses))
    if effect.penetration > 0:
        parts.append((f"Pen {effect.penetration}", round_down(effect.penetration / 2)))
    parts += [
        (label, levels)
        for flag, label, levels in MODIFICATIONS
        if getattr(effect, flag)
    ]
    return parts


def computed_modified_level(device: EnchantedDevice, effect: InstilledEffect) -> int:
    return sum(levels for _, levels in level_breakdown(device, effect))


def modified_level(device: EnchantedDevice, effect: InstilledEffect) -> int:
    """The modified level: the override if set, else worked out."""
    if effect.modified_level_override is not None:
        return effect.modified_level_override
    return computed_modified_level(device, effect)


def computed_vis(device: EnchantedDevice, effect: InstilledEffect) -> int:
    """Pawns of vis to instil it: modified level / 10, rounded up (DE ch. 8,
    Instilling the Effect); none for a Charged Item."""
    if device.type == CHARGED:
        return 0
    return round_up(modified_level(device, effect) / 10)


def vis_cost(device: EnchantedDevice, effect: InstilledEffect) -> int:
    if effect.vis_override is not None:
        return effect.vis_override
    return computed_vis(device, effect)


def pawns_used(device: EnchantedDevice) -> int:
    """The capacity the effects take: the vis of every effect, including
    partly instilled and unknown ones."""
    return sum(vis_cost(device, effect) for effect in device.effects)


def uses_text(uses_per_day: str) -> str:
    return "unlimited" if uses_per_day == "Unlimited" else f"{uses_per_day}/day"


def expiry_year(effect: InstilledEffect) -> int | None:
    """The year the effect expires: its first use plus the expiry period."""
    years = EFFECT_EXPIRIES.get(effect.expiry)
    if years is None or effect.first_use_year is None:
        return None
    return effect.first_use_year + years


def arts_text(effect: InstilledEffect) -> str:
    """ "CrIg" -- the effect's Technique and Form abbreviated."""
    return "".join(
        ART_ABBREVIATIONS.get(art, "") for art in (effect.technique, effect.form)
    )


def linked_effect(
    device: EnchantedDevice, effect: InstilledEffect
) -> InstilledEffect | None:
    return next(
        (e for e in device.effects if e.id == effect.linked_to and e is not effect),
        None,
    )


def effect_name(effect: InstilledEffect) -> str:
    return effect.name if effect.known else "(unknown power)"


# ------------------------------------------------------------------- charges


def max_charges(device: EnchantedDevice) -> int | None:
    """The most charges its Lab Total gives (DE ch. 8, Charged Items): the
    excess over the effect's level / 5, rounded up, at least 1 when the Lab
    Total equals the level, and 0 below it. None without a Lab Total or an
    effect."""
    if device.lab_total is None or not device.effects:
        return None
    level = modified_level(device, device.effects[0])
    if device.lab_total < level:
        return 0
    return max(1, round_up((device.lab_total - level) / 5))


def charges_made(device: EnchantedDevice) -> int | None:
    """Charges made: as set, else the maximum."""
    if device.charges_made is not None:
        return device.charges_made
    return max_charges(device)


def charges_left(device: EnchantedDevice) -> int | None:
    """Charges left: as set, else all those made."""
    if device.charges_left is not None:
        return device.charges_left
    return charges_made(device)


def use_charge(device: EnchantedDevice) -> bool:
    """Take one charge off a Charged Item; False (nothing changes) at 0 or
    with no charges known."""
    left = charges_left(device)
    if device.type != CHARGED or not left:
        return False
    device.charges_left = left - 1
    return True


# ------------------------------------------------------------------ warnings


def warnings(saga: Saga, device: EnchantedDevice) -> list[str]:
    """What doesn't add up on `device` (DE ch. 8), one line each: shown in
    its details panel and flagged on its row, never blocking."""
    lines: list[str] = []
    used = pawns_used(device)
    total = capacity(saga, device)
    made_by = maker(saga, device)
    if device.type in (INVESTED, LESSER) and made_by is not None:
        limit = magic_theory(made_by) or 0
        if len(device.components) > limit:
            lines.append(
                f"{_plural(len(device.components), 'component')}: at most the "
                f"maker's Magic Theory ({limit})."
            )
    if device.type == INVESTED and used > device.pawns_opened:
        lines.append(
            f"Its effects use {_plural(used, 'pawn')}, but only "
            f"{device.pawns_opened} {'was' if device.pawns_opened == 1 else 'were'} "
            "opened."
        )
    if device.type == LESSER and total is not None and used > total:
        lines.append(
            f"Its effect's vis ({used}) is more than its Material and Size allow "
            f"({total})."
        )
    if is_talisman(device):
        lines += _talisman_warnings(saga, device)
    if device.type == CHARGED and device.effects and device.lab_total is not None:
        level = modified_level(device, device.effects[0])
        most = max_charges(device) or 0
        if device.lab_total < level:
            lines.append(
                f"Its Lab Total ({device.lab_total}) is below its effect's level "
                f"({level}): it can't be made."
            )
        elif device.charges_made is not None and device.charges_made > most:
            lines.append(
                f"{_plural(device.charges_made, 'charge')} made, but its Lab Total "
                f"gives at most {most}."
            )
    return lines


def _talisman_warnings(saga: Saga, device: EnchantedDevice) -> list[str]:
    lines: list[str] = []
    magus_id = talisman_magus_id(device)
    others = [
        d
        for d in saga.enchanted_devices
        if d is not device and is_talisman(d) and talisman_magus_id(d) == magus_id
    ]
    if magus_id is not None and others:
        lines.append(
            f"{escape(others[0].name)} is already this magus's talisman: a magus "
            "has one at a time."
        )
    if device.maker_id is None:
        lines.append("A talisman needs its magus as its Maker.")
    elif device.holder_kind != "character" or device.holder_id != device.maker_id:
        lines.append("A talisman is held by the magus who made it.")
    per_season = Counter(
        (a.year, a.season) for a in device.attunements if a.year is not None
    )
    for (year, season), count in sorted(
        per_season.items(),
        key=lambda item: (item[0][0], _season_order(item[0][1])),
    ):
        if count > 1:
            when = f"{season} {year}".strip()
            lines.append(f"{count} attunements gained in {when}: one a season.")
    return lines


def _season_order(season: str) -> int:
    return SEASONS.index(season) if season in SEASONS else -1


# ---------------------------------------------------------------- list rows

#: The widest a device or effect name column gets.
_NAME_WIDTH = 30


def device_targets(
    saga: Saga, kind: str, holder_id: str
) -> list[tuple[EnchantedDevice, InstilledEffect | None]]:
    """What each row of a holder's device list stands for, in list order:
    a device, then each of its effects. A row's data index is its position
    here."""
    targets: list[tuple[EnchantedDevice, InstilledEffect | None]] = []
    for device in held_by(saga, kind, holder_id):
        targets.append((device, None))
        targets += [(device, effect) for effect in device.effects]
    return targets


def device_status(saga: Saga, device: EnchantedDevice) -> str:
    """The row's summary after the type: opening, charges or effects."""
    effects = _plural(len(device.effects), "effect")
    if device.type == CHARGED:
        left, made = charges_left(device), charges_made(device)
        charges = (
            f"{left}/{made} charges" if made is not None else "charges not worked out"
        )
        objects = f" x{device.objects} objects" if device.objects > 1 else ""
        return charges + objects
    if device.type == INVESTED:
        return f"{opening_text(saga, device)}  {effects}"
    return effects


def device_rows(saga: Saga, kind: str, holder_id: str) -> list[tuple[int, str]]:
    """The holder's devices, each followed by its effects indented:
    "Wand of Flames  Invested  Opened 4/4  2 effects", then
    "  Pilum of Fire  CrIg 35  6/day  Pen 10". A device with warnings ends
    in a red "!"."""
    targets = device_targets(saga, kind, holder_id)
    width = min(
        _NAME_WIDTH,
        max(
            (len(d.name) if e is None else len(effect_name(e)) + 2 for d, e in targets),
            default=0,
        ),
    )
    rows: list[tuple[int, str]] = []
    for index, (device, effect) in enumerate(targets):
        if effect is None:
            word = "Talisman" if is_talisman(device) else TYPE_WORDS[device.type]
            label = (
                f"{escape(fit(device.name, width))}  {fit(word, 8)}  "
                f"{device_status(saga, device)}"
            )
            if warnings(saga, device):
                label += f"  [$text-error]{PROBLEM_GLYPH}[/]"
        else:
            label = "  " + escape(fit(effect_name(effect), width - 2))
            if effect.known:
                label += "  " + effect_summary(device, effect)
        rows.append((index, label.rstrip()))
    return rows


def device_table(saga: Saga, kind: str, holder_id: str) -> Table:
    """The holder's devices as a table (markup), each followed by its
    effects, indented, in the same order as device_rows: a device's Type
    and charges or effects, an effect's Arts and level and the rest of
    its summary. A device with warnings ends in a red "!"."""
    rows: list[list[str]] = []
    for device, effect in device_targets(saga, kind, holder_id):
        if effect is None:
            word = "Talisman" if is_talisman(device) else TYPE_WORDS[device.type]
            state = device_status(saga, device)
            if warnings(saga, device):
                state += f"  [$text-error]{PROBLEM_GLYPH}[/]"
            rows.append([escape(device.name), word, state])
        elif effect.known:
            first, *rest = effect_summary(device, effect).split("  ")
            rows.append(["    " + escape(effect_name(effect)), first, "  ".join(rest)])
        else:
            rows.append(["    " + escape(effect_name(effect)), "", ""])
    return Table(["Device", "Type", "Charges or effects"], rows, markup=True)


def effect_summary(device: EnchantedDevice, effect: InstilledEffect) -> str:
    """ "CrIg 35  6/day  Pen 10  partly instilled (12 / 44)"."""
    parts = [f"{arts_text(effect) or '--'} {effect.level}"]
    if device.type != CHARGED:
        parts.append(uses_text(effect.uses_per_day))
    if effect.penetration:
        parts.append(f"Pen {effect.penetration}")
    if device.type == INVESTED and effect.instilling_progress is not None:
        parts.append(_partly_instilled(device, effect))
    return "  ".join(parts)


def _partly_instilled(device: EnchantedDevice, effect: InstilledEffect) -> str:
    return (
        f"partly instilled ({effect.instilling_progress} / "
        f"{modified_level(device, effect)})"
    )


def target_labels(saga: Saga, kind: str, holder_id: str) -> list[str]:
    """Each row's label, for a "which one?" picker."""
    return [label for _, label in device_rows(saga, kind, holder_id)]


# ------------------------------------------------------------ details panel


def bonus_text(bonus: ShapeMaterialBonus, *, when: bool = False) -> str:
    """ "+4 destroy wood (Axe)", with ", Spring 1221" for an attunement
    (`when`). Plain text: escape it for markup."""
    text = f"{bonus.bonus:+d} {bonus.applies_to}".rstrip()
    if bonus.shape:
        text += f" ({bonus.shape})"
    if when and (bonus.season or bonus.year is not None):
        date = " ".join(part for part in (bonus.season, str(bonus.year or "")) if part)
        text += f", {date}"
    return text


def component_text(component: DeviceComponent) -> str:
    """ "oak staff: wood, large (8 pawns)". Plain text: escape it for
    markup."""
    what = component.description or "(no description)"
    return (
        f"{what}: {component.material}, {component.size} "
        f"({_plural(component_capacity(component), 'pawn')})"
    )


def device_info_text(saga: Saga, device: EnchantedDevice) -> str:
    """The details panel for a device."""
    kind = "Talisman (Invested Device)" if is_talisman(device) else device.type
    lines = [
        f"[b]{escape(device.name)}[/] -- {kind}",
        f"[b]Holder:[/] {escape(holder_label(saga, device.holder_kind, device.holder_id))}",
        f"[b]Maker:[/] {escape(maker_label(saga, device))}",
    ]
    if device.type != CHARGED:
        if device.components:
            lines.append("[b]Components:[/]")
            lines += [f"  {escape(component_text(c))}" for c in device.components]
            if device.type == INVESTED and len(device.components) > 1:
                lines.append(f"[b]Opening paid:[/] {device.payment}")
        lines.append(f"[b]Capacity:[/] {capacity_text(saga, device)}")
        total = capacity(saga, device)
        used = pawns_used(device)
        if device.type == INVESTED:
            lines.append(
                f"[b]Pawns opened:[/] {device.pawns_opened} -- "
                f"{'Opened' if is_opened(saga, device) else 'Opening'}"
            )
            lines.append(f"[b]Pawns used:[/] {used} of {device.pawns_opened} opened")
        elif total is not None:
            lines.append(f"[b]Vis used:[/] {used} of {total}")
    else:
        lines += _charges_lines(device)
    if device.bonuses:
        lines.append("[b]Shape & Material bonuses:[/]")
        lines += [f"  {escape(bonus_text(b))}" for b in device.bonuses]
    if is_talisman(device):
        lines.append(f"[b]Attunements:[/] {len(device.attunements) or 'none'}")
        lines += [f"  {escape(bonus_text(a, when=True))}" for a in device.attunements]
    lines.append(f"[b]Effects:[/] {len(device.effects)}")
    problems = warnings(saga, device)
    if problems:
        lines += ["", *(problem(line) for line in problems)]
    if device.description:
        lines += ["", markdown_text(device.description)]
    return "\n".join(lines)


def _charges_lines(device: EnchantedDevice) -> list[str]:
    lab_total = "(not set)" if device.lab_total is None else str(device.lab_total)
    most = max_charges(device)
    made = charges_made(device)
    left = charges_left(device)
    lines = [f"[b]Lab Total:[/] {lab_total}"]
    if made is None:
        lines.append("[b]Charges:[/] not worked out (needs a Lab Total and an effect)")
    else:
        how = "the maximum" if device.charges_made is None else f"maximum {most}"
        lines.append(f"[b]Charges made:[/] {made} ({how})")
        lines.append(f"[b]Charges left:[/] {left}")
    if device.objects > 1:
        lines.append(f"[b]Objects:[/] {device.objects} (the charges are split across)")
    return lines


def effect_info_text(device: EnchantedDevice, effect: InstilledEffect) -> str:
    """The details panel for an effect: every field, its modified level with
    the breakdown, its vis and its expiry."""
    arts = " / ".join(a for a in (effect.technique, effect.form) if a) or "(none)"
    rdt = " / ".join(
        escape(part) or "-" for part in (effect.range, effect.duration, effect.target)
    )
    lines = [
        f"[b]{escape(effect.name) or '(unnamed)'}[/] -- in {escape(device.name)}",
    ]
    if not effect.known:
        lines.append(
            "[dim]Not yet found by Investigation: listed as (unknown power).[/]"
        )
    lines += [
        f"[b]Technique / Form:[/] {arts}"
        + (f" (req. {escape(effect.requisites)})" if effect.requisites else ""),
        f"[b]Range / Duration / Target:[/] {rdt}",
        f"[b]Effect level:[/] {effect.level}",
        f"[b]Modified level:[/] {_modified_level_text(device, effect)}",
    ]
    if device.type != CHARGED:
        vis = vis_cost(device, effect)
        typed = " (typed)" if effect.vis_override is not None else ""
        lines.append(
            f"[b]Vis:[/] {_plural(vis, 'pawn')}{typed} of {arts.replace(' / ', ' or ')}"
        )
        lines.append(f"[b]Uses per day:[/] {uses_text(effect.uses_per_day)}")
    lines.append(f"[b]Penetration:[/] {effect.penetration}")
    mods = [
        f"{label} (+{levels})"
        + (
            f": {escape(effect.restricted_to)}"
            if flag == "restricted_use" and effect.restricted_to
            else ""
        )
        for flag, label, levels in MODIFICATIONS
        if getattr(effect, flag)
    ]
    if mods:
        lines.append(f"[b]Modifications:[/] {', '.join(mods)}")
    if effect.linked_trigger:
        linked = linked_effect(device, effect)
        lines.append(
            f"[b]Triggered by:[/] {escape(effect_name(linked)) if linked else '(not set)'}"
        )
    if effect.trigger:
        lines.append(f"[b]Trigger:[/] {escape(effect.trigger)}")
    if device.type == INVESTED:
        lines.append(f"[b]Effect Expiry:[/] {_expiry_text(effect)}")
        lines.append(
            "[b]Instilling:[/] "
            + (
                "finished"
                if effect.instilling_progress is None
                else _partly_instilled(device, effect)
            )
        )
    if effect.description:
        lines += ["", markdown_text(effect.description)]
    lines += experiment_text.effect_lines(effect.experimental_effects)
    return "\n".join(lines)


def _modified_level_text(device: EnchantedDevice, effect: InstilledEffect) -> str:
    worked = computed_modified_level(device, effect)
    parts = level_breakdown(device, effect)
    breakdown = " + ".join(
        [str(parts[0][1]), *(f"{levels} ({label})" for label, levels in parts[1:])]
    )
    if effect.modified_level_override is not None:
        return f"{effect.modified_level_override} (typed; worked out: {worked})"
    return f"{worked}" if len(parts) == 1 else f"{worked} = {breakdown}"


def _expiry_text(effect: InstilledEffect) -> str:
    if EFFECT_EXPIRIES.get(effect.expiry) is None:
        return "none"
    year = expiry_year(effect)
    if year is None:
        return f"{effect.expiry} from first use (year not set)"
    return f"{effect.expiry} from {effect.first_use_year}: expires {year}"


def target_info_text(
    saga: Saga, target: tuple[EnchantedDevice, InstilledEffect | None] | None
) -> str:
    """The details panel for a row of a device list (None: the hint)."""
    if target is None:
        return PANEL_HINT
    device, effect = target
    if effect is None:
        return device_info_text(saga, device)
    return effect_info_text(device, effect)


def talisman_line(saga: Saga, character: Character) -> str:
    """The Hermetic Magic tab's line naming the magus's talisman."""
    device = talisman_of(saga, character)
    if device is None:
        return "[b]Talisman:[/] (none)"
    return (
        f"[b]Talisman:[/] {escape(device.name)}  {opening_text(saga, device)}  "
        f"{_plural(len(device.attunements), 'attunement')}"
    )
