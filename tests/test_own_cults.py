"""A saga's own Mystery Cults (The Mysteries Revised Edition pp. 13-19;
DE pp. 387-389): the record and its checks, the catalogs that offer it,
its members, its Scripts' components and bonus, the Initiation season
following its Scripts, an experiment for a degree's first Script, and
Saga Content's Mystery Cults tab's core (forms/mystery_cults.py)."""

from __future__ import annotations

import random
from dataclasses import asdict

import pytest

from ars_magica_manager import actions, catalog, deeds, traditions
from ars_magica_manager import mystery_cults as mc
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import mystery_cults as cf
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    CultComponent,
    CultDegree,
    CultScript,
    MysteryCult,
    Ordeal,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.models.mystery_cults import COMPONENT_KINDS
from ars_magica_manager.rules import mysteries
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.xp import ability_xp

LORE = "Spinner's Thread Lore"
AFFINITY = VirtueFlawInstance("vf_affinity_with_art", {"art": "imaginem"})


def _script() -> CultScript:
    """The Silk Hall at Midsummer: place +3, Quest +3, Minor Ordeal +3,
    goods +1 = +10."""
    return CultScript(
        "The Silk Hall at Midsummer",
        [
            mc.component("place", note="To the Silk Hall under the hill"),
            mc.component("quest", note="A thread of a faerie's gown"),
            mc.component("ordeal_minor", flaw_id="vf_visions"),
            mc.component("goods", note="His finest garment"),
        ],
    )


def _cult() -> MysteryCult:
    return MysteryCult(
        id="custom_cult_spinners_thread",
        name="The Spinner's Thread",
        lore=LORE,
        realm="Faerie",
        founder_id="h",
        founded=1218,
        description="Weavers of the silk pact under the hill.",
        degrees=[
            CultDegree(
                "degree_1", "Spinner", AFFINITY.vf_id, dict(AFFINITY.params), _script()
            ),
            CultDegree(
                "degree_2",
                "Weaver",
                "vf_elemental_magic",
                script=CultScript("The Thread Owed", [mc.component("unique_quest")]),
            ),
            CultDegree("degree_3", "Thread-reader", "vf_second_sight"),
        ],
    )


def _person(
    ident: str, name: str, lore: int | None, *vfs: VirtueFlawInstance
) -> Character:
    person = Character(id=ident, name=name, type="magus")
    person.characteristics = Characteristics(presence=2, intelligence=3)
    if lore is not None:
        person.abilities = [Ability(LORE, xp=ability_xp(lore))]
    person.virtues_flaws = list(vfs)
    return person


@pytest.fixture
def saga():
    """Hildegund (Lore 5, Spinner), Matthaios (Lore 1, a probationer) and
    Wulf (no Lore), with the cult; the catalogs offer it."""
    found = Saga(
        id="s",
        name="S",
        characters=[
            _person("h", "Hildegund", 5, AFFINITY),
            _person("m", "Matthaios", 1),
            _person("w", "Wulf", None),
        ],
        custom_cults=[_cult()],
    )
    catalog.use_saga(found)
    yield found
    catalog.use_saga(None)


# -- the record -----------------------------------------------------------------


def test_a_cult_round_trips_through_a_save(saga):
    loaded = Saga.from_dict(asdict(saga))
    assert loaded.custom_cults == saga.custom_cults
    assert loaded.custom_cults[0].degrees[0].script.bonus == 10


@pytest.mark.parametrize(
    ("change", "says"),
    [
        ({"id": "cult_x"}, "custom_cult_"),
        ({"realm": "Air"}, "unknown realm"),
        ({"characteristic": "Strength"}, "unknown Characteristic"),
        ({"who": "nobody"}, "unknown membership"),
        ({"founded": "soon"}, "the year founded"),
        (
            {
                "degrees": [
                    {
                        "id": "d",
                        "name": "D",
                        "script": {"name": "S", "components": [{"key": "dance"}]},
                    }
                ]
            },
            "isn't a kind",
        ),
        (
            {
                "degrees": [
                    {
                        "id": "d",
                        "name": "D",
                        "script": {
                            "name": "S",
                            "components": [{"key": "quest", "bonus": "x"}],
                        },
                    }
                ]
            },
            "whole number",
        ),
    ],
)
def test_a_bad_cult_in_a_save_is_reported_by_name(saga, change, says):
    data = asdict(saga.custom_cults[0]) | change
    with pytest.raises(ValueError, match=says):
        MysteryCult.from_dict(data)


def test_the_component_kinds_are_the_seasons_table_and_three_more():
    assert set(COMPONENT_KINDS) == {c.key for c in mysteries.COMPONENTS} | {
        "virtue_replaced",
        "rite",
        "flawed_ordeal",
    }


# -- the catalogs ------------------------------------------------------------------


def test_the_cult_joins_the_tradition_catalog_with_its_scripts(saga):
    tradition = catalog.load_tradition_catalog_by_id()["custom_cult_spinners_thread"]
    assert tradition.realm == "Faerie"
    rule = tradition.initiation
    assert rule is not None and rule.lore == LORE
    spinner, weaver = rule.scripts  # the third degree has no Script yet
    assert (spinner.ease_factor, spinner.bonus) == (15, 10)
    assert spinner.gains == "Affinity with Imaginem (Minor)"
    assert spinner.requires == ((LORE, 1),)  # TMRE p. 13
    # Lore 3 for later Initiations is a warning, not a requirement.
    assert (weaver.ease_factor, weaver.bonus, weaver.requires) == (21, 6, ((LORE, 1),))
    assert "Visions (Minor Ordeal)" in spinner.ordeal


def test_its_lore_joins_the_ability_catalog_unless_the_catalog_names_it(saga):
    names = {a.name for a in catalog.load_ability_catalog()}
    assert LORE in names
    saga.custom_cults[0].lore = "Mystery Cult Lore: Spinner"
    catalog.use_saga(saga)
    assert "Mystery Cult Lore: Spinner" not in {
        a.name for a in catalog.load_ability_catalog()
    }


def test_a_saga_cult_is_not_among_the_traditions_to_turn_on(saga):
    assert all(not t.id.startswith("custom_cult_") for t in traditions.in_play(saga))
    catalog.use_saga(None)
    assert "custom_cult_spinners_thread" not in catalog.load_tradition_catalog_by_id()


# -- members -----------------------------------------------------------------------


def test_members_are_who_holds_the_lore(saga):
    cult = saga.custom_cults[0]
    found = [(m.character.name, m.degree) for m in mc.members(saga, cult)]
    assert found == [("Hildegund", 0), ("Matthaios", None)]
    assert mc.members_text(saga, cult) == "Hildegund (I), 1 probationer"
    assert ts.belongs(saga.character("m"), cult.id)
    assert not ts.belongs(saga.character("w"), cult.id)


def test_a_virtue_alone_doesnt_make_a_member(saga):
    """Most Initiated Virtues can be taken at creation: membership is the
    Lore (TMRE pp. 11, 13)."""
    cult = saga.custom_cults[0]
    wulf = saga.character("w")
    wulf.virtues_flaws.append(AFFINITY)
    assert not mc.is_member(wulf, cult)
    assert not ts.belongs(wulf, cult.id)
    assert "Wulf" not in mc.members_text(saga, cult)


def test_the_founder_is_a_member_at_lore_0(saga):
    """A founder may start with the Lore at 0 (TMRE p. 19)."""
    cult = saga.custom_cults[0]
    cult.founder_id = "w"
    assert mc.is_member(saga.character("w"), cult)
    saga.character("w").abilities = [Ability(LORE, xp=0)]
    cult.founder_id = ""
    assert ts.belongs(saga.character("w"), cult.id)


def test_a_degree_target_is_known_when_someone_holds_its_virtue(saga):
    spinner, weaver, reader = saga.custom_cults[0].degrees
    assert mc.degree_target(saga, spinner) == 15
    assert mc.degree_target(saga, weaver) == 30  # Major, no one has it
    assert mc.degree_target(saga, reader) == 18
    assert "Target 18, and its Script must be found" in cf.degree_note(saga, reader)


# -- Scripts -----------------------------------------------------------------------


def test_a_script_bonus_is_its_components_added_up(saga):
    assert _script().bonus == 10
    assert mc.bonus_words(_script()).endswith("= +10")


@pytest.mark.parametrize(
    ("parts", "says"),
    [
        ([mc.component("place"), mc.component("place")], "only once"),
        ([mc.component("goods"), mc.component("goods")], "only once"),
        ([CultComponent("great_sacrifice", 7)], "+3 to +6"),
        ([CultComponent("sympathy", -6)], "-5 to +5"),
        ([mc.component("ordeal_major")], "Flaw each Ordeal"),
    ],
)
def test_a_script_breaking_the_rules_is_refused(parts, says):
    assert says in mc.script_problem(parts)


def test_reconcile_keeps_the_words_of_what_stays(saga):
    old = _script().components
    wanted = {"quest": [mc.component("quest"), mc.component("quest")], "place": []}
    parts = mc.reconcile(old, wanted)
    assert [p.key for p in parts] == ["quest", "ordeal_minor", "goods", "quest"]
    assert parts[0].note == "A thread of a faerie's gown"


# -- the Initiation season follows a cult's Script -----------------------------------


def _plan(**kw) -> SeasonPlan:
    base = {
        "hedge_script": "custom_cult_spinners_thread/Spinner: The Silk Hall at Midsummer",
        "teacher_id": "h",
        "effect_id": AFFINITY.vf_id,
        "effect_params": dict(AFFINITY.params),
        "ordeal_kind": "gain",
        "device_id": "vf_visions",
    }
    return SeasonPlan("m", 1220, "Spring", "undergo_initiation", [], **(base | kw))


def test_the_initiation_season_offers_the_cults_scripts(saga):
    offered = {v: k for k, v in ts.script_options(saga, saga.character("m"))}
    key = "custom_cult_spinners_thread/Spinner: The Silk Hall at Midsummer"
    assert key in offered
    assert "Ease 15, +10" in offered[key]


def test_an_initiation_by_a_cult_script_works_as_a_catalog_cults(saga):
    matthaios = saga.character("m")
    assert sw.problems(saga, matthaios, _plan()) == []
    # Presence 2 + Lore 5 + Script 10 = 17 against 15.
    result = sw.work(saga, matthaios, _plan(), random.Random(1))
    assert AFFINITY in result.add_vfs
    assert any("Initiation Total 17" in n for n in result.notes)


def _weaver_plan() -> SeasonPlan:
    return _plan(
        hedge_script="custom_cult_spinners_thread/Weaver: The Thread Owed",
        effect_id="vf_elemental_magic",
        effect_params={},
    )


def test_lore_3_is_a_warning_counted_by_initiations_taken(saga):
    """Later Initiations typically need Lore 3 (TMRE p. 13): a warning,
    counted by the Initiations taken, not by the degree; Lore 1 is the
    only must."""
    matthaios = saga.character("m")
    # His first Initiation, though into the second degree: no warning.
    assert sw.problems(saga, matthaios, _weaver_plan()) == []
    notes = sw.work(saga, matthaios, _weaver_plan(), None).notes
    assert not any("typically needs" in n for n in notes)
    # Once he has taken one, a later one warns, and still may go ahead.
    matthaios.virtues_flaws.append(AFFINITY)
    assert sw.problems(saga, matthaios, _weaver_plan()) == []
    notes = sw.work(saga, matthaios, _weaver_plan(), None).notes
    assert any(f"typically needs {LORE} 3 (he has 1)" in n for n in notes)


def test_an_initiate_needs_the_lore_at_1(saga):
    wulf = saga.character("w")
    wulf.abilities = [Ability(LORE, xp=0)]
    found = sw.problems(saga, wulf, _plan())
    assert any(f"{LORE} 1" in p for p in found)


def test_one_outside_the_cult_cant_lead_it(saga):
    found = sw.problems(saga, saga.character("m"), _plan(teacher_id="w"))
    assert any("Wulf isn't one of" in p for p in found)


# -- experimenting (TMRE p. 18) ----------------------------------------------------


class _Dice(random.Random):
    """Every d10 shows `face`."""

    def __init__(self, face: int) -> None:
        super().__init__(0)
        self.face = face

    def randrange(self, *_args: object, **_kw: object) -> int:  # type: ignore[override]
        return self.face


@pytest.mark.parametrize(
    ("face", "goes_on", "says"),
    [
        # Chart 3 + 1 = 4: nothing; validity 3 + 1 + Int 3 + Lore 5 = 12 vs 15.
        (3, False, "invalid"),
        # Chart 7 + 1 = 8: complete failure, whatever the validity.
        (7, False, "complete failure"),
        # Chart 9 + 1 = 10: a Discovery; validity 9 + 1 + 3 + 5 = 18 vs 15.
        (9, True, "Discovery"),
    ],
)
def test_an_experiments_chart_and_validity(saga, face, goes_on, says):
    cult = saga.custom_cults[0]
    found = mc.experiment(_Dice(face), saga, cult, saga.character("h"), True, 6, 1)
    assert found.goes_on is goes_on
    assert any(says in n for n in found.notes)


def test_on_another_initiate_the_validity_is_harder(saga):
    cult = saga.custom_cults[0]
    found = mc.experiment(_Dice(9), saga, cult, saga.character("h"), False, 6, 1)
    assert not found.goes_on  # 18 against 15 + 6


def test_the_chart_keeps_what_it_writes_into_the_script(saga):
    cult = saga.custom_cults[0]
    # Chart 2 + 3 = 5: a side effect; simple die 2 + 3 = 5: a minor side effect.
    found = mc.experiment(_Dice(2), saga, cult, saga.character("h"), True, 0, 3)
    assert found.traits == ["minor side effect"]
    rite = mysteries.ExperimentalRite()
    mysteries._read_rite(rite, 5, _Dice(7), 0)  # side 7: a major flaw
    mysteries._read_rite(rite, 5, _Dice(9), 0)  # side 9: a major benefit
    mysteries._read_rite(rite, 11, _Dice(1), 0)  # a modified effect
    assert (rite.major_flaws, rite.major_benefits, rite.modified) == (1, 1, True)


def test_finishing_an_experiment(saga):
    cult = saga.custom_cults[0]
    reader = cult.degrees[2]
    hildegund = saga.character("h")
    # Presence 2 + Lore 5 + 6 + sympathy 3 + risk 2 = 18 against 18 (she lacks it).
    notes = mc.finish_experiment(saga, cult, reader, hildegund, hildegund, 6, 3, 2)
    assert reader.script is not None and reader.script.bonus == 9  # no risk kept
    assert VirtueFlawInstance("vf_second_sight") in hildegund.virtues_flaws
    assert "works" in notes[0]


def test_an_experiment_short_of_its_target_writes_nothing(saga):
    cult = saga.custom_cults[0]
    reader = cult.degrees[2]
    hildegund = saga.character("h")
    found = mc.Findings(rite_flaw="vf_visions")
    notes = mc.finish_experiment(
        saga, cult, reader, hildegund, hildegund, 6, 0, 0, found
    )
    assert reader.script is None and "fails" in notes[0]
    # Its Ordeal is suffered even so (TMRE p. 18).
    assert VirtueFlawInstance("vf_visions") in hildegund.virtues_flaws
    assert [o.size for o in hildegund.ordeals] == ["Minor"]


def test_an_experiment_writes_its_results_into_the_script(saga):
    """A side effect becomes a Personality Trait, a major flaw an Ordeal
    Flaw with no bonus, a major benefit a Virtue, and a modified effect
    Initiates a different Virtue, not the degree's own (TMRE p. 18)."""
    cult = saga.custom_cults[0]
    reader = cult.degrees[2]
    hildegund = saga.character("h")
    found = mc.Findings(
        rite_flaw="vf_visions",
        traits=["Devoted to the Spinner +1"],
        flaws=["vf_poor_memory"],
        virtues=["vf_luck"],
        instead="vf_premonitions",
    )
    # Presence 2 + Lore 5 + 10 + sympathy 1 = 18 against 18.
    notes = mc.finish_experiment(
        saga, cult, reader, hildegund, hildegund, 10, 1, 0, found
    )
    script = reader.script
    assert script is not None and script.bonus == 11  # the extra Flaw gives 0
    assert [c.key for c in script.components] == ["rite", "sympathy", "flawed_ordeal"]
    assert script.components[0].flaw_id == "vf_visions"
    assert (script.traits, script.virtues, script.initiates) == (
        ["Devoted to the Spinner +1"],
        ["vf_luck"],
        "vf_premonitions",
    )
    held = {vf.vf_id for vf in hildegund.virtues_flaws}
    assert {"vf_premonitions", "vf_luck", "vf_visions", "vf_poor_memory"} <= held
    assert "vf_second_sight" not in held
    assert [(t.name, t.score) for t in hildegund.personality_traits] == [
        ("Devoted to the Spinner", 1)
    ]
    assert any("not the degree's own" in n for n in notes)
    # The catalog's Script names what it gives.
    tradition = catalog.load_tradition_catalog_by_id()[cult.id]
    assert tradition.initiation is not None
    third = tradition.initiation.scripts[-1]
    assert "Personality Trait Devoted to the Spinner +1" in third.gains
    assert "Poor Memory (Ordeal)" in third.ordeal
    # Edit Script keeps them.
    form = cf.script_ops(saga, lambda: 0, lambda: 2).edit(0)
    assert isinstance(form, Form)
    form.apply({f.key: f.value for f in form.fields()})
    assert reader.script is not None and reader.script.initiates == "vf_premonitions"
    assert "Initiates instead" in cf.degree_info(saga, cult, 2)


def test_the_experiments_target_takes_past_ordeals(saga):
    """TMRE p. 14: the Initiate's past Ordeal lowers the Target, never
    below 9."""
    cult = saga.custom_cults[0]
    reader = cult.degrees[2]
    hildegund, matthaios = saga.character("h"), saga.character("m")
    matthaios.ordeals = [Ordeal("Major")]
    assert mc.target_for(hildegund, reader) == 18
    assert mc.target_for(hildegund, reader, matthaios) == 9


# -- Saga Content's Mystery Cults tab's core -------------------------------------


def test_the_lists_rows(saga):
    rows = cf.cult_rows(saga)
    assert rows[0][0] == 0 and "Hildegund" in rows[0][1] and "3 degrees" in rows[0][1]
    degrees = cf.degree_rows(saga, lambda: 0)
    assert "+10 / 15" in degrees[0][1]
    assert "(none: experiment)" in degrees[2][1]
    parts = cf.script_rows(saga, lambda: 0, lambda: 0)
    assert len(parts) == 4 and parts[2][1].startswith("Ordeal: Visions (Minor Flaw)")
    assert (
        cf.script_title(saga, lambda: 0, lambda: 0) == "The Silk Hall at Midsummer: +10"
    )
    assert "no Script yet" in cf.script_title(saga, lambda: 0, lambda: 2)


def test_the_cult_facts(saga):
    facts = dict(cf.cult_facts(saga, saga.custom_cults[0]))
    assert facts["Founded"] == "1218, by Hildegund"
    assert facts["Initiation"] == "Presence + Lore + Script"
    assert facts["Members"] == "Hildegund (I), 1 probationer"


def test_adding_a_cult(saga):
    form = cf.cults_ops(saga).add()
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()} | {
        "name": "The Seventh Wave",
        "lore": "Seventh Wave Lore",
    }
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    added = saga.custom_cults[-1]
    assert added.id == "custom_cult_the_seventh_wave"
    assert "Seventh Wave Lore" in {a.name for a in catalog.load_ability_catalog()}


@pytest.mark.parametrize(
    ("values", "says"),
    [
        ({"name": ""}, "Name the cult"),
        ({"name": "The Spinner's Thread", "lore": "X Lore"}, "already has"),
        ({"name": "New", "lore": LORE}, "Another of the saga's cults"),
        ({"name": "New", "lore": "Magic Theory"}, "an Ability of the catalog"),
        ({"name": "New", "lore": ""}, "Name the cult's Lore"),
    ],
)
def test_a_cult_form_refuses(saga, values, says):
    form = cf.cults_ops(saga).add()
    assert isinstance(form, Form) and form.validate is not None
    assert says in (form.validate(values) or "")


def test_renaming_the_lore_carries_it_to_its_members(saga):
    form = cf.cults_ops(saga).edit(0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()} | {"lore": "Thread Lore"}
    form.apply(values)
    assert saga.character("h").abilities[0].name == "Thread Lore"
    assert mc.members_text(saga, saga.custom_cults[0]) == "Hildegund (I), 1 probationer"


def test_deleting_a_cult_asks_first(saga):
    step = cf.cults_ops(saga).remove(0)
    assert isinstance(step, Confirm)
    step.apply()
    assert saga.custom_cults == []
    assert "custom_cult_spinners_thread" not in catalog.load_tradition_catalog_by_id()


def test_a_degree_needs_what_its_virtue_names(saga):
    form = cf.degree_ops(saga, lambda: 0).add()
    assert isinstance(form, Form) and form.validate is not None
    values = {"name": "Seer", "virtue_id": "vf_puissant_art", "virtue_detail": ""}
    assert "Say what the Virtue names" in (form.validate(values) or "")
    values["virtue_detail"] = "Vim"
    assert form.validate(values) is None
    form.apply(values)
    assert saga.custom_cults[0].degrees[-1].virtue_params == {"art": "vim"}


def test_the_script_form_sets_the_components_and_keeps_their_words(saga):
    form = cf.script_ops(saga, lambda: 0, lambda: 0).edit(0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert (values["place"], values["quests"], values["ordeal"]) == (True, 1, "minor")
    assert values["flaw"] == "vf_visions" and values["mystagogue"] == "h"
    assert form.live is not None
    assert "17[/] against Target 15" in form.live(values)
    values |= {"quests": 2, "teaching": True, "sympathy": 1}
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    script = saga.custom_cults[0].degrees[0].script
    assert script is not None and script.bonus == 10 + 3 + 3 + 1
    assert script.components[1].note == "A thread of a faerie's gown"


@pytest.mark.parametrize(
    ("change", "says"),
    [
        ({"name": ""}, "Name the Script"),
        ({"great": 2}, "+3 to +6"),
        ({"sympathy": 6}, "−5 to +5"),
        ({"ordeal": "major", "flaw": None}, "Choose the Flaw"),
        ({"quests": 12}, "0 to 9"),
    ],
)
def test_the_script_form_refuses(saga, change, says):
    form = cf.script_ops(saga, lambda: 0, lambda: 0).edit(0)
    assert isinstance(form, Form) and form.validate is not None
    values = {f.key: f.value for f in form.fields()} | change
    assert says in (form.validate(values) or "")


def test_add_on_a_degree_without_a_script_writes_one(saga):
    form = cf.script_ops(saga, lambda: 0, lambda: 2).add()
    assert isinstance(form, Form) and form.title == "Add Script"
    form = cf.script_ops(saga, lambda: 0, lambda: 0).add()
    assert isinstance(form, Form) and form.title.startswith("Add Component")


def test_adding_a_second_special_place_is_refused(saga):
    form = cf.script_ops(saga, lambda: 0, lambda: 0).add()
    assert isinstance(form, Form) and form.validate is not None
    assert "only once" in (form.validate({"kind": "place", "note": ""}) or "")


def test_experiment_is_offered_for_no_script_or_one_that_falls_short(saga):
    """TMRE p. 18: with no Script, or only an inadequate one."""
    # The Spinner's +10 falls short for Matthaios: 2 + 1 + 10 = 13 against 18.
    assert cf.offers_experiment(saga, lambda: 0, 0)
    # Hildegund alone leads Initiations: 2 + 5 + 10 = 17 against 15.
    saga.character("m").abilities = []
    assert not cf.offers_experiment(saga, lambda: 0, 0)
    assert cf.offers_experiment(saga, lambda: 0, 2)
    # The Weaver's +6: 2 + 5 + 6 = 13 against 30.
    assert cf.offers_experiment(saga, lambda: 0, 1)
    assert isinstance(cf.experiment_form(saga, lambda: 0, 0), Refuse)
    form = cf.experiment_form(saga, lambda: 0, 2)
    assert isinstance(form, Form) and form.save_label == "Roll"
    weaver = cf.experiment_form(saga, lambda: 0, 1)
    assert isinstance(weaver, Form) and weaver.validate is not None
    values = {f.key: f.value for f in weaver.fields()}
    assert values["degree"] == "degree_2" and weaver.validate(values) is None
    # The Spinner's Script reaches the Target for Hildegund: refused.
    assert "already reaches the Target" in (
        weaver.validate(values | {"degree": "degree_1"}) or ""
    )


def test_the_experiment_form_rolls_then_asks_the_sympathy(saga):
    form = cf.experiment_form(saga, lambda: 0, 2, rng=lambda: _Dice(9))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()} | {"proposed": 6, "risk": 1}
    assert form.live is not None and "against Target 18" in form.live(values)
    # Chart 9 + 1 = 10, a Discovery; validity 9 + 1 + 3 + 5 = 18 vs 15.
    step = form.apply(values)
    assert isinstance(step, Form) and step.save_label == "Write the Script"
    # Presence 2 + Lore 5 + 6 + sympathy 4 + risk 1 = 18 against 18.
    notes = step.apply({"sympathy": 4})
    reader = saga.custom_cults[0].degrees[2]
    assert reader.script is not None and reader.script.bonus == 10
    assert any("Discovery" in n for n in notes)


def test_the_sympathy_form_asks_what_the_chart_gave(saga):
    cult = saga.custom_cults[0]
    hildegund = saga.character("h")
    rolled = mc.Experiment(traits=["minor flaw"], major_flaws=1, modified=True)
    step = cf._sympathy_form(
        saga, cult, (cult.degrees[2], hildegund, hildegund), 10, 0, rolled
    )
    keys = [f.key for f in step.fields()]
    assert keys == ["sympathy", "trait_0", "flaw_0", "instead"]
    assert step.validate is not None
    assert "a score" in (step.validate({"sympathy": 0, "trait_0": "Grim"}) or "")
    values = {
        "sympathy": 1,
        "trait_0": "Grim +2",
        "flaw_0": "vf_poor_memory",
        "instead": "vf_premonitions",
    }
    assert step.validate(values) is None
    step.apply(values)
    script = cult.degrees[2].script
    assert script is not None and script.initiates == "vf_premonitions"


def test_a_disaster_gives_both_a_major_flaw(saga):
    """TMRE p. 18: the Initiation fails completely, and the Mystagogue and
    the Initiate each gain a Major Flaw."""
    form = cf.experiment_form(saga, lambda: 0, 2, rng=lambda: _Dice(0))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()} | {
        "initiate": "m",
        "rite_flaw": "vf_visions",
    }
    step = form.apply(values)
    assert isinstance(step, Form) and step.title.startswith("Disaster")
    assert step.validate is not None and step.validate({}) is not None
    step.apply({"guide_flaw": "vf_blind", "initiate_flaw": "vf_deaf"})
    held = {vf.vf_id for vf in saga.character("m").virtues_flaws}
    assert {"vf_deaf", "vf_visions"} <= held
    assert "vf_blind" in {vf.vf_id for vf in saga.character("h").virtues_flaws}
    assert saga.custom_cults[0].degrees[2].script is None


def test_the_experiment_is_on_the_mystagogues_deeds(saga):
    """TMRE p. 18: the Mystagogue's rolls, so her sheet offers it."""
    assert "experiment_script" not in actions.MORE_SECTIONS
    hildegund = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="h")
    assert [i.action for i in menu_forms.placed(hildegund, deeds.MYSTERY_CULTS)] == [
        "experiment_script"
    ]
    wulf = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="w")
    assert not menu_forms.placed(wulf, deeds.MYSTERY_CULTS)
    assert isinstance(cf.mystagogue_experiment(saga, saga.character("w")), Refuse)
    form = cf.mystagogue_experiment(saga, saga.character("m"))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["mystagogue"] == "m" and values["degree"] == "degree_1"


def test_a_mystagogue_of_two_cults_chooses_one_first(saga):
    second = _cult()
    second.name = "The Second Loom"
    saga.custom_cults.append(second)
    step = cf.mystagogue_experiment(saga, saga.character("h"))
    assert isinstance(step, Choose)
    assert [c.label for c in step.choices()] == [
        saga.custom_cults[0].name,
        "The Second Loom",
    ]
    assert isinstance(step.apply(step.choices()[1].value), Form)
