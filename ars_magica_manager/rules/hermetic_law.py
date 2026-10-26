"""Hermetic law on a Tribunal's docket: the Wizard's War, the Wizard's
March, a Quaesitor's evidence from spell traces, and Intrigue worked on a
case. Each is a kind of case or a few of a case's fields; what follows
from it is worked out here and shown with the case, and a March the
meeting votes is written on the outcast's Hermetic Background when the
meeting closes.

Wizard's War (DE p. 21; HoH: Societates pp. 22-24; HoH: True Lineages
pp. 47-48). A declaration must arrive on the night of a full moon; the war
begins at the rise of the next full moon and lasts until the rise of the
one after: a month to prepare, a month of war. It is between exactly two
magi; one may be at war with several at once, each a war of its own, but
a second war between the same two can only be declared once the first
has ended, so renewing it gives a month of war, a month of peace. Either
may slay the other without retribution, and declaring a war is no crime;
but harm to other magi or to property the foe shares with them, and
scrying on or attacking those not at war, are not covered. Declared
unjustly or too often, war is a charge of endangering the Order, even a
March; no book says how often is too often (DE p. 21; HoH: TL pp. 47-48;
Societates p. 24), so the docket's warning at three in seven years is a
storyguide's default the app chose. How the declaration is served is the Tribunal's custom: most hold
one nailed to the door of the sanctum of a magus at home duly served; one
undelivered is reported to a Quaesitor, who rules whether it stands.

Wizard's March (DE p. 18; HoH: TL pp. 46, 54, 58-60, 63). Only a high
crime lets the prosecution call for a March on conviction; it carries on
a simple majority, a tie defeating it. Otherwise the Presiding Quaesitor
offers a lesser penalty, and three refusals March the convicted magus.
A Quaesitor may call a March between meetings when a magus is an
immediate danger; the next Tribunal ratifies it, and he may not profit
by it. The outcast may not be attacked until the Tribunal closes; then
he is outside the Code, and any magus may slay him. The estate: a quarter
to the victim, as damages, and a quarter to the prosecutor, as a fine (a
half if the victim prosecutes), the rest to the heir, nothing to the
Tribunal's coffers (TL p. 59). Victim and prosecutor are separate roles:
anyone may bring the case of a slain victim, and a Quaesitor may
prosecute a high crime (TL p. 56). By tradition what he has goes to those
who slay him (DE p. 18); TL p. 53 fits the two together, since the heir
takes the parens's duty to strike first and the slayer may charge him
with failing it and settle for the inheritance, a convention so
established that no one bothers with the formality. So the TL split is
shown, and beside it the slayer taking the heir's half once the victim's
and prosecutor's shares are paid. The parens's duty is a legal one in TL
pp. 46, 53, which the Definitive Edition (p. 21) calls a social
expectation rather than a duty; the Definitive Edition is followed, so
nothing charges an heir.

Quaesitorial magic (HoH: TL pp. 70-72). A spell's trace halves its
magnitude when the spell ends (rounded down: the app's assumption, as
neither TL p. 71 nor Hooks p. 83 says), then loses a magnitude for each
of the spell's Durations that passes (a Momentary spell's, each round);
from nothing it falls into negative magnitudes, a month at a time for a
non-Ritual Momentary, Concentration or Diameter spell and a year at a
time for all others (a Moon or Year spell among them), and is gone at
-10. Acute Sense (a Mastery ability for magical sense spells) spots
deceptive magic: Perception + Penetration + stress die against 6 + the
deception's magnitude (or its maker's Might's). A copied sigil made with
Shroud Magic sets an Ease Factor of Intelligence + Finesse + stress die
(-3 from memory, +3 with the sigil to hand), tested by By His Works
against Perception + Awareness + stress die.

Intrigue (HoH: TL pp. 24-25). To sway someone, Presence + Intrigue; to
learn from them, Communication + Intrigue; a stress roll against an Ease
Factor of 6 to 15 by what is sought. The Gift costs 3 (6 for the Blatant
Gift), unless both parties are under Parma Magica, as magi at a Tribunal
usually are; with a mundane, or a magus whose Parma is down, it is taken.
Folk Ken rolls through a Tribunal give -3 to +3 to Intelligence +
Intrigue, at the storyguide's word.

The Errata change nothing on these pages (its True Lineages entries touch
p. 52's scrying, where Criamon becomes Verditius, and not the rules here).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import SEASONS, Case, Character, Saga, Tribunal, season_order
from . import code_of_hermes
from .casting import magnitude
from .lab import ability_score

SOURCE = (
    "Ars Magica Definitive Edition, The Code of Hermes, pp. 18-21; Houses of "
    "Hermes: Societates, Wizard's War, pp. 22-25; Houses of Hermes: True "
    "Lineages, Intrigue pp. 24-25, The Code of Hermes pp. 45-63, Quaesitorial "
    "Magic pp. 70-72"
)

# -- the kinds of case Hermetic law adds to the docket --


@dataclass(frozen=True)
class LawKind:
    key: str
    label: str
    #: The label a docket's narrow Kind column shows.
    short: str
    #: Whether a meeting hears it (a war is heard only if disputed).
    heard: bool
    #: Whether notice of it is due before the meeting.
    notice: bool
    about: str


WAR = "war"
MARCH = "march"
CHARGE = "charge"

KINDS: tuple[LawKind, ...] = (
    LawKind(
        WAR,
        "Wizard's War",
        "War",
        heard=False,
        notice=False,
        about="A declaration of Wizard's War, kept on the docket: it arrives "
        "on a full moon, the war begins at the next and ends at the one after "
        "(DE p. 21). A meeting hears it only if its service is disputed.",
    ),
    LawKind(
        MARCH,
        "Wizard's March",
        "March",
        heard=True,
        notice=False,
        about="A March a Quaesitor called between meetings, for the next "
        "Tribunal to ratify (HoH: True Lineages p. 63).",
    ),
)


def law_kind(key: str) -> LawKind | None:
    return next((k for k in KINDS if k.key == key), None)


def kind_label(key: str, *, short: bool = False) -> str:
    """A case kind as it is shown: "Wizard's War" ("War" in a narrow
    column), or "Charge"."""
    found = law_kind(key)
    if found is None:
        return key.title()
    return found.short if short else found.label


def kind_options(kinds: tuple[str, ...]) -> list[tuple[str, str]]:
    """The Kind choice: the docket's own kinds, then Hermetic law's."""
    return [(k.title(), k) for k in kinds] + [(k.label, k.key) for k in KINDS]


def heard(case: Case) -> bool:
    """Whether a meeting hears `case`: a war only when its service is
    disputed."""
    found = law_kind(case.kind)
    return found is None or found.heard or disputed(case)


def needs_notice(kind: str) -> bool:
    found = law_kind(kind)
    return found is None or found.notice


# -- Wizard's War --

#: Full moons in a season.
MONTHS = 3
_ORDINAL = ("first", "second", "third")


def moon(year: int, season: str, month: int) -> int:
    """The full moon of `month` (1-3) of a season, as a number that counts
    the months."""
    return season_order(season=season, year=year) * MONTHS + month - 1


def moon_text(n: int) -> str:
    """ "the second month of Summer 1221"."""
    order, month = divmod(n, MONTHS)
    year, season = divmod(order, len(SEASONS))
    return f"the {_ORDINAL[month]} month of {SEASONS[season]} {year}"


@dataclass(frozen=True)
class War:
    declared: int
    #: The war runs from the full moon `begins` until the one at `ends`.
    begins: int
    ends: int


def war_of(case: Case) -> War | None:
    """A declaration's month, and its war's: None until it says when it
    arrived."""
    if case.kind != WAR or case.filed_year is None or case.month is None:
        return None
    declared = moon(case.filed_year, case.filed_season or SEASONS[0], case.month)
    return War(declared, declared + 1, declared + 2)


#: How a declaration was served, and what that makes of it (HoH: TL p. 47,
#: HoH: Societates p. 23).
SERVICE: tuple[tuple[str, str, str], ...] = (
    (
        "redcap",
        "By a Redcap, who witnessed it",
        "duly served: the Redcap is its legal witness (HoH: TL p. 47)",
    ),
    ("in_person", "Into his hands", "duly served"),
    (
        "sanctum_door",
        "Nailed to his sanctum door, he at home",
        "duly served, as most Tribunals hold (HoH: Societates p. 23)",
    ),
    (
        "representative",
        "To his representative or forwarding address",
        "served, where the Tribunal asks magi to name one (HoH: Societates p. 23)",
    ),
    (
        "absent",
        "He was away and named no one",
        "taken as wilfully ignored where the Tribunal asks magi to name a "
        "representative (HoH: Societates p. 23)",
    ),
    (
        "undelivered",
        "Not delivered",
        "the messenger reports to a Quaesitor, who rules whether it stands "
        "(HoH: Societates p. 23)",
    ),
)
UNDELIVERED = "undelivered"


def service_options() -> list[tuple[str, str]]:
    return [(label, key) for key, label, _note in SERVICE]


def disputed(case: Case) -> bool:
    """Whether a declaration's service is in doubt, for a Tribunal or a
    Quaesitor to rule on."""
    return case.kind == WAR and (case.contested or case.served == UNDELIVERED)


def _same(a: str, b: str) -> bool:
    return a.strip().casefold() == b.strip().casefold()


def _pair(case: Case) -> frozenset[str]:
    return frozenset(
        (case.brought_by.strip().casefold(), case.against.strip().casefold())
    )


def wars(saga: Saga) -> list[tuple[Tribunal, Case]]:
    """Every declaration of Wizard's War on the saga's dockets, not
    withdrawn."""
    return [
        (t, c)
        for t in saga.tribunals
        for c in t.cases
        if c.kind == WAR and c.status != "withdrawn"
    ]


def war_problem(saga: Saga, case_id: str, values: dict[str, object]) -> str | None:
    """Why a declaration can't be filed as `values` give it: it names when
    it arrived and two magi, not a covenant, and the same two may not be
    at war again until the first war has ended (HoH: Societates p. 23)."""
    by = str(values.get("brought_by") or "").strip()
    against = str(values.get("against") or "").strip()
    month, year = values.get("month"), values.get("filed_year")
    if not by or not against:
        return "A Wizard's War names the magus who declares it and the one he declares it on."
    if _same(by, against):
        return "A magus can't declare Wizard's War on himself."
    if any(_same(against, c.name) for c in saga.covenants):
        return (
            "A Wizard's War is between two magi: declare one on each of the "
            "covenant's magi (HoH: Societates p. 23)."
        )
    if not isinstance(month, int) or not 1 <= month <= MONTHS:
        return "Say which month of the season's full moon the declaration arrived on (1 to 3)."
    if not isinstance(year, int):
        return "Say the year the declaration arrived."
    season = str(values.get("filed_season") or SEASONS[0])
    declared = moon(year, season, month)
    pair = frozenset((by.casefold(), against.casefold()))
    for _tribunal, other in wars(saga):
        war = war_of(other)
        if other.id == case_id or war is None or _pair(other) != pair:
            continue
        if declared < war.ends and war.declared < declared + 2:
            return (
                f"{by} and {against} are already at war, or waiting for it, "
                f"until the full moon of {moon_text(war.ends)}: a new war "
                "can be declared once it has ended (HoH: Societates p. 23)."
            )
    return None


def war_state(war: War, year: int, season: str) -> str:
    """Where the war stands in the saga's season."""
    first = season_order(season=season, year=year) * MONTHS
    if first + MONTHS - 1 < war.begins:
        return "to come: the month to prepare runs"
    if first > war.ends:
        return "over"
    return "this season"


#: Declarations in seven years that the docket warns of: a storyguide's
#: default the app chose, since no book gives a number (DE p. 21 says only
#: "too often"; HoH: Societates p. 24 only extreme abuse).
TOO_OFTEN = 3
#: The years counted: a Tribunal's term.
TOO_OFTEN_YEARS = 7


def declared_by(saga: Saga, name: str, year: int) -> int:
    """How many Wizard's Wars `name` has declared in the seven years to
    `year`."""
    return sum(
        1
        for _t, c in wars(saga)
        if _same(c.brought_by, name)
        and c.filed_year is not None
        and year - TOO_OFTEN_YEARS < c.filed_year <= year
    )


def _service_note(case: Case) -> str:
    return next((note for key, _l, note in SERVICE if key == case.served), "")


def war_lines(saga: Saga, case: Case) -> list[tuple[str, str]]:
    war = war_of(case)
    if war is None:
        return [("War", "Say the month whose full moon the declaration arrived on.")]
    lines = [
        (
            "War",
            f"declared at the full moon of {moon_text(war.declared)}; it "
            f"begins at the next ({moon_text(war.begins)}) and lasts until "
            f"the one after ({moon_text(war.ends)}) (DE p. 21)",
        ),
        ("Now", war_state(war, saga.current_year, saga.current_season)),
    ]
    note = _service_note(case)
    if note:
        lines.append(("Served", note))
    if disputed(case):
        lines.append(
            (
                "Disputed",
                "its service is in doubt: the Tribunal hears it, or a Quaesitor rules",
            )
        )
    lines.append(
        (
            "Under the Code",
            "either may slay the other without retribution, and neither is "
            "charged for declaring it (DE p. 19; HoH: TL p. 47); harm to "
            "other magi, to property shared with them, or scrying on or "
            "attacking those not at war, stays a crime (HoH: Societates pp. "
            "22-23; HoH: TL p. 47)",
        )
    )
    count = declared_by(saga, case.brought_by, case.filed_year or saga.current_year)
    if count >= TOO_OFTEN:
        lines.append(
            (
                "Too often",
                f"{case.brought_by.strip()} has declared {count} Wizard's Wars "
                f"in {TOO_OFTEN_YEARS} years, past the storyguide's default of "
                f"{TOO_OFTEN} (no book gives a number): unjust or constant use "
                "can be charged as endangering the Order, even Marched (DE p. "
                "21; HoH: TL p. 48)",
            )
        )
    return lines


# -- the Wizard's March --

REFUSALS = code_of_hermes.REFUSALS


def may_march(case: Case) -> bool:
    """Whether the Tribunal may March the accused for this case: a
    Quaesitor's March to ratify, or a conviction for a high crime (HoH: TL
    p. 46). Three refusals of a lesser penalty March him for any crime."""
    if case.kind == MARCH:
        return True
    return case.kind == CHARGE and code_of_hermes.high_crime(case.charge) is not None


def marched(called: bool, refused: int | None) -> bool:
    """Whether the ruling casts the accused out: the March voted, or the
    lesser penalty refused three times (HoH: TL p. 59)."""
    return called or (refused or 0) >= REFUSALS


def refusals_problem(refused: int | None) -> str | None:
    if refused is not None and not 0 <= refused <= REFUSALS:
        return f"A convicted magus refuses a lesser penalty at most {REFUSALS} times."
    return None


def march_problem(case: Case, called: bool, refused: int | None) -> str | None:
    """Why a ruling can't March the accused: refusals out of range, or a
    March called for a case that allows none."""
    problem = refusals_problem(refused)
    if problem:
        return problem
    if called and not may_march(case):
        return (
            f"{case.title}: only a high crime lets the prosecution call for a "
            "Wizard's March; any other conviction Marches the magus only if he "
            f"refuses the penalty {REFUSALS} times (HoH: TL pp. 46, 59)."
        )
    return None


def estate_shares(case: Case) -> list[tuple[str, float]]:
    """Who takes the outcast's estate (HoH: TL p. 59): the victim (the
    case's, else whoever brought it), the prosecutor (else whoever brought
    it), a half for one who is both, and the heir; the Tribunal's coffers
    take nothing, except a Quaesitor's share of a March he called himself
    (p. 63)."""
    brought = case.brought_by.strip()
    victim = case.victim.strip() or brought or "the victim"
    prosecutor = case.prosecutor.strip() or brought or victim
    victim_share = code_of_hermes.MARCH_SHARES["victim"]
    prosecutor_share = code_of_hermes.MARCH_SHARES["prosecutor"]
    heir = ("his heir", code_of_hermes.MARCH_SHARES["heir"])
    if case.kind == MARCH:
        return [("the Tribunal's coffers", victim_share + prosecutor_share), heir]
    if _same(victim, prosecutor):
        return [(victim, victim_share + prosecutor_share), heir]
    return [(victim, victim_share), (prosecutor, prosecutor_share), heir]


def _share_text(share: float) -> str:
    return {0.25: "a quarter", 0.5: "half"}.get(share, f"{share:.0%}")


def march_lines(case: Case) -> list[tuple[str, str]]:
    """A case that may March the accused: how, and what follows."""
    if not may_march(case):
        return []
    lines = []
    if case.kind == MARCH:
        lines.append(
            (
                "Ratified",
                "at the next Tribunal, where the Quaesitor who called it must "
                "justify it; he may gain nothing by it (HoH: TL p. 63)",
            )
        )
        how = ""
    else:
        how = (
            "carried by a simple majority (a tie defeats it), or after "
            f"{REFUSALS} refusals of a lesser penalty; "
        )
    shares = ", ".join(f"{who} {_share_text(s)}" for who, s in estate_shares(case))
    lines.append(
        (
            "If Marched",
            f"{how}his estate: {shares}; safe until the Tribunal closes, then "
            "any magus may slay him (DE p. 18; HoH: TL pp. 58-60)",
        )
    )
    lines.append(("By convention", _convention_text(case)))
    return lines


def _convention_text(case: Case) -> str:
    """The slayer's claim on the heir's share (HoH: TL p. 53), shown beside
    True Lineages's split."""
    paid = [who for who, _s in estate_shares(case) if who != "his heir"]
    first = " and ".join(paid)
    return (
        "whoever slays him takes the heir's half, once "
        f"{first} {'is' if len(paid) == 1 else 'are'} paid: the heir takes "
        "the parens's duty to strike first, and the slayer may charge him "
        "with failing it and settle for the inheritance, a convention so "
        "established that no one bothers with the formality (HoH: TL p. 53), "
        "which fits the tradition that his goods go to his slayers (DE p. "
        "18). The Definitive Edition makes the parens's duty a social "
        "expectation (p. 21), so no heir is charged here"
    )


def _named(saga: Saga, words: str) -> Character | None:
    wanted = words.strip().casefold()
    if not wanted:
        return None
    return next((c for c in saga.characters if c.name.casefold() == wanted), None)


def renounce(saga: Saga, tribunal: Tribunal, case: Case, year: int) -> Character | None:
    """The Tribunal's March written on the outcast's Hermetic Background:
    the magus the case is against, if he is in the saga."""
    outcast = _named(saga, case.against)
    if outcast is None:
        return None
    outcast.hermetic.renounced_year = year
    outcast.hermetic.renounced_by = f"{tribunal.name.strip()}: {case.title.strip()}"
    return outcast


def standing_text(saga: Saga, character: Character) -> str:
    """A magus's standing under the Code, for his Hermetic Background: cast
    out, or at Wizard's War."""
    lines = []
    h = character.hermetic
    if h.renounced_year is not None:
        by = f" ({h.renounced_by})" if h.renounced_by.strip() else ""
        lines.append(
            f"Renounced in {h.renounced_year}{by}: cast out of the Order, any "
            "magus may slay him (DE p. 18)"
        )
    now = season_order(season=saga.current_season, year=saga.current_year) * MONTHS
    for _tribunal, case in wars(saga):
        war = war_of(case)
        if war is None or war.ends < now:
            continue
        if _same(case.brought_by, character.name):
            foe = case.against.strip()
        elif _same(case.against, character.name):
            foe = case.brought_by.strip()
        else:
            continue
        lines.append(
            f"Wizard's War with {foe}: from {moon_text(war.begins)} until "
            f"{moon_text(war.ends)}"
        )
    return "\n".join(lines)


# -- low crimes by the Peripheral Code --

#: Offences the Peripheral Code makes low crimes (HoH: TL), the words in a
#: charge that name them, and the page.
LOW_CRIMES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    (
        "Reading a text marked with another's sanctum or House mark",
        ("sanctum mark", "marked text", "house mark", "house symbol"),
        "p. 71",
    ),
    (
        "Reading Quaesitorial texts without being a Quaesitor",
        ("quaesitorial text", "quaesitorial lab text"),
        "p. 70",
    ),
    (
        "Failing to cooperate with a Quaesitor's investigation",
        ("cooperat", "obstruct"),
        "p. 62",
    ),
    ("Perjury at Tribunal", ("perjur",), "p. 56"),
    ("Deceiving a Quaesitor", ("deceiv",), "p. 56"),
    ("Breaking a contract", ("contract",), "p. 56"),
    ("Vagrancy", ("vagran",), "p. 49"),
    ("Keeping a Gifted child only as a lab assistant", ("lab assistant",), "p. 52"),
    ("An assault short of life or magic", ("assault",), "p. 56"),
)


def low_crime(charge: str) -> tuple[str, str] | None:
    """The low crime a charge's words name (and its page), if it names no
    high crime."""
    if code_of_hermes.high_crime(charge) is not None:
        return None
    words = charge.casefold()
    return next(
        (
            (name, page)
            for name, found, page in LOW_CRIMES
            if any(w in words for w in found)
        ),
        None,
    )


# -- spell traces and Quaesitorial magic --

#: Durations whose trace, once at nothing, fades a month at a time (when
#: not a Ritual); every other fades a year at a time.
MONTHLY = frozenset({"Momentary", "Concentration", "Diameter"})
#: Months one Duration of each lasts, for those of a month or more; the
#: others pass in under a month.
DURATION_MONTHS = {"Moon": 1, "Year": 12}
#: A trace is gone at this magnitude.
GONE = -10
#: Acute Sense's Ease Factor before the deception's magnitude.
ACUTE_BASE = 6
#: A copied sigil's modifiers by how it was studied (p. 71).
SHROUD_STUDY = {"memory": -3, "aided": 0, "example": 3}


def trace_magnitude(level: int, duration: str, ritual: bool, months: int | None) -> int:
    """A spell's trace `months` after it ended (None: still active): half
    its magnitude (rounded down, the app's assumption), less one for each
    Duration passed (a Momentary spell's each round, so within a month),
    then into negative magnitudes by the month for a non-Ritual Momentary,
    Concentration or Diameter spell and by the year for any other, gone at
    -10 (HoH: TL p. 71; Hooks p. 83)."""
    full = magnitude(level)
    if months is None:
        return full
    halved = full // 2
    per = DURATION_MONTHS.get(duration, 0)
    if per:
        if months < halved * per:
            return halved - months // per
        months -= halved * per
    elif months == 0:
        return halved
    rate = 1 if duration in MONTHLY and not ritual else 12
    return max(GONE, -(months // rate))


def detectable(trace: int) -> bool:
    return trace > GONE


def acute_sense_ease(level: int) -> int:
    """Acute Sense's Ease Factor to notice a deception of a spell of
    `level` (HoH: TL p. 71): 6 + its magnitude."""
    return ACUTE_BASE + magnitude(level)


def trace_lines(case: Case) -> list[tuple[str, str]]:
    if case.trace_level is None:
        return []
    duration = case.trace_duration or "Momentary"
    ritual = " Ritual" if case.trace_ritual else ""
    now = trace_magnitude(
        case.trace_level, duration, case.trace_ritual, case.trace_months
    )
    months = case.trace_months
    if months is None:
        when = "still active"
    elif months == 0:
        when = "just ended"
    else:
        when = f"ended {months} month{'' if months == 1 else 's'} ago"
    seen = "still to be found" if detectable(now) else "gone"
    after = "a month" if duration in MONTHLY and not case.trace_ritual else "a year"
    return [
        (
            "Spell trace",
            f"a level {case.trace_level} {duration}{ritual} spell, {when}: its "
            f"trace is of magnitude {now}, {seen} (gone at {GONE}; HoH: TL p. 71)",
        ),
        (
            "Fading",
            f"half its magnitude {magnitude(case.trace_level)} when it ended, "
            "rounded down (the app's assumption: the books don't say), less "
            "one for each of its Durations that passes (a Momentary spell's "
            f"each round); past nothing, one {after} (HoH: TL p. 71)",
        ),
        (
            "Acute Sense",
            "to see deceptive magic over it: Perception + Penetration + stress "
            f"die against {acute_sense_ease(case.trace_level)}; taken twice, "
            "the Mastery score is added (HoH: TL p. 71)",
        ),
    ]


# -- Intrigue --

INFLUENCE = "influence"
LEARN = "learn"


@dataclass(frozen=True)
class Aim:
    key: str
    ease: int
    #: INFLUENCE (Presence + Intrigue) or LEARN (Communication + Intrigue).
    asks: str
    words: str


#: What Intrigue may seek and its Ease Factor (HoH: TL p. 24).
INTRIGUE_AIMS: tuple[Aim, ...] = (
    Aim("overt_goal", 6, LEARN, "learn someone's open political aim"),
    Aim("stay_course", 6, INFLUENCE, "keep someone on the course he follows"),
    Aim("allies", 9, LEARN, "learn someone's political allies"),
    Aim("suspicion", 9, INFLUENCE, "make someone suspicious"),
    Aim("delay", 9, INFLUENCE, "hold up what someone is doing"),
    Aim("meet_rival", 9, INFLUENCE, "bring someone to meet a rival"),
    Aim("hidden_agenda", 12, LEARN, "learn someone's unspoken agenda"),
    Aim("divide_allies", 12, INFLUENCE, "set wavering allies against each other"),
    Aim("change_course", 12, INFLUENCE, "change what someone means to do"),
    Aim("settle_minor", 12, INFLUENCE, "help rivals settle a small dispute"),
    Aim("silent_partners", 15, LEARN, "learn someone's hidden partners"),
    Aim("sever_alliance", 15, INFLUENCE, "break an alliance of trusted allies"),
    Aim("against_interest", 15, INFLUENCE, "lead someone to act against his own good"),
    Aim("settle_major", 15, INFLUENCE, "help rivals settle a great dispute"),
)

#: An Intrigue contest's margins and what each wins (HoH: TL p. 24).
CONTEST: tuple[tuple[int, str], ...] = (
    (3, "learn whether the other is a likely ally or foe; keep him on his course"),
    (6, "rattle him, draw out a small secret, or push him to a new course"),
    (
        9,
        "shame him in public, draw out a great secret, or have him betray a wavering alliance",
    ),
    (12, "lay bare all his secrets, or have him betray a trusted alliance"),
    (15, "have a magus act against the good of his own House"),
)

GIFT_PENALTY = 3
BLATANT_PENALTY = 6
#: Folk Ken through a Tribunal sways Intelligence + Intrigue by this much
#: either way (p. 25).
FOLK_KEN_LIMIT = 3


def aim(key: str) -> Aim | None:
    return next((a for a in INTRIGUE_AIMS if a.key == key), None)


def aim_options() -> list[tuple[str, str]]:
    return [(f"{a.words.capitalize()} ({a.ease})", a.key) for a in INTRIGUE_AIMS]


def contest_result(margin: int) -> str | None:
    """What a victor's margin wins in an Intrigue contest, or None below 3."""
    won = [words for floor, words in CONTEST if margin >= floor]
    return won[-1] if won else None


def folk_ken_bonus(bonus: int) -> int:
    """The storyguide's Folk Ken modifier, kept within -3 to +3."""
    return max(-FOLK_KEN_LIMIT, min(FOLK_KEN_LIMIT, bonus))


def gift_penalty(
    character: Character, *, both_under_parma: bool, blatant: bool = False
) -> int:
    """What The Gift takes from an Intrigue roll (HoH: TL p. 24): none
    when both parties are under Parma Magica, or for a Gentle Gift or
    none; else 3, or 6 for a Blatant Gift (the Flaw, or `blatant`)."""
    if both_under_parma:
        return 0
    ids = {vf.vf_id for vf in character.virtues_flaws}
    if "vf_gentle_gift" in ids:
        return 0
    if blatant or "vf_blatant_gift" in ids:
        return BLATANT_PENALTY
    if character.type == "magus" or "vf_the_gift" in ids:
        return GIFT_PENALTY
    return 0


def intrigue_total(
    character: Character,
    sought: Aim,
    *,
    both_under_parma: bool = True,
    blatant: bool = False,
) -> int:
    """Presence (to sway) or Communication (to learn) + Intrigue, less The
    Gift's penalty."""
    c = character.characteristics
    base = c.presence if sought.asks == INFLUENCE else c.communication
    return (
        base
        + sum(ability_score(character, "Intrigue"))
        - gift_penalty(character, both_under_parma=both_under_parma, blatant=blatant)
    )


def intrigue_lines(saga: Saga, case: Case) -> list[tuple[str, str]]:
    who = saga.character(case.intrigue_by) if case.intrigue_by else None
    sought = aim(case.intrigue_aim)
    if who is None or sought is None:
        return []
    using = "Presence" if sought.asks == INFLUENCE else "Communication"
    parma, blatant = case.intrigue_parma, case.intrigue_blatant
    total = intrigue_total(who, sought, both_under_parma=parma, blatant=blatant)
    cost = gift_penalty(who, both_under_parma=parma, blatant=blatant)
    if parma:
        gift = "The Gift costs nothing, both being under Parma Magica"
    elif cost:
        gift = f"The Gift costs {cost}, as not both are under Parma Magica"
    else:
        gift = "he has no Gift to cost him anything"
    return [
        (
            "Intrigue",
            f"{who.name} works to {sought.words}: {using} + Intrigue {total:+d} "
            f"+ stress die against {sought.ease}; {gift}, and Folk Ken through "
            "the Tribunal may give -3 to +3 (HoH: TL pp. 24-25)",
        )
    ]


# -- a case, and its form --


def case_lines(saga: Saga, case: Case) -> list[tuple[str, str]]:
    """What Hermetic law adds to a case's details, label and words."""
    lines: list[tuple[str, str]] = []
    if case.kind == WAR:
        lines += war_lines(saga, case)
    if case.kind == CHARGE:
        low = low_crime(case.charge)
        if low is not None:
            lines.append(
                ("Peripheral Code", f"a low crime: {low[0]} (HoH: TL {low[1]})")
            )
    lines += march_lines(case)
    lines += trace_lines(case)
    lines += intrigue_lines(saga, case)
    return lines


def case_problem(saga: Saga, case_id: str, values: dict[str, object]) -> str | None:
    """Why the case form's values can't be saved, for Hermetic law (the
    case's id, "" for a new one)."""
    if values.get("kind") == WAR:
        return war_problem(saga, case_id, values)
    level = values.get("trace_level")
    if isinstance(level, int) and level < 1:
        return "A spell's level is 1 or more."
    months = values.get("trace_months")
    if isinstance(months, int) and months < 0:
        return "Months since the spell ended can't be fewer than none."
    return None
