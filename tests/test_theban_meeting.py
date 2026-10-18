"""The Theban meeting: the Hermetic Assembly's decrees and ostrakismos, and
the Council of Archai's end-of-term tokens, sortition and election of the
archon and polemarch."""

from __future__ import annotations

import random

import pytest
from support import everything_saga

from ars_magica_manager import meeting, theban_meeting
from ars_magica_manager.commands import Form
from ars_magica_manager.models import Character, Covenant, Saga
from ars_magica_manager.tribunal_packages import theban


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    form.apply(values)


@pytest.fixture(autouse=True)
def _seeded(monkeypatch):
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(7))


def _polity(saga: Saga, per_phyle: int = 6):
    """The sample Theban Tribunal with a covenant in each phyle, each with
    `per_phyle` magi, and the Keep (Aegean) moved into it."""
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    for covenant in saga.covenants:
        covenant.tribunal_id = "thebes"
    for phyle in theban.PHYLAI:
        cid = f"cov_{phyle.lower()}"
        saga.covenants.append(
            Covenant(id=cid, saga_id="s", name=f"{phyle} Hall", tribunal_id="thebes")
        )
        theban.phylai(thebes)[cid] = phyle
        for n in range(per_phyle):
            saga.characters.append(
                Character(
                    id=f"{cid}_{n}",
                    name=f"{phyle} {n}",
                    type="magus",
                    covenant_id=cid,
                )
            )
    _save(meeting.hold(saga, thebes))
    return thebes


def _step(tribunal, key: str):
    return next(s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == key)


def _hold(saga, tribunal, key: str, **changes):
    _save(meeting.step_form(saga, tribunal, _step(tribunal, key)), **changes)


def _entry(tribunal, ident):
    return theban_meeting.entry_of(tribunal, ident)


def test_the_four_phases_are_held_in_the_books_order():
    saga = everything_saga()
    thebes = _polity(saga)
    keys = [s.key for s in meeting.steps(thebes, thebes.meeting)]
    assert keys.index("assembly") < keys.index("ostrakismos") < keys.index("rulings")
    at = keys.index("end_of_term")
    assert keys[at : at + 4] == [
        "end_of_term",
        "sortition",
        "archon_polemarch",
        "rulings",
    ]
    titles = [s.title for s in meeting.steps(thebes, thebes.meeting)]
    assert "The Assembly's decrees" in titles and "The sortition" in titles


def test_the_principal_phyle_turns_from_meeting_to_meeting():
    saga = everything_saga()
    thebes = _polity(saga)
    assert theban_meeting.next_principal(thebes) == "Ionian"
    _hold(saga, thebes, "assembly")
    assert theban.data(thebes, theban.KEY)["principal_phyle"] == "Ionian"
    assert theban_meeting.next_principal(thebes) == "Aegean"
    _hold(saga, thebes, "assembly", principal="Kretan")
    assert theban.data(thebes, theban.KEY)["principal_phyle"] == "Kretan"


def test_the_assemblys_decrees_change_status_and_shards():
    saga = everything_saga()
    thebes = _polity(saga)
    theban.magi(thebes).append({"character_id": "cov_ionian_0", "status": "metoikos"})
    theban.magi(thebes).append({"character_id": "cov_kretan_0", "shards": 2})
    labels = [
        f.label
        for f in meeting.step_form(saga, thebes, _step(thebes, "assembly")).fields()
    ]
    assert "Decree of citizenship: Ionian 0" in labels
    assert "Decree of contrition: Kretan 0 (2 shards)" in labels
    _hold(
        saga,
        thebes,
        "assembly",
        citizen_cov_ionian_0=True,
        contrition_cov_kretan_0=True,
        accused="cov_aegean_0",
        accuser="cov_aegean_1",
        verdict="rejected",
    )
    assert _entry(thebes, "cov_ionian_0")["status"] == "polites"
    assert _entry(thebes, "cov_kretan_0")["shards"] == 1
    assert _entry(thebes, "cov_aegean_1")["shards"] == 1
    assert _entry(thebes, "cov_aegean_0") is None
    # Holding it again undoes the first holding before doing it anew.
    _hold(
        saga,
        thebes,
        "assembly",
        citizen_cov_ionian_0=False,
        contrition_cov_kretan_0=False,
        accused="cov_aegean_0",
        verdict="upheld",
    )
    assert _entry(thebes, "cov_aegean_1")["shards"] == 0
    assert _entry(thebes, "cov_aegean_0")["shards"] == 1
    assert _entry(thebes, "cov_kretan_0")["shards"] == 2
    assert _entry(thebes, "cov_ionian_0")["status"] == "metoikos"


def test_a_rejected_defamation_needs_its_accuser():
    saga = everything_saga()
    thebes = _polity(saga)
    form = meeting.step_form(saga, thebes, _step(thebes, "assembly"))
    values = _values(form, accused="cov_aegean_0", verdict="rejected")
    assert form.validate is not None
    assert "accuser" in (form.validate(values) or "")


def test_the_ostrakismos_sends_out_the_one_chosen():
    saga = everything_saga()
    thebes = _polity(saga)
    form = meeting.step_form(saga, thebes, _step(thebes, "ostrakismos"))
    read = next(f.value for f in form.fields() if f.key == "read")
    assert "Leandro (1 shard)" in read
    _hold(saga, thebes, "ostrakismos", ostracised="mag1")
    entry = _entry(thebes, "mag1")
    assert entry["status"] == "metoikos"
    assert (entry["tokens"], entry["shards"]) == (0, 0)
    assert entry["ostracised_until"] == thebes.meeting["year"] + 7
    form = meeting.step_form(saga, thebes, _step(thebes, "assembly"))
    assert not any("Leandro" in f.label for f in form.fields())
    # Counted again for no one, the magus is restored.
    _hold(saga, thebes, "ostrakismos", ostracised=None)
    entry = _entry(thebes, "mag1")
    assert (entry.get("status"), entry["tokens"], entry["shards"]) == (None, 2, 1)
    assert entry.get("ostracised_until") is None


def test_the_outgoing_magistrates_are_paid_once():
    saga = everything_saga()
    thebes = _polity(saga)
    theban.archai(thebes)[1]["holder_id"] = "cov_ionian_5"
    theban.archai(thebes).append(
        {"office": "Arche (Kretan)", "holder_id": "cov_kretan_5"}
    )
    _hold(saga, thebes, "end_of_term")
    assert _entry(thebes, "mag1")["tokens"] == 2 + 3
    assert _entry(thebes, "cov_ionian_5")["tokens"] == 5
    assert _entry(thebes, "cov_kretan_5")["tokens"] == 2
    _hold(saga, thebes, "end_of_term", pay_1=False)
    assert _entry(thebes, "mag1")["tokens"] == 5
    assert _entry(thebes, "cov_ionian_5")["tokens"] == 0


def test_the_sortition_draws_four_from_each_phyle_and_one_may_be_set_aside():
    saga = everything_saga()
    thebes = _polity(saga)
    theban.archai(thebes).append(
        {"office": "Arche (Ionian)", "holder_id": "cov_ionian_0"}
    )
    _hold(saga, thebes, "sortition")
    seated = [o for o in theban.archai(thebes) if theban_meeting.is_arche(o)]
    assert len(seated) == 16
    by_phyle = {p: [o for o in seated if p in o["office"]] for p in theban.PHYLAI}
    assert all(len(found) == 4 for found in by_phyle.values())
    assert "cov_ionian_0" not in {o["holder_id"] for o in seated}
    assert {o["term_ends"] for o in seated} == {meeting._next(thebes, thebes.meeting)}
    out = by_phyle["Kretan"][0]["holder_id"]
    _hold(saga, thebes, "sortition", set_aside=out)
    seated = [o for o in theban.archai(thebes) if theban_meeting.is_arche(o)]
    kretan = [o["holder_id"] for o in seated if "Kretan" in o["office"]]
    assert out not in kretan and len(kretan) == 4
    assert [o["office"] for o in theban.archai(thebes)[:2]] == ["Archon", "Polemarch"]


def test_the_new_archai_elect_the_archon_and_polemarch():
    saga = everything_saga()
    thebes = _polity(saga)
    _hold(saga, thebes, "sortition")
    seated = [
        o["holder_id"] for o in theban.archai(thebes) if theban_meeting.is_arche(o)
    ]
    form = meeting.step_form(saga, thebes, _step(thebes, "archon_polemarch"))
    archon = next(f for f in form.fields() if f.key == "archon")
    assert {value for _, value in archon.options} == set(seated)
    _hold(saga, thebes, "archon_polemarch", archon=seated[3], polemarch="mag1")
    offices = {o["office"]: o["holder_id"] for o in theban.archai(thebes)}
    assert offices["Archon"] == seated[3] and offices["Polemarch"] == "mag1"
    assert thebes.praeco_id == seated[3]
    acta = meeting.acta_text(saga, thebes, thebes.meeting)
    assert "Polemarch" in acta


def test_the_minutes_say_what_the_council_did():
    saga = everything_saga()
    thebes = _polity(saga)
    _hold(saga, thebes, "ostrakismos", ostracised="mag1")
    words, margin = _step(thebes, "ostrakismos").minutes(saga, thebes, thebes.meeting)
    assert "Leandro was ostracised" in words and margin == "Ostracised"
    _hold(saga, thebes, "sortition")
    words, margin = _step(thebes, "sortition").minutes(saga, thebes, thebes.meeting)
    assert words.startswith("By sortition the new archai were drawn")
    assert margin == "16 archai"
