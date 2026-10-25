"""The Transylvanian Tribunal's customs (Against the Dark: The
Transylvanian Tribunal). Its magi live in oppida, the places other
Tribunals call covenants, and each magus belongs to one of the five
legal covenants the Sundering left it, which serve as privileges: what
the magus may do in the Tribunal (stand for office, take apprentices,
trade vis). The members of one oppidum hold different privileges by
rule, so the privilege belongs to the magus, not the oppidum. Each
oppidum has one or two aediles from among its magi.

Kept in the package's data: "members", each {"character_id",
"privilege" (a key of PRIVILEGES), "office"}; and "aediles", {covenant
id: [character id, ...]}. Saves made before privileges belonged to the
magus kept "classes", {covenant id: class}; members() hands each of that
oppidum's magi its class the first time it is read."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Character, Covenant, Saga, Tribunal
from ..sections import PRIVILEGES_SECTION
from . import (
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "transylvania"


@dataclass(frozen=True)
class Privilege:
    """One of the five legal covenants, as the privilege it grants."""

    name: str
    covenant: str
    allows: str

    @property
    def label(self) -> str:
        """ "Cives (Coeris)"."""
        return f"{self.name} ({self.covenant})"


#: The privileges, cives first (the book ranks them no further), each
#: with the legal covenant it belongs to and what it allows.
PRIVILEGES: dict[str, Privilege] = {
    "cives": Privilege(
        "Cives", "Coeris", "any office, Praeco too; apprentices; chooses an aedile"
    ),
    "socii": Privilege(
        "Socii", "Domostron", "any office but Praeco; must not provoke Wizard War"
    ),
    "coloniae": Privilege(
        "Coloniae", "Asclepius", "settlers: no office but aedile; apprentices by leave"
    ),
    "hospites": Privilege(
        "Hospites",
        "Diodorus",
        "hired specialists: office, apprentices and more by leave",
    ),
    "foederati": Privilege(
        "Foederati",
        "Pannonia",
        "keep their own customs; trade with outsiders by leave",
    ),
}

#: An oppidum has at most this many aediles.
AEDILES = 2


def _privilege_key(value: str) -> str:
    """A privilege's key from its key or its name ("Cives"), or ""."""
    key = value.strip().casefold()
    return key if key in PRIVILEGES else ""


def residents(saga: Saga, covenant: Covenant) -> list[Character]:
    """The magi who live in the oppidum."""
    return [
        c for c in saga.characters if c.type == "magus" and c.covenant_id == covenant.id
    ]


def _carry_over_classes(saga: Saga, tribunal: Tribunal, found: list) -> None:
    """Give each magus of an oppidum that a save gave a class that class,
    unless they already have an entry."""
    classes = data(tribunal, KEY).pop("classes", None)
    if not isinstance(classes, dict):
        return
    entered = {m.get("character_id") for m in found}
    for covenant_id, name in classes.items():
        covenant = saga.covenant(covenant_id)
        key = _privilege_key(str(name))
        if covenant is None or not key:
            continue
        for magus in residents(saga, covenant):
            if magus.id not in entered:
                found.append({"character_id": magus.id, "privilege": key})
                entered.add(magus.id)


def members(saga: Saga, tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each magus's privilege and office, in the order entered."""
    found = entries(tribunal, KEY, "members")
    if "classes" in data(tribunal, KEY):
        _carry_over_classes(saga, tribunal, found)
    return found


def entry_of(saga: Saga, tribunal: Tribunal, character_id: str) -> dict | None:
    """The magus's entry, or None."""
    for entry in members(saga, tribunal):
        if entry.get("character_id") == character_id:
            return entry
    return None


def privilege_label(entry: dict[str, Any] | None) -> str:
    """ "Cives (Coeris)", or "" for none entered."""
    privilege = PRIVILEGES.get((entry or {}).get("privilege", ""))
    return privilege.label if privilege is not None else ""


# -- the aediles --


def aediles(tribunal: Tribunal) -> dict[str, list[str]]:
    """Each oppidum's aediles, by covenant id."""
    found = data(tribunal, KEY).setdefault("aediles", {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's aediles should be a mapping, not {found!r}.")
    return found


def aediles_of(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> list[Character]:
    """The oppidum's aediles who are still in the saga."""
    chosen = (saga.character(i) for i in aediles(tribunal).get(covenant.id, []))
    return [c for c in chosen if c is not None]


def aediles_text(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    return ", ".join(c.name for c in aediles_of(saga, tribunal, covenant))


def aedile_fields(
    saga: Saga, _tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """An oppidum's own form: its aediles, from the magi who live there."""
    magi = residents(saga, covenant) if covenant is not None else []
    chosen = aediles(_tribunal).get(covenant.id, []) if covenant is not None else []
    options = [(escape(c.name), c.id) for c in magi]
    needed = aediles_needed(saga, _tribunal, covenant) if covenant is not None else None
    due = f"; it should have {needed}." if needed is not None else "."
    hint = (
        "One of the magi who live here, from the group that isn't dominant "
        "(cives against the rest)" + due
        if magi
        else "Its magi choose the aediles: give it magi first."
    )
    return [
        DialogField(
            f"aedile_{n}",
            "Aedile" if n == 0 else "Second aedile",
            "select",
            chosen[n] if n < len(chosen) else None,
            options=options,
            allow_blank=True,
            placeholder="(none chosen)",
            hint=hint if n == 0 else "Some oppida have two.",
        )
        for n in range(AEDILES)
    ]


def save_aediles(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    chosen: list[str] = []
    for n in range(AEDILES):
        value = values.get(f"aedile_{n}")
        if value and value not in chosen:
            chosen.append(value)
    if chosen:
        aediles(tribunal)[ident] = chosen
    else:
        aediles(tribunal).pop(ident, None)


def aedile_of(saga: Saga, tribunal: Tribunal, character_id: str) -> Covenant | None:
    """The oppidum the magus is an aedile of, or None."""
    for covenant_id, chosen in aediles(tribunal).items():
        if character_id in chosen:
            return saga.covenant(covenant_id)
    return None


# -- offices and oppida, by privilege --

#: The offices the package knows by name.
PRAECO, AEDILE, CURATOR = "Praeco", "Aedile", "Curator of Tablinum"


def office_rule(privilege: str, office: str) -> tuple[str, bool]:
    """What a privilege says of holding `office`: the words, and whether
    they forbid it (False: it needs the Praeco's leave, or is allowed
    with "" for words). Only a cives may be Praeco, a socius may hold
    any office but Praeco, a colona none but aedile, a hospes must seek
    leave, and a foederatus may stand for any (Against the Dark pp.
    15-18); the Curator of Tablinum must be a cives and a master when
    appointed (p. 58)."""
    office_key = office.strip().casefold()
    if office_key == CURATOR.casefold() and privilege != "cives":
        return "The Curator of Tablinum must be a cives (Against the Dark p. 58).", True
    if privilege == "coloniae" and office_key != AEDILE.casefold():
        return f"A colona may hold no office but aedile, not {office}.", True
    if privilege == "socii" and office_key == PRAECO.casefold():
        return "Only a cives may be Praeco: a socius may hold any office but it.", True
    # An aedile is chosen by the oppidum's dominant group, not sought.
    if privilege == "hospites" and office_key and office_key != AEDILE.casefold():
        return (
            f"{office}: a hospes holds office only by the Praeco's leave "
            "(Against the Dark p. 16).",
            False,
        )
    return "", False


def magus_office_problem(
    saga: Saga, tribunal: Tribunal, character_id: str, office: str
) -> str:
    """Why the magus's privilege forbids `office` ("": it doesn't, or no
    privilege is entered)."""
    entry = entry_of(saga, tribunal, character_id)
    privilege = (entry or {}).get("privilege", "")
    if not privilege:
        return ""
    words, refuses = office_rule(privilege, office)
    return f"{_name(saga, character_id)}: {words}" if refuses else ""


def office_notes(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> list[str]:
    """What the magus's privilege says of each office he holds: those it
    forbids, and those he holds by leave."""
    privilege = entry.get("privilege", "")
    if not privilege:
        return []
    found = []
    for office in [o.strip() for o in offices(saga, tribunal, entry).split(",")]:
        if office and office != "Presiding Quaesitor":
            words, _refuses = office_rule(privilege, office)
            if words:
                found.append(words)
    return found


def _privileges_of(saga: Saga, tribunal: Tribunal, magi: list[Character]) -> list[str]:
    return [(entry_of(saga, tribunal, m.id) or {}).get("privilege", "") for m in magi]


def aediles_needed(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> int | None:
    """How many aediles the oppidum should have: two where its cives and
    its other magi are as many, else one (Against the Dark p. 15, whose
    "even numbers" is read as equal ones); None while a resident's
    privilege isn't entered."""
    privileges = _privileges_of(saga, tribunal, residents(saga, covenant))
    if not privileges or not all(privileges) or covenant.unnamed_magi:
        return None
    cives = privileges.count("cives")
    return 2 if cives * 2 == len(privileges) else 1


def oppidum_problems(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> list[str]:
    """Where the oppidum breaks the Tribunal's rulings on oppida: at least
    two members, at least one cives, not all of one House (Against the
    Dark p. 15), and its aediles from the group that isn't dominant,
    cives against the rest (p. 16)."""
    magi = residents(saga, covenant)
    found: list[str] = []
    if not magi:
        return found
    if len(magi) + covenant.unnamed_magi < 2:
        found.append("fewer than two members")
    privileges = _privileges_of(saga, tribunal, magi)
    known = all(privileges) and not covenant.unnamed_magi
    if known and len(magi) >= 2 and len({m.hermetic.house for m in magi}) == 1:
        found.append("all of one House")
    if known and "cives" not in privileges:
        found.append("no cives")
    needed = aediles_needed(saga, tribunal, covenant)
    chosen = aediles_of(saga, tribunal, covenant)
    if needed is not None and chosen and len(chosen) != needed:
        found.append(f"{needed} aedile{'s' if needed > 1 else ''} due")
    if known and needed == 1:
        dominant_cives = privileges.count("cives") * 2 > len(privileges)
        for aedile in chosen:
            entry = entry_of(saga, tribunal, aedile.id) or {}
            if (entry.get("privilege") == "cives") == dominant_cives:
                found.append(f"{aedile.name} is of the dominant group")
    return found


def oppidum_status(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """ "lawful", what the oppidum lacks, or "" with no magi named."""
    if not residents(saga, covenant):
        return ""
    return "; ".join(oppidum_problems(saga, tribunal, covenant)) or "lawful"


# -- the five covenants --


def offices(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> str:
    """The magus's offices: Praeco, Presiding Quaesitor, aedile, and any
    office entered."""
    ident = entry.get("character_id", "")
    found = []
    if ident and ident == tribunal.praeco_id:
        found.append("Praeco")
    if ident and ident == tribunal.quaesitor_id:
        found.append("Presiding Quaesitor")
    if aedile_of(saga, tribunal, ident) is not None:
        found.append("Aedile")
    if entry.get("office"):
        found.append(entry["office"])
    return ", ".join(found)


def _name(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(gone)"


def _rank(entry: dict[str, Any]) -> int:
    keys = list(PRIVILEGES)
    privilege = entry.get("privilege", "")
    return keys.index(privilege) if privilege in keys else len(keys)


def ordered(saga: Saga, tribunal: Tribunal) -> list[int]:
    """The members' indices, by legal covenant and then by name."""
    found = members(saga, tribunal)
    return sorted(
        range(len(found)),
        key=lambda i: (
            _rank(found[i]),
            _name(saga, found[i].get("character_id")).casefold(),
        ),
    )


def members_title(saga: Saga, tribunal: Tribunal) -> str:
    return f"The Five Covenants ({len(members(saga, tribunal))})"


def members_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each magus: the oppidum they live in, their privilege and legal
    covenant, and their offices, grouped by legal covenant."""
    found = members(saga, tribunal)
    order = ordered(saga, tribunal)
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for row, index in enumerate(order):
        entry = found[index]
        character = saga.character(entry.get("character_id"))
        oppidum = saga.covenant(character.covenant_id) if character else None
        label = privilege_label(entry)
        if not label:
            styles[(row, 2)] = "$label"
        rows.append(
            [
                _name(saga, entry.get("character_id")),
                oppidum.name if oppidum is not None else "",
                label or "not entered",
                offices(saga, tribunal, entry),
            ]
        )
    return Grid(
        ["Magus", "Oppidum", "Privilege", "Office"],
        rows,
        list[int | None](order),
        "No magus's privilege recorded: each magus belongs to one of the "
        "five legal covenants, whose privilege says what they may do.",
        styles,
        caps=[20, 16, 22, 0],
        stretch=3,
    )


def _magus_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]


def member_fields(saga: Saga, entry: dict[str, Any] | None) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "character_id",
            "Magus",
            "select",
            e.get("character_id"),
            options=_magus_options(saga),
            required=True,
            hint="A magus of the saga, at any detail.",
        ),
        DialogField(
            "privilege",
            "Privilege",
            "select",
            e.get("privilege"),
            options=[(f"{p.label}: {p.allows}", key) for key, p in PRIVILEGES.items()],
            allow_blank=True,
            placeholder="(not entered)",
            hint="The legal covenant the magus belongs to, agreed with the Praeco.",
        ),
        DialogField(
            "office",
            "Office",
            "text",
            e.get("office", ""),
            placeholder="e.g. Curantis",
            hint="Praeco, Presiding Quaesitor and aedile show by themselves.",
        ),
    ]


def member_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def problem(values: dict[str, Any]) -> str | None:
            other = entry_of(saga, tribunal, values.get("character_id") or "")
            if other is not None and other is not entry:
                name = _name(saga, values.get("character_id"))
                return f"{name} already has a privilege: edit theirs instead."
            privilege, office = values.get("privilege"), values.get("office")
            if privilege and office:
                words, refuses = office_rule(privilege, office)
                if refuses:
                    return words
            ident = values.get("character_id")
            if privilege and ident and ident == tribunal.praeco_id:
                words, refuses = office_rule(privilege, PRAECO)
                if refuses:
                    return f"{_name(saga, ident)} is Praeco: {words}"
            return None

        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if not target.get("privilege"):
                target.pop("privilege", None)
            if entry is None:
                members(saga, tribunal).append(target)

        return Form(
            "Add a Magus's Privilege" if entry is None else "Edit a Privilege",
            lambda: member_fields(saga, entry),
            apply,
            validate=problem,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = members(saga, tribunal)[index]

        def apply() -> None:
            members(saga, tribunal).remove(entry)

        name = escape(_name(saga, entry.get("character_id")))
        return Confirm(f"Delete {name}'s privilege?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(members(saga, tribunal)[index]),
        remove=remove,
        rows=lambda: [
            _name(saga, m.get("character_id")) for m in members(saga, tribunal)
        ],
    )


def magus_facts(
    saga: Saga, tribunal: Tribunal, character: Character
) -> list[tuple[str, str]]:
    """A Transylvanian magus's privilege, for their sheet."""
    entry = entry_of(saga, tribunal, character.id)
    found = [("Privilege", privilege_label(entry) or "(not entered)")]
    found += [("Office", words) for words in office_notes(saga, tribunal, entry or {})]
    return found


TRANSYLVANIA = TribunalPackage(
    KEY,
    "Transylvania",
    customs="Privileges",
    book="AtD",
    place="oppidum",
    places="oppida",
    columns=(
        RosterColumn("Aediles", aediles_text, 18),
        RosterColumn("Oppidum", oppidum_status, 18),
    ),
    tabs=(
        PackageTab(
            "The Five Covenants",
            "tab-trib-privileges",
            (PackageList(PRIVILEGES_SECTION, members_title, members_grid, member_ops),),
        ),
    ),
    about="Its magi live in oppida, and each belongs to one of five legal "
    "covenants, whose privilege (cives, socii, coloniae, hospites, "
    "foederati) says what the magus may do; each oppidum has its aediles.",
    covenant_fields=aedile_fields,
    save_covenant=save_aediles,
    magus_facts=magus_facts,
    office_problem=magus_office_problem,
)

register(TRANSYLVANIA)
