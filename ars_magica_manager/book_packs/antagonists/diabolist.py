"""The Infatuated Diabolist (Ant pp. 80-94): Hannelore, a baron's daughter
printed at sixteen and at twenty-one and as an Infernal ghost, with her
family, her places, and her story from a chance meeting to her last gambit,
dormant. Stat blocks are the book's; the rest is a summary, not its words.

Her maleficia follow Realms of Power: The Infernal, whose rules have no home
on the sheet here, so they are kept in her secrets, by page. They are varied
as she casts them, not fixed spells."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from ... import storage
from ...models import BodyVis, Book, Character, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    secrets,
    vf_ability,
    vf_puissant,
)

S = Builder.stage

FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
COMBAT = (
    "Combat: dagger Init +1, Attack +5, Defense +4, Damage +2. Soak -1. Fatigue "
    f"levels {FATIGUE}. Wounds -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
    "(16-20), Dead (21+)."
)
SPOILED, DIABOLIST = "Spoiled Daughter", "The Diabolist"
_CHARACTERISTICS = characteristics(0, 0, 1, 3, 0, -1, 0, 1)
_YOUNG_ABILITIES = [
    ("Artes Liberales", 2, "writing"),
    ("Awareness", 2, "mannerisms"),
    ("Brawl", 2, "dagger"),
    ("Charm", 3, "men"),
    ("Etiquette", 3, "courtly manners"),
    ("Folk Ken", 2, "men"),
    ("Guile", 3, "lying to relatives"),
    ("Dead Language: Latin", 4, "reading"),
    ("Living Language: (Native)", 5, "local dialect"),
    ("Noble Lore", 3, "positions of authority"),
    ("Philosophiae", 2, "ethics"),
    ("Ride", 2, "while hawking"),
]
_DARK_ABILITIES = [
    ("Ceremony", 3, "Diablerie"),
    ("Infernal Lore", 3, "powers"),
    ("Penetration", 3, "Malediction"),
    ("Incantation", 9, "affecting self"),
    ("Diablerie", 5, "Infernal blessings"),
    ("Malediction", 4, "Personality Flaws"),
    ("Psychomachia", 4, "lustful actions"),
]
_TRAITS = {
    "Hateful": 5,
    "Attracted to Power": 3,
    "Inquisitive": 2,
    "Sensible": -3,
}
_DIABOLIST_VIRTUES: list[str | tuple[str, dict[str, str]]] = [
    "Diabolist",
    "Gentleman/woman",
    "Ceremony (Major)",
    "Diablerie",
    "Incantation",
    "Malediction",
    "Psychomachia",
    vf_ability("Affinity with {ability}", "Incantation"),
    "Arcane Lore",
    "Educated",
    "Infernal Blessing (Minor)",
    *["Mentored by Demons"] * 5,
    vf_puissant("Incantation"),
    "Self-Confident",
    "Unaffected by The Gift",
    "Curse of Venus",
    "Hatred (Major)",
    ("Restriction", {"detail": "maleficia won't work on children"}),
    "Fragile Constitution",
    ("Obsessed (Minor)", {"detail": "knowledge is power"}),
    "Tainted With Evil",
]

_SPOILED: StatBlock = {
    "characteristics": _CHARACTERISTICS,
    "confidence": (1, 3),
    "virtues_flaws": [
        "Gentleman/woman",
        "Educated",
        "Unaffected by The Gift",
        "Curse of Venus",
        ("Obsessed (Minor)", {"detail": "knowledge is power"}),
    ],
    "traits": {k: v for k, v in _TRAITS.items() if k != "Hateful"},
    "reputations": {"Fierce Temper (Local)": 1},
    "abilities": _YOUNG_ABILITIES,
    "notes": paragraphs(
        COMBAT,
        "Equipment: fine clothes. Encumbrance 0 (0).",
        "Appearance: a girl on the edge of womanhood, very pretty, with dark "
        "wavy hair and deep green eyes. She talks about philosophy with an "
        "eagerness thought unsuited to her rank.",
        "One Flaw point more than Virtues at this age; the Protection Virtue "
        "would probably have balanced it had she not gone the way she does "
        "(p. 86).",
    ),
}

_DIABOLIST: StatBlock = {
    "characteristics": _CHARACTERISTICS,
    "aging_points": {"presence": 1, "communication": 1},
    "decrepitude": (0, 2),
    "warping": (5, 2),
    "confidence": (2, 6),
    "virtues_flaws": _DIABOLIST_VIRTUES,
    "traits": _TRAITS,
    "reputations": {"Ambitious (Infernal)": 3, "Fierce Temper (Local)": 2},
    "abilities": [*_YOUNG_ABILITIES, *_DARK_ABILITIES],
    "notes": paragraphs(
        COMBAT,
        "Equipment: fine clothes, curved dagger. Encumbrance 0 (0).",
        "Appearance: a good-looking young woman, bareheaded, her dark hair "
        "waving over green eyes. Red velvet is her choice of dress, under a "
        "fur cloak she is seldom without, for she feels the cold. Men remember "
        "her voice above all, which is full and low.",
    ),
}

_MALEFICIA = (
    "A Crown of Twelve Stars on Her Head (Psychomachia, level 40; R Voice, D "
    "Moon, T Ind; Base 15, +2 Voice, +3 Moon): the target obeys her commands "
    "for the duration, but must be able to see her, hear her voice or smell "
    "her perfume, or it ends at once. Usually laid with vis and a sacrifice on "
    "a victim she already holds.",
    "A Ghost on the Wind I Shall Become / No Door Can Stop Me (Diablerie, 45; R "
    "Per, D Sun, T Ind; Base 35, +2 Sun): the Nightwalker Major Virtue (Hedge "
    "Magic Revised Edition p. 104) until sunrise. Her spirit leaves her prone "
    "body and travels at great speed, changing between corporeal and "
    "immaterial in three rounds, and invisible at will when immaterial. "
    "Corporeal she can lift what she could normally carry, which then goes "
    "immaterial with her. People near her spirit grow drowsy, and sleepers "
    "cannot be woken. Spells on ghosts or spirits affect her, but with no "
    "Might she cannot be warded off or laid to rest. She cannot enter the "
    "Dominion so.",
    "And the Devil Shall Take Care of His Own (Diablerie, 40; R Per, D "
    "Forsaken, T Ind; base effect, +4 Forsaken): Magic Resistance 25, not "
    "stacking with other sources.",
    "Black Wings, Eye-Piercing Beak (Diablerie, 35; R Per, D Forsaken, T Ind; "
    "Base 15, +4 Forsaken): a False Power copying Skinchanger, crow shape. Her "
    "focal item is a fetish made of the wings of the bird she sacrificed.",
    "Blood and Body of the Beast (Diablerie, 35; R Touch, D Mom, T Ind; Base "
    "30, +1 Touch): a short mockery of the Eucharist turning a pawn of vis to "
    "vis prava (RoP: Infernal p. 19), worth +5 a pawn to her, not +2.",
    "Break Not, Bend Not, Burn Not / Thy Powers Desert (Diablerie, 25; R Touch, "
    "D Sun, T Ind; base effect, +1 Touch, +2 Sun): one object, not living and "
    "no larger than a base Individual of its Form, gains Magic Resistance 15, "
    "not stacking.",
    "Clothed in the Dragon's Scales (Diablerie, 50; R Per, D Moon, T Ind; Base "
    "35, +3 Moon): a False Power copying Greater Immunity, chosen for the "
    "peril, fire being the obvious one. Its level means she can really try "
    "only once, with a heavy sacrifice, much vis or a good Ceremony bonus. "
    "Could she reach level 55 she would make it Forsaken.",
    "Her Iniquities Shall Be Hidden From His Eyes (Psychomachia, 25; R Eye, D "
    "Moon, T Ind; Level 5, +1 Eye, +3 Moon): the target mistakes one thing for "
    "something else, a man for a serving maid, a malefic casting for a country "
    "dance.",
    "Mother Lilith, Queen of Desire / Stroke his Staff, Stoke the Fire "
    "(Psychomachia, 25; R Eye, D Sun, T Ind; Base 10, +1 Eye, +2 Sun): burning "
    "lust. She cannot direct the victim but can work him like an addict. "
    "Usually follows her power to hold him still.",
    "Pact of the Chalice of Blood (Diablerie, 25; R Voice, D Moon, T Ind; Base "
    "4, +2 Voice, +3 Moon): solemnizes an uncoerced pact with an intelligent "
    "creature of Infernal Might, both drinking a sacrifice's blood; it must "
    "keep the terms to the letter. Such as a Fimus (RoP: Infernal p. 68), a "
    "Fictilis (p. 69) or Morrighu (pp. 72-73) are within her power.",
    "She Who Bears the Mark Shall Be Unharmed (Diablerie, 35; R Per, D "
    "Forsaken, T Ind; Base 15, +4 Forsaken): a False Power copying Lesser "
    "Immunity, perhaps several times over, to long swords or another weapon, "
    "or to magical fire or the like. Each costs resources and Warping, so she "
    "may leave a gap; she has likely not guarded against her love's favourite "
    "magic, thinking he would never attack her.",
    "The Scorched Heart of a Man Obsessed (Malediction, 35; R Eye, D Moon, T "
    "Ind; Base 15, +1 Eye, +3 Moon): the Obsessed Flaw, fixed on her. Near her "
    "he can only attend on her; away, she fills his thoughts. Often laid once "
    "she has already bewitched him.",
    "The Wrath of Woman Scorches the Valor of Man (Malediction, 35; R Voice, D "
    "Sun, T Ind; Base 15, +2 Voice, +2 Sun): overwhelming Fear of women, as "
    "the Flaw.",
    "Thy Health Shall Shrivel Like Straw in a Flame (Malediction, 30; R Eye, D "
    "Sun, T Ind; Level 5, +1 Eye, +2 Sun, +1 extra point, +1 to lower the "
    "minimum): Stamina down 2, to no less than -1, with sudden pain and a "
    "hacking cough, trembling heart or other small ailment for the duration.",
    "Trampled Under Death's Pale Hooves (Malediction, 30; R Eye, D Sun, T Ind; "
    "base effect, +1 Eye, +2 Sun): -6 to all Ride rolls and 6 extra botch dice "
    "on a 0. This and its like for other Abilities are how she disposes of "
    "unwanted suitors.",
)


def _hannelore(b: Builder) -> Character:
    hannelore = b.magus(
        "Hannelore",
        covenant=None,
        house="",
        age=21,
        type="companion",
        summary=paragraphs(
            "The favoured daughter of Baron Hugo, raised in comfort by a "
            "doting father and taught by private tutors, who noticed her "
            "temper and ambition and prayed for whoever marries her. She is "
            "educated, eloquent and sure of herself, and the Gift does not "
            "trouble her. She loves hawking and courtly romances.",
            "She has never married. Those proposed for her fall ill, meet "
            "with accidents or disappear, and people find they cannot bear to "
            "stay long in her company.",
        ),
        secrets=paragraphs(
            "Attracted to power, she reads the jealousy the Gift stirs as "
            "power's natural effect, and fixes on a magus who seems strong "
            "(p. 85). She is infatuated with him and his power; he may love "
            "her, she does not love him. Her target is best not repulsive, and "
            "need not be a man. Variants: avarice (she wants to be taught, "
            "impossible without the Gift) or envy (she wants his magic from "
            "him); a male Hannelore; a same-sex pursuit, kept secret, where "
            "Hugo might seek no clemency; a companion or storyguide character "
            "as target, whom she can enslave and later curse at Arcane Range "
            "from connections taken while she held him, watching in crow form "
            "if he dwells within an Aegis; a weaker version, with a Power or "
            "her vis taken away, keeping Diablerie; a stronger one, with a "
            "coven, demons and corrupted beasts in pact, or more Powers; a "
            "one-time threat with no prior romance, going straight to her "
            "death and return (pp. 80, 84-85).",
            "From a block of forbidden books she initiated herself into the "
            "Unholy Method of Incantation, at the cost of a Warping point. "
            "The rite drew a powerful demon in a pleasing form, who taught her "
            "for five years, feeding her instability with its Obsession power. "
            "She knows her power is illicit but does not at first know it is "
            "Infernal, or that her beloved's is not (p. 87). She has more "
            "Virtues than creation allows: demonic tutelage equal to Mentored "
            "by Demons five times (RoP: Infernal p. 86), 50 extra experience "
            "a year, and Vituperations that gave her Self-Confident and Aging "
            "Points. Such an outlay suggests Hell plans more for her, and that "
            "the infatuation is a distraction (p. 81).",
            "Hierarchy Score 3. Fragile Constitution, Infernal Blessing and "
            "Tainted With Evil come from Warping, and Arcane Lore free with "
            "Diabolist. Her Warping is so high because she takes Warping to "
            "fuel her magic (RoP: Infernal p. 104) and carries lasting "
            "effects. Unaffected by The Gift: RoP: Magic p. 47 (p. 81).",
            "Powers from her Infernal Blessing, a Level 25 Debauchery / "
            "Phantasm effect (Base 4, +1 Touch, +4 Forsaken) (p. 81). Gaze of "
            "the Wolf: with eye contact she fixes a person in place while she "
            "holds the stare; Penetration 5 + Penetration Bonus + Aura "
            "Modifier. The text calls this her Transfix power (pp. 83, 88). "
            "Exhaustion: her touch inflicts a Long-Term Fatigue level; not in "
            "the Dominion or on women; Penetration as above.",
            "Her vis (p. 81): at least 3 + simple die pawns at any time, some "
            "turned to vis prava. Not Personal Vis Sources, as it is never "
            "automatic. She steals the Host at Communion and profanes it (RoP: "
            "Infernal p. 96); has replaced the relic in her father's chapel "
            "with a fake and profaned the true one; contests the spring's "
            "vis; and has the beads on one book of her father's.",
            "Casting (p. 82): Communication + Incantation + Power + Aura "
            "modifier + stress die. Her Hierarchy spares her the harsh effects "
            "of a failed maleficium of level 30 or below. Each use costs a "
            "Confidence point, adding nothing, or a Warping point. Range "
            "Personal, Duration Forsaken maleficia are taken as already cast "
            "(And the Devil, Black Wings, She Who Bears the Mark); each gives a "
            "Warping point a year, not included in her score. Bonuses: +5 a "
            "pawn of vis prava or +2 of other vis (at most Incantation + Power "
            "pawns); +3 a Confidence point (at most 2); +6 for sacrificing a "
            "black animal; +5 an assistant at Communication +1 and Incantation "
            "4 (at most 3 with Diablerie, 2 otherwise). With Diablerie, her "
            "best Power, around 53 + stress die with Infernal aura 2, 2 "
            "Confidence, 4 pawns of vis prava and a black goat; +15 with a "
            "coven of 3. See RoP: Infernal chapter 10.",
            "Her maleficia (pp. 82-83) are not formulaic, and she may vary "
            "Range, Duration, Target or effect:\n" + "\n".join(_MALEFICIA),
            "Tactics (pp. 88-90): a maleficium is very obvious, all chanted "
            "blasphemies, so she uses Gaze of the Wolf first unless she has "
            "surprise. She times incantations for sunrise or sunset, when "
            "the Parma Magica lapses. She is no match for a group of magi, with "
            "low Penetration against those she has no interest in, but curses "
            "companions and grogs with Minor Flaws such as Noncombatant, "
            "Palsied Hands or Fear, or blights an Ability or Characteristic, "
            "all deliverable at Duration Diameter. She fights hit and run from "
            "spirit form, leaves in crow shape, and may bring minor demons "
            "under a pact, or a former suitor ensorceled with A Crown of "
            "Twelve Stars. His name, and any letters in his own hand, are "
            "sympathetic connections she holds to her love.",
            "Redemption (p. 89): she is not beyond it. A patient character, "
            "perhaps with the baron, may bring her to see the source of her "
            "power and give it up. Abandoned after a true wish to repent, she "
            "relapses and seeks revenge. Her wish will be tested by God and "
            "fought by her patron; penance means a nunnery.",
        ),
    )
    blank = deepcopy(hannelore)
    b.variants[hannelore.id] = [
        {
            "label": label,
            "age": age,
            "character": asdict(b.stats(deepcopy(blank), block)),
        }
        for label, age, block in (
            (SPOILED, 16, _SPOILED),
            (DIABOLIST, 21, _DIABOLIST),
        )
    ]
    b.stats(hannelore, _DIABOLIST, source="Ant")
    return hannelore


def _ghost(b: Builder, hannelore: Character) -> None:
    ghost = b.creature(
        "Hannelore, Vengeful Ghost",
        page="p. 94",
        realm="Infernal",
        might=20,
        form="Mentem",
        order="Accusers",
        size=0,
        confidence=(2, 6),
        block={
            "characteristics": _CHARACTERISTICS,
            "virtues_flaws": _DIABOLIST_VIRTUES,
            "traits": _TRAITS,
            "reputations": {"Ambitious (Infernal)": 3},
            "abilities": [*_YOUNG_ABILITIES, *_DARK_ABILITIES],
        },
        attacks=[b.attack("Dagger", 1, 5, 4, 2)],
        soak=-1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Betrayal of the Heart",
                2,
                0,
                "Mentem",
                does="Each use shows her one fact about the target that he "
                "would never admit, drawn from his secret fears and sins. The "
                "truly holy may be immune, having no secrets however small.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="For 1 point she enters a sleeper's dreams; she cannot "
                "change them at a stroke but can slowly darken them and speak "
                "through any figure in them. For 5 points she forces a waking "
                "vision of whatever she likes, which may stun for a round, and "
                "the victim needs a Brave roll of 9+ to avoid retching, "
                "convulsions or terror. It is her only way of speaking to "
                "humans.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="1 to 3 points. When a mortal indulges a venial sin she "
                "may impose her Obsession Traits, Infatuation or Revenge; if "
                "it penetrates, sinful thoughts assail him and he gains the "
                "Trait at the points spent, which may stick if he indulges "
                "again at his next chance. RoP: Infernal pp. 31-32.",
            ),
            b.power(
                "Possession",
                0,
                2,
                "Mentem",
                does="Variable points. Any Might she spends becomes a "
                "Possession Might Pool inside the victim, not regained until "
                "the possession ends; more does more with the host but "
                "penetrates less. If it overcomes resistance she controls him "
                "directly. RoP: Infernal p. 32.",
            ),
            b.power(
                "Whispers Behind the Back",
                2,
                0,
                "Mentem",
                does="Exactly as the spell Pains of the Perpetual Worry: a "
                "month's nagging dread, tied to the victim's secret sins, "
                "that everyone knows and talks behind his back.",
            ),
        ],
        vis=[BodyVis(4, "", "vis prava, but insubstantial")],
        appearance=(
            "As in life, but her face is pinched into a caricature of itself "
            "and her skin scarlet as if boiled. Small horns show in her tousled "
            "hair, and her faded fine clothes stream behind her as if blown by "
            "a furnace wind."
        ),
        notes=paragraphs(
            "Virtues, Flaws and Abilities as in life; her diabolist block is "
            "entered. Wounds -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20), Dead (21+). The book gives no Hierarchy Score here.",
            "Incorporeal in her natural form, with no power to form a solid "
            "body, so only a spirit can fight her physically.",
            "The storyguide may raise her Might: her Infernal Reputation could "
            "make her a Master or Lord, +5 or +10. Whether she keeps her "
            "maleficia as a demon is left open.",
        ),
        secrets=(
            "Hell lets her back, with her punishment eased a little for each "
            "soul won. She has a year from the anniversary of her death to win "
            "one, tempting it to mortal sin and seeing it die unrepentant; each "
            "success gives another year. Possessed humans pass an Aegis unless "
            "the demon extends its Magic Resistance over the host (RoP: "
            "Infernal p. 32), but if the Aegis's Penetration beats her Infernal "
            "Might all powers cost double. She flees superior force. If she "
            "sees her beloved she cannot help dropping her plans to kill him "
            "(p. 94)."
        ),
    )
    b.link(ghost, "characters", hannelore, "Hannelore after her death")


def _family(
    b: Builder, hannelore: Character
) -> tuple[Neighbour, Character, Character, Neighbour, Neighbour, Neighbour]:
    castle = b.place(
        "Baron Hugo's Castle",
        realm="Divine",
        aura=1,
        summary=(
            "The seat of Baron Hugo, a nobleman of middling importance with "
            "authority in the area."
        ),
        secrets=(
            "Hannelore's work has spread an Infernal aura over the baron's "
            "lands and worn the castle's Dominion aura down to 1, so it fades "
            "entirely after dark (p. 88). The book names no strength for the "
            "Infernal aura here."
        ),
    )
    hugo = b.lord(
        "Baron Hugo",
        title="baron",
        seat="Baron Hugo's Castle",
        place=castle,
        summary=paragraphs(
            "A local nobleman of middling rank, whom the covenant will want to "
            "keep on good terms with. He loves his daughter Hannelore dearly, "
            "means to marry her to a wholesome and useful groom, and is "
            "disappointed that every match has failed. Little happens on his "
            "lands that he does not hear of.",
        ),
        secrets=paragraphs(
            "He need not be a baron or landed: a knight or sheriff does as "
            "well, or an older brother or uncle who is her guardian. Whoever "
            "he is, he has a secret past (pp. 84, 86).",
            "He owns books of Infernal Lore. Why is the storyguide's choice "
            "(p. 87): he was a sorcerer in youth who broke his staff and has "
            "lived blamelessly since, kept safe by a Faith point from a "
            "pilgrimage; or he belongs to a secret society within the Church "
            "against evil, run through an order such as the Templars, and "
            "keeps them as spoils to study the Enemy; or they are his wife's "
            "(see Lady Ermengarde); or an ancestor left them, he can barely "
            "read, and Hell has seen they stay with those who will use them.",
            "As the story runs (pp. 88-89): depending on these he is ignorant "
            "or blinded by love, a pawn she forces, or a demon-hunter calling "
            "the magi in. Asked for help with proof and respect he is saddened "
            "but can believe it, given what he has seen. His price is her life "
            "spared, and he comes along to see to it. He supplies four soldiers "
            "(Standard Soldier, ArM5 p. 22) under a serjeant (Grizzled Veteran, "
            "ArM5 p. 21), perhaps a knight in residence, more in a day, and "
            "knowledge of the manor. He has probably the right of judge, jury "
            "and executioner over intruders.",
        ),
    )
    ermengarde = b.magus(
        "Lady Ermengarde",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="The wife of Baron Hugo and Hannelore's stepmother.",
        secrets=(
            "She may be a sorceress herself, the true owner of the books, "
            "using Hannelore as a cat's-paw to hide her own evil and having "
            "corrupted her (p. 87). As a ghost Hannelore possesses her, stirs "
            "her and Hugo with Infatuation, fakes or uncovers an infidelity, "
            "and drives her with Revenge to kill him; she dies under arrest, "
            "her soul forsaken (p. 93)."
        ),
    )
    b.link(hannelore, "characters", ermengarde, "Her stepmother")
    fulke = b.magus(
        "Father Fulke",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="The priest assigned to the pastoral care of the nuns.",
        secrets=(
            "No priest at all, but an infernalist posing as one, sworn to the "
            "demon who trained Hannelore and told to help her. If she is to "
            "escape quickly he corrupted the nunnery before she came, drawing "
            "younger nuns into rebellion and licence by personal influence "
            "(RoP: Infernal pp. 22-23) (p. 91)."
        ),
    )
    caves = b.place(
        "The Baron's Old Storage Caves",
        realm="",
        summary=(
            "A run of caves once used by the baron's household to keep "
            "perishable food, since abandoned. They were enlarged long ago, "
            "dressed with stone, and go deep into the bedrock for the cool."
        ),
        secrets=(
            "Hannelore's hiding place. One cave is her ritual chamber, which "
            "holds the Infernal aura of 3; the aura is that cave's (p. 89)."
        ),
    )
    spring = b.place(
        "The Sulfurous Spring",
        realm="",
        summary="A spring on the baron's estate that smells of sulfur.",
        secrets=(
            "Once a year on Lammas Eve it belches forth vis, which the local "
            "witch coven has collected since time immemorial and Hannelore "
            "contests (p. 81)."
        ),
    )
    coven = b.faction(
        "The Local Witch Coven",
        faction="Hedge coven",
        realm="Infernal",
        place=spring,
        summary="A coven of witches said to meet about the baron's estate.",
        secrets=(
            "It has taken the sulfurous spring's Lammas Eve vis since time "
            "immemorial (p. 81). A stronger Hannelore takes over a coven of "
            "infernalists early on, for a Ceremony bonus (p. 84); younger "
            "siblings she corrupts could form hers instead (p. 86). The book "
            "gives no members."
        ),
    )
    b.link(hannelore, "places", caves, "Where she hides")
    b.link(hugo, "characters", hannelore, "His daughter")
    b.link(hugo, "characters", ermengarde, "His wife")
    return castle, ermengarde, fulke, caves, spring, coven


def _books(b: Builder, hannelore: Character) -> None:
    book = Book(
        id=storage.generate_unique_id(
            "Baron Hugo's Forbidden Books", [x.id for x in b.saga.books]
        ),
        name="Baron Hugo's Forbidden Books",
        type="Other",
        language="",
        owner_kind="character",
        owner_id=hannelore.id,
        description=secrets(
            "A set of books the baron keeps locked in a chest in his chamber "
            "and has forbidden his daughter to read.",
            "A corpus of diabolic lore, Infernal Lore at the least; the library "
            "may also hold tomes on the maleficia, the Goetic Arts, hedge "
            "wizardry or even Hermetic magic. No Level or Quality is printed. "
            "They are entered under Hannelore, who reads them in secret, "
            "because a baron cannot own a book here. One has glass beads on its "
            "cover, each holding a pawn of vis (pp. 81, 87).",
        ),
    )
    b.saga.books.append(book)


def _nunnery(b: Builder, fulke: Character) -> Neighbour:
    nunnery = b.church(
        "The Nunnery",
        church="Monastery or nunnery",
        summary=("An ordinary religious house with a solid foundation and high walls."),
        secrets=paragraphs(
            "The book gives it no name. Establish it early in the saga, perhaps "
            "by having the characters guide lost novices there, so it seems an "
            "ordinary house (p. 91).",
            "Hannelore is walled in here as an anchorite, fed through a hole. "
            "For an immediate escape it was corrupted before she came, by "
            "Father Fulke, and Hugo was steered to it by the demon; for a slow "
            "one it is in a state of grace and she brings it down (p. 91).",
            "Most of it stays in the Dominion, but its aura weakens, an "
            "Infernal aura rises at night, and her cell's Dominion erodes "
            "until it no longer hinders her. Within months a few nuns make her "
            "comfortable; within a year she has grimoires and smuggled vis "
            "(pp. 91, 92).",
            "Corrupted nuns are Initiated into her patron's Favored Abilities: "
            "Ceremony, Diablerie, Incantation, Malediction, Psychomachia. Each "
            "adds Presence + Incantation as a ceremonial bonus, and she leads "
            "one nun per point of Ceremony (RoP: Infernal p. 91); or in a "
            "leaderless ceremony 12 nuns and she add the sum of their Ceremony "
            "scores, less 13, on top (p. 91).",
            "After she flies, her nuns cover for her and the prioress, ashamed, "
            "tells no one unless the magi stressed the danger. Her cell holds "
            "books on the maleficia and vis infesta, a crust of profaned Host "
            "that looks like Corpus vis to Hermetic magic; she took her vis "
            "prava (p. 91).",
            "An attack on the nunnery must be utterly secret. Her patron warns "
            "the authorities, the walls keep people out and the Dominion "
            "hampers spells. If pressed she may burn it (p. 92).",
        ),
    )
    b.link(fulke, "places", nunnery, "Priest to the nuns")
    b.faction(
        "The Younger Nuns",
        faction="Religious community",
        place=nunnery,
        summary="A group of the younger nuns, lately rebellious and licentious.",
        secrets=(
            "Hannelore's servants within the nunnery, won by her or by Father "
            "Fulke. Neither can corrupt the whole house, but their licence "
            "weakens its Dominion (p. 91)."
        ),
    )
    return nunnery


def _patron(b: Builder) -> None:
    b.creature(
        "Hannelore's Demonic Patron",
        page="p. 87",
        realm="Infernal",
        notes=(
            "The book deliberately gives no statistics, so no Might or Order "
            "is entered. A Watcher (Realms of Power: The Infernal p. 64) suits "
            "it well."
        ),
        secrets=paragraphs(
            "It stays in the background, using Hannelore on Earth. Watchers "
            "specialize in teaching corrupt magic and are among the most "
            "powerful demons outside Hell, patient beyond most of their kind "
            "for a time. It came to her in a form pleasing to the eye and "
            "fed her instability with its Obsession power. It wants as many "
            "corrupted as possible. She is not its only project, and it may "
            "send other cultists if she falters (p. 87).",
            "It expects her beloved to spurn her and hopes she destroys him "
            "in her rage; if not, it has her soul anyway (p. 88). It cannot "
            "visit her in the nunnery (p. 91).",
        ),
    )


def _story(
    b: Builder,
    hannelore: Character,
    records: tuple[Neighbour, Character, Character, Neighbour, Neighbour, Neighbour],
    nunnery: Neighbour,
) -> None:
    castle, ermengarde, fulke, caves, spring, coven = records
    tavern = b.place(
        "The Road Tavern",
        realm="",
        summary=(
            "A tavern outside any town, by a busy road between two major "
            "towns, serving travellers. It is famed for its ale and a favourite "
            "of redcaps."
        ),
        secrets=(
            "Where Hannelore burns her enemies. The book gives it no name (p. 92)."
        ),
    )
    links: list[tuple[str, Any, str]] = [
        ("characters", hannelore, "The diabolist"),
        ("characters", ermengarde, "Hannelore's stepmother"),
        ("characters", fulke, "The false priest"),
        ("places", castle, "The invitation"),
        ("places", caves, "The confrontation"),
        ("places", spring, "Vis she contests with the coven"),
        ("places", tavern, "The showdown"),
    ]
    threat = dormant(
        b.threat(
            "The Infatuated Diabolist",
            antagonist="Hannelore, daughter of Baron Hugo",
            summary=(
                "Baron Hugo's clever, wilful daughter has taken a liking to a "
                "magus of the covenant, and her father would not approve."
            ),
            secrets=paragraphs(
                "Five years turn a spoiled girl into a powerful diabolist, "
                "still infatuated with a player character, and if she cannot "
                "have him no one shall. It shows both the perils of diabolists "
                "and their weakness: great strength given preparation, but "
                "none of a magus's ready firepower. Have Realms of Power: The "
                "Infernal to hand (pp. 7, 80).",
                "Other kin (p. 86): brothers may avenge her honour; older "
                "sisters let Hugo indulge her refusing to marry; siblings, "
                "younger sisters above all, may form her coven.",
                "A child (p. 90): if she consummates her lust with her beloved "
                "she may conceive, if he has no Longevity Ritual yet, or even "
                "if he is sterile with the help of an Infernal witch or demon "
                "(the Consumption Power). She may bear it hidden in the nunnery, "
                "for him to find after she escapes, or a child already born may "
                "move him to clemency. If it has the Gift it could be his "
                "apprentice; if Infernal powers helped, is it tainted?",
                "The burning tavern (pp. 92-93). Smoke: Deprivation rolls "
                "(ArM5 p. 180) every 5 rounds, then every round; a wet cloth "
                "gives +3. Heat: a Short-Term Fatigue roll (ArM5 p. 178) each "
                "active round, -3 in mostly metal armour. Flames: +5 damage a "
                "round; metal armour stops protecting after 5 rounds; heroics "
                "may double to quadruple the base (ArM5 p. 181). After 10 "
                "rounds it is +10 and the roof may fall: each round a simple "
                "die at or under the rounds since it reached +10 brings +15 "
                "damage on everyone. Some two dozen panicking people are "
                "inside; Communication + Leadership, Ease Factor 12, gives "
                "some influence. Examples: a merchant offering silver to save "
                "his wares upstairs, a mother whose children are upstairs, "
                "lovers under a burning table, a local hero flinging ale at "
                "the fire.",
                "The doors: Strength against Ease Factor 12. A charge costs a "
                "Short-Term Fatigue level and adds Athletics. Up to four may "
                "combine Strength to force, not to charge. A bench as a ram "
                "adds +3. An axe lies by the back door: each round a stress "
                "die +3 against Ease Factor 15, and failure, as printed, takes "
                "one of the door's 2 damage levels.",
                "Timeline (p. 93). Round 1: Perception + Awareness, Ease Factor "
                "12, to smell smoke, +3 by day with the cooking fire, +9 if "
                "asleep; all make a smoke Deprivation roll. Round 3: Ease "
                "Factor 6. Round 5: unmissable, Deprivation and Fatigue rolls "
                "every round. Round 10: fires everywhere, +5 a round. Round 15: "
                "+10 a round, door Ease Factor down 3, collapse possible.",
            ),
            stages=[
                S(
                    "A chance encounter",
                    at=1,
                    clues=(
                        "The characters meet Baron Hugo and his daughter of "
                        "sixteen at a social occasion, perhaps part of another "
                        "story: an ally's wedding, where the bride's family "
                        "seems uncanny; a hunting party with a lunch and a tale "
                        "of a fantastic beast; a feast for those who saved an "
                        "important local. She fixes on a powerful male magus "
                        "and invites him to try her new hawk, chaperoned."
                    ),
                    ignored="She pursues him anyway, sure she can win him.",
                ),
                S(
                    "The affair",
                    at=2,
                    clues=(
                        "A love affair must stay secret: Hugo would never "
                        "approve, and the covenant may fear a noble's wrath "
                        "breaking the Oath. A lukewarm magus may be pushed by a "
                        "faerie who kidnaps her and sends him a ransom demand, "
                        "as a monster would in a story."
                    ),
                    ignored=(
                        "She expects wooing he has no time for. Refused, she "
                        "pesters, then turns petulant with blackmail or a "
                        "noble's son defending her honour, small and easily "
                        "handled, and seems to accept it. Outright rejection "
                        "ends as badly. Hugo, hearing of it, breaks them up. "
                        "Public scandal would sour the covenant's standing."
                    ),
                ),
                S(
                    "Obsession and corruption",
                    at=3,
                    clues=(
                        "Rejected, she blames her lack of power; loved, she "
                        "resents his absences and wants to share his work. She "
                        "turns to her father's books. Over five years suitors "
                        "sicken, have accidents, vanish or are found dead behind "
                        "barred doors, and nobody can stand her company for "
                        "long, not even Hugo."
                    ),
                    ignored="She waits until she thinks herself worthy of him.",
                ),
                S(
                    "Hannelore woos her love",
                    at=4,
                    clues=(
                        "An invitation comes from Hugo, willing or forced, or a "
                        "plea about demons, or her faked disappearance. At "
                        "dinner she is calm. At night, once the Dominion fades, "
                        "she comes to him in spirit, pours out her heart, then "
                        "fades, leaving a foul sulfurous slime, and returns "
                        "laughing. Intellego Vim shows Infernally tainted magic."
                    ),
                    ignored=(
                        "He recoils: she screams and flees, seeking an Arcane "
                        "Connection, then returns by surprise to bind him with "
                        "Mother Lilith and The Scorched Heart, drains his "
                        "Fatigue, and hides him from her father as a female "
                        "companion. He may be her slave until his sodales come "
                        "looking."
                    ),
                    turned=(
                        "He plays along: she happily tells of the suitors she "
                        "murdered and her dreams of killing her father. Social "
                        "rolls of Ease Factor 6 or more keep her trusting, but "
                        "every meeting risks a new Arcane Connection."
                    ),
                ),
                S(
                    "Confronting Hannelore",
                    at=5,
                    clues=(
                        "The characters need the baron, who knows his lands and "
                        "staff, to find her in the old caves. Without him he "
                        "confronts them with armed men."
                    ),
                    stopped=(
                        "They can outmatch her, but if he is not with them he "
                        "arrives in time to stand between them and beg for her "
                        "life; she may rush to his side and plead. If she dies "
                        "here, skip to her final gambit."
                    ),
                    turned=(
                        "He offers the nunnery, where as an anchorite she could "
                        "do little harm and might repent. His goodwill may make "
                        "the magi agree."
                    ),
                ),
                S(
                    "Confinement and escape",
                    at=6,
                    clues=(
                        "Quick release keeps the tension; years away make an old "
                        "enemy's return, and she may have gained experience, "
                        "slower than before, with vis and profane reading. When "
                        "she has nothing more to gain she flies out as a crow."
                    ),
                    stopped=(
                        "Magi who go after her there, or strike by Arcane "
                        "Connection, deserve reward. It robs the story of a "
                        "showdown, so make her return as a ghost the more "
                        "dramatic."
                    ),
                ),
                S(
                    "The showdown",
                    at=7,
                    clues=(
                        "Each of her foes, and Hugo, gets a message seeming to "
                        "come from an ally, naming a tavern."
                    ),
                    ignored=(
                        "With all inside she bars the doors. An aethnicus "
                        "(RoP: Infernal p. 67), bound by pact, lights the fire, "
                        "and she follows it warding roof, doors and walls with "
                        "Break Not, Bend Not. Clothed in the Dragon's Scales, "
                        "she dances in the flames with a knife for any who get "
                        "out, perhaps with demonic allies."
                    ),
                    stopped=(
                        "Even Hugo now sees she must die. She may flee as a crow "
                        "and be shot down, or call her father or love close to "
                        "hear her confession and spit one last curse, offering "
                        "herself as the sacrifice. Saving Hugo cements an "
                        "alliance."
                    ),
                ),
                S(
                    "Hannelore's final gambit",
                    at=8,
                    clues=(
                        "A year after her death a run of killings begins in her "
                        "family, then among the baron's knights: wives slay "
                        "husbands over infidelities and die soon after, or kill "
                        "themselves. The deaths cluster around the anniversary. "
                        "A character keeping up with the family or the local "
                        "nobles may notice."
                    ),
                    ignored=(
                        "She moves on to grogs and companions who helped her "
                        "beloved. Thwarted and short of time, she goes straight "
                        "for him, through possessed women if she must, wanting "
                        "him to sin and die knowing who did it."
                    ),
                    stopped=(
                        "A showdown on the anniversary, and angels of punishment "
                        "drag her soul back to Hell in flame and smoke."
                    ),
                ),
            ],
        )
    )
    for kind, target, note in links:
        b.link(threat, kind, target, note)
    b.link(threat, "places", nunnery, "Her confinement")
    b.link(coven, "places", spring, "Its vis")


def build(b: Builder) -> None:
    hannelore = _hannelore(b)
    _ghost(b, hannelore)
    family = _family(b, hannelore)
    _books(b, hannelore)
    nunnery = _nunnery(b, family[2])
    _patron(b)
    _story(b, hannelore, family, nunnery)
