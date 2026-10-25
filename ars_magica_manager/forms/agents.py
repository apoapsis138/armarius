"""A character's agents (Lords of Men, Control Through Emotional Bonds,
pp. 22-25; the rules are rules.agents'): the Agents tab's title, header,
rows and details, the form that adds or edits an agent, and More's
Impress, Spend Agency Experience and Set a Task. Both front-ends draw
them: the terminal's list and details panel, the desktop's ledger and
inspector.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any

from ..commands import Act, Command, Form, Refuse, SectionOps, delete, notes
from ..form_spec import DialogField
from ..markup import BULLET, escape, fit
from ..models import Agent, Character, Saga
from ..rules import agents as ag
from ..rules import dice, scores
from ..rules.supplement_work import gift_penalty
from ..sections import AGENTS_SECTION
from ..tables import Table

#: The book, as the panel cites it.
LOM = "LoM"

#: Who is never an agent, counted or listed (p. 22).
NOT_AGENTS = (
    "Not agents (LoM p. 22): Hermetic magi, people with no political role, "
    "an agent's own people, hirelings, and other players' characters."
)

#: The Abilities a task's persuasion may use, "as situationally
#: appropriate" (p. 24).
PERSUADERS = ("Charm", "Intrigue", "Leadership")

COLUMNS = ["Name", "Status", "Bond", "Resistance", "Resources"]

#: The terminal list's column widths (Name, Status, Bond, Resistance);
#: Resources takes what is left, cut at RESOURCES_WIDTH.
WIDTHS = (23, 14, 25, 14)
RESOURCES_WIDTH = 16


def status_label(agent: Agent) -> str:
    """ "Minor Social Virtue": his Social Status, without the examples."""
    found = ag.STATUS_RESISTANCE.get(agent.status, ag.STATUS_RESISTANCE["free"])
    return found[0].split(" (")[0]


def _short_status(agent: Agent) -> str:
    """ "Minor Virtue", for the terminal's narrow column."""
    short = status_label(agent).replace(" Social", "")
    return "Free" if short == "Free Virtue" else short


#: The modifiers' words where the terminal's panel has one line for them.
_SHORT_MODIFIERS = {
    "major_trouble": "Major troubling Flaw",
    "minor_trouble": "Minor troubling Flaw",
    "dominated": "Flaw used to dominate him",
    "skill": "Main Ability 6+",
    "exceptional": "Main Ability 8+",
    "minor_virtue": "Minor Virtue",
    "major_virtue": "Major Virtue",
    "rival": "Serves a rival",
    "underlings": "Underlings",
    "many_underlings": "Many underlings",
    "useful_flaw": "Useful Minor Flaw",
}


def _modifier_label(key: str, *, short: bool = False) -> str:
    if short:
        return _SHORT_MODIFIERS[key]
    return ag.MODIFIERS[key][0].split(" (")[0]


def title(character: Character) -> str:
    return f"Agents ({len(character.agents)})"


def _better(character: Character) -> tuple[str, int]:
    """The higher of Intrigue and Leadership, which the limit uses."""
    intrigue = scores.ability_level(character, "Intrigue")
    leadership = scores.ability_level(character, "Leadership")
    if intrigue == leadership:
        return "Intrigue or Leadership", intrigue
    if intrigue > leadership:
        return "Intrigue", intrigue
    return "Leadership", leadership


def header(character: Character, *, two_lines: bool = False) -> str:
    """The limit and how it is worked out, the recruited agents counted
    against it, those still being won, and the unspent Agency experience."""
    kept = ag.kept(character)
    pending = ag.pending(character)
    limit = ag.character_max_agents(character)
    name, level = _better(character)
    presence = character.characteristics.presence
    gift = gift_penalty(character)
    shown = "[$text-error]" if kept > limit else "[b]"
    first = (
        f"Agents: {shown}{kept} of {limit}[/] [dim](2 x (Presence {presence} + "
        f"{name} {level} - Gift {gift}), at least 1; LoM p. 22)[/]"
    )
    rest = (f"{pending} being recruited  ·  " if pending else "") + (
        f"Agency experience: [b]{character.agency_xp}[/] unspent"
    )
    return first + ("\n" if two_lines else "  ·  ") + rest


def _bond(agent: Agent) -> str:
    if not ag.recruited(agent):
        return "[dim]—[/]"
    return f"{escape(agent.bond_trait or 'Bond')} {agent.bond:+d}"


def _resistance(agent: Agent) -> str:
    if ag.recruited(agent):
        return "[$text-success]agent[/]"
    now = ag.current_resistance(agent)
    return f"{now}, impressed" if agent.impressed else str(now)


def table(character: Character) -> Table:
    """The desktop's ledger: name, Social Status, Bond, resistance and
    resources."""
    return Table(
        list(COLUMNS),
        [
            [
                escape(a.name or "(unnamed)"),
                status_label(a) + (", coerced" if a.coerced else ""),
                _bond(a),
                _resistance(a),
                escape(a.resources),
            ]
            for a in character.agents
        ],
        markup=True,
        stretch=4,
    )


def table_header() -> str:
    """The terminal list's column titles (after its two-character marker)."""
    return (
        "  "
        + "".join(
            fit(words, width) for words, width in zip(COLUMNS, WIDTHS, strict=False)
        )
        + COLUMNS[-1]
    )


def _cell(plain: str, width: int, colour: str = "") -> str:
    """`plain` fitted to `width` and escaped, in `colour` if given."""
    cell = escape(fit(plain, width))
    return f"[{colour}]{cell}[/]" if colour else cell


def rows(character: Character) -> list[tuple[int | None, str]]:
    """The terminal list's rows: (index, row)."""
    if not character.agents:
        return [
            (
                None,
                "[dim]None: people won over through a personal bond (LoM "
                "p. 22). Add one with a.[/]",
            )
        ]
    found: list[tuple[int | None, str]] = []
    for n, a in enumerate(character.agents):
        name_w, status_w, bond_w, res_w = WIDTHS
        bond = (
            _cell(f"{a.bond_trait or 'Bond'} {a.bond:+d}", bond_w)
            if ag.recruited(a)
            else _cell("—", bond_w, "dim")
        )
        resistance = (
            _cell("agent", res_w, "$text-success")
            if ag.recruited(a)
            else _cell(
                f"{ag.current_resistance(a)}" + (", impressed" if a.impressed else ""),
                res_w,
            )
        )
        found.append(
            (
                n,
                _cell(a.name or "(unnamed)", name_w)
                + _cell(_short_status(a), status_w)
                + bond
                + resistance
                + escape(fit(a.resources, RESOURCES_WIDTH).rstrip()),
            )
        )
    return found


def recruitment_lines(agent: Agent, *, short: bool = False) -> list[str]:
    """The Agent Recruitment Table lines that make up his starting
    resistance (p. 23), each with its figure (`short`: in fewer words)."""
    label, value = ag.STATUS_RESISTANCE.get(agent.status, ag.STATUS_RESISTANCE["free"])
    lines = [(label.split(" (")[0], value)]
    chosen = [m for m in dict.fromkeys(agent.modifiers) if m in ag.MODIFIERS]
    lines += [(_modifier_label(m, short=short), ag.MODIFIERS[m][1]) for m in chosen]
    resources = sum(1 for m in chosen if ag.MODIFIERS[m][2])
    if resources > 6:
        lines.append(("More than six resources", 9))
    elif resources > 3:
        lines.append(("More than three resources", 6))
    return [f"{words} {figure:+d}" for words, figure in lines]


def _persuader(character: Character, name: str | None = None) -> tuple[str, int]:
    """The Ability a persuasion uses: `name`, or his best of the three."""
    if name in PERSUADERS:
        return name, scores.ability_level(character, name)
    found = [(n, scores.ability_level(character, n)) for n in PERSUADERS]
    return max(found, key=lambda pair: pair[1])


def persuasion(
    character: Character, agent: Agent, ability: str | None = None
) -> tuple[int, str]:
    """What a die adds to, to set him a task, and its terms."""
    communication = character.characteristics.communication
    gift = gift_penalty(character)
    name, level = _persuader(character, ability)
    total = ag.persuasion_total(communication, level, agent.bond, gift)
    return total, (
        f"Communication {communication} + {name} {level} + Bond {agent.bond} "
        f"- Gift {gift}"
    )


def _impress_terms(character: Character) -> tuple[int, str]:
    presence = character.characteristics.presence
    leadership = scores.ability_level(character, "Leadership")
    gift = gift_penalty(character)
    return ag.impress_total(presence, leadership, gift), (
        f"Presence {presence} + Leadership {leadership} - Gift {gift}"
    )


def _die_needed(ease: int, total: int) -> str:
    need = ease - total
    return "any" if need <= 0 else f"{need}+"


#: The Tasks for Agents table's rows (p. 24), shortened for the panel.
_INFORMATION = (
    ("common", "Common, easily had"),
    ("sensitive", "Sensitive, hard to get"),
    ("secret", "Secret, known to a few"),
)
_DEEDS = (
    ("easy", "Easy task (EF 6 or less)"),
    ("hard", "Hard task (EF 12 or less)"),
    ("impressive", "Impressive (EF 18 or less)"),
)
_ADJUSTMENTS = (
    "Haste +1 in days, +3 in a day  ·  Risk +1 reputation, +3 injury, "
    "+6 death (1/3/5 botch dice)"
)


def _coercion_lines(agent: Agent) -> list[str]:
    lines: list[str] = []
    if agent.coerced:
        lines.append(
            "[$text-warning]Held by coercion: he thinks you his inferior. You "
            "have Difficult Underlings for him, and he a Story Flaw such as "
            "Blackmail or Dark Secret (LoM pp. 22-23).[/]"
        )
    elif "dominated" in agent.modifiers:
        lines.append(
            "[$text-warning]Dominated through a Flaw, he hates you: Difficult "
            "Underlings for him only (LoM p. 23).[/]"
        )
    return lines


def info(character: Character, index: int | None, *, wide: bool) -> str:
    """The chosen agent's details: how his resistance was set, whether he
    is impressed and what winning him needs, and for an agent his Bond,
    persuasion and the Tasks for Agents table. `wide`: the terminal's
    panel (the tasks in two columns); otherwise the desktop inspector's
    (bulleted lists)."""
    if index is None or not 0 <= index < len(character.agents):
        # One line, as every details panel's hint is.
        return "[dim]Choose an agent to see how he was won and what he can be asked.[/]"
    a = character.agents[index]
    start = ag.starting_resistance(a)
    lines: list[str] = []
    if wide:
        state = "an agent" if ag.recruited(a) else "being recruited"
        lines.append(
            f"[b]{escape(a.name)}[/]  [dim]{status_label(a)} · {state}"
            + (f" · {escape(a.resources)}" if a.resources else "")
            + "[/]"
        )
        lines.append(
            f"[$label]Resistance[/] [b]{start}[/] [dim]({LOM} p. 23)[/]: "
            + ", ".join(recruitment_lines(a, short=True))
        )
    else:
        lines.append(f"[$label]Agent Recruitment Table[/] [dim]({LOM} p. 23)[/]")
        lines += [f"{BULLET} {line}" for line in recruitment_lines(a)]
        lines.append(f"Resistance [b]{start}[/]")
        lines.append("")
    lines += _coercion_lines(a)
    if not a.impressed and not ag.recruited(a):
        total, terms = _impress_terms(character)
        now = ag.current_resistance(a)
        lines.append(
            f"[$label]Impressed:[/] not yet. Stress die + [b]{total}[/] ({terms}) "
            f"against {ag.IMPRESS_EASE} [dim]({LOM} p. 24)[/]; a failure waits "
            "for another story."
        )
        lines.append(
            f"Once impressed, {ag.xp_to_recruit(now)} Agency experience wears his "
            f"resistance of {now} to nothing ({character.agency_xp} unspent)."
        )
        return _finish(lines, a)
    if not ag.recruited(a):
        now = ag.current_resistance(a)
        steps = " + ".join(str(n) for n in range(now, 0, -1))
        lines.append(
            f"[$label]Impressed:[/] yes. Resistance now [b]{now}[/]: "
            f"{ag.xp_to_recruit(now)} Agency experience recruits him ({steps}); "
            f"{character.agency_xp} unspent [dim]({LOM} p. 24)[/]."
        )
        lines.append(
            "[dim]Recruited, his Bond starts at 0; tasks need a Bond of +1.[/]"
        )
        return _finish(lines, a)
    need = ag.XP_PER_LEVEL * (a.bond + 1)
    lines.append(
        f"[$label]Impressed:[/] yes  ·  [$label]Bond:[/] [b]"
        f"{escape(a.bond_trait or 'Bond')} {a.bond:+d}[/] [dim]({a.bond_xp} of "
        f"{need} xp to {a.bond + 1:+d}; LoM p. 25)[/]"
    )
    if not ag.may_be_asked(a):
        lines.append("[$text-error]A Bond of +1 is needed before he takes a task.[/]")
        return _finish(lines, a)
    total, terms = persuasion(character, a)
    lines.append(f"[$label]Persuasion:[/] stress die + [b]{total}[/] [dim]= {terms}[/]")
    if wide:
        lines.append(f"[$label]Tasks for Agents[/] [dim]({LOM} p. 24)[/]")
        lines.append(
            f"  [dim]{'Information':<26}{'Ease':>5}  {'Die':<6}    "
            f"{'Deeds':<28}{'Ease':>5}  {'Die':<6}[/]"
        )
        for (i_key, i_words), (d_key, d_words) in zip(
            _INFORMATION, _DEEDS, strict=True
        ):
            i_ease, d_ease = ag.TASKS[i_key][1], ag.TASKS[d_key][1]
            lines.append(
                f"  {i_words:<26}{i_ease:>5}  {_die_needed(i_ease, total):<6}    "
                f"{d_words:<28}{d_ease:>5}  {_die_needed(d_ease, total):<6}"
            )
        lines.append(f"  [dim]{_ADJUSTMENTS}[/]")
    else:
        lines.append("")
        lines.append(f"[$label]Tasks for Agents[/] [dim]({LOM} p. 24)[/]")
        lines.append("[i]Ease Factor, and the die he needs[/]")
        for heading, keys in (("Information", _INFORMATION), ("Deeds", _DEEDS)):
            lines.append(f"[b]{heading}[/]")
            for key, words in keys:
                ease = ag.TASKS[key][1]
                lines.append(
                    f"{BULLET} {words.split(',')[0]} {ease}: "
                    f"[b]{_die_needed(ease, total)}[/]"
                )
        lines.append(f"[dim]{_ADJUSTMENTS}[/]")
    return _finish(lines, a)


def _finish(lines: list[str], agent: Agent) -> str:
    if agent.notes:
        lines.append(f"[$label]Notes:[/] {escape(agent.notes)}")
    return "\n".join(lines)


def inspector_title(character: Character, index: int) -> tuple[str, str]:
    """The inspector's heading and the line under it for the chosen agent."""
    a = character.agents[index]
    state = "An agent" if ag.recruited(a) else "Being recruited"
    return a.name or "(unnamed)", f"{state}  ·  {status_label(a)}"


# -- the agent's form --

#: The form's key for each Agent Recruitment Table modifier.
_MOD_KEYS = {key: f"mod_{key}" for key in ag.MODIFIERS}


def fields(existing: Agent | None) -> list[DialogField]:
    a = existing or Agent("")
    found = [
        DialogField("not_agents", "Who counts", "info", NOT_AGENTS),
        DialogField(
            "name",
            "Name",
            "text",
            a.name,
            required=True,
            placeholder="e.g. Udo the Miller",
        ),
        DialogField(
            "status",
            "Social Status",
            "select",
            a.status,
            options=[
                (f"{label} {value:+d}", key)
                for key, (label, value) in ag.STATUS_RESISTANCE.items()
            ],
            hint="His Social Status Virtue or Flaw (LoM p. 23).",
        ),
        DialogField(
            "coerced",
            "Thinks you his inferior (held by coercion)",
            "check",
            a.coerced,
            hint="You gain Difficult Underlings for him; he has a Story Flaw "
            "such as Blackmail or Dark Secret (LoM pp. 22-23).",
        ),
    ]
    for key, (label, change, _resource) in ag.MODIFIERS.items():
        found.append(
            DialogField(
                _MOD_KEYS[key], f"{label} ({change:+d})", "check", key in a.modifiers
            )
        )
    found += [
        DialogField(
            "resources",
            "Resources",
            "text",
            a.resources,
            placeholder="What you gain through him: Abilities, wealth, men",
        ),
        DialogField(
            "impressed",
            "Impressed",
            "check",
            a.impressed,
            hint="Stress die + Presence + Leadership - Gift against 6 (LoM p. 24).",
        ),
        DialogField(
            "resistance",
            "Resistance left (blank: the table's; 0: recruited)",
            "optint",
            a.resistance,
        ),
        DialogField(
            "bond_trait",
            "Bond",
            "text",
            a.bond_trait,
            placeholder="Why he is drawn to you, e.g. Loves wife",
        ),
        DialogField("bond", "Bond score", "int", a.bond, hint="A new agent's is 0."),
        DialogField("bond_xp", "Bond experience", "int", a.bond_xp),
        DialogField("notes", "Notes", "text", a.notes),
    ]
    return found


def _made(values: dict[str, Any], existing: Agent | None) -> Agent:
    resistance = values.get("resistance")
    made = replace(
        existing or Agent(""),
        name=values.get("name") or "",
        status=values.get("status") or "free",
        coerced=bool(values.get("coerced")),
        modifiers=[key for key, field in _MOD_KEYS.items() if values.get(field)],
        resources=values.get("resources") or "",
        impressed=bool(values.get("impressed")),
        resistance=None if resistance is None else max(0, int(resistance)),
        bond_trait=values.get("bond_trait") or "",
        bond=max(0, int(values.get("bond") or 0)),
        bond_xp=max(0, int(values.get("bond_xp") or 0)),
        notes=values.get("notes") or "",
    )
    if made.resistance == 0:
        # An agent has been impressed and won.
        made.impressed = True
    return made


def live(character: Character, index: int | None) -> Any:
    """The form's inspector: the resistance the choices so far give him."""

    def inspect(values: dict[str, Any]) -> str:
        existing = character.agents[index] if index is not None else None
        draft = _made(values, existing)
        start = ag.starting_resistance(draft)
        lines = [
            f"[b]{escape(draft.name or 'This agent')}[/]  "
            f"[$label]{status_label(draft)}[/]",
            f"[i]Resistance {start} on the Agent Recruitment Table (LoM p. 23): "
            + ", ".join(recruitment_lines(draft))
            + ".[/]",
        ]
        if ag.recruited(draft):
            lines.append("An agent: counted against your limit.")
        else:
            now = ag.current_resistance(draft)
            lines.append(
                f"Being recruited, not yet counted: {ag.xp_to_recruit(now)} Agency "
                f"experience wears a resistance of {now} to nothing"
                + ("." if draft.impressed else ", once he is impressed.")
            )
        lines += _coercion_lines(draft)
        return "\n".join(lines)

    return inspect


def ops(character: Character) -> SectionOps:
    """Add, Edit and Delete on the Agents list; a row is the agent's index."""

    def form(index: int | None) -> Form:
        existing = character.agents[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _made(values, existing)
            if index is None:
                character.agents.append(made)
            else:
                character.agents[index] = made

        return Form(
            "Add an Agent" if index is None else "Edit an Agent",
            lambda: fields(existing),
            apply,
            live=live(character, index),
            save_label="Add" if index is None else "Save",
            help_id=AGENTS_SECTION,
            inspector="The Agent",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            character.agents, index, character.agents[index].name or "the agent"
        ),
        rows=lambda: [a.name or "(unnamed)" for a in character.agents],
    )


# -- More: Impress, Spend Agency Experience, Set a Task --


def _chosen(character: Character, index: int, what: str) -> Agent | Refuse:
    if not 0 <= index < len(character.agents):
        return Refuse(what, "Choose an agent first.")
    return character.agents[index]


def impress(
    saga: Saga, character: Character, index: int, rng: random.Random | None = None
) -> Command:
    """Impress: a stress die + Presence + Leadership - the Gift's penalty
    against 6 (p. 24). A failure waits for another story."""
    agent = _chosen(character, index, "Impress")
    if isinstance(agent, Refuse):
        return agent
    if not ag.can_impress(agent):
        return Refuse("Impress", f"{escape(agent.name)} is already impressed.")
    total, terms = _impress_terms(character)

    def apply() -> list[str]:
        roll = dice.Roll(
            total,
            dice.stress_die(rng or random.Random(), saga=saga),
            ag.IMPRESS_EASE,
        )
        shown = "a botch" if roll.die.botched else str(roll.die.value)
        if roll.succeeded:
            agent.impressed = True
            if agent.resistance is None:
                agent.resistance = ag.starting_resistance(agent)
        return notes(
            f"Impress {escape(agent.name)}: the die shows {shown}, + {total} "
            f"({terms}) = {roll.total} against {ag.IMPRESS_EASE}.",
            f"{escape(agent.name)} is impressed: Agency experience can now wear "
            "his resistance down."
            if roll.succeeded
            else "He is not impressed: try again in another story (LoM p. 24).",
        )

    return Act(apply)


def _spend_fields(character: Character, agent: Agent) -> list[DialogField]:
    if ag.recruited(agent):
        need = ag.XP_PER_LEVEL * (agent.bond + 1) - agent.bond_xp
        how = [
            ("Raise his Bond with Agency experience (LoM p. 25)", "bond"),
            (f"Raise his Bond with money ({ag.XP_PER_POUND} a pound)", "pounds"),
        ]
        default = "bond" if character.agency_xp else "pounds"
    else:
        need = ag.xp_to_recruit(ag.current_resistance(agent))
        how = [("Wear down his resistance (LoM p. 24)", "resistance")]
        default = "resistance"
    return [
        DialogField(
            "unspent",
            "Unspent",
            "info",
            f"{character.agency_xp} Agency experience; {character.silver} pounds "
            "of silver carried.",
        ),
        DialogField("how", "Spend on", "select", default, options=how),
        DialogField(
            "xp",
            "Agency experience",
            "int",
            max(0, min(character.agency_xp, need)),
            show_if=lambda v: v.get("how") != "pounds",
        ),
        DialogField(
            "pounds",
            "Pounds",
            "int",
            1,
            show_if=lambda v: v.get("how") == "pounds",
            hint="Fails for an agent already prosperous, or who thinks taking "
            "money for service a crime or sin (LoM p. 25).",
        ),
    ]


def _spend_preview(
    character: Character, agent: Agent, values: dict[str, Any]
) -> tuple[Agent, ag.Spent, int]:
    """What spending `values` would do, on a copy: the agent after, what
    it did, and the Agency experience it uses."""
    trial = replace(agent, modifiers=list(agent.modifiers))
    how = values.get("how")
    if how == "pounds":
        spent = ag.strengthen(trial, ag.xp_for_pounds(int(values.get("pounds") or 0)))
        return trial, spent, 0
    xp = max(0, int(values.get("xp") or 0))
    if how == "resistance":
        spent = ag.wear_down(trial, xp)
        return trial, spent, xp - spent.left
    return trial, ag.strengthen(trial, xp), xp


def spend(character: Character, index: int) -> Command:
    """Spend Agency Experience on the chosen agent: wear an impressed
    potential agent's resistance down (1 for as many points as it stands
    at, p. 24), or raise an agent's Bond as an Ability rises, with Agency
    experience or with money at 5 points a pound (p. 25)."""
    agent = _chosen(character, index, "Spend Agency Experience")
    if isinstance(agent, Refuse):
        return agent
    if not ag.can_spend(character, agent):
        why = (
            "impress him first"
            if not agent.impressed
            else "there is no Agency experience to spend"
        )
        return Refuse(
            "Spend Agency Experience", f"Not for {escape(agent.name)}: {why}."
        )

    def validate(values: dict[str, Any]) -> str | None:
        if values.get("how") == "pounds":
            pounds = int(values.get("pounds") or 0)
            if pounds < 1:
                return "Spend at least a pound."
            if pounds > character.silver:
                return (
                    f"{escape(character.name)} carries only {character.silver} pounds."
                )
            return None
        xp = int(values.get("xp") or 0)
        if xp < 1:
            return "Spend at least 1 Agency experience."
        if xp > character.agency_xp:
            return f"Only {character.agency_xp} Agency experience is unspent."
        if values.get("how") == "resistance" and xp < ag.current_resistance(agent):
            return (
                f"Wearing a resistance of {ag.current_resistance(agent)} down by "
                f"one takes {ag.current_resistance(agent)} Agency experience."
            )
        return None

    def preview(values: dict[str, Any]) -> str:
        after, spent, used = _spend_preview(character, agent, values)
        lines = [f"[b]{escape(agent.name)}[/]"]
        if values.get("how") == "resistance":
            lines.append(
                f"Resistance {ag.current_resistance(agent)} to [b]"
                f"{ag.current_resistance(after)}[/], for {used} Agency experience"
                + (f" ({spent.left} left over, kept)." if spent.left else ".")
            )
            if spent.recruited:
                lines.append("[$text-success]He becomes an agent, with a Bond of 0.[/]")
        else:
            lines.append(
                f"Bond {agent.bond:+d} to [b]{after.bond:+d}[/] "
                f"({after.bond_xp} of {ag.XP_PER_LEVEL * (after.bond + 1)} xp "
                f"to {after.bond + 1:+d})."
            )
        return "\n".join(lines)

    def apply(values: dict[str, Any]) -> list[str]:
        how = values.get("how")
        if how == "pounds":
            pounds = int(values.get("pounds") or 0)
            character.silver -= pounds
            spent = ag.strengthen(agent, ag.xp_for_pounds(pounds))
            return notes(
                f"{pounds} pounds for {ag.xp_for_pounds(pounds)} Agency experience: "
                f"{escape(agent.name)}'s Bond is {agent.bond:+d}"
                + (f" (+{spent.levels})." if spent.levels else ".")
            )
        xp = int(values.get("xp") or 0)
        if how == "resistance":
            spent = ag.wear_down(agent, xp)
            character.agency_xp -= xp - spent.left
            return notes(
                f"{escape(agent.name)}'s resistance is now {agent.resistance}.",
                f"{escape(agent.name)} is now your agent, with a Bond of 0."
                if spent.recruited
                else "",
            )
        spent = ag.strengthen(agent, xp)
        character.agency_xp -= xp
        return notes(f"{escape(agent.name)}'s Bond is {agent.bond:+d}.")

    return Form(
        f"Spend Agency Experience: {escape(agent.name)}",
        lambda: _spend_fields(character, agent),
        apply,
        validate=validate,
        live=preview,
        save_label="Spend",
        help_id=AGENTS_SECTION,
        inspector="What It Buys",
    )


def task_fields(character: Character, agent: Agent) -> list[DialogField]:
    best, _ = _persuader(character)
    return [
        DialogField(
            "ability",
            "Persuade with",
            "select",
            best,
            options=[
                (f"{name} {scores.ability_level(character, name)}", name)
                for name in PERSUADERS
            ],
            hint="Charm, Intrigue or Leadership, as suits the request (LoM p. 24).",
        ),
        DialogField(
            "task",
            "Task",
            "select",
            "common",
            options=[(label, key) for key, (label, _) in ag.TASKS.items()],
        ),
        DialogField(
            "timeframe",
            "Done",
            "select",
            "weeks",
            options=[(label, key) for key, (label, _) in ag.TIMEFRAME.items()],
        ),
        DialogField(
            "risk",
            "Risk to him",
            "select",
            "none",
            options=[(label, key) for key, (label, _, _) in ag.RISK.items()],
        ),
        DialogField(
            "what",
            "What he is asked",
            "text",
            "",
            placeholder="e.g. Learn what the bishop wrote to the duke",
        ),
    ]


def _task_terms(
    character: Character, agent: Agent, values: dict[str, Any]
) -> tuple[str, str, str, str, int, int, str]:
    task = values.get("task") or "common"
    timeframe = values.get("timeframe") or "weeks"
    risk = values.get("risk") or "none"
    ability = values.get("ability") or _persuader(character)[0]
    ease = ag.task_ease(task, timeframe, risk)
    total, terms = persuasion(character, agent, ability)
    return task, timeframe, risk, ability, ease, total, terms


def task_live(character: Character, agent: Agent) -> Any:
    """Set a Task's inspector: the Ease Factor, the persuasion total and
    the botch dice, from the same terms the roll uses."""

    def inspect(values: dict[str, Any]) -> str:
        task, timeframe, risk, _ability, ease, total, terms = _task_terms(
            character, agent, values
        )
        label, base = ag.TASKS[task]
        risk_label, risk_change, botch = ag.RISK[risk]
        die = "a stress die" if botch is not None else "a simple die"
        botches = f", {botch} botch {'die' if botch == 1 else 'dice'}" if botch else ""
        return "\n".join(
            [
                f"[b]{escape(agent.name)}[/]  "
                f"[$label]{escape(agent.bond_trait or 'Bond')} {agent.bond:+d}[/]",
                f"[i]{label}, {ag.TIMEFRAME[timeframe][0].lower()}, "
                + (
                    "at no risk to him"
                    if botch is None
                    else f"risking {risk_label.lower()}"
                )
                + ".[/]",
                f"Ease Factor [b]{ease}[/] [dim](task {base} + haste "
                f"{ag.TIMEFRAME[timeframe][1]} + risk {risk_change}; LoM p. 24)[/]",
                f"Persuasion: {die} + [b]{total}[/] [dim]({terms})[/]{botches}",
                f"He takes it on with a die of [b]{_die_needed(ease, total)}[/].",
            ]
        )

    return inspect


def set_task(
    saga: Saga, character: Character, index: int, rng: random.Random | None = None
) -> Command:
    """Set a Task: the persuasion roll, a stress die (a simple one with no
    risk to him) + Communication + the chosen Ability + Bond - the Gift's
    penalty against the task's Ease Factor (p. 24). He needs a Bond of +1."""
    agent = _chosen(character, index, "Set a Task")
    if isinstance(agent, Refuse):
        return agent
    if not ag.may_be_asked(agent):
        return Refuse(
            "Set a Task",
            f"{escape(agent.name)} needs to be an agent with a Bond of +1 or "
            "more before he takes a task (LoM p. 24).",
        )

    def apply(values: dict[str, Any]) -> list[str]:
        task, _timeframe, risk, ability, ease, total, _terms = _task_terms(
            character, agent, values
        )
        botch = ag.RISK[risk][2]
        source = rng or random.Random()
        die = (
            dice.simple_roll(source)
            if botch is None
            else dice.stress_die(source, botch, saga=saga)
        )
        roll = dice.Roll(total, die, ease)
        shown = (
            f"a botch ({die.botches} zero{'s' if die.botches > 1 else ''})"
            if die.botched
            else str(die.value)
        )
        what = (values.get("what") or "").strip()
        return notes(
            f"{escape(agent.name)}"
            + (f", asked to {escape(what)}" if what else "")
            + f": the die shows {shown}, + {total} ({ability}) = {roll.total} "
            f"against {ease}.",
            f"He takes the task on ({ag.TASKS[task][0].lower()})."
            if roll.succeeded
            else "He refuses"
            + (", and the botch costs him dearly." if die.botched else "."),
        )

    return Form(
        f"Set a Task: {escape(agent.name)}",
        lambda: task_fields(character, agent),
        apply,
        live=task_live(character, agent),
        save_label="Roll",
        help_id=AGENTS_SECTION,
        inspector="The Task",
    )
