"""What happens at a place over time: its triggers (a regio opening each
Midsummer, a white stag every seven years), its roll tables (rolled with
More's Roll and written to its diary), its diary, and how its aura
changes with the Realms of Power: Magic option.

A trigger comes once (a season and year), each year (a season), every N
years (a season, from a year), or whenever something happens (a
sentence, which the yearly step reminds the storyguide of). The dated
ones are worked out to their next date. A dated trigger can be tied to
a threat moving along a track (its "clock"): each time it comes, the
season it comes in asks whether the troupe failed it, which moves the
threat on its steps, or kept it, which leaves it (world_turns).

A roll table names its die (a simple die, a stress die, a d6 or a d10)
and its rows, one a line: "1-3: Nothing stirs", "4: The stag", "9+: The
Hall opens"; a stress die's botch reads a "botch" row.

With the aura change option on, a Magic aura varies each year as
Realms of Power: Magic says, an Infernal aura inside a stronger one
erodes as Realms of Power: The Infernal says, and a Faerie aura follows
the glamour of the faerie that claims it as Realms of Power: Faerie says
(rules.aura_change); this module adds their fields to a place's form.

Kept in Neighbour.details: "triggers" (each {"name", "when", "season",
"year", "every", "what", "threat_id", "steps"}), "tables" (each {"name", "die", "rows",
"last"}) and "diary" (each {"year", "season", "text"}); the aura
change's own keys are listed in rules.aura_change."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any, Required, TypedDict, cast

from . import places, threats
from .commands import Command, Confirm, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Neighbour, Saga, details_list, season_order
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .rules import aura_change, dice
from .rules.sites import whole_number
from .sections import DIARY_SECTION, TABLES_SECTION, TRIGGERS_SECTION

#: How often a trigger comes.
ONCE, YEARLY, EVERY, WHENEVER = "Once", "Each year", "Every N years", "Whenever"
WHEN: tuple[str, ...] = (ONCE, YEARLY, EVERY, WHENEVER)

#: The dice a roll table can name.
DICE: tuple[str, ...] = ("Simple die", "Stress die", "d6", "d10")


def _season_index(season: Any) -> int:
    return SEASONS.index(season) if season in SEASONS else 0


# -- triggers --


class Trigger(TypedDict, total=False):
    """An event that comes to a place on a date: once, yearly or every
    few years, and what happens."""

    name: Required[str]
    when: str
    season: str
    year: int | None
    every: int | None
    what: str
    #: The threat whose track failing this trigger moves, and how far.
    threat_id: str
    steps: int | None


def triggers(place: Neighbour) -> list[Trigger]:
    return cast(list[Trigger], details_list(place, "triggers"))


def threat_of(saga: Saga, trigger: Trigger) -> Neighbour | None:
    """The threat a trigger is tied to, while it is one a trigger can
    move (None if untied, or the threat is gone or now moves by date)."""
    wanted = trigger.get("threat_id")
    if not wanted:
        return None
    found = saga.neighbour(wanted)
    return found if found is not None and threats.tied(found) else None


def steps(trigger: Trigger) -> int:
    """How far failing a tied trigger moves its threat (1 unless said)."""
    return max(1, whole_number(trigger.get("steps") or 1))


def tie_text(saga: Saga, trigger: Trigger) -> str:
    """ "failing it moves The Hollow Crown 1 step"; "" when untied."""
    threat = threat_of(saga, trigger)
    if threat is None:
        return ""
    count = steps(trigger)
    return f"failing it moves {threat.name} {count} step{'' if count == 1 else 's'}"


def next_date(saga: Saga, trigger: Trigger) -> tuple[int, str] | None:
    """The next season (this one included) a dated trigger comes, as
    (year, season); None for a sentence, or a one-off already past."""
    when = trigger.get("when") or ONCE
    season = trigger.get("season") or SEASONS[0]
    now_year, now = saga.current_year, _season_index(saga.current_season)
    passed = _season_index(season) < now
    if when == ONCE:
        year = trigger.get("year")
        if year is None or (year, _season_index(season)) < (now_year, now):
            return None
        return year, season
    if when == YEARLY:
        return (now_year + 1 if passed else now_year), season
    if when == EVERY:
        step = max(1, whole_number(trigger.get("every")))
        start = trigger.get("year")
        year = now_year if start is None else start
        while (year, _season_index(season)) < (now_year, now):
            year += step
        return year, season
    return None


def comes_in(trigger: Trigger, year: int) -> str | None:
    """The season a dated trigger comes in `year`, or None."""
    when = trigger.get("when") or ONCE
    season = trigger.get("season") or SEASONS[0]
    start = trigger.get("year")
    if when == ONCE:
        return season if start == year else None
    if when == YEARLY:
        return season
    if when == EVERY:
        step = max(1, whole_number(trigger.get("every")))
        if start is None:
            return season
        return season if year >= start and (year - start) % step == 0 else None
    return None


def when_text(trigger: Trigger) -> str:
    """ "Summer 1220", "Summer each year", "Winter every 7 years" (its
    next date says which), or "Whenever"."""
    when = trigger.get("when") or ONCE
    season = trigger.get("season") or ""
    year = trigger.get("year")
    if when == ONCE:
        return " ".join(str(p) for p in (season, year) if p)
    if when == YEARLY:
        return f"{season or 'Once'} each year".replace("Once each", "Each")
    if when == EVERY:
        every = max(1, whole_number(trigger.get("every")))
        return f"{season} every {every} years".strip()
    return WHENEVER


def upcoming(saga: Saga, place: Neighbour) -> list[tuple[int, str]]:
    """Each dated trigger's next date (sortable) and "Name, Summer
    1220", soonest first: what Ahead lists."""
    found = []
    for trigger in triggers(place):
        date = next_date(saga, trigger)
        if date is not None:
            year, season = date
            found.append(
                (
                    season_order(season=season, year=year),
                    f"{trigger['name']}, {season} {year}",
                )
            )
    return sorted(found)


def next_text(saga: Saga, place: Neighbour) -> str:
    found = upcoming(saga, place)
    return found[0][1] if found else ""


def triggers_title(_saga: Saga, place: Neighbour) -> str:
    return f"Triggers ({len(triggers(place))})"


def triggers_grid(saga: Saga, place: Neighbour) -> Grid:
    rows = []
    for trigger in triggers(place):
        date = next_date(saga, trigger)
        what = trigger.get("what", "")
        if tie := tie_text(saga, trigger):
            what = f"{what} ({tie})" if what else tie[0].upper() + tie[1:]
        rows.append(
            [
                trigger["name"],
                when_text(trigger),
                f"{date[1]} {date[0]}" if date is not None else "",
                what,
            ]
        )
    return Grid(
        ["Trigger", "When", "Next", "What happens"],
        rows,
        list(range(len(rows))),
        "No triggers: add what comes on a date, each year, every few years, "
        "or whenever something happens.",
        caps=[18, 22, 11, 0],
        stretch=3,
    )


def trigger_fields(
    saga: Saga, _place: Neighbour, entry: Trigger | None
) -> list[DialogField]:
    e = entry or {}
    clocks = [(n.name, n.id) for n in saga.neighbours if threats.tied(n)]
    return [
        DialogField(
            "name",
            "Trigger",
            "text",
            e.get("name", ""),
            required=True,
            placeholder="e.g. Level 3 opens",
        ),
        DialogField(
            "when",
            "Comes",
            "select",
            e.get("when", ONCE),
            options=pairs(WHEN),
            required=True,
        ),
        DialogField(
            "season",
            "Season",
            "select",
            e.get("season") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField(
            "year",
            "Year",
            "optint",
            e.get("year"),
            hint="Once: the year it comes. Every N years: a year it comes.",
        ),
        DialogField("every", "Every (years)", "optint", e.get("every")),
        DialogField("what", "What happens", "text", e.get("what", "")),
        DialogField(
            "threat_id",
            "Moves a threat",
            "select",
            e.get("threat_id") or None,
            options=clocks,
            allow_blank=True,
            placeholder="(none)",
            hint="A threat moving along a track: each time this comes, its "
            "season asks whether the troupe failed it (the threat moves on) "
            "or kept it (it stays).",
        ),
        DialogField(
            "steps",
            "Failing moves it (steps)",
            "optint",
            e.get("steps"),
            show_if=lambda v: bool(v.get("threat_id")),
            placeholder="1",
        ),
    ]


def _trigger_problem(values: dict[str, Any]) -> str | None:
    when = values.get("when")
    if when == ONCE and values.get("year") is None:
        return "A trigger that comes once needs its year."
    if when in (ONCE, YEARLY, EVERY) and not values.get("season"):
        return "A dated trigger needs its season."
    if when == EVERY and (values.get("every") or 0) < 1:
        return "Say how many years apart it comes."
    if when == WHENEVER and not (values.get("what") or "").strip():
        return "Say what sets it off and what happens."
    if values.get("threat_id") and when == WHENEVER:
        return "A trigger that moves a threat needs a date: its season asks."
    if (values.get("steps") or 1) < 1:
        return "Failing it moves the threat at least 1 step."
    return None


def trigger_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        place,
        "triggers",
        "Trigger",
        trigger_fields,
        lambda t: t["name"],
        validate=_trigger_problem,
    )


# -- roll tables --


@dataclass(frozen=True)
class TableRow:
    """A row of a roll table: the rolls it covers (inclusive; `high` None
    for "and up") and its result. A botch row covers a stress die's
    botch."""

    low: int
    high: int | None
    result: str
    botch: bool = False

    def covers(self, value: int, botched: bool) -> bool:
        if self.botch or botched:
            return self.botch and botched
        return value >= self.low and (self.high is None or value <= self.high)


_ROW = re.compile(
    r"^\s*(?:(botch)|(\d+)\s*(?:([-–])\s*(\d+)|(\+))?)\s*[:.]\s*(.+)$", re.IGNORECASE
)


def parse_rows(text: str) -> list[TableRow] | None:
    """The rows written one a line ("1-3: Nothing", "9+: The Hall
    opens", "botch: The mist closes"); None if a line isn't one."""
    found = []
    for line in (text or "").splitlines():
        if not line.strip():
            continue
        match = _ROW.match(line)
        if match is None:
            return None
        botch, low, _dash, high, plus, result = match.groups()
        if botch:
            found.append(TableRow(0, 0, result.strip(), botch=True))
            continue
        start = int(low)
        end = None if plus else int(high) if high else start
        found.append(TableRow(start, end, result.strip()))
    return found


class RollTable(TypedDict, total=False):
    """A table rolled at a place: its die, its rows as typed, and the
    last roll."""

    name: Required[str]
    die: str
    rows: str
    last: str


def tables(place: Neighbour) -> list[RollTable]:
    return cast(list[RollTable], details_list(place, "tables"))


def tables_title(_saga: Saga, place: Neighbour) -> str:
    return f"Roll Tables ({len(tables(place))})"


def tables_grid(_saga: Saga, place: Neighbour) -> Grid:
    rows = [
        [
            table["name"],
            table.get("die") or DICE[0],
            str(len(parse_rows(table.get("rows", "")) or [])),
            table.get("last", ""),
        ]
        for table in tables(place)
    ]
    return Grid(
        ["Table", "Die", "Rows", "Last rolled"],
        rows,
        list(range(len(rows))),
        "No roll tables: add one, then roll it with More's Roll.",
        caps=[26, 10, 4, 0],
        stretch=3,
    )


def table_fields(
    _saga: Saga, _place: Neighbour, entry: RollTable | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "name",
            "Table",
            "text",
            e.get("name", ""),
            required=True,
            placeholder="e.g. Who walks the Mist Wood",
        ),
        DialogField(
            "die",
            "Die",
            "select",
            e.get("die") or DICE[0],
            options=pairs(DICE),
            required=True,
        ),
        DialogField(
            "rows",
            "Rows",
            "area",
            e.get("rows", ""),
            required=True,
            hint='One a line: "1-3: Nothing stirs", "9+: The Hall opens", '
            '"botch: The mist closes".',
        ),
    ]


def _table_problem(values: dict[str, Any]) -> str | None:
    if not parse_rows(values.get("rows") or ""):
        return 'Write each row as "1-3: what happens", one a line.'
    return None


def table_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        place,
        "tables",
        "Roll Table",
        table_fields,
        lambda t: t["name"],
        validate=_table_problem,
    )


def _roll(die: str, rng: random.Random, saga: Saga) -> tuple[int, bool, str]:
    """The roll of `die`: its value, whether it botched, and how it reads."""
    if die == "Stress die":
        result = dice.stress_die(rng, saga=saga)
        return (
            result.value,
            result.botched,
            "a botch" if result.botched else str(result.value),
        )
    if die == "d6":
        value = rng.randint(1, 6)
    else:
        value = dice.simple_die(rng)
    return value, False, str(value)


def roll_table(
    saga: Saga, place: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Roll on the chosen table: roll its die, read its row, and
    write the result to the place's diary if kept."""
    listed = tables(place)
    if index >= len(listed):
        return Refuse("Roll", "Choose a roll table first.")
    table = listed[index]
    rows = parse_rows(table.get("rows", "")) or []
    value, botched, shown = _roll(
        table.get("die") or DICE[0], rng or random.Random(), saga
    )
    row = next((r for r in rows if r.covers(value, botched)), None)
    result = row.result if row is not None else "no row covers it"
    when = f"{saga.current_season} {saga.current_year}"

    def apply() -> None:
        table["last"] = f"{when}: {shown}, {result}"
        diary(place).append(
            {
                "year": saga.current_year,
                "season": saga.current_season,
                "text": f"{table['name']}: rolled {shown}, {result}",
            }
        )

    return Confirm(
        f"{escape(table['name'])}: the {escape((table.get('die') or DICE[0]).lower())} "
        f"shows {shown}.\n\n[b]{escape(result)}[/]\n\nWrite it in "
        f"{escape(place.name)}'s diary?",
        apply,
        yes_label="Write",
        title="Roll a Table",
    )


# -- the diary --


class PlaceDiaryEntry(TypedDict, total=False):
    """A line of a place's diary."""

    year: int | None
    season: str
    text: str


def diary(place: Neighbour) -> list[PlaceDiaryEntry]:
    return cast(list[PlaceDiaryEntry], details_list(place, "diary"))


def diary_title(_saga: Saga, place: Neighbour) -> str:
    return f"Diary ({len(diary(place))})"


def diary_grid(_saga: Saga, place: Neighbour) -> Grid:
    return diary_rows(
        place, "Nothing written yet: a roll on one of its tables is written here."
    )


def diary_rows(record: Neighbour, empty: str) -> Grid:
    """A neighbour's diary, oldest first; `empty` says why there is none."""
    rows = [
        [
            " ".join(str(p) for p in (e.get("season"), e.get("year")) if p),
            e.get("text", ""),
        ]
        for e in diary(record)
    ]
    return Grid(
        ["When", "What happened"],
        rows,
        list(range(len(rows))),
        empty,
        caps=[12, 0],
        stretch=1,
    )


def diary_fields(
    saga: Saga, _place: Neighbour, entry: PlaceDiaryEntry | None
) -> list[DialogField]:
    e = entry or {"year": saga.current_year, "season": saga.current_season}
    return [
        DialogField("year", "Year", "optint", e.get("year")),
        DialogField(
            "season",
            "Season",
            "select",
            e.get("season") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField("text", "What happened", "text", e.get("text", ""), required=True),
    ]


def diary_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        place,
        "diary",
        "Diary Entry",
        diary_fields,
        lambda e: "the entry",
    )


# -- the aura's change (Realms of Power: Magic and The Infernal) --


def changes(saga: Saga) -> bool:
    return aura_change.is_on(saga)


_realm_is = places.realm_is


def fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """What the aura change option adds to a place's form: for a Magic aura
    what moves it each year, for an Infernal one what it sits in."""
    if not changes(saga):
        return []
    d = place.details if place is not None else {}
    magic, infernal = _realm_is("Magic"), _realm_is("Infernal")
    found = [
        DialogField(
            f"impinging_{realm.lower()}",
            f"A stronger {realm} aura impinges",
            "check",
            bool(d.get(f"impinging_{realm.lower()}")),
            hint=f"Around it or sharing its ground: {amount:+d} to the yearly "
            "modifier (RoP: Magic p. 10).",
            show_if=magic,
        )
        for realm, amount in aura_change.IMPINGING.items()
    ]
    found += [
        DialogField(
            "aura_adjust",
            "This year's botches and other magic",
            "int",
            d.get("aura_adjust", d.get("raising", 0)),
            hint="+1 for each beneficial botch of 2+ Warping Points, -1 for each "
            "detrimental one, +1 for each other spending of 3+ pawns of vis "
            "there; the app counts vis study and extraction itself. Cleared "
            "each winter.",
            show_if=magic,
        ),
        DialogField(
            "aura_botch_dice",
            "Aura roll botch dice",
            "int",
            d.get("aura_botch_dice", 0),
            hint="Starts at 0; +1 after each roll of 9 or more, -1 after a year "
            "with no roll.",
            show_if=magic,
        ),
        DialogField(
            "around",
            "Stronger aura around it",
            "int",
            d.get("around", 0),
            hint="The aura it sits inside: weaker than that, it erodes by 1 "
            "after as many years as its strength (RoP: The Infernal p. 11).",
            show_if=infernal,
        ),
        DialogField(
            "around_realm",
            "Realm of that aura",
            "select",
            d.get("around_realm") or "Divine",
            options=pairs(("Divine", "Magic", "Faerie")),
            show_if=infernal,
        ),
        DialogField(
            "maintained",
            "Kept by a demon or an Infernal enchantment",
            "check",
            bool(d.get("maintained")),
            hint="While something keeps it, it doesn't erode.",
            show_if=infernal,
        ),
        DialogField(
            "eroding_since",
            "Eroding since (year)",
            "optint",
            aura_change.eroding_since(place) if place is not None else None,
            hint="When its erosion clock last started; a corruption roll that "
            "keeps it starts the clock again.",
            show_if=infernal,
        ),
    ]
    return found + faerie_fields(saga, place)


def faerie_fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """What the aura change option asks of a Faerie place: whose glamour
    claims it (RoP: Faerie pp. 14-16)."""
    d = place.details if place is not None else {}
    faerie = _realm_is("Faerie")
    faeries = [(escape(c.name), c.id) for c in saga.creatures if c.realm == "Faerie"]

    def pick(key: str, label: str, hint: str) -> DialogField:
        return DialogField(
            key,
            label,
            "select",
            d.get(key) or None,
            options=faeries,
            allow_blank=True,
            placeholder="(none)",
            hint=hint,
            show_if=faerie,
        )

    return [
        pick(
            "presiding",
            "Glamour of (presiding faerie)",
            "Its aura is this faerie's Might / 5 (RoP: Faerie p. 14).",
        ),
        pick(
            "contesting",
            "Contested by",
            "While two faeries clash over it: 2 + the higher Might / 5, at most 9.",
        ),
        pick(
            "steward",
            "Steward",
            "While the presiding faerie is away, the steward's Might / 5 (p. 16).",
        ),
        DialogField(
            "presiding_away",
            "The presiding faerie is away",
            "check",
            bool(d.get("presiding_away")),
            show_if=faerie,
        ),
        DialogField(
            "vis_bargain",
            "A bargain lets the magi take its vis",
            "check",
            bool(d.get("vis_bargain")),
            hint="Without one, each season of vis extraction there lowers the "
            "aura by 1 until the faerie gets redress (p. 15).",
            show_if=faerie,
        ),
        DialogField(
            "glamour_lost",
            "Aura lost to vis taken",
            "int",
            d.get("glamour_lost", 0),
            hint="Set it back to 0 once the faerie has had redress.",
            show_if=faerie,
        ),
    ]


#: The corrupted auras of Realms of Power: The Infernal pp. 14-15.
CORRUPTIONS: tuple[str, ...] = ("Debauched", "Malevolent", "Perfidious")


def infernal_fields(place: Neighbour | None) -> list[DialogField]:
    """An Infernal aura's tarnish and corruption (RoP: The Infernal pp.
    13-15), asked of an Infernal place."""
    d = place.details if place is not None else {}
    infernal = _realm_is("Infernal")
    return [
        DialogField(
            "tarnish",
            "Tarnished with",
            "text",
            d.get("tarnish", ""),
            placeholder="e.g. Lust",
            hint="A sinful Personality Trait: everyone in the aura acts as if "
            "theirs were moved by its strength.",
            show_if=infernal,
        ),
        DialogField(
            "corruption",
            "Corrupted",
            "select",
            d.get("corruption") or None,
            options=pairs(CORRUPTIONS),
            allow_blank=True,
            placeholder="(not corrupted)",
            hint="Only an aura of 3 or more; its tarnish then can't change. "
            "Write its features in Notes.",
            show_if=infernal,
        ),
    ]


def infernal_problem(values: dict[str, Any]) -> str | None:
    if values.get("corruption") and (values.get("aura") or 0) < 3:
        return "Only an Infernal aura of 3 or more can be corrupted."
    return None


# -- a place, as its kind shows it --


def place_fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """New Place's and Edit's own fields: the place's, an Infernal aura's
    tarnish, then the aura change option's."""
    return places.fields(saga, place) + infernal_fields(place) + fields(saga, place)


def place_problem(values: dict[str, Any]) -> str | None:
    return places.problem(values) or infernal_problem(values)


def place_facts(saga: Saga, place: Neighbour) -> list[Fact]:
    """The place's facts, its next trigger and how its aura changes."""
    found = places.facts(saga, place)
    found.insert(1, Fact("Next", next_text(saga, place)))
    change = aura_change.summary(saga, place)
    if change:
        found.insert(2, Fact("Aura change", change))
    if place.realm == "Infernal" and (
        place.details.get("tarnish") or place.details.get("corruption")
    ):
        tarnish = place.details.get("tarnish") or ""
        corruption = place.details.get("corruption") or ""
        text = ", ".join(
            part
            for part in (
                f"tarnished with {tarnish}" if tarnish else "",
                f"{corruption.lower()}" if corruption else "",
            )
            if part
        )
        found.insert(2, Fact("Infernal", text[0].upper() + text[1:]))
    return found


# -- the tabs --


TRIGGERS = KindList(TRIGGERS_SECTION, triggers_title, triggers_grid, trigger_ops)
REGIO_TAB = KindTab("Regio", "tab-nb-place", (*places.LISTS, TRIGGERS))
TABLES_TAB = KindTab(
    "Roll Tables",
    "tab-nb-tables",
    (KindList(TABLES_SECTION, tables_title, tables_grid, table_ops),),
)
DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-place-diary",
    (KindList(DIARY_SECTION, diary_title, diary_grid, diary_ops),),
)

#: A threat's Diary: what moved it, delayed it or came of its stages,
#: kept as a place's is.
THREAT_DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-threat-diary",
    (
        KindList(
            DIARY_SECTION,
            diary_title,
            lambda _saga, threat: diary_rows(
                threat,
                "Nothing written yet: what moves it, delays it or comes of its "
                "stages is written here.",
            ),
            diary_ops,
        ),
    ),
)
