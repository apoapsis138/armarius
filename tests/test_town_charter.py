"""A town's Charter, Guilds and Court tabs: the rules they work out
(City & Guild pp. 8-14, 23-24, 28-30, 41-50, 54; Realms of Power: The
Divine p. 10; the Definitive Edition p. 204 for The Gift)."""

import random

from ars_magica_manager import (
    neighbours,
    storage,
    town_charter,
    town_court,
    town_guilds,
    towns,
)
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    Neighbour,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.sections import (
    CHARTER_GIVES_SECTION,
    CHARTER_TERMS_SECTION,
    CITIZENS_SECTION,
    COURT_CASES_SECTION,
    GUILD_MEMBERS_SECTION,
    GUILDS_SECTION,
    TOWN_PEOPLE_SECTION,
)

#: Ability xp for a score: 1, 2, 3, 5, 7.
XP = {1: 5, 2: 15, 3: 30, 5: 75, 7: 140}


def _saga() -> Saga:
    leandro = Character(id="leandro", name="Leandro", type="companion")
    leandro.characteristics.communication = 2
    leandro.abilities = [
        Ability("Civil and Canon Law", "Academic", XP[3]),
        Ability("Artes Liberales", "Academic", XP[2]),
    ]
    kyrillos = Character(id="kyrillos", name="Kyrillos", type="magus")
    kyrillos.characteristics.communication = 1
    kyrillos.virtues_flaws = [VirtueFlawInstance("vf_the_gift")]
    priest = Character(id="priest", name="Father Udo", type="companion")
    priest.virtues_flaws = [VirtueFlawInstance("vf_priest")]
    worms = Neighbour(id="worms", name="Worms", kind="town")
    worms.details = {"population": 3000}
    speyer = Neighbour(id="speyer", name="Speyer", kind="town")
    return Saga(
        id="t",
        name="Towns",
        characters=[leandro, kyrillos, priest],
        neighbours=[worms, speyer],
        current_year=1220,
        current_season="Spring",
    )


def _town(saga: Saga) -> Neighbour:
    found = saga.neighbour("worms")
    assert found is not None
    return found


def _save(form: object, values: dict) -> object:
    assert isinstance(form, Form)
    return form.apply(values)


# -- the tabs --


def test_a_town_has_charter_guilds_and_court_tabs_after_its_town_tab():
    kind = neighbours.KINDS["town"]
    assert kind.tab is not None and kind.tab.title == "Town"
    assert [t.title for t in kind.more] == ["Charter", "Guilds", "Court"]
    assert all(not t.after_standing for t in kind.more)
    # The guilds moved off the Town tab, which keeps its fairs.
    assert [e.section_id for e in kind.tab.lists] == ["section-nb-fairs"]


def test_the_charter_tab_shows_lords_terms_gives_citizens_then_people():
    parts = [p.section_id for p in town_charter.CHARTER_TAB.parts()]
    assert parts == [
        "section-nb-charter-lords",
        CHARTER_TERMS_SECTION,
        CHARTER_GIVES_SECTION,
        CITIZENS_SECTION,
        TOWN_PEOPLE_SECTION,
    ]


def test_every_list_and_block_on_a_town_has_its_verbs():
    saga = _saga()
    ops = neighbour_forms.neighbour_ops(saga, _town(saga))
    for section in (CITIZENS_SECTION, GUILDS_SECTION, GUILD_MEMBERS_SECTION):
        assert ops[section].add is not None
    for section in (CHARTER_TERMS_SECTION, CHARTER_GIVES_SECTION, TOWN_PEOPLE_SECTION):
        assert ops[section].edit is not None and ops[section].add is None


def test_an_old_save_town_loads_and_shows_empty_tabs(tmp_path):
    """A town saved before the tabs, with only its guilds, still loads and
    every new list starts empty."""
    saga = _saga()
    town = _town(saga)
    town.details = {"population": 800, "guilds": [{"trade": "Weavers", "masters": 3}]}
    storage.save_saga(saga)
    town = storage.load_saga("t").neighbour("worms")
    assert town is not None
    assert town_charter.charter_lords(town) == []
    assert town_charter.terms(town) == {}
    assert town_court.cases(town) == []
    assert town_guilds.members(town) == []
    grid = town_guilds.guilds_grid(saga, town)
    assert grid.rows == [["Weavers", "Craft", "", "", "3", "", "", "3"]]


# -- the walls' aura (C&G pp. 10-11; DE p. 418, over RoP: The Divine p. 10) --


def _lord(name: str, kind: str, hold: str = "Sole") -> dict:
    return {"lord": name, "kind": kind, "hold": hold}


def test_a_town_s_and_a_city_s_normal_aura_is_3():
    saga = _saga()
    town = _town(saga)
    assert town_charter.walls_aura(town)[0] == 3
    town.details["city"] = True
    assert town_charter.walls_aura(town)[0] == 3
    town.details["city"] = False
    town.details["population"] = 25000  # as large as a city
    assert town_charter.walls_aura(town)[0] == 3


def test_an_ecclesiastical_charter_gives_one_more_and_a_faerie_one_1():
    saga = _saga()
    town = _town(saga)
    town.details["charter_lords"] = [_lord("Bishop of Worms", "Church")]
    assert town_charter.walls_aura(town)[0] == 4
    town.details["charter_lords"] = [_lord("The King of the Wood", "Faerie")]
    assert town_charter.walls_aura(town)[0] == 1


def test_a_shared_charter_keeps_the_normal_aura_unless_the_church_holds_it():
    saga = _saga()
    town = _town(saga)
    town.details["charter_lords"] = [
        _lord("Bishop of Worms", "Church", "Shared"),
        _lord("Count Palatine", "Noble", "Shared"),
    ]
    assert town_charter.holder_kind(town) == "Shared"
    assert town_charter.walls_aura(town)[0] == 3
    town.details["charter_terms"] = {"church_holds": True}
    assert town_charter.walls_aura(town)[0] == 4


def test_a_rival_or_parallel_charter_does_not_change_the_aura():
    saga = _saga()
    town = _town(saga)
    town.details["charter_lords"] = [
        _lord("Count Palatine", "Noble"),
        _lord("The Elf King", "Faerie", "Rival"),
        _lord("Szarlen", "Demon", "Parallel"),
    ]
    assert town_charter.holder_kind(town) == "Noble"
    assert town_charter.walls_aura(town)[0] == 3


def test_with_no_lords_listed_the_town_s_charter_field_decides():
    saga = _saga()
    town = _town(saga)
    town.details["charter"] = "Church"
    assert town_charter.walls_aura(town)[0] == 4
    town.details["charter"] = "Faerie"
    assert town_charter.walls_aura(town)[0] == 1
    town.details["charter"] = "Commune"
    assert town_charter.walls_aura(town)[0] == 3


def test_a_demon_s_charter_shows_might_15_and_its_services():
    saga = _saga()
    town = _town(saga)
    demon = _lord("Szarlen", "Demon", "Parallel")
    demon["disease"] = True
    town.details["charter_lords"] = [demon]
    text = town_charter.gives_text(saga, town)
    assert "Infernal Might [b]15[/]" in text
    assert "relief from disease" in text
    assert "+2 to the Living Conditions modifier" in text
    assert "Help for merchants" not in text


def test_the_charter_holds_one_pawn_until_it_is_taken():
    saga = _saga()
    town = _town(saga)
    assert town_charter.pawns(town) == 1
    assert "[b]1[/] pawn of Rego vis" in town_charter.gives_text(saga, town)
    _save(
        town_charter.edit_gives(saga, town),
        {"church_holds": False, "pawns": 3, "vis_taken": True},
    )
    assert town_charter.pawns(town) == 3
    assert not town_charter.connected(town)
    assert "destroyed" in town_charter.gives_text(saga, town)


# -- the terms (pp. 10-13) --


def test_terms_tick_their_privileges_and_the_tax_defaults_to_40_pounds():
    saga = _saga()
    town = _town(saga)
    form = town_charter.edit_terms(saga, town)
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    assert fields["tax_amount"].value == "40 pounds"
    assert fields["tax_amount"].show_if is not None
    assert not fields["tax_amount"].show_if({"tax": False})
    _save(form, {"family": "Freiburg", "granted": 1184, "tax": True, "courts": True})
    lines = town_charter.privilege_lines(town)
    assert "Annual tax" in lines[0] and "40 pounds (C&G p. 12)" in lines[0]
    assert lines[1].startswith("[$text-success]")
    assert lines[2].startswith("[dim]–")  # ordeal not limited
    assert town_charter.terms_facts(saga, town)[0].value == "Freiburg"


# -- citizens (p. 9) --


def test_a_year_and_a_day_makes_a_citizen():
    saga = _saga()
    entry = {"character_id": "leandro", "since_year": 1219, "since_season": "Summer"}
    assert town_charter.citizen_from(entry) == "Summer 1220"
    assert not town_charter.is_citizen(saga, entry)
    saga.current_season = "Summer"
    assert town_charter.is_citizen(saga, entry)


def test_a_citizen_gets_the_plus_one_multiplier_until_the_vis_is_taken():
    saga = _saga()
    town = _town(saga)
    town.details["citizens"] = [
        {"character_id": "leandro", "since_year": 1218, "since_season": "Spring"},
        {"character_id": "kyrillos", "since_year": 1220, "since_season": "Spring"},
    ]
    grid = town_charter.citizens_grid(saga, town)
    assert [row[3] for row in grid.rows] == ["+1 multiplier", "not yet"]
    town.details["charter_terms"] = {"vis_taken": True}
    assert town_charter.citizens_grid(saga, town).rows[0][3] == "severed"


def test_becoming_a_citizen_elsewhere_ends_the_old_link():
    saga = _saga()
    worms, speyer = saga.neighbours
    speyer.details["citizens"] = [
        {"character_id": "leandro", "since_year": 1210, "since_season": "Spring"}
    ]
    ops = town_charter.citizen_ops(saga, worms)
    form = ops.add()
    assert isinstance(form, Form) and form.live is not None
    assert "Listed in Speyer" in form.live({"character_id": "leandro"})
    form.apply(
        {"character_id": "leandro", "since_season": "Spring", "since_year": 1220}
    )
    assert [c["character_id"] for c in town_charter.citizens(worms)] == ["leandro"]
    assert town_charter.citizens(speyer) == []


def test_a_cleric_is_warned_he_is_rarely_a_citizen():
    saga = _saga()
    town = _town(saga)
    town.details["citizens"] = [{"character_id": "priest", "since_year": 1210}]
    assert "canon law rarely" in town_charter.citizen_info(saga, town, 0)


# -- size and people (pp. 13-14, 23-24, 29) --


def test_occupations_follow_the_town_s_size():
    saga = _saga()
    town = _town(saga)  # 3,000: a medium town
    assert town_charter.occupations(town) == [
        ("Agriculture", 10, 300),
        ("Craft", 50, 1500),
        ("Service", 30, 900),
        ("Trade", 10, 300),
    ]
    town.details["population"] = 400
    assert town_charter.occupations(town)[0] == ("Agriculture", 50, 200)
    town.details["city"] = True  # a city counts as a large town
    assert town_charter.occupations(town)[3] == ("Trade", 30, 120)


def test_officials_are_read_a_line_each():
    saga = _saga()
    town = _town(saga)
    _save(
        town_charter.edit_people(saga, town),
        {"officials": "Mayor: Heinrich Holtmunt\n\nCoroners: 2", "burgesses": 400},
    )
    assert town_charter.officials(town) == [
        ("Mayor", "Heinrich Holtmunt"),
        ("Coroners", "2"),
    ]
    assert town_charter.people_facts(saga, town)[1].value == "400"


# -- guilds (pp. 41-54) --


def test_a_town_of_a_thousand_has_one_to_three_guilds_by_1300():
    assert towns.guilds_expected(900, 1300) == "1 to 3"
    assert towns.guilds_expected(900, 1220) == "0 to 1"


def test_renaming_a_guild_keeps_its_members_and_deleting_it_drops_them():
    saga = _saga()
    town = _town(saga)
    town.details["guilds"] = [{"trade": "Weavers"}]
    town.details["guild_members"] = [
        {"character_id": "leandro", "guild": "Weavers", "rank": "journeyman"}
    ]
    ops = town_guilds.guild_ops(saga, town)
    form = ops.edit(0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    form.apply({**values, "trade": "Clothiers"})
    assert town_guilds.members(town)[0]["guild"] == "Clothiers"
    confirm = ops.remove(0)
    assert isinstance(confirm, Confirm)
    assert "Its 1 member from the saga leave it" in confirm.question
    confirm.apply()
    assert town_guilds.members(town) == []


def test_a_member_needs_a_guild_first():
    saga = _saga()
    assert isinstance(town_guilds.member_ops(saga, _town(saga)).add(), Refuse)


def test_a_rank_s_needs_are_checked():
    saga = _saga()
    leandro = saga.character("leandro")
    assert leandro is not None
    guild = {"trade": "Weavers", "craft": "Weaver"}
    lacking = town_guilds.shortfalls(leandro, guild, "journeyman")
    assert lacking == [
        "Craft 5 (has 0)",
        "Guild Lore 1 (has 0)",
        "the Social Status Virtue for a journeyman",
    ]
    leandro.abilities += [
        Ability("Craft: Weaver", xp=XP[5]),
        Ability("Organization Lore: Weavers' Guild", xp=XP[1]),
    ]
    leandro.virtues_flaws.append(VirtueFlawInstance("vf_journeyman"))
    assert town_guilds.shortfalls(leandro, guild, "journeyman") == []
    master = town_guilds.shortfalls(leandro, guild, "master")
    assert "Guild Lore 2 (has 1)" in master
    assert "Leadership half his Craft (has 0)" in master


# -- the court (pp. 29-30) --


def _case(**more: object) -> dict:
    return {"accused": "Agnes", "charge": "Slander", **more}


def test_the_court_roll_is_communication_and_law_against_six():
    saga = _saga()
    plea = town_court.plea(saga, {"arguer": "leandro", "law": "civil"})
    assert (plea.total, plea.ease) == (5, 6)
    assert plea.logic == 2  # Civil Law weighs Artes Liberales
    assert town_court.plea(saga, {"arguer": "leandro", "law": "common"}).logic is None


def test_innocence_a_bad_name_and_witnesses_move_the_ease_factor():
    saga = _saga()
    base = {"arguer": "leandro", "law": "civil"}
    assert town_court.plea(saga, {**base, "innocent": True}).ease == 3
    assert (
        town_court.plea(saga, {**base, "bad_name": True, "witnesses": True}).ease == 12
    )


def test_the_gift_of_whoever_pleads_counts_and_a_proxy_avoids_it():
    saga = _saga()
    gifted = town_court.plea(saga, {"arguer": "kyrillos", "social": 1})
    assert gifted.total == 1 + 0 - 3 + 1
    assert "- The Gift 3" in gifted.terms
    proxy = town_court.plea(saga, {"arguer": None, "communication": 1, "law_score": 4})
    assert (proxy.arguer, proxy.total) == ("A proxy", 5)


def test_a_court_roll_records_the_verdict_and_refuses_a_judged_case():
    saga = _saga()
    town = _town(saga)
    town.details["court_cases"] = [_case()]
    form = town_court.court_roll(saga, town, 0, random.Random(3))
    assert isinstance(form, Form) and form.inspector == "The Verdict"
    assert form.live is not None
    assert "Against [b]3[/]" in form.live({"arguer": "leandro", "innocent": True})
    form.apply({"arguer": "leandro", "law": "civil", "innocent": True})
    case = town_court.cases(town)[0]
    assert case["verdict"] in ("Guilty", "Not guilty")
    assert "Leandro pleaded" in case["roll"]
    assert isinstance(town_court.court_roll(saga, town, 0), Refuse)


def test_an_unpaid_fine_makes_an_outlaw():
    saga = _saga()
    town = _town(saga)
    town.details["court_cases"] = [
        _case(verdict="Guilty", sentence="fine", detail="3 pounds", unpaid=True)
    ]
    assert town_court.outlawed(town_court.cases(town)[0])
    grid = town_court.cases_grid(saga, town)
    assert grid.rows[0][4] == "Fine: 3 pounds, unpaid"
    assert "an outlaw" in town_court.case_info(saga, town, 0)


def test_the_case_form_offers_a_sentence_only_once_guilty():
    saga = _saga()
    town = _town(saga)
    ops = neighbour_forms.neighbour_ops(saga, town)[COURT_CASES_SECTION]
    form = ops.add()
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    show = fields["sentence"].show_if
    assert (
        show is not None and not show({"verdict": None}) and show({"verdict": "Guilty"})
    )
    unpaid = fields["unpaid"].show_if
    assert unpaid is not None and unpaid({"verdict": "Guilty", "sentence": "fine"})
    assert set(town_court.SENTENCES) == {
        "death",
        "fine",
        "mutilation",
        "branding",
        "shaming",
    }


# -- the covenant's own charter (C&G p. 11) --


def test_a_covenant_s_charter_is_kept_on_the_covenant_and_old_saves_load():
    saga = _saga()
    covenant = Covenant(id="dam", saga_id="t", name="Dammerstein")
    covenant.boons_hooks = [VirtueFlawInstance(town_charter.CHARTERED_TOWN)]
    saga.covenants = [covenant]
    assert town_charter.has_boon_hook(covenant, town_charter.CHARTERED_TOWN)
    assert not town_charter.has_boon_hook(covenant, town_charter.CHARTER_LORD)
    ops = town_charter.covenant_charter_ops(saga, covenant)
    form = ops["section-cov-charter-lords"].add()
    assert isinstance(form, Form)
    form.apply({"lord": "Count of Katzenelnbogen", "kind": "Noble", "hold": "Sole"})
    terms = ops["section-cov-charter-terms"].edit(0)
    assert isinstance(terms, Form) and terms.help_id == "section-cov-charter-terms"
    terms.apply({"tax": True, "family": "Freiburg"})
    storage.save_saga(saga)
    loaded = storage.load_saga("t").covenants[0]
    assert loaded.charter["charter_lords"][0]["lord"] == "Count of Katzenelnbogen"
    assert loaded.charter["charter_terms"]["family"] == "Freiburg"
    assert (
        Covenant.from_dict({"id": "old", "saga_id": "t", "name": "Old"}).charter == {}
    )


def test_a_charter_lord_covenant_lists_the_towns_naming_it():
    saga = _saga()
    covenant = Covenant(id="dam", saga_id="t", name="Dammerstein")
    covenant.boons_hooks = [VirtueFlawInstance(town_charter.CHARTER_LORD)]
    assert "No town lists Dammerstein" in town_charter.chartered_towns_text(
        saga, covenant
    )
    _town(saga).details["charter_lords"] = [
        {"lord": "dammerstein", "kind": "Noble", "hold": "Shared", "since": 1210}
    ]
    text = town_charter.chartered_towns_text(saga, covenant)
    assert "[b]Worms[/]: shared (paragium), since 1210" in text
