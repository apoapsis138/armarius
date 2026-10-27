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
  level points until they reach it. Its vis (modified level / 10, each
  pawn of the Technique or Form, in any mix) is spent in the first season,
  and must fit in what was opened.
- A lesser enchantment: one season, Lab Total at least twice the level;
  the same vis, within the object's capacity.
- A charged item: one season, Lab Total at least the level, no vis;
  (Lab Total - level) / 5 charges, at least 1.
- Attuning a talisman: a season, an invested device the magus opened and
  whose effects he instilled himself; one talisman at a time.
- Investigating an item: Intellego Vim Lab Total + a stress die against the
  weakest power not yet found; each success reveals it and rolls again,
  the first failure ends the season.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import TYPE_CHECKING

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
    ShapeMaterialBonus,
)
from . import (
    book_seasons,
    enchantment,
    experiment,
    house_magic,
    lab,
    lab_virtues,
    library,
    tmre_divination,
    tmre_numerology,
    verditius,
)
from . import hybrid_magic as hybrid
from .breakdown import Line
from .rounding import round_up

#: Halves what added levels give an effect's Penetration (DE p. 152).
WEAK_MAGIC = "vf_weak_magic"

if TYPE_CHECKING:
    from .lab_seasons import LabWork

_CH8 = "Ars Magica Definitive Edition, Chapter 8: Laboratory, {}, {}"
SOURCE = _CH8.format("Enchantments", "pp. 252-260")
OPEN_SOURCE = _CH8.format("Preparation for Enchantment", "p. 254")
INSTIL_SOURCE = _CH8.format("Instilling the Effect", "p. 258")
LESSER_SOURCE = _CH8.format("Lesser Enchantments", "p. 253")
CHARGED_SOURCE = _CH8.format("Charged Items", "p. 253")
ATTUNE_SOURCE = _CH8.format("Talisman Attunement", "p. 259")
INVESTIGATE_SOURCE = _CH8.format("Investigating Enchantments", "p. 260")

#: Effect Expiry: an effect that lasts only 1, 7 or 70 years from its first
#: use multiplies the season's excess by 10, 5 or 2; it still needs a Lab
#: Total above its level (DE p. 257).
EXPIRY_SPEED: dict[str, int] = {"1 year": 10, "7 years": 5, "70 years": 2}

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
    held = enchantment.held_by(saga, "character", magus.id) + enchantment.held_by(
        saga, "laboratory", lab_.id
    )
    if lab_.covenant_id:
        held += enchantment.held_by(saga, "covenant", lab_.covenant_id)
    return held


def device_of(saga: Saga, plan: SeasonPlan) -> EnchantedDevice | None:
    return next((d for d in saga.enchanted_devices if d.id == plan.device_id), None)


def effect_of(device: EnchantedDevice, plan: SeasonPlan) -> InstilledEffect | None:
    return next((e for e in device.effects if e.id == plan.effect_id), None)


#: Words too common in a bonus's "applies to" to say which effect it
#: suits ("+3 to project a bolt of fire": "bolt", "fire" count).
_COMMON_WORDS = frozenset(
    {"and", "any", "for", "from", "into", "its", "of", "on", "or", "the", "to", "with"}
)


def _words(text: str) -> set[str]:
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text.casefold())
    return {w for w in cleaned.split() if len(w) > 2 and w not in _COMMON_WORDS}


def _matching(
    device: EnchantedDevice, effect: InstilledEffect
) -> list[ShapeMaterialBonus]:
    said = _words(
        f"{effect.name} {effect.description} {effect.technique} {effect.form}"
    )
    return [
        b
        for b in device.bonuses
        if b.year is None and b.bonus and _words(b.applies_to) & said
    ]


#: The seasons a talisman can gain an attunement: preparing it for
#: enchantment, or instilling an effect (DE p. 259).
ATTUNING = (OPEN, INSTIL)


def attunement_options(saga: Saga, magus: Character) -> list[tuple[str, str]]:
    """The attunements the magus's talisman could take: its Shape &
    Material bonuses it isn't yet attuned to, as (label, "<device
    id>:<index>")."""
    talisman = enchantment.talisman_of(saga, magus)
    if talisman is None:
        return []
    held = {(a.applies_to, a.shape) for a in talisman.attunements}
    return [
        (
            f"{talisman.name}: +{b.bonus} {b.applies_to}"
            + (f" ({b.shape})" if b.shape else ""),
            f"{talisman.id}:{i}",
        )
        for i, b in enumerate(talisman.bonuses)
        if b.year is None and b.bonus and (b.applies_to, b.shape) not in held
    ]


def attune(device: EnchantedDevice, plan: SeasonPlan) -> str | None:
    """The season's attunement, gained (DE p. 259): one a season, while
    opening or instilling the talisman. What it gave, for the Diary."""
    device_id, _, index = plan.attunement.partition(":")
    if (
        plan.activity not in ATTUNING
        or device_id != device.id
        or not device.talisman
        or not index.isdigit()
        or int(index) >= len(device.bonuses)
    ):
        return None
    chosen = device.bonuses[int(index)]
    if any(
        (a.applies_to, a.shape) == (chosen.applies_to, chosen.shape)
        for a in device.attunements
    ):
        return None
    device.attunements.append(replace(chosen, year=plan.year, season=plan.season))
    return f"{device.name} is attuned: +{chosen.bonus} {chosen.applies_to}."


def suggested_shape_bonus(
    magus: Character, device: EnchantedDevice, effect: InstilledEffect
) -> int:
    """The Shape & Material bonus to offer for instilling `effect`: the
    device's matching bonuses, at most the magus's Magic Theory (DE p.
    258). Only a suggestion: the troupe decides which bonuses apply."""
    total = sum(b.bonus for b in _matching(device, effect))
    return max(0, min(total, lab.shape_material_cap(magus)))


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
    name = enchantment.effect_name(effect)
    if text.type != "Lab Text" or text.text_kind != TEXT_ENCHANTMENT:
        return f"{text.name} isn't the Lab Text of an enchantment."
    if not library.can_read(saga, magus, text) and not lab_virtues.remembers(
        magus, text
    ):
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
    level = enchantment.modified_level(device, effect)
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
    material bonuses (with Verditius Runes, up to Magic Theory), the
    Verditius maker's Craft, and in an invested device, the talisman and
    shared-Arts bonuses."""
    shape = max(0, plan.shape_bonus)
    if shape:
        shape += verditius.rune_bonus(saga, magus, device)
    total = lab.lab_total(
        saga,
        magus,
        effect.technique,
        effect.form,
        lab_,
        activity="enchant_items",
        days_missed=max(0, plan.days_away),
        experimenting=plan.experimenting,
        shape_material=shape,
        similar_spell_level=lab.similar_spell_level(saga, magus, plan.similar_spell_id),
        from_lab_text=text is not None,
        others_text=text is not None and text.author_id != magus.id,
        hermetic_text=text is not None and hybrid.hermetic_source(saga, text),
    )
    extra: list[Line] = []
    craft = verditius.craft_line(saga, magus, device)
    if craft is not None:
        extra.append(craft)
    extra += verditius.mystery_lines(magus, device, effect)
    # Hermetic Architecture: the Numerologist's book bonus.
    extra += tmre_numerology.architecture_lines(saga, magus, device)
    if device.type == INVESTED:
        if device.talisman and enchantment.talisman_magus_id(device) == magus.id:
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
        if lab_virtues.has(magus, lab_virtues.DISJOINTED):
            shared = 0  # no bonus from the Arts already in it
        if shared:
            extra.append(
                Line(
                    "Effects sharing its Technique or Form",
                    amount=shared,
                    source=INSTIL_SOURCE,
                )
            )
    return lab.with_lines(total, extra)


def _open_device(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
    device: EnchantedDevice,
) -> tuple[list[str], LabWork | None]:
    """Opening a device for enchantment: its Vim vis, and a pawn of each
    elder rune's Art when they are inscribed (its first season)."""
    from .lab_seasons import LabWork

    limit = verditius.enchanting_vis_limit(magus)
    empty = lab.LabTotal(total=0, lines=[])
    room = enchantment.capacity(saga, device)
    if room is None:
        return [
            f"{device.name} has no capacity yet: give it a material and size "
            "(or a capacity) on its Inventory tab."
        ], None
    left = room - device.pawns_opened
    if left <= 0:
        return [f"{device.name} is already opened."], None
    first = not device.pawns_opened
    found = verditius.elder_rune_problems(magus, device) if first else []
    if found:
        return found, None
    runes = verditius.rune_vis(device) if first else {}
    # Verditius Magic: the maker pays his Craft score fewer pawns, at
    # least one, for the whole of what it opens.
    discount = verditius.opening_discount(saga, magus, device)
    opened = min(left, limit + discount) if device.talisman else left
    pawns = max(1, opened - discount) if discount else opened
    # Celestial Magic: a sound Laboratory Horoscope takes its bonus off too.
    starry, starry_note = tmre_divination.horoscope_opening(magus, plan)
    pawns = max(1, pawns - starry) if starry else pawns
    if pawns + sum(runes.values()) > limit:
        kind = "" if runes else "Vim "
        return [
            f"Opening {device.name} takes {pawns + sum(runes.values())} pawns of "
            f"{kind}vis; {magus.name} can handle {limit} in a season "
            f"({verditius.vis_limit_text(magus)})."
        ], None
    if limit <= 0:
        return [f"{magus.name} can't handle any vis (no Magic Theory)."], None
    work_ = LabWork(
        None,
        empty,
        0,
        finished=True,
        vis_cost={"Vim": pawns + runes.pop("Vim", 0), **runes},
        device=device,
        pawns_opened=opened,
    )
    if discount and pawns < opened:
        work_.notes.append(
            f"Verditius Magic: {pawns} pawns open it for {opened} ({verditius.SOURCE})."
        )
    if starry_note:
        work_.notes.append(starry_note)
    if device.elder_runes and first:
        work_.notes.append(
            f"Elder runes ({', '.join(device.elder_runes)}): a pawn of each Art's "
            f"vis, which the device holds besides its effects "
            f"({verditius.ELDER_RUNES_SOURCE})."
        )
    return [], work_


def _attune(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
    device: EnchantedDevice,
) -> tuple[list[str], LabWork | None]:
    """Attuning an opened device as the magus's talisman."""
    from .lab_seasons import LabWork

    empty = lab.LabTotal(total=0, lines=[])
    if not enchantment.is_opened(saga, device) and not device.pawns_opened:
        return [f"{device.name} has to be opened first."], None
    if device.maker_id and device.maker_id != magus.id:
        return [f"Only the magus who opened {device.name} can attune it."], None
    if not device.maker_id and device.maker_name:
        return [
            f"{device.name} was made by {device.maker_name}: only the magus who "
            "prepared it for enchantment can attune it."
        ], None
    others = sorted(
        {
            e.instilled_by
            for e in device.effects
            if e.instilled_by and e.instilled_by != magus.id
        }
    )
    if others:
        who = ", ".join(_name_of(saga, i) for i in others)
        return [
            f"{who} instilled effects in {device.name}: an item worked on by "
            "more than one magus can't be a talisman (an assistant's help "
            "aside)."
        ], None
    if device.talisman:
        return [f"{device.name} is already a talisman."], None
    if device.verditius_item:
        return [
            f"{device.name} is an {device.verditius_item} item: it can't also be a "
            "talisman."
        ], None
    current = enchantment.talisman_of(saga, magus)
    if current is not None:
        return [
            f"{magus.name} already has a talisman ({current.name}); the old "
            "one must be destroyed first."
        ], None
    return [], LabWork(None, empty, 0, finished=True, device=device)


def _name_of(saga: Saga, character_id: str) -> str:
    found = saga.character(character_id)
    return found.name if found is not None else "another magus"


def _investigate(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
    device: EnchantedDevice,
) -> tuple[list[str], LabWork | None]:
    """Investigating a device for its hidden powers."""
    from .lab_seasons import LabWork

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


#: The activities that work on the device as a whole, not one of its
#: effects (Strategy, as a table).
_DEVICE_WORK = {OPEN: _open_device, ATTUNE: _attune, INVESTIGATE: _investigate}


def work(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
) -> tuple[list[str], LabWork | None]:
    """The problems with a season of enchanting, or what it does. `options`
    adds the plan's Focus / Specialty / Other lines to a Lab Total."""

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
    # An attuned item or an automaton is made only by a magus with its
    # Mystery (investigating one asks nothing of him).
    if plan.activity != INVESTIGATE:
        found = verditius.item_problems(
            magus,
            device,
            effect_of(device, plan) if plan.activity in EFFECT_ACTIVITIES else None,
        )
        # A Mutantum effect or a Mercere's Portal asks its own of him.
        if plan.activity in EFFECT_ACTIVITIES:
            found = [
                *found,
                *house_magic.effect_problems(
                    magus,
                    effect_of(device, plan),
                    invested=device.type == INVESTED,
                ),
            ]
        if found:
            return found, None
    special = _DEVICE_WORK.get(plan.activity)
    if special is not None:
        return special(saga, magus, plan, lab_, options, device)
    return _effect_work(saga, magus, plan, lab_, options, device)


def _instilled_by(
    magus: Character, effect: InstilledEffect | None
) -> InstilledEffect | None:
    """The effect `magus` is instilling, marked for his Weak Magic, which
    buys its Penetration a level a point (DE p. 152)."""
    if effect is not None:
        effect.weak_penetration = lab_virtues.has(magus, WEAK_MAGIC)
    return effect


def _effect_work(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    lab_: Laboratory,
    options: lab.LabOptions,
    device: EnchantedDevice,
) -> tuple[list[str], LabWork | None]:
    """Instilling, a lesser enchantment or a charged item: one effect."""
    from .lab_seasons import LabWork

    limit = verditius.enchanting_vis_limit(magus)
    effect = _instilled_by(magus, effect_of(device, plan))
    if effect is None:
        return ["Choose the effect (add it to the device on its Inventory tab)."], None
    if not effect.technique or not effect.form:
        return [f"Give {enchantment.effect_name(effect)} its Technique and Form."], None
    level = enchantment.modified_level(device, effect)
    if level <= 0:
        return [f"Give {enchantment.effect_name(effect)} its level."], None
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
    total = house_magic.with_portal_note(
        effect, options(magus, plan, effect.technique, effect.form, total)
    )
    lab_total = int(total.total)
    name = enchantment.effect_name(effect)
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

    pawns = enchantment.vis_cost(device, effect)
    arts = (effect.technique, effect.form)
    art = plan.vis_art if plan.vis_art in arts else ""
    split = enchantment.split_vis(arts, art, plan.other_vis, pawns) if art else {}
    if plan.activity == LESSER_WORK:
        why = ""
        if text is None and lab_total < 2 * level:
            why = (
                f"Lab Total {lab_total}: a lesser enchantment of level {level} "
                f"needs {2 * level} (twice the level) to be made in one season"
            )
            if not plan.experimenting:
                return [f"{why}."], None
        room = enchantment.capacity(saga, device)
        if room is not None and pawns > room:
            return [
                f"{name} takes {pawns} pawns of vis; {device.name} holds {room}."
            ], None
        found = _vis_problem(saga, magus, plan, arts, split, pawns, limit)
        if found:
            return [found], None
        return [], LabWork(
            None,
            total,
            level,
            points_gained=0 if why else level,
            finished=not why,
            vis_cost=split,
            device=device,
            effect=effect,
            too_low=experiment.too_low(why) if why else "",
        )

    # Instilling in an invested device.
    if effect.instilling_progress is None:
        return [f"{name} is already instilled."], None
    if device.talisman and enchantment.talisman_magus_id(device) not in (
        None,
        magus.id,
    ):
        return [f"No one else can instil effects in {device.name}, a talisman."], None
    if not device.pawns_opened:
        return [f"{device.name} has to be opened first."], None
    if enchantment.pawns_used(device, effect) > device.pawns_opened:
        return [
            f"{device.name}'s effects take {enchantment.pawns_used(device, effect)} pawns; only "
            f"{device.pawns_opened} were opened."
        ], None
    why = ""
    if text is None and lab_total <= level:
        why = (
            f"Lab Total {lab_total} isn't above {name}'s level {level}: it "
            "can't be instilled yet"
        )
        if not plan.experimenting:
            return [f"{why}."], None
    before = effect.instilling_progress
    cost: dict[str, int] = {}
    if before == 0:
        found = _vis_problem(saga, magus, plan, arts, split, pawns, limit)
        if found:
            return [found], None
        cost = split
    gained = (
        max(0, level - before)
        if text is not None
        else 0
        if why
        else lab.points_per_season(lab_total, level)
        * EXPIRY_SPEED.get(effect.expiry, 1)
    )
    return [], LabWork(
        None,
        total,
        level,
        points_before=before,
        points_gained=gained,
        finished=not why and before + gained >= level,
        vis_cost=cost,
        device=device,
        effect=effect,
        too_low=experiment.too_low(why) if why else "",
    )


def _vis_problem(
    saga: Saga,
    magus: Character,
    plan: SeasonPlan,
    arts: tuple[str, str],
    split: dict[str, int],
    pawns: int,
    limit: int,
) -> str:
    from .lab_seasons import vis_pool, whose_vis

    if pawns and not split:
        return f"Choose the vis to pay with: {arts[0]} or {arts[1]}."
    if pawns > limit:
        return (
            f"It takes {pawns} pawns of vis; {magus.name} can handle {limit} in "
            f"a season ({verditius.vis_limit_text(magus)})."
        )
    return enchantment.vis_shortfall(
        split, vis_pool(saga, magus, plan), whose_vis(magus, plan)
    )


def hidden_powers(device: EnchantedDevice) -> list[tuple[int, str]]:
    """The powers an investigation can still find, weakest first: (level,
    effect id)."""
    found: list[tuple[int, str]] = [
        (enchantment.modified_level(device, e), e.id)
        for e in device.effects
        if not e.known
    ]
    return sorted(found)


def investigate(
    work_: LabWork, plan: SeasonPlan, rng: random.Random, saga: Saga | None = None
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
