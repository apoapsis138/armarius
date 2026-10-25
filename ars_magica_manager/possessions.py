"""Logic behind a covenant's Possessions tab -- no UI in here.

Works out what each list shows (laboratories listed automatically as sanctums,
plus stored entries) and the text for list rows and the details panel.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from . import catalog, storage, vis
from .markup import escape, fit, markdown_text
from .models import (
    GEAR_POINTS,
    GEAR_QUALITY_DEFAULT,
    GEAR_TYPES_BY_KIND,
    SANCTUM_USAGE_DEFAULT,
    ArmorDef,
    Covenant,
    Laboratory,
    LabVirtueFlawDef,
    Possession,
    Saga,
    WeaponDef,
)
from .rules.lab_stats import lab_build_points, lab_characteristic_total
from .tables import Table

#: Section titles on the tab.
KIND_TITLES: dict[str, str] = {
    "property": "Properties and Land",
    "sanctum": "Sanctums",
    "weapon": "Weapons",
    "armor": "Armor",
    "vis_source": "Vis Sources",
    "vis_store": "Raw Vis Stores",
    "item": "Items",
}

#: How a single entry is named in dialogs ("Add a Sanctum").
KIND_SINGULAR: dict[str, str] = {
    "property": "Property",
    "sanctum": "Sanctum",
    "weapon": "Weapon",
    "armor": "Armor",
    "vis_source": "Vis Source",
    "vis_store": "Raw Vis Store",
    "item": "Item",
}

#: Kinds whose entries carry a Quantity.
QUANTITY_KINDS: tuple[str, ...] = ("weapon", "armor", "item")

#: The book's weapon tables a weapon form offers: a familiar's Natural
#: Weapons its own table; characters' and covenants' weapons the rest
#: (melee, with the shields, and missile).
GEAR_WEAPON_TABLES: tuple[str, ...] = ("melee", "missile")
NATURAL_WEAPON_TABLES: tuple[str, ...] = ("natural",)

#: The armor Type that means a full suit (the other is partial).
FULL_ARMOR = GEAR_TYPES_BY_KIND["armor"][1]


#: What a Raw Vis Store marked Infernal does in casting (rules.casting).
INFERNAL_VIS_NOTE = (
    "twice the botch dice in casting; with the Harsher Infernal vis option "
    "+5 a pawn and 3 more botch dice a pawn, never fewer than its pawns "
    "(DE p. 422; RoP: The Infernal p. 19)"
)


@dataclass
class PossessionEntry:
    """One row of a list, whatever it was built from.

    `lab` entries are laboratories of the covenant listed automatically as
    sanctums: name, owner, location and build points are read live from the
    laboratory, and `record` -- once the user has edited it -- only holds the
    covenant-side extras. Every other entry is its own `record`.
    """

    kind: str
    record: Possession | None
    lab: Laboratory | None = None
    lab_owner: str = ""
    lab_catalog: Mapping[str, LabVirtueFlawDef] | None = None
    #: The saga a `lab` entry's laboratory is in (for its magic items).
    lab_saga: Saga | None = None
    #: A Raw Vis Store: where it is kept, by name (vis.location_label).
    place: str = ""

    def _own(self, attribute: str, default: Any):
        return getattr(self.record, attribute) if self.record is not None else default

    @property
    def auto(self) -> bool:
        return self.lab is not None

    @property
    def name(self) -> str:
        return self.lab.name if self.lab is not None else self._own("name", "")

    @property
    def owner(self) -> str:
        return self.lab_owner if self.lab is not None else self._own("owner", "")

    @property
    def location(self) -> str:
        return self.lab.location if self.lab is not None else self._own("location", "")

    @property
    def build_points(self) -> int | None:
        if self.lab is not None:
            return lab_build_points(self.lab)
        return self._own("build_points", None)

    @property
    def quality(self) -> int | None:
        if self.lab is not None:
            _, _, _, total = lab_characteristic_total(
                self.lab, self.lab_catalog or {}, "general_quality", self.lab_saga
            )
            return total
        return self._own("quality", None)

    @property
    def upkeep(self) -> int | None:
        if self.lab is not None:
            _, _, _, total = lab_characteristic_total(
                self.lab, self.lab_catalog or {}, "upkeep", self.lab_saga
            )
            return total
        return self._own("upkeep", None)

    @property
    def usage(self) -> str:
        return self._own("usage", SANCTUM_USAGE_DEFAULT)

    @property
    def quantity(self) -> int:
        return self._own("quantity", 1)

    @property
    def dimensions(self) -> str:
        return self._own("dimensions", "")

    @property
    def inhabitants(self) -> str:
        return self._own("inhabitants", "")

    @property
    def art(self) -> str:
        return self._own("art", "")

    @property
    def pawns(self) -> int:
        return self._own("pawns", 0)

    @property
    def season(self) -> str:
        return self._own("season", "")

    @property
    def physical_form(self) -> str:
        return self._own("physical_form", "")

    @property
    def infernal(self) -> bool:
        return bool(self._own("infernal", False))

    @property
    def description(self) -> str:
        return self._own("description", "")

    @property
    def gear_type(self) -> str:
        return self._own("gear_type", "")

    @property
    def gear_quality(self) -> str:
        return self._own("gear_quality", GEAR_QUALITY_DEFAULT)

    @property
    def points_each(self) -> int:
        """Points of one weapon/armor of this type and quality (0 if the type
        isn't set, or the quality doesn't exist for it)."""
        return GEAR_POINTS.get(self.gear_type, {}).get(self.gear_quality, 0)

    @property
    def points(self) -> int:
        """Points of the whole entry: points each times the Quantity."""
        return self.points_each * self.quantity

    @property
    def weapon_init(self) -> int:
        return self._own("weapon_init", 0)

    @property
    def weapon_attack(self) -> int | None:
        return self._own("weapon_attack", 0)

    @property
    def weapon_defense(self) -> int:
        return self._own("weapon_defense", 0)

    @property
    def weapon_damage(self) -> int | None:
        return self._own("weapon_damage", 0)

    @property
    def armor_protection(self) -> int:
        return self._own("armor_protection", 0)

    @property
    def load(self) -> int:
        return self._own("load", 0)

    @property
    def gear_id(self) -> str | None:
        return self._own("gear_id", None)

    @property
    def make(self) -> str:
        return self._own("make", "")

    @property
    def make_bonus(self) -> int:
        return self._own("make_bonus", 0)

    @property
    def carried(self) -> bool:
        return self._own("carried", True)

    @property
    def assists(self) -> str:
        return self._own("assists", "")

    @property
    def assistance(self) -> str:
        return self._own("assistance", "")


def entries_for_kind(
    saga: Saga,
    covenant: Covenant,
    kind: str,
    lab_catalog: Mapping[str, LabVirtueFlawDef] | None = None,
) -> list[PossessionEntry]:
    """The rows of `kind`'s list, in display order: for Sanctums the covenant's
    laboratories first, then stored entries in the order added."""
    entries: list[PossessionEntry] = []
    if kind == "sanctum":
        for lab in saga.laboratories:
            if lab.covenant_id != covenant.id:
                continue
            record = next(
                (
                    r
                    for r in covenant.possessions
                    if r.kind == "sanctum" and r.lab_id == lab.id
                ),
                None,
            )
            owner = next((c.name for c in saga.characters if c.id == lab.owner_id), "")
            entries.append(
                PossessionEntry(
                    kind,
                    record,
                    lab,
                    lab_owner=owner,
                    lab_catalog=lab_catalog,
                    lab_saga=saga,
                )
            )
    for record in covenant.possessions:
        if record.kind != kind:
            continue
        if kind == "sanctum" and record.lab_id is not None:
            continue  # extras of a listed laboratory; shown above
        place = (
            vis.location_label(saga, covenant, record) if kind == "vis_store" else ""
        )
        entries.append(PossessionEntry(kind, record, place=place))
    return entries


# ------------------------------------------------------------------- text


_NAME_WIDTH = 20
_LOCATION_WIDTH = 18
_DIMENSIONS_WIDTH = 14
_OWNER_WIDTH = 16
_QUALITY_WIDTH = 7
_UPKEEP_WIDTH = 8
_TYPE_WIDTH = 20
_GEAR_QUALITY_WIDTH = 12
_QTY_WIDTH = 5
_ART_WIDTH = 10
_PAWNS_WIDTH = 6
_SEASON_WIDTH = 8
_COMBAT_STAT_WIDTH = 5


def table_header(kind: str) -> str:
    """The column titles above one kind's Possessions list; the two-character
    indent is the list's selector marker."""
    name = f"{'Name':<{_NAME_WIDTH}}"
    if kind == "property":
        return (
            f"  {name}{'Location':<{_LOCATION_WIDTH}}"
            f"{'Dimensions':<{_DIMENSIONS_WIDTH}}Inhabitants"
        )
    if kind == "sanctum":
        return (
            f"  {name}{'Owner':<{_OWNER_WIDTH}}"
            f"{'Quality':>{_QUALITY_WIDTH}}{'Upkeep':>{_UPKEEP_WIDTH}}"
        )
    if kind == "weapon":
        return (
            f"  {name}{'Type':<{_TYPE_WIDTH}}"
            f"{'Quality':<{_GEAR_QUALITY_WIDTH}}{'Qty':>{_QTY_WIDTH}}"
            f"{'Init':>{_COMBAT_STAT_WIDTH}}{'Atk':>{_COMBAT_STAT_WIDTH}}"
            f"{'Def':>{_COMBAT_STAT_WIDTH}}{'Dmg':>{_COMBAT_STAT_WIDTH}}"
            f"{'Load':>{_COMBAT_STAT_WIDTH}}"
        )
    if kind == "armor":
        return (
            f"  {name}{'Type':<{_TYPE_WIDTH}}"
            f"{'Quality':<{_GEAR_QUALITY_WIDTH}}{'Qty':>{_QTY_WIDTH}}"
            f"{'Prot':>{_COMBAT_STAT_WIDTH}}{'Load':>{_COMBAT_STAT_WIDTH}}"
        )
    if kind == "item":
        return f"  {name}{'Qty':>{_QTY_WIDTH}}"
    if kind == "vis_source":
        return (
            f"  {name}{'Art':<{_ART_WIDTH}}"
            f"{'Pawns':>{_PAWNS_WIDTH}}  {'Season':<{_SEASON_WIDTH}}"
        )
    return f"  {name}{'Art':<{_ART_WIDTH}}{'Pawns':>{_PAWNS_WIDTH}}"  # vis_store


def group_header(kind: str, title: str) -> str:
    """A header row naming one kind within a mixed list (a character's
    Personal Gear), with that kind's column titles: `title` stands in the
    selector marker and Name columns, the rest line up with `row_label`."""
    name_columns = 2 + _NAME_WIDTH
    return f"{title:<{name_columns}}{table_header(kind)[name_columns:]}"


def row_label(entry: PossessionEntry) -> str:
    """One list row (markup), columns lined up with `table_header`. Trailing
    whitespace from an unset last column is stripped."""
    kind = entry.kind
    name = escape(fit(entry.name or "(unnamed)", _NAME_WIDTH))
    if kind == "property":
        location = escape(fit(entry.location, _LOCATION_WIDTH))
        dimensions = escape(fit(entry.dimensions, _DIMENSIONS_WIDTH))
        row = f"{name}{location}{dimensions}{escape(entry.inhabitants)}"
    elif kind == "sanctum":
        owner = escape(fit(entry.owner, _OWNER_WIDTH))
        quality = "" if entry.quality is None else entry.quality
        upkeep = "" if entry.upkeep is None else entry.upkeep
        row = f"{name}{owner}{quality:>{_QUALITY_WIDTH}}{upkeep:>{_UPKEEP_WIDTH}}"
    elif kind in ("weapon", "armor"):
        gear_type = escape(fit(entry.gear_type, _TYPE_WIDTH))
        gear_quality = escape(fit(entry.gear_quality, _GEAR_QUALITY_WIDTH))
        row = f"{name}{gear_type}{gear_quality}{entry.quantity:>{_QTY_WIDTH}}"
        if kind == "weapon":
            row += (
                f"{signed(entry.weapon_init):>{_COMBAT_STAT_WIDTH}}"
                f"{signed(entry.weapon_attack):>{_COMBAT_STAT_WIDTH}}"
                f"{signed(entry.weapon_defense):>{_COMBAT_STAT_WIDTH}}"
                f"{signed(entry.weapon_damage):>{_COMBAT_STAT_WIDTH}}"
                f"{entry.load:>{_COMBAT_STAT_WIDTH}}"
            )
        else:
            row += (
                f"{signed(entry.armor_protection):>{_COMBAT_STAT_WIDTH}}"
                f"{entry.load:>{_COMBAT_STAT_WIDTH}}"
            )
    elif kind == "item":
        row = f"{name}{entry.quantity:>{_QTY_WIDTH}}"
    elif kind == "vis_source":
        art = escape(fit(entry.art, _ART_WIDTH))
        season = escape(fit(entry.season, _SEASON_WIDTH))
        row = f"{name}{art}{entry.pawns:>{_PAWNS_WIDTH}}  {season}"
    else:  # vis_store
        art = escape(fit(entry.art, _ART_WIDTH))
        row = f"{name}{art}{entry.pawns:>{_PAWNS_WIDTH}}"
    return row.rstrip()


def _line(label: str, value: object) -> str:
    return f"[b]{label}:[/] {escape(str(value))}"


def signed(value: int | None) -> str:
    """A combat figure as the book prints it: +2, +0, -1, or n/a."""
    return "n/a" if value is None else f"{value:+d}"


def weapon_summary(weapon: WeaponDef) -> str:
    """What the book says of a weapon beyond the figures an entry holds:
    its Ability, minimum Strength and range ("Bows, Min Str -1, range 15
    paces")."""
    parts = [weapon.ability]
    if weapon.strength is not None:
        parts.append(f"Min Str {weapon.strength:+d}")
    if weapon.range is not None:
        parts.append(f"range {weapon.range} paces")
    return ", ".join(parts)


def armor_summary(armor: ArmorDef) -> str:
    """The book's figures for an armor Material, partial and full
    ("partial +6 Load 4, full +9 Load 6")."""
    partial = f"partial +{armor.partial_protection} Load {armor.partial_load}"
    full = armor.figures(full=True)
    if full is None:
        return f"{partial}, partial only"
    return f"{partial}, full +{full[0]} Load {full[1]}"


def _book_line(entry: PossessionEntry) -> str | None:
    """The details panel's line naming the book entry a weapon or armor was
    filled from, or None for one typed in."""
    gear_id = entry.gear_id
    if not gear_id:
        return None
    if entry.kind == "weapon":
        weapon = catalog.load_weapon_catalog_by_id().get(gear_id)
        if weapon is None:
            return _line("Weapon", f"{gear_id} (not in the catalog)")
        return _line("Weapon", f"{weapon.name} ({weapon_summary(weapon)})")
    armor = catalog.load_armor_catalog_by_id().get(gear_id)
    if armor is None:
        return _line("Material", f"{gear_id} (not in the catalog)")
    return _line("Material", armor.name)


def detail_text(entry: PossessionEntry | None) -> str:
    """The details panel (markup) for a chosen entry: the row's fields plus
    the rest, with the description rendered with inline emphasis."""
    if entry is None:
        return "[dim]Select a possession to see its details.[/]"
    kind = entry.kind
    lines = [_line("Name", entry.name or "(unnamed)")]

    def optional(label: str, value: object) -> None:
        if value not in ("", None):
            lines.append(_line(label, value))

    if kind == "property":
        optional("Location", entry.location)
        optional("Dimensions", entry.dimensions)
        optional("Inhabitants", entry.inhabitants)
    elif kind == "sanctum":
        optional("Owner", entry.owner)
        optional("Location", entry.location)
        optional("Quality", entry.quality)
        if entry.upkeep is not None:
            lines.append(_line("Upkeep", f"{entry.upkeep} Points"))
        optional("Build Points", entry.build_points)
        lines.append(_line("Usage", entry.usage))
    elif kind in QUANTITY_KINDS:
        book = _book_line(entry) if kind != "item" else None
        if book is not None:
            lines.append(book)
        if kind != "item":
            lines.append(_line("Type", entry.gear_type or "(not set)"))
            lines.append(_line("Quality", entry.gear_quality))
        lines.append(_line("Quantity", entry.quantity))
        if kind != "item" and entry.gear_type:
            lines.append(
                _line(
                    "Points",
                    f"{entry.points} ({entry.points_each} each, for the "
                    "covenant's finances)",
                )
            )
        if kind == "weapon":
            # One line, so the fixed-height panel shows them all.
            lines.append(
                "   ".join(
                    (
                        _line("Init", signed(entry.weapon_init)),
                        _line("Attack", signed(entry.weapon_attack)),
                        _line("Defense", signed(entry.weapon_defense)),
                        _line("Damage", signed(entry.weapon_damage)),
                        _line("Load", entry.load),
                    )
                )
            )
        elif kind == "armor":
            lines.append(_line("Protection", signed(entry.armor_protection)))
            lines.append(_line("Load", entry.load))
    elif kind == "vis_source":
        lines.append(_line("Art", entry.art))
        lines.append(_line("Pawns", entry.pawns))
        lines.append(_line("Season", entry.season))
        optional("Location", entry.location)
        optional("Physical Form", entry.physical_form)
    else:  # vis_store
        lines += [_line("Art", entry.art), _line("Pawns", entry.pawns)]
        optional("Infernal vis", INFERNAL_VIS_NOTE if entry.infernal else "")
        optional("Kept at", entry.place)
        optional("Location", entry.location)
        optional("Physical Form", entry.physical_form)

    if entry.lab is not None:
        lines.append(
            f"[dim]A laboratory of this covenant: {escape(entry.lab.name)}.[/]"
        )
    if entry.description.strip():
        lines += ["", "[b]Description:[/]", markdown_text(entry.description.strip())]
    return "\n".join(lines)


def gear_points(saga: Saga, covenant: Covenant) -> int:
    """Points of Weapons and Armor: every weapon and armor entry's points."""
    return sum(
        entry.points
        for kind in ("weapon", "armor")
        for entry in entries_for_kind(saga, covenant, kind)
    )


# ------------------------------------------------------------------ changes


def save_entry(
    covenant: Covenant, kind: str, entry: PossessionEntry | None, values: dict[str, Any]
) -> None:
    """Apply an add/edit form's `values`: an update to the entry's record,
    or a new record -- for a new entry, or for a laboratory's sanctum edited
    for the first time (linked to that lab). A Raw Vis Store's "place"
    (vis.location_options' "kind:id") becomes its location link."""
    values = dict(values)
    place = values.pop("place", None)
    if place:
        values["location_kind"], _, values["location_id"] = place.partition(":")
    if entry is not None and entry.record is not None:
        for key, value in values.items():
            setattr(entry.record, key, value)
        return
    lab_id = entry.lab.id if entry is not None and entry.lab else None
    covenant.possessions.append(
        Possession(
            id=storage.generate_unique_id(
                values.get("name") or f"{kind}-{lab_id or 'new'}",
                [r.id for r in covenant.possessions],
            ),
            kind=kind,
            lab_id=lab_id,
            **values,
        )
    )


def form_problem(values: dict[str, Any]) -> str | None:
    """What's wrong with a possession form's values, if anything."""
    if values.get("quantity", 1) < 1:
        return "Quantity must be at least 1."
    if values.get("pawns", 1) < 1:
        return "Pawns must be at least 1."
    if values.get("load", 0) < 0:
        return "Load can't be negative."
    gear_type = values.get("gear_type")
    if gear_type and values.get("gear_quality") not in GEAR_POINTS[gear_type]:
        return f"{gear_type} only comes {' or '.join(GEAR_POINTS[gear_type]).lower()}."
    armor = catalog.load_armor_catalog_by_id().get(values.get("gear_id") or "")
    if armor is not None and gear_type == FULL_ARMOR and armor.figures(True) is None:
        return f"{armor.name} only comes as partial armor."
    return None


def _follows_the_book(name: str, book_names: set[str]) -> bool:
    """Whether a form's Name may be replaced by the chosen entry's: it's
    blank, or still the name of a catalog entry (so it was filled in, not
    typed)."""
    return not name or name in book_names


def weapon_fills(
    values: dict[str, Any], weapons: Mapping[str, WeaponDef]
) -> dict[str, Any]:
    """What choosing the book weapon `values["gear_id"]` (one of `weapons`)
    suggests for the rest of a weapon form: its Init/Attack/Defense/Damage;
    for a carried weapon (not a natural one) its Load, the Type that prices
    it and, when the book gives one, its cost as the Quality; and its name,
    unless the user has typed their own."""
    weapon = weapons.get(values.get("gear_id") or "")
    if weapon is None:
        return {}
    filled: dict[str, Any] = {
        "weapon_init": weapon.init,
        "weapon_attack": weapon.attack,
        "weapon_defense": weapon.defense,
        "weapon_damage": weapon.damage,
    }
    if weapon.table != "natural":
        filled["load"] = weapon.load or 0
        filled["gear_type"] = GEAR_TYPES_BY_KIND["weapon"][0]
        if weapon.cost is not None:
            filled["gear_quality"] = weapon.cost
    names = {w.name for w in weapons.values()}
    if _follows_the_book(values.get("name") or "", names):
        filled["name"] = weapon.name
    return filled


def armor_fills(
    values: dict[str, Any], armors: Mapping[str, ArmorDef]
) -> dict[str, Any]:
    """What choosing the book armor Material `values["gear_id"]` (one of
    `armors`), as partial or full armor (`values["gear_type"]`), suggests
    for the rest of an armor form: its Protection and Load (unless it
    doesn't come that way), its cost as the Quality, and its name unless
    the user has typed their own."""
    armor = armors.get(values.get("gear_id") or "")
    if armor is None:
        return {}
    filled: dict[str, Any] = {"gear_quality": armor.cost}
    figures = armor.figures(values.get("gear_type") == FULL_ARMOR)
    if figures is not None:
        filled["armor_protection"], filled["load"] = figures
    names = {a.name for a in armors.values()}
    if _follows_the_book(values.get("name") or "", names):
        filled["name"] = armor.name
    return filled


def book_text(kind: str, gear_id: str | None) -> str:
    """A weapon or armor form's live line (markup): the chosen book entry's
    summary and description, or a hint to choose one."""
    if kind == "weapon":
        weapon = catalog.load_weapon_catalog_by_id().get(gear_id or "")
        if weapon is None:
            return "[dim]Choose a Weapon to fill in the book's figures.[/]"
        summary, description = weapon_summary(weapon), weapon.description
        name = weapon.name
    else:
        armor = catalog.load_armor_catalog_by_id().get(gear_id or "")
        if armor is None:
            return "[dim]Choose a Material to fill in the book's figures.[/]"
        summary, description = armor_summary(armor), armor.description
        name = armor.name
    text = f"[b]{escape(name)}[/] ({escape(summary)})"
    return f"{text}: {escape(description)}" if description else text


# As a table (tables.py)

#: Each kind's columns after its name: a title, and how to read the cell
#: from a PossessionEntry.
_TABLE_COLUMNS: dict[str, tuple[tuple[str, Callable[[Any], str]], ...]] = {
    "property": (
        ("Location", lambda e: e.location),
        ("Dimensions", lambda e: e.dimensions),
        ("Inhabitants", lambda e: e.inhabitants),
    ),
    "sanctum": (
        ("Owner", lambda e: e.owner),
        ("Quality", lambda e: "" if e.quality is None else str(e.quality)),
        ("Upkeep", lambda e: "" if e.upkeep is None else str(e.upkeep)),
    ),
    "weapon": (
        ("Type", lambda e: e.gear_type),
        ("Quality", lambda e: e.gear_quality),
        ("Qty", lambda e: str(e.quantity)),
        ("Init", lambda e: signed(e.weapon_init)),
        ("Atk", lambda e: signed(e.weapon_attack)),
        ("Def", lambda e: signed(e.weapon_defense)),
        ("Dmg", lambda e: signed(e.weapon_damage)),
        ("Load", lambda e: str(e.load)),
    ),
    "armor": (
        ("Type", lambda e: e.gear_type),
        ("Quality", lambda e: e.gear_quality),
        ("Qty", lambda e: str(e.quantity)),
        ("Prot", lambda e: signed(e.armor_protection)),
        ("Load", lambda e: str(e.load)),
    ),
    "item": (("Qty", lambda e: str(e.quantity)),),
    "vis_source": (
        ("Art", lambda e: e.art),
        ("Pawns", lambda e: str(e.pawns)),
        ("Season", lambda e: e.season),
    ),
    "vis_store": (("Art", lambda e: e.art), ("Pawns", lambda e: str(e.pawns))),
}


def table(
    kind: str, entries: Sequence[PossessionEntry], keys: list[int | None] | None = None
) -> Table:
    """`entries` of one kind as a table (plain cells): the Name column,
    then the kind's own columns."""
    columns = _TABLE_COLUMNS[kind]
    return Table(
        ["Name", *(title for title, _ in columns)],
        [
            [entry.name or "(unnamed)", *(cell(entry) for _, cell in columns)]
            for entry in entries
        ],
        keys,
    )
