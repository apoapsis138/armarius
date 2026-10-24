"""The supernatural senses' Ease Factors (DE pp. 168-170), seeing into a
regio level (DE p. 421), and Magic Resistance from Magic Sensitivity and the
Dominion option."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import places, sheet_text
from ars_magica_manager.models import Ability, ArtScore, Character, Neighbour
from ars_magica_manager.rules import penetration, senses
from ars_magica_manager.rules.xp import ability_xp, art_xp


def test_the_senses_ease_factors():
    assert senses.magic_aura_ease(3) == 9
    assert senses.magic_effect_ease(4) == 17
    assert senses.magic_creature_ease(25) == 10
    assert senses.illusion_ease(2) == 8
    assert (senses.AREA_EASE, senses.PERSON_EASE, senses.DEMON_EASE) == (9, 15, 0)


def test_regio_sight_adds_the_auras_from_another_realm():
    # DE p. 421's example: from a Divine 3 aura into a Magic 5 level, 21.
    assert senses.regio_sight_ease(3, "Divine", 5, "Magic") == 21
    assert senses.regio_sight_ease(3, "Magic", 5, "Magic") == 9
    assert senses.regio_sight_ease(0, "Magic", 4, "Faerie") == 13


def test_a_regio_level_shows_its_own_roll_or_the_book_s():
    place = Neighbour(id="p", name="P", kind="place", realm="Magic")
    place.details = {
        "aura": 3,
        "levels": [
            {"name": "Low", "realm": "Magic", "aura": 5},
            {
                "name": "High",
                "realm": "Magic",
                "aura": 6,
                "see": "Per + Awareness against 12",
            },
        ],
    }
    assert places.see_in_text(place, 1) == "9 DE"
    assert places.see_in_text(place, 2) == "12"


def test_an_ability_s_details_list_its_ease_factors():
    abilities = [Ability("Second Sight", xp=ability_xp(2))]
    text = sheet_text.ability_info_text(abilities, 0)
    assert "a naturally invisible thing 9" in text
    assert "Ease Factors" not in sheet_text.ability_info_text(
        [Ability("Brawl", xp=ability_xp(2))], 0
    )


def test_magic_sensitivity_lowers_magic_resistance():
    magus = Character(
        id="m",
        name="M",
        type="magus",
        arts={"ignem": ArtScore(xp=art_xp(5))},
        abilities=[
            Ability("Parma Magica", xp=ability_xp(2)),
            Ability("Magic Sensitivity", xp=ability_xp(3)),
        ],
    )
    total = penetration.magic_resistance(magus, "Ignem")
    assert total.total == 5 + 10 - 3


def test_the_dominion_option_gives_the_faithful_magic_resistance():
    saga = everything_saga()
    character = saga.characters[0]
    covenant = saga.covenant(character.covenant_id)
    assert covenant is not None
    covenant.aura, covenant.aura_realm = 3, "Divine"
    covenant.boons_hooks = []
    assert penetration.faith_magic_resistance(character, saga) == 0
    saga.rule_options["dominion_magic_resistance"] = True
    character.background.religion = "Christian"
    assert penetration.faith_magic_resistance(character, saga) == 15
    character.background.religion = "Norse paganism"
    assert penetration.faith_magic_resistance(character, saga) == 0
