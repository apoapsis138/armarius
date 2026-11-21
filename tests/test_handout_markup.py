"""A written Handout's text: the app's markup plus six handout tags, each
starting a line, read into blocks both front-ends draw. Nothing else is a
tag: any other bracket comes out as text, and nothing names a file or an
address (ADR 0021)."""

from __future__ import annotations

from ars_magica_manager import handout_markup as hm
from ars_magica_manager.handout_markup import Block


def test_plain_text_is_paragraphs_with_the_app_s_emphasis():
    assert hm.blocks("Know all men **by these** presents.\nIt is so.\n\nNext.") == [
        Block(hm.TEXT, "Know all men [b]by these[/b] presents.\nIt is so."),
        Block(hm.TEXT, "Next."),
    ]


def test_each_of_the_six_tags_gives_its_block():
    text = (
        "[heading] A Proclamation\n"
        "[centre] By order of the Count\n"
        "[right] Given at Cologne\n"
        "[initial] Know all men\n"
        "that the ford is closed.\n"
        "\n"
        "[flourish]\n"
        "[picture 2]"
    )
    assert hm.blocks(text, pictures=2) == [
        Block(hm.HEADING, "A Proclamation"),
        Block(hm.CENTRED, "By order of the Count"),
        Block(hm.RIGHT, "Given at Cologne"),
        Block(hm.INITIAL, "Know all men\nthat the ford is closed."),
        Block(hm.FLOURISH),
        Block(hm.PICTURE, picture=2),
    ]


def test_tags_read_in_any_case_and_center_as_centre():
    assert hm.blocks("[Center] x\n[HEADING] y") == [
        Block(hm.CENTRED, "x"),
        Block(hm.HEADING, "y"),
    ]


def test_anything_else_in_brackets_is_text():
    """An unknown tag, a tag with nothing after it, a tag mid-line, a
    picture the Handout hasn't got, and markup that would name a file or
    an address all come out as plain, escaped text."""
    for line in (
        "[shout] Hear ye",
        "[heading]",
        "Hear [heading] ye",
        "[picture 3]",
        "[picture 0]",
        "[picture two]",
        "[flourish] and more",
        "[link=file:///C:/secret.txt]x[/link]",
        "[img https://example.com/x.png]",
    ):
        (block,) = hm.blocks(line, pictures=2)
        assert block.kind == hm.TEXT, line
        assert block.text == line.replace("[", "\\["), line


def test_nothing_a_block_holds_is_a_path_or_address():
    """A picture is only ever a number among the Handout's own pictures."""
    (block,) = hm.blocks("[picture 1]", pictures=1)
    assert block == Block(hm.PICTURE, picture=1)
    assert block.text == ""


def test_the_tags_are_exactly_six():
    assert set(hm.TAGS.values()) | {hm.PICTURE} == {
        hm.HEADING,
        hm.CENTRED,
        hm.RIGHT,
        hm.INITIAL,
        hm.FLOURISH,
        hm.PICTURE,
    }


def test_plain_gives_the_text_without_its_tags():
    """What the terminal and a list row show."""
    text = "[heading] A Proclamation\n[flourish]\n[picture 1]\nKnow **all** men."
    assert hm.plain(text, pictures=1) == "A Proclamation\n\n(picture 1)\nKnow all men."
