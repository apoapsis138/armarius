"""The Theban Tribunal's Byzantine customs (The Sundered Eagle): Hermetic
correspondence (p. 44), the Oath Invocation roll and its maledictions
(p. 48), Greek Fire's botch dice (p. 47), Mythic Blood (Gigantes) (p.
120), painting and venerating icons (pp. 133-134) and a mother's curse
(p. 136)."""

import random
from dataclasses import replace

import pytest

from ars_magica_manager import catalog, churches, deeds
from ars_magica_manager import theban_customs as byzantine
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Neighbour,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import theban_customs as tc
from ars_magica_manager.rules.xp import ability_xp


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _saga() -> Saga:
    monk = Character(id="c", name="Theodoros", type="companion")
    monk.characteristics = Characteristics(
        intelligence=2, communication=1, presence=1, dexterity=2
    )
    monk.abilities = [
        Ability("Order of Hermes Lore", xp=ability_xp(2)),
        Ability("Faerie Lore", xp=ability_xp(4)),
        Ability("Charm", xp=ability_xp(3)),
        Ability("Craft: Painting", xp=ability_xp(5)),
        Ability("Theology: Christian", xp=ability_xp(3)),
        Ability("Concentration", xp=ability_xp(2)),
        Ability("Leadership", xp=ability_xp(2)),
    ]
    # A hieromonk: a monk ordained a priest.
    monk.virtues_flaws = [
        VirtueFlawInstance("vf_religious"),
        VirtueFlawInstance("vf_eastern_priest"),
    ]
    monk.personality_traits = [ScoredTrait("Pious", 2)]
    rogue = Character(id="r", name="Basil", type="companion")
    church = Neighbour(id="ch", name="St Demetrios", kind="church")
    return Saga(
        id="s",
        name="S",
        characters=[monk, rogue],
        neighbours=[church],
        books_in_play=["TSE"],
    )


def _form(command) -> Form:
    assert isinstance(command, Form)
    return command


# -- Hermetic correspondence --


def test_a_letter_is_communication_or_intelligence_and_a_lore_against_six():
    monk = _saga().character("c")
    assert tc.lores(monk) == ["Faerie Lore", "Order of Hermes Lore"]
    composed = tc.letter(monk, tc.COMPOSE, "Faerie Lore", 0)
    assert (composed.total, composed.ease) == (5, 6)
    read = tc.letter(monk, tc.READ, "Order of Hermes Lore", 3)
    assert (read.total, read.ease) == (4, 9)


def test_the_letter_form_rolls_a_simple_die_and_keeps_nothing():
    saga = _saga()
    monk = saga.character("c")
    form = _form(byzantine.letter_form(saga, monk, Faces(1)))
    values = {"mode": tc.COMPOSE, "lore": "Faerie Lore", "subtlety": None}
    assert "Against [b]6[/]: any die" in form.live(values)
    lines = form.apply(values)
    assert lines[0] == "Die 1 + 5 = 6 against 6."
    assert "well wrapped" in lines[1]
    assert monk.diary == []


# -- the Oath Invocation roll and maledictions --


def test_the_oath_invocation_is_communication_charm_and_styx_against_fifteen():
    monk = _saga().character("c")
    assert tc.oath_total(monk, styx=False)[0] == 4
    assert tc.oath_total(monk, styx=True)[0] == 10
    rolled = tc.invoke_oath(monk, True, Faces(5, 0))
    # 10 + 5 = 15 against 15 + 10.
    assert (rolled.rolled, rolled.ease, rolled.heard) == (15, 25, False)
    assert tc.invoke_oath(monk, True, Faces(9, 3)).heard


def test_a_major_flaw_needs_might_forty():
    assert tc.punishment_tier(None) == "Minor"
    assert tc.punishment_tier(39) == "Minor"
    assert tc.punishment_tier(40) == "Major"
    assert "vf_greater_malediction_toad_of_lies" not in tc.maledictions(30)
    assert "vf_greater_malediction_toad_of_lies" in tc.maledictions(50)


def test_every_malediction_is_in_the_catalog():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    for tier, ids in tc.MALEDICTIONS.items():
        for vf_id in ids:
            assert by_id[vf_id].tier == tier
            assert by_id[vf_id].category == "Supernatural"


def test_a_heard_oath_lays_the_malediction_on_the_breaker():
    saga = _saga()
    monk, rogue = saga.character("c"), saga.character("r")
    form = _form(byzantine.oath_form(saga, monk, Faces(9, 3)))
    values = {
        "breaker": "r",
        "styx": True,
        "might": 20,
        "curse": "vf_lesser_malediction_ashen_food",
    }
    assert form.validate is not None and form.validate(values) is None
    assert "Minor" in form.live(values)
    major = {**values, "curse": "vf_greater_malediction_breaking_tools"}
    assert "Might 40" in (form.validate(major) or "")
    lines = form.apply(values)
    assert lines[0] == "Die 9 + 10 = 19 against 15 + 3 = 18."
    assert VirtueFlawInstance("vf_lesser_malediction_ashen_food") in rogue.virtues_flaws
    assert "Basil now bears Lesser Malediction: Ashen Food." in lines
    assert monk.diary[-1].name == rogue.diary[-1].name


def test_an_unheard_oath_lays_nothing():
    saga = _saga()
    form = _form(byzantine.oath_form(saga, saga.character("c"), Faces(1, 9)))
    lines = form.apply({"breaker": "r", "curse": "vf_lesser_malediction_mephitic_odor"})
    assert "does not hear" in lines[1]
    assert saga.character("r").virtues_flaws == []


# -- Greek Fire --


def test_greek_fire_rolls_a_botch_die_a_dose_less_safety():
    monk = _saga().character("c")
    assert tc.greek_fire_botch_dice(monk, 3, 0) == 3
    assert tc.greek_fire_botch_dice(monk, 3, 2) == 1
    assert tc.greek_fire_botch_dice(monk, 2, 4) == 0
    assert tc.greek_fire_botch_dice(monk, 2, -1) == 3


def test_greek_fire_explodes_only_on_a_botch():
    saga = _saga()
    monk = saga.character("c")
    # The die shows 0; of three botch dice one shows 0: it explodes.
    form = _form(byzantine.greek_fire_form(saga, monk, Faces(0, 4, 0, 7)))
    values = {"doses": 3, "safety": 0}
    assert "3[/] botch dice" in form.live(values)
    assert "lead 2 subordinates" in form.live(values)
    lines = form.apply(values)
    assert "explodes" in lines[1]
    assert monk.diary[-1].name == "Made Greek Fire"
    # A 0 with no botch dice left is no botch.
    calm = _form(byzantine.greek_fire_form(saga, monk, Faces(0)))
    assert "without mishap" in calm.apply({"doses": 2, "safety": 2})[1]
    assert form.validate is not None and form.validate({"doses": 0, "safety": 0})


# -- Mythic Blood (Gigantes) --


def test_mythic_blood_of_the_gigantes_is_in_the_catalog():
    entry = catalog.load_virtue_flaw_catalog_by_id()["vf_mythic_blood_gigantes"]
    assert (entry.name, entry.tier, entry.category, entry.source) == (
        "Mythic Blood (Gigantes)",
        "Major",
        "Hermetic",
        "TSE",
    )
    assert "Rebellious" in entry.summary


# -- icons --


def test_an_eikon_is_dexterity_painting_and_its_decoration():
    monk = _saga().character("c")
    plain = tc.eikon(monk)
    assert plain.quality == 2 + 5
    rich = tc.eikon(monk, standard=2, excellent=1, patron=True, other=3)
    # 7 + 2 + 3 + Pious 2 + 3.
    assert rich.quality == 17
    assert tc.invocation_bonus(17) == 4
    assert tc.invocation_bonus(15) == 3
    assert tc.invocation_bonus(0) == 0


def test_only_holy_orders_and_theology_three_paint_an_eikon():
    saga = _saga()
    monk = saga.character("c")
    assert tc.icon_problem(monk) is None
    assert "Holy Orders" in (tc.icon_problem(saga.character("r")) or "")
    assert isinstance(byzantine.icon_form(saga, saga.character("r")), Refuse)
    # A monk or nun as such is not in Holy Orders (DE p. 500, p. 74).
    monk.virtues_flaws = [VirtueFlawInstance("vf_religious")]
    assert "Holy Orders" in (tc.icon_problem(monk) or "")
    monk.virtues_flaws.append(VirtueFlawInstance("vf_priest"))
    assert tc.icon_problem(monk) is None
    monk.abilities = [a for a in monk.abilities if not a.name.startswith("Theology")]
    assert "Theology" in (tc.icon_problem(monk) or "")


def test_a_painted_icon_goes_on_its_churchs_relics():
    saga = _saga()
    monk = saga.character("c")
    form = _form(byzantine.icon_form(saga, monk))
    values = {
        "saint": "St Demetrios",
        "of_christ": False,
        "name": "",
        "church": "ch",
        "standard": 1,
        "excellent": None,
        "patron": True,
        "other": None,
    }
    # 7 + 1 + Pious 2 = 10: +2 to invoking him.
    assert "Aesthetic Quality [b]10[/]" in form.live(values)
    form.apply(values)
    church = saga.neighbour("ch")
    assert church is not None
    [icon] = churches.relics(church)
    assert icon == {
        "name": "An icon of St Demetrios",
        "saint": "St Demetrios",
        "kind": "eikon",
        "quality": 10,
        "painter": "Theodoros",
    }
    grid = churches.relics_grid(saga, church)
    assert grid.rows[0] == ["An icon of St Demetrios", "St Demetrios", "", "", "", "+2"]
    # An eikon has no Faith, so adds nothing to the aura.
    assert churches.relic_bonus(saga, church) == 0
    assert monk.diary[-1].name == "Painted An icon of St Demetrios"


def test_the_relic_form_takes_an_icon_with_the_sundered_eagle():
    saga = _saga()
    church = saga.neighbour("ch")
    assert church is not None
    keys = [f.key for f in churches.relic_fields(saga, church, None)]
    assert keys == ["name", "saint", "faith", "kind", "quality", "painter", "of_christ"]
    saga.books_in_play = []
    assert [f.key for f in churches.relic_fields(saga, church, None)] == [
        "name",
        "saint",
        "faith",
    ]


def test_venerating_an_icon_in_an_emergency_costs_a_fatigue_level():
    saga = _saga()
    monk = saga.character("c")
    assert isinstance(byzantine.venerate_form(saga, monk), Refuse)
    church = saga.neighbour("ch")
    assert church is not None
    churches.relics(church).append(
        {
            "name": "The Hodegetria",
            "saint": "the Theotokos",
            "kind": "eikon",
            "quality": 12,
        }
    )
    calm = _form(byzantine.venerate_form(saga, monk))
    values = {"icon": "ch:0", "emergency": False}
    assert "[b]+3[/]" in calm.live(values)
    assert "+3" in calm.apply(values)[0]
    assert monk.fatigue_level == "fresh"
    # Presence 1 + Concentration 2 + 9 = 12 against 15: it fails.
    rushed = _form(byzantine.venerate_form(saga, monk, Faces(9)))
    lines = rushed.apply({"icon": "ch:0", "emergency": True})
    assert lines[0].startswith("Die 9 + 3 = 12 against 15")
    assert "no bonus" in lines[1]
    assert monk.fatigue_level == "winded"


# -- a mother's curse --


def test_a_mothers_curse_is_a_lesser_malediction_on_one_area():
    saga = _saga()
    monk = saga.character("c")
    form = _form(byzantine.curse_form(saga, monk))
    values = {"mother": "Anna", "expertise": "military", "task": "rescue his sister"}
    assert "[b]-3[/] to every military roll" in form.live(values)
    lines = form.apply(values)
    curse = VirtueFlawInstance(tc.MOTHERS_CURSE, {"expertise": "military"})
    assert curse in monk.virtues_flaws
    assert lines[0] == (
        "Theodoros now bears Lesser Malediction: A Mother's Curse (Military)."
    )
    assert "rescue his sister" in monk.diary[-1].details
    entry = catalog.load_virtue_flaw_catalog_by_id()[tc.MOTHERS_CURSE]
    assert (entry.tier, entry.cost, entry.parameters) == ("Minor", -1, ["expertise"])


# -- where they are offered --


#: Where the customs are set out: Deeds, A Season's Work and Faith.
_SPOTS = (deeds.TRIBUNAL, deeds.SEASON_WORK, "Faith")


@pytest.mark.parametrize(
    "action",
    ["theban_letter", "invoke_oath", "make_greek_fire", "paint_icon", "mothers_curse"],
)
def test_the_customs_are_offered_on_a_character_with_the_sundered_eagle(action):
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="c")
    assert available(action, page)
    assert action in {
        i.action for spot in _SPOTS for i in menu_forms.placed(page, spot)
    }
    assert isinstance(menu_forms.command(page, action), Form)
    saga.books_in_play = []
    assert not available(action, replace(page))


def test_icons_are_offered_only_where_they_can_be_painted_or_venerated():
    saga = _saga()
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="r")
    assert not available("paint_icon", page)
    assert not available("venerate_icon", page)
    church = saga.neighbour("ch")
    assert church is not None
    churches.relics(church).append({"name": "Icon", "kind": "eikon", "quality": 5})
    assert available("venerate_icon", page)
