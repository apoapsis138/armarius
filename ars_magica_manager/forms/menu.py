"""The More and New menus and deleting a record, for a front-end that
shows one record's page at a time (the desktop), independent of how they
are drawn.

A `Page` is actions.ActionFacts for such a front-end: the record on show,
and no focused section. Its menus offer what more.available offers
anywhere on the page: each More command is asked about with the page's
sections (PAGE_SECTIONS) one by one, and kept if any offers it. Every
command acts on the record on show, so the page counts as being "on the
record" (Delete, Export, In Creation / In Play); a command that would act
on a chosen row asks which first (a commands.Choose).

`command(page, action)` builds the first step of a menu entry, or of
Delete (`DELETE_RECORD`), as commands.py steps: mutating the saga only in
the last step's apply, so cancelling any step changes nothing.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import NamedTuple

from .. import (
    deeds,
    giving,
    viewing,
)
from ..actions import (
    RECORD_SECTION,
    MenuItem,
    NodeKind,
    silver_purse,
)
from ..commands import Command, Refuse
from ..markup import escape
from ..rules import covenfolk
from ..sections import FAITH_SECTION, LAB_TEXTS_SECTION
from . import hosting as hosting_forms
from . import more
from .menu_steps import OTHER_STEPS, delete_record, familiar_binder
from .more import MORE_MENU, MORE_SECTIONS, NEW_MENU, available
from .page import (
    Page,
    Record,
)

#: Delete's action: the record on show, after a confirmation that says
#: what happens to what it owns.
DELETE_RECORD = "delete_record"

#: Per page, the sections whose More commands its menu offers (None: the
#: page itself, with no section).
PAGE_SECTIONS: dict[NodeKind, tuple[str | None, ...]] = {
    NodeKind.SAGA: (None,),
    NodeKind.CHARACTER: (
        RECORD_SECTION[NodeKind.CHARACTER],
        "section-hermetic-background",
        "section-known-spells",
        "section-raw-vis-hermetic",
        "section-raw-vis-inventory",
        "section-inventory",
    ),
    NodeKind.FAMILIAR: (RECORD_SECTION[NodeKind.FAMILIAR],),
    NodeKind.TRIBUNAL: (RECORD_SECTION[NodeKind.TRIBUNAL],),
    NodeKind.NEIGHBOUR: (RECORD_SECTION[NodeKind.NEIGHBOUR],),
    NodeKind.CREATURE: (RECORD_SECTION[NodeKind.CREATURE],),
    NodeKind.LABORATORY: (
        RECORD_SECTION[NodeKind.LABORATORY],
        "section-lab-raw-vis",
        LAB_TEXTS_SECTION,
    ),
    NodeKind.COVENANT: (
        RECORD_SECTION[NodeKind.COVENANT],
        *(f"section-inh-{kind}" for kind in covenfolk.AUTO_KINDS),
        "section-eco-income",
        "section-eco-wealth",
        "section-pos-vis_store",
        "section-lib-books",
    ),
}


#: The sections only a magus's sheet has.
_MAGUS_SECTIONS = frozenset(
    {"section-hermetic-background", "section-known-spells", "section-raw-vis-hermetic"}
)


def page_sections(page: Page) -> tuple[str | None, ...]:
    """The sections of PAGE_SECTIONS the page shows."""
    sections = PAGE_SECTIONS.get(page.kind, ()) if page.kind else ()
    if page.kind == NodeKind.CHARACTER and (
        page.character is None or page.character.type != "magus"
    ):
        sections = tuple(s for s in sections if s not in _MAGUS_SECTIONS)
    return sections


def _anything(_page: Page) -> bool:
    return True


#: More commands the page's menu leaves out while they have nothing to act
#: on (the terminal offers them in their section and then says so).
_PAGE_CHECKS: dict[str, Callable[[Page], bool]] = {
    "improve": lambda page: bool(
        page.covenant is not None and page.covenant.economics.income_sources
    ),
    # Philosophic Alchemy's digestions.
    "philosophic_alchemy": lambda page: available(
        "philosophic_alchemy", replace(page, section="section-char-season")
    ),
}


def more_items(page: Page) -> list[MenuItem]:
    """What More offers on the page, in the menu's order."""
    sections = page_sections(page)
    return [
        item
        for item in MORE_MENU
        if item.action not in NOT_ON_PAGES
        and _PAGE_CHECKS.get(item.action, _anything)(page)
        and any(
            available(item.action, replace(page, section=section))
            for section in sections
        )
    ]


def section_of(page: Page, action: str) -> str | None:
    """The first of the page's sections that offers `action`."""
    for section in page_sections(page):
        if available(action, replace(page, section=section)):
            return section
    return None


class ManageItem(NamedTuple):
    """One entry of a record's Manage chapter: its action (a More
    command's, or DELETE_RECORD), its label and a line on what it does."""

    action: str
    label: str
    detail: str


#: A record's Manage chapter: what manages it as a file rather than as
#: part of the saga, each with what it does; Delete is last.
MANAGE: dict[str, str] = {
    "export_record": "Write it to a file that another saga, or this saga on "
    "another computer, can import.",
    "export_markdown": "Write its sheet as a Markdown file, for notes, a wiki "
    "or a message: the same copy and sheet as Print to PDF.",
    "update_record": "Read an export of it over it, for example after working "
    "on it elsewhere: shows what would change first, and keeps its place in "
    "this saga.",
    "edit_interests": "Tick the kinds of deed this character takes up: an "
    "interest left unticked (Knightly for a magus, Scholarly for a "
    "blacksmith) takes its actions off the Deeds chapter, A Season's Work "
    "and More.",
    "promote": "Write more of it down: a line becomes a sketch with a "
    "statblock, and a sketch a full record, In Creation, keeping everything "
    "it had.",
    "demote": "Keep less of it: a full record becomes a sketch, left out "
    "of seasons, ageing and upkeep, and a sketch a line. Nothing is deleted; the "
    "chapters it no longer shows keep what they hold.",
    "found_covenant": "Raise a new covenant on this ruin, as Winter Ruins "
    "does: it starts In Creation, sited here, and the ruin becomes its claim.",
    "begin_story": "Start this dormant story: its stages begin to come, the "
    "first due next season at the soonest.",
    "merge_doubles": "Make one record of each faction that shares its name "
    "with a character or creature: its attitudes, favours, links, words and "
    "memberships move to the character or creature.",
    "grow_story": "Make the chosen open story a threat of the Region, from "
    "its words; the story is marked Grown, naming the threat.",
    "take_up_tale": "Write a chapter of the threat's tale: what the troupe "
    "did, met or avoided, in its Diary and the troupe's covenants'.",
    "reveal": "Tell the players of it: they see it in lists, Find and the "
    "Atlas, and its name where a page names it. A dated line goes in the "
    "troupe's covenants' Diary.",
    "conceal": "Take it back: it is left out of everything the players read "
    "until you reveal it again, and the line its reveal wrote goes.",
    "assign_storyguide": "Take it as your story while it has no storyguide, "
    "or release or hand on one of yours: its storyguide alone reads its "
    "Secrets, and any other storyguide reads it as a player would.",
    "delay_threat": "Push the threat later or bring it sooner: its dated stages "
    "still to come move together, or it moves back or on along its track; "
    "the reason goes in its Diary.",
    DELETE_RECORD: "Remove it from the saga, after saying what happens to "
    "what it holds.",
}

#: The More commands a record's own page offers instead: in its Manage
#: chapter, or as its In Creation / In Play toggle and the Creation
#: Worksheet beside it.
ON_THE_PAGE = frozenset({*MANAGE, "toggle_mode", "creation_worksheet"})


def _managed(page: Page, action: str, detail: str) -> str:
    """A Manage entry's line, with Its Storyguide saying whose it is now."""
    if action != "assign_storyguide":
        return detail
    record = page.record_to_delete()
    who = viewing.storyguide_name(page.saga, viewing.storyguide_of(record, page.saga))
    return f"{detail} Now: {escape(who)}."


def manage_items(page: Page) -> list[ManageItem]:
    """What the page's Manage chapter offers, in order."""
    labels = {item.action: item.label for item in MORE_MENU}
    items = [
        ManageItem(action, labels[action], _managed(page, action, detail))
        for action, detail in MANAGE.items()
        if action != DELETE_RECORD and available(action, page)
    ]
    record = deletes(page)
    if record is not None:
        items.append(
            ManageItem(
                DELETE_RECORD,
                f"Delete {escape(record.name or '(unnamed)')}",
                MANAGE[DELETE_RECORD],
            )
        )
    return items


#: Edit Saga: in the saga page's Saga Settings, where the terminal's e
#: edits it.
EDIT_SAGA = MenuItem("e", "edit_saga", "Edit Saga")

# Where a page sets out what isn't a More or New action.
_OTHER_PLACES: dict[str, tuple[tuple[NodeKind, str], ...]] = {
    "edit_saga": ((NodeKind.SAGA, "Saga Settings"),),
}

#: Where a page sets each action out itself (the registry's, and the
#: page's own).
PLACES: dict[str, tuple[tuple[NodeKind, str], ...]] = {
    **more.PLACES,
    **_OTHER_PLACES,
}

#: The More actions a page offers nowhere: a section's or row's own button.
NOT_ON_PAGES = more.NOT_ON_PAGES


#: The saga page's Saga Management: each entry with what it does.
SAGA_MANAGEMENT: dict[str, str] = {
    "import_data": "Bring books, spells or records in from a file, such as "
    "another saga's export or a list of books.",
    "export_cult": "Write one of the saga's own Mystery Cults, its degrees "
    "and Scripts, to a file another saga can import.",
    "export_saga": "Write the whole saga, every record and what it holds, to "
    "one file that another saga, or this one on another computer, can import.",
    "export_pack": "Write chosen Tribunals, covenants, places and neighbours, "
    "with what goes with them, to a content pack another saga can import or "
    "start from.",
    "host_saga": "Let the players open the saga in a web browser on their own "
    "computers, over your private network, each signing in as one of Saga "
    "Content's Players.",
}


def management_note(action: str) -> str:
    """What Saga Management says beside `action` (plain text)."""
    if action == "stop_hosting":
        return hosting_forms.hosting_note()
    return SAGA_MANAGEMENT.get(action, "")


def lives_at(action: str, kind: NodeKind, spot: str) -> bool:
    """Whether PLACES puts `action` at `spot` on a `kind` page."""
    return (kind, spot) in PLACES.get(action, ())


#: Whether the page offers a placed action where `available`, which
#: answers for the terminal's New and More, doesn't say.
_PLACED_CHECKS: dict[str, Callable[[Page], bool]] = {
    "edit_saga": lambda page: page.kind == NodeKind.SAGA,
    "create_familiar": lambda page: familiar_binder(page) is not None,
    # The page's sections (PAGE_SECTIONS) leave This Season out.
    "labor_story": lambda page: available(
        "labor_story", replace(page, section="section-char-season")
    ),
    "invest_labor": lambda page: available(
        "invest_labor", replace(page, section="section-char-season")
    ),
    "grog_story_xp": lambda page: available(
        "grog_story_xp", replace(page, section="section-char-season")
    ),
    "plan_copying": lambda page: available(
        "plan_copying", replace(page, section="section-char-season")
    ),
    "clear_copying": lambda page: available(
        "clear_copying", replace(page, section="section-char-season")
    ),
    # A craftsman's sale of his finished goods.
    "sell_goods": lambda page: available(
        "sell_goods", replace(page, section="section-char-season")
    ),
    # An apothecary's searching and preserving.
    "apothecary_store": lambda page: available(
        "apothecary_store", replace(page, section="section-char-season")
    ),
    # The pilgrim's road (The Church).
    "pilgrimage": lambda page: available(
        "pilgrimage", replace(page, section="section-char-season")
    ),
    # Gaining and losing Virtues and Flaws in play: the page's sections
    # leave the Virtues & Flaws lists out.
    "change_virtues_flaws": lambda page: available(
        "change_virtues_flaws", replace(page, section="section-vf-virtues")
    ),
}


#: The section a placed spot stands for, for the checks that ask which
#: section focus is in: a desktop page has none focused.
SPOT_SECTIONS: dict[str, str] = {
    "Faith": FAITH_SECTION,
    "Reputations": "section-reputations",
    # The Deeds chapter's Reputation actions answer as on Reputations.
    deeds.SESSION: "section-reputations",
    "Health": "section-char-health",
    "Aging": "section-aging",
}


def _offered_at(page: Page, spot: str, action: str, offered: set[str]) -> bool:
    """Whether `action` is offered at `spot`: as the page offers it, or as
    it would be with focus in the section the spot stands for (its More
    section, or the spot's own)."""
    if action in offered:
        return True
    section = MORE_SECTIONS.get(action) or SPOT_SECTIONS.get(spot)
    return section is not None and available(action, replace(page, section=section))


def placed(page: Page, spot: str) -> list[MenuItem]:
    """The actions the page offers at `spot` (a chapter's or section's
    name, or "New" / "More"), in PLACES's order."""
    items = {item.action: item for item in (EDIT_SAGA, *NEW_MENU, *MORE_MENU)}
    offered = {i.action for i in (*new_items(page), *more_items(page))}
    return [
        items[action]
        for action, places in PLACES.items()
        if (page.kind, spot) in places
        and (
            # A check of its own still answers to who sits here.
            (
                viewing.offers(action)
                and page.player_may(action)
                and _PLACED_CHECKS[action](page)
            )
            if action in _PLACED_CHECKS
            else _offered_at(page, spot, action, offered)
        )
    ]


def new_items(page: Page) -> list[MenuItem]:
    """What New can make from the page."""
    return [item for item in NEW_MENU if available(item.action, page)]


def deletes(page: Page) -> Record | None:
    """The record Delete deletes on the page, if any."""
    if page.kind is None or not available(DELETE_RECORD, page):
        return None
    return page.record_to_delete()


def command(page: Page, action: str) -> Command:
    """The first step of the menu entry `action` on the page."""
    saga = page.saga
    if action == DELETE_RECORD:
        record = deletes(page)
        if record is None:
            return Refuse("Delete", "Nothing here to delete.")
        return delete_record(saga, record)
    builder = _COMMANDS.get(action)
    if builder is None:
        return Refuse("More", "That isn't available here.")
    return builder(page)


# Give Silver gives from the purse of the section that offers it, which
# the page's placement finds.


def _silver_command(page: Page) -> Command:
    section = section_of(page, "give_silver")
    purse = silver_purse(replace(page, section=section))
    if purse is None:
        return Refuse("Give Silver", "No silver to give here.")
    return giving.give(page.saga, giving.SILVER, purse)


#: Each action's first step: the registry's, the page's own, and Give
#: Silver's.
_COMMANDS: dict[str, Callable[[Page], Command]] = {
    **more.STEPS,
    **OTHER_STEPS,
    "give_silver": _silver_command,
}
