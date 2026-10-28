"""Open stories: the troupe's covenants' open Story Events, the stories
the saga has set in motion and not yet told. An experiment's story event
and a Disaster's covenant story write one (DE pp. 275-276: such a
story may come some time later), as does Suggest a Story
from a covenant's Hook, and the storyguide adds them by hand in the
covenant's Diary.

A story can say what it concerns (a character, a laboratory, the
covenant or the Region), and the Region lists every open one together.
It can be told (Resolved), or grow into a threat of the Region: Grow
into a Threat makes the threat, from the story's words, and marks the
story Grown, naming the threat.

Pattern: State, as a Story Event's status (Open, Resolved, Grown into a
threat), on the Diary entry the covenant already keeps rather than a
record of its own; what it concerns is an id reference ("characters:<id>")
resolved when shown, as a Ref's kind and id are."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import diaries, neighbours, threats, world
from .commands import Form, SectionOps, notes
from .form_spec import DialogField
from .grids import Grid
from .markup import escape
from .models import (
    SEASONS,
    STORY_EVENT,
    STORY_EVENT_STATUSES,
    Character,
    Covenant,
    CovenantDiaryEntry,
    Laboratory,
    Link,
    Saga,
)
from .references import Fact, refs

OPEN, RESOLVED, GROWN = STORY_EVENT_STATUSES

#: What a story concerns when it is the Region's.
REGION = "region"

GROW_TITLE = "Grow into a Threat"


@dataclass(frozen=True)
class Story:
    """An open story: the covenant whose Diary keeps it, and its entry's
    place there."""

    covenant: Covenant
    index: int

    @property
    def entry(self) -> CovenantDiaryEntry:
        return self.covenant.diary[self.index]


def is_open(entry: CovenantDiaryEntry) -> bool:
    return entry.category == STORY_EVENT and (entry.status or OPEN) == OPEN


def stories(saga: Saga) -> list[Story]:
    """Every open story of the troupe's covenants, oldest first."""
    found = [
        Story(covenant, index)
        for covenant in world.player_covenants(saga)
        for index, entry in enumerate(covenant.diary)
        if is_open(entry)
    ]
    found.sort(key=lambda s: (s.entry.year, _season(s.entry.season)))
    return found


def _season(season: str) -> int:
    return SEASONS.index(season) if season in SEASONS else 0


# -- what it concerns --


def concerns_of(record: Character | Laboratory) -> str:
    """The `concerns` value naming `record`."""
    kind = "characters" if isinstance(record, Character) else "laboratories"
    return f"{kind}:{record.id}"


def concerned(saga: Saga, entry: CovenantDiaryEntry) -> Character | Laboratory | None:
    """The character or laboratory a story concerns (None for the
    covenant, the Region, or one since deleted)."""
    kind, _, record_id = entry.concerns.partition(":")
    if kind == "characters":
        return saga.character(record_id)
    if kind == "laboratories":
        return saga.laboratory(record_id)
    return None


def concerns_text(saga: Saga, covenant: Covenant, entry: CovenantDiaryEntry) -> str:
    """ "Aurelia", "the Region", or the covenant's name."""
    if entry.concerns == REGION:
        return "The Region"
    found = concerned(saga, entry)
    return found.name if found is not None else covenant.name


def concerns_options(saga: Saga, covenant: Covenant) -> list[tuple[str, str]]:
    """What a covenant's story can concern: the covenant, the Region, and
    its characters and laboratories."""
    return [
        (f"The covenant ({escape(covenant.name)})", ""),
        ("The Region", REGION),
        *(
            (escape(c.name), concerns_of(c))
            for c in saga.characters
            if c.covenant_id == covenant.id
        ),
        *(
            (escape(lab.name), concerns_of(lab))
            for lab in saga.laboratories
            if lab.covenant_id == covenant.id
        ),
    ]


def facts(saga: Saga, record: Any) -> list[Fact]:
    """A character's or laboratory's open stories, for its Connections:
    each names the covenant whose Diary keeps it."""
    if not isinstance(record, (Character, Laboratory)):
        return []
    found = [s for s in stories(saga) if concerned(saga, s.entry) is record]
    if not found:
        return []
    keeping = list({id(s.covenant): s.covenant for s in found}.values())
    return [
        Fact(
            "Open stories",
            "; ".join(s.entry.name or "(unnamed)" for s in found)
            + f" ({', '.join(c.name for c in keeping)} Diary)",
            refs(*keeping),
        )
    ]


# -- the Region's list --


def title(saga: Saga) -> str:
    return f"Open Stories ({len(stories(saga))})"


def grid(saga: Saga) -> Grid:
    """Each open story: what it concerns, the covenant keeping it, and
    the season it arose."""
    rows = [
        [
            s.entry.name or "(unnamed)",
            concerns_text(saga, s.covenant, s.entry),
            s.covenant.name,
            f"{s.entry.season} {s.entry.year}",
        ]
        for s in stories(saga)
    ]
    return Grid(
        ["Story", "Concerns", "Covenant", "Arose"],
        rows,
        list(range(len(rows))),
        "No open stories: an experiment's story event, a Disaster's covenant "
        "story or Suggest a Story writes one in a covenant's Diary.",
        caps=[34, 20, 22, 0],
    )


def text(saga: Saga, row: int) -> str:
    """The story at `row` in full, for the desktop's inspector and the
    terminal's details panel; "" for no such row."""
    every = stories(saga)
    if not 0 <= row < len(every):
        return ""
    story = every[row]
    entry = story.entry
    lines = [
        f"[b]{escape(entry.name or '(unnamed)')}[/]",
        f"[$label]Concerns:[/] {escape(concerns_text(saga, story.covenant, entry))}",
        f"[$label]Arose:[/] {escape(entry.season)} {entry.year}, in "
        f"{escape(story.covenant.name)}'s Diary",
    ]
    if entry.revisit_year is not None:
        lines.append(f"[$label]Revisit:[/] {entry.revisit_year}")
    if entry.details.strip():
        lines.append(escape(entry.details.strip()))
    return "\n".join(lines)


def ops(saga: Saga, edit: Any) -> SectionOps:
    """The Region's Open Stories: Edit opens the story's Diary entry
    (`edit(covenant)` is that covenant's Diary ops)."""

    def edit_row(row: int) -> Any:
        story = stories(saga)[row]
        return edit(story.covenant).edit(story.index)

    return SectionOps(
        edit=edit_row,
        rows=lambda: [s.entry.name or "(unnamed)" for s in stories(saga)],
    )


# -- growing into a threat --


def grow_form(saga: Saga, row: int) -> Form:
    """Grow into a Threat on the Region's chosen open story: a threat of
    the Region named for it, with its antagonist and how it moves, its
    summary the story's words; the story is marked Grown, naming it, and
    the threat's Diary says where it came from. Its stages are added on
    its page."""
    story = stories(saga)[row]
    entry = story.entry

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "name",
                "Threat",
                "text",
                entry.name,
                required=True,
                placeholder="e.g. The Salamander's Hunger",
            ),
            *threats.fields(saga, None)[:2],
            DialogField(
                "dormant",
                "Begin it now",
                "select",
                "now",
                options=[("Now", "now"), ("Later: dormant until begun", "later")],
                required=True,
            ),
        ]

    def apply(values: dict[str, Any]) -> list[str]:
        threat = grow(saga, story, values)
        return notes(
            escape(
                f"{threat.name} is a threat of the Region: add its stages on its page."
            )
        )

    return Form(
        GROW_TITLE,
        fields,
        apply,
        save_label="Grow",
        help_id="grow-story",
    )


def grow(saga: Saga, story: Story, values: dict[str, Any]) -> Any:
    """Make the threat `story` grows into, from the form's values, and
    mark the story Grown. Returns the threat."""
    entry = story.entry
    threat = neighbours.add(saga, threats.THREAT, values["name"].strip())
    threat.summary = entry.details.strip() or entry.name
    threat.details["antagonist"] = (values.get("antagonist") or "").strip()
    threat.details["moves"] = values.get("moves") or threats.MOVES[0]
    if values.get("dormant") == "later":
        threat.details[threats.DORMANT] = True
    threat.links.append(
        Link("covenants", story.covenant.id, f"Grew from its story: {entry.name}")
    )
    entry.status = GROWN
    entry.threat_id = threat.id
    diaries.write(
        saga.current_year,
        saga.current_season,
        threat.name,
        f"Grew from {story.covenant.name}'s story, {entry.name} "
        f"({entry.season} {entry.year})",
        neighbours=[threat],
    )
    return threat
