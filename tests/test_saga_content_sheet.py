"""The Saga Content page's figures (saga_content_sheet), without a
front-end."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager import house_rules as hr
from ars_magica_manager import players as pl
from ars_magica_manager import saga_content as sc
from ars_magica_manager.forms import saga_content as scf
from ars_magica_manager.models import Spell
from ars_magica_manager.sheets import saga_content as scs


def _saga():
    saga = _sample_saga_with_covenant()
    catalog.use_saga(saga)
    return saga


def test_every_book_is_a_card_marked_in_play_or_not():
    saga = _saga()
    sc.add_source(saga, {"abbreviation": "RhT", "title": "Rhine Homebrew"})
    sc.set_books_in_play(saga, ["RhT"])
    cards = {c.book: c for c in scs.book_cards(saga)}
    assert cards[sourcebooks.CORE].state == scs.ALWAYS
    assert (cards["RhT"].state, cards["RhT"].own) == (scs.IN_PLAY, True)
    assert cards[sourcebooks.SUPPLEMENTS[0]].state == scs.OUT_OF_PLAY
    assert scs.sources_table(saga).rows == [["RhT", "Rhine Homebrew", "0"]]


def test_the_catalogs_count_their_entries_and_what_is_hidden():
    saga = _saga()
    spell = catalog.load_spell_catalog()[0]
    sc.hide_entry(saga, "spells", spell.id)
    sc.set_catalog_shown(saga, "abilities", False)
    rows = {row[0]: row for row in scs.catalogs_table(saga).rows}
    assert rows["Spells"][3] == "1"
    assert rows["Abilities"][1] == "No"
    assert scs.hidden_table(saga).rows == [[spell.name, "Spells"]]


def test_house_rules_are_cards_that_cost_or_give_points():
    saga = _saga()
    for name, kind_type in (("Roman Cellars", "Boon"), ("Ravens", "Hook")):
        hr.add(
            saga,
            hr.COVENANT,
            {"name": name, "type": kind_type, "tier": "Minor", "category": "Site"},
        )
    cellars, ravens = scs.house_rule_cards(saga)
    assert (cellars.kind, cellars.gives, cellars.points) == (
        "Covenant",
        False,
        "Minor Boon: costs 1 point",
    )
    assert ravens.gives


def test_a_spell_row_sorts_a_general_spell_by_number():
    saga = _saga()
    general = Spell("s1", "Wizard's Reach", "Rego", "Vim", None, ritual=True)
    (row,) = scs.spell_rows(saga, [general])
    assert (row.level, row.level_text, row.arts, row.ritual) == (
        None,
        "Gen",
        "ReVi",
        True,
    )


def test_the_players_say_whom_they_play():
    saga = _saga()
    player = pl.add(saga, {"name": "Alex", "passcode": "x"})
    saga.characters[0].background.player_id = player.id
    assert scs.players_table(saga).rows == [["Alex", "Player", saga.characters[0].name]]


def test_a_card_counts_what_its_book_brings_leaving_out_the_zeros():
    saga = _saga()
    sc.add_source(saga, {"abbreviation": "RhT", "title": "Rhine Homebrew"})
    hr.add(
        saga,
        hr.CHARACTER,
        {"name": "Ours", "type": "Virtue", "tier": "Minor", "source": "RhT"},
    )
    cards = {c.book: c for c in scs.book_cards(saga)}
    lab = sum(
        "Covenants" in sourcebooks.books_of(e.source)
        for e in sc.CATALOGS["lab_virtues_flaws"].shared()
    )
    covenants = cards["Covenants"].brings
    assert covenants.startswith(f"{lab} Laboratory Virtues & Flaws, ")
    assert "optional rules" in covenants and "kinds of book" in covenants
    assert not any(part.startswith("0 ") for part in covenants.split(", "))
    # A book with nothing in the app's catalogs or rules says nothing.
    assert cards["HtM"].brings == ""
    # A saga source counts the saga's own entries citing it.
    assert cards["RhT"].brings == "1 Virtue or Flaw"


def test_the_counts_list_each_catalog_once_for_every_card(monkeypatch):
    saga = _saga()
    calls: dict[str, int] = {}

    def counted(key, shared):
        def listing():
            calls[key] = calls.get(key, 0) + 1
            return shared()

        return listing

    for key, info in list(sc.CATALOGS.items()):
        monkeypatch.setitem(
            sc.CATALOGS,
            key,
            sc.SagaCatalog(info.key, info.label, counted(key, info.shared)),
        )
    scs.book_cards(saga)
    assert calls == dict.fromkeys(sc.CATALOGS, 1)


def test_every_supplement_is_in_exactly_one_group():
    grouped = [book for _, _, books in sourcebooks.BOOK_GROUPS for book in books]
    twice = sorted({b for b in grouped if grouped.count(b) > 1})
    missing = [b for b in sourcebooks.SUPPLEMENTS if b not in grouped]
    assert (twice, missing) == ([], [])
    # The core book has a group of its own, before them.
    assert sourcebooks.CORE not in grouped


def test_the_cards_come_grouped_core_book_first_and_saga_sources_last():
    saga = _saga()
    sc.add_source(saga, {"abbreviation": "RhT", "title": "Rhine Homebrew"})
    groups = scs.book_groups(saga, scs.book_cards(saga))
    assert [c.book for c in groups[0].cards] == [sourcebooks.CORE]
    assert (groups[1].heading, groups[1].subheading) == (
        "The Order",
        "Houses of Hermes",
    )
    assert [c.book for c in groups[1].cards] == ["HoH:TL", "HoH:MC", "HoH:S"]
    assert (groups[-1].heading, [c.book for c in groups[-1].cards]) == (
        "The Saga's Own Sources",
        ["RhT"],
    )
    tribunals = next(g for g in groups if g.heading == "Tribunals")
    # Books not yet in the app are skipped; SiS sits beside B&S.
    assert [c.book for c in tribunals.cards][-2:] == ["B&S", "SiS"]
    shown = [c.book for g in groups for c in g.cards]
    assert sorted(shown) == sorted(sc.every_book(saga))


def test_the_chip_toggles_one_book_and_leaves_the_others():
    saga = _saga()
    sc.set_books_in_play(saga, ["Covenants", "HP"])
    scf.toggle_book(saga, "RoP:F").apply()
    assert saga.books_in_play == ["Covenants", "HP", "RoP:F"]
    scf.toggle_book(saga, "Covenants").apply()
    assert saga.books_in_play == ["HP", "RoP:F"]
