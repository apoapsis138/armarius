"""Logic behind a covenant's Inhabitants tab -- no UI in here.

Works out what each list shows (people listed automatically from character
sheets plus manually stored entries), the headcounts and the calculated Total
Inhabitants, which grogs are still available to assign, and the text for list
rows and the details panel.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any

from . import catalog, covenant_diary, storage
from .markup import aligned, escape, fit, inherited, markdown_text
from .models import (
    INHABITANT_KINDS,
    LOYALTY_EQUIPMENT,
    LOYALTY_MONEY,
    Character,
    Covenant,
    Inhabitant,
    Saga,
    character_age,
)
from .rules import reputations, study, xp
from .rules.animal_grogs import describe as describe_animal
from .rules.covenfolk import (
    AUTO_KINDS,
    GIFT_LOYALTY_MODIFIERS,
    ROLE_TASKS,
    InhabitantEntry,
    character_kind,
    entries_for_kind,
    headcount,
    minimum_servants,
    minimum_teamsters,
    other_covenfolk_count,
)
from .rules.rounding import round_away_from_zero

INHABITANTS_SOURCE = (
    "Covenants, Chapter Five: Wealth & Poverty, Points of Inhabitants, p. 63"
)
LOYALTY_SOURCE = (
    "Covenants, Chapter Three: Governance, Calculating Prevailing Loyalty, p. 36"
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
    "hound": "Hounds",
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
    "hound": "Hound",
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

#: Kinds a grog (a `grog` character) can be assigned to.
GROG_KINDS: tuple[str, ...] = ("specialist", "craftsperson", "turb", "inhabitant")
#: Kinds an animal grog can be assigned to: a horse grog is one of the
#: covenant's horses, a dog or a hawk one of its hounds.
ANIMAL_KINDS: tuple[str, ...] = ("horse", "hound")
#: Kinds listed but not counted as inhabitants: Covenants' Points of
#: Inhabitants count horses (1 point each) but no other animal, so hounds
#: count no more than livestock do.
UNCOUNTED_KINDS: tuple[str, ...] = ("hound", "livestock")

#: Loyalty points from the Equipment/Money situational modifiers, keyed by
#: the LOYALTY_EQUIPMENT/LOYALTY_MONEY option text (same order as those
#: tuples). A pension adds a flat bonus on top of the Money figure.
EQUIPMENT_LOYALTY_POINTS: dict[str, int] = dict(
    zip(LOYALTY_EQUIPMENT, (-10, 0, 10, 20))
)
MONEY_LOYALTY_POINTS: dict[str, int] = dict(zip(LOYALTY_MONEY, (-20, -10, 0, 10, 20)))
PENSION_LOYALTY_POINTS = 10

#: Loyalty points become a Prevailing Loyalty Score by the Ability
#: Advancement Table, negative points to a negative score (DE p. 186;
#: Covenants p. 36); the table goes on past 105 (7 at 140, 8 at 180).
#: At -6 the covenant's productivity is halved, at +6 raised (DE p. 185).
PRODUCTIVITY_LOYALTY = 6
PRODUCTIVITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Prevailing Loyalty, p. 185"
)


def departed_entries_for_kind(
    saga: Saga, covenant: Covenant, kind: str
) -> list[InhabitantEntry]:
    """Departed Magi/Companions of `kind`: still in the covenant on their
    sheet, but marked as no longer counting as an inhabitant (see
    Inhabitant.departed). Not applicable to any other kind."""
    if kind not in AUTO_KINDS:
        return []
    entries: list[InhabitantEntry] = []
    for character in saga.characters:
        if character_kind(character) != kind or character.covenant_id != covenant.id:
            continue
        record = next(
            (
                r
                for r in covenant.inhabitants
                if r.kind == kind and r.character_id == character.id
            ),
            None,
        )
        if record is not None and record.departed:
            entries.append(InhabitantEntry(kind, record, character, auto=True))
    return entries


def addable_characters(saga: Saga, covenant: Covenant, kind: str) -> list[Character]:
    """The saga's characters `kind`'s list (Magi or Companions) could take
    in: every one of that kind not on it, whether in another covenant, in
    none, or taken off it earlier."""
    if kind not in AUTO_KINDS:
        return []
    listed = {
        e.character.id
        for e in entries_for_kind(saga, covenant, kind)
        if e.character is not None
    }
    return [
        c for c in saga.characters if character_kind(c) == kind and c.id not in listed
    ]


def take_in(covenant: Covenant, kind: str, character: Character) -> None:
    """Put a character on `kind`'s list: they join the covenant, and count
    as an inhabitant again if they had been taken off."""
    character.covenant_id = covenant.id
    for record in covenant.inhabitants:
        if record.kind == kind and record.character_id == character.id:
            record.departed = False


def total_inhabitants(saga: Saga, covenant: Covenant) -> int:
    """The calculated Total Inhabitants: Other People plus every list's headcount
    except Hounds and Livestock -- per the book, only people and horses are
    inhabitants (the others are tracked here for convenience, but never
    counted)."""
    return covenant.population.other_people + sum(
        headcount(entries_for_kind(saga, covenant, kind))
        for kind in INHABITANT_KINDS
        if kind not in UNCOUNTED_KINDS
    )


def takes_grogs(kind: str) -> bool:
    """Whether `kind`'s list offers the covenant's grogs: a person's list
    its people, Horses and Hounds its animals."""
    return kind in GROG_KINDS or kind in ANIMAL_KINDS


def available_grogs(
    saga: Saga, covenant: Covenant, kind: str | None = None
) -> list[Character]:
    """Grogs belonging to the covenant that aren't assigned to any section
    yet: for `kind`, the animal grogs if it is Horses or Hounds, else the
    people."""
    assigned = {r.character_id for r in covenant.inhabitants if r.character_id}
    return [
        c
        for c in saga.characters
        if c.type == "grog"
        and c.covenant_id == covenant.id
        and c.id not in assigned
        and (kind is None or (c.animal is not None) == (kind in ANIMAL_KINDS))
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
        if bh.vf_id in by_id and by_id[bh.vf_id].governance
    ]


# ---------------------------------------------------------- inhabitant points


# ----------------------------------------------------------------- loyalty


#: Familiarity's Loyalty points for each year the covenant has stood.
FAMILIARITY_PER_YEAR = 2


def familiarity(saga: Saga, covenant: Covenant) -> int:
    """Familiarity: 2 Loyalty points for each year since the covenant was
    founded, at most what the magi's Gift takes off (Base Loyalty), plus
    the typed adjustment (DE p. 186)."""
    grown = 0
    if covenant.year_founded is not None:
        years = max(0, saga.current_year - covenant.year_founded)
        grown = min(FAMILIARITY_PER_YEAR * years, max(0, -base_loyalty(saga, covenant)))
    return grown + covenant.loyalty.familiarity


def base_loyalty(saga: Saga, covenant: Covenant) -> int:
    """Base Loyalty: the average, across the covenant's magi, of each one's
    Gift modifier. 0 with no magi. An unset manual Gift is assumed to be the
    ordinary Gift (the default expectation for a magus). LOYALTY_SOURCE; the
    average rounds away from zero (covenant finances)."""
    magi = entries_for_kind(saga, covenant, "magus")
    if not magi:
        return 0
    total = sum(
        GIFT_LOYALTY_MODIFIERS.get(entry.gift, GIFT_LOYALTY_MODIFIERS["The Gift"])
        for entry in magi
    )
    return round_away_from_zero(total / len(magi))


def _role_holders(saga: Saga, covenant: Covenant) -> list[InhabitantEntry]:
    """Every Companion or Specialist whose role earns a Loyalty bonus."""
    return [
        entry
        for kind in ("companion", "specialist")
        for entry in entries_for_kind(saga, covenant, kind)
        if entry.role_bonus is not None
    ]


def counted_role_holders(saga: Saga, covenant: Covenant) -> list[InhabitantEntry]:
    """The role-holders whose Loyalty bonus counts: at most one for each of
    the three tasks (turb captain, steward, chamberlain; an autocrat does
    two), so at most three specialists (ROLES_SOURCE). When more hold a
    task, the choice covering the most tasks, then the highest total,
    counts."""
    holders = _role_holders(saga, covenant)
    best: tuple[int, int] = (0, 0)
    chosen: tuple[InhabitantEntry, ...] = ()
    for size in range(1, len(ROLE_TASKS) + 1):
        for group in combinations(holders, size):
            tasks = [ROLE_TASKS[e.role] for e in group]
            covered = frozenset().union(*tasks)
            if len(covered) != sum(len(t) for t in tasks):
                continue  # two of them doing the same task
            key = (len(covered), sum(e.role_bonus or 0 for e in group))
            if key > best:
                best, chosen = key, group
    return list(chosen)


def specialists_loyalty(saga: Saga, covenant: Covenant) -> int:
    """The Specialists Loyalty bonus: the counted role-holders' role_bonus
    (Presence + the role's Ability for each task), summed."""
    return sum(e.role_bonus or 0 for e in counted_role_holders(saga, covenant))


def uncounted_role_holders(saga: Saga, covenant: Covenant) -> list[InhabitantEntry]:
    """Role-holders left out because another already does their task."""
    counted = {_holder_key(e) for e in counted_role_holders(saga, covenant)}
    return [e for e in _role_holders(saga, covenant) if _holder_key(e) not in counted]


def _holder_key(entry: InhabitantEntry) -> tuple[str, str, str]:
    return (
        entry.kind,
        entry.record.id if entry.record is not None else "",
        entry.character.id if entry.character is not None else "",
    )


def reputation_loyalty(covenant: Covenant) -> int:
    """-5 Loyalty per point of every bad Reputation the covenfolk know of,
    +5 per point of every good local one (Covenants p. 40)."""
    return reputations.loyalty_points(covenant.reputations)


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
        + familiarity(saga, covenant)
        + reputation_loyalty(covenant)
        + covenant_diary.actions_and_events(covenant)
        + loyalty.magical_influence
    )


def prevailing_loyalty_score(points: int) -> int:
    """Loyalty Points Total -> Prevailing Loyalty Score by the Ability
    Advancement Table, symmetric for a negative total."""
    score = xp.score_from_xp(abs(points), xp.ABILITY_FACTOR)
    return -score if points < 0 else score


def prevailing_loyalty(saga: Saga, covenant: Covenant) -> int:
    """The covenant's Prevailing Loyalty Score."""
    return prevailing_loyalty_score(
        base_loyalty(saga, covenant) + total_modifiers(saga, covenant)
    )


def productivity_note(score: int) -> str:
    """What a Prevailing Loyalty of +-6 or beyond does to the covenant's
    productivity ("" otherwise): halved at -6 (cost savings and income
    that rely on covenfolk), raised at +6 (the book gives no figure)."""
    if score <= -PRODUCTIVITY_LOYALTY:
        return (
            f"Prevailing Loyalty {score}: productivity halved (laborers' and "
            "craftspeople's savings, and income that relies on covenfolk)"
        )
    if score >= PRODUCTIVITY_LOYALTY:
        return (
            f"Prevailing Loyalty {score:+d}: productivity raised (the book gives "
            "no figure; the troupe decides)"
        )
    return ""


# ------------------------------------------------------------------- text


def _year(year: int | None) -> str:
    return "Unknown" if year is None else str(year)


def house_name(house_id: str | None) -> str:
    if not house_id:
        return ""
    house = catalog.load_house_catalog_by_id().get(house_id)
    return house.name if house is not None else house_id


_NAME_WIDTH = 20
_HOUSE_WIDTH = 16
_YEAR_WIDTH = 10
_RESPONSIBILITY_WIDTH = 18
_ROLE_WIDTH = 14
_SCORE_WIDTH = 7
_QTY_WIDTH = 5


def table_header(kind: str) -> str:
    """The column titles above one kind's Inhabitants list; the two-character
    indent is the list's selector marker."""
    name = f"{'Name':<{_NAME_WIDTH}}"
    year = f"{'Year Born':>{_YEAR_WIDTH}}"
    if kind == "magus":
        return f"  {name}{'House':<{_HOUSE_WIDTH}}{year}  Gift"
    if kind in ("companion", "specialist"):
        return (
            f"  {name}{'Responsibility':<{_RESPONSIBILITY_WIDTH}}"
            f"{'Role':<{_ROLE_WIDTH}}{year}"
        )
    if kind == "craftsperson":
        return (
            f"  {name}{'Responsibility':<{_RESPONSIBILITY_WIDTH}}"
            f"{'Score':>{_SCORE_WIDTH}}{'Qty':>{_QTY_WIDTH}}  {year}"
        )
    if kind == "turb":
        return (
            f"  {name}{'Responsibility':<{_RESPONSIBILITY_WIDTH}}"
            f"{'Qty':>{_QTY_WIDTH}}  {year}"
        )
    if kind == "inhabitant":
        return f"  {name}{'Role':<{_ROLE_WIDTH}}{'Qty':>{_QTY_WIDTH}}  {year}"
    return f"  {name}{'Qty':>{_QTY_WIDTH}}  {year}"  # horse, hound, livestock


def row_label(entry: InhabitantEntry) -> str:
    """One list row (markup), columns lined up with `table_header`."""
    kind = entry.kind
    name = escape(fit(entry.name or "(unnamed)", _NAME_WIDTH))
    year = f"{_year(entry.year_born):>{_YEAR_WIDTH}}"
    if kind == "magus":
        house = escape(fit(house_name(entry.house_id) or "Unknown", _HOUSE_WIDTH))
        return f"{name}{house}{year}  {escape(entry.gift)}"
    if kind in ("companion", "specialist"):
        resp = escape(fit(entry.responsibility, _RESPONSIBILITY_WIDTH))
        role = escape(fit(entry.role, _ROLE_WIDTH))
        return f"{name}{resp}{role}{year}"
    if kind == "craftsperson":
        resp = escape(fit(entry.responsibility, _RESPONSIBILITY_WIDTH))
        score = f"{entry.skill_value:>{_SCORE_WIDTH}}"
        qty = f"{entry.quantity:>{_QTY_WIDTH}}"
        return f"{name}{resp}{score}{qty}  {year}"
    if kind == "turb":
        resp = escape(fit(entry.responsibility, _RESPONSIBILITY_WIDTH))
        qty = f"{entry.quantity:>{_QTY_WIDTH}}"
        return f"{name}{resp}{qty}  {year}"
    if kind == "inhabitant":
        # The role is redundant (and left blank) when the name is already its
        # plural, e.g. a "Teamsters" entry tagged Teamster.
        role_text = (
            entry.role
            if entry.role and entry.name != OTHER_COVENFOLK_ROLE_PLURALS.get(entry.role)
            else ""
        )
        role = escape(fit(role_text, _ROLE_WIDTH))
        qty = f"{entry.quantity:>{_QTY_WIDTH}}"
        shown_year = year if entry.quantity == 1 else f"{'-':>{_YEAR_WIDTH}}"
        return f"{name}{role}{qty}  {shown_year}"
    qty = f"{entry.quantity:>{_QTY_WIDTH}}"  # horse, hound, livestock
    return f"{name}{qty}  {year}"


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
                f"(Presence {entry.role_presence:+d}"
                + (" twice" if len(ROLE_TASKS[entry.role]) > 1 else "")
                + f", Ability {entry.role_ability_total})"
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
    if entry.character is not None and entry.character.animal is not None:
        lines.append(f"[b]Animal:[/] {escape(describe_animal(entry.character.animal))}")
    if entry.character is not None:
        lines.append(
            f"[dim]From the character sheet of {escape(entry.character.name)}.[/]"
        )
    if entry.description.strip():
        lines += ["", "[b]Description:[/]", markdown_text(entry.description.strip())]
    return "\n".join(lines)


def loyalty_left_text(saga: Saga, covenant: Covenant) -> str:
    """Type of Governance and the four loyalty figures -- all calculated now
    except Governance (which follows the covenant's governance Boon if it has
    one, shown dimmed since it isn't typed here; otherwise whatever the user
    typed)."""
    styles = governance_names(covenant)
    if styles:
        governance = inherited(escape(", ".join(styles)))
    else:
        governance = escape(covenant.loyalty.governance) or "(not set)"
    base = base_loyalty(saga, covenant)
    modifiers = total_modifiers(saga, covenant)
    current = base + modifiers
    return aligned(
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
    body = aligned(
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
            ("Specialists", _specialists_text(saga, covenant)),
            (
                "Familiarity",
                f"{familiarity(saga, covenant)} (2 a year since founding, at most "
                f"what the Gift takes"
                + (
                    f", {loyalty.familiarity:+d} adjusted"
                    if loyalty.familiarity
                    else ""
                )
                + ")",
            ),
            ("Reputation", str(reputation_loyalty(covenant))),
            ("Actions and events", _actions_and_events_text(covenant)),
            ("Magical Influence", str(loyalty.magical_influence)),
        ]
    )
    return f"[b]Situational Modifiers for:[/]\n{body}"


def _specialists_text(saga: Saga, covenant: Covenant) -> str:
    """The total, and how many role-holders it leaves out (one for each
    task)."""
    total = str(specialists_loyalty(saga, covenant))
    left_out = uncounted_role_holders(saga, covenant)
    if not left_out:
        return total
    return f"{total}  [dim]({len(left_out)} not counted: one for each task)[/]"


def _actions_and_events_text(covenant: Covenant) -> str:
    """The total, and its two parts once the Diary has Loyalty points."""
    diary = covenant_diary.diary_loyalty(covenant)
    total = covenant_diary.actions_and_events(covenant)
    if not diary:
        return str(total)
    manual = covenant.loyalty.actions_and_events
    return f"{total}  [dim](Diary {diary:+d}, manual {manual:+d})[/]"


def population_text(saga: Saga, covenant: Covenant) -> str:
    """Teamsters, Servants and Laborers are read from the Other Covenfolk
    list below (entries tagged with that Covenant Role), not typed here."""
    population = covenant.population
    teamsters = other_covenfolk_count(saga, covenant, "Teamster")
    servants = other_covenfolk_count(saga, covenant, "Servant")
    laborers = other_covenfolk_count(saga, covenant, "Laborer")
    return aligned(
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
    """ "actual / minimum", both numbers coloured as one unit in the theme's
    colours: $text-success when the minimum is met, $text-error otherwise
    (same "colour the pair together" idea as the covenant Boons/Hooks point
    totals)."""
    color = "$text-success" if actual >= minimum else "$text-error"
    return f"[{color}]{actual} / {minimum}[/]"


def misc_text(covenant: Covenant) -> tuple[str, str]:
    """The Miscellaneous block as two columns."""
    p = covenant.population
    left = aligned(
        [
            ("Aging for Magi", str(p.aging_magi)),
            ("Aging for Mundane", str(p.aging_mundane)),
            ("Magic Laborers", str(p.magic_laborers)),
        ]
    )
    right = aligned(
        [
            ("Magic Servants", str(p.magic_servants)),
            ("Magic Teamsters", str(p.magic_teamsters)),
            ("Magic Turbula", str(p.magic_turbula)),
        ]
    )
    return left, right


# ------------------------------------------------------------------ changes


def _listed_record_id(covenant: Covenant, kind: str, name: str) -> str:
    """Id for the stored record of someone listed from their character sheet."""
    return storage.generate_unique_id(
        f"{kind}-{name}", [r.id for r in covenant.inhabitants]
    )


def save_entry(
    covenant: Covenant,
    kind: str,
    entry: InhabitantEntry | None,
    values: dict[str, Any],
    grog: Character | None = None,
) -> None:
    """Apply an add/edit form's `values`: a new record (for `grog`, if it's
    a grog's own), an update to the entry's record, or -- for a character
    listed from its sheet and edited for the first time -- a new record
    linked to that character."""
    if entry is None:
        covenant.inhabitants.append(
            Inhabitant(
                id=storage.generate_unique_id(
                    values.get("name") or kind,
                    [r.id for r in covenant.inhabitants],
                ),
                kind=kind,
                character_id=grog.id if grog is not None else None,
                **values,
            )
        )
    elif entry.record is not None:
        for key, value in values.items():
            setattr(entry.record, key, value)
    else:
        covenant.inhabitants.append(
            Inhabitant(
                id=_listed_record_id(covenant, kind, entry.name),
                kind=kind,
                character_id=entry.character.id if entry.character else None,
                **values,
            )
        )


def mark_departed(covenant: Covenant, kind: str, entry: InhabitantEntry) -> None:
    """A character listed from its sheet stops counting as an inhabitant
    (they stay in the covenant on their sheet)."""
    if entry.record is not None and entry.record in covenant.inhabitants:
        entry.record.departed = True
    else:
        covenant.inhabitants.append(
            Inhabitant(
                id=_listed_record_id(covenant, kind, entry.name),
                kind=kind,
                character_id=entry.character.id if entry.character else None,
                departed=True,
            )
        )


def form_problem(values: dict[str, Any]) -> str | None:
    """What's wrong with an inhabitant form's values, if anything."""
    if values.get("quantity", 1) < 1:
        return "Quantity must be at least 1."
    return None


def bought_kind(ability: str, category: str, *, teacher: bool = False) -> str:
    """Which covenfolk category a person bought with Build Points belongs
    to, from the Ability they serve the covenant with: the Build Points
    rules call them all specialists, but the covenant's finances count a
    Craft as a craftsperson and a Martial Ability as the turb (full-time
    soldiers); a teacher, or anyone else, is a specialist."""
    if teacher:
        return "specialist"
    if ability.startswith("Craft"):
        return "craftsperson"
    if category == "Martial":
        return "turb"
    return "specialist"


# ------------------------------------------------- growing used to the Gifted

#: A grog's Loyal trait begins at most this far from the turb's Prevailing
#: Loyalty (Grogs p. 56).
LOYAL_SPREAD = 3
GIFTED_SOURCE = "Grogs, Chapter 4, Growing Used to The Gifted, p. 56"


def _loyal(character: Character, name: str) -> int | None:
    return next(
        (
            t.score
            for t in character.personality_traits
            if t.name.strip().casefold() == name.casefold()
        ),
        None,
    )


def loyal_toward(character: Character, magus: Character) -> tuple[int, str]:
    """A covenfolk's Loyal toward one magus, and how: his own Loyal to that
    magus where he has grown used to him (a trait "Loyal to <name>"), else
    his Loyal to Covenant (or plain Loyal), with the magus's Gift penalty
    either way (Grogs p. 56: Loyal to Covenant +2 and Loyal to Tillitus +3
    give 0 with Tillitus and -1 with the other magi)."""
    penalty = study.gift_social_penalty(magus)
    own = _loyal(character, f"Loyal to {magus.name}")
    if own is not None:
        why = f"Loyal to {magus.name} {own:+d}"
        base = own
    else:
        base = _loyal(character, "Loyal to Covenant")
        if base is None:
            base = _loyal(character, "Loyal") or 0
        why = f"Loyal {base:+d}"
    if penalty:
        why += f", the Gift -{penalty}"
    return base - penalty, why


def loyal_spread_problem(saga: Saga, character: Character) -> str:
    """A grog's Loyal more than LOYAL_SPREAD from his covenant's Prevailing
    Loyalty, which he begins within ("" when it fits, or he has none)."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is None or character.type != "grog":
        return ""
    own = _loyal(character, "Loyal to Covenant")
    if own is None:
        own = _loyal(character, "Loyal")
    if own is None:
        return ""
    prevailing = prevailing_loyalty(saga, covenant)
    if abs(own - prevailing) <= LOYAL_SPREAD:
        return ""
    return (
        f"{character.name}'s Loyal {own:+d} is more than {LOYAL_SPREAD} from "
        f"{covenant.name}'s Prevailing Loyalty {prevailing:+d}: a grog begins "
        "within 3 of it (Grogs p. 56)."
    )
