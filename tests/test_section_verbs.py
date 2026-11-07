"""The core's table from a record and a sheet section to its Add, Edit and
Delete (section_verbs.py): checked through the table, with no screen."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import actions, section_verbs
from ars_magica_manager.commands import Choose, Confirm, Form, SectionOps
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.models import Breakthrough, Character, Saga
from ars_magica_manager.rules import activities as season_rules


def _leandro() -> tuple[Saga, Character]:
    saga = everything_saga()
    return saga, next(c for c in saga.characters if c.name == "Leandro")


def _ops(saga: Saga, character: Character, section: str) -> SectionOps:
    ops = section_verbs.section_ops(saga, character, section)
    assert ops is not None, section
    return ops


def test_every_section_in_the_table_has_the_verbs_the_keys_declare():
    saga, leandro = _leandro()
    wrong = []
    for section in section_verbs.character_ops(saga, leandro):
        offered = {
            verb
            for verb in ("add", "edit", "remove")
            if getattr(_ops(saga, leandro, section), verb) is not None
        }
        if offered != actions.SECTION_VERBS.get(section, frozenset()):
            wrong.append(f"{section}: table {sorted(offered)}")
    assert not wrong, wrong


def test_the_table_has_nothing_for_a_section_it_does_not_hold():
    saga, leandro = _leandro()
    assert section_verbs.section_ops(saga, leandro, "section-char-info") is None
    assert section_verbs.section_ops(saga, object(), "tab-abilities") is None


def test_deleting_an_ability_asks_first_and_then_removes_it():
    saga, leandro = _leandro()
    first = leandro.abilities[0]
    step = _ops(saga, leandro, "tab-abilities").remove(0)
    assert isinstance(step, Confirm)
    assert first.name in step.question
    assert first in leandro.abilities
    step.apply()
    assert first not in leandro.abilities


def test_a_tradition_chapter_offers_only_its_own_abilities():
    from ars_magica_manager import traditions

    saga, leandro = _leandro()
    tradition = traditions.all_traditions()[0]
    section = traditions.tradition_section(tradition.id)
    chooser = _ops(saga, leandro, section).add()
    offered = {choice.value.name for choice in chooser.choices()}
    assert offered <= set(tradition.abilities), offered - set(tradition.abilities)


def test_both_raw_vis_sections_change_the_one_pool():
    saga, leandro = _leandro()
    leandro.raw_vis = {"creo": 3}
    add = _ops(saga, leandro, "section-raw-vis-inventory").add()
    assert isinstance(add, Form)
    add.apply({"art": "creo", "pawns": 2})
    assert leandro.raw_vis == {"creo": 5}
    remove = _ops(saga, leandro, "section-raw-vis-hermetic").remove(0)
    assert isinstance(remove, Confirm)
    remove.apply()
    assert leandro.raw_vis == {}


def test_inventory_asks_which_kind_then_adds_it():
    saga, leandro = _leandro()
    ops = _ops(saga, leandro, "section-inventory")
    kind = ops.add()
    assert isinstance(kind, Choose)
    form = kind.apply("item")
    assert isinstance(form, Form)
    before = len(leandro.inventory)
    form.apply({"name": "Fine wool cloak"})
    assert len(leandro.inventory) == before + 1
    assert leandro.inventory[-1].name == "Fine wool cloak"


def test_a_research_goal_is_deleted_after_asking():
    saga, leandro = _leandro()
    leandro.breakthroughs.append(Breakthrough(name="A new lab text"))
    step = _ops(saga, leandro, "section-research-goals").remove(
        len(leandro.breakthroughs) - 1
    )
    assert isinstance(step, Confirm)
    step.apply()
    assert all(b.name != "A new lab text" for b in leandro.breakthroughs)


def test_this_season_offers_plan_then_edit_and_clear():
    saga, leandro = _leandro()
    ops = _ops(saga, leandro, "section-char-season")
    assert ops.edit is not None
    assert ops.remove is not None
    # A grog's Plan is the Yearly Update, with nothing to change or clear.
    leandro.type = "grog"
    assert not season_rules.is_planned(leandro)
    grog = _ops(saga, leandro, "section-char-season")
    assert grog.add is not None
    assert grog.edit is None
    assert grog.remove is None


def test_virtues_and_flaws_rows_count_within_their_side():
    saga, leandro = _leandro()
    virtues = section_verbs.section_ops(saga, leandro, "section-vf-virtues")
    flaws = section_verbs.section_ops(saga, leandro, "section-vf-flaws")
    assert virtues is not None and flaws is not None
    assert len(virtues.rows()) + len(flaws.rows()) == len(leandro.virtues_flaws)
    # A sheet's list gives the index into the whole list; the table's rows
    # count within the side.
    for index in range(len(leandro.virtues_flaws)):
        for section, ops in (
            ("section-vf-virtues", virtues),
            ("section-vf-flaws", flaws),
        ):
            try:
                row = section_verbs.table_row(leandro, section, index)
            except ValueError:
                continue
            assert 0 <= row < len(ops.rows())


def test_a_virtue_change_redraws_both_lists_and_the_characteristics():
    _, leandro = _leandro()
    assert section_verbs.refreshed(leandro, "section-vf-flaws") == (
        "section-vf-virtues",
        "section-vf-flaws",
        "section-char-characteristics",
    )
    assert section_verbs.refreshed(leandro, "tab-diary") == ("tab-diary",)


def test_traits_and_reputations_are_in_the_table():
    saga, leandro = _leandro()
    before = len(leandro.reputations)
    add = _ops(saga, leandro, "section-reputations").add()
    assert isinstance(add, Form)
    add.apply({"name": "Skilled Enchanter", "score": 2})
    assert len(leandro.reputations) == before + 1


def test_every_familiar_and_laboratory_section_has_the_verbs_the_keys_declare():
    saga, _ = _leandro()
    familiar, lab = saga.familiars[0], saga.laboratories[0]
    wrong = []
    for record, table in (
        (familiar, section_verbs.familiar_ops(saga, familiar)),
        (lab, section_verbs.laboratory_ops(saga, lab)),
    ):
        for section in table:
            ops = section_verbs.section_ops(saga, record, section)
            assert ops is not None, section
            offered = {
                verb
                for verb in ("add", "edit", "remove")
                if getattr(ops, verb) is not None
            }
            if offered != actions.SECTION_VERBS.get(section, frozenset()):
                wrong.append(f"{section}: table {sorted(offered)}")
    assert not wrong, wrong


def test_the_table_builds_for_every_record_the_sheets_show():
    """A sheet no longer decides which of its sections the table has, so
    every builder must cope with a record that does not use its section."""
    saga, _ = _leandro()
    saga.characters.append(
        Character(id="grog1", name="Hugo", type="grog", covenant_id="cov1")
    )
    records = [
        *saga.characters,
        *saga.familiars,
        *saga.laboratories,
        *saga.covenants,
        *saga.tribunals,
        *saga.neighbours,
        saga,
    ]
    for record in records:
        built = section_verbs.BUILDERS[type(record)](saga, record)
        for section, ops in built.items():
            assert ops is not None, (type(record).__name__, section)


def test_every_covenant_section_offers_no_verb_the_keys_do_not_declare():
    saga, _ = _leandro()
    covenant = saga.covenants[0]
    wrong = []
    for section in section_verbs.covenant_ops(saga, covenant):
        ops = section_verbs.section_ops(saga, covenant, section)
        assert ops is not None, section
        offered = {
            verb for verb in ("add", "edit", "remove") if getattr(ops, verb) is not None
        }
        # A Seasons list plans with Add as well as Edit, on the sheet.
        if not offered <= actions.SECTION_VERBS.get(section, frozenset()):
            wrong.append(f"{section}: table {sorted(offered)}")
    assert not wrong, wrong


def test_a_boon_row_maps_to_its_place_among_the_boons():
    saga, _ = _leandro()
    covenant = saga.covenants[0]
    kinds = covenant_forms.attached(covenant, "Hook")
    if kinds:
        assert section_verbs.table_row(covenant, "section-cov-hooks", kinds[0]) == 0
    assert section_verbs.refreshed(covenant, "section-cov-boons")[0] == (
        "section-cov-boons"
    )


def test_a_laboratory_feature_change_redraws_the_features_and_both_virtue_lists():
    saga, _ = _leandro()
    lab = saga.laboratories[0]
    assert section_verbs.refreshed(lab, "section-lab-features") == (
        "section-lab-features",
        "section-lab-vf-virtues",
        "section-lab-vf-flaws",
    )


def test_the_diary_adds_an_entry_through_its_form():
    saga, leandro = _leandro()
    step = _ops(saga, leandro, "tab-diary").add()
    assert isinstance(step, Form)


def test_editing_a_known_spell_opens_its_mastery_form():
    saga, leandro = _leandro()
    assert leandro.spells_known, "everything_saga gives Leandro a spell"
    step = _ops(saga, leandro, "section-known-spells").edit(0)
    assert isinstance(step, Form)
    assert step.title.startswith("Mastery")
