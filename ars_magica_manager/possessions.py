"""Logic behind a covenant's Possessions tab -- no UI in here.

Works out what each list shows (laboratories listed automatically as sanctums,
plus stored entries) and the text for list rows and the details panel.
"""

from __future__ import annotations

from dataclasses import dataclass

from .markup import escape, markdown_inline
from .models import (
    GEAR_POINTS,
    GEAR_QUALITY_DEFAULT,
    Covenant,
    Laboratory,
    LabVirtueFlawDef,
    Possession,
    Saga,
    lab_characteristic_total,
)

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
    lab_catalog: dict[str, LabVirtueFlawDef] | None = None

    def _own(self, attribute: str, default):
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
            return self.lab.build_points
        return self._own("build_points", None)

    @property
    def quality(self) -> int | None:
        if self.lab is not None:
            _, _, _, total = lab_characteristic_total(
                self.lab, self.lab_catalog or {}, "general_quality"
            )
            return total
        return self._own("quality", None)

    @property
    def upkeep(self) -> int | None:
        if self.lab is not None:
            _, _, _, total = lab_characteristic_total(
                self.lab, self.lab_catalog or {}, "upkeep"
            )
            return total
        return self._own("upkeep", None)

    @property
    def usage(self) -> str:
        return self._own("usage", "Standard (2 Seasons)")

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


def entries_for_kind(
    saga: Saga,
    covenant: Covenant,
    kind: str,
    lab_catalog: dict[str, LabVirtueFlawDef] | None = None,
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
                    kind, record, lab, lab_owner=owner, lab_catalog=lab_catalog
                )
            )
    for record in covenant.possessions:
        if record.kind != kind:
            continue
        if kind == "sanctum" and record.lab_id is not None:
            continue  # extras of a listed laboratory; shown above
        entries.append(PossessionEntry(kind, record))
    return entries


# ------------------------------------------------------------------- text


def _fit(text: str, width: int) -> str:
    text = text.replace("\n", " ")
    if len(text) > width:
        text = text[: width - 1] + "…"
    return text.ljust(width)


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
    if kind in ("weapon", "armor"):
        return (
            f"  {name}{'Type':<{_TYPE_WIDTH}}"
            f"{'Quality':<{_GEAR_QUALITY_WIDTH}}{'Qty':>{_QTY_WIDTH}}"
        )
    if kind == "item":
        return f"  {name}{'Qty':>{_QTY_WIDTH}}"
    if kind == "vis_source":
        return (
            f"  {name}{'Art':<{_ART_WIDTH}}"
            f"{'Pawns':>{_PAWNS_WIDTH}}  {'Season':<{_SEASON_WIDTH}}"
        )
    return f"  {name}{'Art':<{_ART_WIDTH}}{'Pawns':>{_PAWNS_WIDTH}}"  # vis_store


def row_label(entry: PossessionEntry) -> str:
    """One list row (markup), columns lined up with `table_header`. Trailing
    whitespace from an unset last column is stripped."""
    kind = entry.kind
    name = escape(_fit(entry.name or "(unnamed)", _NAME_WIDTH))
    if kind == "property":
        location = escape(_fit(entry.location, _LOCATION_WIDTH))
        dimensions = escape(_fit(entry.dimensions, _DIMENSIONS_WIDTH))
        row = f"{name}{location}{dimensions}{escape(entry.inhabitants)}"
    elif kind == "sanctum":
        owner = escape(_fit(entry.owner, _OWNER_WIDTH))
        quality = "" if entry.quality is None else entry.quality
        upkeep = "" if entry.upkeep is None else entry.upkeep
        row = f"{name}{owner}{quality:>{_QUALITY_WIDTH}}{upkeep:>{_UPKEEP_WIDTH}}"
    elif kind in ("weapon", "armor"):
        gear_type = escape(_fit(entry.gear_type, _TYPE_WIDTH))
        gear_quality = escape(_fit(entry.gear_quality, _GEAR_QUALITY_WIDTH))
        row = f"{name}{gear_type}{gear_quality}{entry.quantity:>{_QTY_WIDTH}}"
    elif kind == "item":
        row = f"{name}{entry.quantity:>{_QTY_WIDTH}}"
    elif kind == "vis_source":
        art = escape(_fit(entry.art, _ART_WIDTH))
        season = escape(_fit(entry.season, _SEASON_WIDTH))
        row = f"{name}{art}{entry.pawns:>{_PAWNS_WIDTH}}  {season}"
    else:  # vis_store
        art = escape(_fit(entry.art, _ART_WIDTH))
        row = f"{name}{art}{entry.pawns:>{_PAWNS_WIDTH}}"
    return row.rstrip()


def _line(label: str, value: object) -> str:
    return f"[b]{label}:[/] {escape(str(value))}"


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
    elif kind == "vis_source":
        lines.append(_line("Art", entry.art))
        lines.append(_line("Pawns", entry.pawns))
        lines.append(_line("Season", entry.season))
        optional("Location", entry.location)
        optional("Physical Form", entry.physical_form)
    else:  # vis_store
        lines.append(_line("Art", entry.art))
        lines.append(_line("Pawns", entry.pawns))
        optional("Location", entry.location)
        optional("Physical Form", entry.physical_form)

    if entry.lab is not None:
        lines.append(
            f"[dim]A laboratory of this covenant: {escape(entry.lab.name)}.[/]"
        )
    if entry.description.strip():
        lines += ["", "[b]Description:[/]", markdown_inline(entry.description.strip())]
    return "\n".join(lines)


def gear_points(saga: Saga, covenant: Covenant) -> int:
    """Points of Weapons and Armor: every weapon and armor entry's points."""
    return sum(
        entry.points
        for kind in ("weapon", "armor")
        for entry in entries_for_kind(saga, covenant, kind)
    )


def total_pawns(saga: Saga, covenant: Covenant, kind: str) -> int:
    """Pawns held in a vis list ("vis_source" per year, "vis_store" on hand)."""
    return sum(e.pawns for e in entries_for_kind(saga, covenant, kind))
