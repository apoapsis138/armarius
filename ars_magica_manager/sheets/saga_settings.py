"""The saga's settings as the figures a page of cards draws, without a
front-end: its seasons, its optional rules under their headings, and its
Tribunal's templates. Each card says in a line what it sets; `detail` says
it in full. What changing one does is in forms/saga_settings.py.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import medallions, ruling_templates, saga_content, sourcebooks
from ..markup import escape
from ..models import Saga
from ..references import Fact
from ..rules import options as rule_options
from ..seasons import defaults

#: The saga's own on/off settings: the fields of Saga, by key.
SAGA_FLAGS = ("keep_season_records", "notify_npc_unplanned")
#: Its settings chosen from a list: the fields of Saga, by key.
UNPLANNED = (
    ("unplanned_magi", "Idle Magi"),
    ("unplanned_companions", "Idle Companions"),
    ("unplanned_grogs", "Idle Grogs"),
)
MEDALLIONS = "medallions"
RULING_TEMPLATES = "ruling_templates"
THE_SAGA = "Saga Details"


@dataclass(frozen=True)
class SettingCard:
    """One setting. A card with `choice` shows that value, and changing it
    asks; any other has a switch, `on`. One that isn't `usable` (its book
    is out of play) is greyed out and says why in `refused`."""

    key: str
    title: str
    subtitle: str
    summary: str
    detail: str
    on: bool = False
    choice: str = ""
    book: str = ""
    usable: bool = True
    refused: str = ""


@dataclass(frozen=True)
class SettingGroup:
    heading: str
    cards: list[SettingCard]


def facts(saga: Saga) -> list[Fact]:
    """Saga Details' figures."""
    return [
        Fact("Name", saga.name),
        Fact("Storyguide", saga.storyguide or "None set"),
        Fact("Description", saga.description or "None set"),
    ]


def _value(options: list[tuple[str, str]], chosen: str) -> str:
    return next(label for label, value in options if value == chosen)


def _unplanned_card(saga: Saga, key: str, title: str) -> SettingCard:
    who, what = {
        "unplanned_magi": (
            "A magus",
            "Work / Exposure gives 2 xp in their profession, else Magic "
            "Theory, else their highest Ability that isn't a language, marked "
            "(default) in the Diary.",
        ),
        "unplanned_companions": (
            "A companion",
            "Work / Exposure gives 2 xp in their profession, else their "
            "highest Ability that isn't a language.",
        ),
        "unplanned_grogs": (
            "A grog with no yearly update",
            "Work / Exposure gives 2 xp of Exposure a season in their "
            "highest Ability, 8 at the year's end.",
        ),
    }[key]
    return SettingCard(
        key,
        title,
        "When the season is advanced",
        f"What {who[0].lower()}{who[1:]} with nothing planned does.",
        f"{who} left with nothing planned takes this when the season is "
        f"advanced. {what}\n\nNothing gives them no season at all.",
        choice=_value(defaults.OPTIONS, getattr(saga, key)),
    )


def season_cards(saga: Saga) -> list[SettingCard]:
    return [
        SettingCard(
            "keep_season_records",
            "Keep Season Records",
            "Seasons",
            "Keeps a record of each season as it is applied.",
            "On: each season applied is kept on the Seasons page, where past "
            "seasons can be browsed.\n\nOff: only the characters' Diaries "
            "keep them.",
            on=saga.keep_season_records,
        ),
        *(_unplanned_card(saga, key, title) for key, title in UNPLANNED),
        SettingCard(
            "notify_npc_unplanned",
            "Name Idle Non-Player Characters",
            "When the season is advanced",
            "Names the non-player characters with nothing planned.",
            "On: Advance Season names the non-player characters who have no "
            "seasonal activity, and asks about each.\n\nOff: it names only "
            "player characters; the others take the default for their kind.",
            on=saga.notify_npc_unplanned,
        ),
        SettingCard(
            MEDALLIONS,
            "Medallion Style",
            "How every medallion is drawn",
            "The set every medallion is drawn in, seasons and figures.",
            "The look of every medallion on the desktop: the seasons', from "
            "the headpiece under the top bar to a siege's track, and the "
            "figures', such as an aura or a covenant's Loyalty.",
            choice=_value(medallions.options(), medallions.chosen(saga)),
        ),
    ]


def _rule_card(saga: Saga, option: rule_options.RuleOption) -> SettingCard:
    book = sourcebooks.title_of(option.book, saga) if option.book else ""
    usable = sourcebooks.in_play(option.book, sourcebooks.saga_books(saga))
    refused = "" if usable else f"Put {book} in play on Books in Play to turn it on."
    lines = [escape(option.effect), f"Source: {escape(option.source)}."]
    if refused:
        lines.append(
            f"{escape(refused)} While it is out of play this rule counts as "
            "off, and the choice is kept for when it comes back."
        )
    return SettingCard(
        option.key,
        option.label,
        book or "Optional rule",
        option.brief,
        "\n\n".join(lines),
        on=rule_options.is_on(saga, option.key),
        book=book,
        usable=usable,
        refused=refused,
    )


def rule_groups(saga: Saga) -> list[SettingGroup]:
    """Every optional rule under its heading, in or out of play."""
    return [
        SettingGroup(
            heading,
            [
                _rule_card(saga, option)
                for option in rule_options.OPTIONS
                if option.group == heading
            ],
        )
        for heading in rule_options.GROUPS
    ]


def tribunal_cards(saga: Saga) -> list[SettingCard]:
    count = len(ruling_templates.templates(saga))
    return [
        SettingCard(
            RULING_TEMPLATES,
            "Ruling Templates",
            "Hold Tribunal",
            "The outcomes a Tribunal's rulings are written from.",
            "Each template is a ruling with blanks filled in at the meeting: "
            "any word in braces is a blank. They are the saga's own, and each "
            "can be added, changed or removed.",
            choice=f"{count} template{'' if count == 1 else 's'}",
        )
    ]


def rules_lead(saga: Saga) -> str:
    """The line over the optional rules: how many are on."""
    on = sum(1 for o in rule_options.OPTIONS if rule_options.is_on(saga, o.key))
    every = saga_content.every_book(saga)
    in_play = sum(1 for book in every if saga_content.is_in_play(saga, book))
    return (
        f"{on} on. A rule from a book out of play is greyed out ({in_play} of "
        f"{len(every)} books in play, chosen on Saga Content)."
    )
