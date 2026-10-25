"""A town's court (City & Guild, Crime, pp. 28-30): the cases before it,
the quick roll that decides one, and the sentences a guilty man faces.

- The Court Roll decides a case quickly: a stress die + Communication +
  Civil and Canon Law (Common Law in England) against 6, rolled for the
  defendant or his proxy; success finds him innocent. It is a social
  interaction, so the arguer's Gift and other social Virtues and Flaws
  apply (p. 29): The Gift takes 3, a Blatant Gift 6, and an unGifted
  proxy avoids it (DE p. 204). The Ease Factor is 3 lower if he truly is
  innocent, 3 higher if the court thinks ill of him, 3 higher if most
  credible witnesses call him guilty. Civil Law, unlike Canon Law,
  weighs logic: Artes Liberales (logic) can shake a witness's credit
  (p. 29), which the storyguide decides.
- Town courts don't judge Church officials, commercial law or heresy:
  canon law does (p. 29).
- Sentences (p. 30): death for thievery, robbery, house-breaking, arson,
  premeditated murder and treason; a fine, from a few pence to 50-60
  pounds, for murder, accidental death, rape, assault, petty thievery and
  failing the charter's duties, an unpaid fine making him an outlaw;
  mutilation (an eye, ear or hand) or branding instead of or beside a
  fine; shaming in the stocks or pillory for minor crimes.

Kept in Neighbour.details: "court_cases", each a CourtCase."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Required, TypedDict, cast

from .commands import Command, Form, Refuse, SectionOps, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import aligned, escape
from .models import Character, Neighbour, Saga, details_list
from .neighbour_lists import KindBlock, KindList, KindTab, list_ops
from .rules import dice, scores
from .rules.supplement_work import gift_penalty
from .sections import COURT_CASES_SECTION, SENTENCES_SECTION

SOURCE = "City & Guild, Crime, pp. 28-30; Definitive Edition, The Gift, p. 204"
CG = "C&G"

#: The Court Roll's Ease Factor and what changes it (p. 29).
EASE = 6
INNOCENT = -3
BAD_NAME = 3
WITNESSES = 3

#: The law argued: its label and the Ability (p. 29).
LAWS: dict[str, tuple[str, str]] = {
    "civil": ("Civil and Canon Law", "Civil and Canon Law"),
    "common": ("Common Law (in England)", "Common Law"),
}

VERDICTS: tuple[str, ...] = ("Guilty", "Not guilty", "Dismissed")


@dataclass(frozen=True)
class Sentence:
    """A sentence: its name, when it is passed, and what it does."""

    name: str
    crimes: str
    effect: str


#: The sentences (p. 30), as a table of kinds and their effects.
SENTENCES: dict[str, Sentence] = {
    "death": Sentence(
        "Death",
        "For thievery, robbery, house-breaking, arson, premeditated murder and "
        "treason.",
        "Hanged, or beheaded, drowned or burned, in public; he may wait in "
        "prison for the next market day.",
    ),
    "fine": Sentence(
        "Fine",
        "For murder, accidental death, rape, assault, petty thievery and "
        "failing the charter's duties.",
        "From a few pence to 50-60 pounds, a burgess's lifetime; part goes to "
        "the victim. Unpaid, he is declared an outlaw anyone may kill.",
    ),
    "mutilation": Sentence(
        "Mutilation",
        "Instead of a fine or beside it; for a violent crime, picked to match it.",
        "The loss of an eye, an ear or a hand.",
    ),
    "branding": Sentence(
        "Branding",
        "Instead of a fine or beside it.",
        "A mark burned into him, borne for life.",
    ),
    "shaming": Sentence(
        "Shaming",
        "For minor crimes: prostitution, begging, petty thievery.",
        "The stocks or the pillory, for a time, in a public place.",
    ),
}


class CourtCase(TypedDict, total=False):
    """A case before the town's courts: the accused, the charge, who
    accuses him, which court, the verdict, the sentence (a SENTENCES key)
    and its detail, whether a fine is unpaid, and the roll that decided
    it."""

    accused: Required[str]
    charge: str
    accuser: str
    court: str
    verdict: str
    sentence: str
    detail: str
    unpaid: bool
    roll: str
    note: str


def cases(neighbour: Neighbour) -> list[CourtCase]:
    return cast(list[CourtCase], details_list(neighbour, "court_cases"))


def sentence_text(case: CourtCase) -> str:
    found = SENTENCES.get(case.get("sentence") or "")
    if found is None:
        return ""
    detail = case.get("detail", "")
    return f"{found.name}: {detail}" if detail else found.name


def outlawed(case: CourtCase) -> bool:
    """Whether an unpaid fine has made him an outlaw (p. 30)."""
    return (
        case.get("verdict") == "Guilty"
        and case.get("sentence") == "fine"
        and bool(case.get("unpaid"))
    )


# -- the Court Roll --


@dataclass(frozen=True)
class Plea:
    """The Court Roll's terms: who argues, the total added to the die, the
    Ease Factor, and each term, as words."""

    arguer: str
    total: int
    ease: int
    terms: tuple[str, ...]
    ease_terms: tuple[str, ...]
    logic: int | None


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def plea(saga: Saga, values: dict[str, Any]) -> Plea:
    """What the Court Roll adds to its die and the Ease Factor it beats,
    from the form's values: the arguer's Communication + the law, less his
    Gift's penalty, + other social Virtues and Flaws; the Ease Factor 6,
    -3 innocent, +3 a bad name, +3 the witnesses (p. 29)."""
    _label, ability = LAWS.get(values.get("law") or "civil", LAWS["civil"])
    character: Character | None = saga.character(values.get("arguer") or "")
    if character is not None:
        arguer = character.name
        communication = character.characteristics.communication
        level = scores.ability_level(character, ability)
        gift = gift_penalty(character)
        logic: int | None = scores.ability_level(character, "Artes Liberales")
    else:
        arguer = "A proxy"
        communication = _number(values.get("communication"))
        level = _number(values.get("law_score"))
        gift = 0
        logic = None
    social = _number(values.get("social"))
    terms = [f"Communication {communication:+d}", f"+ {ability} {level}"]
    if gift:
        terms.append(f"- The Gift {gift}")
    if social:
        sign = "+" if social > 0 else "-"
        terms.append(f"{sign} social Virtues and Flaws {abs(social)}")
    ease = EASE
    ease_terms = [str(EASE)]
    for key, change, words in (
        ("innocent", INNOCENT, "truly innocent"),
        ("bad_name", BAD_NAME, "a bad name"),
        ("witnesses", WITNESSES, "the witnesses"),
    ):
        if values.get(key):
            ease += change
            ease_terms.append(f"{change:+d} {words}")
    return Plea(
        arguer,
        communication + level - gift + social,
        ease,
        tuple(terms),
        tuple(ease_terms),
        logic if values.get("law") != "common" else None,
    )


def die_needed(total: int, ease: int) -> str:
    """The die a plea needs: "any roll" when the total already makes it."""
    need = ease - total
    return "any roll but a botch" if need <= 0 else f"{need} or more"


def roll_fields(saga: Saga) -> list[DialogField]:
    def proxy(values: dict[str, Any]) -> bool:
        return not values.get("arguer")

    return [
        DialogField(
            "arguer",
            "Who pleads",
            "select",
            None,
            options=[(escape(c.name), c.id) for c in saga.characters],
            allow_blank=True,
            placeholder="(the defendant or a proxy without a sheet)",
            hint="The defendant, or his proxy: an unGifted proxy spares him "
            "The Gift's penalty.",
        ),
        DialogField("communication", "Communication", "optint", 0, show_if=proxy),
        DialogField("law_score", "His score in the law", "optint", 0, show_if=proxy),
        DialogField(
            "law",
            "Law argued",
            "select",
            "civil",
            options=[(label, key) for key, (label, _) in LAWS.items()],
            required=True,
        ),
        DialogField(
            "social",
            "Other social Virtues and Flaws",
            "optint",
            None,
            hint="The arguer's, as a + or -; The Gift is counted already.",
        ),
        DialogField("innocent", "He truly is innocent", "check", False),
        DialogField("bad_name", "A bad name in this court", "check", False),
        DialogField(
            "witnesses",
            "Witnesses say guilty",
            "check",
            False,
            hint="Most credible witnesses declare him guilty.",
        ),
    ]


def roll_live(saga: Saga, case: CourtCase) -> Any:
    def live(values: dict[str, Any]) -> str:
        p = plea(saga, values)
        lines = [
            f"[b]{escape(case['accused'])}[/]  [$label]"
            f"{escape(case.get('charge') or 'charged')}[/]",
            f"[i]{escape(p.arguer)} pleads for him before the "
            f"{escape(court_name(case))}.[/]",
            f"Stress die + [b]{p.total}[/] [dim]= {' '.join(p.terms)}[/]",
            f"Against [b]{p.ease}[/]"
            + (f" [dim]= {' '.join(p.ease_terms)}[/]" if len(p.ease_terms) > 1 else ""),
            f"Innocent on a die of [b]{die_needed(p.total, p.ease)}[/]; below it, "
            f"guilty [dim]({CG} p. 29)[/].",
        ]
        if p.logic is not None:
            lines.append(
                f"[dim]Civil Law weighs logic: his Artes Liberales {p.logic} may "
                "shake a witness's credit, if the storyguide allows.[/]"
            )
        return "\n".join(lines)

    return live


def court_name(case: CourtCase) -> str:
    court = (case.get("court") or "Town").strip()
    return "town court" if court.casefold() == "town" else f"{court} court"


def court_roll(
    saga: Saga, neighbour: Neighbour, index: int, rng: random.Random | None = None
) -> Command:
    """More's Court Roll on the chosen case: the roll that decides it
    (p. 29), kept as its verdict."""
    listed = cases(neighbour)
    if index >= len(listed):
        return Refuse("Court Roll", "Choose a case first.")
    case = listed[index]
    if case.get("verdict"):
        return Refuse(
            "Court Roll",
            f"{escape(case['accused'])} was found {case.get('verdict', '').lower()} already: "
            "edit the case to clear its verdict and hear it again.",
        )

    def apply(values: dict[str, Any]) -> list[str]:
        p = plea(saga, values)
        die = dice.stress_die(rng or random.Random(), saga=saga)
        roll = dice.Roll(p.total, die, p.ease)
        shown = "a botch" if die.botched else str(die.value)
        innocent = bool(roll.succeeded)
        case["verdict"] = "Not guilty" if innocent else "Guilty"
        case["roll"] = (
            f"{saga.current_season} {saga.current_year}: {p.arguer} pleaded; die "
            f"{shown} + {p.total} = {roll.total} against {p.ease}"
        )
        return notes(
            f"{escape(case['accused'])}: the die shows {shown}, + {p.total} = "
            f"{roll.total} against {p.ease}.",
            "The court finds him innocent."
            if innocent
            else "The court finds him guilty: edit the case to pass sentence "
            f"({CG} p. 30).",
        )

    return Form(
        f"Court Roll: {escape(case['accused'])}",
        lambda: roll_fields(saga),
        apply,
        live=roll_live(saga, case),
        save_label="Roll",
        help_id=COURT_CASES_SECTION,
        inspector="The Verdict",
    )


# -- the Cases list --


def cases_title(_saga: Saga, neighbour: Neighbour) -> str:
    return f"Cases ({len(cases(neighbour))})"


def cases_grid(_saga: Saga, neighbour: Neighbour) -> Grid:
    rows, styles = [], {}
    for i, case in enumerate(cases(neighbour)):
        verdict = case.get("verdict") or ""
        rows.append(
            [
                case["accused"],
                case.get("charge", ""),
                case.get("court") or "Town",
                verdict or "to be heard",
                sentence_text(case) + (", unpaid" if outlawed(case) else ""),
            ]
        )
        if verdict == "Guilty":
            styles[(i, 3)] = "$text-error"
        elif verdict:
            styles[(i, 3)] = "$text-success"
        if outlawed(case):
            styles[(i, 4)] = "$text-error"
    return Grid(
        ["Accused", "Charge", "Court", "Verdict", "Sentence"],
        rows,
        list(range(len(rows))),
        "No cases before the town's courts.",
        styles=styles,
        caps=[24, 26, 9, 11, 0],
    )


def case_info(_saga: Saga, neighbour: Neighbour, row: int) -> str:
    listed = cases(neighbour)
    if row >= len(listed):
        return ""
    case = listed[row]
    lines = [
        f"[i]{escape(case.get('charge') or 'A charge')}, before the "
        f"{escape(court_name(case))}[/]"
    ]
    if case.get("accuser"):
        lines.append(f"[$label]Accuser:[/] {escape(case.get('accuser', ''))}")
    verdict = case.get("verdict") or ""
    if verdict:
        tone = "$text-error" if verdict == "Guilty" else "$text-success"
        lines.append(f"[$label]Verdict:[/] [{tone}]{verdict}[/]")
        if case.get("roll"):
            lines.append(f"[dim]{escape(case.get('roll', ''))}[/]")
    else:
        lines.append(
            "[$label]Verdict:[/] to be heard. More, Court Roll: Communication + "
            f"Civil and Canon Law against 6 [dim]({CG} p. 29)[/]."
        )
    found = SENTENCES.get(case.get("sentence") or "")
    if found is not None:
        detail = case.get("detail", "")
        lines.append(
            f"[$label]Sentence:[/] [b]{found.name}[/]"
            + (f", {escape(detail)}" if detail else "")
            + f". [dim]{found.effect} ({CG} p. 30)[/]"
        )
    if outlawed(case):
        lines.append("[$text-error]His fine is unpaid: he is an outlaw.[/]")
    if case.get("note"):
        lines.append(escape(case.get("note", "")))
    return "\n".join(lines)


def case_fields(
    _saga: Saga, _neighbour: Neighbour, case: CourtCase | None
) -> list[DialogField]:
    c = case or {}

    def guilty(values: dict[str, Any]) -> bool:
        return values.get("verdict") == "Guilty"

    def fined(values: dict[str, Any]) -> bool:
        return guilty(values) and values.get("sentence") == "fine"

    return [
        DialogField("accused", "Accused", "text", c.get("accused", ""), required=True),
        DialogField("charge", "Charge", "text", c.get("charge", "")),
        DialogField(
            "accuser",
            "Accuser",
            "text",
            c.get("accuser", ""),
            hint="Not always the victim: a kinsman accuses for the dead (p. 29).",
        ),
        DialogField(
            "court",
            "Court",
            "text",
            c.get("court", "Town"),
            hint="The town court, or another: churchmen, commercial law and "
            "heresy go to the Church's courts (p. 29).",
        ),
        DialogField(
            "verdict",
            "Verdict",
            "select",
            c.get("verdict") or None,
            options=pairs(VERDICTS),
            allow_blank=True,
            placeholder="(to be heard)",
        ),
        DialogField(
            "sentence",
            "Sentence",
            "select",
            c.get("sentence") or None,
            options=[(s.name, key) for key, s in SENTENCES.items()],
            allow_blank=True,
            placeholder="(none yet)",
            show_if=guilty,
        ),
        DialogField(
            "detail",
            "Sentence in detail",
            "text",
            c.get("detail", ""),
            placeholder="e.g. 3 pounds, the right hand",
            show_if=guilty,
        ),
        DialogField(
            "unpaid",
            "The fine is unpaid",
            "check",
            bool(c.get("unpaid")),
            hint="An unpaid fine makes him an outlaw (p. 30).",
            show_if=fined,
        ),
        DialogField("note", "Note", "text", c.get("note", "")),
    ]


def case_ops(saga: Saga, neighbour: Neighbour) -> SectionOps:
    return list_ops(
        saga, neighbour, "court_cases", "Case", case_fields, lambda c: c["accused"]
    )


# -- the Sentences block --


def sentences_text(_saga: Saga, _neighbour: Neighbour) -> str:
    return (
        aligned(
            [(s.name, f"{s.effect} [dim]{s.crimes}[/]") for s in SENTENCES.values()]
        )
        + f"\n[dim]A defendant who insists he is innocent may choose a trial by "
        f"ordeal, which many charters limit or ban ({CG} p. 30).[/]"
    )


COURT_TAB = KindTab(
    "Court",
    "tab-nb-court",
    (KindList(COURT_CASES_SECTION, cases_title, cases_grid, case_ops, case_info),),
    blocks=(
        KindBlock(
            SENTENCES_SECTION, "Sentences", sentences_text, after=COURT_CASES_SECTION
        ),
    ),
    icon="tribunal",
    panel="[dim]Choose a case to see its verdict.[/]",
)
