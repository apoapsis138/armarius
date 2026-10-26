"""The add/edit form for a possession, independent of how it is drawn: a
covenant's (property, sanctums, weapons, armor, vis sources and stores,
items), a character's Personal Gear, or a familiar's Natural Weapons.

`possession_fields` is the form's fields; `possession_form` bundles them
with the form's checks and live line as a commands.Form whose `apply` the
caller gives. `possession_ops` is a covenant's Possessions section's Add,
Edit and Delete.
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Sequence
from typing import Any

from .. import catalog, sourcebooks, vis
from .. import possessions as pos
from ..arts import ARTS
from ..commands import Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, attr, description_field, pairs
from ..markup import escape
from ..models import (
    ARMOR_SLOTS,
    GEAR_QUALITIES,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    SANCTUM_USAGE_DEFAULT,
    SANCTUM_USAGES,
    SEASONS,
    ArmorPieceDef,
    Covenant,
    Saga,
)
from ..rules import equipment, vis_kinds

#: The book whose armour pieces an armor form offers.
LORDS_OF_MEN = "LoM"

#: A year's pawns from a source, by its yield and the saga's vis level
#: (Covenants p. 72).
VIS_YIELD_HINT = (
    "A year's pawns (Covenants p. 72): a low-yield source 1, 2 or 4 in a "
    "low-, moderate- or high-vis saga; moderate 2, 4 or 8; high 4, 8 or 16."
)


def possession_fields(
    kind: str,
    entry: pos.PossessionEntry | None,
    *,
    natural: bool = False,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
    vis_kind_options: Sequence[tuple[str, str]] | None = None,
    books: Collection[str] | None = None,
) -> list[DialogField]:
    """The add/edit form for one kind of possession. For a laboratory listed as
    a sanctum, name/owner/location/build points are shown read-only (edit them
    on the laboratory) and only the covenant-side fields are editable.
    `natural`: a familiar's Natural Weapons. A Raw Vis Store's asks where it
    is kept: one of `places` (vis.location_options), `place` to start with.
    A vis source or store offers `vis_kind_options` as its kind of vis
    (vis_kinds.kind_options; None: every kind). A weapon's book entries
    are those of the `books` in play (sourcebooks.saga_books; None: every
    book), and the one it was filled from."""
    auto = entry is not None and entry.auto
    fields = (
        _sanctum_from_lab_fields(kind, entry)
        if auto and entry is not None
        else [
            DialogField("name", "Name", "text", attr(entry, "name", ""), required=True)
        ]
    )
    if kind == "property":
        fields += _property_fields(entry)
    elif kind == "sanctum":
        fields += _sanctum_fields(entry, auto)
    elif kind in pos.QUANTITY_KINDS:
        fields += _quantity_possession_fields(kind, entry, natural=natural, books=books)
    elif kind in ("vis_source", "vis_store"):
        fields += _vis_possession_fields(kind, entry, places, place)
        fields += vis_kind_fields(
            entry.record if entry is not None else None, vis_kind_options
        )

    if kind != "vis_store":
        fields.append(description_field(attr(entry, "description", "")))
    return fields


def possession_live(kind: str) -> Callable[[dict[str, Any]], str] | None:
    """A weapon or armor form's live line: the chosen book entry."""
    if kind not in GEAR_TYPES_BY_KIND:
        return None
    return lambda values: pos.book_text(kind, values.get("gear_id"))


def possession_form(
    title: str,
    kind: str,
    entry: pos.PossessionEntry | None,
    apply: Callable[[dict[str, Any]], Any],
    *,
    natural: bool = False,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
    vis_kind_options: Sequence[tuple[str, str]] | None = None,
    books: Collection[str] | None = None,
) -> Form:
    """The possession form as a step: `apply` gets its values."""
    return Form(
        title,
        lambda: possession_fields(
            kind,
            entry,
            natural=natural,
            places=places,
            place=place,
            vis_kind_options=vis_kind_options,
            books=books,
        ),
        apply,
        validate=pos.form_problem,
        live=possession_live(kind),
    )


def _sanctum_from_lab_fields(
    kind: str, entry: pos.PossessionEntry
) -> list[DialogField]:
    """The read-only fields of a possession listed from a laboratory."""
    note = " (from the laboratory)"
    fields = [
        DialogField("_n", "Name", "info", entry.name + note),
        DialogField("_o", "Owner", "info", (entry.owner or "(none)") + note),
        DialogField("_l", "Location", "info", entry.location or "(not set)"),
        DialogField(
            "_b",
            "Build Points",
            "info",
            "(not set)" if entry.build_points is None else entry.build_points,
        ),
    ]
    if kind == "sanctum":
        fields.append(DialogField("_q", "Quality", "info", str(entry.quality) + note))
        fields.append(
            DialogField("_u", "Upkeep (Points)", "info", str(entry.upkeep) + note)
        )
    return fields


def _property_fields(entry: pos.PossessionEntry | None) -> list[DialogField]:
    return [
        DialogField("location", "Location", "text", attr(entry, "location", "")),
        DialogField("dimensions", "Dimensions", "text", attr(entry, "dimensions", "")),
        DialogField(
            "inhabitants", "Inhabitants", "text", attr(entry, "inhabitants", "")
        ),
    ]


def _sanctum_fields(entry: pos.PossessionEntry | None, auto: bool) -> list[DialogField]:
    """A sanctum's covenant-side fields; one listed from a laboratory keeps
    only Usage editable."""
    fields: list[DialogField] = []
    if not auto:
        fields += [
            # Unowned sanctums are "Free": narratively, visitors can use them.
            DialogField("owner", "Owner", "text", attr(entry, "owner", "Free")),
            DialogField("location", "Location", "text", attr(entry, "location", "")),
            DialogField("quality", "Quality", "optint", attr(entry, "quality", None)),
            DialogField(
                "upkeep", "Upkeep (Points)", "optint", attr(entry, "upkeep", None)
            ),
            DialogField(
                "build_points",
                "Build Points",
                "optint",
                attr(entry, "build_points", None),
            ),
        ]
    fields.append(
        DialogField(
            "usage",
            "Usage",
            "select",
            attr(entry, "usage", SANCTUM_USAGE_DEFAULT),
            options=pairs(SANCTUM_USAGES),
        )
    )
    return fields


def _gear_book_field(
    kind: str,
    entry: pos.PossessionEntry | None,
    natural: bool,
    books: Collection[str] | None = None,
) -> DialogField:
    """The weapon's or armor Material's book entry: choosing one fills in
    the book's figures (see possessions.weapon_fills/armor_fills). A
    supplement's weapon is offered with its book in play (`books`), or when
    it is the one the entry was filled from."""
    if kind == "weapon":
        tables = pos.NATURAL_WEAPON_TABLES if natural else pos.GEAR_WEAPON_TABLES
        keep = attr(entry, "gear_id", None)
        weapons = {
            w.id: w
            for w in catalog.load_weapon_catalog(tables=tables)
            if w.id == keep or sourcebooks.in_play(w.source, books)
        }
        options = [
            (escape(w.name if natural else f"{w.name} ({w.ability})"), w.id)
            for w in weapons.values()
        ]
        label = "Natural Weapon" if natural else "Weapon"

        def fills(values: dict[str, Any]) -> dict[str, Any]:
            return pos.weapon_fills(values, weapons)

    else:
        armors = {a.id: a for a in catalog.load_armor_catalog()}
        options = [
            (
                escape(a.name + (" (partial only)" if a.figures(True) is None else "")),
                a.id,
            )
            for a in armors.values()
        ]
        pieces = armor_pieces(entry, books)
        options += [
            (escape(f"{p.name} ({p.slot}, LoM)"), p.id) for p in pieces.values()
        ]
        label = "Material"

        def fills(values: dict[str, Any]) -> dict[str, Any]:
            return pos.armor_fills(values, armors, pieces)

    return DialogField(
        "gear_id",
        label,
        "select",
        attr(entry, "gear_id", None),
        options=options,
        allow_blank=True,
        placeholder="(custom)",
        fills=fills,
    )


def armor_pieces(
    entry: pos.PossessionEntry | None, books: Collection[str] | None
) -> dict[str, ArmorPieceDef]:
    """Lords of Men's armour pieces an armor form offers: with the book in
    play (`books`), or the one the entry was filled from."""
    keep = attr(entry, "gear_id", None)
    return {
        p.id: p
        for p in catalog.load_armor_piece_catalog()
        if p.id == keep or sourcebooks.in_play(p.source, books)
    }


def _armor_slot_field(
    entry: pos.PossessionEntry | None, books: Collection[str] | None
) -> list[DialogField]:
    """Where a Lords of Men piece is worn ("" a whole suit): offered with
    the book in play, or for an entry already worn as a piece."""
    slot = attr(entry, "armor_slot", "")
    if not slot and not sourcebooks.in_play(LORDS_OF_MEN, books):
        return []
    return [
        DialogField(
            "armor_slot",
            "Worn as",
            "select",
            slot,
            options=[("Whole suit", "")] + [(s, s) for s in ARMOR_SLOTS],
            hint="A piece adds its Protection and Load to the others worn "
            "(Lords of Men p. 140).",
        )
    ]


def _quantity_possession_fields(
    kind: str,
    entry: pos.PossessionEntry | None,
    *,
    natural: bool = False,
    books: Collection[str] | None = None,
) -> list[DialogField]:
    """The book entry, Type and Quality (gear kinds), Quantity, and a
    weapon's or armor's combat figures."""
    fields: list[DialogField] = []
    if kind in GEAR_TYPES_BY_KIND:
        types = GEAR_TYPES_BY_KIND[kind]
        book = _gear_book_field(kind, entry, natural, books)
        fields += [
            book,
            DialogField(
                "gear_type",
                "Type",
                "select",
                attr(entry, "gear_type", types[0]) or types[0],
                options=pairs(types),
                # Partial or full armor changes the book's figures.
                fills=book.fills if kind == "armor" else None,
            ),
            DialogField(
                "gear_quality",
                "Quality",
                "select",
                attr(entry, "gear_quality", GEAR_QUALITY_DEFAULT),
                options=pairs(GEAR_QUALITIES),
            ),
        ]
    fields.append(
        DialogField("quantity", "Quantity", "int", attr(entry, "quantity", 1))
    )
    if kind == "weapon":
        fields += [
            DialogField("weapon_init", "Init", "int", attr(entry, "weapon_init", 0)),
            DialogField(
                "weapon_attack",
                "Attack (blank = n/a)",
                "optint",
                attr(entry, "weapon_attack", 0),
            ),
            DialogField(
                "weapon_defense", "Defense", "int", attr(entry, "weapon_defense", 0)
            ),
            DialogField(
                "weapon_damage",
                "Damage (blank = n/a)",
                "optint",
                attr(entry, "weapon_damage", 0),
            ),
        ]
    elif kind == "armor":
        fields.append(
            DialogField(
                "armor_protection",
                "Protection",
                "int",
                attr(entry, "armor_protection", 0),
            )
        )
        if not natural:
            fields += _armor_slot_field(entry, books)
    if kind in GEAR_TYPES_BY_KIND and not natural:
        fields.append(DialogField("load", "Load", "int", attr(entry, "load", 0)))
        fields += [
            DialogField(
                "make",
                "Made",
                "select",
                attr(entry, "make", ""),
                options=[("Standard", "")] + [(m, m) for m in equipment.MAKES if m],
                hint="Superior +1, Excellent +2 or more; Shoddy breaks easily.",
            ),
            DialogField(
                "make_bonus",
                "Excellent bonus",
                "int",
                attr(entry, "make_bonus", 0) or equipment.EXCELLENT_LEAST,
                show_if=lambda v: v.get("make") == equipment.EXCELLENT,
            ),
        ]
    if kind == "weapon" and not natural:
        fields.append(
            DialogField(
                "carried",
                "Carried",
                "check",
                attr(entry, "carried", True),
            )
        )
    if kind == "item":
        fields += [
            DialogField(
                "assists",
                "Helps (Ability, specialty)",
                "text",
                attr(entry, "assists", ""),
                placeholder="e.g. Athletics (climbing)",
            ),
            DialogField(
                "assistance",
                "How much",
                "select",
                attr(entry, "assistance", ""),
                options=[
                    ("(none)", ""),
                    ("Minor: -1 Ease Factor", "Minor"),
                    ("Major: -3 Ease Factor", "Major"),
                ],
                hint="Equipment that isn't essential to the task (Grogs p. 47).",
            ),
        ]
    return fields


def _vis_possession_fields(
    kind: str,
    entry: pos.PossessionEntry | None,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
) -> list[DialogField]:
    """Art, Season harvested (a source), Pawns, Kept at (a store, one of
    `places`), Location and Physical Form."""
    fields = [
        DialogField(
            "art",
            "Art",
            "select",
            attr(entry, "art", ""),
            options=pairs(ARTS),
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
        )
    ]
    if kind == "vis_source":
        fields.append(
            DialogField(
                "season",
                "Season harvested",
                "select",
                attr(entry, "season", ""),
                options=pairs(SEASONS),
                required=True,
                allow_blank=True,
                placeholder="(choose a Season)",
            )
        )
        # The Hooks are on the record: a PossessionEntry has no such fields.
        fields += contested_fields(entry.record if entry is not None else None)
    fields.append(
        DialogField(
            "pawns",
            "Pawns",
            "int",
            attr(entry, "pawns", 1) or 1,
            hint=VIS_YIELD_HINT if kind == "vis_source" else "",
        )
    )
    if kind == "vis_store" and places:
        fields.append(
            DialogField(
                "place",
                "Kept at",
                "select",
                place,
                options=list(places),
                required=True,
                hint="The covenant, one of its laboratories, or one of its "
                "characters. Location says where exactly.",
            )
        )
    fields += [
        DialogField("location", "Location", "text", attr(entry, "location", "")),
        DialogField(
            "physical_form",
            "Physical Form",
            "text",
            attr(entry, "physical_form", ""),
        ),
    ]
    if kind == "vis_store":
        fields.append(
            DialogField(
                "infernal",
                "Infernal vis",
                "check",
                bool(attr(entry, "infernal", False)),
                hint="Tainted by Hell: from a demon or an Infernal aura (RoP: "
                "The Infernal p. 18). Its casting lines count the extra botch "
                "dice.",
            )
        )
    return fields


def _kind_is(*kinds: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: (values.get("vis_kind") or "") in kinds


def vis_kind_fields(
    record: Any, options: Sequence[tuple[str, str]] | None = None
) -> list[DialogField]:
    """A vis source's or store's kind of vis (blank: ordinary) and what
    goes with it: a dedicated pawn's other Art, a Thing of Virtue, an
    extraordinary power's level (rules.vis_kinds)."""
    kind = attr(record, "vis_kind", "") or ""
    offered = (
        list(options) if options is not None else vis_kinds.kind_options(None, kind)
    )
    if not offered:
        return []
    things = [
        *vis_kinds.thing_options(vis_kinds.HERB_OF_VIRTUE),
        *vis_kinds.thing_options(vis_kinds.OBJECT_OF_VIRTUE),
    ]
    return [
        DialogField(
            "vis_kind",
            "Kind of vis",
            "select",
            kind,
            options=offered,
            allow_blank=True,
            placeholder="Ordinary vis",
            hint="Extraordinary, dedicated and Things of Virtue: Realms of "
            "Power: Magic pp. 119-128; faerie vis: Realms of Power: Faerie pp. "
            "18-19.",
        ),
        DialogField(
            "paired_art",
            "Dedicated with",
            "select",
            attr(record, "paired_art", "") or "",
            options=pairs(ARTS),
            allow_blank=True,
            placeholder="(its other Art)",
            show_if=_kind_is(vis_kinds.DEDICATED),
            hint="A dedicated pawn is one Technique and one Form together.",
        ),
        DialogField(
            "virtue_thing",
            "Thing of Virtue",
            "select",
            attr(record, "virtue_thing", "") or "",
            options=things,
            allow_blank=True,
            placeholder="(another, not in the book)",
            show_if=_kind_is(*vis_kinds.THINGS),
        ),
        DialogField(
            "effect_level",
            "Level of its power",
            "optint",
            attr(record, "effect_level", None),
            show_if=_kind_is(*vis_kinds.EXTRAORDINARY),
            hint="Usually a pawn for every 10 levels (RoP: Magic p. 120).",
        ),
    ]


def contested_fields(entry: Any) -> list[DialogField]:
    """A vis or income source's Contested / Dwindling Resource Hooks."""
    return [
        DialogField(
            "contested",
            "Contested Resource",
            "check",
            bool(attr(entry, "contested", False)),
            hint="Covered by a Contested or Indiscreet Resource Hook: advancing "
            "asks whether it was secured once its security lapses.",
        ),
        DialogField(
            "secured_until",
            "Secured through (year)",
            "optint",
            attr(entry, "secured_until", None),
            show_if=lambda values: bool(values.get("contested")),
            hint="A story secures it for five years.",
        ),
        DialogField(
            "dwindling",
            "Dwindling Resource (gone in 10 years)",
            "check",
            bool(attr(entry, "dwindling", False)),
        ),
    ]


# A covenant's Possessions


def entries(saga: Saga, covenant: Covenant, kind: str) -> list[pos.PossessionEntry]:
    """The covenant's possessions of `kind`, as its section lists them."""
    return pos.entries_for_kind(
        saga, covenant, kind, catalog.load_lab_virtue_flaw_catalog_by_id()
    )


def form_title(kind: str, entry: pos.PossessionEntry | None) -> str:
    """ "Add a Weapon", or "Edit <its name>"."""
    singular = pos.KIND_SINGULAR[kind]
    if entry is None:
        return f"Add a {singular}"
    return f"Edit {escape(entry.name or 'this ' + singular.lower())}"


def covenant_possession_form(
    saga: Saga, covenant: Covenant, kind: str, entry: pos.PossessionEntry | None
) -> Form:
    """Add (`entry` None) or edit one of the covenant's possessions."""
    places: list[tuple[str, str]] = []
    place = ""
    if kind == "vis_store":
        places = vis.location_options(saga, covenant)
        place = vis.location_value(covenant, entry.record if entry else None)
        if place not in [value for _, value in places]:
            place = places[0][1]  # whoever kept it has left the covenant

    def apply(values: dict[str, Any]) -> None:
        pos.save_entry(covenant, kind, entry, values)

    keep = entry.record.vis_kind if entry is not None and entry.record else ""
    return possession_form(
        form_title(kind, entry),
        kind,
        entry,
        apply,
        places=places,
        place=place,
        vis_kind_options=vis_kinds.kind_options(saga, keep),
        books=sourcebooks.saga_books(saga),
    )


def remove_possession(
    covenant: Covenant, kind: str, entry: pos.PossessionEntry
) -> Confirm | Refuse:
    """Delete one of the covenant's possessions, after confirming; one
    listed from a laboratory can't be deleted here."""
    if entry.auto:
        return Refuse(
            f"Delete {escape(entry.name)}",
            f"{escape(entry.name)} is a laboratory of this covenant, so it "
            "can't be deleted here. Move it to another covenant from the "
            "laboratory's Identity instead.",
        )

    def apply() -> None:
        if entry.record in covenant.possessions:
            covenant.possessions.remove(entry.record)

    return Confirm(f"Delete {escape(entry.name or 'this entry')}?", apply)


def possession_ops(saga: Saga, covenant: Covenant, kind: str) -> SectionOps:
    """A covenant's Possessions section of `kind`: Add, Edit and Delete,
    by the row's index in the section's list."""
    return SectionOps(
        add=lambda: covenant_possession_form(saga, covenant, kind, None),
        edit=lambda index: covenant_possession_form(
            saga, covenant, kind, entries(saga, covenant, kind)[index]
        ),
        remove=lambda index: remove_possession(
            covenant, kind, entries(saga, covenant, kind)[index]
        ),
        rows=lambda: [e.name or "(unnamed)" for e in entries(saga, covenant, kind)],
    )
