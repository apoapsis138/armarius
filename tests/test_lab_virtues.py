"""Virtues and Flaws during a season of lab work: the plan's options
(Potent Magic, Cyclic Magic, Environmental Magic Condition), a Laboratory
Horoscope, Short-Ranged and Disjointed Magic, Hubris, Waster of Vis, and
extracting Form vis."""

import random

from ars_magica_manager import seasons
from ars_magica_manager.forms.lab_plan import LabPlanForm
from ars_magica_manager.models import (
    Ability,
    ArcaneConnection,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    KnownSpell,
    Laboratory,
    Saga,
    ScoredTrait,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import activities as rules
from ars_magica_manager.rules import lab_seasons, lab_virtues, study
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params=params)


def _saga(*virtues: VirtueFlawInstance) -> Saga:
    magus = Character(id="m", name="Tiberius", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    # CrIg 5 + 5 + 2 + 3 = 15; CrVi 5 + 4 + 2 + 3 = 14.
    magus.arts = {
        "creo": ArtScore(xp=art_xp(5)),
        "ignem": ArtScore(xp=art_xp(5)),
        "vim": ArtScore(xp=art_xp(4)),
        "aquam": ArtScore(xp=art_xp(2)),
    }
    magus.virtues_flaws = list(virtues)
    magus.raw_vis = {"vim": 1}
    magus.assigned_lab_id = "lab"
    lab = Laboratory(id="lab", covenant_id="cov", name="Tower", owner_id="m")
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep")],
        characters=[magus],
        laboratories=[lab],
    )
    saga.spells = [
        Spell("bolt", "Bolt", "Creo", "Ignem", level=5, range="Voice"),
        Spell("warm", "Warm Hands", "Creo", "Ignem", level=10, range="Touch"),
        Spell("spark", "Spark", "Creo", "Ignem", level=10),
    ]
    return saga


def _plan(activity=lab_seasons.INVENT, spell_id="warm", **kw) -> SeasonPlan:
    return SeasonPlan(
        "m", 1220, "Spring", activity, lab_id="lab", spell_id=spell_id, **kw
    )


def _total(saga: Saga, plan: SeasonPlan) -> int:
    found, work = lab_seasons.work(saga, saga.characters[0], plan)
    assert found == [] and work is not None, found
    return int(work.lab_total.total)


def test_potent_magic_adds_three_or_six_when_ticked():
    saga = _saga(_vf("vf_potent_magic", field="fire"))
    assert _total(saga, _plan()) == 15
    assert _total(saga, _plan(potent=True)) == 18
    saga.characters[0].virtues_flaws.append(_vf("vf_potent_magic_major", field="heat"))
    assert _total(saga, _plan(potent=True)) == 21  # the best one only


def test_cyclic_magic_and_environmental_magic_condition():
    saga = _saga(_vf("vf_cyclic_magic_positive"), _vf("vf_cyclic_magic_negative"))
    assert _total(saga, _plan(cycle_bonus=True)) == 18
    assert _total(saga, _plan(cycle_penalty=True)) == 12
    saga.characters[0].virtues_flaws = [_vf("vf_environmental_magic_condition")]
    extract = _plan(lab_seasons.EXTRACT, None, vis_from="laboratory", condition=True)
    assert _total(saga, extract) == 7  # 14 halved


def test_short_ranged_magic_halves_designing_beyond_touch():
    saga = _saga(_vf("vf_short_ranged_magic"))
    assert _total(saga, _plan(spell_id="warm")) == 15
    _found, work = lab_seasons.work(saga, saga.characters[0], _plan(spell_id="bolt"))
    assert int(work.lab_total.total) == 7
    assert any("Short-Ranged" in line.label for line in work.lab_total.lines)


def test_disjointed_magic_gets_nothing_from_a_similar_spell():
    saga = _saga()
    saga.characters[0].spells_known = [KnownSpell("spark")]
    assert _total(saga, _plan(similar_spell_id="spark")) == 17
    saga.characters[0].virtues_flaws = [_vf("vf_disjointed_magic")]
    assert _total(saga, _plan(similar_spell_id="spark")) == 15


def test_a_laboratory_horoscope_adds_its_bonus_when_the_roll_succeeds():
    saga = _saga(_vf("vf_planetary_magic"))
    # Planetary Magic serves only enchanting: inventing gains nothing.
    assert _total(saga, _plan(horoscope=3, horoscope_die=10)) == 15
    saga.characters[0].virtues_flaws = [_vf("vf_celestial_magic")]
    # Die 7 + Intelligence 2 + Artes Liberales 0 = 9, against 3 x 3.
    assert _total(saga, _plan(horoscope=3, horoscope_die=7)) == 18
    worked = rules.outcome(
        saga.characters[0], _plan(horoscope=3, horoscope_die=6), saga
    )
    assert any("failed" in note for note in worked.notes)
    # Not typed: rolled as the season is played, noted until then.
    preview = rules.outcome(saga.characters[0], _plan(horoscope=3), saga)
    assert any("rolled when the season is applied" in n for n in preview.notes)
    played = rules.outcome(
        saga.characters[0], _plan(horoscope=3), saga, random.Random(4)
    )
    assert played.plan.horoscope_die is not None


def test_hubris_adds_its_score_to_binding_and_a_talisman():
    magus = _saga(_vf("vf_hubris")).characters[0]
    magus.personality_traits = [ScoredTrait("Hubris", 2)]
    lines, _ = lab_virtues.option_lines(
        magus,
        _plan(),
        enchanting=False,
        talisman=False,
        binding=True,
        horoscope_score=0,
    )
    assert [(line.label, line.amount) for line in lines] == [("Hubris", 2)]


def test_waster_of_vis_needs_a_third_more():
    assert [lab_virtues.with_waste(n) for n in (1, 3, 10, 12)] == [2, 4, 14, 16]
    saga = _saga(_vf("vf_waster_of_vis"))
    saga.laboratories[0].arcane_connections = [ArcaneConnection("ac", "a lock")]
    fix = _plan(lab_seasons.FIX_AC, None, connection_id="ac", vis_from="character")
    found, _ = lab_seasons.work(saga, saga.characters[0], fix)
    assert "Waster of Vis" in found[0]
    saga.characters[0].raw_vis = {"vim": 2}
    found, work = lab_seasons.work(saga, saga.characters[0], fix)
    assert found == [] and work.vis_wasted == {"Vim": 1}
    seasons.plan_lab_work(saga, fix)
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.characters[0].raw_vis == {}
    # Vis study too: Ignem 5 takes one pawn, two with the waste.
    assert study.season_vis_pawns(saga.characters[0], 5) == 2


def test_hermetic_alchemy_extracts_form_vis_at_a_twentieth():
    saga = _saga(_vf("vf_hermetic_alchemy"))
    extract = _plan(lab_seasons.EXTRACT, None, vis_from="laboratory")
    _found, work = lab_seasons.work(saga, saga.characters[0], extract)
    assert (work.vis_gained, work.vis_gained_art) == (2, "Vim")  # 14 / 10
    # Ignem (5) above Vim (4): the total stays 14, plus shape and
    # material up to Magic Theory 3; 17 / 20 rounds up to 1.
    ignem = _plan(
        lab_seasons.EXTRACT,
        None,
        vis_from="laboratory",
        extract_form="Ignem",
        shape_bonus=5,
    )
    _found, work = lab_seasons.work(saga, saga.characters[0], ignem)
    assert int(work.lab_total.total) == 17
    assert (work.vis_gained, work.vis_gained_art) == (1, "Ignem")
    # Aquam (2) below Vim limits the total as a requisite.
    aquam = _plan(
        lab_seasons.EXTRACT, None, vis_from="laboratory", extract_form="Aquam"
    )
    assert _total(saga, aquam) == 12
    seasons.plan_lab_work(saga, ignem)
    seasons.apply(saga, seasons.resolve(saga))
    assert saga.laboratories[0].raw_vis == {"ignem": 1}


def test_an_extractor_of_form_vis_gets_a_tenth_and_only_its_form():
    saga = _saga(_vf("vf_extractor_of_form_vis", form="ignem"))
    ignem = _plan(
        lab_seasons.EXTRACT, None, vis_from="laboratory", extract_form="Ignem"
    )
    _found, work = lab_seasons.work(saga, saga.characters[0], ignem)
    assert (work.vis_gained, work.vis_gained_art) == (2, "Ignem")  # 14 / 10
    aquam = _plan(
        lab_seasons.EXTRACT, None, vis_from="laboratory", extract_form="Aquam"
    )
    found, _ = lab_seasons.work(saga, saga.characters[0], aquam)
    assert "only Vim" in found[0]


def test_the_lab_plan_form_offers_only_the_magus_s_own_options():
    saga = _saga()
    magus, lab = saga.characters[0], saga.laboratories[0]
    keys = {f.key for f in LabPlanForm(saga, magus, lab, "Spring", 1220, None).fields()}
    options = {"potent", "cycle_bonus", "condition", "horoscope", "extract_form"}
    assert not options & keys
    magus.virtues_flaws = [
        _vf("vf_potent_magic", field="fire"),
        _vf("vf_cyclic_magic_positive"),
        _vf("vf_environmental_magic_condition"),
        _vf("vf_celestial_magic"),
        _vf("vf_hermetic_alchemy"),
    ]
    form = LabPlanForm(saga, magus, lab, "Spring", 1220, None)
    assert options <= {f.key for f in form.fields()}
    plan = form.plan_of(
        {
            "activity": lab_seasons.EXTRACT,
            "potent": True,
            "horoscope": 9,
            "extract_form": "Ignem",
            "extract_shape": 4,
        }
    )
    assert (plan.potent, plan.horoscope, plan.extract_form, plan.shape_bonus) == (
        True,
        5,
        "Ignem",
        4,
    )


def test_magical_memory_needs_no_copy_of_the_magus_s_own_lab_texts():
    magus = _saga(_vf("vf_magical_memory")).characters[0]
    own = Book("t", "Lab Text: Ward", "Lab Text", author_id="m")
    other = Book("u", "Lab Text: Lamp", "Lab Text", author_id="x")
    assert lab_virtues.remembers(magus, own) and not lab_virtues.remembers(magus, other)
    magus.virtues_flaws = []
    assert not lab_virtues.remembers(magus, own)
