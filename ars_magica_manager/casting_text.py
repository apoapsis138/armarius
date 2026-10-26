"""The Hermetic Magic tab's casting text: the magus's Casting
Score for every Technique + Form pair, and a known spell's Casting Score
and what the die must reach. Like the other domain modules it returns
markup. Casting is worked out in the aura of the magus's covenant, with
firm words and bold gestures (the book's defaults). A hybrid magus's
styles (Holy or Chthonic Magic, Goetic Arts, Hermetic rites) close it."""

from __future__ import annotations

from . import spells as spl
from . import vis as vis_stores
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .markup import escape, problem
from .models import Character, KnownSpell, Saga, Spell
from .rules import (
    casting,
    casting_virtues,
    certamen,
    craft_magic,
    house_mastery,
    penetration,
)
from .rules import hybrid_magic as hybrid
from .rules import lab as lab_rules
from .rules.realms import home_aura, home_in_regio


def _levels(count: int) -> str:
    """ "a Fatigue level", "2 Fatigue levels", "no Fatigue"."""
    if count <= 0:
        return "no Fatigue"
    return "a Fatigue level" if count == 1 else f"{count} Fatigue levels"


def casting_virtue_lines(magus: Character) -> list[str]:
    """Lines (markup) for the Virtues and Flaws that change a cast beyond
    the Casting Score: Diedne Magic's Spontaneous division, and those that
    count only when their circumstance holds."""
    lines: list[str] = []
    if casting_virtues.diedne_spontaneous(magus):
        lines.append(
            "Diedne Magic: without Fatigue, (score + stress die) / 2 may be "
            "chosen instead of / 5; with Fatigue, the lower Art counts twice."
        )
    reminders = casting_virtues.reminders(magus)
    if reminders:
        lines.append("When they apply: " + " ".join(escape(r) for r in reminders))
    return lines


def casting_scores_text(saga: Saga, magus: Character) -> str:
    aura, realm = home_aura(saga, magus)
    header = " " * 12 + "".join(f"{ART_ABBREVIATIONS[f]:>5}" for f in FORMS)
    rows = [header]
    sample = None
    for technique in TECHNIQUES:
        cells = []
        for form in FORMS:
            score = casting.casting_score(
                magus, technique, form, aura=aura, aura_realm=realm
            )
            sample = sample or score
            cells.append(f"{int(score.total):>5}")
        rows.append(f"{technique:<12}" + "".join(cells))
    assert sample is not None
    shared = [
        f"{escape(line.label)} {line.amount:+g}"
        for line in sample.lines[2:]
        if line.amount is not None
    ]
    lines = [
        *rows,
        "",
        "Every score adds: " + ", ".join(shared) + " (firm words, bold gestures).",
        "Formulaic: score + die >= level casts it; up to 10 short costs "
        + _levels(casting.fatigue_levels(1, magus.virtues_flaws, "formulaic"))
        + ".",
        "Spontaneous: score / 5 without Fatigue; (score + stress die) / 2 for "
        + _levels(casting.fatigue_levels(1, magus.virtues_flaws, "spontaneous"))
        + ".",
    ]
    lines += _spontaneous_lines(magus, aura, realm)
    lines += option_lines(saga, magus)
    lines += casting_virtue_lines(magus)
    resistances = [
        f"{ART_ABBREVIATIONS[form]} "
        + str(
            int(
                penetration.magic_resistance(
                    magus, form, aura=aura, aura_realm=realm
                ).total
            )
        )
        for form in FORMS
    ]
    parma = sum(lab_rules.ability_score(magus, "Parma Magica"))
    lines.append(
        f"Magic Resistance (Form + Parma {parma} x 5 + aura): " + ", ".join(resistances)
    )
    bonus = int(penetration.penetration_bonus(magus).total)
    weak = penetration.penetration_halved_by(magus.virtues_flaws)
    lines.append(
        f"Penetration: Casting Total - spell level {bonus:+d} (Penetration), "
        "multiplied by Arcane Connections"
        + (f", then halved ({escape(', '.join(weak))})" if weak else "")
        + "."
    )
    duel = certamen.certamen_totals(magus, TECHNIQUES[0], FORMS[0])
    c = magus.characteristics
    lines.append(
        f"Certamen: Initiative {duel.initiative:+d}, Attack Presence {c.presence:+d} "
        f"+ Art, Defence Perception {c.perception:+d} + the other Art, Weakening "
        f"{duel.weakening_base:+d} + advantage, Resistance {duel.resistance:+d}."
        + (
            " Tremere Focus: the lower of the two Arts counts double."
            if certamen.certamen_focus(magus)
            else ""
        )
    )
    school = certamen.school_text(magus)
    if school:
        lines.append(escape(school))
    multipliers = [line for line in sample.lines if line.multiplier is not None]
    halved = sorted({line.label for line in multipliers})
    if halved:
        lines.append(f"Halved totals for: {escape(', '.join(halved))}.")
    lines += [escape(line) for line in hybrid.summary(magus)]
    return "\n".join(lines)


def _spontaneous_lines(magus: Character, aura: int, realm: str) -> list[str]:
    """The Spontaneous levels without Fatigue, Technique by Technique,
    when they aren't the Formulaic grid's / 5: a Virtue that counts only
    for Formulaic spells (Method Caster, Poor Formulaic Magic, Unstructured
    Caster), one that changes the Spontaneous score (Ceremonial
    Spontaneous Magic) or its division (Weak and Difficult Spontaneous
    Magic, Diedne Magic), or a Deficiency, which halves the total (DE pp.
    76, 98, 122, 125, 126, 141, 149, 153, 214)."""
    rows: list[str] = []
    mode = casting.spontaneous_mode(magus)
    differs = mode != casting.NORMAL
    for technique in TECHNIQUES:
        cells = []
        for form in FORMS:
            formulaic = casting.casting_score(
                magus, technique, form, aura=aura, aura_realm=realm
            )
            own = casting.casting_score(
                magus, technique, form, aura=aura, aura_realm=realm, spontaneous=True
            )
            level = casting.non_fatiguing_level(magus, own)
            differs = differs or level != int(formulaic.total) // 5
            cells.append(f"{'-' if level is None else level:>5}")
        rows.append(f"{technique:<12}" + "".join(cells))
    if not differs:
        return []
    return ["", SPONTANEOUS_HEADINGS[mode], *rows]


#: The second grid's heading, by how the magus casts Spontaneous spells.
SPONTANEOUS_HEADINGS = {
    casting.NORMAL: "Spontaneous levels without Fatigue (own score / 5):",
    casting.WEAK: "Spontaneous levels (Weak Spontaneous Magic: always score / 5, "
    "never exerting; DE p. 153):",
    casting.DIFFICULT: "Spontaneous magic only exerting (Difficult Spontaneous "
    "Magic, DE p. 126): (score + stress die) / 2, a Fatigue level:",
    casting.NO_SPONTANEOUS: "No Spontaneous magic (Weak and Difficult "
    "Spontaneous Magic together):",
    casting.DIEDNE: "Spontaneous levels without Fatigue (Diedne Magic: score / 2 "
    "+ a stress die / 2, or score / 5; exerting, the lowest Art doubled; DE p. 76):",
}


def option_lines(saga: Saga, magus: Character) -> list[str]:
    """The spellcasting options' figures for this magus: fast and
    ceremonial casting, Concentration, aiming and a talisman (DE pp.
    215-218, 223, 260)."""
    lines = [
        f"Fast casting (Spontaneous): speed Quickness + Finesse "
        f"{casting.fast_casting_speed(magus):+d} + stress die against the foe's "
        f"Initiative, -6 for each spell after the first; score "
        f"{casting.FAST_PENALTY}, +{casting.FAST_BOTCH_DICE} botch dice, no vis. "
        "To know an attacking spell's Form: Perception + Awareness + die "
        "against 15 - its magnitude (DE p. 217).",
    ]
    if casting.can_ceremonial(magus):
        learned = sum(lab_rules.ability_score(magus, "Artes Liberales")) + sum(
            lab_rules.ability_score(magus, "Philosophiae")
        )
        lines.append(
            f"Ceremonial casting (Spontaneous): + Artes Liberales + Philosophiae "
            f"{learned:+d} and props +1 to +5, in place of words and gestures; "
            "15 minutes a magnitude (3 in a laboratory), and no more magnitudes "
            "than quarter-hours spent."
        )
    lines.append(
        f"Concentration: Stamina + Concentration {casting.concentration_base(magus):+d}"
        " + stress die; a failure ends the spell and adds a botch die. "
        f"Aiming: Perception + Finesse {casting.aiming_base(magus):+d} + die, +6 "
        "for each size step past a basic Individual."
    )
    lines.append(escape(craft_magic.summary_line(magus)))
    attuned = casting.talisman_attunements(saga, magus)
    if attuned:
        lines.append(
            "Talisman, while touching it (the best that applies): "
            + ", ".join(f"+{bonus} {escape(what)}" for bonus, what in attuned)
            + "."
        )
    return lines


#: What a reader needs to cast from a Casting Tablet (DE: an apprentice
#: whose Arts are opened can, with these).
TABLET_ARTES_LIBERALES, TABLET_LATIN = 1, 4


def tablet_casting_line(saga: Saga, magus: Character, spell: Spell) -> str:
    """One magus casting a Casting Tablet's spell (markup): the Casting
    Total before the stress die and what each die gives, by DE's table."""
    from .rules.book_seasons import language_score
    from .rules.scores import ability_level

    name = escape(magus.name)
    if (
        ability_level(magus, "Artes Liberales") < TABLET_ARTES_LIBERALES
        or language_score(magus, "Latin") < TABLET_LATIN
    ):
        return (
            f"{name}: can't read it (needs Artes Liberales "
            f"{TABLET_ARTES_LIBERALES} and Latin {TABLET_LATIN})"
        )
    aura, realm = home_aura(saga, magus)
    score = int(
        casting.tablet_casting_score(magus, spell, aura=aura, aura_realm=realm).total
    )
    level = spell.level or 0
    steps = []
    for floor, fatigue, warping in casting.TABLET_BANDS:
        need = level + floor - score
        text = f"{max(need, 0)}+ {fatigue} Fatigue"
        if warping:
            text += f" and {warping} Warping"
        steps.append(text)
        if need <= 0:
            break
    else:
        points = casting.magnitude(level)
        steps.append(f"less: not cast, {points} Warping, 5 Fatigue")
    kind = "long-term" if spell.ritual else "short-term"
    return f"{name}: {score} + stress die; " + ", ".join(steps) + f" ({kind})"


def known_spell_casting_lines(
    saga: Saga, magus: Character, known: KnownSpell, spell: Spell
) -> list[str]:
    """The details panel's casting lines for a known spell."""
    aura, realm = home_aura(saga, magus)
    abilities = casting.mastery_counts(known.mastery_abilities)
    score = casting.spell_casting_score(
        magus,
        spell,
        aura=aura,
        aura_realm=realm,
        mastery=known.mastery_score,
        mastery_abilities=abilities,
    )
    total = int(score.total)
    terms = ", ".join(
        f"{escape(line.label)} {line.amount:+g}"
        for line in score.lines
        if line.amount is not None
    )
    lines = [f"[b]Casting Score:[/] {total} ({terms})"]
    if casting_virtues.incompatible(
        magus, spell.technique, spell.form, tuple(spell.requisites)
    ):
        lines.append(
            problem("Incompatible Arts: these Arts can't be used together (DE p. 134).")
        )
        return lines
    if spell.level is None:
        return lines
    vis = spl.vis_cost(spell) or 0
    if spell.ritual:
        pawns = casting_virtues.ritual_vis(magus, vis)
        if pawns is None:
            lines.append("Rigid Magic: no vis in casting, so no Ritual.")
            return lines
        vis = pawns
    botch = casting.botch_dice(
        vis_pawns=vis,
        aura_realm=realm,
        aura=aura,
        in_regio=home_in_regio(saga, magus),
        mastery=known.mastery_score,
        golden_cord=casting.golden_cord(saga, magus),
        virtues_flaws=magus.virtues_flaws,
        magus=magus,
    )
    calm = " (none when calm)" if known.mastery_score else ""
    need = spell.level - total
    if spell.ritual:
        # Cast while up to 10 short: 1, 2 or 3 levels as the total falls.
        steps = []
        for slack, levels in ((0, 1), (5, 2), (10, 3)):
            cost = casting.fatigue_levels(levels, magus.virtues_flaws, "ritual")
            steps.append(f"{max(need - slack, 0)}+ for {cost}")
            if need - slack <= 0:
                break
        lines.append(
            "Ritual, stress die: "
            + ", ".join(steps)
            + f" long-term Fatigue levels; {vis} pawn(s) of vis; {botch} botch "
            + ("die" if botch == 1 else "dice")
            + f"{calm}. Fatigue past unconsciousness becomes a wound."
        )
        tainted = vis_stores.infernal_stores(saga, magus, (spell.technique, spell.form))
        if tainted and vis:
            text = casting.infernal_vis_text(
                saga,
                vis,
                aura_realm=realm,
                aura=aura,
                in_regio=home_in_regio(saga, magus),
                mastery=known.mastery_score,
                golden_cord=casting.golden_cord(saga, magus),
                virtues_flaws=magus.virtues_flaws,
                magus=magus,
            )
            lines.append(
                problem(
                    escape(
                        f"With Infernal vis ({', '.join(p.name or p.art for p in tainted)}): "
                        f"{text} (RoP: The Infernal p. 19)."
                    )
                )
            )
        if vis:
            for note in vis_stores.casting_notes(
                saga, magus, spell.technique, spell.form, vis
            ):
                lines.append(f"[dim]{escape(note)}[/]")
    elif need <= 0:
        lines.append(
            "Formulaic: cast without Fatigue on any die, unless a stressed die "
            f"botches ({botch} botch {'die' if botch == 1 else 'dice'}{calm})."
        )
    else:
        short = _levels(casting.fatigue_levels(1, magus.virtues_flaws, "formulaic"))
        lines.append(
            f"Formulaic: a die of {need}+ casts it; {max(need - 10, 1)}+ casts it "
            f"for {short}."
            if need > 10
            else f"Formulaic: a die of {need}+ casts it without Fatigue; "
            f"less still casts it for {short}, unless a stressed die botches."
        )
    lines += _mastery_lines(magus, known, spell, abilities)
    return lines


def _mastery_lines(
    magus: Character, known: KnownSpell, spell: Spell, abilities: dict[str, int]
) -> list[str]:
    """What the spell's Mastery special abilities do (DE pp. 225-226)."""
    score = known.mastery_score
    if not score or not abilities:
        return []
    found: list[str] = []
    if abilities.get(casting.FAST_CASTING) and not spell.ritual:
        speed = casting.fast_casting_speed(
            magus, abilities.get(casting.QUICK_CASTING, 0)
        )
        found.append(
            f"fast-cast at {casting.FAST_PENALTY} (speed {speed:+d} + stress die)"
        )
    if abilities.get(casting.CEREMONIAL_CASTING) and not spell.ritual:
        found.append("cast ceremonially (+ Artes Liberales + Philosophiae)")
    if abilities.get(casting.PENETRATION_MASTERY):
        found.append(f"+{score} to Penetration")
    if abilities.get(casting.RESISTANCE_MASTERY):
        found.append("Magic Resistance doubled against it and similar spells")
    if abilities.get(casting.IMPERTURBABLE):
        found.append(f"+{score} to its Concentration rolls")
    if abilities.get(casting.MULTIPLE_CASTING):
        # DE pp. 225-226: additional copies up to the Mastery Score, cast
        # together; a Ritual spends its vis again for each copy.
        copies = f"{score} more cop{'y' if score == 1 else 'ies'} at most, cast at once"
        if spell.ritual:
            copies += ", each with its own vis (a pawn per magnitude)"
        found.append(copies)
    if abilities.get(casting.PRECISE_CASTING):
        found.append(f"+{abilities[casting.PRECISE_CASTING]} to its Finesse rolls")
    if abilities.get(casting.QUICK_CASTING) and not spell.ritual:
        found.append(f"+{abilities[casting.QUICK_CASTING]} Initiative")
    found += house_mastery.notes(
        abilities, score, ritual=spell.ritual, general=spell.level is None
    )
    if not found:
        return []
    return ["[b]Mastery:[/] " + escape("; ".join(found)) + "."]
