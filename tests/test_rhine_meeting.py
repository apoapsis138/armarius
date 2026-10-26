"""The Rhine's ranks and its meeting's rite (Guardians of the Forests pp.
19-24, 26-27): marks of approval making a master, the archmage's
challenge, the apprentice a journeyman may not formally take, and the
new magi introduced and sigils conferred at the meeting."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import meeting, tribunal_packages
from ars_magica_manager.commands import Form, Refuse, Then
from ars_magica_manager.models import (
    Background,
    Character,
    Covenant,
    HermeticBackground,
    Saga,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import rhine_ranks as ranks
from ars_magica_manager.tribunal_packages import rhine


def _magus(
    ident: str,
    name: str,
    covenant: str,
    house: str,
    rank: str = "",
    born: int | None = 1150,
    parens: str = "",
) -> Character:
    character = Character(
        id=ident,
        name=name,
        type="magus",
        covenant_id=covenant,
        background=Background(year_born=born),
        hermetic=HermeticBackground(house=house, parens=parens),
        reputations=[ScoredTrait("Master of Mentem", 3, type="Hermetic")],
    )
    if rank:
        character.virtues_flaws.append(VirtueFlawInstance(rank))
    return character


def _saga() -> Saga:
    """The sample Rhine with Durenmar beside Keep and Fengheld: three
    masters of three gilds, an archmage, and Leandro of Keep a
    journeyman."""
    saga = everything_saga()
    saga.covenants.append(
        Covenant(id="cov_dur", saga_id="s", name="Durenmar", tribunal_id="rhine")
    )
    saga.characters += [
        _magus("m_oak", "Murion", "cov_dur", "house_bonisagus", ranks.MASTER),
        _magus("m_ash", "Philippus", "cov_sketch", "house_tytalus", ranks.MASTER),
        _magus("m_haw", "Urgen", "cov_dur", "house_bjornaer", ranks.MASTER),
        _magus("m_arch", "Stentorius", "cov_sketch", "house_tremere", ranks.ARCHMAGE),
    ]
    leandro = saga.character("mag1")
    assert leandro is not None
    leandro.background.year_born = 1170
    leandro.hermetic.house = "house_flambeau"
    leandro.reputations.append(ScoredTrait("Fire-handed", 2, type="Hermetic"))
    tribunal = _rhine(saga)
    listed = rhine.gilds(tribunal)
    for name, ident in (
        ("Oak Gild", "m_oak"),
        ("Ash Gild", "m_ash"),
        ("Hawthorn Gild", "m_haw"),
    ):
        gild = {"name": name, "magi": [], "members": []}
        listed.append(gild)
        rhine.join(tribunal, ident, gild)
    return saga


def _rhine(saga: Saga):
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return tribunal


def _char(saga: Saga, ident: str) -> Character:
    found = saga.character(ident)
    assert found is not None
    return found


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def _verb(tribunal, action: str) -> tribunal_packages.PackageVerb:
    verb = tribunal_packages.package_verb(tribunal, action)
    assert verb is not None
    return verb


# -- the ranks --


def test_a_magus_with_no_rank_is_a_journeyman_and_promotion_replaces_it():
    saga = _saga()
    leandro = _char(saga, "mag1")
    leandro.virtues_flaws.append(VirtueFlawInstance(ranks.HERMETIC_MAGUS))
    assert ranks.rank(leandro) == ranks.JOURNEYMAN
    assert not ranks.is_master(leandro)
    ranks.promote(leandro, ranks.MASTER)
    held = [vf.vf_id for vf in leandro.virtues_flaws]
    assert ranks.MASTER in held and ranks.HERMETIC_MAGUS not in held
    assert ("Master", 2) in [(r.name, r.score) for r in leandro.reputations]
    ranks.promote(leandro, ranks.ARCHMAGE, "Slew the wyrm")
    held = [vf.vf_id for vf in leandro.virtues_flaws]
    assert held.count(ranks.ARCHMAGE) == 1 and ranks.MASTER not in held
    reps = {r.name: r.score for r in leandro.reputations}
    assert reps["Archmage"] == 4 and reps["Slew the wyrm"] == 4
    # The book pack counts sigils by the same table.
    assert ranks.RANK_SIGILS == {ranks.ARCHMAGE: 2, ranks.MASTER: 1}


def test_a_mark_comes_from_a_master_of_another_covenant_and_house():
    saga = _saga()
    leandro, murion = _char(saga, "mag1"), _char(saga, "m_oak")
    assert ranks.mark_problem(leandro, murion, []) == ""
    assert "already" in ranks.mark_problem(leandro, murion, ["m_oak"])
    assert "journeyman" in ranks.mark_problem(leandro, _char(saga, "mag_sketch"), [])
    murion.covenant_id = "cov1"
    assert "covenant" in ranks.mark_problem(leandro, murion, [])
    murion.covenant_id = "cov_dur"
    murion.hermetic.house = "house_flambeau"
    assert "House" in ranks.mark_problem(leandro, murion, [])
    assert "already a master" in ranks.mark_problem(murion, leandro, [])


def test_what_custom_frowns_on_in_the_marks():
    saga = _saga()
    leandro = _char(saga, "mag1")
    sponsors = [
        ranks.Sponsor(_char(saga, "m_oak"), "Oak Gild"),
        ranks.Sponsor(_char(saga, "m_haw"), "Oak Gild"),
    ]
    # Fifty years old, 25 past his Gauntlet: early is no concern.
    found = ranks.mark_warnings(saga, leandro, sponsors, ["Oak Gild"])
    assert any("three different gilds" in w for w in found)
    assert any("Enmity of the Oak Gild" in w for w in found)
    assert not any("years past" in w for w in found)
    leandro.background.year_born = 1190
    leandro.reputations.clear()
    found = ranks.mark_warnings(saga, leandro, sponsors[:1])
    assert any("5 years past his Gauntlet" in w for w in found)
    assert any("magical prowess" in w for w in found)


def test_three_marks_make_a_master():
    saga = _saga()
    tribunal = _rhine(saga)
    form = _verb(tribunal, "rhine_mark").build(saga, tribunal, 0)
    assert isinstance(form, Form)
    applicants = {f.key: f for f in form.fields()}["applicant"].options
    assert ("Leandro (Journeyman)", "mag1") in applicants
    # A master of his own House is refused.
    _char(saga, "m_oak").hermetic.house = "house_flambeau"
    refused = form.validate(_values(form, applicant="mag1", sponsor="m_oak"))
    assert refused is not None and "House" in refused
    _char(saga, "m_oak").hermetic.house = "house_bonisagus"
    for sponsor in ("m_oak", "m_ash"):
        form = _verb(tribunal, "rhine_mark").build(saga, tribunal, 0)
        _save(form, applicant="mag1", sponsor=sponsor, asked="a tract")
    leandro = _char(saga, "mag1")
    assert not ranks.is_master(leandro)
    assert ("Marks", "2 of 3 toward master") in rhine.magus_facts(
        saga, tribunal, leandro
    )
    form = _verb(tribunal, "rhine_mark").build(saga, tribunal, 0)
    assert isinstance(form, Form) and form.live is not None
    live = form.live(_values(form, applicant="mag1", sponsor="m_haw"))
    assert "3 of 3 marks: Murion, Philippus, Urgen" in live
    assert "becomes a master" in live
    _save(form, applicant="mag1", sponsor="m_haw")
    assert ranks.is_master(leandro)
    assert rhine.promotions(tribunal)[-1]["character_id"] == "mag1"
    assert rhine.promotions(tribunal)[-1]["conferred"] is None


def test_no_mark_without_a_master_in_the_tribunal():
    saga = everything_saga()
    tribunal = _rhine(saga)
    found = _verb(tribunal, "rhine_mark").build(saga, tribunal, 0)
    assert isinstance(found, Refuse)


# -- the archmage's challenge --


def test_who_may_challenge_an_archmage():
    saga = _saga()
    murion, stentorius = _char(saga, "m_oak"), _char(saga, "m_arch")
    leandro = _char(saga, "mag1")
    assert ranks.challenge_problem(murion, stentorius, []) == ""
    assert "journeyman" in ranks.challenge_problem(leandro, stentorius, [])
    assert "before" in ranks.challenge_problem(
        murion, stentorius, [ranks.Bout("m_oak", False)]
    )
    seven = [ranks.Bout(f"x{i}", True) for i in range(7)]
    assert "no more" in ranks.challenge_problem(murion, stentorius, seven)
    assert "not an archmage" in ranks.challenge_problem(murion, leandro, [])
    six = [ranks.Bout(f"x{i}", True) for i in range(6)]
    found = ranks.challenge_warnings(saga, murion, stentorius, six)
    assert any("bad etiquette" in w for w in found)
    assert any("7th magnitude" in w for w in found)
    # One whose parens is an archmage challenges him first.
    _char(saga, "m_haw").virtues_flaws = [VirtueFlawInstance(ranks.ARCHMAGE)]
    murion.hermetic.parens = "Urgen"
    found = ranks.challenge_warnings(saga, murion, stentorius, [])
    assert any("parens Urgen" in w for w in found)
    assert not any(
        "parens" in w
        for w in ranks.challenge_warnings(saga, murion, stentorius, [], ["m_haw"])
    )


def test_winning_the_challenge_makes_an_archmage_and_the_contest_stays():
    saga = _saga()
    tribunal = _rhine(saga)
    murion = _char(saga, "m_oak")
    murion.invented_spells.append(Spell("s1", "Great Ward", "rego", "vim", 35))
    assert ranks.invented_magnitude(murion) == 7
    form = _verb(tribunal, "rhine_challenge").build(saga, tribunal, 0)
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    challenger = fields["challenger"]
    assert challenger.fills is not None
    assert challenger.fills({"challenger": "m_oak"}) == {"spell": True}
    # Murion, the first challenger listed, has one: ticked as it opens.
    assert fields["spell"].value is True
    values = _values(form, challenger="m_ash", archmage="m_arch", deed="x", spell=False)
    assert "7th magnitude" in (form.validate(values) or "")
    values = _values(
        form, challenger="m_ash", archmage="m_arch", deed="x", spell=True, contest=""
    )
    assert "contest" in (form.validate(values) or "")
    _save(
        form,
        challenger="m_ash",
        archmage="m_arch",
        contest="defeat him in certamen",
        deed="Broke the Order of Odin's ward",
        spell=True,
        outcome=rhine.LOST,
    )
    assert not ranks.is_archmage(_char(saga, "m_ash"))
    form = _verb(tribunal, "rhine_challenge").build(saga, tribunal, 0)
    assert isinstance(form, Form)
    again = _values(form, challenger="m_ash", archmage="m_arch", deed="x", spell=True)
    assert "before" in (form.validate(again) or "")
    # The contest is set: the second challenger isn't asked it.
    contest = next(f for f in form.fields() if f.key == "contest")
    assert contest.show_if is not None
    assert not contest.show_if({"archmage": "m_arch"})
    _save(
        form,
        challenger="m_oak",
        archmage="m_arch",
        deed="Restored the Great Library",
        spell=True,
        outcome=rhine.WON,
    )
    assert ranks.is_archmage(murion)
    record = rhine.challenge_record(tribunal, "m_arch")
    assert record["contest"] == "defeat him in certamen"
    assert [b["won"] for b in record["bouts"]] == [False, True]
    assert rhine.promotions(tribunal)[-1]["rank"] == ranks.ARCHMAGE


def test_a_magus_of_another_tribunal_may_challenge_without_being_a_master():
    saga = _saga()
    tribunal = _rhine(saga)
    thebes = saga.tribunal("thebes")
    assert thebes is not None and thebes.package != rhine.KEY
    saga.covenants.append(
        Covenant(id="cov_far", saga_id="s", name="Far Hall", tribunal_id="thebes")
    )
    saga.characters.append(_magus("m_far", "Kosmas", "cov_far", "house_jerbiton"))
    kosmas, stentorius = _char(saga, "m_far"), _char(saga, "m_arch")
    leandro = _char(saga, "mag1")
    assert rhine.is_rhine_magus(saga, leandro)
    assert not rhine.is_rhine_magus(saga, kosmas)
    able = [m.id for m in rhine.challengers(saga, tribunal)]
    # The Rhine's masters first; its journeyman Leandro is not listed.
    assert set(able[:3]) == {"m_oak", "m_ash", "m_haw"}
    assert "m_far" in able and "mag1" not in able and "m_arch" not in able
    assert ranks.challenge_problem(kosmas, stentorius, [], rhine_magus=False) == ""
    assert "journeyman" in ranks.challenge_problem(leandro, stentorius, [])
    form = _verb(tribunal, "rhine_challenge").build(saga, tribunal, 0)
    assert isinstance(form, Form)
    options = {f.key: f for f in form.fields()}["challenger"].options
    assert (f"Kosmas ({thebes.name})", "m_far") in options
    promoted = len(rhine.promotions(tribunal))
    _save(
        form,
        challenger="m_far",
        archmage="m_arch",
        contest="defeat him in certamen",
        deed="Healed the Patriarch",
        spell=True,
        outcome=rhine.WON,
    )
    # An archmage by his Reputation, without the Rhine's rank Virtue or a
    # sigil owed at its rite.
    assert ranks.is_archmage(kosmas)
    assert ranks.ARCHMAGE not in [vf.vf_id for vf in kosmas.virtues_flaws]
    assert len(rhine.promotions(tribunal)) == promoted
    assert "m_far" not in [m.id for m in rhine.challengers(saga, tribunal)]


# -- the apprentice limit --


def test_only_a_master_takes_an_apprentice():
    saga = _saga()
    tribunal = _rhine(saga)
    leandro = _char(saga, "mag1")
    assert "journeyman" in ranks.apprentice_problem(leandro)
    assert ranks.apprentice_problem(_char(saga, "m_oak")) == ""
    saga.characters.append(
        Character(
            id="app1",
            name="Arn",
            type="companion",
            hermetic=HermeticBackground(parens="Leandro"),
        )
    )
    facts = dict(rhine.magus_facts(saga, tribunal, leandro))
    assert "hedge wizard" in facts["Apprentice"]


# -- the meeting's rite --


def _to_rite(saga: Saga, tribunal):
    """The roll call and the Opening held: the rite's form."""
    following = _save(meeting.hold(saga, tribunal))
    assert isinstance(following, Then)
    following = _save(following.step)
    assert isinstance(following, Then) and isinstance(following.step, Form)
    return following.step


def test_the_rite_follows_the_opening():
    saga = _saga()
    titles = [
        s.title for s in meeting.steps(_rhine(saga), meeting.record(saga, _rhine(saga)))
    ]
    assert titles[2] == "The new magi and the sigils by proxy"


def test_the_rite_introduces_the_new_magi_and_confers_the_sigils():
    saga = _saga()
    tribunal = _rhine(saga)
    # Felicia passed her Gauntlet in 1225, since the meeting of 1221;
    # Arn, trained by Severinus, a journeyman, in 1227.
    saga.characters += [
        _magus(
            "felicia",
            "Felicia",
            "cov_dur",
            "house_bonisagus",
            born=1200,
            parens="Murion",
        ),
        _magus("arn", "Arn", "cov1", "house_flambeau", born=1202, parens="Severinus"),
        _magus("old", "Old Horst", "cov_dur", "house_bonisagus", born=1150),
    ]
    for sponsor in ("m_oak", "m_ash", "m_haw"):
        _save(
            _verb(tribunal, "rhine_mark").build(saga, tribunal, 0),
            applicant="mag1",
            sponsor=sponsor,
        )
    leandro = _char(saga, "mag1")
    leandro.hermetic.parens = "Notatus"
    rite = _to_rite(saga, tribunal)
    assert rite.save_label == "Confer"
    fields = {f.key: f for f in rite.fields()}
    assert {"intro_felicia", "intro_arn"} <= set(fields) and "intro_old" not in fields
    assert "recruited hedge wizard" in fields["intro_arn"].hint
    assert fields["sigil_0"].value == "Notatus"
    assert tribunal.proxies.get("cov1", 0) == 0
    keep_at_roll = tribunal.meeting["attendance"]["cov1"]["proxies"]
    _save(rite, sigil_0="Notatus")
    assert tribunal.proxies["cov1"] == 1
    assert tribunal.meeting["attendance"]["cov1"]["proxies"] == keep_at_roll + 1
    assert rhine.entrusted(tribunal)["mag1"] == ["Notatus"]
    assert rhine.promotions(tribunal)[0]["conferred"] == 1228
    assert ("Sigils by proxy", "Notatus") in rhine.magus_facts(saga, tribunal, leandro)
    minutes = tribunal.diary[-1].details
    assert "Introduced: Felicia, trained by Murion" in minutes
    assert "the sigil of Notatus" in minutes
    # Holding it again confers afresh, never twice.
    step = next(
        s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == "rhine_rite"
    )
    again = meeting.step_form(saga, tribunal, step)
    fields = {f.key: f for f in again.fields()}
    assert fields["confer_0"].value is True and fields["intro_felicia"].value is True
    _save(again, sigil_0="Bonisagus", intro_arn=False)
    assert tribunal.proxies["cov1"] == 1
    assert rhine.entrusted(tribunal)["mag1"] == ["Bonisagus"]
    assert tribunal.meeting["rhine_rite"]["introduced"] == ["felicia"]
    _save(meeting.step_form(saga, tribunal, step), confer_0=False)
    assert tribunal.proxies.get("cov1", 0) == 0
    assert "mag1" not in rhine.entrusted(tribunal)
    assert rhine.promotions(tribunal)[0]["conferred"] is None


def test_a_rite_with_nothing_to_confer_says_so():
    saga = _saga()
    rite = _to_rite(saga, _rhine(saga))
    infos = [str(f.value) for f in rite.fields() if f.kind == "info"]
    assert any("No master or archmage has been made since" in v for v in infos)
