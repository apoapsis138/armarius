"""A town's charter (City & Guild, Town Charters, pp. 8-14; Populace, pp.
23-24): who granted it and how they hold it, its terms and privileges,
what it gives (the Divine aura within the walls, a demon's services, the
pawn of vis in the signed document), the saga's characters who are its
citizens, and the town's size and people.

- A charter is granted by whoever claims the land: a king or lesser
  noble, a bishop or abbot, a faerie lord, or a demon (pp. 9-12). Several
  French nobles may grant one in partnership, paragium, by an agreement
  that splits the revenue (p. 10); claims can be contested, and a faerie
  lord may offer a rival charter (pp. 9-10); a town may keep a secret
  demonic charter beside its mundane one (p. 11).
- The townsfolk pay an annual tax: 40 pounds for a town of several
  hundred burgesses (p. 12). Common privileges: the town's own courts,
  limits on ordeal, combat and fines (Breteuil's 12 pence), monopolies,
  toll exemptions, a market or fair, salvage, the choice of officials,
  and the sale of land (pp. 12-13); a French royal charter adds militia
  duty (p. 10).
- A town's or city's Divine aura is 3 over most of it (Definitive Edition
  p. 418, which wins over Realms of Power: The Divine p. 10's town 2). An
  ecclesiastical charter makes it one higher within the walls (C&G p. 10:
  "one higher than would be normally expected"), so 4; a faerie one 1
  (p. 11); the churches inside keep their own.
- A charter demon has Infernal Might 15 (Mentem) and offers some of three
  services: relief from disease (+2 Living Conditions), help for
  merchants (+3 to Bargain and Profession: Merchant totals), dangerous
  labor (p. 11).
- The signed charter holds one pawn of Rego vis, tainted by the Divine
  (very large towns more); extracting it destroys the charter's
  sympathetic connections (p. 9).
- A year and a day of residence makes a townsman (p. 9); clerics are
  rarely citizens (pp. 9-10). A citizen has a sympathetic connection to
  everyone under the same charter (its family included): +1 to the
  Penetration multiplier of a spell against them. Becoming a citizen of
  another town ends the old connection (p. 9).
- The occupations of a small, medium and large town (p. 24), and the
  officials a charter appoints (pp. 13-14).

Kept in Neighbour.details: "charter_lords" (each CharterLord),
"charter_terms" (CharterTerms), "citizens" (each Citizen), and beside the
town's "population" and "council", "burgesses", "city", "magistrates" and
"officials"."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Required, TypedDict, cast

from . import towns
from .commands import Command, Form, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import BULLET, aligned, escape
from .models import (
    SEASONS,
    Character,
    Covenant,
    Neighbour,
    Saga,
    details_list,
    season_order,
)
from .neighbour_lists import KindBlock, KindList, KindTab, list_ops
from .references import Fact
from .rules import options
from .sections import (
    CHARTER_GIVES_SECTION,
    CHARTER_LORDS_SECTION,
    CHARTER_TERMS_SECTION,
    CITIZENS_SECTION,
    COV_CHARTER_LORDS_SECTION,
    COV_CHARTER_TERMS_SECTION,
    TOWN_PEOPLE_SECTION,
)

SOURCE = (
    "City & Guild, Town Charters pp. 8-14, Populace pp. 23-24; "
    "Realms of Power: The Divine p. 10"
)
CG = "C&G"

#: Who may grant a charter (pp. 9-12).
LORD_KINDS: tuple[str, ...] = ("Noble", "Church", "Faerie", "Demon")

#: How a lord holds the charter: (label, what it means).
HOLDS: dict[str, tuple[str, str]] = {
    "Sole": ("Sole", "He holds the charter alone."),
    "Shared": (
        "Shared (paragium)",
        "Lords granting in partnership; an agreement between them, generally "
        "older than the charter, splits the revenue (p. 10).",
    ),
    "Rival": (
        "Rival",
        "A contested claim (p. 9), or a faerie lord's rival charter (p. 10); "
        "a neutral party, the Church or an overlord, often decides it.",
    ),
    "Parallel": (
        "Parallel",
        "A secret demonic charter beside a mundane one (p. 11).",
    ),
}
#: The holds that make a lord the charter's holder: a rival claim or a
#: secret parallel charter doesn't change what the walls hold.
HOLDING = frozenset({"Sole", "Shared"})

#: A charter demon's Infernal Might (p. 11).
DEMON_MIGHT = 15
#: A charter demon's services: (key, name, what it gives) (p. 11).
DEMON_SERVICES: tuple[tuple[str, str, str], ...] = (
    ("disease", "Relief from disease", "+2 to the Living Conditions modifier"),
    ("merchants", "Help for merchants", "+3 to Bargain and Profession: Merchant"),
    ("labour", "Dangerous or difficult labor", "a mine worked for the town"),
)

#: A town's normal Divine aura, a city's, and what an ecclesiastical or
#: faerie charter makes it within the walls.
TOWN_AURA = 3
CITY_AURA = 3
CHURCH_AURA = TOWN_AURA + 1
FAERIE_AURA = 1

#: The typical tax of a town of several hundred burgesses (p. 12).
TYPICAL_TAX = "40 pounds"
#: The pawns of Rego vis most charter documents hold (p. 9).
CHARTER_PAWNS = 1


@dataclass(frozen=True)
class Privilege:
    """A common privilege of a charter: its key in the terms, its name, the
    key of its note (what it is, exactly) and the note's hint, and its
    page."""

    key: str
    name: str
    note: str = ""
    hint: str = ""
    page: str = "p. 12"


PRIVILEGES: tuple[Privilege, ...] = (
    Privilege("tax", "Annual tax", "tax_amount", "40 pounds for several hundred"),
    Privilege("courts", "Its own courts", hint="burgesses tried only in town"),
    Privilege("no_ordeal", "Ordeal and combat limited"),
    Privilege("fine_cap", "A cap on fines", "fine_cap_note", "Breteuil's: 12 pence"),
    Privilege("monopolies", "Monopolies", "monopolies_note", "e.g. on millstones"),
    Privilege("tolls", "Toll exemptions", "tolls_note", "through whose lands"),
    Privilege("market", "A market or fair", "market_note", "when, and its terms"),
    Privilege("salvage", "Salvage", page="p. 13"),
    Privilege("officials", "Chooses its officials", page="p. 13"),
    Privilege("land", "Land may be sold", page="p. 13"),
    Privilege("militia", "Militia duty", "militia_note", "to whom", page="p. 10"),
)

#: Families of charters the book describes (pp. 12-14).
FAMILIES = "Lorris, Breteuil, Freiburg, Lübeck, Cuenca..."

#: The officials a charter may name (p. 13).
OFFICIAL_TITLES = (
    "aldermen, bailiffs, consuls, coroners, councilors, magistrates, mayors, "
    "ministerials, portmen, rectors, reeves"
)

#: Occupations by a town's size, as percentages of its people:
#: agriculture, craft, service, trade (p. 24).
OCCUPATIONS: dict[str, tuple[int, int, int, int]] = {
    "Small town": (50, 50, 0, 0),
    "Medium town": (10, 50, 30, 10),
    "Large town": (10, 30, 30, 30),
}
OCCUPATION_NAMES = ("Agriculture", "Craft", "Service", "Trade")

#: Social Status Virtues that make a character a cleric, whom a town
#: rarely takes as a citizen (pp. 9-10).
CLERICS = frozenset(
    {
        "vf_priest",
        "vf_brother_chaplain",
        "vf_eastern_priest",
        "vf_mendicant_friar",
        "vf_senior_clergy",
        "vf_clerk",
    }
)


# -- the record --


class CharterLord(TypedDict, total=False):
    """A lord of the charter: his name, kind, how he holds it, his share
    of the revenue (free text), since when, a note, and for a demon its
    services."""

    lord: Required[str]
    kind: str
    hold: str
    share: str
    since: int | None
    note: str
    disease: bool
    merchants: bool
    labour: bool
    # Charter Strength, an optional rule (Transforming Mythic Europe p. 36):
    # the lord's (superior) and the town's or covenant's (subordinate)
    # scores, None until drafted, the last loophole found in it, and
    # whether it is English (its notaries use Common Law).
    superior_strength: int | None
    subordinate_strength: int | None
    loophole: str
    in_england: bool


class CharterTerms(TypedDict, total=False):
    """The charter's family, the year granted, its privileges (each a tick
    and, for some, a note), and what it gives: whether the Church holds a
    shared charter, the pawns of vis in it and whether they were taken."""

    family: str
    granted: int | None
    tax: bool
    tax_amount: str
    courts: bool
    no_ordeal: bool
    fine_cap: bool
    fine_cap_note: str
    monopolies: bool
    monopolies_note: str
    tolls: bool
    tolls_note: str
    market: bool
    market_note: str
    salvage: bool
    officials: bool
    land: bool
    militia: bool
    militia_note: str
    church_holds: bool
    pawns: int | None
    vis_taken: bool


class Citizen(TypedDict, total=False):
    """One of the saga's characters living in the town, from the season
    he came to live there."""

    character_id: Required[str]
    since_year: int | None
    since_season: str
    note: str


def charter_lords(neighbour: Neighbour) -> list[CharterLord]:
    return cast(list[CharterLord], details_list(neighbour, "charter_lords"))


def terms(neighbour: Neighbour) -> CharterTerms:
    """The charter's terms (empty until first edited)."""
    found = neighbour.details.get("charter_terms")
    if found is None:
        return {}
    if not isinstance(found, dict):
        raise ValueError(f"A town's charter terms should be a mapping, not {found!r}.")
    return cast(CharterTerms, found)


def citizens(neighbour: Neighbour) -> list[Citizen]:
    return cast(list[Citizen], details_list(neighbour, "citizens"))


def _hold(entry: CharterLord) -> str:
    return entry.get("hold") or "Sole"


# -- what the charter gives --


def is_city(neighbour: Neighbour) -> bool:
    """Whether the town is a city: one given the right to call itself so
    (pp. 7-8), or as large as one."""
    if neighbour.details.get("city"):
        return True
    people = towns.population(neighbour)
    return people is not None and towns.size(people) == "City"


def normal_aura(neighbour: Neighbour) -> int:
    """The Divine aura a town or a city has without a charter's say: 3
    (Definitive Edition p. 418)."""
    return CITY_AURA if is_city(neighbour) else TOWN_AURA


#: The old one-word charter field (towns.CHARTERS) as a lord's kind.
_OLD_KINDS = {"Noble lord": "Noble", "Church": "Church", "Faerie": "Faerie"}


def holder_kind(neighbour: Neighbour) -> str:
    """The kind of lord holding the charter: Noble, Church, Faerie or
    Demon when every holder is of that kind, "Shared" for a charter held
    by lords of different kinds, "" for none. With no lords listed, the
    town's Charter field says."""
    holders = [e for e in charter_lords(neighbour) if _hold(e) in HOLDING]
    if not holders:
        return _OLD_KINDS.get(neighbour.details.get("charter") or "", "")
    kinds = {e.get("kind") or "Noble" for e in holders}
    return kinds.pop() if len(kinds) == 1 else "Shared"


def walls_aura(neighbour: Neighbour) -> tuple[int, str]:
    """The Divine aura within the walls, and why."""
    normal = normal_aura(neighbour)
    place = "a city's" if normal == CITY_AURA else "a town's"
    if terms(neighbour).get("church_holds"):
        return CHURCH_AURA, f"the Church holds the charter ({CG} p. 10)"
    kind = holder_kind(neighbour)
    if kind == "Church":
        return CHURCH_AURA, f"an ecclesiastical charter ({CG} p. 10)"
    if kind == "Faerie":
        return FAERIE_AURA, (
            f"a faerie charter ({CG} p. 11); a stronger Faerie aura may swamp it"
        )
    if kind == "Shared":
        return normal, f"{place} normal aura: no one Church lord holds it"
    return normal, f"{place} normal aura (Definitive Edition p. 418)"


def demons(neighbour: Neighbour) -> list[CharterLord]:
    return [e for e in charter_lords(neighbour) if e.get("kind") == "Demon"]


def pawns(neighbour: Neighbour) -> int:
    found = terms(neighbour).get("pawns")
    return CHARTER_PAWNS if found is None else int(found)


def connected(neighbour: Neighbour) -> bool:
    """Whether the charter's sympathetic connections stand: extracting its
    vis destroys them (p. 9)."""
    return not terms(neighbour).get("vis_taken")


# -- citizens --


def resident_since(entry: Citizen) -> str:
    year = entry.get("since_year")
    if year is None:
        return ""
    return f"{entry.get('since_season') or 'Spring'} {year}"


def citizen_from(entry: Citizen) -> str:
    """When a year and a day of residence makes him a citizen: the same
    season of the next year (the day passes within it)."""
    year = entry.get("since_year")
    if year is None:
        return ""
    return f"{entry.get('since_season') or 'Spring'} {year + 1}"


def is_citizen(saga: Saga, entry: Citizen) -> bool:
    """Whether he has lived there a year and a day by now."""
    year = entry.get("since_year")
    if year is None:
        return False
    began = season_order(season=entry.get("since_season") or "Spring", year=year)
    now = season_order(season=saga.current_season, year=saga.current_year)
    return now - began >= len(SEASONS)


def is_cleric(character: Character) -> bool:
    return any(vf.vf_id in CLERICS for vf in character.virtues_flaws)


def _name(saga: Saga, entry: Citizen) -> str:
    character = saga.character(entry["character_id"])
    return character.name if character is not None else "(a character no longer here)"


def homes_of(saga: Saga, character_id: str) -> list[Neighbour]:
    """The towns listing `character_id` among their citizens."""
    return [
        n
        for n in saga.neighbours
        if any(c["character_id"] == character_id for c in n.details.get("citizens", []))
    ]


def move_citizen(saga: Saga, town: Neighbour, character_id: str) -> list[str]:
    """Take `character_id` off every other town's citizens: becoming a
    citizen of `town` ends the old connection (p. 9). The towns he left."""
    left = []
    for other in homes_of(saga, character_id):
        if other is town:
            continue
        listed = citizens(other)
        listed[:] = [c for c in listed if c["character_id"] != character_id]
        left.append(other.name)
    return left


# -- size and people --


def burgesses(neighbour: Neighbour) -> int | None:
    found = neighbour.details.get("burgesses")
    return int(found) if found else None


def size_class(neighbour: Neighbour) -> str:
    """Small, medium or large town (towns.size), or a city; "" with no
    population."""
    people = towns.population(neighbour)
    if people is None:
        return ""
    return "City" if is_city(neighbour) else towns.size(people)


def occupations(neighbour: Neighbour) -> list[tuple[str, int, int]]:
    """Each occupation's share of the people (p. 24) and how many that is;
    a city counts as a large town."""
    people = towns.population(neighbour)
    if people is None:
        return []
    row = OCCUPATIONS.get(size_class(neighbour), OCCUPATIONS["Large town"])
    return [
        (name, share, people * share // 100)
        for name, share in zip(OCCUPATION_NAMES, row, strict=True)
    ]


def officials(neighbour: Neighbour) -> list[tuple[str, str]]:
    """The town's officials, each line of its Officials "Title: who"."""
    found = []
    for line in str(neighbour.details.get("officials") or "").splitlines():
        if not line.strip():
            continue
        title, _, who = line.partition(":")
        found.append((title.strip(), who.strip()))
    return found


# -- the Lords list --


def lords_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Lords ({len(charter_lords(neighbour))})"


def lords_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows = [
        [
            e["lord"],
            e.get("kind") or "Noble",
            HOLDS.get(_hold(e), HOLDS["Sole"])[0],
            e.get("share", ""),
            "" if e.get("since") is None else str(e.get("since")),
        ]
        for e in charter_lords(neighbour)
    ]
    return Grid(
        ["Lord", "Kind", "Holds it", "Share", "Since"],
        rows,
        list(range(len(rows))),
        "No charter lord listed: whoever claims the land grants it (p. 9).",
        caps=[34, 7, 17, 14, 0],
        stretch=0,
    )


def lord_info(saga: Saga, neighbour: Neighbour, row: int) -> str:
    listed = charter_lords(neighbour)
    if row >= len(listed):
        return ""
    e = listed[row]
    kind = e.get("kind") or "Noble"
    hold, meaning = HOLDS.get(_hold(e), HOLDS["Sole"])
    head = " · ".join(
        part
        for part in (
            kind,
            hold,
            f"{escape(e.get('share', ''))} of the revenue" if e.get("share") else "",
            f"since {e.get('since')}" if e.get("since") is not None else "",
        )
        if part
    )
    lines = [f"[i]{head}[/]"]
    if e.get("note"):
        lines.append(escape(e.get("note", "")))
    lines.append(f"[$label]{hold}:[/] {meaning}")
    if strength := strength_line(saga, e):
        lines.append(strength)
    if kind == "Church":
        lines.append(
            f"[$label]Church:[/] a charter the Church holds gives the walls a "
            f"Divine aura of {CHURCH_AURA}, one higher than a town's, and "
            f"clerics rarely become citizens ({CG} p. 10)."
        )
    elif kind == "Faerie":
        lines.append(
            "[$label]Faerie:[/] may ask mortal wives or festivals for its tax "
            f"(p. 12), test the town's officials at its court, and lower the "
            f"walls' aura to 1 ({CG} p. 11)."
        )
    elif kind == "Demon":
        lines.append(
            f"[$label]Demon:[/] Infernal Might {DEMON_MIGHT} (Mentem); may take "
            f"the tithe or ask worship ({CG} pp. 11-12)."
        )
        lines += [
            f"{BULLET} {name}: {what}"
            for key, name, what in DEMON_SERVICES
            if e.get(key)
        ] or ["[dim]No services offered yet.[/]"]
    return "\n".join(lines)


def lord_fields(
    _saga: Saga, _neighbour: Neighbour, entry: CharterLord | None
) -> list[DialogField]:
    e = entry or {}

    def demon(values: dict[str, Any]) -> bool:
        return values.get("kind") == "Demon"

    return [
        DialogField(
            "lord",
            "Lord",
            "text",
            e.get("lord", ""),
            required=True,
            placeholder="e.g. the Bishop of Laon",
        ),
        DialogField(
            "kind",
            "Kind",
            "select",
            e.get("kind", "Noble"),
            options=pairs(LORD_KINDS),
            required=True,
        ),
        DialogField(
            "hold",
            "Holds it",
            "select",
            e.get("hold", "Sole"),
            options=[(label, key) for key, (label, _) in HOLDS.items()],
            required=True,
            hint="Shared: paragium, nobles granting together (p. 10); Rival: a "
            "contested claim; Parallel: a secret demonic charter (p. 11).",
        ),
        DialogField(
            "share",
            "Share of the revenue",
            "text",
            e.get("share", ""),
            placeholder="e.g. half, the Rhine toll",
        ),
        DialogField("since", "Since (year)", "optint", e.get("since")),
        DialogField("note", "Note", "text", e.get("note", "")),
        *(
            DialogField(key, name, "check", bool(e.get(key)), hint=what, show_if=demon)
            for key, name, what in DEMON_SERVICES
        ),
        *_strength_fields(_saga, e),
    ]


def _strength_fields(saga: Saga, e: CharterLord | dict[str, Any]) -> list[DialogField]:
    """The charter's two Charter Strengths, typed in, while the saga uses
    the optional rule (Transforming Mythic Europe p. 36)."""
    if not options.is_on(saga, options.CHARTER_STRENGTH):
        return []
    return [
        DialogField(
            "superior_strength",
            "Lord's Charter Strength",
            "optint",
            e.get("superior_strength"),
            hint="Blank until drafted: More's Draft the Charter rolls it.",
        ),
        DialogField(
            "subordinate_strength",
            "Town's Charter Strength",
            "optint",
            e.get("subordinate_strength"),
        ),
        DialogField(
            "in_england",
            "In England",
            "check",
            bool(e.get("in_england")),
            hint="Its notaries use Common Law, not Civil and Canon Law (p. 36).",
        ),
    ]


#: An English charter, as the lord's details say it (TME p. 36).
ENGLISH = "; in England, Common Law"


def strength_line(saga: Saga, e: CharterLord) -> str:
    """The charter's two Charter Strengths as a line of markup, while the
    saga uses the optional rule; "" otherwise."""
    if not options.is_on(saga, options.CHARTER_STRENGTH):
        return ""

    def shown(key: str) -> str:
        value = e.get(key)
        return "not drafted" if value is None else str(value)

    line = (
        f"[$label]Charter Strength:[/] the lord's {shown('superior_strength')}, "
        f"the town's {shown('subordinate_strength')}"
        f"{ENGLISH if e.get('in_england') else ''} (TME p. 36)"
    )
    if e.get("loophole"):
        line += f"\n[$label]Loophole:[/] {escape(str(e.get('loophole')))}"
    return line


def lord_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        neighbour,
        "charter_lords",
        "Charter Lord",
        lord_fields,
        lambda e: e["lord"],
    )


# -- the Terms block --


def _tick(held: bool, words: str, note: str = "") -> str:
    tail = f" [dim]{escape(note)}[/]" if note else ""
    if held:
        return f"[$text-success]{BULLET}[/] {escape(words)}{tail}"
    return f"[dim]– {escape(words)}[/]"


def terms_facts(_saga: Saga, neighbour: Neighbour) -> list[Fact]:
    t = terms(neighbour)
    granted = t.get("granted")
    people = burgesses(neighbour)
    return [
        Fact("Charter family", t.get("family", "")),
        Fact("Granted", "" if granted is None else str(granted)),
        Fact("Burgesses", "" if people is None else f"{people:,}"),
    ]


def privilege_lines(neighbour: Neighbour) -> list[str]:
    t = cast(dict[str, Any], terms(neighbour))
    lines = []
    for p in PRIVILEGES:
        note = str(t.get(p.note) or "") if p.note else ""
        if p.key == "tax" and t.get("tax") and not note:
            note = f"{TYPICAL_TAX} ({CG} p. 12)"
        lines.append(_tick(bool(t.get(p.key)), p.name, note))
    return lines


def terms_columns(_saga: Saga, neighbour: Neighbour) -> list[str]:
    lines = privilege_lines(neighbour)
    half = (len(lines) + 1) // 2
    return ["\n".join(lines[:half]), "\n".join(lines[half:])]


def terms_fields(neighbour: Neighbour) -> list[DialogField]:
    t = cast(dict[str, Any], terms(neighbour))
    found = [
        DialogField(
            "family",
            "Charter family",
            "text",
            t.get("family", ""),
            hint=f"The law it shares with other towns: {FAMILIES} (pp. 12-14).",
        ),
        DialogField("granted", "Granted (year)", "optint", t.get("granted")),
    ]
    for p in PRIVILEGES:
        found.append(DialogField(p.key, p.name, "check", bool(t.get(p.key))))
        if p.note:
            found.append(
                DialogField(
                    p.note,
                    f"{p.name}: what",
                    "text",
                    t.get(p.note, TYPICAL_TAX if p.key == "tax" else ""),
                    placeholder=p.hint,
                    show_if=lambda values, key=p.key: bool(values.get(key)),
                )
            )
    return found


def _update_terms(neighbour: Neighbour, values: dict[str, Any]) -> None:
    neighbour.details.setdefault("charter_terms", {}).update(values)


def edit_terms(_saga: Saga, neighbour: Neighbour) -> Command:
    return Form(
        "Edit the Charter's Terms",
        lambda: terms_fields(neighbour),
        lambda values: _update_terms(neighbour, values),
        help_id=CHARTER_TERMS_SECTION,
    )


# -- the What It Gives block --


def gives_text(_saga: Saga, neighbour: Neighbour) -> str:
    aura, why = walls_aura(neighbour)
    rows: list[tuple[str, str]] = [
        (
            "Divine aura",
            f"[b]{aura}[/] within the walls: {why}; churches keep their own "
            f"[dim]({CG} pp. 10-11)[/]",
        )
    ]
    found = demons(neighbour)
    if found:
        for demon in found:
            services = [name for key, name, _ in DEMON_SERVICES if demon.get(key)]
            rows.append(
                (
                    "Demon's charter",
                    f"{escape(demon['lord'])}, Infernal Might [b]{DEMON_MIGHT}[/] "
                    f"(Mentem): "
                    + (", ".join(services).lower() if services else "no services yet")
                    + f" [dim]({CG} p. 11)[/]",
                )
            )
        for key, name, what in DEMON_SERVICES:
            if any(d.get(key) for d in found):
                rows.append((name, what))
    else:
        rows.append(
            (
                "Demon's charter",
                f"[dim]none: one would have Might {DEMON_MIGHT} and offer relief "
                f"from disease, help for merchants or dangerous labor ({CG} p. 11)[/]",
            )
        )
    count = pawns(neighbour)
    rows.append(
        (
            "Pawn",
            (
                f"[b]{count}[/] pawn{'' if count == 1 else 's'} of Rego vis, "
                f"Divine-tainted, in the signed charter [dim]({CG} p. 9)[/]"
            )
            if connected(neighbour)
            else "[dim]taken from the charter: its sympathetic connections are "
            f"destroyed ({CG} p. 9)[/]",
        )
    )
    return aligned(rows)


def gives_fields(neighbour: Neighbour) -> list[DialogField]:
    t = terms(neighbour)
    return [
        DialogField(
            "church_holds",
            "The Church holds the charter",
            "check",
            bool(t.get("church_holds")),
            hint="For a shared charter the Church holds: the walls' aura is "
            f"{CHURCH_AURA}, one higher than a town's.",
        ),
        DialogField(
            "pawns",
            "Pawns of vis in it",
            "optint",
            t.get("pawns"),
            hint="Most charters hold one pawn of Rego vis; very large towns more.",
        ),
        DialogField(
            "vis_taken",
            "Its vis was taken",
            "check",
            bool(t.get("vis_taken")),
            hint="Extracting the vis destroys the charter's sympathetic "
            "connections (p. 9).",
        ),
    ]


def _gives_problem(values: dict[str, Any]) -> str | None:
    if (values.get("pawns") or 0) < 0:
        return "Pawns can't be fewer than none."
    return None


def edit_gives(_saga: Saga, neighbour: Neighbour) -> Command:
    return Form(
        "Edit What the Charter Gives",
        lambda: gives_fields(neighbour),
        lambda values: _update_terms(neighbour, values),
        validate=_gives_problem,
        help_id=CHARTER_GIVES_SECTION,
    )


# -- the Citizens list --


def citizens_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Citizens ({len(citizens(neighbour))})"


def citizens_grid(saga: Saga, neighbour: Neighbour) -> Grid:
    rows, styles = [], {}
    linked = connected(neighbour)
    for i, entry in enumerate(citizens(neighbour)):
        now = is_citizen(saga, entry)
        rows.append(
            [
                _name(saga, entry),
                resident_since(entry),
                citizen_from(entry),
                ("+1 multiplier" if linked else "severed") if now else "not yet",
            ]
        )
        if now and linked:
            styles[(i, 3)] = "$text-success"
    return Grid(
        ["Citizen", "Resident since", "Citizen from", "Penetration"],
        rows,
        list(range(len(rows))),
        "None of the saga's characters lives here.",
        styles=styles,
        caps=[26, 14, 14, 0],
    )


def citizen_info(saga: Saga, neighbour: Neighbour, row: int) -> str:
    listed = citizens(neighbour)
    if row >= len(listed):
        return ""
    entry = listed[row]
    character = saga.character(entry["character_id"])
    lines = []
    if entry.get("since_year") is None:
        lines.append("[i]When he came to live here isn't recorded.[/]")
    elif is_citizen(saga, entry):
        lines.append(
            f"[i]Resident since {resident_since(entry)}: a citizen since "
            f"{citizen_from(entry)}, after a year and a day ({CG} p. 9).[/]"
        )
    else:
        lines.append(
            f"[i]Resident since {resident_since(entry)}: a citizen in "
            f"{citizen_from(entry)}, a year and a day after he came ({CG} p. 9).[/]"
        )
    if connected(neighbour):
        lines.append(
            "[$label]Sympathetic connection:[/] +1 to the Penetration multiplier "
            "against everyone under the same charter, its family's towns too, "
            "while he is a citizen."
        )
    else:
        lines.append(
            "[$text-error]The charter's vis was taken: its connections are gone.[/]"
        )
    if character is not None and is_cleric(character):
        lines.append(
            "[$text-warning]A cleric: canon law rarely lets him be a citizen "
            f"({CG} pp. 9-10).[/]"
        )
    if entry.get("note"):
        lines.append(escape(entry.get("note", "")))
    lines.append("[dim]Becoming a citizen of another town ends this link.[/]")
    return "\n".join(lines)


def citizen_fields(
    saga: Saga, neighbour: Neighbour, entry: Citizen | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "character_id",
            "Character",
            "select",
            e.get("character_id"),
            options=[(escape(c.name), c.id) for c in saga.characters],
            required=True,
        ),
        DialogField(
            "since_season",
            "Came to live here (season)",
            "select",
            e.get("since_season") or saga.current_season,
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField(
            "since_year",
            "Came to live here (year)",
            "optint",
            e.get("since_year", saga.current_year),
            hint="A year and a day of residence makes him a citizen (p. 9).",
        ),
        DialogField("note", "Note", "text", e.get("note", "")),
    ]


def citizen_live(saga: Saga, neighbour: Neighbour) -> Any:
    def live(values: dict[str, Any]) -> str:
        chosen = values.get("character_id")
        if not chosen:
            return ""
        elsewhere = [n.name for n in homes_of(saga, chosen) if n is not neighbour]
        if not elsewhere:
            return ""
        return (
            f"[$text-warning]Listed in {escape(', '.join(elsewhere))}: becoming a "
            "citizen here ends that link (p. 9).[/]"
        )

    return live


def citizen_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    def move() -> None:
        for entry in list(citizens(neighbour)):
            move_citizen(saga, neighbour, entry["character_id"])

    base = list_ops(
        saga,
        neighbour,
        "citizens",
        "Citizen",
        citizen_fields,
        lambda e: _name(saga, e),
        after=move,
    )
    live = citizen_live(saga, neighbour)

    def with_live(form: Command) -> Command:
        return replace(form, live=live) if isinstance(form, Form) else form

    add, edit = base.add, base.edit
    assert add is not None and edit is not None
    return SectionOps(
        add=lambda: with_live(add()),
        edit=lambda index: with_live(edit(index)),
        remove=base.remove,
        rows=base.rows,
    )


# -- the Size and People block --


def people_facts(_saga: Saga, neighbour: Neighbour) -> list[Fact]:
    people = towns.population(neighbour)
    d = neighbour.details
    many = burgesses(neighbour)
    return [
        Fact(
            "Population",
            "" if people is None else f"{people:,} ({size_class(neighbour).lower()})",
        ),
        Fact("Burgesses", "" if many is None else f"{many:,}"),
        Fact("Council", f"{d['council']} seats" if d.get("council") else ""),
        Fact("Magistrates", str(d["magistrates"]) if d.get("magistrates") else ""),
    ]


def people_columns(_saga: Saga, neighbour: Neighbour) -> list[str]:
    jobs = occupations(neighbour)
    work = (
        aligned([(name, f"{count:,} ({share}%)") for name, share, count in jobs])
        if jobs
        else "[dim]A population shows how its people earn their living.[/]"
    )
    held = officials(neighbour)
    office = (
        aligned([(title, escape(who) or "[dim]—[/]") for title, who in held])
        if held
        else f"[dim]None recorded: {OFFICIAL_TITLES} (p. 13).[/]"
    )
    return [
        f"[b]Occupations[/] [dim]({CG} p. 24)[/]\n{work}",
        f"[b]Officials[/] [dim]({CG} pp. 13-14)[/]\n{office}",
    ]


def people_fields(neighbour: Neighbour) -> list[DialogField]:
    d = neighbour.details
    return [
        DialogField(
            "population",
            "Population",
            "optint",
            d.get("population"),
            hint="Most towns hold only a few hundred (p. 31).",
        ),
        DialogField(
            "burgesses",
            "Burgesses",
            "optint",
            d.get("burgesses"),
            hint="The citizens under the charter.",
        ),
        DialogField("city", "A city by right", "check", bool(d.get("city"))),
        DialogField("council", "Council (seats)", "optint", d.get("council")),
        DialogField(
            "magistrates",
            "Magistrates",
            "optint",
            d.get("magistrates"),
            hint="An average town has up to half a dozen (p. 29).",
        ),
        DialogField(
            "officials",
            "Officials",
            "area",
            d.get("officials", ""),
            hint=f"One a line, as Title: who. The book's titles: {OFFICIAL_TITLES}.",
        ),
    ]


def _people_problem(values: dict[str, Any]) -> str | None:
    for key, label in (
        ("population", "A population"),
        ("burgesses", "Burgesses"),
        ("council", "A council"),
        ("magistrates", "Magistrates"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{label} can't be fewer than none."
    return None


def edit_people(_saga: Saga, neighbour: Neighbour) -> Command:
    return Form(
        "Edit the Town's Size and People",
        lambda: people_fields(neighbour),
        lambda values: neighbour.details.update(values),
        validate=_people_problem,
        help_id=TOWN_PEOPLE_SECTION,
    )


CHARTER_TAB = KindTab(
    "Charter",
    "tab-nb-charter",
    (
        KindList(CHARTER_LORDS_SECTION, lords_title, lords_grid, lord_ops, lord_info),
        KindList(
            CITIZENS_SECTION, citizens_title, citizens_grid, citizen_ops, citizen_info
        ),
    ),
    blocks=(
        KindBlock(
            CHARTER_TERMS_SECTION,
            "Terms",
            edit=edit_terms,
            edit_label="Edit Terms",
            facts=terms_facts,
            after=CHARTER_LORDS_SECTION,
            columns=terms_columns,
        ),
        KindBlock(
            CHARTER_GIVES_SECTION,
            "What It Gives",
            gives_text,
            edit=edit_gives,
            after=CHARTER_LORDS_SECTION,
        ),
        KindBlock(
            TOWN_PEOPLE_SECTION,
            "Size and People",
            edit=edit_people,
            facts=people_facts,
            after=CITIZENS_SECTION,
            columns=people_columns,
        ),
    ),
    icon="lab_text",
    panel="[dim]Choose a lord or a citizen to see his hold or his link.[/]",
)


# -- the covenant's own charter (p. 11) --

#: The Minor Boon of a covenant that is a chartered town, and the Major
#: Hook of one that grants charters to towns on its land (p. 11).
CHARTERED_TOWN = "covbh_boon_minor_chartered_town"
CHARTER_LORD = "covbh_hook_major_charter_lord"


def has_boon_hook(covenant: Covenant, vf_id: str) -> bool:
    return any(bh.vf_id == vf_id for bh in covenant.boons_hooks)


def charter_of(covenant: Covenant) -> Neighbour:
    """The covenant's own charter as a town record (an Adapter): its
    details are the covenant's charter itself, so what the town's lists
    and forms change is kept on the covenant."""
    return Neighbour(
        id=f"charter-{covenant.id}",
        name=covenant.name,
        kind="town",
        details=covenant.charter,
    )


def chartered_towns(
    saga: Saga, covenant: Covenant
) -> list[tuple[Neighbour, CharterLord]]:
    """The towns listing the covenant among their charter lords, by its
    name, with that entry."""
    wanted = covenant.name.strip().casefold()
    return [
        (town, entry)
        for town in saga.neighbours
        for entry in town.details.get("charter_lords", [])
        if str(entry.get("lord", "")).strip().casefold() == wanted
    ]


def chartered_towns_text(saga: Saga, covenant: Covenant) -> str:
    found = chartered_towns(saga, covenant)
    lines = [
        f"{BULLET} [b]{escape(town.name)}[/]: "
        + HOLDS.get(_hold(entry), HOLDS["Sole"])[0].lower()
        + (f", {escape(entry.get('share', ''))}" if entry.get("share") else "")
        + (f", since {entry.get('since')}" if entry.get("since") is not None else "")
        for town, entry in found
    ]
    if not lines:
        lines.append(
            f"[dim]No town lists {escape(covenant.name)} among its charter lords: "
            "add it as a lord on the town's Charter tab.[/]"
        )
    lines.append(
        "[dim]Granting charters is interference in the mundane: neighbouring "
        f"lords, petitions and revolts, and the Quaesitores, follow ({CG} p. 11).[/]"
    )
    return "\n".join(lines)


def covenant_terms_form(saga: Saga, covenant: Covenant) -> Command:
    form = edit_terms(saga, charter_of(covenant))
    return (
        replace(form, help_id=COV_CHARTER_TERMS_SECTION)
        if isinstance(form, Form)
        else form
    )


def covenant_charter_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The covenant's own charter's lords and terms, edited as a town's."""
    return {
        COV_CHARTER_LORDS_SECTION: lord_ops(saga, charter_of(covenant)),
        COV_CHARTER_TERMS_SECTION: SectionOps(
            edit=lambda _row: covenant_terms_form(saga, covenant)
        ),
    }
