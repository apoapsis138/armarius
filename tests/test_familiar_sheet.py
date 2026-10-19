"""The familiar page's figures (familiar_sheet), without a front-end."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import familiars as fam
from ars_magica_manager.models import BondPower, Possession
from ars_magica_manager.sheets import familiar as fs


def _familiar():
    saga = _sample_saga_with_covenant()
    magus = next(c for c in saga.characters if c.type == "magus")
    return saga, magus, fam.bind_familiar(saga, magus, "Nox")


def test_the_subtitle_names_the_magus_species_and_binding():
    saga, magus, familiar = _familiar()
    familiar.species = "an owl"
    familiar.season_bound, familiar.year_bound = "Autumn", 1218
    assert fs.subtitle(saga, familiar) == (
        f"Familiar of {magus.name}  ·  an owl  ·  bound Autumn 1218  ·  Spring 1220"
    )


def test_each_cord_has_its_score_cost_and_effect():
    _saga, _magus, familiar = _familiar()
    familiar.golden_cord = 3
    golden, silver, bronze = fs.cords(familiar)
    assert (golden.name, golden.score, golden.cost) == (
        "Golden Cord",
        3,
        fam.cord_cost(3),
    )
    assert "Botch" in golden.effect
    assert (silver.score, bronze.score) == (0, 0)


def test_the_might_pool_is_shown_only_when_tracked():
    _saga, _magus, familiar = _familiar()
    familiar.magic_might = 15
    assert fs.might_pool(familiar) == ""
    familiar.might_pool = 12
    assert fs.might_pool(familiar) == "12 of 15 in the pool"


def test_natural_weapons_show_only_their_combat_figures():
    _saga, _magus, familiar = _familiar()
    familiar.natural_weapons = [
        Possession("w1", "weapon", "Talons", weapon_init=2, weapon_damage=None)
    ]
    table = fs.natural_weapons(familiar)
    assert table.columns == ["Attack", "Init", "Atk", "Def", "Dmg"]
    assert table.rows == [["Talons", "+2", "+0", "+0", "n/a"]]


def test_the_wound_track_follows_the_familiars_size():
    _saga, _magus, familiar = _familiar()
    familiar.size = -2
    light = fs.wound_track(familiar)[0]
    assert (light.name, light.low, light.high) == ("Light", 1, 3)


def test_bond_powers_are_cards_with_their_arts():
    _saga, _magus, familiar = _familiar()
    familiar.bond_powers = [BondPower("b1", "Silent Wings", 10, "Perdo", "Imaginem")]
    (card,) = fs.bond_power_cards(familiar)
    assert (card.index, card.name, card.level, card.arts) == (
        0,
        "Silent Wings",
        10,
        "Perdo Imaginem",
    )


def test_a_familiar_belongs_to_its_maguss_covenant():
    saga, magus, familiar = _familiar()
    assert fs.familiars_in(saga, magus.covenant_id) == [familiar]
    assert fs.familiars_in(saga, None) == []
    card = fs.familiar_card(saga, familiar)
    assert (card.id, card.name) == (familiar.id, "Nox")
    assert card.subtitle == f"Familiar of {magus.name}"
