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
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    Character,
    Covenant,
    Inhabitant,
    Saga,
    character_age,
    round_away_from_zero,
)

#: Section titles on the tab.
KIND_TITLES: dict[str, str] = {
    "magus": "Magi",
    "companion": "Companions",
    "specialist": "Specialists",
    "craftsperson": "Craftspeople",
    "turb": "Turb",
    "inhabitant": "Other Covenfolk",
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
    "inhabitant": "Covenfolk Member",
    "horse": "Horse",
    "livestock": "Livestock",
}

#: If an "inhabitant" (Other Covenfolk) entry's Name is exactly this plural
#: form of its Covenant Role, the role is redundant in the row label and is
#: left out there (still shown in the details panel).
OTHER_COVENFOLK_ROLE_PLURALS: dict[str, str] = {
    "Laborer": "Laborers",
    "Servant": "Servants",
    "Teamster": "Teamsters",
    "Dependent": "Dependents",
}

#: Kinds whose characters are listed automatically from their sheets.
AUTO_KINDS: tuple[str, ...] = ("magus", "companion")

#: Kinds a grog (a `grog` character) can be assigned to.
GROG_KINDS: tuple[str, ...] = ("specialist", "craftsperson", "turb", "inhabitant")

#: Points of one inhabitant by kind: (Spring/Winter covenant, Summer/Autumn
#: covenant). Livestock are not in the book's table and count nothing.
INHABITANT_POINTS: dict[str, tuple[int, int]] = {
    "magus": (5, 10),
    "companion": (3, 5),
    "specialist": (2, 3),
    "craftsperson": (2, 3),
    "turb": (1, 2),
    "inhabitant": (1, 2),
    "horse": (1, 1),
    "livestock": (0, 0),
}

#: Other People (the one Inhabitants-summary figure with no list behind it)
#: scores the same as the "inhabitant" kind (Other Covenfolk) -- 1/2 points.
OTHER_COVENFOLK_POINTS: tuple[int, int] = (1, 2)

#: "Gentle Gift"/"The Gift"/"Blatant Gift" display text -> Loyalty's Gift
#: modifier to Base Loyalty. A magus with "No Gift" (a deliberate choice, not
#: the default) scores the same as Gentle Gift: no social penalty.
GIFT_LOYALTY_MODIFIERS: dict[str, int] = {
    "Gentle Gift": 0,
    "The Gift": -30,
    "Blatant Gift": -105,
    "No Gift": 0,
}
#: GIFT_CHOICES (models.py) -> the display text above.
_GIFT_DISPLAY: dict[str, str] = {
    "Gentle": "Gentle Gift",
    "Normal": "The Gift",
    "Blatant": "Blatant Gift",
    "None": "No Gift",
}

#: A Covenant Role's Loyalty bonus is Presence plus these Abilities' Levels,
#: summed (Autocrat, doing both a Steward's and a Chamberlain's job, gets
#: both Profession abilities).
ROLE_ABILITY_MAP: dict[str, tuple[str, ...]] = {
    "Turb Captain": ("Leadership",),
    "Steward": ("Profession: Steward",),
    "Chamberlain": ("Profession: Chamberlain",),
    "Autocrat": ("Profession: Chamberlain", "Profession: Steward"),
}

#: Loyalty points from the Equipment/Money situational modifiers, keyed by
#: the LOYALTY_EQUIPMENT/LOYALTY_MONEY option text (same order as those
#: tuples). A pension adds a flat bonus on top of the Money figure.
EQUIPMENT_LOYALTY_POINTS: dict[str, int] = dict(
    zip(LOYALTY_EQUIPMENT, (-10, 0, 10, 20))
)
MONEY_LOYALTY_POINTS: dict[str, int] = dict(zip(LOYALTY_MONEY, (-20, -10, 0, 10, 20)))
PENSION_LOYALTY_POINTS = 10

#: Loyalty Points Total -> Prevailing Loyalty Score, the cumulative
#: thresholds from the same table used for Ability Advancement (symmetric
#: for a negative total -- see prevailing_loyalty_score()). The doc doesn't
#: extend the table past +/-105, so anything beyond that clamps to +/-6.
PREVAILING_LOYALTY_TABLE: tuple[tuple[int, int], ...] = (
    (0, 0),
    (5, 1),
    (15, 2),
    (30, 3),
    (50, 4),
    (75, 5),
    (105, 6),
)


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
    def gift(self) -> str:
        """Display text ("Gentle Gift"/"The Gift"/"Blatant Gift"/"No Gift"):
        "" if not applicable (not a magus), or if this is a manual entry with
        no choice made yet -- base_loyalty() then assumes the magus default,
        The Gift. A sheet-linked magus's Gift is read from their Virtues."""
        if self.kind != "magus":
            return ""
        if self.character is not None:
            vf_ids = {i.vf_id for i in self.character.virtues_flaws}
            if "vf_gentle_gift" in vf_ids:
                return "Gentle Gift"
            if "vf_blatant_gift" in vf_ids:
                return "Blatant Gift"
            return "The Gift"
        return _GIFT_DISPLAY.get(self._own("gift", ""), "")

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
    def role_presence(self) -> int:
        """The Presence behind a Specialist role's Loyalty bonus: the linked
        character's Characteristic when tied to a sheet, else the number
        typed in."""
        if self.character is not None:
            return self.character.characteristics.presence
        return self._own("presence", 0)

    @property
    def role_ability_total(self) -> int:
        """The Ability portion of a Specialist role's Loyalty bonus: the
        level(s) of ROLE_ABILITY_MAP's ability/abilities on the linked
        character (summed, for Autocrat's two), else the number typed in."""
        names = ROLE_ABILITY_MAP.get(self.role, ())
        if not names:
            return 0
        if self.character is not None:
            levels = {a.name: a.level for a in self.character.abilities}
            return sum(levels.get(name, 0) for name in names)
        return self._own("skill_value", 0)

    @property
    def role_bonus(self) -> int | None:
        """The covenant Role's Loyalty bonus (Presence + Ability), or None
        when the role isn't one of the four the book gives a bonus for."""
        if self.role not in ROLE_ABILITY_MAP:
            return None
        return self.role_presence + self.role_ability_total

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
    """The calculated Total Inhabitants: Other People plus every list's headcount
    except Livestock -- per the book, livestock aren't inhabitants at all (they're
    tracked here for convenience, but never counted)."""
    return covenant.population.other_people + sum(
        headcount(entries_for_kind(saga, covenant, kind))
        for kind in INHABITANT_KINDS
        if kind != "livestock"
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


# ---------------------------------------------------------- inhabitant points


def _season_column(pair: tuple[int, int], covenant: Covenant) -> int:
    return pair[1] if covenant.covenant_season in ("Summer", "Autumn") else pair[0]


def inhabitant_points(
    saga: Saga, covenant: Covenant, *, exclude_roles: tuple[str, ...] = ()
) -> int:
    """Points of Inhabitants: each list's headcount times its kind's points
    (the covenant's Covenant Season picks the column), plus Other People
    counted by number. `exclude_roles` leaves out Other Covenfolk entries
    (the "inhabitant" kind) whose Covenant Role matches -- used by the
    minimum Servants/Teamsters formulas below, which each exclude
    themselves."""
    total = 0
    for kind in INHABITANT_KINDS:
        entries = entries_for_kind(saga, covenant, kind)
        if kind == "inhabitant" and exclude_roles:
            entries = [e for e in entries if e.role not in exclude_roles]
        total += headcount(entries) * _season_column(INHABITANT_POINTS[kind], covenant)
    total += covenant.population.other_people * _season_column(
        OTHER_COVENFOLK_POINTS, covenant
    )
    return total


def other_covenfolk_count(saga: Saga, covenant: Covenant, role: str) -> int:
    """Total quantity of Other Covenfolk (the "inhabitant" kind) entries with
    this Covenant Role (one of OTHER_COVENFOLK_ROLES) -- what the Inhabitants
    summary's Teamsters/Servants/Laborers counts are read from."""
    return sum(
        e.quantity
        for e in entries_for_kind(saga, covenant, "inhabitant")
        if e.role == role
    )


def minimum_servants(saga: Saga, covenant: Covenant) -> int:
    """2 Servants for every 10 points of inhabitants, excluding Servants,
    Laborers and Teamsters themselves."""
    points = inhabitant_points(
        saga, covenant, exclude_roles=("Servant", "Laborer", "Teamster")
    )
    return round_away_from_zero(points * 2 / 10)


def minimum_teamsters(saga: Saga, covenant: Covenant) -> int:
    """1 Teamster for every 10 points of inhabitants (excluding Laborers and
    Teamsters), after subtracting twice the number of Laborers."""
    points = inhabitant_points(saga, covenant, exclude_roles=("Laborer", "Teamster"))
    points -= 2 * other_covenfolk_count(saga, covenant, "Laborer")
    return round_away_from_zero(max(points, 0) / 10)


# ----------------------------------------------------------------- loyalty


def base_loyalty(saga: Saga, covenant: Covenant) -> int:
    """Base Loyalty: the average, across the covenant's magi, of each one's
    Gift modifier. 0 with no magi. An unset manual Gift is assumed to be the
    ordinary Gift (the default expectation for a magus)."""
    magi = entries_for_kind(saga, covenant, "magus")
    if not magi:
        return 0
    total = sum(GIFT_LOYALTY_MODIFIERS.get(entry.gift, -30) for entry in magi)
    return round_away_from_zero(total / len(magi))


def specialists_loyalty(saga: Saga, covenant: Covenant) -> int:
    """The Specialists Loyalty bonus: every Companion/Specialist entry's
    role_bonus (Presence + the role's Ability, or Abilities for Autocrat),
    summed."""
    return sum(
        entry.role_bonus or 0
        for kind in ("companion", "specialist")
        for entry in entries_for_kind(saga, covenant, kind)
        if entry.role_bonus is not None
    )


def reputation_loyalty_penalty(covenant: Covenant) -> int:
    """-5 Loyalty per point of every bad Reputation the covenant is aware of.
    A Reputation the covenant doesn't know about, or a good one, costs
    nothing."""
    return -5 * sum(
        abs(r.score) for r in covenant.reputations if r.score < 0 and r.known
    )


def living_conditions_loyalty(covenant: Covenant) -> int:
    """10 Loyalty points per point of the covenant's Living Conditions
    (Mundane) -- covenfolk are mundane, so Living Conditions (Magi) doesn't
    apply here."""
    return covenant.living_conditions_mundane * 10


def equipment_loyalty(covenant: Covenant) -> int:
    return EQUIPMENT_LOYALTY_POINTS.get(covenant.loyalty.equipment, 0)


def money_loyalty(covenant: Covenant) -> int:
    points = MONEY_LOYALTY_POINTS.get(covenant.loyalty.money, 0)
    if covenant.loyalty.pension:
        points += PENSION_LOYALTY_POINTS
    return points


def total_modifiers(saga: Saga, covenant: Covenant) -> int:
    """Every situational contributor to Loyalty, summed."""
    loyalty = covenant.loyalty
    return (
        living_conditions_loyalty(covenant)
        + equipment_loyalty(covenant)
        + money_loyalty(covenant)
        + specialists_loyalty(saga, covenant)
        + loyalty.familiarity
        + reputation_loyalty_penalty(covenant)
        + loyalty.actions_and_events
        + loyalty.magical_influence
    )


def current_loyalty_points(saga: Saga, covenant: Covenant) -> int:
    """Base Loyalty + Total Modifiers."""
    return base_loyalty(saga, covenant) + total_modifiers(saga, covenant)


def prevailing_loyalty_score(points: int) -> int:
    """Loyalty Points Total -> Prevailing Loyalty Score, via the fixed
    cumulative table (symmetric for a negative total)."""
    magnitude = abs(points)
    score = 0
    for threshold, table_score in PREVAILING_LOYALTY_TABLE:
        if magnitude >= threshold:
            score = table_score
    return -score if points < 0 else score


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
        add(entry.gift)
    elif kind == "companion" or kind == "specialist":
        add(entry.responsibility)
        add(entry.role)
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind == "craftsperson":
        add(entry.responsibility)
        add(f"Score: {entry.skill_value}")
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind == "turb":
        add(entry.responsibility)
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
    elif kind == "inhabitant":
        # The role is redundant (and left out) when the name is already its
        # plural, e.g. a "Teamsters" entry tagged Teamster.
        if entry.role and entry.name != OTHER_COVENFOLK_ROLE_PLURALS.get(entry.role):
            add(entry.role)
        add(f"Qty: {entry.quantity}")
        if entry.quantity == 1:
            add(f"Year Born: {_year(entry.year_born)}")
    else:  # horse, livestock
        add(f"Qty: {entry.quantity}")
        add(f"Year Born: {_year(entry.year_born)}")
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
    if kind == "magus" and entry.gift:
        lines.append(f"[b]Gift:[/] {escape(entry.gift)}")
    if kind in GROG_KINDS + ("companion",) and entry.responsibility:
        lines.append(f"[b]Responsibility:[/] {escape(entry.responsibility)}")
    if kind in ("companion", "specialist", "inhabitant") and entry.role:
        lines.append(f"[b]Covenant Role:[/] {escape(entry.role)}")
        if entry.role_bonus is not None:
            lines.append(
                f"[b]Loyalty Bonus:[/] {entry.role_bonus} "
                f"(Presence {entry.role_presence:+d}, Ability {entry.role_ability_total})"
            )
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


def loyalty_left_text(saga: Saga, covenant: Covenant) -> str:
    """Type of Governance and the four loyalty figures -- all calculated now
    except Governance (which follows the covenant's governance Boon if it has
    one, shown dimmed since it isn't typed here; otherwise whatever the user
    typed)."""
    styles = governance_names(covenant)
    if styles:
        governance = f"[dim]{escape(', '.join(styles))}[/]"
    else:
        governance = escape(covenant.loyalty.governance) or "(not set)"
    base = base_loyalty(saga, covenant)
    modifiers = total_modifiers(saga, covenant)
    current = base + modifiers
    return _aligned(
        [
            ("Type of Governance", governance),
            ("Base Loyalty Points", str(base)),
            ("Total modifiers", str(modifiers)),
            ("Current Loyalty Points", str(current)),
            ("Prevailing Loyalty Score", str(prevailing_loyalty_score(current))),
        ]
    )


def loyalty_right_text(saga: Saga, covenant: Covenant) -> str:
    """The situational modifiers behind Total Modifiers -- all calculated
    from elsewhere on the sheet except Familiarity, Actions and Events and
    Magical Influence, which stay free-form (meant to come from the Diary
    once that tab exists)."""
    loyalty = covenant.loyalty
    money = (
        f"{escape(loyalty.money)}  ({MONEY_LOYALTY_POINTS.get(loyalty.money, 0):+d})"
    )
    if loyalty.pension:
        money += f" [dim]+ pension ({PENSION_LOYALTY_POINTS:+d})[/]"
    body = _aligned(
        [
            (
                "Living Conditions",
                f"{covenant.living_conditions_mundane:+d}  "
                f"({living_conditions_loyalty(covenant):+d})",
            ),
            (
                "Equipment",
                f"{escape(loyalty.equipment)}  ({equipment_loyalty(covenant):+d})",
            ),
            ("Money", money),
            ("Specialists", str(specialists_loyalty(saga, covenant))),
            ("Familiarity", str(loyalty.familiarity)),
            ("Reputation", str(reputation_loyalty_penalty(covenant))),
            ("Actions and events", str(loyalty.actions_and_events)),
            ("Magical Influence", str(loyalty.magical_influence)),
        ]
    )
    return f"[b]Situational Modifiers for:[/]\n{body}"


def population_text(saga: Saga, covenant: Covenant) -> str:
    """Teamsters, Servants and Laborers are read from the Other Covenfolk
    list below (entries tagged with that Covenant Role), not typed here."""
    population = covenant.population
    teamsters = other_covenfolk_count(saga, covenant, "Teamster")
    servants = other_covenfolk_count(saga, covenant, "Servant")
    laborers = other_covenfolk_count(saga, covenant, "Laborer")
    return _aligned(
        [
            (
                "Number of Teamsters / Needed",
                _min_colored(teamsters, minimum_teamsters(saga, covenant)),
            ),
            (
                "Number of Servants / Needed",
                _min_colored(servants, minimum_servants(saga, covenant)),
            ),
            ("Number of Laborers", str(laborers)),
            ("Other People", str(population.other_people)),
            ("Total Inhabitants", str(total_inhabitants(saga, covenant))),
        ]
    )


def _min_colored(actual: int, minimum: int) -> str:
    """ "actual / minimum", both numbers coloured as one unit: green when the
    minimum is met, red otherwise (same "colour the pair together" idea as
    the covenant Boons/Hooks point totals)."""
    color = "green" if actual >= minimum else "red"
    return f"[{color}]{actual} / {minimum}[/]"


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
