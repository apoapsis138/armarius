"""The ids of the sheets' sections that actions refer to.

A section id names one part of a sheet (a list, a panel, a tab). Both what
a front-end draws and what actions.py says can be done there use these
ids, so a front-end that draws a section under this id gets its add /
edit / delete and More actions for free."""

from __future__ import annotations

#: The Spells view's list section (a / e / d act on the saga's own spells).
SPELL_SECTION = "section-spells"

#: The House Rules view's list section (a / e / d act on user-made entries).
HOUSE_RULES_SECTION = "section-house-rules"

#: The Players view's list section (a / e / d act on the saga's players).
PLAYERS_SECTION = "section-players"

#: The Saga Content sheet's sections.
BOOKS_SECTION = "section-books-in-play"
SOURCES_SECTION = "section-saga-sources"
CATALOGS_SECTION = "section-catalogs"
HIDDEN_SECTION = "section-hidden-entries"

#: The covenant Library tab's sections, where More's Import puts books into the
#: covenant's library.
LIBRARY_SECTIONS: frozenset[str] = frozenset(
    {"section-lib-summary", "section-lib-books"}
)

#: The Enchanted Devices section of each sheet, and the kind of
#: holder whose devices it lists.
DEVICE_SECTIONS: dict[str, str] = {
    "section-char-devices": "character",
    "section-lab-devices": "laboratory",
    "section-cov-devices": "covenant",
}

#: The laboratory's Lab Texts database: a book list of its own.
LAB_TEXTS_SECTION = "section-lab-texts"

#: Section ids of every book list; 'a' in any of them adds a book, and
#: e / d act on books everywhere but the read-only Summary.
BOOK_SECTIONS: frozenset[str] = frozenset(
    {
        "section-lib-summary",
        "section-lib-books",
        "section-lab-books",
        "section-books",
        "section-unassigned-books",
        LAB_TEXTS_SECTION,
    }
)

#: The lab's Virtues and Flaws sections: either refreshes both lists and
#: their shared details panel.
LAB_VF_SECTIONS = ("section-lab-vf-virtues", "section-lab-vf-flaws")

#: The scored-trait lists (Personality Traits and Reputations) of the
#: character, familiar and covenant sheets.
TRAIT_SECTIONS: tuple[str, ...] = (
    "section-personality-traits",
    "section-reputations",
    "section-fam-personality-traits",
    "section-fam-reputations",
    "section-cov-reputations",
)

#: The sections whose chosen row Give hands to another record, and what
#: kind of thing (a giving.GIVERS key) each lists.
GIVE_SECTIONS: dict[str, str] = {
    "section-raw-vis-hermetic": "vis",
    "section-raw-vis-inventory": "vis",
    "section-lab-raw-vis": "vis",
    "section-pos-vis_store": "vis",
    **{
        section: "book"
        for section in BOOK_SECTIONS
        if section not in ("section-lib-summary", "section-unassigned-books")
    },
    **dict.fromkeys(DEVICE_SECTIONS, "device"),
    "section-inventory": "gear",
    "section-pos-weapon": "gear",
    "section-pos-armor": "gear",
    "section-pos-item": "gear",
}

#: Where Give Silver gives from, and whose purse it is: a character's
#: Personal Gear, a covenant's Wealth.
SILVER_SECTIONS: dict[str, str] = {
    "section-inventory": "character",
    "section-eco-wealth": "covenant",
}
