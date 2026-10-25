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
from .arts import FORMS, TECHNIQUES
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
from .rules import casting_virtues, combat_groups, derived
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
        DialogField(
            "range",
            "Range increments",
            "int",
            f.range if f else 0,
            hint="0: hand to hand. Missiles take -3 for each range increment "
            "past the first, and fighters without them can't strike at range "
            "(DE p. 395).",
        ),
        DialogField(
            "aura",
            "Magic aura",
            "int",
            f.aura if f else 0,
            hint="Added to the Casting Totals of spells cast in the fight (DE p. 214).",
        ),
    ]


def _write(fight: Fight, values: dict[str, Any]) -> None:
    fight.name = values["name"]
    fight.place = values.get("place") or ""
    fight.season = values.get("season") or fight.season
    fight.year = int(values.get("year") or fight.year)
    fight.range = max(0, int(values.get("range") or 0))
    fight.aura = int(values.get("aura") or 0)
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


def _defend_options(saga: Saga, fight: Fight, own: str = "") -> list[tuple[str, str]]:
    return [
        ("No one", ""),
        *(
            (
                f"{escape(rules.Fighter(saga, c).name)} "
                f"({escape(rules.side_name(fight, i))})",
                c.id,
            )
            for i, c in _every_combatant(fight)
            if c.id != own
        ),
    ]


def _stance_fields(
    saga: Saga, fight: Fight, c: Combatant | None, from_sheet: Any
) -> list[DialogField]:
    """Mounted, Ride, Magic Resistance and whom it defends: what a
    combatant brings beyond its figures (DE pp. 396-397)."""
    v = c or Combatant()
    typed = lambda values: not from_sheet(values)
    return [
        DialogField(
            "mounted",
            "Mounted",
            "check",
            v.mounted,
            hint="Adds Ride, at most +3, to Attack and Defence (DE p. 397). A "
            "Gifted rider needs magic to stay in the saddle (p. 205).",
        ),
        DialogField(
            "ride",
            "Ride",
            "int",
            v.ride,
            show_if=lambda values: bool(values.get("mounted")) and typed(values),
        ),
        DialogField(
            "resistance",
            "Magic Resistance",
            "int",
            v.resistance,
            show_if=typed,
            hint="Against spells and devices; a creature's is its Might.",
        ),
        DialogField(
            "defends",
            "Defends",
            "select",
            v.defends,
            options=_defend_options(saga, fight, v.id if c else ""),
            hint="A shield grog: while it stands, the one it defends can't be "
            "struck (DE p. 397).",
        ),
    ]


def _write_stance(combatant: Combatant, values: dict[str, Any]) -> None:
    combatant.mounted = bool(values.get("mounted"))
    combatant.ride = max(0, int(values.get("ride") or 0))
    combatant.resistance = max(0, int(values.get("resistance") or 0))
    combatant.defends = values.get("defends") or ""


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
        *_stance_fields(
            saga, fight, None, lambda v: v.get("kind") == CHARACTER_FIGHTER
        ),
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
            resistance=creature.might,
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
        for combatant in made:
            _write_stance(combatant, values)
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
        live=lambda v: combatant_live(saga, fight, v),
        save_label="Add",
        help_id="fights",
        inspector="The Fighter",
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
                _write_stance(combatant, values)

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
                    *_stance_fields(saga, fight, combatant, lambda _v: True),
                    _out_field(combatant),
                ],
                apply_weapon,
                live=lambda v: combatant_live(
                    saga,
                    fight,
                    {**v, "kind": CHARACTER_FIGHTER, "character": combatant.ref_id},
                ),
                help_id="fights",
                inspector="The Fighter",
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
            _write_stance(combatant, values)

        return Form(
            f"Edit {escape(combatant.name)}",
            lambda: [
                *_figure_fields(combatant, None),
                *_stance_fields(saga, fight, combatant, lambda _v: False),
                _out_field(combatant),
            ],
            apply,
            live=lambda v: combatant_live(saga, fight, {**v, "kind": TYPED_FIGHTER}),
            help_id="fights",
            inspector="The Fighter",
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
            options=pairs(rules.actions_for(saga, fight, who)),
            hint="The inspector below says what it does and what it rolls.",
        ),
        DialogField(
            "target",
            "Against",
            "select",
            default.id if default else None,
            options=[(escape(u.name), u.id) for u in enemies],
            show_if=lambda v: (
                v.get("action") not in (rules.DISENGAGE, rules.WAIT, rules.BREAK_FREE)
            ),
        ),
        *_magic_fields(saga, who),
    ]


def _magic_fields(saga: Saga, who: rules.Unit | None) -> list[DialogField]:
    """What Cast a Spell and Use a Device ask: the spell (or the Arts and
    level of a spontaneous one) or the device's effect, and the damage it
    does."""
    character = who.vanguard.character if who is not None else None
    spells = rules.spells_of(saga, character)
    effects = rules.device_effects(saga, character)
    casting = lambda v: v.get("action") == rules.CAST
    spontaneous = lambda v: casting(v) and v.get("spell") == rules.SPONTANEOUS
    return [
        DialogField(
            "spell",
            "Spell",
            "select",
            spells[0][1] if spells else rules.SPONTANEOUS,
            options=[*spells, ("Spontaneous magic", rules.SPONTANEOUS)],
            show_if=casting,
            hint="Cast at the magus's place in the order (DE p. 397).",
        ),
        DialogField(
            "arts",
            "Arts",
            "select",
            "Creo Ignem",
            options=pairs(rules.ART_PAIRS),
            show_if=spontaneous,
        ),
        DialogField("level", "Level", "int", 10, show_if=spontaneous),
        DialogField(
            "requisite_technique",
            "Casting requisite (Technique)",
            "select",
            None,
            options=pairs(TECHNIQUES),
            allow_blank=True,
            placeholder="(none)",
            show_if=casting,
            hint="For what it is used on this time: the lowest Technique and "
            "Form among the spell's Arts and these count (DE p. 312).",
        ),
        DialogField(
            "requisite_form",
            "Casting requisite (Form)",
            "select",
            None,
            options=pairs(FORMS),
            allow_blank=True,
            placeholder="(none)",
            show_if=casting,
        ),
        DialogField(
            "fatiguing",
            "Fatiguing",
            "check",
            True,
            show_if=spontaneous,
            hint="Spend a Fatigue level for the stress die; otherwise the "
            "Casting Score alone, divided by five (DE p. 214).",
        ),
        # Only a fighter holding a device is asked which: an empty list
        # can't be drawn.
        *(
            [
                DialogField(
                    "effect",
                    "Device and effect",
                    "select",
                    effects[0][1],
                    options=effects,
                    show_if=lambda v: v.get("action") == rules.DEVICE,
                    hint="Used at Quickness + stress die, Penetration as "
                    "enchanted (DE p. 259).",
                )
            ]
            if effects
            else []
        ),
        DialogField(
            "spell_damage",
            "Damage",
            "optint",
            None,
            show_if=lambda v: v.get("action") in (rules.CAST, rules.DEVICE),
            hint="A damaging effect's +X: stress die + X against Soak + stress "
            "die, with the right Form Bonus (DE p. 394). Blank: no damage.",
        ),
    ]


def _terms(terms: list[rules.Term]) -> str:
    """ "+11 (Attack +9, Mounted +2)": a total and, when it has more than
    its base, what makes it."""
    total = sum(t.amount for t in terms)
    parts = ", ".join(f"{t.label} {t.amount:+d}" for t in terms)
    return f"{total:+d}" + (f" ({parts})" if len(terms) > 1 else "")


#: What each action does, as the inspector says it (DE pp. 394-398).
ACTION_WORDS: dict[str, str] = {
    rules.ATTACK: "A hit by any margin does Damage plus the Attack Advantage, "
    "less Soak.",
    rules.EXERTION: "Spends a Fatigue level (each member's, in a group) for "
    "the Combat Ability on the Attack.",
    rules.SCUFFLE: "Knocks out rather than kills: the wound is read as "
    "Fatigue on the Scuffle Effects table.",
    rules.GRAPPLE: "Brawl, with free hands: any Advantage above 0 becomes the "
    "Grapple Strength, and the one held may only try to break free.",
    rules.BREAK_FREE: "An attack on the one holding you: its Advantage comes "
    "off the Grapple Strength, and at 0 you are free and the one holding "
    "you takes a Light Wound.",
    rules.SPLIT: "An Advantage of 0 or more splits the group rather than "
    "wounding it: in half, or in thirds when three press it.",
    rules.CAST: "Cast at the magus's place in the order; a Casting Total "
    "short of the level by 10 or less still casts it, for a Fatigue level.",
    rules.DEVICE: "Used at Quickness + stress die, with no Fatigue; its "
    "Penetration is what it was enchanted with.",
    rules.DISENGAGE: "A Defence Total against each foe who struck it last "
    "round; +3 for each try after the first.",
    rules.WAIT: "Holds its action this turn.",
}


def blow_live(saga: Saga, fight: Fight, values: dict[str, Any]) -> str:
    """The inspector under Next Blow: who acts, against whom, what the
    action does and the totals it rolls against."""
    if fight.round == 0:
        return "Initiative is rolled first; the highest acts first."
    who = rules.actor(saga, fight)
    if who is None:
        return "A new round begins."
    action = values.get("action") or rules.ATTACK
    every = rules.units(saga, fight)
    target = every.get(values.get("target") or "")
    grip = rules.grip_on(fight, who.id)
    if action == rules.BREAK_FREE and grip is not None:
        target = every.get(grip.by)
    lines = [f"[b]{escape(who.name)}[/]  [$label]{escape(unit_line(saga, who))}[/]"]
    if target is not None and action not in (rules.DISENGAGE, rules.WAIT):
        lines.append(
            f"[$label]against[/] [b]{escape(target.name)}[/]  "
            f"[$label]{escape(unit_line(saga, target))}[/]"
        )
    lines.append(f"[i]{ACTION_WORDS.get(action, '')}[/]")
    if target is None or action in (rules.DISENGAGE, rules.WAIT):
        return "\n".join(lines)
    if action in (rules.CAST, rules.DEVICE):
        lines += _magic_lines(saga, fight, who, target, action, values)
        return "\n".join(lines)
    chances = rules.odds(saga, fight, who, target, action)
    if chances.blocked:
        lines.append(f"[$text-error]{escape(chances.blocked)}[/]")
        return "\n".join(lines)
    lines.append(
        f"Attack {_terms(chances.attack)} + stress die against Defence "
        f"{_terms(chances.defence)} + stress die."
    )
    if action == rules.BREAK_FREE and grip is not None:
        lines.append(
            f"The grip is {grip.strength}: an Advantage of {grip.strength} or more "
            "frees you; less loosens it."
        )
    elif action == rules.GRAPPLE:
        lines.append("Any Advantage above 0 takes hold, with that strength.")
    if action in combat_groups.SPECIAL_EFFECTS or action == rules.SPLIT:
        lines.append(f"It needs an Attack Advantage of {chances.need} or more.")
    elif action not in (rules.GRAPPLE, rules.BREAK_FREE):
        lines.append(
            f"On a hit: Damage {_terms(chances.damage)} + the Advantage against "
            f"Soak {_terms(chances.soak)}."
        )
    return "\n".join(lines)


def blow_of(values: dict[str, Any]) -> rules.Blow:
    """The blow Next Blow's values describe."""
    damage = values.get("spell_damage")
    return rules.Blow(
        values.get("action") or rules.ATTACK,
        values.get("target") or "",
        spell=values.get("spell") or "",
        arts=values.get("arts") or "",
        level=int(values.get("level") or 0),
        fatiguing=bool(values.get("fatiguing", True)),
        effect=values.get("effect") or "",
        damage=None if damage is None else int(damage),
        casting_requisites=tuple(
            art
            for art in (values.get("requisite_technique"), values.get("requisite_form"))
            if art
        ),
    )


def _magic_lines(
    saga: Saga,
    fight: Fight,
    who: rules.Unit,
    target: rules.Unit,
    action: str,
    values: dict[str, Any],
) -> list[str]:
    """The inspector's lines for a spell or a device: what it casts, the
    total it needs, its Penetration against the target's Magic Resistance,
    and any damage."""
    blow = blow_of(values)
    odds = (
        rules.spell_odds(saga, fight, who, target, blow)
        if action == rules.CAST
        else rules.device_odds(saga, fight, target, blow)
    )
    if odds is None:
        return ["[$text-error]Choose what to cast or use.[/]"]
    lines = [
        f"[b]{escape(odds.name)}[/]: {odds.technique} {odds.form}, level {odds.level}."
    ]
    magus = who.vanguard.character
    if magus is not None and action == rules.CAST:
        if casting_virtues.incompatible(
            magus, odds.technique, odds.form, odds.requisites
        ):
            lines.append(
                "[$text-error]Incompatible Arts: these Arts can't be used together "
                "(DE p. 134).[/]"
            )
            return lines
        lines += [
            f"[i]{note}[/]"
            for vf_id, note in (
                (casting_virtues.SLOW_CASTER, "Slow Caster: two rounds to cast."),
                (casting_virtues.PAINFUL, "Painful Magic: a level of pain after."),
                (
                    casting_virtues.LIFE_LINKED,
                    "Life-Linked: short of the level, a Fatigue level more for "
                    "each 5 (fatiguing spontaneous).",
                ),
            )
            if any(vf.vf_id == vf_id for vf in magus.virtues_flaws)
        ]
    if odds.score is not None:
        if odds.spontaneous:
            lines.append(
                f"Casting Score {odds.score:+d}: with Fatigue, (score + stress die) "
                f"/ 2 must reach {odds.level}; without, {odds.score // 5}."
            )
        else:
            lines.append(
                f"Casting Score {odds.score:+d} (aura included) + stress die "
                f"against level {odds.level}."
            )
        lines.append(
            f"Penetration: Casting Total - {odds.level} + {odds.penetration} "
            f"against Magic Resistance {odds.resistance}."
        )
    else:
        lines.append(
            f"Penetration {odds.penetration} against Magic Resistance "
            f"{odds.resistance}: "
            + (
                "it takes effect."
                if odds.penetration > odds.resistance
                else "resisted."
            )
        )
    damage = values.get("spell_damage")
    if damage is not None:
        soak = target.vanguard.figures().soak
        lines.append(
            f"Damage +{damage} + stress die against Soak {soak:+d} + stress die."
        )
    return lines


def combatant_live(saga: Saga, fight: Fight, values: dict[str, Any]) -> str:
    """The inspector under Add and Edit Combatant: the fighter as the
    fight will see it."""
    kind = values.get("kind") or CHARACTER_FIGHTER
    lines: list[str] = []
    if kind == CHARACTER_FIGHTER:
        ref, _, _weapon = str(values.get("character") or "").partition("|")
        character = saga.character(ref)
        if character is None:
            return "Choose the character."
        lines.append(f"[b]{escape(character.name)}[/]: figures from the sheet.")
        if values.get("mounted") and rules.unsettles_horses(character):
            lines.append(
                "[$text-error]Gifted: a horse throws the rider without magic to "
                "calm it (DE p. 205).[/]"
            )
    else:
        name = values.get("name") or "The fighter"
        attack = values.get("attack")
        lines.append(
            f"[b]{escape(str(name))}[/]  Init {int(values.get('init') or 0):+d}   "
            f"Atk {'n/a' if attack is None else f'{int(attack):+d}'}   "
            f"Dfn {int(values.get('defence') or 0):+d}   "
            f"Soak {int(values.get('soak') or 0):+d}"
        )
        if int(values.get("resistance") or 0):
            lines.append(f"Magic Resistance {int(values.get('resistance') or 0)}.")
    if values.get("mounted"):
        ride = min(rules.MOST_RIDE, int(values.get("ride") or 0))
        lines.append(
            "Mounted: Ride adds "
            + (f"+{ride}" if kind != CHARACTER_FIGHTER else "up to +3")
            + " to Attack and Defence."
        )
    defended = values.get("defends") or ""
    if defended:
        guarded = next(
            (c for _, c in _every_combatant(fight) if c.id == defended), None
        )
        if guarded is not None:
            lines.append(
                f"Defends {escape(rules.Fighter(saga, guarded).name)}: nobody may "
                "strike them while this fighter stands."
            )
    return "\n".join(lines)


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
            blow_of(values),
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
        inspector="The Blow to Come",
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
        f"[$label]Where:[/] {rules.range_text(fight)}"
        + (f", aura {fight.aura:+d}" if fight.aura else ""),
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
            tags = rules.tags(saga, fight, unit)
            if tags:
                lines.append(f"    [i $label]{escape('  ·  '.join(tags))}[/]")
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
