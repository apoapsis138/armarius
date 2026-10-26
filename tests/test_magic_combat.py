"""Magic in a fight (rules.magic_combat, wired into rules.fight): House
Flambeau's schools of magical combat, indirect spells that bypass Magic
Resistance and are aimed, Spell Mastery and Arcane Connections in a
spell's totals, and fighting invisibly (Houses of Hermes: Societates pp.
25-33; DE pp. 219-226). The dice are scripted: each test says what each
d10 shows."""

import dataclasses
import random

from ars_magica_manager import catalog, fights
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Combatant,
    Fight,
    FightGroup,
    FightSide,
    KnownSpell,
    MasteryAbility,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import fight as rules
from ars_magica_manager.rules import magic_combat
from ars_magica_manager.rules.xp import ability_xp


class Scripted(random.Random):
    """A d10 that throws the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def typed(name: str, **figures) -> Combatant:
    return Combatant(name, id=name.lower().replace(" ", "-"), **figures)


def fight_of(first: list[Combatant], second: list[Combatant]) -> Fight:
    return Fight(
        "Test fray",
        sides=[
            FightSide("Ours", combatants=first),
            FightSide("Theirs", combatants=second),
        ],
    )


def saga_with(fight: Fight, *characters: Character) -> Saga:
    return Saga(id="s", name="S", fights=[fight], characters=list(characters))


def spell_id(name: str) -> str:
    found = catalog.find_spell_by_name(Saga(id="x", name="x"), name)
    assert found is not None
    return found.id


def flambeau(**arts: int) -> Character:
    """A magus with each Art at the score given (xp for 10 is 55)."""
    magus = Character(id="m", name="Marcus", type="magus")
    for art, xp in arts.items():
        magus.arts[art] = ArtScore(xp=xp)
    return magus


def caster_fight(target: Combatant, magus: Character) -> tuple[Saga, Fight]:
    fight = fight_of([Combatant("Marcus", "character", "m", id="marcus")], [target])
    return saga_with(fight, magus), fight


# -- schools of magical combat (HoH:S pp. 25-30) --


def test_a_magus_is_suited_to_the_schools_his_virtues_recommend():
    magus = flambeau()
    magus.virtues_flaws = [VirtueFlawInstance("vf_puissant_art", {"art": "Ignem"})]
    names = [s.name for s in magic_combat.schools_for(magus)]
    assert names == ["The Founder", "Boreas"]
    assert magic_combat.schools_text(magus) == (
        "Suited to the Schools of the Founder and Boreas (HoH:S p. 26)."
    )
    vilano = flambeau()
    vilano.virtues_flaws = [
        VirtueFlawInstance("vf_cautious_with_ability", {"ability": "Finesse"})
    ]
    assert [s.name for s in magic_combat.schools_for(vilano)] == ["Vilano"]
    assert magic_combat.schools_for(flambeau()) == []
    assert set(magic_combat.VARIANT_HOUSE_SCHOOLS) <= {
        s.name for s in magic_combat.SCHOOLS
    }


# -- indirect spells (DE p. 223; HoH:S p. 30) --


def test_the_spells_societates_names_are_indirect_and_in_the_catalog():
    saga = Saga(id="x", name="x")
    for name in magic_combat.INDIRECT_SPELLS:
        spell = catalog.find_spell_by_name(saga, name)
        assert spell is not None, name
        assert magic_combat.is_indirect(spell), name
    pilum = catalog.find_spell_by_name(saga, "Pilum of Fire")
    assert not magic_combat.is_indirect(pilum)
    # p. 30 lists 18; the Invisible Sling of Vilano is one of the new spells.
    assert len(magic_combat.SOCIETATES_INDIRECT) == 18
    assert "Invisible Sling of Vilano" not in {
        s.name for s in magic_combat.SOCIETATES_INDIRECT
    }


def test_each_partly_indirect_spell_says_its_limit():
    saga = Saga(id="x", name="x")
    corpse = catalog.find_spell_by_name(saga, "The Walking Corpse")
    assert "non-magical weapon" in magic_combat.indirect_note(corpse)
    chasm = catalog.find_spell_by_name(saga, "The Earth Split Asunder")
    assert "crushed" in magic_combat.indirect_note(chasm)
    pit = catalog.find_spell_by_name(saga, "Pit of the Gaping Earth")
    assert magic_combat.indirect_note(pit) == ""
    harmless = {s.name for s in magic_combat.SOCIETATES_INDIRECT if s.harmless}
    assert harmless == {
        "Weaver's Trap of Webs",
        "Footsteps of Slippery Oil",
        "Trap of the Entwining Vines",
        "Coils of the Entangling Plants",
    }


def test_a_spell_that_only_holds_refuses_damage_and_the_inspector_says_its_limit():
    magus = flambeau(creo=55, animal=55)
    saga, fight = caster_fight(typed("Giant", resistance=50), magus)
    every = rules.units(saga, fight)
    webs = spell_id("Weaver's Trap of Webs")
    hurt = rules.Blow(rules.CAST, "giant", spell=webs, damage=5)
    odds = rules.spell_odds(saga, fight, every["marcus"], every["giant"], hurt)
    assert odds is not None and "does no harm itself" in odds.blocked
    held = rules.Blow(rules.CAST, "giant", spell=webs)
    odds = rules.spell_odds(saga, fight, every["marcus"], every["giant"], held)
    assert odds is not None and not odds.blocked
    assert any("holds him in place" in note for note in odds.notes)


def test_an_indirect_spell_ignores_magic_resistance_but_is_aimed():
    magus = flambeau(perdo=55, terram=55)
    giant = typed("Giant", resistance=50, defence=0, soak=0)
    saga, fight = caster_fight(giant, magus)
    blow = rules.Blow(
        rules.CAST, "giant", spell=spell_id("Pit of the Gaping Earth"), damage=10
    )
    # Initiative 5, 2; casting 6 (20 + 6 >= 15); aim 7 against Defence 2;
    # damage 5 + 10 against Soak 2.
    played = rules.play(saga, fight, blow, Scripted(5, 2, 6, 7, 2, 5, 2))
    assert not any(line.startswith("Penetration") for line in played.lines)
    assert any("must be aimed" in line for line in played.lines)
    assert "strikes Giant" in played.text
    assert giant.wounds.light + giant.wounds.medium + giant.wounds.heavy >= 1


def test_an_indirect_spell_can_miss_its_aim():
    magus = flambeau(perdo=55, terram=55)
    giant = typed("Giant", resistance=50, defence=3)
    saga, fight = caster_fight(giant, magus)
    blow = rules.Blow(rules.CAST, "giant", spell=spell_id("Pit of the Gaping Earth"))
    played = rules.play(saga, fight, blow, Scripted(5, 2, 6, 2, 8))
    assert played.text == "Pit of the Gaping Earth misses Giant."


def test_a_direct_spell_must_still_penetrate():
    magus = flambeau(creo=55, ignem=55)
    giant = typed("Giant", resistance=50)
    saga, fight = caster_fight(giant, magus)
    blow = rules.Blow(rules.CAST, "giant", spell=spell_id("Pilum of Fire"), damage=10)
    played = rules.play(saga, fight, blow, Scripted(5, 2, 6))
    assert played.text == "Giant resists Pilum of Fire."


def test_any_spell_can_be_marked_indirect_with_size_steps_to_aim():
    magus = flambeau(creo=55, ignem=55)
    magus.characteristics = Characteristics(perception=2)
    magus.abilities = [Ability("Finesse", xp=ability_xp(3))]
    giant = typed("Giant", resistance=50)
    saga, fight = caster_fight(giant, magus)
    every = rules.units(saga, fight)
    blow = rules.Blow(
        rules.CAST, "giant", spell=spell_id("Pilum of Fire"), indirect=True, aim_steps=2
    )
    odds = rules.spell_odds(saga, fight, every["marcus"], every["giant"], blow)
    assert odds is not None and odds.indirect and odds.aim is not None
    assert int(odds.aim.total) == 2 + 3 + 12


# -- Spell Mastery and the Penetration multiplier (DE pp. 219-226) --


def test_mastery_adds_to_the_score_penetration_and_takes_botch_dice():
    magus = flambeau(creo=55, ignem=55)
    pilum = spell_id("Pilum of Fire")
    magus.spells_known = [
        KnownSpell(
            pilum, mastery_score=2, mastery_abilities=[MasteryAbility("Penetration")]
        )
    ]
    saga, fight = caster_fight(typed("Giant"), magus)
    every = rules.units(saga, fight)
    blow = rules.Blow(rules.CAST, "giant", spell=pilum)
    odds = rules.spell_odds(saga, fight, every["marcus"], every["giant"], blow)
    unmastered = saga_with(fight, flambeau(creo=55, ignem=55))
    bare = rules.spell_odds(
        unmastered,
        fight,
        rules.units(unmastered, fight)["marcus"],
        every["giant"],
        blow,
    )
    assert odds is not None and bare is not None
    assert odds.score == (bare.score or 0) + 2
    assert odds.penetration == bare.penetration + 2
    assert odds.mastery == 2
    # A 0 on the casting die is no botch with no botch dice left.
    played = rules.play(saga, fight, blow, Scripted(5, 2, 0, 0))
    assert "botches" not in played.text


def test_an_arcane_connection_and_sympathies_multiply_penetration():
    magus = flambeau(creo=55, ignem=55)
    magus.abilities = [Ability("Penetration", xp=ability_xp(2))]
    saga, fight = caster_fight(typed("Giant"), magus)
    every = rules.units(saga, fight)
    blow = rules.Blow(
        rules.CAST,
        "giant",
        spell=spell_id("Pilum of Fire"),
        arcane="Indefinitely",
        named=True,
        symbol=True,
    )
    odds = rules.spell_odds(saga, fight, every["marcus"], every["giant"], blow)
    # 2 x (1 + 4 + 1 + 2), DE pp. 219-220 and HoH:S p. 27.
    assert odds is not None and odds.penetration == 16


def test_mastered_magic_resistance_doubles_against_that_spell():
    pilum = spell_id("Pilum of Fire")
    caster = flambeau(creo=55, ignem=55)
    rival = Character(id="r", name="Rival", type="magus")
    rival.arts["ignem"] = ArtScore(xp=55)
    rival.spells_known = [
        KnownSpell(
            pilum,
            mastery_score=1,
            mastery_abilities=[MasteryAbility("Magic Resistance")],
        )
    ]
    fight = fight_of(
        [Combatant("Marcus", "character", "m", id="marcus")],
        [Combatant("Rival", "character", "r", id="rival")],
    )
    saga = saga_with(fight, caster, rival)
    every = rules.units(saga, fight)
    odds = rules.spell_odds(
        saga,
        fight,
        every["marcus"],
        every["rival"],
        rules.Blow(rules.CAST, spell=pilum),
    )
    assert odds is not None and odds.resistance == 20
    assert any("doubled" in note for note in odds.notes)


# -- fighting invisibly (HoH:S pp. 32-33) --


def test_an_unlocated_invisible_fighter_cant_be_struck_until_found():
    ghost = typed("Ghost", invisible="clear", defence=0)
    fight = fight_of([typed("Guard", attack=5)], [ghost])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    blocked = rules.odds(saga, fight, every["guard"], every["ghost"], rules.ATTACK)
    assert "locate it first" in blocked.blocked
    assert rules.LOCATE in rules.actions_for(saga, fight, every["guard"])
    # Search 0 + 9 against Stealth +3 + 2.
    fight.order, fight.round = ["guard", "ghost"], 1
    played = rules.play(saga, fight, rules.Blow(rules.LOCATE, "ghost"), Scripted(9, 2))
    assert "locates" in played.text
    assert fight.located == {"ghost": ["guard"]}
    chances = rules.odds(saga, fight, every["guard"], every["ghost"], rules.ATTACK)
    assert not chances.blocked
    assert ("Invisible", 3) in [(t.label, t.amount) for t in chances.defence]
    assert rules.LOCATE not in rules.actions_for(saga, fight, every["guard"])


def test_obvious_signs_need_no_search():
    fight = fight_of([typed("Guard", attack=5)], [typed("Ghost", invisible="obvious")])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["guard"], every["ghost"], rules.ATTACK)
    assert not chances.blocked
    assert chances.total("defence") == 3


def test_an_invisible_attacker_strikes_with_surprise_and_goes_first():
    fight = fight_of(
        [typed("Ghost", invisible="faint", attack=0)], [typed("Quick", init=20)]
    )
    saga = saga_with(fight)
    rules.roll_initiative(saga, fight, Scripted(2, 5))
    assert fight.order == ["ghost", "quick"]
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["ghost"], every["quick"], rules.ATTACK)
    labels = {t.label: t.amount for t in chances.attack}
    assert labels["Invisible"] == 6 and labels["Surprise"] == 3
    # The rolled order stands from the second round.
    rules._next_round(fight)
    assert fight.order == ["quick", "ghost"]


def test_once_engaged_the_foe_strikes_back_without_a_search():
    fight = fight_of([typed("Ghost", invisible="faint")], [typed("Guard", attack=5)])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    fight.attacked_by = {"guard": ["ghost"]}
    chances = rules.odds(saga, fight, every["guard"], every["ghost"], rules.ATTACK)
    assert not chances.blocked
    surprise = rules.odds(saga, fight, every["ghost"], every["guard"], rules.ATTACK)
    assert "Surprise" not in [t.label for t in surprise.attack]


def test_magic_resistance_keeps_out_an_invisible_weapon():
    fight = fight_of(
        [typed("Ghost", invisible="clear", attack=9)], [typed("Spirit", resistance=5)]
    )
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["ghost"], every["spirit"], rules.ATTACK)
    assert "Magic Resistance" in chances.blocked


def test_obvious_signs_dont_make_the_blow_non_magical():
    # HoH:S p. 32: only a weapon picked up after turning invisible gets
    # through; Obvious signs change the bonuses, not that.
    ghost = typed("Ghost", invisible="obvious", attack=9)
    fight = fight_of([ghost], [typed("Spirit", resistance=5)])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["ghost"], every["spirit"], rules.ATTACK)
    assert "Magic Resistance" in chances.blocked
    ghost.weapon_after_invisible = True
    chances = rules.odds(saga, fight, every["ghost"], every["spirit"], rules.ATTACK)
    assert not chances.blocked
    # Its touch is still magical.
    scuffle = rules.odds(saga, fight, every["ghost"], every["spirit"], rules.SCUFFLE)
    assert "Magic Resistance" in scuffle.blocked


def test_invisible_members_spoil_a_trained_group_and_add_botch_dice():
    members = [typed("A", ability=3), typed("B", ability=3, invisible="clear")]
    fight = fight_of(members, [typed("Foe")])
    fight.sides[0].groups = [
        FightGroup("Pair", ["a", "b"], trained=True, leader="a", id="pair")
    ]
    members[0].leadership = 3
    saga = saga_with(fight)
    unit = rules.units(saga, fight)["pair"]
    assert unit.bonus() == 0
    assert rules.group_dice(unit) == 2


def test_allies_cant_defend_an_invisible_fighter():
    fight = fight_of(
        [typed("Guard", attack=5)],
        [typed("Ghost", invisible="clear"), typed("Shield", defends="ghost")],
    )
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    assert rules.defenders_of(saga, fight, every["ghost"]) == []
    fight.sides[1].combatants[0].invisible = ""
    assert [f.name for f in rules.defenders_of(saga, fight, every["ghost"])] == [
        "Shield"
    ]


def test_spells_need_the_invisible_found_unless_they_fill_an_area():
    magus = flambeau(creo=55, ignem=55)
    saga, fight = caster_fight(typed("Ghost", invisible="clear"), magus)
    every = rules.units(saga, fight)
    pilum = rules.Blow(rules.CAST, "ghost", spell=spell_id("Pilum of Fire"))
    odds = rules.spell_odds(saga, fight, every["marcus"], every["ghost"], pilum)
    assert odds is not None and "area spell" in odds.blocked
    arc = rules.Blow(rules.CAST, "ghost", spell=spell_id("Arc of Fiery Ribbons"))
    odds = rules.spell_odds(saga, fight, every["marcus"], every["ghost"], arc)
    assert odds is not None and odds.blocked == ""


def test_eye_range_fails_when_either_is_invisible():
    eye = next(s for s in catalog.load_spell_catalog() if s.range == "Eye")
    saga, fight = caster_fight(typed("Ghost", invisible="obvious"), flambeau())
    every = rules.units(saga, fight)
    odds = rules.spell_odds(
        saga,
        fight,
        every["marcus"],
        every["ghost"],
        rules.Blow(rules.CAST, spell=eye.id),
    )
    assert odds is not None and "Eye range" in odds.blocked


def test_locate_and_hide_bases_come_from_the_sheet():
    seeker = Character(
        id="s",
        name="Seeker",
        type="grog",
        characteristics=Characteristics(perception=2),
        abilities=[Ability("Awareness", xp=ability_xp(3))],
    )
    hider = Character(
        id="h",
        name="Hider",
        type="grog",
        characteristics=Characteristics(dexterity=1),
        abilities=[Ability("Stealth", xp=ability_xp(2))],
    )
    assert int(magic_combat.locate_base(seeker).total) == 5
    signs = magic_combat.clarity("none")
    assert signs is not None and signs.unseeable and signs.stealth == 12
    assert int(magic_combat.hide_base(hider, signs).total) == 1 + 2 + 12


# -- the forms and the inspector --


def test_the_combatant_form_writes_invisibility_and_the_inspector_says_so():
    combatant = typed("Ghost")
    fights._write_stance(combatant, {"invisible": "faint"})
    assert combatant.invisible == "faint"
    assert not combatant.weapon_after_invisible
    fights._write_stance(
        combatant, {"invisible": "faint", "weapon_after_invisible": True}
    )
    assert combatant.weapon_after_invisible
    fights._write_stance(
        combatant, {"invisible": "nonsense", "weapon_after_invisible": True}
    )
    assert combatant.invisible == "" and not combatant.weapon_after_invisible
    fight = fight_of([typed("Guard")], [typed("Ghost")])
    text = fights.combatant_live(
        saga_with(fight),
        fight,
        {"kind": "typed", "name": "Ghost", "invisible": "faint"},
    )
    assert "Invisible (Faint)" in text


def test_the_blow_inspector_shows_aiming_and_locating():
    magus = flambeau(perdo=55, terram=55)
    saga, fight = caster_fight(typed("Giant", resistance=50), magus)
    fight.order, fight.round = ["marcus", "giant"], 1
    text = fights.blow_live(
        saga,
        fight,
        {
            "action": rules.CAST,
            "target": "giant",
            "spell": spell_id("Pit of the Gaping Earth"),
        },
    )
    assert "Indirect" in text and "Penetration:" not in text
    ghostly = fight_of([typed("Guard")], [typed("Ghost", invisible="clear")])
    ghostly.order, ghostly.round = ["guard", "ghost"], 1
    text = fights.blow_live(
        saga_with(ghostly), ghostly, {"action": rules.LOCATE, "target": "ghost"}
    )
    assert "Perception + Awareness" in text
    blow = fights.blow_of(
        {"action": rules.CAST, "arcane": "Indefinitely", "named": True}
    )
    assert (blow.arcane, blow.named, blow.symbol) == ("Indefinitely", True, False)


def test_invisibility_and_locating_survive_a_save():
    fight = fight_of([typed("Guard")], [typed("Ghost", invisible="clear")])
    fight.located = {"ghost": ["guard"]}
    again = Fight.from_dict(dataclasses.asdict(fight))
    assert again.located == {"ghost": ["guard"]}
    assert again.sides[1].combatants[0].invisible == "clear"
    rules.restart(again)
    assert again.located == {}
