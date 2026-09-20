"""Logic behind a covenant's Inhabitants tab -- no UI in here.

Works out what each list shows (people listed automatically from character
sheets plus manually stored entries), the headcounts and the calculated Total
Inhabitants, which grogs are still available to assign, and the text for list
rows and the details panel.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import catalog
from .markup import escape, markdown_inline
from .models import (
    GOVERNANCE_STYLE_IDS,
    INHABITANT_KINDS,
    Character,
    Covenant,
    Inhabitant,
    Saga,
    character_age,
)

#: Section titles on the tab.
KIND_TITLES: dict[str, str] = {
    "magus": "Magi",
    "companion": "Companions",
    "specialist": "Specialists",
    "craftsperson": "Craftspeople",
    "turb": "Turb",
    "inhabitant": "Inhabitants",
    "horse": "Horses",
    "livestock": "Livestock",
}

#: How a single entry is named in dialogs ("Add a Magus").
KIND_SINGULAR: dict[str, str] = {
    "magus": "Magus",
    "companion": "Companion",
    "specialist": "Specialist",
    "craftsperson": "Craftsperson",
    "turb": "Turb Member",
    "inhabitant": "Inhabitant",
    "horse": "Horse",
    "livestock": "Livestock",
}

#: Kinds whose characters are listed automatically from their sheets.
AUTO_KINDS: tuple[str, ...] = ("magus", "companion")

#: Kinds a grog (a `grog` character) can be assigned to.
GROG_KINDS: tuple[str, ...] = ("specialist", "craftsperson", "turb", "inhabitant")


@dataclass
class InhabitantEntry:
    """One row of a list, whatever it was built from.

    `auto` entries are characters (magi/companions) listed straight from their
    sheets: name, year born and house are read live from the character, and
    `record` -- if the user has edited it -- only holds the covenant-side extras.
    Every other entry is its own `record`.
    """

    kind: str
    record: Inhabitant | None
    character: Character | None = None
    auto: bool = False

    def _own(self, attribute: str, default):
        return getattr(self.record, attribute) if self.record is not None else default

    @property
    def name(self) -> str:
        if self.auto and self.character is not None:
            return self.character.name
        return self._own("name", "")

    @property
    def year_born(self) -> int | None:
        if self.auto and self.character is not None:
            return self.character.background.year_born
        return self._own("year_born", None)

    @property
    def house_id(self) -> str | None:
        if self.auto and self.character is not None:
            return self.character.hermetic.house
        return self._own("house", None)

    @property
    def loyalty(self) -> int:
        return self._own("loyalty", 0)

    @property
    def quantity(self) -> int:
        return 1 if self.auto else self._own("quantity", 1)

    @property
    def responsibility(self) -> str:
        return self._own("responsibility", "")

    @property
    def role(self) -> str:
        return self._own("role", "")

    @property
    def skill_from_ability(self) -> int | None:
        """The Level of the linked Ability on the character's sheet, or None when
        the score isn't tied to one (no sheet, no Ability chosen, or the sheet
        no longer has it)."""
        if self.character is None or not self.linked_ability:
            return None
        ability = next(
            (a for a in self.character.abilities if a.name == self.linked_ability),
            None,
        )
        return ability.level if ability is not None else None

    @property
    def skill_value(self) -> int:
        """A Craftsperson's score: the linked Ability's Level when tied to a
        sheet, otherwise the number typed in."""
        from_ability = self.skill_from_ability
        return from_ability if from_ability is not None else self._own("skill_value", 0)

    @property
    def field_of_work(self) -> str:
        return self._own("field_of_work", "None")

    @property
    def rare(self) -> bool:
        return self._own("rare", False)

    @property
    def linked_ability(self) -> str:
        return self._own("linked_ability", "")

    @property
    def description(self) -> str:
        return self._own("description", "")

    @property
    def linked(self) -> bool:
        """Tied to a character sheet (auto-listed, or a grog assigned here)."""
        return self.character is not None


def _character_of(saga: Saga, character_id: str | None) -> Character | None:
    return next((c for c in saga.characters if c.id == character_id), None)


def entries_for_kind(
    saga: Saga, covenant: Covenant, kind: str
) -> list[InhabitantEntry]:
    """The rows of `kind`'s list, in display order: characters listed from their
    sheets first (Magi/Companions), then stored entries in the order added."""
    entries: list[InhabitantEntry] = []
    if kind in AUTO_KINDS:
        for character in saga.characters:
            if character.type == kind and character.covenant_id == covenant.id:
                record = next(
                    (
                        r
                        for r in covenant.inhabitants
                        if r.kind == kind and r.character_id == character.id
                    ),
                    None,
                )
                if record is not None and record.departed:
                    continue  # still in the covenant on the sheet, not counted here
                entries.append(InhabitantEntry(kind, record, character, auto=True))
    for record in covenant.inhabitants:
        if record.kind != kind:
            continue
        if kind in AUTO_KINDS and record.character_id is not None:
            continue  # an override of an auto-listed character; shown above
        entries.append(
            InhabitantEntry(kind, record, _character_of(saga, record.character_id))
        )
    return entries


def headcount(entries: list[InhabitantEntry]) -> int:
    """How many people or animals a list stands for: quantities added up, so
    "Servants x2" counts as two, not one."""
    return sum(entry.quantity for entry in entries)


def total_inhabitants(saga: Saga, covenant: Covenant) -> int:
    """The calculated Total Inhabitants: Other People plus every list's headcount."""
    return covenant.population.other_people + sum(
        headcount(entries_for_kind(saga, covenant, kind)) for kind in INHABITANT_KINDS
    )


def available_grogs(saga: Saga, covenant: Covenant) -> list[Character]:
    """Grogs belonging to the covenant that aren't assigned to any section yet."""
    assigned = {r.character_id for r in covenant.inhabitants if r.character_id}
    return [
        c
        for c in saga.characters
        if c.type == "grog" and c.covenant_id == covenant.id and c.id not in assigned
    ]


def ability_names(character: Character | None) -> list[str]:
    """The Abilities of a character, for a Craftsperson's Linked Ability."""
    return [a.name for a in character.abilities] if character is not None else []


def governance_names(covenant: Covenant) -> list[str]:
    """Names of the "Style of Governance" Boons the covenant has, in order."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return [
        by_id[bh.vf_id].name
        for bh in covenant.boons_hooks
        if bh.vf_id in GOVERNANCE_STYLE_IDS and bh.vf_id in by_id
    ]


# ------------------------------------------------------------------- text


def _year(year: int | None) -> str:
    return "Unknown" if year is None else str(year)


def house_name(house_id: str | None) -> str:
    if not house_id:
        return ""
    house = catalog.load_house_catalog_by_id().get(house_id)
    return house.name if house is not None else house_id


def row_label(entry: InhabitantEntry) -> str:
    """One list row (markup), following the layout of the paper sheet."""
    kind = entry.kind
    parts: list[str] = [escape(entry.name or "(unnamed)")]

    def add(text: str) -> None:
        if text:
            parts.append(escape(text))

    if kind == "magus":
        add(f"House {house_name(entry.house_id) or 'Unknown'}")
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind == "companion" or kind == "specialist":
        add(entry.responsibility)
        add(entry.role)
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind == "craftsperson":
        add(entry.responsibility)
        add(f"Score: {entry.skill_value}")
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind in ("turb", "inhabitant"):
        add(entry.responsibility)
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
    else:  # horse, livestock
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
    add(f"Loyalty: {entry.loyalty}")
    return " | ".join(parts)


def detail_text(entry: InhabitantEntry | None, current_year: int) -> str:
    """The details panel (markup) for a chosen entry, description included and
    rendered with inline emphasis."""
    if entry is None:
        return "[dim]Select an inhabitant to see its details.[/]"
    kind = entry.kind
    lines = [f"[b]Name:[/] {escape(entry.name or '(unnamed)')}"]
    lines.append(f"[b]Kind:[/] {KIND_SINGULAR[kind]}")
    if kind == "magus":
        lines.append(f"[b]House:[/] {escape(house_name(entry.house_id) or 'Unknown')}")

    age = character_age(entry.year_born, current_year)
    born = _year(entry.year_born) + (f" (age {age})" if age is not None else "")
    lines.append(f"[b]Year Born:[/] {born}")
    if kind in GROG_KINDS + ("companion",) and entry.responsibility:
        lines.append(f"[b]Responsibility:[/] {escape(entry.responsibility)}")
    if kind in ("companion", "specialist") and entry.role:
        lines.append(f"[b]Covenant Role:[/] {escape(entry.role)}")
    if kind == "craftsperson":
        lines.append(f"[b]Field of Work:[/] {escape(entry.field_of_work)}")
        source = (
            " (from the linked Ability)" if entry.skill_from_ability is not None else ""
        )
        lines.append(f"[b]Skill Value:[/] {entry.skill_value}{source}")
        lines.append(f"[b]Rare:[/] {'Yes' if entry.rare else 'No'}")
        if entry.linked_ability:
            lines.append(f"[b]Linked Ability:[/] {escape(entry.linked_ability)}")
    if kind not in AUTO_KINDS:
        lines.append(f"[b]Quantity:[/] {entry.quantity}")
    lines.append(f"[b]Loyalty:[/] {entry.loyalty}")
    if entry.character is not None:
        lines.append(
            f"[dim]From the character sheet of {escape(entry.character.name)}.[/]"
        )
    if entry.description.strip():
        lines += ["", "[b]Description:[/]", markdown_inline(entry.description.strip())]
    return "\n".join(lines)


def _aligned(rows: list[tuple[str, str]]) -> str:
    width = max(len(label) for label, _ in rows)
    return "\n".join(f"{label + ':':<{width + 1}} {value}" for label, value in rows)


def loyalty_left_text(covenant: Covenant) -> str:
    """Type of Governance and the four loyalty figures. The governance follows the
    Boon the covenant has (shown dimmed, since it isn't typed here); otherwise it
    is whatever the user typed."""
    styles = governance_names(covenant)
    if styles:
        governance = f"[dim]{escape(', '.join(styles))}[/]"
    else:
        governance = escape(covenant.loyalty.governance) or "(not set)"
    loyalty = covenant.loyalty
    return _aligned(
        [
            ("Type of Governance", governance),
            ("Base Loyalty Points", str(loyalty.base_points)),
            ("Total modifiers", str(loyalty.total_modifiers)),
            ("Current Loyalty Points", str(loyalty.current_points)),
            ("Prevailing Loyalty Score", str(loyalty.prevailing_score)),
        ]
    )


def loyalty_right_text(covenant: Covenant) -> str:
    loyalty = covenant.loyalty
    body = _aligned(
        [
            ("Living Conditions", str(loyalty.living_conditions)),
            (
                "Equipment",
                f"{escape(loyalty.equipment)}  ({loyalty.equipment_modifier})",
            ),
            ("Money", f"{escape(loyalty.money)}  ({loyalty.money_modifier})"),
            ("Specialists", str(loyalty.specialists)),
            ("Familiarity", str(loyalty.familiarity)),
            ("Actions and events", str(loyalty.actions_and_events)),
        ]
    )
    return f"[b]Situational Modifiers for:[/]\n{body}"


def population_text(saga: Saga, covenant: Covenant) -> str:
    population = covenant.population
    return _aligned(
        [
            (
                "Number of Teamsters / Needed",
                f"{population.teamsters} / {population.teamsters_needed}",
            ),
            (
                "Number of Servants / Needed",
                f"{population.servants} / {population.servants_needed}",
            ),
            ("Other People", str(population.other_people)),
            ("Total Inhabitants", str(total_inhabitants(saga, covenant))),
        ]
    )


def misc_text(covenant: Covenant) -> tuple[str, str]:
    """The Miscellaneous block as two columns."""
    p = covenant.population
    left = _aligned(
        [
            ("Aging for Magi", str(p.aging_magi)),
            ("Aging for Mundane", str(p.aging_mundane)),
            ("Magic Laborers", str(p.magic_laborers)),
        ]
    )
    right = _aligned(
        [
            ("Magic Servants", str(p.magic_servants)),
            ("Magic Teamsters", str(p.magic_teamsters)),
            ("Magic Turbula", str(p.magic_turbula)),
        ]
    )
    return left, right
