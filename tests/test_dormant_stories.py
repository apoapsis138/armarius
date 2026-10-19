"""Stories chosen on import: a threat left unticked comes in dormant,
reaches no stage until it is begun, and the Tribunal sheet counts it."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import actions, packs, storage, threats, transfer
from ars_magica_manager.commands import Confirm
from ars_magica_manager.models import Neighbour, Saga
from ars_magica_manager.sheets import region as region_sheet
from ars_magica_manager.sheets import tribunal as tribunal_sheet


def _threat(saga: Saga) -> Neighbour:
    crown = next(n for n in saga.neighbours if n.id == "crown")
    return crown


def _pack(saga: Saga) -> dict:
    return packs.pack_data(saga, "Threats", [], [], [_threat(saga)])


def test_a_dormant_threat_reaches_nothing_and_shows_as_dormant():
    saga = everything_saga()
    crown = _threat(saga)
    saga.current_year, saga.current_season = 1221, "Spring"
    assert threats.reached(saga, crown).current is not None
    crown.details[threats.DORMANT] = True
    assert threats.reached(saga, crown) == threats.Reached(None, None)
    assert threats.due(saga, crown) is None
    assert region_sheet.kind_text(crown) == "Dormant"
    facts = {f.label: f.value for f in threats.facts(saga, crown)}
    assert "Begin This Story" in facts["Dormant"]
    grid = threats.stages_grid(saga, crown)
    assert {row[2] for row in grid.rows} == {"To come"}


def test_beginning_a_story_moves_its_dates_on():
    saga = everything_saga()
    crown = _threat(saga)
    crown.details[threats.DORMANT] = True
    saga.current_year, saga.current_season = 1225, "Summer"
    command = threats.begin_command(saga, crown)
    assert isinstance(command, Confirm)
    shown = command.apply()
    assert not threats.is_dormant(crown)
    stages = threats.stages(crown)
    # The first stage was Spring 1219: now it is next season, Autumn 1225,
    # and the others keep their distance from it.
    assert (stages[0]["year"], stages[0]["season"]) == (1225, "Autumn")
    assert (stages[1]["year"], stages[1]["season"]) == (1227, "Summer")
    # A stage with no season comes at the start of its year.
    assert (stages[2]["year"], stages[2]["season"]) == (1229, None)
    assert threats.reached(saga, crown).next is stages[0]
    assert "Autumn 1225" in shown[0]


def test_beginning_keeps_dates_still_to_come():
    saga = everything_saga()
    crown = _threat(saga)
    crown.details[threats.DORMANT] = True
    saga.current_year, saga.current_season = 1218, "Spring"
    threats.begin(saga, crown)
    assert threats.stages(crown)[0]["year"] == 1219


def test_begin_is_offered_on_a_dormant_threat_only():
    assert any(item.action == "begin_story" for item in actions.MORE_MENU)
    saga = everything_saga()
    crown = _threat(saga)
    assert not threats.is_dormant(crown)
    crown.details[threats.DORMANT] = True
    assert threats.is_dormant(crown)
    other = next(n for n in saga.neighbours if n.kind != "threat")
    other.details[threats.DORMANT] = True
    assert not threats.is_dormant(other)


def test_the_tribunal_sheet_counts_dormant_stories():
    saga = everything_saga()
    tribunal = saga.tribunals[0]
    labels = [f.label for f in tribunal_sheet.facts(saga, tribunal)]
    assert "Stories" not in labels
    _threat(saga).details[threats.DORMANT] = True
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, tribunal)}
    assert facts["Stories"] == "0 under way, 1 dormant"


def test_the_import_form_asks_which_stories_to_begin():
    saga = everything_saga()
    data = _pack(saga)
    fields = {f.key: f for f in packs.import_fields(data)}
    tick = fields[packs.story_key("crown")]
    assert tick.label == "Begin: The Hollow Crown" and tick.value is True
    assert tick.show_if is not None and not tick.show_if({"world": False})
    # A story the saga already has isn't asked about.
    assert packs.story_key("crown") not in {
        f.key for f in packs.import_fields(data, saga)
    }
    left = packs.narrow(data, {packs.story_key("crown"): False})
    (crown,) = [n for n in left["saga"]["neighbours"] if n["id"] == "crown"]
    assert crown["details"][threats.DORMANT] is True
    assert not data["saga"]["neighbours"][0]["details"].get(threats.DORMANT)
    target = Saga(id="t", name="Target")
    transfer.apply(target, transfer.plan_import(target, left))
    assert threats.is_dormant(target.neighbours[0])


def test_starting_from_a_pack_asks_which_stories_to_begin(tmp_path):
    saga = everything_saga()
    path = packs.write(storage.EXPORTS_DIR / "threats.amm.json", _pack(saga))
    found = [("Threats", str(path))]
    (tick,) = packs.start_story_fields(found)
    assert tick.key == "pack0_story_crown"
    assert tick.show_if is not None and tick.show_if({"pack": str(path)})
    assert not tick.show_if({"pack": ""})
    choices = packs.start_choices({"name": "S", "pack0_story_crown": False})
    assert choices == {"story_crown": False}
    target = Saga(id="t", name="Target")
    packs.start_from(target, path, choices)
    assert threats.is_dormant(target.neighbours[0])
