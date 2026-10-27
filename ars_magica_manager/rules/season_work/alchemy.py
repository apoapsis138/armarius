"""The Mysteries Revised Edition's alchemy as a season: reinventing the
Lesser Elixir (pp. 42-43). The rules are rules.tmre_alchemy's.

The plan names the new special ingredient (its title), its Shape and
Material bonus (book_level) and whether the alchemist devised it himself
by Vulgar Alchemy (devised: its points are doubled). The season prepares a
dose of his Longevity Ritual from its Lab Text -- the vis of his age / 5,
of the plan's vis_art (Creo, Corpus or Vim), from the pool its vis_from
names -- adds the ingredient, and devises the formula again at his Magic
Theory: the dose in force from then on adds the Elixir Level to the
ritual's aging-roll modifier, until an Aging Crisis ends it.
"""

from __future__ import annotations

import random

from ... import vis
from ...models import (
    TEXT_LONGEVITY,
    Book,
    Character,
    ElixirIngredient,
    Saga,
    SeasonPlan,
)
from .. import activity_groups as groups
from .. import book_seasons, lab, library
from .. import tmre_alchemy as alchemy
from ..rounding import round_up
from .base import MAGI, SimpleActivity, SupplementWork, register, source

LESSER = source(alchemy.LESSER_SOURCE, "TMRE")
STORY = "TMRE-1"

REINVENT_ELIXIR = "reinvent_lesser_elixir"
#: The Arts a Longevity Ritual's vis may be (DE p. 261).
DOSE_ARTS = ("Creo", "Corpus", "Vim")


def ritual_texts(saga: Saga, character: Character) -> list[Book]:
    """His own Longevity Ritual's Lab Texts that he can get at and read
    (a dose is prepared from one, DE p. 261)."""
    return [
        b
        for b in saga.books
        if b.type == "Lab Text"
        and b.text_kind == TEXT_LONGEVITY
        and b.ritual_subject == character.name
        and library.can_read(saga, character, b)
        and book_seasons.can_use_lab_text(character, b)
    ]


def dose_vis(saga: Saga, character: Character) -> int | None:
    """Pawns a dose of his Longevity Ritual takes: his age / 5, rounded up
    (DE p. 261); None without a year of birth."""
    born = character.background.year_born
    return None if born is None else max(0, round_up((saga.current_year - born) / 5))


def _art(plan: SeasonPlan) -> str:
    return plan.vis_art if plan.vis_art in DOSE_ARTS else "Vim"


def _reinvent(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The dose's vis, the ingredient added, and the Level it gives."""
    pawns = dose_vis(saga, character) or 0
    if pawns:
        result.vis_cost[_art(plan)] = pawns
    ingredient = ElixirIngredient(
        plan.title.strip(),
        max(0, plan.book_level or 0),
        devised=plan.devised,
        year=plan.year,
    )
    result.elixir_ingredient = ingredient
    theory = alchemy.magic_theory(character)
    had = character.alchemy.ingredients if character.alchemy is not None else []
    points = alchemy.elixir_points([*had, ingredient], theory)
    level = alchemy.elixir_level(points, theory)
    result.notes.append(
        f"{ingredient.name}: {alchemy.ingredient_points(ingredient.bonus, ingredient.devised, theory)} "
        f"Elixir Point(s); {points} in all give Elixir Level {level} (at most "
        f"Magic Theory {theory}), added to his Longevity Ritual's "
        f"{character.aging.longevity_modifier} while this dose is in force "
        f"({alchemy.LESSER_SOURCE})."
    )
    if pawns:
        result.notes.append(
            f"The dose of his Longevity Ritual takes {pawns} pawn(s) of "
            f"{_art(plan)} vis from {vis.payer(character, plan)} raw vis."
        )


def _problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    why = alchemy.lesser_elixir_problem(character)
    if why:
        return [why]
    if not plan.title.strip():
        return ["Name the special ingredient added."]
    if plan.book_level is None or plan.book_level < 0:
        return ["Type the ingredient's Shape and Material bonus."]
    if character.aging.longevity_modifier <= 0:
        return [
            f"{character.name} has no Longevity Ritual in force: the Elixir adds "
            f"to one ({alchemy.LESSER_SOURCE})."
        ]
    if not ritual_texts(saga, character):
        return [
            f"A dose of {character.name}'s Longevity Ritual is prepared from its "
            "Lab Text, and none is at hand (DE p. 261)."
        ]
    pawns = dose_vis(saga, character)
    if pawns is None:
        return [f"Give {character.name} a year of birth: the dose's vis is age / 5."]
    # The dose is a rebrew from the Lab Text: its Art's vis at most his score.
    over = lab.ritual_vis_problem(character, _art(plan), pawns)
    if over:
        return [over]
    held = vis.season_pool(saga, character, plan).get(_art(plan).lower(), 0)
    if held < pawns:
        return [
            f"The dose takes {pawns} pawn(s) of {_art(plan)} vis; "
            f"{vis.payer(character, plan)} raw vis has {held}."
        ]
    return []


register(
    SimpleActivity(
        REINVENT_ELIXIR,
        "Reinvent the Lesser Elixir",
        "A season in the laboratory adding a special ingredient to the Lesser "
        "Elixir, its Shape and Material bonus in Elixir Points: the Elixir "
        "Level adds to his own Longevity Ritual.",
        LESSER,
        STORY,
        hint="Exposure (2 xp), as other lab work, in Magic Theory.",
        who=MAGI,
        group=groups.MYSTERIES,
    ),
    _reinvent,
    _problems,
)
