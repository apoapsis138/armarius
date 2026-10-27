"""House Bjornaer's Mysteries: the heartbeast's temperaments, choice and
statistics, the Ritual of Twelve Years, the House and Clan Mysteries, the
Inner Heartbeast and its Refinements, and Sensory Magic in the lab
(Houses of Hermes: Mystery Cults pp. 18-33, Errata p. 54; DE pp.
233-235)."""

from __future__ import annotations

from ars_magica_manager import artwork, catalog
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    DiaryEntry,
    Familiar,
    Ordeal,
    Saga,
    SeasonPlan,
    SpellDesign,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import bjornaer as bj
from ars_magica_manager.rules import casting_virtues
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.activities import ACTIVITIES
from ars_magica_manager.rules.xp import ability_xp

LORE = bj.CULT_LORE


def _key(name: str) -> str:
    return f"{bj.CULT_TRADITION}/{name}"


def _magus(
    id_: str, name: str, *vf_ids: str, presence: int = 0, lore: int = 0
) -> Character:
    magus = Character(id=id_, name=name, type="magus")
    magus.characteristics = Characteristics(presence=presence, stamina=2)
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in vf_ids]
    if lore:
        magus.abilities.append(Ability(LORE, xp=ability_xp(lore)))
    return magus


def _saga() -> Saga:
    """Hrafn, an apprentice to be; Ardea, a Swan Elder of Clan Ilfetu
    (Presence +3, Lore 8, a heron heartbeast); Ulf, a wolf Bjornaer with
    Lore 5."""
    hrafn = _magus("h", "Hrafn", presence=1)
    ardea = _magus("a", "Ardea", bj.HEARTBEAST, bj.CLAN_ILFETU, presence=3, lore=8)
    ardea.abilities.append(
        Ability(bj.ABILITY, xp=ability_xp(6), specialty="changing into a heron")
    )
    ulf = _magus("u", "Ulf", bj.HEARTBEAST, presence=2, lore=5)
    ulf.abilities.append(
        Ability(bj.ABILITY, xp=ability_xp(4), specialty="changing into a wolf")
    )
    return Saga(id="s", name="S", characters=[hrafn, ardea, ulf])


def _plan(who: str, script: str, **kw: object) -> SeasonPlan:
    plan = SeasonPlan(who, 1220, "Spring", "undergo_initiation", [])
    plan.hedge_script = _key(script)
    for name, value in kw.items():
        setattr(plan, name, value)
    return plan


def _who(saga: Saga, id_: str) -> Character:
    found = saga.character(id_)
    assert found is not None
    return found


# -- temperaments and the heartbeast ----------------------------------------------


def test_temperaments_and_their_oppositions():
    assert bj.temperament_of("the Wolf") == (bj.CHOLERIC, "")
    assert bj.temperament_of("herons") == (bj.SANGUINE, bj.PHLEGMATIC)
    assert bj.temperament_of("Bear") == (bj.MELANCHOLIC, bj.CHOLERIC)
    assert bj.temperament_of("griffin") is None
    assert bj.OPPOSED[bj.SANGUINE] == bj.MELANCHOLIC
    assert bj.OPPOSED[bj.PHLEGMATIC] == bj.CHOLERIC
    ulf = _who(_saga(), "u")
    assert bj.heartbeast_of(ulf) == "wolf"
    assert "wolf, choleric; opposed to phlegmatic" in bj.temperament_line(ulf)


def test_the_heartbeasts_a_magus_may_choose():
    assert bj.choice_problems(-2) == []
    # A Size -8 creature only as a noble specimen, a Size larger.
    assert bj.heartbeast_size(-8, noble=True) == -7
    assert bj.choice_problems(-8, noble=True) == []
    assert (
        "Dwarf Flaw is then obligatory (the magus lacks it)"
        in (bj.choice_problems(-8)[0])
    )
    assert bj.choice_problems(-8, vf_ids=frozenset({bj.DWARF}))[0].endswith(
        "obligatory."
    )
    assert "Giant Blood" in bj.choice_problems(4)[0]
    assert bj.choice_problems(0, noble=True) == [
        "Only a heartbeast of Size -5 or less may be a Size larger."
    ]
    assert len(bj.choice_problems(0, domesticated=True, might=True)) == 2


def test_changing_form_against_magic():
    assert bj.resist_ease(2) == 5
    ulf = _who(_saga(), "u")
    assert bj.change_total(ulf).total == 6  # Stamina 2 + Heartbeast 4


def test_ringing_the_changes_with_the_errata():
    ulf = Characteristics(
        intelligence=2,
        perception=-1,
        presence=2,
        communication=0,
        strength=-1,
        stamina=1,
        dexterity=1,
        quickness=1,
    )
    wolf = {
        "cunning": 1,
        "perception": 2,
        "presence": 0,
        "communication": 1,
        "strength": -1,
        "stamina": 3,
        "dexterity": 2,
        "quickness": 1,
    }
    found = bj.animal_characteristics(ulf, wolf)
    # The Errata (p. 54) corrects Ulf's Perception to +1.
    assert found == {
        "intelligence": 2,
        "perception": 1,
        "presence": 2,
        "communication": 1,
        "strength": -1,
        "stamina": 3,
        "dexterity": 2,
        "quickness": 1,
    }
    werewolf = bj.animal_characteristics(ulf, wolf, lycanthrope=True)
    assert werewolf["cunning"] == 1 and "intelligence" not in werewolf


def test_the_inner_heartbeasts_shapes():
    # An eagle's Perception +2, the magus's -1: the inner heartbeast +5,
    # the human form 0, so the outer heartbeast +2 (p. 30).
    inner, human = bj.epitome_characteristic(2, -1)
    assert (inner, human) == (5, 0)
    assert bj.combine(human, 2) == 2
    assert bj.chimera_size(-2, 2) == 2  # an eagle with a lion's features
    assert bj.chimera_size(2, -2) == 3  # a lion with an eagle's
    assert bj.CHIMERA_VIRTUE[bj.PHLEGMATIC] == "vf_intuition"
    ulf = _who(_saga(), "u")
    assert bj.great_beast_might(ulf) == 0
    ulf.virtues_flaws.append(VirtueFlawInstance(bj.ANIMA))
    assert bj.great_beast_might(ulf) == 20


# -- refinements ----------------------------------------------------------------------


def test_a_refinements_ease_vis_and_script():
    assert bj.refinement_ease("size") == 18
    assert bj.refinement_ease("size", earlier=2) == 24
    assert bj.refinement_ease("quality", earlier=2) == 15
    assert bj.refinement_vis(21) == 7
    assert bj.refinement_vis(16) == 6
    ulf = _who(_saga(), "u")
    ulf.virtues_flaws.append(VirtueFlawInstance(bj.ANIMA))
    assert bj.embryonic_script(ulf, "minor_power").total == 10
    assert bj.embryonic_script(ulf, "size", sympathy=9).total == 12  # capped +5
    assert bj.power_problems("minor_power", 20, 20) == [
        "The Lab Total 20 must exceed the Power's level 20: its formulation is "
        "beyond him."
    ]
    assert bj.power_problems("major_power", 20, 25, constant=True) == [
        "A Major Power can't have a constant effect."
    ]


# -- the Ritual of Twelve Years -----------------------------------------------------------


def test_the_ritual_of_twelve_years_gives_the_heartbeast():
    saga = _saga()
    hrafn = _who(saga, "h")
    plan = _plan("h", bj.TWELVE_YEARS, teacher_id="a", effect_id=bj.HEARTBEAST)
    assert sw.problems(saga, hrafn, plan) == []
    assert sw.initiation_target(saga, hrafn, plan) == 15
    done = sw.work(saga, hrafn, plan, None)
    # Presence 3 + Lore 8 + Script 6 = 17.
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == [bj.HEARTBEAST]
    assert done.ability_xp == [(bj.ABILITY, 5)]
    assert done.ordeal == "Minor"
    assert any("Participation Modifier" in note for note in done.notes)


def test_the_witnesses_temperaments():
    witnesses = [bj.SANGUINE, bj.SANGUINE, bj.MELANCHOLIC, bj.CHOLERIC]
    assert bj.participation(bj.SANGUINE, witnesses) == 1
    assert bj.participation(bj.MELANCHOLIC, witnesses) == -1
    ardea = _who(_saga(), "a")
    assert bj.twelve_years_total(ardea, -2).total == 15


def test_what_stops_the_ritual_of_twelve_years():
    saga = _saga()
    hrafn = _who(saga, "h")
    plan = _plan("h", bj.TWELVE_YEARS, teacher_id="a", effect_id=bj.HEARTBEAST)
    saga.familiars.append(Familiar(id="f", name="Corvus", character_id="h"))
    assert "has bound a familiar" in sw.problems(saga, hrafn, plan)[0]
    saga.familiars.clear()
    hrafn.virtues_flaws.append(VirtueFlawInstance("vf_verditius_magic"))
    assert "another House's Mystery" in sw.problems(saga, hrafn, plan)[0]
    hrafn.virtues_flaws.clear()
    ardea = _who(saga, "a")
    ardea.virtues_flaws = [VirtueFlawInstance(bj.HEARTBEAST)]
    assert "isn't of Clan Ilfetu" in sw.problems(saga, hrafn, plan)[0]
    ulf = _who(saga, "u")
    again = _plan("u", bj.TWELVE_YEARS, effect_id=bj.HEARTBEAST)
    assert "never repeated" in sw.problems(saga, ulf, again)[0]


def test_a_familiar_ever_bound_stops_the_ritual():
    # "Any magus who has ever bound a familiar, even if it has since died,
    # cannot successfully complete the Ritual of Twelve Years" (HoH:MC p. 24).
    saga = _saga()
    hrafn = _who(saga, "h")
    plan = _plan("h", bj.TWELVE_YEARS, teacher_id="a", effect_id=bj.HEARTBEAST)
    hrafn.diary.append(
        DiaryEntry(1215, "Autumn", "Binding Corvus", activity=bj.FAMILIAR_DIARY[0])
    )
    assert "Autumn 1215, in his Diary" in sw.problems(saga, hrafn, plan)[0]
    hrafn.diary.clear()
    assert sw.problems(saga, hrafn, plan) == []
    plan.familiar_ever_bound = True
    assert "has bound a familiar before" in sw.problems(saga, hrafn, plan)[0]


def test_the_familiar_diary_labels_are_the_seasons():
    assert bj.FAMILIAR_DIARY == (
        ACTIVITIES["bind_familiar"].label,
        ACTIVITIES["empower_bond"].label,
    )


def test_the_books_name_for_the_lore_scores_in_the_initiation():
    # The books call it House Bjornaer Lore (HoH:MC pp. 28, 30; Errata p. 54).
    saga = _saga()
    hrafn, ardea = _who(saga, "h"), _who(saga, "a")
    ardea.abilities = [
        Ability("House Bjornaer Lore", xp=ability_xp(8)) if a.name == LORE else a
        for a in ardea.abilities
    ]
    plan = _plan("h", bj.TWELVE_YEARS, teacher_id="a", effect_id=bj.HEARTBEAST)
    assert sw.problems(saga, hrafn, plan) == []
    done = sw.work(saga, hrafn, plan, None)
    assert done.initiated
    assert any("Initiation Total 17" in note for note in done.notes)


def test_house_and_clan_mysteries_need_their_mystagogue():
    saga = _saga()
    ulf = _who(saga, "u")
    alone = _plan("u", bj.THERIOMORPHY_SCRIPT, effect_id=bj.THERIOMORPHY)
    assert "needs a Mystagogue" in sw.problems(saga, ulf, alone)[0]
    by_ardea = _plan(
        "u", bj.THERIOMORPHY_SCRIPT, teacher_id="a", effect_id=bj.THERIOMORPHY
    )
    assert sw.problems(saga, ulf, by_ardea) == []
    hrafn = _who(saga, "h")
    plan = _plan("h", bj.SENSORY_SCRIPT, teacher_id="a", effect_id=bj.SENSORY_MAGIC)
    assert "hasn't the Heartbeast" in sw.problems(saga, hrafn, plan)[0]
    # A Clan Mystery's Mystagogue needs Presence + Lore 8; Ulf has 7, and 4
    # once a Minor Ordeal lowers it by 3.
    oath = _plan("a", bj.OATH, teacher_id="u")
    ardea = _who(saga, "a")
    assert "below 8" in sw.problems(saga, ardea, oath)[0]
    ardea.ordeals = [Ordeal("Minor")]
    assert sw.problems(saga, ardea, oath) == []


# -- the Inner Heartbeast -------------------------------------------------------------------


def test_the_great_beast_initiates_the_inner_heartbeast():
    saga = _saga()
    ulf = _who(saga, "u")
    plan = _plan(
        "u",
        bj.INNER_SCRIPT,
        effect_id=bj.ANIMA,
        ordeal_kind="gain",
        device_id="vf_restriction",
    )
    assert sw.problems(saga, ulf, plan) == []
    assert sw.initiation_target(saga, ulf, plan) == 21
    done = sw.work(saga, ulf, plan, None)
    # The Great Beast: Presence 2 + Lore 8 + Script 13 = 23.
    assert done.initiated
    assert done.ordeal == "Major"
    assert [vf.vf_id for vf in done.add_vfs] == [bj.ANIMA, "vf_restriction"]
    assert any("Great Beast is the Mystagogue" in n for n in done.notes)
    assert "Initiation Total 23" in done.notes[-1]


def test_what_stops_the_inner_heartbeast():
    saga = _saga()
    ulf = _who(saga, "u")
    minor = _plan(
        "u",
        bj.INNER_SCRIPT,
        effect_id=bj.EPITOME,
        ordeal_kind="gain",
        device_id="vf_feral_scent",
    )
    assert "Major Hermetic or Supernatural" in sw.problems(saga, ulf, minor)[0]
    ulf.virtues_flaws.append(VirtueFlawInstance("vf_skinchanger"))
    assert "can change shape" in sw.problems(saga, ulf, minor)[0]
    shed = _plan(
        "u",
        bj.INNER_SCRIPT,
        effect_id=bj.EPITOME,
        ordeal_kind="lose",
        ordeal_lost_id="vf_skinchanger",
    )
    assert sw.problems(saga, ulf, shed) == []
    ulf.virtues_flaws = [VirtueFlawInstance(bj.HEARTBEAST)]
    ulf.abilities = [a for a in ulf.abilities if a.name != LORE]
    ulf.abilities.append(Ability(LORE, xp=ability_xp(4)))
    assert f"needs {LORE} 5" in sw.problems(saga, ulf, minor)[0]
    ulf.virtues_flaws.append(VirtueFlawInstance(bj.CHIMERA))
    assert "inner heartbeast already" in sw.problems(saga, ulf, minor)[0]


def test_ulf_refines_his_shadow_wolf():
    """The book's example (p. 33): a Minor Power just after the Major
    Ordeal: 21 less 9 is 12, and Presence 2 + Lore 5 + 10 reaches it."""
    saga = _saga()
    ulf = _who(saga, "u")
    ulf.virtues_flaws.append(VirtueFlawInstance(bj.ANIMA))
    ulf.ordeals = [Ordeal("Major")]
    plan = _plan("u", bj.REFINEMENT_PREFIX + "Acquiring a Minor Power")
    assert sw.problems(saga, ulf, plan) == []
    assert sw.initiation_target(saga, ulf, plan) == 12
    done = sw.work(saga, ulf, plan, None)
    assert done.initiated
    assert "Initiation Total 17" in done.notes[-1]
    assert any("eat 7 pawns of the Power's Form vis" in n for n in done.notes)
    led = _plan("u", bj.REFINEMENT_PREFIX + "Acquiring a Quality", teacher_id="a")
    assert "Initiates himself" in sw.problems(saga, ulf, led)[0]
    hrafn = _who(saga, "h")
    hrafn.virtues_flaws = [VirtueFlawInstance(bj.HEARTBEAST)]
    hrafn.abilities = [Ability(LORE, xp=ability_xp(1))]
    bare = _plan("h", bj.REFINEMENT_PREFIX + "Acquiring a Quality")
    assert "no inner heartbeast" in sw.problems(saga, hrafn, bare)[0]


# -- Sensory Magic, reminders and the catalog ---------------------------------------------


def test_sensory_magic_adds_heartbeast_inventing_its_spells():
    ulf = _who(_saga(), "u")
    scent = SpellDesign(key="k", technique="Creo", form="Mentem", target="Scent")
    assert bj.sensory_line(ulf, scent) is None
    ulf.virtues_flaws.append(VirtueFlawInstance(bj.SENSORY_MAGIC))
    line = bj.sensory_line(ulf, scent)
    assert line is not None and line.amount == 4
    sense = SpellDesign(key="s", technique="Intellego", form="Vim", target="Vision")
    assert bj.sensory_line(ulf, sense) is not None
    plain = SpellDesign(key="p", technique="Creo", form="Ignem", target="Individual")
    assert bj.sensory_line(ulf, plain) is None


def test_the_form_changing_reminders():
    ulf = _who(_saga(), "u")
    ulf.virtues_flaws += [
        VirtueFlawInstance(bj.THERIOMORPHY),
        VirtueFlawInstance(bj.EPITOME),
    ]
    found = bj.reminders(ulf)
    assert found[0].startswith("Heartbeast: Stamina + Heartbeast (6) against 3")
    assert any(r.startswith("Theriomorphy:") for r in found)
    assert any("Great Beast of Magic Might 20" in r for r in found)
    assert set(found) <= set(casting_virtues.reminders(ulf))
    assert bj.reminders(_who(_saga(), "h")) == []


def test_the_catalog_holds_the_houses_scripts():
    tradition = catalog.load_tradition_catalog_by_id()[bj.CULT_TRADITION]
    assert tradition.initiation is not None
    names = {s.name for s in tradition.initiation.scripts}
    expected = {
        *bj.HOUSE_SCRIPTS,
        *bj.CLAN_SCRIPTS,
        bj.INNER_SCRIPT,
        *(bj.REFINEMENT_PREFIX + r.name for r in bj.REFINEMENTS.values()),
    }
    assert names == expected
    for script in tradition.initiation.scripts:
        if script.components:
            assert sum(b for _, b in script.components) == script.bonus, script.name
        key = bj.refinement_key(_key(script.name))
        if key:
            assert script.ease_factor == bj.REFINEMENTS[key].ease
    assert ts.belongs(_who(_saga(), "u"), bj.CULT_TRADITION)
    assert artwork.tradition_symbol(bj.CULT_TRADITION) is not None
