"""Giving what one record holds to another: raw vis, a book (a lab text is
a book), an enchanted device, personal gear or silver, from a character,
a laboratory or a covenant to another of the saga's records.

Each kind of thing is a `Giver`: who can hold it, whether it asks how many,
how it leaves the giver and where it lands with the receiver. A book or a
device changes owner; gear moves between a character's inventory and a
covenant's Possessions (a laboratory holds no gear); silver between a
character's purse and a covenant's Wealth, in pounds; vis as vis.move does.
Both sides' Diaries say what changed hands. `give` is the one step every
front-end runs, whatever the kind.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, NamedTuple

from . import books as bk
from . import vis
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Laboratory,
    Possession,
    Saga,
    new_instance_id,
)
from .rules import library

Holder = Character | Laboratory | Covenant

VIS, BOOK, DEVICE, GEAR, SILVER = "vis", "book", "device", "gear", "silver"
#: The Possession kinds a character carries and a covenant keeps alike.
GEAR_KINDS = ("weapon", "armor", "item")


def kind_of(holder: Holder) -> str:
    return vis.kind_of(holder)


def gear(holder: Holder) -> list[Possession]:
    """The holder's list of gear: a character's inventory, a covenant's
    Possessions (a laboratory has none)."""
    if isinstance(holder, Character):
        return holder.inventory
    if isinstance(holder, Covenant):
        return holder.possessions
    return []


def silver(holder: Holder) -> int:
    if isinstance(holder, Character):
        return holder.silver
    if isinstance(holder, Covenant):
        return holder.economics.wealth
    return 0


def _add_silver(holder: Holder, pounds: int) -> None:
    if isinstance(holder, Character):
        holder.silver += pounds
    elif isinstance(holder, Covenant):
        holder.economics.wealth += pounds


# ------------------------------------------------------------------ givers


def _anyone(_holder: Holder) -> bool:
    return True


def _magus_or_not_character(holder: Holder) -> bool:
    # Only a magus's sheet has Raw Vis.
    return not isinstance(holder, Character) or holder.type == "magus"


def _no_laboratory(holder: Holder) -> bool:
    return not isinstance(holder, Laboratory)


def _give_vis(saga: Saga, source: Holder, thing: Any, count: int, to: Holder) -> None:
    vis.move(saga, source, thing, count, to)


def _give_book(saga: Saga, source: Holder, thing: Any, count: int, to: Holder) -> None:
    bk.set_owner(saga, thing, kind_of(to), to.id)


def _give_device(
    saga: Saga, source: Holder, thing: Any, count: int, to: Holder
) -> None:
    _hand_device(saga, thing, to)


def _hand_device(saga: Saga, device: Any, to: Holder) -> None:
    """`to` holds `device` now; a talisman keeps its mark."""
    epitome = next((b for b in saga.books if b.device_id == device.id), None)
    if epitome is not None:
        # An epitome is a book: the book and its codex go with it.
        bk.set_owner(saga, epitome, kind_of(to), to.id)
    device.holder_kind, device.holder_id = kind_of(to), to.id


def _give_gear(saga: Saga, source: Holder, thing: Any, count: int, to: Holder) -> None:
    given = thing
    if count < thing.quantity:
        thing.quantity -= count
        given = replace(thing, id=f"gear_{new_instance_id()}", quantity=count)
    else:
        gear(source).remove(thing)
    gear(to).append(given)


def _give_silver(
    saga: Saga, source: Holder, thing: Any, count: int, to: Holder
) -> None:
    _add_silver(source, -count)
    _add_silver(to, count)


def _vis_words(thing: Any, count: int) -> str:
    return f"{count} pawn{'s' if count != 1 else ''} of {thing.art} vis"


def _named(thing: Any, count: int) -> str:
    return thing.name or "an unnamed one"


def _gear_words(thing: Any, count: int) -> str:
    name = thing.name or "unnamed gear"
    return f"{count} × {name}" if thing.quantity > 1 else name


def _pounds(thing: Any, count: int) -> str:
    return f"{count} pound{'s' if count != 1 else ''} of silver"


@dataclass(frozen=True)
class Giver:
    """How one kind of thing changes hands."""

    noun: str
    #: Who can hold this kind of thing.
    takes: Callable[[Holder], bool]
    #: Moves `count` of the thing from the giver to the receiver.
    move: Callable[[Saga, Holder, Any, int, Holder], None]
    #: What was given, in words: "3 pawns of Vim vis", "Summa on Ignem".
    words: Callable[[Any, int], str]
    #: How many the giver has, when it asks how many (None: given whole).
    most: Callable[[Holder, Any], int] | None = None
    unit: str = ""


GIVERS: dict[str, Giver] = {
    VIS: Giver(
        "raw vis",
        _magus_or_not_character,
        _give_vis,
        _vis_words,
        lambda _holder, held: held.pawns,
        "Pawns",
    ),
    BOOK: Giver("book", _anyone, _give_book, _named),
    DEVICE: Giver("enchanted device", _anyone, _give_device, _named),
    GEAR: Giver(
        "gear",
        _no_laboratory,
        _give_gear,
        _gear_words,
        lambda _holder, item: item.quantity,
        "How many",
    ),
    SILVER: Giver(
        "silver",
        _no_laboratory,
        _give_silver,
        _pounds,
        lambda holder, _thing: silver(holder),
        "Pounds",
    ),
}


# ---------------------------------------------------------------- receivers


def _label(holder: Holder) -> str:
    if isinstance(holder, Covenant):
        return f"Covenant: {holder.name}"
    if isinstance(holder, Laboratory):
        return f"Laboratory: {holder.name}"
    return f"{holder.name} ({holder.type})"


def receivers(saga: Saga, kind: str, source: Holder | None) -> list[Holder]:
    """Everyone in the saga who can take `kind` from `source` (None: an
    unassigned book or device, from nobody): the covenants, their
    laboratories, then the characters, in any covenant."""
    takes = GIVERS[kind].takes
    found: list[Holder] = [*saga.covenants, *saga.laboratories, *saga.characters]
    return [h for h in found if h is not source and takes(h)]


def _value(holder: Holder) -> str:
    return f"{kind_of(holder)}:{holder.id}"


def _find(saga: Saga, value: str | None) -> Holder | None:
    kind, _, holder_id = (value or "").partition(":")
    return vis.find_holder(saga, kind, holder_id)


# ------------------------------------------------------------------ diaries


def _write(saga: Saga, holder: Holder, text: str, kind: str, pounds: int) -> None:
    if isinstance(holder, Covenant):
        holder.diary.append(
            CovenantDiaryEntry(
                year=saga.current_year,
                season=saga.current_season,
                name=text,
                category="Library" if kind == BOOK else "Purchases & Sales",
                pounds=pounds or None,
            )
        )
    else:
        holder.diary.append(
            DiaryEntry(year=saga.current_year, season=saga.current_season, name=text)
        )


def _record(
    saga: Saga, kind: str, source: Holder | None, to: Holder, what: str, count: int
) -> None:
    """Both sides' Diary lines (vis.move writes its own); only the
    receiver's for what nobody held."""
    if kind == VIS:
        return
    pounds = count if kind == SILVER else 0
    if source is None:
        _write(saga, to, f"Received {what}", kind, pounds)
        return
    _write(saga, source, f"Gave {what} to {to.name}", kind, -pounds)
    _write(saga, to, f"Received {what} from {source.name}", kind, pounds)


# --------------------------------------------------------------------- give


def problem(kind: str, source: Holder | None, thing: Any, count: int) -> str | None:
    """Why `count` can't be given, or None."""
    giver = GIVERS[kind]
    if giver.most is None or source is None:
        return None
    most = giver.most(source, thing)
    if count < 1:
        return f"Give at least 1 ({giver.unit.lower()})."
    if count > most:
        return f"{source.name} has only {most}."
    return None


def give_now(
    saga: Saga, kind: str, source: Holder | None, thing: Any, count: int, to: Holder
) -> str:
    """Give `count` of `thing` (all of it, for what is given whole) from
    `source` (None: an unassigned book or device) to `to`, with the
    Diaries' lines; what was given, in words."""
    giver = GIVERS[kind]
    what = giver.words(thing, count)
    if source is not None:
        giver.move(saga, source, thing, count, to)
    elif kind == BOOK:
        bk.set_owner(saga, thing, kind_of(to), to.id)
    elif kind == DEVICE:
        _hand_device(saga, thing, to)
    else:
        raise ValueError(f"Only a book or a device can be given from nobody: {kind}.")
    _record(saga, kind, source, to, what, count)
    return what


class Gift(NamedTuple):
    """What Give would give: the kind of thing, who gives it (None for an
    unassigned book or device) and the thing itself (None for silver)."""

    kind: str
    source: Holder | None
    thing: Any = None


def gift(saga: Saga, kind: str, shown: Holder | None, thing: Any = None) -> Gift | None:
    """The Gift of `thing` from the record on show (`shown`): a book from
    whoever owns it and a device from whoever holds it, wherever it is
    listed, or from nobody when it is unassigned; anything else from
    `shown` (None when nothing is on show)."""
    if kind == BOOK:
        return Gift(kind, library.owner_record(saga, thing), thing)
    if kind == DEVICE:
        source = vis.find_holder(saga, thing.holder_kind or "", thing.holder_id)
        return Gift(kind, source, thing)
    return Gift(kind, shown, thing) if shown is not None else None


def blocked(
    saga: Saga, kind: str, source: Holder | None, thing: Any = None
) -> str | None:
    """Why `source` can't give `thing` now, or None."""
    giver = GIVERS[kind]
    if source is None:
        if kind not in (BOOK, DEVICE):
            return "Nobody holds this: give it an owner first."
    elif not giver.takes(source):
        return f"{escape(source.name)} holds no {giver.noun}."
    elif giver.most is not None and giver.most(source, thing) < 1:
        return f"{escape(source.name)} has none to give."
    if not receivers(saga, kind, source):
        return f"Nobody else in the saga can take {giver.noun}."
    return None


def codex_words(saga: Saga, kind: str, thing: Any) -> str:
    """For a book bound in a codex with others: that the whole codex goes
    with it ("" otherwise)."""
    if kind != BOOK:
        return ""
    codex = library.codex_of(saga, thing)
    mates = bk.codex_books(saga, thing)
    if codex is None or len(mates) < 2:
        return ""
    return f"Bound in {codex.name}: its {len(mates)} books go together."


def give(saga: Saga, kind: str, source: Holder | None, thing: Any = None) -> Command:
    """Give `thing` (a vis.Held, a Book, an EnchantedDevice, a gear
    Possession; nothing for silver) from `source` to another record: who
    gets it and, for vis, gear and silver, how many. An unassigned book or
    device (`source` None) is given from nobody: only its receiver's
    Diary records it."""
    giver = GIVERS[kind]
    reason = blocked(saga, kind, source, thing)
    if reason is not None:
        return Refuse("Give Silver" if kind == SILVER else "Give Away", reason)
    most = (
        giver.most(source, thing)
        if giver.most is not None and source is not None
        else None
    )
    choices = receivers(saga, kind, source)
    shown = giver.words(thing, most or 1)
    codex = codex_words(saga, kind, thing)

    def fields() -> list[DialogField]:
        found = [
            DialogField(
                "_what",
                "From",
                "info",
                f"{source.name} ({shown})"
                if source is not None
                else f"Unassigned ({shown})",
            ),
            *([DialogField("_codex", "Codex", "info", codex)] if codex else []),
            DialogField(
                "to",
                "To",
                "select",
                None,
                options=[(_label(h), _value(h)) for h in choices],
                required=True,
                allow_blank=True,
                placeholder="(choose who gets it)",
                hint="Both sides' Diaries record the gift."
                if source is not None
                else "The receiver's Diary records it.",
            ),
        ]
        if most is not None:
            found.append(
                DialogField(
                    "count",
                    giver.unit,
                    "int",
                    most if kind != SILVER else min(most, 1),
                )
            )
        return found

    def count_of(values: dict[str, Any]) -> int:
        return int(values.get("count") or 0) if most is not None else 1

    def apply(values: dict[str, Any]) -> list[str] | None:
        to = _find(saga, values.get("to"))
        if to is None:
            return None
        what = give_now(saga, kind, source, thing, count_of(values), to)
        return notes(f"Gave {escape(what)} to {escape(to.name)}.")

    title = "Give Silver"
    if kind != SILVER:
        title = f"Give {escape(_named(thing, 1) if most is None else shown)}"
    return Form(
        title,
        fields,
        apply,
        validate=lambda values: problem(kind, source, thing, count_of(values)),
        save_label="Give",
    )


def give_gift(saga: Saga, found: Gift | None) -> Command:
    """Give what `gift` found, or say why there is nothing to give."""
    if found is None:
        return Refuse("Give Away", "Nobody holds this: give it an owner first.")
    return give(saga, found.kind, found.source, found.thing)
