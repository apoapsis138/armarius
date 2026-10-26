"""More's Labor Points from a Story and Invest Time or Money on a
character's This Season: a story's award of Labor Points, and what a
merchant does with his surplus, written in the Diary -- no UI in here.
The rules are rules.merchants'."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, DiaryEntry, Investment, Saga, ScoredTrait
from .rules import confidence
from .rules import merchants as mr
from .rules import supplement_work as sw
from .rules.aging import CHARACTERISTICS
from .rules.scores import ability_level

STORY_TITLE = "Labor Points from a Story"
INVEST_TITLE = "Invest Time or Money"


def _band_field(character: Character) -> DialogField:
    usual = mr.default_band(character)
    return DialogField(
        "band",
        "Income source",
        "select",
        character.income_band or None,
        options=[(mr.band_label(b), b) for b in mr.BANDS],
        allow_blank=True,
        placeholder=(
            f"(as the Social Status: {usual.title()})"
            if usual
            else "(none: choose one)"
        ),
        hint="What Labor Points are worth in money (City & Guild pp. 37, 40).",
    )


def _work_fields(character: Character, show: Any = None) -> list[DialogField]:
    """The Ability and Characteristic a season's worth is reckoned from."""
    abilities = mr.work_abilities(character)
    return [
        DialogField(
            "ability",
            "Works with",
            "select",
            abilities[0] if abilities else None,
            options=[(escape(a), a) for a in abilities],
            required=True,
            allow_blank=not abilities,
            placeholder="(no Craft or Profession)",
            show_if=show,
            hint="A season's worth: (Characteristic + Craft or Profession) x "
            "the Wealth Multiplier (City & Guild p. 39).",
        ),
        DialogField(
            "characteristic",
            "Characteristic",
            "select",
            None,
            options=[(c.title(), c) for c in CHARACTERISTICS],
            allow_blank=True,
            placeholder="(Communication for a Profession, else Dexterity)",
            show_if=show,
        ),
    ]


def _season(character: Character, values: dict[str, Any]) -> tuple[int, str]:
    """A season's worth of Labor Points, and how it is reckoned."""
    ability = str(values.get("ability") or "")
    trait = str(values.get("characteristic") or mr.default_characteristic(ability))
    points = mr.season_labor(character, ability, trait)
    return points, (
        f"({trait.title()} + {ability}) x {sw.multiplier(character)} "
        f"({sw.wealth(character)}) = {points}"
    )


def _set_band(character: Character, values: dict[str, Any]) -> None:
    if "band" in values:
        character.income_band = str(values.get("band") or "")


def _diary(saga: Saga, character: Character, name: str, lines: list[str]) -> None:
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            name,
            "\n".join([*lines, f"Rules: {mr.SOURCE}"]),
        )
    )


# -- Labor Points from a Story ---------------------------------------------


def story_fields(character: Character) -> list[DialogField]:
    awards = mr.stories_for(character)
    return [
        DialogField("story", "The story", "text", "", placeholder="(its name)"),
        DialogField(
            "award",
            "Award",
            "select",
            awards[0].key,
            options=[(escape(mr.story_label(a)), a.key) for a in awards],
            required=True,
            hint="Given when the story's central issue is resolved; smaller "
            "awards for a part in another's story (City & Guild p. 39).",
        ),
        DialogField(
            "seasons",
            "Seasons' worth",
            "select",
            None,
            options=[(mr.seasons_text(s), f"{s:g}") for s in mr.SEASON_CHOICES],
            allow_blank=True,
            placeholder="(as the award says)",
        ),
        *_work_fields(character),
        _band_field(character),
    ]


def _story_seasons(values: dict[str, Any]) -> tuple[mr.StoryAward, float]:
    award = mr.STORY_BY_KEY[str(values.get("award") or "subplot")]
    chosen = values.get("seasons")
    return award, float(chosen) if chosen else award.seasons


def story_award(character: Character, values: dict[str, Any]) -> tuple[int, list[str]]:
    """The Labor Points the story gives and what is said of them."""
    award, seasons = _story_seasons(values)
    season, how = _season(character, values)
    points = mr.award_points(season, seasons)
    lines = [
        f"{mr.worth_text(seasons)} of Labor Points: {how} a season, "
        f"so {points} (City & Guild p. {award.page}).",
        award.also,
    ]
    return points, notes(*lines)


def story_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        points, lines = story_award(character, values)
        after = character.labor_points + points
        return escape(
            " ".join([*lines, f"Labor Points {character.labor_points} -> {after}."])
        )

    return live


def apply_story(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    points, lines = story_award(character, values)
    award, _ = _story_seasons(values)
    _set_band(character, values)
    character.labor_points += points
    lines.append(f"Labor Points now {character.labor_points}.")
    lines.append(
        "A story is the only way to earn Labor Points and experience other "
        "than Exposure in the same season (City & Guild p. 39)."
    )
    story = str(values.get("story") or "").strip() or award.label
    _diary(saga, character, f"Labor Points from a story: {story}", lines)
    return notes(*lines)


def story_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(STORY_TITLE, "Choose a character first.")
    if not mr.work_abilities(character):
        return Refuse(
            STORY_TITLE,
            f"{escape(character.name)} has no Craft or Profession to reckon a "
            "season's worth of Labor Points from: add one on Abilities first.",
        )
    return Form(
        f"{STORY_TITLE}: {escape(character.name)}",
        lambda: story_fields(character),
        lambda values: apply_story(saga, character, values),
        live=story_live(character),
        help_id="labor-from-story",
    )


# -- Invest Time or Money --------------------------------------------------

_SEASONED = (
    mr.CHARITY,
    mr.SPECULATION,
    mr.INTRODUCTION,
    mr.MARRIAGE,
    mr.LEGAL,
    mr.SPONSOR,
)
_NAMED = (*_SEASONED, mr.BOOM)
_POINTS = (mr.CHARITY, mr.SPECULATION, mr.BOOM)
_REPUTED = (mr.CHARITY, mr.MARRIAGE)
#: Open investments that End takes back.
_ENDED = (mr.SPECULATION, mr.SPONSOR)


def _kind_is(*kinds: str) -> Any:
    return lambda values: values.get("kind") in kinds


def _open(character: Character) -> list[tuple[int, Investment]]:
    return [
        (i, record)
        for i, record in enumerate(character.investments)
        if record.kind in _ENDED
    ]


def _open_label(record: Investment) -> str:
    kind = "Speculation" if record.kind == mr.SPECULATION else "Sponsoring smugglers"
    named = f" ({record.name})" if record.name else ""
    return f"{kind}{named}, {record.year}: {record.lp} Labor Points"


def invest_fields(character: Character) -> list[DialogField]:
    offered = mr.investments_for(character)
    if not _open(character):
        offered = [k for k in offered if k.key != mr.END]
    kinds = mr.merchant_kinds(character)
    abilities = [a.name for a in character.abilities]
    return [
        DialogField(
            "kind",
            "Investment",
            "select",
            offered[0].key,
            options=[(f"{k.label} (p. {k.page})", k.key) for k in offered],
            required=True,
        ),
        DialogField(
            "name",
            "In what",
            "text",
            "",
            placeholder="(the charity, the goods, the couple, the suit...)",
            show_if=_kind_is(*_NAMED),
        ),
        DialogField(
            "lp",
            "Labor Points",
            "int",
            0,
            show_if=_kind_is(*_POINTS),
            hint="Given, invested or set aside, out of the surplus.",
        ),
        DialogField(
            "items", "Sumptuous items", "int", 1, show_if=_kind_is(mr.DRAWINGS)
        ),
        DialogField(
            "which",
            "Which one",
            "select",
            str(_open(character)[0][0]) if _open(character) else None,
            options=[(escape(_open_label(r)), str(i)) for i, r in _open(character)],
            allow_blank=not _open(character),
            show_if=_kind_is(mr.END),
        ),
        DialogField(
            "lost",
            "Lost to story events (nothing comes back)",
            "check",
            False,
            show_if=_kind_is(mr.END),
        ),
        DialogField(
            "reputation",
            "Reputation it grows",
            "text",
            _charity_reputation(character),
            show_if=_kind_is(*_REPUTED),
            hint="An existing Reputation of this name, or a new one.",
        ),
        DialogField(
            "merchant",
            "Giving as",
            "select",
            kinds[0] if kinds else None,
            options=[(k.title(), k) for k in kinds],
            allow_blank=not kinds,
            show_if=lambda v: v.get("kind") == mr.CHARITY and len(kinds) > 1,
            hint="The Social Status Multiplier of the crowd (p. 110).",
        ),
        DialogField(
            "mine",
            "His representative's roll",
            "int",
            0,
            show_if=_kind_is(mr.LEGAL),
            hint="Intelligence + Civil or Canon Law + a die.",
        ),
        DialogField(
            "theirs", "The opponent's roll", "int", 0, show_if=_kind_is(mr.LEGAL)
        ),
        DialogField(
            "suit",
            "The suit is",
            "select",
            "",
            options=[
                ("True (+3)", "true"),
                ("Neither (+0)", ""),
                ("False (-3)", "false"),
                ("Outlandish (-6)", "outlandish"),
            ],
            show_if=_kind_is(mr.LEGAL),
        ),
        DialogField(
            "die",
            "Die",
            "int",
            0,
            show_if=_kind_is(mr.BOOM, mr.PARTY),
            hint="The stress die rolled at the table.",
        ),
        DialogField("botched", "Botched", "check", False, show_if=_kind_is(mr.BOOM)),
        DialogField(
            "party_trait",
            "Characteristic",
            "select",
            "presence",
            options=[(c.title(), c) for c in CHARACTERISTICS],
            show_if=_kind_is(mr.PARTY),
        ),
        DialogField(
            "theme",
            "The party's theme",
            "select",
            "Carousing" if "Carousing" in abilities else None,
            options=[(escape(a), a) for a in abilities],
            allow_blank=True,
            placeholder="(an Ability: Carousing, Hunting, Athletics...)",
            show_if=_kind_is(mr.PARTY),
        ),
        DialogField(
            "pounds",
            "Pounds spent",
            "int",
            0,
            show_if=_kind_is(mr.MONEY, mr.PARTY),
            hint="From the silver on Personal Gear.",
        ),
        *_work_fields(character, _kind_is(*_SEASONED)),
        _band_field(character),
    ]


def _charity_reputation(character: Character) -> str:
    known = next(
        (r.reputation for r in character.investments if r.kind == mr.CHARITY), ""
    )
    return known or "Charitable"


@dataclass
class Outcome:
    """What an investment does, worked out before anything changes."""

    lines: list[str] = field(default_factory=list)
    labor: int = 0
    silver: int = 0
    record: Investment | None = None
    #: An open investment ended (its index), or the charity given to.
    ends: int | None = None
    #: A Reputation and the experience it gains.
    reputation: tuple[str, int] | None = None
    problem: str = ""


def _surplus(character: Character, cost: int) -> str:
    if cost > character.labor_points:
        return (
            f"It costs {cost} Labor Points; {character.name} has "
            f"{character.labor_points}."
        )
    return ""


def outcome(saga: Saga, character: Character, values: dict[str, Any]) -> Outcome:
    """What the investment the form describes would do."""
    kind = str(values.get("kind") or mr.MONEY)
    name = str(values.get("name") or "").strip()
    year = saga.current_year
    wm = sw.multiplier(character)
    if kind in _SEASONED:
        if not values.get("ability"):
            return Outcome(problem="Choose the Craft or Profession worked with.")
        season, how = _season(character, values)
    else:
        season, how = 0, ""
    points = max(0, int(values.get("lp") or 0))
    found = _BUILDERS[kind](
        _Ask(saga, character, values, kind, name, year, wm, season, how, points)
    )
    if not found.problem and found.labor < 0:
        found.problem = _surplus(character, -found.labor)
    return found


@dataclass(frozen=True)
class _Ask:
    saga: Saga
    character: Character
    values: dict[str, Any]
    kind: str
    name: str
    year: int
    wm: int
    season: int
    how: str
    points: int


def _money(ask: _Ask) -> Outcome:
    c, pounds = ask.character, max(0, int(ask.values.get("pounds") or 0))
    chosen = str(ask.values.get("band") or "") or mr.default_band(c)
    if chosen not in mr.BANDS:
        return Outcome(problem="Choose the income source the money goes into.")
    if pounds > c.silver:
        return Outcome(problem=f"{c.name} has {c.silver} pounds of silver.")
    gained = mr.lp_for_money(pounds, chosen)
    return Outcome(
        [
            f"{pounds} pounds into a {chosen.title()} business buy {gained} Labor "
            f"Points ({mr.LP_PER_QUARTER} for a quarter of its "
            f"{mr.BANDS[chosen]:,} pounds a year, City & Guild p. 40; Errata p. 56)."
        ],
        labor=gained,
        silver=-pounds,
    )


def _charity(ask: _Ask) -> Outcome:
    c = ask.character
    if ask.points < 1:
        return Outcome(problem="Give at least 1 Labor Point.")
    index = next(
        (
            i
            for i, r in enumerate(c.investments)
            if r.kind == mr.CHARITY and r.name == ask.name
        ),
        None,
    )
    before = c.investments[index] if index is not None else Investment(mr.CHARITY)
    given = before.lp + ask.points
    xp = mr.charity_xp(given, ask.season) - before.paid
    reputation = str(ask.values.get("reputation") or "Charitable").strip()
    record = Investment(
        mr.CHARITY,
        ask.name,
        given,
        ask.year,
        returns=ask.points,
        paid=before.paid + xp,
        reputation=reputation,
        merchant=str(ask.values.get("merchant") or ""),
    )
    lines = [
        f"{ask.points} Labor Points to charity, {given} in all: 1 Reputation "
        f"experience point for each season's worth ({ask.how}), so {xp} more in "
        f"{reputation} (p. 110).",
    ]
    if ask.points >= ask.wm:
        lines.append(
            "Given at least 1 x the Wealth Multiplier this year, the merchant can call a "
            "crowd of those it helps, willing to do mildly illegal things."
        )
    return Outcome(
        lines,
        labor=-ask.points,
        record=record,
        ends=index,
        reputation=(reputation, xp) if xp else None,
    )


def _speculation(ask: _Ask) -> Outcome:
    if ask.points < mr.SPECULATION_PER:
        return Outcome(problem=f"Invest at least {mr.SPECULATION_PER} Labor Points.")
    guards = mr.speculation_guards(ask.points, ask.season)
    return Outcome(
        [
            f"{ask.points} Labor Points in stored goods: +"
            f"{mr.speculation_return(ask.points)} a year, each Winter from next "
            "year, the Labor Points kept, unless story events destroy them "
            f"(p. 110). {guards} guard(s) for an hour a week (one for each half "
            f"season's worth, {ask.season // 2}).",
        ],
        labor=-ask.points,
        record=Investment(mr.SPECULATION, ask.name, ask.points, ask.year),
    )


def _end(ask: _Ask) -> Outcome:
    c = ask.character
    which = ask.values.get("which")
    if which in (None, "") or not 0 <= int(which) < len(c.investments):
        return Outcome(problem="Choose the investment to end.")
    record = c.investments[int(which)]
    back = 0 if ask.values.get("lost") or record.kind != mr.SPECULATION else record.lp
    return Outcome(
        [
            f"{_open_label(record)} ends: "
            + (f"{back} Labor Points back." if back else "nothing comes back.")
        ],
        labor=back,
        ends=int(which),
    )


def _drawings(ask: _Ask) -> Outcome:
    items = max(0, int(ask.values.get("items") or 0))
    if items < 1:
        return Outcome(problem="At least one item.")
    cost = mr.drawings_cost(items, ask.wm)
    return Outcome(
        [
            f"{items} sumptuous item(s) of hand-tool size or smaller, {ask.wm} Labor "
            "Points each; larger things come from the yearly profit or the Social "
            "Status (p. 111)."
        ],
        labor=-cost,
    )


def _introduction(ask: _Ask) -> Outcome:
    cost = mr.INTRODUCTION_COST * ask.season
    back = mr.INTRODUCTION_RETURN * ask.season
    due = ask.year + mr.INTRODUCTION_YEARS
    return Outcome(
        [
            f"Two seasons' worth put in ({cost}; {ask.how} a season), three "
            f"({back}) back in Winter {due}. The junior merchant owes a Favor, "
            "to be called in by then. Spend the season itself introducing them "
            "(p. 111)."
        ],
        labor=-cost,
        record=Investment(
            mr.INTRODUCTION, ask.name, cost, ask.year, returns=back, due_year=due
        ),
    )


def _marriage(ask: _Ask) -> Outcome:
    cost = mr.MARRIAGE_COST * ask.season
    due = ask.year + mr.MARRIAGE_YEARS
    reputation = str(ask.values.get("reputation") or "Charitable").strip()
    return Outcome(
        [
            f"Two seasons' worth lost ({cost}; {ask.how} a season). An honored "
            f"place at the wedding: 1 experience point in {reputation}, Social "
            f"Contacts in the couple's class until Winter {due} unless another "
            "is arranged, and Favors owed by the couple or their parents "
            "(p. 111)."
        ],
        labor=-cost,
        record=Investment(mr.MARRIAGE, ask.name, cost, ask.year, due_year=due),
        reputation=(reputation, 1),
    )


def _legal(ask: _Ask) -> Outcome:
    cost = mr.award_points(ask.season, mr.LEGAL_COST)
    suit = str(ask.values.get("suit") or "")
    mine = int(ask.values.get("mine") or 0)
    theirs = int(ask.values.get("theirs") or 0)
    won = mr.legal_result(mine, theirs, suit)
    total = mine + mr.SUIT_MODIFIERS.get(suit, 0)
    lines = [
        f"Half a season's worth for the suit ({cost}); it takes a season, with or "
        f"without the merchant (p. 114). {total} against {theirs}: "
        + (
            "won: add or take 1 from one of the loser's Reputations."
            if won
            else "lost: perhaps a poor Reputation, at the troupe's word."
        ),
        "Win or lose, the merchant may gain the Enemy Flaw (the troupe's call).",
    ]
    return Outcome(lines, labor=-cost)


def _boom(ask: _Ask) -> Outcome:
    c = ask.character
    if ask.points < 1:
        return Outcome(problem="Set aside at least 1 Labor Point.")
    die = int(ask.values.get("die") or 0)
    total = c.characteristics.intelligence + mr.area_lore(c) + die
    back, what = mr.boom_return(total, ask.points, bool(ask.values.get("botched")))
    return Outcome(
        [
            f"Intelligence + Area Lore + die = {total}. {what} {ask.points} set "
            f"aside, {back} back (pp. 111-112). Use it when the troupe's boom "
            "comes."
        ],
        labor=back - ask.points,
    )


def _smuggling(ask: _Ask) -> Outcome:
    points = mr.smuggling_season(ask.character)
    return Outcome(
        [
            f"A season smuggling: (Intelligence + Intrigue) x {ask.wm} = {points} "
            "Labor Points. Smugglers have the Dark Secret Flaw and the Social "
            "Contacts Virtue (p. 117)."
        ],
        labor=points,
    )


def _sponsor(ask: _Ask) -> Outcome:
    return Outcome(
        [
            f"Sponsoring smugglers, fencing and supplying them: a season's worth "
            f"({ask.how}) each Winter from next year, beside the legitimate work, "
            "and the Dark Secret Flaw (p. 117)."
        ],
        record=Investment(mr.SPONSOR, ask.name, 0, ask.year, returns=ask.season),
    )


def _government(ask: _Ask) -> Outcome:
    points = mr.government_points(ask.character)
    return Outcome(
        [
            f"Change of government, invested: (Communication + Intrigue) x "
            f"{ask.wm} = {points} Labor Points and the Favor of a minor political "
            "figure (p. 122)."
        ],
        labor=points,
    )


def _talent(ask: _Ask) -> Outcome:
    points = mr.talent_points(ask.character)
    owed = mr.favors(points, mr.TALENT_PER_FAVOR)
    return Outcome(
        [
            f"Young talent, invested: (Communication + Leadership) x {ask.wm} = "
            f"{points} Labor Points, and {owed} Favor(s), one for each 10 rounded "
            "up (p. 128)."
        ],
        labor=points,
    )


def _party(ask: _Ask) -> Outcome:
    c, values = ask.character, ask.values
    pounds = max(0, int(values.get("pounds") or 0))
    if pounds > c.silver:
        return Outcome(problem=f"{c.name} has {c.silver} pounds of silver.")
    trait = str(values.get("party_trait") or "presence")
    theme = str(values.get("theme") or "")
    intrigue = ability_level(c, "Intrigue")
    total = mr.party_total(
        int(values.get("die") or 0),
        getattr(c.characteristics, trait, 0),
        ability_level(c, theme) if theme else 0,
        pounds,
        intrigue,
    )
    owed = mr.favors(total, mr.PARTY_PER_FAVOR)
    counted = min(pounds, max(0, intrigue))
    return Outcome(
        [
            f"Die + {trait.title()} + {theme or 'the theme'} + {counted} pound(s) "
            f"counted (at most Intrigue {intrigue}) = {total}: the benefits of "
            f"{owed} Favor(s), one for each 5 rounded up (p. 129)."
        ],
        silver=-pounds,
    )


_BUILDERS = {
    mr.MONEY: _money,
    mr.CHARITY: _charity,
    mr.SPECULATION: _speculation,
    mr.END: _end,
    mr.DRAWINGS: _drawings,
    mr.INTRODUCTION: _introduction,
    mr.MARRIAGE: _marriage,
    mr.LEGAL: _legal,
    mr.BOOM: _boom,
    mr.SMUGGLING: _smuggling,
    mr.SPONSOR: _sponsor,
    mr.GOVERNMENT: _government,
    mr.TALENT: _talent,
    mr.PARTY: _party,
}


def invest_live(saga: Saga, character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        found = outcome(saga, character, values)
        if found.problem:
            return escape(found.problem)
        after = character.labor_points + found.labor
        return escape(
            " ".join(
                [*found.lines, f"Labor Points {character.labor_points} -> {after}."]
            )
        )

    return live


def _grow(character: Character, name: str, xp: int) -> str:
    reputation = next(
        (r for r in character.reputations if r.name.lower() == name.lower()), None
    )
    if reputation is None:
        reputation = ScoredTrait(name, 0)
        character.reputations.append(reputation)
    before = reputation.score
    confidence.add_deeds(reputation, xp)
    if reputation.score != before:
        return f"{reputation.name} {before:+d} to {reputation.score:+d}."
    return f"{reputation.name}: {reputation.deeds} toward the next level."


def apply_investment(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    found = outcome(saga, character, values)
    lines = list(found.lines)
    _set_band(character, values)
    character.labor_points += found.labor
    character.silver += found.silver
    if found.ends is not None:
        del character.investments[found.ends]
    if found.record is not None:
        character.investments.append(found.record)
    if found.reputation is not None:
        lines.append(_grow(character, *found.reputation))
    lines.append(f"Labor Points now {character.labor_points}.")
    kind = mr.INVESTMENT_BY_KEY[str(values.get("kind") or mr.MONEY)]
    _diary(saga, character, kind.label, lines)
    return notes(*lines)


def invest_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(INVEST_TITLE, "Choose a character first.")
    return Form(
        f"{INVEST_TITLE}: {escape(character.name)}",
        lambda: invest_fields(character),
        lambda values: apply_investment(saga, character, values),
        validate=lambda values: outcome(saga, character, values).problem or None,
        live=invest_live(saga, character),
        help_id="merchant-investment",
    )
