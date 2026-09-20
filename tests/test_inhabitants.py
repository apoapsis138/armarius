import re
from dataclasses import asdict

import pytest
from textual.content import Content

from ars_magica_manager import catalog
from ars_magica_manager import inhabitants as inh
from ars_magica_manager.models import (
    GOVERNANCE_STYLE_IDS,
    INHABITANT_KINDS,
    Ability,
    Background,
    Character,
    Covenant,
    HermeticBackground,
    Inhabitant,
    Saga,
    VirtueFlawInstance,
)


def _saga() -> tuple[Saga, Covenant]:
    covenant = Covenant(id="cov1", saga_id="s", name="Dammerstein")
    saga = Saga(
        id="s",
        name="Saga",
        current_year=1220,
        covenants=[covenant, Covenant(id="cov2", saga_id="s", name="Elsewhere")],
        characters=[
            Character(
                id="mag1",
                name="Corvinus",
                type="magus",
                covenant_id="cov1",
                background=Background(year_born=1195),
                hermetic=HermeticBackground(house="house_bonisagus"),
            ),
            Character(id="mag2", name="Far Away", type="magus", covenant_id="cov2"),
            Character(id="comp1", name="Alys", type="companion", covenant_id="cov1"),
            Character(
                id="grog1",
                name="Old Thomae",
                type="grog",
                covenant_id="cov1",
                background=Background(year_born=1193),
                abilities=[Ability(name="Athletics"), Ability(name="Brawl")],
            ),
            Character(id="grog2", name="Dieter", type="grog", covenant_id="cov1"),
            Character(id="grog3", name="Not Ours", type="grog", covenant_id="cov2"),
            Character(id="grog4", name="Unassigned", type="grog", covenant_id=None),
        ],
    )
    return saga, covenant


def _plain(markup: str) -> str:
    return re.sub(r"\[/?[a-z]*\]", "", markup)


def _labels(saga: Saga, cov: Covenant, kind: str) -> list[str]:
    return [inh.row_label(e) for e in inh.entries_for_kind(saga, cov, kind)]


# ------------------------------------------------------------------ entries


def test_magi_and_companions_are_listed_from_character_sheets():
    saga, cov = _saga()
    magi = inh.entries_for_kind(saga, cov, "magus")
    assert [e.name for e in magi] == ["Corvinus"]  # only this covenant's magus
    assert magi[0].auto and magi[0].year_born == 1195
    assert inh.house_name(magi[0].house_id) == "Bonisagus"
    assert [e.name for e in inh.entries_for_kind(saga, cov, "companion")] == ["Alys"]


def test_manual_npc_magi_follow_the_listed_characters():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(id="npc", kind="magus", name="Hidden Hermit", house="house_criamon")
    )
    entries = inh.entries_for_kind(saga, cov, "magus")
    assert [e.name for e in entries] == ["Corvinus", "Hidden Hermit"]
    assert not entries[1].auto and entries[1].character is None
    assert inh.house_name(entries[1].house_id) == "Criamon"


def test_a_record_for_a_listed_character_only_overrides_covenant_side_fields():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(
            id="o",
            kind="magus",
            character_id="mag1",
            name="IGNORED",
            year_born=1,
            loyalty=4,
            description="Trusted.",
        )
    )
    entries = inh.entries_for_kind(saga, cov, "magus")
    assert len(entries) == 1  # not listed twice
    entry = entries[0]
    assert entry.name == "Corvinus" and entry.year_born == 1195  # live from the sheet
    assert entry.loyalty == 4 and entry.description == "Trusted."


def test_a_departed_magus_or_companion_is_neither_listed_nor_counted():
    saga, cov = _saga()
    before = inh.total_inhabitants(saga, cov)
    cov.inhabitants += [
        Inhabitant(id="d1", kind="magus", character_id="mag1", departed=True),
        Inhabitant(id="d2", kind="companion", character_id="comp1", departed=True),
    ]
    assert inh.entries_for_kind(saga, cov, "magus") == []
    assert inh.entries_for_kind(saga, cov, "companion") == []
    assert inh.total_inhabitants(saga, cov) == before - 2
    # Still in the covenant on their sheets.
    assert {c.id for c in saga.characters if c.covenant_id == "cov1"} >= {
        "mag1",
        "comp1",
    }


def test_a_departed_record_only_hides_that_character_and_kind():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="d", kind="magus", character_id="mag1", departed=True),
        Inhabitant(id="npc", kind="magus", name="Hidden Hermit"),
    ]
    assert [e.name for e in inh.entries_for_kind(saga, cov, "magus")] == [
        "Hidden Hermit"
    ]
    assert [e.name for e in inh.entries_for_kind(saga, cov, "companion")] == ["Alys"]


def test_a_craftspersons_score_is_manual_unless_tied_to_a_sheets_ability():
    saga, cov = _saga()
    brawl = next(a for a in saga.characters[3].abilities if a.name == "Brawl")
    brawl.level = 4
    cov.inhabitants += [
        # Manual: a person with no sheet.
        Inhabitant(id="a", kind="craftsperson", name="Visitor", skill_value=6),
        # A grog, but no Ability chosen yet: still manual.
        Inhabitant(
            id="b", kind="craftsperson", name="A", character_id="grog1", skill_value=3
        ),
        # A grog with an Ability chosen: its Level wins over the stored number.
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="B",
            character_id="grog1",
            skill_value=3,
            linked_ability="Brawl",
        ),
        # The chosen Ability is gone from the sheet: back to the manual number.
        Inhabitant(
            id="d",
            kind="craftsperson",
            name="C",
            character_id="grog1",
            skill_value=2,
            linked_ability="Smithing",
        ),
    ]
    entries = inh.entries_for_kind(saga, cov, "craftsperson")
    assert [e.skill_value for e in entries] == [6, 3, 4, 2]
    assert [e.skill_from_ability for e in entries] == [None, None, 4, None]
    assert "Score: 4" in _plain(inh.row_label(entries[2]))
    assert "(from the linked Ability)" in inh.detail_text(entries[2], 1220)
    assert "(from the linked Ability)" not in inh.detail_text(entries[1], 1220)


def test_grog_kinds_list_only_stored_records_in_order():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="a", kind="turb", name="First", character_id="grog1"),
        Inhabitant(id="b", kind="specialist", name="Other"),
        Inhabitant(id="c", kind="turb", name="Second"),
    ]
    turb = inh.entries_for_kind(saga, cov, "turb")
    assert [e.name for e in turb] == ["First", "Second"]
    assert turb[0].linked  # tied to grog1's sheet
    assert not turb[1].linked


# --------------------------------------------------------------- headcounts


def test_headcount_adds_up_quantities_not_rows():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="a", kind="inhabitant", name="Marta and Simon", quantity=2),
        Inhabitant(id="b", kind="inhabitant", name="Jakob"),
    ]
    entries = inh.entries_for_kind(saga, cov, "inhabitant")
    assert len(entries) == 2 and inh.headcount(entries) == 3


def test_total_inhabitants_is_calculated_from_every_list_and_other_people():
    saga, cov = _saga()
    cov.population.other_people = 4
    cov.inhabitants += [
        Inhabitant(id="c1", kind="craftsperson", name="Smith"),
        Inhabitant(id="c2", kind="craftsperson", name="Scribe"),
        Inhabitant(id="t1", kind="turb", name="Guard", quantity=3),
        Inhabitant(id="h1", kind="horse", name="Grey", quantity=2),
        Inhabitant(id="l1", kind="livestock", name="Sheep", quantity=10),
    ]
    # 4 other + 1 magus + 1 companion + 2 craft + 3 turb + 2 horses + 10 livestock
    assert inh.total_inhabitants(saga, cov) == 4 + 1 + 1 + 2 + 3 + 2 + 10


# --------------------------------------------------------------------- grogs


def test_available_grogs_are_this_covenants_unassigned_grogs():
    saga, cov = _saga()
    assert [g.name for g in inh.available_grogs(saga, cov)] == ["Old Thomae", "Dieter"]
    cov.inhabitants.append(
        Inhabitant(id="a", kind="specialist", name="Old Thomae", character_id="grog1")
    )
    assert [g.name for g in inh.available_grogs(saga, cov)] == ["Dieter"]
    cov.inhabitants.clear()  # removed from its section: available again
    assert len(inh.available_grogs(saga, cov)) == 2


def test_ability_names_come_from_the_character():
    saga, _ = _saga()
    grog = next(c for c in saga.characters if c.id == "grog1")
    assert inh.ability_names(grog) == ["Athletics", "Brawl"]
    assert inh.ability_names(None) == []


# ---------------------------------------------------------------- governance


def test_governance_styles_are_real_free_residents_boons():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert len(GOVERNANCE_STYLE_IDS) == 7
    for entry_id in GOVERNANCE_STYLE_IDS:
        entry = by_id[entry_id]
        assert (entry.type, entry.tier, entry.category) == ("Boon", "Free", "Residents")


def test_governance_follows_the_boon_else_the_typed_value():
    _, cov = _saga()
    assert inh.governance_names(cov) == []
    assert "(not set)" in inh.loyalty_left_text(cov)

    cov.loyalty.governance = "Guild of Mercers"
    assert "Guild of Mercers" in inh.loyalty_left_text(cov)

    cov.boons_hooks.append(VirtueFlawInstance(vf_id="covbh_boon_free_autocracy"))
    assert inh.governance_names(cov) == ["Autocracy"]
    left = inh.loyalty_left_text(cov)
    assert "Autocracy" in left and "Guild of Mercers" not in left  # the Boon wins
    assert "[dim]Autocracy[/]" in left  # shown as inherited


# --------------------------------------------------------------------- text


def test_row_labels_follow_the_paper_sheet_per_kind():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="m", kind="magus", name="NPC", year_born=None),
        Inhabitant(
            id="cr",
            kind="craftsperson",
            name="Gerhard",
            year_born=1187,
            responsibility="Blacksmithing",
            skill_value=7,
        ),
        Inhabitant(
            id="t", kind="turb", name="Thomae", responsibility="Shield Grog", loyalty=2
        ),
        Inhabitant(id="h", kind="horse", name="Grey", quantity=3),
    ]
    magi = _labels(saga, cov, "magus")
    assert magi[0] == "Corvinus | House Bonisagus | Year Born: 1195 | Loyalty: 0"
    assert magi[1] == "NPC | House Unknown | Year Born: Unknown | Loyalty: 0"
    assert _labels(saga, cov, "craftsperson") == [
        "Gerhard | Blacksmithing | Score: 7 | Qty: 1 | Year Born: 1187 | Loyalty: 0"
    ]
    assert _labels(saga, cov, "turb") == [
        "Thomae | Shield Grog | Qty: 1 | Year Born: Unknown | Loyalty: 2"
    ]
    assert _labels(saga, cov, "horse") == [
        "Grey | Qty: 3 | Year Born: Unknown | Loyalty: 0"
    ]


def test_row_labels_escape_user_text():
    saga, cov = _saga()
    cov.inhabitants.append(Inhabitant(id="x", kind="turb", name="[Bold] Bob"))
    assert _labels(saga, cov, "turb")[0].startswith(r"\[Bold] Bob")


def test_detail_text_shows_the_fields_and_renders_description_emphasis():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(
            id="c",
            kind="craftsperson",
            name="Gerhard",
            year_born=1187,
            responsibility="Smith",
            skill_value=7,
            field_of_work="Building",
            rare=True,
            linked_ability="Craft: Smith",
            loyalty=1,
            quantity=2,
            description="Master **smith**. Works *only* in iron.",
        )
    )
    text = inh.detail_text(inh.entries_for_kind(saga, cov, "craftsperson")[0], 1220)
    plain = _plain(text)
    for expected in (
        "Name: Gerhard",
        "Kind: Craftsperson",
        "Year Born: 1187 (age 33)",
        "Responsibility: Smith",
        "Field of Work: Building",
        "Skill Value: 7",
        "Rare: Yes",
        "Linked Ability: Craft: Smith",
        "Quantity: 2",
        "Loyalty: 1",
        "Description:",
        "Master smith. Works only in iron.",
    ):
        assert expected in plain, expected
    content = Content.from_markup(text)
    styled = {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert ("smith", "b") in styled and ("only", "i") in styled


def test_detail_text_for_a_listed_character_and_for_nothing():
    saga, cov = _saga()
    text = _plain(inh.detail_text(inh.entries_for_kind(saga, cov, "magus")[0], 1220))
    assert "House: Bonisagus" in text and "Year Born: 1195 (age 25)" in text
    assert "From the character sheet of Corvinus." in text
    assert "Quantity" not in text  # a listed person is always one
    assert "Select an inhabitant" in _plain(inh.detail_text(None, 1220))


def test_loyalty_and_population_text():
    saga, cov = _saga()
    cov.loyalty.base_points = -30
    cov.loyalty.equipment = "Anything they need"
    cov.loyalty.equipment_modifier = 2
    cov.population.teamsters, cov.population.teamsters_needed = 1, 3
    cov.population.other_people = 5
    right = _plain(inh.loyalty_right_text(cov))
    assert "Situational Modifiers for:" in right
    assert "Anything they need  (2)" in right and "Standard salary  (0)" in right
    assert re.search(r"Base Loyalty Points:\s+-30", _plain(inh.loyalty_left_text(cov)))
    population = inh.population_text(saga, cov)
    assert "1 / 3" in population
    assert re.search(r"Total Inhabitants:\s+7\b", population)  # 5 + magus + companion


# -------------------------------------------------------------------- model


def test_covenant_inhabitant_data_round_trips_and_old_saves_default():
    _, cov = _saga()
    cov.inhabitants.append(Inhabitant(id="i", kind="horse", name="Grey", quantity=2))
    cov.loyalty.base_points = -30
    cov.population.aging_magi = 1
    again = Covenant.from_dict(asdict(cov))
    assert again.inhabitants == cov.inhabitants
    assert again.loyalty.base_points == -30 and again.population.aging_magi == 1

    old = Covenant.from_dict({"id": "c", "saga_id": "s", "name": "Old"})
    assert old.inhabitants == [] and old.loyalty.equipment == "Standard"
    assert old.loyalty.money == "Standard salary"


def test_unknown_inhabitant_kind_is_rejected():
    with pytest.raises(ValueError, match="kind"):
        Inhabitant(id="x", kind="dragon")
    assert len(INHABITANT_KINDS) == 8
