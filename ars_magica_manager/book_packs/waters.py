"""The waters of the packs: where a ship covenant can stop, pack by pack.

A stop must be a Place, a Town is not one, and a Place cannot sit inside a
Town, so a port town gets a harbour Place beside it in the same region,
and the town links to it. A Place does not inherit an aura and a Town has
none, so a harbour holds its own: a town or city has a Divine aura of 3 over
most of its area and a village 2, of any Divine faith (Definitive Edition p.
418), unless the book prints another figure.

Three tables, each row citing its book's page where Grimoire shows it:
`PORT_TOWNS` for towns the pack holds, `NAMED_PORTS` for ports the book only
names, and `MARKS` for Places the pack already has. The packs' text stays
where it is; `chart` adds these once a pack is assembled. It is table-driven
so that one rule covers every book, and a row that matches nothing stops the
build."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Neighbour
from ..rules import mobile, sites
from .builder import DIVINE_CITY_AURA, DIVINE_VILLAGE_AURA, Builder

CITY, VILLAGE = DIVINE_CITY_AURA, DIVINE_VILLAGE_AURA


@dataclass(frozen=True)
class PortTown:
    """A town the pack holds that ships can reach: the page, its aura, and
    the supplement that adds the town, if one does."""

    town: str
    page: str = ""
    aura: int = CITY
    supplement: str = ""


@dataclass(frozen=True)
class NamedPort:
    """A port the book only names, in the Place that holds it."""

    name: str
    inside: str
    summary: str
    page: str = ""
    aura: int = CITY


@dataclass(frozen=True)
class Mark:
    """What a Place the pack already has offers ships. `aura` replaces a
    settled Place's blank one, as Divine."""

    place: str
    waters: str
    page: str = ""
    aura: int | None = None
    supplement: str = ""


PORT_TOWNS: dict[str, tuple[PortTown, ...]] = {
    "africa": (
        PortTown("Anfa", "p. 43"),
        PortTown("Asfi", "p. 43"),
        PortTown("Tangier", "p. 48"),
        PortTown("Mahdia", "p. 50"),
        PortTown("Sfax", "p. 50"),
        PortTown("Tunis", "p. 54"),
        PortTown("Tripoli", "p. 55"),
        PortTown("Sharshal", "p. 56"),
        PortTown("En Nassria", "p. 56"),
        PortTown("Sidi Rafaa", "p. 60", VILLAGE),
    ),
    "cradle": (
        PortTown("Hajar", "p. 109"),
        PortTown("Muscat", "p. 119"),
        PortTown("Kish", "p. 146"),
    ),
    "hibernia": (
        PortTown("Cork", "p. 50"),
        PortTown("Waterford", "p. 50"),
        PortTown("Limerick", "p. 50"),
        PortTown("Wexford", "p. 51"),
        PortTown("Bannow", "p. 51"),
        PortTown("New Ross", "p. 52"),
        PortTown("Wicklow", "p. 53"),
        PortTown("Dublin", "p. 54"),
        PortTown("Arklow", "p. 54"),
        PortTown("Drogheda-in-Meath", "p. 68"),
        PortTown("Donegal", "p. 90"),
        PortTown("Dundrum", "p. 97"),
        PortTown("Tralee"),
    ),
    "iceland": (
        PortTown("De Panne", "p. 81"),
        PortTown("Exeter", "p. 81"),
        PortTown("Bergen"),
    ),
    "levant": (
        PortTown("Acre", "p. 19"),
        PortTown("Tripoli", "p. 20"),
        PortTown("Famagusta"),
        PortTown("Alexandria"),
        # The sack of 1219 left the Dominion here at +1, gone at night (p. 25).
        PortTown("Damietta", "p. 25", 1),
    ),
    "nile": (
        PortTown("Alexandria", "p. 57"),
        PortTown("Damietta", "p. 65"),
        PortTown("'Aydhab", "p. 69"),
        PortTown("Sawakin", "p. 96"),
        PortTown("Badi", "p. 96"),
        PortTown("Adulis", "p. 114"),
        PortTown("Massawa", "p. 115"),
        PortTown("Zeila", "p. 117"),
    ),
    "normandy": (
        PortTown("St Malo", "p. 36"),
        PortTown("St Brieuc", "p. 36"),
        PortTown("Brest", "p. 40"),
        PortTown("Redon", "p. 50"),
        PortTown("Barfleur", "p. 57"),
        PortTown("La Rochelle", "p. 66"),
        PortTown("Bergerac", "p. 69"),
        PortTown("Bruges", "p. 93"),
        PortTown("Antwerp", "p. 96"),
        PortTown("Boulogne", "p. 100"),
        PortTown("Landerneau"),
        PortTown("Dinan"),
        PortTown("Angers"),
        PortTown("Angoulême"),
        PortTown("Ghent"),
    ),
    "provence": (
        PortTown("Bordeaux", "p. 53"),
        PortTown("Blaye", "p. 54"),
        PortTown("Langon", "p. 60"),
        PortTown("Bayonne", "p. 61"),
        PortTown("Narbonne", "p. 101", 2),
        PortTown("Arles", "p. 117"),
        PortTown("Marseille", "p. 124"),
        PortTown("Beaucaire"),
    ),
    "rhine": (
        PortTown("Hamburg", "p. 68"),
        PortTown("Lübeck", "p. 69"),
        PortTown("Rostock", "p. 75"),
        PortTown("Bremen", "p. 77"),
        PortTown("Stettin", "p. 99"),
        PortTown("Baccharach"),
    ),
    "stonehenge": (PortTown("Exeter", "p. 46"),),
    "theban": (
        PortTown("Durazzo", "p. 51"),
        PortTown("Corfu", "p. 51"),
        PortTown("Thessaloniki", "p. 54"),
        PortTown("Athens", "p. 58"),
        PortTown("Corinth", "p. 61"),
        PortTown("Andros", "p. 77"),
        PortTown("Kos", "p. 78"),
        PortTown("Chandax", "p. 79"),
        PortTown("Hebdomon", "p. 93"),
        PortTown("Holkos", "p. 106"),
        PortTown("Smyrna", "p. 108"),
        PortTown("Amastris", "p. 111"),
        PortTown("Sinope", "p. 111"),
        PortTown("Trebizond", "p. 111"),
        PortTown("Miletos", "Through the Aegis p. 89", 2, "TtA"),
        PortTown("Panormos", "Through the Aegis p. 72", CITY, "TtA"),
    ),
    "transylvania": (
        PortTown("Dubrovnik"),
        PortTown("Zadar"),
    ),
}

NAMED_PORTS: dict[str, tuple[NamedPort, ...]] = {
    "cradle": (
        NamedPort(
            "Hindijan",
            "Fars",
            "Arranjan's port, on the lower reaches of the Tab.",
            "p. 145",
        ),
        NamedPort(
            "Tiz", "Makran", "A halt for ships between Al-Sind and Fars.", "p. 156"
        ),
    ),
    "levant": (
        NamedPort("Kyrenia", "Cyprus", "A port on Cyprus's north coast."),
        NamedPort("Limassol", "Cyprus", "Once the chief port of Cyprus."),
    ),
    "nile": (
        NamedPort("Qusayr", "Egypt", "One of the rival ports of the Red Sea.", "p. 97"),
    ),
    "normandy": (
        NamedPort(
            "Damme",
            "Flanders",
            "The harbour on the Zwin estuary, five miles from Bruges and "
            "joined to it by canal.",
            "p. 93",
        ),
    ),
    "provence": (
        NamedPort(
            "Collioure",
            "County of Roussillon",
            "A southern port town where many crusaders take ship, under the "
            "Templars' castle above the bay.",
            "p. 103",
        ),
    ),
    "theban": (
        NamedPort("Modon", "The Morea", "A port on the coast of the Morea.", "p. 60"),
        NamedPort("Myrina", "Lemnos", "A port town on Lemnos's west coast."),
        NamedPort(
            "Rodos",
            "The island of Rodos",
            "The city's harbour, where Venice's fleet keeps a base.",
            "p. 79",
        ),
    ),
    "transylvania": (
        NamedPort("Varna", "Bulgaria", "A Black Sea port of Bulgaria.", "p. 45"),
        NamedPort("Nesebar", "Bulgaria", "A Black Sea port of Bulgaria.", "p. 45"),
    ),
}

MARKS: dict[str, tuple[Mark, ...]] = {
    "africa": (
        Mark("Apollonia", mobile.PORT, aura=VILLAGE),
        Mark("Leptis Magna", mobile.ANCHORAGE),
    ),
    "cradle": (Mark("Al-Khadar, the Green Ocean", mobile.OPEN_WATER),),
    "hibernia": (
        Mark("Achill Island", mobile.ANCHORAGE),
        Mark("Clew Bay", mobile.ANCHORAGE),
        Mark("The River Shannon", mobile.OPEN_WATER),
    ),
    "iceland": (
        Mark("Husavik", mobile.ANCHORAGE),
        Mark("The Southeastern Harbor", mobile.ANCHORAGE),
    ),
    "legends_of_hermes": (Mark("Qadis", mobile.PORT, "p. 32"),),
    "nile": (
        Mark("The Village South of Adulis", mobile.PORT, "pp. 141-142"),
        Mark("Ceto's Well", mobile.ANCHORAGE, "p. 141"),
        Mark("The Red Sea", mobile.OPEN_WATER, "p. 97"),
        Mark("The Nile", mobile.OPEN_WATER),
    ),
    "normandy": (Mark("The Isle of Oléron", mobile.PORT, "p. 71"),),
    "provence": (
        Mark("The Hyères Islands", mobile.ANCHORAGE, "p. 125"),
        Mark("The Gulf of Lion", mobile.OPEN_WATER),
        Mark("The Whaling Grounds of Bayonne", mobile.OPEN_WATER),
        Mark("The Rhone", mobile.OPEN_WATER, "p. 115"),
        Mark("The River Aude", mobile.OPEN_WATER, "p. 101"),
    ),
    "rhine": (
        Mark("Terschelling", mobile.PORT, "p. 67"),
        Mark("The Rhine Gorge", mobile.OPEN_WATER),
    ),
    "theban": (
        Mark("Polyaigos", mobile.PORT),
        Mark("The Harbours of Constantinople", mobile.PORT, "p. 92", CITY),
        Mark("The Venetian Quarter", mobile.PORT, "p. 95", CITY),
        Mark("The Bay of Thera", mobile.ANCHORAGE, "p. 78"),
        Mark("The Hellespont", mobile.OPEN_WATER, "p. 106"),
        Mark("The Euripus Strait", mobile.OPEN_WATER),
        Mark(
            "The Lion Harbour Warehouses",
            mobile.PORT,
            "Through the Aegis p. 89",
            supplement="TtA",
        ),
    ),
    "transylvania": (
        Mark("The Isle of Achilles", mobile.ANCHORAGE, "p. 9"),
        Mark("The Villa of Shrouded Bay", mobile.PORT),
    ),
}


def _named(b: Builder, kind: str, name: str) -> Neighbour:
    for record in b.saga.neighbours:
        if record.kind == kind and record.name == name:
            return record
    raise ValueError(f"No {kind} named {name!r} in this pack.")


def chart(key: str, b: Builder, supplements: tuple[str, ...] = ()) -> None:
    """Add the waters of the pack `key` to its assembled saga, leaving out
    the rows of supplements not in play."""
    for port in PORT_TOWNS.get(key, ()):
        if not port.supplement or port.supplement in supplements:
            b.harbour(_named(b, "town", port.town), aura=port.aura)
    for named in NAMED_PORTS.get(key, ()):
        b.named_port(
            named.name,
            inside=_named(b, sites.PLACE, named.inside),
            summary=named.summary,
            aura=named.aura,
        )
    for mark in MARKS.get(key, ()):
        if mark.supplement and mark.supplement not in supplements:
            continue
        found = _named(b, sites.PLACE, mark.place)
        found.details[sites.WATERS] = mark.waters
        if mark.aura is not None:
            found.realm = "Divine"
            found.details["aura"] = mark.aura
