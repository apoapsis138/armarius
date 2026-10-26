"""The Byzantine customs' More actions on a character (The Sundered Eagle,
Culture & Customs and the Divine): a Hermetic letter, the Oath Invocation
roll, a season making Greek Fire, painting and venerating an icon, and a
mother's curse. Each is a form with a live inspector, rolled or kept on
saving -- no UI in here. The rules are rules.theban_customs'.

What is kept: an oath-breaker's malediction and a mother's curse are
Flaws on the cursed character's sheet, and both, an icon painted and a
batch of Greek Fire, are written in the Diary; an icon goes on its
church's Relics list (churches.Relic). A letter and a veneration's roll
are only reported."""

from __future__ import annotations

import random
from typing import Any

from . import catalog, churches, diaries, sourcebooks
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Neighbour, Saga, VirtueFlawInstance
from .rules import dice, harm
from .rules import theban_customs as tc
from .rules.lab import botch_conditions

HELP_ID = "theban-customs"
TSE = "TSE"


def in_play(saga: Saga) -> bool:
    """Whether The Sundered Eagle is among the saga's books."""
    return sourcebooks.in_play(TSE, sourcebooks.saga_books(saga))


def _number(value: Any) -> int:
    return int(value) if value is not None else 0


def _rng(rng: random.Random | None) -> random.Random:
    return rng or random.Random()


def _diary(saga: Saga, name: str, text: str, *who: Character) -> None:
    diaries.write(
        saga.current_year,
        saga.current_season,
        name,
        f"{text} Rules: {tc.SOURCE}.",
        characters=who,
    )


def _vf_name(vf_id: str, params: dict[str, str] | None = None) -> str:
    return catalog.describe_virtue_flaw(
        VirtueFlawInstance(vf_id, params or {}),
        catalog.load_virtue_flaw_catalog_by_id(),
    )


# -- a Hermetic letter (p. 44) --

LETTER = "Hermetic Letter"


def letter_fields(character: Character) -> list[DialogField]:
    held = tc.lores(character)
    return [
        DialogField(
            "mode",
            "The letter",
            "select",
            tc.COMPOSE,
            options=[(label, key) for key, label in tc.LETTER_MODES.items()],
            required=True,
        ),
        DialogField(
            "lore",
            "Lore",
            "select",
            held[0] if held else None,
            options=[(escape(name), name) for name in held],
            allow_blank=True,
            placeholder="(no Lore)",
            hint="A Lore the story draws on: the patron's legends, Greek myth, "
            "the recipient's covenant.",
        ),
        DialogField(
            "subtlety",
            "Subtler than plain, by",
            "optint",
            None,
            hint="Added to the Ease Factor of 6 for a more sophisticated "
            "or subtle message.",
        ),
    ]


def _letter_terms(character: Character, values: dict[str, Any]) -> tc.Letter:
    return tc.letter(
        character,
        str(values.get("mode") or tc.COMPOSE),
        str(values.get("lore") or ""),
        _number(values.get("subtlety")),
    )


def letter_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        found = _letter_terms(character, values)
        reading = values.get("mode") == tc.READ
        need = found.ease - found.total
        lines = [
            "[i]Discern the rhetorical purpose of a letter's tale.[/]"
            if reading
            else "[i]A day's work: a far-fetched tale of the patron, standing "
            "for the covenant and the letter's purpose.[/]",
            f"Simple die + [b]{found.total}[/] [dim]= {' '.join(found.terms)}[/]",
            f"Against [b]{found.ease}[/]: "
            + ("any die" if need <= 1 else f"a die of {need} or more")
            + " [dim](The Sundered Eagle p. 44)[/]",
        ]
        return "\n".join(lines)

    return live


def letter_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Hermetic Letter: composing a rhetorical letter, or reading
    one's purpose, as a roll; nothing is kept."""
    if character is None:
        return Refuse(LETTER, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        found = _letter_terms(character, values)
        die = dice.simple_die(_rng(rng))
        total = found.total + die
        reading = values.get("mode") == tc.READ
        if total >= found.ease:
            outcome = (
                "The tale's purpose is plain to him."
                if reading
                else "The message is well wrapped in its tale."
            )
        else:
            outcome = (
                "The tale's purpose escapes him."
                if reading
                else "The tale muddles the message."
            )
        return notes(
            f"Die {die} + {found.total} = {total} against {found.ease}.", outcome
        )

    return Form(
        f"{LETTER}: {escape(character.name)}",
        lambda: letter_fields(character),
        apply,
        live=letter_live(character),
        save_label="Roll",
        cancel_label="Close",
        help_id=HELP_ID,
        inspector="The Letter",
    )


# -- the Oath Invocation roll (p. 48) --

OATH = "Invoke a Broken Oath"


def oath_fields(saga: Saga, character: Character) -> list[DialogField]:
    def named(values: dict[str, Any]) -> bool:
        return bool(values.get("breaker"))

    return [
        DialogField(
            "breaker",
            "The oath-breaker",
            "select",
            None,
            options=[
                (escape(c.name), c.id) for c in saga.characters if c.id != character.id
            ],
            allow_blank=True,
            placeholder="(someone without a sheet)",
        ),
        DialogField(
            "styx",
            "Styx was named in the oath",
            "check",
            False,
            hint="+6 to the roll.",
        ),
        DialogField(
            "might",
            "The witnessing spirit's Might",
            "optint",
            None,
            hint="From 40 it may lay a Major Flaw; below, a Minor one.",
        ),
        DialogField(
            "curse",
            "Its punishment, if heard",
            "select",
            None,
            options=[
                (escape(_vf_name(vf_id)), vf_id)
                for vf_id in (*tc.MALEDICTIONS["Minor"], *tc.MALEDICTIONS["Major"])
            ],
            allow_blank=True,
            placeholder="(the storyguide decides)",
            hint="Laid on the oath-breaker's sheet if the spirit hears.",
            show_if=named,
        ),
    ]


def _oath_problem(values: dict[str, Any]) -> str | None:
    curse = values.get("curse")
    if curse and curse not in tc.maledictions(values.get("might")):
        return (
            f"A Major Flaw needs an entity of Might {tc.MAJOR_MIGHT} or more "
            "(The Sundered Eagle p. 48)."
        )
    if (values.get("might") or 0) < 0:
        return "A Might can't be below 0."
    return None


def oath_live(saga: Saga, character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        total, terms = tc.oath_total(character, bool(values.get("styx")))
        breaker = saga.character(values.get("breaker") or "")
        who = escape(breaker.name) if breaker is not None else "the oath-breaker"
        tier = tc.punishment_tier(values.get("might"))
        lines = [
            f"[i]{escape(character.name)} returns to where the oath was sworn and "
            f"declaims {who} an oath-breaker.[/]",
            f"Simple die + [b]{total}[/] [dim]= {' '.join(terms)}[/]",
            "Against [b]15 + a simple die[/]: heard, the spirit that witnessed "
            "it takes vengeance [dim](The Sundered Eagle p. 48)[/].",
            f"Its punishment: a [b]{tier}[/] Flaw, any General Flaw or a "
            "Malediction, for a time set by the oath's severity.",
            "[dim]A minor river spirit can't act beyond its own waters.[/]",
        ]
        problem = _oath_problem(values)
        if problem:
            lines.append(f"[$text-error]{problem}[/]")
        return "\n".join(lines)

    return live


def oath_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Invoke a Broken Oath, made by the injured party: the Oath
    Invocation roll, and if the spirit hears, the malediction chosen laid on
    the oath-breaker's sheet; both Diaries record it."""
    if character is None:
        return Refuse(OATH, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        styx = bool(values.get("styx"))
        rolled = tc.invoke_oath(character, styx, _rng(rng))
        breaker = saga.character(values.get("breaker") or "")
        who = breaker.name if breaker is not None else "the oath-breaker"
        lines = [
            f"Die {rolled.die} + {rolled.total} = {rolled.rolled} against 15 + "
            f"{rolled.ease_die} = {rolled.ease}."
        ]
        if not rolled.heard:
            lines.append("The spirit does not hear the complaint.")
        else:
            lines.append("The spirit that witnessed the oath hears the complaint.")
            curse = values.get("curse")
            if breaker is not None and curse:
                if all(vf.vf_id != curse for vf in breaker.virtues_flaws):
                    breaker.virtues_flaws.append(VirtueFlawInstance(curse))
                lines.append(f"{who} now bears {_vf_name(curse)}.")
            else:
                lines.append(
                    f"The storyguide decides {who}'s punishment: a "
                    f"{tc.punishment_tier(values.get('might'))} Flaw."
                )
        text = " ".join(lines)
        _diary(
            saga,
            f"{character.name} invoked an oath broken by {who}",
            text,
            *([character] + ([breaker] if breaker is not None else [])),
        )
        return notes(*map(escape, lines))

    return Form(
        f"{OATH}: {escape(character.name)}",
        lambda: oath_fields(saga, character),
        apply,
        validate=_oath_problem,
        live=oath_live(saga, character),
        save_label="Roll",
        help_id=HELP_ID,
        inspector="The Oath",
    )


# -- Greek Fire (p. 47) --

GREEK_FIRE = "Make Greek Fire"


def _safety(saga: Saga, character: Character) -> int:
    _aura, safety = botch_conditions(saga, character)
    return safety


def greek_fire_fields(saga: Saga, character: Character) -> list[DialogField]:
    return [
        DialogField(
            "doses",
            "Doses being made",
            "int",
            1,
            hint="A botch die for each: the more Greek Fire, the more danger.",
        ),
        DialogField(
            "safety",
            "The laboratory's Safety",
            "int",
            _safety(saga, character),
            hint="His own laboratory's, unless he works in another's "
            "workshop; it takes away botch dice.",
        ),
    ]


def _problem(values: dict[str, Any]) -> str | None:
    if _number(values.get("doses")) < 1:
        return "Make at least one dose."
    return None


def greek_fire_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        doses = max(1, _number(values.get("doses")))
        count = tc.greek_fire_botch_dice(
            character, doses, _number(values.get("safety"))
        )
        chance = dice.botch_chance(count) * 100
        init, attack, defense, damage, reach, strength, load, cost = tc.SIPHON
        leadership = next(
            (a.level for a in character.abilities if a.name == "Leadership"), 0
        )
        lines = [
            f"[i]A season's work on a reagent of level {tc.GREEK_FIRE_LEVEL} "
            "(Art & Academe p. 76).[/]",
            f"A stress die with [b]{count}[/] botch "
            f"{'die' if count == 1 else 'dice'}: it matters only if it botches, "
            f"and then the batch explodes ([b]{chance:.1f}%[/]) "
            "[dim](The Sundered Eagle p. 47)[/].",
            f"[dim]A master alchemist's workshop: he can lead {leadership} "
            "subordinates (his Leadership), each making two or more doses.[/]",
            f"[dim]The hand-held siphon (Profession: Naffatun): Init {init:+d}, "
            f"Atk {attack:+d}, Dfn {defense:+d}, Dam {damage:+d}, Range {reach}, "
            f"Str {strength:+d}, Load {load}, {cost}; a shield's Defense adds to "
            f"Soak instead; a dose is {tc.SPRAYS_PER_DOSE} sprays.[/]",
        ]
        return "\n".join(lines)

    return live


def greek_fire_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Make Greek Fire: the season's botch roll, written in the
    Diary."""
    if character is None:
        return Refuse(GREEK_FIRE, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        doses = _number(values.get("doses"))
        batch = tc.make_greek_fire(
            character, doses, _number(values.get("safety")), _rng(rng), saga=saga
        )
        noun = "dose" if doses == 1 else "doses"
        if batch.exploded:
            outcome = (
                f"The reagent explodes during its making ({batch.die.botches} "
                f"{'botch' if batch.die.botches == 1 else 'botches'}): the "
                "storyguide decides the harm."
            )
        else:
            outcome = f"The {doses} {noun} are made without mishap."
        lines = [
            f"Greek Fire, {doses} {noun}, {batch.botch_dice} botch "
            f"{'die' if batch.botch_dice == 1 else 'dice'}.",
            outcome,
        ]
        _diary(saga, "Made Greek Fire", " ".join(lines), character)
        return notes(*lines, f"Written in {escape(character.name)}'s Diary.")

    return Form(
        f"{GREEK_FIRE}: {escape(character.name)}",
        lambda: greek_fire_fields(saga, character),
        apply,
        validate=_problem,
        live=greek_fire_live(character),
        save_label="Roll",
        help_id=HELP_ID,
        inspector="The Batch",
    )


# -- painting an icon (pp. 133-134) --

PAINT = "Paint an Icon"


def church_list(saga: Saga) -> list[Neighbour]:
    return [n for n in saga.neighbours if n.kind == "church"]


def icon_fields(saga: Saga) -> list[DialogField]:
    listed = church_list(saga)
    return [
        DialogField("saint", "Depicting", "text", "", required=True),
        DialogField("of_christ", "An icon of Christ", "check", False),
        DialogField(
            "name",
            "The icon's name",
            "text",
            "",
            placeholder="blank: An icon of (whom it depicts)",
        ),
        DialogField(
            "church",
            "Kept at",
            "select",
            listed[0].id if listed else None,
            options=[(escape(n.name), n.id) for n in listed],
            required=True,
        ),
        DialogField(
            "standard",
            "Seasons of Standard decoration",
            "optint",
            None,
            hint="Gilding or bejewelling by a talented craftsman: +1 each.",
        ),
        DialogField(
            "excellent",
            "Excellent decoration results",
            "optint",
            None,
            hint="+3 each.",
        ),
        DialogField(
            "patron",
            "His patron saint",
            "check",
            False,
            hint="Adds his Pious trait.",
        ),
        DialogField(
            "other",
            "Other bonuses",
            "optint",
            None,
            hint="Art & Academe p. 124's: Inspirational or Free Expression "
            "+3, more time +1, overtime +1...",
        ),
    ]


def _icon(character: Character, values: dict[str, Any]) -> tc.Eikon:
    return tc.eikon(
        character,
        _number(values.get("standard")),
        _number(values.get("excellent")),
        bool(values.get("patron")),
        _number(values.get("other")),
    )


def _icon_problem(values: dict[str, Any]) -> str | None:
    if _number(values.get("standard")) < 0 or _number(values.get("excellent")) < 0:
        return "Decoration can't be below 0."
    return None


def icon_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        found = _icon(character, values)
        bonus = tc.invocation_bonus(found.quality)
        whom = "God's aid" if values.get("of_christ") else "its saint"
        lines = [
            "[i]A single painting (Art & Academe p. 117): an eikon, an aid to "
            "prayer, with no Divine Might.[/]",
            f"Aesthetic Quality [b]{found.quality}[/] [dim]= {' '.join(found.terms)}[/]",
            f"Venerated, it adds [b]+{bonus}[/] to invoking {whom} "
            "[dim](Aesthetic Quality / 5, The Sundered Eagle pp. 133-134)[/].",
            "[dim]Plan the painting as a season's Create a work of art.[/]",
        ]
        return "\n".join(lines)

    return live


def icon_form(saga: Saga, character: Character | None) -> Command:
    """More's Paint an Icon: an eikon's Aesthetic Quality, the icon kept
    on its church's Relics list and in the painter's Diary."""
    if character is None:
        return Refuse(PAINT, "Choose a character first.")
    problem = tc.icon_problem(character)
    if problem:
        return Refuse(PAINT, f"{escape(character.name)}: {problem}")
    if not church_list(saga):
        return Refuse(
            PAINT, "No church to keep the icon: add one as a neighbour first."
        )

    def apply(values: dict[str, Any]) -> list[str]:
        found = _icon(character, values)
        church = saga.neighbour(values.get("church"))
        if church is None:
            return notes("That church is gone.")
        saint = str(values.get("saint") or "").strip()
        name = str(values.get("name") or "").strip() or f"An icon of {saint}"
        relic: churches.Relic = {
            "name": name,
            "saint": saint,
            "kind": tc.EIKON,
            "quality": found.quality,
            "painter": character.name,
        }
        if values.get("of_christ"):
            relic["of_christ"] = True
        churches.relics(church).append(relic)
        bonus = tc.invocation_bonus(found.quality)
        line = (
            f"{name}, Aesthetic Quality {found.quality}, kept at {church.name}: "
            f"+{bonus} to invoking {saint} when venerated."
        )
        diaries.write(
            saga.current_year,
            saga.current_season,
            f"Painted {name}",
            f"{line} Rules: {tc.SOURCE}.",
            characters=[character],
        )
        return notes(escape(line), f"On {escape(church.name)}'s Relics.")

    return Form(
        f"{PAINT}: {escape(character.name)}",
        lambda: icon_fields(saga),
        apply,
        validate=_icon_problem,
        live=icon_live(character),
        save_label="Paint",
        help_id=HELP_ID,
        inspector="The Icon",
    )


# -- venerating an icon (p. 134) --

VENERATE = "Venerate an Icon"


def icon_choices(saga: Saga) -> list[tuple[str, str, churches.Relic]]:
    """Every eikon in the saga's churches: (label, "church id:row", it)."""
    found = []
    for church in church_list(saga):
        for row, relic in enumerate(churches.relics(church)):
            if churches.is_eikon(relic):
                found.append(
                    (f"{relic['name']} ({church.name})", f"{church.id}:{row}", relic)
                )
    return found


def _chosen(saga: Saga, value: Any) -> churches.Relic | None:
    return next((r for _, key, r in icon_choices(saga) if key == value), None)


def venerate_fields(saga: Saga) -> list[DialogField]:
    listed = icon_choices(saga)
    return [
        DialogField(
            "icon",
            "The icon",
            "select",
            listed[0][1] if listed else None,
            options=[(escape(label), key) for label, key, _ in listed],
            required=True,
        ),
        DialogField(
            "emergency",
            "In an emergency",
            "check",
            False,
            hint="A Fatigue level and Presence + Concentration against 15, in "
            "place of an hour's peaceful contemplation.",
        ),
    ]


def venerate_live(saga: Saga, character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        relic = _chosen(saga, values.get("icon"))
        if relic is None:
            return "[dim]Choose an icon.[/]"
        bonus = churches.eikon_bonus(relic)
        whom = (
            "God's aid"
            if relic.get("of_christ")
            else f"the intercession of {escape(relic.get('saint') or 'its saint')}"
        )
        lines = [
            f"[b]+{bonus}[/] to invoking {whom}: Communication + Charm + "
            "modifiers + a simple die against 15 + a simple die "
            "[dim](The Sundered Eagle pp. 133-136)[/].",
        ]
        if values.get("emergency"):
            total = tc.emergency_total(character)
            lines.append(
                f"In an emergency: stress die + [b]{total}[/] [dim]= Presence + "
                f"Concentration[/] against [b]{tc.EMERGENCY_EASE}[/], and a "
                "Fatigue level."
            )
        else:
            lines.append("[dim]An hour of peaceful contemplation.[/]")
        lines.append(
            "[dim]The saint's miracle comes when the saint decides, not "
            "necessarily at once.[/]"
        )
        return "\n".join(lines)

    return live


def venerate_form(
    saga: Saga, character: Character | None, rng: random.Random | None = None
) -> Command:
    """More's Venerate an Icon: the bonus to invoking its saint, and in an
    emergency the roll and the Fatigue level it costs."""
    if character is None:
        return Refuse(VENERATE, "Choose a character first.")
    if not icon_choices(saga):
        return Refuse(
            VENERATE, "No icons in the saga's churches: add one on a church's Relics."
        )

    def apply(values: dict[str, Any]) -> list[str]:
        relic = _chosen(saga, values.get("icon"))
        if relic is None:
            return notes("That icon is gone.")
        bonus = churches.eikon_bonus(relic)
        if not values.get("emergency"):
            return notes(
                f"After an hour's contemplation: +{bonus} to invoking "
                f"{escape(relic.get('saint') or 'its saint')}."
            )
        total = tc.emergency_total(character)
        roll = dice.Roll(
            total, dice.stress_die(_rng(rng), saga=saga), tc.EMERGENCY_EASE
        )
        already_out = harm.lose_fatigue(character, long_term=False)
        shown = "a botch" if roll.die.botched else str(roll.die.value)
        lines = [
            f"Die {shown} + {total} = {roll.total} against {tc.EMERGENCY_EASE}; "
            "a Fatigue level spent"
            + (" (already unconscious)." if already_out else "."),
            f"+{bonus} to invoking {relic.get('saint') or 'its saint'}."
            if roll.succeeded
            else "The veneration fails: no bonus.",
        ]
        return notes(*map(escape, lines))

    return Form(
        f"{VENERATE}: {escape(character.name)}",
        lambda: venerate_fields(saga),
        apply,
        live=venerate_live(saga, character),
        save_label="Venerate",
        help_id=HELP_ID,
        inspector="The Veneration",
    )


# -- a mother's curse (p. 136) --

CURSE = "A Mother's Curse"


def curse_fields() -> list[DialogField]:
    return [
        DialogField("mother", "His mother", "text", "", required=True),
        DialogField(
            "expertise",
            "Area of expertise",
            "select",
            tc.EXPERTISE[0],
            options=[(e.title(), e) for e in tc.EXPERTISE],
            required=True,
        ),
        DialogField(
            "task",
            "What lifts it",
            "text",
            "",
            required=True,
            placeholder="e.g. rescue his captured sister",
            hint="A curse needs a good reason; most demand he set a family "
            "matter right.",
        ),
    ]


def curse_live(character: Character) -> Any:
    def live(values: dict[str, Any]) -> str:
        area = str(values.get("expertise") or tc.EXPERTISE[0])
        task = escape(str(values.get("task") or "").strip()) or "the task she sets"
        lines = [
            f"[b]{escape(_vf_name(tc.MOTHERS_CURSE, {'expertise': area}))}[/], "
            f"on {escape(character.name)}'s sheet.",
            f"[b]{tc.CURSE_PENALTY}[/] to every {area} roll, until he "
            f"completes it: {task} [dim](The Sundered Eagle p. 136)[/].",
            "[dim]Only the task done, or divine intervention, lifts it; a "
            "saint may refuse.[/]",
        ]
        return "\n".join(lines)

    return live


def curse_form(saga: Saga, character: Character | None) -> Command:
    """More's A Mother's Curse: the Lesser Malediction on the child's
    sheet, and its task in his Diary."""
    if character is None:
        return Refuse(CURSE, "Choose a character first.")

    def apply(values: dict[str, Any]) -> list[str]:
        area = str(values.get("expertise") or tc.EXPERTISE[0])
        params = {"expertise": area}
        cursed = VirtueFlawInstance(tc.MOTHERS_CURSE, params)
        if cursed not in character.virtues_flaws:
            character.virtues_flaws.append(cursed)
        mother = str(values.get("mother") or "").strip()
        task = str(values.get("task") or "").strip()
        line = (
            f"{mother} cursed him: {tc.CURSE_PENALTY} to every {area} roll until "
            f"he completes his task: {task}."
        )
        _diary(saga, f"{mother}'s curse", line, character)
        return notes(
            escape(f"{character.name} now bears {_vf_name(tc.MOTHERS_CURSE, params)}."),
            escape(line),
        )

    return Form(
        f"{CURSE}: {escape(character.name)}",
        curse_fields,
        apply,
        live=curse_live(character),
        save_label="Curse",
        help_id=HELP_ID,
        inspector="The Curse",
    )
