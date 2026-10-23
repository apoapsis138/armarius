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


def test_a_lord_s_battle_records_its_events_and_losses():
    from support import everything_saga

    from ars_magica_manager import battles, lords
    from ars_magica_manager.commands import Form

    saga = everything_saga()
    lord = saga.neighbours[0]
    assert "section-nb-battles" in [k.section_id for k in lords.TAB.lists]
    entry = battles.battles(lord)[0]
    assert (battles.weight(entry), battles.territorial(entry)) == (2, 2)
    assert battles.grid(saga, lord).rows[0][2:] == ["40 v 20", "+2", "+2", "none yet"]
    form = battles.event_form(saga, lord, 0)
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields()}
    values |= {"who": "comp1", "size": "Outnumbered", "result": "won"}
    assert "Engaged, Ease Factor 9" in battles.event_live(saga, entry, values)
    form.apply(values)
    assert entry["theirs"] == 16  # Outnumbered (2) x Weight of Numbers (2)
    assert battles.record_text(entry) == "1 won, 0 lost"
    assert "1. Engaged (9)" in battles.info(saga, lord, 0)
    # The next event is the second stage's, against the smaller army.
    values["result"] = "lost"
    battles.event_form(saga, lord, 0).apply(values)  # type: ignore[union-attr]
    assert entry["ours"] == 40  # the enemy, outnumbered, takes no extra toll
    assert battles.record_text(entry) == "1 won, 1 lost"


def test_a_battle_short_of_baggage_lowers_its_event_totals():
    from support import everything_saga

    from ars_magica_manager import battles

    saga = everything_saga()
    entry = battles.battles(saga.neighbours[0])[0]
    entry["baggage"] = 1
    assert battles.baggage_short(entry) == 3
    values = {"who": "comp1", "maneuver": "Defend", "enemy": "Standard", "size": "Even"}
    event = battles.event_of(saga, entry, values)
    assert event is not None and event.baggage_short == 3
    assert isinstance(battles.event_form(saga, saga.neighbours[0], 5), Refuse)
