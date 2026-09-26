from dataclasses import asdict

import pytest
from support import strip_markup
from textual.content import Content

from ars_magica_manager import possessions as pos
from ars_magica_manager.models import (
    POSSESSION_KINDS,
    Character,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Possession,
    Saga,
)


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="cov1", saga_id="s", name="Dammerstein")
    saga = Saga(
        id="s",
        name="Saga",
        covenants=[covenant, Covenant(id="cov2", saga_id="s", name="Elsewhere")],
        characters=[Character(id="mag1", name="Corvinus", type="magus")],
        laboratories=[
            Laboratory(
                id="lab1",
                covenant_id="cov1",
                name="Obsidian Crucible",
                owner_id="mag1",
                location="The north tower",
                build_points=30,
                characteristics=LabCharacteristics(general_quality=4, upkeep=12),
            ),
            Laboratory(id="lab2", covenant_id="cov2", name="Not Ours"),
            Laboratory(id="lab3", covenant_id=None, name="Loose Lab"),
        ],
    )
    return saga, covenant


def _labels(saga: Saga, cov: Covenant, kind: str) -> list[str]:
    return [pos.row_label(e) for e in pos.entries_for_kind(saga, cov, kind)]


# ------------------------------------------------------------------ entries


def test_the_covenants_laboratories_are_listed_as_sanctums():
    saga, cov = _saga()
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert [e.name for e in entries] == ["Obsidian Crucible"]  # only this covenant's
    entry = entries[0]
    assert entry.auto and entry.owner == "Corvinus"
    assert entry.location == "The north tower" and entry.build_points == 30


def test_manual_sanctums_follow_the_laboratories():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(id="s", kind="sanctum", name="Hidden Study", owner="Leandro")
    )
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert [e.name for e in entries] == ["Obsidian Crucible", "Hidden Study"]
    assert not entries[1].auto and entries[1].owner == "Leandro"


def test_a_record_for_a_laboratory_only_adds_covenant_side_fields():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(
            id="o",
            kind="sanctum",
            lab_id="lab1",
            name="IGNORED",
            owner="IGNORED",
            location="IGNORED",
            quality=999,  # ignored -- Quality comes from the laboratory
            upkeep=999,  # ignored -- Upkeep comes from the laboratory
            usage="Heavy (3+ Seasons)",
            description="Very busy.",
        )
    )
    entries = pos.entries_for_kind(saga, cov, "sanctum")
    assert len(entries) == 1  # not listed twice
    entry = entries[0]
    assert (entry.name, entry.owner, entry.location) == (
        "Obsidian Crucible",
        "Corvinus",
        "The north tower",
    )  # live from the laboratory
    assert (entry.quality, entry.upkeep, entry.usage) == (4, 12, "Heavy (3+ Seasons)")
    assert entry.description == "Very busy."


def test_sanctum_quality_and_upkeep_come_from_the_laboratory():
    """A laboratory's General Quality and Upkeep Characteristics (manual plus
    any Virtue/Flaw modifiers) map directly onto its Sanctum entry."""
    saga, cov = _saga()
    lab = saga.laboratories[0]
    entry = pos.entries_for_kind(saga, cov, "sanctum")[0]
    assert (entry.quality, entry.upkeep) == (
        lab.characteristics.general_quality,
        lab.characteristics.upkeep,
    )
    lab.characteristics.general_quality = 0
    lab.characteristics.upkeep = 0
    entry = pos.entries_for_kind(saga, cov, "sanctum")[0]
    assert (entry.quality, entry.upkeep) == (0, 0)


def test_other_kinds_list_only_their_records_in_order():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="a", kind="weapon", name="Crossbows", quantity=6),
        Possession(id="b", kind="armor", name="Mail"),
        Possession(id="c", kind="weapon", name="Spears"),
    ]
    assert [e.name for e in pos.entries_for_kind(saga, cov, "weapon")] == [
        "Crossbows",
        "Spears",
    ]
    assert [e.name for e in pos.entries_for_kind(saga, cov, "armor")] == ["Mail"]
    assert pos.entries_for_kind(saga, cov, "item") == []


def test_total_pawns_adds_up_a_vis_list():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="a", kind="vis_store", name="A", art="Vim", pawns=9),
        Possession(id="b", kind="vis_store", name="B", art="Creo", pawns=3),
        Possession(id="c", kind="vis_source", name="C", art="Vim", pawns=4),
    ]
    assert pos.total_pawns(saga, cov, "vis_store") == 12
    assert pos.total_pawns(saga, cov, "vis_source") == 4


# --------------------------------------------------------------------- text


def test_row_labels_show_the_fields_the_sheet_lists():
    saga, cov = _saga()
    cov.possessions += [
        Possession(
            id="p",
            kind="property",
            name="North Field",
            location="By the river",
            dimensions="40 acres",
            inhabitants="Two families",
        ),
        Possession(id="p2", kind="property", name="Bare Plot"),
        Possession(
            id="s", kind="sanctum", name="Study", owner="Leandro", quality=3, upkeep=10
        ),
        Possession(id="w", kind="weapon", name="Crossbows", quantity=6),
        Possession(
            id="v", kind="vis_source", name="Well", art="Vim", pawns=3, season="Winter"
        ),
        Possession(id="r", kind="vis_store", name="Vim Vis", art="Vim", pawns=9),
    ]
    assert _labels(saga, cov, "property") == [
        "North Field         By the river      40 acres      Two families",
        "Bare Plot",  # every field but the name is optional
    ]
    sanctums = _labels(saga, cov, "sanctum")
    assert sanctums[0] == "Obsidian Crucible   Corvinus              4      12"
    assert sanctums[1] == "Study               Leandro               3      10"
    assert _labels(saga, cov, "weapon") == [
        # Weapons get four trailing combat-figure columns (Init/Attack/
        # Defense/Damage), defaulting to 0 -- see STORY-205.
        "Crossbows                               Standard        6    0    0    0    0"
    ]
    assert _labels(saga, cov, "vis_source") == [
        "Well                Vim            3  Winter"
    ]
    assert _labels(saga, cov, "vis_store") == ["Vim Vis             Vim            9"]


def test_row_labels_escape_user_text():
    saga, cov = _saga()
    cov.possessions.append(Possession(id="i", kind="item", name="[Bold] Lens"))
    assert _labels(saga, cov, "item")[0].startswith(r"\[Bold] Lens")


def test_detail_text_shows_everything_for_a_sanctum_and_renders_emphasis():
    saga, cov = _saga()
    cov.possessions.append(
        Possession(
            id="o",
            kind="sanctum",
            lab_id="lab1",
            description="Works **all** year, *never* idle.",
        )
    )
    text = pos.detail_text(pos.entries_for_kind(saga, cov, "sanctum")[0])
    plain = strip_markup(text)
    for expected in (
        "Name: Obsidian Crucible",
        "Owner: Corvinus",
        "Location: The north tower",
        "Quality: 4",
        "Upkeep: 12 Points",
        "Build Points: 30",
        "Usage: Standard (2 Seasons)",
        "A laboratory of this covenant: Obsidian Crucible.",
        "Description:",
        "Works all year, never idle.",
    ):
        assert expected in plain, expected
    content = Content.from_markup(text)
    styled = {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert ("all", "b") in styled and ("never", "i") in styled


def test_detail_text_omits_empty_optional_fields():
    saga, cov = _saga()
    cov.possessions += [
        Possession(id="p", kind="property", name="Bare Plot"),
        Possession(
            id="v",
            kind="vis_source",
            name="Well",
            art="Vim",
            pawns=3,
            season="Winter",
            location="Chapel",
            physical_form="Water",
            description="Cold.",
        ),
        Possession(id="r", kind="vis_store", name="Vim Vis", art="Vim", pawns=9),
        Possession(id="w", kind="armor", name="Mail", quantity=2, description="Rusty."),
    ]
    bare = strip_markup(pos.detail_text(pos.entries_for_kind(saga, cov, "property")[0]))
    assert bare == "Name: Bare Plot"
    source = strip_markup(
        pos.detail_text(pos.entries_for_kind(saga, cov, "vis_source")[0])
    )
    for expected in (
        "Art: Vim",
        "Pawns: 3",
        "Season: Winter",
        "Location: Chapel",
        "Physical Form: Water",
        "Description:",
        "Cold.",
    ):
        assert expected in source, expected
    store = strip_markup(
        pos.detail_text(pos.entries_for_kind(saga, cov, "vis_store")[0])
    )
    assert "Location" not in store and "Physical Form" not in store
    armor = strip_markup(pos.detail_text(pos.entries_for_kind(saga, cov, "armor")[0]))
    assert "Quantity: 2" in armor and "Rusty." in armor
    assert "Select a possession" in strip_markup(pos.detail_text(None))


# -------------------------------------------------------------------- model


def test_possession_data_round_trips_and_old_saves_default():
    _, cov = _saga()
    cov.possessions.append(
        Possession(
            id="v", kind="vis_source", name="Well", art="Vim", pawns=3, season="Winter"
        )
    )
    again = Covenant.from_dict(asdict(cov))
    assert again.possessions == cov.possessions

    old = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "Old"})
    assert old.possessions == []


def test_legacy_vis_stock_becomes_raw_vis_stores():
    cov = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "Old",
            "vis_stock": {"ignem": 5, "Vim": 2, "Mystery": 1},
        }
    )
    stores = [
        (p.name, p.art, p.pawns) for p in cov.possessions if p.kind == "vis_store"
    ]
    assert stores == [
        ("Ignem Vis", "Ignem", 5),
        ("Vim Vis", "Vim", 2),
        ("Mystery Vis", "Mystery", 1),  # an unknown Art is kept as typed
    ]
    assert cov.vis_stock == {}  # moved, not copied
    # Loading the migrated data again doesn't migrate twice.
    assert len(Covenant.from_dict(asdict(cov)).possessions) == 3


def test_unknown_possession_kind_is_rejected():
    with pytest.raises(ValueError, match="kind"):
        Possession(id="x", kind="spaceship")
    assert len(POSSESSION_KINDS) == 7
