"""The Hermetic Magic tab's casting text: the magus's Casting
Score for every Technique + Form pair, and a known spell's Casting Score
and what the die must reach. Like the other domain modules it returns
markup. Casting is worked out in the aura of the magus's covenant, with
firm words and bold gestures (the book's defaults). A hybrid magus's
styles (Holy or Chthonic Magic, Goetic Arts, Hermetic rites) close it."""

from __future__ import annotations

from . import spells as spl
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .covenants import home_aura
from .markup import escape
from .models import Character, KnownSpell, Saga, Spell
from .rules import casting, certamen, penetration
from .rules import hybrid_magic as hybrid
from .rules import lab as lab_rules


def _levels(count: int) -> str:
    """ "a Fatigue level", "2 Fatigue levels", "no Fatigue"."""
    if count <= 0:
        return "no Fatigue"
    return "a Fatigue level" if count == 1 else f"{count} Fatigue levels"


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
    )
    multipliers = [line for line in sample.lines if line.multiplier is not None]
    halved = sorted({line.label for line in multipliers})
    if halved:
        lines.append(f"Halved totals for: {escape(', '.join(halved))}.")
    lines += [escape(line) for line in hybrid.summary(magus)]
    return "\n".join(lines)


#: What a reader needs to cast from a Casting Tablet (DE: an apprentice
#: whose Arts are opened can, with these).
TABLET_ARTES_LIBERALES, TABLET_LATIN = 1, 4


def tablet_casting_line(saga: Saga, magus: Character, spell: Spell) -> str:
    """One magus casting a Casting Tablet's spell (markup): the Casting
    Total before the stress die and what each die gives, by DE's table."""
    from .rules.book_seasons import ability_score, language_score

    name = escape(magus.name)
    if (
        ability_score(magus, "Artes Liberales") < TABLET_ARTES_LIBERALES
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
    score = casting.spell_casting_score(
        magus, spell, aura=aura, aura_realm=realm, mastery=known.mastery_score
    )
    total = int(score.total)
    terms = ", ".join(
        f"{escape(line.label)} {line.amount:+g}"
        for line in score.lines
        if line.amount is not None
    )
    lines = [f"[b]Casting Score:[/] {total} ({terms})"]
    if spell.level is None:
        return lines
    botch = casting.botch_dice(
        vis_pawns=spl.vis_cost(spell) or 0,
        aura_realm=realm,
        aura=aura,
        mastery=known.mastery_score,
        virtues_flaws=magus.virtues_flaws,
    )
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
            + f" long-term Fatigue levels; {botch} botch "
            + ("die." if botch == 1 else "dice.")
        )
    elif need <= 0:
        lines.append("Formulaic: always cast without Fatigue, even on a die of 0.")
    else:
        short = _levels(casting.fatigue_levels(1, magus.virtues_flaws, "formulaic"))
        lines.append(
            f"Formulaic: a die of {need}+ casts it; {max(need - 10, 1)}+ casts it "
            f"for {short}."
            if need > 10
            else f"Formulaic: a die of {need}+ casts it without Fatigue; "
            f"anything less still casts it for {short}."
        )
    return lines
