import pytest

from ars_magica_manager import books as bk
from ars_magica_manager.models import (
    Book,
    Character,
    Covenant,
    Laboratory,
    Saga,
    Spell,
)


def _book(book_type: str, **kwargs) -> Book:
    return Book(id="b", name="A Book", type=book_type, **kwargs)


@pytest.mark.parametrize(
    ("book", "expected"),
    [
        (_book("Art Summa", art="Creo", level=12, quality=10), 22),
        (_book("Ability Summa", ability="Latin", level=5, quality=9), 24),
        (_book("Tractatus", subject_kind="Art", art="Ignem", quality=8), 8),
        (_book("Lab Text", spell_name="Pilum of Fire", level=20), 4),
        # Fractions round up: 12 levels is 2.4 -> 3 (Lab Text), 4.8 -> 5 (Tablet).
        (_book("Lab Text", spell_name="x", level=12), 3),
        (_book("Casting Tablet", spell_name="x", level=12), 5),
        (_book("Casting Tablet", spell_name="x", level=25), 10),
        (_book("Other"), 0),
        (_book("Art Summa", art="Creo"), 0),  # blank level/quality count as 0
    ],
)
def test_cost(book, expected):
    assert bk.cost(book) == expected


def test_art_summa_limits():
    # Level 15: quality up to 11 + 5 = 16.
    assert bk.limit_warnings(_book("Art Summa", level=15, quality=16)) == []
    assert bk.limit_warnings(_book("Art Summa", level=15, quality=17)) == [
        "Quality 17 is over the covenant-creation limit of 16."
    ]
    # Low levels are capped at 22, not 11 + (20 - level).
    assert bk.limit_warnings(_book("Art Summa", level=5, quality=22)) == []
    assert len(bk.limit_warnings(_book("Art Summa", level=5, quality=23))) == 1
    assert bk.limit_warnings(_book("Art Summa", level=21, quality=5)) == [
        "Level 21 is over the covenant-creation limit of 20.",
    ]


def test_ability_summa_limits():
    # Level 5: quality up to 11 + 3 x 3 = 20.
    assert bk.limit_warnings(_book("Ability Summa", level=5, quality=20)) == []
    assert bk.limit_warnings(_book("Ability Summa", level=5, quality=21)) == [
        "Quality 21 is over the covenant-creation limit of 20."
    ]
    assert bk.limit_warnings(_book("Ability Summa", level=8, quality=11)) == []
    assert bk.limit_warnings(_book("Ability Summa", level=9, quality=1)) == [
        "Level 9 is over the covenant-creation limit of 8."
    ]
    assert bk.limit_warnings(_book("Ability Summa", level=1, quality=22)) == []


def test_tractatus_and_unchecked_limits():
    assert bk.limit_warnings(_book("Tractatus", quality=11)) == []
    assert len(bk.limit_warnings(_book("Tractatus", quality=12))) == 1
    assert bk.limit_warnings(_book("Lab Text", level=100)) == []
    assert bk.limit_warnings(_book("Other")) == []


def _saga() -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[
            Covenant(id="cov1", saga_id="s", name="Fengheld"),
            Covenant(id="cov2", saga_id="s", name="Other"),
        ],
        laboratories=[Laboratory(id="lab1", covenant_id="cov1", name="Tower")],
        characters=[
            Character(id="ch1", name="Leandro", type="magus", covenant_id="cov1"),
            Character(id="ch2", name="Nomad", type="magus"),
        ],
        books=[
            Book(
                id="b1",
                name="One",
                type="Other",
                owner_kind="covenant",
                owner_id="cov1",
            ),
            Book(
                id="b2",
                name="Two",
                type="Other",
                owner_kind="laboratory",
                owner_id="lab1",
            ),
            Book(
                id="b3",
                name="Three",
                type="Other",
                owner_kind="character",
                owner_id="ch1",
            ),
            Book(
                id="b4",
                name="Four",
                type="Other",
                owner_kind="covenant",
                owner_id="cov2",
            ),
            Book(id="b5", name="Five", type="Other"),
            Book(
                id="b6",
                name="Six",
                type="Other",
                owner_kind="laboratory",
                owner_id="gone",
            ),
            Book(
                id="b7",
                name="Seven",
                type="Other",
                owner_kind="character",
                owner_id="ch2",
            ),
        ],
    )


def test_books_in_covenant_includes_labs_and_characters():
    saga = _saga()
    ids = [b.id for b in bk.books_in_covenant(saga, saga.covenants[0])]
    assert ids == ["b1", "b2", "b3"]


def test_unassigned_books_include_missing_owners_only():
    # b7 belongs to a character with no covenant: owned, so not unassigned.
    assert [b.id for b in bk.unassigned_books(_saga())] == ["b5", "b6"]


def test_location_and_owner_labels():
    saga = _saga()
    by_id = {b.id: b for b in saga.books}
    assert bk.location_label(saga, by_id["b1"]) == "Covenant Library"
    assert bk.location_label(saga, by_id["b2"]) == "Lab: Tower"
    assert bk.location_label(saga, by_id["b3"]) == "Leandro"
    assert bk.location_label(saga, by_id["b5"]) == "Unassigned"
    assert bk.owner_label(saga, by_id["b2"]) == "Laboratory: Tower"
    assert bk.owner_label(saga, by_id["b6"]) == "(none - unassigned)"


def test_detail_text_field_order_and_warning():
    saga = _saga()
    book = Book(
        id="x",
        name="Summa [of] Fire",
        type="Art Summa",
        art="Ignem",
        level=15,
        quality=17,
        author="Pralix",
        owner_kind="covenant",
        owner_id="cov1",
        description="**Rare**",
    )
    # In play the Build Point cost and creation limits aren't shown
    # (STORY-1314): they matter only while the covenant is In Creation.
    in_play = bk.detail_text(saga, book)
    assert "Cost:" not in in_play and "covenant-creation limit" not in in_play
    saga.covenant("cov1").in_creation = True
    text = bk.detail_text(saga, book)
    # Name; then two columns (Type..Quality | Language..Owner); then Cost.
    rows = [
        ["Name:"],
        ["Type:", "Language:"],
        ["Art:", "Author:"],
        ["Level:", "Year Published:"],
        ["Quality:", "Owner:"],
        ["Cost:"],
    ]
    lines = text.split("\n")
    for line, labels in zip(lines, rows, strict=False):
        positions = [line.index(f"[b]{label}[/]") for label in labels]
        assert positions == sorted(positions)
    # The right-hand column starts at the same place on every row.
    plain = [line.replace("[b]", "").replace("[/]", "") for line in lines[1:5]]
    right = ["Language:", "Author:", "Year Published:", "Owner:"]
    assert len({line.index(label) for line, label in zip(plain, right)}) == 1
    assert "32 Build Points (Level 15 + Quality 17)" in text
    assert (
        "[$text-error]Quality 17 is over the covenant-creation limit of 16.[/]" in text
    )
    assert r"Summa \[of] Fire" in text  # user text is escaped
    assert (
        text.index("Cost:") < text.index("[$text-error]") < text.index("Description:")
    )


def test_row_label_columns_line_up_with_header():
    saga = _saga()
    header = bk.table_header()
    row = bk.row_label(
        saga,
        Book(
            id="x",
            name="On Fire",
            type="Art Summa",
            art="Ignem",
            level=12,
            quality=10,
            owner_kind="covenant",
            owner_id="cov1",
        ),
    )
    # The header carries the list's two-character selector indent.
    assert header.index("Location") - 2 == row.index("Covenant Library")
    assert header.index("Type") - 2 == row.index("Art Summa")
    assert "   12      10  " in row
    blank = bk.row_label(saga, Book(id="y", name="Misc", type="Other"))
    assert "    -       -  Unassigned" in blank


def test_old_book_and_library_records_are_upgraded():
    saga = Saga.from_dict(
        {
            "id": "s",
            "name": "S",
            "covenants": [
                {"id": "cov1", "saga_id": "s", "name": "C", "library_id": "lib1"}
            ],
            "libraries": [{"id": "lib1", "covenant_id": "cov1", "books": ["b1", "b2"]}],
            "books": [
                {
                    "id": "b1",
                    "type": "Summa",
                    "subject": "Creo",
                    "quality": 6,
                    "level": 8,
                },
                {
                    "id": "b2",
                    "type": "Lab Text",
                    "subject": "Ignem",
                    "quality": 9,
                    "spell_id": "sp1",
                },
                {
                    "id": "b3",
                    "type": "Tractatus",
                    "subject": "Magic Theory",
                    "quality": 7,
                    "notes": "Old",
                },
            ],
            "spells": [
                {
                    "id": "sp1",
                    "name": "Pilum of Fire",
                    "technique": "Creo",
                    "form": "Ignem",
                    "level": 20,
                }
            ],
        }
    )
    b1, b2, b3 = saga.books
    assert (b1.type, b1.art, b1.name, b1.owner_kind, b1.owner_id) == (
        "Art Summa",
        "Creo",
        "Creo",
        "covenant",
        "cov1",
    )
    assert (b2.type, b2.spell_name, b2.owner_id) == (
        "Lab Text",
        "Pilum of Fire",
        "cov1",
    )
    assert (b3.subject_kind, b3.ability, b3.description, b3.owner_kind) == (
        "Ability",
        "Magic Theory",
        "Old",
        None,
    )
    assert not hasattr(saga, "libraries")
    assert saga.spells == [
        Spell(id="sp1", name="Pilum of Fire", technique="Creo", form="Ignem", level=20)
    ]


_CSV_HEADER = (
    "name,type,language,author,owner,year_published,description,cost,"
    "art,ability,level,quality,tractatus_type,spell\n"
)


def test_parse_books_csv_reads_every_type():
    text = _CSV_HEADER + (
        'On Flame,Art Summae,Latin,Ignatia,,1174,"Fiery, passionate.",27,Ignem,,15,12,,\n'
        "Theorica,Ability Summae,Latin,Didacus,Covenant,1179,Standard.,26,,Magic Theory,5,11,,\n"
        "A Letter,Tractatus,Latin,,,,,8,ig,,,8,Art,\n"
        "Notes,tractatus,Latin,,,,,11,,Penetration,,11,,\n"
        "Pilum,Lab Text,Latin,,,,,4,,,20,,,Pilum of Fire\n"
        "Porter,Casting Tablet,,,,,,4,,,10,,,The Unseen Porter\n"
        "Chronicle,Other,Old French,Various,Covenant,1165,Records.,0,,,,,,\n"
        "\n"
    )
    result = bk.parse_books_csv(text)
    assert result.skipped == []
    assert result.unused_columns == ["owner", "cost"]
    flame, theorica, letter, notes, pilum, porter, chronicle = result.books
    assert (flame.type, flame.art, flame.level, flame.quality) == (
        "Art Summa",
        "Ignem",
        15,
        12,
    )
    assert (flame.year_published, flame.description) == (1174, "Fiery, passionate.")
    assert (theorica.type, theorica.ability) == ("Ability Summa", "Magic Theory")
    assert (letter.subject_kind, letter.art) == ("Art", "Ignem")  # abbreviation
    assert (notes.subject_kind, notes.ability) == ("Ability", "Penetration")  # inferred
    assert (pilum.spell_name, pilum.level, bk.cost(pilum)) == ("Pilum of Fire", 20, 4)
    assert (porter.language, bk.cost(porter)) == ("Latin", 4)  # blank -> Latin
    assert (chronicle.type, chronicle.language) == ("Other", "Old French")
    # No owner or id yet: the import decides.
    assert all(b.owner_kind is None and b.id == "" for b in result.books)


def test_parse_books_csv_skips_bad_rows_with_reasons():
    text = _CSV_HEADER + (
        ",Other,,,,,,,,,,,,\n"
        "Odd,Scroll,,,,,,,,,,,,\n"
        "Nope,Art Summa,,,,,,,Fire,,5,5,,\n"
        "Vague,Tractatus,,,,,,,,,,5,,\n"
        "Bad Level,Ability Summa,,,,,,,,Latin,five,5,,\n"
        "No Spell,Lab Text,,,,,,,,,10,,,\n"
        "Fine,Other,,,,,,,,,,,,\n"
    )
    result = bk.parse_books_csv(text)
    assert [b.name for b in result.books] == ["Fine"]
    assert result.skipped == [
        "Row 2: no name.",
        "Row 3 (Odd): unknown type 'Scroll'.",
        "Row 4 (Nope): unknown Art 'Fire'.",
        "Row 5 (Vague): a Tractatus needs a tractatus_type of Art or Ability.",
        "Row 6 (Bad Level): Level 'five' isn't a whole number.",
        "Row 7 (No Spell): no spell.",
    ]


def test_parse_books_csv_needs_name_and_type_columns():
    with pytest.raises(ValueError, match="no type column"):
        bk.parse_books_csv("Name,Author\nX,Y\n")
    # Headers are matched in any case, and other columns are reported.
    result = bk.parse_books_csv("NAME, Type ,Shelf\nX,Other,3\n")
    assert [b.name for b in result.books] == ["X"]
    assert result.unused_columns == ["shelf"]


def test_read_books_csv_handles_excel_encodings(tmp_path):
    utf8 = tmp_path / "bom.csv"
    utf8.write_bytes("\ufeffname,type\nKitāb,Other\n".encode())
    assert [b.name for b in bk.read_books_csv(utf8).books] == ["Kitāb"]
    legacy = tmp_path / "legacy.csv"
    legacy.write_bytes("name,type\nLivre d'Heures é,Other\n".encode("cp1252"))
    assert [b.name for b in bk.read_books_csv(legacy).books] == ["Livre d'Heures é"]


def test_import_preview_mentions_what_matters():
    text = _CSV_HEADER + (
        "Big,Art Summa,,,,,,,Ignem,,15,17,,\n"
        "Again,Other,,,,,,,,,,,,\n"
        + "".join(f"Bad {i},Scroll,,,,,,,,,,,,\n" for i in range(7))
    )
    result = bk.parse_books_csv(text)
    preview = bk.import_preview(result, "books.csv", "as unassigned books", {"Again"})
    assert preview.startswith(
        "Import 2 books from [b]books.csv[/] as unassigned books?"
    )
    assert "the owner and cost columns" in preview
    assert "1 has the same name as another book; you'll be asked" in preview
    assert "1 goes over covenant-creation limits" in preview
    assert "7 row(s) will be skipped" in preview
    assert "...and 2 more." in preview


def test_canonical_ability_matches_the_catalog_in_any_case():
    assert bk.canonical_ability("magic theory") == "Magic Theory"
    assert bk.canonical_ability("area lore: Rhine") == "Area Lore: Rhine"
    assert bk.canonical_ability("Area Lore:") is None  # the blank must be filled
    assert bk.canonical_ability("Latin") is None  # only "Dead/Living Language: ..."


def test_an_unknown_ability_is_flagged_red_with_a_status():
    saga = _saga()
    known = _book("Ability Summa", ability="Magic Theory", level=1, quality=1)
    unknown = _book("Tractatus", subject_kind="Ability", ability="Latin", quality=5)
    assert bk.status_problems(known) == []
    assert bk.status_problems(unknown) == [
        "Unknown ability: 'Latin' isn't in the ability list; edit the book to "
        "choose one."
    ]
    # An Art book never has an ability problem, whatever `ability` holds.
    assert bk.status_problems(_book("Art Summa", art="Vim", ability="Latin")) == []
    assert not bk.row_label(saga, known).startswith("[$text-error]")
    assert bk.row_label(saga, unknown).startswith("[$text-error]")
    first_line = bk.detail_text(saga, unknown).split("\n")[0]
    assert first_line.startswith("[$text-error][b]Unknown ability:")


def test_import_keeps_an_unknown_ability_and_fixes_the_case_of_known_ones():
    result = bk.parse_books_csv(
        "name,type,ability,level,quality\n"
        "A,Ability Summa,magic theory,1,1\n"
        "B,Ability Summa,Latin,1,1\n"
    )
    assert [b.ability for b in result.books] == ["Magic Theory", "Latin"]
    preview = bk.import_preview(result, "x.csv", "as unassigned books", set())
    assert "1 names an unknown ability" in preview


def test_duplicate_names_counts_the_saga_and_the_file_itself():
    books = [_book("Other"), _book("Other"), Book(id="", name="New", type="Other")]
    # "A Book" twice in the file: the second is the duplicate.
    assert bk.duplicate_names(books, set()) == [books[1]]
    assert bk.duplicate_names(books, {"A Book", "New"}) == books


def test_summary_counts_books_by_kind():
    books = [
        _book("Art Summa", art="Creo", level=10, quality=5),  # 15
        _book("Art Summa", art="Vim", level=2, quality=3),  # 5
        _book("Ability Summa", ability="Latin", level=1, quality=4),  # 7
        _book("Tractatus", subject_kind="Art", art="Ignem", quality=6),  # 6
        _book("Tractatus", subject_kind="Ability", ability="Magic Theory", quality=8),
        _book("Tractatus", subject_kind="Ability", ability="Latin", quality=2),
        _book("Lab Text", spell_name="x", level=12),  # 3
        _book("Casting Tablet", spell_name="y", level=12),  # 5
        _book("Other"),
    ]
    left, right = bk.summary_texts(books)
    plain = [line.replace("[b]", "").replace("[/]", "") for line in left.split("\n")]
    assert [" ".join(line.split()) for line in plain] == [
        "Summae: 3",
        "• Ability: 1",
        "• Art: 2",
        "",
        "Tractatus: 3",
        "• Ability: 2",
        "• Art: 1",
    ]
    plain = [line.replace("[b]", "").replace("[/]", "") for line in right.split("\n")]
    assert [" ".join(line.split()) for line in plain] == [
        "Lab Texts: 1",
        "Casting Tablets: 1",
        "Other: 1",
        "",
        "Total Books: 9",
    ]
    # Values line up in one column.
    assert len({line.index("1") for line in right.split("\n")[:3]}) == 1


def test_subject_width_uses_the_spare_room_within_limits():
    assert bk.subject_width(10) == bk.SUBJECT_MIN_WIDTH
    assert bk.subject_width(1000) == bk.SUBJECT_MAX_WIDTH
    wide = bk.subject_width(100)
    assert bk.SUBJECT_MIN_WIDTH < wide < bk.SUBJECT_MAX_WIDTH
    saga = _saga()
    book = Book(id="x", name="N", type="Other", owner_kind="covenant", owner_id="cov1")
    header, row = bk.table_header(wide), bk.row_label(saga, book, wide)
    assert header.index("Location") - 2 == row.index("Covenant Library")
    assert "Subject" in header


def test_lab_texts_link_to_spells_by_id_or_typed_name():
    saga = _saga()
    by_id = _book("Lab Text", spell_id="spell_pilum_of_fire", spell_name="whatever")
    by_name = _book("Casting Tablet", spell_name="wizard\u2019s sidestep", level=15)
    unknown = _book("Lab Text", spell_name="The Lost Art", level=10)
    assert bk.book_spell(saga, by_id).name == "Pilum of Fire"
    assert bk.book_spell(saga, by_name).id == "spell_wizard_s_sidestep"
    assert bk.book_spell(saga, unknown) is None
    assert bk.book_spell(saga, _book("Art Summa", art="Ignem")) is None


def test_a_linked_books_level_and_cost_come_from_its_spell():
    saga = _saga()
    # Stench of the Twenty Corpses is level 10; the typed 15 doesn't count.
    tablet = _book(
        "Casting Tablet", spell_name="Stench of the Twenty Corpses", level=15
    )
    assert bk.level_of(tablet, saga) == 10
    assert bk.cost(tablet, saga) == 4  # 2 per 5 levels
    assert bk.cost(tablet) == 6  # without the saga, only the stored level
    # A General spell (the Aegis) keeps the book's own level.
    aegis = _book("Lab Text", spell_id="spell_aegis_of_the_hearth", level=30)
    assert bk.level_of(aegis, saga) == 30 and bk.cost(aegis, saga) == 6
    text = bk.detail_text(saga, aegis)
    assert "Aegis of the Hearth (ReVi Gen)" in text
    assert "30 (General spell)" in text
    assert "10 (the spell's)" in bk.detail_text(saga, tablet)
    row = bk.row_label(saga, tablet)
    assert "Stench of the Tw" in row and "   10 " in row  # the column is 17 wide


def test_a_book_whose_spell_cant_be_found_is_flagged():
    saga = _saga()
    lost = _book("Lab Text", spell_name="The Lost Art", level=10)
    assert bk.status_problems(lost, saga) == [
        "Unknown spell: 'The Lost Art' isn't in the spell list; edit the book to "
        "choose one."
    ]
    assert bk.row_label(saga, lost).startswith("[$text-error]")
    assert bk.level_of(lost, saga) == 10  # its typed level is kept
    assert bk.status_problems(lost) == []  # without the saga, no lookup
    linked = _book("Lab Text", spell_id="spell_pilum_of_fire")
    assert bk.status_problems(linked, saga) == []


def test_add_book_gives_it_a_unique_id_and_no_owner():
    saga = _saga()
    first = bk.add_book(saga, "Summa of Flame", "Art Summa")
    second = bk.add_book(saga, "Summa of Flame", "Art Summa")
    assert (first.id, second.id) == ("summa_of_flame", "summa_of_flame_2")
    assert saga.books[-2:] == [first, second]
    assert (second.owner_kind, second.owner_id) == (None, None)


def test_add_imported_books_links_spells_and_files_them_under_the_covenant():
    saga = _saga()
    spell = Spell(id="own1", name="Lamp of Tobias", technique="Creo", form="Ignem")
    saga.spells.append(spell)
    lab_text = Book(id="", name="Notes", type="Lab Text", spell_name="Lamp of Tobias")
    loose = Book(id="", name="Notes", type="Other")
    bk.add_imported_books(saga, [lab_text, loose], saga.covenants[0])
    assert (lab_text.id, loose.id) == ("notes", "notes_2")
    assert (lab_text.spell_id, loose.spell_id) == ("own1", None)
    assert all(
        b.owner_kind == "covenant" and b.owner_id == "cov1" for b in (lab_text, loose)
    )
    assert saga.books[-2:] == [lab_text, loose]

    unassigned = Book(id="", name="Stray", type="Other")
    bk.add_imported_books(saga, [unassigned], None)
    assert unassigned.owner_id is None


def test_form_problem():
    assert bk.form_problem({"type": "Lab Text"}).startswith("Choose the spell")
    assert bk.form_problem({"type": "Lab Text", "spell_id": "x"}) is None
    assert bk.form_problem({"ability": "Area Lore: {region}"}) == (
        "Area Lore: {region} needs its Ability detail filled in."
    )
    assert bk.form_problem({"level": -1}) == "Level can't be negative."
    assert bk.form_problem({"quality": None, "level": None}) is None


def test_duplicate_names_can_compare_by_a_key():
    books = [
        Book(id="1", name="a book", type="Other"),
        Book(id="2", name="A BOOK", type="Other"),
    ]
    assert bk.duplicate_names(books, {"A Book"}) == []
    assert bk.duplicate_names(books, {"A Book"}, str.lower) == books


def test_imported_lab_texts_link_to_their_spells_and_keep_a_lost_ones_level():
    saga = _saga()
    parsed = bk.parse_books_csv(
        "name,type,level,spell\n"
        "Pilum notes,Lab Text,,pilum of fire\n"
        "Mystery notes,Lab Text,15,The Lost Art\n"
    )
    assert not parsed.skipped  # a Lab Text's level may be left blank
    bk.add_imported_books(saga, parsed.books, saga.covenants[0])
    pilum, mystery = parsed.books
    assert pilum.spell_id == "spell_pilum_of_fire"  # a typed name, any case
    assert (mystery.spell_id, mystery.level) == (None, 15)
    assert bk.row_label(saga, mystery).startswith("[$text-error]")
