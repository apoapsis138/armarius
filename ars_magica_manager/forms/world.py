"""The forms of the saga's world shared by every record that has them: an
attitude's reasons, the favours owed, and links to other records, each
with its Add, Edit and Delete (commands.SectionOps); and a sketch
covenant's own fields."""

from __future__ import annotations

from typing import Any

from .. import catalog, creation, deletion, places, vassals, viewing, world
from ..commands import Choice, Choose, Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import EMPHASIS_HINT, DialogField, attr, pairs
from ..markup import escape
from ..models import (
    ATTITUDE_RANGE,
    FULL,
    LINE,
    LINK_KINDS,
    SEASONS,
    SKETCH,
    Attitude,
    Character,
    Covenant,
    Favour,
    Link,
    Reason,
    Saga,
)
from ..rules import sites
from ..sections import (
    ATTITUDE_SECTION,
    FAVOURS_SECTION,
    LINKS_SECTION,
    MAGI_SECTION,
    WHAT_MATTERS_SECTION,
)
from ..sheets.character import house_name
from ..tables import Table
from .secrets import secrets_ops
from .tribunal import package_fields, save_package_fields, tribunal_field

#: How each link kind is named in a form.
LINK_NOUNS: dict[str, str] = {
    "characters": "Character",
    "covenants": "Covenant",
    "books": "Book",
    "possessions": "Possession",
    "familiars": "Familiar",
    "places": "Place",
    "creatures": "Creature",
}


def _when_fields(saga: Saga, year: int | None, season: str) -> list[DialogField]:
    return [
        DialogField("year", "Year", "optint", year),
        DialogField(
            "season",
            "Season",
            "select",
            season or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
    ]


# -- attitude --


def attitude_targets(saga: Saga, record: Any) -> list[Covenant]:
    """The player covenants `record` can hold an attitude toward: every
    one but itself."""
    return [c for c in world.player_covenants(saga) if c is not record]


def attitude_entries(saga: Saga, record: Any) -> list[tuple[str, int | None]]:
    """The attitude section's rows, as (player covenant id, reason index),
    a None index being the score it started at."""
    entries: list[tuple[str, int | None]] = []
    for covenant in attitude_targets(saga, record):
        entries.append((covenant.id, None))
        attitude = world.attitude_toward(record, covenant.id)
        if attitude is not None:
            entries += [(covenant.id, i) for i in range(len(attitude.reasons))]
    return entries


def attitude_rows(saga: Saga, record: Any) -> list[tuple[int | None, str]]:
    """The attitude section as SelectableList rows: a heading per player
    covenant with its seal, then where it started and each reason."""
    rows: list[tuple[int | None, str]] = []
    position = 0
    for covenant in attitude_targets(saga, record):
        attitude = world.attitude_toward(record, covenant.id)
        score = world.attitude_score(attitude)
        rows.append(
            (None, f"[b]Toward {escape(covenant.name)}:[/] {world.seal_markup(score)}")
        )
        start = attitude.start if attitude is not None else 0
        rows.append((position, f"  {'Started':<12} {world.signed(start):>2}"))
        position += 1
        for reason in attitude.reasons if attitude is not None else []:
            when = world.when_text(reason.year, reason.season) or "—"
            rows.append(
                (
                    position,
                    f"  {when:<12} {world.signed(reason.change):>2}  "
                    f"{escape(reason.what)}",
                )
            )
            position += 1
    return rows


def _attitude(record: Any, covenant_id: str) -> Attitude:
    """`record`'s attitude toward `covenant_id`, made at 0 if it has none."""
    found = world.attitude_toward(record, covenant_id)
    if found is None:
        found = Attitude(covenant_id)
        record.attitudes.append(found)
    return found


def _change_problem(values: dict[str, Any]) -> str | None:
    if not values.get("change"):
        return "The change can't be 0: say how far it moved, +1 or −1."
    return None


def reason_fields(
    saga: Saga, record: Any, covenant_id: str | None, reason: Reason | None
) -> list[DialogField]:
    targets = attitude_targets(saga, record)
    fields = []
    if reason is None:
        fields.append(
            DialogField(
                "covenant",
                "Toward",
                "select",
                covenant_id or (targets[0].id if targets else None),
                options=[(c.name, c.id) for c in targets],
            )
        )
    fields += [
        DialogField(
            "what",
            "What happened",
            "text",
            attr(reason, "what", ""),
            required=True,
            placeholder="e.g. Helped at the ford",
        ),
        DialogField(
            "change",
            "Change (+1, −1 or more)",
            "int",
            attr(reason, "change", 1),
        ),
        *_when_fields(
            saga,
            reason.year if reason is not None else saga.current_year,
            reason.season if reason is not None else saga.current_season,
        ),
    ]
    return fields


def _start_form(record: Any, covenant: Covenant) -> Form:
    attitude = world.attitude_toward(record, covenant.id)
    low, high = ATTITUDE_RANGE

    def apply(values: dict[str, Any]) -> None:
        _attitude(record, covenant.id).start = values["start"]

    return Form(
        f"Attitude toward {covenant.name}",
        lambda: [
            DialogField(
                "start",
                f"Started at ({low:+d} to {high:+d})",
                "int",
                attitude.start if attitude is not None else 0,
                hint="Where it stood before any reason was written down.",
            )
        ],
        apply,
        validate=lambda values: (
            None
            if low <= values["start"] <= high
            else f"The start must be between {low:+d} and {high:+d}."
        ),
    )


def attitude_ops(saga: Saga, record: Any) -> SectionOps:
    """Add, Edit and Delete for `record`'s attitude reasons toward each
    player covenant. Editing the "Started" row sets where it began;
    a reason's change moves the score, which is worked out, never stored."""

    def entries() -> list[tuple[str, int | None]]:
        return attitude_entries(saga, record)

    def add(covenant_id: str | None = None) -> Command:
        if not attitude_targets(saga, record):
            return Refuse(
                "Add a Reason",
                "There is no player covenant for it to have an attitude toward.",
            )

        def apply(values: dict[str, Any]) -> None:
            _attitude(record, values["covenant"]).reasons.append(
                Reason(
                    values["what"],
                    values["change"],
                    values.get("year"),
                    values.get("season") or "",
                )
            )

        return Form(
            "Add a Reason",
            lambda: reason_fields(saga, record, covenant_id, None),
            apply,
            validate=_change_problem,
        )

    def edit(index: int) -> Command:
        covenant_id, reason_index = entries()[index]
        covenant = saga.covenant(covenant_id)
        assert covenant is not None
        if reason_index is None:
            return _start_form(record, covenant)
        reason = _attitude(record, covenant_id).reasons[reason_index]

        def apply(values: dict[str, Any]) -> None:
            reason.what = values["what"]
            reason.change = values["change"]
            reason.year = values.get("year")
            reason.season = values.get("season") or ""

        return Form(
            "Edit a Reason",
            lambda: reason_fields(saga, record, covenant_id, reason),
            apply,
            validate=_change_problem,
        )

    def remove(index: int) -> Command:
        covenant_id, reason_index = entries()[index]
        if reason_index is None:
            return Refuse(
                "Delete",
                "Where it started can't be deleted: edit it to change it.",
            )
        reasons = _attitude(record, covenant_id).reasons
        reason = reasons[reason_index]

        def apply() -> None:
            reasons.remove(reason)

        return Confirm(f"Delete the reason {escape(reason.what)}?", apply)

    def rows() -> list[str]:
        out = []
        for covenant_id, reason_index in entries():
            covenant = saga.covenant(covenant_id)
            name = covenant.name if covenant is not None else ""
            if reason_index is None:
                out.append(f"where it started toward {name}")
            else:
                out.append(_attitude(record, covenant_id).reasons[reason_index].what)
        return out

    return SectionOps(add=add, edit=edit, remove=remove, rows=rows)


# -- favours --


def favour_fields(saga: Saga, favour: Favour | None) -> list[DialogField]:
    return [
        DialogField(
            "what",
            "What for",
            "text",
            attr(favour, "what", ""),
            required=True,
            placeholder="e.g. Hid a fugitive grog",
        ),
        DialogField(
            "owed_by",
            "Owed by",
            "text",
            attr(favour, "owed_by", ""),
            placeholder="e.g. Fengheld",
        ),
        DialogField(
            "owed_to",
            "Owed to",
            "text",
            attr(favour, "owed_to", ""),
            placeholder="e.g. Arnhaven",
        ),
        *_when_fields(
            saga,
            favour.year if favour is not None else saga.current_year,
            favour.season if favour is not None else saga.current_season,
        ),
        DialogField(
            "repaid_year",
            "Repaid in (year)",
            "optint",
            attr(favour, "repaid_year", None),
            hint="Leave blank while it is still owed.",
        ),
        DialogField(
            "repaid_season",
            "Repaid in (season)",
            "select",
            attr(favour, "repaid_season", "") or None,
            options=pairs(SEASONS),
            allow_blank=True,
        ),
    ]


def _set_favour(favour: Favour, values: dict[str, Any]) -> None:
    favour.what = values["what"]
    favour.owed_by = values.get("owed_by", "")
    favour.owed_to = values.get("owed_to", "")
    favour.year = values.get("year")
    favour.season = values.get("season") or ""
    favour.repaid_year = values.get("repaid_year")
    favour.repaid_season = values.get("repaid_season") or ""


def favour_ops(saga: Saga, record: Any) -> SectionOps:
    favours: list[Favour] = record.favours

    def form(title: str, index: int | None) -> Form:
        existing = favours[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            favour = existing if existing is not None else Favour("")
            _set_favour(favour, values)
            if existing is None:
                favours.append(favour)

        return Form(title, lambda: favour_fields(saga, existing), apply)

    def remove(index: int) -> Command:
        favour = favours[index]

        def apply() -> None:
            favours.remove(favour)

        return Confirm(f"Delete the favour {escape(favour.what)}?", apply)

    return SectionOps(
        add=lambda: form("Add a Favour", None),
        edit=lambda index: form("Edit a Favour", index),
        remove=remove,
        rows=lambda: [f.what for f in favours],
    )


# -- links --


def link_candidates(saga: Saga, record: Any, kind: str) -> list[tuple[str, str]]:
    """The records of `kind` a link could point at, as (name, id) pairs;
    never `record` itself."""
    if kind == "possessions":
        found = [p for c in saga.covenants for p in c.possessions]
    else:
        found = list(getattr(saga, kind, None) or [])
    return [
        (getattr(r, "name", "") or "(unnamed)", r.id)
        for r in found
        if r is not record and getattr(r, "id", None)
    ]


def link_fields(
    saga: Saga, record: Any, kind: str, link: Link | None
) -> list[DialogField]:
    return [
        DialogField(
            "target_id",
            LINK_NOUNS.get(kind, kind.title()),
            "select",
            attr(link, "target_id", None),
            options=link_candidates(saga, record, kind),
            required=True,
        ),
        DialogField(
            "note",
            "Note",
            "text",
            attr(link, "note", ""),
            placeholder="e.g. Holds the ford's vis",
        ),
    ]


def link_ops(saga: Saga, record: Any) -> SectionOps:
    links: list[Link] = record.links

    def link_form(kind: str, existing: Link | None) -> Form:
        def apply(values: dict[str, Any]) -> None:
            if existing is None:
                links.append(Link(kind, values["target_id"], values.get("note", "")))
            else:
                existing.target_id = values["target_id"]
                existing.note = values.get("note", "")

        return Form(
            f"{'Edit' if existing else 'Add'} a Link",
            lambda: link_fields(saga, record, kind, existing),
            apply,
        )

    def add() -> Command:
        kinds = [k for k in LINK_KINDS if link_candidates(saga, record, k)]
        if not kinds:
            return Refuse("Add a Link", "There is nothing in the saga to link to yet.")
        return Choose(
            "Link to what?",
            lambda: [Choice(LINK_NOUNS.get(k, k), k) for k in kinds],
            lambda kind: link_form(kind, None),
        )

    def remove(index: int) -> Command:
        link = links[index]

        def apply() -> None:
            links.remove(link)

        return Confirm(f"Delete the link to {world.link_label(saga, link)}?", apply)

    return SectionOps(
        add=add,
        edit=lambda index: link_form(links[index].kind, links[index]),
        remove=remove,
        rows=lambda: [world.link_label(saga, link) for link in links],
    )


def link_rows(saga: Saga, record: Any) -> list[tuple[int | None, str]]:
    """The links as rows, each with its kind; a link to a record the
    reader doesn't know of is left out (viewing.py). The records that link
    here are the page's Linked from (connections)."""
    return [
        (i, f"{LINK_NOUNS.get(link.kind, link.kind)}: {world.link_label(saga, link)}")
        for i, link in enumerate(record.links)
        if (target := world.link_target(saga, link)) is None or viewing.reads(target)
    ]


# -- a sketch covenant --


def sketch_covenant_fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    """Edit Covenant at Line or Sketch detail: who it is, and for a sketch
    its season, aura, founding and unnamed magi."""
    fields = [
        DialogField("name", "Name", "text", covenant.name, required=True),
        tribunal_field(saga, covenant.tribunal_id),
        DialogField(
            "summary",
            "In the Saga",
            "area",
            covenant.summary,
            hint="A sentence or a paragraph: who they are to the player "
            f"covenants. {EMPHASIS_HINT}",
        ),
    ]
    if covenant.detail != LINE:
        fields += [
            DialogField(
                "covenant_season",
                "Covenant Season",
                "select",
                covenant.covenant_season,
                options=pairs(SEASONS),
            ),
            *(
                []
                if sites.covenant_place(saga, covenant) is not None
                else [DialogField("aura", "Aura", "int", covenant.aura)]
            ),
            places.where_field(saga, covenant, "Place"),
            DialogField(
                "year_founded", "Year Founded", "optint", covenant.year_founded
            ),
            DialogField(
                "unnamed_magi",
                "Unnamed magi",
                "int",
                covenant.unnamed_magi,
                hint="Magi counted for its votes but never written down.",
            ),
        ]
    fields.append(
        DialogField(
            "played",
            "Played by the troupe",
            "check",
            covenant.played,
            hint="A player covenant: other records' attitudes point at it.",
        )
    )
    return fields + package_fields(saga, covenant) + vassals.fields(saga, covenant)


def _unnamed_problem(values: dict[str, Any]) -> str | None:
    if values.get("unnamed_magi", 0) < 0:
        return "Unnamed magi can't be fewer than none."
    return None


def sketch_covenant_form(saga: Saga, covenant: Covenant) -> Form:
    def apply(values: dict[str, Any]) -> None:
        values = dict(values)
        covenant.tribunal_id = values.get("tribunal_id", covenant.tribunal_id)
        save_package_fields(saga, covenant, values)
        vassals.save(saga, covenant, values)
        if "where" in values:
            places.put(covenant, values.pop("where"))
        for key, value in values.items():
            setattr(covenant, key, value)
        places.sync(saga)

    return Form(
        "Edit Covenant",
        lambda: sketch_covenant_fields(saga, covenant),
        apply,
        validate=lambda values: (
            _unnamed_problem(values) or vassals.problem(saga, covenant, values)
        ),
    )


def what_matters_form(covenant: Covenant) -> Form:
    def apply(values: dict[str, Any]) -> None:
        covenant.what_matters = values["what_matters"]

    return Form(
        "What Matters",
        lambda: [
            DialogField(
                "what_matters",
                "What Matters",
                "area",
                covenant.what_matters,
                hint="One short entry a line; start one with a label and a "
                'colon to head it ("Vis: Vim 6 a year").',
            )
        ],
        apply,
    )


def what_matters_text(covenant: Covenant) -> str:
    rows = world.what_matters_rows(covenant.what_matters)
    if not rows:
        return "[$label]Nothing written yet: edit it to say what matters to it.[/]"
    return "\n".join(
        f"• [b]{escape(label)}:[/] {escape(words)}" if label else f"• {escape(words)}"
        for label, words in rows
    )


# -- a sketch covenant's magi --


def magus_fields(magus: Character | None) -> list[DialogField]:
    return [
        DialogField("name", "Name", "text", attr(magus, "name", ""), required=True),
        DialogField(
            "house",
            "House",
            "select",
            magus.hermetic.house if magus is not None else None,
            options=[(h.name, h.id) for h in catalog.load_house_catalog()],
            allow_blank=True,
        ),
        DialogField(
            "detail",
            "Detail",
            "select",
            attr(magus, "detail", LINE),
            options=pairs((LINE, SKETCH)),
            hint="Promote a magus to a full character from their own sheet.",
        )
        if magus is None or magus.detail != FULL
        else DialogField("detail", "Detail", "info", FULL),
        DialogField(
            "summary",
            "In the Saga",
            "area",
            attr(magus, "summary", ""),
            placeholder="e.g. Prosecutes Arnhaven over the ford",
        ),
    ]


def _set_magus(magus: Character, values: dict[str, Any]) -> None:
    magus.name = values["name"]
    magus.hermetic.house = values.get("house")
    if values.get("detail"):
        magus.detail = values["detail"]
    magus.summary = values.get("summary", "")


def magus_ops(saga: Saga, covenant: Covenant) -> SectionOps:
    """A sketch covenant's named magi: Add writes a new line or sketch
    magus into it, Edit their name, House, detail and part in the saga,
    and Delete removes the character, saying what goes with them."""

    def magi() -> list[Character]:
        return world.covenant_magi(saga, covenant)

    def add() -> Command:
        def apply(values: dict[str, Any]) -> None:
            magus = creation.add_character(saga, values["name"], "magus", covenant.id)
            magus.in_creation = False
            _set_magus(magus, values)

        return Form("Add a Magus", lambda: magus_fields(None), apply, save_label="Add")

    def edit(index: int) -> Command:
        magus = magi()[index]
        return Form(
            f"Edit {magus.name}",
            lambda: magus_fields(magus),
            lambda values: _set_magus(magus, values),
        )

    def remove(index: int) -> Command:
        magus = magi()[index]
        consequences = deletion.character_consequences(saga, magus)
        message = f"Delete {escape(magus.name)}?"
        if consequences:
            message += "\n\n" + "\n".join(map(escape, consequences))
        return Confirm(message, lambda: deletion.delete_character(saga, magus))

    return SectionOps(
        add=add, edit=edit, remove=remove, rows=lambda: [m.name for m in magi()]
    )


def magi_rows(saga: Saga, covenant: Covenant) -> list[tuple[int | None, str]]:
    """The magi as a table: name, House, detail and votes; then the
    unnamed magi, counted."""
    magi = world.covenant_magi(saga, covenant)
    rows: list[tuple[int | None, str]] = []
    if magi:
        rows.append(
            (None, f"[$label]  {'Magus':<26} {'House':<12} {'Detail':<7} Votes[/]")
        )
    for index, magus in enumerate(magi):
        rows.append(
            (
                index,
                f"{escape(magus.name[:26]):<26} {escape((house_name(magus) or '—')[:12]):<12} "
                f"{magus.detail:<7} 1",
            )
        )
    if covenant.unnamed_magi:
        noun = "magus" if covenant.unnamed_magi == 1 else "magi"
        votes = "vote" if covenant.unnamed_magi == 1 else "votes"
        rows.append(
            (
                None,
                f"[$label]+ {covenant.unnamed_magi} unnamed {noun}, "
                f"{covenant.unnamed_magi} {votes}[/]",
            )
        )
    if not rows:
        rows.append((None, "[$label]No magi written down.[/]"))
    return rows


def magi_title(saga: Saga, covenant: Covenant) -> str:
    named = len(world.covenant_magi(saga, covenant))
    if covenant.unnamed_magi:
        return f"Magi ({named} named, {covenant.unnamed_magi} unnamed)"
    return f"Magi ({named})"


def covenant_ops(saga: Saga, covenant: Covenant) -> dict[str, SectionOps]:
    """The core sections a Line or Sketch covenant's sheet shows, by id."""
    return {
        MAGI_SECTION: magus_ops(saga, covenant),
        WHAT_MATTERS_SECTION: SectionOps(edit=lambda _row: what_matters_form(covenant)),
        **record_ops(saga, covenant),
    }


def standing_ops(saga: Saga, record: Any) -> dict[str, SectionOps]:
    """Attitude and favours: a record's standing with the troupe."""
    return {
        ATTITUDE_SECTION: attitude_ops(saga, record),
        FAVOURS_SECTION: favour_ops(saga, record),
    }


def record_ops(saga: Saga, record: Any) -> dict[str, SectionOps]:
    """Attitude, favours, links and secrets: the sections any world
    record has."""
    return {
        **standing_ops(saga, record),
        LINKS_SECTION: link_ops(saga, record),
        **secrets_ops(record),
    }


# -- the same sections as tables, for a page that draws columns --


def attitude_table(saga: Saga, record: Any) -> Table:
    """The attitude section's rows as a table: a heading per player
    covenant, then where it started and each reason (keys as
    attitude_ops counts them)."""
    rows: list[list[str]] = []
    keys: list[int | None] = []
    position = 0
    for covenant in attitude_targets(saga, record):
        attitude = world.attitude_toward(record, covenant.id)
        score = world.attitude_score(attitude)
        rows.append([f"Toward {escape(covenant.name)}: {world.seal_markup(score)}"])
        keys.append(None)
        rows.append(["", "Started", world.signed(attitude.start if attitude else 0)])
        keys.append(position)
        position += 1
        for reason in attitude.reasons if attitude is not None else []:
            rows.append(
                [
                    escape(reason.what),
                    world.when_text(reason.year, reason.season),
                    world.signed(reason.change),
                ]
            )
            keys.append(position)
            position += 1
    return Table(["Reason", "When", "Change"], rows, keys, markup=True)


def favour_table(record: Any) -> Table:
    rows = []
    for favour in record.favours:
        repaid = (
            ""
            if world.favour_is_open(favour)
            else world.when_text(favour.repaid_year, favour.repaid_season) or "yes"
        )
        rows.append(
            [
                escape(favour.what),
                escape(favour.owed_by),
                escape(favour.owed_to),
                world.when_text(favour.year, favour.season),
                repaid,
            ]
        )
    return Table(["Favour", "Owed by", "Owed to", "Since", "Repaid"], rows, markup=True)


def link_table(saga: Saga, record: Any) -> Table:
    """The links, each with its kind; a link to a record the reader
    doesn't know of is left out (viewing.py)."""
    rows = []
    keys: list[int | None] = []
    for index, link in enumerate(record.links):
        target = world.link_target(saga, link)
        if target is not None and not viewing.reads(target):
            continue
        name = getattr(target, "name", "") if target is not None else "(gone)"
        keys.append(index)
        rows.append(
            [escape(name), LINK_NOUNS.get(link.kind, link.kind), escape(link.note)]
        )
    return Table(["Linked to", "What", "Note"], rows, keys, markup=True)


def magi_table(saga: Saga, covenant: Covenant) -> Table:
    rows: list[list[str]] = []
    keys: list[int | None] = []
    for index, magus in enumerate(world.covenant_magi(saga, covenant)):
        rows.append(
            [
                escape(magus.name),
                escape(house_name(magus) or ""),
                "1",
                escape(magus.summary.splitlines()[0] if magus.summary else ""),
                magus.detail,
            ]
        )
        keys.append(index)
    if covenant.unnamed_magi:
        rows.append(
            [
                f"{covenant.unnamed_magi} more",
                "",
                str(covenant.unnamed_magi),
                "Unnamed",
                "Count only",
            ]
        )
        keys.append(None)
    return Table(
        ["Magus", "House", "Votes", "Role", "Detail"],
        rows,
        keys,
        markup=True,
        stretch=3,
    )
