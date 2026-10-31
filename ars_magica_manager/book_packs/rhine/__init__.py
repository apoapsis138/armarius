"""Guardians of the Forests: the Rhine Tribunal, as of spring 1220, in
paraphrase. Built in parts: the land (places), the covenants and their
magi and libraries, the mundane world round them, the Tribunal's Code,
docket and history, and the Rhine Gorge threat.

Source: Guardians of the Forests: The Rhine Tribunal (Atlas Games), open
content under CC-BY-SA 4.0 at redcap.org; the text here is a summary of
it, not its words."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from .. import BookPack, register
from ..builder import Builder

NAME = "Guardians of the Forests: the Rhine Tribunal"
SOURCE = (
    "Guardians of the Forests: The Rhine Tribunal, by Atlas Games, open "
    "content under the Creative Commons Attribution-ShareAlike 4.0 licence "
    "(redcap.org); summarised, not quoted."
)


@dataclass
class Rhine:
    """The records the parts hand one another, by a short key."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    """The pack, with Through the Aegis's part if `supplements` names it,
    so the pack on its own stays as its book has it."""
    # start-up: a region's parts load when its pack is built, not at import.
    from . import (
        bestiary,
        collem_leonis,
        covenants_east,
        covenants_west,
        gorge,
        history,
        places,
        stats_gorge,
        stats_magi,
        stats_sketched,
        tribunal,
        world_north_east,
        world_west,
    )

    rhine = Rhine(Builder(NAME, source="GotF"))
    places.build(rhine)
    tribunal.build(rhine)
    covenants_west.build(rhine)
    covenants_east.build(rhine)
    stats_magi.build(rhine)
    world_west.build(rhine)
    world_north_east.build(rhine)
    gorge.build(rhine)
    bestiary.build(rhine)
    stats_gorge.build(rhine)
    history.build(rhine)
    if "TtA" in supplements:
        collem_leonis.build(rhine)
    tribunal.finish(rhine)
    stats_magi.peregrinatores(rhine)
    stats_sketched.build(rhine)
    if "TtA" in supplements:
        collem_leonis.stats(rhine)
    return rhine.b


def build() -> Saga:
    return assemble().saga


register(BookPack("rhine", "GotF", NAME, assemble, SOURCE, ("TtA",)))
