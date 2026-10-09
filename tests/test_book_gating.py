"""Everything a supplement adds switches off with its book: season
activities, optional rules, and the library's book kinds."""

import re

from ars_magica_manager import book_kinds, sourcebooks
from ars_magica_manager.models import Book, Character, Codex, Saga, SeasonPlan
from ars_magica_manager.rules import activities, options
from ars_magica_manager.screens.forms import (
    _book_fields,
    _saga_fields,
    saga_rule_options,
)
from ars_magica_manager.screens.forms.creation import RULE_OPTION_PREFIX
from ars_magica_manager.screens.forms.season_plans import _study_fields


def _words(text: str) -> str:
    return re.sub(r"[^a-z0-9&]+", " ", text.lower()).strip()


def _cited_book(citation: str) -> str:
    """The book a rules citation opens with ("Covenants, Chapter Seven..." ->
    "Covenants"), matching titles whatever their punctuation."""
    cited = _words(citation)
    found = [
        abbreviation
        for abbreviation, title in sourcebooks.SOURCEBOOKS.items()
        if cited.startswith(_words(title))
    ]
    assert found, f"no known book opens {citation!r}"
    return max(found, key=lambda b: len(sourcebooks.SOURCEBOOKS[b]))


def _core_only(**kwargs) -> Saga:
    return Saga(id="s", name="S", books_in_play=[], **kwargs)


def test_every_activity_carries_the_book_its_rule_cites():
    wrong = {
        key: (activity.book, _cited_book(activity.source))
        for key, activity in activities.ACTIVITIES.items()
        if (activity.book or sourcebooks.CORE) != _cited_book(activity.source)
    }
    assert wrong == {}


def test_every_rule_option_carries_the_book_its_rule_cites():
    wrong = {
        option.key: (option.book, _cited_book(option.source))
        for option in options.OPTIONS
        if (option.book or sourcebooks.CORE) != _cited_book(option.source)
    }
    assert wrong == {}


def test_every_book_kind_names_a_known_book():
    kinds = [
        *book_kinds.OPUS_TYPES.values(),
        *book_kinds.PHYSICAL_FORMS.values(),
        *book_kinds.COLLECTIONS.values(),
        book_kinds.GLOSS,
    ]
    books = {k.book for k in kinds} | {
        book_kinds.PALIMPSEST_BOOK,
        book_kinds.ENCYCLOPEDIA_BOOK,
        book_kinds.EPITOME_BOOK,
    }
    assert books <= set(sourcebooks.SOURCEBOOKS)


def test_supplement_activities_leave_the_menu_with_their_book():
    magus = Character(id="m", name="M", type="magus")
    core = {sourcebooks.CORE}
    offered = {a.key for a in activities.activities_for(magus, books=core)} | {
        a.key for a in activities.activities_for(magus, lab=True, books=core)
    }
    for key in (
        "edit_florilegium",
        "translate_book",
        "take_over_lab",
        "move_lab",
        "hermetic_taming",
        "stabilize_discovery",
        "integrate_insight",
    ):
        assert key not in offered
    # A plan already using one keeps it.
    kept = activities.activities_for(magus, books=core, keep="translate_book")
    assert "translate_book" in {a.key for a in kept}


def test_an_option_from_a_book_out_of_play_is_off_and_not_offered():
    saga = _core_only(rule_options={"harsher_infernal_vis": True})
    assert not options.is_on(saga, "harsher_infernal_vis")
    assert "harsher_infernal_vis" not in {o.key for o in options.offered(saga)}
    keys = {f.key for f in _saga_fields(saga)}
    assert RULE_OPTION_PREFIX + "harsher_infernal_vis" not in keys
    assert RULE_OPTION_PREFIX + "simple_dice_only" in keys
    # Saving the form keeps the hidden choice for when the book comes back.
    kept = saga_rule_options({}, kept=saga.rule_options)
    assert kept == {"harsher_infernal_vis": True}
    saga.books_in_play = None
    assert options.is_on(saga, "harsher_infernal_vis")


def _keys(saga: Saga, book: Book | None = None) -> set[str]:
    return {f.key for f in _book_fields(saga, book, "")}


def test_the_book_form_leaves_off_the_kinds_of_books_out_of_play():
    every = _keys(Saga(id="s", name="S"))
    assert {"opus", "physical_form", "glossed", "epitome"} <= every
    assert {"palimpsest", "encyclopedia", "collection"} <= every
    core = _keys(_core_only())
    for key in (
        "opus",
        "commentary_on",
        "physical_form",
        "glossed",
        "epitome",
        "palimpsest",
        "encyclopedia",
        "collection",
        "florilegium_bonus",
    ):
        assert key not in core


def test_the_book_form_offers_only_the_kinds_in_play():
    saga = Saga(id="s", name="S", books_in_play=["A&A"])
    opus = next(f for f in _book_fields(saga, None, "") if f.key == "opus")
    assert [value for _, value in opus.options] == [book_kinds.LECTURE_COMMENTARY]
    # Florilegium is Covenants', Folio HoH:TL's: no collection to offer.
    assert "collection" not in _keys(saga)
    assert "encyclopedia" in _keys(saga)


def test_a_book_keeps_what_it_already_uses():
    saga = _core_only()
    saga.codices.append(Codex(id="c", name="Tome", palimpsest=True, collection="Folio"))
    book = Book(
        id="b",
        name="Notes",
        type="Tractatus",
        opus=book_kinds.COMMENTARY,
        physical_form="Exemplar",
        glossed=True,
        codex_id="c",
    )
    saga.books.append(book)
    fields = {f.key: f for f in _book_fields(saga, book, "")}
    assert {"opus", "physical_form", "glossed", "palimpsest", "collection"} <= set(
        fields
    )
    assert [value for _, value in fields["opus"].options] == [book_kinds.COMMENTARY]
    assert [value for _, value in fields["collection"].options] == ["Folio"]
    assert "encyclopedia" not in fields


def test_glossing_a_read_needs_covenants_in_play():
    magus = Character(id="m", name="M", type="magus")
    every = Saga(id="s", name="S", characters=[magus])
    assert "gloss" in {f.key for f in _study_fields(every, magus, None)}
    core = _core_only(characters=[magus])
    assert "gloss" not in {f.key for f in _study_fields(core, magus, None)}
    plan = SeasonPlan(
        character_id="m", year=1220, season="Spring", activity="read", gloss=True
    )
    assert "gloss" in {f.key for f in _study_fields(core, magus, plan)}
