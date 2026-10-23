"""Art & Academe: the schoolmen's disputatio (the five totals, the
Virtues and Flaws that change them, the exchanges, the over-exertion
check, More's Disputatio keeping it in both Diaries) and a physician's
regimen."""

import random

from ars_magica_manager import disputations
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.models import (
    Ability,
    Character,
    Characteristics,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import disputatio
from ars_magica_manager.rules.xp import ability_xp


def _scholar(id_: str, name: str, *virtues: str, artes=4) -> Character:
    scholar = Character(id=id_, name=name, type="companion")
    scholar.characteristics = Characteristics(
        communication=2, perception=1, intelligence=3, presence=1, stamina=1
    )
    scholar.abilities = [Ability("Artes Liberales", xp=ability_xp(artes))]
    scholar.reputations = [
        ScoredTrait("Good Logician", 2, type="Academic"),
        ScoredTrait("Brave", 4, type="Local"),
    ]
    scholar.virtues_flaws = [VirtueFlawInstance(v) for v in virtues]
    return scholar


def test_a_disputer_s_totals():
    side = disputatio.disputer(_scholar("a", "Odo"), "Artes Liberales", "deliberative")
    assert (side.attack, side.defence, side.intelligence, side.resistance) == (
        6,
        5,
        3,
        3,  # Presence 1 + the Academic Reputation 2, not the Local one
    )
    assert disputatio.levels_lost(8, 3) == 1
    assert disputatio.levels_lost(14, 3) == 3
    assert disputatio.levels_lost(3, 3) == 0


def test_virtues_and_flaws_change_the_totals():
    scholar = _scholar(
        "a",
        "Odo",
        "vf_good_teacher",
        "vf_afflicted_tongue",
        "vf_short_attention_span",
        "vf_piercing_gaze",
        "vf_strong_willed",
        "vf_poor_disputer",
        "vf_aristotelian_training",
    )
    side = disputatio.disputer(scholar, "Artes Liberales", "deliberative")
    # Good Teacher +3 and Afflicted Tongue -2, Aristotelian Training +1;
    # its +1 to Artes Liberales for logic and rhetoric too.
    assert side.attack == 6 + 3 - 2 + 1 + 1
    assert side.defence == 5 - 3 + 1 + 1
    assert (side.weakening, side.resistance, side.die) == (4, 3 + 3 + 1, -3)
    epideictic = disputatio.disputer(scholar, "Artes Liberales", "epideictic")
    assert epideictic.attack == side.attack - 3  # Good Teacher: deliberative only
    magus = _scholar("m", "Bonisagus")
    magus.type = "magus"
    assert (
        disputatio.disputer(magus, "Philosophiae", "epideictic", crowd=True).die == -3
    )
    gentle = _scholar("g", "Gentle", "vf_the_gift", "vf_gentle_gift")
    assert (
        disputatio.disputer(gentle, "Philosophiae", "epideictic", crowd=True).die == 0
    )


def test_a_disputatio_runs_until_the_questions_end_or_a_side_falls():
    strong = disputatio.disputer(
        _scholar("a", "Odo", artes=9), "Artes Liberales", "deliberative"
    )
    weak = disputatio.disputer(
        _scholar("b", "Hugh", artes=0), "Artes Liberales", "deliberative"
    )
    result = disputatio.run((strong, weak), 12, random.Random(3))
    assert result.winner == 0 and result.lost[1] == 5
    assert result.exchanges < 12
    # Statements below the judge's Ease Factor go unanswered.
    short = disputatio.run((weak, weak), 1, random.Random(1), ease=99)
    assert short.lost == [0, 0] and short.winner is None
    assert all("short of 99, unanswered" in line for line in short.lines)


def test_the_over_exertion_check():
    side = disputatio.disputer(_scholar("a", "Odo"), "Artes Liberales", "forensic")
    totals = [disputatio.over_exertion(side, 9, random.Random(n)) for n in range(40)]
    assert all(lost == 0 for total, lost in totals if total >= 9)
    assert any(lost >= 1 for _total, lost in totals)
    assert disputatio.reward("forensic", "Odo", "Hugh") == "Odo proves the case."


def test_more_s_disputatio_keeps_it_in_both_diaries():
    odo, hugh = _scholar("a", "Odo", artes=9), _scholar("b", "Hugh", artes=0)
    saga = Saga(id="s", name="S", characters=[odo, hugh])
    assert isinstance(
        disputations.disputatio_form(Saga(id="t", name="T"), None), Refuse
    )
    form = disputations.disputatio_form(saga, odo, random.Random(3))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    assert values["against"] == "b" and values["subject"] == "Artes Liberales"
    assert "Odo: Attack +11" in form.live(values)  # type: ignore[misc]
    assert form.validate is not None
    assert form.validate(values | {"exchanges": 0})
    keep = form.apply(values)
    assert isinstance(keep, Confirm) and "Odo wins" in keep.question
    keep.apply()
    assert [c.diary[-1].name for c in (odo, hugh)] == [
        "Disputatio in Artes Liberales with Hugh",
        "Disputatio in Artes Liberales with Odo",
    ]


def test_a_physician_s_regimen_raises_living_conditions_after_a_year():
    from ars_magica_manager import seasons
    from ars_magica_manager.rules import medicine
    from ars_magica_manager.sheets import character as cs

    doctor = _scholar("d", "Galen")
    doctor.abilities.append(Ability("Medicine", xp=ability_xp(5)))
    patient = _scholar("p", "Odo")
    saga = Saga(id="s", name="S", characters=[doctor, patient])
    saga.current_year = 1221
    patient.aging.regimen, patient.aging.regimen_by = 3, "d"
    patient.aging.regimen_since = 1221
    assert seasons.living_conditions(saga, patient) == 0  # not a year yet
    assert "from 1222" in cs.aging_text(patient, saga)
    patient.aging.regimen_since = 1220
    # Medicine 5 keeps a +2 regimen, not the +3 asked for.
    assert seasons.living_conditions(saga, patient) == 2
    assert "Medicine 5 keeps +2 at most (+3 needs 7)" in cs.aging_text(patient, saga)
    assert medicine.regimen_level(0, 3) == 0
    assert medicine.regimen_bonus(None, 1, 1200, 1221) == 0
