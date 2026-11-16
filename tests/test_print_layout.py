"""A record's printed sheet: its blocks (print_layout's character layout)
and where pages break (paginate), with no UI library."""

from itertools import pairwise

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager import print_records as pr
from ars_magica_manager.models import (
    Familiar,
    Player,
    Possession,
    ScoredTrait,
    Secret,
    VirtueFlawInstance,
)
from ars_magica_manager.viewing import STORYGUIDE_VIEWER, viewer_for


def _headings(doc: pl.Document) -> list[str]:
    return [b.text for b in doc.blocks if isinstance(b, pl.Heading)]


def _blocks(doc: pl.Document, kind: type) -> list:
    return [b for b in doc.blocks if isinstance(b, kind)]


def _leandro():
    saga = _sample_saga_with_covenant()
    return saga, saga.characters[0]


# ---------------------------------------------------------------- the sheet


def test_a_magus_full_record_follows_the_page_plan():
    saga, magus = _leandro()
    magus.hermetic.wizards_sigil = "A faint smell of rain"
    doc = pr.document(saga, "character", magus)
    assert doc.title == "Leandro"
    headings = _headings(doc)
    # Page 1: Abilities and Combat & Condition, then the Virtues and Flaws
    # flowing on; the Hermetic Background waits for the Arts' page.
    order = [
        "Abilities",
        "Combat & Condition",
        "Virtues & Flaws",
        "Hermetic Background",
        "Hermetic Arts",
        "Description & Biography",
    ]
    assert [h for h in headings if h in order] == order
    starts = [
        type(doc.blocks[i + 1]).__name__ + getattr(doc.blocks[i + 1], "text", "")
        for i, b in enumerate(doc.blocks)
        if isinstance(b, pl.NewPage)
    ]
    assert starts == [
        "HeadingHermetic Background",
        "HeadingDescription & Biography",
        "GrimoireTitle",
    ]
    # The Grimoire is last.
    assert isinstance(doc.blocks[-1], pl.Spell)


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
        "Secrets",
        "Notes & Goals",
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
    (flow,) = _blocks(pl.character_document(saga, magus), pl.Flow)
    names = [b.name for b in flow.blocks if isinstance(b, pl.Entry)]
    assert names == ["Affinity with Creo", "Great Intelligence × 2"]


# ---------------------------------------------------------------- the Grimoire


def test_the_grimoire_gives_each_spell_in_full():
    saga, magus = _leandro()
    (spell,) = _blocks(pl.character_document(saga, magus), pl.Spell)
    assert spell.parameters.startswith("R: ")
    assert spell.casting.startswith("Casting Total ")
    found = next(s for s in saga.spells if s.id == "spell1")
    assert spell.description == found.description


def test_the_grimoire_groups_spells_under_their_form():
    saga, magus = _leandro()
    doc = pl.character_document(saga, magus)
    title = doc.blocks.index(_blocks(doc, pl.GrimoireTitle)[0])
    heading = doc.blocks[title + 1]
    assert isinstance(heading, pl.Heading)
    assert heading.symbol is not None and heading.symbol.kind == "art"


# ---------------------------------------------------------------- the copy


def _texts(doc: pl.Document) -> str:
    """Every word the document prints, in one string."""
    words = []
    for b in doc.blocks:
        for name in ("text", "name", "summary"):
            value = getattr(b, name, None)
            if isinstance(value, str):
                words.append(value)
    return "\n".join(words)


def _with_secrets():
    saga, magus = _leandro()
    magus.secrets = [
        Secret("Hidden debt", "Owes the Tremere a sigil."),
        Secret("Old name", "Was once called Marcus.", 1220, "Spring"),
    ]
    magus.private_notes = "Means to found a covenant."
    pat = Player(id="pat", name="Pat")
    saga.players.append(pat)
    magus.background.player_ids = [pat.id]
    return saga, magus, pat


def test_the_storyguide_copy_prints_every_secret():
    saga, magus, _ = _with_secrets()
    options = pl.PrintOptions(copy=pl.STORYGUIDE_COPY)
    words = _texts(pr.document(saga, "character", magus, options, STORYGUIDE_VIEWER))
    assert "Owes the Tremere a sigil." in words
    assert "Was once called Marcus." in words
    assert "Not revealed to the players" in words


def test_a_player_copy_holds_no_unrevealed_secret_or_storyguide_note():
    saga, magus, _ = _with_secrets()
    magus.secrets.append(Secret("Storyguide Notes", "His master still lives."))
    words = _texts(pr.document(saga, "character", magus, viewer=STORYGUIDE_VIEWER))
    assert "Was once called Marcus." in words
    assert "Owes the Tremere" not in words
    assert "His master still lives." not in words
    # Read as the table: no private notes either.
    assert "Means to found a covenant." not in words
    # The record itself is untouched.
    assert len(magus.secrets) == 3


def test_a_player_gets_the_player_copy_whatever_they_ask():
    saga, magus, pat = _with_secrets()
    options = pl.PrintOptions(copy=pl.STORYGUIDE_COPY)
    words = _texts(pr.document(saga, "character", magus, options, viewer_for(pat)))
    assert "Owes the Tremere" not in words
    # Their own character keeps its private parts.
    assert "Means to found a covenant." in words


# ---------------------------------------------------------------- the play sheet


def _play(saga, character) -> pl.Document:
    return pl.character_document(saga, character, pl.PrintOptions(sheet=pl.PLAY_SHEET))


def test_a_magus_play_sheet_is_two_pages_of_what_is_rolled():
    saga, magus = _leandro()
    doc = _play(saga, magus)
    headings = _headings(doc)
    for heading in ("Abilities", "Combat & Condition", "Hermetic Arts", "Spells"):
        assert heading in headings
    for left_off in ("Description & Biography", "Books", "Diary", "Secrets"):
        assert left_off not in headings
    assert not _blocks(doc, pl.GrimoireTitle)
    assert len(_blocks(doc, pl.NewPage)) == 1
    # Virtues and Flaws by name only.
    assert not _blocks(doc, pl.Entry)
    (spells,) = [t for t in _blocks(doc, pl.Table) if t.columns[0].title == "Spell"]
    assert spells.rows[0][2].text.count("/") == 2


def test_a_companion_play_sheet_has_no_magic():
    saga, character = _leandro()
    character.type = "companion"
    doc = _play(saga, character)
    assert not _blocks(doc, pl.NewPage)
    assert "Hermetic Arts" not in _headings(doc)


def test_raw_vis_keeps_lines_to_pencil_in():
    saga, magus = _leandro()
    doc = pl.character_document(saga, magus)
    at = _headings(doc).index("Raw Vis")
    assert at >= 0
    assert _blocks(doc, pl.Blanks)


def test_the_familiar_box_is_short_and_points_to_its_own_sheet():
    saga, magus = _leandro()
    saga.familiars.append(Familiar(id="fam", name="Grey", character_id=magus.id))
    doc = pl.character_document(saga, magus)
    at = doc.blocks.index(pl.Heading("Familiar"))
    (box,) = [b for b in doc.blocks[at:] if isinstance(b, pl.Facts)][:1]
    assert [label for label, _ in box.facts] == [
        "Name",
        "Species",
        "Magic Might",
        "Cords",
    ]
    assert "Grey's full sheet prints from its own page." in _texts(doc)


def test_combat_and_condition_is_kept_together():
    assert pl.keeps_with_next(pl.Heading("Combat & Condition"))
    for kept in (pl.CombatSummary("", "", "", ""), pl.Weapons(())):
        assert pl.keeps_with_next(kept)
    assert not pl.keeps_with_next(pl.Equipment((), 2))


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


def test_a_table_runs_on_at_the_foot_of_a_page():
    rows = (20.0,) * 10
    table = pl.Piece(20 + sum(rows), 0, header=20, rows=rows)
    pages = pl.paginate([pl.Piece(150), table], 300)
    parts = [p for page in pages for p in page if p.index == 1]
    # Seven rows fit under the first piece; the last three go on.
    assert [(p.first, p.last) for p in parts] == [(0, 6), (6, 10)]
    assert max(_bottoms(pages, [pl.Piece(150), table])) <= 300


def test_a_soft_new_page_breaks_only_when_little_is_left():
    soft = pl.Piece(0, new_page=True, soft=True)
    pages = pl.paginate([pl.Piece(100), soft, pl.Piece(50)], 300)
    assert [[p.index for p in page] for page in pages] == [[0, 2]]
    pages = pl.paginate([pl.Piece(250), soft, pl.Piece(20)], 300)
    assert [[p.index for p in page] for page in pages] == [[0], [2]]


def test_columns_side_by_side_each_run_on():
    left = (40.0,) * 8
    right = (40.0,) * 3
    columns = pl.Piece(320, runs=(left, right), run_keeps=((False,) * 8, (False,) * 3))
    pages = pl.paginate([pl.Piece(100), columns], 300)
    parts = [p for page in pages for p in page if p.index == 1]
    assert parts[0].spans == ((0, 5), (0, 3))
    assert parts[1].spans == ((5, 8), (3, 3))


def test_a_column_never_ends_on_a_heading():
    run = (20.0, 60.0, 20.0, 60.0)
    keeps = (True, False, True, False)
    columns = pl.Piece(160, runs=(run, ()), run_keeps=(keeps, ()))
    pages = pl.paginate([pl.Piece(200), columns], 300)
    parts = [p for page in pages for p in page if p.index == 1]
    # Room for three blocks, but the third heads the fourth: both go on.
    assert parts[0].spans[0] == (0, 2)
    assert parts[1].spans[0] == (2, 4)


def test_a_two_up_table_balances_its_columns_at_a_group():
    rows = (29.0, 16.0, 16.0, 29.0, 16.0, 16.0, 16.0)
    table = pl.Piece(0, header=15, rows=rows, two_up=True, breaks=(0, 3), cont=13)
    assert pl.balance(table, 0, len(rows)) == 3
    assert pl.two_up_height(table) == 15 + 29 + 16 * 3


def test_a_two_up_table_too_long_fills_both_columns_then_runs_on():
    rows = (16.0,) * 40
    table = pl.Piece(0, header=15, rows=rows, two_up=True, breaks=(0,), cont=13)
    table = pl.Piece(
        pl.two_up_height(table), header=15, rows=rows, two_up=True, breaks=(0,), cont=13
    )
    pages = pl.paginate([pl.Piece(100), table], 300)
    parts = [p for page in pages for p in page if p.index == 1]
    assert len(parts) == 2
    (a, b), (c, d) = parts[0].spans
    assert a == 0 and b == c and d == parts[1].spans[0][0]
    assert parts[1].spans[-1][1] == 40


def test_new_page_starts_a_page_but_never_an_empty_one():
    pieces = [
        pl.Piece(50),
        pl.Piece(0, new_page=True),
        pl.Piece(0, new_page=True),
        pl.Piece(50),
    ]
    pages = pl.paginate(pieces, 300)
    assert [[p.index for p in page] for page in pages] == [[0], [3]]
