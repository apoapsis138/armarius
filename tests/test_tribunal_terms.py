"""Rulings written from templates, and rulings made for a term: the
blanks a template asks, the term a {years} blank sets, the notice the
season before it ends, and the case put back on the docket when it does."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import ahead, meeting, ruling_templates, tribunal_terms
from ars_magica_manager.commands import Form, Then
from ars_magica_manager.models import CASE_OPEN, Saga


def _rhine(saga: Saga):
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return tribunal


def _save(form, **changes):
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def test_a_template_names_its_blanks_and_fills_them():
    text = "{party} holds {what} for {years} years, until {party} yields."
    assert ruling_templates.blanks(text) == ["party", "what", "years"]
    filled = ruling_templates.fill(text, {"party": "Keep", "years": 7})
    assert filled == "Keep holds [what] for 7 years, until Keep yields."
    assert ruling_templates.refused("{party pays") is not None
    assert ruling_templates.refused("{party!} pays") is not None
    assert ruling_templates.refused("{vis source} is shared") is None


def test_a_saga_uses_the_apps_templates_until_it_has_its_own():
    saga = everything_saga()
    names = [t["name"] for t in ruling_templates.templates(saga)]
    assert "Holds for a term" in names
    saga.ruling_templates = [{"name": "Banished", "text": "{party} leaves."}]
    assert ruling_templates.named(saga, "Banished") is not None
    assert ruling_templates.named(saga, "Holds for a term") is None
    field = ruling_templates.saga_field(saga)
    assert field.display is not None and field.display(field.value) == "1 template"


def _rule_with_a_term(saga: Saga, rhine) -> tuple[object, list]:
    """Hold the meeting to its Rulings, and rule the first case with
    "Holds for a term"; the blanks' form that follows."""
    _save(meeting.hold(saga, rhine))
    found = meeting.steps(rhine, rhine.meeting)
    rulings = next(s for s in found if s.key == "rulings")
    case = rhine.cases[0]
    asked = _save(
        meeting.step_form(saga, rhine, rulings),
        **{f"template_{case.id}": "Holds for a term"},
    )
    return asked, found


def test_a_template_asks_its_blanks_then_the_next_step_opens():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    asked, _found = _rule_with_a_term(saga, rhine)
    assert isinstance(asked, Form) and asked.title.startswith("Ruling: Fengheld")
    labels = {f.label: f.value for f in asked.fields() if f.kind != "info"}
    # {party} starts as the accused.
    assert labels["Party"] == "Keep" and labels["Years"] is None
    assert asked.live is not None
    sentence = asked.live({"blank_party": "Keep", "blank_what": "the ford"})
    assert sentence.startswith("Keep holds the ford for \\[years] years")
    following = _save(asked, blank_what="the ford", blank_years=7)
    assert isinstance(following, Then)
    assert following.step.title.endswith("Treasury and vis")
    kept = meeting.ruling_of(rhine.meeting, case)
    assert kept["term"] == 7
    assert kept["outcome"] == (
        "Keep holds the ford for 7 years, until it is debated again."
    )


def test_a_term_is_set_when_the_meeting_closes():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    asked, found = _rule_with_a_term(saga, rhine)
    _save(asked, blank_what="the ford", blank_years=7)
    year = rhine.meeting["year"]
    _save(meeting.step_form(saga, rhine, found[-1]))
    assert case.term_ends_year == year + 7
    assert tribunal_terms.ends_text(case) == f"Summer {year + 7}"


def test_a_written_out_ruling_can_take_a_term_of_its_own():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    _save(meeting.hold(saga, rhine))
    found = meeting.steps(rhine, rhine.meeting)
    rulings = meeting.step_form(
        saga, rhine, next(s for s in found if s.key == "rulings")
    )
    values = {f.key: f.value for f in rulings.fields() if f.kind != "info"}
    values[f"term_{case.id}"] = 0
    assert rulings.validate is not None and "year or more" in (
        rulings.validate(values) or ""
    )
    following = _save(
        rulings,
        **{f"outcome_{case.id}": "Keep shares the ford", f"term_{case.id}": 3},
    )
    assert isinstance(following, Then)
    assert meeting.ruling_of(rhine.meeting, case)["term"] == 3


def _termed(saga: Saga):
    rhine = _rhine(saga)
    case = rhine.cases[0]
    case.outcome = "Keep holds the ford"
    case.term_ends_year = saga.current_year + 1
    case.term_ends_season = saga.current_season
    return rhine, case


def test_a_term_is_told_the_season_before_and_docketed_when_it_ends():
    saga = everything_saga()
    rhine, case = _termed(saga)
    cases = len(rhine.cases)
    assert tribunal_terms.come_due(saga) == []
    # The season before it ends: told, nothing docketed.
    saga.current_year += 1
    saga.current_season, saga.current_year = _season_before(saga)
    told = tribunal_terms.come_due(saga)
    assert len(told) == 1 and "ends next season" in told[0]
    assert len(rhine.cases) == cases
    # The season it ends: back on the docket, once.
    saga.current_season, saga.current_year = case.term_ends_season, case.term_ends_year
    told = tribunal_terms.come_due(saga)
    assert len(told) == 1 and "debated again" in told[0]
    again = rhine.cases[-1]
    assert again.title == "Fengheld v. Keep (debated again)"
    assert again.status == CASE_OPEN and "Keep holds the ford" in again.charge
    assert case.term_docketed
    assert tribunal_terms.come_due(saga) == []
    assert len(rhine.cases) == cases + 1


def _season_before(saga: Saga) -> tuple[str, int]:
    from ars_magica_manager.models import SEASONS

    at = SEASONS.index(saga.current_season)
    if at == 0:
        return SEASONS[-1], saga.current_year - 1
    return SEASONS[at - 1], saga.current_year


def test_ahead_shows_a_term_ending():
    saga = everything_saga()
    _, case = _termed(saga)
    titles = [e.title for e in ahead.entries(saga)]
    assert f"The term of {case.title} ends next season" in titles
    assert f"The term of {case.title} ends: back on the docket" in titles
    case.term_docketed = True
    titles = [e.title for e in ahead.entries(saga)]
    assert not any("The term of" in t for t in titles)
