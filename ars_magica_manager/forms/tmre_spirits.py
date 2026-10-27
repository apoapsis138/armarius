"""More's Spirits and Names on a magus with a Mystery of spirit magic or
theurgy: the totals of a working with spirits, and a roll where the book
asks for one -- no UI in here, and nothing kept. The rules and their pages
are rules.tmre_spirits' (The Mysteries Revised Edition pp. 64-88)."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from ..arts import FORMS, TECHNIQUES
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import Character, Saga
from ..rules import dice, penetration, realms
from ..rules import hybrid_magic as hybrid
from ..rules import tmre_spirits as ts
from ..rules.creation_virtues import tally
from ..rules.realms import present_aura
from ..rules.rounding import round_up

TITLE = "Spirits and Names"
HELP_ID = "spirits-and-names"
NONE = "none"

SPELL_SPIRIT = "spell_spirit"
FORM_SPIRIT = "form_spirit"
DAIMON_PACT = "daimon_pact"
THEURGIC_LAB = "theurgic_lab"
NAMES = "names"
SYNTHEMATA = "synthemata"
INTUIT = "intuit"
FASTING = "fasting"
EMPOWERMENT = "empowerment"
FAMILIAR = "spirit_familiar"
BLENDING = "blending"
GHOST = "living_ghost"
ASCENSION = "ascension"

#: Each working, its label, and the Virtues that offer it (none: any of
#: them, as a pact may be cast from a Lab Text without Hermetic Theurgy).
WORKINGS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (SPELL_SPIRIT, "Invoke the Spirit of (spell)", (ts.HERMETIC_THEURGY,)),
    (FORM_SPIRIT, "Invoke the Spirit of (Form)", (ts.HERMETIC_THEURGY,)),
    (DAIMON_PACT, "Invoke the Pact of (Daimon)", ()),
    (THEURGIC_LAB, "Invent a theurgic spell", (ts.HERMETIC_THEURGY,)),
    (NAMES, "Names of Power", (ts.NAMES_OF_POWER, ts.INVOCATION_MAGIC)),
    (SYNTHEMATA, "Research Hermetic Synthemata", (ts.HERMETIC_SYNTHEMATA,)),
    (INTUIT, "Intuit Synthemata", (ts.SYNTHEMATA_MAGIA,)),
    (FASTING, "Research Synthemata by fasting", (ts.SYNTHEMATA_MAGIA,)),
    (EMPOWERMENT, "Power Ritual effects", (ts.HERMETIC_EMPOWERMENT,)),
    (
        FAMILIAR,
        "Bond a spirit familiar",
        (ts.SPIRIT_FAMILIAR, ts.THEURGIC_SPIRIT_FAMILIAR),
    ),
    (BLENDING, "Blending with Substance", (ts.INSCRIPTION_ON_THE_SOUL,)),
    (GHOST, "The Living Ghost", (ts.LIVING_GHOST,)),
    (ASCENSION, "Ascendancy to the Hall of Heroes", (ts.ASCENDANCY,)),
)
#: The workings that roll a die.
ROLLED = (INTUIT, FASTING, ASCENSION)
STEPS = (("As learned", "0"), ("A magnitude higher", "1"), ("A magnitude lower", "-1"))
SPIRIT_REALMS = (realms.HERMETIC, "Faerie", "Infernal", "Divine")


def offers(character: Character) -> bool:
    """Whether More offers Spirits and Names: one of the Mysteries held."""
    return bool(ts.held_virtues(character))


def workings(character: Character) -> list[tuple[str, str]]:
    held = set(ts.held_virtues(character))
    return [
        (label, key)
        for key, label, needs in WORKINGS
        if not needs or held.intersection(needs)
    ]


def _working(values: dict[str, Any], character: Character) -> str:
    return str(values.get("working") or workings(character)[0][1])


def _on(character: Character, *keys: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: _working(values, character) in keys


SPIRITED = (
    SPELL_SPIRIT,
    FORM_SPIRIT,
    DAIMON_PACT,
    SYNTHEMATA,
    INTUIT,
    FASTING,
    EMPOWERMENT,
    FAMILIAR,
)


#: The workings an aura changes.
AURAL = (SPELL_SPIRIT, FORM_SPIRIT, THEURGIC_LAB, SYNTHEMATA, INTUIT, FASTING, FAMILIAR)


def spirits_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What Spirits and Names asks."""
    aura, aura_realm = present_aura(saga, character)

    def on(*keys: str) -> Callable[[dict[str, Any]], bool]:
        return _on(character, *keys)

    offered = workings(character)
    return [
        DialogField("working", "Working", "select", offered[0][1], options=offered),
        DialogField(
            "might",
            "The spirit's Might",
            "int",
            10,
            hint="The storyguide's figure; the sheet never knows it.",
            show_if=on(*SPIRITED),
        ),
        DialogField(
            "spirit_realm",
            "The spirit's realm",
            "select",
            realms.HERMETIC,
            options=pairs(SPIRIT_REALMS),
            show_if=on(SPELL_SPIRIT, FORM_SPIRIT, INTUIT, FAMILIAR),
        ),
        DialogField(
            "power_level",
            "The spell-like power's level",
            "int",
            10,
            show_if=on(SPELL_SPIRIT),
        ),
        DialogField(
            "step",
            "He varies it",
            "select",
            "0",
            options=list(STEPS),
            hint="One of Range, Duration or Target by a step.",
            show_if=on(SPELL_SPIRIT),
        ),
        DialogField(
            "duration_levels",
            "Levels added for Duration",
            "int",
            0,
            hint="How long the spirit waits to be instructed.",
            show_if=on(SPELL_SPIRIT, FORM_SPIRIT),
        ),
        DialogField(
            "penetration_levels",
            "Levels added for Penetration",
            "int",
            0,
            hint="+2 Penetration a level.",
            show_if=on(SPELL_SPIRIT),
        ),
        DialogField(
            "effect_level",
            "The effect's level",
            "int",
            10,
            show_if=on(FORM_SPIRIT),
        ),
        DialogField(
            "pact_level",
            "The pact's level",
            "int",
            20,
            show_if=on(DAIMON_PACT),
        ),
        DialogField(
            "gathered",
            "Points gathered so far",
            "int",
            0,
            show_if=on(DAIMON_PACT, ASCENSION),
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            TECHNIQUES[0],
            options=pairs(TECHNIQUES),
            show_if=on(THEURGIC_LAB, FAMILIAR),
        ),
        DialogField(
            "form",
            "Form",
            "select",
            "Vim",
            options=pairs(FORMS),
            show_if=on(THEURGIC_LAB, FAMILIAR),
        ),
        DialogField(
            "spell_level",
            "The spell's level",
            "int",
            10,
            hint="For synthemata, at least the being's Might.",
            show_if=on(THEURGIC_LAB, SYNTHEMATA),
        ),
        DialogField(
            "lasting",
            "The Lasting Synthemata (Diameter)",
            "check",
            False,
            show_if=on(SYNTHEMATA),
        ),
        DialogField(
            "lore",
            "Realm Lore",
            "select",
            "Magic Lore",
            options=pairs(hybrid.REALM_LORES),
            show_if=on(THEURGIC_LAB, SYNTHEMATA, INTUIT, FASTING),
        ),
        DialogField(
            "bonuses",
            "Bonuses, comma-separated",
            "text",
            "",
            hint="Names of Power's bonuses; or the item's Shape and Material "
            "bonuses for Blending.",
            show_if=on(THEURGIC_LAB, NAMES, BLENDING),
        ),
        DialogField(
            "name_hiding",
            "Name hiding",
            "int",
            0,
            hint="A spirit that hides its name: about Might / 2.",
            show_if=on(SYNTHEMATA, INTUIT, FASTING),
        ),
        DialogField(
            "connection",
            "Arcane Connection",
            "select",
            NONE,
            options=[("None", NONE), *pairs(penetration.ARCANE_CONNECTIONS)],
            hint="Its multiplier is a bonus to the research.",
            show_if=on(SYNTHEMATA, FASTING),
        ),
        DialogField(
            "rituals",
            "Ritual effects' levels, in order of use",
            "text",
            "25",
            show_if=on(EMPOWERMENT),
        ),
        DialogField(
            "daimon",
            "The spirit is a Daimon",
            "check",
            False,
            show_if=lambda v: (
                _working(v, character) == FAMILIAR
                and ts.THEURGIC_SPIRIT_FAMILIAR in ts.held_virtues(character)
            ),
        ),
        DialogField(
            "focus",
            "A Magical Focus applies",
            "check",
            False,
            hint="It doubles the lower of his best Arts.",
            show_if=on(GHOST, ASCENSION),
        ),
        DialogField(
            "size_levels",
            "Levels added for the Haunt's Size",
            "int",
            0,
            show_if=on(GHOST),
        ),
        DialogField(
            "ritual_level",
            "The Transformation's level",
            "int",
            0,
            hint="0: his transformation limit.",
            show_if=on(GHOST, ASCENSION),
        ),
        DialogField(
            "ascendant_level",
            "The Ascendant Form's level",
            "int",
            0,
            hint="0: the least it may be.",
            show_if=on(ASCENSION),
        ),
        DialogField(
            "aura",
            "Aura",
            "int",
            aura,
            show_if=on(*AURAL),
        ),
        DialogField(
            "aura_realm",
            "Aura's realm",
            "select",
            aura_realm,
            options=pairs(realms.REALMS),
            show_if=on(*AURAL),
        ),
    ]


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    value = values.get(key)
    return value if isinstance(value, int) else default


def numbers(text: str) -> list[int]:
    """Whole numbers from a comma-separated list; ValueError otherwise."""
    return [int(part) for part in text.replace(";", ",").split(",") if part.strip()]


def problem(values: dict[str, Any]) -> str | None:
    for key in ("bonuses", "rituals"):
        try:
            numbers(str(values.get(key) or ""))
        except ValueError:
            return "List whole numbers, separated by commas."
    return None


def _list(values: dict[str, Any], key: str) -> list[int]:
    try:
        return numbers(str(values.get(key) or ""))
    except ValueError:
        return []


def _magus_aura(values: dict[str, Any]) -> int:
    return realms.aura_modifier(
        realms.HERMETIC,
        str(values.get("aura_realm") or realms.HERMETIC),
        _int(values, "aura"),
    )


def _spirit_aura(values: dict[str, Any]) -> int:
    realm = str(values.get("spirit_realm") or realms.HERMETIC)
    return realms.aura_modifier(
        realm, str(values.get("aura_realm") or realms.HERMETIC), _int(values, "aura")
    )


def _multiplier(values: dict[str, Any]) -> int:
    connection = str(values.get("connection") or NONE)
    return 0 if connection == NONE else 1 + penetration.ARCANE_CONNECTIONS[connection]


def _seasons(points: int, level: int) -> str:
    if points <= 0:
        return "no points a season: it can't be invented."
    seasons = round_up(level / points)
    return f"{points} point(s) a season, {seasons} season(s) for level {level}."


def lines(character: Character, values: dict[str, Any]) -> list[str]:
    """What the working comes to, plain."""
    working = _working(values, character)
    might = max(0, _int(values, "might", 10))
    if working == SPELL_SPIRIT:
        return _spell_spirit(values, might)
    if working == FORM_SPIRIT:
        return _form_spirit(values, might)
    if working == DAIMON_PACT:
        return _daimon_pact(character, values, might)
    if working == THEURGIC_LAB:
        return _theurgic_lab(character, values)
    if working == NAMES:
        return _names(character, values)
    if working == SYNTHEMATA:
        return _synthemata(character, values, might)
    if working in (INTUIT, FASTING):
        total, ease = _intuit_roll(character, values, might)
        what = "Intuit" if working == INTUIT else "A season's fasting and invocation"
        after = (
            "Failing, he can't try again until Per + Lore rises; a botch warns "
            "the spirit."
            if working == INTUIT
            else "Failing, he may try another season."
        )
        return [
            f"{what}: stress die {total:+d} against {ease}: a die of "
            f"{max(ease - total, 0)}.",
            after,
            "Known, his own synthemata give a Muto Vim spell adding its level "
            "to his Casting Score against the being (the Hedge Lord's "
            "Synthemata, Diameter: level - 5).",
        ]
    if working == EMPOWERMENT:
        return _empowerment(values, might)
    if working == FAMILIAR:
        return _familiar(character, values, might)
    if working == BLENDING:
        return _blending(values)
    if working == GHOST:
        return _ghost(character, values)
    return _ascension(character, values)


def _spell_spirit(values: dict[str, Any], might: int) -> list[str]:
    power = max(0, _int(values, "power_level", 10))
    added = max(0, _int(values, "penetration_levels"))
    level = ts.invoke_level(might, _int(values, "duration_levels"), added)
    cast = ts.spell_spirit(
        might,
        power,
        _spirit_aura(values),
        step=int(str(values.get("step") or "0")),
        penetration_levels=added,
    )
    said = [ts.spell_spirit_problem(might, power)] if might < power else []
    said += [
        f"His Invoke spell: level {level} (Might {might} + Duration + "
        f"Penetration), with the power's Arts; +{ts.invoke_penetration_bonus(added)} "
        "to the spirit's Penetration.",
        f"The spirit casts at {cast.casting_total} (Might + aura, no die) "
        f"against level {cast.level}: "
        + ("it works" if cast.succeeds else f"short of {cast.level - 10}")
        + f"; Penetration {cast.penetration:+d}.",
        "The first summons must overcome its Might as Magic Resistance; after "
        "that the pact holds. Instructing it takes a round.",
    ]
    return said


def _form_spirit(values: dict[str, Any], might: int) -> list[str]:
    effect = max(0, _int(values, "effect_level", 10))
    cast = ts.form_spirit(might, _spirit_aura(values), effect)
    level = ts.invoke_level(might, _int(values, "duration_levels"))
    return [
        f"His Invoke spell: level {level} (Might {might} + Duration).",
        f"The spirit's Casting Total {cast.casting_total} ((Might + aura) / 2, "
        f"no die): level {effect} "
        + ("works" if cast.succeeds else "is beyond it")
        + f"; Penetration {cast.penetration:+d}.",
        "Its effects are only of the Invoke spell's own Technique and Form.",
    ]


def _daimon_pact(character: Character, values: dict[str, Any], might: int) -> list[str]:
    level = max(0, _int(values, "pact_level", 20))
    gathered = max(0, _int(values, "gathered"))
    pact = ts.daimon_pact(level, might, gathered)
    theurgist = ts.HERMETIC_THEURGY in ts.held_virtues(character)
    said = [
        f"Each casting that penetrates the Daimon's Might gathers {pact.points} "
        f"point(s) (level {level} - Might {might}); the Aspect comes at {might}."
    ]
    if pact.at_once:
        said.append("Twice its Might: one penetrating casting calls it.")
    elif not theurgist:
        said.append(
            f"Without Hermetic Theurgy points aren't kept: only level "
            f"{2 * might} calls it, in one casting."
        )
    elif pact.castings is None:
        said.append("It must be above the Daimon's Might to gather anything.")
    else:
        said.append(f"{pact.castings} more casting(s) call it.")
    said.append(
        f"A Ritual: {ts.daimon_points(level)} pawn(s) of vis, and as many Daimon "
        "Points to the Daimon."
    )
    return said


def _theurgic_lab(character: Character, values: dict[str, Any]) -> list[str]:
    technique = str(values.get("technique") or TECHNIQUES[0])
    form = str(values.get("form") or "Vim")
    theory = ts.magic_theory(character)
    names = ts.names_bonus(_list(values, "bonuses"), theory)
    total = ts.theurgic_lab_total(
        character,
        technique,
        form,
        lore=str(values.get("lore") or "Magic Lore"),
        aura_modifier=_magus_aura(values),
        names=names,
    )
    level = max(1, _int(values, "spell_level", 10))
    return [
        f"Theurgic Lab Total {total} ({technique} + {form} + Int + Magic "
        f"Theory + aura + Realm Lore + Names {names}).",
        "Inventing: " + _seasons(total - level, level),
        f"Names of Power worked in add {names} to its Casting Score too, and "
        "must be spoken firmly aloud.",
    ]


def _names(character: Character, values: dict[str, Any]) -> list[str]:
    bonuses = _list(values, "bonuses")
    theory = ts.magic_theory(character)
    total = ts.names_bonus(bonuses, theory)
    levels = ", ".join(str(ts.name_level(b)) for b in bonuses) or "none listed"
    return [
        f"Their bonus together: {total} (no more than Magic Theory {theory}).",
        f"Each Name is a Muto Vim spell of level 5 x its bonus: {levels}.",
        "Invocation Magic casts each Name before the spell, a round apiece, "
        "firmly aloud; Loud Voice or Exaggerated Gestures add +2 to the Name's "
        "own casting. A botch strikes his magic.",
    ]


def _synthemata(character: Character, values: dict[str, Any], might: int) -> list[str]:
    lasting = bool(values.get("lasting"))
    level = max(0, _int(values, "spell_level", 10))
    least = ts.synthemata_least_level(might, lasting=lasting)
    hiding = max(0, _int(values, "name_hiding"))
    multiplier = _multiplier(values)
    total = ts.synthemata_lab_total(
        character,
        lore=str(values.get("lore") or "Magic Lore"),
        aura_modifier=_magus_aura(values),
        bonuses=multiplier,
    )
    points = ts.synthemata_points(total, level, hiding)
    said = [] if level >= least else [f"The spell must be at least level {least}."]
    return said + [
        f"Lab Total {total} (Muto + Vim + Int + Realm Lore + aura"
        + (f" + Arcane Connection x{multiplier}" if multiplier else "")
        + ").",
        f"Less level {level} and name hiding {hiding}: " + _seasons(points, level),
        f"Done, it adds +{ts.synthemata_penetration(level, lasting=lasting)} "
        "Penetration against the being"
        + (", until the Diameter ends." if lasting else ", for the next spell."),
    ]


def _intuit_roll(
    character: Character, values: dict[str, Any], might: int
) -> tuple[int, int]:
    lore = str(values.get("lore") or "Magic Lore")
    hiding = max(0, _int(values, "name_hiding"))
    if _working(values, character) == INTUIT:
        total = ts.intuit_total(character, lore, _magus_aura(values))
        return total, ts.intuit_ease(might, _spirit_aura(values), hiding)
    total = ts.intuit_total(character, lore, _magus_aura(values)) + _multiplier(values)
    return total, ts.intuit_ease(might, 0, hiding)


def _empowerment(values: dict[str, Any], might: int) -> list[str]:
    said = [
        f"Its Empowering Prison: base level at least {ts.prison_level(might)}, "
        "with the Ritual effects' Forms as requisites."
    ]
    for use in ts.drain_uses(might, _list(values, "rituals")):
        if use.powered:
            said.append(
                f"Level {use.level}: -{ts.might_drained(use.level)} Might Score, "
                f"{use.might_left} left."
            )
        else:
            said.append(
                f"Level {use.level}: Might {use.might_left} is too little "
                "(x 2 must reach the level); nothing drained."
            )
    return said


def _familiar(character: Character, values: dict[str, Any], might: int) -> list[str]:
    technique = str(values.get("technique") or TECHNIQUES[0])
    form = str(values.get("form") or "Vim")
    aura = ts.bonding_aura(_magus_aura(values), _spirit_aura(values))
    total = ts.spirit_familiar_total(character, technique, form, aura)
    level = ts.spirit_familiar_level(might)
    said = [
        f"Lab Total {total} ({technique} + {form} + Int + Magic Theory + the "
        f"worse aura {aura:+d}) against {level} (Might + 25): "
        + ("enough" if total >= level else "short")
        + f"; {ts.bonding_vis(total)} pawn(s) of {technique} or {form} vis.",
        f"{ts.familiar_pyramid_points(might)} point(s) buy its Intelligence, "
        "Perception and Communication.",
        "The Hekate Cord adds its score to a Stamina roll for each Might point "
        "the familiar spends (up to 5).",
    ]
    if values.get("daimon"):
        te_fo = ts.art_total(character, technique) + ts.art_total(character, form)
        said.append(
            f"A Daimon: {ts.daimon_familiar_vis(might)} pawn(s) sacrificed first"
            + (
                f"; Technique + Form {te_fo} is under twice its Might, and it may "
                "think him unworthy."
                if ts.daimon_rejects(te_fo, might)
                else "."
            )
        )
    return said


def _blending(values: dict[str, Any]) -> list[str]:
    bonuses = _list(values, "bonuses")
    if not bonuses:
        return ["List the item's Shape and Material bonuses."]
    level = ts.blending_level(bonuses)
    return [
        f"A Rego Vim effect (Muto, Corpus and the item's Form requisites) of "
        f"level {level}; {ts.blending_warping(level)} Warping Point(s).",
        "He may attune one of its bonuses in the first season.",
    ]


def _ghost(character: Character, values: dict[str, Any]) -> list[str]:
    limit, arts = ts.best_combination(character, focus=bool(values.get("focus")))
    size = max(0, _int(values, "size_levels"))
    ritual = _int(values, "ritual_level") or limit
    might = ts.ghost_might(ritual, size, limit)
    return ts.ghost_problems(ritual, size, limit) + [
        f"Transformation limit {limit} ({arts or 'no Arts'}).",
        f"Bind the Living Ghost: level {ts.bind_ghost_level(size)}; "
        f"Transformation of the Living Ghost: level {ritual}, Might {might}.",
        "As a ghost: Ghostly Magic costs a Might point a magnitude; Ghostly Vis "
        "a point of Might Score a pawn.",
    ]


def _ascension(character: Character, values: dict[str, Any]) -> list[str]:
    best, arts = ts.best_combination(character, focus=bool(values.get("focus")))
    least = ts.ascendant_minimum(best)
    form_level = _int(values, "ascendant_level") or least
    transformation = _int(values, "ritual_level") or form_level + 5
    counted = tally(character)
    needed = ts.transformation_needed(
        form_level,
        ts.negative_characteristics_cost(character),
        character.aging.decrepitude,
        counted.virtue_points,
        counted.flaw_points,
    )
    points = ts.transformation_points(transformation, form_level)
    left = ts.ceremonies(needed, max(0, _int(values, "gathered")), points)
    said = (
        [f"The Ascendant Form must be at least level {least} ({arts or 'his Arts'})."]
        if form_level < least
        else []
    )
    return said + [
        f"Points needed {needed} (Form {form_level} + negative Characteristics, "
        "Decrepitude and excess Flaws); Might as a Daimon "
        f"{ts.ascended_might(form_level)}.",
        f"Each Transformation (level {transformation}) that penetrates gives "
        f"{points}: "
        + (
            f"{left} more ceremon(ies)."
            if left is not None
            else "it must exceed the Form."
        ),
        f"He rolls Stamina against {ts.ASCENSION_STAMINA_EASE} or passes out.",
    ]


def _live(character: Character) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        return "\n".join(
            f"{BULLET} {escape(line)}" for line in lines(character, values)
        )

    return live


def roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """A roll where the working has one; otherwise its figures. Nothing is
    kept."""
    working = _working(values, character)
    if working not in ROLLED:
        return lines(character, values)
    if working == ASCENSION:
        rolled = dice.roll(
            rng,
            character.characteristics.stamina,
            ease_factor=ts.ASCENSION_STAMINA_EASE,
            saga=saga,
        )
        said = (
            "botched: the ritual is lost to him"
            if rolled.die.botched
            else "he endures"
            if rolled.succeeded
            else "he passes out, but still gains its points"
        )
        return notes(f"Stamina {rolled.modifiers:+d} + {rolled.die.value}: {said}.")
    total, ease = _intuit_roll(character, values, max(0, _int(values, "might", 10)))
    rolled = dice.roll(rng, total, ease_factor=ease, saga=saga)
    if rolled.die.botched:
        outcome = "Botched: the spirit knows of the attempt" + (
            ", and a channel past his Magic Resistance opens."
            if rolled.die.botches > 1
            else "."
        )
    elif rolled.succeeded:
        outcome = "He knows its synthemata."
    else:
        outcome = "It escapes him."
    return notes(
        f"{total:+d} + {rolled.die.value} = {rolled.total} against {ease}: {outcome}"
    )


def spirits_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Spirits and Names: the calculator; Roll rolls where a die is
    asked for."""
    if character is None or not offers(character):
        return Refuse(
            TITLE, "Only a magus with a Mystery of spirit magic or theurgy works this."
        )
    chance = rng or random.Random()
    magus = character
    return Form(
        f"{TITLE}: {escape(magus.name)}",
        lambda: spirits_fields(saga, magus),
        lambda values: roll(saga, magus, values, chance),
        validate=problem,
        live=_live(magus),
        save_label="Roll",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Spirits' Totals",
    )
