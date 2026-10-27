"""Open a Tunnel: More's Wizard's War calculator on a magus's Known
Spells -- no UI in here. The tunnel spell he knows and the level he casts
it at, the Arcane Connection and sympathetic connections he holds, his
target's Magic Resistance and any Aegis he shelters in; the inspector
gives the tunnel's Penetration, then each spell he knows that fits
through it and its own. Nothing is kept: it is a calculator, as Craft by
Magic is. The rules and pages are rules.hermetic_projects' (Hermetic
Projects pp. 78-81) and rules.penetration's (DE p. 219)."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from ..catalog import find_spell
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import Character, KnownSpell, Saga, Spell
from ..rules import casting, dice, penetration
from ..rules import hermetic_projects as hp
from ..rules.realms import home_aura, home_aura_kind
from ..rules.scores import ability_level

OPEN_TUNNEL = "Open a Tunnel"
HELP_ID = "open-tunnel"


def known_tunnels(saga: Saga, magus: Character) -> list[tuple[KnownSpell, Spell]]:
    """The tunnel spells the magus knows (HP pp. 80-81; DE p. 372)."""
    found: list[tuple[KnownSpell, Spell]] = []
    for known in magus.spells_known:
        spell = find_spell(saga, known.spell_id)
        if spell is not None and spell.id in hp.TUNNEL_BY_ID:
            found.append((known, spell))
    return found


def offers(saga: Saga, magus: Character) -> bool:
    """Whether Open a Tunnel is offered: he knows a tunnel spell."""
    return bool(known_tunnels(saga, magus))


def _connections(saga: Saga, magus: Character) -> list[tuple[str, str]]:
    """The Arcane Connections kept in his covenant's laboratories."""
    labs = [
        lab
        for lab in saga.laboratories
        if lab.covenant_id == magus.covenant_id or lab.owner_id == magus.id
    ]
    return [
        (escape(f"{c.to} ({'fixed' if c.fixed else c.lasts or 'not fixed'})"), c.id)
        for lab in labs
        for c in lab.arcane_connections
    ]


def _targets(saga: Saga, magus: Character) -> list[tuple[str, str]]:
    return [
        (escape(c.name), c.id)
        for c in sorted(saga.characters, key=lambda c: c.name.casefold())
        if c.type == "magus" and c.id != magus.id
    ]


def tunnel_fields(saga: Saga, magus: Character) -> list[DialogField]:
    tunnels = known_tunnels(saga, magus)
    return [
        DialogField(
            "tunnel",
            "Tunnel",
            "select",
            tunnels[0][1].id if tunnels else None,
            options=[(escape(spell.name), spell.id) for _, spell in tunnels],
            required=True,
        ),
        DialogField(
            "level",
            "Level cast",
            "int",
            20,
            hint="A General spell: the level of his version.",
        ),
        DialogField(
            "connection",
            "Arcane Connection",
            "select",
            None,
            options=_connections(saga, magus),
            allow_blank=True,
            placeholder="(one not in a laboratory)",
        ),
        DialogField(
            "lasts",
            "It lasts",
            "select",
            "Years or decades",
            options=pairs(penetration.ARCANE_CONNECTIONS),
            allow_blank=True,
            placeholder="(no Arcane Connection)",
            hint="Fixed ones last indefinitely (DE p. 219).",
        ),
        *(
            DialogField(
                f"sympathy_{index}",
                f"{sympathy.name} (+{sympathy.bonus})",
                "check",
                False,
            )
            for index, sympathy in enumerate(penetration.SYMPATHIES)
        ),
        DialogField(
            "target",
            "Target",
            "select",
            None,
            options=_targets(saga, magus),
            allow_blank=True,
            placeholder="(someone not in the saga)",
            hint="A magus of the saga: his own Magic Resistance against each Form.",
        ),
        DialogField(
            "parma",
            "Target's Parma Magica",
            "int",
            0,
            hint="For a target not in the saga: x5, his Forms not counted.",
        ),
        DialogField(
            "aegis",
            "He shelters in an Aegis of level",
            "optint",
            None,
        ),
        DialogField(
            "token",
            "The caster holds its token",
            "check",
            False,
            hint="Then no spell need Penetrate the Aegis (HP p. 79).",
        ),
    ]


def _resistance(saga: Saga, values: dict[str, Any], form: str) -> tuple[int, str]:
    target = saga.character(values.get("target"))
    if target is not None:
        found = penetration.magic_resistance(target, form)
        return int(found.total), f"{escape(target.name)}'s Magic Resistance"
    parma = (values.get("parma") or 0) * 5
    return parma, f"Parma {values.get('parma') or 0} x 5"


def _bonus(saga: Saga, magus: Character, values: dict[str, Any]) -> tuple[int, str]:
    lasts = values.get("lasts") or None
    sympathies = [
        sympathy
        for index, sympathy in enumerate(penetration.SYMPATHIES)
        if values.get(f"sympathy_{index}")
    ]
    target = saga.character(values.get("target"))
    found = penetration.penetration_bonus(
        magus, arcane_connection=lasts, sympathies=sympathies, target=target
    )
    score = ability_level(magus, "Penetration")
    multiplier = 1 + sum(int(line.multiplier or 0) for line in found.lines)
    words = (
        f"Penetration {score} x {multiplier}"
        + (f" ({', '.join(escape(s.name) for s in sympathies)})" if sympathies else "")
        if lasts
        else f"Penetration {score} (no Arcane Connection: no multiplier)"
    )
    return int(found.total), words


def _score(saga: Saga, magus: Character, known: KnownSpell, spell: Spell) -> int:
    aura, realm = home_aura(saga, magus)
    return int(
        casting.spell_casting_score(
            magus,
            spell,
            aura=aura,
            aura_realm=realm,
            aura_kind=home_aura_kind(saga, magus),
            mastery=known.mastery_score,
        ).total
    )


def tunnel_live(saga: Saga, magus: Character) -> Callable[[dict[str, Any]], str]:
    def live(values: dict[str, Any]) -> str:
        pair = next(
            (p for p in known_tunnels(saga, magus) if p[1].id == values.get("tunnel")),
            None,
        )
        if pair is None:
            return "Choose the tunnel spell."
        known, spell = pair
        tunnel = hp.TUNNEL_BY_ID[spell.id]
        level = values.get("level") or 0
        aegis = None if values.get("token") else values.get("aegis")
        bonus, bonus_words = _bonus(saga, magus, values)
        score = _score(saga, magus, known, spell)
        pen = score + bonus - level
        resistance, whose = _resistance(saga, values, "Vim")
        need = max(resistance, aegis or 0) + 1 - pen
        limit = hp.tunnel_limit(tunnel, level)
        lines = [
            f"{bonus_words} = [b]+{bonus}[/]",
            f"The tunnel: Casting Score {score} + {bonus} − {level} = "
            f"[b]{pen} + die[/] against {whose} (Vim) {resistance}"
            + (f" and the Aegis {aegis}" if aegis else "")
            + ": "
            + (
                "[$text-success]opens on any die[/]"
                if need <= 0
                else f"opens on a die of {need} or more"
            ),
        ]
        if tunnel.arcane and not values.get("lasts"):
            lines.append(
                "[$text-warning]Its range is Arcane Connection: it needs one.[/]"
            )
        lines += [
            "",
            f"[b]Through it[/] (up to level {limit}, Touch or more; each must "
            "Penetrate too, with the same multiplier):",
        ]
        spells = [
            (k, s)
            for k in magus.spells_known
            if (s := find_spell(saga, k.spell_id)) is not None and s.id != spell.id
        ]
        fits = hp.through([(s.name, s.level, s.range) for _, s in spells], limit)
        for index in fits:
            k, s = spells[index]
            if s.level is None:
                continue
            through_score = _score(saga, magus, k, s)
            through_pen = through_score + bonus - s.level
            against, _ = _resistance(saga, values, s.form)
            short = max(against, aegis or 0) + 1 - through_pen
            tone = "$text-success" if short <= 0 else "$text-warning"
            lines.append(
                f"  {escape(s.name)} {s.technique[:2]}{s.form[:2]} {s.level}: "
                f"{through_score} + {bonus} − {s.level} = [{tone}]{through_pen} + "
                f"die[/] against {against}"
                + ("" if short <= 0 else f" (a die of {short})")
            )
        if not fits:
            lines.append("  [dim]None of the spells he knows fits through.[/]")
        if aegis:
            lines.append(
                f"[$text-warning]Inside an Aegis of {aegis}: every spell must also "
                "Penetrate it, unless cast by one who holds its token.[/]"
            )
        lines.append(
            "[dim]The target can cast back through it once he senses it; Break "
            "the Siege suppresses a tunnel of less than its level + 2 "
            "magnitudes (HP pp. 78-81, errata p. 81; DE p. 219).[/]"
        )
        return "\n".join(lines)

    return live


def cast(
    saga: Saga, magus: Character, values: dict[str, Any], rng: random.Random
) -> list[str]:
    """Cast rolls the tunnel's stress die once: whether it opens. The
    spells cast through it are each rolled at the table."""
    pair = next(
        (p for p in known_tunnels(saga, magus) if p[1].id == values.get("tunnel")),
        None,
    )
    if pair is None:
        return ["Choose the tunnel spell."]
    known, spell = pair
    level = values.get("level") or 0
    aegis = None if values.get("token") else values.get("aegis")
    bonus, _ = _bonus(saga, magus, values)
    score = _score(saga, magus, known, spell)
    die = dice.stress_die(rng, saga=saga)
    resistance, whose = _resistance(saga, values, "Vim")
    if die.botched:
        return notes(
            f"A botch ({die.botches}): the tunnel doesn't open, and a botched "
            "tunnel may briefly open onto the Magic Realm (HP p. 81)."
        )
    pen = score + die.value + bonus - level
    opens = hp.penetrates(pen, resistance, aegis)
    return notes(
        f"{escape(spell.name)}: {score} + die {die.value} + {bonus} − {level} = "
        f"{pen} against {whose} (Vim) {resistance}"
        + (f" and the Aegis {aegis}" if aegis else "")
        + (": the tunnel opens." if opens else ": it fails to Penetrate."),
    )


def tunnel_form(
    saga: Saga, magus: Character, rng: random.Random | None = None
) -> Command:
    """More's Open a Tunnel on a magus's Known Spells: the calculator; Cast
    rolls the tunnel once, and nothing is kept."""
    if not offers(saga, magus):
        return Refuse(OPEN_TUNNEL, f"{escape(magus.name)} knows no tunnel spell.")
    chance = rng or random.Random()
    return Form(
        f"{OPEN_TUNNEL}: {escape(magus.name)}",
        lambda: tunnel_fields(saga, magus),
        lambda values: cast(saga, magus, values, chance),
        live=tunnel_live(saga, magus),
        save_label="Cast",
        cancel_label="Close",
        inspector="Wizard's War",
        help_id=HELP_ID,
    )
