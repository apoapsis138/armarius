"""The Bestiary (ch03, ch08, ch09): the four creature blocks Sanctuary of
Ice prints, converted from the Fourth Edition (A19).

Hera, the Cave's ghost autocrat (Magic Might 65, the block's figure, not
the text's 45); Jane, the Fifth Primus, for the spectral Primi (Magic
Might 75 in a pool all the Primi share); the barbegazi, the snow gnomes
(Faerie Might 5, as the dwarf of RoP:F pp. 96-97; 20 as printed); and Crucifixo, Andru's cat, whose Familiar record
stats_magi.py rebuilds by the Definitive Edition's rules.

The conversion, by fourth.py's rules for creatures: Characteristics as
printed; Abilities renamed to the Definitive Edition's; Confidence at the
Definitive Edition's baseline for important creatures (a Score of 1 and 3
Points, DE p. 426), not the old 9. Beings the book names with no stats (Mircalla, the Tatzelwurmli,
Pilate's ghost, the Dachstein giants, the Fanes, the blizzard demons,
the folly spirits, the basilisks) are in their places' summaries.

Keys: creatures["hera"], ["jane"], ["barbegazi"] and ["crucifixo"]."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import characteristics, paragraphs

if TYPE_CHECKING:
    from .state import Alps

#: A person's Fatigue levels.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)


def build(alps: Alps) -> None:
    _ghosts(alps)
    _barbegazi(alps)
    _crucifixo(alps)


def _ghosts(alps: Alps) -> None:
    b, places = alps.b, alps.places
    axis = places.get("axis_magica")
    alps.creatures["hera"] = b.creature(
        "Hera, Autocrat of the Cave",
        page="p. 37",
        realm="Magic",
        might=65,
        form="Mentem",
        place=axis,
        level=1,
        confidence=CONFIDENCE,
        age="Centuries; looks about sixty-five, her age at death",
        block={
            "characteristics": characteristics(3, 1, 2, 2, 0, 0, 1, 1),
            "virtues_flaws": ["Wise One", "Piercing Gaze"],
            "abilities": [
                ("Awareness", 6, "things out of place in the covenant"),
                ("Bargain", 9, "with Criamon magi"),
                ("Chirurgy", 3, "magical injuries"),
                ("Area Lore: the Cave of Twisting Shadows", 9, "history"),
                ("Enigmatic Wisdom", 3, "the Primi's succession"),
                ("Etiquette", 5, "covenfolk"),
                ("Faerie Lore", 3, "the Alps"),
                ("Finesse", 9, "telekinesis"),
                ("Folk Ken", 6, "her covenant"),
                ("Guile", 6, "detecting forgeries"),
                ("Area Lore: Greater Alps Tribunal", 6, "the covenants' history"),
                ("Code of Hermes", 5, "House Criamon"),
                ("Organization Lore: Order of Hermes", 6, "history"),
                ("Organization Lore: House Criamon", 9, "history"),
                ("Leadership", 3, "in a crisis"),
                ("Magic Lore", 3, "dream spirits"),
                ("Infernal Lore", 6, "detecting diabolists"),
                ("Philosophiae", 3, "historical trivia"),
                ("Artes Liberales", 6, "instructions"),
                ("Dead Language: Latin", 6, "with magi"),
                ("Living Language: Romansch", 6, "covenfolk"),
            ],
            "traits": {"Faithful to Criamon": 5, "Desires Rest": 2},
            "reputations": {
                "Always knows what you will say (covenfolk)": 2,
                "First servant of the House (Criamon magi)": 3,
            },
        },
        attacks=[b.attack("Fist, in her magical gloves", 1, -1, 1, 0)],
        soak=0,
        fatigue_levels=FATIGUE,
        tires=False,
        powers=[
            b.power(
                "Mementos",
                0,
                1,
                "Terram",
                rtd=("Touch", "Concentration", "Individual"),
                level=10,
                does="Handles the things she loved in life as if alive. Her "
                "gloves make it needless, but most strong ghosts have it.",
            ),
            b.power(
                "Unquiet Spirit",
                1,
                0,
                "Terram",
                rtd=("Voice", "Momentary", "Individual"),
                level=25,
                does="Flings things with her thoughts: in the Cave, up to 250 "
                "pounds as far as 100 paces, lighter things falling straight "
                "down at the edge of its reach; landing one precisely is a "
                "targeting roll, +2 to hit a man-sized target with a small "
                "object. ReTe with Animal, Aquam, Corpus or Herbam requisites "
                "for what she throws.",
            ),
        ],
        appearance="Tall and lean, dark-haired and speckled with grey, with "
        "very dark eyes; her magic is so strong that, when she wishes, she "
        "seems entirely solid. She may look any age from her life.",
        equipment="Pale grey leather gloves that let her handle things; an "
        "elaborate galena chatelaine whose keys, material, magical, spectral "
        "and illusory, open every lock in the covenant and more.",
        notes=paragraphs(
            "The Cave's autocrat, appointed by Criamon himself, who bound her "
            "to the place of her death, poisoned, to care for his children "
            "until the Enigma is solved; she is no genius loci. She cares "
            "chiefly for the Enigma's completion, which is easy to forget, as "
            "it so often means seeing to everyone's comfort; those who know it "
            "bargain with her better. She can be hurt only by Mentem or Vim "
            "magic, and will never possess anyone, which breaks her faith.",
            "Converted: the block's Destiny (to serve the final Criamon "
            "magus) has no Definitive Edition Virtue and is kept here; "
            "Craft (many) 3 is left out; Forgery 6 is Guile, the better of "
            "the two; Confidence 9 is the Definitive Edition's baseline. "
            "The text gives her Might as 45 adjusted by the aura; the block's "
            "65 stands (A19).",
        ),
        can_be_wounded=False,
    )
    alps.creatures["jane"] = b.creature(
        "Jane, the Fifth Primus",
        page="p. 38",
        realm="Magic",
        might=75,
        form="Vim",
        place=axis,
        level=8,
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(3, -1, 3, 1, 0, 0, 0, -2),
            "traits": {"Devoted to the House": 5, "Cheerful": 1},
            "reputations": {
                "Will mark the coming of the New Criamon (some Criamon magi)": 2
            },
        },
        soak=0,
        tires=False,
        can_be_wounded=False,
        powers=[
            b.power(
                "Poltergeist",
                3,
                -5,
                "Terram",
                rtd=("Voice", "Concentration", "Group"),
                level=15,
                does="Moves things of extraordinary weight anywhere in the aura, "
                "a Might point a magnitude of Target; she seems to touch what "
                "she moves. Nothing in the aura less than a year can be moved, "
                "though she can push it with other things.",
            ),
            b.power(
                "The Primi's Magic",
                0,
                -2,
                "Vim",
                does="Casts any spontaneous spell up to level 25 and any "
                "formulaic spell she knows up to level 60, at 1 Might point a "
                "magnitude; she earns no Twilight. Points spent come back to "
                "the Primi when a new Primus joins them. She knows every Vim "
                "and Mentem spell of the core rules to level 60 and many spells "
                "to level 25 of other Forms.",
            ),
        ],
        notes=paragraphs(
            "The youngest of the past Primi who knew Criamon in life, looking "
            "about thirty: friendly and approachable, she often offers to "
            "tutor outsiders who come to the Cave. Some Criamon believe the "
            "Primi will vanish in order shortly before a new Criamon takes "
            "the Founder's place, and that Jane will be the last to go. Her "
            "block stands for every spectral Primus: their 75 Might is one "
            "pool, so points one spends are gone from all.",
            "Sanctuary of Ice makes the slain Primi genii loci bound to the "
            "Axis Magica, harmed only by Vim magic and never truly in solid "
            "form; Houses of Hermes: Mystery Cults calls them ghosts of past "
            "Primi who serve in place of a library and will one day enter the "
            "Hypostasis. The block is recorded as printed, with Confidence at "
            "the Definitive Edition's baseline. She never possesses anyone: "
            "the Primi think taking on matter like swimming through sewage.",
        ),
    )


def _barbegazi(alps: Alps) -> None:
    b = alps.b
    alps.creatures["barbegazi"] = b.creature(
        "Barbegazi",
        page="p. 105",
        realm="Faerie",
        might=20,
        form="Terram",
        size=-2,
        how_many="Bands, in tunnels under the snow of high peaks",
        place=alps.places.get("pilatus"),
        block={
            "characteristics": characteristics(2, 4, -1, 0, 2, 5, 3, 2),
            "traits": {"Sense of justice": 3, "Sense of mischief": 2},
        },
        soak=15,
        fatigue_levels="OK, -1, -5, Incapacitated",
        powers=[
            b.power(
                "Bury in Snow",
                3,
                -1,
                "Auram",
                rtd=("Voice", "Diameter", "Group"),
                level=25,
                does="A snowstorm that buries the gnomes and their enemies: "
                "the book's Control Auram 8, fixed as a Greater Power, as "
                "their Might follows their role.",
            ),
            b.power(
                "Shake the Mountain",
                3,
                -1,
                "Terram",
                rtd=("Voice", "Momentary", "Group"),
                level=25,
                does="Brings snow and rock down on those below: the book's "
                "Control Terram 8, fixed as a Greater Power.",
            ),
            b.power(
                "Faerie Gifts",
                2,
                0,
                "Terram",
                does="Enchants small objects, as the Fourth Edition's Faeries "
                "describes: the cheese one gave a poor girl of Lucerne turned "
                "to gold.",
            ),
        ],
        vis=[
            BodyVis(
                2,
                "Terram",
                "one pawn in each great foot; its Art is whatever the gnome was doing when killed",
            )
        ],
        appearance="Small blue gnomes, always male, with icicles in their "
        "beards and huge feet they use as skis or to dig through snow.",
        notes=paragraphs(
            "They keep above the tree line and sleep through the summer, and "
            "live through much of western Europe in tunnels on peaks that are "
            "always snow-capped; their name probably means icicle beards. "
            "They shun melee, fighting with the weather. Mundane cold and "
            "metal weapons cannot hurt them; the block's Soak +10 is Stamina "
            "plus 10. Carlo of Journeys End has their features.",
            "The Lucerne girl's tale: sent to beg from her uncle for her sick "
            "mother, she was refused even the rind of his cheese, and met a "
            "barbegazi who gave her healing herbs and a cheese that became "
            "gold; that night an avalanche buried the uncle and filled his "
            "fields with stones.",
        ),
    )


def _crucifixo(alps: Alps) -> None:
    b = alps.b
    alps.creatures["crucifixo"] = b.creature(
        "Crucifixo",
        page="p. 86",
        realm="Magic",
        might=10,
        form="Animal",
        size=0,
        place=alps.places.get("valnastium_valley"),
        cunning=False,
        block={
            "characteristics": characteristics(3, 3, 0, 1, -3, 0, 3, 3),
            "abilities": [
                ("Artes Liberales", 1, "logic"),
                ("Athletics", 6, "chasing humans"),
                ("Awareness", 2, "food"),
                ("Bargain", 1, "magi"),
                ("Brawl", 1, "with cats"),
                ("Charm", 3, "people who like cats"),
                ("Civil and Canon Law", 1, "what Andru thinks aloud"),
                ("Concentration", 2, "outstaring people"),
                ("Etiquette", 1, "whom to claw"),
                ("Faerie Lore", 1, "edibility"),
                ("Finesse", 1, "bond powers"),
                ("Folk Ken", 6, "where the food is"),
                ("Area Lore: Greater Alps Tribunal", 4, "cat familiars"),
                ("Guile", 1, "covenfolk"),
                ("Code of Hermes", 1, "familiars"),
                ("Organization Lore: House Jerbiton", 2, "life in Valnastium"),
                ("Hunt", 4, "small edible things"),
                ("Intrigue", 1, "cats"),
                ("Leadership", 1, "cats"),
                ("Magic Lore", 3, "the Urbastis cult"),
                ("Infernal Lore", 2, "cats"),
                ("Organization Lore: Order of Hermes", 4, "cat familiars"),
                ("Philosophiae", 1, "natural"),
                ("Music", 1, "caterwauling"),
                ("Dead Language: Latin", 5, "magi"),
                ("Living Language: Greek", 4, "magi"),
                ("Survival", 3, "round Valnastium"),
                ("Stealth", 6, "hunting"),
                ("Theology: Christian", 1, "Andru's favourite stories"),
            ],
            "traits": {"Curious": 3},
        },
        attacks=[b.attack("Claws and teeth", 5, 5, 7, -3)],
        soak=0,
        fatigue_levels="OK, -3, Unconscious",
        vis=[BodyVis(1, "Mentem", "in his body")],
        appearance="A small aristocratic black cat (Houses of Hermes: "
        "Societates p. 52; Sanctuary of Ice spells him Crucifixio).",
        notes=paragraphs(
            "Andru's familiar, of the Black Lineage: so many Valnastium magi "
            "have kept black cats as familiars that a magical strain of them "
            "lives in the valley. He could talk before he was bound, and is "
            "not the lineage's most senior cat, though his tie to the Primus "
            "will speed his rise. His Scribe Latin 5 (he reads, but cannot "
            "write) is Artes Liberales and Latin here. The book's Size 0 is "
            "kept.",
        ),
    )
