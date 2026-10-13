"""The Saga Content page's figures (saga_content_sheet), without a
front-end."""

from __future__ import annotations

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager import house_rules as hr
from ars_magica_manager import players as pl
from ars_magica_manager import saga_content as sc
from ars_magica_manager import saga_content_sheet as scs
from ars_magica_manager.models import Spell


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
