"""Optional rules and rounding (STORY-819)."""

import pytest

from ars_magica_manager import storage
from ars_magica_manager.models import Saga
from ars_magica_manager.rules import options, rounding
from ars_magica_manager.screens.forms import (
    RULE_OPTION_PREFIX,
    _saga_fields,
    saga_rule_options,
)


def test_every_option_starts_off():
    saga = Saga(id="s", name="S")
    assert all(not options.is_on(saga, o.key) for o in options.OPTIONS)
    assert options.summary(saga).startswith("none")


def test_an_unknown_option_is_a_mistake():
    with pytest.raises(KeyError):
        options.is_on(Saga(id="s", name="S"), "no_such_rule")


def test_turning_an_option_on_is_saved(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "SAGAS_DIR", tmp_path)
    saga = Saga(id="s", name="S", rule_options={"simple_dice_only": True})
    storage.save_saga(saga)
    loaded = storage.load_saga("s")
    assert options.is_on(loaded, "simple_dice_only")
    assert options.summary(loaded) == "Simple dice only"


def test_the_saga_form_offers_each_option_and_keeps_only_those_on():
    saga = Saga(id="s", name="S")
    keys = [f.key for f in _saga_fields(saga)]
    assert RULE_OPTION_PREFIX + "simple_dice_only" in keys
    assert not any(
        k.startswith(RULE_OPTION_PREFIX) for k in [f.key for f in _saga_fields(None)]
    )

    values = {"name": "S", RULE_OPTION_PREFIX + "simple_dice_only": False}
    assert saga_rule_options(values) == {}
    assert values == {"name": "S"}  # the option keys are taken out
    values = {RULE_OPTION_PREFIX + "simple_dice_only": True}
    assert saga_rule_options(values) == {"simple_dice_only": True}


def test_a_removed_option_is_dropped():
    assert options.normalized({"simple_dice_only": True, "gone": True}) == {
        "simple_dice_only": True
    }


@pytest.mark.parametrize(
    ("value", "down", "up", "toward_zero", "nearest"),
    [
        (2.5, 2, 3, 2, 3),
        (-2.5, -3, -2, -2, -3),
        (-37.5, -38, -37, -37, -38),  # Covenants' Base Loyalty example
        (55.5, 55, 56, 55, 56),  # Affinity with Perdo: 37 xp x1.5 -> 56
        (4.0, 4, 4, 4, 4),
    ],
)
def test_rounding(value, down, up, toward_zero, nearest):
    assert rounding.round_down(value) == down
    assert rounding.round_up(value) == up
    assert rounding.round_toward_zero(value) == toward_zero
    assert rounding.round_nearest(value) == nearest
