"""Hermetic law on the docket (rules.hermetic_law): Wizard's War, the
Wizard's March, spell traces and Intrigue, and how the meeting and the
sheets take them."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import meeting
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import CASE_DECIDED, Case, Saga, Tribunal
from ars_magica_manager.rules import hermetic_law as law
from ars_magica_manager.sheets import character as character_sheet
from ars_magica_manager.sheets import tribunal as tribunal_sheet


def _rhine(saga: Saga) -> Tribunal:
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return tribunal


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _war(month: int = 1, season: str = "Spring", year: int = 1220, **kw) -> Case:
    return Case(
        "Leandro's war",
        kind=law.WAR,
        brought_by=kw.get("by", "Leandro"),
        against=kw.get("against", "Severinus"),
        filed_year=year,
        filed_season=season,
        month=month,
        served=kw.get("served", "redcap"),
    )


# -- Wizard's War --


def test_a_war_begins_at_the_next_full_moon_and_ends_at_the_one_after():
    war = law.war_of(_war(month=3, season="Winter", year=1220))
    assert war is not None
    assert law.moon_text(war.declared) == "the third month of Winter 1220"
    assert law.moon_text(war.begins) == "the first month of Spring 1221"
    assert law.moon_text(war.ends) == "the second month of Spring 1221"


def test_a_war_without_its_month_says_so():
    case = _war()
    case.month = None
    assert law.war_of(case) is None
    assert law.war_lines(everything_saga(), case)[0][1].startswith("Say the month")


def test_a_declaration_is_between_two_magi_not_a_covenant():
    saga = everything_saga()
    values = {
        "brought_by": "Leandro",
        "against": "Fengheld",
        "month": 1,
        "filed_year": 1220,
        "filed_season": "Spring",
    }
    assert "two magi" in (law.war_problem(saga, "", values) or "")
    values["against"] = "Leandro"
    assert "himself" in (law.war_problem(saga, "", values) or "")
    values["against"] = "Severinus"
    values["month"] = 4
    assert "1 to 3" in (law.war_problem(saga, "", values) or "")


def test_the_same_two_may_not_be_at_war_again_until_the_first_has_ended():
    saga = everything_saga()
    _rhine(saga).cases.append(_war(month=1))
    values = {
        "brought_by": "Severinus",
        "against": "Leandro",
        "filed_year": 1220,
        "filed_season": "Spring",
    }
    # The first war runs from month 2 to month 3 of Spring.
    for month in (1, 2):
        values["month"] = month
        assert "already at war" in (law.war_problem(saga, "", values) or "")
    values["month"] = 3
    assert law.war_problem(saga, "", values) is None
    # Another magus may be at war with Leandro meanwhile.
    values |= {"month": 2, "brought_by": "Alys"}
    assert law.war_problem(saga, "", values) is None


def test_a_war_is_kept_on_the_docket_but_heard_only_if_disputed():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = _war()
    rhine.cases.append(case)
    assert case in tribunal_sheet.open_cases(rhine)
    assert case not in tribunal_sheet.heard_cases(rhine)
    case.served = law.UNDELIVERED
    assert case in tribunal_sheet.heard_cases(rhine)
    text = tribunal_sheet.case_text(saga, rhine, case)
    assert "Wizard's War" in text and "a Quaesitor" in text


def test_declaring_too_often_is_warned_of():
    saga = everything_saga()
    rhine = _rhine(saga)
    for year in (1215, 1217, 1219):
        rhine.cases.append(_war(year=year, against=f"Foe {year}"))
    lines = dict(law.war_lines(saga, rhine.cases[-1]))
    assert "3 Wizard's Wars in 7 years" in lines["Too often"]
    # No book gives a number: three is the storyguide's default.
    assert "storyguide's default" in lines["Too often"]
    assert law.declared_by(saga, "Leandro", 1223) == 2


def test_the_war_shows_on_both_magi_and_ends():
    saga = everything_saga()
    _rhine(saga).cases.append(_war(month=2))
    leandro, severinus = saga.character("mag1"), saga.character("mag_sketch")
    assert leandro is not None and severinus is not None
    assert "Wizard's War with Severinus" in law.standing_text(saga, leandro)
    assert "Wizard's War with Leandro" in (
        character_sheet.hermetic_background_right_text(saga, severinus)
    )
    saga.current_season = "Autumn"
    assert law.standing_text(saga, leandro) == ""


def test_war_state_follows_the_saga_season():
    war = law.war_of(_war(month=3, season="Spring"))
    assert war is not None
    assert law.war_state(war, 1220, "Spring").startswith("to come")
    assert law.war_state(war, 1220, "Summer") == "this season"
    assert law.war_state(war, 1220, "Autumn") == "over"
    assert law.war_state(war, 1219, "Winter").startswith("to come")


# -- the case form --


def test_the_case_form_files_a_war_with_its_month_and_no_notice():
    saga = everything_saga()
    rhine = _rhine(saga)
    form = tribunal_forms.case_ops(saga, rhine).add()
    assert isinstance(form, Form)
    values = _values(
        form,
        title="Leandro declares on Severinus",
        kind=law.WAR,
        brought_by="Leandro",
        against="Severinus",
        month=2,
        served="sanctum_door",
        trace_level=15,
    )
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    case = rhine.cases[-1]
    assert (case.kind, case.month, case.served, case.notice_given) == (
        law.WAR,
        2,
        "sanctum_door",
        True,
    )
    # A war's form keeps no spell trace.
    assert case.trace_level is None
    grid = tribunal_sheet.cases_grid(saga, rhine)
    assert grid.rows[-1][1:4] == ["War", "Spring 1220", "none due"]
    # A second declaration between them now is refused.
    again = tribunal_forms.case_ops(saga, rhine).add()
    assert isinstance(again, Form) and again.validate is not None
    refused = again.validate(
        _values(again, kind=law.WAR, brought_by="Severinus", against="Leandro", month=3)
    )
    assert refused is not None and "already at war" in refused


def test_a_charge_takes_a_spell_trace_and_intrigue():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    form = tribunal_forms.case_ops(saga, rhine).edit(0)
    assert isinstance(form, Form)
    form.apply(
        _values(
            form,
            trace_level=20,
            trace_duration="Sun",
            trace_months=2,
            intrigue_by="mag1",
            intrigue_aim="delay",
        )
    )
    text = tribunal_sheet.case_text(saga, rhine, case)
    # Magnitude 4 halved to 2; a Sun spell's trace is at nothing within a
    # month, then fades a year at a time.
    assert "level 20 Sun spell" in text and "magnitude 0" in text
    # Halving rounds down by the app's own assumption, and says so.
    assert "the app's assumption" in text and "one a year" in text
    assert "against 10" in text  # Acute Sense: 6 + magnitude 4
    assert "Leandro works to hold up" in text and "against 9" in text


# -- the Wizard's March --


def test_only_a_high_crime_or_a_quaesitors_march_may_march():
    high = Case("A", charge="Slaying a magus outside Wizard's War")
    low = Case("B", charge="Reading a text with his sanctum mark")
    assert law.may_march(high) and not law.may_march(low)
    assert law.may_march(Case("C", kind=law.MARCH))
    assert law.march_problem(low, True, None) is not None
    assert law.march_problem(low, False, 3) is None
    assert law.marched(False, 3) and not law.marched(False, 2)
    assert law.march_problem(high, True, 4) is not None
    assert law.low_crime(low.charge) == (
        "Reading a text marked with another's sanctum or House mark",
        "p. 71",
    )
    assert law.low_crime(high.charge) is None


def test_the_estate_is_shared_and_a_quaesitor_gains_nothing():
    case = Case("A", brought_by="Leandro", prosecutor="Alys")
    assert law.estate_shares(case) == [
        ("Leandro", 0.25),
        ("Alys", 0.25),
        ("his heir", 0.5),
    ]
    case.prosecutor = ""
    assert law.estate_shares(case) == [("Leandro", 0.5), ("his heir", 0.5)]
    case.kind = law.MARCH
    assert law.estate_shares(case)[0] == ("the Tribunal's coffers", 0.5)


def test_the_victim_and_the_prosecutor_are_separate_roles():
    # HoH: TL p. 59: a quarter to the victim, a quarter to the prosecutor,
    # a half to one who is both; p. 56: anyone may bring a slain victim's
    # case.
    case = Case(
        "A",
        charge="Slaying a magus outside Wizard's War",
        brought_by="Leandro",
        victim="Alys",
    )
    assert law.estate_shares(case) == [
        ("Alys", 0.25),
        ("Leandro", 0.25),
        ("his heir", 0.5),
    ]
    case.prosecutor = "Alys"
    assert law.estate_shares(case) == [("Alys", 0.5), ("his heir", 0.5)]
    # Beside it, TL p. 53's convention: the slayer takes the heir's half
    # once the victim and prosecutor are paid; no heir is charged.
    lines = dict(law.march_lines(case))
    assert "Alys half" in lines["If Marched"]
    assert (
        "slays him takes the heir's half, once Alys is paid" in lines["By convention"]
    )
    assert "no heir is charged" in lines["By convention"]


def test_the_case_form_keeps_a_victim():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    form = tribunal_forms.case_ops(saga, rhine).edit(0)
    assert isinstance(form, Form)
    form.apply(_values(form, victim="Alys of Merinita"))
    assert case.victim == "Alys of Merinita"
    assert "Victim:[/] Alys of Merinita" in tribunal_sheet.case_text(saga, rhine, case)


def _rulings_form(saga: Saga, rhine: Tribunal) -> tuple[Form, list]:
    form = meeting.hold(saga, rhine)
    assert isinstance(form, Form)
    form.apply(_values(form))
    found = meeting.steps(rhine, rhine.meeting)
    rulings = next(s for s in found if s.key == "rulings")
    return meeting.step_form(saga, rhine, rulings), found


def test_a_march_voted_at_the_rulings_renounces_the_magus_at_the_close():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    case.against = "Severinus"
    form, found = _rulings_form(saga, rhine)
    values = _values(
        form,
        **{f"outcome_{case.id}": "Severinus is cast out", f"march_{case.id}": True},
    )
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    assert "Marched" in found[-3].text(saga, rhine, rhine.meeting)
    closing = meeting.step_form(saga, rhine, found[-1])
    closing.apply(_values(closing))
    assert case.status == CASE_DECIDED
    severinus = saga.character("mag_sketch")
    assert severinus is not None
    assert severinus.hermetic.renounced_year == 1228
    assert severinus.hermetic.renounced_by == "Rhine: Fengheld v. Keep"
    assert "Renounced in 1228" in law.standing_text(saga, severinus)


def test_three_refusals_march_and_a_fourth_is_refused():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    form, _found = _rulings_form(saga, rhine)
    assert form.validate is not None
    assert form.validate(_values(form, **{f"refused_{case.id}": 4})) is not None
    form.apply(_values(form, **{f"refused_{case.id}": 3}))
    assert meeting.ruling_of(rhine.meeting, case)["marched"] is True


def test_a_march_case_is_heard_and_ticked_marched():
    saga = everything_saga()
    rhine = _rhine(saga)
    rhine.cases.append(
        Case("Severinus the diabolist", kind=law.MARCH, against="Severinus")
    )
    form, _found = _rulings_form(saga, rhine)
    fields = {f.key: f for f in form.fields()}
    march = rhine.cases[-1]
    assert fields[f"march_{march.id}"].value is True
    assert f"refused_{march.id}" not in fields
    text = tribunal_sheet.case_text(saga, rhine, march)
    assert "Ratified" in text and "coffers" in text


# -- spell traces and Intrigue --


def test_a_trace_halves_then_fades_by_its_duration_then_by_month_or_year():
    # Level 20 Moon: magnitude 4, halved to 2, a magnitude a month.
    assert law.trace_magnitude(20, "Moon", False, None) == 4
    assert law.trace_magnitude(20, "Moon", False, 0) == 2
    assert law.trace_magnitude(20, "Moon", False, 1) == 1
    assert law.trace_magnitude(20, "Moon", False, 2) == 0
    # Then a year at a time.
    assert law.trace_magnitude(20, "Moon", False, 14) == -1
    # A non-Ritual Momentary spell fades by the month; a Ritual by the year.
    assert law.trace_magnitude(30, "Momentary", False, 0) == 3
    assert law.trace_magnitude(30, "Momentary", False, 5) == -5
    assert law.trace_magnitude(30, "Momentary", True, 5) == 0
    assert law.trace_magnitude(30, "Momentary", False, 40) == law.GONE
    assert not law.detectable(law.GONE) and law.detectable(-9)
    assert law.acute_sense_ease(25) == 11


def test_intrigue_uses_presence_to_sway_and_communication_to_learn():
    saga = everything_saga()
    leandro = saga.character("mag1")
    assert leandro is not None
    c = leandro.characteristics
    sway, learn = law.aim("delay"), law.aim("allies")
    assert sway is not None and learn is not None
    assert (
        law.intrigue_total(leandro, sway) - c.presence
        == law.intrigue_total(leandro, learn) - c.communication
    )
    # A magus's Gift costs 3 unless both are under Parma, 6 if Blatant.
    assert law.gift_penalty(leandro, both_under_parma=False) == law.GIFT_PENALTY
    assert law.gift_penalty(leandro, both_under_parma=True) == 0
    assert (
        law.gift_penalty(leandro, both_under_parma=False, blatant=True)
        == law.BLATANT_PENALTY
    )
    assert law.gift_penalty(leandro, both_under_parma=True, blatant=True) == 0
    assert law.contest_result(2) is None
    assert law.contest_result(10) is not None and "shame him" in law.contest_result(10)
    assert law.folk_ken_bonus(5) == 3 and law.folk_ken_bonus(-7) == -3


def test_a_saved_war_reads_back_and_a_bad_month_is_refused():
    saga = everything_saga()
    rhine = _rhine(saga)
    rhine.cases.append(_war(month=2))
    data = asdict(rhine)
    again = Tribunal.from_dict(data)
    assert again.cases[-1].month == 2 and again.cases[-1].served == "redcap"
    data["cases"][-1]["month"] = 5
    with pytest.raises(ValueError, match="month"):
        Tribunal.from_dict(data)


def test_the_gift_costs_intrigue_unless_both_are_under_parma():
    # HoH: TL p. 24: -3, -6 for a Blatant Gift, unless both parties are
    # under Parma Magica.
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    case.intrigue_by, case.intrigue_aim = "mag1", "delay"
    assert case.intrigue_parma and "costs nothing" in tribunal_sheet.case_text(
        saga, rhine, case
    )
    form = tribunal_forms.case_ops(saga, rhine).edit(0)
    assert isinstance(form, Form)
    form.apply(_values(form, intrigue_parma=False, intrigue_blatant=True))
    assert not case.intrigue_parma and case.intrigue_blatant
    assert "The Gift costs 6" in tribunal_sheet.case_text(saga, rhine, case)
