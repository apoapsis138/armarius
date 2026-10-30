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

SESSION = "Session & Reputation"
KNIGHTLY = "Knightly"
SCHOLARLY = "Scholarly"
INSIGHT = "Insight"
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
