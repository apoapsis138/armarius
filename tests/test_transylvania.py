"""Transylvania's customs: its magi live in oppida, each magus holds the
privilege of one of the five legal covenants, and each oppidum has its
aediles."""

from __future__ import annotations

from typing import Any

from support import everything_saga

from ars_magica_manager import meeting, saga_overview, treasury, tribunal_packages
from ars_magica_manager.commands import Choose, Form
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import Saga, TreasuryEntry, Tribunal
from ars_magica_manager.sheets import character as character_sheet
from ars_magica_manager.sheets import covenant as covenant_sheet
from ars_magica_manager.sheets import tribunal as tribunal_sheet
from ars_magica_manager.treasury import LEVY, NOTE
from ars_magica_manager.tribunal_packages import transylvania as tr


def _transylvanian() -> tuple[Saga, Tribunal]:
    """The sample saga with its Rhine Tribunal following Transylvania's
    customs: Keep (Leandro's) and the sketched covenant are its oppida."""
    saga = everything_saga()
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    rhine.package = "transylvania"
    return saga, rhine


def test_its_screens_call_the_place_an_oppidum():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    assert tribunal_sheet.roster_title(saga, rhine) == "Oppida (2)"
    assert tribunal_sheet.roster_grid(saga, rhine).columns[0] == "Oppidum"
    assert tribunal_sheet.magi_grid(saga, rhine).columns[2] == "Oppidum"
    assert "Spring oppidum" in covenant_sheet.subtitle(saga, keep)
    assert "Spring oppidum" in saga_overview.covenant_subtitle(saga, keep)
    # Elsewhere the place is still a covenant.
    rhine.package = "rhine"
    assert tribunal_sheet.roster_title(saga, rhine) == "Covenants (2)"
    assert "Spring covenant" in covenant_sheet.subtitle(saga, keep)


def test_a_magus_sheet_shows_their_oppidum_and_privilege():
    saga, rhine = _transylvanian()
    leandro = saga.character("mag1")
    assert leandro is not None
    facts = {f.label: f.value for f in character_sheet.glance_facts(saga, leandro)}
    assert facts["Oppidum"] == "Keep"
    assert facts["Privilege"] == "(not entered)"
    tr.members(saga, rhine).append({"character_id": "mag1", "privilege": "cives"})
    text = character_sheet.info_right_text(saga, leandro)
    assert "Oppidum" in text and "Cives (Coeris)" in text
    rhine.package = "rhine"
    facts = {f.label: f.value for f in character_sheet.glance_facts(saga, leandro)}
    assert "Privilege" not in facts and facts["Covenant"] == "Keep"


def test_the_five_covenants_list_by_legal_covenant_with_offices():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    rhine.praeco_id = "mag_sketch"
    tr.members(saga, rhine).extend(
        [
            {"character_id": "mag1", "privilege": "coloniae", "office": "Curantis"},
            {"character_id": "mag_sketch", "privilege": "cives"},
        ]
    )
    tr.save_aediles(rhine, keep.id, {"aedile_0": "mag1"})
    grid = tr.members_grid(saga, rhine)
    assert grid.columns == ["Magus", "Oppidum", "Privilege", "Office"]
    assert [row[2] for row in grid.rows] == ["Cives (Coeris)", "Coloniae (Asclepius)"]
    assert grid.keys == [1, 0]
    assert grid.rows[0][3] == "Praeco"
    assert grid.rows[1][1:] == ["Keep", "Coloniae (Asclepius)", "Aedile, Curantis"]
    assert tr.members_title(saga, rhine) == "The Five Covenants (2)"


def test_a_magus_has_one_privilege():
    saga, rhine = _transylvanian()
    ops = tr.member_ops(saga, rhine)
    form = ops.add()
    assert isinstance(form, Form)
    form.apply({"character_id": "mag1", "privilege": "socii", "office": ""})
    assert tr.privilege_label(tr.entry_of(saga, rhine, "mag1")) == "Socii (Domostron)"
    again = ops.add()
    assert isinstance(again, Form) and again.validate is not None
    assert "already has a privilege" in (again.validate({"character_id": "mag1"}) or "")
    edit = ops.edit(0)
    assert isinstance(edit, Form) and edit.validate is not None
    assert edit.validate({"character_id": "mag1"}) is None


def test_an_oppidum_s_own_form_chooses_its_aediles_from_its_magi():
    saga, rhine = _transylvanian()
    keep = saga.covenant("cov1")
    assert keep is not None
    fields = tribunal_forms.package_fields(saga, keep)
    aediles = [f for f in fields if f.key.startswith("package_rhine_aedile")]
    assert len(aediles) == 2
    assert [value for _, value in aediles[0].options] == ["mag1"]
    assert aediles[0].show_if is not None
    assert aediles[0].show_if({"tribunal_id": "rhine"})
    assert not aediles[0].show_if({"tribunal_id": "thebes"})
    values = {aediles[0].key: "mag1", aediles[1].key: None, "name": "Keep"}
    tribunal_forms.save_package_fields(saga, keep, values)
    assert values == {"name": "Keep"}
    assert tr.aediles(rhine) == {"cov1": ["mag1"]}
    roster = tribunal_sheet.roster_grid(saga, rhine)
    assert roster.columns[5] == "Aediles"
    assert roster.rows[0][5] == "Leandro"
    tr.save_aediles(rhine, keep.id, {"aedile_0": None, "aedile_1": None})
    assert tr.aediles(rhine) == {}


def test_only_a_transylvanian_tribunal_asks_for_aediles():
    saga = everything_saga()
    keep = saga.covenant("cov1")
    keys = [f.key for f in tribunal_forms.package_fields(saga, keep)]
    assert not any(k.startswith("package_rhine_aedile") for k in keys)
    assert "package_transylvania_aedile_0" in keys


def test_a_save_that_gave_an_oppidum_a_class_gives_it_to_its_magi():
    saga, rhine = _transylvanian()
    tribunal_packages.data(rhine, tr.KEY)["classes"] = {
        "cov1": "Hospites",
        "cov_sketch": "Foederati",
    }
    tr.members(saga, rhine).append({"character_id": "mag_sketch"})
    found = tr.members(saga, rhine)
    assert "classes" not in rhine.package_data[tr.KEY]
    assert {m["character_id"]: m.get("privilege") for m in found} == {
        "mag_sketch": None,
        "mag1": "hospites",
    }


# -- the Praeco's purse and the Curantis (Against the Dark pp. 19, 97) --


def _values(form: Form, **changes: Any) -> dict[str, Any]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form: Any, **changes: Any) -> Any:
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def _problem(form: Form, **changes: Any) -> str:
    assert form.validate is not None
    return form.validate(_values(form, **changes)) or ""


def _step_form(saga: Saga, tribunal: Tribunal, key: str) -> Form:
    """The meeting opened (its roll call held), then `key`'s form."""
    if tribunal.meeting is None:
        _save(meeting.hold(saga, tribunal))
    record = tribunal.meeting
    assert record is not None
    step = next(s for s in meeting.steps(tribunal, record) if s.key == key)
    return meeting.step_form(saga, tribunal, step)


def _rows(tribunal: Tribunal, kind: str) -> list[TreasuryEntry]:
    return [e for e in tribunal.treasury if e.kind == kind]


def test_its_meetings_hold_the_praeco_s_purse_and_the_curantis():
    saga, rhine = _transylvanian()
    titles = [s.title for s in meeting.steps(rhine, meeting.record(saga, rhine))]
    i = titles.index("The Praeco's purse")
    assert titles[i + 1] == "The Curantis and his Notary"
    assert titles[i + 2] == "Rulings and fines"


def _treasury_add(tribunal: Tribunal) -> Any:
    ops = tribunal_forms.treasury_ops(tribunal)
    assert ops.add is not None
    return ops.add()


def test_only_its_treasury_takes_levies_and_promissory_notes():
    _saga, rhine = _transylvanian()
    add = _treasury_add(rhine)
    assert isinstance(add, Choose)
    offered = [c.value for c in add.choices()]
    assert offered[-2:] == ["levy", "note"]
    note = add.apply("note")
    assert isinstance(note, Form)
    labels = [f.label for f in note.fields()]
    assert "Held by" in labels and "Redeemed" in labels
    rhine.package = "rhine"
    add = _treasury_add(rhine)
    assert isinstance(add, Choose)
    assert "levy" not in [c.value for c in add.choices()]


def test_levies_count_once_paid_and_notes_once_redeemed():
    _saga, rhine = _transylvanian()
    rhine.treasury = [
        TreasuryEntry("vis", 10, art="Vim"),
        TreasuryEntry(LEVY, 3, art="Vim", who="Keep"),
        TreasuryEntry(NOTE, 4, art="Vim", who="Old Histria"),
    ]
    assert treasury.balance(rhine) == {"Vim": 10}
    lines = dict(tribunal_sheet.balance_lines(rhine))
    assert lines["Levies unpaid"] == "3 pawns of Vim"
    assert lines["Notes outstanding"] == "4 pawns of Vim"
    grid = tribunal_sheet.treasury_grid(rhine)
    assert [row[3] for row in grid.rows[1:]] == ["unpaid", "outstanding"]
    rhine.treasury[1].paid = rhine.treasury[2].paid = True
    assert treasury.balance(rhine) == {"Vim": 9}
    # A Tribunal with neither shows no lines for them.
    rhine.treasury = rhine.treasury[:1]
    assert "Levies unpaid" not in dict(tribunal_sheet.balance_lines(rhine))


def test_the_praeco_levies_the_oppida_and_issues_a_note():
    saga, rhine = _transylvanian()
    old = TreasuryEntry(NOTE, 4, art="Vim", who="Old Histria", note="An old note")
    rhine.treasury = [old]
    tr.members(saga, rhine).append({"character_id": "mag1", "privilege": "cives"})
    form = _step_form(saga, rhine, "praeco_purse")
    hints = {f.key: f.hint for f in form.fields()}
    assert hints["levy_cov1"] == (
        "1 of its magi belong to the cives, socii or coloniae, whose covenants owe aid."
    )
    assert _problem(form, levy_cov1=-1) == "An amount can't be fewer than none."
    _save(
        form,
        projects="A Mercere Portal from Old Histria to Venice",
        art="Vim",
        levy_cov1=3,
        levy_cov_sketch=2,
        source=6,
        source_art="Corpus",
        note_holder="Harco",
        note_pawns=5,
        note_art="Vim",
    )
    levies = _rows(rhine, LEVY)
    assert [(e.who, e.amount, e.paid) for e in levies] == [
        ("Keep", 3, False),
        ("Fengheld", 2, False),
    ]
    assert treasury.balance(rhine) == {"Corpus": 6, "Vim": 5}
    assert tr.projects(rhine) == "A Mercere Portal from Old Histria to Venice"
    minutes = rhine.diary[-1].details
    assert "Levies (owed): Keep 3 pawns of Vim, Fengheld 2 pawns of Vim" in minutes
    assert "A promissory note issued to Harco, for 5 pawns of Vim" in minutes
    # Held again, it makes its rows afresh, and redeems the old note.
    again = _step_form(saga, rhine, "praeco_purse")
    _save(again, levy_cov_sketch=None, note_holder="", **{f"redeem_{old.id}": True})
    assert [e.who for e in _rows(rhine, LEVY)] == ["Keep"]
    assert _rows(rhine, NOTE) == [old] and old.paid
    assert treasury.balance(rhine) == {"Corpus": 6, "Vim": -4}
    assert "Redeemed: Old Histria's note of 4 pawns of Vim" in rhine.diary[-1].details


def test_no_levy_reaches_an_oppidum_of_hospites():
    saga, rhine = _transylvanian()
    tr.members(saga, rhine).append({"character_id": "mag1", "privilege": "hospites"})
    form = _step_form(saga, rhine, "praeco_purse")
    hints = {f.key: f.hint for f in form.fields()}
    assert "all hospites" in hints["levy_cov1"]
    assert "hospites" in _problem(form, levy_cov1=2)


def test_the_curantis_serves_one_term_with_his_notary_and_salary():
    saga, rhine = _transylvanian()
    rhine.treasury = []
    form = _step_form(saga, rhine, "curantis")
    assert _problem(form, curantis="mag1", notary="mag1") == (
        "The Curantis can't be his own Notary."
    )
    _save(form, curantis="mag1", notary="mag_sketch", salary=8, salary_art="Corpus")
    assert tr.curantes(rhine)[-1]["character_id"] == "mag1"
    assert [(e.amount, e.art) for e in rhine.treasury] == [(-8, "Corpus")]
    tr.members(saga, rhine).extend(
        [{"character_id": "mag1"}, {"character_id": "mag_sketch"}]
    )
    assert tr.offices(saga, rhine, tr.entry_of(saga, rhine, "mag1") or {}) == "Curantis"
    notary = tr.entry_of(saga, rhine, "mag_sketch") or {}
    assert tr.offices(saga, rhine, notary) == "Praeco, Curantis's Notary"
    assert "Leandro was appointed Curantis, with Severinus as his Notary" in (
        rhine.diary[-1].details
    )
    # Held again, the salary isn't paid twice.
    _save(_step_form(saga, rhine, "curantis"), curantis="mag1", salary=8)
    assert len(rhine.treasury) == 1 and len(tr.curantes(rhine)) == 1
    # At the next meeting he may not be appointed again.
    rhine.meeting = None
    rhine.next_year = 1235
    form = _step_form(saga, rhine, "curantis")
    assert "two terms running" in _problem(form, curantis="mag1")
    _save(form, built=False, curantis="mag_sketch", notary=None, salary=None)
    assert tr.curantes(rhine)[0]["built"] is False
    assert "Leandro built no new zenodochium in his term" in rhine.diary[-1].details


def test_a_colona_may_not_be_curantis():
    saga, rhine = _transylvanian()
    tr.members(saga, rhine).append({"character_id": "mag1", "privilege": "coloniae"})
    form = _step_form(saga, rhine, "curantis")
    assert "no office but aedile" in _problem(form, curantis="mag1")
