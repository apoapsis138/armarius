"""The three Tribunal books' rules beyond the first reads: The Sundered
Eagle's sentences, refusal shard, boards and Propitiation; Against the
Dark's offices by privilege, aediles and oppida; Guardians of the
Forests' gilds of magi."""

from __future__ import annotations

import random

import pytest
from support import everything_saga

from ars_magica_manager import meeting, theban_meeting, tribunal_packages
from ars_magica_manager.commands import Form
from ars_magica_manager.models import Case, Character, Covenant, Saga
from ars_magica_manager.sheets import tribunal as tribunal_sheet
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
    return thebes


def _begin(saga: Saga, thebes):
    _save(meeting.hold(saga, thebes))


def _step(tribunal, key: str):
    return next(s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == key)


def _hold(saga, tribunal, key: str, **changes):
    _save(meeting.step_form(saga, tribunal, _step(tribunal, key)), **changes)


def _entry(tribunal, ident):
    return theban_meeting.entry_of(tribunal, ident) or {}


# -- The Sundered Eagle --


def test_refusing_to_stand_costs_a_shard_and_another_cause_none():
    saga = everything_saga()
    thebes = _polity(saga)
    _begin(saga, thebes)
    _hold(saga, thebes, "sortition")
    seated = [o for o in theban.archai(thebes) if theban_meeting.is_arche(o)]
    out = seated[0]["holder_id"]
    _hold(saga, thebes, "sortition", set_aside=out, why=theban_meeting.REFUSED)
    assert _entry(thebes, out)["shards"] == 1
    words, _ = _step(thebes, "sortition").minutes(saga, thebes, thebes.meeting)
    assert "refused to stand and was given a shard" in words
    # Held again for another cause, the shard is taken back.
    _hold(saga, thebes, "sortition", set_aside=out, why="other")
    assert _entry(thebes, out)["shards"] == 0


def test_the_boards_take_three_each_and_the_treasury_the_rest():
    saga = everything_saga()
    thebes = _polity(saga)
    _begin(saga, thebes)
    _hold(saga, thebes, "sortition")
    members = theban_meeting.board_members(thebes)
    assert [len(members[b]) for b in theban_meeting.BOARDS] == [3, 3, 3]
    assert len(members[theban_meeting.TREASURY_COUNCIL]) == 7
    duties = [o["duties"] for o in theban.archai(thebes) if theban_meeting.is_arche(o)]
    assert duties.count(theban_meeting.TAMIAS_DUTY) == 1
    assert duties.count(theban_meeting.COLLECTOR_DUTY) == 4
    assert duties.count(theban_meeting.TUTOR_DUTY) == 2
    served = theban_meeting.boards_served(thebes)
    assert len(served) == 9
    # Held again, the same boards, and the history not doubled.
    _hold(saga, thebes, "sortition")
    assert sum(len(b) for b in theban_meeting.boards_served(thebes).values()) == 9


def test_a_veteran_never_sits_on_the_same_board_twice():
    dice = random.Random(3)
    ids = [f"m{n}" for n in range(16)]
    served = {f"m{n}": ["Judicial Board", "Legislative Board"] for n in range(5)}
    phyle = {
        i: ("Ionian", "Aegean", "Kretan", "Propontian")[n % 4]
        for n, i in enumerate(ids)
    }
    duties, redcaps = theban_meeting.assign_boards(ids, served, phyle, dice)
    for n in range(5):
        assert duties[f"m{n}"] not in ("Judicial Board", "Legislative Board")
    # Five veterans can only sit on the Conciliatory Board: three do, two
    # go to the Treasury Council.
    assert sum(duties[f"m{n}"] == "Conciliatory Board" for n in range(5)) == 3
    assert redcaps == {}
    collectors = [i for i, d in duties.items() if d == theban_meeting.COLLECTOR_DUTY]
    assert len({phyle[i] for i in collectors}) == 4


def test_a_board_no_arche_can_fill_is_left_to_redcaps():
    served = {f"m{n}": ["Judicial Board"] for n in range(4)}
    duties, redcaps = theban_meeting.assign_boards(
        [f"m{n}" for n in range(4)], served, {}, random.Random(1)
    )
    assert redcaps["Judicial Board"] == 3
    assert "Judicial Board" not in duties.values()


def test_a_conviction_and_a_defeated_case_give_shards_and_tokens():
    saga = everything_saga()
    thebes = _polity(saga)
    guilty_case = Case(
        "Scrying on Ionian Hall",
        against="Kretan 1",
        brought_by="Ionian 2",
        charge="A High Crime",
    )
    defeated = Case("Theft of vis", against="Aegean 1", brought_by="Aegean 2")
    thebes.cases[:] = [guilty_case, defeated]
    _begin(saga, thebes)
    thebes.meeting.setdefault("votes", {}).update(
        {
            guilty_case.id: {"for": 10, "against": 2},
            defeated.id: {"for": 1, "against": 9},
        }
    )
    form = meeting.step_form(saga, thebes, _step(thebes, "sentences"))
    values = _values(form)
    assert values[f"verdict_{guilty_case.id}"] == theban_meeting.CONVICTED
    assert values[f"crime_{guilty_case.id}"] == "high"
    assert values[f"guilty_{guilty_case.id}"] == "cov_kretan_1"
    assert values[f"verdict_{defeated.id}"] == theban_meeting.EXONERATED
    _hold(saga, thebes, "sentences", **{f"marched_{guilty_case.id}": True})
    assert _entry(thebes, "cov_kretan_1")["shards"] == 3
    assert _entry(thebes, "cov_ionian_2")["tokens"] == 3
    assert _entry(thebes, "cov_aegean_2")["shards"] == 1
    assert _entry(thebes, "cov_aegean_1").get("shards", 0) == 0
    # Held again as a Low Crime with no March: undone, then done anew.
    _hold(
        saga,
        thebes,
        "sentences",
        **{f"crime_{guilty_case.id}": "low", f"marched_{guilty_case.id}": False},
    )
    assert _entry(thebes, "cov_kretan_1")["shards"] == 1
    assert _entry(thebes, "cov_ionian_2")["tokens"] == 1
    assert _entry(thebes, "cov_aegean_2")["shards"] == 1


def test_a_metoikos_is_given_no_shards_for_a_sentence():
    saga = everything_saga()
    thebes = _polity(saga)
    theban.magi(thebes).append({"character_id": "cov_kretan_1", "status": "metoikos"})
    case = Case("A Low Crime", against="Kretan 1")
    thebes.cases[:] = [case]
    _begin(saga, thebes)
    thebes.meeting.setdefault("votes", {})[case.id] = {"for": 5, "against": 1}
    _hold(saga, thebes, "sentences")
    assert _entry(thebes, "cov_kretan_1").get("shards", 0) == 0


@pytest.mark.parametrize(
    ("might", "pawns", "xp"),
    [(25, 10, 20), (25, 0, 0), (25, 1, 2), (10, 5, 25), (40, 3, 0), (0, 1, 25)],
)
def test_a_patron_gains_xp_by_its_might_and_the_pawns_offered(might, pawns, xp):
    assert theban_meeting.patron_xp(might, pawns) == xp


def test_the_propitiation_takes_the_rituals_vis_and_records_each_patron():
    saga = everything_saga()
    thebes = _polity(saga)
    _begin(saga, thebes)
    _hold(saga, thebes, "propitiation", pawns_cov_ionian=10, might_cov_ionian=25)
    held = theban_meeting._record(thebes.meeting)["propitiation"]
    assert held["offerings"]["cov_ionian"]["xp"] == 20
    assert theban_meeting.patrons(thebes)["cov_ionian"]["might"] == 25
    assert tribunal_sheet.balance(thebes).get("Vim") == -8
    # Held again, the Ritual's vis is taken once.
    _hold(saga, thebes, "propitiation", art="Creo")
    balance = tribunal_sheet.balance(thebes)
    assert balance.get("Vim", 0) == 0 and balance.get("Creo") == -8
    words, margin = _step(thebes, "propitiation").minutes(saga, thebes, thebes.meeting)
    assert "Ceremony of Propitiation" in words and margin == "10 pawns offered"


def _tokens(thebes, ident, tokens=0, shards=0, **more):
    entry = {
        "character_id": ident,
        "status": "polites",
        "tokens": tokens,
        "shards": shards,
    }
    entry.update(more)
    theban.magi(thebes).append(entry)
    return entry


def test_a_token_neutralizes_a_shard_of_another_covenant():
    saga = everything_saga()
    thebes = _polity(saga)
    _tokens(thebes, "cov_ionian_0", tokens=2)
    _tokens(thebes, "cov_ionian_1", tokens=1)
    shard = _tokens(thebes, "cov_kretan_0", shards=1)
    problem = theban.neutralize_problem
    assert "own covenant" in (
        problem(saga, thebes, "cov_ionian_0", "cov_ionian_1") or ""
    )
    assert "his own" in (problem(saga, thebes, "cov_kretan_0", "cov_kretan_0") or "")
    assert "no tokens" in (problem(saga, thebes, "cov_aegean_0", "cov_kretan_0") or "")
    row = theban.magi(thebes).index(shard)
    form = theban.neutralize_step(saga, thebes, row)
    assert isinstance(form, Form)
    options = next(f for f in form.fields() if f.key == "token_id").options
    assert {"cov_ionian_0", "cov_ionian_1"} <= {v for _, v in options}
    _save(form, token_id="cov_ionian_0", service="a season in the laboratory")
    assert _entry(thebes, "cov_ionian_0")["tokens"] == 1
    assert shard["shards"] == 0
    logged = theban.log(thebes, "neutralizations")[-1]
    assert logged["service"] == "a season in the laboratory"
    # With no shard left, More's Neutralize refuses.
    assert not isinstance(theban.neutralize_step(saga, thebes, row), Form)


def test_the_tribunals_longevity_ritual_goes_to_the_most_tokens():
    saga = everything_saga()
    thebes = _polity(saga)
    saga.character("cov_ionian_0").background.year_born = 1150
    saga.character("cov_ionian_1").background.year_born = 1120
    _tokens(thebes, "cov_ionian_0", tokens=4)
    _tokens(thebes, "cov_ionian_1", tokens=4)
    _tokens(thebes, "cov_ionian_2", tokens=9, shards=1)
    _tokens(thebes, "cov_ionian_3", tokens=9)
    saga.character("cov_ionian_3").aging.longevity_modifier = 5
    crafter = _tokens(thebes, "cov_kretan_0", tokens=0)
    eligible = {e["character_id"] for e in theban.longevity_eligible(saga, thebes)}
    assert {"cov_ionian_0", "cov_ionian_1"} <= eligible
    assert not {"cov_ionian_2", "cov_ionian_3"} & eligible
    form = theban.longevity_form(saga, thebes)
    _save(form, crafter_id="cov_kretan_0", great=True)
    # A tie on tokens goes to the elder.
    assert _entry(thebes, "cov_ionian_1")["tokens"] == 0
    assert _entry(thebes, "cov_ionian_0")["tokens"] == 4
    assert crafter["tokens"] == 2
    again = theban.longevity_form(saga, thebes)
    assert again.validate is not None
    assert "has sponsored" in (again.validate(_values(again)) or "")


def test_the_tokens_list_offers_its_more_commands():
    saga = everything_saga()
    thebes = _polity(saga)
    thebes.package = theban.KEY
    assert tribunal_packages.package_verb(thebes, "neutralize_shard") is not None
    assert tribunal_packages.package_verb(thebes, "tribunal_longevity") is not None


# -- related languages --


def _speaker(*abilities):
    from ars_magica_manager.models import Ability
    from ars_magica_manager.rules.xp import ability_xp

    found = Character(id="x", name="Speaker", type="magus")
    for name, level, *specialty in abilities:
        found.abilities.append(
            Ability(name, xp=ability_xp(level), specialty=(specialty or [None])[0])
        )
    return found


def test_romaic_greek_reads_classical_greek_at_minus_two():
    from ars_magica_manager.rules import languages

    theban_magus = _speaker(("Living Language: Greek", 6))
    assert languages.understanding_score(theban_magus, "Classical Greek") == 4
    assert (
        languages.understanding_score(
            _speaker(("Living Language: Greek", 5)), "Classical Greek"
        )
        == 3
    )
    assert languages.penalty("Living Language: Vlach", "Dead Language: Latin") == 3
    assert languages.penalty("Living Language: High German", "Low German") == 2
    assert languages.penalty("Living Language: Low German", "West Norse", "Saxon") == 2
    assert languages.penalty("Living Language: Low German", "West Norse") == 3
    assert languages.penalty("Living Language: Magyar", "Latin") is None


def test_a_theban_magus_may_study_a_classical_greek_book_with_romaic_six(monkeypatch):
    from ars_magica_manager.models import Book, SeasonPlan
    from ars_magica_manager.rules import activities, library

    monkeypatch.setattr(library, "can_read", lambda *_args: True)
    saga = everything_saga()
    book = Book(
        id="greek_creo",
        name="On Creo",
        type="Art Summa",
        art="Creo",
        level=10,
        quality=10,
        language="Classical Greek",
    )
    saga.books.append(book)
    plan = SeasonPlan("x", 1220, "Spring", "study", book_id=book.id)

    def problems(romaic: int) -> list[str]:
        magus = _speaker(("Living Language: Greek", romaic), ("Artes Liberales", 1))
        found = activities._reading_problems(saga, magus, plan)
        return [p for p in found if "Classical Greek" in p]

    assert not problems(6)
    assert problems(5)


# -- Against the Dark --


def _transylvania(saga: Saga):
    from ars_magica_manager.tribunal_packages import transylvania

    tribunal = saga.tribunal("thebes")
    assert tribunal is not None
    tribunal.package = transylvania.KEY
    covenant = Covenant(id="opp", saga_id="s", name="Oppidum", tribunal_id=tribunal.id)
    saga.covenants.append(covenant)
    for n, (house, privilege) in enumerate(
        [
            ("house_tremere", "cives"),
            ("house_bonisagus", "socii"),
            ("house_tremere", "socii"),
        ]
    ):
        saga.characters.append(
            Character(id=f"o{n}", name=f"Opp {n}", type="magus", covenant_id="opp")
        )
        saga.characters[-1].hermetic.house = house
        transylvania.members(saga, tribunal).append(
            {"character_id": f"o{n}", "privilege": privilege}
        )
    return tribunal, covenant


def test_a_privilege_says_who_may_hold_which_office():
    from ars_magica_manager.tribunal_packages.transylvania import office_rule

    assert office_rule("cives", "Praeco") == ("", False)
    assert office_rule("foederati", "Praeco") == ("", False)
    assert office_rule("socii", "Praeco")[1]
    assert not office_rule("socii", "Curantis")[1]
    assert office_rule("coloniae", "Curantis")[1]
    assert office_rule("coloniae", "Aedile") == ("", False)
    words, refuses = office_rule("hospites", "Curantis")
    assert words and not refuses
    assert office_rule("socii", "Curator of Tablinum")[1]


def test_the_praeco_and_offices_are_refused_against_the_privilege():
    from ars_magica_manager.forms import tribunal as tribunal_forms
    from ars_magica_manager.tribunal_packages import transylvania

    saga = everything_saga()
    tribunal, _covenant = _transylvania(saga)
    form = tribunal_forms.edit_tribunal_form(saga, tribunal)
    assert form.validate is not None
    assert "Praeco" in (form.validate(_values(form, praeco_id="o1")) or "")
    assert form.validate(_values(form, praeco_id="o0")) is None
    ops = transylvania.member_ops(saga, tribunal)
    edit = ops.edit(1)
    assert isinstance(edit, Form) and edit.validate is not None
    assert edit.validate(_values(edit, privilege="coloniae", office="Curantis"))


def test_an_oppidum_needs_two_members_a_cives_two_houses_and_its_aediles():
    from ars_magica_manager.tribunal_packages import transylvania as t

    saga = everything_saga()
    tribunal, covenant = _transylvania(saga)
    # One cives against two others: the others are dominant, so one
    # aedile, and he must be the cives.
    assert t.aediles_needed(saga, tribunal, covenant) == 1
    t.aediles(tribunal)["opp"] = ["o1"]
    assert "Opp 1 is of the dominant group" in t.oppidum_problems(
        saga, tribunal, covenant
    )
    t.aediles(tribunal)["opp"] = ["o0"]
    assert t.oppidum_status(saga, tribunal, covenant) == "lawful"
    t.members(saga, tribunal)[0]["privilege"] = "socii"
    assert "no cives" in t.oppidum_problems(saga, tribunal, covenant)
    saga.characters[:] = [c for c in saga.characters if c.id != "o2"]
    t.members(saga, tribunal)[0]["privilege"] = "cives"
    # One cives and one socius: two aediles.
    assert t.aediles_needed(saga, tribunal, covenant) == 2
    assert "2 aediles due" in t.oppidum_problems(saga, tribunal, covenant)


def test_the_transylvania_pack_builds_the_chronicle_labs_and_zenodochium():
    from ars_magica_manager.book_packs import PACKS
    from ars_magica_manager.rules import enchantment

    saga = PACKS["transylvania"].build()
    chronicle = [
        b for b in saga.books if b.name.startswith("The Transylvania Chronicle")
    ]
    assert len(chronicle) == 18
    assert {b.ability for b in chronicle} == {
        "Organization Lore: Order of Hermes",
        "Code of Hermes",
    }
    codex = next(c for c in saga.codices if c.name == "The Transylvania Chronicle")
    assert codex.encyclopedia and all(b.codex_id == codex.id for b in chronicle)
    levels = {
        d.name: [enchantment.modified_level(d, e) for e in d.effects]
        for d in saga.enchanted_devices
    }
    assert levels["The Hippocratic Staff"] == [34, 34]
    assert levels["The Ankh of Moving Forward"] == [60]
    assert levels["The Bowl of the Honest Traveler"] == [29]
    tablets = {b.name: b.level for b in saga.books if b.type == "Casting Tablet"}
    assert tablets["Arms of the Salamander"] == 30
    labs = {lab.name: lab for lab in saga.laboratories}
    distillery = labs["The Vim Distillery"]
    assert [(e.specialization, e.points) for e in distillery.specialties] == [
        ("Vis Extraction", 10)
    ]
    assert labs["Theodore's Laboratory"].characteristics.aesthetics == 6


def test_the_theban_pack_has_apparent_ages_boons_patrons_and_shared_labs():
    from ars_magica_manager import catalog
    from ars_magica_manager.book_packs import PACKS

    saga = PACKS["theban"].build()
    by_name = {c.name: c for c in saga.characters}
    assert by_name["Xenias the Leper"].aging.apparent_age == 107
    assert by_name["Petros"].aging.apparent_age == 11
    names = catalog.load_covenant_boon_hook_catalog_by_id()
    ingasia = next(c for c in saga.covenants if c.name == "Ingasia")
    held = {names[b.vf_id].name for b in ingasia.boons_hooks}
    assert {"Powerful Ally", "House Covenant"} <= held
    tribunal = saga.tribunals[0]
    patrons = theban_meeting.patrons(tribunal)
    assert patrons[ingasia.id]["name"] == "Mosychlos"
    forge = next(
        lab for lab in saga.laboratories if lab.name == "The Forge of Hephaistos"
    )
    assert {(e.specialization, e.points) for e in forge.specialties} == {
        ("Rego", 8),
        ("Items", 5),
    }


# -- Guardians of the Forests --


def _rhine(saga: Saga):
    from ars_magica_manager.tribunal_packages import rhine

    tribunal = saga.tribunals[0]
    assert tribunal.package == rhine.KEY
    rhine.gilds(tribunal)[:] = [
        {"name": "Oak Gild", "members": [], "agenda": ""},
        {"name": "Hawthorn Gild", "members": [], "agenda": ""},
    ]
    covenant = saga.covenants[0]
    covenant.tribunal_id = tribunal.id
    return tribunal, covenant


def test_a_magus_joins_one_gild_and_never_one_he_has_enmity_for():
    from ars_magica_manager import world
    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.tribunal_packages import rhine

    saga = everything_saga()
    tribunal, covenant = _rhine(saga)
    magi = world.covenant_magi(saga, covenant)
    assert magi
    magus = magi[0]
    magus.virtues_flaws.append(
        VirtueFlawInstance("vf_gild_enmity", params={"gild": "Hawthorn Gild"})
    )
    fields = rhine.covenant_gild_fields(saga, tribunal, covenant)
    mine = next(f for f in fields if f.key == f"gild_of_{magus.id}")
    assert [label for label, _ in mine.options] == ["Oak Gild"]
    rhine.save_covenant_gilds(tribunal, covenant.id, {mine.key: "0"})
    assert rhine.gild_of(tribunal, magus.id)["name"] == "Oak Gild"
    rhine.join(tribunal, magus.id, rhine.gilds(tribunal)[1])
    # Joining another leaves the first: one gild at most.
    assert magus.id not in rhine.gilds(tribunal)[0]["magi"]
    rhine.save_covenant_gilds(tribunal, covenant.id, {mine.key: None})
    assert rhine.gild_of(tribunal, magus.id) is None
    rhine.join(tribunal, magus.id, rhine.gilds(tribunal)[0])
    assert ("Gild", "Oak Gild") in tribunal_packages.magus_facts(saga, magus)


def test_a_tremere_whose_sigil_the_exarch_casts_has_no_vote_of_his_own():
    from ars_magica_manager import world
    from ars_magica_manager.tribunal_packages import rhine

    saga = everything_saga()
    tribunal, covenant = _rhine(saga)
    _save(meeting.hold(saga, tribunal))
    before = meeting.present(saga, tribunal, tribunal.meeting, covenant)
    magus = world.covenant_magi(saga, covenant)[0]
    rhine.sigil_held_by(tribunal)[magus.id] = "someone"
    after = meeting.present(saga, tribunal, tribunal.meeting, covenant)
    assert after[0] == before[0] - 1


def test_gild_trained_is_thirty_on_lore_and_sixty_on_abilities_and_arts():
    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.rules import creation_access as access
    from ars_magica_manager.rules import creation_later as later

    magus = Character(id="g", name="Gilded", type="magus")
    magus.virtues_flaws.append(
        VirtueFlawInstance("vf_gild_trained", params={"gild": "Ash Gild"})
    )
    pools = access.virtue_xp(magus)
    assert {k: r.xp for k, r in pools.items()} == {
        "vf_gild_trained": 30,
        access.GILD_POOL: 60,
    }
    lore = pools["vf_gild_trained"]
    assert access.virtue_xp_allows(lore, "Intrigue")
    assert access.virtue_xp_allows(lore, "Organization Lore: Durenmar")
    assert not access.virtue_xp_allows(lore, "Penetration")
    gild = pools[access.GILD_POOL]
    assert access.virtue_xp_allows(gild, "Penetration")
    assert access.virtue_xp_allows(gild, "Creo")
    assert not access.virtue_xp_allows(lore, "Creo")
    assert "Ignem" in later.virtue_targets(magus, access.GILD_POOL)
    assert access.pool_name(access.GILD_POOL).endswith("the gild's Abilities and Arts")


def test_the_rhine_pack_seats_its_magi_in_gilds_and_counts_tremere_sigils_once():
    from ars_magica_manager.book_packs import PACKS
    from ars_magica_manager.tribunal_packages import rhine

    saga = PACKS["rhine"].build()
    tribunal = saga.tribunals[0]
    by_name = {c.name: c for c in saga.characters}
    apple = next(g for g in rhine.gilds(tribunal) if g["name"].startswith("Apple"))
    leaders = {saga.character(i).name for i in apple["leader_ids"]}
    assert leaders == {"Henri de Tours", "Wilhelm Weiss", "Daria la Gris"}
    assert all("dues" not in g for g in rhine.gilds(tribunal))
    seated = [i for g in rhine.gilds(tribunal) for i in g["magi"]]
    assert len(seated) == len(set(seated))
    held = rhine.sigil_held_by(tribunal)
    assert held[by_name["Hygwald Veritas"].id] == by_name["Severicus"].id
    assert held[by_name["Sicero"].id] == by_name["Stentorius"].id
