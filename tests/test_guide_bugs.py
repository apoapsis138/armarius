"""The bugs the walkthrough guides found, fixed: an opened child's season,
Turbulence's age modifier once (Apprentices p. 23), House Acclaim's
dismal tournament (HoH:S p. 31), the quick Virtues' page (DE p. 47), a
siege event's day (Lords of Men p. 112), a Wizard's War on the docket,
the Ritual advice for lasting Creo (DE pp. 311, 344), the Hubris Ordeal's
Script bonus (HoH:MC p. 117) and the Human-like Vampire's Might (Against
the Dark p. 118)."""

from __future__ import annotations

from ars_magica_manager import book_packs, choice_templates, deeds, sieges
from ars_magica_manager.models import (
    Case,
    Character,
    Saga,
    SeasonPlan,
    Siege,
    Tribunal,
)
from ars_magica_manager.rules import acclaim, faerie_build, hermetic_law
from ars_magica_manager.rules import apprentice_seasons as aps
from ars_magica_manager.rules import siege as siege_rules
from ars_magica_manager.seasons import plans
from ars_magica_manager.sheets import tribunal as tribunal_sheet


def test_a_child_whose_arts_are_opened_has_no_default_season():
    magus = Character(id="m", name="Leandro", type="magus")
    child = Character(id="k", name="Kaspar", type="companion")
    saga = Saga(id="s", name="S", characters=[magus, child])
    assert child in plans.unplanned(saga)
    saga.season_plans.append(
        SeasonPlan(
            "m",
            saga.current_year,
            saga.current_season,
            aps.OPEN_ARTS,
            subject_id="k",
        )
    )
    # DE p. 270: the apprentice learns nothing else that season.
    assert child not in plans.unplanned(saga)


def test_a_dismal_tournament_is_minus_three_and_still_one_for_competing():
    label, xp = acclaim.TOURNAMENT["dismal"]
    assert xp == -2 and "-3" in label and "+1 for competing" in label


def test_the_quick_virtues_and_flaws_are_on_de_page_47():
    quick = [t for t in choice_templates.load_catalog() if "(DE quick)" in t.name]
    assert quick and {t.page for t in quick} == {47}


def test_a_siege_event_is_dated_the_day_it_is_played():
    siege = Siege("The Siege", castle="Burg", defenses="Superior", garrison=12)
    saga = Saga(id="s", name="S", sieges=[siege])
    form = sieges.next_event(saga, siege)
    form.apply({"event": siege_rules.WAIT})
    # Invested on day 0: the first event is played then (p. 112).
    assert siege.events[0].day == 0 and siege.days > 0


def test_a_wizards_war_on_the_docket_is_not_to_be_heard():
    war = Case(
        "Rudolf's war on Adelheid",
        kind=hermetic_law.WAR,
        brought_by="Rudolf",
        against="Adelheid",
    )
    tribunal = Tribunal(id="t", name="Rhine", next_year=1227, next_season="Spring")
    text = tribunal_sheet.case_text(Saga(id="s", name="S"), tribunal, war)
    assert "to be heard" not in text and "not heard" in text
    war.contested = True
    text = tribunal_sheet.case_text(Saga(id="s", name="S"), tribunal, war)
    assert "to be heard Spring 1227" in text


def test_the_human_like_vampires_might_comes_from_two_minor_virtues():
    saga = book_packs.PACKS["transylvania"].assemble().saga
    vampire = next(c for c in saga.creatures if c.name == "Human-like Vampire")
    assert faerie_build.might_from_virtues(vampire).might == 15
    assert not faerie_build.problems(vampire)


def test_a_disguise_roll_takes_the_covers_reputation_off_when_questioned():
    from ars_magica_manager.forms import covers
    from ars_magica_manager.models import Ability, DeepCover

    magus = Character(id="m", name="Carolus", type="magus")
    magus.characteristics.intelligence = 2
    magus.characteristics.presence = 1
    magus.abilities.append(Ability("Guile", xp=15))  # 2
    magus.covers.append(DeepCover("Reynard", reputation_xp=15))  # Reputation 2
    form = covers.disguise_form(Saga(id="s", name="S"), magus)
    assert not (form is None) and hasattr(form, "apply")
    # Int 2 + Guile 2 + 2 = 6 against 9 + Change social status 3 - 2 = 10.
    values = {"cover": magus.covers[0].id, "roll": "looks", "questioned": True}
    values |= {"mod_0": True, "die": 2}
    assert form.apply(values)[0] == "Disguise 6 against 10: the disguise fails."
    values["die"] = 6
    assert form.apply(values)[0].endswith("the disguise holds.")
    # Talking: Pre 1 + Guile 2 + 4 = 7 against Int + Folk Ken 3 + 5 (HoH:S p.
    # 87); an unGifted companion has no Gift to count.
    magus.type = "companion"
    talk = {"cover": magus.covers[0].id, "roll": "talks", "against": 3}
    talk |= {"die": 4, "their_die": 5}
    assert form.apply(talk)[0] == "Presence + Guile 7 against 8: they see through it."


def test_the_silver_cord_adds_to_a_trait_roll_and_rescues_a_mind():
    from ars_magica_manager.forms import trait_roll
    from ars_magica_manager.models import Familiar, ScoredTrait

    magus = Character(id="m", name="Ulric", type="magus")
    magus.personality_traits = [ScoredTrait("Brave", 2)]
    corax = Familiar(id="f", character_id="m", name="Corax", silver_cord=3)
    saga = Saga(id="s", name="S", characters=[magus], familiars=[corax])
    form = trait_roll.roll_form(saga, magus)
    # Brave 2 + Silver Cord 3 + die 4 = 9 against 9.
    said = form.apply({"kind": trait_roll.TRAIT, "trait": "0", "ease": 9, "die": 4})
    assert said[0].endswith("= 9 against 9: it holds.")
    rescue = trait_roll.roll_form(saga, corax)
    said = rescue.apply({"kind": trait_roll.RESCUE, "die": 5})
    assert "against 9: not today" in said[0]


def test_a_battle_event_played_as_a_fight():
    """Lords of Men pp. 105-108: the event makes its fight, and once the
    fight is over the event records its Maneuver's condition, with the
    groups the fight cost on top of the attrition."""
    from ars_magica_manager import battle_fights as bf
    from ars_magica_manager import battles
    from ars_magica_manager.models import Battle, BattleSide

    knight = Character(id="k", name="Sir Konrad", type="companion")
    entry = Battle(
        "Werl", sides=[BattleSide("Ours", groups=10), BattleSide("Theirs", groups=10)]
    )
    saga = Saga(id="s", name="S", characters=[knight], battles=[entry])
    form = battles.event_form(saga, entry)
    values = {f.key: f.value for f in form.fields()}
    values |= {
        "who": "k",
        "maneuver": "Attack",
        "enemy": "Standard",
        "size": "Outnumbered",
        "play_fight": True,
    }
    said = form.apply(values)
    assert said and "is on Conflicts" in said[0]
    (fight,) = saga.fights
    ours, theirs = fight.sides
    # The leader and four of his group; two groups of five infantry.
    assert len(ours.combatants) == 5 and ours.combatants[0].ref_id == "k"
    assert [len(g.members) for g in theirs.groups] == [5, 5]
    assert all(g.trained for g in theirs.groups)  # infantry (p. 108)
    assert entry.events == [] and bf.pending(saga, entry) is fight
    # The enemy beaten: everyone of theirs out.
    for c in theirs.combatants:
        c.out = True
    fight.over = "Ours win the fight."
    form = battles.event_form(saga, entry)
    values = {f.key: f.value for f in form.fields()}
    assert values["maneuver"] == "Attack" and values["condition_Attack"] == "routed"
    form.apply(values)
    (event,) = entry.events
    assert event.won and event.fight_id == fight.id
    # Two groups lost in the fight; no attrition at even numbers.
    assert entry.sides[1].groups == 8
    assert bf.pending(saga, entry) is None


def test_a_failed_rally_disorders_an_army_and_a_second_routs_it():
    """Lords of Men p. 106: a first failed rally applies Disordered, and a
    player character may rally it; a second routs it."""
    from ars_magica_manager import battles
    from ars_magica_manager.models import Battle, BattleEvent, BattleSide

    entry = Battle("Werl", sides=[BattleSide("Ours"), BattleSide("Theirs")])
    failed = BattleEvent("k", 0, won=True, morale=3, rally=4)  # theirs fails
    entry.events = [failed]
    assert battles.spirits(entry) == ["steady", "disordered"]
    assert battles.routed(entry) is None
    rallied = BattleEvent("k", 0, won=True, rally_by="k", rally_side=1, rally_roll=9)
    entry.events.append(rallied)
    assert battles.spirits(entry) == ["steady", "steady"]
    entry.events += [failed, failed]
    assert battles.routed(entry) == 1


def test_a_failed_morale_disorders_a_group_and_a_second_routs_it():
    from ars_magica_manager import fight_morale
    from ars_magica_manager.models import Combatant, Fight, FightGroup, FightSide
    from ars_magica_manager.rules import group_morale, options

    men = [Combatant(f"Levy {n}", leadership=2) for n in range(5)]
    group = FightGroup("Levies", [m.id for m in men], leader=men[0].id)
    fight = Fight(
        "Skirmish",
        sides=[FightSide("Ours", combatants=men, groups=[group]), FightSide("Them")],
    )
    saga = Saga(id="s", name="S", fights=[fight], books_in_play=["LoM"])
    assert not hasattr(fight_morale.check_form(saga, fight), "apply")  # off
    saga.rule_options[options.MORALE_DISCIPLINE] = True
    form = fight_morale.check_form(saga, fight)
    values = {"group": group.id, "check": "morale", "die": 1}
    values["morale_cause"] = next(iter(group_morale.MORALE_EASE))  # 6
    form.apply(values)  # Leadership 2 + 1 = 3 against 6
    assert group.state == group_morale.DISORDERED
    # Untrained and disordered: half its attacks hit (p. 135).
    assert group_morale.hits(group, 5) == 3
    form.apply(values)
    assert group.state == group_morale.ROUTED
    rally = fight_morale.rally_form(saga, fight)
    rally.apply({"group": group.id, "situation": "Not engaged", "die": 5})
    assert group.state == group_morale.DISORDERED


def test_casting_amid_a_battle_needs_concentration():
    """Lords of Men p. 109: Stamina + Concentration + stress die against
    12 engaged, 9 standing off (DE p. 215)."""
    import random

    from ars_magica_manager.models import Ability, Combatant, Fight, FightSide
    from ars_magica_manager.rules import fight as fight_rules

    magus = Character(id="m", name="Ulric", type="magus")
    magus.characteristics.stamina = 1
    magus.abilities.append(Ability("Concentration", xp=15))  # 2
    me = Combatant("Ulric", "character", "m")
    fight = Fight("Melee", sides=[FightSide("Us", combatants=[me]), FightSide("Them")])
    saga = Saga(id="s", name="S", characters=[magus], fights=[fight])
    assert not fight_rules.in_battle(fight)
    fight.part_of_battle = True
    assert fight_rules.in_battle(fight)
    unit = fight_rules.units(saga, fight)[me.id]

    class Six(random.Random):
        def randrange(self, *_a, **_k):
            return 6

    lines: list[str] = []
    engaged = fight_rules.Blow(fight_rules.CAST)
    assert not fight_rules._battle_concentration(saga, unit, engaged, Six(), lines)
    off = fight_rules.Blow(fight_rules.CAST, standing_off=True)
    assert fight_rules._battle_concentration(saga, unit, off, Six(), lines)


def test_a_year_campaigning_costs_living_conditions_and_a_disease_roll():
    """Lords of Men pp. 102-103: -1 Living Conditions for a year with a
    season in the army, a Disease Avoidance roll after a whole year, and
    -2 on the Aging roll returning to land put to chevauchee."""
    import random

    from ars_magica_manager.models import Battle, Covenant
    from ars_magica_manager.rules import living
    from ars_magica_manager.seasons import character_effects

    knight = Character(id="k", name="Sir Konrad", type="companion", covenant_id="c")
    saga = Saga(
        id="s",
        name="S",
        current_year=1220,
        characters=[knight],
        covenants=[Covenant(id="c", saga_id="s", name="Keep")],
    )
    assert living.campaign_living(saga, knight) == 0
    knight.campaign_seasons = ["1220 Summer"]
    assert living.campaign_living(saga, knight) == -1
    assert living.chevauchee_aging(saga, knight) == 0
    saga.battles = [Battle("Werl", year=1220, chevauchee_on="c")]
    assert living.chevauchee_aging(saga, knight) == -2
    # Those returning to the ravaged land, whether they campaigned or not
    # (LoM p. 103).
    knight.campaign_seasons = []
    assert living.chevauchee_aging(saga, knight) == -2
    knight.campaign_seasons = ["1220 Summer"]
    assert character_effects._camp_disease(saga, knight, 1220, random.Random(1)) == []
    knight.campaign_seasons = [
        f"1220 {s}" for s in ("Spring", "Summer", "Autumn", "Winter")
    ]
    told = character_effects._camp_disease(saga, knight, 1220, random.Random(1))
    assert told and told[0].startswith("A year with the army: Bloody Flux")


def test_a_mounted_charge_adds_the_ability_and_may_unhorse():
    """Lords of Men pp. 126-127: the Combat Ability on the Attack, the
    horse's Fatigue, and the shock of the charge on a smaller target."""
    import random

    from ars_magica_manager.models import Combatant, Fight, FightSide
    from ars_magica_manager.rules import fight as fight_rules

    knight = Combatant("Knight", attack=10, ability=4, damage=6, mounted=True, ride=3)
    rider = Combatant("Rider", defence=5, soak=2, mounted=True, ride=0)
    fight = Fight(
        "Joust",
        sides=[FightSide("A", combatants=[knight]), FightSide("B", combatants=[rider])],
    )
    saga = Saga(id="s", name="S", fights=[fight])
    units = fight_rules.units(saga, fight)
    chances = fight_rules.odds(saga, fight, units[knight.id], units[rider.id], "Charge")
    assert any(t.label == "Charge" and t.amount == 4 for t in chances.attack)

    class Low(random.Random):
        def randrange(self, *_a, **_k):
            return 2

    blow = fight_rules.Blow("Charge", horse_size=2)
    told = fight_rules.shock_of_the_charge(saga, blow, units[rider.id], 8, Low())
    assert told and "unhorsed" in told[0]
    assert not rider.mounted


def _siege_living_at(saga, miner, siege, days: int) -> int:
    from ars_magica_manager.rules import living

    siege.days = days
    return living.siege_living(saga, miner)


def test_a_siege_year_counts_only_the_days_that_fall_in_it():
    from ars_magica_manager.rules import living

    assert living.siege_days_in("Winter", 1220, 120, 1220) == 91
    assert living.siege_days_in("Winter", 1220, 120, 1221) == 29


def test_siege_experts_castles_outworks_and_engines():
    """Lords of Men pp. 111-116: a siege from a lord's castle, experts as
    characters, the garrison's engines, several walls, outworks, life
    inside and the Veronese Flag."""
    import random

    from ars_magica_manager import siege_actions, sieges
    from ars_magica_manager.models import Ability, Neighbour, Outwork
    from ars_magica_manager.rules import siege as rules

    lord = Neighbour(id="l", name="Count", kind="lord")
    lord.details["castles"] = [
        {
            "name": "Burg",
            "kind": "great",
            "groups": 30,
            "supply": "Superior",
            "moat": True,
        }
    ]
    miner = Character(id="m", name="Hans", type="grog")
    miner.characteristics.intelligence = 1
    miner.abilities = [Ability("Profession: Miner", xp=15)]
    saga = Saga(
        id="s", name="S", current_year=1220, characters=[miner], neighbours=[lord]
    )
    siege = Siege("New")
    sieges._fill_from_castle(saga, siege, "l:0")
    assert (
        siege.castle,
        siege.defenses,
        siege.garrison,
        siege.supplies,
        siege.moat,
    ) == (
        "Burg",
        "Excellent",
        30,
        "Superior",
        True,
    )
    siege.experts = {"sapper": "m"}
    found = rules.expert(saga, siege, "sapper")
    assert (found.total, found.botch_dice) == (3, 3)  # Int 1 + Miner 2
    miner.abilities = []
    assert rules.expert(saga, siege, "sapper").problem
    # The garrison's engines destroy one besieger mangonel a hit.
    siege.engines = {"Mangonel": 2}
    siege.garrison_engines = {"Trebuchet": 1}
    siege.garrison_gunner = 10
    rules.counter_battery(siege, "Mangonel", random.Random(1), saga)
    assert siege.engines.get("Mangonel", 0) <= 1
    # Each group picks the engine it fires at (LoM p. 116).
    siege.engines = {"Mangonel": 1, "Trebuchet": 1}
    siege.garrison_engines = {"Trebuchet": 6}
    siege.garrison_gunner = 30
    targets = ["Trebuchet", "Trebuchet"]  # its two groups, of five and one
    rules.counter_battery(siege, "Mangonel", random.Random(1), saga, targets)
    assert siege.engines == {"Mangonel": 1}
    # Several walls: one group of five at the North, one at the East.
    siege.engines = {"Mangonel": 10}
    siege.gunner = 30
    rules.bombard(siege, 0, random.Random(2), saga, [0, 1])
    assert siege.walls is not None and siege.walls[0] < rules.full_wall(siege)
    assert siege.walls[1] < rules.full_wall(siege)
    # An outwork is struck first, and taken by an escalade won.
    siege.outworks = [Outwork("The Accursed Tower")]
    sieges.play_event(
        siege, {"event": rules.ESCALADE, "result": "won"}, random.Random(3), saga
    )
    assert siege.outworks[0].taken and rules.outwork(siege) is None
    # Inside the walls: -2 Living Conditions for the year.
    siege.inside = ["m"]
    siege.year, siege.season = 1220, "Spring"
    saga.sieges = [siege]
    # Only once a season, 91 days, of it falls in the year (LoM p. 112).
    assert [_siege_living_at(saga, miner, siege, d) for d in (90, 91)] == [0, -2]
    # Raise the Veronese Flag: no wall looks undefended until sunset.
    siege.besieger_walls = [1, 0, 0, 0]
    siege.garrison_walls = [0, 0, 0, 0]
    assert siege_actions.undefended(siege) == [0]
    siege_actions.supplies_story(saga, siege).apply({"story": siege_actions.SPELL_FLAG})
    assert siege_actions.undefended(siege) == []


def test_an_escalade_fought_as_one_battle():
    """Lords of Men pp. 114-115: the wall's troops only, the Garrison row
    and Defense Bonus for the garrison, no baggage, a step of Garrison lost
    for each besiegers' win, a breach at a Shoddy wall."""
    import random

    from ars_magica_manager import battle_muster, battles, siege_actions, sieges
    from ars_magica_manager.rules import siege as rules

    siege = Siege("S", castle="Burg", garrison=25, defenses="Shoddy")
    siege.besieger_walls = [4, 0, 0, 0]
    siege.garrison_walls = [3, 2, 2, 2]
    knight = Character(id="k", name="Sir Konrad", type="companion")
    saga = Saga(id="s", name="S", characters=[knight], sieges=[siege])
    sieges.play_event(
        siege, {"event": rules.ESCALADE, "one_battle": True}, random.Random(1), saga
    )
    (entry,) = saga.battles
    assert [s.groups for s in entry.sides] == [4, 3]
    # Garrison 25: Weight of Numbers +3 for the garrison; Defense Bonus +1.
    assert battles.weight(entry, 0) == -3 and battles.territorial(entry, 1) == 1
    form = battles.event_form(saga, entry)
    values = {f.key: f.value for f in form.fields()}
    values |= {"who": "k", "side": "0", "enemy": "Baggage"}
    assert form.validate(values)
    values |= {"enemy": "Standard", "maneuver": "Attack", "condition_Attack": "routed"}
    form.apply(values)
    assert siege.garrison == 20  # a step down
    battle_muster.end_of_day(saga, entry).apply({"how": "won", "side": "0"})
    assert siege.ended == "Breached"
    assert hasattr(siege_actions.actions(saga, siege), "apply")  # The Castle Taken


def test_a_found_child_is_added_and_opening_the_arts_makes_the_apprentice():
    """DE pp. 269-271: a search's Gifted child becomes a character, and the
    magus claims his apprentice the season he opens the Arts; at double the
    Lab Total a Supernatural Ability becomes a Hermetic Virtue."""
    from ars_magica_manager.models import SeasonPlan
    from ars_magica_manager.rules import activities
    from ars_magica_manager.rules import apprentice_seasons as aps
    from ars_magica_manager.seasons import advance

    magus = Character(id="m", name="Leandro", type="magus", covenant_id="c")
    magus.hermetic.house = "house_bonisagus"
    saga = Saga(id="s", name="S", characters=[magus])
    plan = SeasonPlan("m", 1220, "Summer", aps.SEARCH)
    found = activities.Outcome("m", plan, None, found_child=True)
    advance._found_child(saga, magus, found)
    child = saga.characters[-1]
    assert child.background.year_born == 1213 and child.in_creation
    assert any(vf.vf_id == "vf_the_gift" for vf in child.virtues_flaws)
    work = aps.ApprenticeWork(converted=["vf_affinity_with_art"])
    told = aps.open_arts(child, work, magus)
    ids = [vf.vf_id for vf in child.virtues_flaws]
    assert aps.APPRENTICE in ids and "vf_affinity_with_art" in ids
    assert (
        child.hermetic.parens == "Leandro" and child.hermetic.house == "house_bonisagus"
    )
    assert any("claims" in line for line in told)


def test_each_supernatural_ability_converts_into_a_virtue_of_its_size():
    """DE p. 271: each Ability is kept or converted, Major for Major and
    Minor for Minor; an old save's single conversion still loads."""
    from ars_magica_manager.models import Ability, SeasonPlan, VirtueFlawInstance
    from ars_magica_manager.rules import apprentice_seasons as aps

    child = Character(id="c", name="Kaspar", type="companion")
    child.virtues_flaws.append(VirtueFlawInstance("vf_second_sight"))
    child.abilities.append(Ability("Second Sight", "Supernatural", xp=5))
    assert aps.supernatural_tiers(child) == ["Minor"]
    assert aps.conversion_problem(child, ["vf_affinity_with_art"]) == ""
    assert "of its own size" in aps.conversion_problem(child, ["vf_chthonic_magic"])
    assert "convert each into one" in aps.conversion_problem(
        child, ["vf_affinity_with_art", "vf_affinity_with_art"]
    )
    old = SeasonPlan.from_dict(
        {
            "character_id": "m",
            "year": 1220,
            "season": "Summer",
            "activity": aps.OPEN_ARTS,
            "convert_to": "vf_affinity_with_art",
        }
    )
    assert old.conversions == ["vf_affinity_with_art"]


def test_a_grogs_story_experience_is_given_at_once_and_counted():
    """Grogs p. 67: story experience is applied when received, and each
    award takes a season of the Winter update; an Adventure's award is 5 to
    10, at most 5 to one Ability (DE p. 376)."""
    from ars_magica_manager.forms import grog_story
    from ars_magica_manager.models import Ability
    from ars_magica_manager.seasons import advance

    grog = Character(id="g", name="Hans", type="grog", covenant_id="c")
    grog.abilities = [Ability("Single Weapon", xp=15), Ability("Awareness", xp=5)]
    saga = Saga(id="s", name="S", characters=[grog])
    too_much = {"ability_0": "Single Weapon", "xp_0": 6}
    assert grog_story.problem(too_much)
    values = {
        "story": "Wolves",
        "ability_0": "Awareness",
        "xp_0": 5,
        "ability_1": "Single Weapon",
        "xp_1": 3,
    }
    assert grog_story.problem(values) is None
    grog_story.apply(saga, grog, values)
    assert [a.xp for a in grog.abilities] == [18, 10]
    assert grog.grog_year is not None and grog.grog_year.story_awards == 1
    assert grog.diary[-1].name == "Story experience: Wolves"
    # Nothing chosen for the year: the default runs, less a season's exposure.
    saga.current_season = "Winter"
    advance.year_end_grogs(saga)
    assert grog.abilities[0].xp == 18 + 8 - 2
    assert grog.grog_year.story_awards == 0
    # A second award takes the vocational season's 7 (Grogs p. 67).
    from ars_magica_manager.seasons.defaults import grog_awards_cost

    assert [grog_awards_cost(n) for n in range(5)] == [0, 2, 9, 13, 15]


def test_a_new_grog_joins_the_covenants_turb():
    from ars_magica_manager import creation
    from ars_magica_manager.models import Covenant

    saga = Saga(
        id="s", name="S", covenants=[Covenant(id="c", saga_id="s", name="Rabenstein")]
    )
    grog = creation.add_character(saga, "Hans", "grog", "c")
    (row,) = saga.covenants[0].inhabitants
    assert row.kind == creation.NEW_GROG_KIND and row.character_id == grog.id
    creation.add_character(saga, "Maria", "companion", "c")
    assert len(saga.covenants[0].inhabitants) == 1


def test_a_school_limits_the_academic_abilities_it_teaches():
    """Art & Academe p. 79: major subjects to the school's limit, minor to
    half (rounded up), the rest it doesn't teach to 0."""
    from ars_magica_manager.models import VirtueFlawInstance
    from ars_magica_manager.rules import creation_access as ca

    scholar = Character(id="x", name="Alcuin", type="companion")
    scholar.virtues_flaws.append(
        VirtueFlawInstance("vf_educated", params={"school": "cathedral school"})
    )
    caps = {
        a: ca.ability_cap_for(scholar, 40, a)
        for a in ("Theology: Christian", "Philosophiae", "Medicine", "Common Law")
    }
    assert caps == {
        "Theology: Christian": 6,
        "Philosophiae": 3,
        "Medicine": 0,
        "Common Law": 7,
    }
    scholar.virtues_flaws[0].params = {"school": ""}
    assert ca.ability_cap_for(scholar, 40, "Medicine") == 7
    # A municipal school's major is Medicine or Civil Law: one, not both.
    scholar.virtues_flaws[0].params = {"school": "municipal school (italy), medicine"}
    assert ca.ability_cap_for(scholar, 40, "Medicine") == 5
    assert ca.ability_cap_for(scholar, 40, "Civil and Canon Law") == 0


def test_a_companion_with_a_council_vote_counts_zero_in_base_loyalty():
    """Covenants p. 38: Semita Errabunda's -225 over six is -38; with a
    companion on the council, over seven, -32.1, rounded to the nearest as
    the book does: -32. A specialist with a full vote counts too."""
    from ars_magica_manager import inhabitants as inh
    from ars_magica_manager.models import Covenant, Inhabitant

    covenant = Covenant(id="c", saga_id="s", name="Semita Errabunda")
    gifts = ["Blatant"] + ["Normal"] * 4 + ["None"]
    covenant.inhabitants = [
        Inhabitant(id=f"m{i}", kind="magus", name=f"M{i}", gift=g)
        for i, g in enumerate(gifts)
    ]
    saga = Saga(id="s", name="S", covenants=[covenant])
    assert inh.base_loyalty(saga, covenant) == -38
    covenant.inhabitants.append(
        Inhabitant(id="k", kind="companion", name="Konrad", on_council=True)
    )
    assert inh.base_loyalty(saga, covenant) == -32
    covenant.inhabitants.append(
        Inhabitant(id="s", kind="specialist", name="Odo", on_council=True)
    )
    assert inh.base_loyalty(saga, covenant) == -28


def test_a_grog_plans_a_season_of_copying_and_it_takes_a_season_of_the_year():
    """DE p. 380: a covenant scribe's copying is planned; Grogs p. 67: the
    season it takes comes off the yearly update."""
    from ars_magica_manager.models import Ability, GrogYear
    from ars_magica_manager.rules import activities, book_seasons
    from ars_magica_manager.seasons import advance

    grog = Character(id="g", name="Wido", type="grog", covenant_id="c")
    grog.abilities = [Ability("Profession: Scribe", xp=30), Ability("Brawl", xp=5)]
    grog.grog_year = GrogYear(exposure="Brawl", exposure_2="Brawl")
    keys = {a.key for a in activities.activities_for(grog)}
    assert keys == {book_seasons.COPY_BOOK, book_seasons.COPY_TEXTS}
    plan = SeasonPlan("g", 1220, "Spring", book_seasons.COPY_BOOK)
    assert not any("Grogs aren't" in p for p in activities.problems(grog, plan))
    fight = SeasonPlan("g", 1220, "Spring", activities.PRACTICE)
    assert any("Grogs aren't" in p for p in activities.problems(grog, fight))
    advance._count_grog_season(grog)
    saga = Saga(id="s", name="S", characters=[grog])
    saga.current_season = "Winter"
    advance.year_end_grogs(saga)
    # The first exposure is taken: only the second's 2 xp is added.
    assert grog.abilities[1].xp == 7
    assert grog.grog_year.copying == 0


def test_joining_a_tradition_in_play_brings_its_virtues_not_its_opening():
    from ars_magica_manager.forms import menu
    from ars_magica_manager.models import VirtueFlawInstance

    witch = Character(id="w", name="Grete", type="companion")
    witch.virtues_flaws.append(VirtueFlawInstance("vf_the_gift"))
    told = menu.apply_character_traditions(
        witch, {menu.TRADITION_KEY + "trad_folk_witches": True}
    )
    assert "trad_folk_witches" in witch.traditions
    assert "vf_folk_witch" in {vf.vf_id for vf in witch.virtues_flaws}
    # The Opening is a master's season, not joining's (HMR p. 7).
    assert not {"Cursing", "Flight"} & {a.name for a in witch.abilities}
    assert any("Opened by a Gifted master" in line for line in told)
    # Ticked again, nothing more is added.
    assert (
        menu.apply_character_traditions(
            witch, {menu.TRADITION_KEY + "trad_folk_witches": True}
        )
        == []
    )
    assert "Cursing" not in {a.name for a in witch.abilities}


def test_a_hook_suggests_a_story_accepted_as_a_story_event():
    from ars_magica_manager import catalog
    from ars_magica_manager.forms import hook_stories
    from ars_magica_manager.models import Covenant, VirtueFlawInstance

    covenant = Covenant(id="c", saga_id="s", name="Rabenstein")
    hook = next(
        e
        for e in catalog.load_covenant_boon_hook_catalog()
        if e.type == "Hook" and e.name == "Monster"
    )
    covenant.boons_hooks = [
        VirtueFlawInstance(hook.id, params={"detail": "the wyrm of the Danube"})
    ]
    saga = Saga(id="s", name="S", covenants=[covenant])
    form = hook_stories.story_form(saga, covenant)
    fields = {f.key: f for f in form.fields()}
    assert "the wyrm of the Danube" in fields["title"].value
    values = {k: f.value for k, f in fields.items()}
    form.apply(values)
    entry = covenant.diary[-1]
    assert entry.status == "Open" and entry.boon_hook_id == covenant.boons_hooks[0].id
    assert saga.calendar[-1].covenant_id == "c"


def test_building_a_ship_by_a_shipwright_and_opening_her():
    """HP pp. 62-67; City & Guild pp. 67-69."""
    import random

    from ars_magica_manager.forms import ship_build
    from ars_magica_manager.models import Ability, Characteristics, Covenant
    from ars_magica_manager.rules import ship_building as sb
    from ars_magica_manager.rules.xp import ability_xp

    assert [sb.seasons_to_build(s) for s in (4, 5, 7, 10)] == [3, 2, 2, 1]
    assert sb.opening(5, ["mast", "rudder"]) == (10, 26)
    assert sb.craft_magic_ease("large_cog") == 27
    # A ship the table doesn't name has her Ease Factor typed (HP p. 63).
    assert sb.craft_magic_ease("medium_cog") is None
    assert ship_build.problem(
        Saga(id="x", name="X", characters=[Character(id="w", name="M", type="magus")]),
        {"builder": "w", "method": sb.CRAFT_MAGIC, "ship_type": "medium_cog"},
    )
    covenant = Covenant(id="c", saga_id="s", name="Oculus")
    wright = Character(id="w", name="Marcus", type="companion", covenant_id="c")
    wright.characteristics = Characteristics(intelligence=3)
    wright.abilities = [Ability("Profession: Shipwright", xp=ability_xp(5))]
    saga = Saga(id="s", name="S", characters=[wright], covenants=[covenant])
    values = {
        "name": "The Hermes",
        "ship_type": "buss",
        "method": sb.SHIPWRIGHT,
        "builder": "w",
        "innovation": 2,
        "raw_materials": 2,
    }
    ship_build.build(saga, covenant, values, random.Random(1))
    (record,) = [p for p in covenant.possessions if p.kind == "ship"]
    assert record.ship is not None and record.ship.quality == "Superior"
    assert saga.calendar[-1].title == "The Hermes is finished"


def test_a_melee_event_rolls_the_table_and_says_the_fair_ransom():
    """Lords of Men pp. 67-68."""
    import random

    from ars_magica_manager import melee_events
    from ars_magica_manager.models import ScoredTrait
    from ars_magica_manager.rules import tournament

    assert tournament.ransom_due(tournament.melee_event(11)).startswith("his horse and")
    knight = Character(id="k", name="Guy", type="companion")
    knight.reputations = [ScoredTrait("Prudhomme", 3)]
    saga = Saga(id="s", name="S", characters=[knight])
    lines = melee_events.roll(saga, knight, {"events": 1}, random.Random(4))
    assert lines and knight.diary[-1].name == "Melee Event: Guy"


def test_a_lord_pays_for_a_manor_from_his_coin_or_by_installments():
    """Lords of Men p. 85."""
    from ars_magica_manager import lords, manors
    from ars_magica_manager.models import Neighbour

    lord = Neighbour(id="l", name="Godfrey", kind="lord", details={"coin": 900})
    saga = Saga(id="s", name="S", neighbours=[lord])
    assert manors._buy_problem(saga, lord, {"price": 1000, "pay": True})
    manors.buy(saga, lord, {"name": "Elm", "price": 800, "pay": True})
    assert lords.coin(lord) == 100
    lines = manors.buy(saga, lord, {"name": "Oak", "price": 800, "pay": False})
    assert any("installments" in line for line in lines)


def test_a_certamen_duel_ends_in_a_fall_or_a_concession():
    """DE pp. 231-233: Moratamis and Carolus, Rego Terram."""
    import random

    from ars_magica_manager.forms import certamen_duel
    from ars_magica_manager.models import ArtScore, Characteristics
    from ars_magica_manager.rules.xp import art_xp

    def magus(cid, name, re, te, pre, per):
        m = Character(id=cid, name=name, type="magus")
        m.characteristics = Characteristics(presence=pre, perception=per, stamina=1)
        m.arts = {"rego": ArtScore(xp=art_xp(re)), "terram": ArtScore(xp=art_xp(te))}
        return m

    mora = magus("m", "Moratamis", 8, 0, 2, 3)
    caro = magus("c", "Carolus", 7, 6, -1, -1)
    saga = Saga(id="s", name="S", characters=[mora, caro])
    values = {
        "rival": "c",
        "technique": "Rego",
        "form": "Terram",
        "concede": "3",
        "their_concede": "3",
        "take_fatigue": True,
    }
    lines = certamen_duel.duel(saga, mora, values, random.Random(2))
    assert any("wins" in line or "draw" in line for line in lines)
    assert mora.diary[-1].name.startswith("Certamen: Moratamis and Carolus")
    # The loser conceded at -3 (Tired) or fell; the Fatigue is on the sheets.
    levels = (mora.fatigue_level, caro.fatigue_level)
    assert "tired" in levels or "unconscious" in levels
    # A botch stops the duel for the storyguide (DE p. 231).
    from ars_magica_manager.rules import certamen_duel as cd

    class Faces(random.Random):
        def __init__(self, *faces: int) -> None:
            super().__init__(0)
            self.faces = list(faces)

        def randrange(self, *_a, **_k) -> int:  # type: ignore[override]
            return self.faces.pop(0) if self.faces else 5

    # Initiative 5 and 5; then the first attacker's die 0 and botch die 0.
    duel = cd.play(
        saga, cd.Plan(mora), cd.Plan(caro), "Rego", "Terram", Faces(5, 5, 0, 0)
    )
    assert duel.winner is None and "botches in round 1" in duel.how


def test_the_grand_tribunal_counts_its_delegates():
    """DE p. 22: three from each regional Tribunal, and the Primi."""
    from ars_magica_manager import meeting
    from ars_magica_manager.tribunal_packages import grand

    rhine = Tribunal(id="rh", name="Rhine")
    great = Tribunal(id="gt", name="The Grand Tribunal", package=grand.KEY)
    saga = Saga(id="s", name="S", tribunals=[rhine, great])
    held: dict = {"year": 1228, "season": "Summer"}
    assert "not quorate" in meeting.quorum(saga, great, held)
    # Any legal Tribunal's quorum: twelve magi, four covenants, a Quaesitor.
    grand.delegates(great).extend(
        [
            {"name": f"Delegate {n}", "sent_by": "rh", "covenant": f"C{n % 4}"}
            for n in range(11)
        ]
        + [{"name": "Primus", "house": "house_guernicus", "sent_by": ""}]
    )
    assert "it needs 4 covenants" not in meeting.quorum(saga, great, held)
    assert meeting.quorum(saga, great, held).endswith(": quorate")
    assert len(grand.envoys(saga, great, held)) == 12
    grand.delegates(great).pop()
    assert "a Quaesitor" in meeting.quorum(saga, great, held)
    # The Primus of Bonisagus named as a magus of the saga is the Praeco.
    saga.characters.append(Character(id="pb", name="Primus Bon", type="magus"))
    grand.delegates(great).append(
        {"name": "Primus Bon", "house": "house_bonisagus", "character_id": "pb"}
    )
    grand.officers(great)
    assert great.praeco_id == "pb"


def test_a_wizards_war_ends_and_its_winner_earns_acclaim():
    """DE p. 21; HoH: Societates p. 31: twice the foe's highest Reputation."""
    from ars_magica_manager.forms import wizards_war
    from ars_magica_manager.models import ScoredTrait
    from ars_magica_manager.rules import acclaim as ac
    from ars_magica_manager.rules import hermetic_law

    flambeau = Character(id="f", name="Ignatius", type="magus")
    flambeau.hermetic.house = ac.FLAMBEAU
    foe = Character(id="t", name="Tytus", type="magus")
    foe.reputations = [ScoredTrait("Liar", 2)]
    war = Case(
        "Ignatius on Tytus",
        kind=hermetic_law.WAR,
        brought_by="Ignatius",
        against="Tytus",
        filed_year=1220,
        filed_season="Spring",
        month=1,
    )
    rhine = Tribunal(id="rh", name="Rhine", cases=[war])
    saga = Saga(id="s", name="S", characters=[flambeau, foe], tribunals=[rhine])
    assert wizards_war.is_war(rhine, 0)
    wizards_war.apply(
        saga,
        rhine,
        war,
        {"outcome": "declarer_won", "declarer_brave": 2, "declarer_foe_reputation": 2},
    )
    held = ac.acclaim_of(flambeau)
    assert war.status == "decided" and held is not None and held.deeds + held.score > 0
    assert foe.diary[-1].name.startswith("War's End")


def test_a_secret_society_s_members_lean_with_it_at_a_meeting():
    """Secret societies as factions: a cult's attitude toward a troupe
    covenant sets how its members' covenants lean."""
    from ars_magica_manager import meeting
    from ars_magica_manager.models import Ability, Attitude, Covenant, MysteryCult

    troupe = Covenant(id="t", saga_id="s", name="Rabenstein", played=True)
    other = Covenant(id="o", saga_id="s", name="Fengheld", played=False)
    member = Character(id="m", name="Ida", type="magus", covenant_id="o")
    member.abilities = [Ability("Spinner's Lore")]
    cult = MysteryCult("saga_cult_spinners", "The Spinners", "Spinner's Lore")
    cult.attitudes = [Attitude("t", -2)]
    saga = Saga(
        id="s",
        name="S",
        covenants=[troupe, other],
        characters=[member],
        custom_cults=[cult],
    )
    case = Case("A charge", brought_by="Rabenstein", against="Someone")
    side, why = meeting.leaning_why(saga, case, other)
    assert side == meeting.AGAINST and "The Spinners" in why


def test_a_magus_away_from_home_casts_in_the_aura_he_is_in():
    """DE pp. 410-411: a foreign aura counts where he casts."""
    from ars_magica_manager.forms import whereabouts
    from ars_magica_manager.models import Covenant
    from ars_magica_manager.rules import realms

    home = Covenant(id="c", saga_id="s", name="Rabenstein", aura=5)
    magus = Character(id="m", name="Leandro", type="magus", covenant_id="c")
    saga = Saga(id="s", name="S", covenants=[home], characters=[magus])
    assert realms.present_aura(saga, magus) == realms.home_aura(saga, magus)
    assert whereabouts.where_line(saga, magus) == (
        "At home, at Rabenstein: a Magic aura of 5."
    )
    whereabouts.apply(saga, magus, {"where": "typed", "aura": 4, "realm": "Divine"})
    assert realms.present_aura(saga, magus) == (4, "Divine")
    assert realms.home_aura(saga, magus)[1] == "Magic"
    assert whereabouts.where_line(saga, magus) == (
        "Away from home: a Divine aura of 4."
    )
    whereabouts.apply(saga, magus, {"where": "home"})
    assert not realms.away(magus)


def test_crossing_the_threshold_counts_the_circumstances_points():
    """RoP: Faerie pp. 21-23: Branoic on Goat Hill, Faerie aura 5."""
    from ars_magica_manager.forms import threshold
    from ars_magica_manager.models import Neighbour
    from ars_magica_manager.rules import faerie_threshold as ft

    hill = Neighbour(
        id="h", name="Goat Hill", kind="place", realm="Faerie", details={"aura": 5}
    )
    saga = Saga(id="s", name="S", neighbours=[hill], books_in_play=["RoP:F"])
    assert threshold.offers(saga, hill) and threshold.strength(hill, 0) == 24
    wedding = next(k for k in ft.LIFE_CHANGES if "religious" in k)
    confluence = next(k for k in ft.BORDERS if k.startswith("Minor"))
    values = {"level": "0", "life_change": wedding, "border": confluence}
    assert threshold.points(saga, values) == 24
    lines = threshold.apply(saga, hill, values)
    assert "the Threshold comes" in lines[0]


def test_a_vampire_records_its_precautions_limitations_and_death():
    """Against the Dark pp. 115-117."""
    from ars_magica_manager.forms import creature as creature_forms
    from ars_magica_manager.models import Creature
    from ars_magica_manager.sheets import creature as creature_sheet

    vampire = Creature(id="v", name="Platenik", realm="Faerie")
    saga = Saga(id="s", name="S", creatures=[vampire])
    keys = {f.key for f in creature_forms.info_fields(saga, vampire)}
    assert {"vampire_precautions", "vampire_limitations", "vampire_death"} <= keys
    vampire.vampire_death = "Decapitate the body"
    facts = {f.label: f.value for f in creature_sheet.faerie_role_facts(vampire)}
    assert facts["Killed for good by"] == "Decapitate the body"


def test_the_desktop_places_reputations_health_and_aging_actions():
    """Bug 3: a desktop page focuses no section, so a placed action is
    offered as its section would offer it."""
    from ars_magica_manager.actions import NodeKind
    from ars_magica_manager.forms import menu
    from ars_magica_manager.models import Covenant, ScoredTrait

    covenant = Covenant(id="c", saga_id="s", name="Keep")
    magus = Character(id="m", name="Leandro", type="magus", covenant_id="c")
    magus.reputations.append(ScoredTrait("Brave", 2))
    saga = Saga(id="s", name="S", characters=[magus], covenants=[covenant])
    page = menu.Page(saga, NodeKind.CHARACTER, covenant=covenant, character=magus)
    labels = {
        spot: [i.label for i in menu.placed(page, spot)]
        for spot in (deeds.SESSION, deeds.KNIGHTLY, "Health", "Aging")
    }
    assert "Reputation Roll" in labels[deeds.SESSION]
    assert "Melee Event" in labels[deeds.KNIGHTLY]
    assert labels["Health"] == ["Take Harm", "Recovery Roll"]
    assert "Place Aging Points" in labels["Aging"]
