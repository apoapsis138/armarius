"""The Rhine Tribunal's ranks of magus (Guardians of the Forests: The
Rhine Tribunal), as plain checks over the characters.

The Rhine classes its magi as journeymen, masters and archmagi, each a
Free Social Status Virtue (pp. 19-20); a magus with no rank Virtue is a
journeyman, as Hermetic Magus is (p. 20).

- A master is made by three marks of approval, each a token from a
  master (or archmage) not of the applicant's covenant or House, the
  three from three different gilds (p. 22); a magus is given none unless
  he is famed for his magical prowess (a Redcap: for his loyal service),
  and few are made within twenty years of their Gauntlet (pp. 23-24). A
  master has a Hermetic Reputation of 2 for it (p. 20). A gild he has
  the Enmity Flaw for is unlikely to sponsor him (p. 20).
- Only a master takes an apprentice: one trained by a journeyman passes
  his Gauntlet as a newly recruited hedge wizard would, never his filius
  (p. 24).
- An archmage is made by defeating one at his own challenge: the
  challenger must, if a Rhine magus, be a master (a magus of another
  Tribunal needn't, as archmagi are found throughout the Order), have
  invented a spell of at least 7th
  magnitude and be famed throughout the Order for a great deed. Each
  archmage sets his contest the first time he is challenged, for life; a
  magus never challenges the same archmage twice, and one whose parens
  is an archmage challenges him first by custom. An archmage who has
  lost seven times is challenged no more, and challenging one who has
  lost six is bad etiquette (p. 24). An archmage has Hermetic
  Reputations of 4 for his deeds and as an Archmage (p. 20).
- At the Rhine's meetings a master wields a retired magus's sigil by
  proxy, an archmage a second (pp. 20, 24, 26), conferred at the rite
  that follows the introduction of the new magi (p. 27).

The Errata (p. 42) makes the Rank of Archmage (p. 24) an insert, as it
is true of the whole Order; it changes no rule. The Definitive Edition
lets any magus train an apprentice and has no ranks (DE p. 30 on
proxies); the Rhine's ranks are its Peripheral Code, kept to its
Tribunal."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, Saga, ScoredTrait, VirtueFlawInstance
from .casting import magnitude
from .creation_magus import gauntlet_age, years_past_gauntlet

SOURCE = (
    "Guardians of the Forests pp. 19-20, 22-24, 26-27; Errata (Ars Magica "
    "5th Edition) p. 42"
)

HERMETIC_MAGUS = "vf_hermetic_magus"
JOURNEYMAN = "vf_journeyman_rhine_tribunal"
MASTER = "vf_master_rhine_tribunal"
ARCHMAGE = "vf_archmage_rhine_tribunal"
#: The ranks, lowest first, as their Virtues.
RANKS = (JOURNEYMAN, MASTER, ARCHMAGE)
RANK_NAMES = {JOURNEYMAN: "Journeyman", MASTER: "Master", ARCHMAGE: "Archmage"}
#: The retired magi's sigils each rank wields by proxy (pp. 20, 26).
RANK_SIGILS = {ARCHMAGE: 2, MASTER: 1}

#: The marks of approval that make a master (p. 22).
MARKS = 3
#: Few masters are made sooner after their Gauntlet (p. 24).
USUAL_YEARS = 20
#: A Redcap's years, as he is made master sooner (p. 24).
REDCAP_YEARS = 15
REDCAP_HOUSE = "house_mercere"
#: The magnitude of spell an archmage's challenger must have invented,
#: and the challenges an archmage may lose (p. 24).
ARCHMAGE_MAGNITUDE = 7
LOSSES = 7

#: The rank Reputations (p. 20): name, score.
MASTER_REPUTATION = ("Master", 2)
ARCHMAGE_REPUTATION = ("Archmage", 4)
DEED_REPUTATION = 4


def rank(character: Character) -> str:
    """The magus's rank, as its Virtue: the highest he holds, a
    journeyman when he holds none ("" for one not a magus)."""
    if character.type != "magus":
        return ""
    held = {vf.vf_id for vf in character.virtues_flaws}
    return next((r for r in reversed(RANKS) if r in held), JOURNEYMAN)


def rank_name(character: Character) -> str:
    """ "Master", or "" for one not a magus."""
    return RANK_NAMES.get(rank(character), "")


def is_master(character: Character) -> bool:
    """A master or an archmage: who may take an apprentice, and give a
    mark of approval."""
    return rank(character) in (MASTER, ARCHMAGE)


def is_archmage(character: Character) -> bool:
    """An archmage: the Rhine's rank Virtue, or, for a magus of another
    Tribunal, whose title the Rhine's ranks don't record, his Hermetic
    Reputation as Archmage."""
    if character.type != "magus":
        return False
    return rank(character) == ARCHMAGE or any(
        r.name == ARCHMAGE_REPUTATION[0] and r.type == "Hermetic"
        for r in character.reputations
    )


def _reputation(character: Character, name: str, score: int) -> None:
    found = next((r for r in character.reputations if r.name == name), None)
    if found is None:
        character.reputations.append(ScoredTrait(name, score, type="Hermetic"))
    elif found.score < score:
        found.score = score


def promote(character: Character, to: str, deed: str = "") -> None:
    """The magus takes the rank `to`: its Virtue replaces Hermetic Magus
    and any lower rank's, and he gains its Reputations (an archmage's
    great deed by name, when given)."""
    replaced = {HERMETIC_MAGUS, *RANKS}
    character.virtues_flaws = [
        vf for vf in character.virtues_flaws if vf.vf_id not in replaced
    ]
    character.virtues_flaws.append(VirtueFlawInstance(to))
    if to == MASTER:
        _reputation(character, *MASTER_REPUTATION)
    elif to == ARCHMAGE:
        _reputation(character, *ARCHMAGE_REPUTATION)
        if deed.strip():
            _reputation(character, deed.strip(), DEED_REPUTATION)


def acclaim(character: Character, deed: str = "") -> None:
    """A magus of another Tribunal made archmage: he gains the title's
    Reputations (and his great deed's), but no Rhine rank Virtue, as the
    ranks are the Rhine's Peripheral Code."""
    _reputation(character, *ARCHMAGE_REPUTATION)
    if deed.strip():
        _reputation(character, deed.strip(), DEED_REPUTATION)


def gauntlet_year(character: Character) -> int | None:
    """The year the magus passed his Gauntlet, from his birth and the age
    he began his apprenticeship; None when his birth isn't known."""
    born = character.background.year_born
    return None if born is None else born + gauntlet_age(character)


def apprentice_problem(master: Character) -> str:
    """Why the magus may not take an apprentice in the Rhine ("" when he
    may): only a master or archmage does (p. 24)."""
    if master.type != "magus" or is_master(master):
        return ""
    return (
        f"{master.name} is a journeyman: only a master takes an apprentice in "
        "the Rhine; one he trains passes his Gauntlet as a recruited hedge "
        "wizard, never his filius (Guardians of the Forests p. 24)."
    )


def apprentices_of(saga: Saga, magus: Character) -> list[Character]:
    """Those not yet magi who name the magus as parens."""
    return [
        c
        for c in saga.characters
        if c is not magus and c.type != "magus" and c.hermetic.parens == magus.name
    ]


# -- the marks of approval --


@dataclass(frozen=True)
class Sponsor:
    """A master giving a mark: who, and the gild he belongs to ("" for
    none)."""

    magus: Character
    gild: str = ""


def mark_problem(applicant: Character, sponsor: Character, given: Sequence[str]) -> str:
    """Why `sponsor` may not give `applicant` a mark ("" when he may):
    the applicant is a journeyman, the sponsor a master not of his
    covenant or House, and not one who has given him a mark already
    (`given`, their ids)."""
    if applicant.type != "magus":
        return f"{applicant.name} is not a magus."
    if is_master(applicant):
        return f"{applicant.name} is already a {rank_name(applicant).lower()}."
    if sponsor.id == applicant.id:
        return "A magus doesn't give himself a mark of approval."
    if not is_master(sponsor):
        return (
            f"{sponsor.name} is a journeyman: only masters give marks of "
            "approval (Guardians of the Forests p. 22)."
        )
    if sponsor.id in given:
        return f"{sponsor.name} has given {applicant.name} a mark already."
    if applicant.covenant_id and sponsor.covenant_id == applicant.covenant_id:
        return (
            f"{sponsor.name} is of {applicant.name}'s covenant: a mark comes "
            "from another covenant (p. 22)."
        )
    house = applicant.hermetic.house
    if house and sponsor.hermetic.house == house:
        return (
            f"{sponsor.name} is of {applicant.name}'s House: a mark comes from "
            "another House (p. 22)."
        )
    return ""


def mark_warnings(
    saga: Saga,
    applicant: Character,
    sponsors: Sequence[Sponsor],
    enmities: Sequence[str] = (),
) -> list[str]:
    """What the custom frowns on in the marks `sponsors` give: gilds
    shared, a gild he has the Enmity Flaw for (`enmities`, gild names), a
    master made early, and no Reputation to be famed for."""
    found = []
    gilds = [s.gild for s in sponsors if s.gild]
    if len(set(gilds)) < len(gilds):
        found.append("The three marks should come from three different gilds (p. 22).")
    for sponsor in sponsors:
        if sponsor.gild and sponsor.gild in enmities:
            found.append(
                f"{applicant.name} has the Enmity of the {sponsor.gild}: its "
                f"magi are unlikely to sponsor him (p. 20)."
            )
    redcap = applicant.hermetic.house == REDCAP_HOUSE
    years = years_past_gauntlet(saga, applicant)
    usual = REDCAP_YEARS if redcap else USUAL_YEARS
    if applicant.background.year_born is not None and years < usual:
        found.append(
            f"{years} years past his Gauntlet: few are made master within "
            f"{usual} (p. 24)."
        )
    if not any(r.type == "Hermetic" for r in applicant.reputations):
        famed = "loyal service to the Order" if redcap else "his magical prowess"
        found.append(
            f"No Hermetic Reputation recorded: no master gives a mark to a "
            f"magus not famed for {famed} (pp. 23-24)."
        )
    return found


# -- the archmage's challenge --


def invented_magnitude(character: Character) -> int:
    """The greatest magnitude of the spells the magus invented (0 for
    none recorded)."""
    levels = [s.level for s in character.invented_spells if s.level is not None]
    return max((magnitude(level) for level in levels), default=0)


@dataclass(frozen=True)
class Bout:
    """One challenge an archmage met: who challenged him, and whether the
    challenger won."""

    challenger_id: str
    won: bool


def losses(bouts: Sequence[Bout]) -> int:
    return sum(b.won for b in bouts)


def challenge_problem(
    challenger: Character,
    archmage: Character,
    bouts: Sequence[Bout],
    rhine_magus: bool = True,
) -> str:
    """Why `challenger` may not challenge `archmage` ("" when he may):
    he is not yet an archmage, a master if he is a Rhine magus
    (`rhine_magus`; one of another Tribunal needn't be), who never
    challenged this one, and the archmage has lost fewer than seven times
    (p. 24)."""
    if challenger.id == archmage.id:
        return "An archmage isn't challenged by himself."
    if not is_archmage(archmage):
        return f"{archmage.name} is not an archmage."
    if is_archmage(challenger):
        return f"{challenger.name} is already an archmage."
    if rhine_magus and not is_master(challenger):
        return (
            f"{challenger.name} is a journeyman: a Rhine magus must be a master "
            "to challenge an archmage (p. 24)."
        )
    if any(b.challenger_id == challenger.id for b in bouts):
        return (
            f"{challenger.name} has challenged {archmage.name} before: no magus "
            "challenges the same archmage twice (p. 24)."
        )
    if losses(bouts) >= LOSSES:
        return (
            f"{archmage.name} has lost {LOSSES} challenges and may be "
            "challenged no more (p. 24)."
        )
    return ""


def challenge_warnings(
    saga: Saga,
    challenger: Character,
    archmage: Character,
    bouts: Sequence[Bout],
    challenged: Sequence[str] = (),
) -> list[str]:
    """What custom frowns on: challenging an archmage who has lost six,
    or another before one's own archmage parens (`challenged`: the ids
    of the archmagi the challenger has challenged before), and no spell
    of 7th magnitude recorded among those he invented."""
    found = []
    if losses(bouts) == LOSSES - 1:
        found.append(
            f"{archmage.name} has lost six: challenging him is bad etiquette, "
            "as a seventh loss makes his title honorary (p. 24)."
        )
    parens = next(
        (c for c in saga.characters if c.name == challenger.hermetic.parens), None
    )
    if (
        parens is not None
        and parens.id != archmage.id
        and is_archmage(parens)
        and parens.id not in challenged
    ):
        found.append(
            f"His parens {parens.name} is an archmage: by custom he is "
            "challenged first (p. 24)."
        )
    if invented_magnitude(challenger) < ARCHMAGE_MAGNITUDE:
        found.append(
            f"No spell of {ARCHMAGE_MAGNITUDE}th magnitude is recorded among "
            f"those {challenger.name} invented (p. 24)."
        )
    return found
