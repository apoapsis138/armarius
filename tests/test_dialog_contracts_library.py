"""Dialog contract tests for the forms of books and lab texts.

Each form runs in one app session; dialog_contract_support.py has the
contract and the driver, dialog_openers.py how each form is reached."""

import pytest
from dialog_contract_support import Contract, character, laboratory, run_contract
from textual.widgets import Select

from ars_magica_manager.models import LabTextAccess

CONTRACTS: dict[str, Contract] = {
    "edit book": Contract(
        prefill={"Name": "Summa", "Type": "Art Summa", "Owner": "covenant:cov1"},
        edits={
            "Art": "Ignem",
            "Level": "10",
            "Quality": "12",
            "Owner": "laboratory:lab1",
        },
        saved=lambda s: [
            (b.owner_kind, b.owner_id) for b in s.books if b.id == "b-cov"
        ],
        expected=[("laboratory", "lab1")],
        invalid={"Name": ""},
    ),
    "add book": Contract(
        prefill={"Name": "", "Type": Select.NULL, "Owner": "covenant:cov1"},
        edits={
            "Name": "Scrolls",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Language": "Greek",
        },
        saved=lambda s: [
            (b.type, b.language, b.owner_kind, b.owner_id)
            for b in s.books
            if b.name == "Scrolls"
        ],
        expected=[("Tractatus", "Greek", "covenant", "cov1")],
        invalid=[
            {"Name": ""},
            # A templated Ability needs its detail.
            {
                "Name": "Lore",
                "Type": "Ability Summa",
                "Ability": "Area Lore: {region}",
            },
        ],
        shown={"#section-lib-books-list": "Scrolls"},
    ),
    # The Armarium's Add: the book form, its owner none.
    "armarium add book": Contract(
        prefill={"Name": "", "Type": Select.NULL, "Owner": ""},
        edits={
            "Name": "Found Folio",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
        },
        saved=lambda s: [
            (b.owner_kind, b.owner_id) for b in s.books if b.name == "Found Folio"
        ],
        expected=[(None, None)],
        invalid={"Name": ""},
        shown={"#armarium-list": "Found Folio"},
    ),
    # The Custodia's Add: the device form, its holder none.
    "custodia add device": Contract(
        prefill={"Name": "", "Holder": ""},
        edits={"Name": "Buried Wand"},
        saved=lambda s: [
            (d.holder_kind, d.holder_id)
            for d in s.enchanted_devices
            if d.name == "Buried Wand"
        ],
        expected=[(None, None)],
        invalid={"Name": ""},
        shown={"#custodia-list": "Buried Wand"},
    ),
    "add book into a codex": Contract(
        prefill={"Name": "", "Codex": Select.NULL, "Owner": "covenant:cov1"},
        edits={
            "Name": "Scrolls",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Codex": "__new__",
            "New codex's name": "Bound Fire",
            "Palimpsest": True,
        },
        saved=lambda s: [
            (c.name, c.palimpsest, [b.name for b in s.books if b.codex_id == c.id])
            for c in s.codices
        ],
        expected=[("Bound Fire", True, ["Scrolls"])],
        invalid={"Name": ""},
        shown={"#section-lib-books-list": "│ Scrolls"},
    ),
    "add commentary": Contract(
        prefill={"Name": "", "Physical form": Select.NULL},
        edits={
            "Name": "Glosses",
            "Type": "Tractatus",
            "Subject": "Art",
            "Art": "Ignem",
            "Quality": "7",
            "Opus": "Commentary",
            "Commentary on": "b-cov",
            "Physical form": "Exemplar",
        },
        saved=lambda s: [
            (b.opus, b.commentary_on, b.physical_form)
            for b in s.books
            if b.name == "Glosses"
        ],
        expected=[("Commentary", "b-cov", "Exemplar")],
        invalid={"Name": ""},
        shown={"#section-lib-books-list": "Glosses"},
    ),
    "book craftsmanship": Contract(
        prefill={"Skilled scribe (+1)": False, "Resonant materials": Select.NULL},
        edits={
            "Skilled scribe (+1)": True,
            "Skilled illuminator (+1)": True,
            "Resonant materials": "story_resonance",
        },
        saved=lambda s: [b.craft for b in s.books if b.id == "b-cov"],
        expected=[["scribe", "illuminator", "story_resonance"]],
        invalid={"Name": ""},
    ),
    "enchant a book": Contract(
        prefill={"Epitome": Select.NULL},
        edits={
            "Art": "Ignem",
            "Level": "10",
            "Quality": "12",
            "Epitome": "__new_epitome__",
        },
        saved=lambda s: [
            (d.name, d.holder_kind, d.holder_id)
            for b in s.books
            if b.id == "b-cov"
            for d in s.enchanted_devices
            if d.id == b.device_id
        ],
        expected=[("Summa", "covenant", "cov1")],
        invalid={"Name": ""},
    ),
    "research bonuses": Contract(
        prefill={"Ignem": "0"},
        edits={"Ignem": "3"},
        saved=lambda s: s.covenants[0].library_research,
        expected={"Ignem": 3},
        shown={"#lib-summary-right": "1 subject"},
    ),
    # Lab Texts
    "add lab text": Contract(
        prefill={"Name": "", "Type": Select.NULL, "Owner": "laboratory:lab1"},
        edits={
            "Name": "Ring of Warmth",
            "Type": "Lab Text",
            "Kind": "Enchantment",
            "Technique": "Creo",
            "Form": "Ignem",
            "Level": "10",
            "Range / Duration / Target": "Touch / Sun / Individual",
            "Device": "Lesser Enchantment",
            "Author's sheet": "mag2",
            "Raw (author's shorthand)": True,
        },
        saved=lambda s: [
            (
                b.text_kind,
                b.technique,
                b.form,
                b.level,
                b.effect_rdt,
                b.device_type,
                b.author_id,
                b.author,
                b.raw,
                b.spell_id,
            )
            for b in s.books
            if b.name == "Ring of Warmth"
        ],
        expected=[
            (
                "Enchantment",
                "Creo",
                "Ignem",
                10,
                "Touch / Sun / Individual",
                "Lesser Enchantment",
                "mag2",
                "Brother Oda",
                True,
                None,
            )
        ],
        # A spell's text needs its spell; any other kind needs its level.
        invalid=[
            {"Name": "Text", "Type": "Lab Text"},
            {"Name": "Text", "Type": "Lab Text", "Kind": "Other"},
        ],
        shown={"#section-lab-texts-list": "Ring of Warmth"},
    ),
    "perform ritual again": Contract(
        prefill={"Vis": "Creo", "Vis from": "laboratory"},
        edits={"Vis from": "character"},
        saved=lambda s: (
            character(s).raw_vis,
            character(s).aging.longevity_modifier,
            laboratory(s).diary[-1].name,
        ),
        # Level 20 / 5; 2 of his 3 pawns of Creo vis.
        expected=({"creo": 1}, 4, "Longevity Ritual performed again: Leandro"),
        # The laboratory has no Creo vis; he has no Vim.
        invalid=[
            {"Vis from": "laboratory"},
            {"Vis": "Vim", "Vis from": "character"},
        ],
    ),
    "lab texts read": Contract(
        prefill={"Author": Select.NULL, "Reads to level": "0"},
        edits={"Author": "mag2", "Reads to level": "20", "How": "decoded"},
        saved=lambda s: character(s).lab_text_access,
        expected={"mag2": LabTextAccess(20, "decoded")},
        # No author; not a number.
        invalid=[
            {"Reads to level": "5"},
            {"Author": "mag2", "Reads to level": "-"},
        ],
        shown={"#hermetic-background-right": "Brother Oda to 20 (decoded)"},
    ),
}


@pytest.mark.parametrize("name", list(CONTRACTS))
async def test_form_contract(name):
    await run_contract(name, CONTRACTS[name])
