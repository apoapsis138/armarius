"""The Lion and the Lily: the Normandy Tribunal, as of spring 1220, in
paraphrase. Built in parts: the Tribunal itself and its Code, docket and
ruined covenants; then each region's land, covenants, magi, libraries,
vis and mundane world; Confluensis; the saga's stories; the history;
and last the lines of fealty and the generated stats.

Source: The Lion and the Lily: The Normandy Tribunal (Atlas Games), open
content under CC-BY-SA 4.0 at redcap.org; the text here is a summary of
it, not its words."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ...models import Character, Covenant, Neighbour, Saga, Tribunal
from ...tribunal_packages import normandy as package
from .. import BookPack, register
from ..builder import Builder

NAME = "The Lion and the Lily: the Normandy Tribunal"
SOURCE = (
    "The Lion and the Lily: The Normandy Tribunal, by Atlas Games, open "
    "content under the Creative Commons Attribution-ShareAlike 4.0 licence "
    "(redcap.org); summarised, not quoted."
)


@dataclass
class Normandy:
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

    def tenure(
        self,
        source: str,
        holder: Covenant | None,
        tenure: str,
        until: int | None = None,
        notes: str = "",
    ) -> dict[str, Any]:
        """A vis source under the Perthean Compact: who holds it (None:
        the Tribunal), on which of package.TENURES, and until when."""
        assert self.tribunal is not None
        assert tenure in package.TENURES, tenure
        entry = {
            "source": source,
            "holder_id": holder.id if holder is not None else None,
            "tenure": tenure,
            "until": until,
            "notes": notes,
        }
        package.tenures(self.tribunal).append(entry)
        return entry


#: The parts, in the order they are built.
PARTS = (
    "tribunal",
    "brittany",
    "duchy",
    "anjou_aquitaine",
    "ile_de_france",
    "flanders_picardy",
    "champagne_burgundy",
    "confluensis",
    "stories",
    "history",
)


def assemble() -> Builder:
    import importlib

    parts = [importlib.import_module(f"{__name__}.{name}") for name in PARTS]
    normandy = Normandy(Builder(NAME, source="L&L"))
    for part in parts:
        part.build(normandy)
    for part in parts:
        finish = getattr(part, "finish", None)
        if finish is not None:
            finish(normandy)
    for part in parts:
        stats = getattr(part, "stats", None)
        if stats is not None:
            stats(normandy)
    return normandy.b


def build() -> Saga:
    return assemble().saga


register(BookPack("normandy", "L&L", NAME, assemble, SOURCE))
