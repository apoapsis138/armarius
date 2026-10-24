"""Sieges played event by event (rules.siege, sieges.py; Lords of Men pp.
111-116): undermining, bombarding, escalade, sallies, the stockade's
supplies rolls, the castle's interval, how long a siege has run, and the
Diaries an ending writes. The dice are scripted: each test says what each
d10 shows."""

import random

from ars_magica_manager import place_events, sieges
from ars_magica_manager.models import Covenant, Neighbour, Saga, Siege
from ars_magica_manager.rules import siege as rules


class Scripted(random.Random):
    """A d10 that throws the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def test_a_mine_that_beats_the_counter_miners_takes_the_defenses_down():
    castle = Siege("S", miners=1, sapper=10, counter_sapper=0)
    played = rules.undermine(castle, 0, Scripted(5, 2))  # 15 against 0 + 2 + 2
    assert castle.defenses == "Shoddy"
    assert "brings it down" in played.text


def test_a_botched_defence_against_a_mine_costs_two_steps():
    castle = Siege("S", defenses="Superior", miners=1, sapper=10)
    rules.undermine(castle, 0, Scripted(5, 0, 0))  # the defence botches
    assert castle.defenses == "Shoddy"


def test_a_botched_mine_loses_a_unit_of_miners():
    castle = Siege("S", miners=2, sapper=10)
    played = rules.undermine(castle, 0, Scripted(0, 0, 2))
    assert castle.miners == 1
    assert castle.defenses == "Standard"
    assert "collapses" in played.text
    assert rules.undermine(Siege("S"), 0, Scripted()).text.startswith(
        "The besiegers have no miners"
    )


def test_engines_bombard_in_groups_of_five_and_a_broken_wall_loses_its_bonus():
    castle = Siege("S", engines={"Trebuchet": 7}, gunner=20)
    assert rules.engine_groups(castle) == [("Trebuchet", 5), ("Trebuchet", 2)]
    assert rules.full_wall(castle) == 8  # Standard (+2) x 4 at Size +9
    rules.bombard(castle, 1, Scripted(5, 2, 5, 2))
    assert rules.walls(castle) == [8, 1, 8, 8]
    assert rules.wall_bonus(castle, 1) == 2
    played = rules.bombard(castle, 1, Scripted(5, 2, 5, 2))
    assert rules.walls(castle)[1] == 0
    assert rules.wall_bonus(castle, 1) == 0
    assert "no longer gives its Defense Bonus" in played.text


def test_an_escalade_won_at_a_shoddy_wall_breaches_the_castle():
    castle = Siege("S", garrison=25, defenses="Shoddy")
    rules.escalade(castle, 0, besiegers_won=True)
    assert (castle.garrison, castle.ended) == (20, "Breached")
    standing = Siege("S", garrison=25)
    rules.escalade(standing, 0, besiegers_won=True)
    assert (standing.garrison, standing.ended) == (20, "")
    held = Siege("S", garrison=25)
    assert "thrown back" in rules.escalade(held, 0, besiegers_won=False).text
    assert held.garrison == 25


def test_a_sally_that_wins_removes_the_units_it_targets():
    castle = Siege("S", miners=3, engines={"Trebuchet": 7}, soldiers=4)
    rules.sally(castle, "Miners", won=True)
    rules.sally(castle, "Trebuchet", won=True)
    rules.sally(castle, "Soldiers", won=False)
    assert (castle.miners, castle.engines["Trebuchet"], castle.soldiers) == (0, 2, 4)


def test_supplies_rolls_come_only_with_a_stockade():
    open_castle = Siege("S", days=60)
    assert rules.supplies_rolls(open_castle, Scripted()) == []
    held = Siege("S", besieger_walls=[1, 1, 1, 0], days=29)
    assert rules.pass_interval(held, Scripted(5)) == ["Supplies roll: 8 against 4"]
    assert (held.days, held.supply_rolls, held.supplies) == (30, 1, "Standard")


def test_a_failed_supplies_roll_at_shoddy_means_surrender():
    castle = Siege("S", supplies="Shoddy", besieger_walls=[1, 1, 1, 1], days=6)
    told = rules.pass_interval(castle, Scripted(2))  # 1 + 2 against 4
    assert castle.ended == "Surrendered"
    assert told[-1] == "The supplies are gone: the castle surrenders."


def test_the_interval_is_the_castles_shortest_and_time_reads_in_its_units():
    castle = Siege("S", garrison=25, defenses="Excellent", supplies="Excellent")
    assert rules.castle_of(castle).interval() == "Month"
    assert rules.interval_days(castle) == 30
    assert sieges.time_text(0) == "just begun"
    assert sieges.time_text(7) == "1 week"
    assert sieges.time_text(100) == "1 season and 1 week"
    assert sieges.time_text(400) == "1 year and 1 month"


def test_an_ending_writes_the_covenants_and_neighbours_diaries():
    keep = Covenant(id="cov1", saga_id="s", name="Keep")
    castle = Neighbour(id="burg", name="Burg Falkenstein", kind="place")
    baron = Neighbour(id="urach", name="Baron of Urach", kind="lord")
    siege = Siege(
        "The Siege",
        castle="Burg Falkenstein",
        defenses="Shoddy",
        covenant_id="cov1",
        castle_id="burg",
        besieger_id="urach",
    )
    saga = Saga(
        id="s", name="S", covenants=[keep], neighbours=[castle, baron], sieges=[siege]
    )
    told = sieges.next_event(saga, siege, Scripted()).apply(
        {"event": rules.ESCALADE, "wall": "0", "result": "won"}
    )
    assert siege.ended == "Breached"
    assert told[-1] == "Written in 3 Diaries."
    assert keep.diary[-1].name == "The Siege"
    assert place_events.diary(baron)[-1]["text"].startswith("The Siege: Breached")
    assert place_events.diary(castle)
    assert sieges.next_event(saga, siege).why.startswith("The siege has ended")
