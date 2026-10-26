"""A covenant's Charter of Covenant: its clauses, their sections and
statuses, the members' seals, and the forms that change them (Covenants
pp. 31-36, the Appendix's blank charter pp. 125-128)."""

import dataclasses

import pytest
from support import strip_markup as plain

from ars_magica_manager import actions
from ars_magica_manager import covenant_charter as cc
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import charter as charter_forms
from ars_magica_manager.models import (
    CLAUSE_AMENDED,
    CLAUSE_BROKEN,
    CLAUSE_IN_FORCE,
    Character,
    CharterClause,
    CharterSeal,
    Covenant,
    CovenantCharter,
    HermeticBackground,
    Saga,
)
from ars_magica_manager.sections import CHARTER_SECTION, CLAUSES_SECTION


def _saga() -> Saga:
    covenant = Covenant(id="stone", saga_id="s", name="Stone House")
    charter = covenant.charter_of_covenant
    charter.name = "The Founders' Accord"
    charter.year, charter.season = 1115, "Spring"
    charter.clauses = [
        CharterClause("1", "What any finds is shared.", 1115, "Spring"),
        CharterClause(
            "2",
            "The house decides in council.",
            1115,
            "Spring",
            status=CLAUSE_AMENDED,
            since_year=1180,
            since_season="Summer",
            note="The warden's keys added.",
        ),
        CharterClause(
            "3",
            "Nothing goes to the Tribunal.",
            1115,
            "Spring",
            status=CLAUSE_BROKEN,
            since_year=1205,
            note="Matthaios's letters.",
        ),
    ]
    ilona = Character(
        id="ilona",
        name="Ilona of Tremere",
        type="magus",
        covenant_id="stone",
        hermetic=HermeticBackground(house="tremere"),
    )
    benedek = Character(id="benedek", name="Benedek", type="magus", covenant_id="stone")
    grog = Character(id="hilda", name="Hilda", type="grog", covenant_id="stone")
    charter.seals = [CharterSeal("ilona", 1115, "Spring")]
    return Saga(
        id="s", name="S", covenants=[covenant], characters=[ilona, benedek, grog]
    )


def _covenant(saga: Saga) -> Covenant:
    return saga.covenants[0]


# -- the model --


def test_an_older_save_loads_with_an_empty_charter():
    loaded = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "C"})
    assert loaded.charter_of_covenant == CovenantCharter()


def test_the_charter_round_trips_through_a_save():
    covenant = _covenant(_saga())
    again = Covenant.from_dict(dataclasses.asdict(covenant))
    assert again.charter_of_covenant == covenant.charter_of_covenant


def test_a_bad_status_or_year_in_a_save_is_reported():
    with pytest.raises(ValueError, match="status"):
        CharterClause.from_dict({"number": "1", "status": "Torn up"})
    with pytest.raises(ValueError, match="year"):
        CovenantCharter.from_dict({"year": "1115"})
    with pytest.raises(ValueError, match="season"):
        CharterSeal.from_dict({"character_id": "x", "season": "Midsummer"})
    with pytest.raises(ValueError, match="magus"):
        CharterSeal.from_dict({"year": 1115})


def test_the_town_charter_keeps_its_own_field():
    """The Chartered Town Boon's town charter is Covenant.charter; the
    magi's own charter doesn't touch it, nor the vassal's oath."""
    covenant = Covenant.from_dict(
        {"id": "c", "saga_id": "s", "name": "C", "charter": {"lords": []}, "oath": "x"}
    )
    assert covenant.charter == {"lords": []}
    assert covenant.oath == "x"
    assert covenant.charter_of_covenant.preamble == ""


# -- what the sheets show --


def test_titles_count_the_clauses_in_force():
    charter = _covenant(_saga()).charter_of_covenant
    assert cc.clauses_title(charter) == "Clauses (2 in force of 3)"
    assert cc.clauses_title(CovenantCharter()) == "Clauses (0)"
    assert cc.charter_title(CovenantCharter()) == "Charter of Covenant"


def test_clause_names_and_marks():
    numbered = CharterClause("4", "x")
    titled = CharterClause("Apprentices", "x")
    assert (cc.clause_mark(numbered), cc.clause_name(numbered)) == ("4.", "Clause 4")
    assert (cc.clause_mark(titled), cc.clause_name(titled)) == (
        "Apprentices",
        "Apprentices",
    )


def test_status_words_and_the_struck_clause():
    clauses = _covenant(_saga()).charter_of_covenant.clauses
    assert [cc.status_words(c) for c in clauses] == [
        "In force",
        "Amended Summer 1180",
        "Broken 1205",
    ]
    assert cc.clause_text(clauses[2]).startswith("[s dim]")
    assert cc.note_line(clauses[0]) == ""
    assert (
        plain(cc.note_line(clauses[1]))
        == "Amended, Summer 1180: The warden's keys added."
    )
    assert plain(cc.note_line(clauses[2])) == "Broken, 1205: Matthaios's letters."


def test_a_broken_clause_is_a_low_crime_only_once_ratified():
    saga = _saga()
    charter = _covenant(saga).charter_of_covenant
    assert "Covenants p. 35" in cc.info(charter, 2, wide=True)
    assert "was ratified" not in cc.info(charter, 2, wide=True)
    charter.ratified = True
    assert "was ratified by a Quaesitor" in cc.info(charter, 2, wide=True)
    assert "Covenants p. 36" in cc.charter_text(saga, _covenant(saga))


def test_an_amended_clause_cites_the_rule_on_altering_the_charter():
    charter = _covenant(_saga()).charter_of_covenant
    shown = cc.info(charter, 1, wide=False)
    assert "Covenants p. 33" in shown and "against a member's will" in shown


def test_with_no_sections_the_clauses_are_one_group_as_entered():
    charter = _covenant(_saga()).charter_of_covenant
    assert cc.grouped(charter) == [("", [0, 1, 2])]
    assert all(index is not None for index, _ in cc.rows(charter))


def test_clauses_group_under_their_sections_in_the_books_order():
    charter = _covenant(_saga()).charter_of_covenant
    charter.clauses[0].section = "Member Rights"
    charter.clauses[2].section = "Oath of Covenant"
    assert cc.grouped(charter) == [
        ("Oath of Covenant", [2]),
        ("Member Rights", [0]),
        (cc.OTHER, [1]),
    ]
    assert cc.order(charter) == [2, 0, 1]
    headings = [plain(text) for index, text in cc.rows(charter) if index is None]
    assert headings == ["Oath of Covenant", "Member Rights", "Other"]


def test_the_seals_list_who_sealed_and_who_has_not_sworn():
    saga = _saga()
    covenant = _covenant(saga)
    shown = cc.seals(saga, covenant)
    assert [(s.character.id, s.when) for s in shown] == [
        ("ilona", "Spring 1115"),
        ("benedek", ""),
    ]
    line = plain(cc.sealed_line(saga, covenant))
    assert line == (
        "Sealed by: Ilona of Tremere (Spring 1115)  ·  Not yet sworn: Benedek"
    )
    facts = {f.label: f.value for f in cc.facts(saga, covenant)}
    assert facts["Sealed"] == "1 of 2"
    assert facts["Clauses"] == "3, 1 broken"


def test_a_magus_who_left_keeps_his_seal_on_the_charter():
    saga = _saga()
    saga.characters[0].covenant_id = None
    assert [s.character.id for s in cc.seals(saga, _covenant(saga))] == [
        "ilona",
        "benedek",
    ]


# -- the forms --


def test_edit_charter_sets_its_name_preamble_and_ratification():
    saga = _saga()
    covenant = _covenant(saga)
    form = charter_forms.charter_ops(saga, covenant)[CHARTER_SECTION].edit
    assert form is not None
    step = form(0)
    assert isinstance(step, Form)
    step.apply(
        {
            "name": "The Oath",
            "season": "Autumn",
            "year": 1197,
            "preamble": "We swear.",
            "ratified": True,
        }
    )
    charter = covenant.charter_of_covenant
    assert (charter.name, charter.season, charter.year) == ("The Oath", "Autumn", 1197)
    assert charter.preamble == "We swear." and charter.ratified


def test_add_edit_and_delete_a_clause():
    saga = _saga()
    covenant = _covenant(saga)
    ops = charter_forms.clause_ops(saga, covenant)
    assert ops.add is not None and ops.edit is not None and ops.remove is not None
    add = ops.add()
    assert isinstance(add, Form)
    keys = [f.key for f in add.fields()]
    assert keys[:3] == ["number", "section", "text"]
    add.apply(
        {
            "number": "Apprentices",
            "section": "Membership",
            "text": "No apprentice without leave.",
            "season": "Autumn",
            "year": 1130,
            "status": CLAUSE_IN_FORCE,
            # Kept only while amended or broken.
            "note": "ignored",
        }
    )
    made = covenant.charter_of_covenant.clauses[-1]
    assert (made.number, made.section, made.note) == ("Apprentices", "Membership", "")
    edit = ops.edit(0)
    assert isinstance(edit, Form)
    edit.apply(
        {
            "number": "1",
            "text": "Shared.",
            "status": CLAUSE_AMENDED,
            "since_season": "Winter",
            "since_year": 1190,
            "note": "Shortened.",
        }
    )
    first = covenant.charter_of_covenant.clauses[0]
    assert (first.status, first.since_year, first.note) == (
        CLAUSE_AMENDED,
        1190,
        "Shortened.",
    )
    remove = ops.remove(0)
    assert isinstance(remove, Confirm) and "Clause 1" in remove.question
    remove.apply()
    assert len(covenant.charter_of_covenant.clauses) == 3


def test_the_clause_forms_inspector_shows_it_as_the_list_will():
    saga = _saga()
    live = charter_forms.clause_live(saga, _covenant(saga), None)
    shown = plain(
        live(
            {
                "number": "9",
                "text": "No dragons.",
                "status": CLAUSE_BROKEN,
                "since_year": 1219,
                "note": "A dragon.",
            }
        )
    )
    assert "Clause 9" in shown and "Broken, 1219: A dragon." in shown


def test_break_a_clause_strikes_it_with_when_and_how():
    saga = _saga()
    covenant = _covenant(saga)
    step = charter_forms.break_clause(saga, covenant, 0)
    assert isinstance(step, Form) and step.inspector == "The Clause Struck"
    assert step.live is not None
    preview = step.live({"season": "Spring", "year": 1220, "note": "Kyrillos."})
    assert "[s dim]" in preview and "Broken, Spring 1220" in plain(preview)
    step.apply({"season": "Spring", "year": 1220, "note": "Kyrillos."})
    clause = covenant.charter_of_covenant.clauses[0]
    assert (clause.status, clause.since_season, clause.since_year, clause.note) == (
        CLAUSE_BROKEN,
        "Spring",
        1220,
        "Kyrillos.",
    )


def test_a_broken_clause_cant_be_broken_again():
    saga = _saga()
    covenant = _covenant(saga)
    assert isinstance(charter_forms.break_clause(saga, covenant, 2), Refuse)
    assert isinstance(charter_forms.break_clause(saga, covenant, None), Refuse)
    assert not charter_forms.can_break(covenant, 2)
    assert charter_forms.can_break(covenant, 1)


def test_seal_the_charter_sets_each_magus_seal():
    saga = _saga()
    covenant = _covenant(saga)
    step = charter_forms.seal_form(saga, covenant)
    assert isinstance(step, Form)
    labels = [f.label for f in step.fields() if f.kind == "check"]
    assert labels == ["Ilona of Tremere", "Benedek"]  # the grog doesn't seal
    step.apply(
        {
            "sealed_ilona": False,
            "sealed_benedek": True,
            "season_benedek": "Winter",
            "year_benedek": 1212,
        }
    )
    assert covenant.charter_of_covenant.seals == [
        CharterSeal("benedek", 1212, "Winter")
    ]


def test_seal_the_charter_needs_magi():
    saga = _saga()
    saga.characters = []
    assert isinstance(charter_forms.seal_form(saga, _covenant(saga)), Refuse)


# -- where the actions are offered --


class _Facts:
    def __init__(self, saga: Saga, section: str, row: int | None) -> None:
        self.saga = saga
        self.selected_kind = actions.NodeKind.COVENANT
        self.selected_covenant = saga.covenants[0]
        self.selected_character = None
        self.selected_laboratory = None
        self._section, self._row = section, row

    def active_section(self) -> str:
        return self._section

    def player_may(self, _action: str) -> bool:
        return True

    def chosen_row(self, _section: str) -> int | None:
        return self._row


def test_break_a_clause_is_offered_on_a_clause_not_yet_broken():
    saga = _saga()

    def offered(section: str, row: int | None) -> bool:
        return actions.available("break_clause", _Facts(saga, section, row))  # type: ignore[arg-type]

    assert offered(CLAUSES_SECTION, 0)
    assert not offered(CLAUSES_SECTION, 2)
    assert not offered(CLAUSES_SECTION, None)
    assert not offered(CHARTER_SECTION, 0)


def test_seal_the_charter_is_offered_on_the_charter():
    saga = _saga()
    assert actions.available("seal_charter", _Facts(saga, CHARTER_SECTION, 0))  # type: ignore[arg-type]
    assert not actions.available("seal_charter", _Facts(saga, CLAUSES_SECTION, 0))  # type: ignore[arg-type]
    assert actions.SECTION_VERBS[CLAUSES_SECTION] == {"add", "edit", "remove"}
    assert actions.SECTION_VERBS[CHARTER_SECTION] == {"edit"}
