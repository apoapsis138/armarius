"""The Definitive Edition's seasons the supplement menu lists beside the
books': training a combat group, worship, taming and training an animal
(points a season toward its Might, kept only over consecutive seasons),
travel and convalescence."""

from __future__ import annotations

import random

from ... import catalog
from ...models import Character, Progress, Saga, SeasonPlan, next_season
from .. import activity_groups as groups
from ..scores import ability_level
from .base import (
    ANYONE,
    SimpleActivity,
    SupplementWork,
    experience_only,
    needs_name,
    progress_of,
    register,
    source,
)

SOURCE = source(
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, pp. 373-392", "DE"
)
DE_TAMING = source(
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Taming Animals "
    "(Training Creatures), pp. 384-386",
    "DE",
)
#: Taming's points last only over consecutive seasons (DE p. 384).
CONSECUTIVE_KINDS = ("taming",)
TAMING_SOURCE = "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Training Creatures, pp. 384-386"
#: The Gift's penalty to taming a mundane beast, a social activity (DE pp.
#: 204, 384): none with the Gentle Gift, 6 with the Blatant Gift.
GIFT_TAMING = {"vf_gentle_gift": 0, "vf_blatant_gift": 6}
MASTER_OF_CREATURES = "vf_master_of_form_creatures"


def kept_points(record: Progress | None, season: str, year: int) -> int:
    """The points a record still holds for a season's work: all of them,
    unless it is taming and the last season on it wasn't the one before."""
    if record is None or record.done:
        return 0
    if record.kind not in CONSECUTIVE_KINDS or record.last_year is None:
        return record.points
    if next_season(record.last_season, record.last_year) != (season, year):
        return 0
    return record.points


def gift_penalty(character: Character) -> int:
    """What The Gift takes off taming a mundane beast (3; 0 Gentle, 6
    Blatant)."""
    ids = {vf.vf_id for vf in character.virtues_flaws}
    for vf_id, penalty in GIFT_TAMING.items():
        if vf_id in ids:
            return penalty
    return 3 if ids & set(catalog.GIFT_IDS) else 0


def master_of_creatures(character: Character) -> str | None:
    """The Form a Master of (Form) Creatures tames, or None."""
    for vf in character.virtues_flaws:
        if vf.vf_id == MASTER_OF_CREATURES:
            return str(vf.params.get("form") or "").title() or "?"
    return None


def more_tamed(points: int, might: int, handling: int) -> int:
    """How many more creatures of the same species a season's points tame
    beside the first, when they are enough for one in a season: shared out,
    at most the tamer's Animal Handling more (DE p. 384)."""
    need = max(1, might)
    if points < need:
        return 0
    return min(handling, points // need - 1)


def beast_might(confidence: int) -> int:
    """A mundane beast's effective Might for taming: 1 + 2 x its
    Confidence Score (DE p. 384)."""
    return 1 + 2 * max(0, confidence)


def _tame_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    named = needs_name(saga, character, plan)
    if named:
        return named
    if plan.book_level is None:
        return ["Type the animal's Might."]
    return []


def _tame_animal(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    might = plan.book_level or 0
    gift = gift_penalty(character)
    handling = ability_level(character, "Animal Handling")
    ken = ability_level(character, "Animal Ken")
    master = master_of_creatures(character)
    if master is not None:
        # A Master of (Form) Creatures tames with his Magic Lore in place of
        # Might (DE p. 385).
        base, label = ability_level(character, "Magic Lore"), "Magic Lore"
        creature = next((c for c in saga.creatures if c.name == name), None)
        if creature is not None and creature.might_form not in ("", master):
            result.notes.append(
                f"A Master of {master} Creatures tames only creatures of {master}: "
                f"{name} is of {creature.might_form}."
            )
    else:
        base, label = character.characteristics.intelligence, "Int"
    points = max(0, base + handling + ken - might - gift)
    record = progress_of(character, "taming", name)
    if (
        record is not None
        and record.points
        and not kept_points(record, plan.season, plan.year)
    ):
        result.notes.append(
            f"The {record.points} points toward taming {name} are lost: the "
            "seasons weren't consecutive (DE p. 384)."
        )
    result.progress.append(("taming", name, max(1, might), points))
    result.notes.append(
        f"{label} + Animal Handling + Animal Ken - Might {might}"
        + (f" - the Gift {gift}" if gift else "")
        + f" = {points} toward taming {name}."
    )
    more = more_tamed(points, might, handling)
    if more:
        result.notes.append(
            f"Enough to tame {more} more of the same kind this season, sharing "
            "the points (at most Animal Handling more, DE p. 384)."
        )


register(
    SimpleActivity(
        "train_group",
        "Train a combat group",
        "A season training together: the group becomes trained. Exposure 2 "
        "in Leadership or the weapon.",
        SOURCE,
        "919",
        group=groups.TEACHING,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "worship",
        "Worship",
        "Source Quality = the church's Divine aura (Church Lore, "
        "Concentration, Music...).",
        SOURCE,
        "921",
        None,
        "the church's Divine aura",
        # Any Christian with a chapel may worship, a magus too (DE p. 378).
        ANYONE,
        group=groups.FAITH,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "tame_animal",
        "Tame and train an animal",
        "Intelligence + Animal Handling + Animal Ken - its Might (less the "
        "Gift's 3, 6 Blatant, none Gentle) points a season until they reach "
        "its Might; a mundane beast's is 1 + 2 x its Confidence. The points "
        "last only over consecutive seasons. A Master of (Form) Creatures "
        "uses Magic Lore in place of Intelligence. Points enough for one in a "
        "season may be shared among more of the same kind, at most Animal "
        "Handling more (DE pp. 384-385). Tamed, a creature of the saga gains "
        "Loyal +0 to its tamer. Exposure 2 in Animal Handling.",
        DE_TAMING,
        "922",
        group=groups.WORK,
    ),
    _tame_animal,
    _tame_problems,
)
register(
    SimpleActivity(
        "travel",
        "Travel",
        "A season travelling (it may lower Living Conditions): Exposure 2 in "
        "an Area Lore or a language.",
        SOURCE,
        "923",
        group=groups.ADVENTURE,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "convalesce",
        "Convalesce from wounds",
        "Recovering: no lab or craft work; study at half (type the halved "
        "Source Quality).",
        SOURCE,
        "923",
        no_xp=True,
        group=groups.REST,
    ),
    experience_only,
)
