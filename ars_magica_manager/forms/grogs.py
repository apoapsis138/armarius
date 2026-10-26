"""More's Reward or Punish and Pension on one of the covenfolk: the forms,
what each choice does, and the Diary entries -- no UI in here. The rules
and their pages are rules.grog_discipline's (Grogs pp. 23-26, Covenants
pp. 38-40, DE p. 186).

Reward or Punish writes the grog's Diary and a record of it on his
sheet; a punishment deals its wounds and Fatigue, may change his own
Loyal to Covenant, and writes what it costs the covenant's Loyalty into
the covenant's Diary, where Actions and Events adds it up. Pension
retires him on a pension (half his Wages) or for rent, or gives a dead
grog's widow his pension.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .. import inhabitants as inh
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape, plural
from ..models import (
    Character,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Discipline,
    Saga,
    ScoredTrait,
)
from ..rules import grog_discipline as gd
from ..rules import harm, recovery

DISCIPLINE_TITLE = "Reward or Punish"
PENSION_TITLE = "Pension"
DISCIPLINE_HELP = "grog-discipline"
PENSION_HELP = "grog-pension"
LOYALTY_EVENT = "Loyalty Event"
LOYAL_TRAIT = "Loyal to Covenant"


def _kind_options() -> list[tuple[str, str]]:
    rewards = [(f"Reward: {gd.LABELS[k]}", k) for k in gd.REWARDS]
    punishments = [
        (f"Punishment {n}: {gd.LABELS[k]}", k)
        for n, k in enumerate(gd.PUNISHMENTS, start=1)
    ]
    return rewards + punishments


def _kind_in(*kinds: str):
    return lambda values: values.get("kind") in kinds


def _punishing(values: dict[str, Any]) -> bool:
    return gd.is_punishment(str(values.get("kind") or ""))


def _wounding(values: dict[str, Any]) -> bool:
    return values.get("kind") in (gd.FLOGGING, gd.WHIPPING, gd.FUSTUARIUM)


def _by_magus(values: dict[str, Any]) -> bool:
    return _punishing(values) and values.get("ordered_by") == gd.MAGUS


def discipline_fields(character: Character) -> list[DialogField]:
    """What Reward or Punish asks: the reward or punishment, then its own
    details, then who orders it and what it costs in Loyalty."""
    durations = [(label, label) for label, _ in gd.DURATIONS]
    return [
        DialogField(
            "kind",
            "Reward or punishment",
            "select",
            gd.IMPROVED_RATIONS,
            options=_kind_options(),
            hint="The punishments in order of severity (Grogs pp. 24-25).",
        ),
        DialogField(
            "duration",
            "For how long",
            "select",
            "A month",
            options=durations,
            hint="A year of improved rations is +1 to his Living Conditions for "
            "aging; a season or two of the year on reduced rations -1, three or "
            "four -2 (Grogs pp. 23, 25).",
            show_if=_kind_in(*gd.LASTING),
        ),
        DialogField(
            "rank",
            "His rank now",
            "text",
            gd.rank(character),
            placeholder="custos",
            hint=f"The usual ranks: {gd.RANKS}.",
            show_if=_kind_in(gd.PROMOTION, gd.REDUCTION_IN_RANK),
        ),
        DialogField(
            "blows",
            "Blows",
            "select",
            "1",
            options=[(str(b), str(b)) for b in gd.FLOGGING_BLOWS],
            show_if=_kind_in(gd.FLOGGING),
        ),
        DialogField(
            "lashes",
            "Lashes",
            "int",
            10,
            hint="10 lashes a Light Wound, 30 a Medium, 50 a Heavy.",
            show_if=_kind_in(gd.WHIPPING),
        ),
        DialogField(
            "short_whip",
            "Short whip",
            "check",
            False,
            hint="The more severe: two wounds of the kind.",
            show_if=_kind_in(gd.WHIPPING),
        ),
        DialogField(
            "leaves",
            "He leaves the covenant",
            "check",
            True,
            show_if=_kind_in(gd.DISMISSAL),
        ),
        DialogField(
            "ordered_by",
            "Ordered by",
            "select",
            gd.OFFICER,
            options=list(gd.ORDERED_BY),
            show_if=_punishing,
        ),
        DialogField(
            "just",
            "Just and in proportion",
            "check",
            True,
            show_if=_punishing,
        ),
        DialogField(
            "category",
            "Counts as",
            "select",
            None,
            options=[
                (f"{name} ({points:+d})", name)
                for name, points in gd.PUNISHMENT_PENALTIES
            ],
            allow_blank=True,
            placeholder="(the usual for this punishment)",
            hint="Covenants p. 38's Loyalty Point penalties for a punishment.",
            show_if=_punishing,
        ),
        DialogField(
            "enjoyed",
            "The magus clearly enjoys it",
            "check",
            False,
            hint="A brutal punishment clearly enjoyed costs -15, not -12.",
            show_if=_by_magus,
        ),
        DialogField(
            "own_hand",
            "Dealt by the magus himself",
            "check",
            False,
            show_if=lambda v: _by_magus(v) and _wounding(v),
        ),
        DialogField(
            "by_magic",
            "  By magic (one step worse)",
            "check",
            False,
            show_if=lambda v: _by_magus(v) and _wounding(v) and bool(v.get("own_hand")),
        ),
        DialogField(
            "reputation",
            "His Reputation",
            "int",
            0,
            hint="Among the covenfolk: + if he is loved (adds to the penalty), - "
            "if disliked.",
            show_if=_punishing,
        ),
        DialogField(
            "loyal_change",
            "His Loyal changes by",
            "int",
            0,
            hint="The books leave his own Loyal to the troupe; it may drop for a "
            "while after a punishment (Grogs p. 24).",
        ),
        DialogField("note", "Why", "text", "", placeholder="for valour at the ford"),
    ]


@dataclass
class Outcome:
    """What a reward or punishment does, worked out from the form's
    values before anything is changed."""

    record: Discipline
    wounds: list[str] = field(default_factory=list)
    fatigue: int = 0
    loyalty: int = 0
    lines: list[str] = field(default_factory=list)
    leaves: bool = False


def _int(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


#: What a reward or punishment does that needs no figures.
_SAID: dict[str, str] = {
    gd.IMPROVED_RATIONS: "A whole year of them is +1 to his Living Conditions for "
    "that year's aging roll.",
    gd.PAY_AND_A_HALF: "Half his Wages again on the covenant's Wages while it lasts.",
    gd.IMPROVED_EQUIPMENT: "His for good, but surrendered if he is demoted (record it "
    "on his Personal Gear).",
    gd.CASTIGATION: "A single blow with the rod, at once.",
    gd.INFERIOR_DUTIES: "The worst jobs, done in his free time.",
    gd.REDUCED_RATIONS: "A season or two of the year on them is -1 to his Living "
    "Conditions for aging, three or four -2.",
    gd.FUSTUARIUM: "Beaten to death by the blindfolded turb. Few covenants have "
    "the right to order a death.",
}


def _record(saga: Saga, values: dict[str, Any]) -> tuple[Discipline, str]:
    """The record the choices make, and the duration's label."""
    kind = str(values.get("kind") or gd.IMPROVED_RATIONS)
    duration = str(values.get("duration") or "A month")
    ranked = kind in (gd.PROMOTION, gd.REDUCTION_IN_RANK)
    record = Discipline(
        saga.current_year,
        saga.current_season,
        kind,
        gd.DURATION_SEASONS.get(duration, 0) if kind in gd.LASTING else 0,
        rank=str(values.get("rank") or "") if ranked else "",
        note=str(values.get("note") or ""),
    )
    return record, duration


def _described(character: Character, record: Discipline, duration: str) -> list[str]:
    """The lines saying what the reward or punishment is."""
    kind = record.kind
    lines = [f"{gd.LABELS[kind]}: {duration.lower()}."] if kind in gd.LASTING else []
    if kind in _SAID:
        lines.append(_SAID[kind])
    rank = record.rank or "(rank not given)"
    if kind == gd.PROMOTION:
        lines.append(f"Now {rank}: better food, lodging, pay and pension.")
    elif kind == gd.REDUCTION_IN_RANK:
        lines.append(f"Now {rank}, for good.")
        held = gd.rewards_held(character)
        if held:
            lines.append(
                "He surrenders the equipment he was given: "
                + "; ".join(r.note or gd.LABELS[r.kind] for r in held)
                + "."
            )
    return lines


def _harm(done: Outcome, values: dict[str, Any]) -> None:
    """The wounds and Fatigue a flogging or whipping deals, and death."""
    kind = done.record.kind
    blows = int(str(values.get("blows") or "1"))
    lashes = max(_int(values.get("lashes"), 10), 0)
    done.wounds = gd.wounds_dealt(
        kind, blows=blows, lashes=lashes, short=bool(values.get("short_whip"))
    )
    done.fatigue = gd.fatigue_dealt(kind, blows)
    if kind == gd.FLOGGING:
        done.lines.append(
            f"{plural(blows, 'blow')}: {plural(len(done.wounds), 'Light Wound')} "
            f"and {plural(done.fatigue, 'Long-Term Fatigue level')}."
        )
    elif kind == gd.WHIPPING:
        hurt = (
            plural(len(done.wounds), f"{done.wounds[0].title()} Wound")
            if done.wounds
            else "no wound"
        )
        days = gd.whipping_recovery(lashes)
        done.lines.append(f"{lashes} lashes: {hurt}.")
        done.lines.append(
            f"{'A day' if days == 1 else 'A week'} to recover; his pay is docked "
            "for any longer."
        )
    elif kind == gd.DISMISSAL:
        done.leaves = bool(values.get("leaves", True))
        done.lines.append(
            "He leaves the covenant and its lists; he may bear a grudge."
            if done.leaves
            else "Dismissed, but still on the covenant's lists."
        )


def _loyalty(
    saga: Saga, character: Character, done: Outcome, values: dict[str, Any]
) -> None:
    """What a punishment costs the covenant's Loyalty points."""
    kind = done.record.kind
    covenant = saga.covenant(character.covenant_id)
    prevailing = inh.prevailing_loyalty(saga, covenant) if covenant else 0
    ordered_by = str(values.get("ordered_by") or gd.OFFICER)
    category = str(values.get("category") or gd.USUAL_CATEGORY[kind])
    if ordered_by == gd.MAGUS and values.get("enjoyed") and category == gd.BRUTAL:
        category = gd.BRUTAL_ENJOYED
    own = done.wounds if ordered_by == gd.MAGUS and values.get("own_hand") else []
    cost = gd.loyalty_cost(
        category,
        ordered_by=ordered_by,
        just=bool(values.get("just", True)),
        prevailing=prevailing,
        reputation=_int(values.get("reputation"), 0),
        own_wounds=own,
        by_magic=bool(values.get("by_magic")),
    )
    done.loyalty = cost.points
    done.lines += cost.lines
    done.lines.append(f"The covenant's Loyalty points: {cost.points:+d}.")


def outcome(saga: Saga, character: Character, values: dict[str, Any]) -> Outcome:
    """What the form's choices do to the grog and the covenant."""
    record, duration = _record(saga, values)
    done = Outcome(record, lines=_described(character, record, duration))
    _harm(done, values)
    if gd.is_punishment(record.kind):
        _loyalty(saga, character, done, values)
    change = _int(values.get("loyal_change"), 0)
    if change:
        done.lines.append(f"His {LOYAL_TRAIT} {change:+d}.")
    return done


def _live(saga: Saga, character: Character):
    def live(values: dict[str, Any]) -> str:
        return "\n".join(
            f"{BULLET} {escape(line)}"
            for line in outcome(saga, character, values).lines
        )

    return live


def _problem(values: dict[str, Any]) -> str | None:
    kind = values.get("kind")
    if kind in (gd.PROMOTION, gd.REDUCTION_IN_RANK) and not str(
        values.get("rank") or ""
    ):
        return "Give the rank he holds now."
    if kind == gd.WHIPPING and _int(values.get("lashes"), 0) < 1:
        return "A whipping is at least one lash."
    return None


def change_loyal(character: Character, change: int) -> None:
    """Move his Loyal to Covenant (or plain Loyal) by `change`, adding the
    trait if he has neither."""
    for name in (LOYAL_TRAIT, "Loyal"):
        trait = next(
            (
                t
                for t in character.personality_traits
                if t.name.strip().casefold() == name.casefold()
            ),
            None,
        )
        if trait is not None:
            trait.score += change
            return
    character.personality_traits.append(ScoredTrait(LOYAL_TRAIT, change))


def leave_covenant(saga: Saga, character: Character) -> None:
    """Take him off the covenant's lists and out of the covenant."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is not None:
        covenant.inhabitants = [
            r for r in covenant.inhabitants if r.character_id != character.id
        ]
    character.covenant_id = None


def _covenant_entry(
    saga: Saga, covenant: Covenant, name: str, details: str, loyalty: int | None
) -> None:
    covenant.diary.append(
        CovenantDiaryEntry(
            saga.current_year,
            saga.current_season,
            name,
            details,
            category=LOYALTY_EVENT if loyalty else "Inhabitants",
            loyalty=loyalty or None,
        )
    )


def apply_discipline(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    """Give the reward or punishment: his record and Diary, his wounds and
    Fatigue, his Loyal, and the covenant's Diary with the Loyalty it
    costs. Returns the lines said about it."""
    done = outcome(saga, character, values)
    covenant = saga.covenant(character.covenant_id)
    for severity in done.wounds:
        recovery.add_wound(character.wounds, severity)
    for _ in range(done.fatigue):
        harm.lose_fatigue(character, long_term=True)
    change = _int(values.get("loyal_change"), 0)
    if change:
        change_loyal(character, change)
    character.discipline.append(done.record)
    title = gd.LABELS[done.record.kind] + (
        f": {done.record.note}" if done.record.note else ""
    )
    details = "\n".join(done.lines)
    character.diary.append(
        DiaryEntry(saga.current_year, saga.current_season, title, details)
    )
    if covenant is not None and (done.loyalty or gd.is_punishment(done.record.kind)):
        _covenant_entry(
            saga, covenant, f"{character.name}: {title}", details, done.loyalty
        )
    if done.leaves:
        leave_covenant(saga, character)
    return notes(f"{character.name}: {title}.", *done.lines)


def _refusal(saga: Saga, character: Character | None, title: str) -> Refuse | None:
    if character is None or character.type != "grog":
        return Refuse(title, "Only one of the covenfolk (a grog) can be given this.")
    if saga.covenant(character.covenant_id) is None:
        return Refuse(title, f"{escape(character.name)} serves no covenant.")
    return None


def discipline_form(saga: Saga, character: Character | None) -> Command:
    """More's Reward or Punish on a grog."""
    refused = _refusal(saga, character, DISCIPLINE_TITLE)
    if refused is not None or character is None:
        return refused or Refuse(DISCIPLINE_TITLE, "Choose a grog first.")
    if character.wounds.dead:
        return Refuse(DISCIPLINE_TITLE, f"{escape(character.name)} is dead.")
    grog = character
    return Form(
        f"{DISCIPLINE_TITLE}: {escape(grog.name)}",
        lambda: discipline_fields(grog),
        lambda values: apply_discipline(saga, grog, values),
        validate=_problem,
        live=_live(saga, grog),
        save_label="Give",
        help_id=DISCIPLINE_HELP,
        inspector="What It Does",
    )


# -- Pension --


def pension_fields(saga: Saga, character: Character) -> list[DialogField]:
    covenant = saga.covenant(character.covenant_id)
    grants = covenant.loyalty.pension if covenant is not None else False
    fields: list[DialogField] = []
    if not character.wounds.dead:
        fields.append(
            DialogField(
                "terms",
                "He retires on",
                "select",
                gd.PENSION,
                options=list(gd.RETIREMENT_TERMS),
                hint="He still counts as one of the covenant for its finances; Grogs "
                "gives half to three-quarters of his pay, the Definitive Edition "
                "half (p. 186), which the app uses.",
            )
        )
    fields += [
        DialogField(
            "grants",
            "Grants pensions",
            "check",
            grants,
            hint="The covenant grants pensions to all its retirees: +10 Loyalty "
            "(DE p. 186), on its Loyalty's Money.",
        ),
        DialogField("note", "Note", "text", ""),
    ]
    return fields


def apply_pension(
    saga: Saga, character: Character, values: dict[str, Any]
) -> list[str]:
    """Retire him, or give his widow his pension."""
    covenant = saga.covenant(character.covenant_id)
    assert covenant is not None  # pension_form refuses a grog with none
    covenant.loyalty.pension = bool(values.get("grants"))
    note = str(values.get("note") or "")
    if character.wounds.dead:
        kind, terms, title = gd.WIDOW_PENSION, "", "His widow's pension"
        covenant.loyalty.pensioners += 1
        lines = [
            "His widow draws the pension he would have had: half Wages a year, "
            f"one of the covenant's {covenant.loyalty.pensioners} pensioner(s)."
        ]
        if not covenant.loyalty.pension:
            lines.append(
                "The covenant grants no pensions: she costs nothing until it does."
            )
    else:
        kind = gd.RETIRED
        terms = str(values.get("terms") or gd.PENSION)
        title = (
            "Retired on a pension" if terms == gd.PENSION else "Retired, paying rent"
        )
        lines = [
            "He still counts as one of the covenant for its finances.",
            "His Wages are halved: his pension."
            if terms == gd.PENSION
            else "He draws no Wages, and pays rent for his lodging; he is fed free.",
        ]
    character.discipline.append(
        Discipline(saga.current_year, saga.current_season, kind, None, note=terms)
    )
    details = "\n".join(lines + ([note] if note else []))
    character.diary.append(
        DiaryEntry(saga.current_year, saga.current_season, title, details)
    )
    _covenant_entry(saga, covenant, f"{character.name}: {title}", details, None)
    return notes(f"{character.name}: {title}.", *lines)


def pension_form(saga: Saga, character: Character | None) -> Command:
    """More's Pension on a grog: he retires, or, dead, his widow gets his
    pension."""
    refused = _refusal(saga, character, PENSION_TITLE)
    if refused is not None or character is None:
        return refused or Refuse(PENSION_TITLE, "Choose a grog first.")
    if character.wounds.dead and gd.widow_pensioned(character):
        return Refuse(PENSION_TITLE, "His widow already has his pension.")
    if not character.wounds.dead and gd.retirement(character) is not None:
        return Refuse(PENSION_TITLE, f"{escape(character.name)} has already retired.")
    grog = character
    title = "Widow's Pension" if grog.wounds.dead else "Retire"
    return Form(
        f"{title}: {escape(grog.name)}",
        lambda: pension_fields(saga, grog),
        lambda values: apply_pension(saga, grog, values),
        save_label="Retire" if not grog.wounds.dead else "Grant",
        help_id=PENSION_HELP,
    )
