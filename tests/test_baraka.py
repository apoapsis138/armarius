"""A Muslim's baraka from the holy forbears and the Hajj (Realms of Power:
The Divine pp. 103-108)."""

import random
from dataclasses import replace

from ars_magica_manager import baraka as forms
from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Saga,
    ScoredTrait,
)
from ars_magica_manager.rules import baraka as bk
from ars_magica_manager.rules import saints as sr
from ars_magica_manager.rules.xp import ability_xp
from ars_magica_manager.sections import FAITH_SECTION


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _yusuf() -> Character:
    """Communication +2, Charm 1, Pious +2, Loyal +1."""
    yusuf = Character(id="y", name="Yusuf", type="companion")
    yusuf.background.religion = "Muslim"
    yusuf.characteristics = Characteristics(communication=2)
    yusuf.abilities = [Ability("Charm", xp=ability_xp(1))]
    yusuf.personality_traits = [ScoredTrait("Loyal", 1), ScoredTrait("Pious", 2)]
    return yusuf


def _saga(*books: str) -> Saga:
    return Saga(
        id="s", name="S", characters=[_yusuf()], books_in_play=list(books) or ["RoP:D"]
    )


def _form(command) -> Form:
    assert isinstance(command, Form)
    return command


def _values(form: Form, **changes) -> dict:
    values = {f.key: f.value for f in form.fields()}
    values.update(changes)
    return values


def test_the_forbears_powers_are_the_books():
    for forbear in bk.FORBEARS.values():
        assert all(key in sr.POWERS for key in forbear.powers)
    assert bk.FORBEARS[bk.QURAN].anywhere
    assert bk.FORBEARS["muhammad"].might == 100
    assert bk.FORBEARS["david"].powers == ()


def test_the_muslim_invocation_modifiers():
    yusuf = _yusuf()
    found = bk.asking(
        yusuf,
        trait=2,
        aura=4,
        ticks=("feast_day", "relic_owned", "no_zakat"),
        donation=2,
        sin=1,
        specific=True,
    )
    # 2 + 1 + 2 + 4 + 3 + 2 - 3 + 2 - 1 - 5 = 7
    assert found.total == 7
    assert "- a specific miracle 5" in found.terms


def test_baraka_is_sought_at_the_shrine_but_the_quran_anywhere():
    saga = _saga()
    yusuf = saga.character("y")
    form = _form(forms.baraka_form(saga, yusuf, Faces(9, 2)))
    assert form.validate is not None
    values = _values(form)
    assert values["trait"] == "Pious"
    assert form.validate(values) is None
    at_tomb = _values(form, forbear="abraham")
    assert "shrine" in str(form.validate(at_tomb))
    assert form.validate({**at_tomb, "at_shrine": True}) is None
    wrong = {**at_tomb, "at_shrine": True, "power": "scourging_of_snakes"}
    assert "no such power" in str(form.validate(wrong))
    # Communication 2 + Charm 1 + Pious 2 = 5; 9 + 5 = 14 against 15 + 2.
    lines = form.apply(values)
    assert lines[0] == "Die 9 + 5 = 14 against 15 + 2 = 17."
    assert yusuf.diary[-1].name.startswith("Sought the baraka of")
    assert isinstance(forms.baraka_form(saga, None), Refuse)


def test_the_hajj_brings_pious_three_and_faith():
    saga = _saga()
    yusuf = saga.character("y")
    form = _form(forms.hajj_form(saga, yusuf))
    assert "Pious +2 → [b]+3[/]" in form.live({})
    lines = form.apply({"notes": ""})
    assert yusuf.background.faith_points == 3
    assert next(t.score for t in yusuf.personality_traits if t.name == "Pious") == 3
    assert lines[0] == "Pious rises from +2 to +3."
    # Made again: Faith restored, Pious never above +3.
    yusuf.personality_traits[1].score = 5
    form.apply({"notes": ""})
    assert yusuf.personality_traits[1].score == 5
    assert yusuf.background.faith_points == 6
    assert yusuf.diary[-1].name == "Made the Hajj"


def test_offered_to_a_muslim_with_the_book():
    saga = _saga()
    faith = replace(
        menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="y"),
        section=FAITH_SECTION,
    )
    for action in ("invoke_baraka", "hajj"):
        assert available(action, faith)
        assert isinstance(menu_forms.command(faith, action), Form)
    assert not available("invoke_saint", faith)
    saga.character("y").background.religion = ""
    assert not available("invoke_baraka", faith)
    saga.character("y").background.religion = "Muslim"
    saga.books_in_play = ["TC"]
    assert not available("hajj", faith)
