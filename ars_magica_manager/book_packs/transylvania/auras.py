"""The auras the book leaves without a number, as the pack sets them.

Against the Dark gives many sites an aura in words ("strong", "a Magic
aura") or none at all. The values here are the ones settled for the
pack; Help's page of the pack's assumptions lists each, as inferred from
the book's words or as a judgement call. Run last, so every place and
oppidum exists."""

from __future__ import annotations

from ...models import Covenant, Neighbour
from . import Transylvania

#: Places: name -> (aura, realm).
PLACES: dict[str, tuple[int, str]] = {
    "Coeris": (5, "Magic"),
    "The Altar of the Standards and the Gate of Eurydice": (6, "Magic"),
    "Sarmizegethusa Fort": (5, "Magic"),
    "The Prokletije Fort": (4, "Magic"),
    "Leviathan's Cache": (3, "Magic"),
    # The book prints 9 for its strongest places (Against the Dark p. 87);
    # the oppidum below works in the safer areas, which don't warp, so 5
    # at most (Warping starts at 6, DE p. 390).
    "The Mountain of Lycaneon": (9, "Magic"),
    "The Rock Womb": (6, "Magic"),
    "Dobsinska Cave": (3, "Magic"),
    "Ochtinska Cave": (3, "Magic"),
    "A storm wizards' ice cave": (6, "Magic"),
    "Mount Klek": (5, "Infernal"),
    "Körösfö": (3, "Infernal"),
    "The Night Streets of Zadar": (3, "Infernal"),
    "The Abandoned Forts of Kezdö Válasz": (3, "Magic"),
    "Pannonia's first site": (3, "Divine"),
    "The Sacred Glens of Perun": (3, "Magic"),
    "The Pirin Mountains": (3, "Magic"),
    "Marienburg": (3, "Divine"),
    "Kronstadt Castle": (3, "Divine"),
    "Rosenau": (3, "Divine"),
    "Schwarzenburg": (3, "Divine"),
    "Kreuzburg": (3, "Divine"),
    "Mount Hum": (3, "Faerie"),
    "The Sasar, River of the Ladies": (3, "Faerie"),
    "The Seventy-Seventh Island": (3, "Faerie"),
    "The Golden Palace of Firtos": (5, "Faerie"),
    "The Palace of Tartos": (5, "Faerie"),
    "Diocletian's Palace": (3, "Magic"),
    "The Mansio of Vrhbosna": (2, "Magic"),
    # Good sites and vis sites the book gives no aura: a typical
    # covenant's.
    **{
        name: (3, "Magic")
        for name in (
            "The Kal Valley and Lake Balaton",
            "Cakoc",
            "The Tomb of Attila",
            "Klingsohr's fields by the Tisza",
            "The Sunken City",
            "The Isle of Achilles",
            "Gyogy-to",
            "The Valley of the Thracian Kings",
            "The Grave of Aspytrus",
            "The Truffle Woods of Northern Istria",
            "The Mirna Valley",
            "Kogaionon",
            "The Palace of Balbona",
            "Ikafalva and the Furus",
            "The Iron Gate",
            "The Vargyas River",
            "The Bran Pass Zenodochium",
            "The Plague House",
            "Danaslepih's Grove",
            "Domostron's first site",
            "Gela",
            "The Lost Zenodochium of Zadar",
        )
    },
}

#: Regio levels: (place, level) -> aura.
LEVELS: dict[tuple[str, str], int] = {
    ("The Shipka Pass", "The Tribunal regio"): 5,
    ("The Altar of the Standards and the Gate of Eurydice", "The City Below"): 7,
}

#: Oppida: name -> aura, in Magic.
OPPIDA: dict[str, int] = {
    "Coeris": 6,
    "Kezdö Válasz": 5,
    "Lycaneon": 5,
    "The Zenodochia": 3,
    "Leviathan": 3,
}


def build(transylvania: Transylvania) -> None:
    pass


def _place(transylvania: Transylvania, name: str) -> Neighbour:
    found = [
        n
        for n in transylvania.b.saga.neighbours
        if n.kind == "place" and n.name == name
    ]
    if len(found) != 1:
        raise KeyError(f"{len(found)} places named {name!r}")
    return found[0]


def finish(transylvania: Transylvania) -> None:
    for name, (aura, realm) in PLACES.items():
        place = _place(transylvania, name)
        place.details["aura"], place.realm = aura, realm
    for (name, level), aura in LEVELS.items():
        levels = _place(transylvania, name).details["levels"]
        (found,) = [entry for entry in levels if entry["name"] == level]
        found["aura"] = aura
    for name, aura in OPPIDA.items():
        covenant: Covenant = transylvania.covenant_named(name)
        covenant.aura, covenant.aura_realm = aura, "Magic"
