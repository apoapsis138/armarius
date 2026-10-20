"""A hedge tradition's seasons: Opening a student's Gift, initiation
totals, advancement and the tradition's own work."""

from ars_magica_manager import catalog, seasons, tradition_text
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import activities
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.xp import xp_for_score


def _member(cid: str, tradition_id: str, gifted: bool = True) -> Character:
    character = Character(id=cid, name=cid.title(), type="companion")
    character.traditions = [tradition_id]
    character.virtues_flaws = [VirtueFlawInstance("vf_the_gift")] if gifted else []
    ct.open_tradition(character)
    return character


def _set(character: Character, name: str, score: int) -> None:
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        ability = ct.opened_ability(name)
        character.abilities.append(ability)
    ability.xp = xp_for_score(score, ability.factor)


def _student(*abilities: tuple[str, int, str]) -> Character:
    """A Gifted child with Supernatural Abilities (name, score, Virtue)."""
    child = Character(id="s", name="Sarah", type="companion")
    child.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    for name, score, vf_id in abilities:
        child.abilities.append(
            Ability(name, category="Supernatural", xp=xp_for_score(score, 5))
        )
        child.virtues_flaws.append(VirtueFlawInstance(vf_id))
    return child


def _plan(activity: str, **kw) -> SeasonPlan:
    return SeasonPlan("m", 1220, "Spring", activity, **kw)


def _learned_master() -> Character:
    """Stefano, the book's example: Int 4, Artes Liberales 5, Succurro 2,
    Magicam 6."""
    master = _member("m", "trad_learned_magicians")
    master.characteristics = Characteristics(intelligence=4)
    _set(master, "Artes Liberales", 5)
    _set(master, "Succurro", 2)
    _set(master, "Magicam", 6)
    return master


def test_the_books_opening_example():
    tradition = catalog.load_tradition_catalog_by_id()["trad_learned_magicians"]
    master = _learned_master()
    assert ts.opening_total(master, tradition).total == 17
    # Entrancement (a Major Virtue) counts 6, Magic Sensitivity 3.
    both = _student(
        ("Entrancement", 2, "vf_entrancement"),
        ("Magic Sensitivity", 3, "vf_magic_sensitivity"),
    )
    assert ts.opening_ease(both, tradition) == 18
    assert ts.opening_result(17, 18) == ts.FAILS
    entranced = _student(("Entrancement", 2, "vf_entrancement"))
    assert ts.opening_result(17, ts.opening_ease(entranced, tradition)) == ts.LOSES
    sensitive = _student(("Magic Sensitivity", 3, "vf_magic_sensitivity"))
    assert ts.opening_result(17, ts.opening_ease(sensitive, tradition)) == ts.KEEPS
    assert ts.opening_result(0, ts.opening_ease(_student(), tradition)) == ts.AUTOMATIC


def test_a_student_opened_before_adds_12():
    tradition = catalog.load_tradition_catalog_by_id()["trad_learned_magicians"]
    student = _member("s", "trad_vitkir")
    # His 24 runes at 0 count nothing, but he was Opened to the runes.
    assert ts.opening_ease(student, tradition) == 12


def test_opening_a_student_to_the_runes():
    master = _member("m", "trad_vitkir")
    master.characteristics = Characteristics(intelligence=2)
    _set(master, "Rune Magic", 3)
    for rune in catalog.load_tradition_catalog_by_id()["trad_vitkir"].favored:
        _set(master, rune, 4)
    _set(master, "Gebo", 1)
    child = _student()
    saga = Saga(id="x", name="X", characters=[master, child])
    seasons.set_plan(saga, _plan(ts.OPEN, subject_id="s"))
    worked = seasons.resolve(saga)
    assert worked[0].problems == []
    assert "Opened to Vitkir" in worked[0].notes[0]
    seasons.apply(saga, worked)
    assert child.traditions == ["trad_vitkir"]
    gebo = next(a for a in child.abilities if a.name == "Gebo")
    assert (gebo.xp, gebo.category, gebo.xp_table) == (0, "Hedge Art", "art")
    flaws = [
        vf for vf in child.virtues_flaws if vf.vf_id == "vf_minor_magical_deficiency"
    ]
    assert [vf.params for vf in flaws] == [{"runes": "Gebo"}]
    teaching = next(a for a in master.abilities if a.name == "Teaching")
    assert teaching.xp == 2


def test_who_can_open():
    master = _member("m", "trad_vitkir", gifted=False)
    child = _student()
    saga = Saga(id="x", name="X", characters=[master, child])
    found, _ = ts.open_work(saga, master, _plan(ts.OPEN, subject_id="s"))
    assert "must have The Gift" in found[0]
    gifted = _member("m", "trad_vitkir")
    saga.characters[0] = gifted
    child.virtues_flaws = []
    found, _ = ts.open_work(saga, gifted, _plan(ts.OPEN, subject_id="s"))
    assert found == ["Sarah doesn't have The Gift."]


def test_a_traditions_own_work_gives_exposure_and_its_lab_total():
    vitki = _member("m", "trad_vitkir")
    vitki.characteristics = Characteristics(intelligence=3)
    _set(vitki, "Rune Magic", 2)
    _set(vitki, "Fehu", 5)
    saga = Saga(id="x", name="X", characters=[vitki])
    keys = [a.key for a in activities.activities_for(vitki)]
    assert "vitki_invent_script" in keys and "folk_witch_brew" not in keys
    assert ts.OPEN in keys
    plan = _plan("vitki_invent_script", allocations=[XpAllocation("ability:Fehu", 0)])
    outcome = activities.outcome(vitki, plan, saga)
    assert outcome.problems == []
    assert outcome.gains[0].result.xp == 2
    assert outcome.notes == ["Vitkar Lab Total (Fehu): 10."]
    plain = Character(id="p", name="P", type="companion")
    assert "vitki_invent_script" not in [
        a.key for a in activities.activities_for(plain)
    ]
    assert ts.OPEN not in [a.key for a in activities.activities_for(plain)]


def test_hedge_arts_that_cant_be_practised():
    gruagach = _member("m", "trad_gruagachan")
    plan = _plan(
        activities.PRACTICE, allocations=[XpAllocation("ability:Gruagach Give", 0)]
    )
    assert "The Gruagachan' Arts can't be practised." in activities.problems(
        gruagach, plan
    )
    _set(gruagach, "Pictish", 1)
    plan.allocations = [XpAllocation("ability:Pictish", 0)]
    assert activities.problems(gruagach, plan) == []
    witch = _member("w", "trad_folk_witches")
    _set(witch, "Healing", 1)
    plan.allocations = [XpAllocation("ability:Healing", 0)]
    assert activities.problems(witch, plan) == []


def test_initiation_totals_and_the_chapter_text():
    by_id = catalog.load_tradition_catalog_by_id()
    elementalist = _member("e", "trad_elementalists")
    elementalist.characteristics = Characteristics(presence=2)
    _set(elementalist, "Organization Lore: Ikhwan as-Safa'", 4)
    assert ts.initiation_total(elementalist, by_id["trad_elementalists"], 12) == 18
    witch = _member("w", "trad_folk_witches")
    text = tradition_text.seasons_text(
        Saga(id="x", name="X"), witch, by_id["trad_folk_witches"]
    )
    assert "Opening Total" in text
    assert "Second Life (ungifted)" in text
    assert "Brew a potion or make a fetish" in text
    assert "Works 2 seasons a year, 15 xp a year." in text


def test_an_effects_casting_score_and_the_die_it_needs():
    from ars_magica_manager.models import TraditionEffect
    from ars_magica_manager.rules import hedge_effects as he

    by_id = catalog.load_tradition_catalog_by_id()
    gruagach = _member("g", "trad_gruagachan")
    gruagach.characteristics = Characteristics(stamina=2)
    _set(gruagach, "Gruagach Give", 6)
    _set(gruagach, "Gruagach Curse", 4)
    spell = TraditionEffect(
        "Withering Word",
        tradition="trad_gruagachan",
        rule="Formulaic spell",
        uses=["Gruagach Give", "Gruagach Curse"],
        level=20,
    )
    found = he.effect_total(gruagach, by_id["trad_gruagachan"], spell)
    # 6 + 4 + 2 = 12: a die of 8 reaches 20; up to 10 short, for Fatigue.
    assert found == he.EffectTotal(12, False, 8, -2)
    assert he.total_words(found, spell) == (
        "Casting Score 12, needs a die of 8 (1 for a Fatigue level)"
    )
    charm = TraditionEffect(
        "Amulet", tradition="trad_gruagachan", kind="amulet", charges=3
    )
    assert he.total_words(None, charm) == "choose its casting rule and Arts; 3 left"
    learned = _member("l", "trad_learned_magicians")
    known = TraditionEffect(
        "Luck",
        tradition="trad_learned_magicians",
        kind="charm",
        rule="Known charm",
        uses=["Succurro", "Fortunam"],
        level=5,
    )
    # A known charm halves the total: 5 x 2 - 0.
    found = he.effect_total(learned, by_id["trad_learned_magicians"], known)
    assert found is not None and found.die == 10


def test_elemental_warping_traits():
    from ars_magica_manager.rules import hedge_warping as hw

    by_id = catalog.load_tradition_catalog_by_id()
    elementalist = _member("e", "trad_elementalists")
    elementalist.abilities = [
        a for a in elementalist.abilities if a.name != "Elementalist Earth"
    ]
    _set(elementalist, "Elementalist Air", 4)
    _set(elementalist, "Elementalist Fire", 6)
    _set(elementalist, "Elementalist Water", 2)
    elementalist.aging.warping_score = 1
    # The book's example: Choleric +3, Phlegmatic +2, Sanguine +2.
    traits = {t.trait: t.value for t in hw.elemental_traits(elementalist)}
    assert traits == {"Choleric": 3, "Phlegmatic": 2, "Sanguine": 2}
    text = tradition_text.warping_text(elementalist, by_id["trad_elementalists"])
    assert "Elemental Warping[/] in place of Twilight" in text
    assert "Choleric +3 (Elementalist Fire 6): acts as a Minor Personality Flaw" in text
    vitki = _member("v", "trad_vitkir")
    assert "Nátt-thel" in tradition_text.warping_text(vitki, by_id["trad_vitkir"])
    night = _member("n", "trad_nightwalkers")
    assert "no response of its own" in tradition_text.warping_text(
        night, by_id["trad_nightwalkers"]
    )


def test_a_familiar_adds_to_its_witchs_lab_totals():
    from ars_magica_manager.models import BoundBeing
    from ars_magica_manager.rules import hedge_casting as hc

    by_id = catalog.load_tradition_catalog_by_id()
    tradition = by_id["trad_folk_witches"]
    witch = _member("w", "trad_folk_witches")
    lab = next(r for r in tradition.casting if r.lab)
    casting = next(r for r in tradition.casting if not r.lab)
    uses = [tradition.abilities[0]]
    before_lab = hc.casting_score(witch, tradition, lab, uses).total
    before = hc.casting_score(witch, tradition, casting, uses).total
    witch.bound_beings = [
        BoundBeing(
            "Grimalkin", "trad_folk_witches", "Familiar", bonus=2, applies_to="lab"
        ),
        BoundBeing("Other", "trad_gruagachan", bonus=5, applies_to="lab"),
    ]
    found = hc.casting_score(witch, tradition, lab, uses)
    assert found.total == before_lab + 2
    assert "Grimalkin (bound)" in [line.label for line in found.lines]
    assert hc.casting_score(witch, tradition, casting, uses).total == before
    rows = tradition_text.bond_rows(witch, tradition)
    assert rows == [(0, "Grimalkin (Familiar): +2 to Lab Totals")]
    assert "Animal Ken Lab Total" in tradition_text.bonds_text(tradition)
    text = tradition_text.casting_text(Saga(id="x", name="X"), witch, tradition)
    assert "Grimalkin (bound) +2" in text


def test_a_traditions_pools():
    from dataclasses import replace

    from ars_magica_manager.forms import tradition as forms
    from ars_magica_manager.models import PoolDef

    tradition = replace(
        catalog.load_tradition_catalog_by_id()["trad_vitkir"],
        pools=[PoolDef("Sparks", income="1 a season", cap="10")],
    )
    vitki = _member("v", "trad_vitkir")
    ops = forms.pool_ops(vitki, tradition)
    assert ops.rows() == ["Pools"] and ops.add is None and ops.edit is not None
    form = ops.edit(0)
    assert [f.label for f in form.fields()] == ["Sparks"]
    assert form.validate is not None and form.validate({"pool_0": -1})
    form.apply({"pool_0": 4})
    assert vitki.tradition_pools == {"trad_vitkir:Sparks": 4}
    assert "[b]Sparks[/] 4" in tradition_text.pools_text(vitki, tradition)
    form.apply({"pool_0": 0})
    assert vitki.tradition_pools == {}
    plain = catalog.load_tradition_catalog_by_id()["trad_vitkir"]
    assert forms.pool_ops(vitki, plain).edit is None


def test_an_ex_miscellanea_magus_keeps_twilight():
    by_id = catalog.load_tradition_catalog_by_id()
    magus = _member("m", "trad_columbae")
    text = tradition_text.warping_text(magus, by_id["trad_columbae"])
    assert "Twilight as for any magus" in text
