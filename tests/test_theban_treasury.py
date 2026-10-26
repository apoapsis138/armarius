"""The Theban meeting's Apprentice Presentation, the conduct of archai
and the common vis sources; the treasury's interest-free loans of vis;
and the Byzantine coins (The Sundered Eagle pp. 28-35, 44-45)."""

from __future__ import annotations

import random
from fractions import Fraction

import pytest
from support import everything_saga

from ars_magica_manager import coinage, meeting, theban_meeting
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.models import Character, Covenant, Saga
from ars_magica_manager.sheets import tribunal as tribunal_sheet
from ars_magica_manager.tribunal_packages import theban


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _problem(form: Form, **changes):
    values = _values(form, **changes)
    return form.validate(values) if form.validate else None


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    form.apply(values)


@pytest.fixture(autouse=True)
def _seeded(monkeypatch):
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(7))


def _polity(saga: Saga, per_phyle: int = 2):
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
                    id=f"{cid}_{n}", name=f"{phyle} {n}", type="magus", covenant_id=cid
                )
            )
    _save(meeting.hold(saga, thebes))
    return thebes


def _step(tribunal, key: str):
    return next(s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == key)


def _form(saga, tribunal, key: str) -> Form:
    return meeting.step_form(saga, tribunal, _step(tribunal, key))


def _hold(saga, tribunal, key: str, **changes):
    _save(_form(saga, tribunal, key), **changes)


def _tokens(tribunal, ident: str, tokens: int = 0, shards: int = 0) -> dict:
    entry = theban_meeting.entry_of(tribunal, ident, create=True)
    assert entry is not None
    entry.update(tokens=tokens, shards=shards)
    return entry


def _count(tribunal, ident: str, key: str) -> int:
    return int((theban_meeting.entry_of(tribunal, ident) or {}).get(key) or 0)


# -- the order of business --


def test_the_new_steps_take_their_places_in_the_books_order():
    saga = everything_saga()
    thebes = _polity(saga)
    keys = [s.key for s in meeting.steps(thebes, thebes.meeting)]
    assert (
        keys.index("assembly")
        < keys.index("apprentice_presentation")
        < keys.index("ostrakismos")
    )
    at = keys.index("sentences")
    assert keys[at : at + 4] == [
        "sentences",
        "conduct_of_archai",
        "common_vis",
        "end_of_term",
    ]


# -- the Apprentice Presentation --


def test_a_child_bid_for_by_one_magus_is_his_and_keeps_his_tokens():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=3)
    _tokens(thebes, "cov_aegean_0", tokens=1)
    before = len(saga.characters)
    _hold(
        saga,
        thebes,
        "apprentice_presentation",
        child_0="Eirene",
        age_0=8,
        found_0="cov_aegean_0",
        bidder_0_0="cov_ionian_0",
        tokens_0_0=2,
    )
    assert _count(thebes, "cov_ionian_0", "tokens") == 1
    # Delivering the child earned a token.
    assert _count(thebes, "cov_aegean_0", "tokens") == 2
    child = saga.characters[before]
    assert child.name == "Eirene" and child.covenant_id == "cov_ionian"
    assert child.hermetic.parens == "Ionian 0"
    assert "keeps 2 tokens" in child.summary
    assert theban_meeting.apprentices(thebes)[-1]["tokens"] == 2


def test_the_child_goes_to_the_most_generous_and_the_others_keep_their_tokens():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=3)
    _tokens(thebes, "cov_kretan_0", tokens=3)
    _hold(
        saga,
        thebes,
        "apprentice_presentation",
        child_0="Nikon",
        bidder_0_0="cov_ionian_0",
        tokens_0_0=1,
        bidder_0_1="cov_kretan_0",
        tokens_0_1=2,
    )
    assert _count(thebes, "cov_kretan_0", "tokens") == 1
    assert _count(thebes, "cov_ionian_0", "tokens") == 3
    given = thebes.meeting["theban"]["presentation"][0]
    assert given["master_id"] == "cov_kretan_0"


def test_she_may_choose_a_lesser_bidder_but_not_one_who_gave_nothing():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=3)
    _tokens(thebes, "cov_kretan_0", tokens=3)
    bids = {
        "child_0": "Nikon",
        "bidder_0_0": "cov_ionian_0",
        "tokens_0_0": 1,
        "bidder_0_1": "cov_kretan_0",
        "tokens_0_1": 2,
    }
    form = _form(saga, thebes, "apprentice_presentation")
    assert _problem(form, **bids, master_0="cov_aegean_0")
    _save(form, **bids, master_0="cov_ionian_0")
    assert _count(thebes, "cov_ionian_0", "tokens") == 2


def test_a_magus_with_a_shard_may_not_bid_unless_bonisagus():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=2, shards=1)
    _tokens(thebes, "cov_ionian_1", tokens=2, shards=1)
    bonisagus = saga.character("cov_ionian_1")
    assert bonisagus is not None
    bonisagus.hermetic.house = theban_meeting.BONISAGUS
    may = {m.id for m in theban_meeting.bidders(saga, thebes, 1225)}
    assert "cov_ionian_0" not in may and "cov_ionian_1" in may


def test_a_bonisagus_may_claim_any_child_without_bidding():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_kretan_0", tokens=3)
    _tokens(thebes, "cov_ionian_1", shards=2)
    bonisagus = saga.character("cov_ionian_1")
    assert bonisagus is not None
    bonisagus.hermetic.house = theban_meeting.BONISAGUS
    assert "cov_ionian_1" in {m.id for m in theban_meeting.claimants(saga, thebes)}
    form = _form(saga, thebes, "apprentice_presentation")
    bids = {
        "child_0": "Nikon",
        "bidder_0_0": "cov_kretan_0",
        "tokens_0_0": 3,
        "claim_0": "cov_ionian_1",
    }
    # Her choice of a bidder doesn't override the claim.
    assert _problem(form, **bids, master_0="cov_kretan_0")
    _save(form, **bids)
    given = thebes.meeting["theban"]["presentation"][0]
    assert given["master_id"] == "cov_ionian_1" and given["claimed"]
    # The unsuccessful bidder keeps his tokens; the claimant gave none.
    assert _count(thebes, "cov_kretan_0", "tokens") == 3
    assert given["tokens"] == 0
    words, _ = _step(thebes, "apprentice_presentation").minutes(
        saga, thebes, thebes.meeting
    )
    assert "Nikon to Ionian 1, claimed by the Oath" in words


def test_a_bonisagus_who_bids_without_claiming_is_one_bidder_among_others():
    found = theban_meeting.presented_master(
        [("cov_kretan_0", 3), ("cov_ionian_1", 1)], None
    )
    assert found == "cov_kretan_0"
    claimed = theban_meeting.presented_master(
        [("cov_kretan_0", 3), ("cov_ionian_1", 1)], "cov_kretan_0", "cov_ionian_1"
    )
    assert claimed == "cov_ionian_1"


def test_no_claim_field_without_a_bonisagus():
    saga = everything_saga()
    thebes = _polity(saga)
    for magus in theban_meeting.tribunal_magi(saga, thebes):
        magus.hermetic.house = None
    form = _form(saga, thebes, "apprentice_presentation")
    assert not any(f.key.startswith("claim_") for f in form.fields())


def test_a_magus_cannot_give_more_tokens_than_he_holds():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=2)
    form = _form(saga, thebes, "apprentice_presentation")
    problem = _problem(
        form,
        child_0="A",
        bidder_0_0="cov_ionian_0",
        tokens_0_0=2,
        child_1="B",
        bidder_1_0="cov_ionian_0",
        tokens_1_0=1,
    )
    assert problem and "holds 2" in problem


def test_a_child_given_no_tokens_may_be_claimed_by_anyone():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", shards=2)
    _hold(
        saga, thebes, "apprentice_presentation", child_0="Zoe", master_0="cov_ionian_0"
    )
    assert thebes.meeting["theban"]["presentation"][0]["master_id"] == "cov_ionian_0"


def test_the_presentation_is_given_once():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=2)
    _hold(
        saga,
        thebes,
        "apprentice_presentation",
        child_0="Zoe",
        bidder_0_0="cov_ionian_0",
        tokens_0_0=1,
    )
    count = len(saga.characters)
    form = _form(saga, thebes, "apprentice_presentation")
    assert any(f.key == "given" for f in form.fields())
    _save(form)
    assert len(saga.characters) == count
    assert _count(thebes, "cov_ionian_0", "tokens") == 1
    words, margin = _step(thebes, "apprentice_presentation").minutes(
        saga, thebes, thebes.meeting
    )
    assert "Zoe to Ionian 0, keeping 1 token" in words and margin == "1 apprentice"


# -- the conduct of archai --


def _with_archai(saga, thebes):
    theban.archai(thebes).extend(
        [
            {"office": "Arche (Ionian)", "holder_id": "cov_ionian_0"},
            {"office": "Polemarch", "holder_id": "cov_kretan_0"},
        ]
    )


def test_the_archai_the_archon_and_the_polemarch_are_scrutinised():
    saga = everything_saga()
    thebes = _polity(saga)
    theban.archai(thebes).clear()
    _with_archai(saga, thebes)
    theban.archai(thebes).append({"office": "Archon", "holder_id": "cov_aegean_0"})
    theban.archai(thebes).append({"office": "Logothete", "holder_id": "cov_aegean_1"})
    ids = [m.id for m in theban_meeting.scrutinised(saga, thebes)]
    assert ids == ["cov_ionian_0", "cov_kretan_0", "cov_aegean_0"]


def test_an_upheld_complaint_fines_the_shards_proposed_and_holding_again_undoes():
    saga = everything_saga()
    thebes = _polity(saga)
    _with_archai(saga, thebes)
    _hold(
        saga,
        thebes,
        "conduct_of_archai",
        against_0="cov_ionian_0",
        by_0="cov_aegean_0",
        fault_0="Indolence",
        fine_0=3,
    )
    assert _count(thebes, "cov_ionian_0", "shards") == 3
    words, margin = _step(thebes, "conduct_of_archai").minutes(
        saga, thebes, thebes.meeting
    )
    assert "upheld, and 3 shards given" in words and margin == "3 shards"
    _hold(
        saga,
        thebes,
        "conduct_of_archai",
        against_0="cov_ionian_0",
        fine_0=3,
        outcome_0=theban_meeting.FINE_REJECTED,
    )
    assert _count(thebes, "cov_ionian_0", "shards") == 0


def test_a_fine_is_of_one_to_seven_shards():
    saga = everything_saga()
    thebes = _polity(saga)
    _with_archai(saga, thebes)
    form = _form(saga, thebes, "conduct_of_archai")
    assert _problem(form, against_0="cov_kretan_0", fine_0=8)
    assert _problem(form, against_0="cov_kretan_0", fine_0=0)
    assert _problem(form, against_0="cov_kretan_0", fine_0=7) is None
    assert _problem(form, against_0="cov_kretan_0", by_0="cov_kretan_0", fine_0=1)


# -- the common vis sources --


def test_gathering_a_common_source_earns_a_token_and_fills_the_coffers():
    saga = everything_saga()
    thebes = _polity(saga)
    rows = len(thebes.treasury)
    _hold(
        saga,
        thebes,
        "common_vis",
        source_0="The spring of Apollon",
        art_0="Creo",
        gatherer_0="cov_ionian_0",
        pawns_0=30,
        source_1="The Kretan cave",
        art_1="Vim",
        gatherer_1="cov_kretan_0",
        pawns_1=10,
        neglected_1=True,
    )
    assert _count(thebes, "cov_ionian_0", "tokens") == 1
    assert _count(thebes, "cov_kretan_0", "shards") == 1
    assert _count(thebes, "cov_kretan_0", "tokens") == 0
    assert len(thebes.treasury) == rows + 1
    assert tribunal_sheet.balance(thebes)["Creo"] == 30
    assert [s["name"] for s in theban_meeting.common_sources(thebes)] == [
        "The spring of Apollon",
        "The Kretan cave",
    ]
    # Holding it again undoes the first holding before doing it anew, and
    # the sources come back as last gathered.
    form = _form(saga, thebes, "common_vis")
    values = _values(form)
    assert values["source_0"] == "The spring of Apollon"
    assert values["gatherer_0"] == "cov_ionian_0"
    _save(form, neglected_1=False)
    assert _count(thebes, "cov_ionian_0", "tokens") == 1
    assert _count(thebes, "cov_kretan_0", "shards") == 0
    assert _count(thebes, "cov_kretan_0", "tokens") == 1
    assert tribunal_sheet.balance(thebes)["Vim"] == 10


# -- loans of vis --


def test_a_polites_borrows_vis_without_interest():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    row = 0  # mag1, a polites
    form = theban.lend_step(saga, thebes, row)
    assert isinstance(form, Form)
    magus = saga.character("mag1")
    assert magus is not None
    had = magus.raw_vis.get("creo", 0)
    _save(form, art="Creo", pawns=4, plan="a pawn a year")
    loan = thebes.treasury[-1]
    assert (loan.kind, loan.amount, loan.art, loan.who) == (
        "loan",
        4,
        "Creo",
        magus.name,
    )
    assert "interest-free" in loan.note and "a pawn a year" in loan.note
    assert magus.raw_vis["creo"] == had + 4
    assert theban.loans_of(saga, thebes, "mag1") == [loan]
    # Repaid as lent, from his own vis.
    repay = theban.repay_step(saga, thebes, row)
    assert isinstance(repay, Form)
    _save(repay)
    assert loan.paid and magus.raw_vis.get("creo", 0) == had
    assert isinstance(theban.repay_step(saga, thebes, row), Refuse)


def test_a_large_loan_not_for_an_emergency_needs_the_assembly():
    form = {"pawns": theban.LARGE_LOAN + 1}
    assert theban.lend_problem(form)
    assert theban.lend_problem({**form, "assembly": True}) is None
    assert theban.lend_problem({**form, "emergency": True}) is None
    assert theban.lend_problem({"pawns": 0})


def test_a_metoikos_or_the_ostracised_may_not_borrow():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    # mag_sketch is ostracised to 1225.
    saga.current_year = 1222
    assert isinstance(theban.lend_step(saga, thebes, 1), Refuse)


def test_a_loan_can_only_be_repaid_from_vis_he_has():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    _save(theban.lend_step(saga, thebes, 0), art="Vim", pawns=5, into_vis=False)
    magus = saga.character("mag1")
    assert magus is not None
    magus.raw_vis.pop("vim", None)
    repay = theban.repay_step(saga, thebes, 0)
    assert isinstance(repay, Form)
    assert _problem(repay)
    assert _problem(repay, from_vis=False) is None


# -- coinage --


def test_the_byzantine_coins_are_worth_what_the_book_says():
    assert coinage.HYPERPYRON.pence == 40
    assert coinage.ASPRON.pence * 3 == coinage.HYPERPYRON.pence
    assert coinage.BILLON.pence < 1  # slightly less than a penny
    assert coinage.TETARTERON.pence * 18 == coinage.BILLON.pence
    assert coinage.worth(coinage.HYPERPYRON, coinage.GROSSO) == 20
    assert coinage.worth(coinage.HYPERPYRON, coinage.TETARTERON) == Fraction(864)


def test_a_sum_is_told_in_coins():
    assert coinage.pounds_in_coins(12) == "72 hyperpyra"
    assert coinage.in_coins(40 + 40 / 3 + 2 * coinage.BILLON.pence) == (
        "1 hyperpyron, 1 aspron and 2 billons"
    )
    assert coinage.in_coins(0) == "no coin"
    assert coinage.in_coins(10, (coinage.GROSSO,)) == "5 grossos"


def test_the_theban_treasury_shows_its_silver_in_hyperpyra():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    thebes.treasury.append(theban.TreasuryEntry("silver", 2))
    lines = dict(tribunal_sheet.balance_lines(thebes))
    assert lines["Silver in hand"] == "2 pounds (12 hyperpyra)"
    core = saga.tribunals[0]
    assert "hyperpyra" not in dict(tribunal_sheet.balance_lines(core))["Silver in hand"]
