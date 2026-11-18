"""The character rule for words typed into the Chronicle (shapes.py):
letters of any language, digits, punctuation, maths signs, spaces and line
breaks; never emoji, control characters or invisible ones."""

from __future__ import annotations

from ars_magica_manager import shapes

ZERO_WIDTH_JOINER = chr(0x200D)
ZERO_WIDTH_SPACE = chr(0x200B)
RIGHT_TO_LEFT_OVERRIDE = chr(0x202E)
LEFT_TO_RIGHT_ISOLATE = chr(0x2066)
VARIATION_SELECTOR = chr(0xFE0F)
KEYCAP = chr(0x20E3)
SKIN_TONE = chr(0x1F3FD)
GRINNING_FACE = chr(0x1F600)
HEART = chr(0x2764)
LINE_SEPARATOR = chr(0x2028)
NO_BREAK_SPACE = chr(0xA0)
COMBINING_ACUTE = chr(0x301)


def test_an_emoji_is_refused_and_named():
    problem = shapes.why_not_words(f"Meet at the mill {GRINNING_FACE}")
    assert problem is not None
    assert "Emoji" in problem


def test_invisible_characters_are_refused_and_shown_by_code():
    for char in (
        ZERO_WIDTH_JOINER,
        ZERO_WIDTH_SPACE,
        RIGHT_TO_LEFT_OVERRIDE,
        LEFT_TO_RIGHT_ISOLATE,
    ):
        problem = shapes.why_not_words(f"Brother{char}Anselm")
        assert problem is not None and "Invisible" in problem
        assert f"U+{ord(char):04X}" in problem


def test_an_emoji_variation_selector_or_skin_tone_is_refused():
    for text in (
        f"{HEART}{VARIATION_SELECTOR}",
        f"thumbs{SKIN_TONE}",
        f"1{VARIATION_SELECTOR}{KEYCAP}",
    ):
        problem = shapes.why_not_words(text)
        assert problem is not None and "Emoji" in problem


def test_control_characters_are_refused_but_a_line_break_is_kept():
    assert shapes.why_not_words("first line\nsecond line") is None
    for char in ("\t", "\r", "\x07", LINE_SEPARATOR):
        problem = shapes.why_not_words(f"a{char}b")
        assert problem is not None and "Control" in problem


def test_letters_of_any_language_and_maths_signs_are_kept():
    for text in (
        "Rúastradh",
        "Ἀπολλώνιος",
        "صلاح الدين",
        "Müller, Ærøskøbing; Þr!",
        "+3 = 12, 5 < 7 (×2) €10 £3",
        f"a{NO_BREAK_SPACE}non-breaking space",
        f"e{COMBINING_ACUTE} with its accent apart",
    ):
        assert shapes.why_not_words(text) is None, text
