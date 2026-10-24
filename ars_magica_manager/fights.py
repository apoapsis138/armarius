"""The saga's fights: the list, the forms that set one up (its sides,
combatants and groups) and the commands that play it (Next Blow, Next
Round, Restart). The rules are rules.fight's; this is the record and its
forms, for either front-end.

Pattern: a fight's side is a Composite of combatants and groups
(rules.fight.Unit), and each command is a commands step, so the
terminal's More menu and the desktop's buttons run the same code.
"""

from __future__ import annotations

import random
from typing import Any

from . import diaries
from .commands import (
    Act,
    Choice,
    Choose,
    Command,
    Confirm,
    Form,
    Refuse,
    SectionOps,
    notes,
)
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    CHARACTER_FIGHTER,
    CREATURE_FIGHTER,
    SEASONS,
    TYPED_FIGHTER,
    Combatant,
    Fight,
    FightGroup,
    FightSide,
    Saga,
)
from .rules import combat_groups, derived
from .rules import fight as rules

SOURCE = rules.SOURCE
KINDS = (
    ("A character", CHARACTER_FIGHTER),
    ("A creature of the Bestiary", CREATURE_FIGHTER),
    ("Typed in", TYPED_FIGHTER),
)
#: How many fighters one Add may make from a creature or typed figures.
MOST_AT_ONCE = 30


def fight_of(saga: Saga, index: int) -> Fight | None:
    return saga.fights[index] if 0 <= index < len(saga.fights) else None


def sides(fight: Fight) -> list[FightSide]:
    """The fight's two sides, made when it has fewer."""
    while len(fight.sides) < 2:
        fight.sides.append(FightSide())
    return fight.sides


def standing_text(saga: Saga, fight: Fight) -> str:
    """Fighters still standing on each side ("3 v 2")."""
    counts = [0, 0]
    for unit in rules.units(saga, fight).values():
        counts[min(unit.side, 1)] += len(unit.standing())
    return f"{counts[0]} v {counts[1]}"


def state_text(fight: Fight) -> str:
    if fight.over:
        return fight.over
    if fight.round == 0:
        return "Not begun"
    return f"Round {fight.round}"


# -- the list --


def title(saga: Saga) -> str:
    return f"Fights ({len(saga.fights)})"


def grid(saga: Saga) -> Grid:
    rows = [
        [
            f.name,
            f"{f.season} {f.year}",
            " v ".join(rules.side_name(f, i) for i in range(len(sides(f)))),
            standing_text(saga, f),
            state_text(f),
        ]
        for f in saga.fights
    ]
    return Grid(
        ["Fight", "When", "Sides", "Standing", "State"],
        rows,
        list(range(len(rows))),
        "No fights yet: add one, give it combatants, then play it with Next Blow.",
        caps=[22, 12, 26, 8, 0],
        stretch=1,
    )


def fields(saga: Saga, fight: Fight | None) -> list[DialogField]:
    f = fight
    first, second = (sides(f) if f is not None else [FightSide(), FightSide()])[:2]
    covenants = [("None", ""), *((escape(c.name), c.id) for c in saga.covenants)]
    return [
        DialogField(
            "name",
            "Fight",
            "text",
            f.name if f else "",
            required=True,
            placeholder="e.g. The Fray at Hallstatt Ford",
        ),
        DialogField(
            "place",
            "Where",
            "text",
            f.place if f else "",
            placeholder="e.g. in the shallows below the mill",
        ),
        DialogField(
            "season",
            "Season",
            "select",
            f.season if f else saga.current_season,
            options=pairs(SEASONS),
        ),
        DialogField("year", "Year", "int", f.year if f else saga.current_year),
        DialogField(
            "first", "First side", "text", first.name, placeholder="e.g. The Covenant"
        ),
        DialogField(
            "first_covenant",
            "First side's arms",
            "select",
            first.covenant_id,
            options=covenants,
            hint="A covenant whose arms the side fights under, on the desktop.",
        ),
        DialogField(
            "second", "Second side", "text", second.name, placeholder="e.g. Brigands"
        ),
        DialogField(
            "second_covenant",
            "Second side's arms",
            "select",
            second.covenant_id,
            options=covenants,
        ),
    ]


def _write(fight: Fight, values: dict[str, Any]) -> None:
    fight.name = values["name"]
    fight.place = values.get("place") or ""
    fight.season = values.get("season") or fight.season
    fight.year = int(values.get("year") or fight.year)
    first, second = sides(fight)[:2]
    first.name, first.covenant_id = (
        values.get("first") or "",
        values.get("first_covenant") or "",
    )
    second.name, second.covenant_id = (
        values.get("second") or "",
        values.get("second_covenant") or "",
    )


def ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete on the Fights list."""

    def form(index: int | None) -> Command:
        fight = None if index is None else fight_of(saga, index)

        def apply(values: dict[str, Any]) -> None:
            if fight is None:
                made = Fight(values["name"], sides=[FightSide(), FightSide()])
                _write(made, values)
                saga.fights.append(made)
            else:
                _write(fight, values)

        return Form(
            "Add a Fight" if fight is None else "Edit a Fight",
            lambda: fields(saga, fight),
            apply,
            save_label="Add" if fight is None else "Save",
            help_id="fights",
        )

    def remove(index: int) -> Command:
        fight = fight_of(saga, index)
        if fight is None:
            return Refuse("Delete Fight", "Choose a fight first.")
        return Confirm(
            f"Delete the fight {escape(fight.name)}? Wounds it dealt stay on the "
            "characters' sheets.",
            lambda: saga.fights.remove(fight),
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=remove,
        rows=lambda: [f.name for f in saga.fights],
    )


# -- combatants --


def _weapon_options(saga: Saga) -> list[tuple[str, str]]:
    """Each character with each weapon they carry ("Gunther, Long Sword"),
    the value "<character id>|<weapon id>"."""
    found: list[tuple[str, str]] = []
    for c in saga.characters:
        weapons = [i for i in c.inventory if i.kind == "weapon"]
        for w in weapons:
            found.append((f"{escape(c.name)}, {escape(w.name)}", f"{c.id}|{w.id}"))
        if not weapons:
            found.append((f"{escape(c.name)} (no weapon: type figures)", f"{c.id}|"))
    return found


def _attack_options(saga: Saga) -> list[tuple[str, str]]:
    """Each creature with each of its attacks ("Wolf, Bite"), the value
    "<creature id>|<attack id>"."""
    found: list[tuple[str, str]] = []
    for c in saga.creatures:
        for a in c.attacks:
            found.append((f"{escape(c.name)}, {escape(a.name)}", f"{c.id}|{a.id}"))
        if not c.attacks:
            found.append((escape(c.name), f"{c.id}|"))
    return found


def _figure_fields(c: Combatant | None, shown: Any) -> list[DialogField]:
    v = c or Combatant()
    return [
        DialogField(
            "name", "Name", "text", v.name, show_if=shown, placeholder="e.g. Bandit"
        ),
        DialogField("init", "Init", "int", v.init, show_if=shown),
        DialogField(
            "attack",
            "Attack",
            "optint",
            v.attack,
            show_if=shown,
            hint="Blank: no attack.",
        ),
        DialogField("defence", "Defence", "int", v.defence, show_if=shown),
        DialogField("damage", "Damage", "optint", v.damage, show_if=shown),
        DialogField("soak", "Soak", "int", v.soak, show_if=shown),
        DialogField("size", "Size", "int", v.size, show_if=shown),
        DialogField(
            "ability",
            "Combat Ability",
            "int",
            v.ability,
            show_if=shown,
            hint="For Exertion and a trained group's bonus.",
        ),
        DialogField("leadership", "Leadership", "int", v.leadership, show_if=shown),
    ]


def combatant_fields(saga: Saga, fight: Fight) -> list[DialogField]:
    names = [rules.side_name(fight, i) for i in range(len(sides(fight)))]
    typed = lambda v: v.get("kind") == TYPED_FIGHTER
    return [
        DialogField(
            "side",
            "Side",
            "select",
            "0",
            options=[(escape(n), str(i)) for i, n in enumerate(names)],
            required=True,
        ),
        DialogField(
            "kind",
            "Drawn from",
            "select",
            CHARACTER_FIGHTER,
            options=list(KINDS),
            required=True,
        ),
        DialogField(
            "character",
            "Character and weapon",
            "select",
            None,
            options=_weapon_options(saga),
            show_if=lambda v: v.get("kind") == CHARACTER_FIGHTER,
            hint="Figures, wounds and Fatigue come from the sheet, and wounds "
            "taken go onto it.",
        ),
        DialogField(
            "creature",
            "Creature and attack",
            "select",
            None,
            options=_attack_options(saga),
            show_if=lambda v: v.get("kind") == CREATURE_FIGHTER,
            hint="Its figures are copied; each fighter keeps its own wounds.",
        ),
        DialogField(
            "count",
            "How many",
            "int",
            1,
            show_if=lambda v: v.get("kind") != CHARACTER_FIGHTER,
            hint=f"Up to {MOST_AT_ONCE}, numbered (Bandit 1, Bandit 2...).",
        ),
        *_figure_fields(None, typed),
    ]


def _made(saga: Saga, values: dict[str, Any]) -> list[Combatant]:
    kind = values.get("kind") or TYPED_FIGHTER
    if kind == CHARACTER_FIGHTER:
        ref, _, weapon = str(values.get("character") or "").partition("|")
        character = saga.character(ref)
        if character is None:
            return []
        return [Combatant(character.name, CHARACTER_FIGHTER, ref, weapon)]
    count = max(1, min(MOST_AT_ONCE, int(values.get("count") or 1)))
    if kind == CREATURE_FIGHTER:
        ref, _, attack_id = str(values.get("creature") or "").partition("|")
        creature = saga.creature(ref)
        if creature is None:
            return []
        attack = next((a for a in creature.attacks if a.id == attack_id), None)
        base = Combatant(
            creature.name,
            CREATURE_FIGHTER,
            creature.id,
            attack_id,
            init=attack.init if attack else 0,
            attack=attack.attack if attack else None,
            defence=attack.defense if attack else 0,
            damage=attack.damage if attack else None,
            soak=creature.soak,
            size=creature.size,
        )
    else:
        base = Combatant(
            values.get("name") or "Fighter",
            init=int(values.get("init") or 0),
            attack=values.get("attack"),
            defence=int(values.get("defence") or 0),
            damage=values.get("damage"),
            soak=int(values.get("soak") or 0),
            size=int(values.get("size") or 0),
            ability=int(values.get("ability") or 0),
            leadership=int(values.get("leadership") or 0),
        )
    if count == 1:
        return [base]
    return [
        Combatant(
            **{**vars(base), "name": f"{base.name} {n + 1}", "id": f"{base.id}{n}"}
        )
        for n in range(count)
    ]


def _combatant_problem(saga: Saga, values: dict[str, Any]) -> str | None:
    kind = values.get("kind")
    if kind == CHARACTER_FIGHTER and not values.get("character"):
        return "Choose the character."
    if kind == CREATURE_FIGHTER and not values.get("creature"):
        return "Choose the creature."
    if kind == TYPED_FIGHTER and not values.get("name"):
        return "Give the fighter a name."
    return None


def add_combatant(saga: Saga, fight: Fight | None) -> Command:
    """More's Add Combatant: a character with a weapon, a Bestiary
    creature (as many as are wanted), or typed figures, to one side."""
    if fight is None:
        return Refuse("Add Combatant", "Choose a fight first.")

    def apply(values: dict[str, Any]) -> list[str]:
        side = sides(fight)[int(values.get("side") or 0)]
        made = _made(saga, values)
        side.combatants += made
        if fight.round:
            # A newcomer acts at the end of the order this fight.
            fight.order += [c.id for c in made]
        return notes(
            f"{len(made)} added to {rules.side_name(fight, sides(fight).index(side))}."
        )

    return Form(
        f"Add a Combatant: {escape(fight.name)}",
        lambda: combatant_fields(saga, fight),
        apply,
        validate=lambda v: _combatant_problem(saga, v),
        save_label="Add",
        help_id="fights",
    )


def _every_combatant(fight: Fight) -> list[tuple[int, Combatant]]:
    return [(i, c) for i, side in enumerate(sides(fight)) for c in side.combatants]


def _combatant_choices(saga: Saga, fight: Fight) -> list[Choice]:
    return [
        Choice(
            escape(rules.Fighter(saga, c).name),
            c.id,
            detail=escape(rules.side_name(fight, i)),
        )
        for i, c in _every_combatant(fight)
    ]


def edit_combatant(saga: Saga, fight: Fight | None) -> Command:
    """More's Edit Combatant: choose one, then its figures (a character's
    come from its sheet: only its weapon is chosen here)."""
    if fight is None or not _every_combatant(fight):
        return Refuse("Edit Combatant", "The fight has no combatants yet.")

    def chosen(ident: str) -> Command:
        combatant = next(c for _, c in _every_combatant(fight) if c.id == ident)
        if combatant.kind == CHARACTER_FIGHTER:
            character = saga.character(combatant.ref_id)
            weapons = (
                [i for i in character.inventory if i.kind == "weapon"]
                if character
                else []
            )

            def apply_weapon(values: dict[str, Any]) -> None:
                combatant.weapon_id = values.get("weapon") or ""
                combatant.out = values.get("out") or ""

            return Form(
                f"Edit {escape(combatant.name)}",
                lambda: [
                    DialogField(
                        "weapon",
                        "Weapon",
                        "select",
                        combatant.weapon_id or (weapons[0].id if weapons else None),
                        options=[(escape(w.name), w.id) for w in weapons],
                    ),
                    _out_field(combatant),
                ],
                apply_weapon,
                help_id="fights",
            )

        def apply(values: dict[str, Any]) -> None:
            for key in ("name", "attack", "damage"):
                setattr(
                    combatant,
                    key,
                    values.get(key)
                    if key != "name"
                    else values.get(key) or combatant.name,
                )
            for key in ("init", "defence", "soak", "size", "ability", "leadership"):
                setattr(combatant, key, int(values.get(key) or 0))
            combatant.out = values.get("out") or ""

        return Form(
            f"Edit {escape(combatant.name)}",
            lambda: [*_figure_fields(combatant, None), _out_field(combatant)],
            apply,
            help_id="fights",
        )

    return Choose(
        "Edit which combatant?",
        lambda: _combatant_choices(saga, fight),
        chosen,
        help_id="fights",
    )


def _out_field(combatant: Combatant) -> DialogField:
    return DialogField(
        "out",
        "Out of the fight",
        "select",
        combatant.out,
        options=[
            ("No: still fighting", ""),
            *pairs(("Disengaged", "Fled", "Surrendered")),
        ],
    )


def remove_combatant(saga: Saga, fight: Fight | None) -> Command:
    """More's Remove Combatant: out of the fight and its groups (a
    character's sheet keeps its wounds)."""
    if fight is None or not _every_combatant(fight):
        return Refuse("Remove Combatant", "The fight has no combatants yet.")

    def chosen(ident: str) -> Command:
        index, combatant = next(
            (i, c) for i, c in _every_combatant(fight) if c.id == ident
        )

        def apply() -> None:
            side = sides(fight)[index]
            side.combatants.remove(combatant)
            for group in side.groups:
                if ident in group.members:
                    group.members.remove(ident)
            side.groups = [g for g in side.groups if g.members]
            fight.order = [u for u in fight.order if u != ident]

        return Confirm(
            f"Take {escape(combatant.name)} out of {escape(fight.name)}?",
            apply,
            yes_label="Remove",
        )

    return Choose(
        "Remove which combatant?", lambda: _combatant_choices(saga, fight), chosen
    )


# -- groups --


def group_fields(saga: Saga, fight: Fight) -> list[DialogField]:
    names = [rules.side_name(fight, i) for i in range(len(sides(fight)))]
    found: list[DialogField] = [
        DialogField(
            "side",
            "Side",
            "select",
            "0",
            options=[(escape(n), str(i)) for i, n in enumerate(names)],
            required=True,
        ),
        DialogField("name", "Group", "text", "", placeholder="e.g. Gunther's turb"),
    ]
    for index, side in enumerate(sides(fight)):
        free = [
            c
            for c in side.combatants
            if not any(c.id in g.members for g in side.groups)
        ]
        shown = lambda v, i=str(index): v.get("side") == i
        found += [
            DialogField(
                f"member_{c.id}",
                escape(rules.Fighter(saga, c).name),
                "check",
                False,
                show_if=shown,
            )
            for c in free
        ]
        options = [(escape(rules.Fighter(saga, c).name), c.id) for c in free]
        found += [
            DialogField(
                f"vanguard_{index}",
                "Vanguard",
                "select",
                options[0][1] if options else None,
                options=options,
                show_if=shown,
                hint="Bears the brunt: the group fights with the vanguard's figures.",
            ),
            DialogField(
                f"leader_{index}",
                "Leader (a trained group)",
                "select",
                "",
                options=[("None: an untrained group", ""), *options],
                show_if=shown,
                hint="A group that spent a season improving combat skills "
                "together; its leader coordinates up to his Leadership in fighters.",
            ),
        ]
    found.append(
        DialogField(
            "bonus_to",
            "A trained group's bonus goes to",
            "select",
            "attack",
            options=[("Attack", "attack"), ("Defence", "defence")],
        )
    )
    return found


def _group_problem(fight: Fight, values: dict[str, Any]) -> str | None:
    index = int(values.get("side") or 0)
    members = [
        k.removeprefix("member_")
        for k, v in values.items()
        if k.startswith("member_") and v
    ]
    side_ids = {c.id for c in sides(fight)[index].combatants}
    members = [m for m in members if m in side_ids]
    if not 1 <= len(members) <= combat_groups.MOST_MEMBERS:
        return f"A group has one to {combat_groups.MOST_MEMBERS} members."
    if values.get(f"vanguard_{index}") not in members:
        return "The vanguard must be one of the group."
    leader = values.get(f"leader_{index}")
    if leader and leader not in members:
        return "The leader must be one of the group."
    return None


def form_group(saga: Saga, fight: Fight | None) -> Command:
    """More's Form a Group: one to six fighters of a side, its vanguard,
    and for a trained group its leader (DE pp. 395-396)."""
    if fight is None or not _every_combatant(fight):
        return Refuse("Form a Group", "The fight has no combatants yet.")

    def apply(values: dict[str, Any]) -> list[str]:
        index = int(values.get("side") or 0)
        side = sides(fight)[index]
        side_ids = {c.id for c in side.combatants}
        members = [
            k.removeprefix("member_")
            for k, v in values.items()
            if k.startswith("member_") and v and k.removeprefix("member_") in side_ids
        ]
        vanguard = values.get(f"vanguard_{index}") or members[0]
        members.remove(vanguard)
        leader = values.get(f"leader_{index}") or ""
        group = FightGroup(
            values.get("name") or "",
            [vanguard, *members],
            trained=bool(leader),
            leader=leader,
            bonus_to=values.get("bonus_to") or "attack",
        )
        side.groups.append(group)
        if fight.round:
            first = min(
                (fight.order.index(m) for m in group.members if m in fight.order),
                default=len(fight.order),
            )
            fight.order = [u for u in fight.order if u not in group.members]
            fight.order.insert(min(first, len(fight.order)), group.id)
            fight.initiative[group.id] = fight.initiative.get(vanguard, 0)
        unit = rules.units(saga, fight)[group.id]
        spread = _spread_problem(unit)
        return notes(f"{unit.name} formed.", *([spread] if spread else []))

    return Form(
        f"Form a Group: {escape(fight.name)}",
        lambda: group_fields(saga, fight),
        apply,
        validate=lambda v: _group_problem(fight, v),
        save_label="Form",
        help_id="fights",
    )


def _spread_problem(unit: rules.Unit) -> str:
    """A note when the members' totals run more than five apart (a group's
    must, when it forms)."""
    figures = [f.figures() for f in unit.fighters]
    for name in ("init", "attack", "defence", "damage"):
        values = [v for f in figures if (v := getattr(f, name)) is not None]
        if values and max(values) - min(values) > combat_groups.SPREAD:
            return (
                f"Their {name.title()} totals run {min(values)} to {max(values)}: "
                f"a group's are within {combat_groups.SPREAD} points (DE p. 395)."
            )
    return ""


def break_group(saga: Saga, fight: Fight | None) -> Command:
    """More's Break up a Group: its members fight alone again."""
    groups = [(side, g) for side in sides(fight) for g in side.groups] if fight else []
    if fight is None or not groups:
        return Refuse("Break up a Group", "The fight has no groups.")
    every = rules.units(saga, fight)

    def chosen(ident: str) -> Command:
        side, group = next((s, g) for s, g in groups if g.id == ident)

        def apply() -> None:
            side.groups.remove(group)
            if group.id in fight.order:
                at = fight.order.index(group.id)
                fight.order[at : at + 1] = group.members
                for m in group.members:
                    fight.initiative[m] = fight.initiative.get(group.id, 0)

        return Act(apply)

    return Choose(
        "Break up which group?",
        lambda: [
            Choice(escape(every[g.id].name if g.id in every else g.name), g.id)
            for _, g in groups
        ],
        chosen,
    )


# -- playing it --


def unit_line(saga: Saga, unit: rules.Unit) -> str:
    """A unit's figures in a line ("Init +4  Atk +12  Dfn +9  Dam +8
    Soak +7")."""
    f = unit.vanguard.figures()

    def signed(value: int | None) -> str:
        return "n/a" if value is None else f"{value:+d}"

    bonus = unit.bonus()
    return (
        f"Init {signed(f.init)}  Atk {signed(f.attack)}  Dfn {signed(f.defence)}  "
        f"Dam {signed(f.damage)}  Soak {signed(f.soak)}"
        + (
            f"  (group bonus +{bonus} to {unit.group.bonus_to})"
            if bonus and unit.group
            else ""
        )
    )


def blow_fields(saga: Saga, fight: Fight) -> list[DialogField]:
    who = rules.actor(saga, fight) if fight.round else None
    every = rules.units(saga, fight)
    side = who.side if who is not None else 0
    enemies = [u for u in every.values() if u.side != side and not u.down()]
    default = rules.default_target(saga, fight, who) if who is not None else None
    return [
        DialogField(
            "action",
            "Action",
            "select",
            rules.ATTACK,
            options=pairs(rules.ACTIONS),
            hint="Exertion spends a Fatigue level for the Combat Ability; a "
            "scuffle knocks out rather than kills; a special effect needs its "
            "Attack Advantage (disarm 9, trip 3, grab a worn item 6, take the "
            "weapon in use 12).",
        ),
        DialogField(
            "target",
            "Against",
            "select",
            default.id if default else None,
            options=[(escape(u.name), u.id) for u in enemies],
            show_if=lambda v: v.get("action") not in (rules.DISENGAGE, rules.WAIT),
        ),
    ]


def blow_live(saga: Saga, fight: Fight, values: dict[str, Any]) -> str:
    if fight.round == 0:
        return "Initiative is rolled first; the highest acts first."
    who = rules.actor(saga, fight)
    if who is None:
        return "A new round begins."
    every = rules.units(saga, fight)
    target = every.get(values.get("target") or "")
    against = f" against {target.name} ({unit_line(saga, target)})" if target else ""
    return f"Round {fight.round}: {who.name} acts ({unit_line(saga, who)}){against}."


def next_blow(
    saga: Saga, fight: Fight | None, rng: random.Random | None = None
) -> Command:
    """More's Next Blow: the unit acting now attacks (or acts) as chosen;
    Initiative is rolled first in a new fight."""
    if fight is None:
        return Refuse("Next Blow", "Choose a fight first.")
    if fight.over:
        return Refuse("Next Blow", f"{escape(fight.over)} Restart it to fight again.")
    if (
        len(rules.units(saga, fight)) < 2
        or len(sides(fight)) < 2
        or not all(s.combatants for s in sides(fight)[:2])
    ):
        return Refuse("Next Blow", "Both sides need combatants first (Add Combatant).")
    dice = rng or random.Random()

    def apply(values: dict[str, Any]) -> list[str]:
        played = rules.play(
            saga,
            fight,
            rules.Blow(
                values.get("action") or rules.ATTACK, values.get("target") or ""
            ),
            dice,
        )
        return notes(played.text, *played.lines, *record_ending(saga, fight))

    return Form(
        f"Next Blow: {escape(fight.name)}",
        lambda: blow_fields(saga, fight),
        apply,
        live=lambda v: blow_live(saga, fight, v),
        save_label="Strike",
        help_id="fights",
    )


def next_round(
    saga: Saga, fight: Fight | None, rng: random.Random | None = None
) -> Command:
    """More's Next Round: every turn left in the round, each striking its
    default target."""
    first = next_blow(saga, fight, rng)
    if isinstance(first, Refuse) or fight is None:
        return first
    dice = rng or random.Random()

    def apply() -> list[str]:
        played = rules.play_round(saga, fight, dice)
        return notes(*(p.text for p in played), *record_ending(saga, fight))

    return Act(apply)


def restart(saga: Saga, fight: Fight | None) -> Command:
    """More's Restart the Fight: the order and chronicle cleared; wounds
    already written onto sheets stay."""
    if fight is None:
        return Refuse("Restart the Fight", "Choose a fight first.")
    return Confirm(
        f"Restart {escape(fight.name)}? Its chronicle is cleared and Initiative "
        "is rolled again; wounds already taken stay.",
        lambda: rules.restart(fight),
        yes_label="Restart",
    )


def record_ending(saga: Saga, fight: Fight) -> list[str]:
    """Once a fight is over, a line in the Diary of every character who
    fought in it and of each side's covenant (written once: a restart
    clears the mark). Returns a note when it writes."""
    if not fight.over or fight.recorded:
        return []
    fought = [
        c
        for side in sides(fight)
        for combatant in side.combatants
        if combatant.kind == CHARACTER_FIGHTER
        and (c := saga.character(combatant.ref_id)) is not None
    ]
    covenants = [
        c for side in sides(fight) if (c := saga.covenant(side.covenant_id)) is not None
    ]
    where = f", {fight.place}" if fight.place else ""
    rounds = max(1, fight.round)
    count = diaries.write(
        fight.year,
        fight.season,
        fight.name,
        f"{fight.over} ({rounds} round{'s' if rounds > 1 else ''}{where}).",
        characters=fought,
        covenants=covenants,
    )
    fight.recorded = True
    return [f"Written in {count} Diar{'y' if count == 1 else 'ies'}."] if count else []


# -- what a fight shows --


def wounds_text(fighter: rules.Fighter) -> str:
    w = fighter.wounds
    parts = [
        f"{n} {name}"
        for n, name in ((w.light, "Light"), (w.medium, "Medium"), (w.heavy, "Heavy"))
        if n
    ]
    if w.incapacitated:
        parts.append("Incapacitated")
    if w.dead:
        parts.append("Dead")
    level = (
        fighter.character.fatigue_level
        if fighter.character is not None
        else fighter.combatant.fatigue_level
    )
    if level != "fresh":
        parts.append(level.title())
    if fighter.combatant.out:
        parts.append(fighter.combatant.out)
    return ", ".join(parts) or "unhurt"


def order_text(saga: Saga, fight: Fight) -> str:
    """The order of blows on a line, the one acting now marked."""
    if fight.round == 0:
        return "Initiative not rolled yet."
    every = rules.units(saga, fight)
    parts = []
    for i, unit_id in enumerate(fight.order):
        unit = every.get(unit_id)
        if unit is None:
            continue
        name = escape(unit.name)
        text = f"{fight.initiative.get(unit_id, 0)} {name}"
        if unit.down():
            text = f"[dim]{text}[/]"
        elif i == fight.turn and not fight.over:
            text = f"[b]> {text}[/]"
        parts.append(text)
    return "  ·  ".join(parts)


def info(saga: Saga, fight: Fight) -> str:
    """A fight in full, as markup: its state, the order of blows, each
    side's units and wounds, the last blow's working and the chronicle."""
    lines = [
        f"[b]{escape(fight.name)}[/]  [dim]{fight.season} {fight.year}"
        + (f", {escape(fight.place)}" if fight.place else "")
        + f"[/]  {escape(state_text(fight))}",
        f"[$label]Order of blows:[/] {order_text(saga, fight)}",
    ]
    every = rules.units(saga, fight).values()
    for index in range(len(sides(fight))):
        lines.append(f"[b]{escape(rules.side_name(fight, index))}[/]")
        for unit in (u for u in every if u.side == index):
            head = escape(unit.name)
            if unit.group is not None:
                head += (
                    " [dim](group"
                    + (", trained" if unit.group.trained else "")
                    + ")[/]"
                )
            lines.append(f"  {head}: {unit_line(saga, unit)}")
            for fighter in unit.fighters:
                lines.append(
                    f"    {escape(fighter.name)}: {escape(wounds_text(fighter))}"
                )
    if fight.log:
        last = fight.log[-1]
        lines.append(f"[$label]Last:[/] {escape(last.text)}")
        lines += [f"  [dim]{escape(x)}[/]" for x in last.lines]
        lines.append("[$label]Chronicle:[/]")
        lines += [f"  {e.round}. {escape(e.text)}" for e in fight.log[-12:]]
    lines.append(f"[dim]{SOURCE}.[/]")
    return "\n".join(lines)


def soak_of(fighter: rules.Fighter) -> int:
    return (
        int(derived.soak(fighter.character).total)
        if fighter.character is not None
        else fighter.combatant.soak
    )
