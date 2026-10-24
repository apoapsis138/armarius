"""The Theban Tribunal's customs (The Sundered Eagle: The Theban
Tribunal), in the book's own terms. Its magi are politai (citizens) or
metoikoi (resident foreigners); a polites earns tokens for services to
the community and shards for acts against its unity, and any polites
with a shard may be ostracised. Every magus present votes once, by
voting sigil, politai and metoikoi alike, so the troupe's votes are
counted as under the core rules. Each covenant belongs to one of four
phylai, and the Council of Magistrates (the archai, the archon, the
polemarch and the logothete) holds the Tribunal's offices.

Kept in the package's data: "magi", each {"character_id", "status"
("polites" or "metoikos"), "tokens", "shards", "services",
"ostracised_until", "why"}; "archai", each {"office", "holder_id",
"term_ends", "duties"}; and "phylai", {covenant id: phyle}. Saves made
before the book's terms were used say "liturgies" for services."""

from __future__ import annotations

from typing import Any

from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Covenant, Saga, Tribunal
from ..sections import ARCHAI_SECTION, TOKENS_SECTION
from . import (
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "theban"

#: The four phylai, each with the lands whose covenants belong to it.
PHYLAI: dict[str, str] = {
    "Ionian": "the western mainland: Thessaly, Epiros, the Peloponnese",
    "Aegean": "around the Aegean: Boeotia, Euboea, Macedonia, the northern islands",
    "Kretan": "Candia, the Cyclades, the Dodecanese and southern Nicaea",
    "Propontian": "Thrace, northern Nicaea, Constantinople and the Black Sea",
}

#: A magus's standing in the polity, as the book names it.
STATUSES: dict[str, str] = {
    "polites": "Polites",
    "metoikos": "Metoikos",
}


def magi(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each magus's status, tokens, shards and services, in the order
    entered."""
    found = entries(tribunal, KEY, "magi")
    for entry in found:
        if "liturgies" in entry:
            entry.setdefault("services", entry.pop("liturgies"))
    return found


def archai(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Council of Magistrates' offices, in the order entered."""
    return entries(tribunal, KEY, "archai")


def phylai(tribunal: Tribunal) -> dict[str, str]:
    """Each covenant's phyle, by covenant id."""
    found = data(tribunal, KEY).setdefault("phylai", {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's phylai should be a mapping, not {found!r}.")
    return found


def phyle_of(_saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The covenant's phyle, or "" if none is entered."""
    return phylai(tribunal).get(covenant.id, "")


def is_metoikos(entry: dict[str, Any]) -> bool:
    return entry.get("status") == "metoikos"


def _name(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(gone)"


def ostracised(saga: Saga, entry: dict[str, Any]) -> bool:
    """Whether the magus is ostracised this year."""
    until = entry.get("ostracised_until")
    return until is not None and until >= saga.current_year


def _offices_of(tribunal: Tribunal, character_id: str) -> list[str]:
    return [a["office"] for a in archai(tribunal) if a.get("holder_id") == character_id]


def standing(saga: Saga, tribunal: Tribunal, entry: dict[str, Any]) -> str:
    """The magus's offices, or that they are ostracised and until when."""
    if ostracised(saga, entry):
        return f"Ostracised to {entry['ostracised_until']}"
    return ", ".join(_offices_of(tribunal, entry.get("character_id", "")))


# -- the phylai --


def phyle_field(
    _saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> DialogField:
    return DialogField(
        "phyle",
        "Phyle",
        "select",
        phylai(tribunal).get(covenant.id) if covenant is not None else None,
        options=[(f"{name}: {lands}", name) for name, lands in PHYLAI.items()],
        allow_blank=True,
        placeholder="(not entered)",
        hint="The tribe its magi belong to, set by where the covenant lies.",
    )


def save_phyle(tribunal: Tribunal, covenant: Covenant, value: Any) -> None:
    if value:
        phylai(tribunal)[covenant.id] = value
    else:
        phylai(tribunal).pop(covenant.id, None)


def covenant_phyle_fields(
    saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: its phyle."""
    return [phyle_field(saga, tribunal, covenant)]


def save_covenant_phyle(tribunal: Tribunal, ident: str, values: dict[str, Any]) -> None:
    if "phyle" not in values:
        return
    if values["phyle"]:
        phylai(tribunal)[ident] = values["phyle"]
    else:
        phylai(tribunal).pop(ident, None)


# -- tokens and shards --


def tokens_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Tokens and Shards ({len(magi(tribunal))})"


def tokens_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each magus: their covenant, whether polites or metoikos, their tokens, shards and services, and their standing (an
    office, or ostracism)."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(magi(tribunal)):
        character = saga.character(entry.get("character_id"))
        covenant = saga.covenant(character.covenant_id) if character else None
        if ostracised(saga, entry):
            styles[(index, 6)] = "$text-error"
        if is_metoikos(entry):
            styles[(index, 2)] = "$label"
        rows.append(
            [
                _name(saga, entry.get("character_id")),
                covenant.name if covenant is not None else "",
                STATUSES["metoikos" if is_metoikos(entry) else "polites"],
                str(entry.get("tokens", 0)),
                str(entry.get("shards", 0)),
                str(entry.get("services", 0)),
                standing(saga, tribunal, entry),
            ]
        )
    return Grid(
        ["Magus", "Covenant", "Status", "Tokens", "Shards", "Services", "Standing"],
        rows,
        list(range(len(rows))),
        "No magus's tokens recorded: a polites earns tokens for services to "
        "the community and shards for acts against its unity.",
        styles,
        caps=[20, 14, 8, 6, 6, 8, 0],
    )


def _magus_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]


def token_fields(saga: Saga, entry: dict[str, Any] | None) -> list[DialogField]:
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
            "status",
            "Status",
            "select",
            e.get("status", "polites"),
            options=[
                ("Polites (citizen)", "polites"),
                ("Metoikos (resident foreigner)", "metoikos"),
            ],
            hint="A metoikos is a guest, or a polites who has lost his rights.",
        ),
        DialogField("tokens", "Tokens", "int", e.get("tokens", 0)),
        DialogField("shards", "Shards", "int", e.get("shards", 0)),
        DialogField(
            "services",
            "Services",
            "int",
            e.get("services", 0),
            hint="Services to the community, each earning a token.",
        ),
        DialogField(
            "ostracised_until",
            "Ostracised until (year)",
            "optint",
            e.get("ostracised_until"),
            hint="Leave blank unless the Tribunal has ostracised them.",
        ),
        DialogField("why", "Why", "text", e.get("why", "")),
    ]


def _token_problem(values: dict[str, Any]) -> str | None:
    for key, words in (
        ("tokens", "Tokens"),
        ("shards", "Shards"),
        ("services", "Services"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{words} can't be fewer than none."
    if values.get("status") == "metoikos" and (
        (values.get("tokens") or 0) or (values.get("shards") or 0)
    ):
        return "A metoikos holds no tokens or shards."
    return None


def token_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if entry is None:
                magi(tribunal).append(target)

        return Form(
            "Add a Magus's Tokens" if entry is None else "Edit Tokens and Shards",
            lambda: token_fields(saga, entry),
            apply,
            validate=_token_problem,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = magi(tribunal)[index]

        def apply() -> None:
            magi(tribunal).remove(entry)

        name = escape(_name(saga, entry.get("character_id")))
        return Confirm(f"Delete {name}'s tokens and shards?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(magi(tribunal)[index]),
        remove=remove,
        rows=lambda: [_name(saga, m.get("character_id")) for m in magi(tribunal)],
    )


# -- the Council of Magistrates --


def archai_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"The Council of Magistrates ({len(archai(tribunal))})"


def archai_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each office: who holds it, when their term ends, and its duties."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, office in enumerate(archai(tribunal)):
        holder = office.get("holder_id")
        if not holder:
            styles[(index, 1)] = "$label"
        ends = office.get("term_ends")
        rows.append(
            [
                office["office"],
                _name(saga, holder) if holder else "vacant",
                f"to {ends}" if ends is not None else "",
                office.get("duties", ""),
            ]
        )
    return Grid(
        ["Office", "Holder", "Term", "Duties"],
        rows,
        list(range(len(rows))),
        "No magistrates recorded: the archon, the polemarch, the logothete "
        "and the archai, chosen at each meeting.",
        styles,
        caps=[22, 20, 7, 0],
        stretch=3,
    )


def archon_fields(saga: Saga, office: dict[str, Any] | None) -> list[DialogField]:
    o = office or {}
    return [
        DialogField(
            "office",
            "Office",
            "text",
            o.get("office", ""),
            required=True,
            placeholder="e.g. Polemarch",
        ),
        DialogField(
            "holder_id",
            "Held by",
            "select",
            o.get("holder_id"),
            options=_magus_options(saga),
            allow_blank=True,
            placeholder="(vacant)",
        ),
        DialogField("term_ends", "Term ends (year)", "optint", o.get("term_ends")),
        DialogField(
            "duties",
            "Duties",
            "text",
            o.get("duties", ""),
            placeholder="e.g. Enforces the Tribunal's sentences",
        ),
    ]


def archon_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(office: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = office if office is not None else {}
            target.update(values)
            target["holder_id"] = values.get("holder_id") or None
            if office is None:
                archai(tribunal).append(target)

        return Form(
            "Add an Office" if office is None else "Edit an Office",
            lambda: archon_fields(saga, office),
            apply,
            save_label="Add" if office is None else "Save",
        )

    def remove(index: int) -> Command:
        office = archai(tribunal)[index]

        def apply() -> None:
            archai(tribunal).remove(office)

        return Confirm(f"Delete the office {escape(office['office'])}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(archai(tribunal)[index]),
        remove=remove,
        rows=lambda: [a["office"] for a in archai(tribunal)],
    )


THEBAN = TribunalPackage(
    KEY,
    "Theban",
    customs="The Polity",
    book="TSE",
    quorum_needs_quaesitor=False,
    redcaps_vote=False,
    praeco_votes=True,
    columns=(RosterColumn("Phyle", phyle_of, 10, phyle_field, save_phyle),),
    tabs=(
        PackageTab(
            "The Polity",
            "tab-trib-tokens",
            (
                PackageList(TOKENS_SECTION, tokens_title, tokens_grid, token_ops),
                PackageList(ARCHAI_SECTION, archai_title, archai_grid, archon_ops),
            ),
        ),
    ),
    meeting_steps=(
        "assembly",
        "ostrakismos",
        "end_of_term",
        "sortition",
        "archon_polemarch",
    ),
    about="Its magi are politai or metoikoi, each voting once; a polites "
    "earns tokens for services and shards for wrongs; its covenants belong "
    "to four phylai; and its Council of Magistrates is chosen at each "
    "meeting.",
    covenant_fields=covenant_phyle_fields,
    save_covenant=save_covenant_phyle,
)

register(THEBAN)
