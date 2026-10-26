"""The Definitive Edition's creatures to pick in the Bestiary (DE pp.
428-492), and tamed creatures in play (DE pp. 384-386)."""

import random

from ars_magica_manager import bestiary_book
from ars_magica_manager.forms import creature as creature_forms
from ars_magica_manager.models import (
    Ability,
    AnimalForm,
    Character,
    Characteristics,
    Combatant,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities, supplement_work, tamed
from ars_magica_manager.rules import fight as fight_rules
from ars_magica_manager.rules.xp import ability_xp


class _Dice(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


# -- The book's creatures --


def test_every_creature_of_the_book_builds():
    book = bestiary_book.catalog()
    assert len(book) == 64
    assert {c.group for c in book} == set(bestiary_book.GROUPS)
    for entry in book:
        creature = bestiary_book.build(entry)
        assert creature.name == entry.name
        assert creature.source == f"ArM5 DE p. {entry.page}"


def test_the_bear_as_printed():
    bear = bestiary_book.build(bestiary_book.by_key("bear"))
    assert (bear.size, bear.soak, bear.cunning) == (2, 10, True)
    assert bear.characteristics.strength == 6
    assert [a.name for a in bear.attacks] == ["Claws", "Teeth", "Grapple"]


def test_new_creature_can_start_from_the_book():
    saga = Saga(id="s", name="S")
    form = creature_forms.new_creature_form(saga)
    assert form.validate is not None
    assert form.validate({"name": ""}) is not None
    assert form.validate({"name": "", "from_book": "wolf"}) is None
    form.apply({"name": "", "from_book": "wolf"})
    form.apply({"name": "Old Grey", "from_book": "wolf"})
    assert [c.name for c in saga.creatures] == ["Wolf", "Old Grey"]
    assert saga.creatures[0].id != saga.creatures[1].id
    assert saga.creatures[1].attacks


# -- Taming (DE pp. 384-385) --


def test_points_enough_tame_more_of_the_same_kind():
    assert supplement_work.more_tamed(9, 3, 5) == 2
    assert supplement_work.more_tamed(9, 3, 1) == 1
    assert supplement_work.more_tamed(2, 3, 5) == 0


def test_a_master_of_creatures_tames_with_magic_lore():
    tamer = Character(id="t", name="Ulf", type="companion")
    tamer.characteristics = Characteristics(intelligence=0)
    tamer.abilities = [
        Ability("Magic Lore", xp=ability_xp(4)),
        Ability("Animal Handling", xp=ability_xp(3)),
    ]
    tamer.virtues_flaws = [
        VirtueFlawInstance("vf_master_of_form_creatures", {"form": "animal"})
    ]
    saga = Saga(id="s", name="S", characters=[tamer])
    assert supplement_work.master_of_creatures(tamer) == "Animal"
    plan = SeasonPlan("t", 1220, "Spring", "tame_animal", title="Wolf", book_level=2)
    result = supplement_work.SupplementWork()
    supplement_work._tame_animal(saga, tamer, plan, None, result)
    # Magic Lore 4 + Animal Handling 3 - Might 2 = 5.
    assert result.progress == [("taming", "Wolf", 2, 5)]
    assert any("more of the same kind" in note for note in result.notes)


# -- Tamed creatures in play (DE pp. 385-386) --


def _animal(loyal: int = 0) -> Character:
    hound = Character(
        id="h", name="Brag", type="companion", animal=AnimalForm("clawed", "Dog")
    )
    hound.personality_traits = [ScoredTrait("Loyal (Ulf)", loyal)]
    return hound


def _handler() -> Character:
    ulf = Character(id="u", name="Ulf", type="companion")
    ulf.characteristics = Characteristics(presence=1)
    ulf.abilities = [Ability("Animal Handling", xp=ability_xp(4))]
    return ulf


def test_commanding_a_beast():
    saga = Saga(id="s", name="S", characters=[_handler(), _animal(2)])
    ulf, hound = saga.characters
    assert tamed.command_total(ulf, "Animal Handling") == 5
    lines = tamed.command(saga, ulf, hound, "unusual", "Animal Handling", _Dice(3))
    assert lines == ["Presence + Animal Handling +5 + die 3 = 8 against 6: it obeys."]
    # Afraid, with no Confidence: a Loyalty test against 6 as well.
    lines = tamed.command(saga, ulf, hound, "feared", "Animal Handling", _Dice(8, 2))
    assert lines[-1] == "Loyalty test: Loyal +2 + die 2 = 4 against 6: it balks."
    assert tamed.command(saga, ulf, hound, "habit", "Ride", _Dice()) == [
        "Brag does it without a roll: a task it knows well."
    ]


def test_an_animal_learning_a_new_ability_tests_its_loyalty():
    ulf, hound = _handler(), _animal(1)
    ulf.abilities.append(Ability("Athletics", xp=ability_xp(4)))
    saga = Saga(id="s", name="S", characters=[ulf, hound])
    plan = SeasonPlan(
        "h",
        1220,
        "Spring",
        activities.TRAINED,
        [XpAllocation("ability:Athletics")],
        teacher_id="u",
    )
    assert activities.problems(hound, plan, saga) == []
    preview = activities.outcome(hound, plan, saga)
    assert any("Loyalty test" in n for n in preview.notes)
    failed = activities.outcome(hound, plan, saga, _Dice(2))  # 1 + 2 < 6
    assert failed.gains[0].result.xp == 0
    passed = activities.outcome(hound, plan, saga, _Dice(7))
    assert passed.gains[0].result.xp > 0
    ulf.abilities = [Ability("Athletics", xp=ability_xp(4))]
    assert any("Animal Handling" in p for p in activities.problems(hound, plan, saga))


def test_tamed_animals_follow_their_handlers_animal_handling():
    ulf = _handler()
    hounds = [
        Character(id=f"h{n}", name=f"Hound {n}", type="grog", animal=AnimalForm())
        for n in range(3)
    ]
    saga = Saga(id="s", name="S", characters=[ulf, *hounds])
    fighters = [
        fight_rules.Fighter(saga, Combatant(c.name, "character", c.id, id=c.id))
        for c in (ulf, *hounds)
    ]
    assert fight_rules.leads_with(fighters, fighters[0]) == 4  # Animal Handling
    mixed = [*fighters, fight_rules.Fighter(saga, Combatant("Guard", id="g"))]
    assert fight_rules.leads_with(mixed, fighters[0]) == 0  # Leadership
