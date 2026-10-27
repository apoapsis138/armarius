"""The Mysteries Revised Edition's alchemy (pp. 39-46) and its Great and
Consummate Talismans (pp. 89-90): Philosophic Alchemy's digestion beside
other lab work, its ready-opened spaces, the Lesser and Great Elixirs, and
the talisman rules. The book's examples are checked where they apply."""

import random
from dataclasses import asdict

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.enchanted_devices import capacity_text, device_info_text
from ars_magica_manager.models import (
    DIGEST_SPACES,
    Ability,
    Alchemy,
    ArtScore,
    Book,
    Character,
    Characteristics,
    Covenant,
    DeviceComponent,
    Digestion,
    ElixirIngredient,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    VirtueFlawInstance,
    XpAllocation,
)
from ars_magica_manager.rules import (
    aging,
    enchant_seasons,
    enchantment,
    lab,
    lab_seasons,
    warping,
)
from ars_magica_manager.rules import tmre_alchemy as alchemy
from ars_magica_manager.rules.season_work import alchemy as season
from ars_magica_manager.rules.season_work import problems
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.seasons import digestion as digestion_apply
from ars_magica_manager.sheets.character import info_right_text


def _vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id, params=params)


def _saga(*virtues: str) -> Saga:
    magus = Character(id="m", name="Parella", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=2, stamina=2)
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(3))]
    # CrVi 10 + 4 + Int 2 + MT 3 + aura 1 = 20; CrIg 10 + 20 + 6 = 36.
    magus.arts = {
        "creo": ArtScore(xp=art_xp(10)),
        "ignem": ArtScore(xp=art_xp(20)),
        "vim": ArtScore(xp=art_xp(4)),
    }
    magus.virtues_flaws = [_vf(v) for v in ("vf_hermetic_alchemy", *virtues)]
    magus.assigned_lab_id = "lab"
    lab = Laboratory(id="lab", covenant_id="cov", name="Athanor", owner_id="m")
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    covenant.aura = 1
    saga = Saga(
        id="s",
        name="S",
        covenants=[covenant],
        characters=[magus],
        laboratories=[lab],
    )
    saga.spells = [Spell("warm", "Warm Hands", "Creo", "Ignem", level=5)]
    return saga


def _settle(saga: Saga, **kw: object) -> Digestion:
    magus = saga.characters[0]
    digestion = Digestion(lab_id="lab", vis_from="laboratory", **kw)  # type: ignore[arg-type]
    return alchemy.start(magus, digestion, saga.current_season, saga.current_year)


def _plan(saga: Saga, **kw: object) -> SeasonPlan:
    return SeasonPlan(
        "m",
        saga.current_year,
        saga.current_season,
        lab_seasons.INVENT,
        lab_id="lab",
        spell_id="warm",
        **kw,  # type: ignore[arg-type]
    )


def _advance(saga: Saga) -> seasons.advance.Advanced:
    return seasons.finish_season(saga, seasons.resolve(saga), {}, random.Random(1))


# -- the rules -----------------------------------------------------------------


def test_tending_adds_seven_days_to_the_other_work_only():
    # Nothing until the two pass ten days, then the extra the seven days cost.
    assert alchemy.tending_line(0).amount == 0
    assert alchemy.tending_line(4).amount == -12
    # TMRE p. 41: 11 days away cost the extraction 12 points and the spell,
    # 18 days in all, 26 (14 more than the 11 alone).
    assert alchemy.tending_line(11).amount == -14
    assert alchemy.tending_problem(13) == ""
    assert "no other lab work" in alchemy.tending_problem(14)
    assert not alchemy.spoils(20) and alchemy.spoils(21)


def test_the_yield_is_the_lowest_season_s_and_spaces_count_against_opening():
    magus = _saga(alchemy.PHILOSOPHIC_MINOR).characters[0]
    vis = Digestion(totals=[44, 30, 51, 38])
    assert alchemy.digestion_yield(vis, magus) == 3  # 30 / 10
    ignem = Digestion(form="Ignem", totals=[44])
    assert alchemy.digestion_yield(ignem, magus) == 3  # 44 / 20, TMRE p. 40
    # Parella: Lab Total 71 makes eight open spaces; a 24-pawn coral then
    # needs 16 (TMRE p. 41).
    spaces = Digestion(product=DIGEST_SPACES, form="Ignem", totals=[71])
    assert alchemy.digestion_yield(spaces, magus) == 8
    assert alchemy.opening_left(24, 8) == 16
    assert alchemy.finished(Digestion(seasons=4, totals=[1, 2, 3])) is False


def test_the_virtue_s_tier_sets_the_seasons_and_needs_hermetic_alchemy():
    saga = _saga(alchemy.PHILOSOPHIC_MINOR)
    magus = saga.characters[0]
    assert alchemy.philosophic_tier(magus) == "Minor"
    assert alchemy.digestion_seasons(magus) == 4
    assert alchemy.replaces_minor(magus)
    magus.virtues_flaws.append(_vf(alchemy.PHILOSOPHIC_MAJOR))
    assert alchemy.digestion_seasons(magus) == 1
    magus.virtues_flaws = [_vf(alchemy.PHILOSOPHIC_MAJOR)]
    assert "Hermetic Alchemy" in alchemy.digest_problem(magus)
    assert "hasn't Philosophic" in alchemy.digest_problem(_saga().characters[0])


def test_the_lesser_elixir_follows_the_book_s_example():
    # Desperata, Magic Theory 5: bloodstone +4 gives Level 2; amber +3 and
    # her own laurel oil +3 (doubled to 6, capped at 5) give 12, Level 4.
    first = [ElixirIngredient("bloodstone", 4)]
    assert alchemy.elixir_level(alchemy.elixir_points(first, 5), 5) == 2
    more = [
        *first,
        ElixirIngredient("amber", 3),
        ElixirIngredient("laurel oil", 3, devised=True),
    ]
    assert alchemy.elixir_points(more, 5) == 12
    assert alchemy.elixir_level(12, 5) == 4
    assert alchemy.elixir_level(55, 9) == 9  # never above Magic Theory
    lines = alchemy.elixir_breakdown(more, 5).lines
    assert lines[-1].amount == 5 and "doubled" in lines[-1].label


def test_adding_an_ingredient_puts_the_elixir_in_force_until_a_crisis():
    saga = _saga(alchemy.LESSER_ELIXIR)
    magus = saga.characters[0]
    assert alchemy.lesser_elixir_problem(magus) == ""
    assert alchemy.add_ingredient(magus, ElixirIngredient("bloodstone", 4)) == (3, 2)
    # Magic Theory 3 caps the bloodstone at 3: Level 2.
    assert magus.alchemy is not None and magus.alchemy.elixir_bonus == 2
    lines = alchemy.aging_lines(15, magus)
    assert [line.amount for line in lines] == [15, 2]
    alchemy.end_elixir(magus)
    assert magus.alchemy.elixir_bonus == 0


def test_the_great_elixir_follows_the_book_s_examples():
    magus = _saga().characters[0]
    assert "Unaging and the Lesser Elixir" in alchemy.great_elixir_problem(
        Character(
            id="x", name="X", type="magus", virtues_flaws=[_vf(alchemy.GREAT_ELIXIR)]
        )
    )
    assert alchemy.great_elixir_problem(magus).startswith("Parella hasn't")
    # Desperata at 157: 4 + Stamina 2 + Level 9 = 15 against 16 fails.
    lines = alchemy.great_test_lines(2, 9, 0, 10)
    assert alchemy.great_ease(157) == 16
    assert not alchemy.great_succeeds(4, lines, 16)
    # Her later potion, with one earlier attempt: 9 + 2 + 9 + 1 = 21 beats 17.
    again = alchemy.great_test_lines(2, 9, 1, 10)
    assert alchemy.great_ease(161) == 17 and alchemy.great_succeeds(9, again, 17)
    assert alchemy.great_test_lines(2, 9, 12, 3)[-1].amount == 3  # by Magic Theory
    assert alchemy.granted_might(80) == 30 and alchemy.granted_might(100) == 40
    assert alchemy.elixir_spaces(31) == 4


def test_great_and_consummate_talismans():
    magus = _saga(alchemy.GREAT_TALISMAN).characters[0]
    assert alchemy.component_limit(magus) == 3
    assert "Great Talisman" in alchemy.talisman_notes(magus)[0]
    assert alchemy.consummate_problem(magus) == ""
    assert alchemy.consummate_ordeal(magus) == (
        alchemy.DELETERIOUS,
        alchemy.TALISMAN_CIRCUMSTANCE,
        "Minor",
    )
    magus.virtues_flaws.append(_vf(alchemy.DELETERIOUS, circumstance="in sunlight"))
    assert alchemy.consummate_ordeal(magus)[2] == "Major"
    magus.virtues_flaws.append(
        _vf(alchemy.NECESSARY_CONDITION, condition="must wield his talisman")
    )
    assert alchemy.consummate_ordeal(magus) == ("", "", "")
    effects = [
        InstilledEffect("a", technique="Muto", form="Vim", range="Personal"),
        InstilledEffect("b", technique="Muto", form="Vim", range="Touch"),
    ]
    assert [e.id for e in alchemy.consummate_effects(effects)] == ["a"]
    plain = _saga(alchemy.INSCRIPTION).characters[0]
    assert alchemy.consummate_problem(plain) == ""
    assert "Inscription on the Soul alone" in alchemy.talisman_notes(plain)[0]
    assert "needs Great Talisman" in alchemy.consummate_problem(_saga().characters[0])


# -- the digestion through the seasons -----------------------------------------


def test_a_major_digestion_runs_beside_inventing_and_gives_its_vis():
    saga = _saga(alchemy.PHILOSOPHIC_MAJOR)
    magus = saga.characters[0]
    _settle(saga)
    found, work = lab_seasons.work(saga, magus, _plan(saga, days_away=11))
    assert found == [] and work is not None
    tending = [line for line in work.lab_total.lines if "Tending" in line.label]
    assert [line.amount for line in tending] == [-14]
    # No second extraction, and not too many days for the other work.
    extract = SeasonPlan(
        "m", 1220, "Spring", lab_seasons.EXTRACT, lab_id="lab", vis_from="laboratory"
    )
    assert "no other vis extraction" in lab_seasons.work(saga, magus, extract)[0][0]
    assert (
        "no other lab work"
        in lab_seasons.work(saga, magus, _plan(saga, days_away=14))[0][0]
    )
    seasons.set_plan(saga, _plan(saga))
    done = _advance(saga)
    # 20 / 10: two pawns of Vim to the laboratory.
    assert saga.laboratories[0].raw_vis == {"vim": 2}
    assert magus.alchemy is not None and magus.alchemy.digestion is None
    assert any("2 pawn(s) of Vim" in line.result for line in done.record.lines)
    assert any(e.name == "Digestion (Vim vis)" for e in magus.diary)


def test_a_minor_digestion_takes_a_year_and_its_lowest_season():
    saga = _saga(alchemy.PHILOSOPHIC_MINOR)
    magus = saga.characters[0]
    _settle(saga, form="Ignem")
    days = [0, 12, 0, 0]
    for away in days:
        seasons.set_plan(saga, _plan(saga, days_away=away))
        _advance(saga)
    # CrVi 20 (Ignem above Vim); the 12 days cost 14: lowest 6 -> 1 pawn.
    assert saga.laboratories[0].raw_vis == {"ignem": 1}
    assert magus.alchemy is not None and magus.alchemy.digestion is None


def test_a_season_out_of_the_laboratory_spoils_the_digestion():
    saga = _saga(alchemy.PHILOSOPHIC_MINOR)
    magus = saga.characters[0]
    _settle(saga)
    seasons.set_plan(saga, SeasonPlan("m", 1220, "Spring", "adventure"))
    done = _advance(saga)
    assert magus.alchemy is not None and magus.alchemy.digestion is None
    assert any("Spoiled" in line.result for line in done.record.lines)
    assert saga.laboratories[0].raw_vis == {}


def test_reading_beside_the_digestion_keeps_it_and_a_month_away_spoils_it():
    assert digestion_apply.days_out(None) == 0
    assert digestion_apply.days_out(SeasonPlan("m", 1220, "Spring", "read")) == 0
    lost = SeasonPlan("m", 1220, "Spring", "read", months_lost=1)
    assert digestion_apply.days_out(lost) == 30
    away = SeasonPlan("m", 1220, "Spring", "teach", in_lab=False)
    assert digestion_apply.days_out(away) is None


def test_experimenting_spoils_the_digestion():
    saga = _saga(alchemy.PHILOSOPHIC_MAJOR)
    magus = saga.characters[0]
    _settle(saga)
    plan = _plan(saga, experimenting=True, experiment_die=5)
    _found, work = lab_seasons.work(saga, magus, plan)
    assert work is not None and any("spoils" in n for n in work.notes)
    seasons.set_plan(saga, plan)
    _advance(saga)
    assert magus.alchemy is not None and magus.alchemy.digestion is None
    assert saga.laboratories[0].raw_vis == {}


def test_ready_opened_spaces_open_the_device_and_cut_its_opening():
    saga = _saga(alchemy.PHILOSOPHIC_MAJOR)
    magus = saga.characters[0]
    coral = EnchantedDevice(
        "coral",
        "Red coral",
        holder_kind="laboratory",
        holder_id="lab",
        maker_id="m",
        components=[DeviceComponent("coral", "semi-precious gem", "tiny")],
    )
    saga.enchanted_devices.append(coral)
    _settle(saga, product=DIGEST_SPACES, device_id="coral")
    _advance(saga)
    assert coral.pawns_opened == 2  # CrVi 20 / 10
    opening = SeasonPlan(
        "m",
        saga.current_year,
        saga.current_season,
        enchant_seasons.OPEN,
        lab_id="lab",
        device_id="coral",
    )
    magus.raw_vis = {"vim": 12}
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(6))]
    found, work = lab_seasons.work(saga, magus, opening)
    assert found == [] and work is not None
    assert work.vis_cost == {"Vim": 10}  # 12 less the 2 already open


def test_a_digestion_round_trips_and_bad_values_are_refused():
    alchemy_ = Alchemy(
        digestion=Digestion(lab_id="lab", season="Spring", year=1220, totals=[3]),
        ingredients=[ElixirIngredient("amber", 3, year=1221)],
        elixir_level=2,
        elixir_active=True,
    )
    again = Alchemy.from_dict(asdict(alchemy_))
    assert again == alchemy_
    with pytest.raises(ValueError, match="product"):
        Digestion.from_dict({"product": "gold"})
    with pytest.raises(ValueError, match="bonus"):
        ElixirIngredient.from_dict({"name": "amber", "bonus": "lots"})
    character = Character.from_dict(
        {"id": "m", "name": "M", "type": "magus", "alchemy": asdict(alchemy_)}
    )
    assert character.alchemy == alchemy_


def test_the_talisman_s_panel_says_what_its_mysteries_allow():
    saga = _saga(alchemy.GREAT_TALISMAN, alchemy.CONSUMMATE_TALISMAN)
    staff = EnchantedDevice(
        "staff",
        "Staff",
        talisman=True,
        holder_kind="character",
        holder_id="m",
        maker_id="m",
        effects=[
            InstilledEffect("boost", "Wizard's Boost", "Muto", "Vim", range="Personal")
        ],
    )
    saga.enchanted_devices.append(staff)
    text = device_info_text(saga, staff)
    assert "Great Talisman: an attunement each season" in text
    assert "On his Formulaic spells:[/] Wizard's Boost" in text


# -- the Lesser Elixir through a season ------------------------------------------


def _alchemist() -> Saga:
    saga = _saga(alchemy.LESSER_ELIXIR)
    magus = saga.characters[0]
    magus.background.year_born = 1200  # 20 in 1220: a dose takes 4 pawns
    magus.aging.longevity_modifier = 15
    magus.raw_vis = {"vim": 6}
    saga.books.append(
        Book(
            id="lr",
            name="Lab Text: Longevity Ritual for Parella",
            type="Lab Text",
            text_kind="Longevity Ritual",
            technique="Creo",
            form="Corpus",
            level=20,
            ritual_subject="Parella",
            owner_kind="laboratory",
            owner_id="lab",
        )
    )
    return saga


def _reinvent(saga: Saga, **kw: object) -> SeasonPlan:
    return SeasonPlan(
        "m",
        saga.current_year,
        saga.current_season,
        season.REINVENT_ELIXIR,
        [XpAllocation("ability:Magic Theory")],
        vis_from="character",
        vis_art="Vim",
        **kw,  # type: ignore[arg-type]
    )


def test_reinventing_the_lesser_elixir_adds_its_level_to_aging_rolls():
    saga = _alchemist()
    magus = saga.characters[0]
    assert problems(saga, magus, _reinvent(saga)) == [
        "Name the special ingredient added."
    ]
    plan = _reinvent(saga, title="bloodstone", book_level=4)
    assert problems(saga, magus, plan) == []
    seasons.set_plan(saga, plan)
    _advance(saga)
    # Bloodstone +4, capped at Magic Theory 3: 3 points, Level 2.
    assert magus.alchemy is not None
    assert (magus.alchemy.elixir_level, magus.alchemy.elixir_bonus) == (2, 2)
    assert magus.raw_vis == {"vim": 2}  # the dose: 20 / 5 = 4 pawns
    rolled = aging.roll(magus, 40, 0, 0, random.Random(3))
    assert "- Longevity Ritual 15 - Lesser Elixir 2" in rolled.notes[0]
    # A dose without his ingredients (a ritual made for him) leaves it out.
    other = Character(id="o", name="Parens", type="magus")
    assert "not in this dose" in alchemy.ritual_performed(magus, other)
    assert magus.alchemy.elixir_bonus == 0
    assert "Elixir Level 2" in alchemy.ritual_performed(magus, magus)


def test_the_lesser_elixir_needs_a_ritual_its_text_and_the_vis():
    saga = _alchemist()
    magus = saga.characters[0]
    plan = _reinvent(saga, title="amber", book_level=3)
    magus.raw_vis = {"vim": 3}
    assert "takes 4 pawn(s) of Vim" in problems(saga, magus, plan)[0]
    saga.books.clear()
    assert "Lab Text" in problems(saga, magus, plan)[0]
    magus.aging.longevity_modifier = 0
    assert "no Longevity Ritual" in problems(saga, magus, plan)[0]


def test_ready_opened_spaces_may_be_extra_room_on_top_of_the_capacity():
    saga = _saga(alchemy.PHILOSOPHIC_MAJOR)
    magus = saga.characters[0]
    coral = EnchantedDevice(
        "coral",
        "Red coral",
        holder_kind="laboratory",
        holder_id="lab",
        maker_id="m",
        components=[DeviceComponent("coral", "semi-precious gem", "tiny")],
    )
    saga.enchanted_devices.append(coral)
    _settle(saga, product=DIGEST_SPACES, device_id="coral", extra_room=True)
    _advance(saga)
    # TMRE p. 41: the 2 spaces are room on top of its 12, already open.
    assert (coral.extra_spaces, coral.pawns_opened) == (2, 2)
    assert enchantment.capacity(saga, coral) == 14
    assert "12 pawns" in capacity_text(saga, coral)
    assert "2 spaces of extra room" in capacity_text(saga, coral)
    assert "extra room on top of its capacity" in magus.diary[-1].details
    opening = SeasonPlan(
        "m",
        saga.current_year,
        saga.current_season,
        enchant_seasons.OPEN,
        lab_id="lab",
        device_id="coral",
    )
    magus.raw_vis = {"vim": 12}
    magus.abilities = [Ability("Magic Theory", xp=ability_xp(6))]
    found, work = lab_seasons.work(saga, magus, opening)
    assert found == [] and work is not None
    assert work.vis_cost == {"Vim": 12}  # its normal capacity


def test_a_rebrew_is_limited_by_the_art_score():
    saga = _alchemist()
    magus = saga.characters[0]
    # A dose of 4 pawns of Vim, and his Vim is 4: allowed; Creo vis needs Creo.
    assert lab.ritual_vis_problem(magus, "Vim", 4) == ""
    magus.arts["vim"] = ArtScore(xp=art_xp(3))
    plan = _reinvent(saga, title="amber", book_level=3)
    found = problems(saga, magus, plan)
    assert "at most his Vim score (3)" in found[0] and "p. 261" in found[0]
    text = saga.books[0]
    found, again = lab_seasons.ritual_again(
        saga, magus, saga.laboratories[0], text, "Vim", "character"
    )
    assert again is None and "at most his Vim score (3)" in found[0]
    assert "TMRE" not in found[0] and "p. 42" in found[0]


def test_the_great_elixir_s_test_makes_him_a_being_of_magic():
    saga = _alchemist()
    magus = saga.characters[0]
    magus.virtues_flaws += [_vf(alchemy.UNAGING), _vf(alchemy.GREAT_ELIXIR)]
    assert magus.alchemy is None and not magus.being_of_magic
    # 20 years old: Ease Factor 2; die 1 + Stamina 2 + Level 0 = 3 passes,
    # but first a failure (Stamina -3): +1 to the next attempt.
    magus.characteristics.stamina = -3
    failed = alchemy.great_test(magus, 20, 1, 80)
    assert (failed.ease, failed.total, failed.succeeds) == (2, -2, False)
    assert "did not work" in alchemy.drink_great_elixir(magus, 20, failed)
    assert magus.alchemy is not None and magus.alchemy.great_attempts == 1
    magus.characteristics.stamina = 2
    test = alchemy.great_test(magus, 20, 1, 80)
    assert [line.label for line in test.lines][-1] == "Earlier attempts"
    assert "Magic Might 30" in alchemy.drink_great_elixir(magus, 20, test)
    assert (magus.magic_might, magus.alchemy.immortal_age) == (30, 20)
    assert magus.alchemy.great_attempts == 0 and magus.being_of_magic
    # No more aging rolls nor Warping.
    assert not aging.rolls_this_year(magus, 60)
    assert warping.immune(magus)
    # Later, his Ease Factor stays at the age he transformed; a better
    # potion raises his Might.
    assert alchemy.great_ease_for(magus, 200) == 2
    better = alchemy.great_test(magus, 200, 5, 100)
    alchemy.drink_great_elixir(magus, 200, better)
    assert (magus.magic_might, magus.alchemy.immortal_age) == (40, 20)
    # The sheet shows his Might where a Might would show.
    assert "40 (the Great Elixir)" in info_right_text(saga, magus)


def test_a_being_of_magic_round_trips_and_bad_might_is_refused():
    magus = Character(id="m", name="Desperata", type="magus", magic_might=30)
    magus.alchemy = Alchemy(immortal_age=161)
    back = Character.from_dict(asdict(magus))
    assert (back.magic_might, back.alchemy.immortal_age) == (30, 161)
    assert (
        Character.from_dict({"id": "m", "name": "N", "type": "magus"}).magic_might == 0
    )
    with pytest.raises(ValueError, match="Magic Might"):
        Character.from_dict({**asdict(magus), "magic_might": "lots"})
    with pytest.raises(ValueError, match="immortal_age"):
        Alchemy.from_dict({"immortal_age": "old"})
    device = EnchantedDevice("d", "Coral", extra_spaces=2)
    assert EnchantedDevice.from_dict(asdict(device)).extra_spaces == 2
    with pytest.raises(ValueError, match="extra spaces"):
        EnchantedDevice.from_dict({**asdict(device), "extra_spaces": "2.5"})
    digestion = Digestion(product=DIGEST_SPACES, extra_room=True)
    assert Digestion.from_dict(asdict(digestion)).extra_room is True
