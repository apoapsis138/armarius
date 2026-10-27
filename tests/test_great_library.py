"""The Rhine's Great Library at Durenmar (Guardians of the Forests pp.
55-57): credit for contributions, who is exempt, and what a search of
its floors finds, with the forms that record them."""

from __future__ import annotations

import os
import random
from collections.abc import Sequence
from typing import Any

import pytest
from support import everything_saga

from ars_magica_manager import books, tribunal_packages
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Covenant,
    HermeticBackground,
    Saga,
    SeasonPlan,
    Tribunal,
    VirtueFlawInstance,
)
from ars_magica_manager.models.seasons import next_season, season_order
from ars_magica_manager.rules import activities, book_seasons
from ars_magica_manager.rules import great_library as gl
from ars_magica_manager.rules import rhine_ranks as ranks
from ars_magica_manager.sections import (
    LIBRARY_CREDIT_SECTION,
    LIBRARY_RULES_SECTION,
    LIBRARY_SEARCHES_SECTION,
)
from ars_magica_manager.tribunal_packages import rhine_library as lib


class Faces(random.Random):
    """Each d10 thrown shows the next of `faces` (0-9, a 0 reading as 10
    on a simple die)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args: int, **kwargs: int) -> int:
        return self.faces.pop(0)


def _magus(
    ident: str, covenant: str = "cov1", house: str = "house_flambeau", rank: str = ""
) -> Character:
    magus = Character(
        id=ident,
        name=ident.title(),
        type="magus",
        covenant_id=covenant,
        hermetic=HermeticBackground(house=house),
    )
    if rank:
        magus.virtues_flaws.append(VirtueFlawInstance(rank))
    return magus


def _saga() -> tuple[Saga, Tribunal]:
    saga = everything_saga()
    saga.covenants.append(
        Covenant(id="cov_dur", saga_id="s", name="Durenmar", tribunal_id="rhine")
    )
    saga.characters += [
        _magus("corvinus", rank=ranks.MASTER),
        _magus("ricardus", "cov_dur", "house_bonisagus"),
        _magus("murion", "cov_dur", "house_bonisagus", ranks.ARCHMAGE),
        _magus("lucan"),
    ]
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return saga, tribunal


def _char(saga: Saga, ident: str) -> Character:
    found = saga.character(ident)
    assert found is not None
    return found


def _values(form: Form, **changes: Any) -> dict[str, Any]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    shown = {f.key for f in form.fields() if f.show_if is None or f.show_if(values)}
    return {k: v for k, v in values.items() if k in shown}


def _save(form: object, **changes: Any) -> Any:
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def _search(
    saga: Saga, tribunal: Tribunal, faces: Sequence[int], **changes: Any
) -> dict[str, Any]:
    form = lib.search_form(saga, tribunal, rng=Faces(*faces))
    _save(form, **changes)
    return lib.searches(tribunal)[-1]


def _give(saga: Saga, tribunal: Tribunal, magus: str, seasons: int = 2) -> None:
    _save(
        lib.contribute_form(saga, tribunal),
        magus=magus,
        kind=gl.BOOK,
        what="Tractatus, Muto Animal Q 8",
        seasons=seasons,
    )


# -- the rules (pp. 55-57) --


def test_who_is_exempt_bonisagus_and_durenmars_own():
    saga, _ = _saga()
    assert gl.is_exempt(saga, _char(saga, "ricardus"))
    durenmar_flambeau = _magus("x", "cov_dur")
    assert gl.is_exempt(saga, durenmar_flambeau)
    assert not gl.is_exempt(saga, _char(saga, "corvinus"))


def test_art_summa_search_bonus_by_rank_and_privilege():
    saga, _ = _saga()
    assert gl.art_search_bonus(saga, _char(saga, "lucan")) == 0
    assert gl.art_search_bonus(saga, _char(saga, "corvinus")) == 3
    assert gl.art_search_bonus(saga, _char(saga, "ricardus")) == 3
    # An archmage's +6 is his whole bonus, not on top of the +3.
    assert gl.art_search_bonus(saga, _char(saga, "murion")) == 6
    assert gl.art_search_total(9, 6) == 20
    assert gl.art_search_total(4, 3) == 17


def test_summa_and_tractatus_quality_caps():
    # 30 - level, or 24, whichever is lower.
    assert gl.summa_quality_cap(4) == 24
    assert gl.summa_quality_cap(18) == 12
    assert gl.summa_quality(9, 5, 18) == 12
    assert gl.summa_quality(6, 0, 16) == 11
    assert gl.tractatus_quality(10, 4) == 12
    assert gl.tractatus_quality(3, 2) == 7


def test_durenmar_lore_loses_a_point_per_earlier_use():
    assert gl.lore_bonus(2, 0) == 2
    assert gl.lore_bonus(2, 1) == 1
    assert gl.lore_bonus(2, 5) == 0


def test_art_summa_found_tied_or_in_use():
    saga, _ = _saga()
    search = gl.Search(gl.ART_SUMMA, "Animal", 16)
    # 4 + 10 + 3 = 17 beats 16; Quality: simple die 6 + 5.
    found = gl.search(Faces(4, 6), saga, _char(saga, "corvinus"), search)
    assert found.outcome == gl.FOUND and found.quality == 11
    assert found.roll == "4 + 13 = 17"
    tied = gl.search(Faces(3), saga, _char(saga, "corvinus"), search)
    assert tied.outcome == gl.CERTAMEN
    low = gl.search(Faces(2), saga, _char(saga, "corvinus"), search)
    assert low.outcome == gl.IN_USE and "level 17" in low.lines[-1]


def test_ability_summa_is_a_simple_die_alone():
    saga, _ = _saga()
    search = gl.Search(gl.ABILITY_SUMMA, "Magic Theory", 5)
    assert gl.search(Faces(3), saga, _char(saga, "murion"), search).outcome == gl.NONE
    assert gl.search(Faces(5), saga, _char(saga, "murion"), search).outcome == (
        gl.CERTAMEN
    )
    found = gl.search(Faces(7, 0), saga, _char(saga, "murion"), search)
    assert found.outcome == gl.FOUND and found.quality == 15


def test_spell_texts_standard_and_others():
    saga, _ = _saga()
    corvinus = _char(saga, "corvinus")
    standard = gl.Search(gl.STANDARD, "Pilum of Fire")
    assert gl.search(Faces(2), saga, corvinus, standard).outcome == gl.IN_USE
    assert gl.search(Faces(3), saga, corvinus, standard).outcome == gl.CERTAMEN
    assert gl.search(Faces(0, 0), saga, corvinus, standard).outcome == gl.NONE
    # 9 is 6 over 3: one Mastery tractatus, simple die 4 + 2.
    found = gl.search(Faces(9, 4), saga, corvinus, standard)
    assert found.outcome == gl.FOUND and found.mastery == [6]
    other = gl.Search(gl.OTHER_SPELL, "The Cursed Day", ease=12)
    assert gl.search(Faces(5), saga, corvinus, other).outcome == gl.NONE
    assert gl.search(Faces(0, 0), saga, corvinus, other).outcome == gl.FLAWED
    general = gl.Search(gl.GENERAL, "Wizard's Sidestep 25")
    assert gl.search(Faces(7), saga, corvinus, general).outcome == gl.FOUND


def test_devices_similar_or_exact():
    saga, _ = _saga()
    corvinus = _char(saga, "corvinus")
    device = gl.Search(gl.DEVICE, "A ring of warding", ease=9)
    assert gl.search(Faces(8), saga, corvinus, device).outcome == gl.NONE
    assert gl.search(Faces(9), saga, corvinus, device).outcome == gl.SIMILAR
    # A 1 doubles: 1 then 8 is 16, beating 9 by 7.
    assert gl.search(Faces(1, 8), saga, corvinus, device).outcome == gl.FOUND


def test_lab_notes_and_records():
    saga, _ = _saga()
    corvinus = _char(saga, "corvinus")
    corvinus.characteristics.intelligence = 2
    corvinus.abilities.append(Ability("Magic Theory", xp=75))
    named = gl.search(Faces(), saga, corvinus, gl.Search(gl.NOTES, "Notatus"))
    assert named.outcome == gl.FOUND and named.roll == "no roll"
    notes = gl.Search(gl.NOTES, "golems", ease=12)
    assert gl.search(Faces(5), saga, corvinus, notes).outcome == gl.FOUND
    assert gl.search(Faces(4), saga, corvinus, notes).outcome == gl.NONE
    # Intelligence 2 + OoH Lore 0 against 9: a 7 the first day, then
    # 6 the second (-1) fails; a 9 on day 2 makes 10.
    records = gl.Search(gl.RECORDS, "Dankmar", ease=9)
    found = gl.search(Faces(6, 9), saga, corvinus, records)
    assert found.outcome == gl.FOUND and found.roll == "day 2"
    season = gl.search(Faces(), saga, corvinus, gl.Search(gl.RECORDS, "Dankmar"))
    assert season.outcome == gl.FOUND


def test_records_give_up_when_a_ten_cannot_succeed():
    saga, _ = _saga()
    corvinus = _char(saga, "corvinus")
    corvinus.characteristics.intelligence = 0
    records = gl.Search(gl.RECORDS, "Dankmar", ease=12)
    # 0 + a 2 each day: by day 1 a 10 couldn't make 12 even then.
    lost = gl.search(Faces(2, 2, 2), saga, corvinus, records)
    assert lost.outcome == gl.NONE


def test_odds_say_what_the_die_must_show():
    saga, _ = _saga()
    corvinus = _char(saga, "corvinus")
    lines = gl.odds(saga, corvinus, gl.Search(gl.ART_SUMMA, "Vim", 18))
    assert "must show 6 or more" in lines[0] and "a master" in lines[0]
    lines = gl.odds(saga, corvinus, gl.Search(gl.ART_SUMMA, "Vim", 21))
    assert "can't be found" in lines[0]


# -- the package: credit, searches and the tab --


def test_the_rhine_adds_the_great_library_tab_after_the_gilds():
    saga, tribunal = _saga()
    package = tribunal_packages.of(tribunal)
    assert [t.tab_id for t in package.tabs] == ["tab-trib-gilds", "tab-trib-library"]
    library = package.tabs[1]
    assert library.text is not None
    assert library.text.section_id == LIBRARY_RULES_SECTION
    assert [e.section_id for e in library.lists] == [
        LIBRARY_CREDIT_SECTION,
        LIBRARY_SEARCHES_SECTION,
    ]
    assert tribunal_packages.package_verb(tribunal, "library_search") is not None
    ops = tribunal_forms.tribunal_ops(saga, tribunal)
    assert LIBRARY_CREDIT_SECTION in ops and LIBRARY_SEARCHES_SECTION in ops
    assert "Librarian" in dict(lib.facts(saga, tribunal))


def test_contribute_earns_credit_and_the_grid_shows_it():
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    _save(
        lib.contribute_form(saga, tribunal),
        magus="corvinus",
        kind=gl.COPYING,
        seasons=1,
    )
    ledger = lib.ledger_of(tribunal, "corvinus")
    assert ledger is not None and lib.credit(ledger) == 3
    grid = lib.credit_grid(saga, tribunal)
    assert grid.rows[0][:2] == ["Corvinus", "Keep"]
    assert "a season copying" in grid.rows[0][2]
    assert grid.rows[0][3] == "3 seasons"
    assert lib.credit_title(saga, tribunal) == "Credit (1 magus)"
    info = lib.credit_info(saga, tribunal, 0)
    assert "3 seasons, 0 used" in info


def test_contribute_needs_a_book_or_words():
    saga, tribunal = _saga()
    form = lib.contribute_form(saga, tribunal)
    values = _values(form, magus="corvinus", kind=gl.BOOK, book=None, what="")
    assert form.validate is not None and form.validate(values)
    vis = _values(form, magus="corvinus", kind=gl.VIS, what="")
    assert form.validate(vis)


def test_reading_a_book_found_takes_credit_and_lends_the_book():
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    entry = _search(
        saga,
        tribunal,
        (4, 6),
        magus="corvinus",
        sought=gl.ART_SUMMA,
        subject="Animal",
        level=16,
    )
    assert entry["outcome"] == gl.FOUND and entry["credit_taken"]
    ledger = lib.ledger_of(tribunal, "corvinus")
    assert ledger is not None and ledger["used"] == 1
    book = next(b for b in saga.books if b.id == entry["book_id"])
    assert book.type == "Art Summa" and book.art == "Animal"
    assert (book.level, book.quality) == (16, 11)
    assert (book.owner_kind, book.owner_id) == ("character", "corvinus")
    assert book.description.startswith(lib.BORROWED)
    # The planner's Study from a Book offers it.
    assert book in books.studyable_books(saga, _char(saga, "corvinus"))
    grid = lib.searches_grid(saga, tribunal)
    assert grid.rows[0][2:] == [
        "Animal summa, level 16",
        "4 + 13 = 17",
        "Found: Q 11",
    ]


def _found_summa(saga: Saga, tribunal: Tribunal) -> tuple[dict[str, Any], Book]:
    """Corvinus, with two seasons of credit, finds and reads an Animal summa."""
    _give(saga, tribunal, "corvinus")
    entry = _search(
        saga,
        tribunal,
        (4, 6),
        magus="corvinus",
        sought=gl.ART_SUMMA,
        subject="Animal",
        level=16,
    )
    book = next(b for b in saga.books if b.id == entry["book_id"])
    return entry, book


def _reading(saga: Saga, book: Book, season: str, year: int) -> list[str]:
    plan = SeasonPlan("corvinus", year, season, activities.READ, book_id=book.id)
    return activities.problems(_char(saga, "corvinus"), plan, saga)


def test_a_library_book_is_lent_only_for_the_seasons_of_credit_paid():
    saga, tribunal = _saga()
    entry, book = _found_summa(saga, tribunal)
    when = (saga.current_season, saga.current_year)
    assert book.loan_seasons == [season_order(season=when[0], year=when[1])]
    assert not any("Great Library" in p for p in _reading(saga, book, *when))
    later = next_season(*when)
    assert any("Great Library" in p for p in _reading(saga, book, *later))
    # Edit pays a second season of credit: the loan covers the next too.
    form = lib.edit_search_form(saga, entry, tribunal)
    _save(form, seasons_paid=2)
    assert entry["seasons_paid"] == 2 and len(book.loan_seasons or []) == 2
    assert not any("Great Library" in p for p in _reading(saga, book, *later))
    ledger = lib.ledger_of(tribunal, "corvinus")
    assert ledger is not None and lib.credit_left(ledger) == 0
    # No credit left for a third.
    third = lib.edit_search_form(saga, entry, tribunal)
    assert third.validate is not None
    assert "credit left" in (third.validate(_values(third, seasons_paid=3)) or "")
    # Deleting the search gives back both seasons.
    remove = lib.search_ops(saga, tribunal).remove(0)
    assert isinstance(remove, Confirm) and "2 seasons" in remove.question
    remove.apply()
    assert ledger["used"] == 0


def test_a_library_book_is_never_copied_or_given_for_credit():
    saga, tribunal = _saga()
    _entry, book = _found_summa(saga, tribunal)
    plan = SeasonPlan(
        "corvinus",
        saga.current_year,
        saga.current_season,
        book_seasons.COPY_BOOK,
        book_id=book.id,
    )
    problems, _ = book_seasons.work(saga, _char(saga, "corvinus"), plan)
    assert any("may not be copied" in p for p in problems)
    offered = [value for _, value in lib._book_options(saga, _char(saga, "corvinus"))]
    assert book.id not in offered


def test_the_storyguide_may_raise_a_found_books_quality_to_the_absolute_limit():
    saga, tribunal = _saga()
    entry, book = _found_summa(saga, tribunal)
    assert gl.suggested_quality_cap(gl.ART_SUMMA, 16) == 14
    assert gl.absolute_quality_limit(gl.ART_SUMMA) == 28
    assert gl.absolute_quality_limit(gl.TRACTATUS) == 14
    form = lib.edit_search_form(saga, entry, tribunal)
    assert form.validate is not None
    assert "28" in (form.validate(_values(form, quality=29)) or "")
    _save(form, quality=20)
    assert book.quality == 20 and entry["quality"] == 20


def test_no_credit_refuses_reading_but_not_notes_or_the_exempt():
    saga, tribunal = _saga()
    form = lib.search_form(saga, tribunal, rng=Faces(5))
    values = _values(form, magus="corvinus", sought=gl.TRACTATUS, subject="Vim")
    assert form.validate is not None and "no credit" in (form.validate(values) or "")
    unread = _values(
        form, magus="corvinus", sought=gl.TRACTATUS, subject="Vim", read=False
    )
    assert form.validate(unread) is None
    notes = _values(form, magus="corvinus", sought=gl.NOTES, subject="Notatus")
    assert form.validate(notes) is None
    exempt = _values(form, magus="ricardus", sought=gl.TRACTATUS, subject="Vim")
    assert form.validate(exempt) is None
    entry = _search(
        saga, tribunal, (5,), magus="ricardus", sought=gl.TRACTATUS, subject="Vim"
    )
    assert not entry["credit_taken"]
    # The exempt magus is listed in Credit all the same.
    assert lib.credit_grid(saga, tribunal).rows[0][3] == "exempt"


def test_durenmar_lore_penalty_counts_earlier_uses_in_the_subject():
    saga, tribunal = _saga()
    ricardus = _char(saga, "ricardus")
    ricardus.abilities.append(Ability("Organization Lore: Durenmar", xp=15))
    first = _search(
        saga,
        tribunal,
        (3,),
        magus="ricardus",
        sought=gl.TRACTATUS,
        subject="Vim",
        lore=True,
    )
    assert first["quality"] == 3 + 2 + 2 and first["lore_used"]
    second = _search(
        saga,
        tribunal,
        (3,),
        magus="ricardus",
        sought=gl.TRACTATUS,
        subject="vim",
        lore=True,
    )
    assert second["quality"] == 3 + 2 + 1
    other = _search(
        saga,
        tribunal,
        (3,),
        magus="ricardus",
        sought=gl.TRACTATUS,
        subject="Ignem",
        lore=True,
    )
    assert other["quality"] == 7
    assert lib.earlier_uses(tribunal, "ricardus", "Vim") == 2


def test_other_spells_need_the_troupes_ease_factor():
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    form = lib.search_form(saga, tribunal)
    values = _values(form, magus="corvinus", sought=gl.OTHER_SPELL, subject="X")
    assert form.validate is not None and form.validate(values)
    values = _values(
        form, magus="corvinus", sought=gl.OTHER_SPELL, subject="X", ease=25
    )
    assert form.validate(values)
    values = _values(
        form, magus="corvinus", sought=gl.OTHER_SPELL, subject="X", ease=12
    )
    assert form.validate(values) is None


def test_deleting_a_search_returns_the_book_and_the_credit():
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    entry = _search(
        saga, tribunal, (5,), magus="corvinus", sought=gl.TRACTATUS, subject="Vim"
    )
    books = len(saga.books)
    ops = lib.search_ops(saga, tribunal)
    assert ops.remove is not None
    step = ops.remove(0)
    assert isinstance(step, Confirm) and "goes back" in step.question
    step.apply()
    assert len(saga.books) == books - 1
    assert entry not in lib.searches(tribunal)
    ledger = lib.ledger_of(tribunal, "corvinus")
    assert ledger is not None and ledger["used"] == 0


def test_edit_credit_and_search():
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    ops = lib.credit_ops(saga, tribunal)
    assert ops.edit is not None
    _save(ops.edit(0), granted=1, used=2, note="Spring 1219 studied Animal.")
    ledger = lib.ledger_of(tribunal, "corvinus")
    assert ledger is not None and lib.credit_left(ledger) == 1
    assert lib.credit_grid(saga, tribunal).rows[0][3] == "1 season"
    _search(saga, tribunal, (5,), magus="corvinus", sought=gl.NOTES, subject="Golems")
    search_ops = lib.search_ops(saga, tribunal)
    assert search_ops.edit is not None
    _save(search_ops.edit(0), outcome=gl.CERTAMEN, note="Fought Urgen.")
    assert lib.headline(lib.searches(tribunal)[0]) == "Certamen"


def test_a_saga_without_magi_refuses_the_search():
    saga, tribunal = _saga()
    saga.characters = [c for c in saga.characters if c.type != "magus"]
    assert isinstance(lib.search_step(saga, tribunal, 0), Refuse)
    assert isinstance(lib.credit_ops(saga, tribunal).add(), Refuse)  # type: ignore[misc]


def test_contribute_fills_the_seasons_each_gift_earns():
    saga, tribunal = _saga()
    kind = next(
        f for f in lib.contribute_form(saga, tribunal).fields() if f.key == "kind"
    )
    assert kind.fills is not None
    assert kind.fills({"kind": gl.COPYING}) == {"seasons": 1}
    assert kind.fills({"kind": gl.BOOK}) == {"seasons": 2}


def test_the_desktop_rules_the_library_off_as_a_ledger():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.ledger_rows import LedgerRow
    from ars_magica_manager.gui.markup_html import plain
    from ars_magica_manager.gui.themes import PALETTES
    from ars_magica_manager.gui.tribunal import TribunalPage

    QApplication.instance() or QApplication([])
    saga, tribunal = _saga()
    _give(saga, tribunal, "corvinus")
    _search(saga, tribunal, (5,), magus="corvinus", sought=gl.TRACTATUS, subject="Vim")
    page = TribunalPage(saga, tribunal, PALETTES[0])
    assert "Great Library" in page.chapters()
    page.codex.open_chapter("Great Library")
    rows = page.findChildren(LedgerRow)
    assert len(rows) == 2
    rows[1].clicked()
    assert page.codex.inspector.title.text() == "Vim tractatus"
    assert "Quality: simple die 5 + 2" in plain(page.codex.inspector.body.text())
