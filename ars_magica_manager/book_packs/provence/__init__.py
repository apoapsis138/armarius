"""Faith & Flame: the Provençal Tribunal, as of 1220, in paraphrase.
Built in parts: the Tribunal itself and its Code, docket and ruined
covenants; then each region's land, covenants, magi, libraries, vis and
mundane world; Val-Negra; Jardin, from Through the Aegis; the saga's
stories; the history; and last the generated stats.

Source: Faith & Flame: The Provençal Tribunal (Atlas Games), content
under CC-BY-SA 4.0; the text here is a summary of it, not its words."""

from __future__ import annotations

from dataclasses import dataclass, field

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from .. import BookPack, register
from ..builder import Builder

NAME = "Faith & Flame: the Provençal Tribunal"
SOURCE = (
    "Faith & Flame: The Provençal Tribunal, by Atlas Games, content under "
    "the Creative Commons Attribution-ShareAlike 4.0 licence; summarised, "
    "not quoted."
)


@dataclass
class Provence:
    """The records the parts hand one another, by a short key."""

    b: Builder
    tribunal: Tribunal | None = None
    places: dict[str, Neighbour] = field(default_factory=dict)
    covenants: dict[str, Covenant] = field(default_factory=dict)
    magi: dict[str, Character] = field(default_factory=dict)
    world: dict[str, Neighbour] = field(default_factory=dict)

    def covenant_named(self, name: str) -> Covenant:
        """The covenant of that name, made by any part."""
        found = next((c for c in self.b.saga.covenants if c.name == name), None)
        if found is None:
            raise KeyError(f"No covenant named {name!r} yet")
        return found


#: The parts, in the order they are built.
PARTS = (
    "tribunal",
    "toulousain",
    "gascony",
    "pyrenees",
    "narbonnais",
    "arelat",
    "val_negra",
    "stories",
    "history",
    "bestiary",
)


#: The parts each supplement adds, run only when asked for, so the pack
#: on its own stays as its book has it.
SUPPLEMENTS = {"TtA": ("jardin",)}


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    names = (*PARTS, *(n for book in supplements for n in SUPPLEMENTS[book]))
    parts = [importlib.import_module(f"{__name__}.{name}") for name in names]
    provence = Provence(Builder(NAME, source="F&F"))
    for part in parts:
        part.build(provence)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(provence)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(provence)
    return provence.b


def build() -> Saga:
    return assemble().saga


register(BookPack("provence", "F&F", NAME, assemble, SOURCE, tuple(SUPPLEMENTS)))
