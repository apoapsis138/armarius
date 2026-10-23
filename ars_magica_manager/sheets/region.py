"""What the Region and a neighbour's sheet show, worked out from the
saga's records for either front-end: the Region's facts, a list per
group of neighbours and the covenants the troupe doesn't play, and a
neighbour's own facts and details."""

from __future__ import annotations

from .. import (
    arms,
    connections,
    neighbour_filter,
    neighbours,
    places,
    references,
    threats,
    tribunal_packages,
    tribunals,
    world,
)
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Neighbour, Saga, Tribunal
from ..references import Fact
from ..rules import sites


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


def facts(saga: Saga, showing: bool = True) -> list[Fact]:
    """The home covenant, its Tribunal, the neighbours and how they
    stand, and when the Tribunal next meets; then what the lists are
    narrowed to, unless `showing` is False (a front-end whose filter
    controls say so themselves)."""
    home = neighbours.home(saga)
    tribunal = tribunals.of(saga, home) if home is not None else None
    held = [n for n in saga.neighbours if neighbours.kind_of(n).attitude]
    scores = [neighbours.score(saga, n) for n in held]
    warm = sum(1 for s in scores if s is not None and s > 0)
    wary = sum(1 for s in scores if s is not None and s < 0)
    count = len(held)
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
        *(_filter_fact(saga) if showing else []),
    ]


def _filter_fact(saga: Saga) -> list[Fact]:
    """What the lists are narrowed to, while they are."""
    wanted = neighbour_filter.current(saga)
    if not wanted.active:
        return []
    return [Fact("Showing", neighbour_filter.describe(saga, wanted))]


def _soonest(saga: Saga) -> tuple[Neighbour, str] | None:
    due = [
        (found, n)
        for n in saga.neighbours
        if n.kind == "threat" and (found := threats.due(saga, n)) is not None
    ]
    if not due:
        return None
    (_when, words), threat = min(due, key=lambda pair: pair[0])
    return threat, words


def threat_due(saga: Saga) -> str:
    """The threat whose next stage comes soonest: "The Hollow Crown,
    Winter 1220"; "" if none has a dated stage to come."""
    soonest = _soonest(saga)
    return soonest[1] if soonest else ""


def due_threat(saga: Saga) -> Neighbour | None:
    """The threat Threat due names, to open from the Region."""
    soonest = _soonest(saga)
    return soonest[0] if soonest else None


def neighbours_title(saga: Saga) -> str:
    """ "Neighbours (6)": those that hold an attitude, places aside."""
    held = [n for n in saga.neighbours if neighbours.kind_of(n).attitude]
    return f"Neighbours ({len(held)})"


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
    """Its kind as the lists show it: "Lord"; "Ruin" for a ruined
    covenant's site, "Dormant" for a threat not yet begun."""
    if places.is_ruin(neighbour):
        return "Ruin"
    if threats.is_dormant(neighbour):
        return "Dormant"
    return neighbours.kind_of(neighbour).name


def group_title(saga: Saga, group_key: str) -> str:
    """ "Lords and Towns (102)", or "(12 of 102)" while filtered."""
    group = neighbours.group(group_key)
    total = len(neighbours.members(saga, group_key))
    if not neighbour_filter.current(saga).active:
        return f"{group.title} ({total})"
    shown = len(neighbour_filter.shown(saga, group_key))
    return f"{group.title} ({shown} of {total})"


def _empty(saga: Saga, words: str) -> str:
    """A list's words when it shows nothing: `words`, or that the
    filter lets none through."""
    if neighbour_filter.current(saga).active:
        return "None match the filter."
    return words


def places_grid(saga: Saga) -> Grid:
    """The places: where each is, its aura, its regio and the gazetteer."""
    rows = []
    for found in neighbour_filter.shown(saga, "places"):
        levels = len(sites.levels(found))
        rows.append(
            [
                found.name,
                places.where_text(saga, found.place_id, found.place_level),
                places.aura_text(found),
                f"{levels} level{'' if levels == 1 else 's'}" if levels else "",
                found.details.get("status") or "",
            ]
        )
    return Grid(
        ["Name", "Inside", "Aura", "Regio", "Status"],
        rows,
        list(range(len(rows))),
        _empty(saga, "None yet: add a forest, a ruin or a regio here."),
        caps=[26, 26, 10, 9, 0],
    )


def group_grid(saga: Saga, group_key: str) -> Grid:
    """The group's neighbours: kind, ruler, attitude toward the home
    covenant and detail."""
    if group_key == "places":
        return places_grid(saga)
    rows = []
    styles: dict[tuple[int, int], str] = {}
    members = neighbour_filter.shown(saga, group_key)
    for index, neighbour in enumerate(members):
        words, colour = _attitude_cell(saga, neighbour)
        if colour:
            styles[(index, 3)] = colour
        rows.append(
            [
                neighbour.name,
                kind_text(neighbour),
                references.ruler_name(saga, neighbour),
                words,
                neighbour.detail,
            ]
        )
    kinds = ", ".join(k.name.lower() for k in neighbours.kinds_of(group_key))
    return Grid(
        ["Name", "Kind", "Ruler or leader", "Attitude", "Detail"],
        rows,
        list(range(len(rows))),
        _empty(saga, f"None yet: add a {kinds} here."),
        styles,
        caps=[26, 10, 20, 15, 0],
    )


# -- a neighbour --


def ruler_fact(saga: Saga, neighbour: Neighbour, label: str, blank: str) -> Fact:
    """Its ruler or leader, linked to their record when they have one."""
    name = references.ruler_name(saga, neighbour)
    found = references.ruler(saga, neighbour)
    return Fact(label, name or blank, references.refs(found))


def answers_to_fact(saga: Saga, neighbour: Neighbour, blank: str) -> Fact:
    above = saga.neighbour(neighbour.answers_to)
    return Fact(
        "Answers to",
        above.name if above is not None else blank,
        references.refs(above),
    )


def inside_fact(saga: Saga, neighbour: Neighbour, blank: str) -> Fact:
    """The places it sits in, outward, each linked."""
    return Fact(
        "Inside",
        places.inside_text(saga, neighbour) or blank,
        references.refs(*places.inside_of(saga, neighbour)),
    )


def below_fact(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """Who answers to it (a lord's vassals, a faction's members), each
    linked; none while no one does."""
    below = neighbours.vassals(saga, neighbour)
    if not below:
        return []
    return [
        Fact(
            "Answer to it",
            ", ".join(n.name for n in below),
            references.refs(*below),
        )
    ]


def neighbour_facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    kind = neighbours.kind_of(neighbour)
    where = places.where_text(saga, neighbour.place_id, neighbour.place_level)
    if not kind.attitude:
        return [
            Fact("Kind", kind.name),
            Fact("Realm", neighbour.realm or "none"),
            inside_fact(saga, neighbour, "nowhere entered"),
            Fact("Book", kind.book or "core rules"),
            *connections.links_back(saga, neighbour),
        ]
    place = sites.place(saga, neighbour.place_id)
    return [
        Fact("Kind", kind.name),
        Fact("Detail", neighbour.detail),
        ruler_fact(saga, neighbour, "Ruler or leader", "(not named)"),
        answers_to_fact(saga, neighbour, "no one"),
        Fact("Realm", neighbour.realm or "none"),
        Fact("Book", kind.book or "core rules"),
        *([Fact("Place", where, references.refs(place))] if where else []),
        *below_fact(saga, neighbour),
        *connections.rules_facts(saga, neighbour),
        *connections.links_back(saga, neighbour),
    ]


def details_text(saga: Saga, record: Neighbour | Covenant | None) -> str:
    """A neighbour or covenant chosen in the Region, as markup: its name
    and kind, its attitude toward each player covenant and why, its
    summary and the favours owed."""
    if record is None:
        return "[$label]Choose a neighbour to see how it stands.[/]"
    if sites.is_place(record):
        assert isinstance(record, Neighbour)
        lines = [f"[b]{escape(record.name)}[/]   Place · {places.aura_text(record)}"]
        inside = places.inside_text(saga, record)
        if inside:
            lines.append(f"[$label]Inside:[/] {escape(inside)}")
        lines += [
            f"[$label]{escape(f.label)}:[/] {escape(f.value)}"
            for f in places.facts(saga, record)
            if f.value and f.label in ("Regio", "Here")
        ]
        summary = record.summary.strip()
        if summary:
            lines.append(escape(summary.splitlines()[0]))
        return "\n".join(lines)
    kind = (
        neighbours.kind_of(record).name if isinstance(record, Neighbour) else "Covenant"
    )
    lines = [f"[b]{escape(record.name)}[/]   {escape(kind)} · {escape(record.detail)}"]
    borne = arms.arms_of(record)
    if borne is not None:
        if borne.motto:
            lines.append(f"[$label]Motto:[/] [i]{escape(borne.motto)}[/]")
        lines.append(f"[$label]Arms:[/] {escape(arms.blazon(borne))}")
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
    """ "Lord · Sketch"; a place's aura, "Place · Magic 5" ("Ruined
    covenant · Magic 5")."""
    if sites.is_place(neighbour):
        what = "Ruined covenant" if places.is_ruin(neighbour) else "Place"
        return f"{what} · {places.aura_text(neighbour)}"
    return f"{kind_text(neighbour)} · {neighbour.detail}"


def card_facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """Its attitude toward the home covenant, and its ruler and liege
    when it has them."""
    if sites.is_place(neighbour):
        inside = inside_fact(saga, neighbour, "")
        return ([inside] if inside.value else []) + [
            f
            for f in places.facts(saga, neighbour)
            if f.value and f.label in ("Regio", "Claimed by")
        ]
    words, _colour = _attitude_cell(saga, neighbour)
    facts = [Fact("Attitude", words)] if words else []
    ruler = ruler_fact(saga, neighbour, "Ruler", "")
    if ruler.value:
        facts.append(ruler)
    above = answers_to_fact(saga, neighbour, "")
    if above.value:
        facts.append(above)
    return facts


#: How many of a group's neighbours the desktop's Region shows as cards
#: until the rest are asked for: a Tribunal's pack brings hundreds, and
#: drawing a card for each made the saga's page slow to open.
CARDS_SHOWN = 12


def cards_shown(members: list[Neighbour], every: bool) -> tuple[list[Neighbour], int]:
    """The group's neighbours to draw as cards (all of them when `every`),
    and how many more are held back."""
    if every or len(members) <= CARDS_SHOWN:
        return members, 0
    return members[:CARDS_SHOWN], len(members) - CARDS_SHOWN


def more_cards(group_key: str, held_back: int) -> tuple[str, str]:
    """The card that shows the rest of a group: its title and the line
    under it ("Show 90 more", "The rest of Lords and Towns")."""
    return f"Show {held_back} more", f"The rest of {neighbours.group(group_key).title}"
