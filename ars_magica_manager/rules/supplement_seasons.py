"""Seasonal activities from the supplements, planned on
the character sheet.

Each gives experience like a study season: a Source Quality in the Ability
(or Art) chosen, the rule's fixed figure or, where the rule depends on the
story (a church's aura, a sermon's Aesthetic Quality, a book's Quality), the
one the storyguide gives, typed on the plan. What else a season does (Labor
Points, a Mystery Virtue, a pilgrimage's progress...) is written in the
Diary for the troupe; the few with a mechanical side effect say so below.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import activity_groups as groups

_CH = "(https://www.redcap.org/page/{})"
SOURCE = "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, pp. 373-392"
COVENANTS = "Covenants, Chapter Seven: Library, pp. 84-102"
CHURCH = "The Church " + _CH.format("The_Church")
CITY_GUILD = "City & Guild " + _CH.format("City_%26_Guild")
ACADEME = "Art & Academe " + _CH.format("Art_%26_Academe_Open_Content")
MYSTERIES = "The Mysteries: Revised Edition " + _CH.format(
    "The_Mysteries:_Revised_Edition"
)
SOCIETATES = "Houses of Hermes: Societates " + _CH.format(
    "Houses_of_Hermes:_Societates"
)
LORDS = "Lords of Men " + _CH.format("Lords_of_Men")
DE_INITIATION = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Mystery Initiation, "
    "pp. 387-389"
)
DE_TAMING = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Taming Animals "
    "(Training Creatures), pp. 384-386"
)


#: Each source's book, as sourcebooks.SOURCEBOOKS abbreviates it.
_BOOKS: dict[str, str] = {
    SOURCE: "DE",
    DE_TAMING: "DE",
    DE_INITIATION: "DE",
    COVENANTS: "Covenants",
    CHURCH: "TC",
    CITY_GUILD: "C&G",
    ACADEME: "A&A",
    MYSTERIES: "TMRE",
    SOCIETATES: "HoH:S",
    LORDS: "LoM",
}


@dataclass(frozen=True)
class SimpleActivity:
    """One supplement activity: its Source Quality (None: typed, as `hint`
    says), who may plan it, and the story it belongs to."""

    key: str
    label: str
    summary: str
    source: str
    story: str
    quality: int | None = 2
    hint: str = ""
    who: tuple[str, ...] = ("magus", "companion", "mythic companion")
    #: No experience (a season spent, logged in the Diary).
    no_xp: bool = False
    #: Faith Points gained.
    faith: int = 0
    #: No longer offered (another activity does it now); kept so an older
    #: plan still loads and says what to plan instead.
    retired: bool = False
    #: What the season is for (activity_groups), as the picker groups it.
    group: str = ""

    @property
    def book(self) -> str:
        """The sourcebook (sourcebooks.SOURCEBOOKS abbreviation) the activity
        comes from: offered only while the saga has it in play."""
        return _BOOKS[self.source]


_C = ("companion", "mythic companion")
_M = ("magus",)

ACTIVITIES: tuple[SimpleActivity, ...] = (
    # More study sources.
    SimpleActivity(
        "study_significato",
        "Study a significato",
        "A mystical event studied like vis: the storyguide's Source Quality "
        "(a stress die + the aura).",
        COVENANTS,
        "913",
        None,
        "a stress die + the aura, as for vis",
        _M,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "study_realia",
        "Study a realia collection",
        "Read like a tractatus: its Quality.",
        COVENANTS,
        "913",
        None,
        "the collection's Quality",
        group=groups.STUDY,
    ),
    SimpleActivity(
        "read_commentary",
        "Read a commentary, florilegium or glossed book",
        "Retired: Read a book adds a commentary's, florilegium's or gloss's "
        "bonus itself.",
        COVENANTS,
        "913",
        None,
        "the book's Quality + the opus bonus",
        retired=True,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "record_lectures",
        "Record a teacher's lectures",
        "A scribe's season: a tractatus of Quality = the teacher's "
        "Communication + Scribe / 2. Exposure 2 in Profession: Scribe.",
        ACADEME,
        "913",
        group=groups.WRITING,
    ),
    SimpleActivity(
        "inspeximus",
        "Write an inspeximus",
        "Annotating your own summa: its Level rises by (your score now - "
        "your score when you wrote it) / 3, up to half your score.",
        COVENANTS,
        "913",
        group=groups.WRITING,
    ),
    SimpleActivity(
        "bind_catalog",
        "Bind a library catalog",
        "A season and 1 pawn of Vim: the catalog becomes an Arcane Connection "
        "to the library and each book in it.",
        COVENANTS,
        "913",
        who=_M,
        group=groups.WRITING,
    ),
    SimpleActivity(
        "library_research",
        "Library research",
        "A season searching lab notes or records: Intelligence + the Ability "
        "+ the library's research bonus against the storyguide's Ease "
        "Factor (Exposure 2 in the Ability used).",
        COVENANTS,
        "913",
        group=groups.STUDY,
    ),
    # Mysteries and House activities.
    SimpleActivity(
        "undergo_initiation",
        "Undergo an Initiation",
        "The Initiate's whole season: the Mystery Virtue, and any Ordeal "
        "Flaw, are added when the Initiation succeeds.",
        DE_INITIATION,
        "918",
        no_xp=True,
        group=groups.MYSTERIES,
    ),
    SimpleActivity(
        "mystagogue",
        "Act as Mystagogue",
        "Leading an Initiation (a season when the Script needs it): Exposure "
        "2 in the Mystery's Lore.",
        MYSTERIES,
        "918",
        group=groups.MYSTERIES,
    ),
    SimpleActivity(
        "quest_season",
        "Serve a Mystagogue / Quest season",
        "A season toward an Initiation Script's bonus: Exposure 2.",
        MYSTERIES,
        "918",
        group=groups.MYSTERIES,
    ),
    SimpleActivity(
        "house_work",
        "House seasonal work",
        "House-specific work (Fenicil rituals, Criamon Path stations, Bjornaer "
        "heartbeast...): the storyguide's Source Quality.",
        SOCIETATES,
        "918",
        None,
        "as the House's rule gives (Exposure 2 if nothing else)",
        _M,
        group=groups.ORDER,
    ),
    SimpleActivity(
        "tribunal_duties",
        "Tribunal or Redcap duties",
        "A season of Order business or Redcap rounds: Exposure 2.",
        SOCIETATES,
        "918",
        group=groups.ORDER,
    ),
    # Crafts and livelihood.
    SimpleActivity(
        "working_season",
        "Working season (earn a living)",
        "Labor Points = (Characteristic + Craft/Profession) x wealth; "
        "Exposure 2 in the craft.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "workshop_production",
        "Craft workshop production",
        "Workshop Total against the Craft Level; items a season. Exposure 2.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "improve_workshop",
        "Improve the workshop",
        "A season raising Innovation (100, 200, 300 Labor Points) or Raw "
        "Materials (50, 100, 150): no production; Practice.",
        CITY_GUILD,
        "919",
        4,
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "make_excellent_item",
        "Make an excellent item",
        "One season, if the Workshop Total reaches the Craft Level (15): +1 "
        "to a feature for every 3 points over it, at most Craft / 3 rounded "
        "up. Exposure 2.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "improve_station",
        "Improve wealth or status",
        "A season and Labor Points: Poor to average 120, average to Wealthy "
        "360, Wealthy to Poor in the next social class 1,080. No production.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "make_wondrous_item",
        "Make a wondrous item",
        "Touched by (Realm): the Workshop Total must beat the Craft Level (12 "
        "+ the effect's magnitude + its uses a day); the excess accumulates "
        "each season until the points equal the Craft Level, with no other "
        "workshop work. One effect: Range Personal or Touch, Duration up to "
        "Sun, Target Individual, of the two Forms chosen at creation; one "
        "assistant at most (City & Guild pp. 70-72). Exposure 2.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "repair_item",
        "Repair an item",
        "A season restoring an item. Exposure 2.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "merchant_venture",
        "Merchant venture, investment or legal action",
        "Labor Points or money, by the venture. Exposure 2.",
        CITY_GUILD,
        "919",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "tournament",
        "Tournament circuit",
        "An errant knight's season: Labor Points from Dexterity + Weapon. Exposure 2.",
        LORDS,
        "919",
        who=_C,
        group=groups.ADVENTURE,
    ),
    SimpleActivity(
        "train_group",
        "Train a combat group",
        "A season training together: the group becomes trained. Exposure 2 "
        "in Leadership or the weapon.",
        SOURCE,
        "919",
        group=groups.TEACHING,
    ),
    SimpleActivity(
        "use_agents",
        "Recruit or use agents",
        "Information once a season per agent. Exposure 2.",
        LORDS,
        "919",
        who=_C,
        group=groups.ORDER,
    ),
    # Scholars, physicians and artists.
    SimpleActivity(
        "attend_university",
        "Attend university",
        "A student's season: the lecturer's Source Quality; exams at its end.",
        ACADEME,
        "920",
        None,
        "the lecture's Source Quality",
        _C,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "vernacular_literature",
        "Read vernacular literature",
        "Exposure in Abilities the storyguide chooses.",
        ACADEME,
        "920",
        who=_C,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "research_formula",
        "Research a formula",
        "Five xp make one formula (an inception, reagent or theriac).",
        ACADEME,
        "920",
        5,
        who=_C,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "medical_season",
        "Medical seasonal work",
        "Care, therapy, regimens, finding ingredients: patients treated; "
        "Exposure 2 in Medicine.",
        ACADEME,
        "920",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "produce_remedies",
        "Produce reagents, theriacs or inceptions",
        "Experimental philosophy items. Exposure 2.",
        ACADEME,
        "920",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "apothecary",
        "Keep an apothecary's store",
        "Labor Points. Exposure 2.",
        ACADEME,
        "920",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "create_art",
        "Create a work of art / seek a sponsor",
        "The work's Aesthetic Quality; Reputation. Exposure 2.",
        ACADEME,
        "920",
        who=_C,
        group=groups.WORK,
    ),
    SimpleActivity(
        "study_artwork",
        "Study another artist's work",
        "Advancement Total = the work's Aesthetic Quality / 2.",
        ACADEME,
        "920",
        None,
        "half the work's Aesthetic Quality",
        _C,
        group=groups.STUDY,
    ),
    # Religious seasons.
    SimpleActivity(
        "worship",
        "Worship",
        "Source Quality = the church's Divine aura (Church Lore, "
        "Concentration, Music...).",
        SOURCE,
        "921",
        None,
        "the church's Divine aura",
        # Any Christian with a chapel may worship, a magus too (DE p. 378).
        (*_M, *_C),
        group=groups.FAITH,
    ),
    SimpleActivity(
        "good_works",
        "Good Works",
        "Source Quality 2, and 1 Faith Point.",
        CHURCH,
        "921",
        who=_C,
        faith=1,
        group=groups.FAITH,
    ),
    SimpleActivity(
        "care_of_souls",
        "Care of Souls",
        "A priest's season: Source Quality 2; a congregation bonus next year.",
        CHURCH,
        "921",
        who=_C,
        group=groups.FAITH,
    ),
    SimpleActivity(
        "follow_preacher",
        "Follow a preacher",
        "Source Quality = the sermons' Aesthetic Quality.",
        CHURCH,
        "921",
        None,
        "the sermons' Aesthetic Quality",
        _C,
        group=groups.FAITH,
    ),
    SimpleActivity(
        "pilgrimage",
        "Pilgrimage",
        "A season on pilgrimage toward its Target Level (18 minor, 30 "
        "major). Exposure 2.",
        CHURCH,
        "921",
        who=_C,
        group=groups.ADVENTURE,
    ),
    SimpleActivity(
        "penance",
        "Visitation, petition or penance",
        "Exposure 2; the penance served.",
        CHURCH,
        "921",
        who=_C,
        group=groups.FAITH,
    ),
    # Animals.
    SimpleActivity(
        "tame_animal",
        "Tame and train an animal",
        "Intelligence + Animal Handling + Animal Ken - its Might (less the "
        "Gift's 3, 6 Blatant, none Gentle) points a season until they reach "
        "its Might; a mundane beast's is 1 + 2 x its Confidence. The points "
        "last only over consecutive seasons. Tamed, a creature of the saga "
        "gains Loyal +0 to its tamer. Exposure 2 in Animal Handling.",
        DE_TAMING,
        "922",
        group=groups.WORK,
    ),
    # Travel and other.
    SimpleActivity(
        "travel",
        "Travel",
        "A season travelling (it may lower Living Conditions): Exposure 2 in "
        "an Area Lore or a language.",
        SOURCE,
        "923",
        group=groups.ADVENTURE,
    ),
    SimpleActivity(
        "search_lacuna",
        "Search for a lacuna",
        "Intelligence + Area Lore against 9; later seasons are practice.",
        SOCIETATES,
        "923",
        4,
        group=groups.STUDY,
    ),
    SimpleActivity(
        "convalesce",
        "Convalesce from wounds",
        "Recovering: no lab or craft work; study at half (type the halved "
        "Source Quality).",
        SOURCE,
        "923",
        no_xp=True,
        group=groups.REST,
    ),
)
BY_KEY: dict[str, SimpleActivity] = {a.key: a for a in ACTIVITIES}
