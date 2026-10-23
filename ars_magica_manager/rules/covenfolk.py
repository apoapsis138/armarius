"""A covenant's inhabitants as the rules count them: each list's entries
(the characters whose sheets place them there, then the ones entered),
the Points of Inhabitants they come to, and the Servants and Teamsters
the covenant needs at the least. The Inhabitants tab, its forms and its
text are inhabitants.py's."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..models import (
    COMPANION_TYPES,
    INHABITANT_KINDS,
    Character,
    Covenant,
    Inhabitant,
    Saga,
)
from . import effects, scores
from .rounding import round_away_from_zero

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Points for "
    "Inhabitants of a Typical Covenant (https://www.redcap.org/page/Ars_Magica"
    "_Definitive_Edition,_Chapter_Six:_Covenants#Points_for_Inhabitants_of_a"
    "_Typical_Covenant)"
)


#: Minimum servants: SERVANTS_PER_TEN for every 10 inhabitant points or part
#: of 10 (2 x ceil(points / 10): 25 points -> 6); minimum
#: teamsters: one per 10, less TEAMSTER_POINTS_PER_LABORER per laborer
#: (INHABITANTS_SOURCE). Fractions round up (covenant finances).
SERVANTS_PER_TEN = 2


TEAMSTER_POINTS_PER_LABORER = 2


#: Kinds whose characters are listed automatically from their sheets.
AUTO_KINDS: tuple[str, ...] = ("magus", "companion")


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
    "hound": (0, 0),
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


#: A Gift modifier -> its display text (No Gift is only ever chosen by hand).
_GIFT_BY_MODIFIER: dict[int, str] = {
    0: "Gentle Gift",
    -30: "The Gift",
    -105: "Blatant Gift",
}


#: GIFT_CHOICES (models/holdings.py) -> the display text above.
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

    def _own(self, attribute: str, default: Any):
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
            # The ordinary Gift, changed by Virtues and Flaws that carry a
            # gift_loyalty effect (Gentle Gift, Blatant Gift).
            modifier = GIFT_LOYALTY_MODIFIERS["The Gift"] + int(
                effects.amount_total(
                    effects.collect(
                        [scores.character_source(self.character.virtues_flaws)],
                        "gift_loyalty",
                    )
                )
            )
            return _GIFT_BY_MODIFIER.get(modifier, "The Gift")
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


def character_kind(character: Character) -> str:
    """The Inhabitants list a character's sheet puts it on: its type, with a
    Mythic Companion listed among the Companions."""
    return "companion" if character.type in COMPANION_TYPES else character.type


def entries_for_kind(
    saga: Saga, covenant: Covenant, kind: str
) -> list[InhabitantEntry]:
    """The rows of `kind`'s list, in display order: characters listed from their
    sheets first (Magi/Companions), then stored entries in the order added."""
    entries: list[InhabitantEntry] = []
    if kind in AUTO_KINDS:
        for character in saga.characters:
            if (
                character_kind(character) == kind
                and character.covenant_id == covenant.id
            ):
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
            InhabitantEntry(kind, record, saga.character(record.character_id))
        )
    return entries


def headcount(entries: list[InhabitantEntry]) -> int:
    """How many people or animals a list stands for: quantities added up, so
    "Servants x2" counts as two, not one."""
    return sum(entry.quantity for entry in entries)


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
    """2 Servants for every 10 points of inhabitants or part of 10,
    excluding Servants, Laborers and Teamsters themselves."""
    points = inhabitant_points(
        saga, covenant, exclude_roles=("Servant", "Laborer", "Teamster")
    )
    return SERVANTS_PER_TEN * round_away_from_zero(points / 10)


def minimum_teamsters(saga: Saga, covenant: Covenant) -> int:
    """1 Teamster for every 10 points of inhabitants (excluding Laborers and
    Teamsters), after subtracting twice the number of Laborers."""
    points = inhabitant_points(saga, covenant, exclude_roles=("Laborer", "Teamster"))
    points -= TEAMSTER_POINTS_PER_LABORER * other_covenfolk_count(
        saga, covenant, "Laborer"
    )
    return round_away_from_zero(max(points, 0) / 10)
