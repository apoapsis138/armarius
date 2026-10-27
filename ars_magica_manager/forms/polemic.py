"""A Tribunal's Arguments tab, for either front-end: its arguments, the
chosen argument's reach, Argument Total and debate bonus, and its texts,
each with Add, Edit and Delete (commands.SectionOps), and More's
Circulate a Text (Transforming Mythic Europe pp. 27-35; the rules are
rules.polemic's, read against the saga by polemic.py).

The chosen argument is the front-end's to keep: each builder takes a
`Chosen` (its index, or None for the first), as the Mystery Cults tab's
do (the Strategy the two front-ends share is these builders; what they
draw is theirs)."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from .. import polemic as pl
from .. import sourcebooks
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, attr, pairs
from ..grids import Grid
from ..markup import escape
from ..models import (
    CASE_OPEN,
    SEASONS,
    TEXT_KINDS,
    Argument,
    Character,
    PolemicText,
    Saga,
    Tribunal,
)
from ..models.polemic import AGAINST, AUDIENCES, DIATRIBE, FOR, LOST, POLEMIC, WON
from ..mystery_cults import numeral
from ..rules import dice
from ..rules import polemic as rules
from ..sections import ARGUMENT_TEXTS_SECTION, ARGUMENTS_SECTION
from ..tribunal_packages import LedgerCard

#: The book, as the texts cite it.
TME = "TME"

#: The chosen row of a list, as the front-end keeps it (None: none).
Chosen = Callable[[], int | None]

CIRCULATE_TITLE = "Circulate a Text"
#: The form's own help page.
CIRCULATE_HELP = "circulate-text"

#: The terminal lists' column widths (the last takes what is left).
ARGUMENT_CAPS = [48, 12, 12, 0]
TEXT_CAPS = [9, 22, 32, 0]

REACH_OPTIONS: list[tuple[str, str]] = [
    ("A magus (3, or his Reputation)", "magus"),
    ("A covenant (6)", "covenant"),
    ("A Tribunal (9)", "tribunal"),
    ("A House (12)", "house"),
    ("The Order (15)", "order"),
]

SIDE_OPTIONS: list[tuple[str, str]] = [
    ("The case or motion (its prosecutor or proposer)", FOR),
    ("The defence, against it", AGAINST),
]

OUTCOME_OPTIONS: list[tuple[str, str]] = [
    ("Not yet debated", ""),
    ("Won: its bonus carries to later Tribunals", WON),
    ("Lost: its bonus is gone", LOST),
]

#: What a debate's outcome means for the argument (TME p. 35).
OUTCOME_WORDS = {
    WON: "won: its bonus carries to later Tribunals",
    LOST: "lost: its bonus is gone",
}

RULE_TEXT = (
    "Argument Total = the polemic's Quality − the Prevailing Wisdom, + each "
    "circulated apologia's Quality, − each diatribe's. At Tribunal it buys a "
    "bonus (or penalty) as experience on the Art table: 1 for +1, 3 for +2, "
    "6 for +3, 10 for +4."
)
CARRY_TEXT = (
    f"Won, the bonus carries to later Tribunals; lost, it is gone ({TME} pp. 29-35)."
)
CIRCULATION_TEXT = (
    "Circulation: each season, Reputation + the text's level (a tractatus "
    "counts 5) + a simple die + 1 for each season already spent, against 15 "
    f"for a Tribunal, 18 a House, 24 the Order ({TME} p. 29)."
)


# -- what is chosen --


def _at[T](entries: list[T], index: int | None) -> T | None:
    return entries[index] if index is not None and 0 <= index < len(entries) else None


def chosen_argument(tribunal: Tribunal, chosen: Chosen) -> Argument | None:
    """The argument chosen, or the first when none is (the tab opens on
    it)."""
    found = _at(tribunal.arguments, chosen())
    return found or (tribunal.arguments[0] if tribunal.arguments else None)


# -- the Arguments list --


def arguments_title(tribunal: Tribunal) -> str:
    return f"Arguments ({len(tribunal.arguments)})"


def reach_words(argument: Argument) -> str:
    """ "Tribunal 9"."""
    return f"{argument.reach.title()} {pl.wisdom(argument)}"


def total_words(saga: Saga, argument: Argument) -> str:
    """ "−7: −3" (the total and the bonus it buys), "lost", or "not out"."""
    total = pl.total(saga, argument)
    if total is None:
        return "not out"
    if argument.outcome == LOST:
        return f"{pl.signed(total)}: lost"
    return f"{pl.signed(total)}: {pl.signed(pl.bonus(saga, argument))}"


def _tone(saga: Saga, argument: Argument) -> str:
    """The palette key the argument's total is drawn in."""
    total = pl.total(saga, argument)
    if argument.outcome == LOST:
        return "text-error"
    if total is None or pl.bonus(saga, argument) <= 0:
        return "text-warning"
    return "text-success"


def arguments_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, argument in enumerate(tribunal.arguments):
        styles[(index, 3)] = f"${_tone(saga, argument)}"
        rows.append(
            [
                argument.topic,
                reach_words(argument),
                pl.name_of(saga, argument.proponent_id, ""),
                total_words(saga, argument),
            ]
        )
    return Grid(
        ["Argument", "Reach", "Proponent", "Total: debate"],
        rows,
        list(range(len(rows))),
        "No argument yet: Add one, then its polemic as a text.",
        styles,
        caps=ARGUMENT_CAPS,
    )


def _meeting_words(tribunal: Tribunal, argument: Argument) -> str:
    """ "for the Tribunal of 1221", or the case it goes to."""
    case = pl.case_of(tribunal, argument)
    if case is not None and case.status != CASE_OPEN:
        return f"debated: {case.title}"
    if tribunal.next_year is None:
        return "for no meeting set yet"
    return f"for the Tribunal of {tribunal.next_year}"


def argument_cards(saga: Saga, tribunal: Tribunal) -> list[LedgerCard]:
    """The arguments as the desktop rules them off on the page."""
    cards = []
    for index, argument in enumerate(tribunal.arguments):
        total = pl.total(saga, argument)
        if argument.outcome == LOST:
            badge = "lost in debate"
        elif total is None:
            badge = "polemic not out"
        else:
            badge = f"{pl.signed(pl.bonus(saga, argument))} in debate"
        cards.append(
            LedgerCard(
                title=argument.topic,
                meta=_meeting_words(tribunal, argument),
                badge=(badge, _tone(saga, argument)),
                rubric=numeral(index),
            )
        )
    return cards


# -- the chosen argument --


def argument_title(tribunal: Tribunal, chosen: Chosen) -> str:
    found = chosen_argument(tribunal, chosen)
    return found.topic if found is not None else "No argument chosen"


def formula(saga: Saga, argument: Argument) -> str:
    """ "11 − 9 − 9 = −7": the circulated texts' Qualities worked into the
    Argument Total."""
    polemic = pl.polemic_of(argument)
    if polemic is None or not polemic.circulated:
        return "none yet: its polemic isn't circulated"
    wisdom = pl.wisdom(argument)
    parts = [str(pl.quality(saga, polemic)), f"− {wisdom}"]
    for text in argument.texts:
        if text is polemic or not text.circulated:
            continue
        mark = "−" if text.kind == DIATRIBE else "+"
        parts.append(f"{mark} {pl.quality(saga, text)}")
    total = pl.total(saga, argument)
    return f"{' '.join(parts)} = {pl.signed(total or 0)}"


def _debated(tribunal: Tribunal, argument: Argument) -> str:
    case = pl.case_of(tribunal, argument)
    words = f"{case.title}, " if case is not None else "no case or motion chosen yet, "
    if case is not None and case.status != CASE_OPEN:
        words = f"{case.title} (heard)"
    elif tribunal.next_year is not None:
        words += f"at the Tribunal of {tribunal.next_season} {tribunal.next_year}"
    else:
        words += "at no meeting set yet"
    if argument.outcome:
        words += f"; {OUTCOME_WORDS[argument.outcome]}"
    return words


def argument_facts(
    saga: Saga, tribunal: Tribunal, argument: Argument
) -> list[tuple[str, str]]:
    """The chosen argument's facts: its reach, proponent, Argument Total,
    what it does in debate, what its next text would change, and where
    it is debated."""
    wisdom = pl.wisdom(argument)
    bonus = pl.bonus(saga, argument)
    if argument.outcome == LOST:
        in_debate = "nothing: the debate on it was lost"
    elif pl.total(saga, argument) is None:
        in_debate = "nothing until its polemic is out"
    elif bonus:
        side = "proponent's" if argument.side == FOR else "defence's"
        in_debate = f"{pl.signed(bonus)} to every Attack and Defense ({side})"
    else:
        in_debate = "no bonus"
    facts = [
        ("Reach", f"{rules.REACH_NAMES[argument.reach]}: Prevailing Wisdom {wisdom}"),
        ("Proponent", pl.name_of(saga, argument.proponent_id)),
        ("Argument Total", formula(saga, argument)),
        ("In debate", in_debate),
    ]
    waiting = next((t for t in argument.texts if not t.circulated), None)
    if waiting is not None:
        after = pl.total_if(saga, argument, waiting)
        name = pl.KIND_NAMES[waiting.kind].lower()
        facts.append(
            (
                f"If the {name} circulates",
                "its polemic must be out first"
                if after is None
                else f"{pl.signed(after)}: {pl.signed(rules.debate_bonus(after))}",
            )
        )
    facts.append(("Debated", _debated(tribunal, argument)))
    return facts


def argument_text(saga: Saga, tribunal: Tribunal, chosen: Chosen) -> str:
    """The chosen argument's section on the terminal: its facts, three on
    a line, then the rule."""
    argument = chosen_argument(tribunal, chosen)
    if argument is None:
        return "[$label]Add an argument to follow its texts and its total.[/]"
    facts = [
        f"[$label]{escape(k)}:[/] {escape(v)}"
        for k, v in argument_facts(saga, tribunal, argument)
    ]
    lines = ["  ·  ".join(facts[:3]), "  ·  ".join(facts[3:])]
    return "\n".join(lines) + "\n\n" + rule_text()


def rule_text() -> str:
    """How the total is worked and spent, as markup."""
    return f"{escape(RULE_TEXT)}\n[dim]{escape(CARRY_TEXT)}[/]"


# -- the texts --


def texts_title(tribunal: Tribunal, chosen: Chosen) -> str:
    argument = chosen_argument(tribunal, chosen)
    return f"Texts ({len(argument.texts) if argument is not None else 0})"


def circulation_words(text: PolemicText) -> str:
    """ "Circulated Summer 1219", "Circulating: 1 season", "Not out"."""
    if text.circulated:
        when = f"{text.circulated_season} {text.circulated_year or ''}".strip()
        return f"Circulated {when}".strip()
    if text.seasons_spent:
        plural = "" if text.seasons_spent == 1 else "s"
        return f"Circulating: {text.seasons_spent} season{plural}"
    return "Not out"


def _text_tone(text: PolemicText) -> str:
    if not text.circulated:
        return "text-warning"
    return "text-error" if text.kind == DIATRIBE else "text-success"


def texts_grid(saga: Saga, tribunal: Tribunal, chosen: Chosen) -> Grid:
    argument = chosen_argument(tribunal, chosen)
    texts = argument.texts if argument is not None else []
    rows = []
    styles: dict[tuple[int, int], str] = {}
    for index, text in enumerate(texts):
        styles[(index, 3)] = f"${_text_tone(text)}"
        rows.append(
            [
                pl.KIND_NAMES[text.kind],
                _author_words(saga, text),
                pl.book_words(saga, text),
                circulation_words(text),
            ]
        )
    return Grid(
        ["Kind", "Author", "Book", "Circulation"],
        rows,
        list(range(len(rows))),
        "No text yet: Add the polemic, a summa or tractatus in the library."
        if argument is not None
        else "Add an argument first.",
        styles,
        caps=TEXT_CAPS,
    )


def _author_words(saga: Saga, text: PolemicText) -> str:
    """ "Corvinus", or "Corvinus (by Matthaios)" when a sponsor circulates
    it."""
    author = pl.name_of(saga, text.author_id, "(no author)")
    sponsor = saga.character(text.circulated_by_id)
    if sponsor is not None and sponsor.id != text.author_id:
        return f"{author} (by {sponsor.name})"
    return author


def _short(character: Character | None) -> str:
    return character.name.split(" ")[0] if character is not None else "Its author"


def _held(saga: Saga, argument: Argument, text: PolemicText) -> str:
    """ "Benedek has Opposed to Charters 1.": the Reputation the text gave
    its author, as he holds it now; "" when he doesn't."""
    author = pl.author(saga, text)
    name = rules.reputation_name(text.kind, argument.ideal or argument.topic)
    if author is None:
        return ""
    found = next(
        (r for r in author.reputations if r.name.casefold() == name.casefold()), None
    )
    return f"{_short(author)} has {name} {abs(found.score)}." if found else ""


def text_effect(saga: Saga, argument: Argument, text: PolemicText) -> str:
    """What the text does to the Argument Total, or how its circulation
    stands, in words."""
    quality = pl.quality(saga, text)
    if text.circulated:
        if text.kind == POLEMIC:
            words = (
                f"Its Quality {quality} less the Prevailing Wisdom "
                f"{pl.wisdom(argument)} starts the Argument Total."
            )
        elif text.kind == DIATRIBE:
            words = f"Subtracts its Quality: −{quality}."
        else:
            words = f"Adds its Quality: +{quality}."
        return escape(f"{words} {_held(saga, argument, text)}".strip())
    lines = []
    if rules.needs_study(text.kind) and not text.studied:
        lines.append(
            f"[$text-warning]{escape(_short(pl.author(saga, text)))} must first "
            f"spend a season studying the work it answers ({TME} p. 31).[/]"
        )
    who = pl.circulator(saga, text)
    reputation = rules.circulation_reputation(who)
    total = rules.circulation_total(
        reputation, pl.level(saga, text), text.seasons_spent, text.bundled
    )
    need = max(1, rules.ease_factor(text.audience) - total)
    lines.append(
        f"Next season: Reputation {reputation} + level {pl.level(saga, text)} + "
        f"{text.seasons_spent} for seasons spent + {text.bundled} bound with it "
        f"= {total} + simple die against {rules.ease_factor(text.audience)}: "
        f"the die must show {need} or more."
    )
    after = pl.total_if(saga, argument, text)
    if after is not None:
        lines.append(
            f"Once out, {'−' if text.kind == DIATRIBE else '+'}{quality}: the "
            f"Argument Total becomes {pl.signed(after)}."
        )
    return "\n".join(lines)


def text_info(saga: Saga, tribunal: Tribunal, chosen: Chosen, row: int | None) -> str:
    """The chosen text in full, for the details panel and the inspector."""
    argument = chosen_argument(tribunal, chosen)
    text = _at(argument.texts, row) if argument is not None else None
    if argument is None or text is None:
        return "[dim]Choose a text.[/]"
    head = "  ·  ".join(
        (
            f"[b]{pl.KIND_NAMES[text.kind]}[/]",
            escape(_author_words(saga, text)),
            escape(pl.book_words(saga, text)),
        )
    )
    lines = [head, text_effect(saga, argument, text)]
    if text.note.strip():
        lines.append(escape(text.note.strip()))
    lines += ["", f"[dim]{escape(CIRCULATION_TEXT)}[/]"]
    return "\n".join(lines)


def argument_info(saga: Saga, tribunal: Tribunal, row: int | None) -> str:
    """An argument in full, for the details panel when its row is chosen."""
    argument = _at(tribunal.arguments, row)
    if argument is None:
        return "[dim]Choose a text.[/]"
    facts = argument_facts(saga, tribunal, argument)
    lines = [f"[b]{escape(argument.topic)}[/]"]
    lines += [f"[$label]{escape(k)}:[/] {escape(v)}" for k, v in facts]
    return "\n".join(lines)


def text_cards(saga: Saga, tribunal: Tribunal, chosen: Chosen) -> list[LedgerCard]:
    """The chosen argument's texts as the desktop rules them off."""
    argument = chosen_argument(tribunal, chosen)
    if argument is None:
        return []
    return [
        LedgerCard(
            title=f"{pl.KIND_NAMES[t.kind]}: {pl.book_words(saga, t)}",
            meta=f"{_author_words(saga, t)}, Quality {pl.quality(saga, t)}",
            badge=(circulation_words(t), _text_tone(t)),
            body=text_effect(saga, argument, t),
            rubric="−" if t.kind == DIATRIBE else "+",
        )
        for t in argument.texts
    ]


# -- Add, Edit and Delete an argument --


def _magi_options(saga: Saga) -> list[tuple[str, str]]:
    magi = [c for c in saga.characters if c.type == "magus"]
    others = [c for c in saga.characters if c.type != "magus"]
    return [(escape(c.name), c.id) for c in (*magi, *others)]


def _case_options(tribunal: Tribunal) -> list[tuple[str, str]]:
    return [(escape(c.title), c.id) for c in tribunal.cases if c.status == CASE_OPEN]


def argument_fields(
    saga: Saga, tribunal: Tribunal, argument: Argument | None
) -> list[DialogField]:
    """An argument: its topic and ideal, its reach, its proponent, the
    Ability its texts are written on, and the case it goes to."""
    case_options = _case_options(tribunal)
    abilities = pl.knowledge_abilities()
    if argument is not None and argument.ability not in abilities:
        abilities.append(argument.ability)
    found = pl.case_of(tribunal, argument) if argument is not None else None
    if found is not None and found.status != CASE_OPEN:
        case_options.append((escape(found.title), found.id))
    fields = [
        DialogField(
            "topic",
            "Argument",
            "text",
            attr(argument, "topic", ""),
            required=True,
            placeholder="e.g. Covenants may hold charters from mundane lords",
        ),
        DialogField(
            "ideal",
            "Its ideal",
            "text",
            attr(argument, "ideal", ""),
            placeholder="e.g. Charters",
            hint="Its texts' Reputations: Supporter of (ideal) for a polemic or "
            "apologia, Opposed to (ideal) for a diatribe.",
        ),
        DialogField(
            "reach",
            "It concerns",
            "select",
            attr(argument, "reach", "tribunal"),
            options=REACH_OPTIONS,
            required=True,
            hint=f"The Prevailing Wisdom ({TME} p. 29).",
        ),
        DialogField(
            "magus_reputation",
            "His Reputation",
            "int",
            attr(argument, "magus_reputation", 0),
            hint="The magus's Reputation, if it is higher than 3.",
            show_if=lambda v: v.get("reach") == "magus",
        ),
        DialogField(
            "proponent_id",
            "Proponent",
            "select",
            attr(argument, "proponent_id", None),
            options=_magi_options(saga),
            allow_blank=True,
            placeholder="(not chosen)",
        ),
        DialogField(
            "ability",
            "Written on",
            "select",
            attr(argument, "ability", rules.SUGGESTED_ABILITIES[0]),
            options=pairs(abilities),
            required=True,
            hint="Any knowledge Ability; the book suggests the first three, Area "
            "Lore with the troupe's agreement (p. 28). Every text on the "
            "argument is written on it.",
        ),
        DialogField(
            "case_id",
            "Goes to",
            "select",
            attr(argument, "case_id", "") or None,
            options=case_options,
            allow_blank=True,
            placeholder="(no case or motion yet)",
            hint="The case or motion on the Docket where it is debated.",
        ),
        DialogField(
            "side",
            "It backs",
            "select",
            attr(argument, "side", FOR),
            options=SIDE_OPTIONS,
            required=True,
            hint="A case or motion hears one argument for each side.",
        ),
    ]
    if argument is not None:
        fields.append(
            DialogField(
                "outcome",
                "Last debate",
                "select",
                argument.outcome,
                options=OUTCOME_OPTIONS,
                hint="Set when a debate on it is held; won, its bonus carries "
                f"on; lost, it is gone ({TME} p. 35).",
            )
        )
    return fields


def argument_problem(
    tribunal: Tribunal, argument: Argument | None, values: dict[str, Any]
) -> str | None:
    """Why the argument can't be saved: a negative Reputation, or a case
    that already hears an argument for the side it backs (one Argument
    Total each side, TME pp. 31, 33)."""
    if (values.get("magus_reputation") or 0) < 0:
        return "A Reputation is 0 or more."
    case_id = values.get("case_id") or ""
    side = values.get("side") or FOR
    rival = pl.rival(tribunal, argument, case_id, side)
    if rival is not None:
        case = pl.case_of(tribunal, rival)
        title = case.title if case is not None else "That case"
        backs = "for it" if side == FOR else "against it"
        return (
            f"{escape(title)} already hears {escape(rival.topic)} {backs}: a "
            f"case takes one argument for each side ({TME} pp. 31, 33). Answer "
            "it with a diatribe or apologia instead."
        )
    return None


def _set_argument(argument: Argument, values: dict[str, Any]) -> None:
    argument.topic = values["topic"].strip()
    argument.ideal = (values.get("ideal") or "").strip()
    argument.reach = values.get("reach") or "tribunal"
    argument.magus_reputation = (
        values.get("magus_reputation") or 0 if argument.reach == "magus" else 0
    )
    argument.proponent_id = values.get("proponent_id") or None
    argument.ability = values.get("ability") or rules.SUGGESTED_ABILITIES[0]
    argument.case_id = values.get("case_id") or ""
    argument.side = values.get("side") or FOR
    argument.outcome = values.get("outcome", argument.outcome) or ""


def argument_form(saga: Saga, tribunal: Tribunal, argument: Argument | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        if argument is None:
            fresh = Argument(values["topic"])
            _set_argument(fresh, values)
            tribunal.arguments.append(fresh)
        else:
            _set_argument(argument, values)

    return Form(
        "Add Argument" if argument is None else "Edit Argument",
        lambda: argument_fields(saga, tribunal, argument),
        apply,
        validate=lambda values: argument_problem(tribunal, argument, values),
        save_label="Add" if argument is None else "Save",
        help_id=ARGUMENTS_SECTION,
    )


def arguments_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    arguments = tribunal.arguments

    def remove(index: int) -> Command:
        argument = arguments[index]

        def delete() -> None:
            arguments.remove(argument)

        return Confirm(
            f"Delete the argument {escape(argument.topic)}?\n\nIts texts stay "
            "in the library; only the argument and their links go.",
            delete,
        )

    return SectionOps(
        add=lambda: argument_form(saga, tribunal, None),
        edit=lambda index: argument_form(saga, tribunal, arguments[index]),
        remove=remove,
        rows=lambda: [a.topic for a in arguments],
    )


def argument_ops(saga: Saga, tribunal: Tribunal, chosen: Chosen) -> SectionOps:
    """The chosen argument's section: Edit Argument."""

    def edit(_row: int) -> Form | Refuse:
        found = chosen_argument(tribunal, chosen)
        if found is None:
            return Refuse("Edit Argument", "Add an argument first.")
        return argument_form(saga, tribunal, found)

    return SectionOps(edit=edit, rows=lambda: [argument_title(tribunal, chosen)])


# -- Add, Edit and Delete a text --


def _book_options(saga: Saga) -> list[tuple[str, str]]:
    found = []
    for book in pl.text_books(saga):
        on = book.ability or book.art or "?"
        q = f"Q{book.quality}" if book.quality is not None else "Q?"
        kind = "tractatus" if book.type == "Tractatus" else f"summa L{book.level or 0}"
        found.append((escape(f"{book.name} ({kind}, {on} {q})"), book.id))
    return found


def _studied_hint(values: dict[str, Any]) -> bool:
    return rules.needs_study(values.get("kind") or POLEMIC)


def text_fields(
    saga: Saga, argument: Argument, text: PolemicText | None
) -> list[DialogField]:
    """A text: what it is, the book it is, its author, and how its
    circulation stands."""
    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            attr(
                text, "kind", POLEMIC if pl.polemic_of(argument) is None else DIATRIBE
            ),
            options=[(pl.KIND_NAMES[k], k) for k in TEXT_KINDS],
            required=True,
            hint="A polemic sets the argument out; a diatribe attacks it, an "
            f"apologia defends it ({TME} p. 28).",
        ),
        DialogField(
            "book_id",
            "Book",
            "select",
            attr(text, "book_id", None),
            options=_book_options(saga),
            required=True,
            hint=f"A summa or tractatus on {escape(argument.ability)} in the "
            "saga's library; a tractatus counts as level 5.",
        ),
        DialogField(
            "author_id",
            "Author",
            "select",
            attr(text, "author_id", None),
            options=_magi_options(saga),
            allow_blank=True,
            placeholder="(the book's author)",
        ),
        DialogField(
            "studied",
            "Studied the work it answers",
            "check",
            attr(text, "studied", False),
            hint=f"A season studying the polemic or diatribe first ({TME} pp. 31, 35).",
            show_if=_studied_hint,
        ),
        DialogField(
            "audience",
            "Circulated to",
            "select",
            attr(text, "audience", "tribunal"),
            options=_audience_options(),
            required=True,
        ),
        DialogField(
            "circulated_by_id",
            "Circulated by",
            "select",
            attr(text, "circulated_by_id", None),
            options=_magi_options(saga),
            allow_blank=True,
            placeholder="(its author)",
            hint="A sponsor may circulate it with his own Reputation (p. 29).",
        ),
        DialogField(
            "seasons_spent",
            "Seasons spent circulating",
            "int",
            attr(text, "seasons_spent", 0),
        ),
        DialogField(
            "bundled",
            "New works bound with it",
            "int",
            attr(text, "bundled", 0),
            hint="A Lab Text or another new item in every copy: +1 each (p. 30).",
        ),
        DialogField(
            "circulated", "Circulated", "check", attr(text, "circulated", False)
        ),
        DialogField(
            "circulated_season",
            "Out since (season)",
            "select",
            attr(text, "circulated_season", "") or None,
            options=pairs(SEASONS),
            allow_blank=True,
            show_if=lambda v: bool(v.get("circulated")),
        ),
        DialogField(
            "circulated_year",
            "Out since (year)",
            "optint",
            attr(text, "circulated_year", None),
            show_if=lambda v: bool(v.get("circulated")),
        ),
        DialogField("note", "Note", "text", attr(text, "note", "")),
    ]


def _audience_options() -> list[tuple[str, str]]:
    return [
        (
            f"{rules.AUDIENCE_NAMES[a][0].upper()}{rules.AUDIENCE_NAMES[a][1:]}: "
            f"{rules.copies(a)} copies, EF {rules.ease_factor(a)}",
            a,
        )
        for a in AUDIENCES
    ]


def text_problem(
    saga: Saga, argument: Argument, text: PolemicText | None, values: dict[str, Any]
) -> str | None:
    """Why the text can't be saved: its book is not a summa or tractatus
    on the argument's Ability, a second polemic, or a reply with no
    polemic to answer (TME p. 28)."""
    book = next((b for b in saga.books if b.id == values.get("book_id")), None)
    if book is None:
        return "Choose its book: a summa or tractatus in the library."
    if not pl.same_ability(argument.ability, book.ability or book.art):
        return (
            f"{escape(book.name)} isn't on {escape(argument.ability)}: every text "
            f"on the argument is written on its Ability ({TME} p. 28)."
        )
    kind = values.get("kind") or POLEMIC
    polemic = pl.polemic_of(argument)
    if kind == POLEMIC and polemic is not None and polemic is not text:
        return "The argument has its polemic: answer it with a diatribe or apologia."
    if kind != POLEMIC and (polemic is None or polemic is text):
        return "Add the polemic first: a diatribe or apologia answers it."
    for key in ("seasons_spent", "bundled"):
        if (values.get(key) or 0) < 0:
            return "Seasons and works bound are 0 or more."
    return None


def _set_text(saga: Saga, text: PolemicText, values: dict[str, Any]) -> None:
    text.kind = values.get("kind") or POLEMIC
    text.book_id = values.get("book_id") or None
    book = next((b for b in saga.books if b.id == text.book_id), None)
    author = values.get("author_id") or (book.author_id if book is not None else None)
    text.author_id = author or None
    text.studied = bool(values.get("studied")) and rules.needs_study(text.kind)
    text.audience = values.get("audience") or "tribunal"
    text.circulated_by_id = values.get("circulated_by_id") or None
    text.seasons_spent = values.get("seasons_spent") or 0
    text.bundled = values.get("bundled") or 0
    text.circulated = bool(values.get("circulated"))
    text.circulated_season = (
        values.get("circulated_season") or "" if text.circulated else ""
    )
    text.circulated_year = values.get("circulated_year") if text.circulated else None
    text.note = values.get("note", "")


def text_form(
    saga: Saga, tribunal: Tribunal, argument: Argument, text: PolemicText | None
) -> Form:
    """Add or Edit a text. A diatribe's or apologia's author gains its
    Reputation on writing it (TME pp. 33, 35)."""

    def apply(values: dict[str, Any]) -> str | None:
        found = text
        if found is None:
            found = PolemicText()
            argument.texts.append(found)
        _set_text(saga, found, values)
        return escape(pl.on_written(saga, tribunal, argument, found)) or None

    return Form(
        "Add Text" if text is None else "Edit Text",
        lambda: text_fields(saga, argument, text),
        apply,
        validate=lambda values: text_problem(saga, argument, text, values),
        save_label="Add" if text is None else "Save",
        help_id=ARGUMENT_TEXTS_SECTION,
    )


def texts_ops(saga: Saga, tribunal: Tribunal, chosen: Chosen) -> SectionOps:
    """The chosen argument's texts."""

    def texts() -> list[PolemicText]:
        argument = chosen_argument(tribunal, chosen)
        return argument.texts if argument is not None else []

    def add() -> Command:
        argument = chosen_argument(tribunal, chosen)
        if argument is None:
            return Refuse("Add Text", "Add an argument first.")
        if not pl.text_books(saga):
            return Refuse(
                "Add Text",
                "The library has no summa or tractatus on an Ability: add the "
                "book first, then its text here.",
            )
        return text_form(saga, tribunal, argument, None)

    def edit(index: int) -> Command:
        argument = chosen_argument(tribunal, chosen)
        if argument is None or index >= len(argument.texts):
            return Refuse("Edit Text", "Choose a text first.")
        return text_form(saga, tribunal, argument, argument.texts[index])

    def remove(index: int) -> Command:
        argument = chosen_argument(tribunal, chosen)
        if argument is None or index >= len(argument.texts):
            return Refuse("Delete Text", "Choose a text first.")
        text = argument.texts[index]

        def delete() -> None:
            argument.texts.remove(text)

        name = f"the {pl.KIND_NAMES[text.kind].lower()} {pl.book_words(saga, text)}"
        return Confirm(
            f"Delete {escape(name)}?\n\nThe book stays in the library.", delete
        )

    return SectionOps(
        add=add,
        edit=edit,
        remove=remove,
        rows=lambda: [pl.book_words(saga, t) for t in texts()],
    )


# -- More: Circulate a Text --


def _circulator_options(saga: Saga, text: PolemicText) -> list[tuple[str, str]]:
    """Its author first, then the saga's other characters, each with the
    Reputation he would roll."""
    author = pl.author(saga, text)
    people = [author] if author is not None else []
    people += [c for c in saga.characters if c is not author]
    found = []
    for person in people:
        reputation = rules.circulation_reputation(person)
        found.append(
            (escape(f"{person.name} (best Reputation {reputation})"), person.id)
        )
    return found


def circulate_fields(saga: Saga, text: PolemicText) -> list[DialogField]:
    who = pl.circulator(saga, text)
    return [
        DialogField(
            "text",
            "Text",
            "info",
            escape(
                f"{pl.KIND_NAMES[text.kind]}: {_short(pl.author(saga, text))}, "
                f"{pl.book_words(saga, text)}"
            ),
        ),
        DialogField(
            "who",
            "Circulated by",
            "select",
            who.id if who is not None else None,
            options=_circulator_options(saga, text),
            required=True,
        ),
        DialogField(
            "audience",
            "To",
            "select",
            text.audience,
            options=_audience_options(),
            required=True,
        ),
        DialogField(
            "seasons", "Seasons spent so far (+1 each)", "int", text.seasons_spent
        ),
        DialogField(
            "bundled",
            "New works bound with it (+1 each)",
            "int",
            text.bundled,
            hint="A Lab Text or another new item in every copy.",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            saga.current_season or "Spring",
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def circulate_live(
    saga: Saga, argument: Argument, text: PolemicText, values: dict[str, Any]
) -> str:
    who = saga.character(values.get("who")) or pl.circulator(saga, text)
    reputation = rules.circulation_reputation(who)
    audience = values.get("audience") or text.audience
    seasons = max(0, values.get("seasons") or 0)
    bundled = max(0, values.get("bundled") or 0)
    level = pl.level(saga, text)
    total = rules.circulation_total(reputation, level, seasons, bundled)
    ease = rules.ease_factor(audience)
    book = pl.book_of(saga, text)
    level_words = (
        f"level {level} (a tractatus)"
        if book is not None and book.type == "Tractatus"
        else f"level {level}"
    )
    lines = [
        f"Reputation {reputation} + {level_words} + {seasons} for seasons spent "
        f"+ {bundled} bound with it = [b]{total} + simple die[/] against "
        f"[b]{ease}[/]: the die must show {max(1, ease - total)} or more.",
        f"A distraction of {rules.distraction_days(audience)} days this season.",
    ]
    name = rules.reputation_name(text.kind, argument.ideal or argument.topic)
    after = pl.total_if(saga, argument, text)
    sign = "−" if text.kind == DIATRIBE else "+"
    effect = (
        f"the {pl.KIND_NAMES[text.kind].lower()} adds its Quality "
        if text.kind != DIATRIBE
        else "the diatribe takes away its Quality "
    )
    if text.kind == POLEMIC:
        effect = "the polemic's Quality less the Prevailing Wisdom starts the total "
    lines.append(
        f"Out: {effect}({sign}{pl.quality(saga, text)}"
        + (
            f"; the Argument Total becomes {pl.signed(after)}"
            if after is not None
            else ""
        )
        + f"), and {_gains_words(saga, text, who, name)}."
    )
    if rules.needs_study(text.kind) and not text.studied:
        lines.append(
            "[$text-warning]Its author hasn't studied the work it answers: tick "
            "Studied on the text first.[/]"
        )
    lines.append(f"[dim]{TME} pp. 29-31, 35.[/]")
    return "\n".join(lines)


def _gains_words(
    saga: Saga, text: PolemicText, who: Character | None, name: str
) -> str:
    """Who gains the text's Reputation once it is out (TME pp. 31, 33,
    35), as markup: no one twice."""
    gaining = [pl.author(saga, text)]
    if rules.needs_study(text.kind):
        gaining.append(who)
    names = [
        escape(_short(c))
        for n, c in enumerate(gaining)
        if c is not None and c.id not in text.reputation_given and c not in gaining[:n]
    ]
    if not names:
        return f"no one gains {escape(name)} again (the text has given it)"
    verb = "gains" if len(names) == 1 else "each gain"
    return (
        f"{' and '.join(names)} {verb} {escape(name)} 1 (or "
        f"{rules.REPUTATION_XP} experience toward it)"
    )


def circulate(
    saga: Saga,
    tribunal: Tribunal,
    argument: Argument,
    text: PolemicText,
    values: dict[str, Any],
    die: int,
) -> str:
    """One season's Circulation Roll with `die`: out, the text counts and
    its author gains his Reputation; not, the season counts +1 toward the
    next (TME pp. 29-31). Returns what happened."""
    who = saga.character(values.get("who")) or pl.circulator(saga, text)
    text.circulated_by_id = (
        who.id if who is not None and who.id != text.author_id else None
    )
    text.audience = values.get("audience") or text.audience
    text.bundled = max(0, values.get("bundled") or 0)
    seasons = max(0, values.get("seasons") or 0)
    reputation = rules.circulation_reputation(who)
    total = rules.circulation_total(
        reputation, pl.level(saga, text), seasons, text.bundled
    )
    ease = rules.ease_factor(text.audience)
    rolled = f"{total} + {die} = {total + die} against {ease}"
    if not rules.circulates(total, die, text.audience):
        text.seasons_spent = seasons + 1
        return (
            f"{rolled}: not yet. The season counts +1 toward the next roll "
            f"({text.seasons_spent} spent)."
        )
    text.circulated = True
    text.seasons_spent = seasons + 1
    text.circulated_season = values.get("season") or saga.current_season
    text.circulated_year = values.get("year") or saga.current_year
    words = " ".join(
        [f"{rolled}: circulated.", *pl.on_circulated(saga, tribunal, argument, text)]
    )
    total_now = pl.total(saga, argument)
    if total_now is not None:
        words += (
            f" The Argument Total is {pl.signed(total_now)}: "
            f"{pl.signed(pl.bonus(saga, argument))} in debate."
        )
    return escape(words)


def circulate_form(
    saga: Saga,
    tribunal: Tribunal,
    chosen: Chosen,
    row: int | None,
    rng: random.Random | None = None,
) -> Command:
    """More's Circulate a Text on the chosen text: a season's Circulation
    Roll (TME p. 29)."""
    argument = chosen_argument(tribunal, chosen)
    text = _at(argument.texts, row) if argument is not None else None
    if argument is None or text is None:
        return Refuse(CIRCULATE_TITLE, "Choose a text of an argument first.")
    if text.circulated:
        return Refuse(CIRCULATE_TITLE, "That text is out already.")
    if pl.book_of(saga, text) is None:
        return Refuse(CIRCULATE_TITLE, "Its book is no longer in the library.")
    chance = rng or random.Random()
    found = text

    def problem(_values: dict[str, Any]) -> str | None:
        if rules.needs_study(found.kind) and not found.studied:
            return (
                "Its author must first spend a season studying the work it "
                f"answers ({TME} pp. 31, 35): tick Studied on the text."
            )
        return None

    return Form(
        CIRCULATE_TITLE,
        lambda: circulate_fields(saga, found),
        lambda values: circulate(
            saga, tribunal, argument, found, values, dice.simple_die(chance)
        ),
        validate=problem,
        live=lambda values: circulate_live(saga, argument, found, values),
        save_label="Roll",
        help_id=CIRCULATE_HELP,
        inspector="The Copies Go Out",
    )


def tab_offered(saga: Saga) -> bool:
    """Whether a Tribunal shows its Arguments tab: while Transforming
    Mythic Europe is in play."""
    return sourcebooks.in_play(TME, sourcebooks.saga_books(saga))
