"""The long Virtues and Flaws from the other books (RoP, HoH:TL, AtD, App and
the rest) read like their printed pages: the book's paragraph breaks, its
lists and Initiation Scripts on lines of their own, and its tables as tables.

A paragraph the book prints whole stays whole, even when it runs over the
ratchet's cap (test_catalog_text), so those few stay on its list: the
ratchet checks which are over the cap, this file their layout."""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path

from ars_magica_manager import handout_markup as hm
from ars_magica_manager.markup import plain

CATALOG = Path(__file__).resolve().parent.parent / "data" / "virtue_flaw_catalog.json"

#: The long Virtues and Flaws taken from their own supplements' pages (RoP,
#: HoH:TL, AtD, App and the rest), by id.
BATCH = [
    "vf_blood_of_heroes",
    "vf_chthonic_magic",
    "vf_chthonic_sorginak_magic",
    "vf_daimon",
    "vf_dhampir",
    "vf_diabolist",
    "vf_ecstatic_magic",
    "vf_external_vis",
    "vf_external_vis_major",
    "vf_eyes_of_theseus",
    "vf_faerie_background",
    "vf_faerie_sight",
    "vf_faerie_speech",
    "vf_the_false_gift",
    "vf_fector",
    "vf_figurine_magic",
    "vf_foe_art",
    "vf_folk_dancer",
    "vf_gild_trained",
    "vf_greater_infernal_power",
    "vf_herbalism",
    "vf_hermetic_inclination_in_form",
    "vf_immune_to_source",
    "vf_immune_to_source_major",
    "vf_infernal_blessing",
    "vf_infernal_blessing_major",
    "vf_inherited_virtue",
    "vf_inherited_virtue_major",
    "vf_invasive_eyes",
    "vf_invisible_to_magic",
    "vf_l_an_l_ith",
    "vf_leadworker",
    "vf_lesser_infernal_power",
    "vf_maestro",
    "vf_magical_champion",
    "vf_magical_master",
    "vf_mythic_blood_zmey",
    "vf_mythic_characteristic",
    "vf_patron_angel",
    "vf_r_astradh",
    "vf_samovily_blood",
    "vf_summoner",
    "vf_thief_of_emotions",
    "vf_transformed_being",
    "vf_zahid",
    "vf_perfectus_mythic",
    "vf_corrupted_beast",
    "vf_greater_charm",
    "vf_heroic_personality",
    "vf_homunculus_wizard",
    "vf_inherited_flaw",
    "vf_inherited_flaw_major",
    "vf_karaite_magic",
    "vf_lesser_charm",
    "vf_magical_friend",
    "vf_traditional_ward",
    "vf_tragic_characteristic",
    "vf_focus_power_quality",
    "vf_gigantic",
    "vf_greater_power_quality",
    "vf_improved_powers_quality",
    "vf_lesser_power_quality",
    "vf_personal_power_quality",
    "vf_ritual_power_quality",
    "vf_miniature",
    "vf_temporary_might",
    "vf_elysian_ecstasy",
    "vf_jinni",
    "vf_mythic_farrier",
    "vf_true_understanding_of_the_realms",
]


@cache
def _by_id() -> dict[str, dict[str, object]]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in data["entries"]}


def _text(entry_id: str) -> str:
    return str(_by_id()[entry_id]["description"])


def _tables(entry_id: str) -> list[hm.Block]:
    blocks = hm.blocks(_text(entry_id), tables=True)
    return [block for block in blocks if block.kind == hm.TABLE]


def test_the_batch_is_all_there() -> None:
    entries = _by_id()
    assert len(set(BATCH)) == len(BATCH) == 70
    assert [i for i in BATCH if i not in entries] == []


def test_a_dash_is_a_dash_not_two_hyphens() -> None:
    double_hyphen = re.compile(r"^(?!\s*\|).*(?<!-)--(?!-)", re.MULTILINE)
    assert [i for i in BATCH if double_hyphen.search(_text(i))] == []


def test_size_charts_are_tables() -> None:
    [gigantic] = _tables("vf_gigantic")
    [miniature] = _tables("vf_miniature")

    assert [plain(c) for c in gigantic.rows[0]] == [
        "Size",
        "Size Increase",
        "Strength Bonus",
        "Quickness Penalty",
    ]
    assert [plain(c) for c in gigantic.rows[1]] == ["-11 or less", "+5", "+10", "-5"]
    assert [plain(c) for c in miniature.rows[5]] == ["+3 or more", "-1", "-2", "+1"]


def test_figurine_magic_has_its_ease_factor_table() -> None:
    [table] = _tables("vf_figurine_magic")

    assert [plain(c) for c in table.rows[-1]] == ["Hermetic Spell", "+1/magnitude"]


def test_elysian_ecstasy_has_its_channeling_table_and_initiation_script() -> None:
    [table] = _tables("vf_elysian_ecstasy")
    text = _text("vf_elysian_ecstasy")

    assert [plain(row[0]) for row in table.rows] == [
        "Ease Factor",
        "9",
        "12",
        "15",
        "18",
        "21+",
    ]
    assert "**Initiation of Elysian Ecstasy**\n\n**Ease Factor:** 18\n" in text


def test_lists_are_one_item_to_a_line() -> None:
    assert (
        "\n- True Faith, Major General\n- Meditation, Major Supernatural (Method)\n"
        in (_text("vf_zahid"))
    )
    assert "\n- *Quickness:* often surprised, lumbering run, easy target" in (
        _text("vf_tragic_characteristic")
    )
    assert "\n- **Infernal Protection (Incantation, Diablerie, Level 40):**" in (
        _text("vf_infernal_blessing")
    )
