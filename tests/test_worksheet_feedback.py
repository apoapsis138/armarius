"""The Creation Worksheet's feedback: each step's budgets as meters, one
ledger of what every step put into each Ability and Art, and a line naming
the broken rules that leads to their steps."""

from __future__ import annotations

import os

import pytest
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import creation
from ars_magica_manager import worksheet_feedback as feedback
from ars_magica_manager.models import CreationXp


def _magus_in_creation():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    magus.in_creation = True
    magus.abilities = []
    for step, target, xp, note in (
        ("childhood", "Living Language: French", 75, "native"),
        ("childhood", "Athletics", 15, ""),
        ("later_life", "Athletics", 10, ""),
        ("later_life", "Magic Theory", 60, ""),
        ("apprenticeship", "Magic Theory", 30, ""),
    ):
        creation.spend_creation_xp(magus, CreationXp(step, target, xp, note))
    return saga, magus


def test_a_meter_says_what_is_left_or_over():
    assert feedback.Meter("Later Life", 30, 45).words() == "30 of 45 xp, 15 left"
    over = feedback.Meter("Later Life", 50, 45)
    assert over.over and over.words() == "50 of 45 xp, 5 over"


def test_each_xp_step_meters_its_budget():
    saga, magus = _magus_in_creation()
    childhood = feedback.meters(saga, magus, "childhood")
    assert [(m.label, m.spent, m.total) for m in childhood] == [
        ("Native Language", 75, 75),
        ("Other childhood xp", 15, 45),
    ]
    later = feedback.meters(saga, magus, "later_life")[0]
    assert (later.label, later.spent) == ("Later Life", 70)
    labels = [m.label for m in feedback.meters(saga, magus, "apprenticeship")]
    assert labels == ["Arts and Abilities", "Spell levels"]
    assert feedback.meters(saga, magus, "concept") == []


def test_the_ledger_shows_every_steps_xp_with_this_steps_first():
    _saga, magus = _magus_in_creation()
    table = feedback.ledger(magus, "later_life")
    assert table.columns == [
        "Ability or Art",
        "Later Life",
        "Early Childhood",
        "Apprenticeship",
        "Total xp",
        "Score",
    ]
    rows = {row[0]: row for row in table.rows}
    assert rows["Magic Theory"][1:] == ["[b]60[/]", "", "30", "90", "5"]
    assert rows["Athletics"][1:4] == ["[b]10[/]", "15", ""]
    assert feedback.shows_ledger(magus, "later_life")
    assert not feedback.shows_ledger(magus, "concept")


def test_broken_rules_name_their_steps():
    saga, magus = _magus_in_creation()
    found = feedback.broken(saga, magus)
    assert found and all(b.step and b.step_title for b in found)
    # Magic Theory in Later Life breaks "Only Abilities the character may
    # learn" for a magus without The Gift.
    assert "Later Life" in {b.step_title for b in found}
    magus.in_creation = False
    assert feedback.broken(saga, magus) == []


def test_the_desktop_worksheet_draws_bars_the_ledger_and_the_broken_line():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager import storage
    from ars_magica_manager.gui.window import MainWindow
    from ars_magica_manager.gui.worksheet import MeterBar, WorksheetPage

    QApplication.instance() or QApplication([])
    saga, magus = _magus_in_creation()
    creation.spend_creation_xp(magus, CreationXp("childhood", "Awareness", 40, ""))
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.open_worksheet(magus.id)
    page = window.page()
    assert isinstance(page, WorksheetPage)
    page.open_step("childhood")
    bars = {
        bar.meter.label: bar
        for bar in page.findChildren(MeterBar)
        if bar.meter.label in ("Native Language", "Other childhood xp")
    }
    assert bars["Native Language"].colour() == window.palette_["accent"]
    # 55 of 45: red.
    assert bars["Other childhood xp"].meter.over
    assert bars["Other childhood xp"].colour() == window.palette_["text-error"]
    assert page.broken.isVisibleTo(page)
    page.broken.linkActivated.emit("later_life")
    assert page.codex.rail.currentRow() == [s.key for s in page.steps].index(
        "later_life"
    )
