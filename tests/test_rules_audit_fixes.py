"""Rules checked against the Definitive Edition in the closing audit:
casting rolls, Divine susceptibility, creation checks, familiars,
enchanting, vis extraction, apprentices, spell design, study and aging."""

import random

from ars_magica_manager import catalog, seasons
from ars_magica_manager import familiars as fam
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    CreationXp,
    EnchantedDevice,
    Familiar,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    Wounds,
)
from ars_magica_manager.rules import (
    aging,
    casting,
    casting_virtues,
    creation_finish,
    creation_magus,
    enchantment,
    lab,
    lab_seasons,
    spell_levels,
    supplement_seasons,
)
from ars_magica_manager.rules import apprentice_seasons as aps
from ars_magica_manager.rules import creation as creation_rules
from ars_magica_manager.rules import creation_access as access
from ars_magica_manager.rules import creation_characteristics as cch
from ars_magica_manager.rules import familiar_seasons as fs
from ars_magica_manager.rules import hybrid_magic as hybrid
from ars_magica_manager.rules.xp import ability_xp, art_xp


class Scripted(random.Random):
    """A d10 that throws the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _vf(*ids: str) -> list[VirtueFlawInstance]:
    return [VirtueFlawInstance(i) for i in ids]


def _magus(*vf_ids: str) -> Character:
    return Character(
        id="m",
        name="Magus",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(stamina=2, quickness=1, perception=1),
        arts={"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(8))},
        abilities=[
            Ability("Finesse", xp=ability_xp(2)),
            Ability("Concentration", xp=ability_xp(3)),
        ],
        virtues_flaws=_vf(*vf_ids),
    )


# -- casting --


def test_fast_caster_wounds_and_fatigue_change_the_casting_rolls():
    magus = _magus()
    assert casting.fast_casting_speed(magus) == 1 + 2
    assert casting.concentration_base(magus) == 2 + 3
    assert casting.aiming_base(magus) == 1 + 2
    magus.virtues_flaws = _vf("vf_fast_caster")
    assert casting.fast_casting_speed(magus) == 1 + 2 + 3  # DE p. 80
    # A Medium Wound (-3) and Tired (-3): Concentration takes the Wound
    # Penalty three times (DE p. 215).
    magus.wounds = Wounds(medium=1)
    magus.fatigue_level = "tired"
    assert casting.fast_casting_speed(magus) == 6 - 3 - 3
    assert casting.concentration_base(magus) == 5 - 9 - 3
    assert casting.aiming_base(magus) == 3 - 3 - 3


def test_twilight_prone_risks_twilight_on_one_botch_zero():
    assert casting.botch_warping(1) == (1, False)
    assert casting.botch_warping(1, prone=True) == (1, True)
    assert casting.twilight_prone(_magus("vf_twilight_prone"))
    assert not casting.twilight_prone(_magus())


def test_afflicted_tongue_takes_two_from_a_spoken_spell():
    plain = casting.casting_score(_magus(), "Creo", "Ignem").total
    afflicted = _magus("vf_afflicted_tongue")
    assert casting.casting_score(afflicted, "Creo", "Ignem").total == plain - 2
    # Cast without words, the impediment doesn't matter (DE p. 119).
    silent = casting.casting_score(_magus(), "Creo", "Ignem", words="None").total
    assert (
        casting.casting_score(afflicted, "Creo", "Ignem", words="None").total == silent
    )


def test_susceptibility_to_divine_power_doubles_a_divine_aura():
    magus = _magus()
    normal, _ = hybrid.aura_modifier(magus, "Divine", 3)
    dice = hybrid.foreign_botch_dice(magus, "Divine", 3)
    magus.virtues_flaws = _vf("vf_susceptibility_to_divine_power")
    assert hybrid.aura_modifier(magus, "Divine", 3) == (
        2 * normal,
        "Susceptibility to Divine Power",
    )
    assert hybrid.foreign_botch_dice(magus, "Divine", 3) == 2 * dice
    # A Magic aura is unchanged (DE p. 146).
    assert hybrid.aura_modifier(magus, "Magic", 3)[0] == 3


def test_heartbeast_and_verditius_casting_reminders():
    found = casting_virtues.reminders(_magus("vf_heartbeast", "vf_verditius_magic"))
    assert any(line.startswith("Heartbeast:") for line in found)
    assert any(line.startswith("Verditius Magic:") for line in found)


# -- creation --


def test_weak_characteristics_takes_three_points():
    character = Character(id="c", name="C", type="companion")
    assert cch.budget(character) == 7
    character.virtues_flaws = _vf("vf_weak_characteristics")
    assert cch.budget(character) == 4
    character.virtues_flaws = _vf("vf_weak_characteristics", "vf_weak_characteristics")
    assert cch.budget(character) == 1  # DE p. 152


def test_virtues_open_their_lores_and_penetration():
    character = Character(id="c", name="C", type="companion")
    assert not access.may_learn(character, "Faerie Lore")
    assert not access.may_learn(character, "Penetration")
    character.virtues_flaws = _vf("vf_faerie_upbringing")
    assert access.may_learn(character, "Faerie Lore")
    character.virtues_flaws = _vf("vf_outsider")
    assert access.may_learn(character, "Magic Lore")
    assert access.may_learn(character, "Faerie Lore")
    # A Supernatural Ability that may need to penetrate opens Penetration
    # (DE p. 158).
    character.virtues_flaws = _vf("vf_second_sight")
    assert access.may_learn(character, "Penetration")
    assert "Penetration" in access.learnable_abilities(character)


def test_magic_theory_3_is_advised_at_gauntlet():
    assert ("Magic Theory", 3) in creation_magus.ADVISED


def _finish(character: Character) -> dict[str, str]:
    saga = Saga(id="s", name="S", characters=[character])
    return {c.label: c.status for c in creation_finish.finish_checks(saga, character)}


def test_loyal_brave_and_church_upbringing_are_advice():
    grog = Character(id="g", name="G", type="grog")
    assert _finish(grog)["A grog has Loyal"] == "advice"
    companion = Character(
        id="c", name="C", type="companion", virtues_flaws=_vf("vf_church_upbringing")
    )
    label = "Church Upbringing: 25 xp on its Abilities"
    assert _finish(companion)[label] == "advice"
    companion.creation_xp = [
        CreationXp("virtue", "Dead Language: Latin", 15),
        CreationXp("virtue", "Theology", 10),
    ]
    assert _finish(companion)[label] == "pass"


def test_more_than_seven_aura_boons_is_warned():
    saga = Saga(
        id="s",
        name="S",
        current_year=1220,
        covenants=[
            Covenant(
                id="cov", saga_id="s", name="Keep", in_creation=True, year_founded=1215
            )
        ],
    )
    covenant = saga.covenants[0]
    label = "Aura Boons: up to seven, for an aura of at most 10"

    def status() -> str:
        found = creation_rules.checks(saga, covenant, "boons_hooks")
        return next(c.status for c in found if c.label == label)

    covenant.boons_hooks = _vf(*["covbh_boon_minor_aura"] * 2)
    assert status() == "pass"
    covenant.boons_hooks = _vf(*["covbh_boon_minor_aura"] * 8)
    assert status() == "warn"  # DE p. 183


def test_winter_ruins_take_the_dangerous_monster_hook():
    ruins = next(
        s
        for s in catalog.load_covenant_situation_catalog()
        if s.id == "situation_de_winter_ruins"
    )
    ids = {e["vf_id"] for e in ruins.entries}
    assert "covbh_hook_major_monster" in ids  # DE p. 185
    known = {e.id for e in catalog.load_covenant_boon_hook_catalog()}
    assert ids <= known


# -- familiars --


def _familiar_saga(*vf_ids: str) -> Saga:
    magus = _magus(*vf_ids)
    magus.detail = "Full"
    lab_ = Laboratory(id="lab", covenant_id="c", name="Tower", owner_id="m")
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="c", saga_id="s", name="Keep")],
        characters=[magus],
        laboratories=[lab_],
    )


def test_a_bjornaer_binds_no_familiar():
    saga = _familiar_saga()
    assert fam.unbonded_magi(saga) == saga.characters
    assert fam.unbonded_magi(_familiar_saga("vf_heartbeast")) == []


def test_binding_and_strengthening_rules():
    saga = _familiar_saga("vf_heartbeast")
    saga.familiars = [Familiar(id="f", character_id="m", name="Raven")]
    plan = SeasonPlan(
        "m", 1220, "Spring", fs.BIND, lab_id="lab", technique="Creo", form="Animal"
    )
    found, _ = lab_seasons.work(saga, saga.characters[0], plan)
    assert found == ["Bjornaer magi cannot bind familiars (DE p. 234)."]
    saga = _familiar_saga()
    saga.familiars = [
        Familiar(
            id="f",
            character_id="m",
            name="Raven",
            year_bound=1215,
            binding_technique="Creo",
            binding_form="Animal",
        )
    ]
    plan.form = "Corpus"
    found, _ = lab_seasons.work(saga, saga.characters[0], plan)
    assert found and "Creo Animal (DE p. 267)" in found[0]


# -- enchanting --


def test_penetration_levels_round_up():
    device = EnchantedDevice(id="d", name="Wand")
    effect = InstilledEffect(id="e", name="Bolt", level=10, penetration=5)
    assert enchantment.computed_modified_level(device, effect) == 10 + 3


def test_capacity_counts_only_effects_begun():
    begun = InstilledEffect(id="a", name="A", level=10, instilling_progress=4)
    planned = InstilledEffect(id="b", name="B", level=20, instilling_progress=0)
    done = InstilledEffect(id="c", name="C", level=30)
    device = EnchantedDevice(id="d", name="Staff", effects=[begun, planned, done])
    assert enchantment.pawns_used(device) == 1 + 3
    assert enchantment.pawns_used(device, planned) == 1 + 2 + 3  # DE p. 258


# -- the laboratory --


def test_vis_extraction_has_no_floor_of_one():
    assert lab.vis_extracted(25) == 3
    assert lab.vis_extracted(0) == 0  # DE p. 250


def test_an_opened_apprentice_gets_a_full_longevity_ritual():
    apprentice = Character(id="a", name="A", type="companion")
    assert lab_seasons.is_mundane(apprentice)
    apprentice.arts = {"creo": ArtScore(xp=1)}
    assert not lab_seasons.is_mundane(apprentice)  # DE p. 262


def test_a_botched_apprentice_search_dupes_the_magus():
    magus = Character(id="m", name="Tiberius", type="magus")
    saga = Saga(id="s", name="S", characters=[magus])
    seasons.set_plan(saga, SeasonPlan("m", 1220, "Spring", aps.SEARCH))
    seasons.apply(saga, seasons.resolve(saga, Scripted(0, 0, 5)))
    assert "is duped" in magus.diary[-1].details  # DE p. 269


# -- spells --


def test_a_momentary_creo_spell_is_reminded_of_the_ritual():
    design = spell_levels.spell_level(5, "Touch", "Momentary", "Individual")
    assert design is not None and spell_levels.MOMENTARY_CREO not in design.notes
    # A flame gone at once, as Pilum of Fire, needs no Ritual (DE p. 344).
    bolt = spell_levels.spell_level(
        5, "Touch", "Momentary", "Individual", technique="Creo"
    )
    assert bolt is not None and spell_levels.MOMENTARY_CREO not in bolt.notes
    creo = spell_levels.spell_level(
        5, "Touch", "Momentary", "Individual", technique="Creo", lasting=True
    )
    assert creo is not None and spell_levels.MOMENTARY_CREO in creo.notes
    assert not creo.ritual_required
    ritual = spell_levels.spell_level(
        5,
        "Touch",
        "Momentary",
        "Individual",
        technique="Creo",
        ritual=True,
        lasting=True,
    )
    assert ritual is not None and spell_levels.MOMENTARY_CREO not in ritual.notes


def test_the_spell_catalog_names_as_printed():
    names = {s.id: s.name for s in catalog.load_spell_catalog()}
    assert names["spell_circle_of_encompassing_flame"] == (
        "Circle of Encompassing Flames"
    )
    assert names["spell_discern_images_of_truth_and_falsehood"] == (
        "Discern the Images of Truth and Falsehood"
    )


# -- study and aging --


def test_any_planned_character_may_worship():
    worship = supplement_seasons.BY_KEY["worship"]
    assert "magus" in worship.who and "companion" in worship.who  # DE p. 378


def test_a_crisis_says_what_a_physician_adds():
    character = Character(id="c", name="C", type="companion")
    text, _ = aging.crisis(character, 60, 1, Scripted(9))
    assert "Int + Medicine against 6" in text  # DE p. 392
