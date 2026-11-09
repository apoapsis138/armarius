"""A story's chapters: what the troupe did each time it took up a tale.

A chapter is its own dated entry in the covenant's Diary (category
Chapter), so the Diary stays a record by season; it names its story by
the story's id (`story_id`), given to the story when it is first taken
up. Take Up the Tale writes one on an open story; resolving a story asks
for a last chapter, how it ended. A story grown into a threat is taken up
on the threat instead: its chapters go into the threat's Diary (marked
chapters) and each troupe covenant's (threats.write_chapter), as does
what the troupe did when a stage's outcome is recorded.

A story's thread reads its chapters, then the threat it grew into and
that threat's chapters; a threat's, the story it grew from first.

Pattern: an id reference resolved when shown, as a story already names
the threat it grew into (`threat_id`); Command chaining (commands.Then)
for Resolve's last chapter."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import place_events, sessions, threats, world
from .commands import Choice, Choose, Command, Form, Refuse, notes
from .form_spec import DialogField, pairs
from .markup import escape
from .models import (
    CHAPTER,
    SEASONS,
    STORY_EVENT,
    STORY_EVENT_STATUSES,
    Covenant,
    CovenantDiaryEntry,
    Neighbour,
    Saga,
    Session,
    season_order,
)
from .neighbour_lists import KindList, KindTab
from .references import Fact, refs
from .sections import DIARY_SECTION

OPEN, RESOLVED, GROWN = STORY_EVENT_STATUSES

TAKE_UP = "Take Up the Tale"
ENDING = "How the Tale Ended"


@dataclass(frozen=True)
class Chapter:
    """One chapter as a thread shows it: when, and what the troupe did."""

    year: int | None
    season: str
    words: str
    #: Who went, by id (a story's chapter; a threat's has none).
    cast: tuple[str, ...] = ()

    @property
    def when(self) -> str:
        return " ".join(str(p) for p in (self.season, self.year) if p)

    @property
    def order(self) -> int:
        return season_order(season=self.season, year=self.year or 0)


def is_story(entry: CovenantDiaryEntry) -> bool:
    return entry.category == STORY_EVENT


def is_open(entry: CovenantDiaryEntry) -> bool:
    return is_story(entry) and (entry.status or OPEN) == OPEN


def story_id(entry: CovenantDiaryEntry) -> str:
    """The story's id, given it now if it has none yet."""
    if not entry.id:
        entry.id = uuid.uuid4().hex[:12]
    return entry.id


# -- finding them --


def story_chapters(covenant: Covenant, entry: CovenantDiaryEntry) -> list[Chapter]:
    """The chapters of the story `entry`, oldest first."""
    if not entry.id:
        return []
    found = [
        Chapter(e.year, e.season, e.details.strip(), tuple(e.cast))
        for e in covenant.diary
        if e.category == CHAPTER and e.story_id == entry.id
    ]
    return sorted(found, key=lambda c: c.order)


def threat_chapters(threat: Neighbour) -> list[Chapter]:
    """The chapters in the threat's Diary, oldest first."""
    found = [
        Chapter(e.get("year"), e.get("season") or "", (e.get("text") or "").strip())
        for e in place_events.diary(threat)
        if e.get("chapter")
    ]
    return sorted(found, key=lambda c: c.order)


def grown_from(
    saga: Saga, threat: Neighbour
) -> tuple[Covenant, CovenantDiaryEntry] | None:
    """The covenant and story `threat` grew from, if it grew from one."""
    for covenant in saga.covenants:
        for entry in covenant.diary:
            if is_story(entry) and entry.threat_id == threat.id:
                return covenant, entry
    return None


def grew_into(saga: Saga, entry: CovenantDiaryEntry) -> Neighbour | None:
    """The threat a story grew into (None: it didn't, or the threat is
    gone)."""
    return saga.neighbour(entry.threat_id) if entry.threat_id else None


# -- the thread --


def _chapter_lines(chapters: list[Chapter], saga: Saga | None = None) -> list[str]:
    """Each chapter (markup): when, what the troupe did, and who went."""
    lines = []
    for c in chapters:
        line = f"[$label]{escape(c.when or 'Undated')}:[/] {escape(c.words)}"
        went = [x.name for i in c.cast if saga and (x := saga.character(i))]
        if went:
            line += f" [$label](went: {escape(', '.join(went))})[/]"
        lines.append(line)
    return lines


def story_thread(
    saga: Saga, covenant: Covenant, entry: CovenantDiaryEntry
) -> list[str]:
    """A story's thread (markup lines): its chapters, then the threat it
    grew into and the threat's chapters; [] for none."""
    lines = _chapter_lines(story_chapters(covenant, entry), saga)
    threat = grew_into(saga, entry)
    if threat is not None:
        lines.append(f"[$label]Grew into[/] [b]{escape(threat.name)}[/]")
        lines += _chapter_lines(threat_chapters(threat))
    if not lines:
        return []
    return ["[b]Chapters[/]", *lines]


def threat_thread(saga: Saga, threat: Neighbour, *, own: bool = True) -> list[str]:
    """A threat's thread (markup lines): the story it grew from and that
    story's chapters, then (`own`) its own; [] for none."""
    lines: list[str] = []
    origin = grown_from(saga, threat)
    if origin is not None:
        covenant, entry = origin
        lines.append(
            f"[$label]Grew from[/] [b]{escape(entry.name or '(unnamed)')}[/] "
            f"[$label]({escape(covenant.name)}'s Diary, {entry.season} "
            f"{entry.year})[/]"
        )
        lines += _chapter_lines(story_chapters(covenant, entry))
    if own:
        lines += _chapter_lines(threat_chapters(threat))
    if not lines:
        return []
    return ["[b]Chapters[/]", *lines]


def threat_header(saga: Saga, threat: Neighbour) -> str:
    """Above a threat's Diary: the story it grew from and that story's
    chapters, which come before the Diary's own (markup; "" for none)."""
    return "\n".join(threat_thread(saga, threat, own=False)[1:])


def threat_facts(saga: Saga, threat: Neighbour) -> list[Fact]:
    """A threat's top panel: the story it grew from, as a link to the
    covenant keeping it."""
    origin = grown_from(saga, threat)
    if origin is None:
        return []
    covenant, entry = origin
    return [
        Fact(
            "Grew from",
            f"{entry.name or '(unnamed)'} ({covenant.name}'s Diary)",
            refs(covenant),
        )
    ]


def facts(saga: Saga, record: Any) -> list[Fact]:
    """A covenant's Connections: the threats its stories grew into, each
    a link that opens it."""
    if not isinstance(record, Covenant):
        return []
    grown = [
        (entry, threat)
        for entry in record.diary
        if is_story(entry) and (threat := grew_into(saga, entry)) is not None
    ]
    if not grown:
        return []
    return [
        Fact(
            "Stories grown into threats",
            "; ".join(f"{e.name or '(unnamed)'}: {t.name}" for e, t in grown),
            refs(*(threat for _story, threat in grown)),
        )
    ]


# -- deleting a story --

KEEP, DROP = "keep", "drop"


def delete_story(covenant: Covenant, entry: CovenantDiaryEntry) -> Choose:
    """Delete a story that has chapters: keep them in the Diary (each
    then names a story since deleted), or delete them with it."""
    count = len(story_chapters(covenant, entry))
    name = escape(entry.name or "(unnamed)")

    def apply(choice: str) -> None:
        if choice == DROP:
            covenant.diary[:] = [
                e
                for e in covenant.diary
                if not (e.category == CHAPTER and e.story_id == entry.id)
            ]
        covenant.diary[:] = [e for e in covenant.diary if e is not entry]

    plural = "" if count == 1 else "s"
    return Choose(
        f"Delete {name}? It has {count} chapter{plural}",
        lambda: [
            Choice(f"Delete the story, keep its chapter{plural} in the Diary", KEEP),
            Choice(f"Delete the story and its chapter{plural}", DROP),
        ],
        apply,
    )


# -- writing them --


def _fields(
    saga: Saga, words_label: str, hint: str, *, cast: bool = True
) -> list[DialogField]:
    return [
        DialogField("year", "Year", "int", saga.current_year, required=True),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season,
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField("words", words_label, "area", "", required=True, hint=hint),
        *(cast_fields(saga) if cast else []),
    ]


#: The key of a "Went" tick, before the character's id.
WENT = "went_"


def session_at_hand(saga: Saga) -> Session | None:
    """The evening a chapter is being written at: the next planned
    Session, else the last played."""
    return sessions.next_planned(saga) or sessions.last_played(saga)


def cast_fields(saga: Saga) -> list[DialogField]:
    """Who went (a tick per troupe character, filled in from who plays
    whom at the Session at hand) and how many days the chapter took."""
    session = session_at_hand(saga)
    played = {c.character_id for c in session.castings} if session else set()
    offered = [
        c
        for c in saga.characters
        if c.id in played
        or c.covenant_id in {v.id for v in world.player_covenants(saga)}
    ]
    return [
        *(
            DialogField(
                f"{WENT}{c.id}",
                f"Went: {escape(c.name)}",
                "check",
                c.id in played,
            )
            for c in offered
        ),
        DialogField(
            "days",
            "Days it took",
            "optint",
            None,
            hint="Days away from the laboratory for a magus who keeps his "
            "season's work (DE p. 265).",
        ),
    ]


def cast_from(saga: Saga, values: dict[str, Any]) -> list[str]:
    return [c.id for c in saga.characters if values.get(f"{WENT}{c.id}")]


def write_story_chapter(
    covenant: Covenant,
    entry: CovenantDiaryEntry,
    year: int,
    season: str,
    words: str,
    cast: list[str] | None = None,
    days: int | None = None,
    session_id: str = "",
) -> CovenantDiaryEntry:
    """A chapter of the story `entry` in the covenant's Diary, with who
    went, the days it took and the Session it was played at."""
    chapter = CovenantDiaryEntry(
        year,
        season,
        entry.name,
        words.strip(),
        category=CHAPTER,
        story_id=story_id(entry),
        cast=list(cast or []),
        days=days,
        session_id=session_id,
    )
    covenant.diary.append(chapter)
    return chapter


def _write(
    saga: Saga, covenant: Covenant, entry: CovenantDiaryEntry, values: dict[str, Any]
) -> CovenantDiaryEntry:
    session = session_at_hand(saga)
    return write_story_chapter(
        covenant,
        entry,
        values["year"],
        values["season"],
        values["words"],
        cast_from(saga, values),
        values.get("days"),
        session.id if session is not None else "",
    )


#: What follows writing a chapter with a cast: its aftermath's first step
#: (story_aftermath.close_chapter, which registers itself; it sits above
#: the seasons, which sit above this module). Observer, as a list.
AFTERMATH: list[Callable[[Saga, Covenant, CovenantDiaryEntry], Command]] = []


def _then_close(
    saga: Saga, covenant: Covenant, chapter: CovenantDiaryEntry, said: str
) -> Command | list[str]:
    """After writing a chapter with a cast: its aftermath (Cancel leaves it
    open, to close later)."""
    if not chapter.cast or not AFTERMATH:
        return notes(said)
    return AFTERMATH[0](saga, covenant, chapter)


def take_up_story(saga: Saga, covenant: Covenant, entry: CovenantDiaryEntry) -> Command:
    """Take Up the Tale on a story: a chapter of what the troupe did, met
    or avoided. Only an open story; one grown into a threat is taken up on
    the threat."""
    if not is_story(entry):
        return Refuse(TAKE_UP, "Take Up the Tale is for a Story Event.")
    if (entry.status or OPEN) == GROWN:
        threat = grew_into(saga, entry)
        where = threat.name if threat is not None else "the threat it grew into"
        return Refuse(
            TAKE_UP,
            f"{escape(entry.name)} grew into {escape(where)}: take up the tale "
            "on the threat (the Region's Threats).",
        )
    if not is_open(entry):
        return Refuse(TAKE_UP, f"{escape(entry.name)} is already told.")

    def apply(values: dict[str, Any]) -> Command | list[str]:
        chapter = _write(saga, covenant, entry, values)
        return _then_close(
            saga,
            covenant,
            chapter,
            escape(f"A chapter of {entry.name}, in {covenant.name}'s Diary."),
        )

    return Form(
        f"{TAKE_UP}: {escape(entry.name)}",
        lambda: _fields(
            saga,
            "What the troupe did",
            "What was done, met or avoided; written in the covenant's Diary.",
        ),
        apply,
        save_label="Write",
        help_id="take-up-tale",
    )


def ending_form(saga: Saga, covenant: Covenant, entry: CovenantDiaryEntry) -> Form:
    """Resolve's last chapter: how the tale ended (Cancel leaves the story
    resolved, with none)."""

    def apply(values: dict[str, Any]) -> Command | list[str]:
        chapter = _write(saga, covenant, entry, values)
        return _then_close(
            saga, covenant, chapter, escape(f"{entry.name}: its last chapter written.")
        )

    return Form(
        f"{ENDING}: {escape(entry.name)}",
        lambda: _fields(
            saga,
            "How it ended",
            "The story's last chapter, in the covenant's Diary; Cancel writes none.",
        ),
        apply,
        save_label="Write",
        help_id="take-up-tale",
    )


def take_up_threat(saga: Saga, threat: Neighbour) -> Command:
    """Take Up the Tale on a threat: a chapter in its Diary and each
    troupe covenant's."""
    if not threats.is_threat(threat):
        return Refuse(TAKE_UP, "Take Up the Tale is for a threat or an open story.")

    def apply(values: dict[str, Any]) -> list[str]:
        threats.write_chapter(
            saga, threat, values["year"], values["season"], values["words"].strip()
        )
        written = len(world.player_covenants(saga))
        return notes(
            escape(
                f"A chapter of {threat.name}, in its Diary"
                + (
                    f" and {written} covenant Diar{'y' if written == 1 else 'ies'}."
                    if written
                    else "."
                )
            )
        )

    return Form(
        f"{TAKE_UP}: {escape(threat.name)}",
        lambda: _fields(
            saga,
            "What the troupe did",
            "What was done, met or avoided; written in the threat's Diary and "
            "the troupe's covenants'.",
            cast=False,
        ),
        apply,
        save_label="Write",
        help_id="take-up-tale",
    )


#: A threat's Diary: what moved it, delayed it or came of its stages, and
#: its chapters, kept as a place's is; above it, the story it grew from.
THREAT_DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-threat-diary",
    (
        KindList(
            DIARY_SECTION,
            place_events.diary_title,
            lambda _saga, threat: place_events.diary_rows(
                threat,
                "Nothing written yet: what moves it, comes of its stages, and "
                "its chapters.",
            ),
            place_events.diary_ops,
            header=threat_header,
        ),
    ),
)
