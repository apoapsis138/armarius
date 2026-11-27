"""Long Virtues and Flaws from The Mysteries Revised Edition (alchemy,
spirit and name magic) read like their printed page: headings set apart,
the rules' tables as tables, and the errata's wording in place (TMRE
pp. 20-88 and 116; Errata p. 50)."""

from __future__ import annotations

import json
from pathlib import Path

from ars_magica_manager import handout_markup as hm
from ars_magica_manager.markup import plain

CATALOG = Path(__file__).resolve().parent.parent / "data" / "virtue_flaw_catalog.json"


def _description(vf_id: str) -> str:
    entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    [entry] = [e for e in entries if e["id"] == vf_id]
    return str(entry["description"])


def test_vulgar_alchemy_lists_its_new_bonuses_as_a_table() -> None:
    blocks = hm.blocks(_description("vf_vulgar_alchemy"), tables=True)
    [table] = [b for b in blocks if b.kind == hm.TABLE]

    assert len(table.rows) == 31  # the header and 30 shapes and materials
    assert [plain(cell) for cell in table.rows[-1]] == [
        "Yellow sandalwood",
        "+3 binding people",
    ]


def test_vulgar_alchemy_leaves_out_the_worked_example_sidebar() -> None:
    assert "Being confident, he tries" not in _description("vf_vulgar_alchemy")


def test_names_of_power_carries_the_errata_limit_on_invocation_magic() -> None:
    # Errata p. 50, for TMRE p. 77.
    text = _description("vf_names_of_power")
    assert (
        "theurgic spellcasting and consummate talisman effects, although the "
        "combined bonus is still limited by Magic Theory."
    ) in text


def test_initiation_style_headings_stand_on_their_own_lines() -> None:
    text = _description("vf_spirit_familiar")
    assert "\n\n**The Three Cords**\n\n" in text
    assert "\n\n**Bonding the Ally as Spirit Familiar**\n\n" in text


def test_both_philosophic_alchemy_entries_share_the_book_text() -> None:
    assert _description("vf_philosophic_alchemy") == _description(
        "vf_philosophic_alchemy_major"
    )
