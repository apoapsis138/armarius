"""Mystery Initiation's seasons (the Definitive Edition and The Mysteries:
Revised Edition): undergoing an Initiation, acting as Mystagogue and a
Quest season toward a Script's bonus.

An Initiation is the Mystagogue's Presence + Lore + the Script's bonus
against 15 / 18 (Minor) or 21 / 30 (Major), less a past Ordeal's
reduction; a hedge tradition's Script brings its own Ease Factor.

A Hermetic Mystery's Script may be written out as its components (The
Mysteries Revised Edition pp. 15-16): then its bonus is theirs, with the
Ordeal's own (+3 / +6 / +9 by its size, or the House Verditius first Inner
Mystery's Hubris, a Minor Ordeal), and the typed Script bonus is added on
top. A catalog Script's printed components are noted with it.
"""

from __future__ import annotations

import random

from ... import catalog
from ...models import (
    Character,
    InitiationScript,
    Saga,
    SeasonPlan,
    TraditionDef,
    VirtueFlawInstance,
)
from ...models.mystery_cults import LATER_LORE, is_saga_cult
from .. import activity_groups as groups
from .. import bjornaer, dice, enchantment, merinita, mysteries, verditius
from .. import tradition_seasons as ts
from ..apprentice_seasons import gifted
from ..breakdown import Line
from ..creation_finish import touched_by_the_fay
from ..rounding import round_up
from ..scores import ability_level
from .base import (
    CH,
    SimpleActivity,
    SupplementWork,
    experience_only,
    register,
    source,
)

DE_INITIATION = source(
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Mystery Initiation, "
    "pp. 387-389",
    "DE",
)
MYSTERIES = source(
    "The Mysteries: Revised Edition " + CH.format("The_Mysteries:_Revised_Edition"),
    "TMRE",
)
INITIATION_TARGET = mysteries.TARGET_LEVELS
ORDEAL_REDUCTION = mysteries.ORDEAL_REDUCTIONS
#: The kinds of Ordeal: the Initiate gains a Flaw, loses a Virtue, or has a
#: Minor Flaw raised to a related Major one.
GAIN_FLAW, LOSE_VIRTUE, RAISE_FLAW = "gain", "lose", "raise"
ORDEAL_KINDS = {
    GAIN_FLAW: "Gains a Flaw",
    LOSE_VIRTUE: "Loses a Virtue",
    RAISE_FLAW: "Raises a Minor Flaw to Major",
}


def initiation_target(saga: Saga, character: Character, plan: SeasonPlan) -> int:
    """The Initiation's Target: the Hermetic Target Level by the Virtue's
    tier and whether the Mystagogue knows it, or a hedge Script's own Ease
    Factor (+ 3 / + 9 when he doesn't know the power), less a past
    Ordeal's reduction."""
    virtue = catalog.load_virtue_flaw_catalog_by_id().get(plan.effect_id or "")
    mystagogue = saga.character(plan.teacher_id) or character
    knows = knows_power(mystagogue, plan)
    # House Bjornaer's Great Beast knows the Inner Mystery, and a
    # Refinement's Ease Factor is its own (HoH:MC pp. 30, 33).
    knows = knows or bjornaer.knows_by_rule(plan.hedge_script)
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is not None:
        _, script = hedge
        tier = (
            virtue.tier
            if virtue is not None and virtue.tier in mysteries.UNKNOWN_POWER
            else mysteries.script_tier(script.ease_factor, script.gains)
        )
        ease = script.ease_factor
        if mystagogue is character and script.self_ease_factor:
            ease = script.self_ease_factor
        return int(
            mysteries.hedge_target(ease, tier, knows, ordeal_reduction(character)).total
        )
    tier = virtue.tier if virtue is not None else "Minor"
    target = INITIATION_TARGET[(tier if tier == "Major" else "Minor", knows)]
    return max(mysteries.MINIMUM_TARGET, target - ordeal_reduction(character))


def knows_power(mystagogue: Character, plan: SeasonPlan) -> bool:
    """Whether the Mystagogue knows the power initiated: he holds the
    Virtue, with what it names, or the plan says he knows it (a hedge
    power that is an Ability, say)."""
    return plan.knows_power or (
        bool(plan.effect_id) and _initiated(plan) in mystagogue.virtues_flaws
    )


def ordeal_reduction(character: Character) -> int:
    """How much the character's past Ordeals lower their next Initiation's
    Target: only the one that lowers it most counts, and none for an
    unGifted Initiate."""
    if not mysteries.ordeals_count(character):
        return 0
    return max(
        (
            ORDEAL_REDUCTION[o.size][o.initiations_since]
            for o in character.ordeals
            if o.size in ORDEAL_REDUCTION and o.initiations_since < 3
        ),
        default=0,
    )


def _initiated(plan: SeasonPlan) -> VirtueFlawInstance:
    """The Virtue an Initiation grants, with what it names."""
    return VirtueFlawInstance(plan.effect_id or "", dict(plan.effect_params))


def ordeal_kind(plan: SeasonPlan) -> str:
    """The plan's kind of Ordeal ("" for none); an older plan's Flaw is
    gained."""
    return plan.ordeal_kind or (GAIN_FLAW if plan.device_id else "")


def _ordeal_gained(plan: SeasonPlan) -> VirtueFlawInstance | None:
    if ordeal_kind(plan) not in (GAIN_FLAW, RAISE_FLAW) or not plan.device_id:
        return None
    return VirtueFlawInstance(plan.device_id, dict(plan.ordeal_params))


def _ordeal_lost(plan: SeasonPlan) -> VirtueFlawInstance | None:
    if ordeal_kind(plan) not in (LOSE_VIRTUE, RAISE_FLAW) or not plan.ordeal_lost_id:
        return None
    return VirtueFlawInstance(plan.ordeal_lost_id, dict(plan.ordeal_lost_params))


def ordeal_size(plan: SeasonPlan) -> str:
    """The Ordeal's size, from what it costs: a Minor Flaw gained or Minor
    Virtue lost is Minor, a Major one Major, a Flaw raised Medium ("" with
    no Ordeal)."""
    kind = ordeal_kind(plan)
    if kind == RAISE_FLAW:
        return "Medium"
    if not plan.ordeal_kind and plan.device_id:
        return plan.research_kind or "Minor"
    costs = _ordeal_gained(plan) or _ordeal_lost(plan)
    entry = catalog.load_virtue_flaw_catalog_by_id().get(costs.vf_id) if costs else None
    return entry.tier if entry is not None and entry.tier in ORDEAL_REDUCTION else ""


#: Each House's Lore by all its names: the Ability catalog's ("Mystery Cult
#: Lore: Bjornaer"), the books' ("House Bjornaer Lore", HoH:MC pp. 28, 30;
#: Errata p. 54; "House Merinita Lore", p. 88) and older ones, so a
#: character holding it under any of them scores it.
_HOUSE_LORE_NAMES = (bjornaer.LORE_NAMES, merinita.LORE_NAMES, verditius.LORE_NAMES)


def _lore_names(lore: str) -> tuple[str, ...]:
    return next((names for names in _HOUSE_LORE_NAMES if lore in names), (lore,))


def _hermetic_lore(character: Character, lore: str) -> int:
    """The character's score in a Hermetic Mystery's Lore, a House's under
    the best of its names."""
    return max(ability_level(character, name) for name in _lore_names(lore))


def _hedge_lore(character: Character, lore: str) -> int:
    """The character's score in a tradition's Lore (or a required
    Ability), a House's under the best of its names."""
    return max(ts.lore_score(character, name) for name in _lore_names(lore))


# -- checks --------------------------------------------------------------------


def _house_lore(character: Character, lore: str) -> bool:
    """Whether `lore` is the Lore of the House `character` belongs to
    ("House Bjornaer Lore" for house_bjornaer)."""
    house = (character.hermetic.house or "").removeprefix("house_")
    return bool(house) and house.replace("_", " ") in lore.lower()


def _initiation_problem(saga: Saga, character: Character, plan: SeasonPlan) -> str:
    """What stops an Initiation plan ("" if nothing). No Mystagogue chosen
    is a self-initiation. The Initiate needs the Lore at 1 unless it is the
    Lore of their own House; the Mystagogue must know it."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    hedge = ts.hedge_script(plan.hedge_script)
    if plan.hedge_script and hedge is None:
        return "That hedge Script is no longer in the catalog: choose another."
    virtue = by_id.get(plan.effect_id or "")
    if virtue is None and hedge is None:
        return "Choose the Mystery Virtue initiated."
    if virtue is not None and virtue.side != "Virtue":
        return f"{virtue.name} is not a Virtue: choose the Virtue initiated."
    mystagogue = saga.character(plan.teacher_id) or character
    if hedge is not None:
        found = _hedge_problem(character, mystagogue, *hedge)
        if found:
            return found
    else:
        lore = plan.title.strip()
        if not lore:
            return "Name the Mystagogue's (Mystery Cult) Lore."
        if _hermetic_lore(mystagogue, lore) < 1:
            return f"{mystagogue.name} doesn't know {lore}."
        if _hermetic_lore(character, lore) < 1 and not _house_lore(character, lore):
            return f"{character.name} needs {lore} 1 to be Initiated."
    return (
        _script_problem(plan)
        # House Bjornaer's own rules (Houses of Hermes: Mystery Cults pp.
        # 17-33): who may be Initiated, and who may lead each Script.
        or bjornaer.mystery_problem(
            saga,
            character,
            plan.effect_id or "",
            plan.hedge_script,
            ever_bound=plan.familiar_ever_bound,
        )
        or bjornaer.mystagogue_problem(
            character, mystagogue, plan.hedge_script, ordeal_reduction(character)
        )
        or (
            mysteries.parts_problem(plan.script_components, components_for(character))
            if hedge is None
            else ""
        )
        or (_mystery_problem(saga, character, virtue.id) if virtue else "")
        or _ordeal_problem(character, plan)
        or merinita.condition_problem(
            character,
            plan.effect_id or "",
            plan.ordeal_condition,
            _ordeal_gained(plan),
        )
        or _house_ordeal_problem(character, plan)
        or mysteries.ungifted_problem(
            character,
            mystagogue,
            knows_power(mystagogue, plan),
            bool(ordeal_kind(plan)),
        )
    )


def _hedge_problem(
    initiate: Character,
    mystagogue: Character,
    tradition: TraditionDef,
    script: InitiationScript,
) -> str:
    """What stops an Initiation by a hedge tradition's Script ("" if
    nothing): the Mystagogue must belong to the tradition and know its
    Lore, a tradition without self-initiation can't Initiate itself, a
    Script for the Gifted needs a Gifted Initiate, and one that requires
    scores (the elementalists' minimums, HMRE pp. 30-31; the learned
    magicians' master's test, pp. 88-89) fails an Initiate without them."""
    rule = tradition.initiation
    assert rule is not None  # ts.hedge_script finds Scripts only in a rule
    if not ts.belongs(mystagogue, tradition.id):
        return (
            f"{mystagogue.name} isn't one of the {tradition.name}: the "
            "Mystagogue must be."
        )
    if mystagogue is initiate and not rule.self_initiation:
        return f"The {tradition.name} can't Initiate themselves: choose a Mystagogue."
    if rule.lore and _hedge_lore(mystagogue, rule.lore) < 1:
        return f"{mystagogue.name} doesn't know {rule.lore}."
    if script.who == "gifted" and not gifted(initiate):
        return f"{script.name} is for the Gifted, and {initiate.name} is unGifted."
    short = [
        f"{ability} {least}"
        for ability, least in script.requires
        if _hedge_lore(initiate, ability) < least
    ]
    if short:
        return (
            f"{script.name} always fails for an Initiate without "
            f"{', '.join(short)}: {initiate.name} is short of it."
        )
    return ""


def _script_problem(plan: SeasonPlan) -> str:
    """An experimental Script is neither varied nor beyond +3 risk."""
    if not plan.experimental_script:
        return ""
    if plan.script_variation:
        return "An experimental Script isn't also varied: choose one or the other."
    if not 0 <= plan.risk <= mysteries.MAX_SCRIPT_RISK:
        return f"An experimental Script's risk is 0 to +{mysteries.MAX_SCRIPT_RISK}."
    return ""


def _mystery_problem(saga: Saga, character: Character, vf_id: str) -> str:
    """What a Mystery's own rule says stops its Initiation ("" if nothing):
    Secret Name fails for one with a talisman or a familiar (DE p. 235);
    Faerie Magic needs one touched by the fay, by a fay Virtue or Flaw or
    a Warping Point from a faerie (DE p. 236; the app can't tell where
    Warping came from, so any counts)."""
    if vf_id == mysteries.SECRET_NAME:
        if enchantment.talisman_of(saga, character) is not None:
            return (
                f"{character.name} has a talisman: Secret Name's Initiation "
                "fails (DE p. 235)."
            )
        if saga.familiar_of(character.id) is not None:
            return (
                f"{character.name} has a familiar: Secret Name's Initiation "
                "fails (DE p. 235)."
            )
    found = verditius.inner_mystery_problem(character, vf_id)
    if found:
        return found
    # House Merinita's Inner Mysteries (Houses of Hermes: Mystery Cults
    # pp. 85-88): a school's Outer Mystery, and the House's Lore 1.
    found = merinita.inner_mystery_problem(character, vf_id)
    if found:
        return found
    if vf_id == mysteries.FAERIE_MAGIC and not (
        touched_by_the_fay(character)
        or character.aging.warping_points
        or character.aging.warping_score
    ):
        return (
            f"{character.name} hasn't been touched by the fay (a fay Virtue or "
            "Flaw, or a Warping Point from a faerie): Faerie Magic can't be "
            "Initiated (DE p. 236)."
        )
    return ""


def _house_ordeal_problem(character: Character, plan: SeasonPlan) -> str:
    """What House Verditius's rules forbid of the Ordeal's Flaw (Houses of
    Hermes: Mystery Cults pp. 120-121)."""
    gained = _ordeal_gained(plan)
    found = verditius.ordeal_problem(character, gained.vf_id) if gained else ""
    return found or _bjornaer_ordeal_problem(character, plan)


def _bjornaer_ordeal_problem(character: Character, plan: SeasonPlan) -> str:
    """House Bjornaer's Inner Heartbeast needs a Major Hermetic or
    Supernatural Flaw, or a shapechanger's lost shapes (HoH:MC pp. 17, 30)."""
    gained, lost = _ordeal_gained(plan), _ordeal_lost(plan)
    flaw = (
        catalog.load_virtue_flaw_catalog_by_id().get(gained.vf_id) if gained else None
    )
    return bjornaer.ordeal_problem(
        character,
        plan.effect_id or "",
        plan.hedge_script,
        (flaw.id, flaw.tier, flaw.category) if flaw is not None else None,
        lost.vf_id if lost else "",
    )


def _ordeal_problem(character: Character, plan: SeasonPlan) -> str:
    """What is wrong with an Initiation's Ordeal ("" if nothing)."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    kind = ordeal_kind(plan)
    if not kind:
        return ""
    gained, lost = _ordeal_gained(plan), _ordeal_lost(plan)
    flaw = by_id.get(gained.vf_id) if gained else None
    if kind in (GAIN_FLAW, RAISE_FLAW):
        if flaw is None:
            return "Choose the Flaw the Ordeal gives."
        if flaw.side != "Flaw":
            return f"{flaw.name} is not a Flaw: choose the Flaw the Ordeal gives."
    if kind == GAIN_FLAW:
        assert flaw is not None
        if flaw.tier not in ORDEAL_REDUCTION:
            return f"{flaw.name} is a {flaw.tier} Flaw: an Ordeal's is Minor or Major."
        return ""
    entry = by_id.get(lost.vf_id) if lost else None
    if lost is None or entry is None or lost not in character.virtues_flaws:
        return (
            "Choose the Virtue the Ordeal takes away."
            if kind == LOSE_VIRTUE
            else "Choose the Minor Flaw the Ordeal raises."
        )
    if kind == LOSE_VIRTUE:
        if entry.side != "Virtue" or entry.tier not in ORDEAL_REDUCTION:
            return f"{entry.name} can't be lost to an Ordeal: choose a Minor or Major Virtue."
        return ""
    assert flaw is not None
    if entry.side != "Flaw" or entry.tier != "Minor":
        return f"{entry.name} is not a Minor Flaw: choose the Minor Flaw raised."
    if flaw.tier != "Major":
        return f"{flaw.name} is not a Major Flaw: choose the Major Flaw it becomes."
    return ""


def _initiation_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    found = _initiation_problem(saga, character, plan)
    return [found] if found else []


# -- the outcome ---------------------------------------------------------------


def _undergo_initiation(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    mystagogue = saga.character(plan.teacher_id) or character
    trait, name, lore, script = _initiation_terms(mystagogue, plan, character)
    result.notes += _script_notes(character, plan)
    result.notes += _later_lore_warning(character, plan)
    beast = _bjornaer_terms(character, mystagogue, plan, name, result)
    lore = beast[1] if beast is not None else lore
    target = initiation_target(saga, character, plan)
    size = ordeal_size(plan)
    risk = 0
    rite_failed = False
    if plan.experimental_script:
        if rng is None:
            result.notes.append(
                "An experimental Script's dice are rolled when the season is played."
            )
            return
        rite_failed, risk = _experiment_with_script(
            saga, character, mystagogue, plan, rng, lore, script, result
        )
        script += plan.script_sympathy
    elif plan.script_variation in mysteries.VARY_EASE:
        if rng is None:
            result.notes.append(
                f"Varying the Script ({plan.script_variation}) is rolled when the "
                "season is played."
            )
            return
        varied = _vary_script(saga, mystagogue, plan, rng, lore, script, result)
        if varied is None:
            return
        script = varied
    value = (
        beast[0]
        if beast is not None
        else getattr(mystagogue.characteristics, trait.lower(), 0)
    )
    full = value + lore + script + risk
    # Each month lost takes a third of the original total, rounded up; an
    # Initiation it makes fail still costs the Ordeal (TMRE p. 12).
    months = max(0, min(plan.months_lost, 3))
    total = max(0, full - months * round_up(full / 3))
    distracted = months > 0 and full >= target > total and not rite_failed
    initiated = total >= target and not rite_failed
    # An experimental rite is carried out, Ordeals and all, before it is
    # checked, so a failed one still costs its Ordeal (TMRE p. 18).
    suffered = initiated or distracted or rite_failed
    if initiated:
        result.initiated = True
        if plan.effect_id:
            result.add_vfs.append(_initiated(plan))
    if suffered:
        if gained := _ordeal_gained(plan):
            result.add_vfs.append(gained)
            if gained.vf_id == verditius.INCREASED_HUBRIS:
                # Enough experience for one more point of Hubris (HoH:MC
                # p. 121), counted when the season is applied.
                result.hubris_rises += 1
        if lost := _ordeal_lost(plan):
            result.remove_vfs.append(lost)
        result.ordeal = size
    if initiated and plan.effect_id:
        _house_hubris(character, plan.effect_id, result)
        _merinita_ordeal(plan, result)
        _bjornaer_outcome(character, plan, result)
    ordeal = f" {size} Ordeal." if size and suffered else ""
    lost_text = f", {months} month(s) lost from {full}" if months else ""
    risk_text = f" + risk {risk}" if risk else ""
    hedge = ts.hedge_script(plan.hedge_script)
    gains = (
        f" Add what it gives by hand: {hedge[1].gains}."
        if initiated and hedge is not None and not plan.effect_id and hedge[1].gains
        else ""
    )
    result.notes.append(
        f"Initiation Total {total} ({trait} + {name} + Script {script}{risk_text}"
        f"{lost_text}) against {target}: "
        + (
            "initiated."
            if initiated
            else "not initiated; the rite failed, but its Ordeal is still "
            "suffered (TMRE p. 18)."
            if rite_failed
            else "not initiated; the distractions failed it, so the Ordeal is "
            "still suffered and the Initiation must be repeated (TMRE p. 12)."
            if distracted
            else "not initiated."
        )
        + ordeal
        + gains
    )


def _later_lore_warning(initiate: Character, plan: SeasonPlan) -> list[str]:
    """A saga cult's guideline, as a warning the troupe may set aside: the
    second and later Initiations typically need the Lore at 3. They are
    counted by the Initiations taken (the cult's Virtues the Initiate
    holds), not by the degree; only the Lore at 1 is a must (The
    Mysteries Revised Edition pp. 11, 13; DE p. 387)."""
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is None or not is_saga_cult(hedge[0].id):
        return []
    tradition = hedge[0]
    rule = tradition.initiation
    assert rule is not None  # ts.hedge_script finds Scripts only in a rule
    virtues = set(tradition.virtues)
    taken = sum(1 for vf in initiate.virtues_flaws if vf.vf_id in virtues)
    score = _hedge_lore(initiate, rule.lore)
    if not taken or score >= LATER_LORE:
        return []
    return [
        f"{initiate.name} has taken {taken} of the cult's Initiations, and a "
        f"later one typically needs {rule.lore} {LATER_LORE} (he has {score}): "
        "the troupe may allow it (TMRE p. 13)."
    ]


def _house_hubris(character: Character, vf_id: str, result: SupplementWork) -> None:
    """The first Inner Mystery of House Verditius always brings the Flaw
    Hubris, a Minor Ordeal, and each one Hubris experience (Houses of
    Hermes: Mystery Cults p. 118; DE p. 241)."""
    result.notes += verditius.initiation_notes(character, vf_id)
    tier = verditius.INNER_MYSTERIES.get(vf_id)
    if tier is not None:
        result.hubris_xp += verditius.INNER_HUBRIS_XP[tier]
    if not verditius.gives_hubris(character, vf_id):
        return
    result.hubris_start = verditius.starting_hubris(character)
    if all(vf.vf_id != verditius.HUBRIS_FLAW for vf in result.add_vfs):
        result.add_vfs.append(VirtueFlawInstance(verditius.HUBRIS_FLAW))
    result.ordeal = result.ordeal or "Minor"


def _merinita_ordeal(plan: SeasonPlan, result: SupplementWork) -> None:
    """Glamour's Initiation always brings Vulnerable Magic, a Major Ordeal,
    with the plan's new condition, unless the plan's Ordeal is that Flaw
    already (Houses of Hermes: Mystery Cults pp. 87, 102); Perpetuity's
    usual Unnatural Magic is noted."""
    vf_id = plan.effect_id or ""
    result.notes += merinita.initiation_notes(vf_id)
    gained = _ordeal_gained(plan)
    flaw = merinita.ordeal_flaw(
        vf_id, gained.vf_id if gained else "", plan.ordeal_condition
    )
    if flaw is not None:
        result.add_vfs.append(flaw)
        result.ordeal = "Major"


def _bjornaer_terms(
    character: Character,
    mystagogue: Character,
    plan: SeasonPlan,
    lore_name: str,
    result: SupplementWork,
) -> tuple[int, int] | None:
    """House Bjornaer's notes on the Initiation, and the Great Beast's
    Presence and Lore when it stands in as Mystagogue (HoH:MC p. 30)."""
    beast = bjornaer.stand_in(character, mystagogue, plan.hedge_script)
    if beast is not None:
        result.notes.append(
            f"The Great Beast is the Mystagogue: Presence +{beast[0]}, "
            f"{lore_name} {beast[1]} (Houses of Hermes: Mystery Cults p. 30)."
        )
    result.notes += bjornaer.initiation_notes(
        character, plan.effect_id or "", plan.hedge_script
    )
    return beast


def _bjornaer_outcome(
    character: Character, plan: SeasonPlan, result: SupplementWork
) -> None:
    """The Ritual of Twelve Years gives Heartbeast 1, and the familiar
    forgone counts as a Minor Ordeal (HoH:MC pp. 25-26)."""
    xp, ordeal, note = bjornaer.outcome(
        character, plan.effect_id or "", plan.hedge_script
    )
    if xp:
        result.ability_xp.append((bjornaer.ABILITY, xp))
    if ordeal:
        result.ordeal = result.ordeal or ordeal
    if note:
        result.notes.append(note)


def components_for(initiate: Character) -> list[mysteries.Component]:
    """The Script components an Initiation plan may list: the general ones,
    and for a Verditius Initiate the House's own (HoH:MC p. 117)."""
    table = list(mysteries.COMPONENTS)
    if verditius.is_verditius(initiate):
        table += verditius.HOUSE_COMPONENTS
    return table


def script_lines(initiate: Character, plan: SeasonPlan) -> list[Line]:
    """A Hermetic Script written out as components: a line for each listed
    one, then the Ordeal's component (by the plan's Ordeal's size, or the
    Minor Ordeal of Hubris a Verditius's first Inner Mystery brings when
    the plan names none). [] when none is listed: the typed bonus is the
    whole Script."""
    if not plan.script_components or plan.hedge_script:
        return []
    lines = mysteries.parts_lines(plan.script_components, components_for(initiate))
    size = ordeal_size(plan)
    if not size and verditius.gives_hubris(initiate, plan.effect_id or ""):
        component = mysteries.ORDEAL_COMPONENTS["Minor"]
        lines.append(
            Line(
                f"{component.name} (Hubris)",
                amount=component.bonus,
                source=verditius.HUBRIS_SOURCE,
            )
        )
    elif not size and merinita.ordeal_flaw(plan.effect_id or "") is not None:
        component = mysteries.ORDEAL_COMPONENTS["Major"]
        lines.append(
            Line(
                f"{component.name} (Vulnerable Magic)",
                amount=component.bonus,
                source=merinita.GLAMOUR_SOURCE,
            )
        )
    elif size in mysteries.ORDEAL_COMPONENTS:
        component = mysteries.ORDEAL_COMPONENTS[size]
        lines.append(
            Line(component.name, amount=component.bonus, source=mysteries.SCRIPT_SOURCE)
        )
    return lines


def _script_notes(initiate: Character, plan: SeasonPlan) -> list[str]:
    """The Script's components as a note: the plan's own, or a catalog
    Script's printed ones, and a confraternity's path."""
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is not None:
        _, script = hedge
        found = [
            mysteries.printed_components_note(script.components, script.bonus),
            verditius.confraternity_note(script.name),
        ]
        return [note for note in found if note]
    lines = script_lines(initiate, plan)
    if not lines:
        return []
    extra = f", with {plan.other_modifier:+d} more" if plan.other_modifier else ""
    return [f"The Script: {mysteries.lines_text(lines)}{extra}."]


def _initiation_terms(
    mystagogue: Character, plan: SeasonPlan, initiate: Character | None = None
) -> tuple[str, str, int, int]:
    """The Initiation Total's terms: the Characteristic, the Lore's name
    and the Mystagogue's score in it, and the Script's bonus (a hedge
    Script's own, plus what the plan adds; a Hermetic one's listed
    components, plus the typed bonus). `initiate`: the one Initiated (the
    Mystagogue himself when not given)."""
    initiate = initiate or mystagogue
    hedge = ts.hedge_script(plan.hedge_script)
    if hedge is None:
        name = plan.title.strip()
        listed = sum(line.amount or 0 for line in script_lines(initiate, plan))
        return (
            "Presence",
            name,
            _hermetic_lore(mystagogue, name),
            int(listed) + plan.other_modifier,
        )
    tradition, script = hedge
    rule = tradition.initiation
    assert rule is not None  # ts.hedge_script finds Scripts only in a rule
    return (
        rule.characteristic,
        ts.hedge_lore(tradition),
        _hedge_lore(mystagogue, rule.lore),
        script.bonus
        + plan.other_modifier
        + bjornaer.script_extra(initiate, plan.hedge_script),
    )


def _vary_script(
    saga: Saga,
    mystagogue: Character,
    plan: SeasonPlan,
    rng: random.Random,
    lore: int,
    script: int,
    result: SupplementWork,
) -> int | None:
    """Roll the one change to the Script: its new bonus, or None when the
    change fails and so the Initiation does (DE p. 389)."""
    ease = mysteries.VARY_EASE[plan.script_variation]
    die = dice.stress_die(rng, 1, saga=saga)
    vary = die.value + mystagogue.characteristics.intelligence + lore
    if die.botched or vary < ease:
        result.notes.append(
            f"Varying the Script: {vary} against {ease}: failed, so the "
            "Initiation fails; the Script as it was may be tried another "
            "season (DE p. 389)."
        )
        return None
    script += plan.variation_bonus
    result.notes.append(
        f"Varying the Script: {vary} against {ease}: the Script bonus is now {script}."
    )
    return script


def _experiment_with_script(
    saga: Saga,
    initiate: Character,
    mystagogue: Character,
    plan: SeasonPlan,
    rng: random.Random,
    lore: int,
    proposed: int,
    result: SupplementWork,
) -> tuple[bool, int]:
    """An experimental Script's two rolls: the Extraordinary Results chart,
    then the rite's validity against 9 (15 on another Initiate) + the
    proposed bonus. Whether the rite failed, and the risk the Initiation
    Total adds (TMRE p. 18)."""
    rite = mysteries.experimental_rite(rng, plan.risk, saga)
    result.notes += rite.notes
    ease = mysteries.validity_ease(proposed, mystagogue is initiate)
    die = dice.simple_die(rng)
    valid = die + plan.risk + mystagogue.characteristics.intelligence + lore
    result.notes.append(
        f"The rite's validity: die {die} + risk {plan.risk} + Intelligence + Lore "
        f"= {valid} against {ease}: "
        + ("valid." if valid >= ease else "invalid, so no Virtue is gained.")
    )
    return rite.no_virtue or valid < ease, plan.risk if rite.risk_counts else 0


register(
    SimpleActivity(
        "undergo_initiation",
        "Undergo an Initiation",
        "The Initiate's whole season: the Mystery Virtue, and any Ordeal "
        "Flaw, are added when the Initiation succeeds.",
        DE_INITIATION,
        "918",
        no_xp=True,
        group=groups.MYSTERIES,
    ),
    _undergo_initiation,
    _initiation_problems,
)
register(
    SimpleActivity(
        "mystagogue",
        "Act as Mystagogue",
        "Leading an Initiation (a season when the Script needs it): Exposure "
        "2 in the Mystery's Lore.",
        MYSTERIES,
        "918",
        group=groups.MYSTERIES,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "quest_season",
        "Serve a Mystagogue / Quest season",
        "A season toward an Initiation Script's bonus: Exposure 2.",
        MYSTERIES,
        "918",
        group=groups.MYSTERIES,
    ),
    experience_only,
)
