"""Transforming Mythic Europe: books copied by magic (pp. 98-105) and the
savings a covenant makes with magic (pp. 120-121; Covenants p. 67)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager import economics as eco
from ars_magica_manager import seasons
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import tme_book_seasons
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Characteristics,
    Covenant,
    Economics,
    EnchantedDevice,
    Inhabitant,
    InstilledEffect,
    KnownSpell,
    Saga,
    SeasonPlan,
    XpAllocation,
)
from ars_magica_manager.rules import options
from ars_magica_manager.rules import tme_books as tb
from ars_magica_manager.rules.rounding import round_away_from_zero
from ars_magica_manager.rules.season_work import problems, work
from ars_magica_manager.rules.season_work import transforming as tw
from ars_magica_manager.rules.xp import ability_xp

QUILL = "spell_the_copyist_s_puissant_quill"
FURROW = "spell_the_first_furrow_guides_the_second_crim_2"
BINDING = "spell_binding_the_mundane_codex"

# -- the table ------------------------------------------------------------------


def test_the_quill_s_ease_factor_follows_the_original_s_quality():
    assert [tb.quill_ease(q) for q in (3, 6, 7, 9, 10, 15)] == [9, 9, 12, 12, 15, 15]


@pytest.mark.parametrize(
    ("quality", "total", "table", "spoiled", "copy"),
    [
        (8, 11, 11, 0, 8),
        (8, 10, 10, 2, 6),  # between rows: the lower one
        (8, 7, 7, 4, 4),
        (8, 5, 5, 6, 2),
        (8, 4, 4, 8, None),  # no readable book
        (5, 8, 11, 0, 5),  # Ease Factor 9: + 3
        (12, 13, 10, 2, 10),  # Ease Factor 15: - 3
        (3, 4, 7, 4, 0),  # never below 0
    ],
)
def test_the_finesse_total_sets_the_copy_s_quality(
    quality: int, total: int, table: int, spoiled: int, copy: int | None
):
    outcome = tb.copy_outcome(quality, total)
    assert (outcome.table_total, outcome.spoiled, outcome.quality) == (
        table,
        spoiled,
        copy,
    )


def test_pages_lab_texts_and_hazards():
    assert tb.book_pages(Book("t", "T", "Tractatus")) == 160
    assert tb.book_pages(Book("s", "S", "Art Summa", level=13)) == 325
    assert tb.book_pages(Book("l", "L", "Lab Text"), 25) == 25
    assert [tb.lab_text_needed(n) for n in (5, 120, 121, 360, 361, 1440)] == [
        11,
        11,
        14,
        14,
        17,
        17,
    ]
    # Past a year's worth no book gives a figure (TME p. 103; DE p. 307).
    assert tb.lab_text_needed(1441) is None
    # A mundane scribe: four pages a day (p. 101), so a tractatus is 40.
    assert tb.scribe_days(160) == 40 and tb.scribe_days(161) == 41
    # Four pages in ten spoiled: risk +2 (p. 103).
    assert tb.hazard_risk(tb.spoiled_pages(7)) == 2
    assert tb.can_bind(6) and not tb.can_bind(5)


def test_a_magic_copy_loses_resonances_and_binding():
    book = Book(
        "b",
        "On Fire",
        "Art Summa",
        art="Ignem",
        level=10,
        quality=9,
        craft=["scribe", "binder", "resonance", "clarified"],
        codex_id="codex",
    )
    loose = tb.magic_copy(book, 7, "character", "m", bound=False)
    assert (loose.quality, loose.craft, loose.physical_form) == (
        7,
        ["scribe"],
        "Unbound",
    )
    assert (loose.copy_of, loose.codex_id, loose.owner_id) == ("b", None, "m")
    bound = tb.magic_copy(book, 9, "character", "m", bound=True)
    assert (bound.craft, bound.physical_form) == (["scribe", "binder"], "")
    assert book.craft == ["scribe", "binder", "resonance", "clarified"]


# -- a large library ---------------------------------------------------------------


def _ignem_library() -> list[Book]:
    best = Book("best", "Best", "Art Summa", art="Ignem", level=6, quality=7)
    summae = [
        Book(f"s{i}", f"S{i}", "Art Summa", art="Ignem", level=5, quality=7)
        for i in range(10)
    ]
    tractatus = [
        Book(f"t{i}", f"T{i}", "Tractatus", art="Ignem", quality=7) for i in range(19)
    ]
    return [best, *summae, *tractatus]


def test_the_large_library_follows_the_book_s_example():
    library = tb.library_score(_ignem_library())
    assert library is not None
    assert (library.level, library.quality, library.best) == (7, 9, "best")
    # Below its Level: Quality + 3; at or above: Quality, for 9 seasons.
    assert tb.library_study(6, library) == (12, None)
    assert tb.library_study(7, library) == (9, 9)
    # A copy adds nothing; no summa, no score.
    copy = Book("c", "C", "Tractatus", art="Ignem", quality=7, copy_of="t0")
    again = tb.library_score([*_ignem_library(), copy])
    assert again == library
    assert tb.library_score([copy]) is None


def test_far_weaker_books_add_nothing():
    best = Book("best", "Best", "Art Summa", art="Ignem", level=15, quality=12)
    weak = Book("weak", "Weak", "Art Summa", art="Ignem", level=4, quality=4)
    poor = Book("poor", "Poor", "Tractatus", art="Ignem", quality=5)
    library = tb.library_score([best, weak, poor])
    assert library is not None
    assert (library.level, library.quality, library.summae, library.tractatus) == (
        15,
        12,
        0,
        0,
    )


# -- the season --------------------------------------------------------------


def _saga(perception: int = 3, finesse: int = 8) -> Saga:
    magus = Character(id="m", name="Scriptor", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(perception=perception)
    magus.abilities = [Ability("Finesse", xp=ability_xp(finesse))]
    magus.spells_known = [KnownSpell(QUILL), KnownSpell(FURROW)]
    covenant = Covenant(id="cov", saga_id="s", name="Keep")
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[magus])
    saga.books_in_play = ["DE", "TME", "Covenants"]
    saga.books.append(
        Book(
            "ign",
            "On Fire",
            "Art Summa",
            art="Ignem",
            level=10,
            quality=9,
            craft=["resonance"],
            owner_kind="character",
            owner_id="m",
        )
    )
    return saga


def _plan(saga: Saga, book_id: str = "ign", **kw: object) -> SeasonPlan:
    return SeasonPlan(
        "m",
        saga.current_year,
        saga.current_season,
        tw.COPY_BY_MAGIC,
        [XpAllocation("ability:Finesse")],
        book_id=book_id,
        **kw,  # type: ignore[arg-type]
    )


def test_copying_by_magic_makes_the_copies_at_the_table_s_quality():
    saga = _saga()
    magus = saga.characters[0]
    assert tb.finesse_total(magus) == 11  # Perception 3 + Finesse 8
    plan = _plan(saga, book_level=3)
    assert problems(saga, magus, plan) == []
    result = work(saga, magus, plan, None)
    assert [b.quality for b in result.books] == [9, 9, 9]
    assert all(b.physical_form == "Unbound" and not b.craft for b in result.books)
    assert result.books[0] is not result.books[1]
    assert "resonances" in " ".join(result.notes)
    seasons.set_plan(saga, plan)
    seasons.finish_season(saga, seasons.resolve(saga), {}, random.Random(1))
    copies = [b for b in saga.books if b.copy_of == "ign"]
    assert len(copies) == 3 and len({b.id for b in copies}) == 3


def test_a_weaker_copyist_loses_quality_and_a_poor_one_makes_nothing():
    saga = _saga(perception=0, finesse=7)
    magus = saga.characters[0]
    assert [b.quality for b in work(saga, magus, _plan(saga), None).books] == [5]
    weak = _saga(perception=0, finesse=4)
    assert "no readable book" in problems(weak, weak.characters[0], _plan(weak))[0]


def test_copying_by_magic_needs_both_spells_and_binding_its_own():
    saga = _saga()
    magus = saga.characters[0]
    magus.spells_known = [KnownSpell(QUILL)]
    assert "The First Furrow Guides the Second" in problems(saga, magus, _plan(saga))[0]
    magus.spells_known.append(KnownSpell(FURROW))
    bind = _plan(saga, quick=True)
    assert "Binding the Mundane Codex" in problems(saga, magus, bind)[0]
    magus.spells_known.append(KnownSpell(BINDING))
    assert problems(saga, magus, bind) == []
    made = work(saga, magus, bind, None).books[0]
    assert (made.physical_form, made.craft) == ("", ["binder"])


def test_lab_texts_copy_flawlessly_only_with_enough_finesse():
    saga = _saga(perception=0, finesse=9)
    magus = saga.characters[0]
    saga.books.append(
        Book(
            "lt",
            "Lab Text: Ward",
            "Lab Text",
            text_kind="Other effect",
            level=30,
            raw=True,
            author_id="m",
            owner_kind="character",
            owner_id="m",
        )
    )
    plan = _plan(saga, book_id="lt", book_level=5)  # 150 levels: 14 needed
    assert problems(saga, magus, plan) == []
    result = work(saga, magus, plan, None)
    assert len(result.books) == 5 and all(b.raw for b in result.books)
    assert "botched page" in result.notes[0]
    saga.rule_options[options.HAZARDOUS_LAB_TEXTS] = True
    assert "risk +1" in work(saga, magus, plan, None).notes[0]  # 2 in 10 spoiled
    saga.rule_options[options.NO_MAGICAL_LAB_TEXTS] = True
    assert "written by hand" in problems(saga, magus, plan)[0]
    few = _plan(saga, book_id="lt", book_level=4)  # 120 levels: 11 needed
    saga.rule_options.clear()
    magus.abilities = [Ability("Finesse", xp=ability_xp(11))]
    assert "flawlessly" in work(saga, magus, few, None).notes[0]


def _scrinium(uses: str = "3", bind_uses: str = "3") -> EnchantedDevice:
    """TME pp. 101-103's Superb Scrinium, its two activations a text."""
    return EnchantedDevice(
        "scrin",
        "Superb Scrinium",
        holder_kind="covenant",
        holder_id="cov",
        effects=[
            InstilledEffect("f", tb.IMAGE_SPELL, level=22, uses_per_day=uses),
            InstilledEffect("q", tb.QUILL_SPELL, level=15, uses_per_day="Unlimited"),
            InstilledEffect("b", tb.BINDING_SPELL, level=22, uses_per_day=bind_uses),
        ],
    )


def test_a_copying_device_is_capped_by_its_uses_a_day():
    device = _scrinium()
    assert tb.copies_books(device) and tb.binds_books(device)
    assert tb.device_books_a_day(device, bound=False) == 3
    assert tb.device_books_a_day(_scrinium("6", "2"), bound=True) == 2
    assert tb.device_books_a_day(_scrinium("Unlimited"), bound=False) is None
    assert tb.device_season_books(device, bound=True) == 3 * 91
    plain = EnchantedDevice("p", "Plain", effects=[InstilledEffect("x", "Pilum")])
    assert not tb.copies_books(plain)


def test_copying_by_a_device_needs_no_spells_but_keeps_its_cap():
    saga = _saga()
    magus = saga.characters[0]
    magus.spells_known = []
    saga.enchanted_devices = [_scrinium()]
    assert [d.id for d in tw.copy_devices(saga, magus)] == ["scrin"]
    plan = _plan(saga, device_id="scrin", book_level=10, quick=True)
    assert problems(saga, magus, plan) == []
    result = work(saga, magus, plan, None)
    assert len(result.books) == 10
    assert all(b.physical_form == "" for b in result.books)  # its own Binding
    assert "Copied by Superb Scrinium, 3 book(s) a day at most" in result.notes[0]
    assert any("4 pages a day" in n and "63 days" in n for n in result.notes)
    too_many = _plan(saga, device_id="scrin", book_level=3 * 91 + 1)
    assert "at most 3 book(s) a day" in problems(saga, magus, too_many)[0]
    gone = _plan(saga, device_id="nothing")
    assert "copying device" in problems(saga, magus, gone)[0]


def test_lab_texts_past_a_year_s_worth_are_flagged():
    saga = _saga(perception=5, finesse=15)
    magus = saga.characters[0]
    saga.books.append(
        Book(
            "lt",
            "Lab Text: Ward",
            "Lab Text",
            text_kind="Other effect",
            level=50,
            author_id="m",
            owner_kind="character",
            owner_id="m",
        )
    )
    plan = _plan(saga, book_id="lt", book_level=30)  # 1,500 levels
    assert "the troupe decides" in work(saga, magus, plan, None).notes[0]


def test_the_season_form_reads_its_fields():
    saga = _saga()
    magus = saga.characters[0]
    keys = {
        f.key
        for f in tme_book_seasons.fields(saga, magus, None, lambda *a: lambda v: True)
    }
    assert keys == {
        "magic_copy_book_id",
        "magic_copy_device",
        "magic_copies",
        "magic_bind",
    }
    (_, read), *_ = tme_book_seasons.READS
    assert read(
        {
            "magic_copy_book_id": "ign",
            "magic_copies": 2,
            "magic_bind": True,
            "magic_copy_device": "scrin",
        }
    ) == {
        "book_id": "ign",
        "book_level": 2,
        "quick": True,
        "device_id": "scrin",
    }


def test_the_options_come_from_the_book():
    for key in (options.HAZARDOUS_LAB_TEXTS, options.NO_MAGICAL_LAB_TEXTS):
        assert options.OPTIONS_BY_KEY[key].book == "TME"


# -- technological savings -------------------------------------------------------


def test_a_pound_a_point_splits_as_the_economics_tab_does():
    assert sum(tb.POUND_SPLIT.values()) == tb.SHILLINGS_PER_POUND
    # The tab's rates per 10 points: provisions 5, wages 2, consumables 2,
    # buildings 1 (Covenants pp. 63-65).
    assert {k: v / 2 for k, v in tb.POUND_SPLIT.items()} == {
        "provisions": 5,
        "wages": 2,
        "consumables": 2,
        "buildings": 1,
    }


def test_the_capacious_silo_follows_the_book_s_example():
    # 50 points, a fifth lost a year (p. 121).
    assert tb.grain_after_year(20_000, 50, "Covered only") == 14_800
    assert tb.grain_after_year(14_800, 50, "Covered only") == 10_640
    assert tb.grain_years(tb.SILO_BUSHELS, 50, "Covered only") == 6
    yearly = tb.bread_saving(50, "Three quarters")
    assert yearly == 18.75 and yearly * 6 == 112.5
    assert tb.bread_saving(50, "Half") == 12.5
    assert tb.grain_years(tb.SILO_BUSHELS, 50, "Protected well") > 6


def _covenant_saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="cov1", saga_id="s", name="Dammerstein")
    magus = Character(id="mag1", name="Corvinus", type="magus", covenant_id="cov1")
    saga = Saga(
        id="s",
        name="Saga",
        current_year=1220,
        covenants=[covenant],
        characters=[magus],
    )
    # Enough covenfolk that half the Provisions covers the magic below.
    covenant.inhabitants.append(
        Inhabitant(id="folk", kind="inhabitant", name="Folk", quantity=100)
    )
    saga.enchanted_devices = [
        EnchantedDevice(
            "baker",
            "Elfin Oven",
            holder_kind="covenant",
            holder_id="cov1",
            effects=[InstilledEffect("e1", "The Elfin Baker", level=20)],
        ),
        EnchantedDevice(
            "wand",
            "Wand of Flame",
            holder_kind="covenant",
            holder_id="cov1",
            effects=[InstilledEffect("e2", "Pilum", level=20)],
        ),
    ]
    return saga, covenant


def _magic(saga: Saga, covenant: Covenant) -> eco.Row:
    return next(r for r in eco.summarize(saga, covenant).savings if r.key == "magic")


def test_the_magic_row_adds_devices_rituals_grain_and_the_typed_figure():
    saga, covenant = _covenant_saga()
    economics = covenant.economics
    assert _magic(saga, covenant).savings == 0
    economics.saving_devices = ["baker"]
    economics.ritual_magnitudes = 4
    economics.magic_savings = 2
    row = _magic(saga, covenant)
    # Elfin Baker 4 magnitudes + Ritual 4 x 5 + 2 typed.
    assert row.savings == 26
    assert "Elfin Oven, 4 magnitude(s) 4" in row.basis
    points = eco.summarize(saga, covenant).inhabitant_points
    economics.magic_grain = tb.year_need(points)
    with_grain = _magic(saga, covenant)
    # A fraction rounds away from zero (the tab's rule).
    assert with_grain.savings == round_away_from_zero(
        26 + tb.bread_saving(points, "Half")
    )
    summary = eco.summarize(saga, covenant)
    before = sum(r.savings for r in summary.expenditure)
    assert summary.cost_savings == before + with_grain.savings
    # The year's end spends the Rituals and eats the grain.
    eco.close_year(saga, covenant)
    assert economics.ritual_magnitudes == 0
    assert economics.magic_grain < tb.year_need(points)
    assert _magic(saga, covenant).savings == 6


def test_magic_doing_laborers_work_shares_their_half_of_the_provisions():
    saga, covenant = _covenant_saga()
    covenant.inhabitants.clear()
    economics = covenant.economics
    economics.saving_devices = ["baker"]
    economics.ritual_magnitudes = 4
    summary = eco.summarize(saga, covenant)
    provisions = next(r for r in summary.expenditure if r.key == "provisions")
    row = _magic(saga, covenant)
    # The oven's 4 and the Rituals' 20 are cut to half the Provisions
    # (Covenants p. 67).
    assert row.savings <= provisions.first / 2 + 1
    assert "over half the Provisions with the laborers" in row.basis
    working = tb.magic_savings(
        2,
        [],
        4,
        points=0,
        grain=0,
        care="Covered only",
        share="Half",
        provisions_room=0,
        labor_room=5,
    )
    # The typed 2 isn't capped; the Rituals' 20 are, to 5.
    assert working.total == 7


def test_the_magic_row_s_form_marks_devices():
    saga, covenant = _covenant_saga()
    row = _magic(saga, covenant)
    fields = covenant_forms.economics_row_fields(covenant, "savings", row, saga)
    keys = [f.key for f in fields]
    assert keys[:2] == ["_n", "magic_savings"]
    assert {"saves__baker", "saves__wand", "magic_grain", "grain_care"} <= set(keys)
    assert "saves__baker" not in [
        f.key for f in covenant_forms.economics_row_fields(covenant, "savings", row)
    ]
    covenant.economics.saving_devices = ["gone"]
    values = {f.key: f.value for f in fields if f.kind != "info"}
    values.update({"saves__baker": True, "ritual_magnitudes": 2})
    eco.apply_row_edit(covenant.economics, "magic", values)
    assert covenant.economics.saving_devices == ["gone", "baker"]
    assert covenant.economics.ritual_magnitudes == 2


def test_bad_grain_values_are_refused_on_load():
    with pytest.raises(ValueError, match="grain_care"):
        Economics.from_dict({"grain_care": "In a ditch"})
    with pytest.raises(ValueError, match="magic_grain"):
        Economics.from_dict({"magic_grain": -5})
    loaded = Economics.from_dict({"magic_grain": 300, "bread_share": "Three quarters"})
    assert (loaded.magic_grain, loaded.grain_care) == (300, "Covered only")
