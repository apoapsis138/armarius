"""The Mysteries of Dreams and Hermetic Sacrifice (The Mysteries Revised
Edition, chapters 12-13).

Dream Magic (Minor Hermetic Mystery Virtue, TMRE pp. 102-107):

- A spiritual traveler's spirit enters a dream; his body lies in a trance.
  A physical disturbance to the body calls for a Concentration roll as to
  maintain a spell (p. 102): Stamina + Concentration + stress die against
  the Definitive Edition's distraction Ease Factors less 3 (DE p. 215).
- In a dream every spell is Imaginem: the traveler casts with his
  Technique and Imaginem, whatever the effect's Form, and a requisite Form
  becomes Imaginem and is ignored (p. 103). The aura is the dream
  setting's (a dream cathedral's is Divine); the body's isn't counted.
  Form-based Magic Resistance is Imaginem's, with Parma Magica; Parma
  stretched over body and spirit as two is 3 less (p. 103, DE p. 66).
  His real wounds, Fatigue and possessions stay with the body: spirits
  feel no Fatigue (p. 106), so only dream wounds take from his totals.
- Dream Duration is as Concentration, Dream Target as Individual, and
  Dream is a Mentem Target (pp. 103-104): the spell has Mentem as its Form
  or a requisite, as the Greater Dream Grimoire's Rego Corpus and Rego
  Terram spells do (p. 109). The Muto Mentem guidelines
  (p. 104) bring a spirit into a dream at 15 to 30.
- Dream rituals may be spontaneous, by the Ceremonial Magic rules, with
  dream vis (always Imaginem); real-world vis on the body may be used for
  known Rituals, its duration in real time (p. 103).
- The dreamer notices travelers on Perception + Awareness + stress die
  against 9, and reshapes the dream on Intelligence + stress die + +3 for
  a magus (or similar power), +3 for Dream Magic, +3 for Hermetic Dream
  Interpreter and +1 each for other supernatural abilities of illusion or
  dreams (at most +3), against 9; the total is the change's magnitude
  (p. 105).
- A wound in a dream: Stamina + stress die + modifiers against the total
  Wound Penalty (an Incapacitating wound 9), or the traveler wakes. The
  earlier wounds' penalties apply to the roll, with Virtues and Flaws of
  pain and wounds, and of strong and weak will (p. 106).
- A botch in a dream gains real Warping Points and may bring real Twilight,
  timed in the waking world (p. 106). No experience is gained and no
  laboratory work done in a dream (p. 106).

The Greater Dream Grimoire (Minor Mystery Virtue, needs Dream Magic, pp.
107-110): bodily travel, like crossing into a regio, and the guidelines
for sending bodies and objects into dreams and giving dream objects real
substance.

Hermetic Sacrifice (Minor Hermetic Mystery Virtue, p. 117): a pure,
unblemished beast sacrificed on a pagan deity's altar stands in for 1
(a lamb) to 6 (a lion) pawns of the vis of a Ritual that summons the
deity, cast via the altar. A magically created or altered beast is never
acceptable. Forcing the summoned spirit (Hermetic Synthemata, as the
Errata p. 51 corrects "True Names") spoils the altar.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..models import Character, Wounds
from . import casting, casting_virtues, lab_virtues, penetration, realms, spell_levels
from .breakdown import Breakdown, Line
from .derived import wound_penalty
from .lab import ability_score

SOURCE = "The Mysteries Revised Edition, Dream Magic, pp. 102-107"
SPELLS_SOURCE = "The Mysteries Revised Edition, Dream Magic Spells, pp. 103-104"
DREAMER_SOURCE = (
    "The Mysteries Revised Edition, The Dreamer in Control (Lucid Dreaming), p. 105"
)
WOUND_SOURCE = "The Mysteries Revised Edition, Fatigue and Wounds, p. 106"
CONCENTRATION_SOURCE = (
    "The Mysteries Revised Edition, Spiritual Dream Travel, p. 102; Ars Magica "
    "Definitive Edition, Concentration, p. 215"
)
GREATER_SOURCE = (
    "The Mysteries Revised Edition, The Greater Dream Grimoire, pp. 107-110"
)
SACRIFICE_SOURCE = (
    "The Mysteries Revised Edition, Hermetic Sacrifice, p. 117; Errata p. 51"
)

DREAM_MAGIC = "vf_dream_magic"
GREATER_GRIMOIRE = "vf_the_greater_dream_grimoire"
DREAM_INTERPRETER = "vf_hermetic_dream_interpreter"
HERMETIC_SACRIFICE = "vf_hermetic_sacrifice"
STRONG_WILLED = "vf_strong_willed"
ENDURING_CONSTITUTION = "vf_enduring_constitution"
LOW_TOLERANCE = "vf_low_tolerance"

#: Every spell a spiritual traveler casts in a dream is of this Form.
DREAM_FORM = "Imaginem"
#: The Art a Dream Target spell has as its Form or a requisite.
DREAM_TARGET_FORM = spell_levels.DREAM_TARGET_FORM

AWARE_EASE = 9
RESHAPE_EASE = 9
#: The reshaping roll's bonuses (p. 105).
MAGUS_BONUS = 3
DREAM_MAGIC_BONUS = 3
INTERPRETER_BONUS = 3
OTHER_POWER_BONUS = 1
MOST_OTHER_POWERS = 3
#: A wound in a dream: an Incapacitating one's Ease Factor (p. 106).
INCAPACITATING_EASE = 9
#: Virtues and Flaws on the wound-shock roll: strength of will, and pain
#: (Strong-Willed +3 to will, DE p. 110; Enduring Constitution +3 and Low
#: Tolerance -3 to resist pain, DE pp. 78, 135).
SHOCK_VIRTUES: dict[str, int] = {
    STRONG_WILLED: 3,
    ENDURING_CONSTITUTION: 3,
    LOW_TOLERANCE: -3,
}
#: Distractions to the entranced body: the Definitive Edition's casting Ease
#: Factors less 3, as for maintaining a spell (DE p. 215).
DISTURBANCES: tuple[tuple[str, int], ...] = (
    ("Shaken or jostled", 6),
    ("Yelled at, a sudden noise or flash", 6),
    ("Knocked down", 9),
    ("Hurt this round", 12),
)

#: Muto Mentem (Dream, Mystery) guidelines (p. 104): level -> effect.
MUTO_MENTEM_GUIDELINES: tuple[tuple[int, str], ...] = (
    (15, "change the caster's own dream to include his spirit"),
    (20, "change another's dream to include the caster's spirit"),
    (25, "change a person's dream to include another's spirit"),
    (30, "change a person's dream to include a group of up to ten spirits"),
)
#: The Greater Dream Grimoire's Creo Imaginem guidelines (p. 109): level ->
#: the largest dream object given real substance (a Momentary Ritual cast
#: in the dream by a spiritual traveler, with real-world vis).
SUBSTANCE_GUIDELINES: tuple[tuple[int, int], ...] = (
    (15, -7),
    (20, -5),
    (25, -3),
    (30, -1),
    (35, 1),
)
#: Its Rego Corpus guidelines (p. 108-109): level -> whose body is sent.
BODILY_GUIDELINES: tuple[tuple[int, str], ...] = (
    (35, "send the caster into a dream"),
    (40, "send the body of another into a person's dream"),
    (45, "send the bodies of a group into a person's dream"),
)
#: Rego Terram (p. 109): send an inanimate object through a portal into a
#: dream; Creo (Form) (p. 108): give an object met in a dream substance,
#: cast there by a physical traveler.
SEND_OBJECT_LEVEL = 15
PHYSICAL_SUBSTANCE_LEVEL = 15


def has(character: Character, vf_id: str) -> bool:
    return lab_virtues.has(character, vf_id)


def dream_traveler(character: Character) -> bool:
    """Whether he knows Dream Magic (or the Greater Dream Grimoire, which
    needs it), and so the Mystery spells of dream travel."""
    return has(character, DREAM_MAGIC) or has(character, GREATER_GRIMOIRE)


def dream_target_problem(
    technique: str, form: str, requisites: Sequence[str] = ()
) -> str:
    """Why a Dream Target spell of these Arts can't be ("" when it can):
    Mentem must be its Form or a requisite (pp. 104, 109)."""
    return spell_levels.dream_target_problem(technique, form, requisites)


# -- a spiritual traveler's magic ---------------------------------------------

#: The Casting Score lines that come from the body left behind.
_BODY_LINES = ("Encumbrance", "Wounds", "Fatigue")


def spirit_casting_score(
    magus: Character,
    technique: str,
    form: str,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    dream_wounds: int = 0,
    mastery: int = 0,
    ritual: bool = False,
    spontaneous: bool = False,
) -> Breakdown:
    """A spiritual traveler's Casting Score in a dream: his Technique and
    Imaginem (for an effect of `form`), Stamina, and the dream setting's
    aura, without the body's Encumbrance, wounds and Fatigue; the dream
    wounds' penalty (`dream_wounds`, 0 or less) instead."""
    score = casting.casting_score(
        magus,
        technique,
        DREAM_FORM,
        aura=aura,
        aura_realm=aura_realm,
        mastery=mastery,
        ritual=ritual,
        spontaneous=spontaneous,
    )
    kept: list[Line] = []
    total = score.total
    for line in score.lines:
        if line.label in _BODY_LINES:
            total -= line.amount or 0
            continue
        if line.label == DREAM_FORM and form and form != DREAM_FORM:
            line = Line(f"Imaginem (for {form})", amount=line.amount, source=SOURCE)
        kept.append(line)
    if dream_wounds:
        kept.append(Line("Dream wounds", amount=dream_wounds, source=WOUND_SOURCE))
        total += dream_wounds
    return Breakdown(total=total, lines=kept)


def spirit_resistance(
    magus: Character,
    *,
    aura: int = 0,
    aura_realm: str = realms.HERMETIC,
    split_parma: bool = False,
) -> Breakdown:
    """A spiritual traveler's Magic Resistance in a dream: Imaginem, Parma
    Magica (3 less when stretched over body and spirit as two) and the
    dream setting's aura."""
    return penetration.magic_resistance(
        magus, DREAM_FORM, aura=aura, aura_realm=aura_realm, sharing=split_parma
    )


def body_note(split_parma: bool) -> str:
    """What protects the entranced body while the spirit is away."""
    if split_parma:
        return (
            "The body keeps its Form scores and the stretched Parma Magica "
            "(3 less); it has no conscious resistance and casts nothing."
        )
    return (
        "The body has only its Form scores: the Parma Magica travels with the "
        "spirit, and the body casts nothing."
    )


# -- the dreamer ---------------------------------------------------------------


def awareness_base(dreamer: Character) -> Breakdown:
    """The dreamer's roll to notice travelers, before the stress die:
    Perception + Awareness, against 9."""
    lines = [
        Line(
            "Perception",
            amount=dreamer.characteristics.perception,
            source=DREAMER_SOURCE,
        ),
        Line(
            "Awareness",
            amount=sum(ability_score(dreamer, "Awareness")),
            source=DREAMER_SOURCE,
        ),
    ]
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def reshape_base(
    dreamer: Character, *, magus: bool | None = None, other_powers: int = 0
) -> Breakdown:
    """The dreamer's roll to reshape the dream, before the stress die:
    Intelligence and the bonuses for dream magic (`magus`: a magus or of
    similar power, by default when he is a magus; `other_powers`: other
    supernatural abilities of illusion or dreams), against 9."""
    lines = [
        Line(
            "Intelligence",
            amount=dreamer.characteristics.intelligence,
            source=DREAMER_SOURCE,
        )
    ]
    if dreamer.type == "magus" if magus is None else magus:
        lines.append(Line("A magus", amount=MAGUS_BONUS, source=DREAMER_SOURCE))
    if has(dreamer, DREAM_MAGIC):
        lines.append(
            Line("Dream Magic", amount=DREAM_MAGIC_BONUS, source=DREAMER_SOURCE)
        )
    if has(dreamer, DREAM_INTERPRETER):
        lines.append(
            Line(
                "Hermetic Dream Interpreter",
                amount=INTERPRETER_BONUS,
                source=DREAMER_SOURCE,
            )
        )
    others = max(0, min(other_powers, MOST_OTHER_POWERS))
    if others:
        lines.append(
            Line(
                "Other powers of illusion or dreams",
                amount=others * OTHER_POWER_BONUS,
                source=DREAMER_SOURCE,
            )
        )
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def reshape_magnitude(total: int) -> int:
    """A successful reshaping changes the dream as a dream spell of this
    magnitude would: the rolled total."""
    return max(0, total)


# -- wounds and disturbances ---------------------------------------------------


@dataclass(frozen=True)
class DreamWounds:
    """The wounds a traveler has taken in this dream."""

    light: int = 0
    medium: int = 0
    heavy: int = 0
    incapacitating: bool = False

    def add(self, wound: str) -> DreamWounds:
        """These wounds and one more ("light", "medium", "heavy" or
        "incapacitating")."""
        if wound == "incapacitating":
            return DreamWounds(self.light, self.medium, self.heavy, True)
        counts = {"light": self.light, "medium": self.medium, "heavy": self.heavy}
        if wound not in counts:
            raise ValueError(f"No wound {wound!r}.")
        counts[wound] += 1
        return DreamWounds(**counts, incapacitating=self.incapacitating)


WOUNDS: tuple[str, ...] = ("light", "medium", "heavy", "incapacitating")


def dream_wound_penalty(traveler: Character, wounds: DreamWounds) -> int:
    """The Wound Penalty of these dream wounds (0 or less), made better or
    worse by his Virtues and Flaws as a real one is."""
    return wound_penalty(
        Wounds(light=wounds.light, medium=wounds.medium, heavy=wounds.heavy),
        traveler.virtues_flaws,
        diseases=False,
    )


def shock_ease(traveler: Character, wounds: DreamWounds) -> int:
    """The Ease Factor to stay in the dream once wounded: the total Wound
    Penalty, the new wound's included, or 9 for an Incapacitating wound."""
    if wounds.incapacitating:
        return INCAPACITATING_EASE
    return -dream_wound_penalty(traveler, wounds)


def shock_base(
    traveler: Character, earlier: DreamWounds, modifiers: int = 0
) -> Breakdown:
    """The roll to stay in the dream when wounded, before the stress die:
    Stamina, the earlier dream wounds' penalty, Virtues and Flaws of will
    and pain, and other `modifiers` the troupe allows."""
    lines = [
        Line("Stamina", amount=traveler.characteristics.stamina, source=WOUND_SOURCE)
    ]
    earlier_penalty = dream_wound_penalty(traveler, earlier)
    if earlier_penalty:
        lines.append(
            Line("Earlier dream wounds", amount=earlier_penalty, source=WOUND_SOURCE)
        )
    for vf_id, amount in SHOCK_VIRTUES.items():
        if has(traveler, vf_id):
            name = vf_id.removeprefix("vf_").replace("_", " ").title()
            lines.append(Line(name, amount=amount, source=WOUND_SOURCE))
    if modifiers:
        lines.append(Line("Other modifiers", amount=modifiers, source=WOUND_SOURCE))
    return Breakdown(total=sum(line.amount or 0 for line in lines), lines=lines)


def disturbance_ease(disturbance: str) -> int:
    """The Concentration Ease Factor for a disturbance to the body
    (ValueError for one not on the table)."""
    for name, ease in DISTURBANCES:
        if name == disturbance:
            return ease
    raise ValueError(f"No disturbance {disturbance!r}.")


def disturbance_base(traveler: Character) -> int:
    """The entranced body's Concentration roll before the stress die:
    Stamina + Concentration, with three times the body's Wound Penalty."""
    return casting.concentration_base(traveler)


# -- the Greater Dream Grimoire ------------------------------------------------


def substance_level(size: int, enchantment_levels: int = 0) -> int | None:
    """The lowest Creo Imaginem level that gives a dream object of `size`
    real substance, with the levels of any enchantment it carries added
    (the levels must be added, with Vim and the enchantments' Arts as
    requisites, or the object comes out mundane). None past Size +1, the
    largest guideline."""
    for level, largest in SUBSTANCE_GUIDELINES:
        if size <= largest:
            return level + max(0, enchantment_levels)
    return None


# -- Hermetic Sacrifice --------------------------------------------------------

LEAST_WORTH = 1
MOST_WORTH = 6
#: The book's two marks: an unblemished lamb is worth one pawn, a pure lion
#: six; the rarer, nobler and harder to find, the more.
BEAST_EXAMPLES: tuple[tuple[str, int], ...] = (("a lamb", 1), ("a lion", 6))


def sacrifices(character: Character) -> bool:
    return has(character, HERMETIC_SACRIFICE)


def sacrifice_problem(
    character: Character, worth: int, *, pure: bool, made_by_magic: bool
) -> str:
    """Why the sacrifice can't stand in for vis ("" when it can)."""
    if not sacrifices(character):
        return f"{character.name} doesn't know Hermetic Sacrifice."
    if made_by_magic:
        return (
            "A magically created or altered beast is never acceptable "
            f"({SACRIFICE_SOURCE})."
        )
    if not pure:
        return (
            "The beast must be pure and unblemished, or the deity isn't "
            f"pleased ({SACRIFICE_SOURCE})."
        )
    if not LEAST_WORTH <= worth <= MOST_WORTH:
        return f"A sacrifice stands in for {LEAST_WORTH} to {MOST_WORTH} pawns of vis."
    return ""


def ritual_vis_breakdown(
    magus: Character, level: int, sacrifice_worth: Sequence[int] = ()
) -> Breakdown | None:
    """The pawns a Ritual of `level` takes: one a magnitude, as his Virtues
    change it (Mercurian Magic halves it, Waster of Vis adds a third), less
    what each pure sacrifice in `sacrifice_worth` stands in for (never
    below 0). None when he can't cast a Ritual (Rigid Magic)."""
    pawns = casting.magnitude(level)
    needed = casting_virtues.ritual_vis(magus, pawns)
    if needed is None:
        return None
    lines = [
        Line(
            f"Level {level}: a pawn a magnitude",
            amount=pawns,
            source=casting.SOURCE,
        )
    ]
    if needed != pawns:
        lines.append(
            Line(
                "His Virtues (Mercurian Magic, Waster of Vis)",
                amount=needed - pawns,
                source=casting_virtues.SOURCE,
            )
        )
    left = needed
    for worth in sacrifice_worth:
        used = min(worth, left)
        if used:
            lines.append(Line("Sacrifice", amount=-used, source=SACRIFICE_SOURCE))
            left -= used
    return Breakdown(total=left, lines=lines)
