"""Advance Season's Experiment results step, independent of how it is drawn:
one form per experiment of the season with anything for the storyguide to
decide (seasons.experiment_results), then a spell form for each spell a
special result lets the magus also create.

Each roll's fields are keyed by its prefix ("a" the first roll, "b" the
second of two dice) and shown only while that roll is chosen to stand.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .. import research_text, seasons
from ..commands import Form
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import SPELL_DURATIONS, SPELL_RANGES, SPELL_TARGETS, Character, Saga
from ..rules import enchant_seasons as es
from ..rules import experiment as ex
from ..rules import lab_seasons
from ..rules.activities import Outcome
from . import saga_content

#: What a modified effect's figures can change: nothing (it is only
#: described), or one of these.
PARAMETERS: tuple[tuple[str, str], ...] = (
    ("No figure changes (describe it)", "none"),
    ("Range", "range"),
    ("Duration", "duration"),
    ("Target", "target"),
    ("Potency", "potency"),
)
_STANDARD = {
    "range": SPELL_RANGES,
    "duration": SPELL_DURATIONS,
    "target": SPELL_TARGETS,
}
#: The two rolls of two dice, as their field prefixes.
_ROLLS = ("a", "b")


def creation(outcome: Outcome) -> str:
    """What the experiment's effects fall on: "spell" (an invention),
    "effect" (an instilled effect), "investigate" (an item's powers),
    "longevity" (a ritual), or "other" (described only)."""
    work = outcome.lab_work
    activity = outcome.plan.activity
    if activity == lab_seasons.INVENT:
        return "spell"
    if activity == es.INVESTIGATE:
        return "investigate"
    if activity == lab_seasons.LONGEVITY:
        return "longevity"
    if work is not None and work.effect is not None:
        return "effect"
    return "other"


def _shown(prefix: str) -> Callable[[dict[str, Any]], bool]:
    return lambda values: (values.get("roll") or "a") == prefix


def _both(
    first: Callable[[dict[str, Any]], bool], second: Callable[[dict[str, Any]], bool]
) -> Callable[[dict[str, Any]], bool]:
    return lambda values: first(values) and second(values)


def _roll_text(chart: ex.Extraordinary) -> str:
    return " ".join(r for r in chart.results if not r.startswith("A second roll"))


def experiment_fields(saga: Saga, outcome: Outcome) -> list[DialogField]:
    """One experiment's questions: which roll stands (with two dice), then
    for each roll its effects, Discoveries, special results, a Disaster's
    choice and the move onto a Discovery."""
    magus = saga.character(outcome.character_id)
    work = outcome.lab_work
    assert magus is not None and work is not None and work.experiment is not None
    chart = work.experiment
    fields = [
        DialogField(
            "_what",
            "",
            "info",
            f"{escape(magus.name)}: "
            f"{escape(seasons.plan_summary(saga, magus, outcome.plan))}.",
        )
    ]
    rolls = [chart] if chart.other is None else [chart, chart.other]
    if chart.other is not None:
        fields.append(
            DialogField(
                "roll",
                "Which roll stands",
                "select",
                "a",
                options=[
                    (f"First roll: {_roll_text(chart)}", "a"),
                    (f"Second roll: {_roll_text(chart.other)}", "b"),
                ],
                hint="Two dice (Exciting Experimentation or Creative Block): the "
                "storyguide applies the more amusing.",
            )
        )
    else:
        fields.append(DialogField("_roll", "", "info", _roll_text(chart)))
    for prefix, roll in zip(_ROLLS, rolls, strict=False):
        fields += _roll_fields(saga, magus, outcome, prefix, roll)
    return fields


def _roll_fields(
    saga: Saga, magus: Character, outcome: Outcome, prefix: str, chart: ex.Extraordinary
) -> list[DialogField]:
    shown = _shown(prefix)
    fields: list[DialogField] = []
    made = creation(outcome)
    for index, (effect, options) in enumerate(
        zip(chart.effects, chart.effect_options, strict=False)
    ):
        fields += _effect_fields(
            outcome, f"{prefix}_e{index}", effect, options, made, shown
        )
    for index, candidates in enumerate(chart.discoveries):
        fields += _discovery_fields(
            magus, outcome, f"{prefix}_d{index}", candidates, chart, shown
        )
    for index in range(chart.specials):
        fields += _special_fields(saga, magus, outcome, f"{prefix}_s{index}", shown)
    if chart.zeroes >= ex.DISASTER_CHOICE:
        fields.append(
            DialogField(
                f"{prefix}_disaster",
                "The Disaster (5 or more zeroes)",
                "select",
                "lab",
                options=[
                    ("The laboratory destroyed (Incapacitating Wounds)", "lab"),
                    ("A story event threatening the whole covenant", "covenant"),
                ],
                show_if=shown,
            )
        )
    if chart.item_at_risk:
        device = outcome.lab_work.device if outcome.lab_work else None
        fields.append(
            DialogField(
                f"{prefix}_protected",
                f"An effect of {escape(device.name) if device else 'the item'}'s "
                "own protects it",
                "check",
                False,
                hint="This result destroys the item investigated, unless one of "
                f"its effects protects it with a level above the Lab Total "
                f"({int(outcome.lab_work.lab_total.total) if outcome.lab_work else 0}).",
                show_if=shown,
            )
        )
    if chart.discovery_shift is not None:
        goal = outcome.plan.research.strip()
        fields += [
            DialogField(
                f"_{prefix}_move",
                "",
                "info",
                research_text.move_card(saga, magus, goal, outcome.plan.risk, chart),
                show_if=shown,
            ),
            DialogField(
                f"{prefix}_move", "Take the Discovery", "check", False, show_if=shown
            ),
        ]
    return fields


def _effect_fields(
    outcome: Outcome,
    key: str,
    effect,
    options: list[str],
    made: str,
    shown: Callable[[dict[str, Any]], bool],
) -> list[DialogField]:
    kind = "Side effect" if effect.kind == "side" else "Modified effect"
    fields = [
        DialogField(
            f"_{key}",
            "",
            "info",
            f"{kind}: {', or '.join(dict.fromkeys(options))}",
            show_if=shown,
        )
    ]
    if len(set(options)) > 1:
        fields.append(
            DialogField(
                f"{key}_result",
                "Which stands",
                "select",
                options[0],
                options=pairs(list(dict.fromkeys(options))),
                show_if=shown,
            )
        )
    fields.append(
        DialogField(
            f"{key}_description",
            "What it is",
            "text",
            "",
            placeholder="e.g. the spell smells of cinnamon",
            hint="May be left blank and described later, on the "
            + ("ritual" if made == "longevity" else "creation")
            + "'s experimental effects.",
            show_if=shown,
        )
    )
    if made == "investigate":
        device = outcome.lab_work.device if outcome.lab_work else None
        powers = [
            (p.name or "(unnamed)", p.id) for p in (device.effects if device else [])
        ]
        if powers:
            fields.append(
                DialogField(
                    f"{key}_power",
                    "The power it falls on",
                    "select",
                    powers[0][1],
                    options=powers,
                    show_if=shown,
                )
            )
    if effect.kind != "modified":
        return fields
    step = -1 if effect.result == ex.REDUCED else 1
    if made == "longevity":
        fields.append(
            DialogField(
                f"{key}_potency",
                "Potency (steps)",
                "int",
                step if effect.result in (ex.REDUCED, ex.INCREASED) else 0,
                hint="Each step moves the ritual's modifier by 1 (5 Lab Total): "
                "the app's reading, as the rules give no size.",
                show_if=shown,
            )
        )
        return fields
    if made not in ("spell", "effect", "investigate"):
        return fields
    parameter = f"{key}_parameter"
    fields.append(
        DialogField(
            parameter,
            "What changes",
            "select",
            "none",
            options=list(PARAMETERS),
            hint="The level never changes and no requisite is added.",
            show_if=shown,
        )
    )
    for name, standard in _STANDARD.items():
        fields.append(
            DialogField(
                f"{key}_{name}",
                f"New {name.title()}",
                "select",
                None,
                options=pairs(standard),
                allow_blank=True,
                show_if=_both(shown, lambda v, p=parameter, n=name: v.get(p) == n),
            )
        )
    fields.append(
        DialogField(
            f"{key}_potency",
            "Potency (steps)",
            "int",
            step,
            hint="Each step is 5 points of the Lab Total behind the effect "
            "(the app's reading, as the rules give no size); recorded on it.",
            show_if=_both(shown, lambda v, p=parameter: v.get(p) == "potency"),
        )
    )
    return fields


def _discovery_fields(
    magus: Character,
    outcome: Outcome,
    key: str,
    candidates: list[int],
    chart: ex.Extraordinary,
    shown: Callable[[dict[str, Any]], bool],
) -> list[DialogField]:
    assert outcome.lab_work is not None
    technique, form = lab_seasons.made_arts(outcome.lab_work, outcome.plan)
    fields = [
        DialogField(
            f"_{key}",
            "",
            "info",
            "Discovery: roll "
            + ", or ".join(str(c) for c in dict.fromkeys(candidates)),
            show_if=shown,
        )
    ]
    roll_key = f"{key}_roll"
    if len(set(candidates)) > 1:
        fields.append(
            DialogField(
                roll_key,
                "Which roll stands",
                "select",
                str(candidates[0]),
                options=[(str(c), str(c)) for c in dict.fromkeys(candidates)],
                show_if=shown,
            )
        )

    def kind(values: dict[str, Any]) -> str:
        roll = values.get(roll_key) or candidates[0]
        return ex.discovery_kind(int(roll))

    abilities = sorted({a.name for a in magus.abilities} | {"Magic Theory"})
    fields += [
        DialogField(
            f"{key}_ability",
            "The Ability it teaches (15 xp)",
            "select",
            "Magic Theory",
            options=pairs(abilities),
            hint="An Ability related to the experiment.",
            show_if=_both(shown, lambda v: kind(v) == "ability"),
        ),
        DialogField(
            f"{key}_art",
            "The Art it teaches",
            "select",
            chart.art if chart.art in (technique, form) else technique,
            options=pairs(list(dict.fromkeys((technique, form)))),
            show_if=_both(shown, lambda v: kind(v) in ("art", "next")),
        ),
    ]
    return fields


def _special_fields(
    saga: Saga,
    magus: Character,
    outcome: Outcome,
    key: str,
    shown: Callable[[dict[str, Any]], bool],
) -> list[DialogField]:
    choice = f"{key}_kind"
    need = seasons.vis_needed(outcome)
    to_hand = seasons.vis_to_hand(saga, magus, outcome)
    held = ", ".join(f"{art} {pawns}" for art, pawns in to_hand.items()) or "none"
    return [
        DialogField(
            choice,
            "Special result",
            "select",
            "story",
            options=[(label, key) for key, label in ex.SPECIALS],
            show_if=shown,
        ),
        DialogField(
            f"{key}_text",
            "What happens",
            "text",
            "",
            placeholder="e.g. a salamander takes an interest in the lab",
            hint="A story event goes into the laboratory's and the covenant's "
            "Diaries (open).",
            show_if=_both(shown, lambda v: v.get(choice) in ("story", "changed")),
        ),
        DialogField(
            f"_{key}_vis",
            "",
            "info",
            f"It needs {need} pawn(s) of the project's Technique or Form vis "
            f"(to hand: {held}); without them it is a Complete Failure.",
            show_if=_both(shown, lambda v: v.get(choice) == "vis"),
        ),
        DialogField(
            f"_{key}_spell",
            "",
            "info",
            "The spell's form opens next: the same Technique and Form, up to "
            f"level {seasons.bonus_spell_limit(outcome)}, with a Lab Text.",
            show_if=_both(shown, lambda v: v.get(choice) == "spell"),
        ),
    ]


def settlement(chart: ex.Extraordinary, values: dict[str, Any]) -> ex.Settlement:
    """The storyguide's answers, from the form's values."""
    second = chart.other is not None and values.get("roll") == "b"
    prefix = "b" if second else "a"
    roll = chart.other if second and chart.other is not None else chart
    effects = []
    for index, effect in enumerate(roll.effects):
        key = f"{prefix}_e{index}"
        parameter = values.get(f"{key}_parameter") or "none"
        choice = ex.EffectChoice(
            result=values.get(f"{key}_result") or effect.result,
            description=values.get(f"{key}_description") or "",
            power=values.get(f"{key}_power") or "",
        )
        if parameter in _STANDARD:
            setattr(choice, parameter, values.get(f"{key}_{parameter}") or "")
        if parameter == "potency" or f"{key}_parameter" not in values:
            choice.potency = int(values.get(f"{key}_potency") or 0)
        effects.append(choice)
    discoveries = []
    for index, candidates in enumerate(roll.discoveries):
        key = f"{prefix}_d{index}"
        discoveries.append(
            ex.DiscoveryChoice(
                roll=int(values.get(f"{key}_roll") or candidates[0]),
                ability=values.get(f"{key}_ability") or "Magic Theory",
                art=values.get(f"{key}_art") or "",
            )
        )
    specials = [
        ex.SpecialChoice(
            values.get(f"{prefix}_s{index}_kind") or "story",
            values.get(f"{prefix}_s{index}_text") or "",
        )
        for index in range(roll.specials)
    ]
    return ex.Settlement(
        second=second,
        effects=effects,
        discoveries=discoveries,
        specials=specials,
        disaster=values.get(f"{prefix}_disaster") or "",
        move=bool(values.get(f"{prefix}_move")),
        protected=bool(values.get(f"{prefix}_protected")),
    )


def experiment_results(
    saga: Saga, worked: list[Any], then: Callable[[], Any], rng: Callable[[], Any]
):
    """The first experiment's form (each one's apply goes on to the next,
    by way of any spell forms its special results open), then `then`."""
    found = seasons.experiments_to_settle(saga, worked)

    def step(index: int):
        if index >= len(found):
            return then()
        outcome = found[index]
        magus = saga.character(outcome.character_id)
        assert magus is not None and outcome.lab_work is not None

        def apply(values: dict[str, Any]):
            work = outcome.lab_work
            assert work is not None and work.experiment is not None
            chosen = settlement(work.experiment, values)
            seasons.settle_experiment(saga, outcome, chosen, rng())
            spells = sum(1 for s in chosen.specials if s.kind == "spell")
            return _spell_forms(outcome, spells, lambda: step(index + 1))

        return Form(
            f"Experiment Results: {escape(magus.name)}",
            lambda: experiment_fields(saga, outcome),
            apply,
            save_label="Continue",
            help_id="advance-experiment-results",
        )

    return step(0)


def _spell_forms(outcome: Outcome, count: int, then: Callable[[], Any]):
    """`count` spell forms, one after another, each spell kept on the
    experiment to be created when the season is applied; then `then`."""
    if count <= 0:
        return then()
    work = outcome.lab_work
    assert work is not None and work.experiment is not None
    chart = work.experiment
    technique, form = lab_seasons.made_arts(work, outcome.plan)
    limit = seasons.bonus_spell_limit(outcome)

    def fields() -> list[DialogField]:
        found = saga_content.spell_fields(None)
        for spec in found:
            if spec.key == "technique":
                spec.value = technique
            elif spec.key == "form":
                spec.value = form
        return found

    def validate(values: dict[str, Any]) -> str | None:
        problem = saga_content.spell_problem(values)
        if problem:
            return problem
        if (values.get("technique"), values.get("form")) != (technique, form):
            return f"The spell is {technique} {form}, as the project is."
        level = values.get("level")
        if level is None or level > limit:
            return f"Its level is at most {limit}: one invented in a single season."
        return None

    def apply(values: dict[str, Any]):
        chart.bonus_spells.append(spell_values(values))
        return _spell_forms(outcome, count - 1, then)

    return Form(
        "The Spell the Magus Also Creates",
        fields,
        apply,
        validate=validate,
        live=saga_content.spell_live,
        save_label="Continue",
        help_id="advance-experiment-results",
    )


def spell_values(values: dict[str, Any]) -> dict[str, Any]:
    """A spell form's values as the spell's own fields."""
    from .. import spells as spl

    return {
        "name": values["name"],
        "technique": values["technique"],
        "form": values["form"],
        "level": values.get("level"),
        "requisites": spl.parse_requisites(values.get("requisites", "")),
        "range": saga_content.spell_rdt(values, "range"),
        "duration": saga_content.spell_rdt(values, "duration"),
        "target": saga_content.spell_rdt(values, "target"),
        "ritual": bool(values.get("ritual")),
        "base_level": values.get("base_level"),
        "description": values.get("description", ""),
    }
