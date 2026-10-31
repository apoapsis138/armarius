"""A covenant's ships (Hermetic Projects pp. 53-54, 63; City & Guild pp.
77, 84-87): the record, its rules, the Ships list's text and forms, and
More's Stress Check and Ship Combat."""

import dataclasses
import random

import pytest

from ars_magica_manager import actions, ships
from ars_magica_manager import possessions as pos
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import possession as possession_forms
from ars_magica_manager.forms import ships as sf
from ars_magica_manager.models import (
    POSSESSION_KINDS,
    Ability,
    Character,
    Covenant,
    Possession,
    Saga,
    Ship,
)
from ars_magica_manager.rules import ships as rules


class Sequence(random.Random):
    """d10s that show the faces given, in turn, then 5s."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _bjorn() -> Character:
    """Bjorn Ironside: Int +2, Profession: Sailor 4."""
    bjorn = Character(id="bjorn", name="Bjorn Ironside", type="companion")
    bjorn.characteristics.intelligence = 2
    bjorn.abilities = [Ability("Profession: Sailor", "General", 50)]
    bjorn.covenant_id = "wadden"
    return bjorn


def _flagship(**changes: object) -> Possession:
    ship = Ship(
        ship_type="large_cog",
        kind_name="Large merchant cog",
        size=7,
        tons=240,
        crew=18,
        quality="Superior",
        damage_lost=2,
        magnitudes=6,
        captain_id="bjorn",
        ballistae=1,
        fighters_tons=6,
    )
    return Possession(
        id="nebel",
        kind="ship",
        name="Nebelkönigin",
        description="Stolen from Oculus Septentrionalis.",
        ship=dataclasses.replace(ship, **changes),  # type: ignore[arg-type]
    )


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="wadden", name="Waddenzee", saga_id="s")
    covenant.possessions = [
        _flagship(),
        Possession(
            id="seehund",
            kind="ship",
            name="Seehund",
            ship=Ship(ship_type="buss", kind_name="Coastal buss"),
        ),
    ]
    other = Covenant(id="oculus", name="Oculus Septentrionalis", saga_id="s")
    other.possessions = [
        Possession(id="hansa", kind="ship", name="Hansa", ship=Ship(size=6, tons=100))
    ]
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant, other],
        characters=[_bjorn()],
    )
    return saga, covenant


def _form(command: object) -> Form:
    assert isinstance(command, Form)
    return command


def _values(form: Form, **changes: object) -> dict[str, object]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


# -- the record --


def test_a_ship_is_the_first_kind_of_possession_and_starts_with_figures():
    assert POSSESSION_KINDS[0] == "ship"
    assert Possession(id="x", kind="ship").ship == Ship()
    assert Possession(id="y", kind="item").ship is None


def test_a_saved_ship_loads_back_and_a_bad_one_is_named():
    _, covenant = _saga()
    data = dataclasses.asdict(covenant)
    again = Covenant.from_dict(data)
    assert again.possessions[0].ship == covenant.possessions[0].ship
    data["possessions"][0]["ship"]["quality"] = "Gilded"
    with pytest.raises(ValueError, match="Nebelkönigin"):
        Covenant.from_dict(data)
    data["possessions"][0]["ship"]["quality"] = "Standard"
    data["possessions"][0]["ship"]["crew"] = "many"
    with pytest.raises(ValueError, match="crew"):
        Covenant.from_dict(data)


# -- the rules --


@pytest.mark.parametrize(
    ("size", "modifier"), [(-1, 1), (1, 1), (2, 2), (5, 2), (6, 3), (8, 3), (9, 4)]
)
def test_the_size_modifier_follows_hermetic_projects_table(size, modifier):
    assert rules.damage_modifier(size) == modifier


def test_damage_levels_are_the_quality_base_times_the_size_modifier():
    ship = _flagship().ship
    assert ship is not None
    assert rules.damage_levels(ship) == 9  # Superior 3 x 3
    assert rules.damage_left(ship) == 7
    assert rules.condition(ship) == "damaged"
    assert rules.damage_levels(Ship(quality="Excellent", size=5)) == 8
    assert rules.damage_levels(Ship(quality="Shoddy", size=4)) == 2
    assert rules.damage_levels(Ship(quality="Supernatural", size=9)) == 20


def test_the_book_types_fill_size_cargo_and_crew():
    filled = rules.type_fills("large_cog", "")
    assert filled == {
        "size": 7,
        "tons": 240,
        "crew": 18,
        "kind_name": "Large merchant cog",
    }
    # A kind of the user's own is kept.
    assert "kind_name" not in rules.type_fills("buss", "Knarr")
    assert len(rules.SHIP_TYPES) == 8
    for t in rules.SHIP_TYPES.values():
        assert rules.damage_modifier(t.size) == t.damage_modifier


def test_crew_fighting_men_artillery_and_cargo():
    ship = Ship(tons=240, crew=18, lateen=True, ballistae=1, fighters_tons=6)
    assert rules.crew(ship) == 27  # half again
    assert rules.fighting_men(ship) == 48  # 8 a ton on a long voyage
    raiders = dataclasses.replace(ship, close_to_home=True, fighters_tons=0.25)
    assert rules.fighting_men(raiders) == 16  # 16 a quarter ton
    assert rules.artillery_limit(ship) == 12
    assert rules.cargo_left(ship) == 233.75
    assert rules.problem(ship) is None
    assert "At most 12" in (
        rules.problem(dataclasses.replace(ship, catapults=12)) or ""
    )
    assert "only 9" in (
        rules.problem(Ship(size=7, quality="Superior", damage_lost=10)) or ""
    )
    assert "more than" in (rules.problem(Ship(tons=20, fighters_tons=21)) or "")


def test_quality_bonus_lab_totals_and_worth():
    assert rules.quality_bonus(Ship(quality="Superior")) == 1
    assert rules.quality_bonus(Ship(quality="Excellent", excellent_bonus=3)) == 3
    assert rules.enchanting_modifier(Ship(quality="Standard")) == -1
    assert rules.enchanting_modifier(Ship(quality="Shoddy")) == -3
    assert rules.enchanting_modifier(Ship(quality="Excellent")) == 2
    cog = Ship(ship_type="large_cog", tons=240)
    assert (rules.book_cost(cog), rules.guild_worth(cog)) == (100, 96)
    assert rules.guild_worth(Ship(tons=20, galley=True)) == 500


def test_the_captain_rolls_his_seafaring_profession():
    bjorn = _bjorn()
    assert rules.profession(bjorn) == ("Profession: Sailor", 4)
    bjorn.abilities.append(Ability("Profession: Steward", "General", 75))
    assert rules.profession(bjorn) == ("Profession: Sailor", 4)
    assert rules.profession(None) == ("Profession: Sailor", 0)


def test_stress_check_terms_and_what_it_costs():
    ship = _flagship().ship
    assert ship is not None
    terms = rules.stress_terms(ship, _bjorn(), "severe", repaired=True)
    # Profession 4 + Superior 1 + enchanted 6 - 3 weather - 1 repaired.
    assert rules.stress_total(terms) == 7
    assert rules.levels_lost(7, 8, 0) == 0
    assert rules.levels_lost(7, 7, 0) == 1
    assert rules.levels_lost(7, 0, 2) == 3
    assert rules.take_damage(ship, 10) == 7
    assert rules.wrecked(ship)


def test_ship_combat_helpers():
    assert rules.captain_terms(2, 4, 5, 1) == 10  # crew counts at most +3
    assert rules.shots(30) == 3
    assert rules.shots(0) == 0
    assert rules.taller(7, 5) == "ours"
    assert rules.taller(5, 5) == ""
    assert rules.founder_minutes(4) == 20
    assert rules.sheared_rowers(3) == 6
    assert rules.catapult_struck(7) == 3


def test_saga_ships_are_what_combat_and_fleets_pick_from():
    saga, covenant = _saga()
    assert [p.name for p in rules.ships_of(covenant)] == ["Nebelkönigin", "Seehund"]
    assert [(c.id, p.id) for c, p in rules.saga_ships(saga)] == [
        ("wadden", "nebel"),
        ("wadden", "seehund"),
        ("oculus", "hansa"),
    ]


# -- the list --


def test_the_ships_list_rows_and_details():
    saga, covenant = _saga()
    entries = pos.entries_for_kind(saga, covenant, "ship")
    assert pos.table_header("ship").split()[:3] == ["Ship", "Kind", "Cargo"]
    row = pos.row_label(entries[0])
    assert row.startswith("Nebelkönigin")
    assert "Large merchant cog +7" in row
    assert "[$text-warning]7 of 9[/]" in row
    assert row.endswith("Bjorn Ironside")
    text = pos.detail_text(entries[0])
    for words in (
        "Large merchant cog, size +7",
        "18 + 48 fighting men",
        "Superior 3 x size 3",
        "6 magnitudes invested",
        "+1 to navigation",
        "60 to 80 miles a day",
        "Stolen from Oculus",
    ):
        assert words in text
    card = ships.card(covenant.possessions[0], saga)
    assert (card.badge, card.tone) == ("7 of 9 damage", "text-warning")
    assert pos.table("ship", entries).rows[1][-1] == ships.NO_CAPTAIN


# -- Add / Edit Ship --


def test_add_ship_fills_from_the_book_and_saves():
    saga, covenant = _saga()
    form = _form(
        possession_forms.covenant_possession_form(saga, covenant, "ship", None)
    )
    assert form.inspector == "The Ship"
    like = next(f for f in form.fields() if f.key == "ship_type")
    assert like.fills is not None
    values = _values(form, name="Möwe", ship_type="buss")
    values.update(like.fills(values))
    assert "8 pounds by HP" in (form.live or str)(values)
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    made = covenant.possessions[-1]
    assert (made.kind, made.name, made.ship) == (
        "ship",
        "Möwe",
        Ship(ship_type="buss", kind_name="Coastal buss", size=5, tons=20, crew=8),
    )


def test_editing_fewer_damage_levels_lost_marks_her_repaired():
    saga, covenant = _saga()
    entry = pos.entries_for_kind(saga, covenant, "ship")[0]
    form = _form(
        possession_forms.covenant_possession_form(saga, covenant, "ship", entry)
    )
    values = _values(form, damage_lost=0)
    assert form.validate is not None
    assert form.validate(_values(form, damage_lost=12)) is not None
    form.apply(values)
    ship = covenant.possessions[0].ship
    assert ship is not None and (ship.damage_lost, ship.repaired) == (0, True)


# -- More: Stress Check and Ship Combat --


def test_the_more_items_are_offered_on_the_ships_list():
    assert actions.MORE_SECTIONS["ship_stress"] == "section-pos-ship"
    assert actions.MORE_SECTIONS["ship_combat"] == "section-pos-ship"
    assert {"ship_stress", "ship_combat"} <= menu_forms.NOT_ON_PAGES
    assert actions.SECTION_VERBS["section-pos-ship"] == frozenset(
        {"add", "edit", "remove"}
    )


def test_a_failed_stress_check_costs_a_damage_level():
    saga, covenant = _saga()
    form = _form(sf.stress_check(saga, covenant, 0, Sequence(2)))
    values = _values(form, weather="severe", repaired=True)
    assert "= [b]+7 + die[/] against 15" in (form.live or str)(values)
    said = form.apply(values)
    ship = covenant.possessions[0].ship
    assert ship is not None and ship.damage_lost == 3
    assert "loses a damage level" in " ".join(said)
    assert covenant.diary[-1].name == "Stress Check: Nebelkönigin"


def test_a_botched_stress_check_costs_one_more_a_botch():
    saga, covenant = _saga()
    form = _form(sf.stress_check(saga, covenant, 0, Sequence(0, 0)))
    form.apply(_values(form))
    ship = covenant.possessions[0].ship
    assert ship is not None and ship.damage_lost == 4  # 2 + one + one botch


def test_a_wrecked_ship_or_no_ship_refuses():
    saga, covenant = _saga()
    ship = covenant.possessions[0].ship
    assert ship is not None
    ship.damage_lost = 9
    assert isinstance(sf.stress_check(saga, covenant, 0), Refuse)
    assert isinstance(sf.ship_combat(saga, covenant, 0), Refuse)
    assert isinstance(sf.stress_check(saga, covenant, 5), Refuse)


def test_winning_the_chase_and_boarding_sets_up_a_fight():
    saga, covenant = _saga()
    form = _form(sf.ship_combat(saga, covenant, 0, Sequence(9, 2)))
    values = _values(form, theirs="oculus/hansa", crew_bonus=3, rounds=30)
    live = (form.live or str)(values)
    assert "Int 2 + Profession: Sailor 4" in live
    assert "+9 + stress die" in live
    assert "shooting 3 time(s)" in live
    assert "Nebelkönigin's men get +3" in live
    said = form.apply(values)
    assert saga.fights[-1].name == "Boarding: Nebelkönigin and Hansa"
    assert saga.fights[-1].sides[0].covenant_id == "wadden"
    assert "boards Hansa" in " ".join(said)


def test_ramming_and_shearing():
    saga, covenant = _saga()
    form = _form(sf.ship_combat(saga, covenant, 0, Sequence(9, 2, 4)))
    said = " ".join(form.apply(_values(form, aim="ram")))
    assert "founders in 20 minutes" in said
    assert "entangled" in said  # a sailing ship rams and is caught
    form = _form(sf.ship_combat(saga, covenant, 0))
    assert form.validate is not None
    assert "galley" in (form.validate(_values(form, aim="shear")) or "")
    assert form.validate(_values(form, crew_bonus=4)) is not None


def test_a_typed_enemy_and_losing():
    saga, covenant = _saga()
    form = _form(sf.ship_combat(saga, covenant, 1, Sequence(2, 9)))
    values = _values(
        form, theirs=sf.TYPED, their_name="A pirate", their_captain=6, aim="board"
    )
    said = " ".join(form.apply(values))
    assert "A pirate slips away" in said
    assert not saga.fights


def test_editing_a_ship_keeps_her_fate():
    sunk = dataclasses.replace(sf.Ship(), fate=sf.SUNK, fate_when="Summer 1219")
    edited = sf.ship_from({"tons": 40}, sunk)
    assert edited.fate == sf.SUNK and edited.fate_when == "Summer 1219"
    assert edited.tons == 40
