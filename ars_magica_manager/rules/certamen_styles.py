"""The schools of certamen (HoH: True Lineages pp. 135-139), as data.

At the start of a certamen each duelist chooses to fight as a follower of
his own school, with its strongest techniques but no change of school
between rounds, or "in the style of" various schools, with weaker
imitations he may swap at the start of any round, before Attack and
Defence are rolled. A magus belongs to the school he was trained in; one
untrained in apprenticeship joins a school by a season's study with a
skilled member, and a season with a member of another school teaches
its imitation (p. 135).

Each style is a row of what it changes; `certamen.styled_totals` and
`certamen.traded` add them to the Definitive Edition's totals (DE pp.
231-233), which stay the rules of the Gladiator school. Most styles
trade between two totals each round, up to a multiple of the duelist's
Finesse: a `Trade` row. The rest act when the duelist lands a blow and
declines to do damage (`forgo`), or change the Fatigue a hit costs.
"""

from __future__ import annotations

from dataclasses import dataclass

SOURCE = "Houses of Hermes: True Lineages, Styles of Certamen, pp. 135-139"

#: The totals a style's trade moves.
INITIATIVE, ATTACK, DEFENCE, RESISTANCE = (
    "initiative",
    "attack",
    "defence",
    "resistance",
)
#: The Attack Advantage of the next three rounds (the Retiarius' cost).
ADVANTAGE = "attack advantage"


@dataclass(frozen=True)
class Trade:
    """A round's trade: the duelist picks up to `up_to` x his Finesse
    points; `gain` rises by `gain_per` per point, and `cost` falls by
    `cost_per` per point. A blank `gain` is a cost paid for what the
    style's `forgo` gives (the Laquerius' noose)."""

    up_to: int
    gain: str
    gain_per: int
    cost: str
    cost_per: int


@dataclass(frozen=True)
class StyleRule:
    """What one way of fighting in a style does: as a follower of the
    school, or in its style."""

    summary: str
    trade: Trade | None = None
    #: The trade's gain lasts the rest of the duel, not only the round.
    lasting: bool = False
    #: Defence bonus, x Finesse, in a round the duelist declines to attack.
    hold_back: int = 0
    #: The most Fatigue levels one hit can cost.
    max_fatigue: int | None = None
    #: Weakening - Resistance is divided by this, not 5, on the hit after a
    #: round the duelist didn't attack (the Scissor).
    divisor_after_skip: int | None = None
    #: Declining damage after a hit takes Finesse // this from the foe's
    #: Resistance (the Velitus); `below_zero` lets it go negative.
    resistance_cut: int | None = None
    below_zero: bool = False
    #: What landing a blow and declining to do damage does instead.
    forgo: str = ""
    #: The Ease Factor of the foe's roll against it, when there is one.
    forgo_target: int | None = None


@dataclass(frozen=True)
class CertamenStyle:
    id: str
    name: str
    school: str
    page: int
    follower: StyleRule | None
    dabbler: StyleRule | None
    #: Whether a magus can belong to it: Charon is a trick, and Bone-
    #: biting's followers died in the Schism (p. 136).
    joinable: bool = True
    #: The Houses whose members alone may use it ("" for any).
    house: str = ""

    def rule(self, follower: bool) -> StyleRule | None:
        """The rule for fighting as its follower, or in its style."""
        return self.follower if follower else self.dabbler


_GLADIATOR = StyleRule(
    "The basic rules: the Founder Tremere's balanced, simple style (p. 135)."
)

STYLES: tuple[CertamenStyle, ...] = (
    CertamenStyle(
        "gladiator", "Gladiator", "School of the Swordsman", 135, _GLADIATOR, None
    ),
    CertamenStyle(
        "andabatus",
        "Andabatus",
        "School of Blind Fighting",
        136,
        StyleRule(
            "Attack up to twice Finesse, the same off Defence.",
            trade=Trade(2, ATTACK, 1, DEFENCE, 1),
        ),
        StyleRule(
            "Attack up to Finesse, twice that off Defence.",
            trade=Trade(1, ATTACK, 1, DEFENCE, 2),
        ),
    ),
    CertamenStyle(
        "bestiarius",
        "Bestiarius",
        "School of Beasts",
        136,
        StyleRule(
            "Heartbeast for Finesse in Muto duels; twice Heartbeast to "
            "Resistance in Muto Corpus or Muto Animal."
        ),
        StyleRule("Heartbeast to Resistance in any duel."),
        house="house_bjornaer",
    ),
    CertamenStyle(
        "bone_biting",
        "Bone-biting",
        "bone-biting technique",
        136,
        None,
        StyleRule(
            "Takes a Body level of damage, then ignores the next two Fatigue "
            "levels lost or adds 10 to his next Attack Total."
        ),
        joinable=False,
    ),
    CertamenStyle(
        "charon",
        "Charon",
        "trick of Charon",
        136,
        None,
        StyleRule(
            "Casts a spell silently and still in an earlier round (Int + "
            "Concentration 15+) and keeps it (12+ each round) until the round "
            "he declares the last; if right, it reaches the loser with the "
            "victor's spell. Likely a breach of the Peripheral Code."
        ),
        joinable=False,
    ),
    CertamenStyle(
        "essedarius",
        "Essedarius",
        "Charioteers",
        136,
        StyleRule(
            "After a hit, may frighten the foe instead of weakening him.",
            forgo="the foe surrenders unless he passes a Brave check of 3 + 2 "
            "per Fatigue level declined this certamen",
            forgo_target=3,
        ),
        StyleRule(
            "After a hit, may frighten the foe instead of weakening him.",
            forgo="the foe surrenders unless he passes a Brave check of 3 + 2 "
            "per Fatigue level declined this round",
            forgo_target=3,
        ),
    ),
    CertamenStyle(
        "gladiatrix",
        "Gladiatrix",
        "School of the Swordswoman",
        136,
        StyleRule(
            "Fights across a phantasmal chessboard.",
            forgo="strikes a piece standing for the foe's idea or value: unless "
            "he makes an Intelligence roll of 9+, a Gladiatrix watching reads "
            "his feelings about it",
            forgo_target=9,
        ),
        StyleRule(
            "The chessboard's spectacle, without reading the foe; any "
            "Gladiator may fight so untrained (p. 137)."
        ),
    ),
    CertamenStyle(
        "hoplomachus",
        "Hoplomachus",
        "Hoplites",
        137,
        StyleRule(
            "Never wins initiative except against a hoplomachus; takes up to "
            "Finesse off Attack for twice that on Defence, or three times "
            "Finesse on Defence in a round he doesn't attack.",
            trade=Trade(1, DEFENCE, 2, ATTACK, 1),
            hold_back=3,
        ),
        StyleRule(
            "Twice Finesse on Defence in a round he doesn't attack.",
            hold_back=2,
        ),
    ),
    CertamenStyle(
        "laquerius",
        "Laquerius",
        "School of the Noose",
        137,
        StyleRule(
            "Takes up to Finesse off his Defence for a noose.",
            trade=Trade(1, "", 0, DEFENCE, 1),
            forgo="the foe's Defence falls by the noose's penalty for the rest "
            "of the duel",
        ),
        StyleRule(
            "Takes up to Finesse off his Defence for a noose.",
            trade=Trade(1, "", 0, DEFENCE, 1),
            forgo="the foe's Defence falls by the noose's penalty for one round",
        ),
    ),
    CertamenStyle(
        "provocator",
        "Provocator",
        "School of Challengers",
        138,
        StyleRule(
            "Takes up to Finesse off Initiative for as much on Resistance in "
            "every later round.",
            trade=Trade(1, RESISTANCE, 1, INITIATIVE, 1),
            lasting=True,
        ),
        StyleRule(
            "Only with the initiative: gives it up for a round, with Finesse "
            "on Resistance, and takes it back the round after."
        ),
    ),
    CertamenStyle(
        "pumilius",
        "Pumilius",
        "School of the (Amusing) Dwarfs",
        138,
        StyleRule(
            "After a hit, may amuse the foe instead of weakening him.",
            forgo="unless the foe makes Int + Concentration 12+ (up to 3 more "
            "if the pumilius has learned what he finds funny; personality "
            "traits apply), he loses his attack or his defence next round",
            forgo_target=12,
        ),
        StyleRule(
            "After a hit, may amuse the foe instead of weakening him.",
            forgo="unless the foe makes Int + Concentration 9+ (personality "
            "traits apply), he loses his attack or his defence next round",
            forgo_target=9,
        ),
    ),
    CertamenStyle(
        "retiarius",
        "Retiarius",
        "School of the Fisherman",
        138,
        StyleRule(
            "Up to Finesse on Initiative, twice that off his Attack Advantage "
            "in each of the next three rounds.",
            trade=Trade(1, INITIATIVE, 1, ADVANTAGE, 2),
            forgo="he takes the initiative",
        ),
        StyleRule(
            "After a hit, may force a fresh initiative roll.",
            forgo="initiative is rolled again",
        ),
    ),
    CertamenStyle(
        "saggitarius",
        "Saggitarius",
        "Technique of the Archer",
        138,
        StyleRule(
            "Up to three times Finesse on Attack, as much off Defence; a hit "
            "never costs more than one Fatigue level.",
            trade=Trade(3, ATTACK, 1, DEFENCE, 1),
            max_fatigue=1,
        ),
        StyleRule(
            "Up to three times Finesse on Attack, as much off Defence; a hit "
            "never costs more than one Fatigue level.",
            trade=Trade(3, ATTACK, 1, DEFENCE, 1),
            max_fatigue=1,
        ),
    ),
    CertamenStyle(
        "scissor",
        "Scissor",
        "School of Carvers",
        138,
        StyleRule(
            "Skips an attack; a hit the round after costs (Weakening - "
            "Resistance) / 3 Fatigue levels.",
            divisor_after_skip=3,
        ),
        StyleRule(
            "Skips an attack; a hit the round after costs (Weakening - "
            "Resistance) / 4 Fatigue levels.",
            divisor_after_skip=4,
        ),
    ),
    CertamenStyle(
        "velitus",
        "Velitus",
        "Style of the Spear",
        138,
        StyleRule(
            "After a hit, may wear down the foe's Resistance instead.",
            resistance_cut=2,
            below_zero=True,
            forgo="the foe's Resistance falls by half the velitus's Finesse, "
            "and may go below zero",
        ),
        StyleRule(
            "After a hit, may wear down the foe's Resistance instead.",
            resistance_cut=3,
            forgo="the foe's Resistance falls by a third of his Finesse, to no "
            "less than zero",
        ),
    ),
)

BY_ID = {style.id: style for style in STYLES}
#: The schools a magus can belong to, for the Hermetic Background form.
SCHOOLS = tuple(style for style in STYLES if style.joinable)


def style(style_id: str) -> CertamenStyle:
    """The style with this id; LookupError for one the catalog lacks."""
    try:
        return BY_ID[style_id]
    except KeyError:
        raise LookupError(f"No certamen style {style_id!r}") from None


def essedarius_target(levels_declined: int) -> int:
    """The Brave check a frightened foe must pass: 3 + 2 per Fatigue level
    the essedarius has declined to inflict (p. 136)."""
    return 3 + 2 * max(0, levels_declined)
