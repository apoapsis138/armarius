"""Codices: several books bound in one tome (Covenants, Varieties of
Manuscript). Each is studied on its own, one reader a season for the whole
codex, and they are always kept together."""

from ars_magica_manager import books as bk
from ars_magica_manager import transfer
from ars_magica_manager.models import (
    Book,
    Character,
    Codex,
    Covenant,
    Saga,
    SeasonPlan,
)
from ars_magica_manager.rules import activities


def _saga() -> Saga:
    covenant = Covenant(id="cov", name="Keep", saga_id="s")
    readers = [
        Character(
            id=cid,
            name=name,
            type="companion",
            covenant_id="cov",
        )
        for cid, name in (("ana", "Ana"), ("bo", "Bo"))
    ]
    books = [
        Book(
            id="hunt",
            name="De arte venandi: Hunt",
            type="Tractatus",
            subject_kind="Ability",
            ability="Hunt",
            quality=9,
            owner_kind="covenant",
            owner_id="cov",
            codex_id="falconry",
        ),
        Book(
            id="animals",
            name="De arte venandi: Animal Handling",
            type="Ability Summa",
            ability="Animal Handling",
            level=4,
            quality=9,
            owner_kind="covenant",
            owner_id="cov",
            codex_id="falconry",
        ),
        Book(
            id="alone",
            name="Herbal",
            type="Ability Summa",
            ability="Medicine",
            level=5,
            quality=14,
            owner_kind="covenant",
            owner_id="cov",
        ),
    ]
    return Saga(
        id="s",
        name="Saga",
        covenants=[covenant],
        characters=readers,
        books=books,
        codices=[Codex(id="falconry", name="De arte venandi cum avibus")],
    )


def _read(saga: Saga, character_id: str, book_id: str) -> SeasonPlan:
    plan = SeasonPlan(character_id, 1220, "Spring", activities.READ, book_id=book_id)
    saga.season_plans.append(plan)
    return plan


def test_a_codexs_books_are_listed_together():
    saga = _saga()
    order = [saga.books[0], saga.books[2], saga.books[1]]
    assert [b.id for b in bk.grouped(saga, order)] == ["hunt", "animals", "alone"]


def test_moving_one_book_moves_its_whole_codex():
    saga = _saga()
    bk.set_owner(saga, saga.books[0], "character", "ana")
    assert [(b.id, b.owner_id) for b in saga.books] == [
        ("hunt", "ana"),
        ("animals", "ana"),
        ("alone", "cov"),
    ]


def test_an_emptied_codex_is_dropped():
    saga = _saga()
    saga.books = [b for b in saga.books if b.codex_id != "falconry"]
    bk.prune_codices(saga)
    assert saga.codices == []


def test_a_palimpsest_is_read_and_priced_at_minus_3():
    saga = _saga()
    saga.codices[0].palimpsest = True
    hunt = saga.books[0]
    assert bk.effective_quality(saga, hunt) == 6
    assert bk.cost(hunt, saga) == 6
    assert bk.effective_quality(saga, saga.books[2]) == 14
    plan = _read(saga, "ana", "hunt")
    gains = activities.outcome(saga.characters[0], plan, saga).gains
    assert [g.result.xp for g in gains] == [6]


def test_one_reader_a_season_for_the_whole_codex():
    saga = _saga()
    _read(saga, "ana", "hunt")
    bo_plan = _read(saga, "bo", "animals")
    assert any(
        "bound in the same codex" in p
        for p in activities.problems(saga.characters[1], bo_plan, saga)
    )
    # A book bound alone, or the same codex another season, is free.
    bo_plan.book_id = "alone"
    assert activities.problems(saga.characters[1], bo_plan, saga) == []
    bo_plan.book_id, bo_plan.season = "animals", "Summer"
    assert activities.problems(saga.characters[1], bo_plan, saga) == []


def test_two_readers_of_one_book_in_a_season():
    saga = _saga()
    _read(saga, "ana", "alone")
    bo_plan = _read(saga, "bo", "alone")
    assert activities.problems(saga.characters[1], bo_plan, saga) == [
        "Ana is reading Herbal this season: one reader at a time."
    ]


def test_the_details_panel_names_the_codex():
    saga = _saga()
    text = bk.detail_text(saga, saga.books[1])
    assert "De arte venandi cum avibus" in text
    assert "(2 books, one reader a season)" in text
    assert bk.row_label(saga, saga.books[1]).startswith(bk.CODEX_MARK)
    assert not bk.row_label(saga, saga.books[2]).startswith(bk.CODEX_MARK)


def test_a_csv_binds_rows_sharing_a_codex_name():
    csv = (
        "name,type,ability,level,quality,codex\n"
        "Hunt,Tractatus,Hunt,,9,De arte venandi\n"
        "Animals,Ability Summa,Animal Handling,4,9,De arte venandi\n"
        "Herbal,Ability Summa,Medicine,5,14,\n"
    )
    result = bk.parse_books_csv(csv)
    assert result.skipped == [] and result.unused_columns == []
    saga = Saga(id="s", name="Saga", covenants=[Covenant("cov", "Keep", "s")])
    bk.add_imported_books(saga, result.books, saga.covenants[0])
    [codex] = saga.codices
    assert codex.name == "De arte venandi"
    assert [b.name for b in saga.books if b.codex_id == codex.id] == [
        "Hunt",
        "Animals",
    ]
    assert saga.books[2].codex_id is None


def test_an_exported_covenant_takes_its_codices():
    saga = _saga()
    data = transfer.export_data(saga, saga.covenants[0])
    target = Saga(id="t", name="Other", codices=[Codex("falconry", "Taken")])
    plan = transfer.plan_import(target, data)
    transfer.apply(target, plan)
    new = target.codices[1]
    assert new.name == "De arte venandi cum avibus" and new.id != "falconry"
    assert sorted(b.id for b in target.books if b.codex_id == new.id) == [
        "animals",
        "hunt",
    ]


def test_a_book_still_to_be_set_cannot_be_studied():
    saga = _saga()
    saga.books[1].level = None
    plan = _read(saga, "ana", "animals")
    assert activities.problems(saga.characters[0], plan, saga) == [
        "De arte venandi: Animal Handling's Level is still to be set: edit the "
        "book first."
    ]
    assert "A season's reading" not in bk.detail_text(saga, saga.books[1])


def test_a_congregational_book_takes_several_readers():
    saga = _saga()
    saga.books[2].physical_form = "Congregational"
    _read(saga, "ana", "alone")
    bo_plan = _read(saga, "bo", "alone")
    assert activities.problems(saga.characters[1], bo_plan, saga) == []
