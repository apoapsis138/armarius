"""Interests: the kinds of deed a character might do in play, and which
supplement actions belong to each.

Each action a supplement brings to the character sheet has one interest
(a knight's tournament is Knightly, a disputation Scholarly). The desktop's
Deeds chapter heads a section with each interest and sets out under it the
actions done in a story, each with a line on what it does; the season-long
ones stay on This Season. The terminal's More groups the same actions under
the same headers. An interest names the kind of person who uses an action,
not the book it comes from: the book decides only whether it is offered
(action_books)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .models import Character, Covenant
from .rules import faiths

SESSION = "Session & Reputation"
KNIGHTLY = "Knightly"
SCHOLARLY = "Scholarly"
INSIGHT = "Insight"
RELIGION = "Religion"
AGENTS = "Agents"
RESEARCH = "Research"
HERMETIC_MYSTERIES = "Hermetic Mysteries"
MYSTERY_CULTS = "Mystery Cults"
CRAFT = "Craft & Trade"
TRIBUNAL = "Tribunal & Order"
FAERIE = "Dealings with Faerie"
INFERNAL = "The Infernal"
APPRENTICESHIP = "Apprenticeship"
COVENFOLK = "Covenfolk"

#: The interests in the order the Deeds chapter and More list them.
INTERESTS: tuple[str, ...] = (
    SESSION,
    KNIGHTLY,
    SCHOLARLY,
    INSIGHT,
    RELIGION,
    AGENTS,
    RESEARCH,
    HERMETIC_MYSTERIES,
    MYSTERY_CULTS,
    CRAFT,
    TRIBUNAL,
    FAERIE,
    INFERNAL,
    APPRENTICESHIP,
    COVENFOLK,
)

#: Each tagged action's interest: those on the Deeds chapter and the
#: season-long ones kept on This Season alike.
INTEREST_OF: dict[str, str] = {
    "end_session": SESSION,
    "what_changed": SESSION,
    "reputation_roll": SESSION,
    "house_acclaim": SESSION,
    "melee_event": KNIGHTLY,
    "tourney_season": KNIGHTLY,
    "disputatio": SCHOLARLY,
    "make_ligature": SCHOLARLY,
    "scholar_career": SCHOLARLY,
    "font_of_knowledge": INSIGHT,
    "tmre_divination": INSIGHT,
    "tmre_astrology": INSIGHT,
    "invoke_saint": RELIGION,
    "threaten_saint": RELIGION,
    "patron_saint": RELIGION,
    "devotion_points": RELIGION,
    "act_of_piety": RELIGION,
    "mystic_path": RELIGION,
    "spiritual_path": RELIGION,
    "monistic_revelation": RELIGION,
    "gods_aid": RELIGION,
    "holy_influence": RELIGION,
    "invoke_baraka": RELIGION,
    "hajj": RELIGION,
    "paint_icon": RELIGION,
    "venerate_icon": RELIGION,
    "mothers_curse": RELIGION,
    "perform_exorcism": RELIGION,
    "pilgrimage": RELIGION,
    "impress_agent": AGENTS,
    "spend_agency_xp": AGENTS,
    "set_agent_task": AGENTS,
    "resolve_agent_task": AGENTS,
    "spirits_and_names": HERMETIC_MYSTERIES,
    "dream_working": HERMETIC_MYSTERIES,
    "hermetic_sacrifice": HERMETIC_MYSTERIES,
    "philosophic_alchemy": HERMETIC_MYSTERIES,
    "great_elixir": HERMETIC_MYSTERIES,
    "learn_cantation": APPRENTICESHIP,
    "experiment_script": MYSTERY_CULTS,
    "make_greek_fire": CRAFT,
    "artist_career": CRAFT,
    "sell_goods": CRAFT,
    "apothecary_store": CRAFT,
    "labor_story": CRAFT,
    "invest_labor": CRAFT,
    "theban_letter": TRIBUNAL,
    "invoke_oath": TRIBUNAL,
    "ars_fabulosa": FAERIE,
    "faerie_bargain": FAERIE,
    "faerie_offer": FAERIE,
    "indulge_sin": INFERNAL,
    "infernal_influence": INFERNAL,
    "ars_goetia": INFERNAL,
    "turbulence": APPRENTICESHIP,
    "gauntlet": APPRENTICESHIP,
    "lose_the_gift": APPRENTICESHIP,
    "grog_story_xp": COVENFOLK,
    "discipline_grog": COVENFOLK,
    "grog_pension": COVENFOLK,
}

#: What each action on the Deeds chapter does, in a line.
NOTES: dict[str, str] = {
    "end_session": "Confidence Points for a session of play, and its "
    "noteworthy deeds as experience in his Reputations.",
    "what_changed": "His scores, spells, Virtues, Warping, wounds and holdings "
    "since the last Session played.",
    "reputation_roll": "Whether someone has heard of him: a stress die and "
    "a Reputation against how far away they are.",
    "house_acclaim": "An award of House Acclaim, or a roll with it, for a "
    "magus of Bonisagus or Flambeau.",
    "melee_event": "A roll on the Melee Events Table in a tournament's grand charge.",
    "disputatio": "A schoolmen's debate with another character.",
    "make_ligature": "A small charm that helps one roll, tied to Artes "
    "Liberales, Philosophiae or Medicine.",
    "font_of_knowledge": "Drawing on Font of Knowledge to use an Ability "
    "he lacks as if he had it at 2.",
    "tmre_divination": "A divination answering one question, as a "
    "Momentary Intellego spell would.",
    "tmre_astrology": "An astrological reckoning: Intelligence + Artes "
    "Liberales (Astronomy).",
    "experiment_script": "As Mystagogue, a rite to find a new Initiation "
    "Script, checked once the Initiate has carried it out.",
    "theban_letter": "Composing or reading a letter in the Theban magi's "
    "rhetorical style.",
    "invoke_oath": "The injured party calls on the spirit that witnessed "
    "a broken oath.",
    "ars_fabulosa": "A summoner's bargaining powers: Summoning, Bonding, "
    "Captivating or Dismissing.",
    "faerie_bargain": "How a bargain made in a summoning ended.",
    "faerie_offer": "Spending a fable point to bargain with the Faerie "
    "Realm over the story.",
    "indulge_sin": "A Confidence Point from indulging a sin, or a ceremony of one.",
    "infernal_influence": "Leading others into temptation, or tarnishing "
    "an Infernal aura.",
    "ars_goetia": "The total of a Goetic Art against a spirit's Might.",
    "turbulence": "A Gifted child's untrained Gift lashing out.",
    "gauntlet": "The parens' test of his apprentice.",
    "lose_the_gift": "Failing an apprentice: the Gift lost or suppressed.",
    "discipline_grog": "A reward or punishment for one of the covenfolk.",
    "grog_pension": "A grog retires on a pension, or pays rent for his "
    "lodging instead.",
}

#: The actions the Deeds chapter sets out.
DEEDS: tuple[str, ...] = tuple(NOTES)

#: What each action on the Religion chapter does, in a line.
RELIGION_NOTES: dict[str, str] = {
    "invoke_saint": "Asking a saint for aid, or a yazata for a Mazdean.",
    "threaten_saint": "Threatening a saint who has refused an invocation.",
    "patron_saint": "Choosing a patron saint.",
    "devotion_points": "Points earned through a Devotion.",
    "act_of_piety": "An indulgence, a vigil or a fast.",
    "mystic_path": "Taking up a mystic path.",
    "spiritual_path": "The next step on a contemplative's Spiritual Path.",
    "monistic_revelation": "A monistic mystic's revelation after an Ascent.",
    "gods_aid": "Asking for God's aid.",
    "holy_influence": "Influence over others through holy standing.",
    "invoke_baraka": "Seeking a holy forbear's blessing.",
    "hajj": "Completing the pilgrimage to Mecca.",
    "paint_icon": "Painting an icon, in the Theban Tribunal's custom.",
    "venerate_icon": "Venerating an icon, in the Theban Tribunal's custom.",
    "mothers_curse": "A mother's curse, in the Theban Tribunal's custom.",
    "perform_exorcism": "A clergyman's exorcism, under Holy Orders.",
}

#: What each action on the Agents chapter does, in a line.
AGENT_NOTES: dict[str, str] = {
    "impress_agent": "Winning over someone not yet impressed.",
    "spend_agency_xp": "Spending Agency experience on an agent's Bond.",
    "set_agent_task": "Giving a bonded agent a task.",
    "resolve_agent_task": "Rolling how an agent's task turned out.",
}

#: What each such action on the Hermetic Magic chapter does, in a line.
HERMETIC_NOTES: dict[str, str] = {
    "spirits_and_names": "Working with spirits and their names, in Magic "
    "Outside the Lab.",
    "dream_working": "Magic worked through dreams, on a known spell.",
    "hermetic_sacrifice": "A sacrifice that strengthens a known spell.",
    "learn_cantation": "An apprentice learning a cantation, on Known Spells.",
}

#: What each such action under Aging does, in a line.
AGING_NOTES: dict[str, str] = {
    "great_elixir": "Testing an enchanted Great Elixir.",
}

#: The Planning chapter's section of the supplements' season-long work,
#: below This Season (whose own buttons keep to planning the season).
SEASON_WORK = "A Season's Work"

#: What each action in A Season's Work does, in a line.
SEASON_NOTES: dict[str, str] = {
    "tourney_season": "A season on the tourney circuit, as a knight or as "
    "the patron who hosts it.",
    "labor_story": "The Labor Points a story gives a craftsman or merchant.",
    "invest_labor": "What he does with surplus Labor Points or money.",
    "sell_goods": "A sale the story calls for, settled with a roll.",
    "apothecary_store": "A season keeping an apothecary's store of medicinals.",
    "make_greek_fire": "A season making Greek Fire, an alchemical reagent.",
    "artist_career": "An artist's Reputation for his Craft or Profession, "
    "and what raises it.",
    "scholar_career": "A scholar's steps between his seasons, from a place "
    "at a school onward.",
    "turbulence": NOTES["turbulence"],
    "grog_story_xp": "A story's experience for a grog, and the season it "
    "takes from his yearly update.",
    "pilgrimage": "A pilgrimage's road, from its aim to its end.",
    "philosophic_alchemy": "An alchemical vis extraction left to digest "
    "while he does other work.",
}


#: Each interest in a line, for its card.
SUMMARIES: dict[str, str] = {
    SESSION: "What every character does: closing a session and finding out "
    "who has heard of them.",
    KNIGHTLY: "Tournaments, from the melee to a season on the circuit.",
    SCHOLARLY: "Debate, learned charms and a scholar's working life.",
    INSIGHT: "Answers drawn from faith, signs and the stars.",
    RELIGION: "The Religion chapter: a character's faith and what it offers.",
    AGENTS: "People who work on a character's behalf.",
    RESEARCH: "A magus's original research.",
    HERMETIC_MYSTERIES: "Spirits, dreams, sacrifice and alchemy.",
    MYSTERY_CULTS: "Finding new Initiation Scripts for a cult.",
    CRAFT: "Making, selling and earning a living by a trade.",
    TRIBUNAL: "Formal letters, and oaths called to account.",
    FAERIE: "Summoning faeries and striking bargains with them.",
    INFERNAL: "Sin, temptation and the Goetic Arts.",
    APPRENTICESHIP: "A Gifted child's training, from Turbulence to the Gauntlet.",
    COVENFOLK: "Grogs' stories, rewards and retirement.",
}

#: Who each interest is for and what it holds, for its inspector.
ABOUT: dict[str, str] = {
    SESSION: "Every character in play has these, so this interest is always on.",
    KNIGHTLY: "For knights, and for the patrons who host them. Leave it off "
    "for someone who will never ride in the lists.",
    SCHOLARLY: "For schoolmen and anyone trained at the schools: disputing "
    "with another character, tying ligatures, and a career from a place at "
    "a school onward.",
    INSIGHT: "For those who look for knowledge beyond study: borrowing an "
    "Ability through Font of Knowledge, a divination, or an astrological "
    "reckoning.",
    RELIGION: "For the devout, and for anyone whose faith shapes their "
    "play. Turned off, the Religion chapter leaves the sheet, which suits a "
    "character whose faith will never come up.",
    AGENTS: "For those who run a network of informants and servants. "
    "Turned off, the Agents chapter leaves the sheet.",
    RESEARCH: "For a magus who pushes the limits of Hermetic magic. Turned "
    "off, the Research chapter leaves the sheet.",
    HERMETIC_MYSTERIES: "For a magus initiated into the deeper magics The "
    "Mysteries describes, from spirit names to the Great Elixir.",
    MYSTERY_CULTS: "For a Mystagogue, who tests a new Initiation Script by "
    "having an Initiate carry it out.",
    CRAFT: "For craftsmen, merchants and artists: Labor Points, sales, an "
    "apothecary's store, an artist's Reputation and Greek Fire. All of it "
    "sits on Planning, not on Deeds.",
    TRIBUNAL: "For those who live by the Order's customs: letters in the "
    "Theban magi's rhetorical style, and calling on the spirit that "
    "witnessed a broken oath.",
    FAERIE: "For summoners and anyone who bargains with the Faerie Realm, "
    "from the Ars Fabulosa to spending a fable point on the story itself.",
    INFERNAL: "For those who deal with the Infernal, knowingly or not: "
    "gaining Confidence from a sin, leading others into temptation, and "
    "pitting a Goetic Art against a spirit's Might.",
    APPRENTICESHIP: "For an apprentice and the parens who teaches them: the "
    "untrained Gift lashing out, the final test, and failing an apprentice.",
    COVENFOLK: "For the covenant's grogs and those who look after them: a "
    "story's experience, a reward or punishment, and a pension.",
}


@dataclass(frozen=True)
class Gate[R]:
    """What an interest that has a chapter or section of its own hides, and
    what keeps it on whatever was chosen: `kept_on` asks the record, `fixed`
    stands where the card's switch would be and `why` heads its inspector."""

    chapter: str
    kept_on: Callable[[R], bool]
    fixed: str
    why: str


#: A character's interests with chapters of their own.
CHARACTER_GATES: dict[str, Gate[Character]] = {
    RELIGION: Gate(
        "Religion",
        faiths.church_career,
        "On for a Church career",
        "Their Church career keeps this on: its Holy Orders, Petitions and "
        "Canon Court are on the Religion chapter.",
    ),
    AGENTS: Gate(
        "Agents",
        lambda character: bool(character.agents),
        "On while they have agents",
        "Their agents keep this on: they are on the Agents chapter.",
    ),
    RESEARCH: Gate(
        "Research",
        lambda character: bool(character.breakthroughs),
        "On while research is under way",
        "Their research keeps this on: its goals and log are on the Research chapter.",
    ),
}

#: The interests only a magus has.
MAGI_ONLY: tuple[str, ...] = (RESEARCH, HERMETIC_MYSTERIES)

MANORS = "Manors"
SHIPS = "Ships"

#: A covenant's interests, in the order its window lists them.
COVENANT_INTERESTS: tuple[str, ...] = (MANORS, SHIPS)

#: A covenant's interests with chapters or sections of their own.
COVENANT_GATES: dict[str, Gate[Covenant]] = {
    MANORS: Gate(
        "Manors",
        lambda covenant: any(covenant.manors.values()),
        "On while it has manors",
        "Its manors keep this on: they are on the Manors chapter.",
    ),
    SHIPS: Gate(
        "Ships",
        lambda covenant: any(p.kind == "ship" for p in covenant.possessions),
        "On while it has ships",
        "Its ships keep this on: they are listed under Possessions.",
    ),
}

#: Each covenant interest's actions, by where they are.
COVENANT_ACTIONS: dict[str, tuple[str, dict[str, str]]] = {
    MANORS: (
        "On the Manors chapter",
        {
            "buy_manor": "Adding a manor at its price.",
            "assart": "Clearing new land on a manor.",
            "winter_roll": "How an establishment comes through the winter.",
            "settle_inheritance": "Settling an inheritance.",
            "hunt_on_manor": "A day's hunt on the chosen manor.",
            "area_lore_on_manor": "Seeking on the chosen manor: Area Lore.",
        },
    ),
    SHIPS: (
        "On Possessions, under Ships",
        {
            "build_ship": "A new ship for the covenant.",
            "ship_stress": "A check against a storm, fire or attack.",
            "ship_combat": "One ship against another.",
            "ship_fate": "What became of a ship after a fight or a storm.",
            "detach_ship": "A ship sailing apart from the fleet for a while.",
            "rejoin_ship": "A ship coming back to the fleet.",
        },
    ),
}

#: Each covenant interest in a line, for its card.
COVENANT_SUMMARIES: dict[str, str] = {
    MANORS: "Land, tenants and the seasons of a manor.",
    SHIPS: "A covenant's fleet, at sea and in battle.",
}

#: Who each covenant interest is for, for its inspector.
COVENANT_ABOUT: dict[str, str] = {
    MANORS: "For a covenant that holds land and answers for the people on "
    "it. Leave it off for one that lives apart from the mundane world.",
    SHIPS: "For a covenant on the coast or a river, with vessels of its own. "
    "Leave it off for one that will never put to sea.",
}

#: The interests a character may turn off: all but Session & Reputation,
#: which every character in play has.
OPTIONAL: tuple[str, ...] = tuple(i for i in INTERESTS if i != SESSION)


#: The laboratory's lab work besides the plan, under its Planning.
LAB_NOTES: dict[str, str] = {
    "create_familiar": "Bind the owner's familiar: a season's lab work, "
    "while he has none.",
    "perform_ritual": "Perform a Longevity Ritual from one of the "
    "laboratory's Lab Texts.",
}

#: The Seasons chapters' Undertakings (a covenant's and the saga's): what
#: the troupe sets out to do besides the seasons' plans.
UNDERTAKINGS = "Undertakings"

#: What each undertaking does, in a line.
UNDERTAKING_NOTES: dict[str, str] = {
    "begin_project": "Begin a great work of Hermetic Projects: a Great "
    "Tower, a Menagerie, or a project followed stage by stage.",
    "travel": "Work out a journey: the days, the cost and the arrival, "
    "written in each traveller's Diary.",
    "hunt": "A hunt on the road, once the party has found a hunting spot.",
    "area_lore": "Seeking along the road: Intelligence + Area Lore.",
}


def interests_off(character: Character) -> list[str]:
    """The interests that are off for `character`: those turned off, but
    never one its record keeps on (CHARACTER_GATES)."""
    gates = CHARACTER_GATES
    return [
        i
        for i in character.interests_off
        if i not in gates or not gates[i].kept_on(character)
    ]


def covenant_interests_off(covenant: Covenant) -> list[str]:
    """The interests that are off for `covenant`, as interests_off."""
    gates = COVENANT_GATES
    return [
        i
        for i in covenant.interests_off
        if i not in gates or not gates[i].kept_on(covenant)
    ]


def chapters_off(character: Character) -> set[str]:
    """The chapters `character`'s interests leave off the sheet."""
    off = interests_off(character)
    return {g.chapter for i, g in CHARACTER_GATES.items() if i in off}


def hidden(off: list[str], action: str) -> bool:
    """Whether `action` is left out for a character with the interests
    `off` turned off."""
    return INTEREST_OF.get(action) in off and INTEREST_OF.get(action) != SESSION


def members(name: str) -> list[str]:
    """The actions of the interest `name`."""
    return [action for action, tag in INTEREST_OF.items() if tag == name]


def interest(action: str) -> str | None:
    """The interest `action` belongs to, if any."""
    return INTEREST_OF.get(action)


def grouped(actions: list[str]) -> list[tuple[str | None, list[str]]]:
    """`actions` as a menu lists them: those with no interest first, then
    each interest's under its name, in INTERESTS order (each group keeps
    the order it was given)."""
    groups: list[tuple[str | None, list[str]]] = []
    for name in (None, *INTERESTS):
        members = [a for a in actions if INTEREST_OF.get(a) == name]
        if members:
            groups.append((name, members))
    return groups
