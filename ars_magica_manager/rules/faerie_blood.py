"""The varieties of Faerie Blood and the charms faeries teach (Realms of
Power: Faerie, Chapter Five, pp. 104-111).

- Each variety of Faerie Blood (or Strong Faerie Blood) has its benefit,
  replaced by a stronger one with the Faerie Legacy Virtue, and typical
  Sympathies (pp. 106-110; the jinni varieties, 'afrit, ghula and jann,
  The Cradle and the Crescent pp. 77-78). The Characteristic and Ability bonuses are
  worked out where those scores are (rules.creation_characteristics,
  rules.scores); the rest are situational, and shown in the Virtue's
  details as the book gives them. A Faerie God's blood may name its
  Olympian ("Faerie God: Zeus"), whose Sympathy Traits it chooses from
  (The Sundered Eagle p. 127).
- A Lesser or Greater Charm Flaw ties a Virtue to a secret charm: the
  Virtue can't be a Social Status Virtue or about the character's
  background, can't affect experience points, must change what he can do
  rather than who he is, and can't be Hermetic, a Mystery or another
  realm's. Revealed, a Lesser Charm must be remade, a Greater one
  recovered (p. 104).
- A folk charm ends a faerie effect when stress die + Intelligence +
  Faerie Lore + aura beats its level, adding the highest applicable
  Sympathy Trait to Penetration; using it costs a Fatigue level and a
  Warping Point (p. 105).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

from ..models import Character, VirtueFlawDef, VirtueFlawInstance
from . import faerie_sympathy
from .scores import ability_level

SOURCE = "Realms of Power: Faerie, Chapter Five: Faerie Blood and Charms, pp. 104-111"

BLOODS_IDS = ("vf_faerie_blood", "vf_strong_faerie_blood")
LEGACY = "vf_faerie_legacy"
CHARMS = ("vf_lesser_charm", "vf_greater_charm")
#: The book spells 'afrit with a turned comma, which a typed name may keep.
LEFT_QUOTE = chr(0x2018)


@dataclass(frozen=True)
class Blood:
    """A variety of Faerie Blood: its benefit, its Legacy benefit (which
    replaces it), its typical Sympathies, and its page."""

    benefit: str
    legacy: str
    sympathies: str
    page: int
    book: str = "RoP: Faerie"


BLOODS: dict[str, Blood] = {
    "bloodcap": Blood(
        "+1 Strength, not above +3",
        "+1 Strength, up to +4",
        "Fear, Winter, Religious Symbols (negative)",
        106,
    ),
    "brownie": Blood(
        "+1 to all totals with a Profession Ability",
        "as Faerie Blood, and +2 with one favored Profession",
        "Tools, Cleaning, Gifts (negative)",
        107,
    ),
    "dwarf": Blood(
        "+1 to all totals with a Craft Ability",
        "as Faerie Blood, and +2 with one favored Craft",
        "Jewelry, Weapons, Theft (negative)",
        107,
    ),
    "ettin": Blood(
        "+1 Stamina, not above +3",
        "+1 Stamina, up to +4",
        "Mountains, Stone, Sunlight (negative)",
        107,
    ),
    "faerie god": Blood(
        "1 point to spend on the ancestor's Sympathy Traits",
        "2 points to spend on the ancestor's Sympathy Traits",
        "anything fitting the ancestor",
        108,
    ),
    "ghul": Blood(
        "retractable claws: Init -1, Atk +2, Dfn +3, Dam +2",
        "large claws: Init -1, Atk +2, Dfn +3, Dam +4",
        "Wastelands, Stalking, Compassion (negative)",
        108,
    ),
    "goblin": Blood(
        "+1 to all totals with stealth",
        "+2 to all totals with stealth",
        "Caves, Mischief, Iron (negative)",
        108,
    ),
    "huldra": Blood(
        "unseen while still and unwatched: Sta + Concentration 9+ every "
        "fifteen minutes; not in a Divine aura",
        "as Faerie Blood, even while watched",
        "Concealment, Fidelity, Secrets (negative)",
        108,
    ),
    "nymph": Blood(
        "+1 Communication, not above +3",
        "+1 Communication, up to +4",
        "Trees, Love, Loyalty (negative)",
        108,
    ),
    "padfoot": Blood(
        "+1 Perception, not above +3",
        "+1 Perception, up to +4",
        "Protection, Hounds, Friendship (negative)",
        109,
    ),
    "satyr": Blood(
        "+1 to Communication and Presence totals with the sexually compatible",
        "+2 to Communication and Presence totals with the sexually compatible",
        "Music, Lust, Politeness (negative)",
        109,
    ),
    "selkie": Blood(
        "+3 to rolls to avoid Deprivation",
        "+3 to avoid Deprivation, and without air a roll each minute, not "
        "each 30 seconds",
        "Shorelines, Birds, Freedom (negative)",
        109,
    ),
    "sidhe": Blood(
        "+1 Presence, not above +3",
        "+1 Presence, up to +4",
        "Light, Nobility, Iron (negative)",
        109,
    ),
    # The jinni varieties of Mythic Arabia (The Cradle and the Crescent
    # pp. 77-78).
    "afrit": Blood(
        "+1 Strength or Intelligence, not above +3",
        "+1 Strength or Intelligence, up to +4",
        "Power, Cruelty, Patience (negative)",
        77,
        "The Cradle and the Crescent",
    ),
    "ghula": Blood(
        "retractable claws: Init -1, Atk +2, Dfn +3, Dam +2",
        "large claws: Init -1, Atk +2, Dfn +3, Dam +4",
        "Wastelands, Stalking, Compassion (negative)",
        77,
        "The Cradle and the Crescent",
    ),
    "jann": Blood(
        "+1 Presence, not above +3",
        "+1 Presence, up to +4",
        "Deserts, Hospitality, Temperance (negative)",
        78,
        "The Cradle and the Crescent",
    ),
    "undine": Blood(
        "+2 to any action under water, partly offsetting the penalty",
        "+2 to any action under water, in place of the penalty",
        "Rivers, Fish, Clothing (negative)",
        110,
    ),
}


#: A Faerie God's blood naming its god: "Faerie God: Zeus".
GOD_PREFIX = "faerie god:"


def blood_of(instance: VirtueFlawInstance) -> Blood | None:
    """The variety a Faerie Blood Virtue names (its "blood"), None if the
    book has none by that name. A Faerie God's blood naming an Olympian
    has that god's Sympathy Traits (The Sundered Eagle p. 127)."""
    if instance.vf_id not in BLOODS_IDS:
        return None
    name = instance.params.get("blood", "").casefold().removesuffix(" blood")
    name = name.strip().replace("'", "").replace(LEFT_QUOTE, "")
    if name.startswith(GOD_PREFIX):
        god = faerie_sympathy.olympian(name.removeprefix(GOD_PREFIX))
        if god is not None:
            return replace(
                BLOODS["faerie god"],
                sympathies=f"{god.text()} (The Sundered Eagle p. 127)",
            )
        name = "faerie god"
    return BLOODS.get(name)


def blood_text(
    instances: Sequence[VirtueFlawInstance], instance: VirtueFlawInstance
) -> str:
    """The variety's benefit, its Legacy one when the character has Faerie
    Legacy, and its Sympathies ("" for a variety the book lacks)."""
    found = blood_of(instance)
    if found is None:
        return ""
    legacy = any(vf.vf_id == LEGACY for vf in instances)
    benefit = f"{found.legacy} (Faerie Legacy)" if legacy else found.benefit
    return f"{benefit}; Sympathies: {found.sympathies} ({found.book} p. {found.page})"


#: Categories a charmed Virtue can't be (p. 104).
UNCHARMED_CATEGORIES = ("Social Status", "Hermetic", "Mystery")


def charm_problem(definition: VirtueFlawDef) -> str:
    """Why a Virtue can't be tied to a charm, or "" when it can, as far as
    its category shows; whether it changes who the character is, or his
    experience, is the storyguide's judgement (p. 104)."""
    if definition.type != "Virtue":
        return "only a Virtue can be charmed"
    categories = (definition.category, *definition.extra_categories)
    bad = [c for c in categories if any(u in c for u in UNCHARMED_CATEGORIES)]
    if bad:
        return f"a {bad[0]} Virtue can't be charmed"
    return ""


CHARM_RULE = (
    "Ties one Virtue to a secret charm: not a Social Status, background, "
    "experience, Hermetic, Mystery or other realm's Virtue, and one that "
    "changes what he can do, not who he is. Revealed, a Lesser Charm must "
    "be remade, a Greater one recovered (RoP: Faerie p. 104)."
)


def folk_charm_total(character: Character, aura: int = 0) -> int:
    """A folk charm's total, before the stress die: Intelligence + Faerie
    Lore + the aura (p. 105)."""
    return (
        character.characteristics.intelligence
        + ability_level(character, "Faerie Lore")
        + aura
    )
