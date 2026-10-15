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

#: Sections whose Add, Edit and Delete come straight from the core
#: (commands.SectionOps): the sheet showing one names the ops for its
#: record, and each front-end runs their steps the same way.
ATTITUDE_SECTION = "section-attitudes"
FAVOURS_SECTION = "section-favours"
LINKS_SECTION = "section-links"
MAGI_SECTION = "section-cov-magi"
WHAT_MATTERS_SECTION = "section-cov-what-matters"
#: A Tribunal sheet's top panel.
TRIBUNAL_INFO_SECTION = "section-trib-info"
#: Its roster of covenants, where the proxies each holds are entered.
ROSTER_SECTION = "section-trib-roster"
#: Its magi of note (worked out, not edited here).
TRIB_MAGI_SECTION = "section-trib-magi"
#: Its docket: the cases for the next meeting, and those past.
CASES_SECTION = "section-trib-cases"
PAST_CASES_SECTION = "section-trib-past"
#: Its Peripheral Code, treasury and Diary.
CODE_SECTION = "section-trib-code"
TREASURY_SECTION = "section-trib-treasury"
TRIB_DIARY_SECTION = "section-trib-diary"
#: The lists Tribunal packages add (tribunal_packages): the Rhine's
#: Gilds, the Theban Tribunal's tokens and shards and its archai,
#: Normandy's vis tenure and Tourney.
GILDS_SECTION = "section-trib-gilds"
TOKENS_SECTION = "section-trib-tokens"
ARCHAI_SECTION = "section-trib-archai"
TENURE_SECTION = "section-trib-tenure"
TOURNEY_SECTION = "section-trib-tourney"
#: The Region's top panel, and the covenants the troupe doesn't play.
REGION_INFO_SECTION = "section-region-info"
REGION_COVENANTS_SECTION = "section-region-covenants"
#: The Region's neighbours, a section per group (neighbours.GROUPS).
REGION_LORDS_SECTION = "section-region-lords"
REGION_CHURCH_SECTION = "section-region-church"
REGION_UNIVERSITIES_SECTION = "section-region-universities"
REGION_FACTIONS_SECTION = "section-region-factions"
REGION_THREATS_SECTION = "section-region-threats"
REGION_PLACES_SECTION = "section-region-places"
#: A neighbour's sheet's top panel.
NEIGHBOUR_INFO_SECTION = "section-nb-info"
#: The lists a kind of neighbour adds: a lord's castles and Gratitude, a
#: town's guilds and fairs.
CASTLES_SECTION = "section-nb-castles"
GRATITUDE_SECTION = "section-nb-gratitude"
GUILDS_SECTION = "section-nb-guilds"
FAIRS_SECTION = "section-nb-fairs"
#: A church's relics; a university's faculties and masters.
RELICS_SECTION = "section-nb-relics"
FACULTIES_SECTION = "section-nb-faculties"
MASTERS_SECTION = "section-nb-masters"
#: A threat's stages.
STAGES_SECTION = "section-nb-stages"
#: A place's regio levels and effects.
LEVELS_SECTION = "section-nb-levels"
EFFECTS_SECTION = "section-nb-effects"
#: A place's triggers, roll tables and diary.
TRIGGERS_SECTION = "section-nb-triggers"
TABLES_SECTION = "section-nb-tables"
DIARY_SECTION = "section-nb-place-diary"
#: The saga's Seasons sheet: its top panel, what is coming, and the
#: seasons recorded; and a covenant's own Ahead, on its Seasons tab.
SEASONS_INFO_SECTION = "section-seasons-info"
AHEAD_SECTION = "section-ahead"
SEASONS_RECORDED_SECTION = "section-seasons-recorded"
COV_AHEAD_SECTION = "section-cov-ahead"
WORLD_TURNS_SECTION = "section-world-turns"
#: A Tribunal's meeting being held (or the next): its order of
#: business, and who is in the hall.
BUSINESS_SECTION = "section-meeting-business"
ATTENDANCE_SECTION = "section-meeting-attendance"
CORE_SECTIONS: dict[str, frozenset[str]] = {
    ATTITUDE_SECTION: frozenset({"add", "edit", "remove"}),
    FAVOURS_SECTION: frozenset({"add", "edit", "remove"}),
    LINKS_SECTION: frozenset({"add", "edit", "remove"}),
    MAGI_SECTION: frozenset({"add", "edit", "remove"}),
    WHAT_MATTERS_SECTION: frozenset({"edit"}),
    TRIBUNAL_INFO_SECTION: frozenset({"edit"}),
    ROSTER_SECTION: frozenset({"edit"}),
    CASES_SECTION: frozenset({"add", "edit", "remove"}),
    PAST_CASES_SECTION: frozenset({"edit", "remove"}),
    CODE_SECTION: frozenset({"add", "edit", "remove"}),
    TREASURY_SECTION: frozenset({"add", "edit", "remove"}),
    TRIB_DIARY_SECTION: frozenset({"add", "edit", "remove"}),
    GILDS_SECTION: frozenset({"add", "edit", "remove"}),
    TOKENS_SECTION: frozenset({"add", "edit", "remove"}),
    ARCHAI_SECTION: frozenset({"add", "edit", "remove"}),
    TENURE_SECTION: frozenset({"add", "edit", "remove"}),
    TOURNEY_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_LORDS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_CHURCH_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_UNIVERSITIES_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_FACTIONS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_THREATS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_PLACES_SECTION: frozenset({"add", "edit", "remove"}),
    NEIGHBOUR_INFO_SECTION: frozenset({"edit"}),
    CASTLES_SECTION: frozenset({"add", "edit", "remove"}),
    GRATITUDE_SECTION: frozenset({"add", "edit", "remove"}),
    GUILDS_SECTION: frozenset({"add", "edit", "remove"}),
    FAIRS_SECTION: frozenset({"add", "edit", "remove"}),
    RELICS_SECTION: frozenset({"add", "edit", "remove"}),
    FACULTIES_SECTION: frozenset({"add", "edit", "remove"}),
    MASTERS_SECTION: frozenset({"add", "edit", "remove"}),
    STAGES_SECTION: frozenset({"add", "edit", "remove"}),
    LEVELS_SECTION: frozenset({"add", "edit", "remove"}),
    EFFECTS_SECTION: frozenset({"add", "edit", "remove"}),
    TRIGGERS_SECTION: frozenset({"add", "edit", "remove"}),
    TABLES_SECTION: frozenset({"add", "edit", "remove"}),
    DIARY_SECTION: frozenset({"add", "edit", "remove"}),
    SEASONS_INFO_SECTION: frozenset({"edit"}),
    AHEAD_SECTION: frozenset({"add", "edit", "remove"}),
    COV_AHEAD_SECTION: frozenset({"add", "edit", "remove"}),
    WORLD_TURNS_SECTION: frozenset({"remove"}),
    BUSINESS_SECTION: frozenset({"edit", "remove"}),
    ATTENDANCE_SECTION: frozenset({"edit"}),
}
