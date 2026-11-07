"""Merge Doubled Records: a person or being kept twice, once as a
neighbour (a faction, most often) and once as the character or Bestiary
creature of the same name, made one record.

Before characters and creatures could hold an attitude, a faerie knight
or a hedge witch the troupe dealt with was entered as a faction to carry
one, and as a creature or character for the stat block, joined only by
the name (and often a link noted "its stat block"). Merging moves what
the neighbour holds onto the character or creature (its attitudes,
favours, links, summary, Secrets, place and pins, the factions it
belongs to, the neighbours it rules) and takes the neighbour away. Only a
faction is offered: a lord, a threat or a place named for its person
keeps rules of its own (a sacred grove and the spirit in it are two
records on purpose). What a faction says of itself (its rules, wants,
offers and diary) goes into the summary, or a creature's notes.

Nothing merges unasked: the storyguide ticks which pairs to merge, and
the form says what each brings.

Pattern: Command, as every step is (commands.Form); the move itself is
one function per piece of the record, run in order."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import memberships, places, references
from .commands import Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Creature, Neighbour, Saga

TITLE = "Merge Doubled Records"


@dataclass(frozen=True)
class Double:
    """A neighbour and the one character or creature with its name."""

    neighbour: Neighbour
    record: Character | Creature

    @property
    def kind(self) -> str:
        return "character" if isinstance(self.record, Character) else "creature"


def _key(name: str) -> str:
    return " ".join(name.casefold().split())


def doubles(saga: Saga) -> list[Double]:
    """Each faction whose name exactly one character or creature has, in
    the Region's order. Only a faction: a lord, a threat or a place
    named for its person ("The Ash of Nortorf" the story and the spirit)
    keeps rules of its own and is a record apart."""
    by_name: dict[str, list[Character | Creature]] = {}
    for record in [*saga.characters, *saga.creatures]:
        by_name.setdefault(_key(record.name), []).append(record)
    found = []
    for neighbour in saga.neighbours:
        if neighbour.kind != "faction":
            continue
        named = by_name.get(_key(neighbour.name), [])
        if len(named) == 1:
            found.append(Double(neighbour, named[0]))
    return found


def brings(saga: Saga, double: Double) -> str:
    """What merging moves, in a line: "2 favours, a link, its summary,
    member of The Spinner's Court"."""
    n = double.neighbour
    parts = []
    held = [a for a in n.attitudes if a.start or a.reasons]
    if held:
        parts.append(f"attitude toward {len(held)} covenant{'s' * (len(held) > 1)}")
    if n.favours:
        parts.append(f"{len(n.favours)} favour{'s' * (len(n.favours) > 1)}")
    links = [k for k in n.links if not _points_at(k, double.record)]
    if links:
        parts.append(f"{len(links)} link{'s' * (len(links) > 1)}")
    if n.summary.strip() or _faction_words(n):
        parts.append("its summary, wants and offers")
    groups = memberships.factions_of(saga, n)
    if groups:
        parts.append("member of " + ", ".join(f.name for f, _ in groups))
    ruled = references.ruled_by(saga, n)
    if ruled:
        parts.append("rules " + ", ".join(r.name for r in ruled))
    return "; ".join(parts) or "nothing besides its name"


# -- the move --


def _points_at(link: Any, record: Character | Creature) -> bool:
    kind = "characters" if isinstance(record, Character) else "creatures"
    return link.kind == kind and link.target_id == record.id


def _written(old: str, new: str) -> str:
    """`old` with `new` after it, a blank line between; once only."""
    old, new = old.strip(), new.strip()
    if not new or new in old:
        return old
    return f"{old}\n\n{new}" if old else new


def _move_standing(n: Neighbour, record: Character | Creature) -> None:
    held = {a.covenant_id for a in record.attitudes}
    record.attitudes += [a for a in n.attitudes if a.covenant_id not in held]
    record.favours += n.favours
    record.links += [k for k in n.links if not _points_at(k, record)]


def _faction_words(n: Neighbour) -> str:
    """What a faction says of itself that a person keeps as words: its
    rules, wants and offers, and its diary, a paragraph each."""
    d = n.details
    lines = [
        f"{label}: {value.strip()}"
        for label, key in (
            ("Its rules", "rules"),
            ("Wants", "wants"),
            ("Offers", "offers"),
        )
        if isinstance(value := d.get(key), str) and value.strip()
    ]
    diary = [
        " ".join(str(p) for p in (e.get("season"), e.get("year")) if p)
        + f": {e.get('text', '')}"
        for e in d.get("diary") or []
        if isinstance(e, dict)
    ]
    if diary:
        lines.append("Diary:\n" + "\n".join(f"- {line}" for line in diary))
    return "\n\n".join(lines)


def _move_words(n: Neighbour, record: Character | Creature) -> None:
    words = _written(n.summary, _faction_words(n))
    if isinstance(record, Character):
        record.summary = _written(record.summary, words)
    else:
        record.notes = _written(record.notes, words)
    record.secrets = [
        *record.secrets,
        *(s for s in n.secrets if s not in record.secrets),
    ]


def _move_place(n: Neighbour, record: Character | Creature) -> None:
    if isinstance(record, Creature) and record.place_id is None and n.place_id:
        record.place_id, record.place_level = n.place_id, n.place_level


def _move_ties(saga: Saga, n: Neighbour, record: Character | Creature) -> None:
    """The factions it belongs to, the neighbours it rules, and a
    creature's pins, now the record's; those that answered to it answer
    to no one."""
    was, now = memberships.who_of(n), memberships.who_of(record)
    for faction in saga.neighbours:
        for member in faction.details.get("roster") or []:
            if member.get("who") == was:
                member["who"] = now
    for ruled in references.ruled_by(saga, n):
        ruled.ruler = record.id
    for other in saga.neighbours:
        if other.answers_to == n.id:
            other.answers_to = None
    if isinstance(record, Creature):
        _move_pins(saga, n, record)
    saga.pins = [
        p for p in saga.pins if not (p.kind == "neighbours" and p.record_id == n.id)
    ]


def _move_pins(saga: Saga, n: Neighbour, creature: Creature) -> None:
    """The neighbour's pins, the creature's on each map it has none on (a
    character has no pins: the Atlas shows him at his covenant's)."""
    pinned = {
        p.map_id
        for p in saga.pins
        if p.kind == "creatures" and p.record_id == creature.id
    }
    for pin in saga.pins:
        if (
            pin.kind == "neighbours"
            and pin.record_id == n.id
            and pin.map_id not in pinned
        ):
            pin.kind, pin.record_id = "creatures", creature.id
            pinned.add(pin.map_id)


def merge(saga: Saga, double: Double) -> None:
    """Make the pair one record: the character's or creature's."""
    n, record = double.neighbour, double.record
    _move_standing(n, record)
    _move_words(n, record)
    _move_place(n, record)
    _move_ties(saga, n, record)
    saga.neighbours.remove(n)
    places.sync(saga)


# -- the form --


def merge_form(saga: Saga) -> Form | Refuse:
    """Each doubled pair, ticked, with what merging it brings; the ticked
    ones are merged."""
    found = doubles(saga)
    if not found:
        return Refuse(
            TITLE,
            "No neighbour shares its name with a character or a creature.",
        )

    def fields() -> list[DialogField]:
        shown = [
            DialogField(
                "_lead",
                "",
                "info",
                "Each neighbour below has the name of one character or creature. "
                "Merging moves what the neighbour holds onto that record and "
                "takes the neighbour away.",
            )
        ]
        for index, double in enumerate(found):
            shown += [
                DialogField(
                    f"_pair_{index}",
                    "",
                    "info",
                    f"{escape(double.neighbour.name)}: the "
                    f"{escape(double.neighbour.kind)} into the {double.kind}. "
                    f"Brings {escape(brings(saga, double))}.",
                ),
                DialogField(f"merge_{index}", "Merge", "check", True),
            ]
        return shown

    def apply(values: dict[str, Any]) -> list[str]:
        merged = [d for i, d in enumerate(found) if values.get(f"merge_{i}")]
        for double in merged:
            merge(saga, double)
        if not merged:
            return notes("Nothing merged.")
        return notes(
            *(f"Merged {escape(d.neighbour.name)} into the {d.kind}." for d in merged)
        )

    return Form(TITLE, fields, apply, save_label="Merge", help_id="merge-doubles")
