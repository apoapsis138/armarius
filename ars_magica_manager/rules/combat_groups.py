"""Combat groups and the DE's combat options (DE pp. 395-398).

A group (Composite: its figures come from its members) is one to six
characters of comparable ability: every combat total of its best member
within five points of its worst, when it forms. Its totals are its
vanguard's. A trained group (a season improving combat skills together)
has a leader too, coordinating at most his Leadership in fighters (more,
and it fights as an untrained group); the other members' Combat Abilities,
together at most three times his Leadership, add to the group's Attack or
its Defence, one of the two each round.

A group's hit lands once for each member, the blows spread as evenly as
can be over the other group, the vanguard taking at least as many as
anyone. Only the vanguard's wounds lower the group's totals.

Options: Exertion spends a Fatigue level for the Combat Ability on one
Attack or a round's Defence (in a group, everyone's level, the vanguard's
Ability); disengaging is a Defence Total against every attacker of the
last round, +3 for each try after the first; a scuffle turns a wound
into Fatigue (the table), -3 to Attack and no weapon Damage with a real
weapon; a grapple holds with the Attack Advantage as its strength;
special effects need an Attack Advantage (disarm 9, trip 3, grab a worn
item 6, take the weapon in use 12).

No screen forms groups yet: these are the rules for one still to come, and
only the tests call them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..models import Character, Possession
from . import combat
from .breakdown import Breakdown
from .lab import ability_score

SOURCE = "Ars Magica Definitive Edition, Chapter 11: Obstacles, Groups and Combat Options, pp. 395-398"
MOST_MEMBERS = 6
#: Every combat total of a group's members within this many points.
SPREAD = 5
BONUS_PER_LEADERSHIP = 3
DISENGAGE_STEP = 3
SCUFFLE_WEAPON_PENALTY = -3
#: A scuffle's effect for each wound a blow would have done: (Fatigue
#: levels, the wound it does as well or "").
SCUFFLE_EFFECTS: dict[str, tuple[int, str]] = {
    "light": (1, ""),
    "medium": (2, ""),
    "heavy": (2, "light"),
    "incapacitating": (3, "light"),
    "dead": (5, "medium"),
}
#: The Attack Advantage a special effect needs.
SPECIAL_EFFECTS: dict[str, int] = {
    "Disarm": 9,
    "Trip": 3,
    "Grab worn item": 6,
    "Take the weapon your opponent is using": 12,
}


@dataclass
class Member:
    """One fighter and the weapon he fights with."""

    character: Character
    weapon: Possession

    def totals(self) -> combat.CombatTotals:
        return combat.combat_totals(self.character, self.weapon)

    def skill(self) -> int:
        ability = combat.weapon_ability(self.weapon)
        return sum(ability_score(self.character, ability)) if ability else 0


@dataclass
class CombatGroup:
    """A group of fighters: its vanguard (members[0] unless named), and a
    leader when it trained together."""

    members: list[Member] = field(default_factory=list)
    vanguard: int = 0
    leader: int | None = None
    trained: bool = False

    def figures(self) -> dict[str, int | None]:
        """The vanguard's combat totals."""
        return _figures(self.members[self.vanguard].totals())

    def coordinated(self) -> bool:
        """A trained group its leader can coordinate (his Leadership in
        fighters at most)."""
        if not self.trained or self.leader is None:
            return False
        lead = sum(ability_score(self.members[self.leader].character, "Leadership"))
        return len(self.members) <= lead

    def bonus(self) -> int:
        """A coordinated group's bonus to Attack or Defence: the other
        members' Combat Abilities, at most three times the leader's
        Leadership."""
        if not self.coordinated() or self.leader is None:
            return 0
        lead = sum(ability_score(self.members[self.leader].character, "Leadership"))
        others = sum(
            m.skill() for i, m in enumerate(self.members) if i != self.vanguard
        )
        return min(others, BONUS_PER_LEADERSHIP * lead)


def _figures(totals: combat.CombatTotals) -> dict[str, int | None]:
    def whole(breakdown: Breakdown | None) -> int | None:
        return None if breakdown is None else int(breakdown.total)

    return {
        "initiative": whole(totals.initiative),
        "attack": whole(totals.attack),
        "defence": whole(totals.defence),
        "damage": whole(totals.damage),
    }


def problems(group: CombatGroup) -> list[str]:
    """Why these fighters can't form a group (none: they can)."""
    found: list[str] = []
    count = len(group.members)
    if not 1 <= count <= MOST_MEMBERS:
        found.append(f"A group has one to {MOST_MEMBERS} members, not {count}.")
        return found
    figures = [_figures(m.totals()) for m in group.members]
    for name in ("initiative", "attack", "defence", "damage"):
        values = [v for f in figures if (v := f[name]) is not None]
        if values and max(values) - min(values) > SPREAD:
            found.append(
                f"Their {name.title()} totals run {min(values)} to {max(values)}: "
                f"a group's are within {SPREAD} points."
            )
    if group.trained and group.leader is not None and not group.coordinated():
        lead = sum(ability_score(group.members[group.leader].character, "Leadership"))
        found.append(
            f"Leadership {lead} coordinates {lead} fighter(s): with {count}, it "
            "fights as an untrained group."
        )
    return found


def blows(attackers: int, defenders: int) -> list[int]:
    """How a group's hits spread over a group of `defenders`: as evenly as
    can be, the vanguard (first) taking at least as many as anyone."""
    if defenders <= 0:
        return []
    each, extra = divmod(max(0, attackers), defenders)
    return [each + (1 if i < extra else 0) for i in range(defenders)]


def scuffle(wound: str) -> tuple[int, str]:
    """A scuffle's Fatigue levels and wound for the wound a blow would do."""
    return SCUFFLE_EFFECTS.get(wound, (0, ""))


def disengage_bonus(attempt: int) -> int:
    """+3 for each try to disengage after the first (reset by attacking)."""
    return DISENGAGE_STEP * max(0, attempt - 1)


def exertion(members: Sequence[Member]) -> int:
    """What Exertion adds: the (vanguard's) Combat Ability."""
    return members[0].skill() if members else 0
