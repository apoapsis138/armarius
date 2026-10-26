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
from .models import Character, DiaryEntry, Disease, Saga, character_age
from .rules import chirurgy, disease, harm, living, recovery
from .seasons.character_effects import age_character

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
    academe = disease.on(saga)
    injury, poison = _kind_is(harm.INJURY, harm.BRUISE), _kind_is(harm.POISON)
    sickness = _kind_is() if academe else _kind_is(harm.DISEASE)
    agents = _kind_is(harm.POISON) if academe else _kind_is(harm.POISON, harm.DISEASE)
    heat = [(f"{name} (+{bonus})", name) for name, bonus in harm.HEAT]
    impact = [(f"{name} (+{bonus})", name) for name, bonus in harm.IMPACT]
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
            "harm_from",
            "What it comes from",
            "select",
            None,
            options=[
                (f"{label} ({'/'.join(forms)})", key)
                for key, (label, forms) in harm.INJURY_SOURCES.items()
            ],
            allow_blank=True,
            placeholder="(the table's, or nothing a Form resists)",
            hint="A magus's Form Bonus for it (Form / 5, rounded up) adds to "
            "Soak (DE pp. 206-209).",
            show_if=injury,
        ),
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
        *([location_field()] if academe else []),
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
            "poison_kind",
            "Kind of poison",
            "select",
            None,
            options=[
                (f"{label} ({'/'.join(forms)})", key)
                for key, (label, forms) in harm.POISON_SOURCES.items()
            ],
            allow_blank=True,
            placeholder="(the table's, or another kind)",
            hint="A magus's Form Bonus for it adds to the Stamina check "
            "(DE pp. 208-209).",
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
            show_if=sickness,
        ),
        *(academe_fields() if academe else []),
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
            "drowning",
            "Drowning",
            "check",
            False,
            hint="Under water: Auram or Aquam's Form Bonus, the higher, adds "
            "to each check (DE pp. 208-209).",
            show_if=lambda values: (
                values.get("kind") == harm.DEPRIVATION
                and values.get("deprived") == "air"
            ),
        ),
        DialogField(
            "periods",
            "For how many of those periods",
            "int",
            1,
            show_if=_kind_is(harm.DEPRIVATION),
        ),
    ]


def location_field() -> DialogField:
    """Where an injury struck, with Art & Academe's medicine: an
    Incapacitating wound's lasting complication fits the place (A&A p. 43)."""
    return DialogField(
        "location",
        "Where it struck",
        "select",
        "torso",
        options=LOCATION_OPTIONS,
        hint="An Incapacitating wound calls for a Stamina roll against 6; "
        "failing leaves a Minor Flaw fitting the place (A&A p. 43).",
        show_if=_kind_is(harm.INJURY),
    )


def academe_fields() -> list[DialogField]:
    """Take Harm's disease, with Art & Academe's medicine: one of the
    book's, or one the troupe makes from its parts."""
    sick = _kind_is(harm.DISEASE)

    def typed(values: dict[str, Any]) -> bool:
        return sick(values) and not values.get("aa_disease")

    return [
        DialogField(
            "aa_disease",
            "Disease",
            "select",
            None,
            options=[
                (f"{d.name} ({d.level}, Severity {d.severity})", d.name)
                for d in disease.CATALOG
            ],
            allow_blank=True,
            placeholder="(make one below)",
            hint="Art & Academe pp. 47-51. The Disease Avoidance roll is made "
            "against its Stable Ease Factor.",
            show_if=sick,
        ),
        DialogField("name", "Its name", "text", "", show_if=typed),
        DialogField(
            "level",
            "Stage",
            "select",
            "Minor",
            options=pairs(disease.LEVELS),
            show_if=typed,
        ),
        DialogField(
            "interval",
            "Interval",
            "select",
            "week",
            options=pairs(disease.INTERVALS),
            show_if=typed,
        ),
        DialogField(
            "stable",
            "Stable Ease Factor",
            "select",
            "6",
            options=[(str(n), str(n)) for n in disease.STABLE_MOD],
            show_if=typed,
        ),
        DialogField(
            "improve",
            "Improvement Ease Factor",
            "select",
            "12",
            options=[(str(n), str(n)) for n in disease.IMPROVE_MOD],
            show_if=typed,
        ),
    ]


def _values(values: dict[str, Any]) -> dict[str, Any]:
    """The form's values as the rule takes them: a preset fills its own."""
    found = dict(values)
    kind = found.get("kind")
    preset = found.get("preset")
    if kind in (harm.INJURY, harm.BRUISE) and preset:
        found["bonus"] = dict(harm.HEAT + harm.IMPACT)[preset]
        found["harm_from"] = found.get("harm_from") or harm.PRESET_SOURCES.get(preset)
    for key, table in (("poison", harm.POISONS), ("disease", harm.DISEASES)):
        name = found.get(key)
        if kind == key and name:
            entry = next(e for e in table if e[0] == name)
            found["ease"], found["wound"] = entry[1], entry[2]
    if kind == harm.POISON and found.get("poison"):
        found["poison_kind"] = found.get("poison_kind") or harm.PRESET_SOURCES.get(
            found["poison"]
        )
    if kind == harm.DEPRIVATION:
        found["kind"] = found.get("deprived") or "food"
    for key in ("stable", "improve"):
        if isinstance(found.get(key), str) and found[key]:
            found[key] = int(found[key])
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


FIRST_AID = "first aid"
SURGERY = "surgery"
ROLLS = ("all", "worst")
LOCATION_OPTIONS = [
    ("The head", "head"),
    ("The torso", "torso"),
    ("A limb", "limbs"),
]


def _rolling(values: dict[str, Any]) -> bool:
    return (values.get("which") or "all") in ROLLS


def _needs_chirurgeon(values: dict[str, Any]) -> bool:
    return not _rolling(values) or bool(values.get("intervene"))


def recovery_fields(
    character: Character, saga: Saga | None = None
) -> list[DialogField]:
    """What Recovery Roll asks: which rolls, and with Art & Academe's
    medicine, first aid, surgery on a disease, or a chirurgeon standing by
    to intervene when a roll fails."""
    academe = saga is not None and chirurgy.on(saga)
    which = list(pairs(ROLLS))
    chirurgeons: list[Character] = []
    if academe and saga is not None:
        if any(s.source == recovery.INJURY for s in recovery.states(character.wounds)):
            which.append((FIRST_AID, FIRST_AID))
        if character.wounds.diseases:
            which.append((SURGERY, SURGERY))
        chirurgeons = chirurgy.chirurgeons(saga, character)
    fields = [
        DialogField(
            "which",
            "Roll for",
            "select",
            "all",
            options=which,
            hint="all: one roll for each wound now; worst: the roll for doing "
            "more than the wounds allow (it can only hold or worsen)."
            + (
                " first aid: within a day of the wounds (A&A p. 61); surgery: "
                "on a disease (A&A p. 61)."
                if len(which) > len(ROLLS)
                else ""
            ),
        ),
    ]
    if academe:
        fields += [
            DialogField(
                "intervene",
                "Surgical intervention when a roll fails",
                "check",
                False,
                hint="Surgery against 9: it holds the wound, but leaves a lasting "
                "consequence (A&A p. 62).",
                show_if=_rolling,
            ),
            DialogField(
                "location",
                "Where the wounds are",
                "select",
                "torso",
                options=LOCATION_OPTIONS,
                show_if=lambda values: (
                    _rolling(values) and bool(values.get("intervene"))
                ),
            ),
            DialogField(
                "chirurgeon",
                "Chirurgeon",
                "select",
                next(
                    (c.id for c in chirurgeons if c.id != character.id),
                    chirurgeons[0].id if chirurgeons else None,
                ),
                options=[
                    (f"{escape(c.name)} (Chirurgy {chirurgy.chirurgy(c)})", c.id)
                    for c in chirurgeons
                ],
                allow_blank=True,
                placeholder="(no one with Chirurgy)",
                show_if=_needs_chirurgeon,
            ),
            DialogField(
                "disease",
                "Disease",
                "select",
                character.wounds.diseases[0].name
                if character.wounds.diseases
                else None,
                options=pairs(d.name for d in character.wounds.diseases),
                show_if=lambda values: values.get("which") == SURGERY,
            ),
            DialogField(
                "procedure",
                "Procedure",
                "select",
                chirurgy.PROCEDURES[0][0],
                options=[
                    (f"{name} (Ease Factor {ease}, {_wound_label(wound)})", name)
                    for name, ease, wound in chirurgy.PROCEDURES
                ],
                hint="Phlebotomy, cautery and cupping help only a disease of "
                "Severity 5 or less (A&A p. 61).",
                show_if=lambda values: values.get("which") == SURGERY,
            ),
        ]
    fields.append(
        DialogField(
            "aid",
            "Magical aid to every Recovery roll",
            "int",
            character.wounds.aid,
            hint="A Zenodochium's +9, Purification of the Festering Wound; kept "
            "until changed.",
        )
    )
    return fields


def _wound_label(wound: str) -> str:
    return "a Fatigue level" if wound == "fatigue" else f"a {wound.title()} Wound"


def _record(character: Character, name: str) -> Disease | None:
    return next((d for d in character.wounds.diseases if d.name == name), None)


def recovery_problem(
    saga: Saga, character: Character, values: dict[str, Any]
) -> str | None:
    """Why the Recovery Roll can't go ahead as chosen, or None."""
    if not chirurgy.on(saga) or not _needs_chirurgeon(values):
        return None
    if saga.character(values.get("chirurgeon")) is None:
        return "Choose a chirurgeon."
    if values.get("which") == SURGERY:
        record = _record(character, str(values.get("disease") or ""))
        if record is None:
            return "Choose the disease."
        return chirurgy.surgery_problem(record, str(values.get("procedure") or ""))
    return None


def _first_aid(
    saga: Saga, character: Character, chirurgeon: Character, dice: random.Random
) -> list[str]:
    found = recovery.states(character.wounds)
    worst = found[-1].severity if found else ""
    ease = recovery.TABLE[worst][2] if worst in recovery.TABLE else None
    rolled, lines = chirurgy.first_aid(saga, character, chirurgeon, ease, found, dice)
    recovery.set_states(character.wounds, found)
    if rolled is not None and rolled.botched:
        lines += recovery.roll_now(saga, character, dice, worst_only=True)
    return lines


def _surgery(
    saga: Saga,
    character: Character,
    chirurgeon: Character,
    values: dict[str, Any],
    dice: random.Random,
) -> list[str]:
    record = _record(character, str(values.get("disease") or ""))
    if record is None:
        return []
    done = chirurgy.surgery(
        saga, character, chirurgeon, record, str(values.get("procedure")), dice
    )
    if done.wound == "fatigue":
        harm.lose_fatigue(character, long_term=False)
    else:
        recovery.add_wound(character.wounds, done.wound)
    return done.lines


def recovery_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Recovery Roll: a roll for each wound now, or for the worst one
    when the character does more than the wounds allow; with Art & Academe's
    medicine, first aid or surgery instead, or a surgical intervention on
    each roll that fails."""
    if character is None:
        return Refuse(RECOVERY_TITLE, "Choose a character first.")
    if not recovery.states(character.wounds) and not character.wounds.diseases:
        return Refuse(RECOVERY_TITLE, f"{character.name} has no wounds.")
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> Command:
        before = (
            copy.deepcopy(character.wounds),
            character.fatigue_level,
            character.long_term_fatigue,
        )
        character.wounds.aid = int(values.get("aid") or 0)
        which = values.get("which") or "all"
        chirurgeon = saga.character(values.get("chirurgeon"))
        surgeon = None
        if which == FIRST_AID and chirurgeon is not None:
            title = "First aid"
            lines = _first_aid(saga, character, chirurgeon, dice)
        elif which == SURGERY and chirurgeon is not None:
            title = "Surgery"
            lines = _surgery(saga, character, chirurgeon, values, dice)
        else:
            title = "Recovery rolls"
            if values.get("intervene") and chirurgeon is not None:
                surgeon = chirurgy.Surgeon(
                    chirurgeon, str(values.get("location") or "torso")
                )
            lines = recovery.roll_now(
                saga, character, dice, worst_only=which == "worst", surgeon=surgeon
            ) + disease.roll_now(
                saga, character, living.living_conditions(saga, character), dice
            )
        after = (character.wounds, character.fatigue_level, character.long_term_fatigue)
        character.wounds, character.fatigue_level, character.long_term_fatigue = before

        def keep() -> None:
            character.wounds, character.fatigue_level, character.long_term_fatigue = (
                after
            )
            kept = list(lines)
            if surgeon is not None:
                kept += _consequences(saga, character, surgeon, dice)
            character.diary.append(
                DiaryEntry(
                    saga.current_year, saga.current_season, title, "\n".join(kept)
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
        lambda: recovery_fields(character, saga),
        apply,
        validate=lambda values: recovery_problem(saga, character, values),
        save_label="Roll",
        help_id="recovery-roll",
    )


def _consequences(
    saga: Saga, character: Character, surgeon: chirurgy.Surgeon, dice: random.Random
) -> list[str]:
    """What the surgical interventions leave, once kept: the Aging Points
    due and the immediate Aging rolls (each written in the Diary)."""
    lines = chirurgy.aging_due_lines(
        character,
        surgeon.consequences,
        f"{saga.current_season} {saga.current_year}",
    )
    rolls = chirurgy.aging_rolls(surgeon.consequences)
    age = character_age(character.background.year_born, saga.current_year)
    for _ in range(rolls):
        if character.wounds.dead:
            break
        if age is None:
            lines.append("An Aging roll is due: the character has no birth year.")
            continue
        age_character(saga, character, age, dice, label="Aging (surgery)")
        lines.append("An Aging roll for the surgery, in the Diary.")
    return lines
