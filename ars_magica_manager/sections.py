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
#: The non-Hermetic traditions the saga offers (Books tab).
TRADITIONS_SECTION = "section-traditions"
#: The Goods catalog and the saga's own goods (Goods tab; forms/goods.py).
GOODS_SECTION = "section-content-goods"

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
#: A Warping laboratory's Personality Traits (forms/trait.py).
LAB_TRAITS_SECTION = "section-lab-personality-traits"
#: What a laboratory's magic items give it (forms/lab_item.py).
LAB_ITEMS_SECTION = "section-lab-magic-items"

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
#: A character's, covenant's or laboratory's Connections: the records
#: that point at it or that it sits in (connections.py), read-only.
CONNECTIONS_SECTION = "section-connections"
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
#: Normandy's vis tenure and Tourney, Transylvania's five covenants,
#: Hibernia's ambassadors and treaties, the Greater Alps's ostracism.
GILDS_SECTION = "section-trib-gilds"
TOKENS_SECTION = "section-trib-tokens"
ARCHAI_SECTION = "section-trib-archai"
TENURE_SECTION = "section-trib-tenure"
TOURNEY_SECTION = "section-trib-tourney"
PRIVILEGES_SECTION = "section-trib-privileges"
AMBASSADORS_SECTION = "section-trib-ambassadors"
TREATIES_SECTION = "section-trib-treaties"
OSTRACISM_SECTION = "section-trib-ostracism"
#: The Grand Tribunal's delegates (tribunal_packages.grand).
DELEGATES_SECTION = "section-trib-delegates"
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
#: The troupe's covenants' open Story Events, together (open_stories).
REGION_STORIES_SECTION = "section-region-stories"
#: A neighbour's sheet's top panel.
NEIGHBOUR_INFO_SECTION = "section-nb-info"
#: The lists a kind of neighbour adds: a lord's castles, Gratitude and
#: battles, a town's guilds and fairs.
CASTLES_SECTION = "section-nb-castles"
GRATITUDE_SECTION = "section-nb-gratitude"
BATTLES_SECTION = "section-nb-battles"
#: The sieges a lord holds out in or lays.
LORD_SIEGES_SECTION = "section-nb-sieges"
GUILDS_SECTION = "section-nb-guilds"
FAIRS_SECTION = "section-nb-fairs"
#: A town's Charter tab (its lords, terms, what the charter gives, its
#: citizens, and its size and people), its Guilds tab (the guilds and the
#: saga's characters in them) and its Court tab (cases and sentences).
CHARTER_LORDS_SECTION = "section-nb-charter-lords"
CHARTER_TERMS_SECTION = "section-nb-charter-terms"
CHARTER_GIVES_SECTION = "section-nb-charter-gives"
CITIZENS_SECTION = "section-nb-citizens"
TOWN_PEOPLE_SECTION = "section-nb-town-people"
GUILD_MEMBERS_SECTION = "section-nb-guild-members"
COURT_CASES_SECTION = "section-nb-court-cases"
SENTENCES_SECTION = "section-nb-sentences"
#: A covenant's Charter of Covenant (covenant_charter.py): the charter
#: itself (its name, preamble and seals) and its clauses, on its Charter
#: tab.
CHARTER_SECTION = "section-cov-charter"
CLAUSES_SECTION = "section-cov-clauses"
#: The magi staying at a covenant as its guests (guest_stays).
GUESTS_SECTION = "section-cov-guests"
#: A covenant's own town charter (the Chartered Town Boon) and the towns
#: it charters (the Charter Lord Hook), on its Charter tab too.
COV_CHARTER_LORDS_SECTION = "section-cov-charter-lords"
COV_CHARTER_TERMS_SECTION = "section-cov-charter-terms"
CHARTERED_TOWNS_SECTION = "section-cov-chartered-towns"
#: The Manors tab of a lord or a covenant (manors.py): its manors, its
#: kennels, mews and stables, a lord's household, and a covenant's check
#: of its manors beside its income.
MANORS_SECTION = "section-manors"
ESTABLISHMENTS_SECTION = "section-establishments"
HOUSEHOLD_SECTION = "section-household"
MANOR_CHECK_SECTION = "section-manor-check"
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
#: The saga's Conflicts: its fights and its sieges.
CONFLICTS_INFO_SECTION = "section-conflicts-info"
FIGHTS_SECTION = "section-fights"
CONFLICT_BATTLES_SECTION = "section-conflict-battles"
SIEGES_SECTION = "section-sieges"
#: The Bestiary's list of creatures, and a creature's sheet: its top
#: panel, Characteristics, description, Virtues and Flaws (Qualities and
#: Inferiorities among them), traits, combat, health, Abilities, powers
#: and the vis in its body.
BESTIARY_INFO_SECTION = "section-bestiary-info"
BESTIARY_SECTION = "section-bestiary"
CREATURE_INFO_SECTION = "section-cr-info"
CREATURE_CHARACTERISTICS_SECTION = "section-cr-characteristics"
CREATURE_DESCRIPTION_SECTION = "section-cr-description"
CREATURE_VF_SECTION = "section-cr-virtues-flaws"
CREATURE_TRAITS_SECTION = "section-cr-personality-traits"
CREATURE_REPUTATIONS_SECTION = "section-cr-reputations"
CREATURE_ATTACKS_SECTION = "section-cr-attacks"
CREATURE_HEALTH_SECTION = "section-cr-health"
CREATURE_ABILITIES_SECTION = "section-cr-abilities"
CREATURE_POWERS_SECTION = "section-cr-powers"
CREATURE_VIS_SECTION = "section-cr-vis"
#: The saga's Seasons sheet: its top panel, what is coming, and the
#: seasons recorded; and a covenant's own Ahead, on its Seasons tab.
SEASONS_INFO_SECTION = "section-seasons-info"
AHEAD_SECTION = "section-ahead"
SEASONS_RECORDED_SECTION = "section-seasons-recorded"
COV_AHEAD_SECTION = "section-cov-ahead"
#: A character's Planning tab: the seasons after the current one.
CHAR_AHEAD_SECTION = "section-char-ahead"
#: A character's Planning tab: their seasons as a calendar, a year a line.
CHAR_CALENDAR_SECTION = "section-char-calendar"
WORLD_TURNS_SECTION = "section-world-turns"
#: A Tribunal's meeting being held (or the next): its order of
#: business, who is in the hall, and the vote on the case in hand.
BUSINESS_SECTION = "section-meeting-business"
ATTENDANCE_SECTION = "section-meeting-attendance"
VOTE_SECTION = "section-meeting-vote"
#: A record's Secrets chapter (forms/secrets.py): the same section on a
#: covenant's, character's, Tribunal's, neighbour's and creature's sheet.
SECRETS_SECTION = "section-secrets"
#: A character's supernatural powers (forms.power).
POWERS_SECTION = "section-char-powers"
#: The supernatural effects on a character all the time
#: (forms.constant_effect).
CONSTANT_EFFECTS_SECTION = "section-char-constant-effects"
#: A character's agents (forms.agents): the people he controls through
#: personal bonds, on their own tab.
AGENTS_SECTION = "section-char-agents"
#: A place's Tomb tab (tombs.py, Lands of the Nile): the tomb, its
#: curses, its talismans and wards, and its traps.
TOMB_SECTION = "section-nb-tomb"
TOMB_CURSES_SECTION = "section-nb-tomb-curses"
TOMB_WARDS_SECTION = "section-nb-tomb-wards"
TOMB_TRAPS_SECTION = "section-nb-tomb-traps"
#: The Rhine's Great Library tab (tribunal_packages.rhine_library): its
#: rule of access, each magus's credit, and the searches made.
LIBRARY_RULES_SECTION = "section-trib-library"
LIBRARY_CREDIT_SECTION = "section-trib-library-credit"
LIBRARY_SEARCHES_SECTION = "section-trib-library-searches"
#: Saga Content's Mystery Cults tab (forms/mystery_cults.py): the saga's
#: own cults, the chosen one, its degrees, and the chosen degree's Script.
CULTS_SECTION = "section-content-cults"
CULT_SECTION = "section-content-cult"
CULT_DEGREES_SECTION = "section-content-cult-degrees"
CULT_SCRIPT_SECTION = "section-content-cult-scripts"
#: A character's Religion tab (forms.religion): his faith and what it lets
#: him do, then (forms.church) his grade in holy orders, his ordinations,
#: his petitions to the Church and his canon-court cases.
FAITH_SECTION = "section-char-faith"
ORDERS_SECTION = "section-char-orders"
ORDINATIONS_SECTION = "section-char-ordinations"
PETITIONS_SECTION = "section-char-petitions"
CANON_SECTION = "section-char-canon"

#: A covenant's Projects tab (hermetic_projects.py, Hermetic Projects): its
#: projects, the shown one's tower, its works and its craft devices.
PROJECTS_SECTION = "section-cov-projects"
#: A covenant's History tab (covenant_history.py): its timeline and its
#: eras.
HISTORY_SECTION = "section-cov-history"
ERAS_SECTION = "section-cov-eras"
HISTORY_VIEW_SECTION = "section-cov-history-view"
TOWER_SECTION = "section-cov-tower"
PROJECT_WORKS_SECTION = "section-cov-tower-works"
PROJECT_DEVICES_SECTION = "section-cov-tower-devices"
#: A Tribunal's Arguments tab (Transforming Mythic Europe pp. 27-35): its
#: arguments, the chosen one, and that one's texts.
ARGUMENTS_SECTION = "section-trib-arguments"
ARGUMENT_SECTION = "section-trib-argument"
ARGUMENT_TEXTS_SECTION = "section-trib-argument-texts"
#: A lord's Marriages tab (marriages.py, Lords of Men pp. 10-11): the
#: marriages joining his house, and the terms of the one that stands.
MARRIAGES_SECTION = "section-nb-marriages"
MARRIAGE_TERMS_SECTION = "section-nb-marriage"

#: A covenant's Menagerie, a Hermetic Project (menagerie.py, Hermetic
#: Projects pp. 119-142): the menagerie shown, its beasts, its breedings.
MENAGERIE_SECTION = "section-cov-menagerie"
BEASTS_SECTION = "section-cov-menagerie-beasts"
BREEDINGS_SECTION = "section-cov-menagerie-breedings"
#: A covenant's staged Hermetic Project (staged_projects.py, Hermetic
#: Projects pp. 9-118): the project shown, its stages and their works.
STAGED_SECTION = "section-cov-staged"
STAGED_STAGES_SECTION = "section-cov-staged-stages"
STAGE_WORKS_SECTION = "section-cov-staged-works"
#: A Criamon magus's The Enigma tab (forms.criamon, HoH:MC pp. 50-73): his
#: path, its stations, and his stigmata.
CRIAMON_PATH_SECTION = "section-char-criamon-path"
CRIAMON_STATIONS_SECTION = "section-char-criamon-stations"
STIGMATA_SECTION = "section-char-stigmata"
#: A character's deep covers and personae (forms/covers.py).
COVERS_SECTION = "section-char-covers"

CORE_SECTIONS: dict[str, frozenset[str]] = {
    POWERS_SECTION: frozenset({"add", "edit", "remove"}),
    CONSTANT_EFFECTS_SECTION: frozenset({"add", "edit", "remove"}),
    COVERS_SECTION: frozenset({"add", "edit", "remove"}),
    AGENTS_SECTION: frozenset({"add", "edit", "remove"}),
    LAB_TRAITS_SECTION: frozenset({"add", "edit", "remove"}),
    LAB_ITEMS_SECTION: frozenset({"add", "edit", "remove"}),
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
    PRIVILEGES_SECTION: frozenset({"add", "edit", "remove"}),
    AMBASSADORS_SECTION: frozenset({"add", "edit", "remove"}),
    TREATIES_SECTION: frozenset({"add", "edit", "remove"}),
    OSTRACISM_SECTION: frozenset({"add", "edit", "remove"}),
    DELEGATES_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_LORDS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_CHURCH_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_UNIVERSITIES_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_FACTIONS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_THREATS_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_PLACES_SECTION: frozenset({"add", "edit", "remove"}),
    REGION_STORIES_SECTION: frozenset({"edit"}),
    NEIGHBOUR_INFO_SECTION: frozenset({"edit"}),
    CASTLES_SECTION: frozenset({"add", "edit", "remove"}),
    GRATITUDE_SECTION: frozenset({"add", "edit", "remove"}),
    BATTLES_SECTION: frozenset({"add", "edit", "remove"}),
    GUILDS_SECTION: frozenset({"add", "edit", "remove"}),
    FAIRS_SECTION: frozenset({"add", "edit", "remove"}),
    CHARTER_LORDS_SECTION: frozenset({"add", "edit", "remove"}),
    CHARTER_TERMS_SECTION: frozenset({"edit"}),
    CHARTER_GIVES_SECTION: frozenset({"edit"}),
    CITIZENS_SECTION: frozenset({"add", "edit", "remove"}),
    TOWN_PEOPLE_SECTION: frozenset({"edit"}),
    GUILD_MEMBERS_SECTION: frozenset({"add", "edit", "remove"}),
    COURT_CASES_SECTION: frozenset({"add", "edit", "remove"}),
    COV_CHARTER_LORDS_SECTION: frozenset({"add", "edit", "remove"}),
    COV_CHARTER_TERMS_SECTION: frozenset({"edit"}),
    CHARTER_SECTION: frozenset({"edit"}),
    CLAUSES_SECTION: frozenset({"add", "edit", "remove"}),
    GUESTS_SECTION: frozenset({"edit"}),
    MANORS_SECTION: frozenset({"add", "edit", "remove"}),
    ESTABLISHMENTS_SECTION: frozenset({"add", "edit", "remove"}),
    HOUSEHOLD_SECTION: frozenset({"edit"}),
    MANOR_CHECK_SECTION: frozenset({"edit"}),
    RELICS_SECTION: frozenset({"add", "edit", "remove"}),
    FACULTIES_SECTION: frozenset({"add", "edit", "remove"}),
    MASTERS_SECTION: frozenset({"add", "edit", "remove"}),
    STAGES_SECTION: frozenset({"add", "edit", "remove"}),
    LEVELS_SECTION: frozenset({"add", "edit", "remove"}),
    EFFECTS_SECTION: frozenset({"add", "edit", "remove"}),
    TRIGGERS_SECTION: frozenset({"add", "edit", "remove"}),
    TABLES_SECTION: frozenset({"add", "edit", "remove"}),
    DIARY_SECTION: frozenset({"add", "edit", "remove"}),
    BESTIARY_SECTION: frozenset({"add", "edit", "remove"}),
    FIGHTS_SECTION: frozenset({"add", "edit", "remove"}),
    CONFLICT_BATTLES_SECTION: frozenset({"add", "edit", "remove"}),
    LORD_SIEGES_SECTION: frozenset({"add", "edit", "remove"}),
    SIEGES_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_INFO_SECTION: frozenset({"edit"}),
    CREATURE_CHARACTERISTICS_SECTION: frozenset({"edit"}),
    CREATURE_DESCRIPTION_SECTION: frozenset({"edit"}),
    CREATURE_VF_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_TRAITS_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_REPUTATIONS_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_ATTACKS_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_HEALTH_SECTION: frozenset({"edit"}),
    CREATURE_ABILITIES_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_POWERS_SECTION: frozenset({"add", "edit", "remove"}),
    CREATURE_VIS_SECTION: frozenset({"add", "edit", "remove"}),
    SEASONS_INFO_SECTION: frozenset({"edit"}),
    AHEAD_SECTION: frozenset({"add", "edit", "remove"}),
    COV_AHEAD_SECTION: frozenset({"add", "edit", "remove"}),
    WORLD_TURNS_SECTION: frozenset({"remove"}),
    BUSINESS_SECTION: frozenset({"edit", "remove"}),
    ATTENDANCE_SECTION: frozenset({"edit"}),
    VOTE_SECTION: frozenset({"edit"}),
    SECRETS_SECTION: frozenset({"edit"}),
    GOODS_SECTION: frozenset({"add", "edit", "remove"}),
    # A place's Tomb tab (Lands of the Nile).
    TOMB_SECTION: frozenset({"edit"}),
    TOMB_CURSES_SECTION: frozenset({"add", "edit", "remove"}),
    TOMB_WARDS_SECTION: frozenset({"add", "edit", "remove"}),
    TOMB_TRAPS_SECTION: frozenset({"add", "edit", "remove"}),
    # The Rhine's Great Library (Guardians of the Forests).
    LIBRARY_CREDIT_SECTION: frozenset({"add", "edit", "remove"}),
    LIBRARY_SEARCHES_SECTION: frozenset({"add", "edit", "remove"}),
    # Saga Content's Mystery Cults.
    CULTS_SECTION: frozenset({"add", "edit", "remove"}),
    CULT_SECTION: frozenset({"edit"}),
    CULT_DEGREES_SECTION: frozenset({"add", "edit", "remove"}),
    CULT_SCRIPT_SECTION: frozenset({"add", "edit", "remove"}),
    # A character's faith (Edit Religion), and a cleric's career (The Church).
    FAITH_SECTION: frozenset({"edit"}),
    ORDERS_SECTION: frozenset({"edit"}),
    ORDINATIONS_SECTION: frozenset({"add", "edit", "remove"}),
    PETITIONS_SECTION: frozenset({"add", "edit", "remove"}),
    CANON_SECTION: frozenset({"add", "edit", "remove"}),
    # A covenant's Hermetic Projects.
    PROJECTS_SECTION: frozenset({"add", "edit", "remove"}),
    HISTORY_SECTION: frozenset({"add", "edit", "remove"}),
    ERAS_SECTION: frozenset({"add", "edit", "remove"}),
    HISTORY_VIEW_SECTION: frozenset({"edit"}),
    TOWER_SECTION: frozenset({"edit"}),
    PROJECT_WORKS_SECTION: frozenset({"add", "edit", "remove"}),
    PROJECT_DEVICES_SECTION: frozenset({"add", "edit", "remove"}),
    # A Tribunal's arguments and their texts (Transforming Mythic Europe).
    ARGUMENTS_SECTION: frozenset({"add", "edit", "remove"}),
    ARGUMENT_SECTION: frozenset({"edit"}),
    ARGUMENT_TEXTS_SECTION: frozenset({"add", "edit", "remove"}),
    # A lord's marriages and the terms of the one that stands.
    MARRIAGES_SECTION: frozenset({"add", "edit", "remove"}),
    MARRIAGE_TERMS_SECTION: frozenset({"edit"}),
    # A covenant's Menagerie (Hermetic Projects).
    MENAGERIE_SECTION: frozenset({"edit"}),
    BEASTS_SECTION: frozenset({"add", "edit", "remove"}),
    BREEDINGS_SECTION: frozenset({"add", "edit", "remove"}),
    # A covenant's staged project (Hermetic Projects).
    STAGED_SECTION: frozenset({"edit"}),
    STAGED_STAGES_SECTION: frozenset({"add", "edit", "remove"}),
    STAGE_WORKS_SECTION: frozenset({"add", "edit", "remove"}),
    # A Criamon magus's path and stigmata (HoH:MC).
    CRIAMON_PATH_SECTION: frozenset({"edit"}),
    STIGMATA_SECTION: frozenset({"add", "edit", "remove"}),
}
