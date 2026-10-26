"""More's dealings with faeries on a character: the Ars Fabulosa (a
bargainer's Summoning, Bonding, Captivating and Dismissing), the end of a
faerie bargain, and an offer to the Faerie Realm made with a fable point
-- no UI in here. Each roll or outcome goes into the Diary. The rules and
their pages are rules.faerie_dealings' (RoP: Faerie pp. 25-29,
131-134)."""

from __future__ import annotations

import random
from typing import Any

from .. import sourcebooks
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import FATIGUE_LEVELS, Character, DiaryEntry, Saga, ScoredTrait
from ..rules import dice, faerie_sympathy, harm, penetration, realms
from ..rules import faerie_dealings as fd
from ..rules.realms import home_aura

ARS_TITLE = "Ars Fabulosa"
ARS_HELP_ID = "ars-fabulosa"
BARGAIN_TITLE = "A Faerie Bargain"
BARGAIN_HELP_ID = "faerie-bargain"
OFFER_TITLE = "An Offer to Faerie"
OFFER_HELP_ID = "faerie-offer"
NONE = "none"
#: How a bargain ended.
STRUCK, NO_BARGAIN, CONTEST, BROKEN = "struck", "none", "contest", "broken"
ENDINGS: dict[str, str] = {
    STRUCK: "A bargain was struck",
    NO_BARGAIN: "No bargain was made",
    CONTEST: "Settle it by a contested Bargain roll",
    BROKEN: "He broke a bargain made in a summoning",
}
TRAIT_KEY = "trait_"


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    value = values.get(key)
    return value if isinstance(value, int) else default


def _bullets(lines: list[str]) -> str:
    return "\n".join(f"{BULLET} {escape(line)}" for line in lines)


def _diary(saga: Saga, character: Character, title: str, lines: list[str]) -> None:
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            title,
            "\n".join([*lines, f"Rules: {fd.SOURCE}"]),
        )
    )


def _exhausted(character: Character) -> bool:
    return character.fatigue_level == FATIGUE_LEVELS[-1]


def _traits(character: Character) -> list[ScoredTrait]:
    return faerie_sympathy.sympathy_traits(character.personality_traits)


def _trait_fields(character: Character) -> list[DialogField]:
    """A tick for each Sympathy Trait: whether it fits the faerie."""
    traits = _traits(character)
    return [
        DialogField(
            f"{TRAIT_KEY}{index}",
            f"Fits the faerie: {trait.name} {trait.score:+d}",
            "check",
            len(traits) == 1,
        )
        for index, trait in enumerate(traits)
    ]


def _applicable(character: Character, values: dict[str, Any]) -> list[ScoredTrait]:
    return [
        trait
        for index, trait in enumerate(_traits(character))
        if values.get(f"{TRAIT_KEY}{index}")
    ]


def _aura_fields(saga: Saga, character: Character) -> list[DialogField]:
    aura, realm = home_aura(saga, character)
    return [
        DialogField("aura", "Aura", "int", aura),
        DialogField(
            "aura_realm", "Aura's realm", "select", realm, options=pairs(realms.REALMS)
        ),
    ]


# -- the Ars Fabulosa --


def _power(character: Character, values: dict[str, Any]) -> str:
    return str(values.get("power") or fd.held_powers(character)[0])


def _dismissal(values: dict[str, Any]) -> str:
    return str(values.get("dismissal") or fd.CANCEL)


def ars_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What the Ars Fabulosa asks."""
    powers = fd.held_powers(character)

    def dismissing(v: dict[str, Any]) -> bool:
        return _power(character, v) == fd.DISMISSING

    return [
        DialogField("power", "Power", "select", powers[0], options=pairs(powers)),
        DialogField(
            "might",
            "The faerie's Might",
            "int",
            10,
            hint="Its Magic Resistance too. Summoning: the Might he calls, at "
            "most 5 x the Traits that fit.",
        ),
        DialogField(
            "dismissal",
            "Dismissing",
            "select",
            fd.CANCEL,
            options=[(label, key) for key, label in fd.DISMISSALS.items()],
            show_if=dismissing,
        ),
        DialogField(
            "effect_level",
            "The effect's level",
            "int",
            10,
            show_if=lambda v: dismissing(v) and _dismissal(v) != fd.RELEASE,
        ),
        DialogField(
            "dismissed",
            "Effects dismissed this round",
            "int",
            1,
            hint="Each beyond the first takes 6 off.",
            show_if=dismissing,
        ),
        DialogField(
            "deflect",
            "Deflecting it before it takes effect",
            "check",
            False,
            hint="First beat its Initiative on Quickness + Finesse.",
            show_if=lambda v: dismissing(v) and _dismissal(v) == fd.CANCEL,
        ),
        DialogField(
            "initiative",
            "The being's Initiative Total",
            "int",
            0,
            show_if=lambda v: dismissing(v) and bool(v.get("deflect")),
        ),
        DialogField(
            "held",
            "Held by his Summoning (one that penetrated)",
            "check",
            False,
            hint="Its Might then counts as level 0 for Penetration.",
            show_if=lambda v: _power(character, v) != fd.SUMMONING,
        ),
        DialogField(
            "connection",
            "Arcane Connection",
            "select",
            NONE,
            options=[("None", NONE), *pairs(penetration.ARCANE_CONNECTIONS)],
            hint="Summoning a particular faerie: without one, the storyguide "
            "picks one that fits the Traits.",
        ),
        DialogField(
            "benefit",
            "The bond's benefit",
            "select",
            fd.BOND_BENEFITS[0],
            options=pairs(fd.BOND_BENEFITS),
            show_if=lambda v: _power(character, v) == fd.BONDING,
        ),
        *_trait_fields(character),
        *_aura_fields(saga, character),
    ]


def _connection(values: dict[str, Any]) -> str | None:
    found = str(values.get("connection") or NONE)
    return None if found == NONE else found


def _target(character: Character, values: dict[str, Any]) -> fd.Target:
    power = _power(character, values)
    return fd.Target(
        power=power,
        might=max(0, _int(values, "might", 10)),
        effect_level=max(0, _int(values, "effect_level", 10)),
        dismissal=_dismissal(values),
        held=bool(values.get("held")) and power != fd.SUMMONING,
        connected=_connection(values) is not None,
    )


def _ars_total(saga: Saga, character: Character, values: dict[str, Any]) -> int:
    power = _power(character, values)
    return int(
        fd.power_total(
            character,
            power,
            aura=_int(values, "aura"),
            aura_realm=str(values.get("aura_realm") or realms.HERMETIC),
            dismissed=max(1, _int(values, "dismissed", 1))
            if power == fd.DISMISSING
            else 1,
        ).total
    )


def _bonus(character: Character, values: dict[str, Any]) -> int:
    return int(
        fd.penetration_bonus(
            character, _applicable(character, values), _connection(values)
        ).total
    )


def ars_lines(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """The total, the limit the Traits set, and what the die must reach."""
    power = _power(character, values)
    breakdown = fd.power_total(
        character,
        power,
        aura=_int(values, "aura"),
        aura_realm=str(values.get("aura_realm") or realms.HERMETIC),
        dismissed=max(1, _int(values, "dismissed", 1)) if power == fd.DISMISSING else 1,
    )
    base = int(breakdown.total)
    terms = ", ".join(
        f"{line.label} {int(line.amount or 0):+d}" for line in breakdown.lines
    )
    applicable = _applicable(character, values)
    target = _target(character, values)
    bonus = _bonus(character, values)
    limit = fd.might_limit(applicable)
    said = [f"{power} {base:+d} + stress die ({terms})."]
    said.append(
        f"The Traits that fit reach Might {limit}"
        + (" or an effect of that level." if power == fd.DISMISSING else ".")
        if applicable
        else "Tick the Sympathy Traits that fit the faerie: none, no power works."
    )
    least = fd.total_needed(target, bonus)
    if fd.needs_penetration(target):
        said.append(
            f"Penetration bonus {bonus:+d} (his Penetration and the best Trait "
            f"that fits) against Magic Resistance {target.might}, less "
            f"{fd.penetration_level(target)} for the level."
        )
    else:
        said.append("No Arcane Connection: the summons needn't penetrate.")
    said.append(f"It works on a total of {least}: a die of {max(least - base, 0)}.")
    if power == fd.DISMISSING and values.get("deflect"):
        said.append(
            f"Deflecting: Quickness + Finesse {fd.deflect_total(character, applicable):+d} "
            f"+ stress die must beat Initiative {_int(values, 'initiative')}."
        )
    said.append(
        f"A Fatigue level (he is {character.fatigue_level}); "
        f"{fd.botch_dice(character, _int(values, 'aura'), str(values.get('aura_realm') or realms.HERMETIC))} "
        "botch dice."
    )
    return said


def ars_problem(character: Character, values: dict[str, Any]) -> str | None:
    applicable = _applicable(character, values)
    if not applicable:
        return "Tick at least one Sympathy Trait that fits the faerie."
    if _int(values, "might", 10) < 0 or _int(values, "effect_level", 10) < 0:
        return "A Might or a level can't be negative."
    target = _target(character, values)
    limit = fd.might_limit(applicable)
    reach = (
        target.effect_level
        if target.power == fd.DISMISSING and target.dismissal != fd.RELEASE
        else target.might
    )
    if reach > limit:
        return (
            f"The Traits that fit reach {limit} at most (5 x their sizes); "
            f"this is {reach}."
        )
    if _exhausted(character):
        return "He has no Fatigue level left to spend."
    if _int(values, "dismissed", 1) < 1:
        return "At least one effect is dismissed."
    return None


def ars_roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll: a Fatigue level spent, the outcome, the Traits'
    experience, and a Diary entry."""
    power = _power(character, values)
    aura = _int(values, "aura")
    aura_realm = str(values.get("aura_realm") or realms.HERMETIC)
    applicable = _applicable(character, values)
    target = _target(character, values)
    bonus = _bonus(character, values)
    base = _ars_total(saga, character, values)
    harm.lose_fatigue(character, long_term=False)
    lines: list[str] = []
    if power == fd.DISMISSING and values.get("deflect"):
        quick = dice.roll(
            rng,
            fd.deflect_total(character, applicable),
            botch_dice=fd.botch_dice(character, aura, aura_realm),
            saga=saga,
        )
        initiative = _int(values, "initiative")
        beat = not quick.die.botched and quick.total > initiative
        lines.append(
            f"Deflecting: Quickness + Finesse {quick.modifiers:+d} + "
            f"{quick.die.value} = {quick.total} against Initiative {initiative}: "
            + ("in time." if beat else "too late; the power takes effect first.")
        )
    rolled = dice.roll(
        rng, base, botch_dice=fd.botch_dice(character, aura, aura_realm), saga=saga
    )
    result = fd.outcome(target, rolled.total, bonus, botched=rolled.die.botched)
    against = (
        f"effect level {target.effect_level}"
        if power == fd.DISMISSING and target.dismissal != fd.RELEASE
        else f"Might {target.might}"
    )
    lines.insert(
        0,
        f"{power} {base:+d} + {rolled.die.value} = {rolled.total} against "
        f"{against}" + (" (held by his Summoning)" if target.held else "") + ".",
    )
    lines.append(result.text)
    if power == fd.BONDING and result.worked:
        lines.append(f"The bond's benefit: {values.get('benefit') or ''}.")
    xp = fd.die_experience(rolled.die.faces[0], rolled.die.botches)
    for trait in applicable if xp else ():
        change = fd.trait_experience(
            trait, xp, character.aging.warping_score, limited=False
        )
        lines.append(fd.experience_line(trait, xp, change))
    lines.append(f"A Fatigue level spent: he is {character.fatigue_level}.")
    if power == fd.SUMMONING:
        lines.append(
            "When the summoning ends, record whether a bargain was struck "
            "(More: A Faerie Bargain)."
        )
    _diary(saga, character, f"{ARS_TITLE}: {power}", lines)
    return notes(*lines)


def ars_fabulosa_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Ars Fabulosa: the calculator; Roll rolls it, kept in the
    Diary."""
    if character is None or not fd.bargains(character):
        return Refuse(
            ARS_TITLE, "Only one who holds an Ars Fabulosa power bargains with them."
        )
    if not _traits(character):
        return Refuse(
            ARS_TITLE,
            "The Ars Fabulosa need a Sympathy Trait that fits the faerie "
            "(RoP: Faerie p. 131); he has none.",
        )
    chance = rng or random.Random()
    who = character
    return Form(
        f"{ARS_TITLE}: {escape(who.name)}",
        lambda: ars_fields(saga, who),
        lambda values: ars_roll(saga, who, values, chance),
        validate=lambda values: ars_problem(who, values),
        live=lambda values: _bullets(ars_lines(saga, who, values)),
        save_label="Roll",
        help_id=ARS_HELP_ID,
        inspector="The Bargainer's Total",
    )


# -- a faerie bargain --


def _ending(values: dict[str, Any]) -> str:
    return str(values.get("ending") or STRUCK)


def bargain_fields(character: Character) -> list[DialogField]:
    """What A Faerie Bargain asks."""
    traits = _traits(character)
    names = [t.name for t in traits]
    return [
        DialogField("faerie", "The faerie", "text", "", required=True),
        DialogField(
            "wants",
            "First work out what it wants",
            "check",
            False,
            hint="Intelligence + Faerie Lore after some trial bargaining.",
        ),
        DialogField(
            "wants_ease",
            "Its Ease Factor",
            "int",
            fd.WANTS_EASE,
            hint="12 or more.",
            show_if=lambda v: bool(v.get("wants")),
        ),
        DialogField(
            "wants_specialty",
            "The Sympathy Trait as Faerie Lore's specialty",
            "check",
            False,
            hint="Adds the Trait, but the die is a stress die and may botch.",
            show_if=lambda v: bool(names) and bool(v.get("wants")),
        ),
        DialogField(
            "ending",
            "How it ended",
            "select",
            STRUCK,
            options=[(label, key) for key, label in ENDINGS.items()],
        ),
        DialogField(
            "faerie_total",
            "The faerie's Communication + Bargain",
            "int",
            3,
            show_if=lambda v: _ending(v) == CONTEST,
        ),
        DialogField(
            "bargain_specialty",
            "The Sympathy Trait as Bargain's specialty",
            "check",
            True,
            hint="Adds the Trait; a stress die that may botch.",
            show_if=lambda v: bool(names) and _ending(v) == CONTEST,
        ),
        DialogField(
            "trait",
            "The Sympathy Trait that fits it",
            "select",
            names[0] if names else "",
            options=pairs(names),
            hint="It gains an experience point for a bargain, loses one for none.",
            show_if=lambda v: bool(names) and _ending(v) != BROKEN,
        ),
        DialogField(
            "new_trait",
            "The -3 Sympathy Trait he gains",
            "text",
            "",
            hint="Named for the faerie, such as Oak Maidens.",
            show_if=lambda v: _ending(v) == BROKEN,
        ),
        DialogField("terms", "The terms", "area", ""),
    ]


def _chosen(character: Character, values: dict[str, Any]) -> ScoredTrait | None:
    name = str(values.get("trait") or "")
    return next((t for t in _traits(character) if t.name == name), None)


def _specialty(
    trait: ScoredTrait | None, values: dict[str, Any], key: str
) -> list[ScoredTrait]:
    """The Trait used as the roll's specialty, if he chose to."""
    return [trait] if trait is not None and values.get(key) else []


def bargain_lines(character: Character, values: dict[str, Any]) -> list[str]:
    ending = _ending(values)
    trait = _chosen(character, values)
    said: list[str] = []
    if values.get("wants"):
        used = _specialty(trait, values, "wants_specialty")
        total = fd.wants_total(character, used)
        die = (
            f"stress die (his {used[0].name} Trait as specialty: it may botch, "
            "for Warping Points)"
            if used
            else "simple die"
        )
        said.append(
            f"What it wants: Intelligence + Faerie Lore {total:+d} + {die} "
            f"against {_int(values, 'wants_ease', fd.WANTS_EASE)}."
        )
    if ending == CONTEST:
        used = _specialty(trait, values, "bargain_specialty")
        mine = fd.bargain_total(character, used)
        said.append(
            f"Contested: his Communication + Bargain + Faerie Rank {mine:+d}"
            + (f" ({used[0].name} as specialty)" if used else "")
            + f" + stress die, against {_int(values, 'faerie_total', 3):+d} + "
            "stress die; the higher wins, a tie striking no bargain (the app's "
            "assumption: the book gives no tie rule)."
        )
    if ending == BROKEN:
        said.append(
            "A bargain made in a summoning binds the faerie; breaking it gives "
            f"him a {fd.BROKEN_BARGAIN_TRAIT} Sympathy Trait fitting the faerie, "
            "and it may cost him Faerie Rank. Dismissing could have freed him "
            "of it without that."
        )
    elif trait is not None:
        said.append(
            f"{trait.name} {trait.score:+d}: +1 xp for a bargain, -1 for none "
            f"({trait.deeds} of {faerie_sympathy.xp_to_raise(trait.score)} toward "
            "the next value)."
        )
    else:
        said.append("He has no Sympathy Trait for the experience.")
    if ending in (STRUCK, CONTEST):
        said.append("The bargain binds the faerie, whatever he does.")
    return said


def _specialty_experience(
    character: Character, used: list[ScoredTrait], rolled: dice.Roll
) -> list[str]:
    """A Trait used as a specialty: a botch gives Warping Points, and a 1
    or a botch's 0s move the Trait (pp. 102-103)."""
    if not used:
        return []
    said: list[str] = []
    if rolled.die.botched:
        said.append(
            f"Botched with {used[0].name} as specialty: Warping Points, as the "
            "storyguide sets (p. 102)."
        )
    xp = fd.die_experience(rolled.die.faces[0], rolled.die.botches)
    if xp:
        change = fd.trait_experience(
            used[0], xp, character.aging.warping_score, limited=False
        )
        said.append(fd.experience_line(used[0], xp, change))
    return said


def bargain_problem(character: Character, values: dict[str, Any]) -> str | None:
    if _ending(values) == BROKEN:
        name = str(values.get("new_trait") or "").strip()
        if not name:
            return "Name the -3 Sympathy Trait he gains."
        if any(t.name.casefold() == name.casefold() for t in _traits(character)):
            return f"He already has a Sympathy Trait named {name}."
    return None


def bargain_save(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The rolls, the Trait's experience or the new -3 Trait, and a Diary
    entry."""
    ending = _ending(values)
    faerie = str(values.get("faerie") or "a faerie").strip()
    trait = _chosen(character, values)
    lines: list[str] = []
    if values.get("wants"):
        ease = _int(values, "wants_ease", fd.WANTS_EASE)
        used = _specialty(trait, values, "wants_specialty")
        rolled = dice.roll(
            rng,
            fd.wants_total(character, used),
            ease_factor=ease,
            stress=bool(used),
            botch_dice=fd.specialty_botch_dice(character),
            saga=saga,
        )
        lines.append(
            f"What it wants: {rolled.modifiers:+d} + {rolled.die.value} = "
            f"{rolled.total} against {ease}: "
            + ("he works it out." if rolled.succeeded else "he can't tell.")
        )
        lines += _specialty_experience(character, used, rolled)
    if ending == CONTEST:
        used = _specialty(trait, values, "bargain_specialty")
        mine = dice.roll(
            rng,
            fd.bargain_total(character, used),
            botch_dice=fd.specialty_botch_dice(character),
            saga=saga,
        )
        theirs = dice.roll(rng, _int(values, "faerie_total", 3), saga=saga)
        # The book gives no tie rule: a tie striking no bargain is the
        # app's assumption.
        won = not mine.die.botched and mine.total > theirs.total
        lines.append(
            f"Contested Bargain: he {mine.total}, the faerie {theirs.total}: "
            + ("a bargain is struck." if won else "no bargain.")
        )
        lines += _specialty_experience(character, used, mine)
        ending = STRUCK if won else NO_BARGAIN
    if ending == BROKEN:
        name = str(values.get("new_trait") or "").strip()
        fd.break_bargain(character, name)
        lines.append(
            f"He broke his bargain with {faerie}: a new Sympathy Trait "
            f"{name} {fd.BROKEN_BARGAIN_TRAIT:+d}."
        )
    else:
        lines.insert(0, f"With {faerie}: {ENDINGS[ending].lower()}.")
        if trait is not None:
            xp = 1 if ending == STRUCK else -1
            change = fd.trait_experience(
                trait, xp, character.aging.warping_score, limited=True
            )
            lines.append(fd.experience_line(trait, xp, change))
    terms = str(values.get("terms") or "").strip()
    if terms:
        lines.append(f"Terms: {terms}")
    _diary(saga, character, BARGAIN_TITLE, lines)
    return notes(*lines)


def faerie_bargain_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's A Faerie Bargain: how a summoning's bargain ended, kept in
    the Diary."""
    if character is None or not fd.bargains(character):
        return Refuse(
            BARGAIN_TITLE, "Only one who holds an Ars Fabulosa power is bound so."
        )
    chance = rng or random.Random()
    who = character
    return Form(
        f"{BARGAIN_TITLE}: {escape(who.name)}",
        lambda: bargain_fields(who),
        lambda values: bargain_save(saga, who, values, chance),
        validate=lambda values: bargain_problem(who, values),
        live=lambda values: _bullets(bargain_lines(who, values)),
        save_label="Record",
        help_id=BARGAIN_HELP_ID,
        inspector="The Bargain",
    )


# -- an offer to the Faerie Realm --


def offer_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What An Offer to Faerie asks."""
    held = fd.offer_abilities(character)
    academe = sourcebooks.in_play("A&A", sourcebooks.saga_books(saga))
    fields = [
        DialogField("change_text", "The change he asks for", "text", "", required=True),
        DialogField("ability", "Ability", "select", held[0], options=pairs(held)),
        DialogField(
            "threat",
            "The threat it overcomes",
            "select",
            "Serious",
            options=pairs(fd.THREATS),
        ),
        DialogField(
            "change",
            "The change",
            "select",
            "The immediate environment gives an advantage",
            options=pairs(fd.CHANGES),
        ),
        DialogField(
            "promise",
            "The promise of service",
            "select",
            "A conventional story",
            options=pairs(fd.PROMISES),
        ),
        DialogField(
            "goods",
            "Offered with it",
            "select",
            "Nothing more",
            options=pairs(fd.GOODS),
        ),
        DialogField(
            "place",
            "Where",
            "select",
            fd.REALM,
            options=[(label, key) for key, label in fd.PLACES.items()],
        ),
        DialogField(
            "fable_score",
            "His fable score",
            "int",
            1,
            hint="This visit's; it needs an unspent fable point.",
        ),
        DialogField(
            "spend_fable",
            "Spend another fable point on the roll",
            "check",
            False,
            hint="+ his fable score.",
        ),
    ]
    if academe:
        fields += [
            DialogField("artistic_reputation", "Artistic Reputation", "int", 0),
            DialogField(
                "patron_might", "Might bequeathed by a Faerie Patron", "int", 0
            ),
        ]
    return fields


def _offer(values: dict[str, Any], character: Character) -> fd.Offer:
    return fd.Offer(
        ability=str(values.get("ability") or fd.offer_abilities(character)[0]),
        goods=str(values.get("goods") or "Nothing more"),
        promise=str(values.get("promise") or "A conventional story"),
        change=str(
            values.get("change") or "The immediate environment gives an advantage"
        ),
        place=str(values.get("place") or fd.REALM),
        artistic_reputation=max(0, _int(values, "artistic_reputation")),
        patron_might=max(0, _int(values, "patron_might")),
        fable_score=max(0, _int(values, "fable_score", 1)),
        spend_fable=bool(values.get("spend_fable")),
    )


def _offer_botch_dice(character: Character) -> int:
    return 1 + faerie_sympathy.extra_botch_dice(character.personality_traits)


def offer_lines(character: Character, values: dict[str, Any]) -> list[str]:
    offer = _offer(values, character)
    breakdown = fd.offer_total(character, offer)
    base = int(breakdown.total)
    ease = fd.offer_ease_factor(str(values.get("threat") or "Serious"), offer.place)
    terms = ", ".join(
        f"{line.label} {int(line.amount or 0):+d}" for line in breakdown.lines
    )
    score = offer.fable_score
    return [
        f"Offer {base:+d} + stress die ({terms}).",
        f"Accepted on {ease}: a die of {max(ease - base, 0)}.",
        f"It costs {fd.offer_fable_cost(offer)} fable point(s) and a Long-Term "
        "Fatigue level, accepted or not; an offer not understood binds him to "
        "no promise.",
        f"Fable score {score}: a point adds +{score} to a roll; raising it to "
        f"{score + 1} costs {fd.fable_points_to_raise(score)} points.",
        f"{_offer_botch_dice(character)} botch dice.",
    ]


def offer_problem(character: Character, values: dict[str, Any]) -> str | None:
    if _int(values, "fable_score", 1) < 1:
        return "An offer needs a fable score and an unspent fable point."
    if _int(values, "artistic_reputation") < 0 or _int(values, "patron_might") < 0:
        return "A Reputation or a Might can't be negative."
    if _exhausted(character):
        return "He has no Fatigue level left to spend."
    return None


def offer_roll(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """The roll: a Long-Term Fatigue level spent, and a Diary entry."""
    offer = _offer(values, character)
    base = int(fd.offer_total(character, offer).total)
    threat = str(values.get("threat") or "Serious")
    ease = fd.offer_ease_factor(threat, offer.place)
    rolled = dice.roll(
        rng,
        base,
        ease_factor=ease,
        botch_dice=_offer_botch_dice(character),
        saga=saga,
    )
    harm.lose_fatigue(character, long_term=True)
    asked = str(values.get("change_text") or "").strip()
    lines = [
        f"Asked: {asked} ({offer.change}; {offer.promise}; a {threat} threat).",
        f"Offer {base:+d} + {rolled.die.value} = {rolled.total} against {ease}: "
        + (
            "accepted; the change happens, and he owes the promise."
            if rolled.succeeded
            else "botched."
            if rolled.die.botched
            else "not accepted."
        ),
        f"{fd.offer_fable_cost(offer)} fable point(s) and a Long-Term Fatigue "
        f"level spent: he is {character.fatigue_level}.",
    ]
    _diary(saga, character, OFFER_TITLE, lines)
    return notes(*lines)


def faerie_offer_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's An Offer to Faerie: the calculator; Roll rolls it, kept in
    the Diary."""
    if character is None or character.animal is not None:
        return Refuse(OFFER_TITLE, "Choose a person first.")
    chance = rng or random.Random()
    who = character
    return Form(
        f"{OFFER_TITLE}: {escape(who.name)}",
        lambda: offer_fields(saga, who),
        lambda values: offer_roll(saga, who, values, chance),
        validate=lambda values: offer_problem(who, values),
        live=lambda values: _bullets(offer_lines(who, values)),
        save_label="Roll",
        help_id=OFFER_HELP_ID,
        inspector="The Offer",
    )
