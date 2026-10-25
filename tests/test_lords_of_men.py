"""Lords of Men's agents, Affinity, Noble Reputation, tournaments and
Gratitude (Lords of Men pp. 7-8, 21-26, 64-69), and replacing a bad
Reputation (DE pp. 386-387)."""

from dataclasses import asdict

from ars_magica_manager import lords, session_end, tourney_season
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.models import (
    Ability,
    Agent,
    Character,
    Characteristics,
    Neighbour,
    Saga,
    ScoredTrait,
)
from ars_magica_manager.rules import agents, confidence, nobility, tournament

# -- Gratitude --


def _lord_saga(points: int) -> tuple[Saga, Neighbour, Character]:
    squire = Character(id="w", name="Walter", type="grog")
    lord = Neighbour(
        "l",
        "Count Adolf",
        kind="lord",
        details={
            "title": "count",
            "manors": 50,
            "gratitude": [{"who": "w", "points": points, "why": "Saved his son"}],
        },
    )
    return Saga(id="s", name="S", characters=[squire], neighbours=[lord]), lord, squire


def test_the_advancement_table_prices_each_step():
    prices = {r.key: r.gratitude for r in nobility.REWARDS}
    assert prices["freeman"] == prices["knight"] == prices["carissimus"] == 5
    assert prices["manor"] == prices["manors"] == prices["officer"] == 10
    assert prices["royal_baron"] == 20
    assert nobility.REWARDS_BY_KEY["knight"].virtue == "Knight"
    assert lords.earns(20) == "Baron of the king"


def test_redeeming_gratitude_spends_the_points_and_writes_the_diaries():
    saga, lord, squire = _lord_saga(7)
    form = lords.redeem_form(saga, lord, 0)
    assert isinstance(form, Form) and form.validate is not None
    fields = {f.key: f for f in form.fields()}
    assert fields["reward"].value == "freeman"  # the first of the dearest
    assert form.validate({"reward": "manor", "spent": 7}) == (
        "Bacheler to lord of the manor needs 10 Gratitude."
    )
    assert form.validate({"reward": "knight", "spent": 8}) == "He owes only 7 points."
    lines = form.apply({"reward": "knight", "spent": 5, "what": "his spurs"})
    entry = lord.details["gratitude"][0]
    assert entry["points"] == 2
    assert entry["spent"] == ["Warrior to knight: his spurs (5 Gratitude)"]
    assert any("add Knight" in line for line in lines)
    assert lord.details["diary"][-1]["text"].startswith("Count Adolf rewarded Walter")
    assert squire.diary[-1].name == "Gratitude redeemed with Count Adolf"
    # Goods may be any number of points.
    assert form.validate({"reward": "goods", "spent": 1}) is None


def test_nothing_owed_cannot_be_redeemed():
    saga, lord, _ = _lord_saga(0)
    assert isinstance(lords.redeem_form(saga, lord, 0), Refuse)
    assert isinstance(lords.redeem_form(saga, lord, 3), Refuse)


# -- Affinity --


def test_affinity_follows_the_title_unless_set_and_halves_when_divided():
    saga, lord, _ = _lord_saga(0)
    assert lords.affinity(lord) == 5
    lord.details["affinity_divided"] = True
    assert lords.affinity(lord) == 2
    lord.details |= {"affinity": "3", "affinity_divided": False}
    assert lords.affinity(lord) == 3
    knight = Neighbour("k", "Sir Konrad", kind="lord", details={"manors": 1})
    assert lords.affinity(knight) == 0
    knight.details["manors"] = 5
    assert lords.affinity(knight) == 1
    facts = {f.label: f.value for f in lords.facts(saga, knight)}
    assert facts["Affinity"].startswith("+1 to social rolls")
    assert nobility.affinity_bonus(3, True) == 1
    # A baron is taken at the lowest baron tier, a minor lord's (LoM p. 21).
    baron = Neighbour("b", "Baron Odo", kind="lord", details={"title": "baron"})
    assert lords.affinity(baron) == 2


def test_the_lord_form_offers_affinity():
    keys = [f.key for f in lords.fields(Saga(id="s", name="S"), None)]
    assert keys[-2:] == ["affinity", "affinity_divided"]


# -- Noble Reputation --


def test_noble_reputation_experience_and_rolls():
    assert nobility.noble_xp(["season", "crusade", "royal_liege"]) == 8
    assert nobility.noble_xp([], might=24) == 4
    assert nobility.noble_roll_ease("Same kingdom", "A vassal of the one rolling") == 3
    assert (
        nobility.noble_roll_ease(
            "Adjoining counties",
            "A landholder of the same status",
            ["An acknowledged lover or bastard"],
        )
        == 12
    )
    reps = [ScoredTrait("Brave", 2, type="Noble"), ScoredTrait("Prudhomme", 1)]
    assert nobility.prudhomme_index(reps) == 1
    assert nobility.prudhomme(reps[:1]) == 2
    assert nobility.prudhomme([ScoredTrait("Wise", 3, type="Local")]) == 0


def test_end_of_session_hints_at_noble_deeds():
    hero = Character(
        id="h",
        name="Hero",
        type="companion",
        reputations=[ScoredTrait("Prudhomme", 2, type="Noble")],
    )
    deeds = next(f for f in session_end.session_fields(hero) if f.key == "deeds_0")
    assert "royal liege 6" in deeds.hint


# -- agents --


def test_how_many_agents_he_can_hold():
    assert agents.max_agents(2, 1, 3, 0) == 10
    assert agents.max_agents(0, 0, 0, 3) == 1
    lord = Character(
        id="a",
        name="Duke Simon",
        type="companion",
        characteristics=Characteristics(presence=2),
        abilities=[Ability("Intrigue", "General", xp=30)],
    )
    assert agents.character_max_agents(lord) == 10


def test_resistance_from_the_recruitment_table():
    assert agents.resistance("minor_virtue", []) == 1
    assert agents.resistance("major_flaw", []) == 1  # never below 1
    assert agents.resistance("major_virtue", ["underlings", "major_virtue"]) == 7
    four = ["skill", "minor_virtue", "underlings", "useful_flaw"]
    assert agents.resistance("free", four) == 4 + 6
    assert agents.resistance("major_virtue", ["dominated"]) == 1


def test_agency_experience_wears_resistance_down_then_builds_the_bond():
    matthew = Agent("Matthew", status="major_virtue", modifiers=["underlings"])
    assert agents.wear_down(matthew, 10).left == 10  # not impressed yet
    matthew.impressed = True
    spent = agents.wear_down(matthew, 5)  # 4, then 3 is too dear for 1 left
    assert (spent.worn, spent.left, matthew.resistance) == (1, 1, 3)
    spent = agents.wear_down(matthew, 6)  # 3 + 2 + 1
    assert spent.recruited and matthew.resistance == 0 and matthew.bond == 0
    assert not agents.may_be_asked(matthew)
    assert agents.strengthen(matthew, agents.xp_for_pounds(1)).levels == 1
    assert matthew.bond == 1 and agents.may_be_asked(matthew)


def test_task_ease_and_persuasion():
    assert agents.task_ease("sensitive", "day", "injury") == 12
    assert agents.persuasion_total(1, 3, 2, 3) == 3
    assert agents.RISK["death"][2] == 5


def test_agents_load_with_the_character():
    hero = Character(id="h", name="H", type="companion")
    hero.agents.append(Agent("Bishop Benedict", bond_trait="Thankful", bond=1))
    loaded = Character.from_dict(asdict(hero))
    assert loaded.agents[0].bond_trait == "Thankful"
    assert Character.from_dict({"id": "x", "name": "X", "type": "grog"}).agents == []


# -- tournaments --


def test_tournament_rules():
    assert tournament.knight_xp(["company", "daring", "prize"]) == 2
    assert tournament.knight_xp([]) == 0
    assert tournament.patron_xp("lavish", 4, 3) == 3
    assert tournament.patron_xp("hosted", 2, 3) == 1
    assert tournament.patron_xp("", 9, 0) == 0
    assert tournament.share(3, 2) == 1
    assert tournament.patron_spend(3) == 30 and tournament.prize_value(3) == 3
    assert tournament.sponsor_cost(10, 2) == 80
    assert tournament.melee_event(0).startswith("An inexperienced knight")
    assert tournament.melee_event(12).startswith("A Wealthy knight")
    assert tournament.melee_event(30).startswith("A large company of three")
    assert tournament.melee_botch_dice(2) == 3
    assert tournament.opponent_light_wounds(3) == 2


def test_tourneying_as_income():
    knight = Character(
        id="k",
        name="K",
        type="companion",
        characteristics=Characteristics(dexterity=2),
        abilities=[Ability("Great Weapon", "Martial", xp=50)],
    )
    assert tournament.labor_per_season(knight) == 18
    assert tournament.seasons_to_live(knight) == 2


def test_a_tournament_season_counts_toward_prudhomme():
    knight = Character(
        id="k",
        name="Sir Hugh",
        type="companion",
        reputations=[ScoredTrait("Prudhomme", 1, type="Noble", deeds=8)],
    )
    saga = Saga(id="s", name="S", characters=[knight])
    form = tourney_season.tourney_form(saga, knight)
    assert isinstance(form, Form)
    fields = {f.key: f for f in form.fields()}
    assert fields["reputation"].value == "0"
    lines = form.apply({"reputation": "0", "prize": True, "company": True})
    assert knight.reputations[0].score == 2
    assert lines[0].startswith("Prudhomme: 2 experience point(s) (2 as a knight)")
    assert knight.diary[-1].name == "A season at the tourney"


def test_a_tournament_can_start_a_prudhomme_and_mark_unpaid_ransom():
    knight = Character(
        id="k",
        name="Sir Hugh",
        type="companion",
        reputations=[ScoredTrait("Oath-breaker", -1, deeds=9)],
    )
    saga = Saga(id="s", name="S", characters=[knight])
    tourney_season.apply_season(
        saga,
        knight,
        {"reputation": "new", "hosting": "hosted", "patrons": 1}
        | {"unpaid": 1, "unpaid_to": "0"},
    )
    started = knight.reputations[-1]
    assert (started.name, started.type, started.deeds) == ("Prudhomme", "Noble", 1)
    assert knight.reputations[0].score == -2


def test_a_second_noble_reputation_starts_prudhomme_at_nothing():
    # LoM p. 25: the 1 for entering feudal life is given once.
    knight = Character(
        id="k",
        name="Sir Hugh",
        type="companion",
        reputations=[ScoredTrait("Brave", 1, type="Noble")],
    )
    saga = Saga(id="s", name="S", characters=[knight])
    tourney_season.apply_season(saga, knight, {"reputation": "new"})
    assert knight.reputations[-1].name == "Prudhomme"
    assert knight.reputations[-1].score == 0


# -- replacing a bad Reputation --


def test_general_deeds_feed_the_old_reputation_until_the_new_passes_it():
    old = ScoredTrait("Coward", -2)
    new = ScoredTrait("Brave", 1, replaces="Coward")
    result = confidence.count_replacing(new, old, supporting=10, general=3)
    assert new.score == 2 and old.deeds == 3 and result.new_gained == 1
    confidence.count_replacing(new, old, supporting=15, general=0)
    assert new.score == 3
    confidence.count_replacing(new, old, supporting=0, general=2)
    assert new.deeds == 2 and old.deeds == 3  # ahead now: they go to Brave


def test_once_ahead_a_rise_may_lower_the_old_reputation_instead():
    old = ScoredTrait("Coward", -1)
    new = ScoredTrait("Brave", 2, replaces="Coward")
    result = confidence.count_replacing(new, old, 15, 0, lower_old=True)
    assert result.old_lowered == 1 and old.score == 0 and new.score == 2
    reps = [old, new]
    assert confidence.drop_spent(reps) == ["Coward"]
    assert reps == [new] and new.replaces == ""


def test_the_end_of_session_form_counts_replacing_deeds():
    hero = Character(
        id="h",
        name="Hero",
        type="companion",
        reputations=[
            ScoredTrait("Coward", -1),
            ScoredTrait("Brave", 2, replaces="Coward"),
        ],
    )
    saga = Saga(id="s", name="S", characters=[hero])
    keys = [f.key for f in session_end.session_fields(hero)]
    assert {"deeds_0", "deeds_1", "general_1", "lower_1"} <= set(keys)
    lines = session_end.end_session(
        saga, hero, {"played": True, "deeds_1": 15, "lower_1": True}
    )
    assert [r.name for r in hero.reputations] == ["Brave"]
    assert any("Coward is gone" in line for line in lines)


def test_the_reputation_form_offers_a_bad_one_to_replace_and_keeps_deeds():
    reps = [ScoredTrait("Coward", -2), ScoredTrait("Brave", 1, deeds=4)]
    ops = trait_forms.trait_ops(reps, "section-reputations")
    assert ops.edit is not None
    form = ops.edit(1)
    assert isinstance(form, Form)
    replaces = next(f for f in form.fields() if f.key == "replaces")
    assert replaces.options == [("Coward", "Coward")]
    form.apply({"name": "Brave", "score": 1, "replaces": "Coward"})
    assert reps[1].deeds == 4 and reps[1].replaces == "Coward"
