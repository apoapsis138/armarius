"""What happens at a place over time: its triggers (a regio opening each
Midsummer, a white stag every seven years), its roll tables (rolled with
More's Roll and written to its diary), its diary, and how its aura
changes with the Realms of Power: Magic option.

A trigger comes once (a season and year), each year (a season), every N
years (a season, from a year), or whenever something happens (a
sentence, which the yearly step reminds the storyguide of). The dated
ones are worked out to their next date.

A roll table names its die (a simple die, a stress die, a d6 or a d10)
and its rows, one a line: "1-3: Nothing stirs", "4: The stag", "9+: The
Hall opens"; a stress die's botch reads a "botch" row.

With the aura change option on (Realms of Power: Magic), a Magic aura
rises by 1 on a stress die plus the magic worked there (+1 to +3)
against 15, rolled once a year; and an Infernal aura whose focus is gone
falls by 1 after as many years as its strength, until it is gone.

Kept in Neighbour.details: "triggers" (each {"name", "when", "season",
"year", "every", "what"}), "tables" (each {"name", "die", "rows",
"last"}), "diary" (each {"year", "season", "text"}), "raising" (the
magic worked there) and "focus_gone" (the year an Infernal focus was
removed)."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Any

from . import places
from .commands import Command, Confirm, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Neighbour, Saga
from .neighbour_lists import KindList, KindTab, details_list, list_ops
from .rules import dice, options
from .sections import DIARY_SECTION, TABLES_SECTION, TRIGGERS_SECTION
from .sheets.character import Fact

#: The aura change option's key (rules.options).
AURA_CHANGE = "aura_change"

#: How often a trigger comes.
ONCE, YEARLY, EVERY, WHENEVER = "Once", "Each year", "Every N years", "Whenever"
WHEN: tuple[str, ...] = (ONCE, YEARLY, EVERY, WHENEVER)

#: The dice a roll table can name.
DICE: tuple[str, ...] = ("Simple die", "Stress die", "d6", "d10")

#: What a Magic aura's yearly roll must reach to rise.
RAISE_EASE = 15


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except TypeError, ValueError:
        return 0


def _season_index(season: Any) -> int:
    return SEASONS.index(season) if season in SEASONS else 0


# -- triggers --


def triggers(place: Neighbour) -> list[dict[str, Any]]:
    return details_list(place, "triggers")


def next_date(saga: Saga, trigger: dict[str, Any]) -> tuple[int, str] | None:
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
        step = max(1, _int(trigger.get("every")))
        start = trigger.get("year")
        year = now_year if start is None else start
        while (year, _season_index(season)) < (now_year, now):
            year += step
        return year, season
    return None


def comes_in(trigger: dict[str, Any], year: int) -> str | None:
    """The season a dated trigger comes in `year`, or None."""
    when = trigger.get("when") or ONCE
    season = trigger.get("season") or SEASONS[0]
    start = trigger.get("year")
    if when == ONCE:
        return season if start == year else None
    if when == YEARLY:
        return season
    if when == EVERY:
        step = max(1, _int(trigger.get("every")))
        if start is None:
            return season
        return season if year >= start and (year - start) % step == 0 else None
    return None


def when_text(trigger: dict[str, Any]) -> str:
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
        every = max(1, _int(trigger.get("every")))
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
                    year * len(SEASONS) + _season_index(season),
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
        rows.append(
            [
                trigger["name"],
                when_text(trigger),
                f"{date[1]} {date[0]}" if date is not None else "",
                trigger.get("what", ""),
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
    _saga: Saga, _place: Neighbour, entry: dict[str, Any] | None
) -> list[DialogField]:
    e = entry or {}
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


def tables(place: Neighbour) -> list[dict[str, Any]]:
    return details_list(place, "tables")


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
    _saga: Saga, _place: Neighbour, entry: dict[str, Any] | None
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


def diary(place: Neighbour) -> list[dict[str, Any]]:
    return details_list(place, "diary")


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
    saga: Saga, _place: Neighbour, entry: dict[str, Any] | None
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


# -- the aura's change (Realms of Power: Magic) --


def changes(saga: Saga) -> bool:
    return options.is_on(saga, AURA_CHANGE)


def infernal_aura(saga: Saga, place: Neighbour) -> int | None:
    """An Infernal aura whose focus is gone, as it stands this year: it
    falls by 1 after as many years as its strength. None unless the
    option is on, the place is Infernal and its focus is gone."""
    gone = place.details.get("focus_gone")
    if not changes(saga) or place.realm != "Infernal" or gone is None:
        return None
    aura = _int(place.details.get("aura"))
    year = gone
    while aura > 0 and year + aura <= saga.current_year:
        year += aura
        aura -= 1
    return aura


def change_text(saga: Saga, place: Neighbour) -> str:
    """How its aura changes, with the option on; "" otherwise."""
    if not changes(saga):
        return ""
    realm = place.realm or "Magic"
    if realm == "Magic":
        bonus = _int(place.details.get("raising"))
        return (
            f"Rises by 1 on a stress die {bonus:+d} against {RAISE_EASE}, "
            "rolled each year"
        )
    if realm == "Infernal":
        now = infernal_aura(saga, place)
        if now is None:
            return "Steady while its focus remains"
        return "Gone" if now == 0 else f"Fading: Infernal {now} this year"
    return "Steady"


def aura_roll(
    saga: Saga, place: Neighbour, rng: random.Random
) -> tuple[int, bool] | None:
    """The year's roll to raise a Magic aura: its total and whether the
    aura rises; None when the option is off or the aura isn't Magic."""
    if not changes(saga) or (place.realm or "Magic") != "Magic":
        return None
    bonus = _int(place.details.get("raising"))
    die = dice.stress_die(rng, saga=saga)
    total = (0 if die.botched else die.value) + bonus
    return total, not die.botched and total >= RAISE_EASE


def raise_aura(saga: Saga, place: Neighbour, rng: random.Random) -> str:
    """The year's roll to raise a Magic aura: on success the aura rises
    by 1 and the diary says so. Returns what happened ("" when the
    option is off or the aura isn't Magic)."""
    rolled = aura_roll(saga, place, rng)
    if rolled is None:
        return ""
    total, rises = rolled
    if not rises:
        return f"{place.name}: the aura holds ({total} against {RAISE_EASE})."
    place.details["aura"] = _int(place.details.get("aura")) + 1
    text = f"The aura rose to Magic {place.details['aura']} ({total} against {RAISE_EASE})."
    diary(place).append(
        {"year": saga.current_year, "season": saga.current_season, "text": text}
    )
    places.sync(saga)
    return f"{place.name}: {text}"


def fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """What the aura change option adds to a place's form."""
    if not changes(saga):
        return []
    d = place.details if place is not None else {}
    return [
        DialogField(
            "raising",
            "Magic worked there",
            "int",
            d.get("raising", 0),
            hint="+1 to +3 for lab work, spells and vis study there: added to "
            "the yearly roll to raise a Magic aura.",
        ),
        DialogField(
            "focus_gone",
            "Infernal focus gone in (year)",
            "optint",
            d.get("focus_gone"),
            hint="An Infernal aura then fades by 1 every so many years.",
        ),
    ]


# -- a place, as its kind shows it --


def place_fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """New Place's and Edit's own fields: the place's, then the aura
    change option's."""
    return places.fields(saga, place) + fields(saga, place)


def place_facts(saga: Saga, place: Neighbour) -> list[Fact]:
    """The place's facts, its next trigger and how its aura changes."""
    found = places.facts(saga, place)
    found.insert(1, Fact("Next", next_text(saga, place)))
    change = change_text(saga, place)
    if change:
        found.insert(2, Fact("Aura change", change))
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
