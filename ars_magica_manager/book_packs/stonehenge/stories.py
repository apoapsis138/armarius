"""The saga's stories (S18), from the Politics chapter's flashpoints
(pp. 140-141) and Houses of Hermes: Societates p. 112.

Under way: Gwrhyr's land suit (world["threat_gwrhyr"]), Voluntas against
Ungulus (["threat_ungulus"]), the eastern covenants' vis quarrel
(["threat_vis"]), Schola Pythagoranis's mundane entanglement
(["threat_schola"]) and Nicola de Hay against Salisbury
(["threat_lincoln"]).

Dormant: Ashenrise's revenge (["threat_ashenrise"]), Immanola's prophecy
(["threat_prophecy"]), Blackthorn's diabolism (["threat_diabolism"]),
Burnham's secret (["threat_burnham"]), the Forgotten Covenant
(["threat_forgotten"]) and Junius's project (["threat_junius"])."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import Builder, dormant, paragraphs

if TYPE_CHECKING:
    from ..records import Records

S = Builder.stage


def build(records: Records) -> None:
    b, w, p = records.b, records.world, records.places
    w["threat_gwrhyr"] = b.threat(
        "The Island of Cad Gadu",
        place=p.get("cad_gadu_island"),
        summary=paragraphs(
            "The mundane island of Cad Gadu belongs in Welsh law to Gwrhyr of "
            "the Columbae, who has no sons but many male kin. His kindred, who "
            "dislike him and his adopted filius Culhwch, will not let the land "
            "pass to Culhwch; when Gwrhyr dies they will claim it and evict the "
            "magi, with the law on their side. Immanola neglected it, and no one "
            "has told Ebroin, Gwrhyr sitting on his Council.",
            "The kindred, suspicious of his great age and his name as a "
            "sorcerer, have brought him to the notice of the Prince of Gwynedd, "
            "who wants to meet this seemingly immortal Welshman. A court date is "
            "set; if Gwrhyr does not appear to be examined, the land goes to his "
            "heirs.",
        ),
        antagonist="Gwrhyr's kindred, and Llywelyn's court",
        position=1,
        stages=[
            S(
                "The court date",
                at=3,
                clues="Gwrhyr's kinsmen are seen about Snowdonia asking after "
                "him; a summons comes from the Prince's court.",
                ignored="Gwrhyr fails to appear, and the island defaults to his "
                "heirs, who move to evict the domus magna.",
                stopped="He appears, or the matter is settled with the kindred.",
            ),
        ],
    )
    w["threat_ungulus"] = b.threat(
        "Voluntas against Ungulus",
        place=p.get("ungulus_tower"),
        summary="Voluntas, seeing Ungulus weak, is encroaching on its lands. "
        "Ungulus is not quite dead, and may fight back; and when it falls, the "
        "Tribunal expects a feeding frenzy over its treasures.",
        antagonist="Voluntas",
        position=1,
    )
    w["threat_vis"] = b.threat(
        "The Eastern Covenants' Vis",
        place=p.get("england"),
        summary="Schola Pythagoranis, Libellus and Nigrasaxa lie in one small "
        "region and face a shortage of vis there, whatever the Tribunal at "
        "large has; their quarrel over sources grows as Schola seeks outpost "
        "laboratories in magic auras. All three were of the old bloc against "
        "Blackthorn, so it has not come to open conflict yet. Across the "
        "Tribunal the plough is taking land where vis grew.",
        antagonist="Want",
        position=1,
    )
    w["threat_schola"] = b.threat(
        "Schola Pythagoranis and the World",
        place=p.get("schola_hall"),
        summary="Schola Pythagoranis is deep in mundane affairs, perhaps beyond "
        "the Code. Its House supports it, and the Jerbitons who speak for "
        "Voluntas and Libellus have shielded it from censure so far; it is on "
        "good terms with the town, and a covenant in the middle of a city is "
        "hard to March. How long that lasts is unclear.",
        antagonist="The Code",
        position=1,
    )
    w["threat_lincoln"] = b.threat(
        "Nicola de Hay and the Earl of Salisbury",
        place=w.get("lincoln"),
        summary="Nicola de Hay, constable of Lincoln castle and arguably its "
        "sheriff, disputes both with William Longespee, earl of Salisbury, who "
        "seized the castle in 1219 and lost it to her and Falkes de Bréauté. "
        "He is still sheriff and tries to win the castle back by bribery or "
        "force; she presses to win back the shrievalty.",
        antagonist="William Longespee, earl of Salisbury",
        position=1,
    )
    w["threat_ashenrise"] = dormant(
        b.threat(
            "Ashenrise's Revenge",
            place=p.get("blackthorn_caves"),
            summary="Ashenrise, in the Hibernian Tribunal, was founded by the "
            "magi of Tagelyn when Blackthorn drove them out in 1062. They have "
            "not forgotten, and Blackthorn's weakness now may be their chance.",
            antagonist="Ashenrise",
        )
    )
    w["threat_prophecy"] = dormant(
        b.threat(
            "Immanola's Prophecy",
            place=p.get("cad_gadu_island"),
            summary="Soon after she claimed the Robes of Dusty Dawn, Immanola "
            "sent word to every magus of her House that the Order was about to "
            "end, and told them to come to Stonehenge to save what they could. "
            "It seemed never to come true, and her name sank; she waited "
            "patiently, sat twelve years gazing into a pool at Cad Gadu, and was "
            "declared in Final Twilight in 1216. Her doom has not been withdrawn.",
            antagonist="Whatever she foresaw",
        )
    )
    w["threat_diabolism"] = dormant(
        b.threat(
            "Blackthorn's Diabolism",
            place=p.get("blackthorn_caves"),
            summary="Blackthorn has faced charges of diabolism many times; "
            "nothing has been proved. The charge could be raised to distract from "
            "another covenant's trouble, or it could be true, which would shake "
            "the Tribunal.",
            antagonist="Unknown",
        )
    )
    w["threat_burnham"] = dormant(
        b.threat(
            "Burnham's Purpose",
            place=p.get("burnham_castle"),
            summary="No one knows what Burnham is doing, it will not explain, "
            "and every covenant has its theory.",
            antagonist="Burnham",
        )
    )
    w["threat_forgotten"] = dormant(
        b.threat(
            "The Forgotten Covenant",
            place=p.get("nameless"),
            summary="The magi come by a bag of old Redcap letters, many with "
            'passages cut out; one fragment left at the bottom speaks of "the '
            "two Diedne covenants\". The Tribunal's list of covenants names only "
            "one, the Nameless Covenant on Anglesey.",
            antagonist="Whoever cut the letters",
        )
    )
    w["threat_junius"] = dormant(
        b.threat(
            "Junius's Project",
            summary="Junius of Verditius, of Semitae, a powerful magus and "
            "maker of devices, spends most of his time on a project he will not "
            "speak of: people will see it, he says, when it is ready. The "
            "Tribunal and his House are curious.",
            antagonist="Junius of Verditius",
        )
    )


TIES: tuple[tuple[str, str, str], ...] = (
    ("threat_gwrhyr", "gwrhyr", "The island's owner"),
    ("threat_gwrhyr", "culhwch", "His adopted filius"),
    ("threat_gwrhyr", "ebroin", "Not yet told"),
    ("threat_gwrhyr", "cad_gadu", "The covenant at risk"),
    ("threat_ungulus", "voluntas", "Encroaching"),
    ("threat_ungulus", "ungulus", "The covenant at risk"),
    ("threat_vis", "schola", "One of the three"),
    ("threat_vis", "libellus", "One of the three"),
    ("threat_vis", "nigrasaxa", "One of the three"),
    ("threat_schola", "schola", "The covenant"),
    ("threat_ashenrise", "blackthorn", "Its target"),
    ("threat_diabolism", "blackthorn", "The accused"),
    ("threat_burnham", "burnham", "The covenant"),
    ("threat_junius", "junius", "The maker"),
)


def finish(records: Records) -> None:
    for threat_key, key, note in TIES:
        threat = records.world.get(threat_key)
        target = records.magi.get(key) or records.covenants.get(key)
        if threat is None or target is None:
            continue
        kind = "characters" if key in records.magi else "covenants"
        records.b.link(threat, kind, target, note)
    lincoln = records.world.get("threat_lincoln")
    for key in ("nicola_de_hay", "salisbury", "falkes"):
        lord = records.world.get(key)
        if lincoln is not None and lord is not None:
            records.b.link(lincoln, "neighbours", lord, "A party")
