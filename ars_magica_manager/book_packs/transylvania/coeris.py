"""Coeris, House Tremere's seat in Maramures, as of 1220: the oppidum on
its terraced mountain, the Altar of the Standards with the Gate of
Eurydice and the City Below beneath it, the free town of Dragonesti and
the two churches raised by ritual magic, the House's hierarchy (the
Prima, her three secretaries, the legata, the exarchs) and war plans,
the Book of Legacies and its companions, and the oppidum's nine named
magi; Monica Ierne's stat block as the book prints it, and generated
stats for the other eight. In paraphrase of Against the Dark chapter
two.

Coeris is also the legal covenant of the cives, which tribunal.py's
rulings describe; the record here is the oppidum. Silexa, Monica's
familiar, is the Bestiary's. The Holy Crown is hungary.py's, described
in the Hungary place, and only its bond with Coeris is noted here.
Keys: the oppidum is covenants["coeris"]; its site places["coeris"],
the Gate places["gate_of_eurydice"], Maramures places["maramures"]
(unless another part made it), Dragonesti world["dragonesti"]."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.world import FULL
from ..builder import StatBlock, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour
    from . import Transylvania

TREMERE = "house_tremere"
TYTALUS = "house_tytalus"
MERINITA = "house_merinita"

#: The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    tribunal = transylvania.tribunal
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    places, world = transylvania.places, transylvania.world

    maramures = places.get("maramures") or next(
        (n for n in b.saga.neighbours if n.name.startswith("Maramures")), None
    )
    if maramures is None:
        maramures = b.place(
            "Maramures",
            summary=paragraphs(
                "A remote land of low, lovely mountains and deep, awkward "
                "valleys in the north-east of the Kingdom of Hungary, a "
                "natural fortress against ordinary armies. Its height makes "
                "the winters bitter and the summers almost southern. Rome "
                "never conquered it and the Church came late, so the old "
                "Dacian magic lingered here until the Founder Tremere "
                "arrived. Its forests are of oak and silver birch, and its "
                "caves yield rhodochrosite, a stone banded red, white and "
                "pink.",
            ),
            realm="Magic",
            status="Known",
            known="In the Order",
        )
    places["maramures"] = maramures

    site = places["coeris"] = b.place(
        "Coeris",
        inside=maramures,
        summary=paragraphs(
            "A mountain above a river in a valley of Maramures, carved by "
            "magic into a stair of terraces, its inside hollowed into rooms "
            "made for every purpose. The buildings outside are severe and "
            "geometric yet oddly graceful, the work of many hands over "
            "centuries with nothing that looks added on; centuries of "
            "limewash make the walls shine white, and many roofs are slates "
            "of rhodochrosite, banded red, white and pink. Every tree within "
            "a mile has been cleared, though oak and birch forest still "
            "surrounds it. The book gives no aura.",
        ),
        realm="Magic",
        status="Known",
        known="In the Order",
    )
    gate = places["gate_of_eurydice"] = b.place(
        "The Altar of the Standards and the Gate of Eurydice",
        inside=site,
        summary=secrets(
            paragraphs(
                "A cave deep under Coeris. In it is a cleft in the earth said "
                "to be the road Orpheus took to the underworld, which the "
                "Tremere call the Gate of Eurydice. Niches line the cave, "
                "one for every Tremere who has died, most holding their "
                "sigils, the Founder's among them.",
                "Asked about it, the Tremere say only that the magi who were "
                "here before the Founder took it for Orpheus's path to Hades, "
                "that they keep no Orphic rites and have no proof, and that "
                "there are many such caves.",
            ),
            paragraphs(
                "The Gate is a permanent, open way into the Magic Realm, to "
                "an insula the Tremere call the City Below: the place "
                "Coeris's people will withdraw to if the oppidum can no "
                "longer be held, almost an afterlife, though perhaps one the "
                "House could come back from once its enemies stop watching. "
                "The book gives no aura for it.",
                "A troupe may prefer another answer: a Portal to a "
                "warded cemetery far off in Africa or Asia; a fortress deep "
                "in Faerie built as a last refuge in the Sundering; a prison "
                "for Diedne magi, still alive since no one ages in the Magic "
                "Realm; or a pleasant garden where a cheerful old man named "
                "Tremere grows roses among the ghosts of his family, plays "
                "with his wolf and wonders whether his brother will call.",
            ),
        ),
        realm="Magic",
        status="Known",
        known="In the Tribunal",
        levels=[
            b.level(
                "The City Below",
                0,
                "Magic",
                enter="Through the Gate of Eurydice, which is always open.",
                notes="An insula of the Magic Realm, House Tremere's last "
                "refuge; the book gives no aura.",
            )
        ],
    )

    world["dragonesti"] = b.town(
        "Dragonesti",
        place=maramures,
        summary=paragraphs(
            "A large town a mile and a half east of Coeris. Its people are "
            "free, but own that the town stands on the wizards' land; "
            "magic made its stone walls, paved streets, sewers and wells. It "
            "feeds Coeris and sends it craftsmen, and its taxes are lighter "
            "than anywhere else in Hungary. Its folk are Christian but wary "
            "of strangers, priests included.",
        ),
        ruler="Free townsfolk on the land of Coeris",
    )
    for key, name, where in (
        ("church_dragonesti", "The church of Dragonesti", maramures),
        ("church_coeris", "The church of Coeris", site),
    ):
        world[key] = b.church(
            name,
            place=where,
            summary=paragraphs(
                "One of two splendid churches, at Coeris and in Dragonesti, "
                "raised by ritual magic to learn whether consecration would "
                "bring them down; had it, House Tremere could have turned "
                "consecration into a weapon against the Order's beloved "
                "towers. They stood, and the experiment failed. The Bishop "
                "of Transylvania appoints their priests.",
            ),
        )

    coeris = transylvania.covenants["coeris"] = b.covenant(
        "Coeris",
        tribunal=tribunal,
        founded=None,
        place=site,
        summary=SUMMARY,
        what_matters=WHAT_MATTERS,
        notes=NOTES,
        unnamed_magi=11,
        detail=FULL,
        season="Summer",
    )
    transylvania.aediles["coeris"] = ["dominic"]
    _books(transylvania, coeris)
    _magi(transylvania, coeris)
    b.link(gate, "covenants", coeris, "Coeris's refuge, beneath the oppidum")


SUMMARY = paragraphs(
    "House Tremere's seat and the place where it keeps the means to carry "
    "out its designs: the home of the Prima, who can lay hands on anything "
    "stored here the moment she judges it urgent. It is where the House's "
    "power on paper becomes strategy, and everything in its life turns, in "
    "the end, on serving a militant and ambitious House.",
    "Dacian magicians used the site long ago, their magic surviving in "
    "remote Maramures until Tremere came, killed their faerie god, burned "
    "its heart and drank its ashes mixed with wine; its priests followed him, "
    "either converted or taking it for the right ordeal of a high priest. "
    "The Hermetic oppidum began as a place for wounded Tremere to recover, "
    "on the site of the legal covenant of Asclepius. After the Sundering "
    "the Founder, no longer trusting his domus magna where Lycaneon stands, "
    "moved his seat here and kept the name; his successor Albanus turned "
    "the anger aimed at Tremere's legacy into the glue of a House remade "
    "under him.",
    "Some twenty magi live here, all Tremere save Archmagus Dominic of "
    "Tytalus and Isaac of Merinita. Five are here for a year, settling "
    "their apprentices or on rotation, and two are young magi being "
    "seasoned on missions while they wait for a lasting post abroad; the "
    "other thirteen are the core that makes the House's policy.",
)

WHAT_MATTERS = _lines(
    "Seat: the Prima of House Tremere, Poena, with her secretaries and the legata",
    "Treasury: the House's chief stores of items, vis and resources, among them the Blessings of the Dead, the talismans of Tremere who have passed",
    "Library: the Book of Legacies (most of its twelve copies), the Book of Placements and the House's official war plans",
    "Defences: layer on layer of wards, many by Hermanus after the Schism War, and more added after the House cast him out",
    "Refuge: the Gate of Eurydice in the Altar of the Standards, opening on the City Below",
    "Lands: Dragonesti, a free town on the magi's land that supplies food and craftsmen",
    "Vis: none named in the book",
    "Aura: none given in the book",
    "Tension: Monica, the legata and heir, has no wish to be Prima; the succession after Poena is unsettled",
    "Tension: House Tytalus baits the Tremere, and Dominic fears the House's patience may wear out",
    "Tension: the previous Primus is lost in the depths of the Novgorod Tribunal, with Coeris's secrets in his memory",
)

NOTES = paragraphs(
    "The hierarchy. The Prima rules from Coeris and the Praeco (Albertus, "
    "at Lycaneon, the House's manufactory and old domus magna) serves her. "
    "Under Poena work her exarchs in the other Tribunals, her councillors, "
    "her legata and three secretaries of middle age: Horatius for "
    "operations, carrying out what the last Decennial planned, with "
    "Juturnus as his troubleshooter; Janus for contingencies, the "
    "stockpiles and odd skills the House may one day need, with Angiola; "
    "and Tatiana for emergencies and spies, with Isaac. The legata, Monica "
    "Ierne, is the House's field commander and Poena's heir: if the Prima "
    "dies or is laid low she rules until an emergency council can meet. "
    "The House chooses its Primus by appointment and duel.",
    "Poena's way. Earlier Primi drove the House with a few striking "
    "projects, or left their councillors to themselves; Poena backs dozens "
    "of projects at once with House aid and has no single flagship that "
    "could fail and shake her rule. She sends a yearly letter to every "
    "Tremere and to the other Primi on the House's state and aims.",
    "Rotations and Decennials. Every Tremere should spend at least a "
    "season in ten in Transylvania, and senior Tremere meet at Coeris each "
    "decade for the Decennial, bringing young magi as aides while magi of "
    "middle age keep the House's work going. Every apprentice spends time "
    "in Transylvania, including at least a season at Coeris meeting the "
    "House's leaders, and time on the frontier; two magi often take "
    "apprentices in the same year so as to swap them.",
    "The war plans. Young Tremere are set to draw up a plan for invading a "
    "covenant of their own Tribunal, and the official plan kept at Coeris "
    "is improved by any good idea they have. The plans are named by "
    "colour: Red for taking Stonehenge and Loch Leagan, with shades such "
    "as ruby and garnet for each covenant; Blue for Normandy; White for the "
    "Alps; Black for Transylvania itself, which includes Night, a plan for "
    "taking Coeris, kept under close guard.",
    "The Earnest Sons of the Grid and Chain. A vexillation of magi and "
    "Redcaps founded by Tremere himself, which surveys the Tribunal's "
    "wilds, sends stronger magi to tame what its scouts cannot, and "
    "proposes sites for new oppida to the Prima, who has the Praeco "
    "recruit settlers, often the apprentices of the House's allies. Its "
    "reports have grown into the Book of Places to Avoid.",
    "The Holy Crown. Hungary's law, guarded by the Holy Crown, a living "
    "Divine being (see Hungary), lets the magi keep their own customs, "
    "laws and judges, and deal with mundanes through their servants; this "
    "is why Coeris can hold Dragonesti openly and tax it lightly, and why "
    "witchcraft, in Hungarian law, does not exist.",
    "Founded: the book gives no year. Of the eleven unnamed magi, five are "
    "on a year's stay, two are being seasoned, and four belong to the core "
    "of thirteen.",
    secrets(
        STORYGUIDE,
        _lines(
            "The Gate of Eurydice opens on the City Below in the Magic Realm, House Tremere's last refuge (see the Gate's place).",
            "The Night Contingency for taking Coeris is closely kept and probably salted with false information.",
            "Janus is a lycanthrope and Tatiana a Keeper of the Silence of the Temple (see their summaries).",
            "Poena may learn she has a wasting illness that will cloud her judgement, and quietly have possible successors weighed before a decisive certamen at the next Decennial.",
            "Should Poena die suddenly, Monica is Prima pro tempore while the councillors are summoned, and may use the time to finish Poena's schemes and push a few of her own.",
            "Poena plans to hold the Order's great chess competition at the Tribunal site in two years, for the House's prestige.",
        ),
    ),
)


def _books(transylvania: Transylvania, coeris: Covenant) -> None:
    b = transylvania.b
    b.book(
        coeris,
        "The Book of Legacies",
        "Other",
        description=paragraphs(
            "A huge white tome listing every item, magical or mundane, that "
            "House Tremere controls, the Blessings of the Dead among them. "
            "Only twelve copies exist and many are kept at Coeris; the "
            "others are held by the exarchs abroad, the Prima, her chosen "
            "successor and the leader of Lycaneon. Its very existence is a "
            "secret, and Poena knows every line of it.",
            "Each copy is guarded by layered defences: its case destroys "
            "the pages if the right passwords are not spoken, if it is laid "
            "on certain surfaces, or if Mentem magic cannot confirm that the "
            "one touching it is a loyal Tremere, which means lowering one's "
            "Parma to the other Mentem spells woven into it.",
        ),
    )
    b.book(
        coeris,
        "The Book of Placements",
        "Other",
        description=paragraphs(
            "The companion to the Book of Legacies: where each item is, "
            "recorded only by its number in the Book of Legacies and a "
            "number for each magus, covenant and oppidum, so a stolen copy "
            "tells a thief nothing. Some nosy Mercere have intercepted parts "
            "of it, grasped what it is, and guessed that a key like the Book "
            "of Legacies must exist. Keeping it is why no two Tremere in the "
            "Tribunal may share a name.",
        ),
    )
    b.book(
        coeris,
        "The Book of Places to Avoid",
        "Other",
        description=paragraphs(
            "The Earnest Sons of the Grid and Chain's record, compiled over "
            "centuries, of every place that resisted their survey teams and "
            "what stopped them: perhaps the longest list of places best left "
            "alone in Mythic Europe. Magi hoping to make a name as slayers of "
            "beasts or tamers of faeries write asking for a fitting "
            "challenge, and the vexillation searches it for one, an "
            "unsanctioned rite of passage for some young magi. The book does "
            "not say where it is kept; it is entered at Coeris.",
        ),
    )
    b.book(
        coeris,
        "The war plans",
        "Other",
        description=paragraphs(
            "House Tremere's official plans for invading covenants, kept at "
            "Coeris and named by colour (Red, Blue, White, Black and their "
            "shades), revised whenever a young magus's exercise plan shows a "
            "better idea. See Coeris's notes.",
        ),
    )


def _magi(transylvania: Transylvania, coeris: Covenant) -> None:
    b = transylvania.b
    m, p = transylvania.magi, transylvania.privileges
    m["poena"] = b.magus(
        "Poena",
        covenant=coeris,
        house=TREMERE,
        age=86,
        summary=paragraphs(
            "Prima of House Tremere these two years, and arguably the most "
            "powerful magus in Mythic Europe in politics: slight and stern, "
            "silver-haired, with a perfect memory. She holds every entry of "
            "the Book of Legacies in her head, knows every Tremere by name "
            "and roughly what each is doing, and fits her exarchs' and "
            "spies' reports together into elaborate designs. She favours "
            "Intellego, Muto, Imaginem and Mentem.",
            "She governs the whole House, but quietly, through her "
            "secretaries, councillors, exarchs and legata. She always wants "
            "new pieces for her plans, unlike those she has, so magi from "
            "outside the House who act predictably are valuable to her; she "
            "holds the key to the richest stores in Europe and likely knows "
            "what the player characters want, or where to find it.",
        ),
        traits={"Precise": 4, "Meticulous": 2},
    )
    p["poena"] = ("cives", "Prima of House Tremere")
    m["angiola"] = b.magus(
        "Angiola",
        covenant=coeris,
        house=TREMERE,
        age=25,
        summary=paragraphs(
            "Young, fair and sharp-tongued, a maga with the Gentle Gift whom "
            "Poena uses to speak for her to those the Gift unsettles. "
            "Trained as an Assessor, she wears strong illusions that make "
            "her seem older and male, the better to be believed, and the "
            "world grows sharper around her when she casts. She favours "
            "Muto and Imaginem, with some Creo and Mentem.",
            "She tidies up trouble between magi and mundanes in the "
            "Tribunal, so she is the one who comes when characters have "
            "badly failed among mortals, and she checks on any who pass "
            "themselves off as nobles. She is Janus's chief aide.",
        ),
        traits={"Cheerful": 3, "Assertive": 2},
    )
    p["angiola"] = ("cives", "Chief aide to the secretary for contingencies")
    m["dominic"] = b.magus(
        "Dominic of Tytalus",
        covenant=coeris,
        house=TYTALUS,
        age=90,
        summary=paragraphs(
            "Archmagus and the aedile of Coeris, a hospes: the Tytalus who "
            "has set himself to read and forestall the schemes of every "
            "other Tytalus and warn the Tremere, a deadly serious game "
            "against his whole House. He believes his House badly "
            "underrates the Tremere, who once, in the Corruption, crushed "
            "it like an egg, and fears that their patience with Tytalus "
            "baiting may give way now that the Theban Tribunal's weakness "
            "leaves them magi to spare.",
            "Very tall, black-clad down to his skullcap, with a devilish "
            "beard he knows looks overdone, which is the point; his sigil, "
            "a thunderclap, he privately finds funny. He favours weather "
            "magic and is a skilled necromancer. Close to the Prima but no "
            "Tremere, he always needs favours against some Tytalus plot and "
            "repays them with contacts, devious counsel and necromantic "
            "mayhem. Leontine of Tytalus of Old Histria is his protégé.",
        ),
        traits={"Fascinated by complex things": 4, "Patient": 3},
    )
    p["dominic"] = ("hospites", "")
    m["horatius"] = b.magus(
        "Horatius",
        covenant=coeris,
        house=TREMERE,
        age=61,
        summary=paragraphs(
            "Secretary for operations, seeing through what the last "
            "Decennial planned; under some Primi this post was mighty, but "
            "Poena's own grip on resources leaves him less, and he keeps "
            "things running and reports what goes wrong. Young for so high a "
            "post and plump for a Tremere, he worked beside Poena before her "
            "rise, helped arrange her succession, and is her husband's "
            "brother. A Signaler by training with his own sigil, comforting "
            "warmth; he favours Creo, Rego, Imaginem and Terram.",
            "He seldom leaves Coeris, but magi abroad write to him with "
            "proposals, as the manager of House business; he is easier to "
            "reach than Poena and can arrange to see her. He does not seek "
            "the Primacy but would be a fine compromise if the House split, "
            "and would ring the north and east shores of the Black Sea with "
            "oppida to make it a Hermetic lake.",
        ),
        traits={"Organized": 4, "Wants to cut a deal": 3},
    )
    p["horatius"] = ("cives", "Secretary for operations")
    m["janus"] = b.magus(
        "Janus",
        covenant=coeris,
        house=TREMERE,
        age=91,
        summary=secrets(
            paragraphs(
                "Secretary for contingencies: he keeps the House's "
                "stockpiles and asks for Tremere, or magi of the oppida, to "
                "be trained in odd skills in case one of his unlikely "
                "events comes to pass. Raised in the Rhineland, muscular "
                "and handsome, chaste and aloof with attractive women; his "
                "sigil is ribbons of scarlet light. He favours Creo, "
                "Intellego, Rego and above all Mentem, a well-known "
                "speciality that weakens him in certamen, and is a "
                "spiritual necromancer with a gift for spycraft and the "
                "Visions Flaw. He was secretary for operations under the "
                "previous Primus.",
                "He watches characters whose doings might, however "
                "remotely, start a crisis, and quietly sets counterweights; "
                "years later he may call on skills he had them learn, to "
                "untangle a crisis born of several unlikely chances at "
                "once.",
            ),
            "Janus suffers a lycanthropy that magic can hold back and that "
            "changes only his shape, not his mind. He is ashamed of it and "
            "keeps it secret, so he will never seek the Primacy, and it "
            "passes by intercourse, hence his coldness to women.",
        ),
        traits={"Chaste": 3, "Secretive": 2, "Proud": 1},
    )
    p["janus"] = ("cives", "Secretary for contingencies")
    m["isaac"] = b.magus(
        "Isaac of Merinita",
        covenant=coeris,
        house=MERINITA,
        age=None,
        summary=paragraphs(
            "Coeris's expert on faeries, a cives, left deeply disturbed if "
            "not mad by the Tribunal's dark faeries; his mood swings from "
            "cheer to gloom without warning. He looks forty but has spent "
            "years in Faerie, so his true age is unknown. His skewed view and "
            "his hatred and vast knowledge of vampiric faeries make him "
            "Tatiana's adviser; she values his knack for surviving anything, "
            "if not always whole. He prefers gloomy faerie magic.",
            "Frail-looking, yet his faerie blood makes him strong and "
            "nimble. Scars as if torn by madmen's teeth mark his wrists, "
            "ankles, neck and thighs, which Hermetic magic cannot heal, from "
            "a faerie curse or torture that harmed his Essential Nature. His "
            "sigil is the smell of burning pine cones, though he says it "
            "was not always so.",
        ),
        traits={"Manic Depressive": 3},
    )
    p["isaac"] = ("cives", "")
    m["juturnus"] = b.magus(
        "Juturnus",
        covenant=coeris,
        house=TREMERE,
        age=45,
        summary=paragraphs(
            "Horatius's troubleshooter, sent to find out why something in "
            "the House's operations went wrong and to put it right. Cocky, "
            "skilled and quick to violence, he is unlike a bureaucratic "
            "Tremere and may have risen too fast. Small objects near him "
            "arrange themselves into geometric shapes. He favours Rego, with "
            "some Perdo and Intellego, Animal and Terram.",
            "He is black and athletic; decades ago a Primus had the Redcaps "
            "find Gifted Arab and African children, thinking they could "
            "work less conspicuously in Arab lands, and he was one of them. "
            "Like many he trained first as an Assessor, a kind of spy, and "
            "has since learnt more widely. The book gives no privilege for "
            "him.",
        ),
        traits={"Cocksure": 3, "Eloquent": 2},
    )
    p["juturnus"] = ("", "Troubleshooter for the secretary for operations")
    m["tatiana"] = b.magus(
        "Tatiana",
        covenant=coeris,
        house=TREMERE,
        age=85,
        summary=secrets(
            paragraphs(
                "Secretary for emergencies and Poena's spymistress: she "
                "warns the House of trouble ahead and finds answers when it "
                "is caught off guard. Of a Szekler family she has not seen "
                "since her apprenticeship; she turns briefly invisible "
                "whenever she casts, to her irritation. She favours Creo, "
                "Muto, Herbam and Corpus, and Isaac assists her.",
                "She appears when something dreadful is close, takes over "
                "the characters' help and resources, and sends them into the "
                "worst of it to buy the House and Order time; magi who "
                "refuse her are tarnished for good in some circles.",
            ),
            "Tatiana secretly belongs to the Keepers of the Silence of the "
            "Temple, a small, unofficial society named for the man who burnt "
            "the temple of Artemis at Ephesus to be famous and whose name "
            "was then forbidden. They hold that Tytalus magi too often do "
            "monstrous, foolish things for fame, and set out to destroy such "
            "vandals, then their memory.",
        ),
        traits={"Ruthless": 3, "Calm": 2},
    )
    p["tatiana"] = ("cives", "Secretary for emergencies")
    m["monica"] = b.magus(
        "Monica Ierne",
        covenant=coeris,
        house=TREMERE,
        age=90,
        summary=paragraphs(
            "Archmaga and legata, the House's field commander since Poena "
            "became Prima two years ago, and so her heir, who would act as "
            "Prima until an emergency council could meet. Raised at "
            "Blackthorn in England and marked from her first training as one "
            "of the House's heavy war-magi, she specialises in Creo, Rego, "
            "Terram and Corpus. Dark-haired and pale, with an athletic build "
            "rare in noblewomen; her sigil is flint. She holds her own sigil "
            "and Tatiana's. Her familiar is the wolf Silexa.",
            "She comes into play whenever the House takes the field, though "
            "she often names another to command for her. She may ask "
            "characters to survey land as battlefields or staging grounds, "
            "and wants every detail of their fights with hedge magi, demons, "
            "faeries and stranger things. She does not want the Primacy and "
            "would take it only to keep out someone odious; if she did, she "
            "would have the Primus chosen by duel of champions and then "
            "step down for someone better at governing.",
        ),
        traits={
            "Loves reading about combat": 3,
            "Loyalty (wolf)": 3,
            "Enjoys sailing": 2,
        },
    )
    p["monica"] = ("cives", "Legata of House Tremere")


# --------------------------------------------------------- printed stats

MONICA: StatBlock = {
    "characteristics": {
        "intelligence": 2,
        "perception": 0,
        "presence": 0,
        "communication": 1,
        "strength": 0,
        "stamina": 2,
        "dexterity": 0,
        "quickness": 0,
    },
    "size": 0,
    "confidence": (3, 3),
    "decrepitude": (0, 0),
    "warping": (6, 10),
    "apparent_age": 55,
    "virtues_flaws": [
        "The Gift",
        ("Affinity with {art}", {"art": "terram"}),
        "Clear Thinker",
        "Leadworker",
        ("Minor Magical Focus", {"focus": "certamen"}),
        "True Friend",
        ("Deficient Technique", {"technique": "muto"}),
    ],
    "traits": {
        "Loves reading about combat": 3,
        "Loyalty (wolf)": 3,
        "Enjoys sailing": 2,
    },
    "reputations": {"Combat maga (Hermetic)": 5},
    "abilities": [
        ("Area Lore: Hibernian Tribunal", 2, "western coast"),
        ("Area Lore: Transylvanian Tribunal", 3, "oppida"),
        ("Artes Liberales", 1, "writing"),
        ("Athletics", 2, "marching"),
        ("Awareness", 3, "faeries"),
        ("Bargain", 2, "magi"),
        ("Brawl", 1, "self-defense"),
        ("Charm", 1, "magi"),
        ("Craft: Flintworking", 3, "blades"),
        ("Code of Hermes", 2, "Transylvanian Tribunal"),
        ("Concentration", 4, "Terram"),
        ("Etiquette", 2, "magi"),
        ("Finesse", 6, "Terram"),
        ("Folk Ken", 2, "Transylvania"),
        ("Organization Lore: Order of Hermes", 3, "specializations of magi"),
        ("Living Language: Irish", 5, "peasants"),
        ("Dead Language: Latin", 6, "magi"),
        ("Leadership", 3, "magi"),
        ("Magic Theory", 4, "Terram"),
        ("Organization Lore: House Tremere", 4, "resources"),
        ("Parma Magica", 9, "faeries"),
        ("Penetration", 8, "Terram"),
        ("Survival", 2, "Transylvania"),
        ("Swim", 1, "endurance"),
    ],
    "arts": {
        "Creo": 12,
        "Intellego": 6,
        "Muto": 6,
        "Perdo": 6,
        "Rego": 24,
        "Animal": 10,
        "Aquam": 0,
        "Auram": 12,
        "Corpus": 6,
        "Herbam": 0,
        "Ignem": 0,
        "Imaginem": 0,
        "Mentem": 0,
        "Terram": 30,
        "Vim": 0,
    },
    "spells": [
        ("Commanding the Harnessed Beast", "ReAn", 30, 0),
        ("Ward Against Rain", "ReAq", 10, 0),
        ("Circling Winds of Protection", "CrAu", 20, 1),
        ("The Incantation of Lightning", "CrAu", 35, 1),
        ("Whispering Winds", "InAu", 15, 0),
        ("Broom of the Winds", "ReAu", 15, 0),
        ("Gathering of the Stormy Might", "ReAu", 40, 0),
        ("The Chirurgeon's Healing Touch", "CrCo", 20, 0),
        ("Restoration of the Defiled Body", "CrCo", 25, 0),
        ("The Leap of Homecoming", "ReCo", 35, 1),
        ("Heat of the Searing Forge", "CrIg", 10, 0),
        ("Pilum of Fire", "CrIg", 20, 1),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Scent of Peaceful Slumber", "ReMe", 20, 0),
        ("Wall of Protecting Stone", "CrTe", 25, 1),
        ("Necessary Monolith", "CrTe", 35, 0),
        ("Sense the Feet that Tread the Earth", "InTe", 30, 0),
        ("Stone Tell of the Mind that Sits", "InTe", 30, 0),
        ("Stone to Falling Dust", "PeTe", 20, 2),
        ("Wielding the Invisible Sling", "ReTe", 10, 3),
        ("The Unseen Porter", "ReTe", 10, 0),
        ("The Earth's Carbuncle", "ReTe", 15, 0),
        ("Hands of the Grasping Earth", "ReTe", 15, 0),
        ("Crest of the Earth Wave", "ReTe", 20, 0),
        ("Abrading Stones", "ReTe", 25, 0),
        ("Earth Shock", "ReTe", 30, 0),
        ("The Earth Split Asunder", "ReTe", 30, 0),
        ("Creeping Chasm", "ReTe", 35, 0),
        ("Sudden Well", "PeTe", 30, 0),
        ("The Field of Millstones", "ReTe", 40, 0),
        ("Diverting the River", "ReTe", 50, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
        ("Circular Ward Against Demons", "ReVi", 20, 0),
        ("Watching Ward", "ReVi", 25, 0),
    ],
    "masteries": {
        "Circling Winds of Protection": ["Fast Casting"],
        "The Incantation of Lightning": ["Fast Casting"],
        "The Leap of Homecoming": ["Fast Casting"],
        "Pilum of Fire": ["Fast Casting"],
        "Wall of Protecting Stone": ["Fast Casting"],
        "Stone to Falling Dust": ["Fast Casting", "Penetration"],
        "Wielding the Invisible Sling": [
            "Fast Casting",
            "Multiple Casting",
            "Penetration",
        ],
    },
    "notes": paragraphs(
        "Stat block printed in Against the Dark, chapter two. Age 90, "
        "looking 55. Perception is left blank in the book and entered as 0. "
        "Soak +5 (Stamina and a bronze cord); Encumbrance 0. Combat: with a "
        "club, Init +1, Atk +5, Dfn +6, Dam +3; brawling, Init 0, Atk +1, "
        "Dfn +2, Dam 0. Hermes Lore 3 is entered as Organization "
        "Lore: Order of Hermes.",
        "Leadworker lets her make small lead dolls or tablets that are "
        "arcane connections to the dead, or to animals that know their own "
        "names, and fix arcane connections without vis or lost study; she "
        "carries hundreds. The book lists no Flaw beyond Deficient Technique "
        "(Muto) and does not name her rank's Virtue.",
        "Spells as the book lists them: Sudden Well appears there as ReTe "
        "35 but is written up as PeTe 30, which the catalog holds; Creeping "
        "Chasm is listed at 35; Gathering of the Stormy Might and Earth "
        "Shock are favourites to follow Sudden Well or Creeping Chasm. "
        "Necessary Monolith dams a river so that Diverting the River has "
        "water to turn; the chasm it cuts can also ring a camp in defensive "
        "circles nearly two miles across.",
        "Equipment: a thigh case of flint spikes, slung with Wielding the "
        "Invisible Sling when nothing better is to hand, some dipped in "
        "arsenic and sealed with beeswax; the case is itself enchanted and "
        "keeps arsenic off its wearer. Several magic items from the House "
        "stores, the strongest a dragon banner whose pole was an "
        "archmagus's staff.",
        "Talisman: a flint wand bound in bronze, with attunements for "
        "paralysis (+9), protection from faeries (+6), control, destruction "
        "and missiles at a distance, Ignem and Terram. Its effects, each 24 "
        "uses a day: The Earth Split Asunder (ReTe 35, holds concentration); "
        "Endurance of the Berserkers at Touch (ReCo 30); the Invisible Siege "
        "Engine, a Sling for things up to three feet across (ReTe 15), and "
        "a second copy with +20 Penetration; Object of Increased Size (MuTe "
        "20); Obliteration of the Metallic Barrier (PeTe 25); Sense the "
        "Feet that Tread the Earth and Stone Tell of the Mind that Sits "
        "(InTe 40 each, holding concentration); and Wings of the Soaring "
        "Wind (Cr(Re)Au 40).",
        "Familiar: Silexa, a wolf of Irish stock with the colour of flint, "
        "senior among the wolves bound to House Tremere (see the Bestiary). "
        "Through their bond Monica shares her sight, speaks mind to mind, "
        "and can call her from up to seven leagues; Silexa often fetches "
        "arcane connections to places for The Leap of Homecoming.",
    ),
}


# --------------------------------------------------------- generated stats

P = Profile
HUNGARIAN = "Hungarian"
TREMERE_LORE = "Organization Lore: House Tremere"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: The magi of Coeris the book sketches without a stat block.
PROFILES: dict[str, Profile] = {
    "poena": P(
        strong="int per com",
        weak="str dex",
        arts={"In": 9, "Mu": 7, "Im": 7, "Me": 9, "Re": 4, "Vi": 3},
        abilities={
            "Intrigue": (6, "House Tremere"),
            "Leadership": (5, "Tremere"),
            TREMERE_LORE: (6, "resources"),
            "Folk Ken": (4, "magi"),
            "Code of Hermes": 4,
            "Organization Lore: Order of Hermes": 3,
        },
        virtues=[
            "Magical Memory",
            "Hermetic Prestige",
            "Dutybound",
            "Driven (Minor)",
        ],
        native=HUNGARIAN,
    ),
    "angiola": P(
        strong="pre com int",
        arts={"Mu": 8, "Im": 9, "Cr": 4, "Me": 5},
        abilities={
            "Etiquette": (4, "nobles"),
            "Guile": (4, "disguise"),
            "Folk Ken": (3, "nobles"),
            "Charm": 3,
            "Intrigue": 2,
        },
        virtues=[
            "Gentle Gift",
            "Dutybound",
            "Overconfident (Minor)",
            "Driven (Minor)",
        ],
        native="Italian",
    ),
    "dominic": P(
        strong="int per pre",
        arts={"Au": 9, "Cr": 5, "Re": 6, "Me": 7, "Co": 5, "Pe": 5, "Vi": 3},
        abilities={
            "Intrigue": (6, "House Tytalus"),
            "Organization Lore: House Tytalus": (5, "schemes"),
            "Magic Lore": (4, "ghosts"),
            "Guile": 3,
            "Code of Hermes": 3,
        },
        virtues=[
            "Large",
            ("Social Contacts", {"group": "House Tytalus"}),
            "Obsessed (Minor)",
            "Proud (Minor)",
        ],
        native=HUNGARIAN,
    ),
    "horatius": P(
        strong="int com pre",
        weak="qik dex",
        arts={"Cr": 7, "Re": 8, "Im": 5, "Te": 6, "In": 3},
        abilities={
            "Leadership": (5, "administration"),
            "Bargain": (5, "magi"),
            TREMERE_LORE: (5, "operations"),
            "Intrigue": 3,
            "Area Lore: Black Sea": 2,
        },
        virtues=["Hermetic Prestige", "Close Family Ties", "Dutybound"],
        native=HUNGARIAN,
    ),
    "janus": P(
        strong="int sta per",
        arts={"Cr": 6, "In": 7, "Re": 6, "Me": 10, "Co": 3},
        abilities={
            "Guile": (5, "spycraft"),
            "Awareness": (4, "watching"),
            "Folk Ken": (4, "magi"),
            TREMERE_LORE: (5, "stockpiles"),
            "Magic Lore": (3, "ghosts"),
            "Stealth": 2,
        },
        virtues=["Premonitions", "Lycanthrope", "Visions"],
        native="High German",
    ),
    "isaac": P(
        strong="dex qik per",
        weak="pre com",
        arts={"Im": 7, "Me": 7, "Pe": 6, "Vi": 6, "Mu": 4, "An": 3},
        abilities={
            "Faerie Lore": (6, "vampiric faeries"),
            "Faerie Magic": (4, "glamour"),
            "Athletics": 3,
            "Survival": 2,
        },
        virtues=[
            ("Faerie Blood", {"blood": "unknown"}),
            "Depressed",
            "Disfigured",
        ],
        age=40,
        native=HUNGARIAN,
    ),
    "juturnus": P(
        strong="qik dex com",
        arts={"Re": 8, "Pe": 4, "In": 4, "An": 6, "Te": 6},
        abilities={
            "Brawl": (4, "dodging"),
            "Guile": (4, "lying to magi"),
            "Stealth": (3, "towns"),
            "Athletics": 3,
            "Living Language: Hungarian": 4,
        },
        virtues=["Foreign Upbringing", "Overconfident (Minor)", "Reckless (Minor)"],
        native="Arabic",
    ),
    "tatiana": P(
        strong="int per pre",
        arts={"Cr": 8, "Mu": 7, "He": 6, "Co": 7, "In": 3},
        abilities={
            "Intrigue": (5, "spies"),
            "Folk Ken": (4, "magi"),
            "Leadership": (4, "in a crisis"),
            TREMERE_LORE: 4,
            "Area Lore: Transylvania": 2,
        },
        virtues=["Hermetic Prestige", "Dutybound", "Secretive"],
        native=HUNGARIAN,
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Monica Ierne's printed stat block, then generated stats for the
    other magi of Coeris."""
    b = transylvania.b
    b.stats(transylvania.magi["monica"], MONICA)
    for key, profile in PROFILES.items():
        apply(b, transylvania.magi[key], profile)


def finish(transylvania: Transylvania) -> None:
    """Put Maramures in the Kingdom of Hungary when this part made it, and
    tie the churches to the Bishop of Transylvania, once hungary.py has
    built them."""
    maramures = transylvania.places["maramures"]
    hungary = transylvania.places.get("hungary")
    if maramures.place_id is None and hungary is not None:
        maramures.place_id = hungary.id
    bishop = _bishop(transylvania)
    if bishop is not None:
        for key in ("church_dragonesti", "church_coeris"):
            transylvania.world[key].answers_to = bishop.id


def _bishop(transylvania: Transylvania) -> Neighbour | None:
    for neighbour in transylvania.world.values():
        name = neighbour.name.casefold()
        if neighbour.kind == "church" and "bishop" in name and "transylvania" in name:
            return neighbour
    return None
