"""The Ranges, Durations and Targets a magus may invent a spell with: the
standard ones, and beyond them only those a Virtue, a reached breakthrough
or a known spell opens; Other... only with the saga's optional rule."""

from __future__ import annotations

from test_experiment import _saga

from ars_magica_manager import spell_parameters as sp
from ars_magica_manager.forms.lab_plan import OTHER, LabPlanForm
from ars_magica_manager.models import (
    Breakthrough,
    KnownSpell,
    Spell,
    SpellDesign,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import integrations, lab_seasons, options
from ars_magica_manager.rules import spell_levels as sl


def _form(saga, design=None) -> LabPlanForm:
    magus = saga.character("m")
    return LabPlanForm(
        saga, magus, saga.laboratories[0], "Spring", 1220, None,
        design=design, activity=lab_seasons.INVENT,
    )  # fmt: skip


def _offered(form: LabPlanForm, kind: str) -> list[str]:
    return [v for _, v in form.parameter_options[kind]]


def _extras(form: LabPlanForm, kind: str) -> list[str]:
    standard = {"range": sl.RANGE_STEPS, "duration": sl.DURATION_STEPS}.get(
        kind, sl.TARGET_STEPS
    )
    return [v for v in _offered(form, kind) if v not in standard]


def test_ancient_magic_s_parameters_cost_as_the_book_says():
    assert sl.steps_of("range", "Veil of Death") == 3  # as Sight
    assert sl.steps_of("range", "Unlimited") == 6
    assert sl.steps_of("duration", "19 Years") == 5
    assert sl.steps_of("duration", "Event (Mom)") == 1
    assert sl.steps_of("duration", "Event (Moon)") == 4
    assert sl.steps_of("target", "Unborn Child") == 0
    assert sl.steps_of("duration", "Rune") == 3
    # Call to Arms: Base 4, +4 Arc, +1 Event [Mom], +2 Room, a Ritual: 35.
    design = sl.spell_level(4, "Arcane Connection", "Event (Mom)", "Room")
    assert design is not None and design.level == 35 and design.ritual_required


def test_a_magus_with_nothing_more_is_offered_the_standard_ones_and_no_other():
    saga = _saga()
    form = _form(saga)
    assert all(_extras(form, kind) == [] for kind in sp.KINDS)
    assert all(OTHER not in _offered(form, kind) for kind in sp.KINDS)


def test_the_saga_s_optional_rule_offers_other():
    saga = _saga()
    saga.rule_options[options.ANY_SPELL_PARAMETER] = True
    form = _form(saga)
    assert all(_offered(form, kind)[-1] == OTHER for kind in sp.KINDS)


def test_a_virtue_opens_its_parameters():
    saga = _saga()
    saga.character("m").virtues_flaws.append(VirtueFlawInstance("vf_canaanite_magic"))
    form = _form(saga)
    assert _extras(form, "range") == ["Veil of Death"]
    labels = {v: label for label, v in form.parameter_options["range"]}
    assert labels["Veil of Death"] == "Veil of Death (as Sight)"
    assert "Veil of Death: a Virtue" in next(
        f.hint for f in form.fields() if f.key == "range"
    )


def test_a_reached_breakthrough_opens_what_it_grants():
    saga = _saga()
    magus = saga.character("m")
    event = integrations.BY_NAME["Duration Event"]
    goal = Breakthrough(
        event.name, grant_kind=event.grant_kind, grant=event.grant, points=30
    )
    magus.breakthroughs.append(goal)
    assert _extras(_form(saga), "duration") == []  # not yet reached
    goal.reached = True
    assert _extras(_form(saga), "duration") == [
        "Event (Mom)",
        "Event (Diam)",
        "Event (Sun)",
        "Event (Moon)",
        "Event (Year)",
    ]


def test_a_troupe_s_own_parameter_costs_what_its_grant_says():
    saga = _saga()
    saga.character("m").breakthroughs.append(
        Breakthrough(
            "Horizon",
            grant_kind="Parameter",
            grant="Range: Horizon (as Sight +1)",
            reached=True,
        )
    )
    form = _form(saga)
    assert _extras(form, "range") == ["Horizon"]
    values = {f.key: f.value for f in form.fields()}
    values |= {"base_level": 5, "range": "Horizon"}
    design = form.design_of(values)
    assert design.range == "Horizon" and design.custom_steps == {"range": 4}
    worked = sl.spell_level(
        5, "Horizon", "Momentary", "Individual", custom_steps={"range": 4}
    )
    assert worked is not None and worked.level == 25


def test_a_grant_naming_nothing_opens_nothing():
    assert sp.parse_grant("Range: Horizon") == []  # no cost given
    assert sp.parse_grant("Horizon (as Sight)") == []  # no kind
    assert sp.parse_grant("Range: Voice (as Sight)") == []  # already standard
    assert [p.name for p in sp.parse_grant("duration: 19 years")] == ["19 Years"]


def test_a_known_spell_teaches_a_breakthrough_s_parameter_not_a_virtue_s():
    saga = _saga()
    magus = saga.character("m")
    saga.spells += [
        Spell("long", "Long Ward", "Rego", "Vim", 30, duration="19 Years"),
        Spell(
            "veil", "Anat's Search", "Intellego", "Mentem", 20, range="Veil of Death"
        ),
    ]
    magus.spells_known = [KnownSpell("long"), KnownSpell("veil")]
    form = _form(saga)
    assert _extras(form, "duration") == ["19 Years"]
    assert _extras(form, "range") == []
    assert "19 Years: the spell Long Ward" in next(
        f.hint for f in form.fields() if f.key == "duration"
    )


def test_a_design_with_a_parameter_the_magus_can_t_use():
    saga = _saga()
    design = SpellDesign(key="k", name="Ghost", range="Veil of Death")
    # Editing a design that has one keeps it, as Other...
    form = _form(saga, design)
    assert OTHER in _offered(form, "range")
    assert form.parameter_choice("range", "Veil of Death") == (OTHER, "Veil of Death")
    # Starting a new design from such a spell takes what it costs as.
    plain = _form(saga)
    assert plain.parameter_choice("range", "Veil of Death") == ("Sight", "")
    assert plain.parameter_choice("range", "Moonbeam") == ("Personal", "")
