"""A character's Description forms (character_forms), without a front-end:
what each Edit asks for and what saving it changes."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import character_forms as cf
from ars_magica_manager import form_spec
from ars_magica_manager.commands import Form


def _magus():
    saga = _sample_saga_with_covenant()
    return saga, next(c for c in saga.characters if c.type == "magus")


def _saved(edit: Form, typed: dict[str, object]):
    """Save `edit`'s form as it opens, with `typed` entered over it."""
    fields = edit.fields()
    values = {spec.key: spec.value for spec in fields}
    values.update(typed)
    result = form_spec.result(
        [spec for spec in fields if spec.kind != "info"],
        lambda spec: "" if values[spec.key] is None else values[spec.key],
    )
    return edit.apply(result)


def test_a_magus_has_a_hermetic_background_to_edit_and_a_companion_does_not():
    saga, magus = _magus()
    assert list(cf.description_edits(saga, magus)) == [
        "Biographical Detail",
        "Wounds",
        "Fatigue",
        "Aging",
        "Hermetic Background",
    ]
    magus.type = "companion"
    assert "Hermetic Background" not in cf.description_edits(saga, magus)


def test_saving_biographical_detail_sets_the_background_and_description():
    saga, magus = _magus()
    edit = cf.description_edits(saga, magus)["Biographical Detail"]
    assert not _saved(edit, {"hair": "Grey", "year_born": "1185", "height": "1.8"})
    assert magus.description.hair == "Grey"
    assert magus.description.height == 1.8
    assert magus.background.year_born == 1185


def test_wounds_fatigue_and_the_hermetic_background_save_whole():
    saga, magus = _magus()
    edits = cf.description_edits(saga, magus)
    _saved(edits["Wounds"], {"light": "2", "dead": False})
    _saved(edits["Fatigue"], {"level": "winded"})
    _saved(edits["Hermetic Background"], {"parens": "Fenicil"})
    assert magus.wounds.light == 2
    assert magus.fatigue_level == "winded"
    assert magus.hermetic.parens == "Fenicil"


def test_changing_decrepitude_resets_its_points_and_gaining_no_warping_says_nothing():
    saga, magus = _magus()
    edit = cf.description_edits(saga, magus)["Aging"]
    assert not _saved(edit, {"decrepitude": "2"})
    assert magus.aging.decrepitude == 2
    assert magus.aging.decrepitude_points > 0


def test_gaining_warping_now_reports_what_happened():
    saga, magus = _magus()
    edit = cf.description_edits(saga, magus)["Aging"]
    notes = _saved(edit, {"gain_warping": "1"})
    assert notes and magus.aging.warping_points == 1
