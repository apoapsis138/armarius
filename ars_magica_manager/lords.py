"""A lord in detail (Lords of Men): his title, wealth and manors, his
seat and castles, and the Gratitude he owes the troupe; and what is
worked out from them: his income and what he has to spend, the army his
title raises, and what he owes his liege.

Where the book gives two figures for the same thing, the lower is used: a
duke raises 75 knights, not 125; scutage is 2 pounds a knight, not 3. What
he has to spend is the Mercenary Budget (p. 103: a landed noble 2 pounds,
5 if wealthy), not the 10 (20) of p. 31, which is largesse and war
together.

Kept in Neighbour.details: "title", "wealth", "manors", "seat",
"castles" (each {"name", "garrison", "defences", "supplies"}) and
"gratitude" (each {"who", "points", "why", "spent"}: "who" a character's
id, "spent" what was redeemed), "affinity" (his Affinity standing, 0-5;
unset, worked out from his title) and "affinity_divided"."""

from __future__ import annotations

from typing import Any, Required, TypedDict, cast

from . import battles, place_events, references, sieges
from .armies import TITLES, WEALTH, army_of, title, wealth
from .commands import Command, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import DiaryEntry, Neighbour, Saga, details_list
from .neighbour_lists import KindList, KindTab, list_ops
from .references import Fact
from .rules import nobility
from .sections import (
    BATTLES_SECTION,
    CASTLES_SECTION,
    DIARY_SECTION,
    GRATITUDE_SECTION,
    LORD_SIEGES_SECTION,
)

#: A manor's yearly income to its lord, in pounds.
MANOR_INCOME = 20

#: Scutage, in pounds a knight, paid in place of knight service.
SCUTAGE = 2

#: Days of knight service owed a year.
SERVICE_DAYS = 40

#: What a lord has left to spend each year on mercenaries, in pounds, by
#: title and wealth (Lords of Men p. 103's Mercenary Budget: a Wealthy
#: duke's is 500 or more).
SURPLUS: dict[str, dict[str, int]] = {
    "landed": {"Poor": 0, "Average": 2, "Wealthy": 5},
    "baron": {"Poor": 0, "Average": 40, "Wealthy": 100},
    "count": {"Poor": 0, "Average": 100, "Wealthy": 250},
    "duke": {"Poor": 0, "Average": 250, "Wealthy": 500},
}

#: A landed noble's free seasons a year, by wealth: Lords of Men's (p.
#: 31). The Definitive Edition's Landed Noble has no free time beyond the
#: usual, and a Poor one spends every season on his fief (DE p. 89).
FREE_SEASONS: dict[str, int] = {"Poor": 1, "Average": 2, "Wealthy": 3}
FREE_SEASONS_SOURCE = "Lords of Men p. 31, not the DE's Landed Noble (p. 89)"


#: Gratitude: what each total earns from the lord, from Lords of Men's
#: advancement table.
GRATITUDE_STEPS: tuple[tuple[int, str], ...] = (
    (5, "knighthood or freedom"),
    (10, "a manor"),
    (20, "baron of the king"),
)


# -- the record --


def manors(neighbour: Neighbour) -> int:
    return max(0, int(neighbour.details.get("manors") or 0))


class Castle(TypedDict, total=False):
    """A castle the lord holds: its garrison, defences and supplies."""

    name: Required[str]
    garrison: str
    defences: str
    supplies: str


def castles(neighbour: Neighbour) -> list[Castle]:
    return cast(list[Castle], details_list(neighbour, "castles"))


class Gratitude(TypedDict, total=False):
    """What the lord owes a character (by id): the points and why, and the
    rewards already redeemed with it."""

    who: str
    points: int
    why: str
    spent: list[str]


def gratitude(neighbour: Neighbour) -> list[Gratitude]:
    return cast(list[Gratitude], details_list(neighbour, "gratitude"))


# -- worked out --


def income(neighbour: Neighbour) -> int:
    """His manors' yearly income, in pounds."""
    return manors(neighbour) * MANOR_INCOME


def surplus(neighbour: Neighbour) -> int:
    """What he has left to spend each year on mercenaries, in pounds."""
    return SURPLUS[title(neighbour)][wealth(neighbour)]


def budget_text(neighbour: Neighbour) -> str:
    """His Mercenary Budget, as the Fief tab gives it ("500+ pounds a year"
    for a Wealthy duke, whose table figure is a floor)."""
    t, w = title(neighbour), wealth(neighbour)
    plus = "+" if (t, w) == ("duke", "Wealthy") else ""
    return f"{surplus(neighbour)}{plus} pounds a year"


def relief(neighbour: Neighbour) -> int:
    """What his heir pays his liege to inherit: a year's income, at most 5
    pounds a manor, and at most 100 for a baron or greater."""
    owed = min(income(neighbour), 5 * manors(neighbour))
    return owed if title(neighbour) == "landed" else min(owed, 100)


def dues(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """What he owes the neighbour he answers to: none if he answers to no
    one."""
    liege = saga.neighbour(neighbour.answers_to)
    if liege is None:
        return []
    knights = manors(neighbour)
    return [
        Fact(
            "Owes",
            f"{liege.name}: {knights} knight{'' if knights == 1 else 's'} for "
            f"{SERVICE_DAYS} days, or {knights * SCUTAGE} pounds scutage",
            references.refs(liege),
        ),
        Fact("Aids", f"{knights} pounds; relief {relief(neighbour)} pounds"),
    ]


def earns(points: int) -> str:
    """What `points` of Gratitude are enough for, and the next step:
    "Knighthood or freedom; 10 for a manor"."""
    reached = [what for need, what in GRATITUDE_STEPS if points >= need]
    ahead = next(
        ((need, what) for need, what in GRATITUDE_STEPS if points < need), None
    )
    parts = [reached[-1]] if reached else []
    if ahead is not None:
        parts.append(f"{ahead[0]} for {ahead[1]}")
    words = "; ".join(parts)
    return words[:1].upper() + words[1:]


def facts(saga: Saga, neighbour: Neighbour) -> list[Fact]:
    """The fief, as the lord's tab shows it."""
    t, w = title(neighbour), wealth(neighbour)
    found = [
        Fact("Title", f"{TITLES[t]}, {w.lower()}"),
        Fact("Seat", neighbour.details.get("seat", "")),
        Fact("Manors", str(manors(neighbour))),
        Fact("Income", f"{income(neighbour)} pounds a year"),
        Fact("Mercenary budget", budget_text(neighbour)),
    ]
    if t == "landed":
        free = FREE_SEASONS[w]
        found.append(
            Fact(
                "Free time",
                f"{free} season{'' if free == 1 else 's'} ({FREE_SEASONS_SOURCE})",
            )
        )
    found.append(Fact("Army", army_of(t, w).text()))
    found.append(Fact("Affinity", affinity_text(neighbour)))
    return found + dues(saga, neighbour)


# -- Affinity --


def default_affinity(neighbour: Neighbour) -> int:
    """His Affinity standing as his title suggests (Lords of Men p. 21): a
    landed noble of 5 manors or more is of banneret stature (+1); a baron
    is taken at the lowest of the baron tiers, a minor lord's (+2), since
    the title doesn't say whose baron he is (a minor baron of the king is
    +3, a greater baron +4: choose it on his form); a count, earl or duke
    is the senior noble beneath the king (+5)."""
    t = title(neighbour)
    if t == "landed":
        return 1 if manors(neighbour) >= 5 else 0
    return BARON_AFFINITY if t == "baron" else SENIOR_AFFINITY


BARON_AFFINITY, SENIOR_AFFINITY = 2, 5


def set_affinity(neighbour: Neighbour) -> int | None:
    """The Affinity standing chosen for him (the form keeps it as "0" to
    "5"), or None when it is left to his title."""
    raw = neighbour.details.get("affinity")
    if isinstance(raw, int):
        return raw
    return int(raw) if isinstance(raw, str) and raw.isdigit() else None


def affinity(neighbour: Neighbour) -> int:
    """His Affinity bonus (Lords of Men p. 21): the standing set on him or
    his title's, halved where warring affinities divide his country."""
    standing = set_affinity(neighbour)
    if standing is None:
        standing = default_affinity(neighbour)
    return nobility.affinity_bonus(
        standing, bool(neighbour.details.get("affinity_divided"))
    )


def affinity_text(neighbour: Neighbour) -> str:
    bonus = affinity(neighbour)
    if bonus == 0:
        return "None: not of banneret stature"
    halved = (
        " (halved: his country is divided)"
        if neighbour.details.get("affinity_divided")
        else ""
    )
    return (
        f"+{bonus}{halved} to social rolls among the region's nobles, for "
        f"{nobility.AFFINITY_USES}; less if he neglects his affinity's offices "
        "and largesse (LoM p. 22)"
    )


# -- the form --


def fields(_saga: Saga, neighbour: Neighbour | None) -> list[DialogField]:
    """What New Lord and Edit add to the common fields."""
    d = neighbour.details if neighbour is not None else {}
    return [
        DialogField(
            "title",
            "Title",
            "select",
            d.get("title", "landed"),
            options=[(name, key) for key, name in TITLES.items()],
            required=True,
        ),
        DialogField(
            "wealth",
            "Wealth",
            "select",
            d.get("wealth", "Average"),
            options=pairs(WEALTH),
            required=True,
        ),
        DialogField(
            "manors",
            "Manors",
            "int",
            d.get("manors", 1),
            hint="A baron holds about 20, a count 50.",
        ),
        DialogField(
            "seat", "Seat", "text", d.get("seat", ""), placeholder="e.g. Arnsberg"
        ),
        *_affinity_fields(d),
    ]


def _affinity_fields(d: dict[str, Any]) -> list[DialogField]:
    raw = d.get("affinity")
    return [
        DialogField(
            "affinity",
            "Affinity",
            "select",
            str(raw) if raw not in (None, "") else None,
            options=[
                (f"{text} (+{bonus})", str(bonus))
                for bonus, text in nobility.AFFINITY.items()
            ],
            allow_blank=True,
            placeholder="(as his title)",
            hint="His bonus to social rolls among the region's nobles (Lords "
            "of Men p. 21).",
        ),
        DialogField(
            "affinity_divided",
            "His country is divided between warring affinities",
            "check",
            bool(d.get("affinity_divided")),
            hint="Halves the bonus.",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("manors") or 0) < 0:
        return "Manors can't be fewer than none."
    return None


# -- castles --


def castles_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Castles ({len(castles(neighbour))})"


def castles_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = [
        [c["name"], c.get("garrison", ""), c.get("defences", ""), c.get("supplies", "")]
        for c in castles(neighbour)
    ]
    return Grid(
        ["Castle", "Garrison", "Defences", "Supplies"],
        rows,
        list(range(len(rows))),
        "No castles recorded.",
        caps=[22, 16, 22, 0],
        stretch=3,
    )


def castle_fields(
    _saga: Saga, _neighbour: Neighbour, castle: Castle | None
) -> list[DialogField]:
    c = castle or {}
    return [
        DialogField("name", "Name", "text", c.get("name", ""), required=True),
        DialogField(
            "garrison",
            "Garrison",
            "text",
            c.get("garrison", ""),
            placeholder="e.g. 4 knights, 20 serjeants",
        ),
        DialogField(
            "defences",
            "Defences",
            "text",
            c.get("defences", ""),
            placeholder="e.g. stone keep, moat",
        ),
        DialogField(
            "supplies",
            "Supplies",
            "text",
            c.get("supplies", ""),
            placeholder="e.g. a season's siege",
        ),
    ]


def castle_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "castles",
        "Castle",
        castle_fields,
        lambda c: c["name"],
    )


# -- Gratitude --


def _who(saga: Saga, entry: Gratitude) -> str:
    character = saga.character(entry.get("who"))
    return character.name if character is not None else "(gone)"


def gratitude_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Gratitude ({len(gratitude(neighbour))})"


def gratitude_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    """Who he owes, how much, and what it is enough for."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(gratitude(neighbour)):
        points = int(entry.get("points") or 0)
        if points >= GRATITUDE_STEPS[0][0]:
            styles[(index, 1)] = "$text-success"
        rows.append(
            [_who(saga, entry), str(points), earns(points), entry.get("why", "")]
        )
    return Grid(
        ["Owed to", "Points", "Earns", "For"],
        rows,
        list(range(len(rows))),
        "He owes no one Gratitude: a story that serves him earns 1 or 2 points, "
        "a renowned feat 5.",
        styles,
        caps=[20, 6, 40, 0],
        stretch=3,
    )


def gratitude_fields(
    saga: Saga, _neighbour: Neighbour, entry: Gratitude | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "who",
            "Owed to",
            "select",
            e.get("who") or (saga.characters[0].id if saga.characters else None),
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
        ),
        DialogField(
            "points",
            "Points",
            "int",
            e.get("points", 1),
            hint="1 or 2 for a story that serves him, 5 for a renowned feat.",
        ),
        DialogField(
            "why",
            "For",
            "text",
            e.get("why", ""),
            placeholder="e.g. Rescued his son from the Ruhr",
        ),
    ]


def gratitude_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "gratitude",
        "Debt of Gratitude",
        gratitude_fields,
        lambda e: f"the Gratitude owed to {_who(saga, e)}",
        validate=_points_problem,
    )


def _points_problem(values: dict[str, Any]) -> str | None:
    if (values.get("points") or 0) < 0:
        return "Points can't be fewer than none."
    return None


# -- redeeming Gratitude --

REDEEM_TITLE = "Redeem Gratitude"


def redeem_fields(entry: Gratitude) -> list[DialogField]:
    """The reward, the points it takes, and what he gave."""
    owed = int(entry.get("points") or 0)
    affordable = [
        r for r in nobility.REWARDS if r.key != "goods" and r.gratitude <= owed
    ]
    first = max(
        affordable, key=lambda r: r.gratitude, default=nobility.REWARDS_BY_KEY["goods"]
    )
    return [
        DialogField(
            "reward",
            "Reward",
            "select",
            first.key,
            options=[(nobility.reward_label(r), r.key) for r in nobility.REWARDS],
            required=True,
            hint="Most rewards also ask a story event, a Reputation or "
            "Abilities, which are the troupe's to judge (Lords of Men p. 8).",
        ),
        DialogField(
            "spent",
            "Points spent",
            "int",
            first.gratitude if first.key != "goods" else min(1, owed),
            hint=f"He owes {owed}.",
        ),
        DialogField(
            "what",
            "What he gave",
            "text",
            "",
            placeholder="e.g. the manor of Hagen, the hand of his ward",
        ),
    ]


def _redeem_problem(entry: Gratitude, values: dict[str, Any]) -> str | None:
    reward = nobility.REWARDS_BY_KEY[str(values.get("reward"))]
    return nobility.redeem_problem(
        int(entry.get("points") or 0), reward, int(values.get("spent") or 0)
    )


def redeem(
    saga: Saga, lord: Neighbour, entry: Gratitude, values: dict[str, Any]
) -> list[str]:
    """Spend the points: take them off what he owes, keep the reward on
    the entry and in his Diary and the character's."""
    reward = nobility.REWARDS_BY_KEY[str(values.get("reward"))]
    spent = int(values.get("spent") or 0)
    entry["points"] = int(entry.get("points") or 0) - spent
    what = str(values.get("what") or "").strip()
    text = f"{reward.change}{f': {what}' if what else ''} ({spent} Gratitude)"
    entry["spent"] = [*entry.get("spent", []), text]
    who = _who(saga, entry)
    line = f"{lord.name} rewarded {who}: {text}."
    lines = [line, f"He owes {who} {entry['points']} point(s) now."]
    if reward.requires:
        lines.append(f"It asks {reward.requires}.")
    if reward.granter:
        lines.append(f"It costs him {reward.granter}.")
    if reward.virtue:
        lines.append(
            f"The new station brings its Virtue: add {reward.virtue} to "
            f"{who}'s Virtues (Lords of Men p. 7)."
        )
    place_events.diary(lord).append(
        {"year": saga.current_year, "season": saga.current_season, "text": line}
    )
    character = saga.character(entry.get("who"))
    if character is not None:
        character.diary.append(
            DiaryEntry(
                saga.current_year,
                saga.current_season,
                f"Gratitude redeemed with {lord.name}",
                "\n".join([*lines, f"Rules: {nobility.SOURCE}"]),
            )
        )
    return notes(*lines)


def redeem_form(saga: Saga, lord: Neighbour, index: int) -> Command:
    """More's Redeem Gratitude on the chosen debt."""
    owed = gratitude(lord)
    if index >= len(owed):
        return Refuse(REDEEM_TITLE, "Choose a debt of Gratitude first.")
    entry = owed[index]
    if int(entry.get("points") or 0) <= 0:
        return Refuse(
            REDEEM_TITLE,
            f"{escape(lord.name)} owes {escape(_who(saga, entry))} nothing.",
        )
    return Form(
        f"{REDEEM_TITLE}: {escape(_who(saga, entry))}",
        lambda: redeem_fields(entry),
        lambda values: redeem(saga, lord, entry, values),
        validate=lambda values: _redeem_problem(entry, values),
        help_id="section-nb-gratitude",
    )


TAB = KindTab(
    "Fief",
    "tab-nb-fief",
    (
        KindList(CASTLES_SECTION, castles_title, castles_grid, castle_ops),
        KindList(GRATITUDE_SECTION, gratitude_title, gratitude_grid, gratitude_ops),
        KindList(
            BATTLES_SECTION,
            battles.LORD_TITLE,
            battles.LORD_GRID,
            battles.LORD_OPS,
            battles.info_for,
        ),
        KindList(
            LORD_SIEGES_SECTION,
            sieges.title,
            sieges.grid,
            sieges.ops,
            sieges.info_for,
        ),
    ),
)


def diary_grid(_saga: Saga, lord: Neighbour) -> Grid:
    return place_events.diary_rows(
        lord,
        "Nothing written yet: each Battle Event, and each fight or siege he is "
        "linked to, is written here.",
    )


#: His Diary: what befell him and his lands, kept as a place's is.
DIARY_TAB = KindTab(
    "Diary",
    "tab-nb-lord-diary",
    (
        KindList(
            DIARY_SECTION, place_events.diary_title, diary_grid, place_events.diary_ops
        ),
    ),
    after_standing=True,
)
