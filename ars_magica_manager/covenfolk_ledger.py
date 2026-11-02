"""The Covenfolk chapter's ledgers, without a front-end: Loyalty's four
figures and what its score means, the situational modifiers, the staffing
the covenant needs, and its household by group, each line with what the
Inspector says about it.

SOURCE: Covenants, Chapter Four: Prevailing Loyalty, pp. 36-41 (the sample
scores, p. 37; situational modifiers, p. 38; familiarity and reputation,
p. 40; crises at -3 or less, p. 41); Ars Magica Definitive Edition,
Covenfolk Categories and Points of Inhabitants, pp. 190-191; Cost Saving and
Magic, pp. 194-195; Emergency Savings, p. 196. The score meanings are
paraphrased, not quoted.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import covenant_diary, goods
from . import economics as eco
from . import inhabitants as inh
from .markup import escape
from .models import INHABITANT_KINDS, LOYALTY_EQUIPMENT, LOYALTY_MONEY, Covenant, Saga
from .rules import covenfolk, living, xp


@dataclass(frozen=True)
class Line:
    """A ledger line: its name, its other cells (markup) and what the
    Inspector shows when it is chosen (markup)."""

    name: str
    cells: tuple[str, ...]
    detail: str


@dataclass(frozen=True)
class Figure:
    """One of Loyalty's four figures: its caption, value and Inspector text."""

    caption: str
    value: str
    detail: str


# -- Loyalty --

#: What each Prevailing Loyalty score means, in paraphrase (Covenants p. 37).
SCORE_MEANINGS: dict[int, str] = {
    -6: "on the verge of revolt, obeying only under threat; productivity halved",
    -4: "unhappy, kept in place by steady work and their own interest",
    -2: "not content, wary of the magi; bribes might turn them",
    0: "moderately content, treating the magi as they would the gentry",
    2: "unusually loyal, close-mouthed about the magi's secrets",
    4: "devoted, treating the magi as family or kindly rulers",
    6: "zealous, going to great lengths for the magi; productivity rises",
}
#: At this score or below the covenant is prone to crises of faithfulness
#: (Covenants p. 41).
CRISIS_SCORE = -3


def meaning_band(score: int) -> int:
    """The sample score nearest to `score` on the side of 0."""
    return int(max(-6, min(6, score)) / 2) * 2


def meaning(score: int) -> str:
    return SCORE_MEANINGS[meaning_band(score)]


def points_to_next(points: int, score: int) -> int:
    """The Loyalty points needed to raise the score by one (scores follow
    the Ability advancement table, Covenants p. 36)."""
    if score >= 0:
        return xp.xp_for_score(score + 1, xp.ABILITY_FACTOR) - points
    return -(xp.xp_for_score(-score, xp.ABILITY_FACTOR) - 1) - points


def meaning_line(saga: Saga, covenant: Covenant) -> str:
    """The line under the four figures: what the score means, how far the
    next one is, and the governance."""
    points = inh.base_loyalty(saga, covenant) + inh.total_modifiers(saga, covenant)
    score = inh.prevailing_loyalty_score(points)
    text = f"{score:+d}: {meaning(score)} (Covenants p. 37)."
    if score <= CRISIS_SCORE:
        text += " Prone to crises of faithfulness (p. 41)."
    text += f" {points_to_next(points, score)} more points reach {score + 1:+d}."
    governance = (
        ", ".join(inh.governance_names(covenant)) or covenant.loyalty.governance
    )
    return text + f" Governance: {governance or 'not set'}."


def figures(saga: Saga, covenant: Covenant) -> list[Figure]:
    """Base Loyalty, Modifiers, Loyalty Points and the Prevailing score."""
    base = inh.base_loyalty(saga, covenant)
    modifiers = inh.total_modifiers(saga, covenant)
    points = base + modifiers
    score = inh.prevailing_loyalty_score(points)
    magi = covenfolk.entries_for_kind(saga, covenant, "magus")
    council = inh.council_companions(saga, covenant)
    members = [
        f"[b]{escape(m.name)}[/]  {escape(m.gift or 'The Gift')} "
        f"{inh.GIFT_LOYALTY_MODIFIERS.get(m.gift, -30):+d}"
        for m in magi
    ] + [f"[b]{escape(c.name)}[/]  on the council, 0" for c in council]
    scores = "\n".join(
        ("[b]" if s == meaning_band(score) else "")
        + f"{s:+d}  {words}"
        + ("[/]" if s == meaning_band(score) else "")
        for s, words in SCORE_MEANINGS.items()
    )
    return [
        Figure(
            "Base Loyalty",
            f"{base:+d}",
            "The average of the council's Gift modifiers: The Gift -30, the "
            "Blatant Gift -105, the Gentle Gift or none 0; a non-magus with a "
            "full vote counts 0 (Covenants pp. 36, 38).\n\n" + "\n".join(members),
        ),
        Figure(
            "Modifiers",
            f"{modifiers:+d}",
            "The situational modifiers, summed. Choose one in the ledger below "
            "for its rule.\n\n"
            + "\n".join(
                f"[b]{ln.name}[/]  {ln.cells[0]}"
                for ln in modifier_lines(saga, covenant)
            ),
        ),
        Figure(
            "Loyalty Points",
            str(points),
            f"Base Loyalty {base:+d} and Modifiers {modifiers:+d}: {points}.\n\n"
            "Points become a score as an Ability's experience does: 5 for +1, "
            "15 for +2, 30 for +3, 50 for +4; negative points a negative score "
            "(Covenants p. 36).",
        ),
        Figure(
            "Prevailing",
            f"{score:+d}",
            f"{points_to_next(points, score)} more points reach {score + 1:+d}.\n\n"
            + scores
            + f"\n\nAt {CRISIS_SCORE} or less, crises of faithfulness come as "
            "stories (Covenants p. 41).",
        ),
    ]


def _options(options: tuple[str, ...], points: dict[str, int], chosen: str) -> str:
    return "\n".join(
        ("[b]" if o == chosen else "")
        + f"{escape(o)}  {points.get(o, 0):+d}"
        + ("[/]" if o == chosen else "")
        for o in options
    )


def _newcomers_text(saga: Saga, covenant: Covenant) -> str:
    new, everyone = inh.newcomers(saga, covenant)
    if not new:
        return ""
    return (
        f"\n\n[b]{new} of {everyone}[/] covenfolk are newcomers still "
        "growing used to the Gift: Recruit and Depart on each list keep when "
        "they came."
    )


def modifier_lines(saga: Saga, covenant: Covenant) -> list[Line]:
    """Each situational modifier, its setting, and its rule."""
    loyalty = covenant.loyalty
    living_points = inh.living_conditions_loyalty(covenant)
    money = f"{escape(loyalty.money)}  ({inh.MONEY_LOYALTY_POINTS.get(loyalty.money, 0):+d})"
    if loyalty.pension:
        money += f" + pension ({inh.PENSION_LOYALTY_POINTS:+d})"
    wages = "\n".join(
        f"{escape(o)}: Wages x{eco.WAGE_MULTIPLIERS.get(o, 1.0):g}"
        for o in LOYALTY_MONEY
    )
    holders = inh.counted_role_holders(saga, covenant)
    specialists = "\n".join(
        f"[b]{escape(e.name)}[/]  {escape(e.role)} {e.role_bonus or 0:+d}"
        for e in holders
    )
    actions = covenant.loyalty.actions_and_events
    return [
        Line(
            "Living Conditions",
            (f"{living.living_text(covenant, magi=False)}  ({living_points:+d})",),
            "10 points for each point of the covenfolk's Living Conditions, from "
            "-20 at -2 to +20 at +2 (Covenants p. 38). It follows the covenant's "
            "season and its Boons and Hooks.",
        ),
        Line(
            "Equipment",
            (f"{escape(loyalty.equipment)}  ({inh.equipment_loyalty(covenant):+d})",),
            "What the covenfolk are given to work and fight with (Covenants p. 38):\n\n"
            + _options(
                LOYALTY_EQUIPMENT, inh.EQUIPMENT_LOYALTY_POINTS, loyalty.equipment
            )
            + "\n\nChange it with Edit on Loyalty.",
        ),
        Line(
            "Money",
            (money,),
            "The covenfolk's wages, and what each level does to Loyalty and to "
            "the Wages the Treasury pays (Covenants p. 38):\n\n"
            + _options(LOYALTY_MONEY, inh.MONEY_LOYALTY_POINTS, loyalty.money)
            + f"\n\n{wages}\n\nA pension for retirees, half Wages until death, "
            f"adds {inh.PENSION_LOYALTY_POINTS:+d}. Change it with Edit on Loyalty.",
        ),
        Line(
            "Specialists",
            (str(inh.specialists_loyalty(saga, covenant)),),
            "Up to three people who deal with the covenfolk for the magi: a turb "
            "captain adds Presence + Leadership, a steward Presence + Profession: "
            "Steward, a chamberlain Presence + Profession: Chamberlain; an "
            "autocrat does two of these and adds both (Covenants p. 37).\n\n"
            + (specialists or "No one holds these roles yet."),
        ),
        Line(
            "Familiarity",
            (str(inh.familiarity(saga, covenant)),),
            f"{inh.FAMILIARITY_PER_YEAR} points a year since the covenant was "
            "founded, at most enough to cancel Base Loyalty (DE p. 186). "
            "Newcomers dilute it by their share of the covenfolk, and grow used "
            f"to the Gift at the same {inh.FAMILIARITY_PER_YEAR} a year from when "
            "they came, so it climbs back (Covenants pp. 37, 40)."
            + _newcomers_text(saga, covenant),
        ),
        Line(
            "Reputation",
            (str(inh.reputation_loyalty(covenant)),),
            "5 points for each point of a Reputation the covenfolk know: added "
            "for a good one, taken off for a bad one (Covenants p. 40).",
        ),
        Line(
            "Actions and events",
            (str(covenant_diary.actions_and_events(covenant)),),
            "What the magi do and what befalls the covenant: rudeness, "
            "punishments, wounds and hardships cost -1 to -15 points; altruism "
            "earns them back, and a year of four feasts adds 1 (Covenants pp. "
            "37-40). The Diary's Loyalty entries count here"
            + (f", with {actions:+d} typed." if actions else "."),
        ),
        Line(
            "Magical Influence",
            (str(loyalty.magical_influence),),
            "Mentem magic that holds the covenfolk loyal: it must be strong and "
            "regular to count, and it warps them (Covenants p. 40).",
        ),
    ]


# -- the household --


def standing(have: int, needed: int) -> str:
    """Met, or a shortfall or an excess, in words (never colour alone)."""
    if have < needed:
        return f"[b $text-error]Shortfall of {needed - have}[/]"
    if have > needed:
        return f"Excess of {have - needed}"
    return "[dim]Met[/]"


def staffing_lines(saga: Saga, covenant: Covenant) -> list[Line]:
    """Teamsters and Servants against what is needed, the Laborers, and the
    devices standing in for servants and teamsters (DE pp. 190-191, 195)."""
    count = covenfolk.other_covenfolk_count
    population = covenant.population
    teamsters, servants = (
        count(saga, covenant, "Teamster"),
        count(saga, covenant, "Servant"),
    )
    laborers = count(saga, covenant, "Laborer")
    need_teamsters = covenfolk.minimum_teamsters(saga, covenant)
    need_servants = covenfolk.minimum_servants(saga, covenant)
    others = covenfolk.inhabitant_points(
        saga, covenant, exclude_roles=("Servant", "Laborer", "Teamster")
    )
    hauled = covenfolk.inhabitant_points(
        saga, covenant, exclude_roles=("Laborer", "Teamster")
    )
    short = (
        "\n\nWith too few, the storyguide decides what goes wrong: overworked "
        "staff, or magi foraging and cooking for themselves (DE p. 196)."
    )
    return [
        Line(
            "Teamsters",
            (str(teamsters), str(need_teamsters), standing(teamsters, need_teamsters)),
            "1 teamster for every 10 points, or part of 10, of everyone but "
            "laborers and teamsters, less 2 points for each laborer (DE p. 191).\n\n"
            f"Here: {hauled} points less {2 * laborers} for laborers; Magic "
            f"Teamsters {population.magic_teamsters}, each standing in for one."
            + (short if teamsters < need_teamsters else ""),
        ),
        Line(
            "Servants",
            (str(servants), str(need_servants), standing(servants, need_servants)),
            "2 servants for every 10 points, or part of 10, of everyone but "
            "laborers, servants and teamsters (DE p. 191).\n\n"
            f"Here: {others} points; Magic Servants {population.magic_servants}, "
            "each standing in for one." + (short if servants < need_servants else ""),
        ),
        Line(
            "Laborers",
            (str(laborers), "-", ""),
            "Each laborer saves a pound of Provisions, at most half of it, and "
            "counts 2 points off the teamsters needed (DE p. 194).",
        ),
        Line(
            "Magic Servants",
            (str(population.magic_servants), "-", ""),
            "Devices that do a servant's work: each lowers the servants needed "
            "by one (DE p. 195). Typed with Edit Miscellaneous.",
        ),
        Line(
            "Magic Teamsters",
            (str(population.magic_teamsters), "-", ""),
            "Devices that do a teamster's work: each lowers the teamsters needed "
            "by one (DE p. 195). Typed with Edit Miscellaneous.",
        ),
    ]


def pounds_per_point(covenant: Covenant) -> float:
    """What a point of inhabitants costs a year: a pound across Buildings,
    Consumables, Provisions and Wages at standard wages, Wages following the
    salary (DE pp. 191-193)."""
    wages = eco.WAGE_MULTIPLIERS.get(covenant.loyalty.money, 1.0)
    return (1 + 2 + 5) / 10 + 2 / 10 * wages


def household_lines(saga: Saga, covenant: Covenant) -> list[Line]:
    """Each group of inhabitants, its people, points and yearly cost, then
    the total (its last line)."""
    rate = pounds_per_point(covenant)
    lines = []
    counted = 0
    for kind in INHABITANT_KINDS:
        entries = covenfolk.entries_for_kind(saga, covenant, kind)
        people = covenfolk.headcount(entries)
        if not people:
            continue
        spring, summer = covenfolk.INHABITANT_POINTS[kind]
        each = covenfolk.kind_points(kind, covenant)
        points = people * each
        counted += points
        names = "\n".join(
            f"[b]{escape(e.name or '(unnamed)')}[/]"
            + (f" x{e.quantity}" if e.quantity != 1 else "")
            for e in entries
        )
        lines.append(
            Line(
                inh.KIND_TITLES[kind],
                (str(people), str(points), f"£{goods.number(round(points * rate, 1))}"),
                f"Each counts {spring} points in a Spring or Winter covenant, "
                f"{summer} in Summer or Autumn (DE p. 190).\n\n{names}",
            )
        )
    others = covenant.population.other_people
    if others:
        each = covenfolk.kind_points("inhabitant", covenant)
        counted += others * each
        lines.append(
            Line(
                "Other People",
                (
                    str(others),
                    str(others * each),
                    f"£{goods.number(round(others * each * rate, 1))}",
                ),
                "People not listed one by one, counted as other covenfolk "
                "(DE p. 190). Typed with Edit Inhabitants.",
            )
        )
    total = covenfolk.inhabitant_points(saga, covenant)
    if total != counted:
        extra = total - counted
        lines.append(
            Line(
                "Regimens and beasts",
                ("", str(extra), f"£{goods.number(round(extra * rate, 1))}"),
                "Points for characters under a physician's regimen (Art & "
                "Academe p. 58) and a menagerie's beasts (Hermetic Projects "
                "p. 123).",
            )
        )
    lines.append(
        Line(
            "Total",
            (
                str(inh.total_inhabitants(saga, covenant)),
                str(total),
                f"£{goods.number(round(total * rate, 1))}",
            ),
            "Buildings, Consumables, Provisions and Wages come to about a pound "
            "a point a year, so a covenant can afford about as many points as "
            "it has pounds of income (DE p. 191).",
        )
    )
    return lines
