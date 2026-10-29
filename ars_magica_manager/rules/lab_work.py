"""What a season of lab work produced (`LabWork`), and the vis pool a lab
plan pays from. Kept apart from lab_seasons so the enchanting, familiar and
laboratory seasons can name them without importing it."""

from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass, field

from .. import vis
from ..models import (
    BondPower,
    Character,
    EnchantedDevice,
    ExperimentalEffect,
    Familiar,
    InstilledEffect,
    Saga,
    SeasonPlan,
    Spell,
)
from . import experiment, lab


@dataclass
class LabWork:
    """What a season of lab work does: the Lab Total and, for inventing, the
    points before and after. One-season work without a spell
    has `spell` None, level 0 and is finished; its results are below."""

    spell: Spell | None
    lab_total: lab.LabTotal
    level: int
    points_before: int = 0
    points_gained: int = 0
    finished: bool = False
    notes: list[str] = field(default_factory=list)
    #: Extracting vis: pawns gained, and of which Art (Vim, or a Form
    #: with Hermetic Alchemy or an Extractor Virtue).
    vis_gained: int = 0
    vis_gained_art: str = "Vim"
    #: Waster of Vis: the pawns wasted on top of vis_cost (Art -> pawns).
    vis_wasted: dict[str, int] = field(default_factory=dict)
    #: Vis paid for the work: Art -> pawns.
    vis_cost: dict[str, int] = field(default_factory=dict)
    #: A Longevity Ritual: its subject and aging-roll modifier.
    subject: Character | None = None
    longevity: int = 0
    #: Enchanting: the device and effect worked on, a charged
    #: item's charges, and the effects an investigation found.
    device: EnchantedDevice | None = None
    effect: InstilledEffect | None = None
    #: Opening: the pawns it counts as opened (Verditius Magic opens it
    #: for fewer than it holds); 0 means what was paid.
    pawns_opened: int = 0
    charges: int = 0
    #: Lab Texts: the other spells learned with `spell` the same season.
    more_spells: list[Spell] = field(default_factory=list)
    revealed: list[str] = field(default_factory=list)
    #: Familiar work: the familiar, and the bond power instilled.
    familiar: Familiar | None = None
    power: BondPower | None = None
    #: Decoding: (reader id, the author's key -- see
    #: book_seasons.author_key --, level) readable when done.
    access: tuple[str, str, int] | None = None
    #: Work on the laboratory: setting up its second season, the
    #: Refinement it will have (and had), and the Virtues/Flaws the season's
    #: roll gains or loses.
    second_season: bool = False
    refinement: int = 0
    old_refinement: int = 0
    gains_vf: list[str] = field(default_factory=list)
    loses_vf: list[str] = field(default_factory=list)
    #: Stabilizing: the Discovery's magnitude.
    research_magnitude: int = 0
    #: Experimental effects an invention carries to its spell.
    carried_effects: list[ExperimentalEffect] = field(default_factory=list)
    #: Recreating a flawed spell: the storyguide chose, in Advance Season,
    #: to retire the flawed one once this one is invented.
    retire_flawed: bool = False
    research_warping: int = 0
    #: Experimenting: the season's Extraordinary Results.
    experiment: experiment.Extraordinary | None = None
    #: Experimenting with a Lab Total too low for the work: why. The
    #: season makes no progress, but the chart is still rolled and any vis
    #: paid is lost.
    too_low: str = ""

    @property
    def points_after(self) -> int:
        return self.points_before + self.points_gained


def vis_pool(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> MutableMapping[str, int]:
    """The raw vis a lab plan pays with (or extracted vis goes to): the
    laboratory's, the magus's own, or the vis stores of the laboratory's
    covenant (the magus's, for a lab with none)."""
    lab_ = saga.laboratory(plan.lab_id) if plan.lab_id else None
    if plan.vis_from == "laboratory":
        return lab_.raw_vis if lab_ is not None else {}
    if plan.vis_from == "covenant":
        covenant_id = (lab_.covenant_id if lab_ is not None else None) or (
            magus.covenant_id
        )
        return vis.covenant_pool(saga, covenant_id, magus.name)
    return magus.raw_vis


def whose_vis(magus: Character, plan: SeasonPlan) -> str:
    if plan.vis_from == "covenant":
        return "the covenant's"
    return "the laboratory's" if plan.vis_from == "laboratory" else f"{magus.name}'s"
