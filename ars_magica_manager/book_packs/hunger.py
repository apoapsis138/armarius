"""Records the two African packs share, so one saga holding both has one of
each: the Great Hunger and the Hope, the two vast spirits both books set
against each other, and the pact that keeps covenants out of Africa until
1225. Summarised from Between Sand and Sea pp. 7-8 and Lands of the Nile
p. 6, not quoted. Their records match by name when both packs come in."""

from __future__ import annotations

from .builder import Builder, dormant, paragraphs


def build(b: Builder) -> None:
    b.faction(
        "The Great Hunger",
        summary=paragraphs(
            "The spirit at the centre of the Great Desert, so vast it gives "
            "gods pause: the parching heat and eroding wind made one, seeking "
            "to reduce the world to dust. The Romans called it the Fames "
            "Magna, the Berbers Lazz, the Arabs Al-Ju'; along the Nile it is "
            "the Red.",
            "Hostile creatures, spirits, faeries and jinn serve it, and some "
            "people do too: the settuten trace their line to the Yemma-t n "
            "Dunnit, perhaps its foremost servant.",
        ),
        realm="Magic",
    )
    b.faction(
        "The Hope",
        summary=paragraphs(
            "The spirit of the Nile and the fertile black earth, called the "
            "Black, which holds back the Hunger. It favours people only by "
            "accident, being too vast to notice them. The lector priests who "
            "were magicians to the pharaohs served it, and so does Wesir, "
            "whom the Greeks called Osiris.",
        ),
        realm="Magic",
    )
    dormant(
        b.threat(
            "The Pact of 1225",
            summary=paragraphs(
                "When most of the Cordovan sahirs joined the Order of Hermes "
                "in 925, one condition was that no covenant be founded in "
                "Africa for three centuries. Nobody now agrees why: to hide "
                "them from jinn they had betrayed, or to keep the settuten "
                "from becoming the Order's enemies. It expires in 1225, and "
                "some magi are eager to go.",
            ),
            stages=[
                b.stage(
                    "The pact expires",
                    year=1225,
                    ignored="Magi are free to found covenants in Africa.",
                )
            ],
        )
    )
