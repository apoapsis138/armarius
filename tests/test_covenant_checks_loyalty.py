"""Covenant creation checks and Prevailing Loyalty in full: the per-magus
income rule, the Unknown Hook counted once, bought specialists' caps and
Gifted teachers, the Prestige Boons' Reputation (DE pp. 179-184), Loyalty
past +-6, the autocrat's two roles and the three-task cap, the +-6
productivity effect and scribes' writing materials (DE pp. 185-194)."""

from __future__ import annotations

from ars_magica_manager import catalog, economics, inhabitants
from ars_magica_manager.covenants import (
    boon_hook_problems,
    covenant_hook_points,
    prestige_shortfall,
)
from ars_magica_manager.models import (
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    Character,
    Covenant,
    Inhabitant,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_covenant as cov


def _saga(magi: int = 2) -> Saga:
    covenant = Covenant(
        id="cov1", saga_id="s", name="Keep", in_creation=True, year_founded=1215
    )
    return Saga(
        id="s",
        name="S",
        current_year=1220,
        covenants=[covenant],
        characters=[
            Character(id=f"m{i}", name=f"M{i}", type="magus", covenant_id="cov1")
            for i in range(magi)
        ],
    )


def _found(saga: Saga, record: Covenant, step: str) -> dict[str, tuple[str, str]]:
    return {c.label: (c.status, c.detail) for c in rules.checks(saga, record, step)}


# -- the income per magus (DE p. 189) --


def _amounts(saga: Saga, covenant: Covenant) -> list[list[int]]:
    return [
        [amount for _, amount in choice.sources]
        for choice in cov.income_choices(saga, covenant)
    ]


def test_the_per_magus_adjustment_is_made_once_to_the_main_source():
    saga = _saga(magi=8)
    saga.rule_options["income_per_magus"] = True
    covenant = saga.covenants[0]
    # Two over six: +30 to the Typical source; two Lesser share it.
    assert _amounts(saga, covenant) == [[130], [55, 55]]
    # A Secondary Income source isn't adjusted; a Greater source is.
    covenant.boons_hooks = [
        VirtueFlawInstance("covbh_boon_minor_wealth"),
        VirtueFlawInstance("covbh_boon_minor_secondary_income"),
    ]
    assert _amounts(saga, covenant) == [[280, 100]]


def test_one_lesser_source_adjusts_only_six_a_magus_and_odd_pounds_split():
    saga = _saga(magi=5)
    saga.rule_options["income_per_magus"] = True
    covenant = saga.covenants[0]
    choices = cov.income_choices(saga, covenant)
    assert [c.label for c in choices] == [
        "One Typical source (85 pounds)",
        "Two Lesser sources (33 and 32 pounds)",
    ]
    covenant.boons_hooks = [VirtueFlawInstance("covbh_hook_minor_poverty")]
    assert _amounts(saga, covenant) == [[34]]
    saga.rule_options = {}
    assert _amounts(saga, covenant) == [[40]]


# -- the Unknown Hook (DE p. 182) --


def test_an_unknown_hook_taken_both_ways_is_flagged():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    covenant = _saga().covenants[0]
    may_be_unknown = next(
        e.id for e in by_id.values() if e.type == "Hook" and e.unknown
    )
    marked = VirtueFlawInstance(may_be_unknown, params={BOON_HOOK_UNKNOWN: "yes"})
    covenant.boons_hooks = [marked]
    assert covenant_hook_points(covenant, by_id) == 3
    assert not any("Unknown" in p for p in boon_hook_problems(covenant, by_id))
    covenant.boons_hooks.append(VirtueFlawInstance("covbh_hook_major_unknown"))
    problems = [p for p in boon_hook_problems(covenant, by_id) if "Unknown" in p]
    assert len(problems) == 1 and "counted twice" in problems[0]
    found = _found(_saga(), covenant, "boons_hooks")
    assert found["Boons and Hooks fit together"][0] == "warn"


# -- bought specialists (DE pp. 180-181) --


def test_bought_specialists_are_capped_by_age_and_teachers_have_no_gift():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.power_level, covenant.build_points_budget = "Low", 300
    covenant.inhabitants = [
        Inhabitant(
            id="a",
            kind="specialist",
            name="Young Scribe",
            linked_ability="Profession: Scribe",
            specialist_score=6,
            year_born=1200,
        ),
        Inhabitant(
            id="b",
            kind="specialist",
            name="Old Master",
            linked_ability="Artes Liberales",
            specialist_score=7,
            teacher_communication=2,
            teacher_teaching=6,
            year_born=1180,
        ),
    ]
    found = _found(saga, covenant, "build_points")
    status, detail = found["Bought specialists' scores within the age cap"]
    assert status == "warn"
    assert "Young Scribe: Profession: Scribe 6 over 5 (age 20)" in detail
    assert "Old Master" not in detail  # 40: cap 7
    label = "Bought teachers have no Gift (so teach no Hermetic Art)"
    assert found[label][0] == "pass"
    covenant.inhabitants[1].linked_ability = "Creo"
    assert _found(saga, covenant, "build_points")[label] == ("warn", "Old Master")


def test_a_specialist_without_a_year_born_is_taken_as_under_thirty():
    saga = _saga()
    person = Inhabitant(
        id="a",
        kind="specialist",
        name="Hand",
        linked_ability="Brawl",
        specialist_score=6,
    )
    assert cov.specialist_over_cap(saga, person) == (
        "Hand: Brawl 6 over 5 (no Year Born, so under 30)"
    )
    person.specialist_score = 5
    assert cov.specialist_over_cap(saga, person) == ""


# -- the Prestige Boons' Reputation (DE pp. 183-184) --


def test_each_prestige_boon_wants_its_reputation():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    covenant = _saga().covenants[0]
    assert prestige_shortfall(covenant, by_id) is None
    covenant.boons_hooks = [
        VirtueFlawInstance(
            "covbh_boon_minor_prestige", params={BOON_HOOK_DETAIL: "the town"}
        ),
        VirtueFlawInstance("covbh_boon_major_prestige"),
    ]
    assert prestige_shortfall(covenant, by_id) == [
        "Prestige (Major Boon): a Reputation of 9",
        "Prestige (Minor Boon) - the town: a Reputation of 3",
    ]
    covenant.reputations = [ScoredTrait(name="Wise neighbours", score=3)]
    assert prestige_shortfall(covenant, by_id) == [
        "Prestige (Major Boon): a Reputation of 9"
    ]
    found = _found(_saga(), covenant, "boons_hooks")
    label = "Each Prestige Boon has its Reputation (Minor 3, Major 9)"
    assert found[label][0] == "advice"


# -- Prevailing Loyalty (DE pp. 185-186; Covenants pp. 36-38) --


def test_loyalty_points_follow_the_advancement_table_past_six():
    assert [inhabitants.prevailing_loyalty_score(p) for p in (105, 139, 140)] == [
        6,
        6,
        7,
    ]
    assert inhabitants.prevailing_loyalty_score(-180) == -8


def _role(id_: str, role: str, presence: int, ability: int) -> Inhabitant:
    return Inhabitant(
        id=id_,
        kind="specialist",
        name=id_,
        role=role,
        presence=presence,
        skill_value=ability,
    )


def test_an_autocrat_adds_both_roles_and_each_task_counts_once():
    saga = _saga()
    covenant = saga.covenants[0]
    # The autocrat: Presence 2 for each role, Steward + Chamberlain 8.
    covenant.inhabitants = [_role("auto", "Autocrat", 2, 8)]
    assert inhabitants.specialists_loyalty(saga, covenant) == 12
    # A second steward does a task the autocrat already does: not counted.
    covenant.inhabitants.append(_role("stew", "Steward", 1, 3))
    covenant.inhabitants.append(_role("capt", "Turb Captain", 1, 5))
    assert inhabitants.specialists_loyalty(saga, covenant) == 12 + 6
    assert [e.name for e in inhabitants.uncounted_role_holders(saga, covenant)] == [
        "stew"
    ]
    # Separate steward and chamberlain who do better than the autocrat.
    covenant.inhabitants += [_role("cham", "Chamberlain", 3, 6)]
    covenant.inhabitants[1] = _role("stew", "Steward", 3, 6)
    assert inhabitants.specialists_loyalty(saga, covenant) == 9 + 9 + 6
    text = inhabitants.loyalty_right_text(saga, covenant)
    assert "1 not counted: one for each task" in text


def test_loyalty_of_minus_six_halves_the_covenfolks_savings():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.inhabitants = [
        Inhabitant(
            id="lab", kind="inhabitant", name="Hands", role="Laborer", quantity=4
        ),
        Inhabitant(
            id="smith",
            kind="craftsperson",
            name="Smith",
            field_of_work="Consumables",
            skill_value=6,
            rare=True,
        ),
    ] + [Inhabitant(id=f"g{i}", kind="turb", name=f"G{i}") for i in range(40)]
    before = {r.key: r.savings for r in economics.summarize(saga, covenant).savings}
    # 4 laborers save 4; the rare smith 6, capped at 20% of Consumables
    # (56 points: 11.2), so 2.24, rounded up to 3.
    assert (before["laborers"], before["craftspeople"]) == (4, 3)
    assert inhabitants.prevailing_loyalty(saga, covenant) > -6
    covenant.loyalty.actions_and_events = -200
    assert inhabitants.prevailing_loyalty(saga, covenant) <= -6
    halved = {r.key: r for r in economics.summarize(saga, covenant).savings}
    # Halved: 2 and 1.12, rounded up to 2.
    assert (halved["laborers"].savings, halved["craftspeople"].savings) == (2, 2)
    assert "productivity halved" in halved["laborers"].basis
    assert inhabitants.productivity_note(6).startswith("Prevailing Loyalty +6")


def test_writing_materials_count_scribes_kept_as_specialists():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.inhabitants = [
        Inhabitant(
            id="s",
            kind="specialist",
            name="Brother Anselm",
            linked_ability="Profession: Scribe",
            quantity=1,
        ),
        Inhabitant(id="c", kind="specialist", name="Copyist", responsibility="Copyist"),
        Inhabitant(id="t", kind="specialist", name="Tutor", role="Teacher"),
    ]
    writing = next(
        r for r in economics.summarize(saga, covenant).expenditure if r.key == "writing"
    )
    assert writing.first == 2 + 2
    assert "2 scribe specialist(s)" in writing.basis
