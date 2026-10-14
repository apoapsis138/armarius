"""A record's printed sheet: its blocks (print_layout's character layout)
and where pages break (paginate), with no UI library."""

from itertools import pairwise

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager.models import Possession, ScoredTrait, VirtueFlawInstance


def _headings(doc: pl.Document) -> list[str]:
    return [b.text for b in doc.blocks if isinstance(b, pl.Heading)]


def _blocks(doc: pl.Document, kind: type) -> list:
    return [b for b in doc.blocks if isinstance(b, kind)]


def _leandro():
    saga = _sample_saga_with_covenant()
    return saga, saga.characters[0]


# ---------------------------------------------------------------- the sheet


def test_a_magus_has_the_magic_pages_each_from_a_new_page():
    saga, magus = _leandro()
    doc = pl.document(saga, "character", magus)
    assert doc.title == "Leandro"
    headings = _headings(doc)
    for heading in (
        "Abilities",
        "Combat & Condition",
        "Hermetic Arts",
        "Casting Scores",
    ):
        assert heading in headings
    starts = [
        type(doc.blocks[i + 1]).__name__ + getattr(doc.blocks[i + 1], "text", "")
        for i, b in enumerate(doc.blocks)
        if isinstance(b, pl.NewPage)
    ]
    assert starts[0] == "HeadingHermetic Arts"
    assert "GrimoireTitle" in starts
    assert starts[-1] == "HeadingDescription & Biography"


def test_a_companion_has_no_magic_pages():
    saga, character = _leandro()
    character.type = "companion"
    doc = pl.character_document(saga, character)
    headings = _headings(doc)
    assert "Hermetic Arts" not in headings
    assert "Hermetic Background" not in headings
    assert not _blocks(doc, pl.GrimoireTitle)
    assert "Combat & Condition" in headings


def test_the_characteristics_are_one_row_of_eight():
    saga, magus = _leandro()
    (boxes,) = _blocks(pl.character_document(saga, magus), pl.ScoreBoxes)
    assert boxes.items[0][0] == "Intelligence"
    assert len(boxes.items) == 8
    assert dict(boxes.items)["Intelligence"] == "+3"


def test_empty_sections_are_left_off():
    saga, magus = _leandro()
    headings = _headings(pl.character_document(saga, magus))
    for empty in (
        "Reputations",
        "Personality Traits",
        "Raw Vis",
        "Diary",
        "Appearance",
    ):
        assert empty not in headings


def test_traits_print_once_there_are_some():
    saga, magus = _leandro()
    magus.personality_traits = [ScoredTrait("Brave", 2)]
    doc = pl.character_document(saga, magus)
    assert "Personality Traits" in _headings(doc)
    assert ("Brave", "+2") in [f for b in _blocks(doc, pl.Facts) for f in b.facts]


def test_abilities_carry_their_marks_and_category_groups():
    saga, magus = _leandro()
    doc = pl.character_document(saga, magus)
    table = next(b for b in _blocks(doc, pl.Table) if b.columns[0].title == "Ability")
    (row,) = table.rows
    assert row[0].text == "Magic Theory"
    assert row[0].symbol == pl.Symbol("ability", "Magic Theory", "Academic")
    assert table.groups == ((0, "Academic"),)


def test_arts_carry_their_symbols():
    saga, magus = _leandro()
    doc = pl.character_document(saga, magus)
    arts = next(b for b in _blocks(doc, pl.Columns) if isinstance(b.left[0], pl.Table))
    creo = arts.left[0].rows[0][0]
    assert (creo.text, creo.symbol) == ("Creo", pl.Symbol("art", "Creo"))


def test_a_virtue_taken_twice_is_printed_once_with_its_count():
    saga, magus = _leandro()
    great = {
        "vf_id": "vf_great_characteristic",
        "params": {"characteristic": "intelligence"},
    }
    magus.virtues_flaws += [VirtueFlawInstance(**great), VirtueFlawInstance(**great)]
    columns = _blocks(pl.character_document(saga, magus), pl.Columns)[0]
    names = [b.name for b in columns.left if isinstance(b, pl.Entry)]
    assert names == ["Affinity with Creo", "Great Intelligence × 2"]


# ---------------------------------------------------------------- the Grimoire


def test_the_grimoire_is_short_unless_full_spells_is_chosen():
    saga, magus = _leandro()
    (short,) = _blocks(pl.character_document(saga, magus), pl.Spell)
    assert short.parameters.startswith("R: ")
    assert short.casting.startswith("Casting Total ")
    assert short.description == ""
    full = pl.character_document(saga, magus, pl.PrintOptions(full_spells=True))
    (spell,) = _blocks(full, pl.Spell)
    found = next(s for s in saga.spells if s.id == "spell1")
    assert spell.description == found.description


def test_the_grimoire_groups_spells_under_their_form():
    saga, magus = _leandro()
    doc = pl.character_document(saga, magus)
    title = doc.blocks.index(_blocks(doc, pl.GrimoireTitle)[0])
    heading = doc.blocks[title + 1]
    assert isinstance(heading, pl.Heading)
    assert heading.symbol is not None and heading.symbol.kind == "art"


# ---------------------------------------------------------------- combat


def _condition(character, saga) -> pl.Condition:
    return _blocks(pl.character_document(saga, character), pl.Condition)[0]


def test_wounds_have_five_boxes_for_light_medium_and_heavy():
    saga, magus = _leandro()
    magus.wounds.light = 2
    wounds = _condition(magus, saga).wounds.rows
    assert [(w.name, w.boxes) for w in wounds] == [
        ("Light", 5),
        ("Medium", 5),
        ("Heavy", 5),
        ("Incapacitated", 1),
        ("Dead", 1),
    ]
    assert wounds[0].range == "1–5" and wounds[0].ticked == 2
    assert wounds[-1].range == "21+"


def test_fatigue_ticks_the_levels_spent():
    saga, magus = _leandro()
    magus.fatigue_level = "tired"
    rows = _condition(magus, saga).fatigue.rows
    assert [r.name for r in rows if r.ticked] == ["Winded", "Weary", "Tired"]
    assert rows[1].recovery == "2 min."


def test_weapons_are_filled_in_and_blank_rows_left_to_pencil_in():
    saga, magus = _leandro()
    (weapons,) = _blocks(pl.character_document(saga, magus), pl.Weapons)
    assert all(not row.name for row in weapons.rows)
    magus.inventory.append(
        Possession(id="sword", kind="weapon", name="Sword", weapon_attack=4)
    )
    (weapons,) = _blocks(pl.character_document(saga, magus), pl.Weapons)
    assert weapons.rows[0].name == "Sword"
    assert weapons.rows[0].initiative
    assert sum(1 for row in weapons.rows if not row.name) >= pl.SPARE_WEAPONS


# ---------------------------------------------------------------- pagination


def _bottoms(pages, pieces) -> list[float]:
    out = []
    for page in pages:
        for place in page:
            piece = pieces[place.index]
            if place.last:
                height = piece.header + sum(piece.rows[place.first : place.last])
            else:
                height = piece.height
            out.append(place.top + height)
    return out


def test_nothing_runs_past_the_page():
    pieces = [pl.Piece(90, 10) for _ in range(12)]
    pages = pl.paginate(pieces, 300)
    assert max(_bottoms(pages, pieces)) <= 300
    assert sorted(p.index for page in pages for p in page) == list(range(12))


def test_a_table_that_fits_a_page_moves_whole_rather_than_split():
    table = pl.Piece(200, 0, header=20, rows=(20,) * 9)
    pages = pl.paginate([pl.Piece(250), table], 300)
    assert len(pages) == 2
    assert [p.index for p in pages[1]] == [1]
    assert pages[1][0].last == 0  # the whole table


def test_a_heading_goes_to_the_next_page_with_what_it_heads():
    pieces = [pl.Piece(260), pl.Piece(20, 0, keep_with_next=True), pl.Piece(60)]
    pages = pl.paginate(pieces, 300)
    assert [[p.index for p in page] for page in pages] == [[0], [1, 2]]


def test_a_table_longer_than_a_page_splits_between_rows_with_its_header():
    rows = (20.0,) * 30
    table = pl.Piece(20 + sum(rows), 0, header=20, rows=rows)
    pages = pl.paginate([pl.Piece(100), table], 300)
    parts = [p for page in pages for p in page if p.index == 1]
    assert len(parts) == 3
    assert parts[0].first == 0 and parts[-1].last == 30
    assert all(a.last == b.first for a, b in pairwise(parts))
    assert all(p.header for p in parts)
    assert max(_bottoms(pages, [pl.Piece(100), table])) <= 300


def test_new_page_starts_a_page_but_never_an_empty_one():
    pieces = [
        pl.Piece(50),
        pl.Piece(0, new_page=True),
        pl.Piece(0, new_page=True),
        pl.Piece(50),
    ]
    pages = pl.paginate(pieces, 300)
    assert [[p.index for p in page] for page in pages] == [[0], [3]]
