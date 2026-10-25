"""The casting Virtues and Flaws the Casting Score can't hold (DE pp.
70-145): their reminders, Clumsy and Inconstant Magic on aiming,
Incompatible Arts, and in a fight Painful Magic and Life-Linked
Spontaneous Magic."""

import random

from ars_magica_manager.models import (
    ArtScore,
    Character,
    Combatant,
    Fight,
    FightSide,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import casting, casting_virtues
from ars_magica_manager.rules import fight as rules


class Scripted(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def magus_with(*vf_ids: str, **params: str) -> Character:
    m = Character(id="m", name="Marcus", type="magus")
    m.arts["creo"] = ArtScore(xp=55)
    m.arts["ignem"] = ArtScore(xp=55)
    for vf_id in vf_ids:
        m.virtues_flaws.append(VirtueFlawInstance(vf_id=vf_id, params=dict(params)))
    return m


def test_every_new_virtue_and_flaw_has_a_reminder_with_its_page():
    for vf_id in casting_virtues.NOTES:
        note = casting_virtues.reminders(magus_with(vf_id))[-1]
        assert "(DE p" in note, vf_id


def test_clumsy_and_inconstant_magic_each_take_three_off_aiming():
    plain = casting.aiming_base(magus_with())
    both = casting.aiming_base(
        magus_with(casting_virtues.CLUMSY_MAGIC, casting_virtues.INCONSTANT)
    )
    assert both == plain - 6


def test_incompatible_arts_rule_out_the_pair_even_as_a_requisite():
    m = magus_with(casting_virtues.INCOMPATIBLE, arts="Intellego Herbam, InAn")
    assert casting_virtues.incompatible(m, "Intellego", "Herbam")
    assert casting_virtues.incompatible(m, "Intellego", "Corpus", ("Animal",))
    assert not casting_virtues.incompatible(m, "Creo", "Herbam")


def _fight_for(magus: Character) -> tuple[Saga, Fight]:
    fight = Fight(
        "Test",
        sides=[
            FightSide(
                "Ours",
                combatants=[Combatant("Marcus", "character", "m", id="marcus")],
            ),
            FightSide(
                "Theirs", combatants=[Combatant("Brigand", id="brigand", soak=0)]
            ),
        ],
    )
    return Saga(id="s", name="S", fights=[fight], characters=[magus]), fight


def test_painful_magic_brings_a_level_of_pain_with_each_spell():
    magus = magus_with(casting_virtues.PAINFUL)
    saga, fight = _fight_for(magus)
    blow = rules.Blow(
        rules.CAST,
        "brigand",
        spell=rules.SPONTANEOUS,
        arts="Creo Ignem",
        level=5,
        fatiguing=False,
    )
    played = rules.play(saga, fight, blow, Scripted(9, 2))
    assert any("Painful Magic" in line for line in played.lines)
    assert magus.fatigue_level != "fresh"


def test_life_linked_spends_more_fatigue_to_reach_the_level_declared():
    magus = magus_with(casting_virtues.LIFE_LINKED)
    saga, fight = _fight_for(magus)
    blow = rules.Blow(
        rules.CAST,
        "brigand",
        spell=rules.SPONTANEOUS,
        arts="Creo Ignem",
        level=40,
        fatiguing=True,
    )
    played = rules.play(saga, fight, blow, Scripted(9, 2, 4))
    assert any("Life-Linked" in line for line in played.lines)
    assert "falls short" not in played.text


def test_without_life_linked_a_short_spontaneous_spell_fails():
    magus = magus_with()
    saga, fight = _fight_for(magus)
    blow = rules.Blow(
        rules.CAST,
        "brigand",
        spell=rules.SPONTANEOUS,
        arts="Creo Ignem",
        level=40,
        fatiguing=True,
    )
    played = rules.play(saga, fight, blow, Scripted(9, 2, 4))
    assert "falls short" in played.text
