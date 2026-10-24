import re

import pytest
from support import strip_markup
from textual.content import Content

from ars_magica_manager import catalog
from ars_magica_manager import inhabitants as inh
from ars_magica_manager.models import (
    INHABITANT_KINDS,
    Ability,
    Background,
    Character,
    Characteristics,
    Covenant,
    HermeticBackground,
    Inhabitant,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import covenfolk
from ars_magica_manager.rules.xp import ability_xp


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


def _labels(saga: Saga, cov: Covenant, kind: str) -> list[str]:
    return [inh.row_label(e) for e in covenfolk.entries_for_kind(saga, cov, kind)]


# ------------------------------------------------------------------ entries


def test_magi_and_companions_are_listed_from_character_sheets():
    saga, cov = _saga()
    magi = covenfolk.entries_for_kind(saga, cov, "magus")
    assert [e.name for e in magi] == ["Corvinus"]  # only this covenant's magus
    assert magi[0].auto and magi[0].year_born == 1195
    assert inh.house_name(magi[0].house_id) == "Bonisagus"
    assert [e.name for e in covenfolk.entries_for_kind(saga, cov, "companion")] == [
        "Alys"
    ]


def test_a_mythic_companion_is_listed_among_the_companions():
    saga, cov = _saga()
    saga.characters.append(
        Character(
            id="myth1", name="Brunhild", type="mythic companion", covenant_id="cov1"
        )
    )
    companions = covenfolk.entries_for_kind(saga, cov, "companion")
    assert [e.name for e in companions] == ["Alys", "Brunhild"]
    cov.inhabitants.append(
        Inhabitant(id="d1", kind="companion", character_id="myth1", departed=True)
    )
    assert [e.name for e in covenfolk.entries_for_kind(saga, cov, "companion")] == [
        "Alys"
    ]
    departed = inh.departed_entries_for_kind(saga, cov, "companion")
    assert [e.name for e in departed] == ["Brunhild"]


def test_manual_npc_magi_follow_the_listed_characters():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(id="npc", kind="magus", name="Hidden Hermit", house="house_criamon")
    )
    entries = covenfolk.entries_for_kind(saga, cov, "magus")
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
            responsibility="IGNORED TOO",
            description="Trusted.",
        )
    )
    entries = covenfolk.entries_for_kind(saga, cov, "magus")
    assert len(entries) == 1  # not listed twice
    entry = entries[0]
    assert entry.name == "Corvinus" and entry.year_born == 1195  # live from the sheet
    assert entry.description == "Trusted."


def test_a_departed_magus_or_companion_is_neither_listed_nor_counted():
    saga, cov = _saga()
    before = inh.total_inhabitants(saga, cov)
    cov.inhabitants += [
        Inhabitant(id="d1", kind="magus", character_id="mag1", departed=True),
        Inhabitant(id="d2", kind="companion", character_id="comp1", departed=True),
    ]
    assert covenfolk.entries_for_kind(saga, cov, "magus") == []
    assert covenfolk.entries_for_kind(saga, cov, "companion") == []
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
    assert [e.name for e in covenfolk.entries_for_kind(saga, cov, "magus")] == [
        "Hidden Hermit"
    ]
    assert [e.name for e in covenfolk.entries_for_kind(saga, cov, "companion")] == [
        "Alys"
    ]


def test_departed_entries_for_kind_lists_only_departed_magi_and_companions():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="d1", kind="magus", character_id="mag1", departed=True),
        Inhabitant(id="npc", kind="magus", name="Hidden Hermit"),
    ]
    departed = inh.departed_entries_for_kind(saga, cov, "magus")
    assert [e.name for e in departed] == ["Corvinus"]
    assert departed[0].auto and departed[0].record is not None
    # Not departed, and not a Magus/Companion kind at all: nothing.
    assert inh.departed_entries_for_kind(saga, cov, "companion") == []
    assert inh.departed_entries_for_kind(saga, cov, "craftsperson") == []


def test_a_craftspersons_score_is_manual_unless_tied_to_a_sheets_ability():
    saga, cov = _saga()
    brawl = next(a for a in saga.characters[3].abilities if a.name == "Brawl")
    brawl.xp = ability_xp(4)
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
    entries = covenfolk.entries_for_kind(saga, cov, "craftsperson")
    assert [e.skill_value for e in entries] == [6, 3, 4, 2]
    assert [e.skill_from_ability for e in entries] == [None, None, 4, None]
    assert strip_markup(inh.row_label(entries[2])).split() == ["B", "4", "1", "Unknown"]
    assert "(from the linked Ability)" in inh.detail_text(entries[2], 1220)
    assert "(from the linked Ability)" not in inh.detail_text(entries[1], 1220)


def test_grog_kinds_list_only_stored_records_in_order():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="a", kind="turb", name="First", character_id="grog1"),
        Inhabitant(id="b", kind="specialist", name="Other"),
        Inhabitant(id="c", kind="turb", name="Second"),
    ]
    turb = covenfolk.entries_for_kind(saga, cov, "turb")
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
    entries = covenfolk.entries_for_kind(saga, cov, "inhabitant")
    assert len(entries) == 2 and covenfolk.headcount(entries) == 3


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
    # 4 other + 1 magus + 1 companion + 2 craft + 3 turb + 2 horses (livestock
    # aren't inhabitants at all, per the rules -- not counted here)
    assert inh.total_inhabitants(saga, cov) == 4 + 1 + 1 + 2 + 3 + 2


def test_livestock_are_tracked_but_never_counted():
    saga, cov = _saga()
    points_before = covenfolk.inhabitant_points(saga, cov)
    total_before = inh.total_inhabitants(saga, cov)
    cov.inhabitants.append(
        Inhabitant(id="l1", kind="livestock", name="Sheep", quantity=50)
    )
    # Neither Total Inhabitants nor the Economics points move.
    assert inh.total_inhabitants(saga, cov) == total_before
    assert covenfolk.inhabitant_points(saga, cov) == points_before
    # Still listed and headcount-able on its own list.
    assert covenfolk.headcount(covenfolk.entries_for_kind(saga, cov, "livestock")) == 50


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
    styles = [entry for entry in by_id.values() if entry.governance]
    assert len(styles) == 7
    for entry in styles:
        assert (entry.type, entry.tier, entry.category) == ("Boon", "Free", "Residents")


def test_governance_follows_the_boon_else_the_typed_value():
    saga, cov = _saga()
    assert inh.governance_names(cov) == []
    assert "(not set)" in inh.loyalty_left_text(saga, cov)

    cov.loyalty.governance = "Guild of Mercers"
    assert "Guild of Mercers" in inh.loyalty_left_text(saga, cov)

    cov.boons_hooks.append(VirtueFlawInstance(vf_id="covbh_boon_free_autocracy"))
    assert inh.governance_names(cov) == ["Autocracy"]
    left = inh.loyalty_left_text(saga, cov)
    assert "Autocracy" in left and "Guild of Mercers" not in left  # the Boon wins
    assert "[i $label]Autocracy[/]" in left  # shown as inherited


# --------------------------------------------------------------------- text


def test_row_labels_follow_the_paper_sheet_per_kind():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="m", kind="magus", name="NPC", year_born=None, gift="Blatant"),
        Inhabitant(
            id="cr",
            kind="craftsperson",
            name="Gerhard",
            year_born=1187,
            responsibility="Blacksmithing",
            skill_value=7,
        ),
        Inhabitant(id="t", kind="turb", name="Thomae", responsibility="Shield Grog"),
        Inhabitant(id="h", kind="horse", name="Grey", quantity=3),
    ]
    assert _labels(saga, cov, "craftsperson") == [
        "Gerhard             Blacksmithing           7    1        1187"
    ]
    assert _labels(saga, cov, "turb") == [
        "Thomae              Shield Grog           1     Unknown"
    ]
    assert _labels(saga, cov, "horse") == ["Grey                    3     Unknown"]


def test_magus_row_label_lines_up_under_the_table_header():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(id="m", kind="magus", name="NPC", year_born=None, gift="Blatant")
    )
    header = inh.table_header("magus")
    rows = [inh.row_label(e) for e in covenfolk.entries_for_kind(saga, cov, "magus")]
    assert rows == [
        "Corvinus            Bonisagus             1195  The Gift",
        "NPC                 Unknown            Unknown  Blatant Gift",
    ]
    assert header == "  Name                House            Year Born  Gift"
    # The House and Year Born columns line up between the header and rows.
    assert header.index("House") == 2 + inh._NAME_WIDTH
    assert header.index("Gift") == 2 + rows[0].index("The Gift")


def test_other_covenfolk_row_label_shows_role_qty_and_year_born_only_if_one():
    saga, cov = _saga()
    cov.inhabitants += [
        # A named individual: role shown, Year Born shown (Qty is 1).
        Inhabitant(
            id="a",
            kind="inhabitant",
            name="Old Marta",
            role="Dependent",
            year_born=1180,
        ),
        # A named group: role shown, Year Born column is "-" (Qty > 1).
        Inhabitant(
            id="b",
            kind="inhabitant",
            name="The Miller Family",
            role="Dependent",
            quantity=4,
            year_born=1190,
        ),
        # Name is exactly the role's plural: role left out as redundant.
        Inhabitant(
            id="c", kind="inhabitant", name="Servants", role="Servant", quantity=3
        ),
        # Plural name but a DIFFERENT role: still shown (not a match).
        Inhabitant(
            id="d", kind="inhabitant", name="Servants", role="Dependent", quantity=2
        ),
    ]
    labels = _labels(saga, cov, "inhabitant")
    assert labels[0] == "Old Marta           Dependent         1        1180"
    assert labels[1] == "The Miller Family   Dependent         4           -"
    assert labels[2] == "Servants                              3           -"
    assert labels[3] == "Servants            Dependent         2           -"


def test_other_covenfolk_detail_panel_shows_the_role():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(
            id="a",
            kind="inhabitant",
            name="Old Marta",
            role="Dependent",
            responsibility="Nursemaid",
            year_born=1180,
        )
    )
    text = strip_markup(
        inh.detail_text(covenfolk.entries_for_kind(saga, cov, "inhabitant")[0], 1220)
    )
    for expected in (
        "Name: Old Marta",
        "Responsibility: Nursemaid",
        "Covenant Role: Dependent",
        "Quantity: 1",
    ):
        assert expected in text, expected
    assert "Loyalty Bonus" not in text  # not one of the Specialist bonus roles


def test_the_inhabitant_kind_is_titled_other_covenfolk():
    assert inh.KIND_TITLES["inhabitant"] == "Other Covenfolk"


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
            quantity=2,
            description="Master **smith**. Works *only* in iron.",
        )
    )
    text = inh.detail_text(
        covenfolk.entries_for_kind(saga, cov, "craftsperson")[0], 1220
    )
    plain = strip_markup(text)
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
        "Description:",
        "Master smith. Works only in iron.",
    ):
        assert expected in plain, expected
    content = Content.from_markup(text)
    styled = {(content.plain[s.start : s.end], str(s.style)) for s in content.spans}
    assert ("smith", "b") in styled and ("only", "i") in styled


def test_detail_text_for_a_listed_character_and_for_nothing():
    saga, cov = _saga()
    text = strip_markup(
        inh.detail_text(covenfolk.entries_for_kind(saga, cov, "magus")[0], 1220)
    )
    assert "House: Bonisagus" in text and "Year Born: 1195 (age 25)" in text
    assert "From the character sheet of Corvinus." in text
    assert "Quantity" not in text  # a listed person is always one
    assert "Select an inhabitant" in strip_markup(inh.detail_text(None, 1220))


def test_loyalty_left_text_shows_the_derived_totals():
    saga, cov = _saga()
    cov.loyalty.equipment = "Anything they need"  # +20
    left = strip_markup(inh.loyalty_left_text(saga, cov))
    # 1 magus, The Gift (no Virtues/Flaws on the fixture's Corvinus) -> -30.
    assert re.search(r"Base Loyalty Points:\s+-30", left)
    assert re.search(r"Total modifiers:\s+20\b", left)
    assert re.search(r"Current Loyalty Points:\s+-10\b", left)
    assert re.search(r"Prevailing Loyalty Score:\s+-1\b", left)


def test_loyalty_right_text_shows_every_situational_modifier():
    saga, cov = _saga()
    cov.loyalty.equipment = "Anything they need"
    cov.loyalty.money = "Lavish salary"
    cov.loyalty.pension = True
    cov.loyalty.familiarity = 4
    cov.loyalty.actions_and_events = -2
    cov.loyalty.magical_influence = 3
    cov.reputations.append(ScoredTrait(name="Litigious", score=-2, known=True))
    right = strip_markup(inh.loyalty_right_text(saga, cov))
    assert "Situational Modifiers for:" in right
    assert "Anything they need  (+20)" in right
    assert "Lavish salary  (+20)" in right and "+ pension" in right
    assert re.search(r"Familiarity:\s+4\b", right)
    assert re.search(r"Reputation:\s+-10\b", right)  # -5 * 2
    assert re.search(r"Actions and events:\s+-2\b", right)
    assert re.search(r"Magical Influence:\s+3\b", right)


def test_population_text_colors_the_needed_pair_by_theme():
    saga, cov = _saga()
    cov.population.other_people = 5
    # Enough inhabitant points (1 magus + 1 companion + 5 other = 8+3+5=16) that
    # some servants/teamsters are required.
    population = inh.population_text(saga, cov)
    minimum = covenfolk.minimum_servants(saga, cov)
    assert f"[$text-error]0 / {minimum}[/]" in population  # none hired yet
    # Hiring them (excluded from the minimum's own formula, so it stays put).
    cov.inhabitants.append(
        Inhabitant(
            id="s", kind="inhabitant", name="Servants", quantity=minimum, role="Servant"
        )
    )
    assert f"[$text-success]{minimum} / {minimum}[/]" in inh.population_text(saga, cov)
    assert re.search(
        r"Total Inhabitants:\s+7\b", strip_markup(population)
    )  # 5 + magus + companion


# ----------------------------------------------------------------- gift


def test_gift_is_read_from_a_sheets_virtues_or_a_manual_choice():
    saga, cov = _saga()  # Corvinus has no Gift-related Virtue/Flaw
    magus = covenfolk.entries_for_kind(saga, cov, "magus")[0]
    assert magus.gift == "The Gift"  # the default assumption

    gentle = next(c for c in saga.characters if c.id == "mag1")
    gentle.virtues_flaws = [VirtueFlawInstance(vf_id="vf_gentle_gift")]
    assert covenfolk.entries_for_kind(saga, cov, "magus")[0].gift == "Gentle Gift"
    gentle.virtues_flaws = [VirtueFlawInstance(vf_id="vf_blatant_gift")]
    assert covenfolk.entries_for_kind(saga, cov, "magus")[0].gift == "Blatant Gift"

    for choice, expected in (
        ("", ""),
        ("Gentle", "Gentle Gift"),
        ("Normal", "The Gift"),
        ("Blatant", "Blatant Gift"),
        ("None", "No Gift"),
    ):
        cov.inhabitants = [Inhabitant(id="npc", kind="magus", name="NPC", gift=choice)]
        entry = covenfolk.entries_for_kind(saga, cov, "magus")[1]
        assert entry.gift == expected, choice


def test_gift_does_not_apply_to_non_magi():
    saga, cov = _saga()
    companion = covenfolk.entries_for_kind(saga, cov, "companion")[0]
    assert companion.gift == ""


def test_base_loyalty_averages_gift_modifiers_and_rounds_away_from_zero():
    saga, cov = _saga()
    saga.characters = [
        Character(id=f"m{i}", name=f"M{i}", type="magus", covenant_id="cov1")
        for i in range(5)
    ]
    saga.characters.append(
        Character(
            id="m5",
            name="M5",
            type="magus",
            covenant_id="cov1",
            virtues_flaws=[VirtueFlawInstance(vf_id="vf_blatant_gift")],
        )
    )
    # 5 x The Gift (-30) + 1 x Blatant Gift (-105) = -255 / 6 = -42.5 -> -43.
    assert inh.base_loyalty(saga, cov) == -43


def test_base_loyalty_is_zero_with_no_magi():
    saga, cov = _saga()
    saga.characters = [c for c in saga.characters if c.type != "magus"]
    assert inh.base_loyalty(saga, cov) == 0


def test_gentle_and_no_gift_both_avoid_the_social_penalty():
    saga, cov = _saga()
    gentle = next(c for c in saga.characters if c.id == "mag1")
    gentle.virtues_flaws = [VirtueFlawInstance(vf_id="vf_gentle_gift")]
    assert inh.base_loyalty(saga, cov) == 0
    gentle.virtues_flaws = []
    cov.inhabitants = []  # manual "None" magus instead of the sheet-linked one
    saga.characters = [c for c in saga.characters if c.id != "mag1"]
    cov.inhabitants.append(Inhabitant(id="npc", kind="magus", name="NPC", gift="None"))
    assert inh.base_loyalty(saga, cov) == 0


# -------------------------------------------------------------- specialists


def _presence(value: int) -> Characteristics:
    return Characteristics(presence=value)


def test_role_bonus_is_presence_plus_the_roles_ability_from_the_sheet():
    saga, cov = _saga()
    grog = next(c for c in saga.characters if c.id == "grog1")
    grog.characteristics = _presence(2)
    grog.abilities.append(Ability(name="Leadership", xp=ability_xp(5)))
    cov.inhabitants.append(
        Inhabitant(
            id="s",
            kind="specialist",
            name="Old Thomae",
            character_id="grog1",
            role="Turb Captain",
        )
    )
    entry = covenfolk.entries_for_kind(saga, cov, "specialist")[0]
    assert entry.role_presence == 2 and entry.role_ability_total == 5
    assert entry.role_bonus == 7


def test_autocrat_sums_both_profession_abilities():
    saga, cov = _saga()
    grog = next(c for c in saga.characters if c.id == "grog1")
    grog.characteristics = _presence(1)
    grog.abilities += [
        Ability(name="Profession: Steward", xp=ability_xp(3)),
        Ability(name="Profession: Chamberlain", xp=ability_xp(4)),
    ]
    cov.inhabitants.append(
        Inhabitant(
            id="s",
            kind="specialist",
            name="Old Thomae",
            character_id="grog1",
            role="Autocrat",
        )
    )
    entry = covenfolk.entries_for_kind(saga, cov, "specialist")[0]
    assert entry.role_ability_total == 7  # 3 + 4
    assert entry.role_bonus == 8  # + Presence 1


def test_role_bonus_is_manual_without_a_sheet_and_none_for_other_roles():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(
            id="s",
            kind="specialist",
            name="Hired Steward",
            role="Steward",
            presence=1,
            skill_value=6,
        ),
        Inhabitant(id="t", kind="specialist", name="A Teacher", role="Teacher"),
    ]
    entries = covenfolk.entries_for_kind(saga, cov, "specialist")
    assert entries[0].role_bonus == 7  # manual Presence + manual Ability
    assert entries[1].role_bonus is None  # not one of the four bonus roles


def test_specialists_loyalty_sums_companions_and_specialists_bonuses():
    saga, cov = _saga()
    comp = next(c for c in saga.characters if c.id == "comp1")
    comp.characteristics = _presence(3)
    comp.abilities.append(Ability(name="Profession: Steward", xp=ability_xp(2)))
    cov.inhabitants = [
        Inhabitant(id="a", kind="companion", character_id="comp1", role="Steward"),
        Inhabitant(
            id="b",
            kind="specialist",
            name="Hired Hand",
            role="Chamberlain",
            presence=1,
            skill_value=4,
        ),
        Inhabitant(id="c", kind="specialist", name="Idle", role="Other"),
    ]
    assert inh.specialists_loyalty(saga, cov) == (3 + 2) + (1 + 4)


# ----------------------------------------------------------- loyalty lookups


def test_equipment_and_money_loyalty_points_match_the_tables():
    _, cov = _saga()
    for option, points in inh.EQUIPMENT_LOYALTY_POINTS.items():
        cov.loyalty.equipment = option
        assert inh.equipment_loyalty(cov) == points
    for option, points in inh.MONEY_LOYALTY_POINTS.items():
        cov.loyalty.money = option
        cov.loyalty.pension = False
        assert inh.money_loyalty(cov) == points
        cov.loyalty.pension = True
        assert inh.money_loyalty(cov) == points + 10


def test_living_conditions_loyalty_follows_the_covenants_mundane_field():
    _, cov = _saga()
    cov.living_conditions_mundane = 1
    assert inh.living_conditions_loyalty(cov) == 10
    cov.living_conditions_mundane = -2
    assert inh.living_conditions_loyalty(cov) == -20


def test_reputations_the_covenfolk_know_of_move_loyalty():
    # Covenants p. 40: -5 a point of a bad one, +5 a point of a good local one.
    _, cov = _saga()
    cov.reputations = [
        ScoredTrait(name="Generous", score=2, known=True),
        ScoredTrait(name="Wise", score=1, known=True, type="Hermetic"),  # not local
        ScoredTrait(name="Litigious", score=-2, known=True),
        ScoredTrait(name="Secret Cult", score=-3, known=False),  # not known yet
    ]
    assert inh.reputation_loyalty(cov) == 10 - 10


def test_prevailing_loyalty_score_is_symmetric_and_clamps_beyond_the_table():
    for points, score in ((0, 0), (5, 1), (104, 5), (105, 6), (500, 6)):
        assert inh.prevailing_loyalty_score(points) == score
        assert inh.prevailing_loyalty_score(-points) == -score


def test_a_covenants_season_picks_the_column_of_the_points_table():
    saga, cov = _saga()
    saga.characters = [c for c in saga.characters if c.type == "grog"]
    cov.covenant_season = "Spring"
    cov.inhabitants = [Inhabitant(id="m", kind="magus", name="M", quantity=1)]
    # A manual magus with no listed grogs/other categories: just the one.
    assert covenfolk.inhabitant_points(saga, cov) == 5
    cov.covenant_season = "Winter"
    assert covenfolk.inhabitant_points(saga, cov) == 5
    cov.covenant_season = "Summer"
    assert covenfolk.inhabitant_points(saga, cov) == 10
    cov.covenant_season = "Autumn"
    assert covenfolk.inhabitant_points(saga, cov) == 10


def test_inhabitant_points_count_each_kind_and_everyone_counted_by_number():
    saga, cov = _saga()
    cov.inhabitants = [
        Inhabitant(id="a", kind="specialist", name="Steward"),  # 2
        Inhabitant(id="b", kind="craftsperson", name="Smith"),  # 2
        Inhabitant(id="c", kind="turb", name="Guards", quantity=4),  # 4
        Inhabitant(id="d", kind="horse", name="Mules", quantity=2),  # 2
        Inhabitant(id="e", kind="livestock", name="Sheep", quantity=9),  # 0
        # Other Covenfolk, each tagged with its Covenant Role: 1 point each.
        Inhabitant(
            id="f", kind="inhabitant", name="Servants", quantity=3, role="Servant"
        ),
        Inhabitant(
            id="g", kind="inhabitant", name="Teamsters", quantity=1, role="Teamster"
        ),
        Inhabitant(
            id="h", kind="inhabitant", name="Laborers", quantity=2, role="Laborer"
        ),
    ]
    cov.population.other_people = 1
    # 8 (magus + companion) + 2 + 2 + 4 + 2 + 0 + (3 + 1 + 2) covenfolk + 1 other
    assert covenfolk.inhabitant_points(saga, cov) == 8 + 10 + 7


def test_a_departed_magus_no_longer_counts_toward_the_points():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(id="d", kind="magus", character_id="mag1", departed=True)
    )
    assert covenfolk.inhabitant_points(saga, cov) == 3  # just the companion


def test_exclude_roles_leaves_matching_other_covenfolk_entries_out_of_the_total():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(
            id="f", kind="inhabitant", name="Laborers", quantity=4, role="Laborer"
        )
    )
    with_ = covenfolk.inhabitant_points(saga, cov)
    without = covenfolk.inhabitant_points(saga, cov, exclude_roles=("Laborer",))
    assert with_ - without == 4  # 1 point per laborer at Spring
    # A role that doesn't appear on the list changes nothing.
    assert covenfolk.inhabitant_points(saga, cov, exclude_roles=("Servant",)) == with_


# ------------------------------------------------------- servants/teamsters


def test_other_covenfolk_count_sums_quantities_by_role():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="a", kind="inhabitant", name="Old Thomae", role="Teamster"),
        Inhabitant(
            id="b", kind="inhabitant", name="Servants", role="Servant", quantity=4
        ),
        Inhabitant(
            id="c", kind="inhabitant", name="More Servants", role="Servant", quantity=2
        ),
        Inhabitant(id="d", kind="inhabitant", name="Unassigned"),  # no role: ignored
    ]
    assert covenfolk.other_covenfolk_count(saga, cov, "Teamster") == 1
    assert covenfolk.other_covenfolk_count(saga, cov, "Servant") == 6
    assert covenfolk.other_covenfolk_count(saga, cov, "Laborer") == 0


def test_minimum_servants_and_teamsters_follow_the_formulas():
    saga, cov = _saga()
    cov.inhabitants.append(Inhabitant(id="t", kind="turb", name="Turb", quantity=17))
    # Points excluding servants/laborers/teamsters: 1 magus(5) + 1 companion(3)
    # + 17 turb(1 each) = 25 -> 2 servants per 10 or part of 10 -> 6.
    assert covenfolk.minimum_servants(saga, cov) == 6
    # Points excluding laborers/teamsters: same 25 (no servants/laborers
    # hired yet) -> 1 teamster per 10 -> 3 (rounded up from 2.5).
    assert covenfolk.minimum_teamsters(saga, cov) == 3


def test_laborers_reduce_the_minimum_teamsters_but_not_servants():
    saga, cov = _saga()
    cov.inhabitants += [
        Inhabitant(id="t", kind="turb", name="Turb", quantity=17),
        Inhabitant(
            id="f", kind="inhabitant", name="Laborers", quantity=5, role="Laborer"
        ),
    ]
    # The servants formula excludes laborers entirely, so hiring some doesn't
    # change it: still 25 points -> 6.
    assert covenfolk.minimum_servants(saga, cov) == 6
    # The teamsters formula also excludes laborers' own points, then
    # subtracts 2 per laborer on top: 25 - 2*5 = 15 -> 2 (rounded up from 1.5).
    assert covenfolk.minimum_teamsters(saga, cov) == 2


def test_minimum_teamsters_never_goes_negative():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(
            id="f", kind="inhabitant", name="Laborers", quantity=100, role="Laborer"
        )
    )
    assert covenfolk.minimum_teamsters(saga, cov) == 0


# -------------------------------------------------------------------- model


def test_a_save_from_before_this_session_loads_and_drops_the_stale_fields():
    """Simulates an older saved covenant that still has the removed Loyalty/
    Population/Inhabitant fields: from_dict must not choke on them."""
    data = {
        "id": "c",
        "saga_id": "s",
        "name": "Old",
        "inhabitants": [
            {"id": "i", "kind": "turb", "name": "Guard", "loyalty": 3},
        ],
        "loyalty": {
            "base_points": -30,
            "current_points": -10,
            "prevailing_score": -1,
            "living_conditions": 10,
            "equipment_modifier": 5,
            "money_modifier": 0,
            "specialists": 2,
            "familiarity": 1,
        },
        "population": {
            "teamsters_needed": 2,
            "servants_needed": 4,
            "teamsters": 1,
            "servants": 3,
            "laborers": 2,
            "other_people": 6,
        },
    }
    cov = Covenant.from_dict(data)
    assert cov.inhabitants[0].name == "Guard"  # the stale "loyalty" key is dropped
    assert not hasattr(cov.inhabitants[0], "loyalty")
    assert cov.loyalty.familiarity == 1  # the still-valid key survives
    assert cov.population.other_people == 6  # the still-valid key survives
    assert not hasattr(cov.population, "teamsters")
    assert not hasattr(cov.population, "servants")
    assert not hasattr(cov.population, "laborers")


def test_unknown_inhabitant_kind_is_rejected():
    with pytest.raises(ValueError, match="kind"):
        Inhabitant(id="x", kind="dragon")
    assert len(INHABITANT_KINDS) == 9


def test_save_entry_adds_updates_and_records_a_listed_character():
    saga, cov = _saga()
    inh.save_entry(cov, "specialist", None, {"name": "Scribe", "quantity": 1})
    scribe = cov.inhabitants[-1]
    assert (scribe.id, scribe.kind, scribe.name) == ("scribe", "specialist", "Scribe")

    entry = next(
        e for e in covenfolk.entries_for_kind(saga, cov, "specialist") if e.record
    )
    inh.save_entry(cov, "specialist", entry, {"name": "Head Scribe"})
    assert scribe.name == "Head Scribe" and len(cov.inhabitants) == 1

    # A magus listed from their sheet gets a record the first time it's edited.
    corvinus = next(
        e for e in covenfolk.entries_for_kind(saga, cov, "magus") if e.record is None
    )
    inh.save_entry(cov, "magus", corvinus, {"presence": 2})
    record = cov.inhabitants[-1]
    assert (record.id, record.character_id) == ("magus_corvinus", "mag1")


def test_save_entry_links_a_new_grogs_record_to_the_grog():
    saga, cov = _saga()
    grog = saga.characters[3]
    inh.save_entry(cov, "turb", None, {"name": ""}, grog)
    assert (cov.inhabitants[-1].id, cov.inhabitants[-1].character_id) == (
        "turb",
        "grog1",
    )


def test_mark_departed_flags_the_record_or_creates_a_departed_one():
    saga, cov = _saga()
    corvinus = next(e for e in covenfolk.entries_for_kind(saga, cov, "magus"))
    inh.mark_departed(cov, "magus", corvinus)
    record = cov.inhabitants[-1]
    assert (record.character_id, record.departed) == ("mag1", True)

    record.departed = False
    again = next(e for e in covenfolk.entries_for_kind(saga, cov, "magus"))
    inh.mark_departed(cov, "magus", again)
    assert record.departed and len(cov.inhabitants) == 1


def test_form_problem_needs_a_quantity_of_at_least_one():
    assert inh.form_problem({"quantity": 0}) == "Quantity must be at least 1."
    assert inh.form_problem({"quantity": 3}) is None
    assert inh.form_problem({}) is None


def test_add_on_the_magi_offers_every_magus_not_on_the_list():
    saga, cov = _saga()
    cov.inhabitants.append(
        Inhabitant(id="d1", kind="magus", character_id="mag1", departed=True)
    )
    assert [c.name for c in inh.addable_characters(saga, cov, "magus")] == [
        "Corvinus",
        "Far Away",
    ]
    assert inh.addable_characters(saga, cov, "craftsperson") == []
    # Taken back on: counted again.
    corvinus = saga.character("mag1")
    assert corvinus is not None
    inh.take_in(cov, "magus", corvinus)
    assert [e.name for e in covenfolk.entries_for_kind(saga, cov, "magus")] == [
        "Corvinus"
    ]
    # From another covenant: they join this one.
    far = saga.character("mag2")
    assert far is not None
    inh.take_in(cov, "magus", far)
    assert far.covenant_id == "cov1"
    assert inh.addable_characters(saga, cov, "magus") == []
