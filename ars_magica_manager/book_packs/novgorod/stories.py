"""The saga's stories, in paraphrase (N17): each a threat whose stages lay
out what the book says may come of it.

Under way in 1220: the trial of Pripet Maior at the meeting of 1221
(world["threat_trial"]), Mikhail of Turov's draining of the marsh
(["threat_drainage"]), Malincka's race to finish her spell before the
meeting (["threat_malincka"]) and the revived cult of Hermes with the
girl Stenya (["threat_hermes"]).

Dormant until the storyguide begins them: Yannes Kolski's vanishing
(["threat_yannes"]), Stolitzya the Swimmer (["threat_stolitzya"]),
Zashya's secret granddaughter (["threat_zashya"]), Leczyca against the
Rhine (["threat_rhine"]), the Gathering of 1227 (["threat_gathering"])
and Durenmar's motion at the Grand Tribunal of 1228
(["threat_durenmar"]).

The Mongols are east.py's shared world["mongol_conquest"], whose stages
this pack's book extends into Russia and Poland (N14)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .. import east
from ..builder import Builder, dormant, paragraphs

if TYPE_CHECKING:
    from ..records import Records

S = Builder.stage
DATED = "Fixed dates"


def build(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    w["mongol_conquest"] = east.mongol_conquest(b, place=p.get("steppe"))
    w["threat_trial"] = b.threat(
        "The Trial of Pripet Maior",
        place=p.get("three_lakes_site"),
        summary=paragraphs(
            "The raid of 1217 cannot go unpunished, yet Pripet Maior ignores "
            "every summons, Casimi Ljech is all but ungovernable, Crintera "
            "will not force the magi to come, and too many of the "
            "Tribunal's magi owe Pripet old loyalties. The meeting of 1221 "
            "must try it, and Thousand Caves too, with the Grand Tribunal "
            "of 1228 and the Rhine watching for a scandal.",
        ),
        antagonist="Pripet Maior's defiance",
        moves=DATED,
        stages=[
            S(
                "The meeting of 1221",
                year=1221,
                season="Summer",
                clues="Magi canvass Three Lakes; Lelya Danichev practises "
                "certamen; Pripet's magi may or may not come.",
                ignored="The Tribunal fails to act, Pripet Maior grows bolder, "
                "and House Bjornaer's quarrel goes to the Gathering.",
                stopped="Pripet Maior is fined, its magi bound to the peace, or "
                "a Wizard's March is declared on Casimi.",
                turned="A troupe that brings Pripet Maior to Three Lakes, or "
                "Casimi to heel, sways the verdict.",
            ),
        ],
    )
    w["threat_drainage"] = b.threat(
        "Draining the Pripet",
        place=p.get("pripet_marsh"),
        summary=paragraphs(
            "Mikhail of Turov has hunted the marsh's monsters, talked of "
            "Norwegian harpoonists, and now means to dig canals to the "
            "Pripet and drain the land for pasture, crushing anyone who "
            "objects. The army that digs will meet Pripet Maior's raids "
            "and hauntings, and if he finds proof of magic he may call the "
            "Church. Crintera will claim Pripet's legacy if it falls.",
        ),
        antagonist="Mikhail of Turov",
        position=1,
        stages=[
            S(
                "The diggers arrive",
                at=2,
                clues="Surveyors on the marsh's southern edge; levies "
                "gathered at Turov.",
                ignored="Pripet Maior strikes the diggers; men die, and "
                "Mikhail sends for priests and harpoonists.",
            ),
            S(
                "War in the marsh",
                at=4,
                clues="Stories of beasts that fight like men and men who "
                "turn into beasts.",
                ignored="Pripet Maior is exposed or destroyed; the Order's "
                "presence in Russia is in danger.",
                stopped="The draining is turned aside, by magic or by "
                "persuasion, without the Order being seen.",
            ),
        ],
    )
    w["threat_malincka"] = b.threat(
        "Malincka's Great Work",
        place=p.get("thousand_caves_site"),
        summary=paragraphs(
            "Malincka is designing a spell of magnitude 11, a development "
            "of Read the Magic Sphere with something of Plumb the Magical "
            "Scent, at Touch, with a Mentem requisite, to let other magi "
            "see auras exactly and how minds move them. Her Lab Total is 69; "
            "even so she must experiment to finish within the year. With "
            "it she hopes to win the Tribunal at the meeting of 1221 and "
            "then devise a Hermetic Great Ritual. Whether aura-making can "
            "succeed is the troupe's to decide (p. 120).",
        ),
        antagonist="Time, and Malincka's own ambition",
        moves=DATED,
        stages=[
            S(
                "The spell, or not",
                year=1221,
                season="Spring",
                clues="Malincka's laboratory runs every season; experiments "
                "go spectacularly wrong.",
                ignored="She comes to the meeting with the spell, or with a "
                "failure that hands her enemies a weapon.",
                turned="A troupe that helps her shapes what the spell "
                "reveals, and what the Tribunal sees.",
            ),
        ],
    )
    w["threat_hermes"] = b.threat(
        "The Return of Hermes",
        place=p.get("thousand_caves_site"),
        summary=paragraphs(
            "For thirty years Thousand Caves has preached Hermes to its "
            "tribes, hoping a great faerie will take up the god's part. "
            "Surges of magic and ecstatic dreams have begun, Basyl has "
            "visions of Hermes's coming, and the girl Stenya Vassanovna, "
            "Gifted, says Lord Hermes speaks to her and preaches him "
            "persuasively; even Rehamchi half believes her. The magi fear "
            "they will draw a demon instead.",
        ),
        antagonist="Whatever answers the worship",
        position=1,
        stages=[
            S(
                "Something answers",
                at=3,
                clues="Stenya's sermons grow stranger; the aura shifts.",
                ignored="A power takes the name of Hermes: a faerie with its "
                "own agenda, a demon, or the Slavic gods' anger.",
                turned="A troupe that learns what speaks to Stenya decides "
                "what kind of god comes.",
            ),
        ],
    )
    _dormant(records)


def _dormant(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    w["threat_yannes"] = dormant(
        b.threat(
            "Where Is Yannes Kolski?",
            place=p.get("russia"),
            summary="The Mad Magus of the East vanished near "
            "Vladimir-in-Suzdalia in 1216, still reciting his vision of the "
            "black serpent from the east. Is he dead, in Final Twilight, "
            "taken by faeries, or gone east to meet what he foresaw? The "
            "Yannes Discourse at Leczyca may say more than anyone has "
            "read in it.",
            antagonist="The vision itself",
            position=0,
            stages=[
                S(
                    "A sighting",
                    at=2,
                    clues="A howling holy fool among the Cumans; a merchant "
                    "repeats the serpent verses.",
                    ignored="The Discourse's warning goes unread until the "
                    "Mongols come.",
                ),
            ],
        )
    )
    w["threat_stolitzya"] = dormant(
        b.threat(
            "Stolitzya the Swimmer",
            place=p.get("pripet_marsh"),
            summary="Pripet Maior's founder, lost forty years in her turtle "
            "heart-beast, may still brood in the marsh's heart, its queen. "
            "If the draining or a war reaches her, she will rise.",
            antagonist="Stolitzya",
            position=0,
            stages=[
                S(
                    "The island that moves",
                    at=3,
                    clues="Floating islands torn apart; boats shattered from beneath.",
                    ignored="Stolitzya wakes against whoever troubles the "
                    "marsh, magi or mundanes.",
                ),
            ],
        )
    )
    w["threat_zashya"] = dormant(
        b.threat(
            "Zashya's Secret",
            place=p.get("three_lakes_site"),
            summary="Zashya Miyovna bore a daughter to a Rurikid prince, and "
            "her granddaughter is Nastassia Baramov. Revealed, it would "
            "shame Zashya before the Royal Embargo's makers, make "
            "Nastassia a prince's kin, and tell Miya Cossuri that the maga "
            "Pripet loathes is her great-granddaughter.",
            antagonist="Whoever learns it",
            position=0,
            stages=[
                S(
                    "The secret is out",
                    at=2,
                    clues="Questions about Nastassia's parents; an old "
                    "servant of the prince's house.",
                    ignored="The quarrel between Pripet and Thousand Caves "
                    "becomes a family feud.",
                ),
            ],
        )
    )
    w["threat_rhine"] = dormant(
        b.threat(
            "Leczyca and the Rhine",
            place=p.get("leczyca_ridge"),
            summary="Rhine interlopers raid Polish vis, Durenmar's agents "
            "work against Leczyca, and Leczyca's sympathy for the Polish "
            "nobles tempts it to intervene by magic against the Germans, "
            "as it did before its fine.",
            antagonist="Durenmar and the lesser Rhine covenants",
            position=0,
            stages=[
                S(
                    "A battle with the Germans",
                    at=3,
                    clues="A Silesian lord asks for help; a Rhine magus is "
                    "seen near Wroclaw.",
                    ignored="Leczyca intervenes, breaks the Embargo again, "
                    "and gives the Rhine its scandal.",
                ),
            ],
        )
    )
    w["threat_gathering"] = dormant(
        b.threat(
            "The Gathering of the Twelve Years",
            place=p.get("russia"),
            summary="House Bjornaer's Gathering is due in 1227, and Pripet "
            "Maior and Thousand Caves have both put their cases at "
            "Crintera. The raid has raised the stakes; the Gathering is "
            "bound to be explosive.",
            antagonist="House Bjornaer's Wilderists",
            moves=DATED,
            stages=[
                S(
                    "The Gathering",
                    year=1227,
                    season="Summer",
                    ignored="The House judges between Pripet Maior and "
                    "Thousand Caves, or splits over them.",
                ),
            ],
        )
    )
    w["threat_durenmar"] = dormant(
        b.threat(
            "Durenmar's Motion",
            place=p.get("poland"),
            summary="At every Grand Tribunal Durenmar moves that the Rhine's "
            "eastern border be reassessed. If the quarrel over Thousand "
            "Caves reaches the Grand Tribunal of 1228 as a scandal, the "
            "Rhine may at last take the 'vacant' Polish lands.",
            antagonist="Durenmar",
            moves=DATED,
            stages=[
                S(
                    "The Grand Tribunal of 1228",
                    year=1228,
                    season="Summer",
                    ignored="The motion is heard with the Tribunal's "
                    "troubles before the whole Order.",
                    stopped="The Tribunal settles its quarrel first and "
                    "the motion fails, as before.",
                ),
            ],
        )
    )


#: Ties between the stories and the people and places they touch:
#: (threat key, the part that made the record, its key, note).
TIES: tuple[tuple[str, str, str, str], ...] = (
    ("threat_trial", "magi", "casimi", "Led the raid"),
    ("threat_trial", "magi", "andrei", "Must judge it"),
    ("threat_trial", "magi", "lelya", "Wants an apology"),
    ("threat_drainage", "world", "mikhail_turov", "Means to drain the marsh"),
    ("threat_drainage", "covenants", "pripet_maior", "Its marsh"),
    ("threat_malincka", "magi", "malincka", "Her spell"),
    ("threat_hermes", "magi", "rehamchi", "Half believes"),
    ("threat_hermes", "magi", "basyl", "Sees visions"),
    ("threat_hermes", "world", "cult_of_hermes", "Its cult"),
    ("threat_yannes", "magi", "yannes", "Vanished"),
    ("threat_stolitzya", "creatures", "stolitzya", "The Swimmer"),
    ("threat_zashya", "magi", "zashya", "Her secret"),
    ("threat_zashya", "magi", "nastassia", "Her granddaughter"),
    ("threat_zashya", "magi", "miya", "Her mother"),
    ("threat_rhine", "covenants", "leczyca", "In the Rhine's sights"),
)


def finish(records: Records) -> None:
    b, w = records.b, records.world
    parts = {
        "magi": records.magi,
        "world": records.world,
        "covenants": records.covenants,
        "creatures": records.creatures,
    }
    kinds = {
        "magi": "characters",
        "world": "places",
        "covenants": "covenants",
        "creatures": "creatures",
    }
    for threat_key, part, key, note in TIES:
        threat, target = w.get(threat_key), parts[part].get(key)
        if threat is not None and target is not None:
            b.link(threat, kinds[part], target, note)
