"""Enchanting as lab work: the seasons that make the laboratory's
enchanted devices. Each works on a device already recorded on an
Inventory tab (its components, effects and levels are entered there).

- Opening an invested device: a season and its capacity in pawns of Vim vis
  (at most twice Magic Theory a season); a talisman may be opened a few
  pawns at a time.
- Instilling an effect in an opened device: the effect's Technique + Form
  Lab Total (+ shape and material bonuses up to Magic Theory, +5 in one's
  own talisman, +1 for each effect already in it sharing its Technique or
  Form) must be above its modified level; each season adds Lab Total -
  level points until they reach it. Its vis (modified level / 10, of the
  Technique or Form) is spent in the first season, and must fit in what
  was opened.
- A lesser enchantment: one season, Lab Total at least twice the level;
  the same vis, within the object's capacity.
- A charged item: one season, Lab Total at least the level, no vis;
  (Lab Total - level) / 5 charges, at least 1.
- Attuning a talisman: a season, an invested device the magus opened; one
  talisman at a time.
- Investigating an item: Intellego Vim Lab Total + a stress die against the
  weakest power not yet found; each success reveals it and rolls again,
  the first failure ends the season.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from .. import books
from .. import enchanted_devices as ed
from ..models import (
    CHARGED,
    INVESTED,
    LESSER,
    TEXT_ENCHANTMENT,
    Book,
    Character,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
)
from . import book_seasons, lab
from .breakdown import Line
from .rounding import round_up

if TYPE_CHECKING:
    from .lab_seasons import LabWork

_CH8 = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, {} "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#{})"
)
SOURCE = _CH8.format("Enchantments", "Enchantments")
OPEN_SOURCE = _CH8.format("Preparation for Enchantment", "Preparation_for_Enchantment")
INSTIL_SOURCE = _CH8.format("Instilling the Effect", "Instilling_the_Effect")
LESSER_SOURCE = _CH8.format("Lesser Enchantments", "Lesser_Enchantments")
CHARGED_SOURCE = _CH8.format("Charged Items", "Charged_Items")
ATTUNE_SOURCE = _CH8.format("Talisman Attunement", "Talisman_Attunement")
INVESTIGATE_SOURCE = _CH8.format(
    "Investigating Enchantments", "Investigating_Enchantments"
)

OPEN = "open_item"
INSTIL = "instil_effect"
LESSER_WORK = "lesser_enchantment"
CHARGED_WORK = "charged_item"
ATTUNE = "attune_talisman"
INVESTIGATE = "investigate_item"
ACTIVITIES: tuple[str, ...] = (
    OPEN,
    INSTIL,
    LESSER_WORK,
    CHARGED_WORK,
    ATTUNE,
    INVESTIGATE,
)
#: The device type each activity works on (None: any).
DEVICE_TYPE: dict[str, str | None] = {
    OPEN: INVESTED,
    INSTIL: INVESTED,
    LESSER_WORK: LESSER,
    CHARGED_WORK: CHARGED,
    ATTUNE: INVESTED,
    INVESTIGATE: None,
}
#: Activities about one of the device's effects.
EFFECT_ACTIVITIES: tuple[str, ...] = (INSTIL, LESSER_WORK, CHARGED_WORK)
TALISMAN_BONUS = 5
#: "Is a talisman" counts as a power of this level when investigated.
TALISMAN_POWER = 20


def devices_for(
    saga: Saga, magus: Character, lab_: Laboratory
) -> list[EnchantedDevice]:
    """The devices a magus can work on in his laboratory: his own and the
    laboratory's (and the covenant's, for investigating)."""
    held = ed.held_by(saga, "character", magus.id) + ed.held_by(
        saga, "laboratory", lab_.id
    )
    if lab_.covenant_id:
        held += ed.held_by(saga, "covenant", lab_.covenant_id)
    return held


def device_of(saga: Saga, plan: SeasonPlan) -> EnchantedDevice | None:
    return next((d for d in saga.enchanted_devices if d.id == plan.device_id), None)


def effect_of(device: EnchantedDevice, plan: SeasonPlan) -> InstilledEffect | None:
    return next((e for e in device.effects if e.id == plan.effect_id), None)


def text_device_type(device: EnchantedDevice) -> str:
    """How a Lab Text names the kind of device an effect went into."""
    return "Talisman" if device.talisman else device.type


def lab_text_of(saga: Saga, plan: SeasonPlan) -> Book | None:
    """The Lab Text an enchanting plan works from, if any."""
    if not plan.book_id:
        return None
    return next((b for b in saga.books if b.id == plan.book_id), None)


def text_problem(
    saga: Saga,
    magus: Character,
    device: EnchantedDevice,
    effect: InstilledEffect,
    text: Book,
) -> str | None:
    """Why `text` can't be worked from to instil `effect` in `device`, if
    it can't: a Lab Text reproduces its effect exactly -- the same Arts and
    level, in the same kind of device (lesser and invested texts aren't
    interchangeable; a talisman's is no use to anyone else)."""
    name = ed.effect_name(effect)
    if text.type != "Lab Text" or text.text_kind != TEXT_ENCHANTMENT:
        return f"{text.name} isn't the Lab Text of an enchantment."
    if not books.can_read(saga, magus, text):
        return f"{magus.name} can't get at {text.name}."
    if not book_seasons.can_use_lab_text(magus, text):
        return (
            f"{text.name} is {book_seasons.author_name(saga, text)}'s raw text: "
            "decode it first (or have it rewritten for general use)."
        )
    if (text.technique, text.form) != (effect.technique, effect.form):
        return (
            f"{text.name} is {text.technique} {text.form}; {name} is "
            f"{effect.technique} {effect.form}."
        )
    level = ed.modified_level(device, effect)
    if (text.level or 0) != level:
        return f"{text.name} is level {text.level or 0}; {name} is level {level}."
    kind = text_device_type(device)
    if text.device_type and text.device_type != kind:
        return f"{text.name} is for a {text.device_type}; {device.name} is a {kind}."
    if text.device_type == "Talisman" and text.author_id != magus.id:
        return f"{text.name} is of a talisman's effect: no use to anyone else."
    return None


def effect_texts(
    saga: Saga, magus: Character, device: EnchantedDevice, effect: InstilledEffect
) -> list[Book]:
    """The Lab Texts `magus` could instil `effect` in `device` from."""
    return [
        b
        for b in saga.books
        if b.type == "Lab Text"
        and b.text_kind == TEXT_ENCHANTMENT
        and text_problem(saga, magus, device, effect, b) is None
    ]


def _effect_total(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    device: EnchantedDevice,
    effect: InstilledEffect,
    text: Book | None = None,
) -> lab.LabTotal:
    """The Lab Total for instilling `effect`: its Technique + Form with the
    Items Specialization (and Texts, working from a Lab Text), shape and
    material bonuses, and in an invested device, the talisman and
    shared-Arts bonuses."""
    total = lab.lab_total(
        saga,
        magus,
        effect.technique,
        effect.form,
        lab_,
        activity="enchant_items",
        days_missed=max(0, plan.days_away),
        experimenting=plan.experimenting,
        shape_material=max(0, plan.shape_bonus),
        from_lab_text=text is not None,
        others_text=text is not None and text.author_id != magus.id,
    )
    extra: list[Line] = []
    if device.type == INVESTED:
        if device.talisman and ed.talisman_magus_id(device) == magus.id:
            extra.append(
                Line("Own talisman", amount=TALISMAN_BONUS, source=ATTUNE_SOURCE)
            )
        shared = sum(
            1
            for other in device.effects
            if other is not effect
            and other.instilling_progress is None
            and (other.technique == effect.technique or other.form == effect.form)
        )
        if shared:
            extra.append(
                Line(
                    "Effects sharing its Technique or Form",
                    amount=shared,
                    source=INSTIL_SOURCE,
                )
            )
    if not extra:
        return total
    return replace(
        total,
        total=total.total + sum(line.amount or 0 for line in extra),
        lines=[*total.lines, *extra],
    )


def work(  # noqa: PLR0915
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options,
) -> tuple[list[str], LabWork | None]:
    """The problems with a season of enchanting, or what it does. `options`
    adds the plan's Focus / Specialty / Other lines to a Lab Total."""
    from .lab_seasons import LabWork

    device = device_of(saga, plan)
    if device is None:
        return [
            "Choose the enchanted device (they're kept on the Inventory tabs)."
        ], None
    wanted = DEVICE_TYPE[plan.activity]
    if wanted is not None and device.type != wanted:
        return [f"{device.name} isn't a {wanted}."], None
    if lab.distraction_penalty(max(0, plan.days_away)) is None:
        return [
            f"{plan.days_away} days away from the laboratory: no lab work is "
            "possible this season (more than 20)."
        ], None
    limit = lab.vis_limit(magus)
    empty = lab.LabTotal(total=0, lines=[])

    if plan.activity == OPEN:
        room = ed.capacity(saga, device)
        if room is None:
            return [
                f"{device.name} has no capacity yet: give it a material and size "
                "(or a capacity) on its Inventory tab."
            ], None
        left = room - device.pawns_opened
        if left <= 0:
            return [f"{device.name} is already opened."], None
        pawns = min(left, limit) if device.talisman else left
        if pawns > limit:
            return [
                f"Opening {device.name} takes {pawns} pawns of Vim vis; "
                f"{magus.name} can handle {limit} in a season (twice Magic Theory)."
            ], None
        if pawns <= 0:
            return [f"{magus.name} can't handle any vis (no Magic Theory)."], None
        return [], LabWork(
            None, empty, 0, finished=True, vis_cost={"Vim": pawns}, device=device
        )

    if plan.activity == ATTUNE:
        if not ed.is_opened(saga, device) and not device.pawns_opened:
            return [f"{device.name} has to be opened first."], None
        if device.maker_id and device.maker_id != magus.id:
            return [f"Only the magus who opened {device.name} can attune it."], None
        if device.talisman:
            return [f"{device.name} is already a talisman."], None
        current = ed.talisman_of(saga, magus)
        if current is not None:
            return [
                f"{magus.name} already has a talisman ({current.name}); the old "
                "one must be destroyed first."
            ], None
        return [], LabWork(None, empty, 0, finished=True, device=device)

    if plan.activity == INVESTIGATE:
        total = lab.lab_total(
            saga,
            magus,
            "Intellego",
            "Vim",
            lab_,
            activity="enchant_items",
            days_missed=max(0, plan.days_away),
            experimenting=plan.experimenting,
        )
        total = options(magus, plan, "Intellego", "Vim", total)
        hidden = hidden_powers(device)
        if not hidden:
            return [f"Every power of {device.name} is already known."], None
        return [], LabWork(None, total, hidden[0][0], finished=True, device=device)

    # Instilling, a lesser enchantment or a charged item: one effect.
    effect = effect_of(device, plan)
    if effect is None:
        return ["Choose the effect (add it to the device on its Inventory tab)."], None
    if not effect.technique or not effect.form:
        return [f"Give {ed.effect_name(effect)} its Technique and Form."], None
    level = ed.modified_level(device, effect)
    if level <= 0:
        return [f"Give {ed.effect_name(effect)} its level."], None
    # Working from a Lab Text: one season if the Lab Total is at
    # least the level; no experimenting.
    text = lab_text_of(saga, plan)
    if text is not None:
        found = text_problem(saga, magus, device, effect, text)
        if found:
            return [found], None
        if plan.experimenting:
            return ["There's no experimenting while working from a Lab Text."], None
    total = _effect_total(saga, magus, plan, lab_, device, effect, text)
    if text is not None and text.shape_material:
        # The rule: the same shape and material. Both are free text, so the
        # magus is told what the text is exact to rather than refused.
        total = replace(
            total,
            notes=[
                *(total.notes or []),
                f"{text.name} reproduces the effect in the same shape and "
                f"material only: {text.shape_material}.",
            ],
        )
    total = options(magus, plan, effect.technique, effect.form, total)
    lab_total = int(total.total)
    name = ed.effect_name(effect)
    if text is not None and lab_total < level:
        return [
            f"Lab Total {lab_total} is below {name}'s level {level}: the Lab "
            "Text can't be used yet."
        ], None

    if plan.activity == CHARGED_WORK:
        if lab_total < level:
            return [
                f"Lab Total {lab_total} is below {name}'s level {level}: no "
                "charges can be made."
            ], None
        return [], LabWork(
            None,
            total,
            level,
            finished=True,
            device=device,
            effect=effect,
            # From a Lab Text: a charge per 5 points of the whole Lab Total.
            charges=max(
                1,
                round_up((lab_total if text is not None else lab_total - level) / 5),
            ),
        )

    pawns = ed.vis_cost(device, effect)
    arts = (effect.technique, effect.form)
    art = plan.vis_art if plan.vis_art in arts else ""
    if plan.activity == LESSER_WORK:
        if text is None and lab_total < 2 * level:
            return [
                f"Lab Total {lab_total}: a lesser enchantment of level {level} "
                f"needs {2 * level} (twice the level) to be made in one season."
            ], None
        room = ed.capacity(saga, device)
        if room is not None and pawns > room:
            return [
                f"{name} takes {pawns} pawns of vis; {device.name} holds {room}."
            ], None
        found = _vis_problem(saga, magus, plan, art, arts, pawns, limit)
        if found:
            return [found], None
        return [], LabWork(
            None,
            total,
            level,
            points_gained=level,
            finished=True,
            vis_cost={art: pawns},
            device=device,
            effect=effect,
        )

    # Instilling in an invested device.
    if effect.instilling_progress is None:
        return [f"{name} is already instilled."], None
    if device.talisman and ed.talisman_magus_id(device) not in (None, magus.id):
        return [f"No one else can instil effects in {device.name}, a talisman."], None
    if not device.pawns_opened:
        return [f"{device.name} has to be opened first."], None
    if ed.pawns_used(device) > device.pawns_opened:
        return [
            f"{device.name}'s effects take {ed.pawns_used(device)} pawns; only "
            f"{device.pawns_opened} were opened."
        ], None
    if text is None and lab_total <= level:
        return [
            f"Lab Total {lab_total} isn't above {name}'s level {level}: it "
            "can't be instilled yet."
        ], None
    before = effect.instilling_progress
    cost: dict[str, int] = {}
    if before == 0:
        found = _vis_problem(saga, magus, plan, art, arts, pawns, limit)
        if found:
            return [found], None
        cost = {art: pawns}
    gained = (
        max(0, level - before)
        if text is not None
        else lab.points_per_season(lab_total, level)
    )
    return [], LabWork(
        None,
        total,
        level,
        points_before=before,
        points_gained=gained,
        finished=before + gained >= level,
        vis_cost=cost,
        device=device,
        effect=effect,
    )


def _vis_problem(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    art: str,
    arts: tuple[str, str],
    pawns: int,
    limit: int,
) -> str:
    from .lab_seasons import vis_pool, whose_vis

    if not art:
        return f"Choose the vis to pay with: {arts[0]} or {arts[1]}."
    if pawns > limit:
        return (
            f"It takes {pawns} pawns of vis; {magus.name} can handle {limit} in "
            "a season (twice Magic Theory)."
        )
    held = vis_pool(saga, magus, plan).get(art.lower(), 0)
    if held < pawns:
        return (
            f"It takes {pawns} pawns of {art} vis; {whose_vis(magus, plan)} raw "
            f"vis has {held}."
        )
    return ""


def hidden_powers(device: EnchantedDevice) -> list[tuple[int, str]]:
    """The powers an investigation can still find, weakest first: (level,
    effect id)."""
    found: list[tuple[int, str]] = [
        (ed.modified_level(device, e), e.id) for e in device.effects if not e.known
    ]
    return sorted(found)


def investigate(
    work_: LabWork, plan: SeasonPlan, rng, saga: Saga | None = None
) -> list[str]:
    """Roll the investigation: Lab Total + a stress die against each hidden
    power, weakest first, until one fails. Records the found effect ids on
    `work_` and returns notes. A die typed on the plan is used for one roll."""
    from . import dice

    device = work_.device
    assert device is not None
    lab_total = int(work_.lab_total.total)
    notes: list[str] = []
    for level, effect_id in hidden_powers(device):
        if plan.die is not None:
            die, botched = plan.die, plan.die == 0
            notes.append(f"Die {plan.die} (as rolled at the table).")
        else:
            rolled = dice.stress_die(rng, 1, saga=saga)
            die, botched = rolled.value, rolled.botched
        if botched:
            notes.append(
                "Botch: a power is misread, or the item goes off (storyguide); "
                "the season ends."
            )
            break
        total = lab_total + die
        if total < level:
            notes.append(
                f"{lab_total} + {die} = {total} against level {level}: failed."
            )
            break
        work_.revealed.append(effect_id)
        effect = next(e for e in device.effects if e.id == effect_id)
        notes.append(
            f"{lab_total} + {die} = {total} against level {level}: found "
            f"{effect.name or 'a power'}."
        )
        if plan.die is not None:
            break
    return notes
