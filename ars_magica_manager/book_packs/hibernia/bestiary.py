"""The Bestiary: every creature The Contested Isle gives a stat block,
from chapter 10's beasts of virtue (the true mare and the king otter)
and chapter 11's faeries (Donn the death god, a trooping faerie, Caílte
mac Rónáin and the Head of Arastotail) to chapter 13's demons (the
Harvest Thief, the Sluagh and Temoneth), with Bóinn the river goddess
from chapter 6, and chapter 12's twelve Irish saints as Divine entries
with their Might and powers.

The beings the book names without stats (Balor, Mug Ruith, the Eagle
King, the Cailleach of Hag's Head, Áillen mac Midgna and the rest) are
a sentence at their places, written by the parts that make those
places; the druid Umor Ard, given a Might but no stat block, is the
Pact of Oireadh's.

Numbers are the book's; what powers do, how a creature looks and the
notes are a summary in the pack's own words. The page reference is the
chapter, since the Open Content text has no page numbers. Each creature
is set at its place in `finish`, once every province has built its
places: the nearest place a part made, or else the province itself."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models import BodyVis
from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Creature, CreaturePower, Neighbour
    from ..builder import Builder
    from . import Hibernia

#: A person's Fatigue levels, as the book's demon blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"

#: Where each creature lives: the place keys a province part may have
#: made (most likely first), words a place's name may hold, and the
#: province (or "ireland") to fall back on.
HOMES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "fiorlair": (
        ("kings_stables", "emhain_mhacha", "navan"),
        ("King's Stables", "Emhain Mhacha"),
        "ulster",
    ),
    "dobhar_chu": ((), (), "ireland"),
    "boinn": (
        ("well_of_wisdom", "carbury", "sidh_neachtain", "boyne"),
        ("Well of Wisdom", "Neachtain", "Carbury", "Boyne"),
        "leinster",
    ),
    "donn": (
        ("teach_duinn", "tech_duinn", "house_of_donn"),
        ("Teach Duínn", "Tech Duínn", "Teach Duinn", "House of Donn"),
        "munster",
    ),
    "trooping_faerie": (
        ("newgrange", "new_grange", "brugh_na_boinne"),
        ("Newgrange", "New Grange"),
        "meath",
    ),
    "cailte": ((), (), "munster"),
    "arastotail": ((), (), "ireland"),
    "harvest_thief": ((), (), "ireland"),
    "sluagh": ((), (), "ireland"),
    "temoneth": ((), (), "ireland"),
    "patrick": ((), (), "ireland"),
    "brigid": (("kildare",), ("Kildare",), "leinster"),
    "columba": (("derry",), ("Derry", "Doire"), "ulster"),
    "abban": (("ferns",), ("Ferns",), "leinster"),
    "kevin": (("glendalough",), ("Glendalough",), "leinster"),
    "ciaran": (("clonmacnoise",), ("Clonmacnoise",), "meath"),
    "malachy": (("armagh_town", "armagh_city"), ("Armagh",), "ulster"),
    "dympna": (("tydavnet",), ("Tydavnet", "Tydavenet"), "ulster"),
    "brendan": (("clonfert",), ("Clonfert",), "connacht"),
    "grellan": (
        ("ballinasloe", "magh_liach"),
        ("Ballinasloe", "Magh Liach"),
        "connacht",
    ),
    "senan": (("scattery", "inis_cathaigh"), ("Scattery", "Inis Cathaigh"), "munster"),
    "cronan": (("roscrea",), ("Roscrea",), "munster"),
}

#: The note on each place's link to its creature.
_ROLE = {
    "fiorlair": "true mares, born now and then of the old royal horses",
    "dobhar_chu": "the king otter of the loughs",
    "boinn": "the white cow goddess of the Boyne",
    "donn": "the death god, whose isle gathers the dead",
    "trooping_faerie": "a gang of trooping faeries",
    "cailte": "the faerie poet who walks Munster with his band",
    "arastotail": "the severed head of the magician Arastotail",
    "harvest_thief": "the tiny demons that spoil the crops",
    "sluagh": "the spirits that carry off the dying",
    "temoneth": "the Fury of lust and betrayal",
    "patrick": "the patron saint of Ireland",
    "brigid": "Saint Brigid, a patron of Ireland",
    "columba": "Saint Columba, a patron of Ireland",
    "abban": "Saint Abbán, venerated in Wexford and Ferns",
    "kevin": "Saint Kevin, who founded Glendalough",
    "ciaran": "Saint Ciarán, who founded Clonmacnoise",
    "malachy": "Saint Malachy, once Archbishop of Armagh",
    "dympna": "Saint Dympna, whose staff is kept at Tydavnet",
    "brendan": "Saint Brendan the Navigator, whose relics lie at Clonfert",
    "grellan": "Saint Grellan, guardian against the Fir Bolg",
    "senan": "Saint Senan of Scattery Island",
    "cronan": "Saint Cronan of Roscrea",
}

#: The creatures this part makes, by slug, for `finish`.
_MADE: dict[str, Creature] = {}

#: A name the catalog has twice (a Magic Quality and a faerie's or a
#: person's Virtue) resolves to the Magic Quality; a faerie or a demon
#: takes the other.
_NOT_MAGIC = {
    "vf_greater_power_quality": "vf_greater_power",
    "vf_lesser_power_quality": "vf_lesser_power",
    "vf_personal_power_quality": "vf_personal_power",
    "vf_focus_power_quality": "vf_focus_power",
    "vf_reduced_damage_inferiority": "vf_reduced_damage",
    "vf_sharp_ears_quality": "vf_sharp_ears",
}


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


def _wounds(size: int) -> str:
    """The wound ranges for a Size, as the book's blocks print them."""
    step = 5 + size
    return (
        f"Wound ranges: Light 1-{step}, Medium to {2 * step}, Heavy to "
        f"{3 * step}, Incapacitated to {4 * step}, Dead from {4 * step + 1}."
    )


def _ward(ward: str) -> tuple[str, dict[str, str]]:
    return ("Traditional Ward", {"ward": ward})


def _salt() -> tuple[str, dict[str, str]]:
    return ("Vulnerable to {substance} (Minor)", {"substance": "salt water"})


def _not_magic(creature: Creature) -> Creature:
    """Give a faerie or a demon the Virtues of its own realm where the
    catalog's name is shared with a Magic Quality."""
    for vf in creature.virtues_flaws:
        vf.vf_id = _NOT_MAGIC.get(vf.vf_id, vf.vf_id)
    return creature


def build(hibernia: Hibernia) -> None:
    _MADE.clear()
    _beasts(hibernia)
    _faeries(hibernia)
    _demons(hibernia)
    _saints(hibernia)


# -- chapter 10: the beasts of virtue --


def _beasts(hibernia: Hibernia) -> None:
    b = hibernia.b
    _MADE["fiorlair"] = b.creature(
        "Fíorláir, the True Mare",
        page="ch. 10",
        realm="Magic",
        might=16,
        form="Animal",
        size=2,
        season="Spring",
        cunning=True,
        confidence=(1, 3),
        how_many="a rare kind; each is a mare's seventh filly in a row",
        block={
            "characteristics": _chars(-2, 0, 0, -4, 4, 2, -2, 3),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Friend",
                ("Ferocity", {"audience": "when racing"}),
                "Improved Characteristics",
                "Improved Characteristics",
                "Long-Winded",
                ("Puissant {ability}", {"ability": "Athletics"}),
                "Proud (Major)",
                "Reckless (Minor)",
                "Imposing Appearance",
                "Fast Runner",
                "Good Jumper",
                "Tireless",
                "Greater Power",
                "Greater Power",
                ("Major Virtue", {"virtue": "Essential Virtue (Swift as the Wind)"}),
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Lesser Power",
            ],
            "abilities": [
                ("Athletics", 5, "racing"),
                ("Awareness", 3, "obstacles"),
                ("Brawl", 2, "dodging"),
            ],
            "traits": {
                "Swift as the Wind (Quickness)": 6,
                "Horse": 3,
                "Proud": 2,
                "Loyal to Owner": 2,
                "Brave": 1,
            },
        },
        attacks=[b.attack("Kick", 4, 2, 6, 5)],
        soak=3,
        fatigue_levels="OK, 0/0, -1/-1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Break the Hex",
                2,
                -1,
                "Vim",
                level=40,
                does="Ends a spell that is on her if she can double its "
                "level on a stress die + 55. PeVi 40, a Greater Power.",
            ),
            b.power(
                "Born in the Saddle",
                0,
                4,
                "Corpus",
                rtd=("Touch", "Sun", "Individual"),
                level=5,
                does="Whoever rides her adds +3 to Ride rolls. MuCo 5, a Lesser Power.",
            ),
            b.power(
                "Ward the Rider",
                2,
                -1,
                "Corpus",
                rtd=("Touch", "Sun", "Individual"),
                level=40,
                does="Her rider gains +5 Soak. She may keep it up as long as "
                "she likes, but regains the Might only once she lets it lapse, "
                "and each use gives the rider a Warping Point. MuCo 40, a "
                "Greater Power.",
            ),
        ],
        vis=[BodyVis(4, "Animal", "one in each hoof")],
        appearance=(
            "A horse of flawless build, caramel-coloured, with a mane and "
            "tail of cream."
        ),
        notes=(
            "When a mare foals seven fillies with no colt between them, the "
            "seventh may be a true mare. Nothing ill-meaning can touch her, "
            "her rider is kept from harm, and no horse can outrun her. Her "
            "Essential Trait, Swift as the Wind, adds +3 to running and "
            "jumping and stands in for her Quickness in any race. The magi of "
            "Lámbaird have tried to breed one and failed so far. A magus "
            "must win her friendship: binding one by magic brings the Eagle "
            "King's complaint at Tribunal, and a fíorláir once spoke for the "
            "beasts of magic there until an English magus asked her to be "
            "his familiar and she gave up the seat. Some of the old royal "
            "horses' descendants roaming near Armagh turn out to be true "
            "mares.\n"
            "Where she first touched the earth at her birth grows seamair "
            "Mhuire, Mary's Clover, a four-leaved shamrock. Enriched "
            "(Realms of Power: Magic), set in silver, blessed by a priest "
            "and sung over to the Virgin daily for a season, it gives its "
            "wearer the Luck Virtue. " + _wounds(2)
        ),
    )
    _MADE["dobhar_chu"] = b.creature(
        "Dobhar-chú, the King Otter",
        page="ch. 10",
        realm="Magic",
        might=8,
        form="Aquam",
        size=1,
        season="Summer",
        cunning=True,
        confidence=(2, 5),
        how_many="usually a mated pair, one hiding while the other fights",
        block={
            "characteristics": _chars(0, 0, 1, -3, 3, 1, 2, 1),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                ("Ways of the {land}", {"land": "Lough"}),
                ("Ferocity", {"audience": "against interlopers"}),
                "Improved Characteristics",
                ("Puissant {ability}", {"ability": "Swim"}),
                "Self Confident",
                "Wrathful (Major)",
                "Infamous",
                "Amphibious",
                "Imposing Appearance",
                "Imposing Appearance",
                "Pursuit Predator",
                "Tireless",
                "Gigantic",
                (
                    "Major Virtue",
                    {"virtue": "Greater Immunity (metal weapons)"},
                ),
                "Ritual Power",
                ("Minor Virtue", {"virtue": "Life Boost"}),
                "Improved Attack",
                "Improved Attack",
                "Lesser Malediction",
                "Temporary Might",
            ],
            "abilities": [
                ("Area Lore: (local)", 4, "waterways"),
                ("Awareness", 3, "food"),
                ("Brawl", 5, "teeth"),
                ("Hunt", 4, "food"),
                ("Stealth", 4, "reed beds"),
                ("Survival", 3, "loughs"),
                ("Swim", 5, "loughs"),
            ],
            "traits": {
                "Territorial": 6,
                "Brave": 3,
                "Devoted to Mate": 3,
                "Otter": 3,
            },
            "reputations": {"Killer (local)": 4},
        },
        attacks=[
            b.attack("Teeth", 4, 15, 11, 6),
            b.attack("Grapple", 4, 14, 9, None),
        ],
        soak=2,
        fatigue_levels="OK, 0/0, -1/-1, -3/-3, -5, Unconscious",
        powers=[
            b.power(
                "Death Curse",
                0,
                -20,
                "Vim",
                level=50,
                does="Falls at once on whoever deals it the killing blow, "
                "with +5 Penetration for each Fatigue level it had left (its "
                "Life Boost). Within a day the killer meets some deadly "
                "mishap, a falling bridge, a fire, a lightning stroke, which "
                "luck or skill may still let him survive. Counts as a level "
                "50 spell for countering; a Ritual Power with no Hermetic "
                "equivalent.",
            ),
        ],
        vis=[BodyVis(2, "Rego", "in the fur that bears the cross")],
        appearance=(
            "An otter grown to seven feet from nose to tail, white all over "
            "save its black ears and a black stripe running down its back "
            "and across its shoulders in the shape of a cross."
        ),
        notes=(
            "Fierce as any lion, and proof against ordinary steel: only "
            "silver wounds it (its Lesser Malediction), and its Soak counts "
            "against any other metal as immunity. Its Combat totals include "
            "Ways of the Lough. It goes for the legs and hauls its prey "
            "toward the water; each round the grapple holds brings the "
            "victim nearer, and once in the water he must make a "
            "Deprivation roll every round he struggles. It is canny and "
            "often spends Fatigue to exert itself.\n"
            "Its cross-marked skin is a famous charm, freed by Enrichment "
            "(Realms of Power: Magic), but only by the one who killed it and "
            "lived through the curse. Cured in salt, in smoke or in sweat, "
            "renewed and rubbed nine times nine times nine every day for a "
            "season, a scrap gives a ship Greater Immunity to Water, a house "
            "Greater Immunity to Fire, or a man Charmed Life (Houses of "
            "Hermes: True Lineages). The ship and the house are kept safe, "
            "not always the people in them. " + _wounds(1)
        ),
    )


# -- chapters 6 and 11: the faeries --


def _faeries(hibernia: Hibernia) -> None:
    b = hibernia.b
    _MADE["boinn"] = _not_magic(
        b.creature(
            "Bóinn, the Great White Cow",
            page="ch. 6",
            realm="Faerie",
            might=35,
            form="Aquam",
            size=2,
            confidence=(3, 1),
            block={
                "characteristics": _chars(-1, 0, 2, -1, 7, 3, 2, -2),
                "virtues_flaws": [
                    "Narrowly Cognizant",
                    "Animal Ken",
                    "Faerie Beast",
                    "Faerie Speech",
                    *["Improved Characteristics"] * 3,
                    "Greater Power",
                    "Greater Power",
                    "Lesser Power",
                    "Lesser Power",
                    "Pretentious",
                    "Reputation As Confidence",
                    ("Ways of the {land}", {"land": "River"}),
                    "Busybody",
                    _salt(),
                    "Poor Combatant",
                    "Reduced Damage",
                    "Tough Hide",
                ],
                "abilities": [
                    ("Animal Ken", 6, "cattle"),
                    ("Area Lore: Ireland", 7, "Leinster"),
                    ("Awareness", 1, "in water"),
                    ("Charm", 3, "men other than her husband"),
                    ("Guile", 3, "about infidelity"),
                    ("Swim", 10, "in rivers"),
                ],
                "traits": {
                    "Inquisitive": 3,
                    "Vengeful": 2,
                    "Unfaithful to Husbands": 1,
                },
                "reputations": {
                    "River Goddess (Meath)": 3,
                    "Wife of Nuadha (Laighin)": 3,
                },
            },
            attacks=[b.attack("Hooves", 0, 3, -2, 6)],
            soak=6,
            powers=[
                b.power(
                    "Spirit Away",
                    0,
                    -2,
                    "Vim",
                    does="A variable cost: adds Threshold points to those a "
                    "mortal or a group has gathered (Realms of Power: "
                    "Faerie).",
                ),
                b.power(
                    "Allure",
                    1,
                    -3,
                    "Mentem",
                    does="+3 to Communication rolls to seduce.",
                ),
                b.power(
                    "Appear Human",
                    1,
                    0,
                    "Imaginem",
                    does="Always on: she seems a lovely noblewoman, but "
                    "hurt in the eye, the arm and the foot, wounds from "
                    "gazing into the Well of Wisdom that will never heal. The "
                    "book gives no Init.",
                ),
                b.power(
                    "Deluge of Rushing and Dashing",
                    8,
                    -10,
                    "Aquam",
                    does="The Hermetic spell, but only on the Boyne; she "
                    "drowns those who betrayed her as they ford it.",
                ),
                b.power(
                    "Drowned Standing",
                    3,
                    -5,
                    "Aquam",
                    does="Fills the target's lungs with Boyne water for +15 "
                    "damage that armour cannot soak.",
                ),
                b.power(
                    "Guide",
                    3,
                    -5,
                    "Mentem",
                    does="Quietly steers a group toward deeds that help Meath "
                    "at Leinster's cost, above all those that move wealth, "
                    "power or office into Meath; the storyguide advises them "
                    "as with Common Sense, but to her ends (Realms of Power: "
                    "Faerie).",
                ),
            ],
            vis=[BodyVis(7, "Aquam", "in her tail")],
            equipment="None.",
            appearance=("A huge white cow that shines, plainly more than a beast."),
            notes=(
                "A river goddess of the Tuatha Dé and wife of Nuadha, who "
                "sleeps under Sídh Neachtain at Carbury. Long ago she came to "
                "the Well of Wisdom, the spring at the Boyne's source, and it "
                "burst out in the flood that made the river. Her infidelity "
                "gave the Daghda a son, Aonghus, and she and Nuadha quarrel "
                "still. Where Nuadha stands for the kings of Leinster, she "
                "likes stories of power and riches flowing into Meath, as "
                "her river does: the Boroimhe tribute, or the justiciarship "
                "passing from FitzHenry to de Lacy, and she would rather her "
                "husband served than ruled. Pretenses are her Abilities "
                "here. Her Pretentious Quality concerns the rulers of Meath. "
                "The book prints Medium wounds to 13 and Incapacitated from "
                "21, which do not fit Size +2; the ranges below are the "
                "standard ones. " + _wounds(2)
            ),
        )
    )
    _MADE["donn"] = _not_magic(
        b.creature(
            "Donn, the Dark One",
            page="ch. 11",
            realm="Faerie",
            might=50,
            form="Corpus",
            size=1,
            confidence=(4, 3),
            block={
                "characteristics": _chars(2, 0, -3, -3, 2, 3, 3, 1),
                "virtues_flaws": [
                    "Negative Reaction",
                    "Greater Power",
                    "Faerie Sight",
                    "Faerie Speech",
                    "Highly Cognizant",
                    "Humanoid Faerie",
                    "Large",
                    "Lesser Power",
                    "Lesser Power",
                    "Personal Power",
                    "Reputation As Confidence",
                    _salt(),
                    "Infamous",
                    _ward("a red ribbon tied in the hair or to a tail"),
                ],
                "abilities": [
                    ("Animal Handling", 3, "chariots"),
                    ("Athletics", 3, "leaping"),
                    ("Etiquette", 3, "hosting feasts"),
                    ("Faerie Lore", 2, "the Tuatha Dé"),
                    ("Single Weapon", 8, "long sword"),
                ],
                "traits": {"Hates Goibhniu": 3, "Rapacious": 2, "Taciturn": 3},
                "reputations": {"The Dark One (Hibernia's Irish)": 4},
            },
            attacks=[
                b.attack("Short Spear", 3, 13, 9, 7),
                b.attack("Short Spear (from chariot)", 3, 16, 12, 7),
                b.attack("Long Sword", 3, 16, 11, 8),
                b.attack("Long Sword (from chariot)", 3, 19, 14, 8),
            ],
            soak=3,
            powers=[
                b.power(
                    "Create the Dead Host",
                    5,
                    -10,
                    "Corpus",
                    rtd=("Touch", "Moon", "Individual"),
                    does="Makes a corpse that is the exact likeness of any "
                    "man or woman he can see. Base 5, +1 Touch, +3 Moon.",
                ),
                b.power(
                    "Bursting the Heart Vessel",
                    1,
                    -4,
                    "Corpus",
                    rtd=("Touch", "Momentary", "Individual"),
                    does="At his touch the victim's heart bursts and he dies "
                    "on the spot. Base 30, +1 Touch, the spare Greater Power "
                    "levels lowering its cost.",
                ),
                b.power(
                    "Summon the Curtains of Donn",
                    5,
                    -10,
                    "Auram",
                    rtd=("Touch", "Sun", "Group"),
                    does="Fog pours from his fingertip into a bank a mile "
                    "across, which then behaves as any fog; he hides his "
                    "comings and goings in it. Built as Base 2 with +1 Touch, "
                    "+2 Sun, +2 Group, +1 size and +1 for being somewhat "
                    "unnatural.",
                ),
                b.power(
                    "Transform into Animal",
                    2,
                    -1,
                    "Animal",
                    rtd=("Personal", "Sun", "Individual"),
                    does="Takes the shape of a fish, a bull, a stag, a hawk or "
                    "a boar, most often to fight his faerie foe Find. Base "
                    "10, +2 Sun, +1 size.",
                ),
            ],
            vis=[BodyVis(10, "Corpus", "one in each severed head tied to his belt")],
            equipment=(
                "A warrior's arms and gear, and a chariot drawn by four horses."
            ),
            appearance=(
                "Seven feet tall and bare but for a broad leather belt over "
                "his belly, from which ten human heads hang; blue tattoos "
                "cover his chest, arms and legs. A great spear fills his "
                "left hand and a sword his right, both forever "
                "dripping blood."
            ),
            notes=secrets(
                "The death god of the Tuatha Dé, a king like any other with "
                "sons, herds and raids on his neighbours. The dead gather at "
                "his rocky island palace, Teach Duínn, off the Munster "
                "coast. In war his three red-haired sons ride through the "
                "land spreading dread, and the slain are said to rise at "
                "Teach Duínn to march in his host; in peace he adds to it a "
                "man at a time, killing sleepers so their spirits fly to him, "
                "or leaving a false corpse behind and carrying the living "
                "man off. He fought the Order in the Schism War and hates the "
                "smith Goibhniu. Within Teach Duínn he keeps things that "
                "command the dead, walking corpse and ghost alike. A "
                "storyguide character, not balanced: his age and long study "
                "of men give him more Pretenses than the rules allow; they "
                "are his Abilities here. Good for feud stories, since his "
                "enemies are many, and for war. " + _wounds(1),
                "No one knows why he gathers an army. His great warded "
                "regio could hide one, and magi fear the endless fighting in "
                "Munster may set off another war with him; anyone starting a "
                "war with the Order would find him a ready ally. Nor is it "
                "known what the living captives are for: servants, husbands "
                "for his daughters, or subjects for his druids' tests.",
            ),
        )
    )
    _MADE["trooping_faerie"] = _not_magic(
        b.creature(
            "Trooping Faerie",
            page="ch. 11",
            realm="Faerie",
            might=5,
            form="Herbam",
            size=0,
            how_many="a troop of about twenty, each like the rest",
            block={
                "characteristics": _chars(-3, 3, -1, 0, 0, 1, 1, 3),
                "virtues_flaws": [
                    "Negative Reaction",
                    "Faerie Speech",
                    "Hybrid Form",
                    "Personal Power",
                    "Incognizant",
                    _ward("a bowl or a drop of fresh cow's milk"),
                ],
                "abilities": [
                    ("Awareness", 4, "lone travellers"),
                    ("Brawl", 7, "claws"),
                    ("Hunt", 5, "tracking"),
                    ("Leadership", 5, "members of the pack"),
                ],
                "traits": {"Herd Mentality": 3, "Savage": 3},
            },
            attacks=[b.attack("Claws", 2, 11, 14, 2)],
            soak=1,
            powers=[
                b.power(
                    "Flight",
                    1,
                    2,
                    "Corpus",
                    rtd=("Personal", "Sun", "Individual"),
                    does="It flies, steering hard turns with Athletics. Base "
                    "4, +2 Sun.",
                ),
                b.power(
                    "Invisibility",
                    1,
                    2,
                    "Imaginem",
                    rtd=("Personal", "Sun", "Individual"),
                    does="It turns invisible. Base 4, +2 Sun, +1 moving image.",
                ),
            ],
            vis=[BodyVis(1, "Herbam", "in one of its thumbnails")],
            equipment="Tattered clothes.",
            appearance=(
                "This troop are cat-folk: nearly a man's height, with a "
                "cat's face and ears and dangerous clawed hands, ragged "
                "clothes, and a leaping, bounding gait through the woods. "
                "Other troops look like ghostly copies of today's soldiers, "
                "stooped and hooded clansmen of old, or phantoms flying "
                "through the air."
            ),
            notes=(
                "The slua sí: roving night gangs that wreck and sometimes "
                "kill along their path. They have played the part so long it "
                "is a story of its own, though some echo the fianna, Ostman "
                "raiders or the English knights now seizing what they can; "
                "the flying ones are taken for the restless dead, but have "
                "nothing to do with the Infernal or the Divine. One alone has "
                "no name and, questioned, can only repeat what its troop "
                "cares about. A single one is no great danger; together they "
                "kill. It fights in a trained group of its fellows as leader "
                "and vanguard, always adding the group bonus to its Attack. "
                "They do not parley beyond threats, other faeries use them as "
                "a menace or turn them on rivals, and their wanderings drive "
                "other faeries from their homes. A horse skull buried under a "
                "house, or a hearth kept lit all year, keeps them out. Lay "
                "brothers at Mellifont's grange near Newgrange have watched "
                "them ruin the crops. " + _wounds(0)
            ),
        )
    )
    _MADE["cailte"] = _not_magic(
        b.creature(
            "Caílte mac Rónáin",
            page="ch. 11",
            realm="Faerie",
            might=20,
            form="Corpus",
            size=0,
            block={
                "characteristics": _chars(-2, 0, -2, 3, 1, 2, 2, 0),
                "virtues_flaws": [
                    ("Infiltrator (Minor)", {"status": "outlaw leader"}),
                    "Greater Power",
                    "Increased Faerie Might (Major)",
                    "Faerie Speech",
                    "Humanoid Faerie",
                    "Lesser Power",
                    "Personal Power",
                    "Difficult Underlings",
                    "Optimistic (Major)",
                    "Incognizant",
                    "Role Requires Suffering",
                    _ward("church bells"),
                ],
                "abilities": [
                    ("Athletics", 4, "hurling"),
                    ("Brawl", 3, "fist"),
                    ("Church Lore", 1, "baptisms"),
                    ("Dominion Lore", 2, "St. Patrick"),
                    ("Hunt", 3, "deer"),
                    ("Etiquette", 3, "hospitality rules"),
                    ("Faerie Lore", 5, "Fenian Cycle"),
                    ("Magic Lore", 1, "Hibernian monsters"),
                    ("Profession: Poet", 5, "poems about Fionn"),
                    ("Single Weapon", 3, "short spear"),
                    ("Thrown Weapon", 2, "javelin"),
                ],
                "traits": {"Optimistic": 3, "Gullible": 2, "Innocent": 2},
            },
            attacks=[
                b.attack("Short Spear", 2, 8, 4, 6),
                b.attack("Javelin", 0, 7, 3, 6),
            ],
            soak=2,
            powers=[
                b.power(
                    "Speech of the Deer",
                    5,
                    -10,
                    "Animal",
                    rtd=("Voice", "Concentration", "Individual"),
                    does="He talks with an animal within reach of his voice. "
                    "Base 10, +2 Voice, +1 Conc.",
                ),
                b.power(
                    "Speed of the Deer",
                    3,
                    -3,
                    "Corpus",
                    rtd=("Personal", "Sun", "Individual"),
                    does="He runs as fast as a deer, +3 to rolls for racing or "
                    "speed. Base 15, +2 Sun.",
                ),
                b.power(
                    "Removal of a Thousand Cares",
                    0,
                    -3,
                    "Mentem",
                    rtd=("Voice", "Moon", "Individual"),
                    does="Like Pains of the Thousand Worries without the "
                    "pain: the target turns idle and listless from joy. He "
                    "often uses it when a tale is done, to prove he belongs "
                    "among Ireland's poets, but needs no poem to use it. "
                    "Base 4, +2 Voice, +3 Moon, +1 complex; four spare "
                    "levels bring the cost to 0.",
                ),
            ],
            vis=[BodyVis(4, "Mentem", "in four strands of his golden hair")],
            equipment=("A spear, a sword, and the old dress of an Irish noble."),
            appearance=(
                "A fine-looking youth, long and straight of limb, with "
                "flowing golden hair, in the clothes of a far older age: a "
                "patterned cloak flung over one shoulder and pinned with a "
                "rich brooch."
            ),
            notes=secrets(
                "Fionn mac Cumhaill's nephew, a poet and warrior from the "
                "Tales of the Elders, who guided Saint Patrick's company "
                "across Munster telling him Fionn's stories. He believes the "
                "saint raised him from the dead, and now he roams Ireland's "
                "fields and woods as a man. Though incognizant, he can raise "
                "his Pretenses, which are his Abilities here. He is "
                "baptised and a true Christian, though Dominion auras weaken "
                "his powers. He leads a band he calls fianna and tries to "
                "keep them to noble deeds, but they mostly rob and plunder "
                "as they please. The book builds him as a companion a player "
                "could run. " + _wounds(0),
                "His fianna are outlaws who have gone over to the faerie.",
            ),
        )
    )
    _MADE["arastotail"] = _not_magic(
        b.creature(
            "The Head of Arastotail",
            page="ch. 11",
            realm="Faerie",
            might=15,
            form="Mentem",
            size=-3,
            block={
                "characteristics": _chars(3, 3, 1, 3, -3, 2, -3, -2),
                "virtues_flaws": [
                    "Negative Reaction",
                    ("Focus Power", {"focus": "Aquam"}),
                    "Greater Power",
                    "Faerie Sight",
                    "Faerie Speech",
                    "Humanoid Faerie",
                    "Narrowly Cognizant",
                    ("Sovereign Ward", {"ward": "women"}),
                ],
                "abilities": [
                    ("Artes Liberales", 6, "rhetoric"),
                    ("Brawl", 1, "dodge"),
                    ("Faerie Lore", 1, "local faeries"),
                    ("Philosophiae", 7, "ethics"),
                ],
                "traits": {"Belligerent to Males": 3, "Gullible to Females": 3},
            },
            attacks=[b.attack("Dodge", 0, None, 0, None)],
            soak=2,
            powers=[
                b.power(
                    "The Master's Agreement",
                    3,
                    -5,
                    "Mentem",
                    rtd=("Voice", "Sun", "Individual"),
                    does="Brings a man round to agree with whatever case the "
                    "head has put. MuMe Base 15, +2 Voice, +2 Sun.",
                ),
                b.power(
                    "Trust of the Master's Servant",
                    1,
                    -3,
                    "Mentem",
                    rtd=("Eye", "Sun", "Individual"),
                    does="Like Trust of Childlike Faith: makes the target "
                    "trust him, if someone holds the head and the target "
                    "meets its eyes. PeMe Base 4, +1 Eye, +2 Sun.",
                ),
                b.power(
                    "Master of Waves",
                    0,
                    -7,
                    "Aquam",
                    does="Any Intellego, Rego, Muto or Perdo Aquam effect of "
                    "level 25 or less, costing a Might Point a magnitude.",
                ),
            ],
            vis=[BodyVis(3, "Mentem", "in his eye-teeth")],
            appearance=(
                "A Greek scholar's head, hook-nosed, with wiry hair going "
                "thin on top; the neck ends in a stump of skin, with no "
                "blood."
            ),
            notes=(
                "The Irish hold Aristotle to have been a magician, "
                "Arastotail, whose wife foiled his study of bees, stars and "
                "tides and beat him in every quarrel. Seeking to live for "
                "ever, he cut off his own head and bade a servant bury it in "
                "a certain spot and dig it up at dawn. In some tellings the "
                "servant forgot and the magician died; in others the head's "
                "muffled shouts carried far from the mound, until a farmer "
                "unearthed it and it ordered him to go and find its body. It "
                "loves to order men about on lowly errands to prove itself "
                "their better, a feeble proof, and now and then enjoys a "
                "learned dispute on philosophy. Women are beyond its power, "
                "and near one it grows slow and foolish. Its Pretenses are "
                "its Abilities here. " + _wounds(-3)
            ),
        )
    )


# -- chapter 13: the demons --


def _demons(hibernia: Hibernia) -> None:
    b = hibernia.b
    _MADE["harvest_thief"] = _not_magic(
        b.creature(
            "Harvest Thief",
            page="ch. 13",
            realm="Infernal",
            might=2,
            form="Herbam",
            size=-10,
            order="Aerial Powers",
            hierarchy=0,
            weakness="Abhorrent Material (the sound of a barking dog)",
            how_many="hundreds, loosed on the fields together",
            block={
                "characteristics": _chars(-2, 1, 0, 0, -20, 0, 3, 10),
                "virtues_flaws": ["Weak Characteristics"],
                "abilities": [
                    ("Area Lore: (local area)", 5, "farmlands"),
                    ("Athletics", 5, "flying"),
                    ("Brawl", 5, "dodge"),
                ],
                "traits": {"Cowardly": 3, "Hungry": 1},
            },
            attacks=[
                b.attack("Dodge", 10, None, 16, None),
                b.attack("Bite", 10, 8, 16, -19),
            ],
            soak=0,
            fatigue_levels=FATIGUE,
            powers=[
                b.power(
                    "Coagulation",
                    1,
                    10,
                    "Corpus",
                    does="Takes on a body, which it must do to gnaw through the crops.",
                ),
                b.power(
                    "The Thief of Vitality",
                    1,
                    10,
                    "Herbam",
                    does="Kills one plant of a grain or root crop, or one "
                    "fruit in an orchard.",
                ),
            ],
            appearance=(
                "Unseen and bodiless, it rides a breeze that runs through "
                "the crops against the wind. Given a body it is a skinny "
                "green imp the size of a wheat grain, with absurdly long "
                "limbs, long ears that thin to a trailing thread, and sharp "
                "crooked teeth for chewing through crops, which sets off its "
                "power."
            ),
            notes=(
                "One of Hibernia's many demons of hardship, each with a "
                "little power over some disaster. Each has a taste for one "
                "crop and cannot bear any other, and they are seldom found "
                "abroad outside the harvest. Timid and easily kept off, by "
                "magic or by a dog's barking, which terrifies them. A swarm "
                "can be boiled down to a single pawn of tainted vis, Vis "
                "Infesta (Realms of Power: The Infernal). Any wound kills one. Like every "
                "demon of Ireland since Saint Patrick, it may not take a "
                "serpent's shape."
            ),
        )
    )
    _MADE["sluagh"] = _not_magic(
        b.creature(
            "The Sluagh",
            page="ch. 13",
            realm="Infernal",
            might=5,
            form="Mentem",
            size=0,
            order="Evil Spirit",
            hierarchy=0,
            weakness=(
                "Compulsiveness (may enter a house only by an open window facing west)"
            ),
            how_many="a flock, gathering wherever a death is near",
            block={
                "characteristics": _chars(0, 2, 0, 0, 0, 0, 1, 2),
                "virtues_flaws": ["Berserk", "Sharp Ears", "Blind"],
                "abilities": [
                    ("Area Lore: (county)", 5, "settlements"),
                    ("Athletics", 3, "flying at speed"),
                    ("Brawl", 5, "grappling"),
                ],
                "traits": {"Selfish": 5, "Cruel": 4},
            },
            attacks=[
                b.attack("Dodge", 2, None, 7, None),
                b.attack("Large Teeth", 2, 10, 7, 3),
                b.attack("Grapple", 2, 7, 8, 0),
            ],
            soak=0,
            fatigue_levels=FATIGUE,
            powers=[
                b.power(
                    "Let Me In",
                    0,
                    2,
                    "Herbam",
                    does="Though bodiless, it can rattle shut doors and "
                    "shutters, and does so at any west window barred against "
                    "it.",
                ),
                b.power(
                    "Come With Me",
                    5,
                    2,
                    "Mentem",
                    does="Pulls the dying target's last breath, and his "
                    "spirit with it. If it gets the spirit a mile off, the "
                    "spirit becomes a Sluagh too; if it loses hold, another "
                    "may pay the Might and try again.",
                ),
            ],
            vis=[BodyVis(1, "Mentem", "Vis Infesta")],
            appearance=(
                "Starved grey things with long thin hair trailing from torn "
                "and clawed scalps, lips pulled so far back the whole jaw "
                "shows, and blind, lidless eyes. They fly with their rags "
                "streaming as if dragged through water."
            ),
            notes=(
                "Invisible spirits that scent death coming and flock to the "
                "dying from the west, keening as they fly and falling silent "
                "at the house. In they climb by the window, to crouch on "
                "every surface with teeth softly clicking, or knock at "
                "shutters closed against them. One seizes the last breath "
                "and drags the spirit out, and the flock flees shrieking, "
                "flaying it until it is gaunt and lidless like them. They "
                "have no hold on a spirit that dies before they get in, or "
                "that has had Extreme Unction. Closing the west windows, "
                "which an Intelligence + Infernal Lore roll against 6 "
                "reveals, keeps them out, and Nightwalkers (Hedge Magic) "
                "gather on a night a death is expected to guard the soul. "
                "Blind but sharp of hearing: under the magical combat rules "
                "of Houses of Hermes: Societates every foe is Indistinct to "
                "them (+3 Attack and +6 Defense for the foe), except when "
                "grappling. They travel together but always fight as an "
                "untrained group, and leave damp patches where they took a "
                "victim, from their slavering. " + _wounds(0)
            ),
        )
    )
    _MADE["temoneth"] = _not_magic(
        b.creature(
            "Temoneth, Messenger of Delgnat's Betrayal",
            page="ch. 13",
            realm="Infernal",
            might=30,
            form="Mentem",
            size=0,
            order="Furies",
            hierarchy=5,
            weakness="Protected Group (those truly happy in marriage)",
            block={
                "characteristics": _chars(0, 3, 0, 1, 2, 3, 4, 4),
                "virtues_flaws": ["Berserk"],
                "abilities": [
                    ("Area Lore: Hibernia", 9, "personalities"),
                    ("Brawl", 3, "dodge"),
                    ("Charm", 5, "earning trust"),
                    ("Folk Ken", 5, "weaknesses"),
                    ("Intrigue", 9, "alliances"),
                ],
                "traits": {"Wrathful": 4, "Arrogant": 3, "Self-Controlled": -6},
                "reputations": {"Ireland's First Corrupter (Infernal)": 5},
            },
            attacks=[
                b.attack("Dodge", 4, None, 4, None),
                b.attack("Large Claws", 4, 12, 12, 8),
            ],
            soak=0,
            fatigue_levels=FATIGUE,
            powers=[
                b.power(
                    "Berserker Rage",
                    1,
                    0,
                    "Mentem",
                    does="Grants anyone the Berserk Virtue until they calm down.",
                ),
                b.power(
                    "The Betrayal Revealed",
                    1,
                    0,
                    "Mentem",
                    does="Once the target has brought himself to the edge of "
                    "suspicion, makes him wholly certain of it.",
                ),
                b.power("Coagulation", 1, 0, "Corpus", does="The usual demonic power."),
                b.power(
                    "Endurance of the Enraged",
                    0,
                    0,
                    "Mentem",
                    does="She suffers no wound penalties save to Defense.",
                ),
                b.power(
                    "Obsession",
                    1,
                    9,
                    "Mentem",
                    does="The usual demonic power; her sin is lust.",
                ),
                b.power(
                    "Possession",
                    0,
                    0,
                    "Mentem",
                    does="The usual demonic power, at a variable cost.",
                ),
                b.power(
                    "Waxing Tide of Humors",
                    3,
                    2,
                    "Mentem",
                    does="Passion swamps reason: the victim needs a stress "
                    "roll against 9, adjusted by fitting Personality Traits, "
                    "to master an anger, lust, wantonness or spite. She often "
                    "follows a successful Obsession with it.",
                ),
            ],
            vis=[BodyVis(6, "Mentem", "Vis Infesta")],
            appearance=(
                "From the front a voluptuous naked woman with only a scrap of "
                "veil over her face. When she turns, a ragged line of flesh "
                "has been torn away to bare the bloody skeleton, her bowels "
                "dangle from the back of her open pelvis, and her heel bones "
                "click wetly as she walks."
            ),
            notes=secrets(
                "The child of greed and deceit, behind many of Ireland's "
                "woes since Delgnat betrayed her husband Partholon, among "
                "them the flight of Dervorgilla, the Uí Ruairc queen, with "
                "her husband's sworn enemy Dermot MacMurrough. She sows lust "
                "and strife between men and women, but is too proud to "
                "trouble the lowly when their betters offer better sport. "
                "The book prints her Area Lore without a score and a stray 9 "
                "after Brawl; the 9 is taken as the Area Lore's. " + _wounds(0),
                "Her chief weapon is Possession: she hides in the courts of "
                "the rich, preferably in several advisers to the main "
                "players at once, and urges reckless deeds dressed as wise "
                "counsel, stirring lust for what cannot be had until "
                "betrayal and cruel revenge follow. But she has no "
                "self-control: an insult to one of her hosts can drive her "
                "to murder, wrecking her schemes and forcing her to flee "
                "before she is found out.",
            ),
        )
    )


# -- chapter 12: the saints --


#: What every saint has, as the book gives it.
_SAINT_BLOCK: dict[str, Any] = {
    "characteristics": {
        "intelligence": 5,
        "perception": 5,
        "presence": 5,
        "communication": 5,
    }
}


def _saint_powers(b: Builder) -> dict[str, CreaturePower]:
    """Chapter 12's eighteen new powers for Irish saints, by name, made
    afresh for each saint so each holds its own."""
    return {
        p.name: p
        for p in (
            b.power(
                "Banish Magical Monster",
                0,
                5,
                "Vim",
                does="Demon's Eternal Oblivion, but against Magic Animals: if "
                "it penetrates, the beast's Might falls for good by the "
                "saint's Might.",
            ),
            b.power(
                "Bless the Book",
                2,
                2,
                "Aquam",
                does="Water can no longer harm the blessed book, which stays "
                "readable even after centuries on a lough bed.",
            ),
            b.power(
                "Borne up by Angels",
                2,
                20,
                "Corpus",
                does="One falling to his death who calls on the saint, if "
                "heard, is caught by angels (Divine Might 15) who slow the "
                "fall and set him down gently.",
            ),
            b.power(
                "Call Forth the Waters",
                4,
                1,
                "Aquam",
                does="Raises a wave fifty paces wide and ten high that can "
                "sweep a small island bare; or, more kindly, opens a spring "
                "of fresh water.",
            ),
            b.power(
                "Counting Sheep",
                3,
                5,
                "Animal",
                does="A flock or herd that was lost, or given to the poor, is "
                "found to be whole again when counted.",
            ),
            b.power(
                "Cure Madness",
                4,
                0,
                "Mentem",
                does="Heals someone, not necessarily the petitioner, of insanity.",
            ),
            b.power(
                "Hide Fugitive",
                1,
                13,
                "Imaginem",
                does="The petitioner looks like a natural feature, and feels "
                "and sounds like one too, hiding her from pursuers.",
            ),
            b.power(
                "Multitude of Fish",
                2,
                9,
                "Aquam",
                does="Waters whose fish have dwindled or gone become a place "
                "fish flock to, enriching the local fisherfolk.",
            ),
            b.power(
                "Protect the Wild Prey",
                5,
                3,
                "Animal",
                does="A wild beast the saint blesses scares off hounds and "
                "cannot be hurt by weapons until sunset.",
            ),
            b.power(
                "Shatter Idol",
                2,
                9,
                "Terram",
                does="A curse that crumbles a false stone idol lately "
                "worshipped into rubble.",
            ),
            b.power(
                "Still the Waves",
                5,
                4,
                "Aquam",
                does="Water stops as if frozen, becalming a ship, holding "
                "back waves or halting a river until the curse is lifted; or "
                "a ship is blessed with one voyage free of storms.",
            ),
            b.power(
                "Strange Fruit",
                2,
                5,
                "Herbam",
                does="Any tree bears good fruit, out of season the first "
                "time; it breeds true, and its offspring fruit in season "
                "after.",
            ),
            b.power(
                "Tame the Wild Beast",
                3,
                5,
                "Animal",
                does="Gives the petitioner one divine animal companion, which "
                "does not age while the petitioner lives and helps as a "
                "friend would; betray or harm it and the saint curses the "
                "petitioner.",
            ),
            b.power(
                "The Captive Made Free",
                5,
                4,
                "Terram",
                does="The ground shakes, prison walls crack, doors fly open "
                "and chains drop from captives or slaves.",
            ),
            b.power(
                "The Unquenchable Fire",
                2,
                6,
                "Ignem",
                does="A blessed hearth fire that never goes out, even with no "
                "fuel left; fires lit from it are ordinary.",
            ),
            b.power(
                "The Sky Made Light",
                2,
                9,
                "Auram",
                does="By day, clears away storm, cloud or magical foul "
                "weather until sunset.",
            ),
            b.power(
                "Test of Truth",
                2,
                9,
                "Mentem",
                does="A curse: until the petitioner has done questioning him, "
                "the victim can speak only truth, and an attempt to lie "
                "throws him down in fits. He may keep silent; even demons "
                "cannot lie under it.",
            ),
            b.power(
                "Walk Upon the Waters",
                3,
                7,
                "Corpus",
                does="The one blessed walks on waves or rivers as on stone, "
                "out to a boat and back again.",
            ),
        )
    }


#: Each saint: slug, name, Might, feast, where venerated, patron of,
#: traits, powers, and a few lines in the pack's words.
_SAINTS: tuple[
    tuple[str, str, int, str, str, str, dict[str, int], tuple[str, ...], str], ...
] = (
    (
        "patrick",
        "Saint Patrick (St. Pátraig)",
        50,
        "17 March",
        "all Ireland",
        "Ireland",
        {"Pious": 3, "Vigorous": 2, "Benevolent": 2},
        (
            "Apparition",
            "Expel Demons",
            "Resist Temptation (St. Patrick's Breastplate)",
            "Scourging of Snakes",
            "Shatter Idol",
            "The Faithful Made Whole",
            "The Captive Made Free",
            "The Unquenchable Fire",
            "The Sky Made Light",
        ),
        "Born in Britain, he converted Ireland (his life is in the history). "
        "His best-known miracle cast every snake and venomous creature out "
        "of the island for ever, and no demon of Ireland may now take a "
        "serpent's form. Anyone born Irish may call on him, as on Brigid "
        "and Columba. His Latin name is Patricius; the name he bore in "
        "life, Cothraige, is forgotten by 1220.",
    ),
    (
        "brigid",
        "Saint Brigid of Kildare (Naomh Bríd)",
        50,
        "1 February",
        "all Ireland",
        "Ireland, with Patrick and Columba",
        {"Pious": 3, "Generous": 2, "Compassionate": 2},
        (
            "Apparition",
            "Call Forth the Waters",
            "Counting Sheep",
            "Cure Blindness",
            "Expel Demons",
            "Resist Temptation",
            "Sanctuary of Virginity",
            "The Faithful Made Whole",
            "Test of Truth",
            "Tomorrow's Bounty",
        ),
        "Also called Brigit, or Mary of the Gael. Daughter of a nobleman and "
        "a concubine sold, while carrying her, to a magician, she was so "
        "holy as a baby that she would not eat his food and lived on cows' "
        "milk. Vowed to lifelong virginity, she became a nun, though some "
        "say the blind bishop who received her vows made her a bishop by "
        "mistake, and saw again as he finished. She drove her chariot "
        "across Ireland healing, preaching and helping the poor, for whom "
        "she had a special love. Her Sacred Fire burns at Kildare.",
    ),
    (
        "columba",
        "Saint Columba (Saint Colum Cille)",
        50,
        "9 June",
        "all Ireland, Kells and Derry; Scotland, above all Iona",
        "Ireland (with Patrick and Brigid), Derry, warriors, exiles, Scotland and Iona",
        {"Pious": 3, "Cheerful": 2, "Aggressive": 2},
        (
            "Acknowledgment of Evil",
            "Apparition",
            "Banish Magical Monster",
            "Borne up by Angels",
            "Dysentric Infliction",
            "Expel Demons",
            "Multitude of Fish",
            "Raise the Dead",
            "Resist Temptation",
            "The Dutiful Shepherd",
            "Walk Upon the Waters",
        ),
        "One of the twelve apostles of Ireland. He founded several "
        "monasteries, then copied a book in Saint Finian of Movilla's "
        "scriptorium and meant to keep the copy; Finian claimed it, the "
        "quarrel grew, and many died at the Battle of Cúl Dreimhne. Exiled "
        "for it, he went to convert the Picts, founded Iona, a house of "
        "great austerity, and banished the beast of Loch Ness, among many "
        "wonders.",
    ),
    (
        "abban",
        "Saint Abbán",
        25,
        "16 March",
        "Leinster, above all Wexford and the diocese of Ferns",
        "those who would keep the Irish Church free of English meddling",
        {"Pious": 3, "Brave": 2, "Determined": 2},
        (
            "Apparition",
            "Banish Magical Monster",
            "Counting Sheep",
            "The Captive Made Free",
            "Still the Waves",
            "Walk Upon the Waters",
        ),
        "A prince of Leinster, unusual for having become a Christian before "
        "Patrick came, on travels in England. He converted some of the "
        "royal kin around Wexford, founded a monastery at Abingdon in "
        "England, banished a sea serpent on a voyage to see the Pope and "
        "saved his people from another monster at home. Loved as an "
        "Irishman who converted the English, he is the patron of those who "
        "resist English interference in the Irish Church. Ailbe Ua Mail "
        "Mhuaidh, Bishop of Ferns, wrote his life in 1218 and is spreading "
        "his cult.",
    ),
    (
        "kevin",
        "Saint Kevin of Glendalough (Saint Cóemgen)",
        25,
        "3 June",
        "Leinster",
        "Dublin, Glendalough and crows",
        {"Pious": 3, "Gentle": 2, "Reclusive": 2},
        (
            "Apparition",
            "Counting Sheep",
            "Protect the Wild Prey",
            "Raise the Dead",
            "Strange Fruit",
            "Tame the Wild Beast",
        ),
        "A hermit of royal blood whose holiness drew followers; he fled "
        "them to a remote hill at Glendalough, and when they came anyway "
        "he founded a monastery there. Best known for making willows bear "
        "apples, he loved wild creatures, which often helped him. His name "
        "means the gentle one.",
    ),
    (
        "ciaran",
        "Saint Ciarán of Clonmacnoise",
        25,
        "9 September",
        "Meath, and Clonmacnoise",
        "herdsmen and cattle",
        {"Pious": 3, "Scholarly": 2, "Rustic": 2},
        (
            "Apparition",
            "Bless the Book",
            "Resist Temptation",
            "Tame the Wild Beast",
            "The Faithful Made Whole",
        ),
        "Ciarán the Younger, one of the twelve apostles of Ireland and a "
        "bishop, spent his youth herding in Connacht. A lover of learning, "
        "he founded many monasteries, the greatest Clonmacnoise, where the "
        "yellow plague of Justinian took him early in the sixth century. "
        "His cow gave the vellum of the Book of the Dun Cow.",
    ),
    (
        "malachy",
        "Saint Malachy (Máel Máedóc Ua Morgair)",
        25,
        "3 November",
        "Ulster, above all Armagh",
        "Armagh, visionaries and fisherfolk",
        {"Pious": 3, "Insightful": 2, "Persevering": 2},
        (
            "Apparition",
            "Expel Demons",
            "Multitude of Fish",
            "The Faithful Made Whole",
            "Rebuke the Unfaithful",
        ),
        "Archbishop of Armagh from 1132 to his death in 1148, in troubled "
        "times for the Irish Church; despite many plots he rose from post "
        "to post, helped by the miracles granted him. A great exorcist and "
        "a visionary, he brought fish back to empty rivers and bays and "
        "healed the sick. The Prophecy of the Popes said to be his lies "
        "lost in the Vatican, not to be found for centuries.",
    ),
    (
        "dympna",
        "Saint Dympna (St. Damhna)",
        25,
        "15 May",
        "Ulster and Flanders, above all Ghent",
        "Ghent, Tydavnet, the insane and the anxious",
        {"Pious": 3, "Innocent": 2, "Compassionate": 2},
        (
            "Apparition",
            "Cure Madness",
            "Grant of Serenity",
            "Sanctuary of Virginity",
            "Test of Truth",
        ),
        "A king's daughter, only fifteen when she died. After her mother's "
        "death her father, who saw his wife in her, sought to marry her; "
        "she fled to Ghent, where his men killed her. Both the Irish and "
        "the Flemish mercenaries in English pay honour her. Her staff, her "
        "bachall, is kept at Tydavnet in Ulster and can tell truth from "
        "lies.",
    ),
    (
        "brendan",
        "Saint Brendan the Navigator (Naomh Breandán)",
        25,
        "16 May",
        "Connacht, above all Ardfert, Inishdadroum, Clonfert and Annaghdown",
        "explorers, navigators, Clonfert and Ardfert",
        {"Pious": 3, "Inquisitive": 2, "Brave": 2},
        (
            "Apparition",
            "Expel Demons",
            "Hide Fugitive",
            "Raise the Dead",
            "Still the Waves",
            "Tame the Wild Beast",
        ),
        "Famed for his voyages to the western isles and the Isle of the "
        "Blessed, he was also an abbot, a founder of monasteries and a "
        "worker of wonders. Once he made a runaway slave look like a rock, "
        "and the rock like the slave, so the pursuers hauled off the stone. "
        "His relics are at Clonfert.",
    ),
    (
        "grellan",
        "Saint Grellan",
        25,
        "29 September",
        "Connacht, above all Ballinasloe",
        "the betrayed, those threatened by the Fir Bolg, and Ballinasloe",
        {"Pious": 3, "Peacemaker": 2, "Brave": 2},
        (
            "Apparition",
            "Raise the Dead",
            "Swallowed Alive and Sent to Hell",
            "Protect the Wild Prey",
            "Grant of Serenity",
        ),
        "In his day the Fir Bolg warred with the tribe of Colla da Chrioch. "
        "They broke a first truce, seizing the king's son and killing him "
        "when their queen grew fond of him, and plotted to break a second; "
        "as they drew their weapons the saint, watching from his church, "
        "prayed, and the ground swallowed them. Some say they lie beneath "
        "the bog of Magh Liach still; others that they went straight to "
        "Hell.",
    ),
    (
        "senan",
        "Saint Senan mac Geirrcinn",
        25,
        "8 March",
        "Munster",
        "Scattery Island, the Corco Baiscinn and the Uí Fhidgeinte",
        {"Pious": 3, "Misogynistic": 2, "Righteous Wrath": 2},
        (
            "Acknowledgement of Evil",
            "Apparition",
            "Banish Magical Monster",
            "Call Forth the Waters",
            "Dysentric Infliction",
        ),
        "Best known for driving off the Scathach, the sea serpent that ate "
        "anyone sailing near Scattery Island, with the sign of the Cross so "
        "he could found his monastery there; he overcame many more monsters "
        "by prayer and cursed many bandits to death. Women were barred from "
        "his island: he buried his beloved sister, Saint Ibie, between the "
        "tide marks rather than on it, and another woman died in her boat "
        "on the shore after years of waiting to be let land.",
    ),
    (
        "cronan",
        "Saint Cronan of Tipperary",
        25,
        "28 April",
        "Munster, above all Tipperary and the diocese of Roscrea",
        "the diocese of Roscrea",
        {"Pious": 3, "Passive": 2, "Protective": 2},
        (
            "Apparition",
            "Walk Upon the Waters",
            "Raise the Dead",
            "Tame the Wild Beast",
            "Celestial Immunity",
            "Bless the Book",
            "The Sky Made Light",
        ),
        "He lived when raiders plagued Ireland, and by a miracle made the "
        "attackers' weapons useless against his flock; yet in the end he "
        "and his monks chose martyrdom when the Vikings burned their "
        "monastery.",
    ),
)


def _saints(hibernia: Hibernia) -> None:
    b = hibernia.b
    for slug, name, might, feast, veneration, patron, traits, powers, text in _SAINTS:
        new = _saint_powers(b)
        own = [new[p] for p in powers if p in new]
        others = [p for p in powers if p not in new]
        _MADE[slug] = b.creature(
            name,
            page="ch. 12",
            realm="Divine",
            might=might,
            confidence=(2, 10),
            block={**_SAINT_BLOCK, "traits": traits},
            powers=own,
            notes=paragraphs(
                text,
                f"Venerated in {veneration}; patron of {patron}. Feast: {feast}.",
                "Other powers (Realms of Power: The Divine): " + ", ".join(others) + "."
                if others
                else "",
                "Irish saints are said to take a close interest in the "
                "doings of magicians, and the Meddlesome Saint Hook "
                "(Covenants) suits a saga here.",
            ),
        )


# -- finish: homes --


def finish(hibernia: Hibernia) -> None:
    """Set each creature at its place and list it among the place's
    creatures; a saint is also listed at a church that bears the name of
    the place where it is venerated."""
    b = hibernia.b
    for slug, creature in _MADE.items():
        keys, words, region = HOMES[slug]
        place = _home(hibernia, keys, words) or hibernia.places.get(region)
        if place is None:
            place = hibernia.places.get("ireland")
        if place is not None:
            creature.place_id = place.id
            b.link(place, "creatures", creature, _ROLE.get(slug, ""))
        if creature.realm == "Divine":
            church = _church(hibernia, words)
            if church is not None:
                b.link(church, "creatures", creature, _ROLE.get(slug, ""))
    lambaird = hibernia.covenants.get("lambaird")
    if lambaird is not None and "fiorlair" in _MADE:
        b.link(
            lambaird,
            "creatures",
            _MADE["fiorlair"],
            "its magi try, so far in vain, to breed a true mare",
        )


def _home(
    hibernia: Hibernia, keys: tuple[str, ...], words: tuple[str, ...]
) -> Neighbour | None:
    """The first of `keys` a part made, else a place whose name holds one
    of `words`."""
    for key in keys:
        if key in hibernia.places:
            return hibernia.places[key]
    places = [n for n in hibernia.b.saga.neighbours if n.kind == "place"]
    for word in words:
        found = next((p for p in places if word.casefold() in p.name.casefold()), None)
        if found is not None:
            return found
    return None


def _church(hibernia: Hibernia, words: tuple[str, ...]) -> Neighbour | None:
    """A church, abbey or see whose name holds one of `words`."""
    churches = [n for n in hibernia.b.saga.neighbours if n.kind == "church"]
    for word in words:
        found = next(
            (c for c in churches if word.casefold() in c.name.casefold()), None
        )
        if found is not None:
            return found
    return None
