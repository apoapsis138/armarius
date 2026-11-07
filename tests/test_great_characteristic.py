"""Great and Poor (Characteristic) move the score they name: taking one
adds (or takes) a point, only from +3/+4 (-3/-4), and removing it gives
the point back."""

from screen_helpers import (
    _open_section,
    _saga_with_bare_character,
    _select_character,
)
from support import choose, strip_markup, wait_until
from textual.widgets import Select, Static

from ars_magica_manager import storage
from ars_magica_manager.models import Character, Saga, VirtueFlawInstance
from ars_magica_manager.rules import creation_characteristics as cch
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.fields import FieldsDialog
from ars_magica_manager.tui.screens.prompts import ConfirmScreen
from ars_magica_manager.tui.screens.steps import ChooseScreen
from ars_magica_manager.tui.screens.workspace import WorkspaceScreen


def _great(key: str = "intelligence") -> VirtueFlawInstance:
    return VirtueFlawInstance("vf_great_characteristic", {"characteristic": key})


def _poor(key: str = "presence") -> VirtueFlawInstance:
    return VirtueFlawInstance("vf_poor_characteristic", {"characteristic": key})


def _magus(**scores: int) -> tuple[Saga, Character]:
    saga = Saga(id="s", name="S", current_year=1220)
    character = Character(id="c", name="Corvinus", type="magus")
    for key, score in scores.items():
        setattr(character.characteristics, key, score)
    return saga, character


def test_great_needs_three_and_stops_at_five():
    saga, corvinus = _magus(intelligence=2)
    assert cch.virtue_refusal(saga, corvinus, _great()) == (
        "Great Intelligence needs Intelligence at +3 first (it is +2)."
    )
    for score in (3, 4):
        corvinus.characteristics.intelligence = score
        assert cch.virtue_refusal(saga, corvinus, _great()) == ""
    corvinus.characteristics.intelligence = 5
    assert "already +5" in cch.virtue_refusal(saga, corvinus, _great())


def test_two_copies_take_three_to_five_and_back():
    saga, corvinus = _magus(intelligence=3)
    for expected in (4, 5):
        cch.apply_virtue(saga, corvinus, _great())
        corvinus.virtues_flaws.append(_great())
        assert corvinus.characteristics.intelligence == expected
    assert cch.removal_changes(saga, corvinus, _great()) == [
        ("intelligence", "Intelligence", 5, 4)
    ]
    cch.unapply_virtue(saga, corvinus, _great())
    assert corvinus.characteristics.intelligence == 4


def test_removing_great_from_a_score_it_never_raised_moves_nothing():
    # A save from before Great raised the score: Int +3 with two copies.
    saga, corvinus = _magus(intelligence=3)
    assert cch.removal_changes(saga, corvinus, _great()) == []
    cch.unapply_virtue(saga, corvinus, _great())
    assert corvinus.characteristics.intelligence == 3


def test_poor_mirrors_great():
    saga, character = _magus(presence=-2)
    assert "at -3 first" in cch.virtue_refusal(saga, character, _poor())
    character.characteristics.presence = -3
    assert cch.virtue_refusal(saga, character, _poor()) == ""
    cch.apply_virtue(saga, character, _poor())
    assert character.characteristics.presence == -4
    assert cch.removal_changes(saga, character, _poor()) == [
        ("presence", "Presence", -4, -3)
    ]


def test_great_on_a_child_counts_from_the_score_before_the_age_modifier():
    # Age 10: -2 on each, so Int +1 shown is +3.
    saga, child = _magus(intelligence=1)
    child.background.year_born = 1210
    assert cch.virtue_refusal(saga, child, _great()) == ""
    cch.apply_virtue(saga, child, _great())
    assert child.characteristics.intelligence == 2


def _bare_saga(**scores: int) -> Saga:
    saga = _saga_with_bare_character()
    for key, score in scores.items():
        setattr(saga.characters[0].characteristics, key, score)
    return saga


async def _open_picker(pilot, app) -> ChooseScreen:
    await _select_character(pilot, app)
    await _open_section(pilot, app, "section-vf-virtues")
    await pilot.press("a")
    assert await wait_until(pilot, lambda: isinstance(app.screen, ChooseScreen))
    picker = app.screen
    assert isinstance(picker, ChooseScreen)
    return picker


async def test_taking_great_raises_the_score_and_offers_only_scores_at_three():
    storage.save_saga(_bare_saga(intelligence=3, strength=4, stamina=2))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_picker(pilot, app)
        await choose(pilot, app, "Great (Characteristic)")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        assert await wait_until(
            pilot, lambda: bool(app.screen.query("#fld-characteristic"))
        )
        select = app.screen.query_one("#fld-characteristic", Select)
        offered = [value for _, value in select._options if isinstance(value, str)]
        assert offered == ["intelligence", "strength"]
        select.value = "intelligence"
        await pilot.click("#btn-save")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    [corvinus] = storage.load_saga("test_saga").characters
    assert corvinus.characteristics.intelligence == 4
    assert corvinus.virtues_flaws == [_great()]


async def test_great_is_ineligible_with_no_score_at_three():
    storage.save_saga(_bare_saga(intelligence=2))

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        picker = await _open_picker(pilot, app)
        # Not offered, and marked with why.
        assert not any(c.value.id == "vf_great_characteristic" for c in picker.choices)
        marked = [
            strip_markup(c.label)
            for c in picker.others
            if c.value.id == "vf_great_characteristic"
        ]
        assert marked and "every Characteristic is refused" in marked[0]


async def test_removing_great_gives_the_point_back():
    saga = _bare_saga(intelligence=4)
    saga.characters[0].virtues_flaws.append(_great())
    storage.save_saga(saga)

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _select_character(pilot, app)
        await _open_section(pilot, app, "section-vf-virtues")
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        message = app.screen.query_one("#confirm-message", Static)
        assert "Intelligence goes from +4 to +3" in str(message.render())
        await pilot.press("y")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))

    [corvinus] = storage.load_saga("test_saga").characters
    assert corvinus.characteristics.intelligence == 3
    assert corvinus.virtues_flaws == []
