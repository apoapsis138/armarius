"""The saga's Tribunals: what each is called, which covenants belong to
it, and making and deleting one. A covenant names its Tribunal by id
(Covenant.tribunal_id); everything else a Tribunal's sheet shows is
worked out from the covenants and characters that belong to it."""

from __future__ import annotations

from . import storage, world
from .models import Covenant, Saga, Tribunal


def title(tribunal: Tribunal) -> str:
    """How a Tribunal is named in a sentence: "Rhine" reads as "Rhine
    Tribunal"; a name that already says Tribunal is left alone."""
    name = tribunal.name.strip()
    return name if name.casefold().endswith("tribunal") else f"{name} Tribunal"


def of(saga: Saga, covenant: Covenant) -> Tribunal | None:
    """The Tribunal `covenant` belongs to, if any."""
    return saga.tribunal(covenant.tribunal_id)


def title_of(saga: Saga, covenant: Covenant) -> str:
    """The name of `covenant`'s Tribunal as a sentence says it, or ""."""
    tribunal = of(saga, covenant)
    return title(tribunal) if tribunal is not None else ""


def covenants_of(saga: Saga, tribunal: Tribunal) -> list[Covenant]:
    """The covenants that belong to `tribunal`, the troupe's first."""
    return world.troupe_first(
        [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    )


def options(saga: Saga) -> list[tuple[str, str]]:
    """The saga's Tribunals as (label, id) choices."""
    return [(t.name, t.id) for t in saga.tribunals]


def add(saga: Saga, name: str) -> Tribunal:
    """A new Tribunal called `name`, with the core rules, added to the
    saga."""
    tribunal = Tribunal(
        id=storage.generate_unique_id(name, [t.id for t in saga.tribunals]),
        name=name,
    )
    saga.tribunals.append(tribunal)
    return tribunal


def deletion_consequences(saga: Saga, tribunal: Tribunal) -> list[str]:
    """What deleting `tribunal` does besides removing it."""
    members = [c.name for c in saga.covenants if c.tribunal_id == tribunal.id]
    if not members:
        return []
    return [
        f"{', '.join(members)} will belong to no Tribunal; "
        "nothing else about them changes."
    ]


def delete(saga: Saga, tribunal: Tribunal) -> None:
    """Remove `tribunal`; its covenants belong to none."""
    for covenant in saga.covenants:
        if covenant.tribunal_id == tribunal.id:
            covenant.tribunal_id = None
    saga.tribunals = [t for t in saga.tribunals if t is not tribunal]
