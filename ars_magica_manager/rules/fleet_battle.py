"""Fleet battles: Lords of Men's massed combat (rules.battle) fought at
sea, as Tales of Power pp. 106-110 tells it. There is no new system, only
three changes to the one on land:

* the Deployment Total takes the pilot's Ability in place of Area Lore,
  unless the troupe plays on some feature of the coast (ToP p. 106; the
  Deployment Total itself is Lords of Men p. 104);
* Weight of Numbers counts ships, not combat groups: every ship on both
  sides at first, then only those engaged in each event, since an
  admiral's aim is to beat part of the enemy fleet alone (ToP p. 106);
* battlefield events are played as usual, told at sea; boarding is
  fought much as on land (ToP p. 106).

ToP p. 110 adds bearded ships (iron plates on the bow: armour as well as
reinforcement in collisions, so the ship is more resistant to damage, but
appreciably slower; p. 106 adds ships were bearded to ram better; no figure
is given) and naptha bombs (+5 damage, the
ship set alight, put out by a great deal of sand but not by water).

The Definitive Edition has no fleet battles, and the Errata correct none
of these pages.
"""

from __future__ import annotations

from .rounding import round_down

SOURCE = "Tales of Power pp. 106-110; Lords of Men pp. 104-106"

#: Combatants in a combat group (Lords of Men p. 105).
GROUP_SIZE = 5
#: A naptha bomb's damage bonus (ToP p. 110).
NAPTHA_DAMAGE = 5

#: What an event at sea can be (ToP pp. 106, 110), key -> the words.
FLEET_EVENTS: dict[str, str] = {
    "cut": "Cut off part of their fleet",
    "board": "Board their flagship",
    "mast": "Bring down their mainmast and signals",
    "intercept": "Intercept them with swift ships",
    "other": "Another event at sea",
}
FLEET_EVENT_DEFAULT = "cut"

PILOT_NOTE = (
    "The pilot's Ability takes Area Lore's place, unless a feature of the "
    "coast matters (ToP p. 106)."
)
BEARDED_NOTE = (
    "Bearded: slower, but armoured: more resistant to damage, and it rams "
    "and takes collisions better; the storyguide sets the bonus in an event "
    "(ToP pp. 106, 110 give no figure)."
)
NAPTHA_NOTE = (
    f"Naptha: +{NAPTHA_DAMAGE} damage, and the ship is set alight; water "
    "won't put it out, a great deal of sand will (ToP p. 110)."
)
BOARDING_NOTE = (
    "Boarding is fought much as on land. Events are told at sea: cutting "
    "off part of their fleet, boarding the flagship, bringing down the "
    "mast that flies the signals (ToP pp. 106, 110)."
)


def crew_groups(men: int) -> int:
    """Combat groups of five a fleet's crews make (whole groups only)."""
    return round_down(max(0, men) / GROUP_SIZE)


def deployment_base(intelligence: int, ability: int) -> int:
    """The pilot's Deployment Total before the stress die: Intelligence
    + his seafaring Ability (in place of Area Lore)."""
    return intelligence + ability
