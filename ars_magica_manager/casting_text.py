"""The Hermetic Magic tab's casting text (STORY-802): the magus's Casting
Score for every Technique + Form pair, and a known spell's Casting Score
and what the die must reach. Like the other domain modules it returns
markup. Casting is worked out in the aura of the magus's covenant, with
firm words and bold gestures (the book's defaults)."""

from __future__ import annotations

from . import catalog
from . import spells as spl
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .covenants import covenant_effective_aura
from .markup import escape
from .models import Character, KnownSpell, Saga, Spell
from .rules import casting, certamen, penetration, realms
from .rules import lab as lab_rules


def home_aura(saga: Saga, magus: Character) -> tuple[int, str]:
    """The aura (score, realm) of the magus's covenant: 0 Magic without one."""
    covenant = saga.covenant(magus.covenant_id)
    if covenant is None:
        return 0, realms.HERMETIC
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_effective_aura(covenant, boons), covenant.aura_realm


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
        "Formulaic: score + die >= level casts it; up to 10 short costs a "
        "Fatigue level.",
        "Spontaneous without Fatigue: score / 5; with Fatigue: (score + stress die) / 2.",
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
    lines.append(
        f"Penetration: Casting Total - spell level {bonus:+d} (Penetration), "
        "multiplied by Arcane Connections."
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
    return "\n".join(lines)


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
            steps.append(f"{max(need - slack, 0)}+ for {levels}")
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
        lines.append(
            f"Formulaic: a die of {need}+ casts it; {max(need - 10, 1)}+ casts it "
            "for a Fatigue level."
            if need > 10
            else f"Formulaic: a die of {need}+ casts it without Fatigue; "
            "anything less still casts it for a Fatigue level."
        )
    return lines
