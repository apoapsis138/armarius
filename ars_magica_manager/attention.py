"""Needs You: what in the saga is waiting on the storyguide, asked of
every part of the saga when the list is shown rather than kept as
notifications, so an item leaves the list as soon as it is dealt with.

Each source is a function that returns its items; the list calls them
all, in the order registered. The troupe's covenants give their open
stories, and first those whose Revisit year has come; the creations
experiments changed, their experimental effects not yet described (a
spell, through a magus who knows it; an enchanted item's effect, through
its holder; a familiar's bond power); and the threats their dated stages
still Pending after their season has passed.

Each item names the record where it is dealt with (a references.Ref),
which both front-ends open.

Pattern: Registry, reduced to a list of functions (SOURCES) that each
answer the same question, as Ahead's sources do; register() adds one."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from . import open_stories, references, story_chapters, threats
from .commands import Act, Command, Go, Refuse, SectionOps
from .grids import Grid
from .markup import escape
from .models import (
    SEASONS,
    Character,
    ExperimentalEffect,
    Saga,
    Spell,
    season_order,
)
from .references import Fact, Ref
from .rules import experiment

#: What each source's items show as, in the list's first column.
REVISIT = "Revisit"
STORY = "Open story"
EFFECT = "Describe"
OVERDUE = "Overdue"

OPEN_TITLE = "Open"


@dataclass(frozen=True)
class Item:
    """One thing waiting on the storyguide: what kind (one of the names
    above), what it is, the record it is dealt with on and where there,
    a line or two on what to do (plain text), and Take Up the Tale's
    first step for a story or a threat (None for neither)."""

    need: str
    title: str
    ref: Ref | None
    where: str
    detail: str = ""
    take_up: Callable[[], Command] | None = None


Source = Callable[[Saga], list[Item]]

#: Every source the list asks, in the order registered.
SOURCES: list[Source] = []


def register(source: Source) -> Source:
    SOURCES.append(source)
    return source


# -- the sources --


def _revisit_due(saga: Saga, story: open_stories.Story) -> bool:
    year = story.entry.revisit_year
    return year is not None and year <= saga.current_year


def _story(saga: Saga, story: open_stories.Story, need: str) -> Item:
    entry = story.entry
    concerns = open_stories.concerns_text(saga, story.covenant, entry)
    detail = f"Arose {entry.season} {entry.year}; concerns {concerns}."
    if need == REVISIT:
        detail += f" Its Revisit year, {entry.revisit_year}, has come."
    return Item(
        need,
        entry.name or "(unnamed)",
        references.ref(story.covenant),
        f"{story.covenant.name}'s Diary",
        detail + " Take up the tale, tell it (Resolved), grow it into a threat, "
        "or change its Revisit.",
        lambda: story_chapters.take_up_story(saga, story.covenant, entry),
    )


@register
def _revisits(saga: Saga) -> list[Item]:
    """Open stories whose Revisit year has come."""
    return [
        _story(saga, s, REVISIT)
        for s in open_stories.stories(saga)
        if _revisit_due(saga, s)
    ]


@register
def _stories(saga: Saga) -> list[Item]:
    """The other open stories, oldest first."""
    return [
        _story(saga, s, STORY)
        for s in open_stories.stories(saga)
        if not _revisit_due(saga, s)
    ]


def _undescribed(effects: list[ExperimentalEffect]) -> list[ExperimentalEffect]:
    return [e for e in effects if experiment.needs_description(e)]


def _effects_item(
    undescribed: list[ExperimentalEffect],
    title: str,
    ref: Ref | None,
    where: str,
    how: str,
) -> Item:
    count = len(undescribed)
    return Item(
        EFFECT,
        f"{title}: {count} experimental effect{'' if count == 1 else 's'}",
        ref,
        where,
        f"{how}, and say what each is: "
        + "; ".join(experiment.describe(e) for e in undescribed)
        + ".",
    )


def _knower(saga: Saga, spell: Spell) -> Character | None:
    """The magus whose sheet opens `spell`: its inventor, else the first
    who knows it."""
    for character in saga.characters:
        if any(s is spell for s in character.invented_spells):
            return character
    return next(
        (
            c
            for c in saga.characters
            if any(k.spell_id == spell.id for k in c.spells_known)
        ),
        None,
    )


@register
def _spells(saga: Saga) -> list[Item]:
    """The saga's own and invented spells with an effect to describe,
    through a magus who knows them (none knowing it: nowhere to open)."""
    found = []
    spells = [*saga.spells, *(s for c in saga.characters for s in c.invented_spells)]
    for spell in spells:
        undescribed = _undescribed(spell.experimental_effects)
        magus = _knower(saga, spell) if undescribed else None
        if magus is None:
            continue
        found.append(
            _effects_item(
                undescribed,
                spell.name,
                references.ref(magus),
                f"{magus.name}'s Known Spells",
                "Edit the spell's Mastery",
            )
        )
    return found


#: An enchanted item's holder kind, as a Ref's.
_HOLDERS = {
    "character": "characters",
    "laboratory": "laboratories",
    "covenant": "covenants",
}


@register
def _devices(saga: Saga) -> list[Item]:
    """Enchanted items' effects with an effect to describe, through the
    item's holder, else its maker."""
    found = []
    for device in saga.enchanted_devices:
        kind = _HOLDERS.get(device.holder_kind or "")
        owner = references.find(saga, kind, device.holder_id) if kind else None
        owner = owner or saga.character(device.maker_id or "")
        for effect in device.effects:
            undescribed = _undescribed(effect.experimental_effects)
            if not undescribed:
                continue
            found.append(
                _effects_item(
                    undescribed,
                    f"{device.name}, {effect.name or 'an effect'}",
                    references.ref(owner),
                    f"{owner.name}'s Enchanted Items"
                    if owner is not None
                    else "No holder",
                    "Edit the item's effect",
                )
            )
    return found


@register
def _bond_powers(saga: Saga) -> list[Item]:
    """Familiars' bond powers with an effect to describe."""
    found = []
    for familiar in saga.familiars:
        for power in familiar.bond_powers:
            undescribed = _undescribed(power.experimental_effects)
            if undescribed:
                found.append(
                    _effects_item(
                        undescribed,
                        f"{familiar.name}, {power.name or 'a bond power'}",
                        references.ref(familiar),
                        f"{familiar.name}'s Bond Powers",
                        "Edit the power",
                    )
                )
    return found


@register
def _overdue(saga: Saga) -> list[Item]:
    """Dated threat stages still Pending after their season: say whether
    each happened, or delay the threat."""
    now = season_order(season=saga.current_season, year=saga.current_year)
    found = []
    for threat in saga.neighbours:
        if (
            threat.kind != threats.THREAT
            or not threats.by_date(threat)
            or threats.is_dormant(threat)
        ):
            continue
        for stage in threats.stages(threat):
            if (stage.get("outcome") or threats.PENDING) != threats.PENDING:
                continue
            when = threats.comes(threat, stage)
            if when is None or when >= now:
                continue
            year, index = divmod(when, len(SEASONS))
            found.append(
                Item(
                    OVERDUE,
                    f"{threat.name}: {stage['title']}",
                    references.ref(threat),
                    "Its Stages",
                    f"Due {SEASONS[index]} {year} and still Pending: record "
                    "what became of it (and what the troupe did), or Delay or "
                    "Hasten the threat.",
                    lambda threat=threat: story_chapters.take_up_threat(saga, threat),
                )
            )
    return found


# -- asking --


def items(saga: Saga) -> list[Item]:
    """Everything waiting on the storyguide, source by source."""
    return [item for source in SOURCES for item in source(saga)]


def title(saga: Saga) -> str:
    return f"Needs You ({len(items(saga))})"


def fact(saga: Saga) -> Fact:
    """The Seasons top panel's count."""
    count = len(items(saga))
    return Fact("Needs you", str(count) if count else "nothing")


def grid(saga: Saga) -> Grid:
    """Each item: what it is, what it needs, and where it is dealt with;
    an overdue stage or a story to revisit is marked."""
    found = items(saga)
    styles = {
        (row, 1): "$text-warning"
        for row, item in enumerate(found)
        if item.need in (OVERDUE, REVISIT)
    }
    return Grid(
        ["What", "Needs", "Where"],
        [[item.title, item.need, item.where] for item in found],
        list(range(len(found))),
        "Nothing needs you: open stories, experimental effects to describe "
        "and overdue threat stages show here.",
        styles,
        caps=[52, 10, 0],
        stretch=1,
    )


def text(saga: Saga, row: int) -> str:
    """The item at `row` in full (markup), for the details panel and the
    desktop's inspector; "" for no such row."""
    found = items(saga)
    if not 0 <= row < len(found):
        return ""
    item = found[row]
    lines = [
        f"[b]{escape(item.title)}[/]",
        f"[$label]{escape(item.need)}, on[/] {escape(item.where)}",
    ]
    if item.detail:
        lines.append(escape(item.detail))
    if item.ref is not None:
        lines.append(f"[$label]Open opens {escape(item.ref.name)}.[/]")
    return "\n".join(lines)


def ops(saga: Saga) -> SectionOps:
    """Needs You's one verb: Edit opens the chosen item's record (the
    steps end in a commands.Go, which the front-end follows)."""

    def open_row(row: int) -> Command:
        found = items(saga)
        ref = found[row].ref if 0 <= row < len(found) else None
        if ref is None:
            return Refuse(OPEN_TITLE, "Nothing in the saga keeps this one to open.")
        return Act(lambda: Go(ref))

    return SectionOps(
        edit=open_row,
        rows=lambda: [item.title for item in items(saga)],
    )
