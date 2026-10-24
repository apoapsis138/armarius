"""Massed combat (Lords of Men): Weight of Numbers, Event Totals, losses
and raising an army."""

from ars_magica_manager.commands import Refuse
from ars_magica_manager.rules import battle


def test_weight_of_numbers_by_the_ratio_of_the_armies():
    assert [battle.weight_of_numbers(n, 10) for n in (10, 14, 15, 20, 30, 40, 90)] == [
        0,
        0,
        1,
        2,
        3,
        4,
        4,
    ]
    assert battle.weight_of_numbers(10, 20) == -2
    assert battle.weight_of_numbers(0, 20) == 0


def test_an_event_total_against_its_stage():
    # The book's example: Stamina +2, Leadership 4, Territorial Advantage 1
    # and no Weight of Numbers need an Event Bonus of 2 for Engaged (9).
    event = battle.Event(2, 4, 1, 0, "Defend", "Standard", "Even")
    assert (event.bonus, event.total) == (2, 9)
    assert event.can_win(0) and not event.can_win(1)
    assert battle.ease_factor(5) == 15
    shy = battle.Event(
        2, 4, 1, 0, "Defend", "Standard", "Lesser", gave_up_initiative=True
    )
    assert shy.total == 9
    short = battle.Event(2, 4, 1, 0, "Defend", "Standard", "Even", baggage_short=2)
    assert short.total == 7


def test_the_book_s_example_events_have_their_bonuses():
    examples = {
        ("Defend", "Inexpensive", "Lesser"): 0,
        ("Defend", "Standard", "Even"): 2,
        ("Run the Gauntlet", "Special", "Lesser"): 5,
        ("Take", "Special", "Outnumbered"): 8,
        ("Heroic Gesture", "Special", "I Stand Alone"): 11,
    }
    for (maneuver, enemy, size), bonus in examples.items():
        assert battle.event_bonus(maneuver, enemy, size) == bonus


def test_losses_and_group_sizes_follow_the_weight_of_numbers():
    assert battle.losses("Outnumbered", 2) == 4
    assert battle.losses("Outnumbered", -2) == 0
    assert battle.group_members(2, ours=True) == 7
    assert battle.group_members(2, ours=False) == 5
    assert battle.group_members(-3, ours=False) == 8


def test_raising_an_army():
    assert battle.allied_proportion(5) == (0, "None")
    assert battle.allied_proportion(13) == (1, "Equal")
    assert battle.allied_groups(9, 7) == 4  # half, rounded down
    assert battle.allied_groups(9, 24) == 27
    assert battle.mercenary_cost({"knights": 2, "infantry": 5, "levies": 3}) == 43
    assert [battle.baggage_needed(n) for n in (0, 1, 10, 11)] == [0, 1, 1, 2]


def _lord_battle():
    from support import everything_saga

    saga = everything_saga()
    entry = saga.battles[0]
    entry.events = []
    return saga, entry


def test_a_lord_s_battle_records_its_events_and_losses():
    from ars_magica_manager import battles, lords
    from ars_magica_manager.commands import Form

    saga, entry = _lord_battle()
    lord = saga.neighbour("gottfried")
    assert lord is not None
    assert "section-nb-battles" in [k.section_id for k in lords.TAB.lists]
    assert battles.involving(saga, lord) == [entry]
    assert (battles.weight(entry), battles.territorial(entry)) == (2, 2)
    assert battles.grid(saga, lord).rows[0][2:] == ["40 v 20", "+2", "+2", "none yet"]
    form = battles.event_for(saga, lord, 0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values |= {"who": "comp1", "size": "Outnumbered", "result": "won"}
    assert "Engaged, Ease Factor 9" in battles.event_live(saga, entry, values)
    form.apply(values)
    assert entry.sides[1].groups == 16  # Outnumbered (2) x Weight of Numbers (2)
    assert battles.record_text(entry) == "1 won, 0 lost"
    assert "1. Engaged (9)" in battles.info_for(saga, lord, 0)
    # The next event is the second stage's, against the smaller army.
    values["result"] = "lost"
    battles.event_form(saga, entry).apply(values)  # type: ignore[union-attr]
    assert entry.sides[0].groups == 40  # the enemy, outnumbered, takes no extra toll
    assert battles.record_text(entry) == "1 won, 1 lost"


def test_a_battle_short_of_baggage_lowers_its_event_totals():
    from ars_magica_manager import battles

    saga, entry = _lord_battle()
    entry.sides[0].baggage = 1
    assert battles.baggage_short(entry) == 3
    values = {"who": "comp1", "maneuver": "Defend", "enemy": "Standard", "size": "Even"}
    event = battles.event_of(saga, entry, values)
    assert event is not None and event.baggage_short == 3
    lord = saga.neighbour("gottfried")
    assert lord is not None
    assert isinstance(battles.event_for(saga, lord, 5), Refuse)
    assert isinstance(battles.event_form(saga, None), Refuse)


def test_an_older_saves_lord_battles_move_to_the_saga():
    from ars_magica_manager.models import Saga

    data = {
        "id": "old",
        "name": "Old",
        "neighbours": [
            {
                "id": "gottfried",
                "name": "Gottfried",
                "kind": "lord",
                "details": {
                    "battles": [
                        {
                            "name": "The ford at Werl",
                            "enemy": "the Count of Mark",
                            "ours": 40,
                            "theirs": 20,
                            "our_deployment": 12,
                            "their_deployment": 10,
                            "baggage": 4,
                            "events": [
                                {
                                    "who": "comp1",
                                    "maneuver": "Attack",
                                    "enemy": "Standard",
                                }
                                | {
                                    "size": "Even",
                                    "total": 11,
                                    "won": True,
                                    "losses": 2,
                                }
                            ],
                        }
                    ]
                },
            }
        ],
    }
    saga = Saga.from_dict(data)
    assert "battles" not in saga.neighbours[0].details
    [entry] = saga.battles
    first, second = entry.sides
    assert (first.neighbour_id, first.groups, first.deployment, first.baggage) == (
        "gottfried",
        40,
        12,
        4,
    )
    assert (second.name, second.groups, second.deployment) == (
        "the Count of Mark",
        20,
        10,
    )
    assert [(e.maneuver, e.total, e.won) for e in entry.events] == [
        ("Attack", 11, True)
    ]


def test_a_battle_between_two_lords_writes_both_their_diaries():
    from support import everything_saga

    from ars_magica_manager import battles, place_events
    from ars_magica_manager.models import Battle, BattleSide, Neighbour

    saga = everything_saga()
    mark = Neighbour(id="mark", name="Count of Mark", kind="lord")
    saga.neighbours.append(mark)
    entry = Battle(
        "Werl",
        sides=[
            BattleSide(neighbour_id="gottfried", groups=20),
            BattleSide(neighbour_id="mark", groups=20),
        ],
    )
    saga.battles = [entry]
    assert battles.side_name(saga, entry, 1) == "Count of Mark"
    assert battles.involving(saga, mark) == [entry]
    form = battles.event_for(saga, mark, 0)
    values = {f.key: f.value for f in form.fields()}  # type: ignore[union-attr]
    form.apply(values | {"who": "comp1", "side": "1", "result": "won"})  # type: ignore[union-attr]
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    for lord in (gottfried, mark):
        assert place_events.diary(lord)[-1]["text"].startswith("Werl: Engaged")
    assert saga.character("comp1").diary[-1].name == "Werl"  # type: ignore[union-attr]
