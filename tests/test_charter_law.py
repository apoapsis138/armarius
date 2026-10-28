"""A charter's law and its life: the Official Seal and the Tribunal's
customs (Covenants pp. 32, 36; Through the Aegis p. 54; Faith & Flame p.
21; The Sundered Eagle p. 31), templates (the Charter of Arae Flaviae,
Covenants pp. 33, 125-128), standings and probation (p. 33), censure
(pp. 35-36), and a breach charged at Tribunal."""

import pytest
from support import strip_markup as plain

from ars_magica_manager import charter_templates as ct
from ars_magica_manager import covenant_charter as cc
from ars_magica_manager.commands import Confirm, Form, Refuse, Then
from ars_magica_manager.forms import charter as charter_forms
from ars_magica_manager.models import (
    CENSURE_EXPELLED,
    CENSURE_LOWERED,
    CENSURE_WITHHELD,
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    STANDING_EXPELLED,
    STANDING_FULL,
    STANDING_GUEST,
    STANDING_PROBATION,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantCharter,
    Saga,
    Tribunal,
)


def _saga(package: str = "core") -> Saga:
    saga = Saga(id="s", name="S", current_year=1220, current_season="Autumn")
    saga.tribunals = [Tribunal(id="t", name="Provence", package=package)]
    saga.covenants = [Covenant(id="c", saga_id="s", name="Jardin", tribunal_id="t")]
    saga.characters = [
        Character(id="joia", name="Joia", type="magus", covenant_id="c"),
        Character(id="lexora", name="Lexora", type="magus", covenant_id="c"),
    ]
    charter = saga.covenants[0].charter_of_covenant
    charter.clauses = [
        CharterClause("1", "Vis is shared.", 1200),
        CharterClause("2", "No guests unasked.", 1200, status=CLAUSE_BROKEN),
    ]
    charter.seals = [CharterSeal("joia", 1200), CharterSeal("lexora", 1200)]
    return saga


def _form(step: object) -> Form:
    assert isinstance(step, Form)
    return step


# -- the Official Seal and the Tribunal's customs --


def test_only_a_notarized_charter_binds_under_the_core_rules():
    saga = _saga()
    covenant = saga.covenants[0]
    assert not cc.binding(saga, covenant)
    assert "Not notarized" in cc.law_line(saga, covenant)
    covenant.charter_of_covenant.ratified = True
    covenant.charter_of_covenant.notarized_by = "Arnulf"
    covenant.charter_of_covenant.notarized_year = 1201
    assert cc.binding(saga, covenant)
    facts = {f.label: f.value for f in cc.facts(saga, covenant)}
    assert facts["Notarized"] == "Yes, by Arnulf, 1201"


def test_in_provence_a_sworn_charter_binds_unnotarized():
    saga = _saga("provence")
    covenant = saga.covenants[0]
    assert cc.binding(saga, covenant)
    line = cc.law_line(saga, covenant)
    assert "legal obligation" in line and "should still notarize" in line
    assert "Through the Aegis p. 54" in plain(cc.charter_text(saga, covenant))


def test_a_theban_charter_asks_the_conciliatory_board():
    saga = _saga("theban")
    covenant = saga.covenants[0]
    keys = [f.key for f in charter_forms.charter_fields(saga, covenant)]
    assert "reviewed" in keys
    facts = {f.label: f.value for f in cc.facts(saga, covenant)}
    assert facts["Reviewed"] == "Not yet"
    form = _form(charter_forms.charter_form(saga, covenant))
    values = {f.key: f.value for f in form.fields()} | {"reviewed": True}
    form.apply(values)
    assert covenant.charter_of_covenant.reviewed
    # Elsewhere there is no such review.
    core = _saga()
    assert "reviewed" not in [
        f.key for f in charter_forms.charter_fields(core, core.covenants[0])
    ]


def test_edit_charter_keeps_who_notarized_it_only_while_ticked():
    saga = _saga()
    covenant = saga.covenants[0]
    form = _form(charter_forms.charter_form(saga, covenant))
    values = {f.key: f.value for f in form.fields()}
    form.apply(values | {"ratified": True, "notarized_by": "Arnulf"})
    assert covenant.charter_of_covenant.notarized_by == "Arnulf"
    form.apply(values | {"ratified": False, "notarized_by": "Arnulf"})
    assert covenant.charter_of_covenant.notarized_by == ""
    assert form.validate is not None
    assert form.validate({"probation_seasons": 0})


def test_an_amended_clause_names_the_high_crime_as_some_tribunals_hold():
    clause = CharterClause("1", "Words.", status=CLAUSE_AMENDED)
    words = plain(cc.gloss(clause, False))
    assert "Several Tribunals" in words and "High Crime" in words


# -- templates --


def test_the_charter_of_arae_flaviae_is_the_books_template():
    [template] = ct.book_templates()
    assert template.id == ct.ARAE_FLAVIAE and template.ratified_unaltered
    assert template.probation_seasons == 7 and len(template.clauses) == 25
    sections = {c.section for c in template.clauses}
    assert sections == {
        "Membership",
        "Method of Governance",
        "Covenant Resources",
        "Member Rights",
        "Member Obligations",
        "Censure",
    }


def test_a_charter_drawn_from_arae_flaviae_is_ratified_while_unaltered():
    saga = _saga()
    covenant = saga.covenants[0]
    ct.use(saga, covenant, ct.book_templates()[0], 1220)
    charter = covenant.charter_of_covenant
    assert "Covenant of Jardin" in charter.preamble
    assert "Tribunal of Provence" in charter.preamble
    # Its seals stay.
    assert [s.character_id for s in charter.seals] == ["joia", "lexora"]
    assert ct.unaltered(saga, covenant) and cc.notarized(saga, covenant)
    facts = {f.label: f.value for f in cc.facts(saga, covenant)}
    assert facts["Notarized"].startswith("At once: The Charter of Arae Flaviae")
    charter.clauses[0].status = CLAUSE_AMENDED
    assert not ct.unaltered(saga, covenant) and not cc.notarized(saga, covenant)


def test_a_saved_template_blanks_the_names_and_suits_its_tribunal():
    saga = _saga("provence")
    covenant = saga.covenants[0]
    covenant.charter_of_covenant.preamble = "We of Jardin, in Provence, swear."
    made = ct.save_as(saga, covenant, "Jardin's Accord", "provence")
    assert made.preamble == "We of {covenant}, in {tribunal}, swear."
    # One of the same name is replaced, not added.
    ct.save_as(saga, covenant, "Jardin's Accord", "provence")
    assert len(saga.charter_templates) == 1
    # A Provençal covenant sees it first; another Tribunal's last.
    assert ct.offered(saga, covenant)[0].id == made.id
    rhine = _saga("rhine")
    rhine.charter_templates = saga.charter_templates
    assert ct.offered(rhine, rhine.covenants[0])[-1].id == made.id
    other = Covenant(id="d", saga_id="s", name="Mistridge", tribunal_id="t")
    ct.use(saga, other, made, 1221)
    assert other.charter_of_covenant.preamble == "We of Mistridge, in Provence, swear."
    ct.forget(saga, made.id)
    assert saga.charter_templates == []


def test_use_a_template_says_what_it_replaces():
    saga = _saga()
    covenant = saga.covenants[0]
    form = _form(charter_forms.use_template(saga, covenant))
    shown = {f.key: f for f in form.fields()}
    assert shown["template"].value == ct.ARAE_FLAVIAE
    assert "2 clauses are replaced" in shown["_replaces"].value
    assert form.live is not None
    assert "25 clauses" in plain(form.live({"template": ct.ARAE_FLAVIAE}))
    assert isinstance(charter_forms.forget_template(saga), Refuse)


# -- standings and probation --


def test_a_probationary_seal_ends_by_the_charters_term():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.charter_of_covenant.probation_seasons = 7
    form = _form(charter_forms.seal_form(saga, covenant))
    form.apply(
        {
            "sealed_joia": True,
            "year_joia": 1200,
            "standing_joia": STANDING_FULL,
            "sealed_lexora": True,
            "year_lexora": 1220,
            "season_lexora": "Autumn",
            "standing_lexora": STANDING_PROBATION,
        }
    )
    lexora = cc.seal_of(covenant.charter_of_covenant, "lexora")
    assert lexora is not None
    assert (lexora.until_year, lexora.until_season) == (1222, "Summer")
    assert "probationary until Summer 1222" in plain(cc.sealed_line(saga, covenant))
    assert cc.probations_ended(saga, covenant) == []
    saga.current_year, saga.current_season = 1222, "Summer"
    assert cc.probations_ended(saga, covenant) == [
        "Lexora's probation ended Summer 1222"
    ]


def test_a_seal_loads_with_a_standing_it_knows():
    assert CharterSeal.from_dict({"character_id": "a"}).standing == STANDING_FULL
    with pytest.raises(ValueError, match="not a standing"):
        CharterSeal.from_dict({"character_id": "a", "standing": "Archmage"})
    with pytest.raises(ValueError, match="probation"):
        CovenantCharter.from_dict({"probation_seasons": 0})


# -- censure --


def test_withholding_a_laboratory_warns_of_the_oath():
    saga = _saga()
    covenant = saga.covenants[0]
    form = _form(charter_forms.censure_clause(saga, covenant, 1))
    assert form.live is not None
    shown = plain(
        form.live(
            {
                "whom": "lexora",
                "penalty": CENSURE_WITHHELD,
                "withheld_laboratory": True,
            }
        )
    )
    assert "Oath of Hermes" in shown and "Covenants p. 36" in shown
    form.apply(
        {
            "whom": "lexora",
            "penalty": CENSURE_WITHHELD,
            "withheld_library": True,
            "withheld_vis_share": True,
            "year": 1220,
            "season": "Autumn",
        }
    )
    censure = covenant.charter_of_covenant.clauses[1].censure
    assert censure is not None and censure.withheld == ["Library", "Vis share"]
    assert "censured" in plain(cc.row(covenant.charter_of_covenant.clauses[1]))


def test_a_censure_is_only_for_a_broken_clause():
    saga = _saga()
    covenant = saga.covenants[0]
    assert isinstance(charter_forms.censure_clause(saga, covenant, 0), Refuse)
    assert not charter_forms.can_censure(covenant, 0)
    assert charter_forms.can_censure(covenant, 1)


@pytest.mark.parametrize(
    ("before", "after"),
    [(STANDING_FULL, STANDING_PROBATION), (STANDING_PROBATION, STANDING_GUEST)],
)
def test_a_lowered_standing_follows_arae_flaviae(before, after):
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.charter_of_covenant.probation_seasons = 7
    covenant.charter_of_covenant.seals[1].standing = before
    form = _form(charter_forms.censure_clause(saga, covenant, 1))
    form.apply(
        {"whom": "lexora", "penalty": CENSURE_LOWERED, "year": 1220, "season": "Autumn"}
    )
    seal = cc.seal_of(covenant.charter_of_covenant, "lexora")
    assert seal is not None and seal.standing == after


def test_expulsion_asks_to_end_membership_and_reminds_each_season():
    saga = _saga()
    covenant = saga.covenants[0]
    form = _form(charter_forms.censure_clause(saga, covenant, 1))
    result = form.apply(
        {
            "whom": "lexora",
            "penalty": CENSURE_EXPELLED,
            "year": 1220,
            "season": "Autumn",
        }
    )
    seal = cc.seal_of(covenant.charter_of_covenant, "lexora")
    assert seal is not None and seal.standing == STANDING_EXPELLED
    assert isinstance(result, Then) and isinstance(result.step, Confirm)
    # Declined: she is still of the covenant, and the charter says so.
    assert [c.id for c in cc.still_resident(saga, covenant)] == ["lexora"]
    assert "Expelled but still of the covenant: Lexora" in plain(
        cc.charter_text(saga, covenant)
    )
    assert "Expelled: Lexora" in plain(cc.sealed_line(saga, covenant))
    reminder = charter_forms.season_reminder(saga, lambda: "played")
    assert isinstance(reminder, Form)
    assert reminder.apply({"end_c_lexora": False}) == "played"
    assert saga.character("lexora").covenant_id == "c"
    # Accepted: she leaves, her seal stays struck, the Diary says so.
    result.step.apply()
    assert saga.character("lexora").covenant_id is None
    assert cc.still_resident(saga, covenant) == []
    assert covenant.diary[-1].name == "Lexora left the covenant"
    assert charter_forms.season_reminder(saga, lambda: "played") == "played"
    assert [s.character.id for s in cc.seals(saga, covenant)] == ["joia", "lexora"]


def test_end_membership_is_offered_only_while_an_expelled_magus_stays():
    saga = _saga()
    covenant = saga.covenants[0]
    assert isinstance(charter_forms.end_membership_step(saga, covenant), Refuse)
    covenant.charter_of_covenant.seals[1].standing = STANDING_EXPELLED
    step = _form(charter_forms.end_membership_step(saga, covenant))
    step.apply({"end_c_lexora": True})
    assert saga.character("lexora").covenant_id is None


# -- charged at Tribunal --


def test_a_breach_of_a_binding_charter_is_charged_at_tribunal():
    saga = _saga()
    covenant = saga.covenants[0]
    assert isinstance(charter_forms.charge(saga, covenant, 1), Refuse)
    covenant.charter_of_covenant.ratified = True
    assert charter_forms.can_charge(saga, covenant, 1)
    assert not charter_forms.can_charge(saga, covenant, 0)
    form = _form(charter_forms.charge(saga, covenant, 1))
    values = {f.key: f.value for f in form.fields()} | {"against": "lexora"}
    form.apply(values)
    [case] = saga.tribunals[0].cases
    assert (case.kind, case.brought_by, case.against) == ("charge", "Jardin", "Lexora")
    assert "a Low Crime" in case.charge
    censure = covenant.charter_of_covenant.clauses[1].censure
    assert censure is not None and censure.case_id == case.id
    assert not charter_forms.can_charge(saga, covenant, 1)


def test_the_tribunal_blank_names_the_region():
    saga = _saga()
    saga.tribunals[0].name = "The Rhine Tribunal"
    assert ct.region_name(saga, saga.covenants[0]) == "Rhine"
    ct.use(saga, saga.covenants[0], ct.book_templates()[0], 1220)
    assert "Tribunal of Rhine." in saga.covenants[0].charter_of_covenant.preamble
