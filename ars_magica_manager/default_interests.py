"""Default Interests: the interests a new character starts with, each with
the reason it is on.

The defaults are Session & Reputation, which every character has, plus
the union of what each rule below turns on. A rule is a small function
registered in RULES with @rule; adding a source of defaults is one more
rule, with no change to the callers. The type rule is the approved design
of the app, not a book rule; the House and Virtue rules follow SOURCE.

The interests are named as `deeds` names them (deeds.INTERESTS). `deeds`
asks this module for a character's defaults, so this one sits below it and
spells the names out; a test checks each is one of deeds'.
"""

from __future__ import annotations

from collections.abc import Callable

from . import catalog
from .models import Character

SOURCE = (
    # Houses: the four Mystery Cult Houses (Bjornaer, Criamon, Merinita,
    # Verditius), Merinita's study of faeries, Verditius's enchanted
    # wares, Jerbiton's mundane scholarship and Flambeau as the Order's
    # knights.
    "Ars Magica Definitive Edition pp. 12-17, 46 (Faerie Magic pp. "
    "236-238); The Mysteries, Revised p. 4. "
    # Virtues and Flaws, by interest.
    "Knightly: Knight DE p. 88, Brother Knight DE p. 73 and RoP:D p. 92, "
    "Landed Noble DE p. 89, Great Noble Lords of Men p. 31. "
    "Scholarly: Educated and its Bardic, Hebrew, Islamic and Vernacular "
    "kinds DE p. 77 (Hebrew RoP:D p. 136, Islamic RoP:D p. 115), Clerk DE "
    "p. 74. "
    "Insight: Font of Knowledge DE p. 82; Divination and Augury The "
    "Mysteries, Revised pp. 58-62, Additional Divination Method ibid. "
    "p. 59; "
    "Mazdean Astrology The Cradle & the Crescent pp. 98-99, Solomonic "
    "Astrology ibid. p. 30; (Type) Divining Hedge Magic, Revised p. 19. "
    "Religion: Priest DE p. 104, Eastern Priest RoP:D pp. 92-93, Mazdean "
    "Priest DE p. 97 and The Cradle & the Crescent p. 93, Patron Angel "
    "RoP:D p. 99. "
    "Dealings with Faerie: Faerie Blood DE p. 79 (Bloodcap HoH:TL p. 104, "
    "Spinnen Lion & Lily p. 97, Jentil and Laminak Faith & Flame p. 91), "
    "Strong Faerie Blood DE p. 110, Faerie Sight and Faerie Speech RoP:F "
    "p. 50 and The Cradle & the Crescent p. 79 (Errata p. 68 is for Tales "
    "of Mythic Europe's Faerie Speech), (Faerie) Summoning RoP:F p. 113, "
    "Faerie Magic DE p. 79, Faerie-Raised Magic DE p. 79 and HoH:MC p. 86 "
    "(Errata p. 55), Faerie Upbringing and Faerie Friend DE p. 128. "
    "Craft & Trade: Craftsman DE p. 75, Merchant DE p. 98, Guild "
    "Apprentice DE p. 84 and City & Guild p. 53, Craft Guild Training DE "
    "p. 75 and Grogs p. 74, Independent Craftsman DE p. 134 and Grogs "
    "p. 81. "
    "The Infernal: Diabolist RoP:I pp. 85, 112, Diabolic Past DE p. 126, "
    "Mentored by Demons DE p. 98 and RoP:I p. 86, Demonic Blood DE p. 75, "
    "Demonic Might and Demonic Powers DE p. 76, Lesser and Greater "
    "Infernal Power RoP:I pp. 78-79, Infernal Blessing RoP:I pp. 85-86, "
    "Summoning (the Goetic Art) RoP:I pp. 87, 114-115. "
    "Tribunal & Order: Redcap DE p. 91 (Errata p. 16), Lone Redcap DE "
    "p. 91 and HoH:TL p. 106 (Errata p. 47). "
    "Covenfolk: Custos DE p. 75. "
    "Apprenticeship: Apprentice DE p. 70, and Apprentice (Rhine Tribunal) "
    "Guardians of the Forests p. 19, the same Virtue for any Tribunal. "
    "None of the Errata's changes alters what a House or Virtue is about."
)

#: An interest the defaults turn on, and why ("a magus").
Reason = tuple[str, str]
Rule = Callable[[Character], list[Reason]]

SESSION = "Session & Reputation"
KNIGHTLY = "Knightly"
SCHOLARLY = "Scholarly"
INSIGHT = "Insight"
RELIGION = "Religion"
RESEARCH = "Research"
MYSTERY_CULTS = "Mystery Cults"
CRAFT = "Craft & Trade"
TRIBUNAL = "Tribunal & Order"
FAERIE = "Dealings with Faerie"
INFERNAL = "The Infernal"
APPRENTICESHIP = "Apprenticeship"
COVENFOLK = "Covenfolk"

#: The default-interest rules, in the order their reasons are given.
RULES: list[Rule] = []


def rule(fn: Rule) -> Rule:
    """Register a default-interest rule."""
    RULES.append(fn)
    return fn


#: What each type of character takes up, and how its reason names it. An
#: animal grog is a grog with an animal form, looked up as ANIMAL_GROG.
ANIMAL_GROG = "animal grog"
BY_TYPE: dict[str, tuple[str, tuple[str, ...]]] = {
    "magus": ("a magus", (RESEARCH, TRIBUNAL)),
    "companion": ("a companion", (RELIGION,)),
    "mythic companion": ("a mythic companion", (RELIGION,)),
    "grog": ("a grog", (COVENFOLK, CRAFT)),
    ANIMAL_GROG: ("an animal grog", (COVENFOLK,)),
}


@rule
def by_type(character: Character) -> list[Reason]:
    """The interests its type takes up."""
    kind = ANIMAL_GROG if character.animal is not None else character.type
    why, interests = BY_TYPE.get(kind, ("", ()))
    return [(interest, why) for interest in interests]


#: What a magus's House takes up, by house_catalog.json id; a House not
#: here adds nothing.
BY_HOUSE: dict[str, tuple[str, ...]] = {
    "house_bjornaer": (MYSTERY_CULTS,),
    "house_criamon": (MYSTERY_CULTS,),
    "house_merinita": (MYSTERY_CULTS, FAERIE),
    "house_verditius": (MYSTERY_CULTS, CRAFT),
    "house_jerbiton": (SCHOLARLY,),
    "house_flambeau": (KNIGHTLY,),
}


@rule
def by_house(character: Character) -> list[Reason]:
    """The interests a magus's House takes up, named "House Merinita"."""
    house = character.hermetic.house
    if character.type != "magus" or house not in BY_HOUSE:
        return []
    why = f"House {catalog.load_house_catalog_by_id()[house].name}"
    return [(interest, why) for interest in BY_HOUSE[house]]


#: The Virtues and Flaws that take up each interest, by
#: virtue_flaw_catalog.json id (SOURCE has each one's book and page).
_VIRTUES_BY_INTEREST: dict[str, tuple[str, ...]] = {
    KNIGHTLY: ("vf_knight", "vf_brother_knight", "vf_landed_noble", "vf_great_noble"),
    SCHOLARLY: (
        "vf_educated",
        "vf_educated_bardic",
        "vf_educated_hebrew",
        "vf_educated_islamic",
        "vf_educated_vernacular",
        "vf_clerk",
    ),
    INSIGHT: (
        "vf_font_of_knowledge",
        "vf_divination_and_augury",
        "vf_additional_divination_method",
        "vf_mazdean_astrology",
        "vf_solomonic_astrology",
        "vf_type_divining",
        "vf_type_divining_major",
    ),
    RELIGION: (
        "vf_priest",
        "vf_eastern_priest",
        "vf_mazdean_priest",
        "vf_patron_angel",
    ),
    FAERIE: (
        "vf_faerie_blood",
        "vf_faerie_blood_bloodcap",
        "vf_faerie_blood_jentil",
        "vf_faerie_blood_jentil_major",
        "vf_faerie_blood_laminak",
        "vf_faerie_blood_spinnen",
        "vf_strong_faerie_blood",
        "vf_faerie_sight",
        "vf_faerie_speech",
        "vf_faerie_summoning",
        "vf_faerie_magic",
        "vf_faerie_raised_magic",
        "vf_faerie_upbringing",
        "vf_faerie_friend",
    ),
    CRAFT: (
        "vf_craftsman",
        "vf_merchant",
        "vf_guild_apprentice",
        "vf_craft_guild_training",
        "vf_independent_craftsman",
    ),
    INFERNAL: (
        "vf_diabolist",
        "vf_diabolic_past",
        "vf_mentored_by_demons",
        "vf_demonic_blood",
        "vf_demonic_might",
        "vf_demonic_powers",
        "vf_lesser_infernal_power",
        "vf_greater_infernal_power",
        "vf_infernal_blessing",
        "vf_infernal_blessing_major",
        # The Goetic Art; (Faerie) Summoning is under FAERIE, and (Type)
        # Summoning, whose spirits may be of any realm, takes up nothing.
        "vf_summoning",
    ),
    TRIBUNAL: ("vf_redcap", "vf_lone_redcap"),
    COVENFOLK: ("vf_custos",),
    APPRENTICESHIP: ("vf_apprentice", "vf_apprentice_rhine_tribunal"),
}

#: The interest each Virtue or Flaw takes up, by virtue_flaw_catalog.json
#: id; one not here (a saga's own among them) takes up nothing.
BY_VIRTUE: dict[str, str] = {
    vf_id: interest
    for interest, vf_ids in _VIRTUES_BY_INTEREST.items()
    for vf_id in vf_ids
}


@rule
def by_virtue(character: Character) -> list[Reason]:
    """The interests its Virtues and Flaws take up, each named as the sheet
    names it ("Faerie Blood (Jentil)")."""
    found: list[Reason] = []
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for vf in character.virtues_flaws:
        if vf.vf_id not in BY_VIRTUE:
            continue
        reason = (BY_VIRTUE[vf.vf_id], catalog.describe_virtue_flaw(vf, by_id))
        if reason not in found:
            found.append(reason)
    return found


def defaults(character: Character) -> list[Reason]:
    """`character`'s Default Interests, each with its reason: Session &
    Reputation first, then each rule's in turn (an interest two rules turn
    on is listed once for each)."""
    found: list[Reason] = [(SESSION, "every character")]
    for fn in RULES:
        found += fn(character)
    return found
