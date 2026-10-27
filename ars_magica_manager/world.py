"""The pieces every record of the saga's world shares, worked out: whether
a record takes part in play, its attitude toward a player covenant, the
favours still open, and the links that point at a record."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from .markup import escape
from .models import (
    ATTITUDE_RANGE,
    DETAIL_LEVELS,
    FULL,
    Attitude,
    Character,
    Covenant,
    Creature,
    Favour,
    Link,
    MysteryCult,
    Neighbour,
    Saga,
)

#: A Reputation's kinds (the core book's, and the supplements that add
#: Academic and Ecclesiastical), offered when one is entered.
REPUTATION_TYPES: tuple[str, ...] = (
    "Hermetic",
    "Local",
    "Noble",
    "Academic",
    "Ecclesiastical",
    "Infernal",
)

#: The word for each attitude score, from -3 to +3.
ATTITUDE_WORDS: dict[int, str] = {
    -3: "Hostile",
    -2: "Unfriendly",
    -1: "Wary",
    0: "Neutral",
    1: "Warm",
    2: "Friendly",
    3: "Allied",
}

#: The seal drawn for an attitude, before its score and word.
SEAL_GLYPH = "◉"
#: The mark before a troupe covenant's name in a list.
TROUPE_GLYPH = "✦"


def troupe_first(covenants: list[Covenant]) -> list[Covenant]:
    """`covenants`, the troupe's first, each group in its own order."""
    return sorted(covenants, key=lambda c: not c.played)


def marked_name(covenant: Covenant) -> str:
    """A covenant's name as a list shows it: a troupe covenant's after
    its mark."""
    return f"{TROUPE_GLYPH} {covenant.name}" if covenant.played else covenant.name


def takes_part_in_play(record: Character | Covenant) -> bool:
    """Whether `record` is played season by season: advanced, aged, planned
    for, and kept in upkeep and creation budgets. A Line or Sketch record
    is part of the world but not of play."""
    return record.detail == FULL


def promoted(detail: str) -> str | None:
    """The detail level Promote moves a record to, or None at Full."""
    index = DETAIL_LEVELS.index(detail)
    return DETAIL_LEVELS[index + 1] if index + 1 < len(DETAIL_LEVELS) else None


def demoted(detail: str) -> str | None:
    """The detail level Demote moves a record to, or None at Line."""
    index = DETAIL_LEVELS.index(detail)
    return DETAIL_LEVELS[index - 1] if index else None


def player_covenants(saga: Saga) -> list[Covenant]:
    """The covenants the troupe plays, which attitudes point at."""
    return [c for c in saga.covenants if c.played]


def attitude_toward(
    record: Character | Covenant | Neighbour | MysteryCult, covenant_id: str
) -> Attitude | None:
    """`record`'s attitude toward the player covenant `covenant_id`, or None
    when none is set."""
    attitudes: list[Attitude] = getattr(record, "attitudes", [])
    return next((a for a in attitudes if a.covenant_id == covenant_id), None)


def attitude_score(attitude: Attitude | None) -> int:
    """The current score: the start plus every reason since, kept within
    -3 to +3. No attitude counts as Neutral."""
    if attitude is None:
        return 0
    low, high = ATTITUDE_RANGE
    total = attitude.start + sum(r.change for r in attitude.reasons)
    return max(low, min(high, total))


def attitude_word(score: int) -> str:
    return ATTITUDE_WORDS[max(ATTITUDE_RANGE[0], min(ATTITUDE_RANGE[1], score))]


def attitude_colour(score: int) -> str:
    """The theme colour an attitude is drawn in (both front-ends' palettes
    name it)."""
    if score <= -2:
        return "text-error"
    if score == -1:
        return "text-warning"
    if score == 0:
        return "label"
    return "text-success"


def signed(score: int) -> str:
    """A score as written on a seal: −1, 0, +2 (a true minus sign)."""
    return f"{score:+d}".replace("-", "−") if score else "0"


def seal_markup(score: int) -> str:
    """An attitude as one line of markup: "◉ −1 Wary" in its colour."""
    colour = attitude_colour(score)
    return f"[${colour}]{SEAL_GLYPH} {signed(score)} {attitude_word(score)}[/]"


def attitude_working(attitude: Attitude | None) -> str:
    """How the score was reached, as plain text: "Started at 0; +1 Helped
    at the ford; −2 Took the vis source"."""
    if attitude is None:
        return "No attitude set: Neutral."
    parts = [f"Started at {signed(attitude.start)}"]
    parts += [f"{signed(r.change)} {r.what}" for r in attitude.reasons]
    return "; ".join(parts)


def when_text(year: int | None, season: str) -> str:
    """ "Spring 1221", "1221", or "" when there is no year."""
    if year is None:
        return ""
    return f"{season} {year}" if season else str(year)


def favour_is_open(favour: Favour) -> bool:
    return favour.repaid_year is None


def favour_rows(favours: list[Favour]) -> list[tuple[int | None, str]]:
    """Favours as (index, "Who owes whom: what (since ...)") rows, the open
    ones marked."""
    rows: list[tuple[int | None, str]] = []
    for index, favour in enumerate(favours):
        who = " owes ".join(p for p in (favour.owed_by, favour.owed_to) if p)
        since = when_text(favour.year, favour.season)
        text = escape(f"{who}: {favour.what}" if who else favour.what)
        if since:
            text += f" (since {since})"
        if not favour_is_open(favour):
            repaid = when_text(favour.repaid_year, favour.repaid_season)
            text = f"[$label]{text}, repaid {repaid}[/]"
        rows.append((index, text))
    return rows


def _records(saga: Saga) -> Iterator[Character | Covenant | Neighbour | Creature]:
    yield from saga.covenants
    yield from saga.characters
    yield from saga.neighbours
    yield from saga.creatures


def link_target(saga: Saga, link: Link) -> Any | None:
    """The record `link` points at, or None if it is gone."""
    if link.kind == "possessions":
        for covenant in saga.covenants:
            for possession in covenant.possessions:
                if possession.id == link.target_id:
                    return possession
        return None
    records = getattr(saga, link.kind, None)
    if not isinstance(records, list):
        return None
    return next((r for r in records if getattr(r, "id", None) == link.target_id), None)


def link_label(saga: Saga, link: Link) -> str:
    """The linked record's name, with the note (markup)."""
    target = link_target(saga, link)
    name = escape(getattr(target, "name", "")) if target else "[$label](gone)[/]"
    return f"{name}: {escape(link.note)}" if link.note else name


def links_to(saga: Saga, kind: str, target_id: str) -> list[tuple[Any, Link]]:
    """The links back: each (record, link) whose link points at the record
    `target_id` of `kind`."""
    return [
        (record, link)
        for record in _records(saga)
        for link in record.links
        if link.kind == kind and link.target_id == target_id
    ]


# -- a covenant's magi and votes --


def covenant_magi(saga: Saga, covenant: Covenant) -> list[Character]:
    """The named magi whose covenant is `covenant`, at any detail."""
    return [
        c for c in saga.characters if c.covenant_id == covenant.id and c.type == "magus"
    ]


def votes(saga: Saga, covenant: Covenant) -> int:
    """A covenant's Tribunal votes: one for each of its magi, named or not.
    Proxies are carried at each meeting, not here."""
    return len(covenant_magi(saga, covenant)) + covenant.unnamed_magi


def votes_text(saga: Saga, covenant: Covenant) -> str:
    """ "5 (3 named, 2 unnamed)", or just "3" when every magus is named."""
    named = len(covenant_magi(saga, covenant))
    total = named + covenant.unnamed_magi
    if not covenant.unnamed_magi:
        return str(total)
    return f"{total} ({named} named, {covenant.unnamed_magi} unnamed)"


def what_matters_rows(what_matters: str) -> list[tuple[str, str]]:
    """What Matters as (label, words) entries, one a line; a line "Vis:
    Vim 6 a year" has the label "Vis", any other none."""
    rows: list[tuple[str, str]] = []
    for line in what_matters.splitlines():
        line = line.strip().lstrip("•-* ").strip()
        if not line:
            continue
        label, sep, words = line.partition(":")
        if sep and words.strip() and len(label.split()) <= 3:
            rows.append((label.strip(), words.strip()))
        else:
            rows.append(("", line))
    return rows
