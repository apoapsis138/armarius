"""Arithmetic magic: Hermetic Numerology's book and Rotes, Hermetic
Geometry's figures and lines, Hermetic Architecture's structures (The
Mysteries Revised Edition pp. 91-101), and their two seasons."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager.forms import arithmetic_seasons as arith_forms
from ars_magica_manager.forms import device as device_forms
from ars_magica_manager.models import (
    INVESTED,
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    InstilledEffect,
    Laboratory,
    Progress,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import enchant_seasons
from ars_magica_manager.rules import tmre_numerology as tn
from ars_magica_manager.rules.season_work import arithmetic as aw
from ars_magica_manager.rules.season_work import base as season_base
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _numera(*vf_ids: str, arithmetic: int = 6) -> Character:
    """The book's Numera (p. 93): Intelligence 3, Stamina 1, Creo 14,
    Ignem 12, Magic Theory 6, Artes Liberales (arithmetic) 6."""
    magus = Character(id="m", name="Numera", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=3, stamina=1)
    magus.virtues_flaws = [VirtueFlawInstance(v) for v in (tn.NUMEROLOGY, *vf_ids)]
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(6)),
        Ability("Artes Liberales", xp=ability_xp(arithmetic), specialty="arithmetic"),
    ]
    magus.arts = {
        "creo": ArtScore(xp=art_xp(14)),
        "ignem": ArtScore(xp=art_xp(12)),
        "rego": ArtScore(xp=art_xp(10)),
        "vim": ArtScore(xp=art_xp(12)),
    }
    magus.assigned_lab_id = "lab"
    return magus


def _book(kind: str = tn.LESSER_BOOK, pawns: int = 8) -> EnchantedDevice:
    return EnchantedDevice(
        "book",
        "De Theoria Magica",
        INVESTED,
        holder_kind="character",
        holder_id="m",
        maker_id="m",
        pawns_opened=pawns,
        mystery_device=kind,
    )


def _saga(magus: Character, *devices: EnchantedDevice, aura: int = 5) -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep", aura=aura)],
        characters=[magus],
        laboratories=[Laboratory(id="lab", covenant_id="cov", name="Study")],
        enchanted_devices=list(devices),
    )


# -- the Numerologist's Book ----------------------------------------------------


def test_book_bonus_is_four_or_eight_capped_by_artes_liberales() -> None:
    magus = _numera()
    assert tn.book_bonus(_saga(magus, _book()), magus) == 4
    magus.abilities[0] = Ability("Magic Theory", xp=ability_xp(8))
    greater = _book(tn.GREATER_BOOK, 16)
    assert tn.book_bonus(_saga(magus, greater), magus) == 6  # Artes Liberales 6
    line = tn.book_line(_saga(magus, greater), magus)
    assert line is not None and "capped by Artes Liberales" in line.label


def test_book_needs_its_maker_the_virtue_and_its_pawns() -> None:
    magus = _numera()
    assert tn.book_bonus(_saga(magus, _book(pawns=7)), magus) == 0
    saga = _saga(magus, _book(pawns=7))
    assert "8 pawns" in (tn.book_problem(saga, saga.enchanted_devices[0]) or "")
    other = _book()
    other.maker_id = "x"
    assert tn.book_bonus(_saga(magus, other), magus) == 0
    plain = _numera()
    plain.virtues_flaws = []
    assert tn.book_bonus(_saga(plain, _book()), plain) == 0


def test_greater_book_needs_magic_theory_8() -> None:
    magus = _numera()
    saga = _saga(magus, _book(tn.GREATER_BOOK, 16))
    assert "Magic Theory 8" in (tn.book_problem(saga, saga.enchanted_devices[0]) or "")


# -- Rotes -------------------------------------------------------------------------


def test_rote_lab_total_is_the_books_example() -> None:
    """Int 3 + Creo 14 + Ignem 12 + Magic Theory 6 + Arithmetic 6 + lesser
    book 4 + aura 5 = 50, Rotes up to level 10 (p. 93)."""
    magus = _numera()
    saga = _saga(magus, _book())
    total = tn.rote_lab_total(saga, magus, "Creo", "Ignem", saga.laboratories[0])
    assert total.total == 50
    assert tn.max_rote_level(int(total.total)) == 10
    labels = [line.label for line in total.lines]
    assert "Arithmetic (Artes Liberales)" in labels


def test_arithmetic_in_the_lab_is_capped_by_magic_theory() -> None:
    magus = _numera(arithmetic=8)
    saga = _saga(magus)
    total = tn.rote_lab_total(saga, magus, "Creo", "Ignem", saga.laboratories[0])
    line = next(x for x in total.lines if x.label.startswith("Arithmetic"))
    assert line.amount == 6


def test_rote_points_and_the_season_fit() -> None:
    rotes = tn.parse_rotes(
        "Ignite: 10; Daylight: 10 (text); Warmth: 5 (text); Red-hot: 10",
        "Creo",
        "Ignem",
    )
    assert rotes is not None
    assert [tn.rote_points(r) for r in rotes] == [20, 10, 5, 20]
    # The book's 45 levels in one season.
    assert tn.rotes_problem(50, rotes[1:]) is None
    assert "take 55 points" in (tn.rotes_problem(50, rotes) or "")
    too_high = tn.parse_rotes("Blaze: 15", "Creo", "Ignem") or []
    assert "level 1 to 10" in (tn.rotes_problem(50, too_high) or "")
    assert tn.parse_rotes("no level here", "Creo", "Ignem") is None


def test_rote_casting_in_a_church() -> None:
    """Stamina 1 + Creo 14 + Ignem 12 + Arithmetic 6 + aura (Divine 4:
    -12) = 21, half rounded up 11, enough for a level 10 Rote (p. 93)."""
    magus = _numera()
    saga = _saga(magus, _book())
    score = tn.rote_casting_score(
        saga, magus, "Creo", "Ignem", aura=4, aura_realm="Divine"
    )
    assert score.total == 21
    total = tn.rote_casting_total(score.total)
    assert total == 11 and tn.rote_works(total, 10)
    assert tn.rote_penetration(total, 10, 2) == 3
    with_book = tn.rote_casting_score(
        saga, magus, "Creo", "Ignem", aura=4, aura_realm="Divine", book=True
    )
    assert with_book.total == 25


def test_rotes_known_read_from_their_records() -> None:
    magus = _numera()
    magus.progress = [
        Progress(tn.ROTE_KIND, "Daylight (CrIg 10)", 10, 10, done=True),
        Progress(tn.ROTE_KIND, "Half-done (CrIg 5)", 5, 2),
    ]
    known = tn.rotes_known(magus)
    assert [(r.name, r.technique, r.form, r.level) for r in known] == [
        ("Daylight", "Creo", "Ignem", 10)
    ]
    assert "Daylight (CrIg 10)" in " ".join(tn.reminders(None, magus))


# -- Hermetic Geometry ---------------------------------------------------------


def test_geometry_bonuses_need_the_virtue() -> None:
    magus = _numera(tn.GEOMETRY)
    assert tn.geometry_bonus(magus, traces=True, regular_figure=True) == 6
    assert tn.geometry_bonus(magus, traces=False, regular_figure=True) == 3
    assert tn.geometry_bonus(_numera(), traces=True, regular_figure=True) == 0


@pytest.mark.parametrize(
    ("paces", "level", "ease"),
    [(10, 1, 9), (200, 8, 9), (225, 9, 9), (275, 10, 10), (1050, 20, 20)],
)
def test_line_range_distance_level(paces: int, level: int, ease: int) -> None:
    assert tn.distance_level(paces) == level
    assert tn.line_ease(paces) == ease


def test_line_calculation_time_and_miss() -> None:
    assert tn.line_rounds(9) == 3
    assert tn.line_rounds(10) == 4
    assert tn.line_miss(9, 7) == 18
    assert tn.line_miss(9, 12) == 0
    assert tn.perfect_shape_ease(with_tools=False) == 15
    assert tn.perfect_shape_ease(with_tools=True) == 6


# -- Hermetic Architecture -----------------------------------------------------


def test_structure_spaces_components_and_placement() -> None:
    """The ten-floor tower: hard stone 4 x Size 7 = 28 spaces, seven
    components, placed against 13 (pp. 97-98)."""
    assert tn.structure_spaces("hard stone", 7) == 28
    assert tn.components_needed(7) == 7
    assert tn.placement_ease(7) == 13
    assert tn.placement_ease(8) == 14
    with pytest.raises(ValueError):
        tn.structure_spaces("gold", 7)


@pytest.mark.parametrize(
    ("effect", "size", "level"),
    [(50, 7, 60), (25, 8, 40), (84, 6, 89), (34, 7, 44), (99, 8, 114)],
)
def test_bind_the_mystical_structure_level(effect: int, size: int, level: int) -> None:
    """The book's examples, pp. 98-100."""
    assert tn.bind_level(effect, size) == level


def test_aura_guidelines_and_investigation() -> None:
    assert tn.aura_guideline(1) == 35
    assert tn.aura_guideline(5) == 55
    assert tn.aura_guideline(9) == 75
    with pytest.raises(ValueError):
        tn.aura_guideline(10)
    assert tn.investigation_total(31) == 15


def test_component_capacity_must_reach_the_structures_spaces() -> None:
    magus = _numera(tn.ARCHITECTURE)
    small = EnchantedDevice("c", "Pillar", INVESTED, capacity_override=20)
    saga = _saga(magus, small)
    assert "needs 28" in (tn.component_problem(saga, small, "hard stone", 7) or "")
    assert tn.component_problem(saga, small, "wood", 7) is None


def test_book_bonus_adds_to_a_components_enchantment() -> None:
    magus = _numera(tn.ARCHITECTURE)
    component = EnchantedDevice(
        "c",
        "Silver staff",
        INVESTED,
        holder_kind="laboratory",
        holder_id="lab",
        maker_id="m",
        capacity_override=28,
        pawns_opened=28,
        mystery_device=tn.COMPONENT,
        effects=[InstilledEffect("e", "Perfection", "Rego", "Terram", level=34)],
    )
    saga = _saga(magus, _book(), component)
    plan = SeasonPlan("m", 1220, "Spring", "enchant_items", lab_id="lab")
    total = enchant_seasons._effect_total(
        saga, magus, plan, saga.laboratories[0], component, component.effects[0]
    )
    assert any(line.label.startswith("Numerologist's Book") for line in total.lines)
    component.mystery_device = ""
    total = enchant_seasons._effect_total(
        saga, magus, plan, saga.laboratories[0], component, component.effects[0]
    )
    assert not any(line.label.startswith("Numerologist's") for line in total.lines)


# -- the seasons -------------------------------------------------------------------


def _rote_plan(rotes: str = "Daylight: 10 (text); Red-hot: 10") -> SeasonPlan:
    return SeasonPlan(
        "m",
        1220,
        "Spring",
        aw.INVENT_ROTES,
        technique="Creo",
        form="Ignem",
        title=rotes,
    )


def test_invent_rotes_season() -> None:
    magus = _numera()
    saga = _saga(magus, _book())
    plan = _rote_plan()
    assert season_base.problems(saga, magus, plan) == []
    work = season_base.work(saga, magus, plan, random.Random(1))
    assert work.progress == [
        (tn.ROTE_KIND, "Daylight (CrIg 10)", 10, 10),
        (tn.ROTE_KIND, "Red-hot (CrIg 10)", 10, 10),
    ]
    assert "Rote Lab Total 50" in work.notes[0]


def test_invent_rotes_problems() -> None:
    magus = _numera()
    saga = _saga(magus, _book())
    assert (
        "take 60 points"
        in season_base.problems(saga, magus, _rote_plan("A: 10; B: 10; C: 10"))[0]
    )
    plain = _numera()
    plain.virtues_flaws = []
    assert (
        "Hermetic Numerology"
        in season_base.problems(_saga(plain), plain, _rote_plan())[0]
    )
    no_lab = _numera()
    no_lab.assigned_lab_id = None
    assert "laboratory" in season_base.problems(_saga(no_lab), no_lab, _rote_plan())[0]


def _bind_plan(level: int | None = 34, size: str = "7", rework: str = "") -> SeasonPlan:
    params = {"size": size} if size else {}
    if rework:
        params["rework_days"] = rework
    return SeasonPlan(
        "m",
        1220,
        "Summer",
        aw.BIND_STRUCTURE,
        title="The Perfected Tower",
        book_level=level,
        effect_params=params,
        vis_from="character",
    )


def test_bind_season_checks() -> None:
    magus = _numera(tn.ARCHITECTURE)
    magus.raw_vis = {"vim": 9}
    saga = _saga(magus)
    # Level 44: 9 pawns of Vim, within Vim 12.
    assert season_base.problems(saga, magus, _bind_plan()) == []
    assert "Size" in season_base.problems(saga, magus, _bind_plan(size=""))[0]
    assert "level" in season_base.problems(saga, magus, _bind_plan(level=None))[0]
    assert (
        "days recomputing"
        in (season_base.problems(saga, magus, _bind_plan(rework="45"))[0])
    )
    assert season_base.problems(saga, magus, _bind_plan(rework="1")) == []
    magus.raw_vis = {"vim": 3}
    assert "9 pawn(s)" in season_base.problems(saga, magus, _bind_plan())[0]
    plain = _numera()
    assert (
        "Hermetic Architecture"
        in season_base.problems(_saga(plain), plain, _bind_plan())[0]
    )


def test_bind_season_preview_and_roll() -> None:
    magus = _numera(tn.ARCHITECTURE)
    magus.raw_vis = {"vim": 9}
    saga = _saga(magus)
    preview = season_base.work(saga, magus, _bind_plan(), None)
    assert "against 13" in preview.notes[0] and "level 44" in preview.notes[0]
    assert preview.vis_cost == {"Vim": 9}
    magus.arts["rego"] = ArtScore(xp=art_xp(25))
    magus.arts["vim"] = ArtScore(xp=art_xp(20))
    bound = 0
    for seed in range(40):
        work = season_base.work(saga, magus, _bind_plan(), random.Random(seed))
        assert work.notes
        if work.progress:
            bound += 1
            assert work.progress == [(aw.STRUCTURE_KIND, "The Perfected Tower", 1, 1)]
            assert work.vis_cost == {"Vim": 9}
            assert "Bind the Mystical Structure (level 44)" in work.notes[-1]
    assert bound


def test_placing_tries_again_while_the_season_lasts():
    # No limit of tries: each miss costs the days of recomputing (a day to
    # a month), and he tries again until the season ends (TMRE p. 98).
    magus = _numera(tn.ARCHITECTURE)
    magus.raw_vis = {"vim": 9}
    magus.characteristics.intelligence = -5  # 13 is hard to reach
    saga = _saga(magus)
    many = 0
    for seed in range(60):
        work = season_base.work(
            saga, magus, _bind_plan(rework="1"), random.Random(seed)
        )
        placing = work.notes[0]
        if "failed" in placing:
            misses = int(placing.split("failed ")[1].split(" time")[0])
            many = max(many, misses)
            assert f"({misses} day(s) in all)" in placing
    assert many > 3
    ended = 0
    for seed in range(60):
        work = season_base.work(
            saga, magus, _bind_plan(rework="30"), random.Random(seed)
        )
        if "season ends" in work.notes[0]:
            ended += 1
            assert "failed 4 time(s)" in work.notes[0]
            assert not work.vis_cost
    assert ended


# -- the forms ---------------------------------------------------------------------


def test_season_form_reads_and_prefills() -> None:
    reads = {choices[0]: read for choices, read in arith_forms.READS}
    rote = reads[aw.INVENT_ROTES](
        {"rote_technique": "Creo", "rote_form": "Ignem", "rotes": " A: 5 "}
    )
    assert rote == {"technique": "Creo", "form": "Ignem", "title": "A: 5"}
    bind = reads[aw.BIND_STRUCTURE](
        {"structure_name": "Tower", "structure_level": 34, "structure_size": "7"}
    )
    assert bind == {"title": "Tower", "book_level": 34, "effect_params": {"size": "7"}}
    rework = reads[aw.BIND_STRUCTURE](
        {"structure_name": "Tower", "structure_size": "7", "structure_rework": 1}
    )
    assert rework["effect_params"] == {"size": "7", "rework_days": "1"}
    fields = {
        f.key: f for f in arith_forms.fields(_bind_plan(), lambda *_a: lambda _v: True)
    }
    assert fields["structure_size"].value == "7"
    assert fields["structure_level"].value == 34
    assert fields["structure_rework"].value is None


def test_device_form_marks_a_numerologists_book() -> None:
    device = EnchantedDevice("d", "Book", INVESTED)
    copy = device_forms.device_from_values(
        _saga(_numera()), device, {"mystery_device": tn.LESSER_BOOK}
    )
    assert copy.mystery_device == tn.LESSER_BOOK
