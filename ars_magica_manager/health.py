"""More's Take Harm and Recovery Roll on a character's Health: the forms,
their rolls and the Diary entries -- no UI in here. The rules are
rules.harm's and rules.recovery's."""

from __future__ import annotations

import copy
import random
from typing import Any

from .commands import Command, Confirm, Form, Refuse
from .form_spec import DialogField, pairs
from .markup import escape
from .models import Character, DiaryEntry, Saga
from .rules import harm, recovery

HARM_TITLE = "Take Harm"
RECOVERY_TITLE = "Recovery Roll"

KIND_LABELS = {
    harm.INJURY: "An injury: fire, a fall, a blow",
    harm.POISON: "A poison",
    harm.DISEASE: "A disease",
    harm.DEPRIVATION: "Deprivation of air, water or food",
    harm.BRUISE: "A bruise (a non-lethal blow)",
}
SEVERITY_OPTIONS = [
    ("Light", "light"),
    ("Medium", "medium"),
    ("Heavy", "heavy"),
    ("Incapacitating", "incapacitating"),
    ("Fatal", "dead"),
]


def _kind_is(*kinds: str):
    return lambda values: values.get("kind") in kinds


def harm_fields(saga: Saga) -> list[DialogField]:
    """What Take Harm asks: the kind, then that kind's own fields."""
    kinds = harm.kinds(saga)
    injury, poison, disease = (
        _kind_is(harm.INJURY, harm.BRUISE),
        _kind_is(harm.POISON),
        _kind_is(harm.DISEASE),
    )
    agents = _kind_is(harm.POISON, harm.DISEASE)
    heat = [(f"{name} (+{bonus})", str(bonus)) for name, bonus in harm.HEAT]
    impact = [(f"{name} (+{bonus})", str(bonus)) for name, bonus in harm.IMPACT]
    return [
        DialogField(
            "kind",
            "Kind",
            "select",
            harm.INJURY,
            options=[(KIND_LABELS[k], k) for k in kinds],
        ),
        DialogField(
            "preset",
            "From the tables",
            "select",
            None,
            options=heat + impact,
            allow_blank=True,
            placeholder="(type the damage bonus)",
            hint="The Heat and Corrosion and Impact tables (DE p. 407); falling "
            "is +1 per two feet, doubled on a hard surface, halved on a soft one.",
            show_if=injury,
        ),
        DialogField("bonus", "Damage bonus", "int", 0, show_if=injury),
        DialogField(
            "coverage",
            "How much it covers (heat and corrosion)",
            "select",
            "1",
            options=[(name, str(n)) for name, n in harm.COVERAGE],
            show_if=_kind_is(harm.INJURY),
        ),
        DialogField(
            "armour",
            "Armour protects",
            "check",
            True,
            hint="Untick for boiling water and the like.",
            show_if=_kind_is(harm.INJURY),
        ),
        DialogField(
            "poison",
            "Poison",
            "select",
            None,
            options=[(f"{n} (Ease Factor {e}, {w})", n) for n, e, w in harm.POISONS],
            allow_blank=True,
            placeholder="(type it below)",
            show_if=poison,
        ),
        DialogField(
            "disease",
            "Disease",
            "select",
            None,
            options=[(f"{n} (Ease Factor {e}, {w})", n) for n, e, w in harm.DISEASES],
            allow_blank=True,
            placeholder="(type it below)",
            show_if=disease,
        ),
        DialogField(
            "ease",
            "Ease Factor of the Stamina check",
            "int",
            6,
            show_if=agents,
        ),
        DialogField(
            "wound",
            "Wound on a failure",
            "select",
            "light",
            options=SEVERITY_OPTIONS,
            show_if=agents,
        ),
        DialogField(
            "deprived",
            "Deprived of",
            "select",
            "food",
            options=[
                (f"{k.title()} (a check every {p})", k) for k, p in harm.DEPRIVATIONS
            ],
            show_if=_kind_is(harm.DEPRIVATION),
        ),
        DialogField(
            "periods",
            "For how many of those periods",
            "int",
            1,
            show_if=_kind_is(harm.DEPRIVATION),
        ),
    ]


def _values(values: dict[str, Any]) -> dict[str, Any]:
    """The form's values as the rule takes them: a preset fills its own."""
    found = dict(values)
    kind = found.get("kind")
    if kind in (harm.INJURY, harm.BRUISE) and found.get("preset"):
        found["bonus"] = int(found["preset"])
    for key, table in (("poison", harm.POISONS), ("disease", harm.DISEASES)):
        name = found.get(key)
        if kind == key and name:
            entry = next(e for e in table if e[0] == name)
            found["ease"], found["wound"] = entry[1], entry[2]
    if kind == harm.DEPRIVATION:
        found["kind"] = found.get("deprived") or "food"
    return found


def take_harm_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Take Harm: the harm's kind and what it is; rolled at once,
    and kept (with a Diary entry) when confirmed."""
    if character is None:
        return Refuse(HARM_TITLE, "Choose a character first.")
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> Command:
        kind = values["kind"]
        before = (
            copy.deepcopy(character.wounds),
            character.fatigue_level,
            character.long_term_fatigue,
        )
        done = harm.apply(saga, character, kind, _values(values), dice)
        after = (character.wounds, character.fatigue_level, character.long_term_fatigue)
        character.wounds, character.fatigue_level, character.long_term_fatigue = before

        def keep() -> None:
            character.wounds, character.fatigue_level, character.long_term_fatigue = (
                after
            )
            character.diary.append(
                DiaryEntry(
                    saga.current_year,
                    saga.current_season,
                    f"{KIND_LABELS[kind].split(':')[0]}: "
                    + (", ".join(w.title() for w in done.wounds) or "no wound"),
                    "\n".join(done.lines),
                )
            )

        return Confirm(
            "\n".join(escape(line) for line in done.lines),
            keep,
            yes_label="Keep",
            title=HARM_TITLE,
        )

    return Form(
        f"{HARM_TITLE}: {escape(character.name)}",
        lambda: harm_fields(saga),
        apply,
        save_label="Roll",
        help_id="take-harm",
    )


def recovery_fields(character: Character) -> list[DialogField]:
    return [
        DialogField(
            "which",
            "Roll for",
            "select",
            "all",
            options=pairs(("all", "worst")),
            hint="all: one roll for each wound now; worst: the roll for doing "
            "more than the wounds allow (it can only hold or worsen).",
        ),
        DialogField(
            "aid",
            "Magical aid to every Recovery roll",
            "int",
            character.wounds.aid,
            hint="A Zenodochium's +9, Purification of the Festering Wound; kept "
            "until changed.",
        ),
    ]


def recovery_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Recovery Roll: a roll for each wound now, or for the worst one
    when the character does more than the wounds allow."""
    if character is None:
        return Refuse(RECOVERY_TITLE, "Choose a character first.")
    if not recovery.states(character.wounds):
        return Refuse(RECOVERY_TITLE, f"{character.name} has no wounds.")
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> Command:
        before = copy.deepcopy(character.wounds)
        character.wounds.aid = int(values.get("aid") or 0)
        lines = recovery.roll_now(
            saga, character, dice, worst_only=values.get("which") == "worst"
        )
        after, character.wounds = character.wounds, before

        def keep() -> None:
            character.wounds = after
            character.diary.append(
                DiaryEntry(
                    saga.current_year,
                    saga.current_season,
                    "Recovery rolls",
                    "\n".join(lines),
                )
            )

        return Confirm(
            "\n".join(escape(line) for line in lines),
            keep,
            yes_label="Keep",
            title=RECOVERY_TITLE,
        )

    return Form(
        f"{RECOVERY_TITLE}: {escape(character.name)}",
        lambda: recovery_fields(character),
        apply,
        save_label="Roll",
        help_id="recovery-roll",
    )


def season_text(character: Character, played: recovery.Season) -> str:
    """A season's recovery for the Diary."""
    if played.died:
        return f"{character.name} died of their wounds.\n" + "\n".join(played.rolls)
    return "\n".join(played.rolls)
