"""A season with nothing planned: what the saga does by default (Edit
Saga), who Advance Season names, and the plan the default makes.

By default a magus or companion with nothing planned spends the season on
Work / Exposure in their profession (else a magus's Magic Theory, else
their highest Ability that isn't a language), and a grog with no yearly
update gains 2 xp of Exposure a season in their highest Ability (8 at the
year's end). Each kind can be set to Nothing instead.
"""

from __future__ import annotations

from ..models import Character, Saga, SeasonPlan, XpAllocation
from ..rules import activities as rules
from .plans import unplanned

EXPOSURE = "exposure"
NOTHING = "nothing"
OPTIONS: list[tuple[str, str]] = [("Work / Exposure", EXPOSURE), ("Nothing", NOTHING)]
#: A grog's default year: 2 xp of Exposure each season.
GROG_YEAR_XP = 8
#: Abilities a default season never goes into while there is another: a
#: season isn't spent working at a language.
LANGUAGES = ("Living Language", "Dead Language")
BARE_LANGUAGES = {"Latin", "Greek", "Arabic", "Hebrew"}

THEORY = "Magic Theory"

#: The Edit Saga field for each kind of character.
SETTING_OF = {
    "magus": "unplanned_magi",
    "companion": "unplanned_companions",
    "mythic companion": "unplanned_companions",
    "grog": "unplanned_grogs",
}


def default_of(saga: Saga, character: Character) -> str:
    """What `character` does with a season left unplanned (EXPOSURE or
    NOTHING)."""
    setting = SETTING_OF.get(character.type)
    return getattr(saga, setting, NOTHING) if setting else NOTHING


def is_player_character(character: Character) -> bool:
    """Whether a Player plays `character` (a non-player character has none)."""
    return bool(character.background.player.strip() or character.background.player_id)


def notified(saga: Saga) -> list[Character]:
    """Those Advance Season names as having nothing planned: the player
    characters, and the others too when the saga says so."""
    return [
        c
        for c in unplanned(saga)
        if saga.notify_npc_unplanned or is_player_character(c)
    ]


def _is_language(name: str) -> bool:
    return name.startswith(LANGUAGES) or name in BARE_LANGUAGES


def exposure_ability(character: Character) -> str | None:
    """Where a default season's Exposure goes: the character's profession
    (their best), else a magus's Magic Theory (Exposure needs a score in
    it), else their highest Ability that isn't a language (a language only
    when they have nothing else)."""
    abilities = sorted(character.abilities, key=lambda a: -a.xp)
    trade = [a for a in abilities if a.name.startswith("Profession")]
    if trade:
        return trade[0].name
    if character.type == "magus" and any(a.name == THEORY for a in abilities):
        return THEORY
    skills = [a for a in abilities if not _is_language(a.name)] or abilities
    return skills[0].name if skills else None


def default_text(saga: Saga, character: Character) -> str:
    """ "Work / Exposure in Profession: Scribe", or "nothing"."""
    ability = exposure_ability(character)
    if default_of(saga, character) == NOTHING or ability is None:
        return "nothing"
    return f"Work / Exposure in {ability}"


def default_plan(saga: Saga, character: Character) -> SeasonPlan | None:
    """The plan the saga's default makes for `character`'s unplanned
    season, or None for Nothing."""
    ability = exposure_ability(character)
    if default_of(saga, character) == NOTHING or ability is None:
        return None
    return SeasonPlan(
        character.id,
        saga.current_year,
        saga.current_season,
        rules.EXPOSURE,
        allocations=[XpAllocation(rules.ability_subject(ability), 0)],
        by_default=True,
    )


def grog_default(saga: Saga, character: Character) -> tuple[str, int] | None:
    """A grog with no yearly update: (the Ability, the year's xp) the
    saga's default gives, or None."""
    if default_of(saga, character) == NOTHING or not character.abilities:
        return None
    best = max(character.abilities, key=lambda a: a.xp)
    return best.name, GROG_YEAR_XP
