"""The Greater Alps Tribunal's customs (Sanctuary of Ice: The Greater
Alps Tribunal, a Fourth Edition book), in the book's own terms: chairs
and ostracism.

Chairs (pp. 9-10): a magus votes at the Tribunal only if his covenant has
"bought a chair" for him, registering with the Quaesitores a permanent
vis source that can pledge ten pawns a year to his upkeep, at least a
year before the meeting. The vis isn't paid to anyone; it shows the
covenant won't poach from its neighbours. A magus with no chair is a
vagrant, a Low Crime, though a chair registered at any time protects him
from its punishments. A chair belongs to the covenant: a magus who leaves
doesn't take it with him. The roster's Chairs column is how many a
covenant has registered, beside how many magi it has.

Ostracism (pp. 11-12): as the first business of each meeting, every
magus writes on a sherd the name of the one he most despises, or leaves
it blank. The magus with the most sherds is ostracised, provided at
least one magus in four named him, and must leave the Greater Alps before
the second full moon, for twenty-one years, or be Marched. The exile
ends the day before a Tribunal, so a returning magus can be ostracised
again. An ostracised Praeco's place goes to the next eldest, and an
ostracised chief Quaesitor's to his deputy.

Kept in the package's data: "chairs", {covenant id: chairs registered};
"ostracised", each {"character_id", "year", "sherds", "voters", "until",
"why"}, in the order entered. The rest of the Tribunal's customs (the
pawn a year to the senior Guernicus and Mercere, no new covenants,
disorder) are in its notes and Peripheral Code."""

from __future__ import annotations

from typing import Any

from ..commands import Command, Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..grids import Grid
from ..markup import escape
from ..models import Character, Covenant, Saga, Tribunal
from ..sections import OSTRACISM_SECTION
from . import (
    PackageList,
    PackageTab,
    RosterColumn,
    TribunalPackage,
    data,
    entries,
    register,
)

KEY = "alps"

#: How long an ostracism lasts, and the share of the voters who must
#: name the magus (Sanctuary of Ice pp. 11-12).
EXILE_YEARS = 21
SHARE = 4
#: The pawns a chair pledges each year (p. 9).
CHAIR_PAWNS = 10


def chairs(tribunal: Tribunal) -> dict[str, int]:
    """The chairs each covenant has registered, by covenant id."""
    found = data(tribunal, KEY).setdefault("chairs", {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's chairs should be a mapping, not {found!r}.")
    return found


def ostracised(tribunal: Tribunal) -> list[dict[str, Any]]:
    """Each ostracism the Tribunal has voted, in the order entered."""
    return entries(tribunal, KEY, "ostracised")


def until(entry: dict[str, Any]) -> int | None:
    """The year the exile ends: as entered, or 21 years after the vote."""
    if entry.get("until") is not None:
        return int(entry["until"])
    year = entry.get("year")
    return int(year) + EXILE_YEARS if year is not None else None


def in_exile(saga: Saga, entry: dict[str, Any]) -> bool:
    """Whether the exile runs this year (it ends the day before the
    Tribunal of the year it ends)."""
    end = until(entry)
    return end is not None and int(entry.get("year") or 0) <= saga.current_year < end


def _name(saga: Saga, character_id: str | None) -> str:
    character = saga.character(character_id)
    return character.name if character is not None else "(gone)"


def _magi_of(saga: Saga, covenant: Covenant) -> int:
    return sum(
        1 for c in saga.characters if c.covenant_id == covenant.id and c.type == "magus"
    )


# -- chairs --


def chairs_of(saga: Saga, tribunal: Tribunal, covenant: Covenant) -> str:
    """The covenant's chairs beside its magi ("3 of 4"), or "" if none is
    entered."""
    held = chairs(tribunal).get(covenant.id)
    if held is None:
        return ""
    return f"{held} of {_magi_of(saga, covenant)}"


def chairs_field(
    _saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> DialogField:
    return DialogField(
        "chairs",
        "Chairs",
        "optint",
        chairs(tribunal).get(covenant.id) if covenant is not None else None,
        hint=f"Chairs it has bought: each registers {CHAIR_PAWNS} pawns of vis a "
        "year for one magus's upkeep with the Quaesitores, so he may vote. A "
        "magus with none is a vagrant.",
    )


def save_chairs(tribunal: Tribunal, covenant: Covenant, value: Any) -> None:
    if value is None or value == "":
        chairs(tribunal).pop(covenant.id, None)
    else:
        chairs(tribunal)[covenant.id] = int(value)


def covenant_chair_fields(
    saga: Saga, tribunal: Tribunal, covenant: Covenant | None
) -> list[DialogField]:
    """A covenant's own form: its chairs."""
    return [chairs_field(saga, tribunal, covenant)]


def save_covenant_chairs(
    tribunal: Tribunal, ident: str, values: dict[str, Any]
) -> None:
    if "chairs" not in values:
        return
    if values["chairs"] is None:
        chairs(tribunal).pop(ident, None)
    else:
        chairs(tribunal)[ident] = int(values["chairs"])


# -- ostracism --


def ostracism_title(_saga: Saga, tribunal: Tribunal) -> str:
    return f"Ostracism ({len(ostracised(tribunal))})"


def ostracism_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each ostracism: the magus, the meeting that voted it, the sherds
    against him of those cast, when the exile ends and why."""
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, entry in enumerate(ostracised(tribunal)):
        if in_exile(saga, entry):
            styles[(index, 3)] = "$text-error"
        end = until(entry)
        rows.append(
            [
                _name(saga, entry.get("character_id")),
                str(entry.get("year", "")),
                f"{entry.get('sherds', 0)} of {entry.get('voters', 0)}",
                ("" if end is None else f"to {end}")
                + (" (in exile)" if in_exile(saga, entry) else ""),
                entry.get("why", ""),
            ]
        )
    return Grid(
        ["Magus", "Voted", "Sherds", "Exile", "Why"],
        rows,
        list(range(len(rows))),
        "No magus ostracised: at each meeting the magus most named on the "
        "sherds leaves the Greater Alps for twenty-one years, if one magus in "
        "four named him.",
        styles,
        caps=[20, 6, 10, 18, 0],
    )


def ostracism_fields(saga: Saga, entry: dict[str, Any] | None) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "character_id",
            "Magus",
            "select",
            e.get("character_id"),
            options=[
                (escape(c.name), c.id) for c in saga.characters if c.type == "magus"
            ],
            required=True,
            hint="A magus of the saga, at any detail.",
        ),
        DialogField(
            "year",
            "Meeting (year)",
            "int",
            e.get("year", saga.current_year),
            hint="The Tribunal that voted it, as its first business.",
        ),
        DialogField(
            "sherds",
            "Sherds against him",
            "int",
            e.get("sherds", 0),
            hint="The sherds naming him, the most of any magus.",
        ),
        DialogField(
            "voters",
            "Sherds cast",
            "int",
            e.get("voters", 0),
            hint="Every sherd in the urn, blank ones too: at least one in four "
            "must name him.",
        ),
        DialogField(
            "until",
            "Exile ends (year)",
            "optint",
            e.get("until"),
            hint=f"Leave blank for {EXILE_YEARS} years after the meeting. It ends "
            "the day before that year's Tribunal.",
        ),
        DialogField("why", "Why", "text", e.get("why", "")),
    ]


def ostracism_problem(values: dict[str, Any]) -> str | None:
    """Why the vote can't stand as entered (None: it can)."""
    sherds, voters = values.get("sherds") or 0, values.get("voters") or 0
    if sherds < 0 or voters < 0:
        return "Sherds can't be fewer than none."
    if sherds > voters:
        return "More sherds name him than were cast."
    if sherds * SHARE < voters:
        return (
            f"Only {sherds} of {voters} sherds name him: at least one magus in "
            "four must, or no one is ostracised."
        )
    end = values.get("until")
    if end is not None and values.get("year") is not None and end <= values["year"]:
        return "The exile must end after the meeting that voted it."
    return None


def ostracism_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    def form(entry: dict[str, Any] | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            target = entry if entry is not None else {}
            target.update(values)
            if entry is None:
                ostracised(tribunal).append(target)

        return Form(
            "Add an Ostracism" if entry is None else "Edit an Ostracism",
            lambda: ostracism_fields(saga, entry),
            apply,
            validate=ostracism_problem,
            save_label="Add" if entry is None else "Save",
        )

    def remove(index: int) -> Command:
        entry = ostracised(tribunal)[index]

        def apply() -> None:
            ostracised(tribunal).remove(entry)

        name = escape(_name(saga, entry.get("character_id")))
        return Confirm(f"Delete {name}'s ostracism of {entry.get('year')}?", apply)

    return SectionOps(
        add=lambda: form(None),
        edit=lambda index: form(ostracised(tribunal)[index]),
        remove=remove,
        rows=lambda: [_name(saga, e.get("character_id")) for e in ostracised(tribunal)],
    )


def magus_facts(
    saga: Saga, tribunal: Tribunal, magus: Character
) -> list[tuple[str, str]]:
    """That the magus is ostracised, and until when, for his sheet."""
    for entry in ostracised(tribunal):
        if entry.get("character_id") == magus.id and in_exile(saga, entry):
            return [
                (
                    "Ostracised",
                    f"to {until(entry)}, by {entry.get('sherds', 0)} of "
                    f"{entry.get('voters', 0)} sherds at the Tribunal of "
                    f"{entry.get('year')}",
                )
            ]
    return []


ALPS = TribunalPackage(
    KEY,
    "Greater Alps",
    customs="Chairs and ostracism",
    book="SoI",
    columns=(RosterColumn("Chairs", chairs_of, 8, chairs_field, save_chairs),),
    tabs=(
        PackageTab(
            "Ostracism",
            "tab-trib-ostracism",
            (
                PackageList(
                    OSTRACISM_SECTION, ostracism_title, ostracism_grid, ostracism_ops
                ),
            ),
        ),
    ),
    magus_facts=magus_facts,
    covenant_fields=covenant_chair_fields,
    save_covenant=save_covenant_chairs,
    about="A magus votes only if his covenant has bought him a chair, "
    f"registering {CHAIR_PAWNS} pawns of vis a year for his upkeep; at each "
    "meeting the magus most named on the sherds is ostracised for "
    f"{EXILE_YEARS} years, if one magus in four named him.",
)

register(ALPS)
