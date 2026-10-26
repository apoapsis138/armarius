"""The noble hunt, hawking and Area Lore (Lords of Men pp. 48-60; City &
Guild pp. 82-83): the rules, and More's The Hunt and Area Lore on a
manor and on the road."""

import random

import pytest

from ars_magica_manager import actions, bestiary_book, manors
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import hunting as hf
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Covenant,
    Neighbour,
    Saga,
)
from ars_magica_manager.rules import hunting as hr
from ars_magica_manager.sections import AHEAD_SECTION, MANORS_SECTION


class Fixed(random.Random):
    """Every d10 shows the same face (5 by default): a stress die of 5,
    a simple die of 5."""

    def __init__(self, face: int = 5) -> None:
        super().__init__(0)
        self.face = face

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.face


def _ability(name: str, xp: int) -> Ability:
    return Ability(name, "General", xp)


def _hunter(**chars: int) -> Character:
    """Konrad: Hunt 5, Ride 3, Animal Handling 3, Area Lore: Harz 3."""
    konrad = Character(id="konrad", name="Konrad", type="grog")
    for key, value in chars.items():
        setattr(konrad.characteristics, key, value)
    konrad.abilities = [
        _ability("Hunt", 75),
        _ability("Ride", 30),
        _ability("Animal Handling", 30),
        _ability("Area Lore: Harz", 30),
        _ability("Area Lore: Rhine", 5),
    ]
    return konrad


def _saga() -> Saga:
    lord = Neighbour(id="dieter", name="Count Dieter", kind="lord")
    lord.details = {"manor_list": [{"name": "Hagen", "acres": 600}]}
    covenant = Covenant(id="cov", name="Dammarstein", saga_id="h")
    covenant.manors = {"manor_list": [{"name": "Kohlergrund"}]}
    return Saga(
        id="h",
        name="Hunts",
        characters=[_hunter(perception=1, intelligence=1, stamina=1)],
        neighbours=[lord],
        covenants=[covenant],
        current_year=1220,
        current_season="Summer",
    )


def _form(command) -> Form:
    assert isinstance(command, Form)
    return command


# -- the rules --


def test_fatigue_levels_read_as_the_book_prints_them():
    assert hr.fatigue_penalties("OK, 0/0, -1/-1, -3, -5, Unconscious") == (
        0,
        0,
        -1,
        -1,
        -3,
        -5,
    )
    assert hr.fatigue_penalties("") == hr.PERSON_FATIGUE
    with pytest.raises(ValueError, match="Fatigue level"):
        hr.fatigue_penalties("OK, tired")
    levels = (0, -1, -3, -5)
    assert hr.penalty(levels, 0) == 0
    assert hr.penalty(levels, 3) == -3
    assert not hr.spent(levels, 4)
    assert hr.spent(levels, 5)


def test_the_hounds_figures_are_lords_of_men_p50():
    dog = hr.HOUNDS[hr.RUNNING_DOG]
    # Perception +3, Hunt 4, +2 to all Hunt rolls.
    assert dog.pursuit == 9
    # Stamina +1, Athletics 3, +3 to all running rolls.
    assert dog.tiring == 7
    assert hr.HOUNDS["mastiff"].pursuit == 3
    assert hr.LYMER_HUNT == 4


def test_the_hart_is_the_definitive_editions_stag_hunted_in_spring_and_summer():
    saga = _saga()
    hart = hf.quarry_of(saga, "book:stag")
    assert hart is not None
    assert (hart.dexterity, hart.athletics, hart.stamina) == (0, 4, 2)
    assert hart.evasion == 4
    assert hart.in_season("Summer")
    assert not hart.in_season("Autumn")
    boar = hf.quarry_of(saga, "book:wild_boar")
    assert boar is not None and boar.dangerous
    assert boar.seasons == ("Summer", "Autumn")
    assert hf.quarry_of(saga, hr.HARE.key) is hr.HARE
    assert hf.quarry_of(saga, "saga:none") is None


def test_the_sagas_bestiary_beasts_are_quarry_too():
    saga = _saga()
    book = bestiary_book.by_key("wolf")
    assert book is not None
    wolf = bestiary_book.build(book)
    wolf.name = "The White Wolf"
    saga.creatures.append(wolf)
    assert ("The White Wolf (the Bestiary)", f"saga:{wolf.id}") in (
        hf.quarry_options(saga)
    )
    quarry = hf.quarry_of(saga, f"saga:{wolf.id}")
    assert quarry is not None and quarry.athletics == 5


def test_the_quest_tracks_quiets_and_judges_against_nine():
    man = hr.Huntsman("Konrad", perception=1, hunt=5, animal_handling=3)
    done = hr.quest([man], [], Fixed())
    # Perception 1 + the lymer's Hunt 4 (the lower) + 5 = 10; Presence 0 +
    # Animal Handling 3 + 5 = 8 fails: the lymer startles the beast.
    assert not done.found
    assert "startled" in done.lines[0]
    quiet = hr.Huntsman("Konrad", perception=1, presence=1, hunt=5, animal_handling=3)
    guest = hr.Hunter("Dieter", perception=2, hunt=5)
    done = hr.quest([quiet], [guest], Fixed())
    assert done.found and done.judged and done.read


def test_a_beast_on_its_own_ground_escapes_a_steady_pack():
    hart = hr.Quarry("stag", "Stag", 0, 4, 3, (0, -1, -3, -5))
    # Pursuit 9 + 5 = 14 against Evasion 4 + 6 + 5 = 15: the hart wins
    # each hour, and never tires (Stamina 3 + Athletics 4 + 5 makes 12).
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [], [], Fixed())
    assert not done.cornered
    assert (done.prey_won, done.rounds) == (4, 4)
    assert "escapes" in done.lines[-1]


def test_off_its_own_ground_the_pack_corners_it():
    hart = hr.Quarry("stag", "Stag", 0, 4, 2, (0, -1, -3, -5))
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [], [], Fixed(), native=False)
    assert done.cornered
    assert done.hounds_won == 4
    assert done.terrain == 0
    assert "turns at bay" in done.lines[-1]


def test_the_relay_and_the_hunters_area_lore_cut_the_terrain_bonus():
    hart = hr.Quarry("stag", "Stag", 0, 4, 2, (0, -1, -3, -5))
    relay = hr.Huntsman("Konrad", intelligence=2, hunt=5, area_lore=9)
    rider = hr.Hunter(
        "Dieter", dexterity=2, ride=3, stamina=3, perception=2, area_lore=9
    )
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [rider], [relay], Fixed())
    # Hour 1: Evasion 15; the relay (2 + 5 + 6 + 5 = 18) brings fresh dogs and
    # its Area Lore (2 + 9 + 5 = 16) cuts 1, the hunter's (2 + 9 + 5) 1 more.
    assert "Terrain Bonus now +4" in done.lines[0]
    assert "fresh dogs" in done.lines[0]
    assert done.cornered


def test_a_poor_rider_falls_behind_and_a_long_chase_tires_the_hunters():
    hart = hr.Quarry("stag", "Stag", 0, 4, 2, (0, -1, -3, -5))
    slow = hr.Hunter("Brother Anselm")
    sore = hr.Hunter("Dieter", dexterity=1, ride=0, stamina=0)
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [slow, sore], [], Fixed(), hours=8)
    assert "Brother Anselm" in done.behind
    # Dexterity 1 + 5 keeps up; Stamina 0 + Ride 0 + 5 fails against 9 at
    # the third hour.
    assert done.long_term == {"Dieter": 1}
    assert "Dieter" in [h.name for h in hr.still_riding([slow, sore], done)]


def test_darkness_ends_a_chase():
    hart = hr.Quarry("stag", "Stag", 0, 4, 2, (0, -1, -3, -5))
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [], [], Fixed(), hours=2)
    assert done.rounds == 2 and not done.cornered
    assert "Darkness" in done.lines[-1]


def _dice_used(monkeypatch: pytest.MonkeyPatch) -> list[tuple[int, bool]]:
    """Record each roll's modifiers and whether it took a stress die."""
    used: list[tuple[int, bool]] = []
    real = hr.dice.roll

    def roll(rng: random.Random, modifiers: int, **kwargs):
        used.append((modifiers, kwargs["stress"]))
        return real(rng, modifiers, **kwargs)

    monkeypatch.setattr(hr.dice, "roll", roll)
    return used


def test_only_the_rolls_the_book_labels_take_a_stress_die(
    monkeypatch: pytest.MonkeyPatch,
):
    used = _dice_used(monkeypatch)
    man = hr.Huntsman("Konrad", perception=1, presence=1, hunt=5, animal_handling=3)
    guest = hr.Hunter("Dieter", perception=2, hunt=5)
    hr.quest([man], [guest], Fixed())
    # The quest and the assembly are unlabelled: simple (p. 52).
    assert used and not any(stress for _, stress in used)
    used.clear()
    hart = hr.Quarry("stag", "Stag", 0, 4, 3, (0, -1, -3, -5))
    rider = hr.Hunter("Dieter", dexterity=1, ride=3, stamina=8, perception=9)
    relay = hr.Huntsman("Konrad", intelligence=0, hunt=0, area_lore=-1)
    hr.chase(hr.HOUNDS[hr.RUNNING_DOG], hart, [rider], [relay], Fixed(), hours=3)
    by_total = dict(used)
    # Dexterity + Ride, the Pursuit and Evasion Totals, the relay and the
    # hunters' Perception + Area Lore are stress rolls (pp. 52-53).
    assert by_total[1 + 3] and by_total[9] and by_total[4 + 6]
    assert by_total[0 + 0 + 6] and by_total[9 + 0]
    # The tiring roll and Stamina + Ride every three hours are simple.
    assert not by_total[1 + 3 + 3] and not by_total[3 + 4]
    assert not by_total[8 + 3]
    used.clear()
    hr.hawk(5, hr.BIRDS["gyrfalcon"], hr.PREY["goose"], Fixed())
    # The hawker's roll is unlabelled; the hawk's attack is a combat roll.
    assert used[0] == (5, False) and used[1][1]


def test_a_spent_quarry_turns_at_bay_by_the_apps_reading():
    weak = hr.Quarry("stag", "Stag", 0, 0, 0, (-1,))
    # Its Evasion 0 + 6 + 5 against Pursuit 14: the hounds win the hours,
    # but it tires past its one level first.
    done = hr.chase(hr.HOUNDS[hr.RUNNING_DOG], weak, [], [], Fixed())
    assert done.cornered and done.hounds_won < hr.ROUNDS_TO_WIN
    assert "the app's reading" in done.lines[-1]


def test_a_hawk_at_21_attacks_on_after_a_miss_to_the_apps_limit(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(hr.combat, "hits", lambda _attack, _defense: False)
    done = hr.hawk(16, hr.BIRDS["sparrowhawk"], hr.PREY["partridge"], Fixed())
    assert done.result.again
    misses = [line for line in done.lines if line.endswith("a miss.")]
    assert len(misses) == hr.MOST_STRIKES
    assert "the book sets no limit" in done.lines[-1]


@pytest.mark.parametrize(
    ("total", "attacks", "bonus", "again", "check"),
    [
        (0, False, 0, False, True),
        (3, False, 0, False, False),
        (6, False, 0, False, False),
        (7, True, 0, False, False),
        (12, True, 1, False, False),
        (15, True, 2, False, False),
        (20, True, 3, False, False),
        (21, True, 5, True, False),
    ],
)
def test_the_hawking_table(total, attacks, bonus, again, check):
    result = hr.flight(total)
    assert (result.attacks, result.bonus, result.again, result.loyalty_check) == (
        attacks,
        bonus,
        again,
        check,
    )


def test_a_goshawk_will_not_stoop_at_a_crane_unless_trained():
    goshawk, crane = hr.BIRDS["goshawk"], hr.PREY["crane"]
    assert not hr.will_stoop(goshawk, crane, trained=False)
    assert hr.will_stoop(goshawk, crane, trained=True)
    assert hr.will_stoop(goshawk, hr.PREY["partridge"], trained=False)
    done = hr.hawk(5, goshawk, crane, Fixed())
    assert "will not stoop" in done.lines[-1]


def test_a_hawk_strikes_on_the_table():
    # 5 + 5 = 10: +1 to the attack; the gyrfalcon's Attack 6 + 1 + 5 = 12
    # against a goose's Defense 6 + 5 = 11 hits, Damage -4 + 1 against Soak 1.
    done = hr.hawk(5, hr.BIRDS["gyrfalcon"], hr.PREY["goose"], Fixed())
    assert done.result.bonus == 1
    assert "Strike 1: Attack 12 against Defense 11" in done.lines[-1]
    assert not done.killed


def test_a_hawk_flown_badly_may_be_lost():
    done = hr.hawk(-10, hr.BIRDS["merlin"], hr.PREY["partridge"], Fixed(), loyal=0)
    assert done.result.loyalty_check
    # Loyal 0 + 5 against 6: gone.
    assert done.lost


def test_the_gift_spoils_hawking():
    magus = _hunter(presence=2)
    magus.type = "magus"
    assert hr.hawker_total(magus) == 2 + 3 - 3


def test_area_lore_is_the_characters_by_name_or_his_best():
    konrad = _hunter()
    assert hr.area_lores(konrad) == [("Area Lore: Harz", 3), ("Area Lore: Rhine", 1)]
    assert hr.area_lore(konrad) == 3
    assert hr.area_lore(konrad, "Area Lore: Rhine") == 1
    assert hr.area_lore(konrad, "Area Lore: Iberia") == 0


def test_area_lore_ease_factors_and_the_townsman_abroad():
    assert hr.FREE_GOODS.ease == 6
    assert {s.ease for s in hr.SOUGHT} == {6, 9, 12, 15, 18}
    roll = hr.area_lore_roll(1, 3, 9, Fixed(), where=hr.TOWNSMAN_ABROAD)
    assert roll.total == 1 + 3 - 3 + 5
    assert not roll.succeeded


# -- the forms --


def test_the_hunt_on_a_lords_manor_writes_his_diary_and_the_hunters():
    saga = _saga()
    lord = saga.neighbour("dieter")
    assert lord is not None
    form = _form(hf.hunt_on_manor(saga, lord, 0, Fixed()))
    assert form.title == "The Hunt: Hagen"
    values = {f.key: f.value for f in form.fields()}
    assert values["hours"] == hr.DAYLIGHT["Summer"]
    values["hunters"] = ["konrad"]
    assert form.live is not None
    live = form.live(values)
    assert "Pursuit [b]+9[/]" in live
    assert "No kennels" in live
    assert form.validate is not None and form.validate(values) is None
    said = form.apply(values)
    konrad = saga.character("konrad")
    assert konrad is not None
    assert konrad.diary[-1].name.startswith("The Hunt")
    assert "Hagen" in konrad.diary[-1].details
    assert lord.details["diary"][-1]["text"].startswith("The Hunt")
    assert said[0].startswith("The Hunt")
    assert isinstance(hf.hunt_on_manor(saga, lord, 3), Refuse)


def test_a_covenants_manor_hunt_goes_in_the_covenants_diary():
    saga = _saga()
    covenant = saga.covenant("cov")
    assert covenant is not None
    holder = manors.manors_of(covenant)
    form = _form(hf.hunt_on_manor(saga, holder, 0, Fixed()))
    values = {f.key: f.value for f in form.fields()}
    form.apply(values)
    assert covenant.diary[-1].name.startswith("The Hunt")


def test_the_hunt_out_of_season_warns():
    saga = _saga()
    saga.current_season = "Winter"
    lord = saga.neighbour("dieter")
    assert lord is not None
    form = _form(hf.hunt_on_manor(saga, lord, 0))
    values = {f.key: f.value for f in form.fields()}
    assert form.live is not None
    assert "Out of season" in form.live(values)


def test_the_kennels_and_hunting_rights_show_on_a_lords_hunt():
    saga = _saga()
    lord = saga.neighbour("dieter")
    assert lord is not None
    lord.details["establishments"] = [
        {"kind": "Kennels", "quality": "Superior", "animals": 40}
    ]
    manors.household(lord)["hunting"] = "a chase in the Harz"
    form = _form(hf.hunt_on_manor(saga, lord, 0))
    values = {f.key: f.value for f in form.fields()}
    assert form.live is not None
    live = form.live(values)
    assert "Kennels: Superior, 40 hounds" in live
    assert "a chase in the Harz" in live


def test_hawking_on_a_manor():
    saga = _saga()
    lord = saga.neighbour("dieter")
    assert lord is not None
    form = _form(hf.hunt_on_manor(saga, lord, 0, Fixed()))
    values = {f.key: f.value for f in form.fields()}
    values.update(kind=hf.HAWKING, hawker="konrad", bird="gyrfalcon", prey="goose")
    assert form.live is not None
    assert "Presence + Animal Handling [b]+3[/]" in form.live(values)
    said = form.apply(values)
    assert said[0].startswith("Hawking")
    konrad = saga.character("konrad")
    assert konrad is not None and konrad.diary[-1].name.startswith("Hawking")


def test_a_hunt_on_the_road_first_finds_a_hunting_spot():
    saga = _saga()
    form = _form(hf.hunt_on_journey(saga, rng=Fixed()))
    values = {f.key: f.value for f in form.fields()}
    assert "huntsman_hunt" in {f.key for f in form.fields()}
    assert form.validate is not None
    assert "Name who hunts" in (form.validate(values) or "")
    values["hunters"] = ["konrad"]
    assert form.live is not None
    assert "First find a hunting spot" in form.live(values)
    form.apply(values)
    konrad = saga.character("konrad")
    assert konrad is not None
    # Intelligence 1 + Area Lore 3 + 5 makes 6.
    assert "knows where game is to be had" in konrad.diary[-1].details
    assert konrad.diary[-1].details.startswith("On the road")


def test_no_hunting_spot_no_hunt():
    saga = _saga()
    form = _form(hf.hunt_on_journey(saga, rng=Fixed(1)))
    values = {f.key: f.value for f in form.fields()}
    values["hunters"] = ["konrad"]
    values["reserved"] = True
    form.apply(values)
    konrad = saga.character("konrad")
    assert konrad is not None
    assert konrad.diary[-1].name == "The Hunt: no game found"


def test_long_term_fatigue_is_taken_from_the_hunters():
    saga = _saga()
    konrad = saga.character("konrad")
    assert konrad is not None
    konrad.characteristics.stamina = -3
    lord = saga.neighbour("dieter")
    assert lord is not None
    form = _form(hf.hunt_on_manor(saga, lord, 0, Fixed()))
    values = {f.key: f.value for f in form.fields()}
    values.update(hunters=["konrad"], huntsmen=["konrad"], native=False)
    konrad.characteristics.presence = 1
    form.apply(values)
    # The chase lasts 4 hours: one Stamina + Ride roll (-3 + 3 + 5) fails.
    assert konrad.long_term_fatigue == 1


def test_area_lore_writes_what_was_found():
    saga = _saga()
    form = _form(hf.area_lore_on_journey(saga, rng=Fixed()))
    values = {f.key: f.value for f in form.fields()}
    assert form.validate is not None
    assert form.validate(values) == "Choose who asks."
    values.update(who="konrad", sought="village_inn", what="the inn at Goslar")
    assert form.live is not None
    live = form.live(values)
    assert "Ease Factor [b]9[/]" in live
    assert "[b]+4[/]" in live
    form.apply(values)
    konrad = saga.character("konrad")
    assert konrad is not None
    assert konrad.diary[-1].name == "Area Lore: found"
    assert "the inn at Goslar" in konrad.diary[-1].details
    lord = saga.neighbour("dieter")
    assert lord is not None
    manor_form = _form(hf.area_lore_on_manor(saga, lord, 0, Fixed()))
    manor_form.apply({"who": "konrad", "sought": "heinous", "away": hr.AT_HOME})
    assert konrad.diary[-1].name == "Area Lore: not found"
    assert isinstance(hf.area_lore_on_manor(saga, lord, 2), Refuse)


def test_a_saga_without_characters_cannot_hunt_on_the_road():
    saga = Saga(id="e", name="Empty")
    assert isinstance(hf.hunt_on_journey(saga), Refuse)
    assert isinstance(hf.area_lore_on_journey(saga), Refuse)


# -- where they are offered --


class _Facts:
    def __init__(self, saga: Saga, section: str) -> None:
        self.saga = saga
        self.section = section


def test_the_hunt_is_offered_on_manors_and_on_ahead():
    assert actions.MORE_SECTIONS["hunt_on_manor"] == MANORS_SECTION
    assert actions.MORE_SECTIONS["area_lore_on_manor"] == MANORS_SECTION
    rule = actions._SECTION_RULES["hunt_on_journey"]
    saga = _saga()
    assert rule(_Facts(saga, AHEAD_SECTION), AHEAD_SECTION)  # type: ignore[arg-type]
    assert not rule(_Facts(saga, MANORS_SECTION), MANORS_SECTION)  # type: ignore[arg-type]
    for action in (
        "hunt_on_manor",
        "area_lore_on_manor",
        "hunt_on_journey",
        "area_lore_on_journey",
    ):
        assert action in menu_forms.NOT_ON_PAGES
