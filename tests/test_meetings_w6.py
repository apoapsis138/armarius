"""Meeting rules from the Tribunal books: Normandy's Library of the
Tribunal (The Lion and the Lily pp. 22-23), Provence's residency (Faith &
Flame p. 22), and the debate rules every Tribunal uses (Houses of Hermes:
Societates pp. 91-93): a proposal's cost at the Grand Tribunal and its
recommendation there, the Power of Truth, the whole Tribunal questioning
a proposer, and certamen in a debate's place."""

from __future__ import annotations

import random
from dataclasses import replace

from support import everything_saga

from ars_magica_manager import meeting, normandy_meeting, tribunal_packages
from ars_magica_manager.commands import Form, Then
from ars_magica_manager.models import Book, Character, Covenant, Saga, Tribunal
from ars_magica_manager.models.traits import ScoredTrait
from ars_magica_manager.rules import debate
from ars_magica_manager.tribunal_packages import normandy, provence


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None, form.validate(values)
    return form.apply(values)


def _step(tribunal: Tribunal, key: str) -> meeting.Step:
    assert tribunal.meeting is not None
    return next(s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == key)


def _form(saga: Saga, tribunal: Tribunal, key: str) -> Form:
    form = meeting.step_form(saga, tribunal, _step(tribunal, key))
    assert isinstance(form, Form)
    return form


def _open(saga: Saga, tribunal: Tribunal) -> Tribunal:
    """The roll called, so the meeting is being held."""
    _save(meeting.hold(saga, tribunal))
    return tribunal


def _rhine(saga: Saga) -> Tribunal:
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return _open(saga, tribunal)


# -- HoH: Societates pp. 91-93 --


def test_a_proposal_at_the_grand_tribunal_costs_one_more():
    assert debate.proposal_penalty("Clarification") == 0
    assert debate.proposal_penalty("Addition") == -1
    assert debate.proposal_penalty("Alteration", debate.AT_GRAND) == -4
    assert debate.proposal_penalty("Addition", debate.RECOMMENDED) == -1


def test_the_forum_counts_in_a_motions_strength():
    saga = everything_saga()
    rhine = _rhine(saga)
    motion = rhine.cases[1]
    form = _form(saga, rhine, f"case:{motion.id}")
    assert {f.key for f in form.fields()} >= {"forum", "thesis_prosecutor"}
    _save(
        form,
        prosecutor="mag1",
        defender="mag_sketch",
        proposal="Addition",
        forum=debate.AT_GRAND,
        lost_for=0,
        lost_against=4,
    )
    assert meeting.strength(rhine.meeting, motion) == (meeting.FOR, 2)


def test_a_recommended_motion_names_the_next_grand_tribunal():
    assert meeting.next_grand_tribunal(1220) == 1228
    assert meeting.next_grand_tribunal(1228) == 1261
    saga = everything_saga()
    rhine = _rhine(saga)
    motion = rhine.cases[1]
    _save(
        _form(saga, rhine, f"case:{motion.id}"),
        prosecutor="mag1",
        defender="mag_sketch",
        forum=debate.RECOMMENDED,
        lost_for=0,
        lost_against=2,
    )
    assert rhine.meeting is not None
    year = int(rhine.meeting.get("year") or saga.current_year)
    assert (
        f"recommended to the Grand Tribunal of {meeting.next_grand_tribunal(year)}"
        in rhine.diary[-1].details
    )


def test_certamen_in_the_debates_place_binds_the_case_with_no_vote():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    # A personal charge between two magi, naming no violation of the Code.
    magi = [c.name for c in saga.characters if c.type == "magus"]
    case.kind, case.brought_by, case.against = "charge", magi[0], magi[1]
    case.charge = "A slight to his honour at the last meeting"
    form = _form(saga, rhine, f"case:{case.id}")
    asked = form.validate(_values(form, heard_by=debate.BY_CERTAMEN))
    assert asked == "Say who won the certamen."
    following = _save(form, heard_by=debate.BY_CERTAMEN, certamen=meeting.AGAINST)
    assert meeting.certamen_winner(rhine.meeting, case) == meeting.AGAINST
    keys = [s.key for s in meeting.steps(rhine, rhine.meeting)]
    assert f"vote:{case.id}" not in keys
    assert isinstance(following, Then)
    assert "decided by certamen" in rhine.diary[-1].details
    rulings = _form(saga, rhine, "rulings")
    assert _values(rulings)[f"outcome_{case.id}"] == (
        "Decided by certamen for the defence."
    )
    # Heard again by debate, it has its vote back.
    _save(
        _form(saga, rhine, f"case:{case.id}"),
        heard_by=debate.BY_DEBATE,
        prosecutor="mag1",
        defender="mag_sketch",
        lost_for=0,
        lost_against=1,
    )
    keys = [s.key for s in meeting.steps(rhine, rhine.meeting)]
    assert f"vote:{case.id}" in keys


def test_certamen_on_one_point_needs_its_levels():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    form = _form(saga, rhine, f"case:{case.id}")
    assert "Fatigue levels" in (form.validate(_values(form, heard_by="point")) or "")
    _save(form, heard_by=debate.ON_A_POINT, lost_for=1, lost_against=4)
    assert meeting.strength(rhine.meeting, case) == (meeting.FOR, 3)


def test_a_flawed_thesis_starts_levels_down():
    able = debate.skilled("Able", debate.ABLE)
    flawed = debate.arguing(able, "flawed_2", None)
    assert flawed.handicap == 2
    held = debate.run((flawed, able), ([], []), 1, random.Random(1))
    assert held.lost[0] >= 2
    beaten = debate.run(
        (debate.arguing(able, "flawed_3", None), able), ([], []), 0, random.Random(1)
    )
    assert beaten.lost[0] >= 3
    knocked = replace(able, handicap=5)
    assert debate.run((knocked, able), ([], []), 5, random.Random(1)).rounds == 0


def test_arguing_a_known_falsehood_costs_the_truthful_trait():
    magus = Character(id="m", name="Honest", type="magus")
    magus.personality_traits.append(ScoredTrait("Truthful", 3))
    assert debate.truthful(magus) == 3
    assert debate.truthful(None) == 0
    side = debate.arguing(debate.skilled("Honest"), debate.KNOWN_FALSE, magus)
    assert side.falsehood == 3
    liar = Character(id="l", name="Liar", type="magus")
    liar.personality_traits.append(ScoredTrait("Deceitful", 3))
    assert debate.arguing(debate.skilled("Liar"), debate.KNOWN_FALSE, liar) == (
        debate.skilled("Liar")
    )
    # A great penalty to Defence makes every attack land.
    plain = debate.skilled("Plain", debate.ABLE)
    lying = replace(plain, falsehood=60)
    held = debate.run((plain, lying), ([], []), 3, random.Random(2))
    assert held.lost[1] == debate.KNOCKED_OUT


def test_the_whole_tribunal_questions_a_proposer_in_turn():
    # No one can be worn down, so every round is debated.
    panel = [
        replace(debate.skilled(name), resistance=99) for name in ("Ana", "Bero", "Cass")
    ]
    held = debate.run(
        (
            replace(debate.skilled("Proposer"), resistance=99),
            debate.skilled("The Tribunal"),
        ),
        ([], []),
        3,
        random.Random(3),
        panel=panel,
    )
    for number, name in enumerate(("Ana", "Bero", "Cass"), start=1):
        assert any(
            line.startswith(f"Round {number}:") and name in line for line in held.lines
        )
    assert not any("The Tribunal" in line for line in held.lines)


def test_a_motion_the_tribunal_opposes_is_questioned_by_those_present(monkeypatch):
    saga = everything_saga()
    rhine = _rhine(saga)
    motion = rhine.cases[1]
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(5))
    _save(
        _form(saga, rhine, f"case:{motion.id}"),
        prosecutor="mag1",
        defender=meeting.THE_TRIBUNAL,
        rounds=4,
    )
    lines = rhine.meeting["debates"][motion.id]["lines"]
    assert lines and not any("The Tribunal" in line for line in lines)
    others = [m.name for m, _c in meeting.magi_present(saga, rhine, rhine.meeting)]
    others = [name for name in others if name != "Leandro"]
    assert any(name in line for line in lines for name in others)


# -- Normandy: the Library of the Tribunal (L&L pp. 22-23) --


def _normandy(saga: Saga) -> tuple[Tribunal, Character, Book, Book, Book]:
    tribunal = saga.tribunal("normandy")
    assert tribunal is not None
    for cid, name in (("confluensis", "Confluensis"), ("cunfin", "Cunfin")):
        saga.covenants.append(
            Covenant(id=cid, saga_id=saga.id, name=name, tribunal_id="normandy")
        )
    author = Character(id="perp", name="Perpauca", type="magus", covenant_id="cunfin")
    saga.characters.append(author)
    held = f"{normandy.LIBRARY_HELD}. A sample."
    cheap = Book(
        "lib_cheap",
        "The Peril of Phoebos",
        "Tractatus",
        art="Ignem",
        quality=11,
        description=held,
        owner_kind="covenant",
        owner_id="confluensis",
    )
    dear = Book(
        "lib_dear",
        "De Lapii",
        "Art Summa",
        art="Terram",
        level=17,
        quality=14,
        description=held,
        owner_kind="covenant",
        owner_id="confluensis",
    )
    written = Book(
        "own",
        "Mirrors Within",
        "Art Summa",
        art="Imaginem",
        level=6,
        quality=10,
        author="Perpauca",
        author_id="perp",
        owner_kind="character",
        owner_id="perp",
    )
    saga.books += [cheap, dear, written]
    return tribunal, author, cheap, dear, written


def test_the_library_step_comes_before_the_tourney():
    saga = everything_saga()
    tribunal, *_rest = _normandy(saga)
    _open(saga, tribunal)
    keys = [s.key for s in meeting.steps(tribunal, tribunal.meeting)]
    assert keys.index("library") < keys.index("tourney") < keys.index("rulings")
    assert _step(tribunal, "library").title == "The Library of the Tribunal"


def test_the_librarys_books_and_keeper():
    saga = everything_saga()
    tribunal, _author, cheap, dear, written = _normandy(saga)
    assert normandy.library_books(saga, tribunal) == [cheap, dear]
    keeper = normandy.keeper(saga, tribunal)
    assert keeper is not None and keeper.id == "confluensis"
    assert normandy.worth(saga, dear) == 31
    assert normandy.worth(saga, written) == 16
    assert [b for b, _m in normandy_meeting.giftable(saga, tribunal)] == [written]


def test_a_gift_wins_its_giver_a_book_worth_no_more():
    saga = everything_saga()
    tribunal, author, cheap, dear, written = _normandy(saga)
    _open(saga, tribunal)
    form = _form(saga, tribunal, "library")
    too_dear = form.validate(_values(form, gift_0=written.id, prize_0=dear.id))
    assert "no more Build Points" in (too_dear or "")
    twice = form.validate(
        _values(
            form, gift_0=written.id, prize_0=cheap.id, won_0=cheap.id, winner_0="cunfin"
        )
    )
    assert "certamen" in (twice or "")
    # The Tourney's books are bought with the team's prize pawns (L&L p. 33).
    unranked = form.validate(_values(form, won_0=dear.id, winner_0="cunfin"))
    assert "no result at this year's Tourney" in (unranked or "")
    year = int(tribunal.meeting.get("year") or saga.current_year)
    normandy.tourney(tribunal).append({"year": year, "team": "Cunfin", "points": 40})
    form = _form(saga, tribunal, "library")
    _save(form, gift_0=written.id, prize_0=cheap.id, won_0=dear.id, winner_0="cunfin")
    assert (written.owner_kind, written.owner_id) == ("covenant", "confluensis")
    assert written in normandy.library_books(saga, tribunal)
    year = int(tribunal.meeting.get("year") or saga.current_year)
    leases = normandy.leases(tribunal)
    assert [(e["book_id"], e["covenant_id"], e["how"], e["until"]) for e in leases] == [
        (cheap.id, author.covenant_id, normandy.BY_GIFT, year + 7),
        (dear.id, "cunfin", normandy.BY_TOURNEY, year + 7),
    ]
    assert normandy.available(saga, tribunal) == [written]
    assert "Leased to Cunfin" in tribunal.diary[-1].details
    # The leased book stays the Tribunal's at Confluensis.
    assert (dear.owner_kind, dear.owner_id) == ("covenant", "confluensis")
    # Held again it rewrites, not adds.
    form = _form(saga, tribunal, "library")
    assert _values(form)["gift_0"] == written.id
    _save(form, gift_0=None, won_0=None)
    assert normandy.leases(tribunal) == [] and normandy.gifts(tribunal) == []
    assert (written.owner_kind, written.owner_id) == ("character", "perp")


def test_a_lease_that_is_up_comes_back_before_the_meeting():
    saga = everything_saga()
    tribunal, _author, cheap, _dear, _written = _normandy(saga)
    normandy.leases(tribunal).append(
        {
            "book_id": cheap.id,
            "covenant_id": "cunfin",
            "year": 1213,
            "until": 1220,
            "how": normandy.BY_TOURNEY,
            "returned": None,
        }
    )
    assert cheap not in normandy.available(saga, tribunal)
    _open(saga, tribunal)
    form = _form(saga, tribunal, "library")
    assert _values(form)["return_0"] is True
    _save(form)
    year = int(tribunal.meeting.get("year") or saga.current_year)
    assert normandy.leases(tribunal)[0]["returned"] == year
    assert cheap in normandy.available(saga, tribunal)
    # Held again unticked, it is still out, and noted.
    _save(_form(saga, tribunal, "library"), return_0=False)
    assert normandy.leases(tribunal)[0]["returned"] is None
    assert "Not returned: The Peril of Phoebos" in tribunal.diary[-1].details


# -- Provence: residency (F&F p. 22) --


def _provence(saga: Saga) -> tuple[Tribunal, Character, Character]:
    tribunal = Tribunal(
        id="provence", name="Provençal", next_year=1221, package="provence"
    )
    saga.tribunals.append(tribunal)
    saga.covenants.append(
        Covenant(
            id="solis", saga_id=saga.id, name="Castra Solis", tribunal_id="provence"
        )
    )
    old = Character(id="garus", name="Garus", type="magus", covenant_id="solis")
    new = Character(id="tibaut", name="Tibaut", type="magus", covenant_id="solis")
    saga.characters += [old, new]
    return tribunal, old, new


def test_residency_follows_the_last_three_meetings():
    saga = everything_saga()
    tribunal, old, new = _provence(saga)
    assert provence.residency(tribunal, new)[0]  # nothing recorded: presumed
    provence.meetings(tribunal).extend([1200, 1207, 1214])
    provence.attended(tribunal)["garus"] = [1200]
    assert provence.residency(tribunal, old)[0]
    assert provence.residency(tribunal, new) == (
        False,
        "absent from the last three meetings",
    )
    provence.meetings(tribunal).append(1221)
    assert not provence.residency(tribunal, old)[0]
    new.background.year_born = 1188  # Gauntleted in 1213
    assert provence.residency(tribunal, new) == (
        True,
        "Gauntleted in the Tribunal in 1213",
    )
    provence.registered(tribunal)["garus"] = 1221
    assert provence.residency(tribunal, old)[0]
    provence.departed(tribunal)["garus"] = {"year": 1228, "breach": True}
    resident, why = provence.residency(tribunal, old)
    assert not resident and "without registering" in why
    facts = tribunal_packages.magus_facts(saga, new)
    assert facts == [("Residency", "Resident: Gauntleted in the Tribunal in 1213")]


def test_the_residency_step_records_attendance_and_grants():
    saga = everything_saga()
    tribunal, old, _new = _provence(saga)
    provence.meetings(tribunal).extend([1200, 1207, 1214])
    provence.attended(tribunal)["garus"] = [1214]
    _open(saga, tribunal)
    keys = [s.key for s in meeting.steps(tribunal, tribunal.meeting)]
    assert keys[:3] == ["attendance", "opening", "residency"]
    form = _form(saga, tribunal, "residency")
    fields = {f.key for f in form.fields()}
    assert "grant_tibaut" in fields and "grant_garus" not in fields
    _save(form, grant_tibaut=True)
    year = int(tribunal.meeting.get("year") or saga.current_year)
    assert provence.registered(tribunal) == {"tibaut": year}
    assert year in provence.attended(tribunal)["garus"]
    assert provence.meetings(tribunal)[-1] == year
    assert "Granted residency by vote: Tibaut" in tribunal.diary[-1].details
    # Held again: the newcomer is still offered, and nothing doubles.
    form = _form(saga, tribunal, "residency")
    assert _values(form)["grant_tibaut"] is True
    _save(form, grant_tibaut=False, departed="garus")
    assert provence.registered(tribunal) == {}
    assert provence.meetings(tribunal).count(year) == 1
    assert provence.attended(tribunal)["garus"].count(year) == 1
    assert not provence.residency(tribunal, old)[0]
    form = _form(saga, tribunal, "residency")
    assert "both" in (form.validate(_values(form, breach="garus")) or "")


def test_the_tourneys_books_follow_the_teams_prize_pawns():
    saga = everything_saga()
    tribunal, _author, cheap, dear, written = _normandy(saga)
    _open(saga, tribunal)
    year = int(tribunal.meeting.get("year") or saga.current_year)
    assert normandy.book_pawns(saga, dear) == 7  # 31 Build Points
    # Cunfin ranks 20th of twenty: 1 prize pawn.
    for rank in range(1, 21):
        team = "Cunfin" if rank == 20 else f"Team {rank}"
        normandy.tourney(tribunal).append(
            {"year": year, "team": team, "points": 100 - rank}
        )
    assert normandy.team_pawns(tribunal, year, "Cunfin") == 1
    form = _form(saga, tribunal, "library")
    # As many books as the Library can lease, not a fixed three.
    keys = {f.key for f in form.fields()}
    assert {"won_0", "won_1"} <= keys
    too_many = form.validate(_values(form, won_0=dear.id, winner_0="cunfin"))
    assert "more than the 1 its rank won" in (too_many or "")
    # First place's 31 pawns buy both.
    normandy.tourney(tribunal)[-1]["points"] = 500
    form = _form(saga, tribunal, "library")
    _save(form, won_0=dear.id, winner_0="cunfin", won_1=cheap.id, winner_1="cunfin")
    assert [e["book_id"] for e in normandy.leases(tribunal)] == [dear.id, cheap.id]
    assert written.owner_id == "perp"


def test_certamen_cant_overrule_a_tribunal_or_the_code():
    # DE p. 230; HoH:S p. 92.
    bar = debate.binding_certamen_bar
    assert bar("charge", "an insult", between_magi=True) == ""
    assert "over-rule a Tribunal" in bar("appeal", "an insult", between_magi=True)
    assert "violation of the Code" in bar(
        "charge", "Molesting the faeries", between_magi=True
    )
    assert "personal charge" in bar("charge", "an insult", between_magi=False)
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    case.kind = "appeal"
    form = _form(saga, rhine, f"case:{case.id}")
    heard = next(f for f in form.fields() if f.key == "heard_by")
    assert debate.BY_CERTAMEN not in [key for _label, key in heard.options]
    assert "over-rule a Tribunal" in heard.hint
    refused = form.validate(
        _values(form, heard_by=debate.BY_CERTAMEN, certamen=meeting.FOR)
    )
    assert "over-rule a Tribunal" in (refused or "")
    # Certamen on one point is still offered: it doesn't win the vote.
    assert debate.ON_A_POINT in [key for _label, key in heard.options]
