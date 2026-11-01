"""A galdraman's forms (More): Conjure a Spirit, Bargain with a Lord and Bind
an Item. Each rolls as the rules in rules.galdor say, writes the result in
the Diary, and gives Warping for a botch's zeroes, as Cast a Power does; a
bargain struck is kept among the tradition's bound beings, an item among
its effects."""

from __future__ import annotations

import random
from typing import Any

from .. import diaries, seasons, traditions
from ..commands import Form, notes
from ..form_spec import DialogField
from ..markup import escape, plural
from ..models import (
    EFFECT_FREQUENCIES,
    BoundBeing,
    CastingRule,
    Character,
    Saga,
    TraditionDef,
    TraditionEffect,
    VirtueFlawInstance,
)
from ..models import FATIGUE_LEVELS as FATIGUE
from ..rules import casting as hermetic_casting
from ..rules import dice, galdor, realms
from ..rules import hedge_casting as hc
from ..rules.casting import magnitude
from ..rules.enchantment import frequency_of

CONJURE_TITLE = "Conjure a Spirit"
BARGAIN_TITLE = "Bargain with a Lord"
BIND_TITLE = "Bind an Item"
CONJURE_HELP = "galdor-conjure"
BARGAIN_HELP = "galdor-bargain"
BIND_HELP = "galdor-bind"

AGREES, REFUSES, ROLLS = "agrees", "refuses", "rolls"
LIFETIME, SERVICE = "lifetime", "service"


def _tradition() -> TraditionDef:
    found = traditions.find(galdor.TRADITION_ID)
    if found is None:
        raise LookupError("The catalog has no Traditional Galdramen")
    return found


def _aura_fields(saga: Saga, character: Character) -> list[DialogField]:
    aura, realm = realms.present_aura(saga, character)
    return [
        DialogField("aura", "Aura", "int", aura, hint="Where he sings."),
        DialogField(
            "aura_realm",
            "Aura realm",
            "select",
            realm,
            options=[(r, r) for r in realms.aura_realms(saga, realm)],
            hint="Landvaettir count as Faerie outside a Magic aura.",
        ),
    ]


def _die_field() -> DialogField:
    return DialogField(
        "die",
        "Die",
        "optint",
        None,
        hint="Blank: rolled now. Type the die shown at the table to use it "
        "instead (0 is a zero, which may botch).",
    )


def _song_field(character: Character) -> DialogField:
    songs = galdor.songs_of(character)
    return DialogField(
        "song",
        "Song Talent",
        "select",
        songs[0] if songs else None,
        options=[(s, s) for s in songs],
        allow_blank=not songs,
        hint="It caps the magnitude he may ask for.",
    )


def _duration_field() -> DialogField:
    return DialogField(
        "duration",
        "Duration",
        "select",
        galdor.DURATIONS[0],
        options=[(d, d) for d in galdor.DURATIONS],
        hint="Anything longer needs a deal with a lord.",
    )


def _level_problem(character: Character, values: dict[str, Any]) -> str | None:
    level = values.get("level") or 0
    if level <= 0:
        return "The effect's level must be above 0."
    return galdor.song_problem(character, values.get("song") or "", level)


def _roll(
    saga: Saga,
    character: Character,
    rule: CastingRule,
    song: str,
    level: int,
    aura: int,
    aura_realm: str,
    typed: int | None,
    rng: random.Random,
) -> tuple[int, int, str]:
    """(the die's value, a botch's zeroes, how to say the die): a stress die
    with the casting's botch dice, or the one typed in."""
    tradition = _tradition()
    count = hc.botch_dice(
        tradition,
        rule,
        level=level,
        aura=aura,
        aura_realm=aura_realm,
        realm=hc.power_realm(
            character, tradition, rule, (song,), aura=aura, aura_realm=aura_realm
        ),
    )
    cord = hermetic_casting.golden_cord(saga, character)
    if count > 1 and cord:
        count = max(1, count - cord)
    return _die(saga, typed, count, rng)


def _die(
    saga: Saga, typed: int | None, count: int, rng: random.Random
) -> tuple[int, int, str]:
    """(the die's value, a botch's zeroes, how to say the die): a stress die
    with `count` botch dice, or the die typed in. A typed 0 rolls the botch
    dice, so a zero at the table can botch."""
    if typed is not None:
        value = max(0, int(typed))
        zeroes = dice.botch_roll(rng, count, saga=saga) if value == 0 else 0
        said = f"die {value} (typed)"
    else:
        rolled = dice.stress_die(rng, count, saga=saga)
        value = rolled.value
        zeroes = rolled.botches if rolled.botched else 0
        said = f"stress die {value}"
    if zeroes:
        said += f", botched with {plural(zeroes, 'zero')}"
    return value, zeroes, said


def _write(
    saga: Saga,
    character: Character,
    name: str,
    lines: list[str],
    zeroes: int,
    aura: int,
    rng: random.Random,
) -> list[str]:
    """The result in the Diary, and Warping for a botch's zeroes."""
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        " ".join(lines),
        characters=[character],
    )
    told = list(lines)
    if zeroes:
        told += seasons.gain_warping(saga, character, zeroes, rng, aura=aura)
    return notes(*(escape(line) for line in told))


# ---------------------------------------------------------------------------
# Conjure a Spirit


def conjure_fields(saga: Saga, character: Character) -> list[DialogField]:
    return [
        _song_field(character),
        DialogField(
            "level",
            "Effect level",
            "int",
            0,
            hint="By the Hermetic guidelines; the storyguide has the last word.",
        ),
        DialogField(
            "effect", "What it does", "text", "", hint="For the Diary; may be blank."
        ),
        _duration_field(),
        DialogField(
            "ritual",
            "A ritual effect",
            "check",
            False,
            hint="15 minutes and a pawn of vis a magnitude, where a Hermetic "
            "magus would need a ritual.",
        ),
        DialogField(
            "ground",
            "Touching the ground",
            "check",
            False,
            hint="Halves the total; a platform, chair or table keeps him off it.",
        ),
        *_aura_fields(saga, character),
        DialogField(
            "hours",
            "Hours he holds the song",
            "int",
            0,
            show_if=lambda values: values.get("duration") == galdor.CONCENTRATION,
            hint="Rolls Sta + Music for each hour, and stops if the song fails.",
        ),
        _die_field(),
    ]


def conjure_problem(character: Character, values: dict[str, Any]) -> str | None:
    if not galdor.songs_of(character):
        return f"{escape(character.name)} knows no Song Talent."
    if (values.get("hours") or 0) < 0:
        return "The hours can't be fewer than 0."
    return _level_problem(character, values)


def _tire(character: Character, levels: int) -> None:
    """Lose Fatigue levels, to the last the sheet has."""
    at = FATIGUE.index(character.fatigue_level)
    character.fatigue_level = FATIGUE[min(at + levels, len(FATIGUE) - 1)]


def _hold(
    saga: Saga, character: Character, hours: int, rng: random.Random
) -> tuple[list[str], int, bool]:
    """An hour's roll at a time, until the hours end or the song does (p.
    47): the lines to say, the zeroes of any botch, and whether it held."""
    base = galdor.hold_total(character)
    tired = 0
    for hour in range(1, hours + 1):
        rolled = dice.stress_die(rng, 1, saga=saga)
        if rolled.botched:
            _tire(character, tired)
            return [f"Hour {hour}: the song botches and fails."], rolled.botches, False
        going, tiring = galdor.holds_song(base + rolled.value, hour)
        tired += 1 if tiring else 0
        if not going:
            _tire(character, tired)
            return (
                [
                    f"The song fails in hour {hour} ({base + rolled.value} against "
                    f"{galdor.hold_ease(hour)}), for {plural(tired, 'Fatigue level')}."
                ],
                0,
                False,
            )
    _tire(character, tired)
    return (
        [
            f"He holds the song {plural(hours, 'hour')}, for "
            f"{plural(tired, 'Fatigue level')}."
        ],
        0,
        True,
    )


def conjure(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    rng: random.Random | None = None,
) -> list[str]:
    """Sing the song and say what comes."""
    rng = rng or random.Random()
    tradition = _tradition()
    song = values.get("song") or ""
    level = values.get("level") or 0
    duration = values.get("duration") or galdor.DURATIONS[0]
    aura = values.get("aura") or 0
    aura_realm = values.get("aura_realm") or realms.HERMETIC
    ritual = bool(values.get("ritual"))
    name = galdor.GROUND_RULE if values.get("ground") else galdor.CONJURE_RULE
    rule = galdor.tradition_rule(tradition, name)
    score = hc.casting_score(
        character, tradition, rule, (song,), aura=aura, aura_realm=aura_realm
    )
    value, zeroes, die_text = _roll(
        saga, character, rule, song, level, aura, aura_realm, values.get("die"), rng
    )
    total = hc.casting_total(rule, int(score.total), value)
    result = galdor.conjured(total, level, duration)
    what = values.get("effect") or "the effect"
    lines = [
        f"{song} for {what}: Casting Score {int(score.total)}, {die_text}: "
        f"{total} against level {level}, "
        f"{plural(galdor.song_minutes(level, ritual=ritual), 'minute')} of song."
    ]
    if values.get("ground"):
        lines.append("Halved for touching the ground.")
    if zeroes:
        lines.append("It botches.")
    elif not result.works:
        lines.append("No spirit comes.")
    else:
        penetration = hc.penetration_total(
            character, total, level, hc.penetration_bonus(character)
        )
        lines.append(
            f"A spirit of Might {result.might} comes; Penetration {penetration}."
        )
        if ritual:
            lines.append(
                f"It takes {plural(galdor.ritual_vis(level), 'pawn')} on arrival."
            )
        hours = values.get("hours") or 0
        finished = True
        if duration == galdor.CONCENTRATION and hours:
            held, held_zeroes, finished = _hold(saga, character, hours, rng)
            lines += held
            zeroes += held_zeroes
        if result.lingers and finished:
            lines.append(
                f"It works on {plural(dice.simple_die(rng), 'hour')} after he stops "
                "singing."
            )
    return _write(saga, character, f"Conjured: {song}", lines, zeroes, aura, rng)


def conjure_form(saga: Saga, character: Character) -> Form:
    return Form(
        f"{CONJURE_TITLE}: {escape(character.name)}",
        lambda: conjure_fields(saga, character),
        lambda values: conjure(saga, character, values),
        validate=lambda values: conjure_problem(character, values),
        save_label="Sing",
        help_id=CONJURE_HELP,
    )


# ---------------------------------------------------------------------------
# Bargain with a Lord


def _rolling(values: dict[str, Any]) -> bool:
    return values.get("how") == ROLLS


def _pairs(table: dict[str, int]) -> list[tuple[str, str]]:
    return [(f"{name} ({value:+d})", name) for name, value in table.items()]


def _offer_fills(values: dict[str, Any]) -> dict[str, Any]:
    return {"offered": galdor.standard_vis(values.get("level") or 0)}


def bargain_fields(character: Character) -> list[DialogField]:
    return [
        DialogField("lord", "The lord", "text", "", required=True),
        DialogField(
            "service",
            "The service",
            "text",
            "",
            required=True,
            hint="What the lord's minion does, and for how long.",
        ),
        DialogField(
            "level",
            "Effect level",
            "int",
            0,
            fills=_offer_fills,
            hint="At Sun Duration, which lets the spirit sustain it; the "
            "storyguide may adjust it.",
        ),
        DialogField(
            "vis_yearly",
            "Vis a year",
            "int",
            0,
            hint="The tithe, if it lasts over a year: about double the magnitude "
            "as a guide, and a skilled galdraman asks less.",
        ),
        DialogField(
            "favour",
            "Favour owed",
            "text",
            "",
            hint="Any service he owes the lord besides.",
        ),
        DialogField(
            "how",
            "His answer",
            "select",
            AGREES,
            options=[
                ("Agrees, in play", AGREES),
                ("Refuses, in play", REFUSES),
                ("Roll the Bargain", ROLLS),
            ],
            hint="Play it out, or roll by Houses of Hermes: Societates p. 136.",
        ),
        DialogField(
            "scope",
            "Its terms",
            "select",
            "Specific",
            options=_pairs(galdor.SCOPES),
            show_if=_rolling,
        ),
        DialogField(
            "length",
            "Service lasts",
            "select",
            "A week",
            options=_pairs(galdor.LENGTHS),
            show_if=_rolling,
        ),
        DialogField(
            "duty",
            "He accepts",
            "select",
            "None",
            options=_pairs(galdor.DUTIES),
            show_if=_rolling,
        ),
        DialogField(
            "offered",
            "Vis offered",
            "int",
            galdor.standard_vis(0),
            show_if=_rolling,
            hint="Double the magnitude is the standard: +2 a pawn under it, -2 "
            "a pawn over.",
        ),
        DialogField(
            "weak",
            "A weak lord",
            "check",
            False,
            show_if=_rolling,
            hint="A botch brings Supernatural Nuisance; from a stronger one, "
            "Plagued by Supernatural Entity.",
        ),
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            show_if=_rolling,
            hint="Blank: rolled now. Type the die shown at the table to use it "
            "instead (0 is a zero, which may botch).",
        ),
    ]


def bargain_problem(values: dict[str, Any]) -> str | None:
    if (values.get("level") or 0) < 0:
        return "The effect's level can't be negative."
    if (values.get("vis_yearly") or 0) < 0 or (values.get("offered") or 0) < 0:
        return "Pawns of vis can't be fewer than 0."
    return None


def _strike(character: Character, values: dict[str, Any]) -> None:
    """The deal, kept among the tradition's bound beings."""
    character.bound_beings.append(
        BoundBeing(
            name=values["lord"],
            tradition=galdor.TRADITION_ID,
            kind=galdor.DEAL,
            service=values.get("service") or "",
            vis_yearly=values.get("vis_yearly") or 0,
            favour=values.get("favour") or "",
        )
    )


def bargain(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    rng: random.Random | None = None,
) -> list[str]:
    """Strike the deal, record the refusal, or roll for it."""
    rng = rng or random.Random()
    lord, service = values["lord"], values.get("service") or ""
    name = f"Bargain: {lord}"
    how = values.get("how") or AGREES
    if how == AGREES:
        _strike(character, values)
        return _write(saga, character, name, [f"{lord} agrees: {service}."], 0, 0, rng)
    if how == REFUSES:
        return _write(saga, character, name, [f"{lord} refuses."], 0, 0, rng)
    level = values.get("level") or 0
    ease = galdor.bargain_ease(
        values.get("scope") or "Specific",
        values.get("length") or "A week",
        values.get("duty") or "None",
        standard=galdor.standard_vis(level),
        offered=values.get("offered") or 0,
    )
    value, zeroes, die_text = _die(saga, values.get("die"), 1, rng)
    total = galdor.bargain_total(character, value)
    lines = [f"Bargain Total {total} ({die_text}) against {ease}."]
    if zeroes:
        flaw = galdor.botch_flaw(weak=bool(values.get("weak")))
        character.virtues_flaws.append(VirtueFlawInstance(flaw, temporary=True))
        lines.append(
            f"It botches: {lord} is offended, and the Flaw {_flaw_name(flaw)} "
            "lasts at least a month; take it off with Gain or Lose when it ends."
        )
    elif total >= ease:
        _strike(character, values)
        lines.append(f"{lord} agrees: {service}.")
    else:
        lines.append(f"No deal with {lord}.")
    # A bargain's botch is the Flaw alone, with no Warping (HoH:S p. 136).
    return _write(saga, character, name, lines, 0, 0, rng)


def _flaw_name(vf_id: str) -> str:
    return (
        "Supernatural Nuisance"
        if vf_id == galdor.NUISANCE
        else "Plagued by Supernatural Entity"
    )


def bargain_form(saga: Saga, character: Character) -> Form:
    return Form(
        f"{BARGAIN_TITLE}: {escape(character.name)}",
        lambda: bargain_fields(character),
        lambda values: bargain(saga, character, values),
        validate=bargain_problem,
        save_label="Record",
        help_id=BARGAIN_HELP,
    )


# ---------------------------------------------------------------------------
# Bind an Item


def _lifetime(values: dict[str, Any]) -> bool:
    return values.get("binding") == LIFETIME


def bind_fields(saga: Saga, character: Character) -> list[DialogField]:
    deals = [d.name for d in galdor.deals(character)]
    crafts = galdor.crafts_of(character)
    return [
        DialogField("name", "The item", "text", "", required=True),
        DialogField(
            "deal",
            "Deal",
            "select",
            deals[0] if deals else None,
            options=[(escape(d), d) for d in deals],
            allow_blank=not deals,
            hint="The bargain struck with a lord comes first.",
        ),
        DialogField(
            "binding",
            "Binding",
            "select",
            LIFETIME,
            options=[
                ("For his lifetime", LIFETIME),
                ("A single service", SERVICE),
            ],
            hint="A single service lasts a year and a day.",
        ),
        _song_field(character),
        DialogField("level", "Effect level", "int", 0),
        _duration_field(),
        DialogField(
            "constant",
            "Constant Use",
            "check",
            False,
            show_if=lambda values: (
                _lifetime(values) and values.get("duration") == galdor.CONCENTRATION
            ),
            hint="Adds 5 to the level.",
        ),
        DialogField(
            "uses",
            "Uses a day",
            "int",
            1,
            show_if=_lifetime,
            hint="More than one adds the Effect Frequency Table's levels.",
        ),
        DialogField(
            "craft",
            "Craft used",
            "select",
            crafts[0] if crafts else None,
            options=[(escape(c), c) for c in crafts],
            allow_blank=not crafts,
            hint="It limits Galdor Wisdom and the Song. Craft: Runes inscribes "
            "a ready-made item.",
        ),
        DialogField(
            "bonuses",
            "Form and effect bonuses",
            "int",
            0,
            hint="The item's shape and material bonuses (DE pp. 111-112).",
        ),
        *_aura_fields(saga, character),
        _die_field(),
    ]


def bind_problem(character: Character, values: dict[str, Any]) -> str | None:
    if not galdor.deals(character):
        return "Strike a bargain with a lord first."
    if not galdor.songs_of(character):
        return f"{escape(character.name)} knows no Song Talent."
    if not values.get("craft"):
        return "He needs a Craft to make the item."
    if (values.get("uses") or 0) < 0:
        return "The uses a day can't be fewer than 0."
    return _level_problem(character, values)


def _needed(values: dict[str, Any]) -> tuple[int, int]:
    """(the effect's level, what the total must reach)."""
    lifetime = _lifetime(values)
    level = galdor.bind_level(
        values.get("level") or 0,
        constant=lifetime
        and bool(values.get("constant"))
        and values.get("duration") == galdor.CONCENTRATION,
    )
    uses = values.get("uses") or 0
    frequency = EFFECT_FREQUENCIES[frequency_of(uses)] if lifetime and uses > 1 else 0
    return level, galdor.bind_needs(level, lifetime=lifetime, frequency=frequency)


def bind(
    saga: Saga,
    character: Character,
    values: dict[str, Any],
    rng: random.Random | None = None,
) -> list[str]:
    """Roll the binding; an item that takes goes on the chapter's list."""
    rng = rng or random.Random()
    tradition = _tradition()
    rule = galdor.tradition_rule(tradition, "Galdor Enchantment")
    song = values.get("song") or ""
    aura = values.get("aura") or 0
    aura_realm = values.get("aura_realm") or realms.HERMETIC
    modifier = hc.aura_modifier(
        tradition,
        aura,
        aura_realm,
        hc.power_realm(
            character, tradition, rule, (song,), aura=aura, aura_realm=aura_realm
        ),
    )
    score = galdor.bind_score(
        character,
        song,
        values.get("craft") or "",
        bonuses=values.get("bonuses") or 0,
        aura=modifier,
    )
    level, needs = _needed(values)
    value, zeroes, die_text = _roll(
        saga, character, rule, song, level, aura, aura_realm, values.get("die"), rng
    )
    total = score + value
    name = values["name"]
    lines = [f"Binding {name}: {score}, {die_text}: {total} against {needs}."]
    if zeroes:
        lines.append("It botches.")
    elif total < needs:
        lines.append("The spirit isn't bound.")
    else:
        lifetime = _lifetime(values)
        character.tradition_effects.append(
            TraditionEffect(
                name=name,
                tradition=tradition.id,
                kind=galdor.BOUND_ITEM,
                rule=rule.name,
                uses=[song],
                level=level,
                parameters=values.get("duration") or galdor.DURATIONS[0],
                charges=0 if lifetime else 1,
                notes=(
                    f"From the deal with {values.get('deal') or 'a lord'}. "
                    + (
                        "Bound for his lifetime."
                        if lifetime
                        else f"One service, within {galdor.SERVICE_LIFE}."
                    )
                ),
            )
        )
        lines.append(
            f"The spirit is bound, magnitude {magnitude(level)}, once paid about "
            f"{plural(galdor.bind_vis(level), 'pawn')}."
        )
    return _write(saga, character, f"Bound: {name}", lines, zeroes, aura, rng)


def bind_form(saga: Saga, character: Character) -> Form:
    return Form(
        f"{BIND_TITLE}: {escape(character.name)}",
        lambda: bind_fields(saga, character),
        lambda values: bind(saga, character, values),
        validate=lambda values: bind_problem(character, values),
        save_label="Bind",
        help_id=BIND_HELP,
    )
