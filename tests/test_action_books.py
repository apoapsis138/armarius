"""A supplement's More actions are offered only while its book is in play."""

from dataclasses import replace

from ars_magica_manager import action_books, sourcebooks
from ars_magica_manager.actions import MORE_MENU, NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import Character, Saga


def _saga(books: list[str] | None) -> Saga:
    knight = Character(id="k", name="Sir Hugo", type="companion")
    return Saga(id="s", name="S", characters=[knight], books_in_play=books)


def _reputations(saga: Saga) -> set[str]:
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="k")
    return {item.action for item in menu_forms.placed(page, "Reputations")}


def test_every_character_action_is_given_a_book_or_none():
    placed = {
        action
        for action, spots in menu_forms.PLACES.items()
        if any(kind == NodeKind.CHARACTER for kind, _ in spots)
    }
    unclassified = placed - action_books.ACTION_BOOKS.keys() - action_books.NO_BOOK
    assert unclassified == set(), (
        "add these to action_books.ACTION_BOOKS or NO_BOOK: "
        + ", ".join(sorted(unclassified))
    )
    both = action_books.ACTION_BOOKS.keys() & action_books.NO_BOOK
    assert both == set()


def test_every_listed_action_and_book_is_known():
    actions = {item.action for item in MORE_MENU} | menu_forms.PLACES.keys()
    unknown_actions = (
        action_books.ACTION_BOOKS.keys() | action_books.NO_BOOK
    ) - actions
    assert unknown_actions == set()
    unknown_books = {
        book
        for books in action_books.ACTION_BOOKS.values()
        for book in books
        if book not in sourcebooks.SUPPLEMENTS
    }
    assert unknown_books == set()


def test_the_tournament_needs_lords_of_men():
    offered = _reputations(_saga([]))
    assert "tourney_season" not in offered
    assert "melee_event" not in offered
    assert "end_session" in offered
    offered = _reputations(_saga(["LoM"]))
    assert {"tourney_season", "melee_event"} <= offered


def test_every_book_in_play_offers_everything():
    assert {"tourney_season", "melee_event"} <= _reputations(_saga(None))


def test_house_acclaim_comes_with_either_houses_book():
    saga = Saga(id="s", name="S", books_in_play=["HoH:S"])
    assert action_books.book_allows("house_acclaim", saga)
    assert not action_books.book_allows(
        "house_acclaim", replace(saga, books_in_play=[])
    )


def test_a_definitive_edition_action_ignores_the_books():
    assert action_books.book_allows(
        "take_harm", Saga(id="s", name="S", books_in_play=[])
    )
