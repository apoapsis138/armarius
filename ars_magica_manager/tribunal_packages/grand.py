"""The Grand Tribunal (DE p. 22): held every 33 years at Durenmar, for
the whole Order. Three representatives come from each regional Tribunal,
and the Primi of every House attend; the Primus of House Bonisagus is its
Praeco and the Primus of House Guernicus its Presiding Quaesitor. It
alone has authority over the whole Order, and settles disputes between
Tribunals.

A Tribunal record following this package is the Grand Tribunal: it holds
no covenants, and its votes are its delegates', a vote each (as Envoys).
Kept in the package's data: "delegates", each {"id", "name", "sent_by"
(a regional Tribunal's id, or "" for a Primus), "house" (a Primus's
House), "character_id" (optional), "covenant" (typed, for one not of the
saga)}.

Its quorum is any legal Tribunal's (DE p. 22): at least twelve magi from
at least four covenants, and a Quaesitor; here the delegates, a magus of
the saga counted at his covenant, and the Primus of Guernicus (or a
Guernicus magus among them) the Quaesitor. Naming the Primi of Bonisagus
and Guernicus as magi of the saga makes them the Praeco and the Presiding
Quaesitor, as the book has it.
"""

from __future__ import annotations

from typing import Any

from .. import catalog
from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Meeting, Saga, Tribunal, new_instance_id
from ..sections import DELEGATES_SECTION
from . import (
    Envoy,
    PackageList,
    PackageTab,
    TribunalPackage,
    entries,
    register,
)

KEY = "grand"
SOURCE = "Ars Magica Definitive Edition, The Grand Tribunal, p. 22"
#: Where it is always held, and how often.
PLACE = "Durenmar"
EVERY = 33
#: Representatives each regional Tribunal sends.
REPRESENTATIVES = 3
#: A legal Tribunal's quorum (DE p. 22).
QUORUM_MAGI = 12
QUORUM_COVENANTS = 4
BONISAGUS, GUERNICUS = "house_bonisagus", "house_guernicus"


def delegates(tribunal: Tribunal) -> list[dict[str, Any]]:
    found = entries(tribunal, KEY, "delegates")
    for entry in found:
        entry.setdefault("id", new_instance_id())
    return found


def regional(saga: Saga, tribunal: Tribunal) -> list[Tribunal]:
    """The saga's other Tribunals, which send representatives."""
    return [t for t in saga.tribunals if t.id != tribunal.id and t.package != KEY]


def _house_name(house_id: str) -> str:
    found = catalog.load_house_catalog_by_id().get(house_id)
    return found.name if found is not None else house_id


def _sent_by(saga: Saga, entry: dict[str, Any]) -> str:
    if entry.get("sent_by"):
        sender = saga.tribunal(entry["sent_by"])
        return sender.name if sender is not None else "a Tribunal no longer kept"
    house = entry.get("house") or ""
    return f"Primus of House {_house_name(house)}" if house else "a Primus"


def envoys(saga: Saga, tribunal: Tribunal, _meeting: Meeting) -> list[Envoy]:
    """Every delegate, a vote each."""
    return [
        Envoy(f"delegate_{d['id']}", d.get("name") or "(unnamed)", _sent_by(saga, d))
        for d in delegates(tribunal)
    ]


def _covenant(saga: Saga, entry: dict[str, Any]) -> str:
    """The delegate's covenant: his of the saga, or as typed ("" unknown)."""
    character = saga.character(entry.get("character_id") or "")
    if character is not None and character.covenant_id:
        found = saga.covenant(character.covenant_id)
        if found is not None:
            return found.name
    return str(entry.get("covenant") or "").strip()


def _quaesitor(saga: Saga, entry: dict[str, Any]) -> bool:
    if not entry.get("sent_by") and entry.get("house") == GUERNICUS:
        return True
    character = saga.character(entry.get("character_id") or "")
    return character is not None and character.hermetic.house == GUERNICUS


def quorum(saga: Saga, tribunal: Tribunal, _meeting: Meeting) -> str:
    """Twelve magi from four covenants and a Quaesitor (DE p. 22)."""
    found = delegates(tribunal)
    covenants = {c.casefold() for d in found if (c := _covenant(saga, d))}
    quaesitor = any(_quaesitor(saga, d) for d in found)
    unknown = sum(1 for d in found if not _covenant(saga, d))
    words = (
        f"{len(found)} delegate{'' if len(found) == 1 else 's'} from "
        f"{len(covenants)} covenant{'' if len(covenants) == 1 else 's'}"
        + (f" ({unknown} not named)" if unknown else "")
        + (", and a Quaesitor" if quaesitor else ", and no Quaesitor")
    )
    lacking = []
    if len(found) < QUORUM_MAGI:
        lacking.append(f"{QUORUM_MAGI} magi")
    if len(covenants) < QUORUM_COVENANTS:
        lacking.append(f"{QUORUM_COVENANTS} covenants")
    if not quaesitor:
        lacking.append("a Quaesitor")
    if lacking:
        return f"{words}: not quorate (it needs {', '.join(lacking)})"
    return f"{words}: quorate"


def officers(tribunal: Tribunal) -> None:
    """The Primus of Bonisagus is the Praeco, the Primus of Guernicus the
    Presiding Quaesitor (DE p. 22), when named as magi of the saga."""
    for entry in delegates(tribunal):
        if entry.get("sent_by") or not entry.get("character_id"):
            continue
        if entry.get("house") == BONISAGUS:
            tribunal.praeco_id = entry["character_id"]
        elif entry.get("house") == GUERNICUS:
            tribunal.quaesitor_id = entry["character_id"]


def delegates_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Delegates ({len(delegates(tribunal))})"


def delegates_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    rows = [
        [d.get("name") or "(unnamed)", _sent_by(saga, d)] for d in delegates(tribunal)
    ]
    return Grid(
        ["Delegate", "Sent by"],
        rows,
        list(range(len(rows))),
        f"No delegates yet: {REPRESENTATIVES} representatives from each regional "
        "Tribunal, and the Primi of every House (DE p. 22).",
        caps=[30, 0],
    )


def delegate_fields(
    saga: Saga, tribunal: Tribunal, entry: dict[str, Any] | None
) -> list[DialogField]:
    e = entry or {}
    tribunals = [(escape(t.name), t.id) for t in regional(saga, tribunal)]
    houses = [(escape(h.name), h.id) for h in catalog.load_house_catalog()]
    people = [(escape(c.name), c.id) for c in saga.characters if c.type == "magus"]
    return [
        DialogField("name", "Name", "text", e.get("name", ""), required=True),
        DialogField(
            "sent_by",
            "Representing",
            "select",
            e.get("sent_by") or None,
            options=tribunals,
            allow_blank=True,
            placeholder="(none: a Primus)",
            hint=f"{REPRESENTATIVES} representatives from each regional Tribunal.",
        ),
        DialogField(
            "house",
            "Primus of House",
            "select",
            e.get("house") or None,
            options=houses,
            allow_blank=True,
            placeholder="(choose)",
            show_if=lambda v: not v.get("sent_by"),
            hint="Bonisagus's Primus is the Praeco, Guernicus's the Presiding "
            "Quaesitor: named as a magus of the saga, he is made so (DE p. 22).",
        ),
        DialogField(
            "character_id",
            "A magus of the saga",
            "select",
            e.get("character_id") or None,
            options=people,
            allow_blank=True,
            placeholder="(none)",
        ),
        DialogField(
            "covenant",
            "Of the covenant",
            "text",
            e.get("covenant", ""),
            hint="For one not of the saga: the quorum counts covenants (DE p. 22).",
            show_if=lambda v: not v.get("character_id"),
        ),
    ]


def _problem(
    tribunal: Tribunal, entry: dict[str, Any] | None, values: dict[str, Any]
) -> str | None:
    sender = values.get("sent_by")
    if sender:
        already = [
            d
            for d in delegates(tribunal)
            if d.get("sent_by") == sender and d is not entry
        ]
        if len(already) >= REPRESENTATIVES:
            return f"That Tribunal sends {REPRESENTATIVES} representatives already."
    elif not values.get("house"):
        return "Choose the Tribunal represented, or the House whose Primus this is."
    return None


def delegate_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {"id": new_instance_id()}
            sender = values.get("sent_by") or ""
            target.update(
                {
                    "name": values.get("name") or "",
                    "sent_by": sender,
                    "house": "" if sender else values.get("house") or "",
                    "character_id": values.get("character_id") or "",
                    "covenant": ""
                    if values.get("character_id")
                    else (values.get("covenant") or ""),
                }
            )
            if entry is None:
                delegates(tribunal).append(target)
            officers(tribunal)

        return Form(
            "Add a Delegate" if entry is None else "Edit a Delegate",
            lambda: delegate_fields(saga, tribunal, entry),
            apply,
            validate=lambda values: _problem(tribunal, entry, values),
            save_label="Add" if entry is None else "Save",
            help_id=DELEGATES_SECTION,
        )

    def remove(index: int) -> Command:
        entry = delegates(tribunal)[index]

        def apply() -> None:
            delegates(tribunal).remove(entry)

        return Confirm(f"Delete {escape(entry.get('name') or 'the delegate')}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(delegates(tribunal)[index]),
        remove=remove,
        rows=lambda: [d.get("name") or "(unnamed)" for d in delegates(tribunal)],
    )


GRAND = TribunalPackage(
    KEY,
    "The Grand Tribunal",
    customs="Delegates of the whole Order",
    tabs=(
        PackageTab(
            "Delegates",
            "tab-trib-delegates",
            (
                PackageList(
                    DELEGATES_SECTION, delegates_title, delegates_grid, delegate_ops
                ),
            ),
        ),
    ),
    envoys=envoys,
    quorum=quorum,
    about="The Order's Grand Tribunal, every 33 years at Durenmar: three "
    "representatives from each regional Tribunal and the Primi of every "
    "House vote, a vote each; the Primus of Bonisagus presides as Praeco and "
    "the Primus of Guernicus as Presiding Quaesitor (DE p. 22). It holds no "
    "covenants of its own.",
)

register(GRAND)
