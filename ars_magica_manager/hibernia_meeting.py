"""The Hibernian Tribunal's meeting steps (The Contested Isle). Before
the meeting opens, the Sacred Council confirms each faction's ambassador,
who then votes as a magus does, and hears the Coill Trí's disputes.
Before it closes, the Coill Trí hand over the seven Gifted children
their treaty owes, one from each túath: the storyguide gives each to a
magus by hand, or lets the step simulate the covenants' bidding
(gifted_children.bid), the price paid from the winner's vis stores. A
child given becomes a sketch character at their master's covenant.

Each step is a meeting.Step (the Template Method the core's steps fill
in), registered under the name the Hibernia package lists. What a step
did is kept in the meeting record under "council" and "tithe"."""

from __future__ import annotations

import random
from typing import Any

from . import gifted_children, storage, tribunals, vis, world
from . import meeting as core
from .form_spec import DialogField
from .markup import escape
from .models import (
    Background,
    Character,
    Covenant,
    HermeticBackground,
    Meeting,
    Saga,
    Tribunal,
)
from .models.world import SKETCH
from .tribunal_packages.hibernia import ambassadors, confirmed, tuatha

#: How the tithe's children are given out.
BY_BIDDING = "By bidding"
BY_HAND = "By hand"

#: How many children each túath offers to choose from (the first is the
#: one it brings unless another is chosen: a reroll).
CHOICES = 3

#: What a child given is, on their sheet.
APPRENTICE = "Apprentice"


# -- the Sacred Council --


def _named(entry: dict[str, Any]) -> str:
    return entry.get("name") or "(to be named)"


class SacredCouncil(core.Step):
    """Each faction's ambassador confirmed (or not) for this meeting, and
    the Coill Trí's disputes heard."""

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        kept = meeting.get("council")
        found: list[DialogField] = []
        for entry in ambassadors(tribunal):
            on = (
                entry["id"] in kept.get("confirmed", [])
                if kept is not None
                else bool(entry.get("confirmed"))
            )
            found.append(
                DialogField(
                    f"confirm_{entry['id']}",
                    f"{escape(entry['faction'])}: {escape(_named(entry))}",
                    "check",
                    on,
                    hint="Confirmed ambassadors vote at the meeting."
                    if not found
                    else "",
                )
            )
        if not found:
            found.append(
                DialogField(
                    "none",
                    "",
                    "info",
                    "No ambassadors are recorded: add them on the Ambassadors tab.",
                )
            )
        found += [
            DialogField(
                "disputes",
                "Disputes heard",
                "area",
                (kept or {}).get("disputes", ""),
                hint="The Coill Trí's grievances and the factions' quarrels.",
            ),
            core._note_field(meeting, self.key),
        ]
        return found

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        chosen = []
        for entry in ambassadors(tribunal):
            on = bool(values.get(f"confirm_{entry['id']}"))
            entry["confirmed"] = on
            if on:
                chosen.append(entry["id"])
        meeting["council"] = {
            "confirmed": chosen,
            "disputes": (values.get("disputes") or "").strip(),
        }
        core._keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        voting = ", ".join(_named(a) for a in confirmed(tribunal, meeting))
        disputes = (meeting.get("council") or {}).get("disputes", "")
        return core._join(
            f"[$label]Ambassadors voting:[/] {escape(voting or 'none')}",
            f"[$label]Disputes heard:[/] {escape(disputes)}" if disputes else "",
            core._note_text(meeting, self.key),
        )

    def save_label(self):
        return "Confirm"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        voting = confirmed(tribunal, meeting)
        names = ", ".join(f"{_named(a)} for {a['faction']}" for a in voting)
        words = (
            f"The Sacred Council confirmed the ambassadors: {names}."
            if voting
            else "The Sacred Council confirmed no ambassador."
        )
        disputes = (meeting.get("council") or {}).get("disputes", "")
        if disputes:
            words += f" It heard: {disputes}"
        count = len(voting)
        return words, f"{count} ambassador{'' if count == 1 else 's'}"


# -- the tithe of Gifted children --


def _record(meeting: Meeting) -> dict[str, Any]:
    return meeting.setdefault("tithe", {})


def _year(saga: Saga, meeting: Meeting) -> int:
    return int(meeting.get("year") or saga.current_year)


def candidates(
    saga: Saga, tribunal: Tribunal, meeting: Meeting
) -> list[list[dict[str, Any]]]:
    """The children each túath offers, CHOICES of them: made once and
    kept with the meeting, so the form shows the same each time."""
    record = _record(meeting)
    if "candidates" not in record:
        rng = core.rng()
        year = _year(saga, meeting)
        offered = [
            gifted_children.tithe(rng, tuatha(tribunal), year) for _ in range(CHOICES)
        ]
        record["candidates"] = [list(slot) for slot in zip(*offered)]
        record["seed"] = rng.randrange(1 << 30)
    return record["candidates"]


def chosen(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
) -> list[dict[str, Any]]:
    """The child each túath brings, as the form chooses."""
    found = []
    for index, slot in enumerate(candidates(saga, tribunal, meeting)):
        pick = int(values.get(f"child_{index}") or 0)
        found.append(slot[pick if 0 <= pick < len(slot) else 0])
    return found


def apprenticed(saga: Saga, magus: Character) -> bool:
    """Whether the magus already has an apprentice: someone not yet a
    magus who names them as parens."""
    return any(
        c.type != "magus" and c.hermetic.parens == magus.name
        for c in saga.characters
        if c is not magus
    )


def represented(saga: Saga, tribunal: Tribunal, meeting: Meeting) -> list[Covenant]:
    """The covenants represented at the meeting (those showing their
    cathach)."""
    return [
        c
        for c in tribunals.covenants_of(saga, tribunal)
        if core.shows(saga, tribunal, meeting, c)
    ]


def masters(saga: Saga, covenant: Covenant) -> list[Character]:
    """The covenant's magi without an apprentice."""
    return [m for m in world.covenant_magi(saga, covenant) if not apprenticed(saga, m)]


def _pawns(covenant: Covenant) -> int:
    return sum(held.pawns for held in vis.held(covenant))


def bidders(
    saga: Saga, tribunal: Tribunal, meeting: Meeting
) -> list[gifted_children.Bidder]:
    return [
        gifted_children.Bidder(
            c.id, c.name, [m.id for m in masters(saga, c)], _pawns(c)
        )
        for c in represented(saga, tribunal, meeting)
    ]


def awards(
    saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
) -> list[gifted_children.Award]:
    """Where each child goes, as the form says: by the bidding (the same
    each time the form is shown) or by the storyguide's hand."""
    children = chosen(saga, tribunal, meeting, values)
    if values.get("how", BY_BIDDING) == BY_BIDDING:
        candidates(saga, tribunal, meeting)
        rng = random.Random(_record(meeting).get("seed", 0))
        return gifted_children.bid(rng, children, bidders(saga, tribunal, meeting))
    found = []
    for index in range(len(children)):
        master = saga.character(values.get(f"claim_{index}"))
        found.append(
            gifted_children.Award(master.covenant_id, master.id)
            if master is not None
            else gifted_children.Award()
        )
    return found


def _award_text(saga: Saga, child: dict[str, Any], award: gifted_children.Award) -> str:
    if child.get("false_gift"):
        return f"{child['name']}: no true Gift, turned away"
    master = saga.character(award.master_id)
    covenant = saga.covenant(award.covenant_id)
    if master is None or covenant is None:
        return f"{child['name']}: unclaimed"
    words = f"{child['name']}: to {master.name} of {covenant.name}"
    if award.price:
        words += f", for {award.price} pawn{'' if award.price == 1 else 's'}"
    return words


def _pay(saga: Saga, covenant: Covenant, pawns: int, child: dict[str, Any]) -> None:
    """Take `pawns` from the covenant's vis stores, the fullest first."""
    pool = vis.StorePool(
        saga, covenant, f"The tithe of Gifted children ({child['name']})"
    )
    for art in sorted(pool, key=lambda a: -pool[a]):
        if pawns <= 0:
            break
        taken = min(pawns, pool[art])
        pool[art] = pool[art] - taken
        pawns -= taken


def _apprentice(
    saga: Saga,
    child: dict[str, Any],
    master: Character,
    covenant: Covenant,
    year: int,
) -> Character:
    """The child given, as a sketch character at their master's covenant."""
    character = Character(
        id=storage.generate_unique_id(child["name"], [c.id for c in saga.characters]),
        name=child["name"],
        type="companion",
        covenant_id=covenant.id,
        detail=SKETCH,
        summary=gifted_children.summary(child)
        + f" {child['gift']}. Apprenticed to {master.name} at the Tribunal of {year}.",
        background=Background(
            year_born=year - int(child.get("age") or 0),
            place_of_origin=child.get("tuath", ""),
            race_nationality="Irish",
            title_profession=APPRENTICE,
        ),
        hermetic=HermeticBackground(
            parens=master.name,
            covenant_of_apprenticeship=covenant.name,
            age_of_apprenticeship=child.get("age"),
        ),
    )
    saga.characters.append(character)
    return character


class Tithe(core.Step):
    """The Coill Trí's seven Gifted children: which child each túath
    brings (of three, a reroll), and who takes each, by hand or by
    simulated bidding. Once given, holding it again changes only the
    note."""

    def _given(self, meeting: Meeting) -> list[dict[str, Any]] | None:
        return _record(meeting).get("given")

    def fields(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        if self._given(meeting) is not None:
            return [
                DialogField(
                    "given",
                    "",
                    "info",
                    "The children are given: holding this again changes only the note.",
                ),
                core._note_field(meeting, self.key),
            ]
        found = [
            DialogField(
                "intro",
                "",
                "info",
                "The Coill Trí bring a Gifted child from each túath. Choose "
                "which of three each brings, then give them out.",
            )
        ]
        for index, slot in enumerate(candidates(saga, tribunal, meeting)):
            tuath, ceannaire = slot[0].get("tuath", ""), slot[0].get("ceannaire", "")
            found.append(
                DialogField(
                    f"child_{index}",
                    escape(tuath or f"Túath {index + 1}"),
                    "select",
                    "0",
                    options=[
                        (escape(gifted_children.label(c)), str(j))
                        for j, c in enumerate(slot)
                    ],
                    required=True,
                    hint=f"Brought by its ceannaire, {escape(ceannaire)}."
                    if ceannaire
                    else "",
                )
            )
        found.append(
            DialogField(
                "how",
                "Given out",
                "select",
                BY_BIDDING,
                options=[(w, w) for w in (BY_BIDDING, BY_HAND)],
                required=True,
                hint="By bidding: each represented covenant bids vis by its magi "
                "without an apprentice, its vis and a roll; the highest wins, "
                "paid from its stores.",
            )
        )
        options = [
            (escape(f"{m.name} ({c.name})"), m.id)
            for c in represented(saga, tribunal, meeting)
            for m in world.covenant_magi(saga, c)
        ]
        for index, slot in enumerate(candidates(saga, tribunal, meeting)):
            found.append(
                DialogField(
                    f"claim_{index}",
                    f"{escape(slot[0].get('tuath') or f'Túath {index + 1}')}: goes to",
                    "select",
                    None,
                    options=options,
                    allow_blank=True,
                    placeholder="(unclaimed)",
                    show_if=lambda v: v.get("how") == BY_HAND,
                )
            )
        found.append(core._note_field(meeting, self.key))
        return found

    def validate(self, meeting: Meeting, values: dict[str, Any]):
        if values.get("how") != BY_HAND:
            return None
        claimed = [v for k, v in values.items() if k.startswith("claim_") and v]
        if len(claimed) != len(set(claimed)):
            return "Each magus takes one child."
        record = _record(meeting)
        for index, slot in enumerate(record.get("candidates", [])):
            pick = int(values.get(f"child_{index}") or 0)
            child = slot[pick] if 0 <= pick < len(slot) else slot[0]
            if values.get(f"claim_{index}") and child.get("false_gift"):
                return f"{child['name']} has no true Gift: no magus takes them."
        return None

    def live(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        if self._given(meeting) is not None:
            return ""
        children = chosen(saga, tribunal, meeting, values)
        given = awards(saga, tribunal, meeting, values)
        return "\n".join(
            escape(_award_text(saga, c, a)) for c, a in zip(children, given)
        )

    def apply(
        self, saga: Saga, tribunal: Tribunal, meeting: Meeting, values: dict[str, Any]
    ):
        core._keep_note(meeting, self.key, values)
        if self._given(meeting) is not None:
            return
        year = _year(saga, meeting)
        children = chosen(saga, tribunal, meeting, values)
        given = []
        for child, award in zip(children, awards(saga, tribunal, meeting, values)):
            master = saga.character(award.master_id)
            covenant = saga.covenant(award.covenant_id)
            kept: dict[str, Any] = {"child": child, "price": award.price}
            if master is not None and covenant is not None:
                if award.price:
                    _pay(saga, covenant, award.price, child)
                apprentice = _apprentice(saga, child, master, covenant, year)
                kept.update(
                    covenant_id=covenant.id,
                    master_id=master.id,
                    character_id=apprentice.id,
                    bids=[list(b) for b in award.bids],
                )
            given.append(kept)
        _record(meeting)["given"] = given

    def _lines(self, saga: Saga, meeting: Meeting) -> list[str]:
        return [
            _award_text(
                saga,
                g["child"],
                gifted_children.Award(
                    g.get("covenant_id"), g.get("master_id"), g.get("price", 0)
                ),
            )
            for g in self._given(meeting) or []
        ]

    def text(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, meeting)
        return core._join(
            *(escape(line) for line in lines), core._note_text(meeting, self.key)
        )

    def save_label(self):
        return "Give"

    def minutes(self, saga: Saga, tribunal: Tribunal, meeting: Meeting):
        lines = self._lines(saga, meeting)
        if not lines:
            return "", ""
        taken = sum(1 for g in self._given(meeting) or [] if g.get("master_id"))
        return (
            "The Coill Trí gave the Gifted children their treaty owes: "
            + "; ".join(lines)
            + ".",
            f"{taken} apprentice{'' if taken == 1 else 's'}",
        )


core.register_step("sacred_council", "The Sacred Council", SacredCouncil, "opening")
core.register_step("tithe", "The tithe of Gifted children", Tithe, "closing")
