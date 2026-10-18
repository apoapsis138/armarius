"""The Bestiary: every creature, spirit, demon and faerie the book gives a
stat block, in paraphrase, each set at the place it haunts and tied to
the threat or court it belongs to. The human magi and mundane folk with
stat blocks are characters, made by the regional parts.

Numbers are the book's; what powers do, how a creature looks and the
notes are a summary in the pack's own words. Any Quality the catalog
lacks goes to the notes. Built after every place, threat and magus
exists, so each creature finds its home by name."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models import BodyVis

if TYPE_CHECKING:
    from ...models import Creature, Neighbour
    from . import Provence

#: A person's Fatigue levels, as most of the book's stat blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"


def _puissant(ability: str) -> tuple[str, dict[str, str]]:
    return ("Puissant {ability}", {"ability": ability})


def _minor(virtue: str) -> tuple[str, dict[str, str]]:
    return ("Minor Virtue", {"virtue": virtue})


def _great(characteristic: str) -> tuple[str, dict[str, str]]:
    return ("Great {characteristic}", {"characteristic": characteristic})


def _chars(
    int_: int, per: int, pre: int, com: int, str_: int, sta: int, dex: int, qik: int
) -> dict[str, int]:
    """Characteristics in the book's order (Int or Cun, Per, Pre, Com, Str,
    Sta, Dex, Qik)."""
    return {
        "intelligence": int_,
        "perception": per,
        "presence": pre,
        "communication": com,
        "strength": str_,
        "stamina": sta,
        "dexterity": dex,
        "quickness": qik,
    }


def build(provence: Provence) -> None:
    saga = provence.b.saga

    def at(name: str) -> Neighbour:
        found = next((n for n in saga.neighbours if n.name == name), None)
        if found is None:
            raise KeyError(f"No neighbour named {name!r} for the bestiary")
        return found

    def tie(creature: Creature, name: str, note: str) -> None:
        provence.b.link(at(name), "creatures", creature, note)

    _toulousain(provence, at, tie)
    _gascony(provence, at, tie)
    _pyrenees(provence, at, tie)
    _narbonnais(provence, at, tie)
    _arelat(provence, at, tie)
    _val_negra(provence, at, tie)


def _toulousain(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    tolosa = b.creature(
        "The Spirit of Tolosa",
        page="p. 37",
        confidence=(1, 3),
        tires=False,
        can_be_wounded=False,
        realm="Magic",
        might=40,
        form="Aquam",
        size=0,
        season="Autumn",
        block={
            "characteristics": _chars(0, 0, 3, 1, 0, 0, 0, 0),
            "virtues_flaws": [
                "Magic Spirit",
                ("Ways of the {land}", {"land": "Land (Toulouse)"}),
                "Entrancement",
                ("Affinity with {ability}", {"ability": "Area Lore"}),
                ("Inoffensive to {being}", {"being": "the Magic Realm"}),
                "Magic Sensitivity",
                _puissant("Area Lore"),
                "Dependent",
                ("Servant of the {land}", {"land": "Land (Toulouse)"}),
                ("Anchored to the {land}", {"land": "Land (Toulouse)"}),
                "Incomprehensible",
                "Soft-Hearted",
                "Susceptibility to Infernal Power",
                "Greater Power",
                "No Fatigue",
                *["Ritual Power"] * 6,
                "Gift of Speech",
                "Improved Abilities",
                *["Improved Powers"] * 10,
                "Vis Mastery",
            ],
            "abilities": [
                ("Area Lore: County of Toulouse", 18, "city of Toulouse"),
                ("Artes Liberales", 1, "poetry"),
                ("Awareness", 1, "fires"),
                ("Folk Ken", 5, "Toulousain residents"),
                ("Bargain", 1, "Toulouse"),
                ("Carouse", 1, "poetry"),
                ("Charm", 3, "strangers"),
                ("Civil and Canon Law", 1, "Toulouse"),
                ("Entrancement", 2, "citizens"),
                ("Living Language: Occitan", 5, "Provençal/Languedoc"),
                ("Magic Sensitivity", 2, "regiones"),
                ("Organization Lore: Tolosate", 1, "lake sacrifices"),
                ("Penetration", 4, "Mentem"),
            ],
            "traits": {"Soft-Hearted": 3},
        },
        soak=0,
        fatigue_levels="N/A",
        powers=[
            b.power(
                "Sturdy Walls of Toulouse",
                8,
                2,
                "Terram",
                does=(
                    "Mends a breach in the city walls with stone that holds "
                    "only until the next sunrise or sunset, then crumbles "
                    "away and leaves the gap."
                ),
            ),
            b.power(
                "The Silent Counsel",
                4,
                -2,
                "Mentem",
                does=(
                    "Quietly steers a body of people, such as the bishop or "
                    "the capitouls in session, toward what is best for the "
                    "city as a whole."
                ),
            ),
            b.power(
                "Human Shape",
                1,
                -1,
                "Corpus",
                does=(
                    "Takes bodily form until the next sunrise or sunset as an "
                    "unremarkable townsman of the lower orders, still "
                    "unsettling to be near because of its Gift."
                ),
            ),
            b.power(
                "Grant Blessing of the City",
                5,
                -19,
                "Vim",
                does=(
                    "Makes its chosen one prosper, granting Ways of Toulouse "
                    "until the spirit takes it back; the Might spent stays "
                    "spent until then."
                ),
            ),
            b.power(
                "Oath Swearing",
                8,
                -9,
                "Vim",
                does=(
                    "Works only on the steps of Saint-Pierre des Cuisines, "
                    "where counts and capitouls swear to the people (a tiny "
                    "Magic aura of 1). If it penetrates, the oath binds: "
                    "breaking it, even in secret, sets mostly false rumours "
                    "running through the county and gives the oathbreaker "
                    "the Minor Flaw Infamous."
                ),
            ),
        ],
        appearance=(
            "To Second Sight, a damp mist or a figure of no clear sex made of "
            "water and pond reeds. At night it may sit in human form as a "
            "fisherman on Adam Carpentiere's river barrage, glad to talk, "
            "though little it says makes sense to mortals."
        ),
        notes=(
            "The genius loci of Toulouse, answering only to the name Tolosa. "
            "The book gives its Size as not applicable. Its Virtues include "
            "Ways of the Land and Servant of the Land (Toulouse), Anchored to "
            "the Land (Toulouse) and Inoffensive to the Magic Realm. It has grown much weaker since the conquest by "
            "de Montfort; the covenant's regio lives or dies with the city's "
            "prosperity and culture."
        ),
        place=at("The City of Toulouse"),
    )
    tie(
        tolosa, "The Drowned Lake of Tolosa", "the genius loci whose work this regio is"
    )


def _gascony(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    spirits = "The Six Deadly Spirits"

    cenodoxus = b.creature(
        "Cenodoxus Superbia, Lord of Pride and Envy",
        page="p. 52",
        confidence=(2, 7),
        order="Lord of the Vessels of Iniquity",
        hierarchy=5,
        weakness="cannot harm the meek",
        realm="Infernal",
        might=40,
        form="Vim",
        size=0,
        block={
            "characteristics": _chars(2, 2, 1, 2, 3, 4, 3, 3),
            "virtues_flaws": [
                "Improved Characteristics",
                "Self-Confident",
                "Overconfident (Minor)",
            ],
            "abilities": [
                ("Bargain", 7, "setting rates for assistance"),
                ("Brawl", 4, "dagger"),
                ("Charm", 7, "first encounters"),
                ("Folk Ken", 7, "humans"),
                ("Guile", 7, "craftsmen"),
                ("Intrigue", 7, "subtly spreading gossip"),
            ],
            "traits": {
                "Depraved": 6,
                "Hateful": 6,
                "Subtle": 5,
                "Cunning": 4,
                "Deceptive": 4,
                "Vessel of Iniquity Demon": 3,
            },
            "reputations": {"Subtle & Effective (Infernal)": 5},
        },
        attacks=[
            b.attack("Fist", 3, 7, 7, 3),
            b.attack("Dagger", 3, 10, 8, 6),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Form of Wickedness",
                4,
                0,
                "Mentem",
                does=(
                    "Its order's version of Coagulation: a material body "
                    "with no shape or size, sin made visible, which drives "
                    "envious onlookers to indulge their envy until they "
                    "drop."
                ),
            ),
            b.power(
                "Form of Man",
                0,
                0,
                "Corpus",
                does="Once embodied, takes any human shape, and drops it at will.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Imposes the Obsession of Pride or Envy, for 1 to 3 points.",
            ),
            b.power(
                "Contagious Obsession",
                1,
                0,
                "Mentem",
                does=(
                    "One point per victim. Whoever falls to its Envy carries "
                    "it on: anyone hurt by the victim's new vice must resist "
                    "it in turn or become a carrier too, up to the points "
                    "spent."
                ),
            ),
            b.power(
                "Grant the Master's Potential",
                10,
                -17,
                "Vim",
                rtd=("Touch", "Mom", "Ind"),
                does=(
                    "A Ritual: raises the Characteristic behind the target's "
                    "craft to +3, or by 1 if that is better (as Great "
                    "Characteristic). Usually lent and taken back when a "
                    "condition set at the gift is broken; given for good, it "
                    "costs the demon Might and leaves the target Tainted "
                    "with Evil."
                ),
            ),
            b.power(
                "Grant the Master's Insight",
                5,
                -7,
                "Vim",
                rtd=("Touch", "Mom", "Ind"),
                does=(
                    "A Ritual: +2 to the target's craft Ability, as Puissant "
                    "Ability and on top of it, lent or given on the same "
                    "terms as the Master's Potential."
                ),
            ),
            b.power(
                "Shroud the Stench of the Pit",
                0,
                3,
                "Vim",
                does=(
                    "Variable cost. Makes another power or aura seem Magic, "
                    "Faerie or wholly mundane, hiding it even from Sense "
                    "Holiness and Unholiness, for the cost (or magnitude) of "
                    "what it hides and as long as that lasts."
                ),
            ),
        ],
        vis=[BodyVis(8, "Vim", "in its tongue and eyes")],
        appearance=(
            "A handsome, fittingly dressed man or woman, whichever suits the "
            "victim, always with a dagger at the belt and fine tools of the "
            "victim's own trade."
        ),
        notes=(
            "It plays muse to a craftsman, "
            "feeding his pride while sowing envy among those around him, "
            "until whole guilds are corrupted; a dagger left lying about "
            "invites murder. Its Might lets it slip through many Aegises, "
            "and it would happily join a Verditius's forge companions."
        ),
        place=at("Gascony"),
    )
    tie(cenodoxus, spirits, "Pride and Envy, still in Gascony")
    tie(cenodoxus, "Bordeaux", "hunts its crowds")

    adrian = b.creature(
        "Adrian, the Voice of Safety",
        page="p. 54",
        order="Spirit of Deceit",
        hierarchy=4,
        weakness="cannot harm Crusaders",
        realm="Infernal",
        might=30,
        form="Vim",
        size=0,
        block={
            "characteristics": _chars(0, 1, 2, 2, 4, 4, 2, 2),
            "virtues_flaws": [_puissant("Charm"), _puissant("Guile"), "Weak-Willed"],
            "abilities": [
                ("Brawl", 5, "Dodge"),
                ("Carouse", 4, "appearing drunk"),
                ("Charm", 5, "first encounters"),
                ("Etiquette", 5, "nobles"),
                ("Folk Ken", 5, "humans"),
                ("Guile", 7, "convincing others"),
                ("Perform", 5, "guitarra latina"),
                ("Theology", 4, "duty"),
            ],
            "traits": {
                "Deceptive": 6,
                "Acedia": 3,
                "Persuasive": 3,
                "Spirit of Deceit Demon": 3,
                "Trustworthy": -5,
            },
            "reputations": {"The Convincing Silver Tongue of Doubt (Infernal)": 4},
        },
        attacks=[
            b.attack("Dodge", 2, None, 8, None),
            b.attack("Fist", 2, 7, 7, 4),
        ],
        soak=4,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Change Form",
                0,
                0,
                "Corpus",
                does=(
                    "Takes any human shape from Size -2 to +2, most often a "
                    "troubadour with a guitar."
                ),
            ),
            b.power(
                "Trust of the Innocent",
                1,
                -1,
                "Mentem",
                does=(
                    "The target sets judgment aside and believes one "
                    "plausible lie until shown otherwise; an Intelligence "
                    "roll against 6 resists."
                ),
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Imposes the Obsession of Acedia or Sloth, for 1 to 3 points.",
            ),
            b.power(
                "Coagulation",
                3,
                -1,
                "Corpus",
                does=(
                    "Builds a body over 30 rounds of manifesting; dissolves "
                    "it with a round's concentration."
                ),
            ),
            b.power(
                "Forked Tongue of the Serpent",
                3,
                -1,
                "Mentem",
                does=(
                    "The target believes any lie, however absurd, until he "
                    "repeats it to someone and hears how foolish it sounds; "
                    "an hourly Intelligence roll against 9, from an hour "
                    "after, also breaks it."
                ),
            ),
            b.power(
                "The Serpent's Oracle",
                2,
                -3,
                "Vim",
                does=(
                    "Duplicates any non-Ritual Intellego spell, or glimpses "
                    "the immediate consequences of one future act."
                ),
            ),
            b.power(
                "Strangle the Noble Endeavor",
                5,
                0,
                "Mentem",
                does=(
                    "Gives a flawless moral and scriptural argument for its "
                    "point, usually that going on crusade ruins one's loved "
                    "ones. Intelligence + Theology against 9, first a day "
                    "later and then monthly, sees through it; someone else "
                    "may explain the flaw and roll for the victim."
                ),
            ),
        ],
        vis=[BodyVis(6, "Vim", "in its hands")],
        appearance=(
            "A handsome troubadour or lovely trobairitz wandering the "
            "country, carrying news and playing for peasant and lord alike."
        ),
        notes=(
            "It tells of atrocities done in the Narbonnais and "
            "overseas in faith's name and talks people out of joining "
            "either the Crusade or the Cathars' defence: the sloth of "
            "standing aside. It wanders Gascony."
        ),
        place=at("Gascony"),
    )
    tie(adrian, spirits, "Sloth, still in Gascony")

    julian = b.creature(
        "Julian/Julia, the Tempter of the Way of St. James",
        page="p. 55",
        order="Tempters (Incubi/Succubi)",
        hierarchy=3,
        weakness="cannot harm those who have already lost a love",
        realm="Infernal",
        might=15,
        form="Vim",
        size=0,
        block={
            "characteristics": _chars(1, 2, 3, 2, 2, 3, 2, 2),
            "virtues_flaws": [
                "Improved Characteristics",
                "Improved Characteristics",
                _puissant("Charm"),
                _puissant("Guile"),
                "Weak-Willed",
            ],
            "abilities": [
                ("Awareness", 3, "humans"),
                ("Brawl", 2, "club"),
                ("Charm", 7, "first encounters"),
                ("Concentration", 3, "maintaining concentration"),
                ("Folk Ken", 7, "humans"),
                ("Guile", 7, "seduction"),
                ("Penetration", 3, "Hag Ride"),
            ],
            "traits": {
                "Selfish": 5,
                "Deceptive": 4,
                "Lustful": 4,
                "Tempter Demon": 3,
                "Cowardly": 2,
            },
            "reputations": {
                "The Despoiler of the Pious (Infernal)": 3,
                "Clever (Pilgrimage Hostels)": 1,
            },
        },
        attacks=[
            b.attack("Club", 3, 7, 6, 5),
            b.attack("Fist", 2, 4, 4, 2),
        ],
        soak=3,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                2,
                -1,
                "Corpus",
                does="Takes a material body, and drops it at will.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Imposes the Obsession of Betraying Lust, for 1 to 3 points.",
            ),
            b.power(
                "Harness the Wind",
                1,
                0,
                "Corpus",
                does=(
                    "Flies from one place to another, until journey's end or "
                    "dawn; it keeps what it carries, unlike a demon that "
                    "simply dissolves and re-forms elsewhere."
                ),
            ),
            b.power(
                "Hag Ride",
                1,
                0,
                "Corpus",
                does=(
                    "Rides a victim for a night: awake but helpless, he "
                    "loses a long-term Fatigue level and recovers none that "
                    "night, and can move again at dawn."
                ),
            ),
            b.power(
                "Mutable Gender",
                0,
                0,
                "Corpus",
                does=(
                    "Shifts at will to any man's or woman's form; Julian is "
                    "most often a black-haired, roguish young man in "
                    "pilgrim's clothes."
                ),
            ),
        ],
        vis=[BodyVis(3, "Vim", "in its belt buckle")],
        appearance=(
            "A lively young man or woman of about twenty, richly but "
            "suggestively dressed in deep blues and browns, hanging on the "
            "victim's every word."
        ),
        notes=(
            "An incubus or succubus. It preys on pilgrims "
            "along the Way of St. James, haunting the Blaye ferry and the "
            "crowds of Bordeaux."
        ),
        place=at("Gascony"),
    )
    tie(julian, spirits, "Lust, still in Gascony")
    tie(julian, "Blaye", "haunts the ferry crossing")
    tie(julian, "Bordeaux", "hunts its crowds")

    oriande = b.creature(
        "Oriande la Fée",
        page="p. 57",
        confidence=(1, 3),
        realm="Faerie",
        might=50,
        form="Herbam",
        size=0,
        block={
            "characteristics": _chars(4, 0, 4, 4, 1, 2, 2, 0),
            "virtues_flaws": [
                "Focus Power",
                "Focus Power",
                _great("intelligence"),
                _great("presence"),
                _great("communication"),
                *["Greater Power"] * 3,
                "Faerie Sight",
                "Faerie Speech",
                "Humanoid Faerie",
                "Highly Cognizant",
                *["Improved Characteristics"] * 6,
                *["Increased Faerie Might (Minor)"] * 9,
                "Improved Powers",
                "Improved Powers",
                "Lesser Power",
                *["Personal Power"] * 3,
                "Time or Place of Power",
                "Pretentious",
                "Monstrous Appearance",
                ("Vulnerable to {substance} (Major)", {"substance": "Iron"}),
                "Poor Combatant",
                "Restricted Might (Minor)",
                "Susceptible to Deprivation",
                ("Traditional Ward", {"ward": "Divine"}),
            ],
            "abilities": [
                ("Area Lore: Provence", 6, "Gascony"),
                ("Animal Handling", 6, "woodland creatures"),
                ("Artes Liberales", 3, "Astronomy"),
                ("Athletics", 3, "dance"),
                ("Awareness", 2, "within court"),
                ("Bargain", 7, "setting favorable terms"),
                ("Brawl", 1, "dodge"),
                ("Carouse", 6, "appearing intoxicated"),
                ("Charm", 6, "knights"),
                ("Concentration", 3, "remaining focused"),
                ("Etiquette", 7, "inciting insult"),
                ("Faerie Speech", 6, ""),
                ("Finesse", 6, "Rego"),
                ("Folk Ken", 2, "men"),
                ("Guile", 3, "entendres"),
                ("Intrigue", 5, "confounding conversation"),
                ("Leadership", 6, "directing fae"),
                ("Organization Lore: Order of Hermes", 4, "Merinita"),
                ("Penetration", 6, "Rego"),
                ("Profession: Storyteller", 4, "history"),
                ("Survival", 4, "fens"),
            ],
            "traits": {"Curious": 4, "Aloof": 3, "Faerie Queen": 3, "Meddling": 3},
            "reputations": {
                "Cruel (local)": 3,
                "Meddlesome (Knights)": 3,
                "Observant (region)": 3,
            },
        },
        attacks=[b.attack("Fist", 0, 3, 1, 1)],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Call of the Kept",
                0,
                0,
                "",
                rtd=("Voice", "Mom", "Ind"),
                does=(
                    "Non-Hermetic: cues one of her faerie allies to appear "
                    "and act as she bids."
                ),
            ),
            b.power(
                "Caress of the Lethe",
                4,
                -4,
                "Mentem",
                rtd=("Touch", "Until", "Ind"),
                does=(
                    "Whoever she touches forgets his mortal life until he "
                    "sees some object, or kind of object, tied to his home."
                ),
            ),
            b.power(
                "Dream's Undeniable Invitation",
                1,
                -1,
                "Corpus",
                rtd=("Voice", "Sun", "Ind"),
                does="Puts a person within earshot to sleep.",
            ),
            b.power(
                "Enthralling Sound",
                3,
                -3,
                "Mentem",
                rtd=("Voice", "Sun", "Group"),
                does=(
                    "Her storytelling stirs, or heightens, one emotion in "
                    "everyone listening; a stress roll on a fitting "
                    "Personality Trait against 9 shakes it off."
                ),
            ),
            b.power(
                "Extended Glamour",
                0,
                0,
                "Mentem",
                does=(
                    "Constant: takes over a mundane place and makes it part "
                    "of her faerie kingdom."
                ),
            ),
            b.power(
                "Focus Power (Plants within her realm)",
                10,
                0,
                "Herbam",
                does=(
                    "Up to 10 points: any Herbam effect up to tenth "
                    "magnitude, with 10 Intricacy points spent on "
                    "Initiative."
                ),
            ),
            b.power(
                "On the Breath of the Wind",
                5,
                -5,
                "Herbam",
                rtd=("Per", "Until", "Ind"),
                does=(
                    "Becomes a whirling breeze of the season's leaves until "
                    "she chooses to take her own shape again."
                ),
            ),
            b.power(
                "The Price of Impertinence",
                5,
                -5,
                "Animal",
                rtd=("Voice", "Until", "Ind"),
                does=(
                    "Turns a person within earshot into a small woodland "
                    "beast (squirrel, hare, fawn, hedgehog, polecat) until a "
                    "condition she sets is met."
                ),
            ),
        ],
        vis=[BodyVis(10, "Herbam", "in her antlers")],
        equipment=(
            "A glass-bladed dagger, which she sometimes gives a knight to use "
            "within her lands, where it becomes whatever weapon he wants; "
            "faeries know it as her token."
        ),
        appearance=(
            "A beautiful, olive-skinned woman with moss-grown wooden antlers "
            "in wild, flower-threaded hair and amber eyes cold with "
            "arrogance, dressed in leaves and cobweb lace, trailing fireflies "
            "or snowflakes. The land grows lovelier in the season's way "
            "where she walks."
        ),
        notes=(
            "Faerie queen of the lands from the Gironde to the Pyrenees and "
            "the Camargue. Faerie Might 60 within her demesne. Her Place of "
            "Power is the Médoc; her Personal Powers and "
            "Restricted Might (Storm) are as printed. Once honoured as a "
            "form of Sirona, she now plays the capricious challenger of "
            "knights and pilgrims, taking hostages and treasures and making "
            "them win them back, and loses interest in those who become "
            "faeries. Maugris and Dama have both stayed at her court."
        ),
        place=at("Rosefleur"),
    )
    tie(oriande, "The Court of Rosefleur", "its queen")

    b.creature(
        "Unicorn",
        page="p. 59",
        cunning=True,
        confidence=(2, 5),
        encumbrance="0 (0)",
        tires=False,
        realm="Divine",
        might=20,
        form="Animal",
        size=3,
        season="Summer",
        block={
            "characteristics": _chars(-2, 2, 2, -2, 6, 3, 1, -1),
            "virtues_flaws": [
                ("Greater Purifying Touch", {"disease": "poison"}),
                "Improved Characteristics",
                "Long-Winded",
                "Sense Holiness and Unholiness",
                "Unaffected by The Gift",
                "Mute",
                "No Hands",
                ("Baneful Circumstances", {"circumstance": "virgin women"}),
                "Compassionate (Minor)",
                "Reclusive",
                "Weakness (Minor)",
                "Greater Power",
                "Improved Abilities",
                "Improved Confidence",
                "Improved Initiative",
                *["Improved Might"] * 3,
                *["Improved Powers"] * 3,
                "Improved Recovery",
                "Lesser Power",
                *[_minor("Improved Characteristics")] * 3,
                "No Fatigue",
            ],
            "abilities": [
                ("Area Lore: Local Region", 1, "hidden places"),
                ("Athletics", 5, "galloping"),
                ("Awareness", 3, "humans"),
                ("Brawl", 4, "alicorn"),
                ("Concentration", 2, "Sense Virginity"),
                ("Folk Ken", 3, "humans"),
                ("Penetration", 4, "Sense Virginity"),
                ("Sense Holiness and Unholiness", 4, "women"),
                ("Stealth", 5, "remaining unseen"),
                ("Survival", 4, "forests"),
            ],
            "traits": {"Brave": 3, "Pure": 3, "Unicorn": 3, "Cautious": 2},
            "reputations": {
                "Reclusive Beast of the Woods (local)": 3,
                "Symbol of Romantic Love (Languedoc)": 2,
            },
        },
        attacks=[
            b.attack("Hooves", 1, 7, 5, 7),
            b.attack("Alicorn", 4, 9, 6, 9),
        ],
        soak=3,
        fatigue_levels="OK, 0, 0, -1, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Righteous Fury",
                4,
                0,
                "Animal",
                rtd=("Per", "Sun", "Ind"),
                level=40,
                does=(
                    "Wreathed in soft white light, its hooves and horn turn "
                    "razor-keen with holy power: +5 to all Attack and Damage."
                ),
            ),
            b.power(
                "Sense Virginity",
                3,
                3,
                "Corpus",
                rtd=("Eye", "Conc", "Ind"),
                level=15,
                does="Looking into someone's eyes, it knows whether they are a virgin.",
            ),
        ],
        vis=[BodyVis(4, "Animal", "Divinely aligned, in its horn (the alicorn)")],
        appearance=(
            "A charger fit for a king, but with a goat's cloven hooves and "
            "beard, a lion's tail and a slender spiral horn."
        ),
        notes=(
            "Built with the Magic rules but turned to the Divine: its Divine "
            "Animal and Divine Master Virtues (not in the catalog) work as "
            "Magic Animal and Magical Master. It spends Confidence instead of "
            "Fatigue on its Purifying Touch, though the book also prints "
            "Fatigue levels for it. Its "
            "Baneful Circumstances and Weakness are virgin women. Natural "
            "weapon: alicorn (Init +2, Atk +3, Def +2, Dam +3). Seen at the "
            "edge of the woods on the moors of Bazas, where shepherds take "
            "it as a sign of three safe days."
        ),
        place=at("The Moors of Bazas"),
    )

    b.creature(
        "Matagot",
        page="p. 62",
        confidence=(1, 3),
        realm="Magic",
        might=15,
        form="Animal",
        size=-3,
        season="Summer",
        how_many="many, around the ruins of Nemetannais",
        block={
            "characteristics": _chars(0, 1, -2, -4, -7, 0, 3, 4),
            "virtues_flaws": [
                "Magic Animal",
                "Luck",
                "Perfect Balance",
                _puissant("Awareness"),
                "Sharp Ears (Minor)",
                "Unaffected by The Gift",
                "Magical Friend",
                "Nocturnal",
                "Proud (Minor)",
                "Tainted With Evil",
                "Vow (Minor)",
                "Ritual Power",
                "Ritual Power",
                "Improved Abilities",
                "Improved Powers",
                "Improved Recovery",
                "Improved Soak",
                "Lesser Power",
                _minor("Shapeshifter"),
                _minor("Tough"),
                "Susceptible to Deprivation",
                "Ambush Predator",
                "Crafty",
                "Good Jumper",
                "Skilled Climber",
                "Thick Fur/Thick Scales",
            ],
            "abilities": [
                ("Area Lore: Local", 2, "villages"),
                ("Athletics", 3, "chase"),
                ("Awareness", 4, "humans"),
                ("Brawl", 4, "claws"),
                ("Guile", 2, "playing dead"),
                ("Hunt", 4, "birds"),
                ("Living Language: Occitan", 4, "conversational"),
                ("Shapeshifter", 4, "human"),
                ("Stealth", 5, "remaining unseen"),
                ("Survival", 3, "home"),
            ],
            "traits": {
                "Cat": 3,
                "Curious": 4,
                "Cruel": 3,
                "Deceptive": 3,
                "Vindictive": 3,
                "Independent": 2,
            },
            "reputations": {
                "Evil (local)": 3,
                "Strange and double-edged creatures (regional)": 2,
            },
        },
        attacks=[
            b.attack("Claws", 3, 10, 12, -5),
            b.attack("Teeth", 4, 10, 9, -6),
        ],
        soak=6,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Quid Pro Quo",
                1,
                -10,
                "Terram",
                rtd=("Touch", "Mom", "Ind"),
                level=35,
                does=(
                    "A Ritual Power: makes a hidden hoard of coins worth "
                    "about 20 Mythic Pounds, under a house or in a "
                    "foundation, and doles it out when its family behaves as "
                    "it likes. The coins copy a local coin it knows, or bear "
                    "a strange design. Using it lowers its Might Score until "
                    "it spends a season in a Magic aura of 3 or eats 15 "
                    "pawns of Animal vis."
                ),
            ),
            b.power(
                "Wages of Greed",
                5,
                -6,
                "Corpus",
                rtd=("Voice", "Sun", "Ind"),
                level=25,
                does=(
                    "Racks a person with pain that keeps him from his daily "
                    "work without wounding him; kept for those who will not "
                    "let it go."
                ),
            ),
        ],
        vis=[BodyVis(3, "Animal", "in its tail")],
        appearance=(
            "A big, dark calico cat flecked with gold, with tufted ears and "
            "cruel dark eyes. A kind of magical creature in its own right, "
            "not a line of magic cats."
        ),
        notes=(
            "Its Vow: it serves whoever first feeds it "
            "until that person dies or frees it. Said to descend from the "
            "familiars of Nemetannais's Diedne magi; the country round La "
            "Romieu teems with them."
        ),
        place=at("Nemetannais"),
    )

    b.creature(
        "Lou Carcolh",
        page="p. 63",
        cunning=True,
        confidence=(1, 3),
        encumbrance="0 (0)",
        realm="Magic",
        might=25,
        form="Animal",
        size=5,
        season="Summer",
        block={
            "characteristics": _chars(0, 0, -2, -5, 10, 7, 1, -3),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                "Greater Immunity (Deprivation)",
                "Ferocity",
                "Homing Instinct",
                "Improved Characteristics",
                _puissant("Brawl"),
                "Tough",
                "Mute",
                "No Hands",
                "Compulsion (Minor)",
                "Greater Power",
                "Greater Power",
                "Improved Defense",
                "Improved Initiative",
                "Improved Initiative",
                ("Improved {characteristic}", {"characteristic": "stamina"}),
                ("Improved {characteristic}", {"characteristic": "stamina"}),
                *["Improved Might"] * 5,
                *["Improved Powers"] * 3,
                "Improved Soak",
                "Lesser Power",
            ],
            "abilities": [
                ("Area Lore: Local Region", 3, "trade routes"),
                ("Athletics", 4, "moving"),
                ("Awareness", 5, "humans"),
                ("Brawl", 5, "tentacle"),
                ("Concentration", 2, "Sense the Quivering Prey"),
                ("Hunt", 3, "people"),
                ("Penetration", 3, "Grasping Tentacles"),
                ("Stealth", 4, "remaining unseen"),
                ("Survival", 4, "finding prey"),
            ],
            "traits": {"Lou Carcolh": 3, "Ravenous": 2, "Uncaring": 2},
            "reputations": {
                "The Terrible Monster which Eats Travelers (Local Area)": 4,
                "Strange Beast of Legend (Local)": 2,
            },
        },
        attacks=[
            b.attack("Fangs", -3, 12, 6, 15),
            b.attack("Tentacle", 3, 14, 11, 14),
            b.attack("Grapple", -3, 8, 4, None),
        ],
        soak=11,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Viscous Travel",
                2,
                -6,
                "Animal",
                rtd=("Per", "Conc", "Ind"),
                level=30,
                does=(
                    "Slides over any ground, unhindered by brambles, wreckage "
                    "or rubble smaller than itself."
                ),
            ),
            b.power(
                "Grasping Tentacles",
                2,
                2,
                "Animal",
                rtd=("Per", "Diam", "Part"),
                level=45,
                does=(
                    "Shoots out a tentacle to strike up to 100 paces away "
                    "with no penalty for the distance; each tentacle is a "
                    "fresh use."
                ),
            ),
            b.power(
                "Sense the Quivering Prey",
                2,
                -4,
                "Imaginem",
                rtd=("Per", "Conc", "Touch"),
                level=10,
                does=(
                    "Feels the shapes of creatures through the air with its "
                    "tentacles: crude, and blind to whether a body lives."
                ),
            ),
        ],
        vis=[BodyVis(5, "Animal", "in its tentacles")],
        appearance=(
            "A vast snail with a dragon's head, a beard of a score of "
            "tentacles that reach impossibly far, and a mouth of teeth as "
            "long as a forearm; its lumpy shell and pebbled hide turn most "
            "blades, and it leaves a trail of thick slime."
        ),
        notes=(
            "Its Ferocity is for trying to eat people, its "
            "Homing Instinct for its cavern and its Compulsion is to eat "
            "people. Natural weapons: fangs (Init 0, Atk +4, Def +2, Dam "
            "+5), tentacle (Init 0, Atk +5, Def +3, Dam +4). It keeps near "
            "its cave in the hills by Bayonne, eating pilgrims mostly; the "
            "Sorginak watch it and sometimes lead troublemakers to it."
        ),
        place=at("The Lou Carcolh's Cavern"),
    )

    b.creature(
        "Sarda Whale",
        page="p. 66",
        cunning=True,
        confidence=(0, 0),
        size=9,
        how_many="pods off the Basque coast",
        block={
            "characteristics": _chars(-3, -2, 2, 0, 19, 5, 2, -4),
            "virtues_flaws": [
                "Improved Characteristics",
                "Reserves of Strength",
                "Tough",
                "Poor Eyesight",
                "Aquatic",
                "Defensive Fighter",
                "Hardy",
                *["Imposing Appearance"] * 3,
                "Tireless",
                "Tough Hide",
                "Vocal",
            ],
            "abilities": [
                ("Awareness", 2, "food"),
                ("Brawl", 4, "dodge"),
                ("Music", 3, "bellowing"),
                ("Survival", 5, "coastlines"),
                ("Swim", 5, "coastlines"),
            ],
            "traits": {"Patient": 3, "Cruel": 2, "Hungry": 2},
            "reputations": {"Creature which drowns sailors (coastlines)": 3},
        },
        attacks=[b.attack("Tail", -4, 10, 2, 24)],
        soak=10,
        fatigue_levels="OK, 0, 0, -1, -1, -3, -3, -5, -5, Unconscious",
        appearance=(
            "A huge, odd fish with a sweet smell from its great mouth, thick "
            "pebbled skin instead of scales, and a tail that lies flat."
        ),
        notes=(
            "A mundane beast. Natural weapon: tail (Init 0, "
            "Atk +4, Def +2, Dam +5). Ill-tempered, it smashes or overturns "
            "the boats of fishermen who harass it. The whalers of Bayonne "
            "hunt it; the bones of a Whale of Virtue hold Animal vis and "
            "its baleen Aquam vis."
        ),
        place=at("The Whaling Grounds of Bayonne"),
    )

    maju = b.creature(
        "The Serpent (Maju)",
        page="p. 72",
        order="Duke of False Gods",
        hierarchy=7,
        weakness="cannot harm those who have given alms that day",
        realm="Infernal",
        might=45,
        form="Vim",
        size=-2,
        block={
            "characteristics": _chars(2, 1, 2, 1, 4, 5, 4, 4),
            "virtues_flaws": [
                _puissant("Charm"),
                _puissant("Guile"),
                "Overconfident (Minor)",
            ],
            "abilities": [
                ("Artes Liberales", 7, "astronomy"),
                ("Awareness", 5, "identifying magi"),
                ("Bargain", 7, "pacts"),
                ("Brawl", 5, "Dodge"),
                ("Carouse", 5, "appearing drunk"),
                ("Ceremony", 3, "summoning"),
                ("Charm", 5, "first encounters"),
                ("Dominion Lore", 5, "angels"),
                ("Etiquette", 5, "magi"),
                ("Faerie Lore", 5, "mannerisms"),
                ("Faerie Magic", 3, "experimentation"),
                ("Folk Ken", 4, "humans"),
                ("Guile", 7, "appearing mundane"),
                ("Magic Theory", 4, "learning spells"),
                ("Music", 6, "guitar"),
                ("Infernal Lore", 6, "demons"),
                ("Intrigue", 6, "long-term plans"),
                ("Philosophiae", 5, "ceremonial magic"),
                ("Teaching", 4, "magic"),
                ("Theology", 3, "contradictions"),
            ],
            "traits": {
                "Deceptive": 6,
                "Proud": 6,
                "Clever": 3,
                "Persuasive": 3,
                "False God Demon": 3,
                "Trustworthy": -5,
            },
            "reputations": {"Duke of Hell (Infernal)": 7},
        },
        attacks=[b.attack("Fist", 4, 9, 9, 4)],
        soak=5,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Change Form",
                0,
                0,
                "Corpus",
                does=(
                    "Takes any humanoid shape from Size -2 to +2, often a "
                    "troubadour with a guitar or a little winged sprite."
                ),
            ),
            b.power(
                "Shapeshifter",
                0,
                0,
                "Animal",
                does=(
                    "Takes any beast's shape from Size -2 to +2, fabulous "
                    "ones included; most often a dove, a hare or a snake."
                ),
            ),
            b.power(
                "A Pretty Cloak to Wrap it Within",
                9,
                0,
                "Imaginem",
                does="Up to 9 points: any Imaginem effect up to ninth magnitude.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Imposes Cruelty, Greed or Pride, for 1 to 3 points.",
            ),
            b.power(
                "Coagulation",
                5,
                -1,
                "Corpus",
                does=(
                    "Builds a body over 45 rounds of manifesting; dissolves "
                    "it with a round's concentration."
                ),
            ),
            b.power(
                "Lend Senses",
                1,
                0,
                "Mentem",
                does=(
                    "Lends its hearing or sight to someone it touches, "
                    "indefinitely, until the eavesdropper witnesses an act "
                    "of religious devotion."
                ),
            ),
            b.power(
                "Shroud the Stench of the Pit",
                0,
                3,
                "Vim",
                does=(
                    "Variable cost. Makes another power or aura seem Magic, "
                    "Faerie or mundane, even to Sense Holiness and "
                    "Unholiness, for the cost (or magnitude) of what it "
                    "hides. It keeps Mimizan's Infernal aura cloaked, so it "
                    "normally has only 42 Might Points to spend."
                ),
            ),
            b.power(
                "Wealth of Nations",
                3,
                0,
                "Terram",
                does=(
                    "Fetches riches worth up to 45 pounds of gold, of any "
                    "kind valued for itself, not made but taken from "
                    "wherever corrupts most: a distant treasury or a "
                    "bystander's purse."
                ),
            ),
            b.power(
                "His Master's Voice",
                0,
                1,
                "Vim",
                does=(
                    "Variable cost. Summons other demons or corrupt beasts "
                    "to it, a Might Point for each point of their Infernal "
                    "Might, without any control over them."
                ),
            ),
            b.power(
                "The Serpent's Oracle",
                2,
                -3,
                "Vim",
                does=(
                    "Duplicates any non-Ritual Intellego spell, or glimpses "
                    "the immediate consequences of one future act."
                ),
            ),
        ],
        vis=[BodyVis(9, "Vim", "in its eyes")],
        appearance=(
            "As Dama's familiar, usually a small winged faerie sprite, or a "
            "hare, snake or dove as suits; in private a snake coiled about "
            "her, teasing her with the threat of strangling."
        ),
        notes=(
            "Dama of Merinita's familiar, called Sugaar among the Basques. "
            "Once a Gaulish god, "
            "it is sliding wholly into the Infernal as it plays a long game "
            "to corrupt both Church and Order through Dama's cult. It waited "
            "as a viper when Dama ambushed the Quaesitor Tibaut, and its "
            "venom killed him."
        ),
        place=at("Dama's Tower at Mimizan"),
    )
    tie(maju, "The Serpent's Venom", "Dama's familiar, the demon behind her cult")
    provence.b.link(provence.magi["dama"], "creatures", maju, "her familiar")


def _pyrenees(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    b.creature(
        "Pyrene the Spectre",
        page="p. 80",
        confidence=(1, 3),
        encumbrance="0 (0)",
        tires=False,
        realm="Magic",
        might=14,
        form="Mentem",
        size=-1,
        season="Autumn",
        block={
            "characteristics": _chars(0, 1, 6, 1, -2, 0, 1, 1),
            "virtues_flaws": [
                "Magic Spirit",
                "Magical Monster",
                "Good Teacher",
                _great("presence"),
                _great("presence"),
                "Homing Instinct",
                ("Inoffensive to {being}", {"being": "Animals"}),
                "Lesser Power",
                "Lesser Power",
                ("{land} Regio Network", {"land": "Mountain"}),
                ("Voice of the {land}", {"land": "Mountains"}),
                "Curse of Venus",
                "Magical Air",
                ("Baneful Circumstances", {"circumstance": "day"}),
                "Proud (Minor)",
                "Small Frame",
                "Soft-Hearted",
                ("Improved {characteristic}", {"characteristic": "presence"}),
                "Improved Abilities",
                "Improved Abilities",
                *["Improved Might"] * 4,
                "Improved Powers",
            ],
            "abilities": [
                ("Animal Ken", 4, "pacifying"),
                ("Area Lore: Pyrenees", 5, "passes"),
                ("Athletics", 2, "sprinting"),
                ("Awareness", 5, "the living"),
                ("Brawl", 2, "dodge"),
                ("Charm", 5, "apologies"),
                ("Dead Language: Gothic", 4, "commands"),
                ("Dead Language: Latin", 4, "commands"),
                ("Etiquette", 4, "nobles"),
                ("Folk Ken", 3, "discerning motivation"),
                ("Intrigue", 2, "spotting conspiracy"),
                ("Leadership", 2, "maintaining a household"),
                ("Living Language: Euskara", 5, "conversation"),
                ("Living Language: Occitan", 4, "commands"),
                ("Magic Lore", 5, "creatures"),
                ("Stealth", 3, "keeping hidden"),
            ],
            "traits": {"Grieving": 3, "Reclusive": 3, "Proud": 2},
            "reputations": {"Weeping woman of the hills (local)": 3},
        },
        attacks=[b.attack("Fist", 1, 3, 3, -2)],
        soak=4,
        fatigue_levels="None",
        powers=[
            b.power(
                "Invisibility",
                0,
                -1,
                "Imaginem",
                rtd=("Touch", "Conc", "Ind"),
                level=15,
                does="Turns invisible at will, though Second Sight still sees her.",
            ),
            b.power(
                "Donning the Corporeal Veil",
                0,
                -2,
                "Corpus",
                does="Takes on a solid body.",
            ),
        ],
        vis=[BodyVis(3, "Mentem", "in her dress")],
        appearance=(
            "A pale, ghostly, achingly beautiful black-haired woman with "
            "mangled lower legs, bloody feet and a tear-stained face, in "
            "nothing but a torn linen shift."
        ),
        notes=(
            "The ghost of the nymph Heracles seduced, torn apart by beasts "
            "and buried under the cairn the mountains grew from. Her Homing "
            "Instinct is for the boulder at the vis site; "
            "she also has Master of Magic Creatures (not in the catalog). "
            "The printed Invisibility notes 25 levels against its PeIm 15 "
            "effect. On the night of her death she weeps at the cairn until "
            "dawn."
        ),
        place=at("The Cairn of Pyrene"),
    )


def _narbonnais(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    old_man = b.creature(
        "Old Man of the Bridge: The Tempter of St. Thibery",
        page="p. 100",
        order="Tempters (tenetores)",
        hierarchy=0,
        weakness=(
            "it can do nothing until it has counted coins thrown on the "
            "ground into its purse"
        ),
        realm="Infernal",
        might=15,
        form="Vim",
        size=0,
        block={
            "characteristics": _chars(1, 2, -1, 2, 3, 2, 1, 3),
            "virtues_flaws": [_puissant("Charm"), _puissant("Guile"), "Weak-Willed"],
            "abilities": [
                ("Awareness", 3, "humans"),
                ("Brawl", 2, "club"),
                ("Charm", 4, "first encounters"),
                ("Concentration", 3, "maintaining concentration"),
                ("Folk Ken", 3, "humans"),
                ("Guile", 5, "reducing risks"),
                ("Penetration", 1, "Rushing Wages of Greed"),
            ],
            "traits": {
                "Greedy": 5,
                "Selfish": 5,
                "Deceptive": 3,
                "Tricky": 3,
                "Tempter Demon": 3,
                "Cowardly": 2,
            },
        },
        attacks=[
            b.attack("Fist", 3, 3, 5, 3),
            b.attack("Walking Stick (club)", 4, 6, 7, 6),
        ],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Coagulation",
                2,
                -1,
                "Corpus",
                does="Takes a material body, and drops it at will.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Imposes the Obsession of Greed, for 1 to 3 points.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does=(
                    "1 point to enter a sleeper's dream, 5 for a waking "
                    "vision, of life in desperate poverty: a Brave roll "
                    "against 9 or the victim is terrified and loses a "
                    "long-term Fatigue level."
                ),
            ),
            b.power(
                "Change Form",
                0,
                0,
                "Corpus",
                does=(
                    "Takes any human or animal shape at will; it may become "
                    "a raven, or make its bundle of firewood vanish."
                ),
            ),
            b.power(
                "Trove Just Beyond Reach",
                4,
                1,
                "Imaginem",
                rtd=("Sight", "Sun", "Ind"),
                level=20,
                does=(
                    "A phantom strongbox spilling gold and silver into the "
                    "riverbed in plain view of the bridge, in water that "
                    "looks calm, clear and deep enough to dive into."
                ),
            ),
            b.power(
                "Rushing Wages of Greed",
                8,
                -1,
                "Aquam",
                rtd=("Sight", "Conc", "Part"),
                level=40,
                does=(
                    "Churns the water into a fierce current with an "
                    "undertow: Swim rolls at -6 to escape, or the swimmer "
                    "begins to drown."
                ),
            ),
        ],
        vis=[BodyVis(3, "Vim", "in its money purse")],
        appearance=(
            "A wizened old peasant with a great bundle of firewood on his "
            "back, a cane and a lantern."
        ),
        notes=(
            "The demon of Greed among the Six Deadly Spirits. It offers to mind "
            "travellers' goods while they dive for the phantom treasure, "
            "for half the haul, then drowns them."
        ),
        place=at("The Bridge of St. Thibery"),
    )
    tie(old_man, "The Six Deadly Spirits", "Greed, gone to the bridge of St. Thibery")

    b.creature(
        "The Jinn Corsair, Howling Knife of the Dunes",
        page="p. 107",
        encumbrance="0 (0)",
        realm="Faerie",
        might=20,
        form="Vim",
        size=0,
        block={
            "characteristics": _chars(0, 2, 1, 1, 2, 3, 1, 1),
            "virtues_flaws": [
                "Narrowly Cognizant",
                "Passes for Human",
                "External Vis (Major)",
                "Greater Power",
                "Increased Faerie Might (Major)",
                "Faerie Sight",
                "Faerie Speech",
                "Feast of the Fae",
                *["Improved Characteristics"] * 3,
                "Infiltrator (Minor)",
                *["Lesser Power"] * 3,
                "Positive Folktales",
                "Pretentious",
                _puissant("Single Weapon"),
                "Fury",
                ("Sovereign Ward", {"ward": "the person it has agreed to serve"}),
                "Overconfident (Minor)",
                "Pious (Minor)",
                "Role Requires Suffering",
                ("Traditional Ward", {"ward": "Name: Howling Knife of the Dunes"}),
            ],
            "abilities": [
                ("Area Lore: Mediterranean Coasts", 3, "places to come ashore"),
                ("Artes Liberales", 1, "astronomy"),
                ("Athletics", 3, "climbing"),
                ("Awareness", 5, "identifying threats"),
                ("Bargain", 3, "establishing terms"),
                ("Brawl", 4, "fist"),
                ("Faerie Speech", 5, "issuing threats"),
                ("Folk Ken", 3, "humans"),
                ("Leadership", 2, "pirates"),
                ("Profession: Navigator", 1, "staying on course"),
                ("Profession: Sailor", 4, "pirate"),
                ("Single Weapon", 5, "scimitar"),
                ("Survival", 1, "desert"),
            ],
            "traits": {"Brave": 3, "Jinn": 3, "Bargaining": 2},
            "reputations": {
                "Capable Bodyguard (Sahir)": 3,
                "Creature for Hire (Maghreb Pirates)": 2,
            },
        },
        attacks=[
            b.attack("Scimitar", 3, 12, 9, 8),
            b.attack("Fist", 1, 6, 6, 2),
        ],
        soak=6,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Sirocco's Form",
                5,
                -4,
                "Auram",
                rtd=("Per", "Until", "Ind"),
                level=50,
                does=(
                    "Becomes a whirling cyclone of gritty desert wind, able "
                    "to carry one person inside it."
                ),
            ),
            b.power(
                "Sense the Living Treasure",
                3,
                -7,
                "Corpus",
                rtd=("Arc", "Conc", "Ind"),
                level=20,
                does=(
                    "Senses where the person is whose arcane connection he "
                    "holds, the distance and direction growing clearer the "
                    "longer he concentrates."
                ),
            ),
            b.power(
                "Scimitar of Blazing Fury",
                3,
                -8,
                "Ignem",
                rtd=("Touch", "Diam", "Ind"),
                level=20,
                does="Sheathes his blade in white fire: +10 damage.",
            ),
            b.power(
                "Conceal the Precious Charge",
                3,
                -5,
                "Imaginem",
                rtd=("Touch", "Diam", "Ind"),
                level=15,
                does=(
                    "Makes someone he touches invisible to ordinary sight "
                    "whatever they do, though they still cast a shadow."
                ),
            ),
        ],
        vis=[
            BodyVis(1, "Auram", "in his scimitar"),
            BodyVis(1, "Corpus", "in his scimitar"),
            BodyVis(1, "Ignem", "in his scimitar"),
            BodyVis(1, "Imaginem", "in his scimitar"),
        ],
        equipment=(
            "His scimitar (his External Vis: weightless, and its bearer gains "
            "Puissant Single Weapon), fine clothes and whatever his work "
            "needs."
        ),
        appearance=(
            "A handsome, grinning Maghrebi pirate with a brand on his left "
            "cheek, dressed in rich cloth, with a fine scimitar that looks "
            "like glass in the morning light."
        ),
        notes=(
            "His abilities are Pretenses. His Infiltrator Virtue mimics "
            "Branded Criminal; failing a mission drives him to Fury; he is "
            "Pious in Islam. Hired by mortals as a bodyguard, he takes the "
            "duty proudly and has lost a charge only twice, once to a "
            "dragon and once to a magus. He has a bargain with a corsair "
            "who raids the Gulf of Lion; the book prints him with Stella "
            "Durus."
        ),
        place=at("The Gulf of Lion"),
    )


def _arelat(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    b.creature(
        "Drac, Lesser",
        page="p. 116",
        cunning=True,
        confidence=(1, 3),
        realm="Faerie",
        might=15,
        form="Animal",
        size=3,
        how_many="a kind haunting the Rhone and its tributaries",
        block={
            "characteristics": _chars(1, 0, -2, -5, 0, 0, 1, 3),
            "virtues_flaws": [
                "Focus Power",
                "Greater Power",
                "Faerie Beast",
                "Improved Powers",
                "Increased Faerie Might (Minor)",
                "Increased Faerie Might (Minor)",
                "Personal Power",
                "Time or Place of Power",
                "Reputation as Confidence",
                ("{land} Regio Network", {"land": "Rhone"}),
                "Monstrous Appearance",
                "Incognizant",
            ],
            "abilities": [
                ("Area Lore: Rhone", 4, "hiding places"),
                ("Athletics", 2, "lunges"),
                ("Awareness", 3, "prey"),
                ("Brawl", 5, "grapple"),
                ("Concentration", 2, "remaining invisible"),
                ("Folk Ken", 2, "river folk"),
                ("Hunt", 4, "prey"),
                ("Living Language: Occitan", 6, "Provençal"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 3, "river"),
                ("Swim", 2, "rivers"),
            ],
            "traits": {"Cruel": 3},
            "reputations": {"Watery threat (local)": 3},
        },
        attacks=[
            b.attack("Bite", 3, 10, 9, 6),
            b.attack("Grapple", 3, 7, 9, None),
        ],
        soak=2,
        fatigue_levels="OK, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Crafter of Illusion",
                0,
                0,
                "Imaginem",
                does=(
                    "0 to 5 points: any Creo or Rego Imaginem effect of "
                    "fourth magnitude or less, for its magnitude in Might, "
                    "mostly to lure prey (a Focus Power)."
                ),
            ),
            b.power(
                "Transform into Human",
                3,
                0,
                "Animal",
                level=30,
                does="Shrinks from its great natural size to a human's.",
            ),
            b.power(
                "Gift of the Drac",
                3,
                -3,
                "Aquam",
                level=30,
                does=(
                    "Someone it has grappled breathes freely underwater "
                    "until they come up in its air-filled lair or escape to "
                    "the bank."
                ),
            ),
        ],
        vis=[BodyVis(3, "Imaginem", "in its eyes")],
        appearance=(
            "In its true shape a greenish-black worm, long and sinuous, with "
            "webbed legs like a flamingo's and stubby fin-like wings of blue "
            "lace."
        ),
        notes=(
            "Faerie Might +10 more at its Place of Power, the Rhone near "
            "Beaucaire. Its Major Flaw is Cruel (not in the "
            "catalog); its Focus Power is Crafter of Illusion, its Greater "
            "Power Gift of the Drac and its Personal Power Transform into "
            "Human. The Bite includes +3 for its crushing jaws, which open "
            "weakly: a Grapple can hold them shut. A young adult; it lures "
            "washerwomen, children and vagrants into its lair and feeds on "
            "the fear its stories spread. Civilised dracs living among men "
            "as boatmen, washerwomen or merchants lack Monstrous Appearance "
            "and take Infiltrator and Dark Secret instead."
        ),
        place=at("The Drac's Well at Beaucaire"),
    )

    b.creature(
        "A Small Tarasque",
        page="p. 120",
        cunning=True,
        confidence=(1, 3),
        encumbrance="0 (0)",
        tires=False,
        realm="Magic",
        might=20,
        form="Animal",
        size=3,
        season="Summer",
        block={
            "characteristics": _chars(0, 1, -2, -5, 6, 3, 2, -1),
            "virtues_flaws": [
                "Magic Animal",
                "Greater Immunity (Deprivation)",
                ("Greater Immunity", {"hazard": "fire"}),
                "Ferocity",
                "Improved Characteristics",
                "Improved Characteristics",
                "Tough",
                "Magical Monster",
                "Mute",
                "No Hands",
                ("Baneful Circumstances", {"circumstance": "Sincere Holy Displays"}),
                "Weakness (Minor)",
                "Greater Power",
                "No Fatigue",
                "Improved Attack",
                "Improved Attack",
                "Improved Damage",
                "Improved Damage",
                *["Improved Might"] * 3,
                "Improved Powers",
                "Improved Powers",
                *["Improved Soak"] * 7,
                "Personal Power",
                "Monstrous Appearance",
            ],
            "abilities": [
                ("Athletics", 4, "charging"),
                ("Awareness", 4, "humans"),
                ("Brawl", 7, "claws"),
                ("Hunt", 4, "woods"),
                ("Stealth", 2, "remaining unseen"),
                ("Survival", 3, "forests"),
            ],
            "traits": {"Ravenous": 3, "Vicious": 3, "Tarasque": 3, "Cunning": 2},
            "reputations": {
                "Savage Beast from Galacia (local)": 3,
                "Dragon Mesmerized by Hymns (Narbonnais)": 2,
            },
        },
        attacks=[
            b.attack("Large Claws", -1, 17, 10, 13),
            b.attack("Large Teeth", -1, 15, 7, 12),
        ],
        soak=20,
        fatigue_levels="None",
        powers=[
            b.power(
                "Unnatural Flight",
                0,
                0,
                "Animal",
                rtd=("Per", "Sun", "Ind"),
                level=15,
                does="Flies, tirelessly, on wings that ought not to lift it.",
            ),
            b.power(
                "Breath of Flame",
                2,
                0,
                "Ignem",
                rtd=("Voice", "Mom", "Ind"),
                level=40,
                does=(
                    "A gout of fire 3 paces by 3 by 9 long: stress die +25 "
                    "damage to all within."
                ),
            ),
        ],
        vis=[BodyVis(4, "Animal", "in its carapace")],
        appearance=(
            "A scaly winged ox some fifteen paces long, with a roughly "
            "reptilian lion's head, six legs ending in hooked talons, a "
            "tortoise's shell, a leathery tail and sword-like teeth; grey "
            "smoke drifts from its nostrils and mouth."
        ),
        notes=(
            "Kin of the great Tarasque. Its Baneful "
            "Circumstances and Weakness are sincere displays of holiness; "
            "hymns are said to mesmerise it. The book's design notes give "
            "Unnatural Flight as a 25-level Personal Power and Breath of "
            "Flame as a 50-level Greater Power against the 15 and 40 levels "
            "of their effects."
        ),
        place=at("The Tarasque's Lair"),
    )

    b.creature(
        "The Ogre Under the Bridge",
        page="p. 121",
        encumbrance="0 (0)",
        realm="Faerie",
        might=20,
        form="Vim",
        size=3,
        block={
            "characteristics": _chars(1, 1, 0, 1, 6, 3, 1, -3),
            "virtues_flaws": [
                "External Vis (Major)",
                "Increased Faerie Might (Major)",
                "Faerie Sight",
                "Faerie Speech",
                "Feast of the Dead",
                "Huge",
                "Huge",
                "Hybrid Form",
                "Improved Characteristics",
                "Improved Powers",
                "Improved Soak",
                "Improved Soak",
                "Lesser Power",
                "Personal Power",
                "Personal Power",
                "Time or Place of Power",
                "Tough",
                "Monstrous Appearance",
                "Might Recovery Requires Vitality",
                "Incognizant",
                "Role Requires Suffering",
                "Susceptible to Deprivation",
                ("Traditional Ward", {"ward": "Payment: those who pay the toll"}),
            ],
            "abilities": [
                ("Awareness", 4, "humans"),
                ("Bargain", 4, "creating terms"),
                ("Brawl", 5, "club"),
                ("Concentration", 4, "maintaining Seeming of the Menhir"),
                ("Faerie Speech", 5, "sounding intimidating"),
                ("Guile", 3, "bluffing"),
                ("Area Lore: Narbonnais", 3, "surrounding Pont Flavian"),
                ("Stealth", 3, "remaining unseen"),
                ("Survival", 3, "hills"),
                ("Thrown Weapon", 5, "rocks"),
            ],
            "traits": {
                "Destructive": 3,
                "Greedy": 2,
                "Hungry": 3,
                "Ogre": 3,
                "Willing to Barter": 2,
            },
            "reputations": {
                "Ravenous Guardian of the Pont Flavian (Narbonnais)": 3,
                "Sheep and Cattle Thief (local)": 2,
            },
        },
        attacks=[
            b.attack("Club", -5, 13, 6, 15),
            b.attack("Thrown Rock", -6, 13, 4, 14),
            b.attack("Large Claws", -3, 11, 5, 10),
            b.attack("Tusks", -3, 10, 4, 11),
        ],
        soak=10,
        powers=[
            b.power(
                "Stone from the Loam",
                0,
                -4,
                "Terram",
                rtd=("Touch", "Mom", "Part"),
                level=10,
                does="Pulls a throwing stone out of natural earth.",
            ),
            b.power(
                "Seeming of the Menhir",
                0,
                -6,
                "Imaginem",
                rtd=("Per", "Conc", "Ind"),
                level=25,
                does="Looks like a great boulder or standing stone that fits the land.",
            ),
            b.power(
                "Stealth through the Grass",
                2,
                -4,
                "Imaginem",
                rtd=("Per", "Sun", "Ind"),
                level=20,
                does=(
                    "Moves without a sound, though its voice, thrown rocks "
                    "and blows are heard as usual."
                ),
            ),
        ],
        vis=[BodyVis(4, "Corpus", "in the skull netted at its belt")],
        equipment=(
            "A tree-stump club with knotted roots for spikes; a sack of "
            "badly cooked mutton, half-empty casks of poor beer or wine and "
            "throwing stones; a skull in a net (its External Vis, "
            "weightless, granting its bearer Tough)."
        ),
        appearance=(
            "A huge, brutish man with clawed hands and a tusked boar's head, "
            "forearms stained rust-brown to the elbow, in a ragged hide "
            "loincloth with a saddle girth for a belt, and heads in various "
            "states of rot hanging from his waist."
        ),
        notes=(
            "Faerie Might 30 at its Place of Power, the Pont Flavian. No "
            "Fatigue levels are printed. Its abilities are Pretenses. Its "
            "Traditional Ward is payment: it cannot harm those who pay its "
            "toll."
        ),
        place=at("Pont Flavian"),
    )


def _val_negra(provence: Provence, at: Any, tie: Any) -> None:
    b = provence.b
    val_negra = at("Val-Negra")
    fortress = 3
    door = "The Adulteration of Flambeau"

    abaddon = b.creature(
        "Abaddon of Tytalus, the Living Ghost",
        page="p. 139",
        realm="Magic",
        might=50,
        form="Mentem",
        block={
            "traits": {"Eclectic": 5, "Obsessed": 3, "Ruthless": 2},
            "reputations": {"Hermetic Prestige": 4, "Necromancer (Hermetic)": 3},
        },
        notes=(
            "Archmagus of House Tytalus, a Living Ghost and great "
            "necromancer; the book prints only his Might, traits and "
            "reputations (see The Mysteries: Revised Edition for Hermetic "
            "spirit magic). One of the two who subdued the Adulteration and "
            "resealed the Iron Door, he guards it forever and keeps the "
            "Aegis over Val-Negra, empowering items with the willing ghosts "
            "of its magi. He haunts the whole covenant, usually in a strong "
            "young body he conjures and possesses, and is a teasing, "
            "befuddling host who may trust visitors with Aegis tokens. The "
            "Aerie Clan serve him."
        ),
        place=val_negra,
        level=fortress,
    )
    tie(abaddon, door, "its guardian at the Iron Door")

    adulteration = b.creature(
        "The Adulteration of Flambeau",
        page="p. 140",
        confidence=(3, 4),
        tires=False,
        realm="Magic",
        might=65,
        form="Ignem",
        size=0,
        season="Autumn",
        block={
            "characteristics": _chars(4, 1, 2, -1, 1, 4, 0, 0),
            "virtues_flaws": [
                "Magic Spirit",
                "Greater Immunity (Deprivation)",
                *["Improved Characteristics"] * 3,
                _great("intelligence"),
                _great("stamina"),
                "Tough",
                "Warrior",
                "Blatant Magical Air",
                "Magical Monster",
                (
                    "Environmental Magic Condition",
                    {"condition": "Enclosed by the Iron Door"},
                ),
                "Wrathful (Major)",
                "Proud (Minor)",
                *["Focus Power"] * 5,
                *["Greater Power"] * 4,
                "Magical Meditation",
                ("Major Virtue", {"virtue": "Greater Immunity to Fire"}),
                "No Fatigue",
                "Ritual Power",
                "Ritual Power",
                "Vis Mastery",
                *["Improved Abilities"] * 5,
                "Improved Confidence",
                *["Improved Powers"] * 9,
                _minor("Arcane Lore"),
                _minor("Educated"),
                _minor("Unaffected by the Gift"),
                "Improved Recovery",
            ],
            "abilities": [
                ("Awareness", 3, "light sources"),
                ("Concentration", 4, "maintaining"),
                ("Dead Language: Latin", 4, "curses"),
                ("Folk Ken", 4, "sensing lies"),
                ("Guile", 3, "concealing intent"),
                ("Finesse", 5, "Ignem"),
                ("Artes Liberales", 1, "literacy"),
                ("Living Language: French", 5, "Gascony dialect"),
                ("Living Language: Spanish", 5, "Asturian dialect"),
                ("Magical Meditation", 4, "recovery"),
                ("Magic Lore", 4, "Ignem entities"),
                ("Magic Theory", 7, "Ignem"),
                ("Organization Lore: Order of Hermes", 4, "early members"),
                ("Philosophiae", 2, "metaphysics"),
                ("Penetration", 6, "Ignem"),
                ("Area Lore: Pyrenees", 4, "caverns"),
                ("Single Weapon", 5, "longsword"),
                ("Theology", 1, "gospel"),
                ("Thrown Weapon", 4, "javelin"),
                ("Area Lore: Val-Negra", 4, "regio boundaries"),
            ],
            "traits": {"Hard-Hearted": 2, "Proud": 3, "Wrathful": 5},
        },
        soak=7,
        fatigue_levels="N/A",
        powers=[
            b.power(
                "Arc of Fiery Ribbons",
                0,
                0,
                "Ignem",
                rtd=("Voice", "Mom", "Group"),
                level=25,
                does=(
                    "As the spell: a dozen ribbons of fire fanning out over "
                    "sixty degrees, +10 damage. Mastered (Fast Cast, Multiple "
                    "Casting, Penetration)."
                ),
            ),
            b.power(
                "Aura of the Avenger",
                0,
                0,
                "Ignem",
                rtd=("Touch", "Conc", "Ind"),
                level=20,
                does="Cloaks it in flame that burns whatever it touches for +10 damage.",
            ),
            b.power(
                "Aura of Enlightenment",
                0,
                -1,
                "Ignem",
                rtd=("Per", "Conc", "Ind"),
                level=10,
                does="Shines as bright as the noon sun.",
            ),
            b.power(
                "Authority of Ignem",
                1,
                0,
                "Ignem",
                level=50,
                does=(
                    "1 to 10 points, Init less the points spent: any "
                    "non-Ritual Ignem effect up to 50th level, a point per "
                    "magnitude (a Focus Power)."
                ),
            ),
            b.power(
                "Ball of Abysmal Flame",
                0,
                0,
                "Ignem",
                rtd=("Voice", "Mom", "Group"),
                level=35,
                does=(
                    "A ball of fire at one target for +30 damage; mastered "
                    "(Fast Cast, Multiple Casting, Penetration)."
                ),
            ),
            b.power(
                "Eidolon",
                0,
                -2,
                "Imaginem",
                rtd=("Touch", "Conc", "Ind"),
                level=15,
                does=(
                    "A single illusory figure, seen and heard, that moves "
                    "and speaks at its bidding for as long as it wants."
                ),
            ),
            b.power(
                "Curse of Ash",
                5,
                -10,
                "Ignem",
                rtd=("Touch", "Mom", "Ind"),
                does=(
                    "A non-Hermetic Ritual Power: inflicts Deficient Form "
                    "(Ignem). Made permanent, the cost comes off its Might "
                    "Score; otherwise the points return when it lifts the "
                    "Flaw."
                ),
            ),
            b.power(
                "Curse of Cinders",
                5,
                -10,
                "Ignem",
                rtd=("Touch", "Mom", "Ind"),
                does=(
                    "A non-Hermetic Ritual Power: inflicts Incompatible Arts "
                    "(CrIg, ReIg), on the same terms as the Curse of Ash."
                ),
            ),
            b.power(
                "Donning the Corporeal Veil",
                0,
                -3,
                "Corpus",
                rtd=("Touch", "Sun", "Ind"),
                level=25,
                does=(
                    "Takes bodily form until the next sunrise or sunset as a "
                    "sun-darkened old man in a rough brown robe, still "
                    "unsettling because of its Gift."
                ),
            ),
            b.power(
                "Ghost Touch",
                0,
                0,
                "Terram",
                level=25,
                does=(
                    "Variable cost, Init less the points spent: moves loose "
                    "objects, 5 pounds for a point and double for each more; "
                    "hurled, they do +5 damage a point and must penetrate. "
                    "It cannot reach past the Iron Door while the door holds "
                    "(a Focus Power)."
                ),
            ),
            b.power(
                "Pilum of Fire",
                0,
                0,
                "Ignem",
                rtd=("Voice", "Mom", "Group"),
                level=20,
                does=(
                    "The Founder's signature jet of flame, +15 damage; "
                    "mastered (Fast Cast, Multiple Casting, Penetration)."
                ),
            ),
            b.power(
                "Presence",
                0,
                -4,
                "Imaginem",
                rtd=("Arc", "Sun", "Ind"),
                level=35,
                does=(
                    "Knows everything that happens in Val-Negra's innermost "
                    "regio, but can touch nothing beyond the Iron Door while "
                    "the ward holds."
                ),
            ),
            b.power(
                "Smoke on the Wind",
                0,
                0,
                "Ignem",
                rtd=("Per", "Sun", "Ind"),
                level=15,
                does=(
                    "Flies any way it wills by concentrating; if distracted "
                    "it loses control but stays aloft."
                ),
            ),
        ],
        appearance=(
            "A deeply tanned, bald man of nearly sixty, who smoulders, "
            "smokes and sheds ash as he grows angry and bursts into flame "
            "when ready to kill."
        ),
        notes=(
            "A Malignancy: magical wreckage from the Founder Flambeau's "
            "Twilights, built from his mistakes, base desires and failings, "
            "which truly believes it is Flambeau. Its Improved Recovery is "
            "listed as (65). It mostly takes human "
            "form, or deals through its Eidolon. It hates Moors and sahirs "
            "and attacks them on sight; bewildered by its prison, it keeps "
            "trying to get out. Loosed, it would lay the land waste in "
            "pure wrath."
        ),
        place=val_negra,
        level=fortress,
    )
    tie(adulteration, door, "the thing behind the Iron Door")

    aerie = b.creature(
        "Aerie Guard",
        page="p. 142",
        age="unknown (33)",
        encumbrance="1",
        realm="Magic",
        might=10,
        form="Mentem",
        size=0,
        how_many="the Aerie Clan; this is a soldier of the Black Guard",
        block={
            "characteristics": _chars(0, 1, 0, 0, 1, 2, 1, 1),
            "virtues_flaws": [
                "Magic Human",
                ("Affinity with {ability}", {"ability": "Single Weapon"}),
                "Custos",
                "Warrior",
                "Covenant Upbringing",
                "Dutybound",
                "Vow (Minor)",
                "Natural Appearance",
                ("Essential Virtue (Minor)", {"trait": "Unnoticeable"}),
                "Gift of Tongues",
                "Improved Powers",
                "Improved Powers",
                "Lesser Power",
                "Lesser Power",
                ("{form} Resistance", {"form": "Mentem"}),
                _minor("Arcane Lore"),
                "Second Sight",
                "Unaffected by The Gift",
                ("Restricted Power", {"power": "Silent Speech of the Aerie Clan"}),
                ("Slow Power", {"power": "Invisibility of Silent Standing"}),
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Aerie Language", 5, "gossip"),
                ("Athletics", 3, "climb"),
                ("Awareness", 2, "alert"),
                ("Brawl", 4, "grapple"),
                ("Carouse", 1, "drinking songs"),
                ("Concentration", 1, "silent speech"),
                ("Folk Ken", 1, "Aerie Clan"),
                ("Dead Language: Latin", 3, "Hermetic"),
                ("Magic Lore", 1, "effects of magic"),
                ("Mentem Resistance", 1, "Hermetic"),
                ("Organization Lore: Aerie", 1, "ancestors"),
                ("Organization Lore: Order of Hermes", 1, "House Flambeau"),
                ("Penetration", 4, "other Aerie"),
                ("Profession: Soldier", 4, "guard duty"),
                ("Second Sight", 4, "spirits"),
                ("Single Weapon", 6, "long sword"),
                ("Stealth", 3, "quiet"),
                ("Thrown Weapon", 4, "spear"),
                ("Area Lore: Val-Negra", 1, "glory days"),
            ],
            "traits": {
                "Unnoticeable (Dexterity)": 3,
                "Loyal": 2,
                "Brave": -2,
                "Inconspicuous (Presence)": -3,
            },
        },
        attacks=[b.attack("Long Sword & Round Shield", 3, 12, 11, 8)],
        soak=7,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Silent Speech of the Aerie Clan",
                0,
                1,
                "Mentem",
                rtd=("Special", "Conc", "Ind"),
                level=20,
                does=(
                    "Speaks mind to mind with any other Aerie within the "
                    "reach of its 'voice', as loud or soft as it chooses. "
                    "Restricted to the clan; between kin its Penetration is "
                    "multiplied by 6, so a typical Aerie reaches 40, enough "
                    "to speak with Romulus and Remus."
                ),
            ),
            b.power(
                "Invisibility of Silent Standing",
                0,
                0,
                "Imaginem",
                rtd=("Per", "Conc", "Ind"),
                level=5,
                does=(
                    "Standing quietly for a few moments, it fades into its "
                    "surroundings until it moves or speaks, aloud or in "
                    "silent speech; takes a round to start, then Init +0. "
                    "Elders can stay hidden longer, even moving."
                ),
            ),
        ],
        vis=[BodyVis(2, "Mentem", "in its brain")],
        equipment="Long sword, round shield, partial chain mail.",
        appearance=(
            "Drab, dull and easy to overlook; the Aerie look nearly "
            "identical, differing only by sex and age."
        ),
        notes=(
            "The template for every member of the "
            "clan: Covenant Upbringing always, an Affinity for the role's "
            "main Ability, and adjusted Characteristics and Abilities; grogs "
            "have Might 10 and companions 20 with more Qualities; children "
            "and youths have 240 fewer experience points, elders 360 more. "
            "A weaver woman, for instance, is Covenfolk with Affinity with "
            "Craft: Weaving, Gossip and Fear of the Outside World. Their "
            "leaders, the twins Romulus (Might 33) and Remus (32), add Aura "
            "of Rightful Authority (0 points, Init -2, Mentem, ReMe 20, "
            "Voice/Conc/Ind). The clan has served Val-Negra's masters for "
            "generations and now serves Abaddon."
        ),
        place=val_negra,
        level=fortress,
    )
    provence.b.link(abaddon, "creatures", aerie, "the clan that serves him")
