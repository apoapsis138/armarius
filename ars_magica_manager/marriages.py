"""A lord's Marriages tab: the marriages joining his house, and the terms
of the one that stands, with what follows from them; and its forms,
Arrange a Marriage (Add and Edit, and the Terms' Edit), End a Marriage
and Delete (Lords of Men pp. 10-11, 81; City & Guild p. 113 and the errata
p. 57; the Definitive Edition pp. 148, 512-513; The Church pp. 37, 47).
The rules are rules.marriage's.

A marriage is kept once, in saga.marriages, and listed on the page of each
house it joins (a lord's), as a battle is on each lord it names. Ending
one with the husband's death, when he is a lord of the Region, goes on to
Settle an Inheritance with his widow ticked.

Pattern: `_marriage_fields` is the form's builder (a FieldsDialog on the
terminal, a form on the desktop); the dowry it works out live is
rules.marriage's Strategy-as-a-dict, one function per kind of family.
"""

from __future__ import annotations

from typing import Any

from . import diaries, manors
from .commands import Command, Confirm, Form, Refuse, SectionOps, Then, notes
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import SEASONS, Character, Neighbour, Saga, character_age
from .models.marriage import (
    BETROTHED,
    CHARACTER_REF,
    ENDED,
    HUSBAND_DIED,
    MARRIAGE_ENDINGS,
    MARRIED,
    MERCHANT,
    NEIGHBOUR_REF,
    NOBLE,
    PARTED,
    TWO_HIGHER,
    WIFE_DIED,
    Marriage,
)
from .neighbour_lists import KindBlock, KindList, KindTab, LedgerEntry
from .references import Fact
from .rules import marriage as rules
from .sections import MARRIAGE_TERMS_SECTION, MARRIAGES_SECTION

ARRANGE = "Arrange a Marriage"
END = "End a Marriage"
#: The forms' own help pages.
ARRANGE_HELP = "arrange-marriage"
END_HELP = "end-marriage"
LORD = "lord"

ENDING_LABELS: dict[str, str] = {
    HUSBAND_DIED: "He dies first",
    WIFE_DIED: "She dies first",
    PARTED: "They separate (or it is annulled)",
}
STATE_LABELS: dict[str, str] = {BETROTHED: "Betrothed", MARRIED: "Married"}


# -- who a marriage joins --


def _record(saga: Saga, ref: str) -> Character | Neighbour | None:
    if ref.startswith(CHARACTER_REF):
        return saga.character(ref.removeprefix(CHARACTER_REF))
    if ref.startswith(NEIGHBOUR_REF):
        return saga.neighbour(ref.removeprefix(NEIGHBOUR_REF))
    return None


def _lord_name(lord: Neighbour) -> str:
    """A lord as a spouse: his ruler's name, or his record's up to its
    title ("Jürgen" of "Jürgen, Baron Schönburg")."""
    return lord.ruler or lord.name.split(",")[0].strip()


def spouse(saga: Saga, marriage: Marriage, side: str) -> str:
    """The bride's or the groom's name (`side` "bride" or "groom"): a name
    typed in, else the record's."""
    typed = marriage.bride if side == "bride" else marriage.groom
    if typed:
        return typed
    found = _record(saga, marriage.bride_ref if side == "bride" else marriage.groom_ref)
    if isinstance(found, Neighbour):
        return _lord_name(found)
    return found.name if found is not None else "(gone)"


def _short(name: str) -> str:
    return name.split()[0] if name.split() else name


def houses(marriage: Marriage) -> list[str]:
    """The lords (neighbour ids) whose pages show the marriage: each
    spouse's house, and a spouse who is a lord himself."""
    found = [
        ref.removeprefix(NEIGHBOUR_REF)
        for ref in (marriage.bride_ref, marriage.groom_ref)
        if ref.startswith(NEIGHBOUR_REF)
    ]
    found += [h for h in (marriage.bride_house, marriage.groom_house) if h]
    return list(dict.fromkeys(found))


def involving(saga: Saga, house: Neighbour) -> list[Marriage]:
    """The marriages joining `house`, as entered."""
    return [m for m in saga.marriages if house.id in houses(m)]


def _of_house(marriage: Marriage, house_id: str) -> str:
    """Which spouse belongs to `house_id` ("bride" or "groom"): a lord
    himself first, then the houses named; the bride when both or neither
    do."""
    lord = NEIGHBOUR_REF + house_id
    if marriage.groom_ref == lord:
        return "groom"
    if marriage.bride_ref == lord:
        return "bride"
    if marriage.groom_house == house_id and marriage.bride_house != house_id:
        return "groom"
    return "bride"


def couple(saga: Saga, marriage: Marriage, house_id: str = "") -> str:
    """The marriage as its house names it: its own spouse by first name,
    then the other in full ("Karlotte and Wolfram von Schattenbach")."""
    first = _of_house(marriage, house_id)
    other = "groom" if first == "bride" else "bride"
    return (
        f"{_short(spouse(saga, marriage, first))} and {spouse(saga, marriage, other)}"
    )


def current(saga: Saga, house: Neighbour) -> Marriage | None:
    """The marriage the Terms show: the last that still stands, else the
    last of all."""
    listed = involving(saga, house)
    standing = [m for m in listed if rules.is_standing(m)]
    return (standing or listed or [None])[-1]


def state_text(marriage: Marriage) -> str:
    """Where it stands: "Betrothed", "Married", "Ended: her death, 1208"."""
    if not marriage.ended:
        return STATE_LABELS.get(marriage.state, "Married")
    when = str(marriage.end_year) if marriage.end_year is not None else ""
    words = {
        HUSBAND_DIED: "Ended: his death",
        WIFE_DIED: "Ended: her death",
        PARTED: "Separated",
    }[marriage.ended]
    return f"{words}, {when}" if when else words


def dowry_text(marriage: Marriage) -> str:
    """The dowry in a few words: what was agreed, else what is worked out."""
    if marriage.dowry:
        return marriage.dowry
    if marriage.heiress:
        return "none: she is the heiress"
    if marriage.family == NOBLE:
        return f"about {rules.noble_share(marriage):g} manors"
    if marriage.family == MERCHANT:
        if marriage.standing == TWO_HIGHER:
            return "none: the groom raised"
        return f"about {rules.merchant_coin(marriage)} pounds"
    return ""


def _described(saga: Saga, marriage: Marriage, side: str) -> str:
    """A spouse for the Terms: the name, an age if the sheet gives one,
    and "heiress"."""
    name = spouse(saga, marriage, side)
    found = _record(saga, marriage.bride_ref if side == "bride" else marriage.groom_ref)
    age = (
        character_age(found.background.year_born, saga.current_year)
        if isinstance(found, Character)
        else None
    )
    extra = [str(age)] if age is not None else []
    if side == "bride" and marriage.heiress:
        extra.append("heiress")
    return ", ".join([name, *extra])


def terms_pairs(saga: Saga, marriage: Marriage) -> list[tuple[str, str]]:
    """The Terms as (label, words) pairs."""
    custom = rules.CUSTOM_LABELS.get(marriage.custom, marriage.custom)
    if marriage.heiress:
        dowry = "none; a dower from the groom's family?"
    else:
        dowry = dowry_text(marriage) or "not settled yet"
    hers = "given" if marriage.her_consent else "refused"
    fathers = "given" if marriage.father_consent else "withheld"
    return [
        ("Bride", _described(saga, marriage, "bride")),
        ("Groom", _described(saga, marriage, "groom")),
        ("Custom", custom),
        ("Dowry", dowry),
        ("Consent", f"hers: {hers}; her father's: {fathers}"),
        ("Church", rules.CHURCH_NEEDS),
    ]


# -- Arrange a Marriage --


def _spouse_options(saga: Saga) -> list[tuple[str, str]]:
    return [
        *(
            (f"{escape(c.name)} ({c.type})", CHARACTER_REF + c.id)
            for c in saga.characters
        ),
        *(
            (f"{escape(_lord_name(n))} ({escape(n.name)})", NEIGHBOUR_REF + n.id)
            for n in saga.neighbours
            if n.kind == LORD
        ),
        ("Someone typed in", ""),
    ]


def _house_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(n.name), n.id) for n in saga.neighbours if n.kind == LORD]


def _family_has(key: str) -> Any:
    return lambda values: any(
        p.key == key for p in rules.points_for(str(values.get("family") or NOBLE))
    )


def _new(saga: Saga, house: Neighbour | None) -> Marriage:
    return Marriage(
        season=saga.current_season,
        year=saga.current_year,
        bride_house=house.id if house is not None else None,
    )


def _marriage_fields(saga: Saga, marriage: Marriage) -> list[DialogField]:
    """Arrange a Marriage's fields, filled from `marriage`."""
    m = marriage

    def typed(key: str) -> Any:
        return lambda values: not values.get(key)

    def family(*kinds: str) -> Any:
        return lambda values: (values.get("family") or NOBLE) in kinds

    found = [
        DialogField(
            "bride_ref",
            "Bride",
            "select",
            m.bride_ref,
            options=_spouse_options(saga),
        ),
        DialogField(
            "bride",
            "Bride's name",
            "text",
            m.bride,
            show_if=typed("bride_ref"),
            placeholder="e.g. Adelheid of Sayn",
        ),
        DialogField(
            "groom_ref",
            "Groom",
            "select",
            m.groom_ref,
            options=_spouse_options(saga),
        ),
        DialogField(
            "groom",
            "Groom's name",
            "text",
            m.groom,
            show_if=typed("groom_ref"),
            placeholder="e.g. Sir Wolfram von Schattenbach",
        ),
        DialogField(
            "bride_house",
            "Her house",
            "select",
            m.bride_house,
            options=_house_options(saga),
            allow_blank=True,
            placeholder="(none of the Region's)",
            hint="The lords whose pages show the marriage; a lord who marries "
            "shows it on his own.",
        ),
        DialogField(
            "groom_house",
            "His house",
            "select",
            m.groom_house,
            options=_house_options(saga),
            allow_blank=True,
            placeholder="(none of the Region's)",
        ),
        DialogField("season", "Season", "select", m.season, options=pairs(SEASONS)),
        DialogField("year", "Year", "int", m.year),
    ]
    if not m.ended:
        found.append(
            DialogField(
                "state",
                "It stands",
                "select",
                m.state if m.state in STATE_LABELS else MARRIED,
                options=[(label, key) for key, label in STATE_LABELS.items()],
            )
        )
    found += [
        DialogField(
            "family",
            "Bride's family",
            "select",
            m.family,
            options=[(label, key) for key, label in rules.FAMILY_LABELS.items()],
        ),
        DialogField(
            "heiress",
            "She is the heiress",
            "check",
            m.heiress,
            show_if=family(NOBLE, MERCHANT),
        ),
        DialogField(
            "lands",
            "Her parents' land (manors)",
            "int",
            m.lands,
            show_if=family(NOBLE),
        ),
        DialogField(
            "patrimony",
            "The eldest son's patrimony, kept out (French custom)",
            "int",
            m.patrimony,
            show_if=family(NOBLE),
            hint="In the French sphere the eldest son and his patrimony both "
            "come out of the division (LoM p. 11).",
        ),
        DialogField(
            "profit",
            "Her father's yearly profit (pounds)",
            "int",
            m.profit,
            show_if=family(MERCHANT),
        ),
        DialogField(
            "standing",
            "Her father's Social Status",
            "select",
            m.standing,
            options=[(label, key) for key, label in rules.STANDING_LABELS.items()],
            show_if=family(MERCHANT),
            hint="Against the groom's (C&G p. 113).",
        ),
        DialogField(
            "children",
            "Her parents' children",
            "int",
            m.children,
            show_if=family(NOBLE, MERCHANT),
            hint="She and her brothers and sisters (a merchant's married "
            "daughters left out); with a patrimony kept out, the eldest son "
            "is left out of the division too.",
        ),
    ]
    found += [
        DialogField(
            f"pt_{point.key}",
            point.label,
            "check",
            point.key in m.points,
            show_if=_family_has(point.key),
        )
        for point in rules.POINTS
    ]
    found += [
        DialogField(
            "custom",
            "Custom for the dowry",
            "select",
            m.custom,
            options=[(label, key) for key, label in rules.CUSTOM_LABELS.items()],
        ),
        DialogField(
            "dowry",
            "The dowry agreed",
            "text",
            m.dowry,
            placeholder="e.g. Hof Sayn, a manor; blank: as worked out",
        ),
        DialogField(
            "her_consent",
            "She consents (needed for the sacrament)",
            "check",
            m.her_consent,
        ),
        DialogField(
            "father_consent",
            "Her father consents (where custom asks it)",
            "check",
            m.father_consent,
        ),
        DialogField("kin", "Close kin or already married", "check", m.kin),
        DialogField(
            "note",
            "Note",
            "text",
            m.note,
            placeholder="e.g. Proposed by the Schattenbachs at Michaelmas",
        ),
    ]
    return found


def _write(marriage: Marriage, values: dict[str, Any]) -> None:
    """The form's values into `marriage` (fields hidden for its family keep
    what they held)."""
    m = marriage
    m.bride_ref = str(values.get("bride_ref") or "")
    m.groom_ref = str(values.get("groom_ref") or "")
    m.bride = "" if m.bride_ref else str(values.get("bride") or "").strip()
    m.groom = "" if m.groom_ref else str(values.get("groom") or "").strip()
    m.bride_house = values.get("bride_house") or None
    m.groom_house = values.get("groom_house") or None
    m.season = str(values.get("season") or m.season)
    m.year = int(values.get("year") or m.year)
    if "state" in values and not m.ended:
        m.state = str(values.get("state") or m.state)
    m.family = str(values.get("family") or m.family)
    for key in ("heiress", "her_consent", "father_consent", "kin"):
        if key in values:
            setattr(m, key, bool(values[key]))
    for key in ("lands", "patrimony", "profit", "children"):
        if values.get(key) is not None:
            setattr(m, key, int(values[key]))
    if values.get("standing"):
        m.standing = str(values["standing"])
    shown = {p.key for p in rules.points_for(m.family)}
    m.points = [
        p.key
        for p in rules.POINTS
        if (values.get(f"pt_{p.key}") if p.key in shown else p.key in m.points)
    ]
    m.custom = str(values.get("custom") or m.custom)
    m.dowry = str(values.get("dowry") or "").strip()
    m.note = str(values.get("note") or "").strip()


def _sketch(base: Marriage, values: dict[str, Any]) -> Marriage:
    """A copy of `base` with the form's values so far, for the live text
    (numbers still being typed count as nought)."""
    shown = Marriage(**{**vars(base), "points": list(base.points)})
    safe = dict(values)
    for key in ("lands", "patrimony", "profit", "children", "year"):
        if not isinstance(safe.get(key), int):
            safe[key] = None
    _write(shown, safe)
    return shown


def contract(base: Marriage, values: dict[str, Any]) -> str:
    """The Contract: the dowry worked out, what the custom does with it,
    and what stands against the marriage (markup)."""
    m = _sketch(base, values)
    lines = rules.dowry_lines(m)
    custom = rules.CUSTOM_KEEPS.get(m.custom, "")
    if custom:
        lines.append(f"[$label]The dowry after:[/] {custom[0].upper()}{custom[1:]}.")
    lines += rules.warnings(m)
    lines.append(
        "[dim]The Church asks only a spoken intent and a dowry; it prefers a "
        f"priest and two witnesses (LoM p. 10). {rules.BLESSING}[/]"
    )
    return "\n".join(lines)


def _problem(values: dict[str, Any]) -> str | None:
    for side in ("bride", "groom"):
        if not values.get(f"{side}_ref") and not str(values.get(side) or "").strip():
            return f"Choose the {side} or type a name."
    if values.get("bride_ref") and values.get("bride_ref") == values.get("groom_ref"):
        return "No one marries themselves."
    if not (
        values.get("bride_house")
        or values.get("groom_house")
        or str(values.get("bride_ref") or "").startswith(NEIGHBOUR_REF)
        or str(values.get("groom_ref") or "").startswith(NEIGHBOUR_REF)
    ):
        return "Name her house or his, so a lord's page shows the marriage."
    for key in ("lands", "patrimony", "profit"):
        if (values.get(key) or 0) < 0:
            return "Land and profit can't be less than none."
    children = values.get("children")
    if children is not None and children < 1:
        return "At least one child shares: the bride herself."
    if (
        (values.get("family") or NOBLE) == NOBLE
        and not values.get("heiress")
        and (values.get("patrimony") or 0) > 0
        and children is not None
        and children < 2
    ):
        return (
            "With a patrimony kept out, count the eldest son among her "
            "parents' children too: at least two."
        )
    return None


def arrange_form(
    saga: Saga, house: Neighbour | None, marriage: Marriage | None = None
) -> Form:
    """Arrange a Marriage (a new one on `house`'s page), or edit `marriage`."""
    base = marriage or _new(saga, house)

    def apply(values: dict[str, Any]) -> None:
        _write(base, values)
        if marriage is None:
            saga.marriages.append(base)

    return Form(
        ARRANGE if marriage is None else "Edit the Marriage",
        lambda: _marriage_fields(saga, base),
        apply,
        validate=_problem,
        live=lambda values: contract(base, values),
        inspector="The Contract",
        save_label="Arrange" if marriage is None else "Save",
        help_id=ARRANGE_HELP,
    )


def ops(saga: Saga, house: Neighbour) -> SectionOps:
    """Add (Arrange), Edit and Delete on the marriages joining `house`."""

    def listed() -> list[Marriage]:
        return involving(saga, house)

    def remove(index: int) -> Command:
        entry = listed()[index]
        return Confirm(
            f"Delete the marriage of {escape(couple(saga, entry, house.id))}?",
            lambda: saga.marriages.remove(entry),
        )

    return SectionOps(
        add=lambda: arrange_form(saga, house),
        edit=lambda index: arrange_form(saga, house, listed()[index]),
        remove=remove,
        rows=lambda: [couple(saga, m, house.id) for m in listed()],
    )


def terms_edit(saga: Saga, house: Neighbour) -> Command:
    """The Terms' Edit: the marriage they show."""
    shown = current(saga, house)
    if shown is None:
        return Refuse("Edit Terms", "No marriage yet: arrange one first.")
    return arrange_form(saga, house, shown)


# -- End a Marriage --


def _end_fields(saga: Saga) -> list[DialogField]:
    return [
        DialogField(
            "how",
            "It ends",
            "select",
            HUSBAND_DIED,
            options=[(ENDING_LABELS[key], key) for key in MARRIAGE_ENDINGS],
        ),
        DialogField(
            "season", "Season", "select", saga.current_season, options=pairs(SEASONS)
        ),
        DialogField("year", "Year", "int", saga.current_year),
    ]


def end_live(saga: Saga, marriage: Marriage, values: dict[str, Any]) -> str:
    """What follows the ending chosen (markup)."""
    how = str(values.get("how") or HUSBAND_DIED)
    bride = _short(spouse(saga, marriage, "bride"))
    groom = _short(spouse(saga, marriage, "groom"))
    text = rules.ending_text(marriage, how, bride, groom)
    lord = _record(saga, marriage.groom_ref)
    if how == HUSBAND_DIED and isinstance(lord, Neighbour):
        text += " Settle an Inheritance follows, with this filled in."
    return text + "\n[dim]Noted on both families' Diaries.[/]"


def end(saga: Saga, marriage: Marriage, values: dict[str, Any]) -> Any:
    """The marriage ends: noted on each house's and spouse's Diary; a lord
    who dies goes on to Settle an Inheritance."""
    how = str(values.get("how") or HUSBAND_DIED)
    marriage.ended = how
    marriage.state = ENDED
    marriage.end_season = str(values.get("season") or saga.current_season)
    marriage.end_year = int(values.get("year") or saga.current_year)
    bride = _short(spouse(saga, marriage, "bride"))
    groom = _short(spouse(saga, marriage, "groom"))
    follows = rules.ending_text(marriage, how, bride, groom)
    records = [_record(saga, marriage.bride_ref), _record(saga, marriage.groom_ref)]
    lords = [saga.neighbour(h) for h in houses(marriage)]
    diaries.write(
        marriage.end_year,
        marriage.end_season,
        "Marriage",
        f"{couple(saga, marriage)}: {state_text(marriage).lower()}.",
        characters=[r for r in records if isinstance(r, Character)],
        neighbours=[n for n in lords if n is not None],
    )
    lord = _record(saga, marriage.groom_ref)
    if how == HUSBAND_DIED and isinstance(lord, Neighbour):
        return Then(manors.settle_form(saga, lord, widow=True))
    return notes(follows)


def end_form(saga: Saga, house: Neighbour, index: int) -> Command:
    """End a Marriage on the chosen marriage of `house`'s page."""
    listed = involving(saga, house)
    if index >= len(listed):
        return Refuse(END, "Choose a marriage first.")
    marriage = listed[index]
    if marriage.ended:
        return Refuse(
            END,
            f"{escape(couple(saga, marriage, house.id))} has ended already "
            f"({escape(state_text(marriage))}).",
        )
    return Form(
        END,
        lambda: _end_fields(saga),
        lambda values: end(saga, marriage, values),
        live=lambda values: end_live(saga, marriage, values),
        inspector="What Follows",
        save_label="Record",
        help_id=END_HELP,
    )


# -- the tab --

#: The list's columns' widest, on the terminal.
CAPS = [44, 13, 26, 0]
PANEL = "[dim]Choose a marriage.[/]"


def _when(marriage: Marriage) -> str:
    return f"{marriage.season} {marriage.year}"


def _tone(marriage: Marriage) -> str:
    """The theme colour a marriage's state is shown in."""
    if marriage.ended:
        return "label"
    return "text-warning" if marriage.state == BETROTHED else "text-success"


#: A character sheet's Marriages section: the marriages naming them.
CHARACTER_SECTION = "section-char-marriages"


def of_character(saga: Saga, character: Character) -> list[Marriage]:
    """The marriages naming `character` as bride or groom, as entered."""
    ref = CHARACTER_REF + character.id
    return [m for m in saga.marriages if ref in (m.bride_ref, m.groom_ref)]


def character_text(saga: Saga, character: Character) -> str:
    """The character's marriages, each with its spouse, when, dowry and
    state; they are arranged and ended on the families' lords' pages
    (markup)."""
    found: list[str] = []
    ref = CHARACTER_REF + character.id
    for m in of_character(saga, character):
        other = "bride" if m.groom_ref == ref else "groom"
        colour = "dim" if m.ended else f"${_tone(m)}"
        found.append(
            f"[b]{escape(spouse(saga, m, other))}[/]  {escape(_when(m))}  "
            f"[{colour}]{escape(state_text(m))}[/]"
        )
        dowry = dowry_text(m)
        if dowry:
            found.append(f"  Dowry: {escape(dowry)}")
        if m.ended:
            bride = spouse(saga, m, "bride").split()[0]
            groom = spouse(saga, m, "groom").split()[0]
            found.append(
                f"  [dim]{rules.ending_text(m, m.ended, escape(bride), escape(groom))}[/]"
            )
    return "\n".join(found)


def marriages_title(saga: Saga, house: Neighbour) -> str:
    return f"Marriages ({len(involving(saga, house))})"


def marriages_grid(saga: Saga, house: Neighbour) -> Grid:
    listed = involving(saga, house)
    rows = [
        [
            couple(saga, m, house.id),
            _when(m),
            dowry_text(m),
            state_text(m),
        ]
        for m in listed
    ]
    styles = {
        (index, 3): ("dim" if m.ended else f"${_tone(m)}")
        for index, m in enumerate(listed)
    }
    return Grid(
        ["Spouses", "When", "Dowry", "State"],
        rows,
        list(range(len(rows))),
        "No marriages yet: a arranges one.",
        styles=styles,
        caps=CAPS,
        stretch=0,
    )


def marriages_ledger(saga: Saga, house: Neighbour) -> list[LedgerEntry]:
    """Each marriage as an entry ruled off on the desktop's page."""
    return [
        LedgerEntry(
            couple(saga, m, house.id),
            rubric="§",
            meta=_when(m),
            badge=state_text(m),
            tone=_tone(m),
            body=escape(f"Dowry: {dowry_text(m) or 'not settled yet'}"),
            subtitle=f"{_when(m)} · {state_text(m)}",
        )
        for m in involving(saga, house)
    ]


def marriage_info(saga: Saga, house: Neighbour, index: int) -> str:
    """A marriage in the details panel: when and where it stands, its note,
    and what its ending brought."""
    listed = involving(saga, house)
    if index >= len(listed):
        return ""
    m = listed[index]
    colour = "dim" if m.ended else f"${_tone(m)}"
    lines = [f"{escape(_when(m))}  ·  [{colour}]{escape(state_text(m))}[/]"]
    if m.note:
        lines.append(escape(m.note))
    if m.ended:
        bride = spouse(saga, m, "bride").split()[0]
        groom = spouse(saga, m, "groom").split()[0]
        lines.append(
            f"[dim]{rules.ending_text(m, m.ended, escape(bride), escape(groom))}[/]"
        )
    return "\n".join(lines)


def terms_title(saga: Saga, house: Neighbour) -> str:
    """ "Karlotte and Wolfram: the Terms"."""
    shown = current(saga, house)
    if shown is None:
        return "The Terms"
    bride = spouse(saga, shown, "bride").split()[0]
    groom = spouse(saga, shown, "groom").split()[0]
    return f"{bride} and {groom}: the Terms"


def terms_facts(saga: Saga, house: Neighbour) -> list[Fact]:
    shown = current(saga, house)
    if shown is None:
        return []
    return [Fact(label, words) for label, words in terms_pairs(saga, shown)]


def terms_text(saga: Saga, house: Neighbour) -> str:
    """What follows from the marriage the Terms show, and what stands
    against it (markup)."""
    shown = current(saga, house)
    if shown is None:
        return "[dim]No marriage yet: arrange one, and its terms show here.[/]"
    bride = spouse(saga, shown, "bride").split()[0]
    groom = spouse(saga, shown, "groom").split()[0]
    follows = rules.what_follows(shown, escape(bride), escape(groom))
    return "\n".join([f"[$label]What follows:[/] {follows}", *rules.warnings(shown)])


MARRIAGES_LIST = KindList(
    MARRIAGES_SECTION,
    marriages_title,
    marriages_grid,
    ops,
    marriage_info,
    ledger=marriages_ledger,
)

TERMS_BLOCK = KindBlock(
    MARRIAGE_TERMS_SECTION,
    "The Terms",
    text=terms_text,
    edit=terms_edit,
    edit_label="Edit Terms",
    after=MARRIAGES_SECTION,
    facts=terms_facts,
    facts_inline=True,
    heading=terms_title,
)

#: A lord's Marriages tab, after his Manors.
TAB = KindTab(
    "Marriages",
    "tab-nb-marriages",
    (MARRIAGES_LIST,),
    blocks=(TERMS_BLOCK,),
    icon="lord",
    panel=PANEL,
)
