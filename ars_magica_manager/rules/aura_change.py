"""How a place's aura changes from year to year, with the saga's "Auras
change" option on: one strategy for each realm that has a rule.

- **Magic** (Realms of Power: Magic pp. 7-12). A base aura comes from its
  tethers: natural ones (1 or 2 each) add up to at most 5; preternatural
  ones (1 to 5) give the strongest plus 1 for each other, at most 5; the
  two scores add. Each year a modifier sums: +3 x (base - current aura),
  +2 / +1 / -6 / -2 for a stronger Magic / Faerie / Divine / Infernal aura
  impinging on it, +1 / +2 / +3 for the magic a Spring / Summer / Autumn or
  Winter covenant works there, +1 for each spending of 3 or more pawns of
  vis in study, casting or certamen, -1 for each season of vis extraction,
  and +/-1 for each magical botch of 2 or more Warping Points; it can't pass
  +9 or -9. From -3 to +3 nothing happens. At +4 or more a stress die plus
  the modifier goes on the Strengthening table; at -4 or less, plus the
  modifier without its sign, on the Weakening table. Those rolls start with
  no botch dice: each roll of 9 or more adds one for later years, a year
  with no roll takes one away. A botch makes (or removes) a regio level.
- **Infernal** (Realms of Power: The Infernal pp. 10-12). An Infernal aura
  inside a stronger aura of another realm erodes by 1 after as many years as
  its strength, unless something keeps it (a demon there, an Infernal
  enchantment, a corruption roll at the maintaining Ease Factor). A
  corruption roll, stress die + the Infernal aura (while it is the weaker),
  against 3 + the stronger aura keeps it; against 6 + that aura raises it
  by 1.

- **Faerie** (Realms of Power: Faerie pp. 14-16). The aura is the
  glamour of the faerie that claims the place: its Faerie Might / 5; 2 +
  the higher Might / 5 (at most 9) while a second faerie contests it; a
  steward's Might / 5 while the presiding faerie is away. Each season of
  vis extraction the faerie can't prevent (no bargain with it) lowers it
  by 1 until the faerie gets redress. A traveling faerie takes its aura
  with it.

Each strategy answers `year(saga, place, year, rng)` with an AuraYear (or
None): the year's reckoning, the place's details to set, and a line for
the place's Diary. The Winter world turn asks it and the storyguide ticks
what to apply. Divine auras keep their own rule (the Dominion growth
option, churches.py).

Kept in the place's details: "tethers" (the place's own text: each tether
counts once it ends with "(natural 2)" or "(preternatural 4)"),
"impinging_<realm>" (whether a stronger aura of that realm impinges on
it), "aura_adjust" (this
year's botches and anything else, typed), "aura_latent" (+3 or -3 carried
from a 9), "aura_botch_dice"; for an Infernal aura "around" and
"around_realm" (the stronger aura it sits in), "maintained" and
"eroding_since" (the year its erosion clock started); for a Faerie aura
"presiding", "contesting" and "steward" (creature ids), "presiding_away",
"vis_bargain" and "glamour_lost" (the points extraction has cost it). Older saves' "raising"
reads as the typed adjustment and "focus_gone" as the erosion clock.

Pattern: Strategy, one per realm, kept in a dict the way the activity
registry keeps activities.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Protocol, TypedDict

from ..models import Creature, Neighbour, Saga
from . import activities, dice, lab_seasons, options, sites, study
from .rounding import round_down

MAGIC_SOURCE = "Realms of Power: Magic, Chapter Two: Magic Auras, pp. 7-12"
INFERNAL_SOURCE = (
    "Realms of Power: The Infernal, Chapter One: Infernal Auras in Play, pp. 10-12"
)
FAERIE_SOURCE = "Realms of Power: Faerie, Chapter One: Faerie Auras, pp. 14-16"
SOURCE = f"{MAGIC_SOURCE}; {INFERNAL_SOURCE}; {FAERIE_SOURCE}"

#: The saga option that turns this on (rules.options).
OPTION = "aura_change"

NATURAL, PRETERNATURAL = "natural", "preternatural"
TETHER_KINDS = (NATURAL, PRETERNATURAL)
TETHER_LIMIT = 5  # each kind's share of the base aura

#: What a stronger aura of each realm impinging on a Magic aura adds.
IMPINGING: dict[str, int] = {"Magic": 2, "Faerie": 1, "Divine": -6, "Infernal": -2}
#: What a covenant's magic adds, by its season.
ACTIVITY: dict[str, int] = {"Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 3}
MODIFIER_LIMIT = 9
STABLE = 3  # a modifier from -3 to +3 changes nothing
LATENT = 3
VIS_SPENT = 3  # pawns in one spending that count

STRENGTHENING = "Strengthening"
WEAKENING = "Weakening"

#: (lowest total, what happens) for each table, highest first; a botch and
#: 21+ are handled apart.
_TABLES: dict[str, tuple[tuple[int, str], ...]] = {
    STRENGTHENING: (
        (15, "The aura's score rises by 1 for good."),
        (14, "The aura expands by several yards, for good."),
        (
            13,
            "Patches of stronger aura (+1) appear, such as one chamber; mundane "
            "residents there gain a Warping Point.",
        ),
        (12, "1 to 3 pawns of vis manifest in the aura (the vis is real and stays)."),
        (11, "The aura is 1 stronger for one season."),
        (
            10,
            "Minor magical effects appear on their own (a Warping Point to "
            "anyone they touch); spontaneous casting totals get up to +3.",
        ),
        (9, "Latent strengthening: +3 to next year's modifier."),
        (7, "Signs of the aura strengthening are noticed."),
        (0, "No change."),
    ),
    WEAKENING: (
        (15, "The aura's score falls by 1 for good."),
        (14, "The aura contracts by several yards, for good."),
        (13, "Patches of weaker aura (-1) appear, such as at its edge."),
        (12, "1 to 3 pawns of vis in the aura lose their power."),
        (11, "The aura is 1 weaker for one season."),
        (10, "Spontaneous magic is stifled: up to -3 to its casting totals."),
        (9, "Latent weakening: -3 from next year's modifier."),
        (7, "Signs of the aura weakening are noticed."),
        (0, "No change."),
    ),
}
_BOTCH: dict[str, str] = {
    STRENGTHENING: (
        "Botch: a regio level appears. With no regio the place becomes one, "
        "a mundane level below a top level at the aura's score; otherwise a "
        "new level appears. Everyone present gains 3 Warping Points."
    ),
    WEAKENING: (
        "Botch: a regio level disappears (3 Warping Points to everyone on it). "
        "With no regio, a new one arises and everything retreats into its "
        "magical level, leaving the mundane level deserted (3 Warping Points to "
        "everyone present)."
    ),
}


class Tether(TypedDict, total=False):
    """Something a Magic aura gathers around."""

    name: str
    kind: str
    score: int


@dataclass
class AuraYear:
    """What one year does to a place's aura: the reckoning shown in the
    review, the details it sets, and the Diary's line."""

    headline: str
    lines: list[str] = field(default_factory=list)
    #: Each value to set: its path within the place's details, and the value.
    sets: list[tuple[list[Any], Any]] = field(default_factory=list)
    diary: str = ""
    #: Whether the review should tick it at first (anything worth applying).
    ticked: bool = True


class Strategy(Protocol):
    def year(
        self, saga: Saga, place: Neighbour, year: int, rng: random.Random
    ) -> AuraYear | None: ...


def is_on(saga: Saga | None) -> bool:
    return options.is_on(saga, OPTION)


def number(value: Any) -> int:
    return sites.whole_number(value)


# -- Magic --


_TETHER = re.compile(r"^(.*?)\s*\((natural|preternatural)\s+(\d+)\)\s*$", re.IGNORECASE)


def tethers(place: Neighbour) -> list[Tether]:
    """The tethers its text scores: each part (between commas, semicolons
    or lines) ending in "(natural 2)" or "(preternatural 4)"."""
    text = str(place.details.get("tethers") or "")
    found: list[Tether] = []
    for part in re.split(r"[,;\n]", text):
        match = _TETHER.match(part.strip())
        if match:
            name, kind, score = match.groups()
            found.append(Tether(name=name, kind=kind.lower(), score=int(score)))
    return found


def impinging(place: Neighbour) -> list[str]:
    """The realms of stronger auras that impinge on it."""
    return [r for r in IMPINGING if place.details.get(f"impinging_{r.lower()}")]


def base_aura(found: list[Tether]) -> int:
    """The base aura its tethers give (RoP: Magic p. 8)."""
    natural = [number(t.get("score")) for t in found if t.get("kind") == NATURAL]
    other = sorted(
        (number(t.get("score")) for t in found if t.get("kind") != NATURAL),
        reverse=True,
    )
    natural_score = min(sum(natural), TETHER_LIMIT)
    other_score = min(other[0] + len(other) - 1, TETHER_LIMIT) if other else 0
    return natural_score + other_score


def _top(place: Neighbour) -> tuple[int, list[Any]]:
    """The aura the rules watch (a regio's top level) and its details path."""
    shown = sites.levels(place)
    if shown:
        index = len(shown) - 1
        return number(shown[index].get("aura")), ["levels", index, "aura"]
    return number(place.details.get("aura")), ["aura"]


def _here(saga: Saga, place: Neighbour) -> tuple[set[str], set[str]]:
    """The covenants at the place, and the characters who live there."""
    covenants = {c.id for c in sites.covenants_at(saga, place)}
    people = {c.id for c in saga.characters if c.covenant_id in covenants}
    return covenants, people


def _label(key: str) -> str:
    found = activities.ACTIVITIES.get(key)
    return found.label if found is not None else key


def _season_counts(saga: Saga, place: Neighbour, year: int) -> tuple[int, int]:
    """This year's seasons there, from the season records: vis study using
    3 or more pawns (judged by the student's Art now), and vis extraction."""
    _, people = _here(saga, place)
    study_label, extract_label = (
        _label(activities.VIS_STUDY),
        _label(lab_seasons.EXTRACT),
    )
    spent = extracted = 0
    for record in saga.season_records:
        if record.year != year:
            continue
        for line in record.lines:
            if line.character_id not in people or "not carried out" in line.result:
                continue
            if line.activity == extract_label:
                extracted += 1
            elif line.activity == study_label:
                student = saga.character(line.character_id)
                if student is None or not line.what:
                    continue
                art = line.what.split()[0]
                pawns = study.season_vis_pawns(student, activities.score(student, art))
                spent += pawns >= VIS_SPENT
    return spent, extracted


def magic_terms(saga: Saga, place: Neighbour, year: int) -> list[tuple[str, int]]:
    """The yearly modifier's terms (label, amount), before its limit."""
    current, _ = _top(place)
    terms: list[tuple[str, int]] = []
    found = tethers(place)
    if found:
        base = base_aura(found)
        if base != current:
            terms.append((f"Base aura {base}, now {current}", 3 * (base - current)))
    for realm in impinging(place):
        terms.append((f"A stronger {realm} aura impinges", IMPINGING[realm]))
    covenants, _ = _here(saga, place)
    seasons = [c.covenant_season for c in saga.covenants if c.id in covenants]
    if seasons:
        best = max(seasons, key=lambda s: ACTIVITY.get(s, 0))
        terms.append((f"Magic worked by a {best} covenant", ACTIVITY.get(best, 0)))
    spent, extracted = _season_counts(saga, place, year)
    if spent:
        terms.append((f"Vis study using {VIS_SPENT}+ pawns ({spent})", spent))
    if extracted:
        terms.append((f"Vis extraction ({extracted} seasons)", -extracted))
    latent = number(place.details.get("aura_latent"))
    if latent:
        terms.append(("Carried from last year", latent))
    adjust = number(place.details.get("aura_adjust", place.details.get("raising")))
    if adjust:
        terms.append(("Botches and other magic this year", adjust))
    return terms


def yearly_modifier(terms: list[tuple[str, int]]) -> int:
    total = sum(amount for _, amount in terms)
    return max(-MODIFIER_LIMIT, min(MODIFIER_LIMIT, total))


def table_row(table: str, total: int) -> str:
    """What a total of 0 to 20 does on `table`."""
    return next(text for low, text in _TABLES[table] if total >= low)


@dataclass
class TableRoll:
    totals: list[int]
    results: list[str]
    botched: bool = False
    #: Rolls of 9 or more (each adds a botch die for later years).
    high: int = 0


def roll_table(
    table: str, modifier: int, botch_dice: int, rng: random.Random, saga: Saga
) -> TableRoll:
    """A roll on `table`: stress die + the modifier's size; 21+ rolls twice
    more, each 21+ of those counting as 20."""
    die = dice.stress_die(rng, botch_dice, saga=saga)
    if die.botched:
        return TableRoll([0], [_BOTCH[table]], botched=True)
    total = die.value + abs(modifier)
    if total < 21:
        return TableRoll([total], [table_row(table, total)], high=int(total >= 9))
    rolled = TableRoll([total], [])
    for _ in range(2):
        again = dice.stress_die(rng, botch_dice, saga=saga)
        if again.botched:
            rolled.totals.append(0)
            rolled.results.append(_BOTCH[table])
            rolled.botched = True
            continue
        value = min(again.value + abs(modifier), 20)
        rolled.totals.append(value)
        rolled.results.append(table_row(table, value))
        rolled.high += value >= 9
    rolled.high += 1  # the 21+ itself
    return rolled


class MagicAura:
    """Realms of Power: Magic's aura variation."""

    def year(
        self, saga: Saga, place: Neighbour, year: int, rng: random.Random
    ) -> AuraYear | None:
        terms = magic_terms(saga, place, year)
        modifier = yearly_modifier(terms)
        botch_dice = number(place.details.get("aura_botch_dice"))
        current, path = _top(place)
        lines = [f"{label} {amount:+d}" for label, amount in terms]
        lines.append(f"Yearly modifier {modifier:+d} (limit +/-{MODIFIER_LIMIT})")
        sets: list[tuple[list[Any], Any]] = []
        if place.details.get("aura_latent"):
            sets.append((["aura_latent"], 0))
        if place.details.get("aura_adjust") or place.details.get("raising"):
            sets.append((["aura_adjust"], 0))
        if abs(modifier) <= STABLE:
            if botch_dice:
                sets.append((["aura_botch_dice"], botch_dice - 1))
            if not sets:
                return None
            return AuraYear(
                f"{place.name}: Magic aura steady (modifier {modifier:+d})",
                lines,
                sets,
                f"The aura held steady (yearly modifier {modifier:+d}).",
                ticked=True,
            )
        table = STRENGTHENING if modifier > 0 else WEAKENING
        rolled = roll_table(table, modifier, botch_dice, rng, saga)
        lines.append(
            f"{table} table, stress die {modifier:+d} with {botch_dice} botch "
            f"{'die' if botch_dice == 1 else 'dice'}: "
            + ", ".join(
                "botch" if t == 0 and rolled.botched else str(t) for t in rolled.totals
            )
        )
        lines += rolled.results
        if rolled.high:
            sets.append((["aura_botch_dice"], botch_dice + rolled.high))
        if any(text.startswith("Latent") for text in rolled.results):
            latent = LATENT if table == STRENGTHENING else -LATENT
            sets = [s for s in sets if s[0] != ["aura_latent"]]
            sets.append((["aura_latent"], latent))
        step = sum(1 for t in rolled.results if t.startswith("The aura's score")) * (
            1 if table == STRENGTHENING else -1
        )
        if step:
            sets.append((path, max(0, current + step)))
        headline = (
            f"{place.name}: Magic aura {table.lower()} (rolled "
            + ", ".join(str(t) for t in rolled.totals)
            + ")"
        )
        if step:
            headline += f", {current} → {max(0, current + step)}"
        diary = f"{table} of the aura: " + " ".join(rolled.results)
        if rolled.botched:
            diary += " Add or remove the regio level on its Regio tab."
        return AuraYear(headline, lines, sets, diary)


# -- Infernal --


def eroding_since(place: Neighbour) -> int | None:
    value = place.details.get("eroding_since", place.details.get("focus_gone"))
    return None if value is None else number(value)


def dominant(place: Neighbour) -> tuple[int, str]:
    """The stronger aura an Infernal aura sits in (score, realm), 0 if none."""
    return number(place.details.get("around")), str(
        place.details.get("around_realm") or "Divine"
    )


def corruption_eases(place: Neighbour) -> tuple[int, int]:
    """A corruption roll's Ease Factors there: to keep the Infernal aura,
    and to raise it (RoP: The Infernal p. 11)."""
    around, _ = dominant(place)
    strongest = max(around, number(place.details.get("aura")))
    return 3 + strongest, 6 + strongest


class InfernalAura:
    """Realms of Power: The Infernal's erosion of a weaker Infernal aura."""

    def year(
        self, saga: Saga, place: Neighbour, year: int, rng: random.Random
    ) -> AuraYear | None:
        aura = number(place.details.get("aura"))
        around, realm = dominant(place)
        if aura <= 0 or around <= aura or place.details.get("maintained"):
            return None
        since = eroding_since(place)
        if since is None:
            return AuraYear(
                f"{place.name}: Infernal {aura} begins to erode in the {realm} {around}",
                [f"Inside a stronger {realm} aura, it loses 1 after {aura} years."],
                [(["eroding_since"], year)],
                f"The Infernal aura, weaker than the {realm} aura around it, began "
                "to erode.",
            )
        if year - since + 1 < aura:
            return None
        after = aura - 1
        return AuraYear(
            f"{place.name}: Infernal aura eroded, {aura} → {after}",
            [f"{aura} years inside the {realm} {around} with nothing keeping it."],
            [(["aura"], after), (["eroding_since"], year + 1 if after else None)],
            f"The Infernal aura eroded to {after}."
            if after
            else "The Infernal aura is gone.",
        )


# -- Faerie --

#: A faerie aura where two faeries' glamours clash: 2 + the higher Might
#: / 5, at most 9 (RoP: Faerie p. 14).
CLASH_BONUS, CLASH_LIMIT = 2, 9


def _faerie(saga: Saga, place: Neighbour, key: str) -> Creature | None:
    found = saga.creature(place.details.get(key))
    return found if found is not None and found.realm == "Faerie" else None


def glamour_aura(
    saga: Saga, place: Neighbour, lost: int | None = None
) -> tuple[int, str] | None:
    """The aura the faeries' glamour gives the place, and why: the
    presiding faerie's Might / 5; 2 + the higher Might / 5 (at most 9)
    while another contests it; the steward's Might / 5 while the presiding
    faerie is away; less 1 for each extraction of vis it couldn't prevent,
    until it gets redress (RoP: Faerie pp. 14-16). None when no faerie
    presides."""
    presiding = _faerie(saga, place, "presiding")
    if presiding is None:
        return None
    rival = _faerie(saga, place, "contesting")
    steward = _faerie(saga, place, "steward")
    if steward is not None and place.details.get("presiding_away"):
        aura, why = round_down(steward.might / 5), f"{steward.name}, its steward"
    elif rival is not None:
        top = max(presiding.might, rival.might)
        aura = min(CLASH_LIMIT, CLASH_BONUS + round_down(top / 5))
        why = f"{presiding.name} and {rival.name} contesting it"
    else:
        aura, why = round_down(presiding.might / 5), presiding.name
    if lost is None:
        lost = number(place.details.get("glamour_lost"))
    if lost:
        why += f", {lost} lost to vis taken"
    return max(0, aura - lost), why


class FaerieAura:
    """Realms of Power: Faerie's aura, which follows the glamour of the
    faerie that claims the place (pp. 14-16)."""

    def year(
        self, saga: Saga, place: Neighbour, year: int, rng: random.Random
    ) -> AuraYear | None:
        if glamour_aura(saga, place) is None:
            return None
        sets: list[tuple[list[Any], Any]] = []
        lines: list[str] = []
        _, extracted = _season_counts(saga, place, year)
        if extracted and not place.details.get("vis_bargain"):
            lost = number(place.details.get("glamour_lost")) + extracted
            sets.append((["glamour_lost"], lost))
            lines.append(
                f"{extracted} season(s) of vis extraction the faerie couldn't "
                "prevent: the aura falls by 1 each, until it gets redress (p. 15)."
            )
            found = glamour_aura(saga, place, lost)
        else:
            found = glamour_aura(saga, place)
        if found is None:
            return None
        aura, why = found
        current, path = _top(place)
        if aura == current and not sets:
            return None
        lines.insert(0, f"Its glamour: {why}, aura {aura}.")
        if aura != current:
            sets.append((path, aura))
        return AuraYear(
            f"{place.name}: Faerie aura {current} → {aura}"
            if aura != current
            else f"{place.name}: Faerie aura {aura}",
            lines,
            sets,
            f"The faerie aura follows its glamour: {aura} ({why}).",
        )


STRATEGIES: dict[str, Strategy] = {
    "Magic": MagicAura(),
    "Infernal": InfernalAura(),
    "Faerie": FaerieAura(),
}


def summary(saga: Saga, place: Neighbour) -> str:
    """How its aura stands to change, for the place's facts; "" with the
    option off."""
    if not is_on(saga):
        return ""
    realm = place.realm or "Magic"
    if realm == "Magic":
        parts = []
        found = tethers(place)
        if found:
            parts.append(f"base {base_aura(found)} from its tethers")
        terms = magic_terms(saga, place, saga.current_year)
        parts.append(f"this year's modifier so far {yearly_modifier(terms):+d}")
        botch = number(place.details.get("aura_botch_dice"))
        if botch:
            parts.append(f"{botch} botch {'die' if botch == 1 else 'dice'}")
        text = "; ".join(parts)
        return text[0].upper() + text[1:] + " (rolled at ±4 or more)"
    if realm == "Infernal":
        keep, rise = corruption_eases(place)
        aura = number(place.details.get("aura"))
        around, around_realm = dominant(place)
        if around > aura and not place.details.get("maintained"):
            since = eroding_since(place)
            start = f"since {since}" if since is not None else "from this winter"
            state = (
                f"Eroding inside the {around_realm} {around}, losing 1 every "
                f"{aura} years ({start})"
            )
        elif around > aura:
            state = f"Kept inside the {around_realm} {around}"
        else:
            state = "Dominant: it doesn't erode"
        return f"{state}; a corruption roll keeps it at {keep}, raises it at {rise}"
    if realm == "Faerie":
        found = glamour_aura(saga, place)
        if found is None:
            return (
                "No faerie presides: a faerie's glamour gives an aura of its "
                "Might / 5 (RoP: Faerie p. 14)"
            )
        aura, why = found
        return (
            f"Its glamour gives {aura} ({why}); a faerie that travels takes its "
            "aura with it (p. 15)"
        )
    return ""


def year(
    saga: Saga, place: Neighbour, year_: int, rng: random.Random
) -> AuraYear | None:
    """What this year does to the place's aura, by its realm's rule; None
    with the option off, or no rule, or nothing to do."""
    if not is_on(saga):
        return None
    strategy = STRATEGIES.get(place.realm or "Magic")
    return None if strategy is None else strategy.year(saga, place, year_, rng)
