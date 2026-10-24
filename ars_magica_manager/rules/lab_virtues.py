"""Virtues and Flaws that change a season of lab work beyond a flat
lab_total modifier, each a function of the plan and the work (rules.
lab_seasons adds their lines to the Lab Total in `_with_options`):

- Plan options, ticked like a Magical Focus: Potent Magic (+3 Minor, +6
  Major, the best one only) in its field; Cyclic Magic, positive (+3 when
  the cycle's good part covers the whole season) or negative (-3 when its
  bad part touches any of it); Environmental Magic Condition (the Lab
  Total halved).
- A Laboratory Horoscope: with Planetary Magic, for enchanting a device;
  with Celestial Magic, any lab work. The magus chooses +1 to +5 and
  must roll Stress die + Intelligence + Artes Liberales (Astronomy with
  Celestial Magic, when the magus has it) against three times it; a botch
  wastes the season.
- Short-Ranged Magic: the Lab Total halved designing a spell or an
  enchanted effect with a Range beyond Touch.
- Disjointed Magic: no bonus for a similar spell known, nor for effects
  already in the device sharing a Technique or Form (rules.lab_seasons,
  rules.enchant_seasons).
- Magical Memory: the magus's own Lab Texts serve wherever they are kept.
  (Having once followed another's text isn't recorded, so that part is
  the troupe's.)
- Hubris (Houses of Hermes: Mystery Cults): its score added to a talisman's
  instilling and to binding a familiar.
- Waster of Vis: a quarter of the pawns used are wasted, so a third more
  are needed; the wasted pawns count toward the season's limit.
- Hermetic Alchemy (The Mysteries): Shape and Material bonuses (up to
  Magic Theory) on extracting vis, and Form vis at a twentieth of a Lab
  Total limited by the Form as a requisite. Extractor of (Form) Vis:
  that Form's vis at a tenth of the same Lab Total.

Halving rounds down (the default); vis extracted rounds up.
"""

from __future__ import annotations

from ..arts import FORMS
from ..models import Book, Character, SeasonPlan
from .breakdown import Line
from .rounding import round_down, round_up

SOURCE = "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, pp. 59-154"
MYSTERIES_SOURCE = "The Mysteries Revised Edition, Chapter 6: Hermetic Astrology"
ALCHEMY_SOURCE = "The Mysteries Revised Edition, Chapter 3: Hermetic Alchemy"
HUBRIS_SOURCE = "Houses of Hermes: Mystery Cults, House Verditius, Hubris"

POTENT = ("vf_potent_magic", "vf_potent_magic_house")
POTENT_MAJOR = ("vf_potent_magic_major", "vf_potent_magic_sign_planet")
CYCLIC_POSITIVE = "vf_cyclic_magic_positive"
CYCLIC_NEGATIVE = "vf_cyclic_magic_negative"
CONDITION = "vf_environmental_magic_condition"
SHORT_RANGED = "vf_short_ranged_magic"
DISJOINTED = "vf_disjointed_magic"
MEMORY = "vf_magical_memory"
WASTER = "vf_waster_of_vis"
HUBRIS = "vf_hubris"
PLANETARY = "vf_planetary_magic"
CELESTIAL = "vf_celestial_magic"
ALCHEMY = "vf_hermetic_alchemy"
EXTRACTOR = "vf_extractor_of_form_vis"

POTENT_BONUS = {"Minor": 3, "Major": 6}
CYCLE_BONUS = 3
HOROSCOPE_MAX = 5
#: Ranges a Short-Ranged magus works at without halving.
NEAR_RANGES = ("", "Personal", "Touch")


def _ids(magus: Character) -> set[str]:
    return {vf.vf_id for vf in magus.virtues_flaws}


def has(magus: Character, vf_id: str) -> bool:
    return vf_id in _ids(magus)


def potent_bonus(magus: Character) -> int:
    """The best Potent Magic the magus has (0 without one)."""
    ids = _ids(magus)
    if ids & set(POTENT_MAJOR):
        return POTENT_BONUS["Major"]
    return POTENT_BONUS["Minor"] if ids & set(POTENT) else 0


def potent_field(magus: Character) -> str:
    """What the magus's Potent Magic covers, for the plan form's label."""
    fields = [
        vf.params.get("field", "")
        for vf in magus.virtues_flaws
        if vf.vf_id in (*POTENT, *POTENT_MAJOR)
    ]
    return ", ".join(f for f in fields if f)


def horoscope_ability(magus: Character) -> str:
    """The Ability a Laboratory Horoscope rolls with."""
    if has(magus, CELESTIAL) and any(a.name == "Astronomy" for a in magus.abilities):
        return "Astronomy"
    return "Artes Liberales"


def horoscope_score(magus: Character) -> int:
    """Intelligence + the horoscope's Ability; Artes Liberales counts as
    astronomy (Academic Concentration, rules.work_virtues)."""
    from . import work_virtues
    from .lab import ability_score

    ability = horoscope_ability(magus)
    score = magus.characteristics.intelligence + sum(ability_score(magus, ability))
    if ability == "Artes Liberales":
        score += sum(n for _, n in work_virtues.artes_liberales(magus, ("astronomy",)))
    return score


def horoscope_applies(magus: Character, activity: str, enchanting: bool) -> bool:
    """Celestial Magic's horoscope serves any lab work; Planetary Magic's only
    making an enchanted device."""
    return has(magus, CELESTIAL) or (has(magus, PLANETARY) and enchanting)


def option_lines(
    magus: Character,
    plan: SeasonPlan,
    *,
    enchanting: bool,
    talisman: bool,
    binding: bool,
    horoscope_score: int,
) -> tuple[list[Line], list[str]]:
    """The flat lines the plan's options and the magus's Virtues add to the
    Lab Total, and notes; `horoscope_score` is Intelligence + the
    horoscope's Ability."""
    lines: list[Line] = []
    notes: list[str] = []
    if plan.potent and potent_bonus(magus):
        lines.append(Line("Potent Magic", amount=potent_bonus(magus), source=SOURCE))
    if plan.cycle_bonus and has(magus, CYCLIC_POSITIVE):
        lines.append(
            Line("Cyclic Magic (its season)", amount=CYCLE_BONUS, source=SOURCE)
        )
    if plan.cycle_penalty and has(magus, CYCLIC_NEGATIVE):
        lines.append(
            Line("Cyclic Magic (its bad time)", amount=-CYCLE_BONUS, source=SOURCE)
        )
    hubris = next((t.score for t in magus.personality_traits if t.name == "Hubris"), 0)
    if has(magus, HUBRIS) and hubris and (talisman or binding):
        lines.append(Line("Hubris", amount=hubris, source=HUBRIS_SOURCE))
    wanted = max(0, min(plan.horoscope, HOROSCOPE_MAX))
    if wanted and horoscope_applies(magus, plan.activity, enchanting):
        needed = 3 * wanted
        die = plan.horoscope_die
        if die is None:
            notes.append(
                f"Laboratory Horoscope +{wanted}: stress die + {horoscope_score} "
                f"(Intelligence + {horoscope_ability(magus)}) against {needed}, "
                "rolled when the season is applied."
            )
        elif die + horoscope_score >= needed:
            lines.append(
                Line(
                    f"Laboratory Horoscope (rolled {die})",
                    amount=wanted,
                    source=MYSTERIES_SOURCE,
                )
            )
        else:
            notes.append(
                f"Laboratory Horoscope +{wanted} failed: {die} + "
                f"{horoscope_score} is below {needed}."
            )
    return lines, notes


def halving_lines(
    magus: Character, plan: SeasonPlan, design_range: str | None
) -> list[Line]:
    """The halvings that apply to this Lab Total: Environmental Magic
    Condition when ticked, Short-Ranged Magic designing beyond Touch."""
    lines: list[Line] = []
    if plan.condition and has(magus, CONDITION):
        lines.append(
            Line("Environmental Magic Condition", multiplier=0.5, source=SOURCE)
        )
    if (
        design_range is not None
        and design_range not in NEAR_RANGES
        and has(magus, SHORT_RANGED)
    ):
        lines.append(
            Line(f"Short-Ranged Magic ({design_range})", multiplier=0.5, source=SOURCE)
        )
    return lines


def halved(total: int, lines: list[Line]) -> int:
    for line in lines:
        if line.multiplier is not None:
            total = round_down(total * line.multiplier)
    return total


def remembers(magus: Character, text: Book) -> bool:
    """Magical Memory: the magus needs no copy at hand of their own Lab Text."""
    return text.author_id == magus.id and has(magus, MEMORY)


# -- vis ---------------------------------------------------------------------


def with_waste(pawns: int) -> int:
    """The pawns a Waster of Vis must use for `pawns` to count: a quarter of
    those used (rounded up) is wasted (12 -> 16, 10 -> 14)."""
    used = pawns
    while used - round_up(used / 4) < pawns:
        used += 1
    return used


def wasted(magus: Character, cost: dict[str, int]) -> dict[str, int]:
    """The extra pawns Waster of Vis loses on top of `cost` ({Art: pawns})."""
    if not has(magus, WASTER):
        return {}
    return {art: with_waste(n) - n for art, n in cost.items() if n}


def extraction_forms(magus: Character) -> list[str]:
    """The Forms the magus can extract vis of besides Vim: any with Hermetic
    Alchemy; one Extractor of (Form) Vis each."""
    if has(magus, ALCHEMY):
        return [f for f in FORMS if f != "Vim"]
    return [
        vf.params.get("form", "").title()
        for vf in magus.virtues_flaws
        if vf.vf_id == EXTRACTOR and vf.params.get("form", "").title() in FORMS
    ]


def form_extraction_divisor(magus: Character, form: str) -> int:
    """Lab Total points per pawn of `form` vis: 10 with its Extractor
    Virtue, else 20 (Hermetic Alchemy's halved yield)."""
    extractor = any(
        vf.vf_id == EXTRACTOR and vf.params.get("form", "").title() == form
        for vf in magus.virtues_flaws
    )
    return 10 if extractor else 20
