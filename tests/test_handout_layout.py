"""A written Handout laid on its Stationery (handout_layout): the one set
of placed blocks both front-ends draw, a storyguide's Preview and a
player's copy alike."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from ars_magica_manager import handout_layout as layout
from ars_magica_manager import handout_markup as hm
from ars_magica_manager import handouts
from ars_magica_manager.forms.handouts import handout_fields, handout_form
from ars_magica_manager.handout_layout import Placed
from ars_magica_manager.markup import plain
from ars_magica_manager.models import (
    PROCLAMATION,
    SEALED_LETTER,
    STATIONERY,
    VELLUM,
    Character,
    Handout,
    HandoutPicture,
    Saga,
)
from ars_magica_manager.paths import HANDOUTS, PORTRAITS
from ars_magica_manager.picture_files import KINDS

TEXT = (
    "[heading] A Proclamation\n"
    "[centre] By order of the Count\n"
    "[initial] **Know** all men\n"
    "that the ford is closed.\n"
    "\n"
    "Plain words.\n"
    "\n"
    "[flourish]\n"
    "[picture 1]\n"
    "[right] Given at Cologne"
)


def test_each_block_is_placed_where_it_stands():
    laid = layout.lay_out("The ford", PROCLAMATION, TEXT, ["Count Konrad"])
    assert laid.title == "The ford"
    assert laid.stationery.name == PROCLAMATION
    assert laid.blocks == (
        Placed(hm.HEADING, "A Proclamation", layout.CENTRE),
        Placed(hm.CENTRED, "By order of the Count", layout.CENTRE),
        Placed(
            hm.INITIAL,
            "[b]now[/b] all men\nthat the ford is closed.",
            layout.LEFT,
            initial="K",
        ),
        Placed(hm.TEXT, "Plain words.", layout.LEFT),
        Placed(hm.FLOURISH, align=layout.CENTRE),
        Placed(hm.PICTURE, align=layout.CENTRE, picture=1, caption="Count Konrad"),
        Placed(hm.RIGHT, "Given at Cologne", layout.RIGHT),
    )


def test_a_picture_the_handout_has_not_got_stays_text():
    laid = layout.lay_out("A", VELLUM, "[picture 2]", ["Only one"])
    assert laid.blocks == (Placed(hm.TEXT, "\\[picture 2]", layout.LEFT),)


def test_an_initial_opening_on_no_letter_keeps_its_words():
    assert layout.split_initial("“Know all") == ("", "“Know all")
    assert layout.split_initial("[i]know[/i]") == ("K", "[i]now[/i]")
    assert layout.split_initial("") == ("", "")


def test_an_initial_is_one_letter_with_its_accents():
    assert layout.split_initial("ßo sei es") == ("ß", "o sei es")
    assert layout.split_initial("étoile") == ("É", "toile")
    assert layout.split_initial("ﬁrst") == ("ﬁ", "rst")


def test_every_stationery_has_its_page_and_an_unknown_one_reads_as_vellum():
    assert set(layout.STATIONERY) == set(STATIONERY)
    for paper in layout.STATIONERY.values():
        assert paper.aspect >= 1 and 0 < paper.margin < 0.25
    assert layout.stationery(SEALED_LETTER).seal
    assert layout.stationery(SEALED_LETTER).title == layout.TITLE_DOCKET
    assert layout.stationery(PROCLAMATION).edge == layout.EDGE_GILT
    assert layout.stationery("papyrus") is layout.STATIONERY[VELLUM]


def test_an_untitled_handout_is_laid_out_untitled():
    assert layout.lay_out("  ", VELLUM, "").title == "(untitled)"


def test_nothing_laid_out_names_a_file():
    laid = layout.lay_out("A", VELLUM, "[picture 1]\nC:\\x.png", ["Map"])
    assert all(":\\" not in block.caption for block in laid.blocks)
    assert laid.blocks[0].caption == "Map"


def _saga() -> Saga:
    saga = Saga(id="lay", name="Fengheld")
    saga.characters = [
        Character(id="c1", name="Agathe", type="companion", portrait="agathe.png")
    ]
    return saga


def test_a_form_s_preview_names_and_finds_each_picture(tmp_path: Path):
    portraits = KINDS[PORTRAITS].directory()
    portraits.mkdir(parents=True, exist_ok=True)
    (portraits / "agathe.png").write_bytes(b"png")
    new = tmp_path / "seal.png"
    new.write_bytes(b"png")
    refs = [
        f"{PORTRAITS}:agathe.png",
        handouts.new_picture_ref(new),
        f"{HANDOUTS}:gone.png",
    ]
    shown = handouts.preview(
        _saga(), "A letter", SEALED_LETTER, "[picture 1]\n[picture 3]", refs
    )
    assert [b.caption for b in shown.laid.blocks] == ["Agathe", "gone.png"]
    assert shown.file(1) == portraits / "agathe.png"
    assert shown.file(2) == new
    assert shown.file(3) is None
    assert shown.file(4) is None and shown.file(0) is None


def _small_handouts_folder(monkeypatch: pytest.MonkeyPatch, cap: int) -> None:
    """The handouts folder takes pictures of at most `cap` bytes."""
    monkeypatch.setitem(KINDS, HANDOUTS, replace(KINDS[HANDOUTS], cap=cap))


def test_preview_keeps_only_the_pictures_saving_would(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """A new file too big for the handouts folder, one of a kind the app
    doesn't take, and a second copy of the same bytes are left out of the
    Preview as Save leaves them out, so the numbers agree."""
    _small_handouts_folder(monkeypatch, 8)
    portraits = KINDS[PORTRAITS].directory()
    portraits.mkdir(parents=True, exist_ok=True)
    (portraits / "agathe.png").write_bytes(b"png")
    big, odd, seal, again = (
        tmp_path / n for n in ("big.png", "notes.txt", "seal.png", "again.png")
    )
    big.write_bytes(b"far too many bytes")
    odd.write_bytes(b"txt")
    seal.write_bytes(b"seal")
    again.write_bytes(b"seal")
    refs = [
        handouts.new_picture_ref(big),
        handouts.new_picture_ref(odd),
        f"{PORTRAITS}:agathe.png",
        handouts.new_picture_ref(seal),
        handouts.new_picture_ref(again),
    ]
    text = "[picture 1]\n[picture 2]\n[picture 3]"
    shown = handouts.preview(_saga(), "A", VELLUM, text, refs)
    saved = handouts.pictures_from(refs)
    assert [b.caption for b in shown.laid.blocks if b.kind == hm.PICTURE] == [
        "Agathe",
        "seal.png",
    ]
    assert len(saved) == len(shown.files) == 2
    assert shown.file(1) == portraits / "agathe.png"
    assert shown.file(2) == seal
    assert shown.laid.blocks[-1].kind == hm.TEXT  # [picture 3]: none kept


def test_preview_copies_nothing_into_the_handouts_folder(tmp_path: Path):
    new = tmp_path / "seal.png"
    new.write_bytes(b"seal")
    handouts.preview(_saga(), "A", VELLUM, "", [handouts.new_picture_ref(new)])
    assert not KINDS[HANDOUTS].directory().exists() or not any(
        KINDS[HANDOUTS].directory().iterdir()
    )


def test_a_reference_that_is_no_picture_is_never_named_by_its_path():
    assert handouts.ref_name(_saga(), "oldkind:C:\\Users\\x.png") == "(picture)"


def test_the_handout_form_previews_what_it_holds_unsaved():
    saga = _saga()
    handout = Handout("h1", title="Old", text="Old words.")
    saga.handouts = [handout]
    form = handout_form(saga, handout)
    assert form.preview is not None
    shown = form.preview(
        {"title": "New", "stationery": PROCLAMATION, "text": "[heading] New"}
    )
    assert shown.laid.title == "New"
    assert shown.laid.stationery.name == PROCLAMATION
    assert shown.laid.blocks == (Placed(hm.HEADING, "New", layout.CENTRE),)
    assert (handout.title, handout.text) == ("Old", "Old words.")


def test_the_fields_hints_show_their_tags_as_typed():
    fields = {f.key: f for f in handout_fields(_saga(), None)}
    shown = plain(fields["text"].hint)
    for tag in ("[heading]", "[centre]", "[right]", "[initial]", "[flourish]"):
        assert tag in shown
    assert "[picture 1] places the first" in plain(fields["pictures"].hint)


def test_a_saved_handout_previews_with_its_own_pictures():
    saga = _saga()
    handout = Handout(
        "h1",
        title="Seen",
        stationery=VELLUM,
        text="[picture 1]",
        pictures=[HandoutPicture(PORTRAITS, "agathe.png")],
    )
    shown = handouts.preview_of(saga, handout)
    assert shown.laid.blocks[0].caption == "Agathe"
