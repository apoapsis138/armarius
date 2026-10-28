"""More's Dream Working and Hermetic Sacrifice: a dream traveler's rolls
(his spells in a dream, the dreamer noticing or reshaping it, a dream
wound's shock, a disturbance to the entranced body) and a sacrifice
standing in for a Ritual's vis, each written in the Diary -- no UI in
here. The rules and their pages are rules.tmre_dreams's (The Mysteries
Revised Edition pp. 102-117)."""

from __future__ import annotations

import random
from typing import Any

from .. import catalog, diaries
from .. import vis as vis_stores
from ..arts import ARTS, FORMS, TECHNIQUES
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import BULLET, escape
from ..models import REALMS, Character, KnownSpell, Saga, Spell
from ..rules import casting, dice
from ..rules import tmre_dreams as dr
from ..rules.breakdown import Breakdown

DREAM_TITLE = "Dream Working"
DREAM_HELP = "dream-working"
SACRIFICE_TITLE = "Hermetic Sacrifice"
SACRIFICE_HELP = "hermetic-sacrifice"

SPELL, AWARE, RESHAPE, WOUND, DISTURBED = (
    "spell",
    "aware",
    "reshape",
    "wound",
    "disturbed",
)
ROLLS: tuple[tuple[str, str], ...] = (
    ("A spell in the dream (Technique + Imaginem)", SPELL),
    ("The dreamer notices travelers (Per + Awareness)", AWARE),
    ("The dreamer reshapes the dream (Int + bonuses)", RESHAPE),
    ("A wound in the dream (Stamina, or he wakes)", WOUND),
    ("The entranced body is disturbed (Concentration)", DISTURBED),
)
SPONTANEOUS = "__spontaneous__"
TYPED_LEVEL = "__level__"


def _is(*what: str) -> Any:
    return lambda values: (values.get("roll") or SPELL) in what


def _int(values: dict[str, Any], key: str, default: int = 0) -> int:
    found = values.get(key)
    return found if isinstance(found, int) else default


def _terms(breakdown: Breakdown) -> str:
    return ", ".join(
        f"{escape(line.label)} {line.amount:+g}"
        for line in breakdown.lines
        if line.amount is not None
    )


# -- the die ------------------------------------------------------------------


def _die_fields() -> list[DialogField]:
    return [
        DialogField(
            "die",
            "Die",
            "optint",
            None,
            placeholder="(blank: the app rolls it)",
            hint="A stress die.",
        ),
        DialogField(
            "botched",
            "The die botched",
            "check",
            False,
            show_if=lambda v: v.get("die") is not None,
        ),
    ]


def _roll(
    saga: Saga, values: dict[str, Any], rng: random.Random, botch_dice: int = 1
) -> tuple[int, bool, str]:
    """The stress die: (its value, whether it botched, as shown)."""
    typed = values.get("die")
    if typed is not None:
        botched = bool(values.get("botched"))
        return int(typed), botched, "a botch" if botched else str(typed)
    found = dice.stress_die(rng, botch_dice, saga=saga)
    return found.value, found.botched, "a botch" if found.botched else str(found.value)


# -- Dream Working --------------------------------------------------------------


def _known(saga: Saga, magus: Character) -> list[tuple[KnownSpell, Spell]]:
    found = []
    for known in magus.spells_known:
        spell = catalog.find_spell(saga, known.spell_id)
        if spell is not None and spell.level is not None:
            found.append((known, spell))
    return found


def _chosen(
    saga: Saga, magus: Character, values: dict[str, Any]
) -> tuple[KnownSpell, Spell] | None:
    """The known spell chosen (None: a Spontaneous spell)."""
    key = values.get("spell") or SPONTANEOUS
    return next(((k, s) for k, s in _known(saga, magus) if k.spell_id == key), None)


def _dreamer(saga: Saga, character: Character, values: dict[str, Any]) -> Character:
    chosen = values.get("dreamer") or character.id
    return next((c for c in saga.characters if c.id == chosen), character)


def _earlier(values: dict[str, Any]) -> dr.DreamWounds:
    return dr.DreamWounds(
        light=_int(values, "earlier_light"),
        medium=_int(values, "earlier_medium"),
        heavy=_int(values, "earlier_heavy"),
    )


def dream_fields(saga: Saga, character: Character) -> list[DialogField]:
    """What Dream Working asks: the roll, and what that roll needs."""
    spells = [
        (f"{escape(s.name)} ({s.technique} {s.form} {s.level})", k.spell_id)
        for k, s in _known(saga, character)
    ]
    spells.append(("A Spontaneous spell", SPONTANEOUS))
    in_spell = _is(SPELL)

    def spontaneous(values: dict[str, Any]) -> bool:
        return in_spell(values) and _chosen(saga, character, values) is None

    people = [(escape(c.name), c.id) for c in saga.characters]
    return [
        DialogField(
            "roll",
            "Roll",
            "select",
            SPELL,
            options=list(ROLLS),
            required=True,
        ),
        DialogField(
            "spell",
            "Spell",
            "select",
            SPONTANEOUS,
            options=spells,
            required=True,
            show_if=in_spell,
            hint="Cast with his Technique and Imaginem, whatever its Form "
            "(TMRE p. 103).",
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            TECHNIQUES[0],
            options=pairs(TECHNIQUES),
            show_if=spontaneous,
        ),
        DialogField(
            "form",
            "The effect's Form",
            "select",
            "Imaginem",
            options=pairs(FORMS),
            show_if=spontaneous,
            hint="Its guidelines are that Form's; the score used is Imaginem.",
        ),
        DialogField(
            "aura_realm",
            "The dream setting's aura",
            "select",
            "Magic",
            options=pairs(REALMS),
            show_if=in_spell,
            hint="Whatever the setting is: a dream cathedral is Divine, a "
            "dream hell-pit Infernal (TMRE p. 103).",
        ),
        DialogField("aura", "Aura", "int", 0, show_if=in_spell),
        DialogField(
            "dream_wounds",
            "Dream wound penalty",
            "int",
            0,
            show_if=in_spell,
            hint="0 or less: the wounds taken in this dream (his real ones stay "
            "with the body).",
        ),
        DialogField(
            "split_parma",
            "Parma stretched over body and spirit (-3)",
            "check",
            False,
            show_if=in_spell,
        ),
        DialogField(
            "dreamer",
            "Dreamer",
            "select",
            character.id,
            options=people,
            required=True,
            show_if=_is(AWARE, RESHAPE),
        ),
        DialogField(
            "magus_power",
            "The dreamer is a magus (or of similar power) (+3)",
            "check",
            character.type == "magus",
            show_if=_is(RESHAPE),
        ),
        DialogField(
            "other_powers",
            "Other powers of illusion or dreams",
            "int",
            0,
            show_if=_is(RESHAPE),
            hint="+1 each, at most +3.",
        ),
        DialogField(
            "wound",
            "The new wound",
            "select",
            "light",
            options=[(w.title(), w) for w in dr.WOUNDS],
            show_if=_is(WOUND),
        ),
        DialogField(
            "earlier_light",
            "Earlier Light dream wounds",
            "int",
            0,
            show_if=_is(WOUND),
        ),
        DialogField(
            "earlier_medium",
            "Earlier Medium dream wounds",
            "int",
            0,
            show_if=_is(WOUND),
        ),
        DialogField(
            "earlier_heavy",
            "Earlier Heavy dream wounds",
            "int",
            0,
            show_if=_is(WOUND),
        ),
        DialogField(
            "modifiers",
            "Other modifiers",
            "int",
            0,
            show_if=_is(WOUND),
            hint="Others for pain or will the troupe allows.",
        ),
        DialogField(
            "disturbance",
            "Disturbance",
            "select",
            dr.DISTURBANCES[0][0],
            options=[(f"{name} ({ease})", name) for name, ease in dr.DISTURBANCES],
            show_if=_is(DISTURBED),
        ),
        *_die_fields(),
    ]


def _dream_validate(saga: Saga, character: Character) -> Any:
    def validate(values: dict[str, Any]) -> str | None:
        roll = values.get("roll") or SPELL
        if roll == SPELL:
            if not 0 <= _int(values, "aura") <= 10:
                return "An aura is 0 to 10."
            if _int(values, "dream_wounds") > 0:
                return "A wound penalty is 0 or less."
        if roll == RESHAPE and not 0 <= _int(values, "other_powers") <= 10:
            return "Other powers: 0 or more (at most 3 count)."
        if roll == WOUND and any(
            _int(values, key) < 0
            for key in ("earlier_light", "earlier_medium", "earlier_heavy")
        ):
            return "Earlier wounds can't be below 0."
        die = values.get("die")
        if die is not None and int(die) < 0:
            return "A die can't be below 0."
        return None

    return validate


def _spell_score(
    saga: Saga, character: Character, values: dict[str, Any]
) -> tuple[Breakdown, str, int | None, bool]:
    """The traveler's Casting Score for the spell chosen: (the score, what
    it is, its level or None, whether it is Spontaneous)."""
    chosen = _chosen(saga, character, values)
    common: dict[str, Any] = {
        "aura": _int(values, "aura"),
        "aura_realm": str(values.get("aura_realm") or "Magic"),
        "dream_wounds": _int(values, "dream_wounds"),
    }
    if chosen is None:
        technique = str(values.get("technique") or TECHNIQUES[0])
        form = str(values.get("form") or dr.DREAM_FORM)
        score = dr.spirit_casting_score(
            character, technique, form, spontaneous=True, **common
        )
        return score, f"a Spontaneous {technique} {form} effect", None, True
    known, spell = chosen
    score = dr.spirit_casting_score(
        character,
        spell.technique,
        spell.form,
        mastery=known.mastery_score,
        ritual=spell.ritual,
        **common,
    )
    return score, f"{spell.name} ({spell.level})", spell.level, False


def dream_lines(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """The inspector's lines for the roll chosen."""
    roll = values.get("roll") or SPELL
    name = escape(character.name)
    if roll == SPELL:
        score, what, level, spontaneous = _spell_score(saga, character, values)
        resistance = dr.spirit_resistance(
            character,
            aura=_int(values, "aura"),
            aura_realm=str(values.get("aura_realm") or "Magic"),
            split_parma=bool(values.get("split_parma")),
        )
        if spontaneous:
            how = (
                "(score + stress die) / 2, and a spirit loses no Fatigue for it "
                "[dim](TMRE p. 106)[/]"
            )
        else:
            how = f"score + stress die against level [b]{level}[/]"
        return [
            f"[b]{name}[/] casts {escape(what)} in the dream as Imaginem.",
            f"Casting Score [b]{int(score.total)}[/] ({_terms(score)}); {how}.",
            f"His Magic Resistance in the dream [b]{int(resistance.total)}[/] "
            f"({_terms(resistance)}) [dim](TMRE p. 103)[/]",
            escape(dr.body_note(bool(values.get("split_parma")))),
            "A botch gains real Warping Points; Twilight is real, timed in the "
            "waking world [dim](TMRE p. 106)[/].",
        ]
    if roll in (AWARE, RESHAPE):
        dreamer = _dreamer(saga, character, values)
        if roll == AWARE:
            base = dr.awareness_base(dreamer)
            return [
                f"[b]{escape(dreamer.name)}[/] notices the travelers on a stress "
                f"die + [b]{int(base.total)}[/] ({_terms(base)}) against "
                f"[b]{dr.AWARE_EASE}[/] [dim](TMRE p. 105)[/]",
                "Unaware, a dreamer near the travelers may still change the dream "
                "unconsciously (the storyguide's).",
            ]
        base = dr.reshape_base(
            dreamer,
            magus=bool(values.get("magus_power")),
            other_powers=_int(values, "other_powers"),
        )
        return [
            f"[b]{escape(dreamer.name)}[/] reshapes the dream on a stress die + "
            f"[b]{int(base.total)}[/] ({_terms(base)}) against "
            f"[b]{dr.RESHAPE_EASE}[/] [dim](TMRE p. 105)[/]",
            "Success reshapes it at will; the rolled total is the change's "
            "magnitude, as a dream spell. Travelers with Magic Resistance "
            "resist, but find the landscape changed.",
        ]
    if roll == WOUND:
        earlier = _earlier(values)
        wound = str(values.get("wound") or "light")
        base = dr.shock_base(character, earlier, _int(values, "modifiers"))
        ease = dr.shock_ease(character, earlier.add(wound))
        return [
            f"[b]{name}[/] stays in the dream on a stress die + "
            f"[b]{int(base.total)}[/] ({_terms(base)}) against [b]{ease}[/], "
            "the total Wound Penalty [dim](TMRE p. 106)[/]",
            "Failing, he wakes from the shock; the wounds aren't real, and heal "
            "once enough dream time passes. An Incapacitating wound leaves him "
            "Incapacitated even if he stays.",
        ]
    disturbance = str(values.get("disturbance") or dr.DISTURBANCES[0][0])
    base = dr.disturbance_base(character)
    return [
        f"[b]{name}[/] stays in the trance on a stress die + [b]{base}[/] "
        "(Stamina + Concentration, the body's wounds three times) against "
        f"[b]{dr.disturbance_ease(disturbance)}[/] [dim](TMRE p. 102; DE p. 215)[/]",
        "Failing, he wakes and is pulled out of the dream.",
    ]


def dream_live(saga: Saga, character: Character) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        return "\n".join(dream_lines(saga, character, values))

    return inspect


#: A rolled die: (its value, whether it botched, as shown).
Die = tuple[int, bool, str]


def _cast(
    saga: Saga, character: Character, values: dict[str, Any], rolled: Die
) -> tuple[str, list[str]]:
    die, botched, shown = rolled
    score, what, level, spontaneous = _spell_score(saga, character, values)
    if botched:
        outcome = (
            "A botch: a nightmare in that part of the dream; roll the botch "
            "dice for real Warping Points and Twilight."
        )
    elif spontaneous:
        total = casting.spontaneous_total(score, die)
        outcome = f"Casting Total {total} (no Fatigue lost in a dream)."
    else:
        total = casting.casting_total(score, die)
        short = (level or 0) - total
        outcome = (
            f"Casting Total {total}: cast."
            if short <= 0
            else f"Casting Total {total}: {short} short of the level."
        )
    return f"Dream: {what}", [
        f"{character.name} casts {what} in a dream. Die {shown}.",
        outcome,
    ]


def _dreams(
    saga: Saga, character: Character, values: dict[str, Any], rolled: Die
) -> tuple[str, list[str]]:
    die, botched, shown = rolled
    dreamer = _dreamer(saga, character, values)
    reshaping = (values.get("roll") or SPELL) == RESHAPE
    if not reshaping:
        base = int(dr.awareness_base(dreamer).total)
        ease, name = dr.AWARE_EASE, f"Dream: {dreamer.name} watches"
        won, lost = "notices the travelers", "doesn't notice the travelers"
    else:
        base = int(
            dr.reshape_base(
                dreamer,
                magus=bool(values.get("magus_power")),
                other_powers=_int(values, "other_powers"),
            ).total
        )
        ease, name = dr.RESHAPE_EASE, f"Dream: {dreamer.name} reshapes it"
        won, lost = "reshapes the dream", "can't take hold of the dream"
    total = base + die
    if botched:
        outcome = f"A botch: {dreamer.name} {lost}."
    elif total >= ease:
        outcome = f"{total} against {ease}: {dreamer.name} {won}."
        if reshaping:
            outcome += f" The change's magnitude: {dr.reshape_magnitude(total)}."
    else:
        outcome = f"{total} against {ease}: {dreamer.name} {lost}."
    return name, [f"{dreamer.name} dreams. Die {shown}.", outcome]


def _stays(total: int, ease: int, botched: bool, woken: str) -> str:
    if not botched and total >= ease:
        return f"{total} against {ease}: he stays in the dream."
    return f"{'A botch' if botched else total} against {ease}: {woken}"


def _wounded(
    character: Character, values: dict[str, Any], rolled: Die
) -> tuple[str, list[str]]:
    die, botched, shown = rolled
    earlier = _earlier(values)
    wound = str(values.get("wound") or "light")
    base = int(dr.shock_base(character, earlier, _int(values, "modifiers")).total)
    ease = dr.shock_ease(character, earlier.add(wound))
    return f"Dream: a {wound} wound", [
        f"{character.name} takes a {wound} wound in a dream. Die {shown}.",
        _stays(base + die, ease, botched, "the shock wakes him; it was only a dream."),
    ]


def _disturbed(
    character: Character, values: dict[str, Any], rolled: Die
) -> tuple[str, list[str]]:
    die, botched, shown = rolled
    disturbance = str(values.get("disturbance") or dr.DISTURBANCES[0][0])
    ease = dr.disturbance_ease(disturbance)
    total = dr.disturbance_base(character) + die
    return f"Dream: {disturbance.lower()}", [
        f"{character.name}'s body: {disturbance.lower()}. Die {shown}.",
        _stays(total, ease, botched, "he wakes, pulled out of the dream."),
    ]


def apply_dream(
    saga: Saga, character: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    roll = values.get("roll") or SPELL
    rolled = _roll(saga, values, rng)
    if roll == SPELL:
        name, lines = _cast(saga, character, values, rolled)
    elif roll in (AWARE, RESHAPE):
        name, lines = _dreams(saga, character, values, rolled)
    elif roll == WOUND:
        name, lines = _wounded(character, values, rolled)
    else:
        name, lines = _disturbed(character, values, rolled)
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        " ".join([*lines, f"Rules: {dr.SOURCE}."]),
        characters=[character],
    )
    return notes(*map(escape, lines), f"Written in {escape(character.name)}'s Diary.")


def offers_dreams(saga: Saga, character: Character) -> bool:
    """Dream Working: a magus who knows Dream Magic."""
    return dr.dream_traveler(character)


def dream_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    if character is None:
        return Refuse(DREAM_TITLE, "Choose a character first.")
    if not offers_dreams(saga, character):
        return Refuse(
            DREAM_TITLE,
            f"{escape(character.name)} doesn't know Dream Magic (TMRE p. 102).",
        )
    return Form(
        f"{DREAM_TITLE}: {escape(character.name)}",
        lambda: dream_fields(saga, character),
        lambda values: apply_dream(saga, character, values, rng or random.Random()),
        validate=_dream_validate(saga, character),
        live=dream_live(saga, character),
        save_label="Roll",
        help_id=DREAM_HELP,
        inspector="The Dream",
    )


# -- Hermetic Sacrifice -------------------------------------------------------------


def _rituals(saga: Saga, magus: Character) -> list[tuple[KnownSpell, Spell]]:
    return [(k, s) for k, s in _known(saga, magus) if s.ritual]


def _level(saga: Saga, magus: Character, values: dict[str, Any]) -> int | None:
    key = values.get("spell") or TYPED_LEVEL
    for known, spell in _rituals(saga, magus):
        if known.spell_id == key:
            return spell.level
    typed = values.get("level")
    return typed if isinstance(typed, int) else None


def sacrifice_fields(saga: Saga, magus: Character) -> list[DialogField]:
    rituals = [
        (f"{escape(s.name)} ({s.technique} {s.form} {s.level})", k.spell_id)
        for k, s in _rituals(saga, magus)
    ]
    rituals.append(("Another Ritual (type its level)", TYPED_LEVEL))
    examples = ", ".join(f"{beast} {worth}" for beast, worth in dr.BEAST_EXAMPLES)
    return [
        DialogField(
            "spell",
            "Ritual",
            "select",
            rituals[0][1],
            options=rituals,
            required=True,
            hint="A Ritual that summons the altar's deity, cast via the altar.",
        ),
        DialogField(
            "level",
            "Its level",
            "optint",
            None,
            show_if=lambda v: (v.get("spell") or TYPED_LEVEL) == TYPED_LEVEL,
        ),
        DialogField("deity", "The altar's deity", "text", ""),
        DialogField("beast", "The beast sacrificed", "text", ""),
        DialogField(
            "worth",
            "Pawns it stands in for",
            "int",
            dr.LEAST_WORTH,
            hint=f"{dr.LEAST_WORTH} to {dr.MOST_WORTH}: the rarer and nobler, the "
            f"more ({examples}) (TMRE p. 117).",
        ),
        DialogField("pure", "Pure and unblemished", "check", True),
        DialogField("made_by_magic", "Created or altered by magic", "check", False),
        DialogField(
            "pay_from",
            "Pay the vis still needed from",
            "select",
            vis_stores.CHARACTER,
            options=[*vis_stores.PLACES, ("Not now (pay it by hand)", NOT_NOW)],
            hint="The rest of the Ritual's vis, of its Technique or Form.",
        ),
        DialogField(
            "pay_art",
            "Of",
            "select",
            None,
            options=pairs(ARTS),
            allow_blank=True,
            placeholder="(the Ritual's Technique)",
            show_if=lambda v: _paying(v) != "",
        ),
    ]


def _sacrifice_validate(saga: Saga, magus: Character) -> Any:
    def validate(values: dict[str, Any]) -> str | None:
        level = _level(saga, magus, values)
        if level is None or level < 1:
            return "Give the Ritual's level."
        if not str(values.get("deity") or "").strip():
            return "Name the altar's deity."
        if not str(values.get("beast") or "").strip():
            return "Name the beast sacrificed."
        short = _short_of_vis(saga, magus, values)
        if short:
            return short
        return (
            dr.sacrifice_problem(
                magus,
                _int(values, "worth"),
                pure=bool(values.get("pure")),
                made_by_magic=bool(values.get("made_by_magic")),
            )
            or None
        )

    return validate


def _pay_art(saga: Saga, magus: Character, values: dict[str, Any]) -> str:
    """The Art the rest of the vis is paid in: the one chosen, else the
    Ritual's Technique (Vim for a typed Ritual)."""
    chosen = values.get("pay_art")
    if chosen:
        return str(chosen)
    for known, spell in _rituals(saga, magus):
        if known.spell_id == values.get("spell"):
            return spell.technique
    return "Vim"


#: Hermetic Sacrifice's "pay the rest by hand".
NOT_NOW = "not_now"


def _paying(values: dict[str, Any]) -> str:
    """Where the rest of the Ritual's vis comes from ("" for by hand)."""
    where = str(values.get("pay_from") or "")
    return "" if where == NOT_NOW else where


def _short_of_vis(saga: Saga, magus: Character, values: dict[str, Any]) -> str:
    where = _paying(values)
    vis = _vis(saga, magus, values)
    if not where or vis is None or int(vis.total) <= 0:
        return ""
    art = _pay_art(saga, magus, values)
    held = vis_stores.pool_of(saga, magus, where).get(art.lower(), 0)
    if held < int(vis.total):
        return f"The Ritual still needs {int(vis.total)} pawn(s) of {art}; there are {held}."
    return ""


def _vis(saga: Saga, magus: Character, values: dict[str, Any]) -> Breakdown | None:
    level = _level(saga, magus, values)
    if level is None or level < 1:
        return None
    problem = dr.sacrifice_problem(
        magus,
        _int(values, "worth"),
        pure=bool(values.get("pure")),
        made_by_magic=bool(values.get("made_by_magic")),
    )
    worth = () if problem else (_int(values, "worth"),)
    return dr.ritual_vis_breakdown(magus, level, worth)


def sacrifice_lines(saga: Saga, magus: Character, values: dict[str, Any]) -> list[str]:
    vis = _vis(saga, magus, values)
    lines = [f"[b]{escape(magus.name)}[/]  [$label]Hermetic Sacrifice[/]"]
    if vis is None:
        level = _level(saga, magus, values)
        lines.append(
            "Rigid Magic: no vis in casting, so no Ritual."
            if level
            else "Give the Ritual's level."
        )
        return lines
    lines.append(
        f"Vis the Ritual still needs: [b]{int(vis.total)}[/] ({_terms(vis)}) "
        "[dim](TMRE p. 117)[/]"
    )
    problem = dr.sacrifice_problem(
        magus,
        _int(values, "worth"),
        pure=bool(values.get("pure")),
        made_by_magic=bool(values.get("made_by_magic")),
    )
    if problem:
        lines.append(f"{BULLET} {escape(problem)}")
    lines.append(
        f"{BULLET} The deity must find it pleasing, and cooperate: forcing the "
        "spirit with Hermetic Synthemata spoils the altar [dim](Errata p. 51)[/]."
    )
    return lines


def sacrifice_live(saga: Saga, magus: Character) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        return "\n".join(sacrifice_lines(saga, magus, values))

    return inspect


def apply_sacrifice(saga: Saga, magus: Character, values: dict[str, Any]) -> list[str]:
    deity = str(values.get("deity") or "").strip()
    beast = str(values.get("beast") or "").strip()
    level = _level(saga, magus, values) or 0
    vis = _vis(saga, magus, values)
    left = int(vis.total) if vis is not None else 0
    worth = _int(values, "worth")
    lines = [
        f"{beast} sacrificed on the altar of {deity}, standing in for {worth} "
        f"pawn(s) of vis.",
        f"The level {level} Ritual still needs {left} pawn(s) of vis.",
    ]
    where = _paying(values)
    if where and left > 0:
        art = _pay_art(saga, magus, values)
        vis_stores.pay(vis_stores.pool_of(saga, magus, where), {art: left})
        named = {v: k for k, v in vis_stores.PLACES}[where].lower()
        lines.append(f"{left} pawn(s) of {art} paid from {named}.")
    diaries.write(
        saga.current_year,
        saga.current_season,
        f"Sacrifice to {deity}",
        " ".join([*lines, f"Rules: {dr.SACRIFICE_SOURCE}."]),
        characters=[magus],
    )
    return notes(*map(escape, lines), f"Written in {escape(magus.name)}'s Diary.")


def offers_sacrifice(saga: Saga, character: Character) -> bool:
    return dr.sacrifices(character)


def sacrifice_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(SACRIFICE_TITLE, "Choose a character first.")
    if not offers_sacrifice(saga, character):
        return Refuse(
            SACRIFICE_TITLE,
            f"{escape(character.name)} doesn't know Hermetic Sacrifice (TMRE p. 117).",
        )
    return Form(
        f"{SACRIFICE_TITLE}: {escape(character.name)}",
        lambda: sacrifice_fields(saga, character),
        lambda values: apply_sacrifice(saga, character, values),
        validate=_sacrifice_validate(saga, character),
        live=sacrifice_live(saga, character),
        save_label="Sacrifice",
        help_id=SACRIFICE_HELP,
        inspector="The Altar",
    )
