"""More's House Acclaim and Reputation Roll on a character's Reputations
-- no UI in here.

House Acclaim: a magus Bonisagi's research made public, in Acclaim
points, or a Flambeau's deed, in experience (taken away for an ignoble
one), with the Bonisagi's argument over a folio and Trianoma's cipher as
rolls. Reputation Roll: whether someone has heard of a Reputation, 3
higher between colleagues of a Jerbiton league. The rules and their pages
are rules.acclaim's."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape
from ..models import Character, DiaryEntry, Saga, ScoredTrait
from ..rules import acclaim as ac
from ..rules.book_seasons import language_score
from ..rules.confidence import add_deeds
from ..rules.scores import ability_level

TITLE = "House Acclaim"
ROLL_TITLE = "Reputation Roll"
HELP = "house-acclaim"
ROLL_HELP = "reputation-roll"
AWARD, FOLIO, CIPHER = "award", "folio", "cipher"
LOUD, CRAFTY = "loud", "crafty"
TOURNAMENT = "tournament"

#: Each figure an award may need is a field of its own: its label -> key.
AMOUNT_KEYS: dict[str, str] = {
    amount: f"amount_{i}"
    for i, amount in enumerate(
        dict.fromkeys(
            a.amount for a in (*ac.RESEARCH.values(), *ac.DEEDS.values()) if a.amount
        )
    )
}


def offers(_saga: Saga, character: Character) -> bool:
    """Whether More offers House Acclaim: a magus of Bonisagus or
    Flambeau, or anyone holding House Acclaim."""
    return ac.keeps_acclaim(character)


def offers_flambeau(character: Character) -> bool:
    """Whether he keeps House Acclaim by House Flambeau's table of deeds."""
    return ac.keeps_acclaim(character) and house(character) == ac.FLAMBEAU


def house(character: Character) -> str:
    """The House whose table applies: his own, else the one his House
    Acclaim's reach names (Bonisagus when it names neither)."""
    own = ac.house_of(character)
    if own is not None:
        return own
    held = ac.acclaim_of(character)
    if held is not None and held.reach == ac.REACH[ac.FLAMBEAU]:
        return ac.FLAMBEAU
    return ac.BONISAGUS


def _table(of: str) -> dict[str, ac.Award]:
    return ac.RESEARCH if of == ac.BONISAGUS else ac.DEEDS


def _chosen(of: str, values: dict[str, Any]) -> ac.Award | None:
    if values.get("what", AWARD) != AWARD:
        return None
    return _table(of).get(str(values.get("award") or ""))


def points(of: str, values: dict[str, Any]) -> int:
    """What the chosen award is worth, from the figures given."""
    award = _chosen(of, values)
    if award is None:
        return 0
    if values.get("award") == TOURNAMENT:
        return ac.TOURNAMENT.get(str(values.get("place") or ""), ("", 0))[1]
    figure = values.get(AMOUNT_KEYS.get(award.amount, ""))
    amount = int(figure) if figure is not None else award.least
    return ac.worth(award, amount, bool(values.get("in_folio")))


def _what(*keys: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: values.get("what", AWARD) in keys


def _label(award: ac.Award) -> str:
    return f"{award.label} ({award.rule})"


def acclaim_fields(character: Character) -> list[DialogField]:
    """What happened, its figure, and for the rolls their numbers."""
    of = house(character)
    table = _table(of)
    held = ac.acclaim_of(character)
    bonisagus = of == ac.BONISAGUS
    whats = [("Research made public" if bonisagus else "A deed", AWARD)]
    if bonisagus:
        whats += [
            ("An argument over a folio's contents (a roll)", FOLIO),
            ("Decode Trianoma's cipher (a roll)", CIPHER),
        ]

    def needs(amount: str) -> Callable[[dict[str, Any]], bool]:
        def show(values: dict[str, Any]) -> bool:
            award = _chosen(of, values)
            return award is not None and award.amount == amount

        return show

    def text(values: dict[str, Any]) -> bool:
        award = _chosen(of, values)
        return award is not None and award.folio

    def ignoble(values: dict[str, Any]) -> bool:
        return points(of, values) < 0

    fields = [
        DialogField("what", "What", "select", AWARD, options=whats),
        DialogField(
            "award",
            "The research" if bonisagus else "The deed",
            "select",
            next(iter(table)),
            options=[(_label(a), key) for key, a in table.items()],
            show_if=_what(AWARD),
            hint=(
                "In Acclaim points; findings must be made public to earn them "
                "(TL p. 21)."
                if bonisagus
                else "In experience points; done before credible witnesses who "
                "will tell of it (HoH:S p. 31)."
            ),
        ),
        *(
            DialogField(key, amount, "optint", None, show_if=needs(amount))
            for amount, key in AMOUNT_KEYS.items()
            if any(a.amount == amount for a in table.values())
        ),
        DialogField(
            "in_folio",
            "In a folio (twice the points)",
            "check",
            False,
            show_if=text,
        ),
    ]
    if not bonisagus:
        fields.append(
            DialogField(
                "place",
                "His place",
                "select",
                "competed",
                options=[
                    (f"{label} ({worth:+d} xp)", key)
                    for key, (label, worth) in ac.TOURNAMENT.items()
                ],
                show_if=lambda v: _what(AWARD)(v) and v.get("award") == TOURNAMENT,
                hint="Competing is 1; a finalist 2 more, the champion 2 more "
                "again; a dismal showing -3 (HoH:S p. 31).",
            )
        )
    if held is None and not bonisagus and ac.has(character, ac.FAMOUS):
        fields.append(
            DialogField(
                "famous",
                "Famous put in it (starts at 4)",
                "check",
                False,
                show_if=_what(AWARD),
            )
        )
    if not bonisagus and (held is None or held.score == 0):
        fields.append(
            DialogField(
                "bad_name",
                "The bad Reputation it starts",
                "text",
                "",
                show_if=ignoble,
                hint="House Acclaim is at 0, so an ignoble act starts a bad "
                "Reputation by the ordinary rules (DE p. 386).",
            )
        )
    if bonisagus:
        fields += [
            DialogField(
                "style",
                "His way of arguing",
                "select",
                LOUD,
                options=[
                    ("Loudly: Presence + Leadership", LOUD),
                    ("Craftily: Communication + Artes Liberales", CRAFTY),
                ],
                show_if=_what(FOLIO),
            ),
            DialogField(
                "opponent",
                "The other magus's total",
                "int",
                0,
                show_if=_what(FOLIO),
                hint="His own stress roll with his House Acclaim; the higher "
                "total wins.",
            ),
            DialogField(
                "communication",
                "The author's Communication",
                "int",
                0,
                show_if=_what(CIPHER),
            ),
            DialogField(
                "intrigue",
                "The author's Intrigue",
                "int",
                0,
                show_if=_what(CIPHER),
            ),
            DialogField(
                "decoded_before",
                "Decoded one before (+3)",
                "check",
                False,
                show_if=_what(CIPHER),
            ),
        ]
    return fields


def _score(character: Character) -> int:
    held = ac.acclaim_of(character)
    return max(0, held.score) if held is not None else 0


def folio_bonus(character: Character, values: dict[str, Any]) -> int:
    """The argument's modifiers: Presence + Leadership, or Communication +
    Artes Liberales, + House Acclaim."""
    traits = character.characteristics
    if values.get("style") == CRAFTY:
        base = traits.communication + ability_level(character, "Artes Liberales")
    else:
        base = traits.presence + ability_level(character, "Leadership")
    return base + _score(character)


def _cipher(character: Character, values: dict[str, Any]) -> tuple[int, int]:
    """(the decoder's modifiers, what they must beat)."""
    bonus = ac.cipher_bonus(
        character.characteristics.intelligence,
        language_score(character, "Latin"),
        bool(values.get("decoded_before")),
    )
    ease = ac.cipher_ease(
        int(values.get("communication") or 0), int(values.get("intrigue") or 0)
    )
    return bonus, ease


def _projected(character: Character, of: str, gained: int, famous: bool) -> str:
    """The score the points would bring House Acclaim to."""
    held = ac.acclaim_of(character)
    trial = (
        ScoredTrait(held.name, held.score, deeds=held.deeds)
        if held is not None
        else ScoredTrait(ac.ACCLAIM, ac.FAMOUS_SCORE if famous else 0)
    )
    if held is None and of == ac.FLAMBEAU and ac.has(character, ac.MILES):
        add_deeds(trial, ac.MILES_XP)
    before = trial.score
    if gained >= 0:
        add_deeds(trial, gained)
    else:
        ac.lose(trial, -gained)
    new = "" if held is not None else "a new "
    rank = f" ({ac.rank(trial.score)})" if of == ac.BONISAGUS else ""
    return (
        f"{new}House Acclaim {before} to {trial.score}{rank}, "
        f"{trial.deeds} toward the next."
    )


def acclaim_lines(character: Character, values: dict[str, Any]) -> list[str]:
    """What Save will do, said in the inspector."""
    of = house(character)
    what = values.get("what", AWARD)
    if what == FOLIO:
        bonus = folio_bonus(character, values)
        return [
            f"Stress die + {bonus} (with House Acclaim {_score(character)}) "
            f"against the other's {int(values.get('opponent') or 0)}; the "
            f"higher wins ({ac.FOLIO_SOURCE}).",
        ]
    if what == CIPHER:
        bonus, ease = _cipher(character, values)
        return [
            f"A day's work: Intelligence + Latin + stress die = {bonus} + die, "
            f"higher than {ease} (6 + the author's Communication + Intrigue) "
            f"to decode ({ac.CIPHER_SOURCE}).",
        ]
    gained = points(of, values)
    unit = "Acclaim points" if of == ac.BONISAGUS else "experience points"
    source = ac.BONISAGUS_SOURCE if of == ac.BONISAGUS else ac.FLAMBEAU_SOURCE
    lines = [
        f"{gained:+d} {unit}: "
        + _projected(character, of, gained, bool(values.get("famous")))
        + f" ({source})."
    ]
    if gained < 0 and _score(character) == 0 and of == ac.FLAMBEAU:
        name = str(values.get("bad_name") or "").strip()
        lines.append(
            f"At 0 it can fall no further: the act starts {name}, a bad "
            "Reputation (DE p. 386)."
            if name
            else "At 0 it can fall no further: name the bad Reputation the "
            "act starts (DE p. 386)."
        )
    if values.get("award") in (
        "won_certamen",
        "won_senior",
        "lost_certamen",
        "lost_junior",
    ):
        lines.append("Only a certamen settling a real dispute counts, never sport.")
    held = ac.acclaim_of(character)
    if held is not None:
        lines += ac.benefits(character, held)
    return lines


def _live(character: Character) -> Callable[[dict[str, Any]], str]:
    return lambda values: "\n".join(
        f"{BULLET} {escape(line)}" for line in acclaim_lines(character, values)
    )


def _problem(character: Character) -> Callable[[dict[str, Any]], str | None]:
    of = house(character)

    def problem(values: dict[str, Any]) -> str | None:
        award = _chosen(of, values)
        if award is None or not award.amount or values.get("award") == TOURNAMENT:
            return None
        figure = values.get(AMOUNT_KEYS[award.amount])
        if figure is None:
            return f"Give the {award.amount.lower()}."
        if int(figure) < 0:
            return f"The {award.amount.lower()} can't be below 0."
        if award.most and not award.least <= int(figure) <= award.most:
            return f"The award is {award.rule}."
        return None

    return problem


def record(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The award kept on House Acclaim, or the roll made; both in the
    Diary."""
    of = house(character)
    what = values.get("what", AWARD)
    if what == FOLIO:
        rolled = ac.folio_argument(
            rng, folio_bonus(character, values), int(values.get("opponent") or 0), saga
        )
        name = "An argument over a folio"
        lines = [
            f"Stress die {rolled.die} + {rolled.modifiers} = {rolled.total}: {rolled.said}"
        ]
    elif what == CIPHER:
        bonus, ease = _cipher(character, values)
        rolled = ac.decode_cipher(rng, bonus, ease, saga)
        name = "Trianoma's cipher"
        lines = [
            f"Stress die {rolled.die} + {rolled.modifiers} = {rolled.total}: {rolled.said}"
        ]
    else:
        award = _chosen(of, values)
        gained = points(of, values)
        held = ac.acclaim_of(character)
        lines = []
        if held is None:
            held = ac.start(character, of, bool(values.get("famous")))
            lines.append(f"Started House Acclaim at {held.score}.")
        change = ac.apply(character, held, gained, str(values.get("bad_name") or ""))
        name = TITLE
        rank = f" ({ac.rank(held.score)})" if of == ac.BONISAGUS else ""
        lines.append(
            f"{award.label if award else 'Acclaim'}: {gained:+d}; House Acclaim "
            f"{change.before} to {change.after}{rank}, {held.deeds} toward the next."
        )
        if change.bad:
            lines.append(f"At 0, the act is a bad Reputation: {change.bad}.")
    source = ac.BONISAGUS_SOURCE if of == ac.BONISAGUS else ac.FLAMBEAU_SOURCE
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            name,
            "\n".join([*lines, f"Rules: {source}"]),
        )
    )
    return notes(*lines)


def acclaim_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's House Acclaim: an award, or a roll, kept in the Diary."""
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    if not offers(saga, character):
        return Refuse(
            TITLE,
            "House Acclaim is kept by magi of House Bonisagus (True Lineages "
            "p. 21) and House Flambeau (Societates p. 31).",
        )
    chance = rng or random.Random()
    magus = character
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: acclaim_fields(magus),
        lambda values: record(saga, magus, values, chance),
        validate=_problem(magus),
        live=_live(magus),
        help_id=HELP,
        inspector=TITLE,
    )


# -- whether someone has heard of a Reputation --


def roll_fields(character: Character) -> list[DialogField]:
    reps = character.reputations
    return [
        DialogField(
            "reputation",
            "Reputation",
            "select",
            "0",
            options=[
                (
                    f"{escape(r.name)} ({r.score:+d}{', ' + r.type if r.type else ''})",
                    str(i),
                )
                for i, r in enumerate(reps)
            ],
            required=True,
        ),
        DialogField(
            "ease",
            "Where the listener is",
            "select",
            "6",
            options=[
                (f"{ease}: {', '.join(p for p in places if p)}", str(ease))
                for ease, places in ac.HEARD_EASE.items()
            ],
            hint="The Reputation's type says which column counts: Local, "
            "Ecclesiastical or Hermetic (DE p. 28).",
        ),
        DialogField(
            "colleague",
            "League colleague (+3)",
            "check",
            False,
            hint="Between magi of one league every Reputation counts 3 higher "
            "(HoH:S p. 53).",
        ),
    ]


def _reputation(character: Character, values: dict[str, Any]) -> ScoredTrait:
    index = int(values.get("reputation") or 0)
    return character.reputations[min(index, len(character.reputations) - 1)]


def roll_lines(character: Character, values: dict[str, Any]) -> list[str]:
    rep = _reputation(character, values)
    ease = int(values.get("ease") or 0)
    bonus = ac.heard_bonus(rep, bool(values.get("colleague")))
    column = dict(ac.heard_eases(rep.type)).get(ease, "")
    where = f" ({column.lower()})" if column else ""
    return [
        f"Stress die + {bonus} against {ease}{where}: equal or beat it and he "
        f"has heard of {rep.name}; the more it beats it by, the more he "
        f"knows ({ac.HEARD_SOURCE}).",
    ]


def record_roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    rep = _reputation(character, values)
    rolled = ac.heard_of(
        rng, rep, int(values.get("ease") or 0), bool(values.get("colleague")), saga
    )
    line = (
        f"{rep.name}: stress die {rolled.die} + {rolled.modifiers} = "
        f"{rolled.total}: {rolled.said}"
    )
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            ROLL_TITLE,
            f"{line}\nRules: {ac.HEARD_SOURCE}; {ac.LEAGUE_SOURCE}",
        )
    )
    return notes(line)


def roll_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Reputation Roll: has someone heard of one of his
    Reputations."""
    if character is None:
        return Refuse(ROLL_TITLE, "Choose a character first.")
    if not character.reputations:
        return Refuse(ROLL_TITLE, f"{escape(character.name)} has no Reputation yet.")
    chance = rng or random.Random()
    who = character
    return Form(
        f"{ROLL_TITLE}: {escape(who.name)}",
        lambda: roll_fields(who),
        lambda values: record_roll(saga, who, values, chance),
        live=lambda values: "\n".join(
            f"{BULLET} {escape(line)}" for line in roll_lines(who, values)
        ),
        save_label="Roll",
        help_id=ROLL_HELP,
        inspector=ROLL_TITLE,
    )
