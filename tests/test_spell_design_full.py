"""Spell design in full: what a Target reaches for its size (DE pp. 310,
546) and casting requisites chosen when a spell is cast (DE p. 312)."""

from ars_magica_manager import fights
from ars_magica_manager.models import (
    ArtScore,
    Character,
    Combatant,
    Fight,
    FightSide,
    Saga,
    Spell,
)
from ars_magica_manager.rules import casting, target_sizes
from ars_magica_manager.rules import fight as rules
from ars_magica_manager.rules.xp import art_xp


def test_a_target_grows_tenfold_a_magnitude_from_its_forms_base():
    text = target_sizes.size_text("Creo", "Terram", "Individual", 2)
    assert "up to 100 times one base Individual" in text
    assert "a cubic pace of stone" in text
    group = target_sizes.size_text("Muto", "Corpus", "Group", 0)
    assert group.startswith("Group at its base size: the mass of ten base Individuals")
    assert "an adult human" in group


def test_where_size_doesnt_matter():
    assert "Intellego" in target_sizes.size_text("Intellego", "Ignem", "Room", 1)
    assert "Circle" in target_sizes.size_text("Rego", "Vim", "Circle", 0)
    assert target_sizes.size_text("Rego", "Mentem", "Individual", 0) == (
        "Size doesn't apply to a Mentem Individual."
    )
    assert "number of minds" in target_sizes.size_text("Rego", "Mentem", "Group", 1)
    assert target_sizes.size_text("Creo", "Ignem", "Taste", 0) == ""


def _magus() -> Character:
    magus = Character(id="m", name="Marcus", type="magus")
    magus.arts = {
        "creo": ArtScore(xp=art_xp(10)),
        "ignem": ArtScore(xp=art_xp(10)),
        "rego": ArtScore(xp=art_xp(3)),
        "animal": ArtScore(xp=art_xp(2)),
    }
    return magus


def test_casting_requisites_lower_the_score_to_the_lowest_art():
    magus = _magus()
    spell = Spell("ball", "Ball of Fire", "Creo", "Ignem", level=15)
    plain = casting.spell_casting_score(magus, spell).total
    both = casting.spell_casting_score(
        magus, spell, casting_requisites=("Rego", "Animal")
    ).total
    assert plain - both == (10 - 3) + (10 - 2)


def test_next_blow_asks_for_casting_requisites():
    blow = fights.blow_of(
        {
            "action": rules.CAST,
            "target": "x",
            "spell": "ball",
            "requisite_technique": "Rego",
            "requisite_form": None,
        }
    )
    assert blow.casting_requisites == ("Rego",)


def test_a_spell_cast_in_a_fight_counts_its_casting_requisites():
    magus = _magus()
    fight = Fight(
        "Test",
        sides=[
            FightSide(
                "Ours", combatants=[Combatant("Marcus", "character", "m", id="me")]
            ),
            FightSide("Theirs", combatants=[Combatant("Brigand", id="them")]),
        ],
    )
    saga = Saga(id="s", name="S", fights=[fight], characters=[magus])
    saga.spells = [Spell("ball", "Ball of Fire", "Creo", "Ignem", level=15)]
    found = rules.units(saga, fight)
    who, target = found["me"], found["them"]
    plain = rules.spell_odds(
        saga, fight, who, target, rules.Blow(rules.CAST, "them", spell="ball")
    )
    with_rego = rules.spell_odds(
        saga,
        fight,
        who,
        target,
        rules.Blow(rules.CAST, "them", spell="ball", casting_requisites=("Rego",)),
    )
    assert plain is not None and with_rego is not None
    assert plain.score is not None and with_rego.score is not None
    assert plain.score - with_rego.score == 7
    assert with_rego.requisites == ("Rego",)
