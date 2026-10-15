"""The Theban Tribunal's customs (The Sundered Eagle: The Theban
Tribunal): its magi vote with tokens, earned by serving liturgies and
passed between them, and cast shards to ostracise one of their number;
its archai hold its offices for a term, elected at each meeting.

Kept in the package's data: "magi", each {"character_id", "tokens",
"shards", "liturgies", "ostracised_until", "why"}, and "archai", each
{"office", "holder_id", "term_ends", "duties"}. The troupe's votes are
its magi's tokens."""

from __future__ import annotations

from typing import Any

from .. import world
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Saga, Tribunal
from ..sections import ARCHAI_SECTION, TOKENS_SECTION
from . import PackageList, PackageTab, TribunalPackage, entries, register

KEY = "theban"


def magi(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each magus's tokens, shards and liturgies, in the order entered."""
    return entries(tribunal, KEY, "magi")


def archai(tribunal: Tribunal) -> list[dict[str, Any]]:
    """The Tribunal's offices, in the order entered."""
    return entries(tribunal, KEY, "archai")


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


def your_tokens(saga: Saga, tribunal: Tribunal) -> int:
    """The tokens the troupe's magi hold."""
    yours = {
        m.id for c in world.player_covenants(saga) for m in world.covenant_magi(saga, c)
    }
    return sum(m.get("tokens", 0) for m in magi(tribunal) if m["character_id"] in yours)


def your_votes(saga: Saga, tribunal: Tribunal) -> str:
    """ "2 tokens of 10": the troupe's tokens, of all those held."""
    held = sum(m.get("tokens", 0) for m in magi(tribunal))
    yours = your_tokens(saga, tribunal)
    return f"{yours} token{'' if yours == 1 else 's'} of {held}"


# -- tokens and shards --


def tokens_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Tokens and Shards ({len(magi(tribunal))})"


def tokens_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each magus: their covenant, tokens, shards, liturgies served and
    standing (an office, or ostracism)."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(magi(tribunal)):
        character = saga.character(entry.get("character_id"))
        covenant = saga.covenant(character.covenant_id) if character else None
        if ostracised(saga, entry):
            styles[(index, 5)] = "$text-error"
        rows.append(
            [
                _name(saga, entry.get("character_id")),
                covenant.name if covenant is not None else "",
                str(entry.get("tokens", 0)),
                str(entry.get("shards", 0)),
                str(entry.get("liturgies", 0)),
                standing(saga, tribunal, entry),
            ]
        )
    return Grid(
        ["Magus", "Covenant", "Tokens", "Shards", "Liturgies", "Standing"],
        rows,
        list(range(len(rows))),
        "No magus's tokens recorded: tokens are the Theban Tribunal's votes, "
        "shards its ostracisms.",
        styles,
        caps=[22, 14, 6, 6, 9, 0],
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
        DialogField("tokens", "Tokens", "int", e.get("tokens", 0)),
        DialogField("shards", "Shards", "int", e.get("shards", 0)),
        DialogField("liturgies", "Liturgies served", "int", e.get("liturgies", 0)),
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
        ("liturgies", "Liturgies"),
    ):
        if (values.get(key) or 0) < 0:
            return f"{words} can't be fewer than none."
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


# -- the archai --


def archai_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"The Archai ({len(archai(tribunal))})"


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
        "No archai recorded: the offices the Tribunal elects at each meeting.",
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
            placeholder="e.g. Archon of Rites",
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
            placeholder="e.g. The Tribunal's ceremonies and oaths",
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
    customs="Tokens",
    book="TSE",
    tabs=(
        PackageTab(
            "Tokens and Archai",
            "tab-trib-tokens",
            (
                PackageList(TOKENS_SECTION, tokens_title, tokens_grid, token_ops),
                PackageList(ARCHAI_SECTION, archai_title, archai_grid, archon_ops),
            ),
        ),
    ),
    your_votes=your_votes,
    meeting_steps=("elections",),
    about="Its magi vote with tokens and ostracise with shards, and elect "
    "its archai at each meeting.",
)

register(THEBAN)
