"""Auras and realm interaction, checked against the book's
worked examples."""

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.covenants import covenant_effective_aura
from ars_magica_manager.models import Covenant, VirtueFlawInstance
from ars_magica_manager.rules import realms


@pytest.mark.parametrize(
    ("power", "aura_realm", "aura", "modifier", "botch"),
    [
        # Dominion 3: Hermetic -9, Faerie -12, Infernal -15, each +3 botch dice.
        ("Magic", "Divine", 3, -9, 3),
        ("Faerie", "Divine", 3, -12, 3),
        ("Infernal", "Divine", 3, -15, 3),
        # Faerie 4: Hermetic +2 with +4 botch dice; Faerie +4, no extra
        # dice; Infernal -4 with +4 botch dice.
        ("Magic", "Faerie", 4, 2, 4),
        ("Faerie", "Faerie", 4, 4, 0),
        ("Infernal", "Faerie", 4, -4, 4),
        ("Magic", "Magic", 5, 5, 0),
        ("Magic", "Faerie", 3, 1, 3),  # half of 3 rounds down
        ("Divine", "Infernal", 6, 0, 0),  # Divine powers are never hindered
    ],
)
def test_realm_interaction(power, aura_realm, aura, modifier, botch):
    assert realms.aura_modifier(power, aura_realm, aura) == modifier
    assert realms.extra_botch_dice(power, aura_realm, aura) == botch


def test_a_regio_of_another_realm_doubles_the_botch_dice():
    assert realms.extra_botch_dice("Magic", "Divine", 3, in_regio=True) == 6


def test_an_unknown_realm_is_refused():
    with pytest.raises(ValueError, match="realm"):
        realms.aura_modifier("Magic", "Elemental", 3)


def test_the_hermetic_note_only_speaks_up_outside_a_magic_aura():
    assert realms.aura_note("Magic", 5) == ""
    assert realms.aura_note("Divine", 3) == "Hermetic magic -9, +3 botch dice"
    assert realms.aura_note("Faerie", 1) == "Hermetic magic +0, +1 botch die"


def test_covenant_aura_adds_its_boons():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    aura_boon = next(
        e.id
        for e in by_id.values()
        if any(
            m.applies_to == "covenant_aura" and (m.amount or 0) > 0 for m in e.modifiers
        )
    )
    covenant = Covenant(
        id="c",
        saga_id="s",
        name="C",
        aura=3,
        boons_hooks=[VirtueFlawInstance(vf_id=aura_boon)] * 2,
    )
    breakdown = realms.covenant_aura(covenant, by_id)
    assert breakdown.total == 5
    assert breakdown.lines[0].label == "Base aura"
    assert covenant_effective_aura(covenant, by_id) == 5


def test_old_covenants_load_with_a_magic_aura():
    assert (
        Covenant.from_dict({"id": "c", "saga_id": "s", "name": "C"}).aura_realm
        == "Magic"
    )
