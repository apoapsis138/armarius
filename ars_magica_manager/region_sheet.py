"""What the Region and a neighbour's sheet show, worked out from the
saga's records for either front-end: the Region's facts, a list per
group of neighbours and the covenants the troupe doesn't play, and a
neighbour's own facts and details."""

from __future__ import annotations

from . import neighbours, threats, tribunal_packages, tribunals, world
from .character_sheet import Fact
from .grids import Grid
from .markup import escape
from .models import Covenant, Neighbour, Saga, Tribunal


def _attitude_cell(saga: Saga, record: Neighbour | Covenant) -> tuple[str, str | None]:
    """The attitude toward the home covenant as a cell, "−1 Wary", and the
    colour it is drawn in; blank with no player covenant."""
    score = neighbours.score(saga, record)
    if score is None:
        return "", None
    words = f"{world.SEAL_GLYPH} {world.signed(score)} {world.attitude_word(score)}"
    return words, f"${world.attitude_colour(score)}"


def others(saga: Saga) -> list[Covenant]:
    """The covenants the troupe doesn't play."""
    return [c for c in saga.covenants if not c.played]


# -- the Region's top panel --


def _next_meeting(tribunal: Tribunal | None) -> str:
    if tribunal is None or tribunal.next_year is None:
        return "(not set)"
    return f"{tribunal.next_season} {tribunal.next_year}"


def facts(saga: Saga) -> list[Fact]:
    """The home covenant, its Tribunal, the neighbours and how they
    stand, and when the Tribunal next meets."""
    home = neighbours.home(saga)
    tribunal = tribunals.of(saga, home) if home is not None else None
    scores = [neighbours.score(saga, n) for n in saga.neighbours]
    warm = sum(1 for s in scores if s is not None and s > 0)
    wary = sum(1 for s in scores if s is not None and s < 0)
    count = len(saga.neighbours)
    standing = f"{count}, {warm} warm, {wary} wary" if home is not None else str(count)
    customs = tribunal_packages.of(tribunal) if tribunal is not None else None
    return [
        Fact("Player covenant", home.name if home is not None else "(none)"),
        Fact(
            "Tribunal",
            tribunal.name if tribunal is not None else "(none chosen)",
        ),
        Fact(
            "Customs",
            tribunal_packages.label(customs) if customs is not None else "",
        ),
        Fact("Neighbours", standing),
        Fact("Other covenants", str(len(others(saga)))),
        Fact("Next Tribunal", _next_meeting(tribunal)),
        Fact("Threat due", threat_due(saga)),
    ]


def threat_due(saga: Saga) -> str:
    """The threat whose next stage comes soonest: "The Hollow Crown,
    Winter 1220"; "" if none has a dated stage to come."""
    due = [
        found
        for n in saga.neighbours
        if n.kind == "threat" and (found := threats.due(saga, n)) is not None
    ]
    return min(due)[1] if due else ""


def neighbours_title(saga: Saga) -> str:
    return f"Neighbours ({len(saga.neighbours)})"


# -- the lists --


def covenants_title(saga: Saga) -> str:
    return f"Other Covenants ({len(others(saga))})"


def covenants_grid(saga: Saga) -> Grid:
    """The covenants the troupe doesn't play: their Tribunal, votes,
    attitude toward the home covenant and detail."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, covenant in enumerate(others(saga)):
        words, colour = _attitude_cell(saga, covenant)
        if colour:
            styles[(index, 3)] = colour
        tribunal = tribunals.of(saga, covenant)
        rows.append(
            [
                covenant.name,
                tribunal.name if tribunal is not None else "",
                str(world.votes(saga, covenant)),
                words,
                covenant.detail,
            ]
        )
    return Grid(
        ["Covenant", "Tribunal", "Votes", "Attitude", "Detail"],
        rows,
        list(range(len(rows))),
        "No other covenants: add one with New Covenant, kept at Line or Sketch detail.",
        styles,
        caps=[24, 16, 5, 15, 0],
    )


def kind_text(neighbour: Neighbour) -> str:
    """Its kind as the lists show it: "Lord"."""
    return neighbours.kind_of(neighbour).name


def group_title(saga: Saga, group_key: str) -> str:
    group = neighbours.group(group_key)
    return f"{group.title} ({len(neighbours.members(saga, group_key))})"


def group_grid(saga: Saga, group_key: str) -> Grid:
    """The group's neighbours: kind, ruler, attitude toward the home
    covenant and detail."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    members = neighbours.members(saga, group_key)
    for index, neighbour in enumerate(members):
        words, colour = _attitude_cell(saga, neighbour)
        if colour:
            styles[(index, 3)] = colour
        rows.append(
            [
                neighbour.name,
                kind_text(neighbour),
                neighbour.ruler,
                words,
                neighbour.detail,
            ]
        )
    kinds = ", ".join(k.name.lower() for k in neighbours.kinds_of(group_key))
    return Grid(
        ["Name", "Kind", "Ruler or leader", "Attitude", "Detail"],
        rows,
        list(range(len(rows))),
        f"None yet: add a {kinds} here.",
        styles,
        caps=[26, 10, 20, 15, 0],
    )


# -- a neighbour --


def neighbour_facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    kind = neighbours.kind_of(neighbour)
    return [
        Fact("Kind", kind.name),
        Fact("Detail", neighbour.detail),
        Fact("Ruler or leader", neighbour.ruler or "(not named)"),
        Fact("Answers to", neighbours.answers_to_name(saga, neighbour) or "no one"),
        Fact("Realm", neighbour.realm or "none"),
        Fact("Book", kind.book or "core rules"),
    ]


def details_text(saga: Saga, record: Neighbour | Covenant | None) -> str:
    """A neighbour or covenant chosen in the Region, as markup: its name
    and kind, its attitude toward each player covenant and why, its
    summary and the favours owed."""
    if record is None:
        return "[$label]Choose a neighbour to see how it stands.[/]"
    kind = (
        neighbours.kind_of(record).name if isinstance(record, Neighbour) else "Covenant"
    )
    lines = [f"[b]{escape(record.name)}[/]   {escape(kind)} · {escape(record.detail)}"]
    for covenant in world.player_covenants(saga):
        if covenant is record:
            continue
        attitude = world.attitude_toward(record, covenant.id)
        seal = world.seal_markup(world.attitude_score(attitude))
        lines.append(
            f"Toward {escape(covenant.name)}: {seal}   "
            f"[$label]{escape(world.attitude_working(attitude))}[/]"
        )
    summary = record.summary.strip()
    if summary:
        lines.append(escape(summary.splitlines()[0]))
    open_favours = [f for f in record.favours if world.favour_is_open(f)]
    if open_favours:
        owed = "; ".join(f.what for f in open_favours)
        lines.append(f"[$label]Favours:[/] {escape(owed)}")
    return "\n".join(lines)


# -- a neighbour as a card (the desktop's Region) --


def card_subtitle(neighbour: Neighbour) -> str:
    """ "Lord · Sketch"."""
    return f"{kind_text(neighbour)} · {neighbour.detail}"


def card_facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """Its attitude toward the home covenant, and its ruler and liege
    when it has them."""
    words, _colour = _attitude_cell(saga, neighbour)
    facts = [Fact("Attitude", words)] if words else []
    if neighbour.ruler:
        facts.append(Fact("Ruler", neighbour.ruler))
    above = neighbours.answers_to_name(saga, neighbour)
    if above:
        facts.append(Fact("Answers to", above))
    return facts
