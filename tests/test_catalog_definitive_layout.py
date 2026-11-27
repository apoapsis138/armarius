"""Definitive Edition Virtues and Flaws laid out as the printed page has
them: their tables read as tables, and their lists as lists."""

from __future__ import annotations

from functools import cache

from ars_magica_manager import catalog, handout_markup


@cache
def _description(entry_id: str) -> str:
    return catalog.load_virtue_flaw_catalog_by_id()[entry_id].description


def _table(entry_id: str) -> list[tuple[str, ...]]:
    found = handout_markup.blocks(_description(entry_id), tables=True)
    [table] = [block for block in found if block.kind == handout_markup.TABLE]
    return [tuple(row) for row in table.rows]


def test_study_bonus_examples_read_as_a_table():
    """ArM5 Definitive Edition p. 110: the minimum presence by Art score."""
    rows = _table("vf_study_bonus")

    assert rows[0] == ("Art Score", "Minimum Presence of Art")
    assert [row[0] for row in rows[1:]] == [str(n) for n in range(0, 40, 5)]
    assert rows[1][1].startswith("A candle flame (Ignem)")


def test_monstrosity_examples_read_as_a_table():
    """ArM5 Definitive Edition p. 131: a monstrous feature for each Form."""
    rows = _table("vf_form_monstrosity")

    assert rows[0] == ("Form", "Monstrosity")
    assert [row[0] for row in rows[1:]] == [
        "Animal",
        "Aquam",
        "Auram",
        "Corpus",
        "Herbam",
        "Ignem",
        "Imaginem",
        "Mentem",
        "Terram",
        "Vim",
    ]


def test_warped_senses_temperatures_are_a_list_from_hot_to_cold():
    """ArM5 Definitive Edition p. 152: the Environmental Temperatures sidebar,
    printed as a list."""
    _, chart = _description("vf_warped_senses").split("**Environmental Temperatures**")
    lines = chart.strip().splitlines()

    assert all(line.startswith("- ") for line in lines)
    items = [line.removeprefix("- ") for line in lines]
    assert (items[0], items[-1], len(items)) == (
        "Unnaturally hot",
        "Unnaturally cold",
        8,
    )


def test_withstand_casting_sets_its_examples_apart():
    """ArM5 Definitive Edition p. 116: two worked examples within the entry."""
    paragraphs = _description("vf_withstand_casting").split("\n\n")

    assert sum(p.startswith("**Example:** ") for p in paragraphs) == 2


def test_sufi_chooses_a_story_flaw_such_as_mentor():
    """ArM5 Definitive Edition p. 111: the Sufi chooses a Minor Story Flaw,
    such as Mentor; it is not Mentor automatically."""
    text = _description("vf_sufi")

    assert "you should choose an appropriate Minor Story Flaw, such as Mentor" in text
    assert "automatically" not in text
