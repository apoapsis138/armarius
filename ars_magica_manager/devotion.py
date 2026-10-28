"""Devotion and the saints' More actions on a character: Invoke a Saint,
Threaten a Saint, Devotion Points, and Indulgence, Vigil or Fast. Each is a
form with a live inspector, rolled or kept on saving -- no UI in here. The
rules are rules.devotion's; the saints and their powers rules.saints'.

What is kept: Devotions and the patron saint are progress records on the
character (rules.devotion.DEVOTION, PATRON), a fast the season's FAST
record; an invocation, a threat, Devotion Points gained and each act of
piety are written in the Diary; a vigil's Confidence Point, an
indulgence's Faith Point and Piety experience, and the Fatigue a vigil or
fast costs go on the sheet. A relic is chosen from the saga's churches'
Relics or is the character's own (Background.relic_faith); an icon from
the churches' eikons (theban_customs.icon_choices). With The Cradle and
the Crescent, a Mazdean yazata is invoked like a saint by one ritually
pure, and never threatened (p. 85)."""

from __future__ import annotations

import random
from typing import Any

from . import churches, diaries, sourcebooks
from . import theban_customs as byzantine
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Saga, ScoredTrait
from .rules import confidence, dice, harm
from .rules import devotion as dv
from .rules import saints as sr

HELP_ID = "devotion"
#: The Cradle and the Crescent: the Mazdean yazdan, invoked like saints.
CRADLE = "TC&TC"
#: An invocation needs any of the books that invoke saints.
INVOKING_BOOKS = (dv.ROPD, dv.TC, sr.TSE, sr.TCI, CRADLE)
#: The saint choice that names a saint not on the list.
OTHER = "-another-"
OWN_RELIC = "own"
_WEALTHY = "vf_wealthy"
_IRISH = ("irish", "ireland", "hibern")


def _books(saga: Saga) -> frozenset[str] | None:
    return sourcebooks.saga_books(saga)


def invokes(saga: Saga) -> bool:
    """Whether a book that invokes saints is in play."""
    return any(sourcebooks.in_play(b, _books(saga)) for b in INVOKING_BOOKS)


def threatens(saga: Saga) -> bool:
    return sourcebooks.in_play(dv.ROPD, _books(saga))


def the_church(saga: Saga) -> bool:
    """Whether The Church's Devotions, relic bonus and acts of piety are in
    play."""
    return sourcebooks.in_play(dv.TC, _books(saga))


def _yazdan(saga: Saga) -> list[DialogField]:
    """The Cradle and the Crescent's yazdan (p. 85): invoked like a saint,
    by one ritually pure, and never threatened."""
    if not sourcebooks.in_play(CRADLE, _books(saga)):
        return []
    return [
        DialogField(
            "yazata",
            "A yazata (Mazdean)",
            "check",
            False,
            hint="Invoked like a saint, but never threatened (The Cradle and "
            "the Crescent p. 85).",
        )
    ]


def _yazata_problem(values: dict[str, Any], threat: bool) -> str | None:
    if not values.get("yazata"):
        return None
    if threat:
        return "A yazata can't be threatened (The Cradle and the Crescent p. 85)."
    if not values.get("pure"):
        return "Invoking a yazata needs ritual purity: the Nahn rite."
    return None


def _rng(rng: random.Random | None) -> random.Random:
    return rng or random.Random()


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def _signed(total: int) -> str:
    """ "+ [b]7[/]" or "- [b]4[/]": a total after its die."""
    return f"{'-' if total < 0 else '+'} [b]{abs(total)}[/]"


def _diary(saga: Saga, character: Character, name: str, text: str) -> None:
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        f"{text} Rules: {dv.SOURCE}.",
        characters=[character],
    )


# -- the saint --


def catalog_saint(saga: Saga, name: str) -> sr.Saint | None:
    """The book's saint of that name, among the books in play."""
    return next(
        (s for s in sr.in_play(_books(saga)).values() if dv.same_saint(s.name, name)),
        None,
    )


def saint_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The saints to choose from: his patron, his Devotions, the saints of
    the churches' relics, the books' saints, and another typed."""
    found: list[tuple[str, str]] = []

    def offer(name: str, label: str) -> None:
        if name.strip() and not any(dv.same_saint(name, v) for _, v in found):
            found.append((escape(label), name.strip()))

    patron = dv.patron(character)
    offer(patron, f"{patron} (his patron)")
    for record in dv.devotions(character):
        offer(record.name, f"{record.name} (Devotion {dv.score(record.points)})")
    for church in byzantine.church_list(saga):
        for relic in churches.relics(church):
            offer(relic.get("saint", ""), relic.get("saint", ""))
    for saint in sr.in_play(_books(saga)).values():
        offer(saint.name, f"{saint.name} ({saint.rank}, Might {saint.might})")
    return [*found, ("(another saint)", OTHER)]


def _saint_name(values: dict[str, Any]) -> str:
    chosen = str(values.get("saint") or "")
    if chosen and chosen != OTHER:
        return chosen
    return str(values.get("other") or "").strip()


def _saint_fields(saga: Saga, character: Character) -> list[DialogField]:
    listed = saint_options(saga, character)
    return [
        DialogField(
            "saint",
            "The saint",
            "select",
            listed[0][1],
            options=listed,
            required=True,
        ),
        DialogField(
            "other",
            "Another saint's name",
            "text",
            "",
            placeholder="e.g. Saint Bartholomew",
            show_if=lambda v: v.get("saint") in (None, "", OTHER),
        ),
    ]


def _refused_fields(character: Character) -> list[DialogField]:
    """Only a saint who has refused his invocation may be threatened (RoP:
    The Divine p. 87)."""
    refused = dv.refused(character)
    return [
        DialogField(
            "saint",
            "The saint who refused",
            "select",
            refused[0] if refused else None,
            options=[(escape(name), name) for name in refused],
            required=True,
        )
    ]


def _power_field(saga: Saga) -> DialogField:
    offered = sr.powers_in_play(_books(saga))
    return DialogField(
        "power",
        "The miracle asked",
        "select",
        None,
        options=[
            (escape(p.name + (" (curse)" if p.curse else "")), key)
            for key, p in sorted(offered.items(), key=lambda kv: kv[1].name)
        ],
        allow_blank=True,
        placeholder="(the storyguide decides)",
    )


def _saint_lines(saga: Saga, name: str, power_key: Any) -> list[str]:
    """The saint's rank, Might and powers, and the miracle asked, if the
    books know him."""
    saint = catalog_saint(saga, name)
    lines: list[str] = []
    power = sr.POWERS.get(str(power_key or ""))
    if saint is not None:
        held = sr.powers_of(saint)
        head = f"{escape(saint.name)}: {saint.rank}, Divine Might {saint.might}"
        if saint.feast:
            head += f", feast {saint.feast}"
        lines.append(f"[dim]{head}; patron of {escape(saint.patron_of)}.[/]")
        if held:
            typical = "" if saint.powers else "favoured by Greek saints: "
            lines.append(
                f"[dim]Powers ({typical}"
                + ", ".join(escape(p.name) for p in held)
                + ").[/]"
            )
        if power is not None and power not in held:
            lines.append(
                f"[$text-error]{escape(power.name)} is not among "
                f"{escape(saint.name)}'s powers.[/]"
            )
    if power is not None:
        lines.append(
            f"Asked: [b]{escape(power.line)}[/]: {escape(power.does)} "
            f"[dim]({escape(power.cited)})[/]"
        )
    return lines


# -- relics and icons --


def relic_choices(saga: Saga, character: Character) -> list[tuple[str, str, str, int]]:
    """The relics he might use: his own (if he relies on one), then each
    church's (not its eikons): (label, key, saint, Faith)."""
    found: list[tuple[str, str, str, int]] = []
    if character.background.relic_faith > 0:
        faith = character.background.relic_faith
        found.append((f"His own relic (Faith {faith})", OWN_RELIC, "", faith))
    for church in byzantine.church_list(saga):
        for row, relic in enumerate(churches.relics(church)):
            if churches.is_eikon(relic):
                continue
            faith = max(0, int(relic.get("faith") or 0))
            saint = relic.get("saint", "")
            label = (
                f"{relic['name']} ({saint or 'no saint'}, Faith {faith}, {church.name})"
            )
            found.append((label, f"{church.id}:{row}", saint, faith))
    return found


def _relic(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[int | None, bool]:
    """The chosen relic's Faith (None for none) and whether it is the
    invoked saint's."""
    key = values.get("relic")
    chosen = next((r for r in relic_choices(saga, character) if r[1] == key), None)
    if chosen is None:
        return None, False
    if key == OWN_RELIC:
        return chosen[3], bool(values.get("own_relic_of_saint"))
    return chosen[3], dv.same_saint(chosen[2], _saint_name(values))


def _icon_bonus(saga: Saga, values: dict[str, Any]) -> tuple[int, str]:
    """A venerated eikon's bonus, and a warning when it is another
    saint's (no bonus then)."""
    key = values.get("icon")
    relic = next((r for _, k, r in byzantine.icon_choices(saga) if k == key), None)
    if relic is None:
        return 0, ""
    if relic.get("of_christ"):
        return 0, "An icon of Christ aids invoking God, not a saint."
    if not dv.same_saint(relic.get("saint", ""), _saint_name(values)):
        return 0, f"{relic['name']} is not an icon of the saint invoked."
    return churches.eikon_bonus(relic), ""


def _irish(character: Character) -> bool:
    b = character.background
    text = f"{b.race_nationality} {b.place_of_origin}".casefold()
    return any(word in text for word in _IRISH)


# -- Invoke a Saint --

INVOKE = "Invoke a Saint"
DONATIONS: list[tuple[str, str]] = [
    ("None within a year (-3)", str(dv.NO_DONATION)),
    ("None now, one within the year", "0"),
    ("A small gift now (+1)", "1"),
    ("A fair gift now (+2)", "2"),
    ("A generous gift now (+3)", "3"),
]


def invoke_fields(saga: Saga, character: Character) -> list[DialogField]:
    church = the_church(saga)
    relics = relic_choices(saga, character)
    icons = byzantine.icon_choices(saga) if byzantine.in_play(saga) else []
    found = [
        *_saint_fields(saga, character),
        DialogField(
            "appropriate",
            "The matter is his concern",
            "check",
            False,
            hint="A saint whose concern is the matter at hand, or a "
            "sacramental's: no -15 though not his patron (The Church p. 13).",
        ),
    ]
    if sourcebooks.in_play(sr.TCI, _books(saga)):
        found.append(
            DialogField(
                "irish",
                "Of Irish birth",
                "check",
                _irish(character),
                hint="Patrick, Brigid and Columba are his patrons "
                "(The Contested Isle p. 134).",
            )
        )
    found += [
        DialogField("tomb", "At the saint's tomb (+1)", "check", False),
        DialogField("aura", "Divine aura where he prays", "int", 0),
        DialogField("feast_day", "On his feast day (+3)", "check", False),
        DialogField(
            "pilgrimage",
            "Pilgrimage for him (+2)",
            "check",
            False,
            hint="In his honour, within the year.",
        ),
    ]
    if relics:
        found += [
            DialogField(
                "relic",
                "A relic he holds",
                "select",
                None,
                options=[(escape(label), key) for label, key, _, _ in relics],
                allow_blank=True,
                placeholder="(none)",
                hint="The saint's own: +2 a Faith Point (The Church p. 13); "
                "another's: +1 for touching it."
                if church
                else "+1 for touching the saint's relic (RoP: The Divine p. 87).",
            ),
            DialogField(
                "own_relic_of_saint",
                "His relic is of this saint",
                "check",
                False,
                show_if=lambda v: v.get("relic") == OWN_RELIC,
            ),
        ]
    if icons:
        found.append(
            DialogField(
                "icon",
                "An icon he venerated",
                "select",
                None,
                options=[(escape(label), key) for label, key, _ in icons],
                allow_blank=True,
                placeholder="(none)",
                hint="Its Aesthetic Quality / 5, for its saint (The Sundered "
                "Eagle p. 133): an hour's veneration first.",
            )
        )
    found += [
        DialogField(
            "donation",
            "A donation",
            "select",
            "0",
            options=DONATIONS,
            required=True,
        ),
        DialogField("peril", "In imminent peril (+2)", "check", False),
    ]
    if church:
        found.append(
            DialogField(
                "fasting",
                "Fasting this season (+1)",
                "check",
                dv.fasting(character, saga.current_season, saga.current_year),
                hint="The Church p. 12: Indulgence, Vigil or Fast keeps one.",
            )
        )
    found += [
        DialogField(
            "unchristian",
            "Unchristian acts this month",
            "select",
            "0",
            options=[("None", "0"), ("-1", "1"), ("-2", "2"), ("-3", "3")],
            required=True,
        ),
        DialogField("miracle_lately", "A miracle this month (-20)", "check", False),
        *_yazdan(saga),
        DialogField(
            "pure",
            "Ritually pure (the Nahn rite)",
            "check",
            False,
            show_if=lambda v: bool(v.get("yazata")),
        ),
        _power_field(saga),
    ]
    return found


def _situation(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[dv.Situation, str]:
    faith, of_saint = _relic(saga, character, values)
    icon, warning = _icon_bonus(saga, values)
    situation = dv.Situation(
        tomb=bool(values.get("tomb")),
        aura=_number(values.get("aura")),
        feast_day=bool(values.get("feast_day")),
        pilgrimage=bool(values.get("pilgrimage")),
        relic_faith=faith,
        relic_of_the_saint=of_saint,
        icon=icon,
        donation=int(values.get("donation") or 0),
        peril=bool(values.get("peril")),
        fasting=bool(values.get("fasting")),
        unchristian=int(values.get("unchristian") or 0),
        miracle_lately=bool(values.get("miracle_lately")),
        appropriate=bool(values.get("appropriate")),
        irish=bool(values.get("irish")),
    )
    return situation, warning


def _petition(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[dv.Petition, str]:
    name = _saint_name(values)
    saint = catalog_saint(saga, name)
    situation, warning = _situation(saga, character, values)
    found = dv.petition(
        character,
        name,
        situation,
        anyone=saint is not None and saint.anyone,
        irish_patron=saint is not None and saint.irish_patron,
        the_church=the_church(saga),
    )
    return found, warning


def _invoke_problem(values: dict[str, Any]) -> str | None:
    if not _saint_name(values):
        return "Name the saint."
    if problem := _yazata_problem(values, threat=False):
        return problem
    if _number(values.get("aura")) < 0:
        return "A Divine aura can't be below 0."
    return None


def invoke_live(saga: Saga, character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        name = _saint_name(values)
        if not name:
            return "[dim]Choose or name the saint.[/]"
        found, warning = _petition(saga, character, values)
        chance = dv.chance(found.total) * 100
        lines = [
            "[i]A heartfelt request, once a day, for a miracle.[/]",
            f"Simple die {_signed(found.total)} [dim]= {' '.join(found.terms)}[/]",
            f"Against [b]15 + the storyguide's simple die[/], rolled in secret: "
            f"[b]{chance:.0f}%[/] [dim](RoP: The Divine p. 87)[/]",
        ]
        if found.familiar:
            lines.append(f"[dim]No -15: {escape(found.familiar)}.[/]")
        else:
            lines.append(
                "[$text-error]-15: not his patron, nor one he is devoted to.[/]"
            )
        faith, of_saint = _relic(saga, character, values)
        if faith is not None and of_saint and the_church(saga):
            lines.append(
                "[dim]The relic: once a day, for the one who tends or carries "
                "it, or a day's veneration at its shrine with the custodians' "
                "leave (The Church p. 13).[/]"
            )
        if the_church(saga):
            record = dv.devotion(character, name)
            if record is not None:
                lines.append(
                    f"[dim]Devotion: {escape(dv.devotion_label(record))}; he "
                    "keeps the saint's feast each year.[/]"
                )
        if warning:
            lines.append(f"[$text-error]{escape(warning)}[/]")
        lines += _saint_lines(saga, name, values.get("power"))
        problem = _invoke_problem(values)
        if problem:
            lines.append(f"[$text-error]{escape(problem)}[/]")
        return "\n".join(lines)

    return live


def invoke_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Invoke a Saint: the roll, and if the saint hears, the miracle
    asked; written in the Diary."""
    if character is None:
        return Refuse(INVOKE, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        name = _saint_name(values)
        found, _ = _petition(saga, character, values)
        rolled = dv.invoke(found.total, _rng(rng))
        lines = [
            f"Die {rolled.die} + {found.total} = {rolled.rolled} against 15 + "
            f"{rolled.ease_die} = {rolled.ease}."
        ]
        power = sr.POWERS.get(str(values.get("power") or ""))
        if rolled.heard:
            asked = f": {power.name}" if power is not None else ""
            lines.append(f"{name} hears him and works a miracle{asked}.")
            if dv.devoted(character, name) and the_church(saga):
                lines.append(
                    "Witnessing it is worth 5 to 10 Devotion Points (The "
                    "Church p. 14): More's Devotion Points."
                )
            title = f"Miracle of {name}"
        else:
            lines.append(f"{name} does not answer; he may ask again tomorrow.")
            title = f"Invoked {name}"
        if not values.get("yazata"):
            dv.note_answer(
                character, name, rolled.heard, saga.current_season, saga.current_year
            )
        _diary(saga, character, title, " ".join(lines))
        return notes(*map(escape, lines))

    return Form(
        f"{INVOKE}: {escape(character.name)}",
        lambda: invoke_fields(saga, character),
        apply,
        validate=_invoke_problem,
        live=invoke_live(saga, character),
        save_label="Pray",
        help_id=HELP_ID,
        inspector="The Invocation",
    )


# -- Threaten a Saint --

THREATEN = "Threaten a Saint"


def threaten_fields(saga: Saga, character: Character) -> list[DialogField]:
    def might_of(values: dict[str, Any]) -> dict[str, Any]:
        saint = catalog_saint(saga, _saint_name(values))
        return {"might": saint.might if saint is not None else None}

    fields = _refused_fields(character)
    fields[0].fills = might_of
    first = catalog_saint(saga, str(fields[0].value or ""))
    return [
        *fields,
        DialogField(
            "might",
            "The saint's Divine Might",
            "int",
            first.might if first is not None else sr.RANKS["local"],
            hint="Mary 100, a greater saint 75, an area saint 50, a local "
            "saint 25 (RoP: The Divine p. 89).",
        ),
        *(
            DialogField(key, f"{label} (+{value})", "check", False)
            for key, (label, value) in dv.THREATS.items()
        ),
        DialogField("miracle_lately", "A miracle this month (-20)", "check", False),
        *_yazdan(saga),
        DialogField(
            "confidence",
            "Confidence Points spent",
            "int",
            0,
            hint="+3 each; Faith Points may not be spent.",
        ),
        _power_field(saga),
    ]


def _threat(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[int, tuple[str, ...], int]:
    name = _saint_name(values)
    saint = catalog_saint(saga, name)
    reason = dv.familiar(
        character,
        name,
        dv.Situation(),
        anyone=saint is not None and saint.anyone,
        the_church=the_church(saga),
    )
    total, terms = dv.threat_total(
        character,
        tuple(key for key in dv.THREATS if values.get(key)),
        miracle_lately=bool(values.get("miracle_lately")),
        unfamiliar=not reason,
        confidence=_number(values.get("confidence")),
    )
    return total, terms, dv.threat_ease(_number(values.get("might")))


def _threat_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        if not _saint_name(values):
            return "Name the saint."
        if found := _yazata_problem(values, threat=True):
            return found
        if not any(
            dv.same_saint(_saint_name(values), n) for n in dv.refused(character)
        ):
            return "Only a saint who refused his invocation may be threatened."
        spent = _number(values.get("confidence"))
        if spent < 0:
            return "Confidence spent can't be below 0."
        if spent > character.background.confidence_points:
            return (
                f"He has only {character.background.confidence_points} "
                "Confidence Points."
            )
        if _number(values.get("might")) < 0:
            return "A Might can't be below 0."
        return None

    return problem


def threaten_live(saga: Saga, character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        name = _saint_name(values)
        if not name:
            return "[dim]Choose or name the saint.[/]"
        total, terms, ease = _threat(saga, character, values)
        lines = [
            "[i]Only after the saint has refused an invocation: the "
            "humiliation of a saint.[/]",
            f"Stress die {_signed(total)} [dim]= {' '.join(terms)}[/]",
            f"Against [b]{ease}[/] [dim](9 + Might / 5, RoP: The Divine pp. 87-88)[/]",
            "[dim]Fail: no answer to his prayers for a month. Fail by 10 or "
            "more: a minor curse and nothing for a season. Botch: the "
            "saint's curse.[/]",
        ]
        lines += _saint_lines(saga, name, values.get("power"))
        problem = _threat_problem(character)(values)
        if problem:
            lines.append(f"[$text-error]{escape(problem)}[/]")
        return "\n".join(lines)

    return live


def threaten_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Threaten a Saint: the roll, its outcome, the Confidence
    spent; written in the Diary."""
    if character is None:
        return Refuse(THREATEN, "Choose a character first.")
    if not dv.refused(character):
        return Refuse(
            THREATEN,
            "No saint has refused him: only a saint who refused his invocation "
            "may be threatened (RoP: The Divine p. 87).",
        )

    def apply(values: dict[str, Any]) -> list[str]:
        name = _saint_name(values)
        total, _, ease = _threat(saga, character, values)
        spent = _number(values.get("confidence"))
        character.background.confidence_points -= max(0, spent)
        roll = dice.Roll(total, dice.stress_die(_rng(rng), saga=saga), ease)
        outcome = dv.threat_outcome(roll)
        shown = "a botch" if roll.die.botched else str(roll.die.value)
        lines = [
            f"Die {shown} + {total} = {roll.total} against {ease}.",
            dv.THREAT_OUTCOMES[outcome],
        ]
        power = sr.POWERS.get(str(values.get("power") or ""))
        if outcome == dv.THREAT_GRANTED and power is not None:
            lines.append(f"{name} works {power.name}.")
        dv.clear_refusal(character, name)
        _diary(saga, character, f"Threatened {name}", " ".join(lines))
        return notes(*map(escape, lines))

    return Form(
        f"{THREATEN}: {escape(character.name)}",
        lambda: threaten_fields(saga, character),
        apply,
        validate=_threat_problem(character),
        live=threaten_live(saga, character),
        save_label="Threaten",
        help_id=HELP_ID,
        inspector="The Threat",
    )


# -- Devotion Points --

POINTS = "Devotion Points"


def points_fields(saga: Saga, character: Character) -> list[DialogField]:
    def suggested(values: dict[str, Any]) -> dict[str, Any]:
        gain = dv.GAINS.get(str(values.get("how") or ""))
        return {"points": abs(gain.low) if gain is not None else None}

    how = dv.CREATION if character.in_creation else "season"
    fields = _saint_fields(saga, character)
    return [
        *fields,
        DialogField(
            "how",
            "How",
            "select",
            how,
            options=[(escape(g.label), key) for key, g in dv.GAINS.items()],
            required=True,
            fills=suggested,
        ),
        DialogField(
            "points",
            "Points gained (or lost)",
            "int",
            abs(dv.GAINS[how].low),
            hint="Devotion Points; lost, for a neglected feast.",
        ),
    ]


def _points(values: dict[str, Any]) -> int:
    """The change in Devotion Points: negative for a neglected feast."""
    points = abs(_number(values.get("points")))
    return -points if values.get("how") == dv.NEGLECT else points


def _points_problem(character: Character) -> Any:
    def problem(values: dict[str, Any]) -> str | None:
        name = _saint_name(values)
        if not name:
            return "Name the saint."
        if _number(values.get("points")) < 0:
            return "Type the points as a number of 0 or more."
        if not _number(values.get("points")):
            return "Gain at least one Devotion Point."
        if values.get("how") == dv.CREATION:
            return dv.creation_problem(character, name, _points(values))
        return None

    return problem


def points_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        name = _saint_name(values)
        gain = dv.GAINS.get(str(values.get("how") or ""))
        lines: list[str] = []
        if gain is not None and gain.hint:
            cited = gain.hint.replace("(p", "(The Church p")
            lines.append(f"[i]{escape(cited)}[/]")
        if name:
            record = dv.devotion(character, name)
            before = record.points if record is not None else 0
            after = max(0, before + _points(values))
            lines.append(
                f"Devotion: {escape(name)} [b]{dv.score(after)}[/] ({after} "
                f"points) [dim]from {dv.score(before)} ({before}); it rises as "
                "an Ability does, on Devotion Points alone, with no "
                "Specialty.[/]"
            )
        if values.get("how") == dv.CREATION:
            lines.append(
                f"[dim]At creation: {dv.creation_points(character)} Devotion "
                "Points, among as many saints.[/]"
            )
        lines.append(
            "[dim]A Devotion costs the saint's feast day each year: neglected, "
            "at least 3 points are lost (The Church pp. 13-14).[/]"
        )
        problem = _points_problem(character)(values)
        if problem:
            lines.append(f"[$text-error]{escape(problem)}[/]")
        return "\n".join(lines)

    return live


def points_form(saga: Saga, character: Character | None) -> Command:
    """More's Devotion Points: a Devotion begun or raised (or lowered for
    a neglected feast); written in the Diary."""
    if character is None:
        return Refuse(POINTS, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        name = _saint_name(values)
        change = _points(values)
        lines: list[str] = []
        if change:
            record = dv.add_points(character, name, change)
            gain = dv.GAINS.get(str(values.get("how") or ""))
            why = gain.label if gain is not None else ""
            verb = "lost" if change < 0 else "gained"
            lines.append(
                f"{abs(change)} Devotion Point(s) {verb} toward {record.name} "
                f"({why}): Devotion {dv.devotion_label(record)}."
            )
        if lines:
            _diary(saga, character, f"Devotion to {name}", " ".join(lines))
        return notes(*map(escape, lines))

    return Form(
        f"{POINTS}: {escape(character.name)}",
        lambda: points_fields(saga, character),
        apply,
        validate=_points_problem(character),
        live=points_live(character),
        help_id=HELP_ID,
        inspector="The Devotion",
    )


# -- the patron saint (The Church p. 13) --

PATRON = "Patron Saint"
NO_PATRON = "-none-"


def patron_fields(saga: Saga, character: Character) -> list[DialogField]:
    listed = saint_options(saga, character)
    held = dv.patron(character)
    return [
        DialogField(
            "saint",
            "His patron saint",
            "select",
            next((v for _, v in listed if dv.same_saint(v, held)), NO_PATRON),
            options=[("(none)", NO_PATRON), *listed],
            required=True,
            hint="Often his church's, his home's or his trade's saint, or one "
            "he is devoted to: the player's choice. Anyone may have one, Pious "
            "or not (The Church p. 13).",
        ),
        DialogField(
            "other",
            "Another saint's name",
            "text",
            "",
            placeholder="e.g. Saint Bartholomew",
            show_if=lambda v: v.get("saint") == OTHER,
        ),
    ]


def _patron_problem(values: dict[str, Any]) -> str | None:
    if values.get("saint") == OTHER and not str(values.get("other") or "").strip():
        return "Name the saint."
    return None


def patron_form(saga: Saga, character: Character | None) -> Command:
    """More's Patron Saint: the saint he calls on without the -15 (The
    Church p. 13; RoP: The Divine p. 87), or none."""
    if character is None:
        return Refuse(PATRON, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        chosen = "" if values.get("saint") == NO_PATRON else _saint_name(values)
        was = dv.patron(character)
        if dv.same_saint(was, chosen) or (not was and not chosen):
            return []
        dv.set_patron(character, chosen)
        line = (
            f"{chosen} is now his patron saint."
            if chosen
            else f"{was} is no longer his patron saint."
        )
        _diary(saga, character, "Patron saint", line)
        return notes(escape(line))

    return Form(
        f"{PATRON}: {escape(character.name)}",
        lambda: patron_fields(saga, character),
        apply,
        validate=_patron_problem,
        help_id=HELP_ID,
    )


# -- Indulgence, Vigil or Fast (The Church pp. 11-12) --

PIETY_ACT = "Indulgence, Vigil or Fast"
INDULGENCE = "indulgence"
VIGIL = "vigil"
FAST = "fast"
ACTS: dict[str, str] = {
    INDULGENCE: "Buy an indulgence",
    VIGIL: "Keep a vigil",
    FAST: "Keep a season's fast",
}


def piety_fields(character: Character) -> list[DialogField]:
    def indulgence(values: dict[str, Any]) -> bool:
        return values.get("act") == INDULGENCE

    wealthy = any(vf.vf_id == _WEALTHY for vf in character.virtues_flaws)
    return [
        DialogField(
            "act",
            "The act",
            "select",
            VIGIL,
            options=[(label, key) for key, label in ACTS.items()],
            required=True,
        ),
        DialogField(
            "seasons",
            "Seasons of penance remitted",
            "int",
            1,
            show_if=indulgence,
        ),
        DialogField(
            "wealthy",
            "He is wealthy",
            "check",
            wealthy,
            hint="A pound or more a season; the poor give what they can, "
            "most often 6 pennies.",
            show_if=indulgence,
        ),
        DialogField(
            "works_done",
            "The season of charitable works is done",
            "check",
            False,
            hint="Then: Piety experience and a Faith Point.",
            show_if=indulgence,
        ),
        DialogField(
            "task",
            "The virtuous task tomorrow",
            "text",
            "",
            placeholder="e.g. facing the bishop's court",
            show_if=lambda v: v.get("act") == VIGIL,
        ),
    ]


def _piety_problem(values: dict[str, Any]) -> str | None:
    if values.get("act") == INDULGENCE and _number(values.get("seasons")) < 1:
        return "An indulgence remits at least one season."
    if values.get("act") == VIGIL and not str(values.get("task") or "").strip():
        return "Name the virtuous task the Confidence Point is for."
    return None


def piety_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        act = values.get("act")
        lines: list[str] = []
        if act == INDULGENCE:
            seasons = max(0, _number(values.get("seasons")))
            price = dv.indulgence_price(seasons, bool(values.get("wealthy")))
            lines += [
                "[i]Not forgiveness, which is confession's: a penance shortened, "
                "with repentance and good works.[/]",
                f"About [b]{price}[/] pennies for {seasons} season(s) "
                "[dim](The Church p. 12)[/], then a season of charitable works.",
                f"After it: [b]{seasons}[/] experience in Reputation: Piety and "
                "[b]1[/] temporary Faith Point.",
            ]
        elif act == VIGIL:
            lines += [
                "[i]The night before an important event, in prayer in a church.[/]",
                "A [b]Fatigue level[/], until a full night's sleep is made up; "
                "[b]1 Confidence Point[/], to spend tomorrow on the task named "
                "[dim](The Church p. 12)[/].",
            ]
        else:
            lines += [
                "[i]Bread and water, as local custom has it, for the season.[/]",
                "[b]+1[/] to invoking a saint this season (not cumulative), and "
                "a [b]Fatigue level[/] all season [dim](The Church p. 12)[/].",
            ]
        problem = _piety_problem(values)
        if problem:
            lines.append(f"[$text-error]{escape(problem)}[/]")
        return "\n".join(lines)

    return live


def _piety(character: Character) -> ScoredTrait:
    found = next(
        (r for r in character.reputations if r.name.casefold() == dv.PIETY.casefold()),
        None,
    )
    if found is None:
        found = ScoredTrait(dv.PIETY, 0)
        character.reputations.append(found)
    return found


def piety_form(saga: Saga, character: Character | None) -> Command:
    """More's Indulgence, Vigil or Fast: what each act gives and costs, on
    the sheet and in the Diary."""
    if character is None:
        return Refuse(PIETY_ACT, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        act = values.get("act")
        if act == INDULGENCE:
            seasons = _number(values.get("seasons"))
            price = dv.indulgence_price(seasons, bool(values.get("wealthy")))
            lines = [f"An indulgence of {seasons} season(s), about {price} pennies."]
            if values.get("works_done"):
                character.background.faith_points += 1
                confidence.add_deeds(_piety(character), seasons)
                lines.append(
                    f"With the season of charitable works: {seasons} experience "
                    "in Reputation: Piety and 1 Faith Point."
                )
            else:
                lines.append("A season of charitable works must follow.")
            title = "Bought an indulgence"
        elif act == VIGIL:
            task = str(values.get("task") or "").strip()
            out = harm.lose_fatigue(character, long_term=True)
            character.background.confidence_points += 1
            lines = [
                f"A night's vigil before {task}: a Confidence Point for it"
                + (" (already unconscious)." if out else ", and a Fatigue level.")
            ]
            title = "Kept a vigil"
        else:
            dv.keep_fast(character, saga.current_season, saga.current_year)
            out = harm.lose_fatigue(character, long_term=True)
            lines = [
                f"A fast through {saga.current_season} {saga.current_year}: +1 to "
                "invoking a saint, and a Fatigue level all season"
                + (" (already unconscious)." if out else ".")
            ]
            title = "Kept a fast"
        _diary(saga, character, title, " ".join(lines))
        return notes(*map(escape, lines))

    return Form(
        f"{PIETY_ACT}: {escape(character.name)}",
        lambda: piety_fields(character),
        apply,
        validate=_piety_problem,
        live=piety_live(character),
        help_id=HELP_ID,
        inspector="The Act of Piety",
    )
