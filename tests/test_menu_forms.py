"""The More and New menus and Delete on the record, as a one-page-at-a-time
front-end offers them, without a front-end (menu_forms.py)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from screen_helpers import _saga_with_familiar, _sample_saga_with_covenant

from ars_magica_manager import (
    commands,
    creation_forms,
    form_spec,
    import_forms,
    menu_forms,
)
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.models import (
    IncomeSource,
    Inhabitant,
    KnownSpell,
    Saga,
    Spell,
)


def _answer(form: commands.Form, typed: dict[str, Any]) -> dict[str, Any]:
    """`form`'s values with `typed` entered, checked as a front-end would."""
    fields = form.fields()
    raw = {f.key: f.value for f in fields} | typed
    values = form_spec.result(fields, lambda f: raw[f.key])
    problem = form.validate(values) if form.validate else None
    assert problem is None, problem
    return values


def _labels(items) -> list[str]:
    return [item.label for item in items]


def _page(saga: Saga, kind: NodeKind, **ids: str) -> menu_forms.Page:
    return menu_forms.page_for(saga, kind, **ids)


def test_each_page_offers_what_applies_there():
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.SAGA)
    assert _labels(menu_forms.more_items(page)) == ["Import", "Export Saga", "Set Date"]
    assert _labels(menu_forms.new_items(page)) == [
        "New Covenant",
        "New Character",
        "New Laboratory",
        "Bind Familiar",
    ]
    assert menu_forms.deletes(page) is None

    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    more = _labels(menu_forms.more_items(page))
    # Fatigue has its own button in Health; the device commands and the
    # Creation Worksheet aren't on the desktop yet.
    assert "Edit Fatigue" not in more
    assert more == [
        "Lab Texts Read",
        "Export",
        "Update from a File",
        "In Creation / In Play",
        "Demote",
    ]
    assert _labels(menu_forms.new_items(page)) == ["New Character", "Bind Familiar"]
    deleted = menu_forms.deletes(page)
    assert deleted is not None and deleted.name == "Leandro"

    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    assert _labels(menu_forms.more_items(page)) == [
        "Import",
        "Set Up Research Library",
        "Export",
        "Update from a File",
        "In Creation / In Play",
    ]
    assert _labels(menu_forms.new_items(page)) == [
        "New Character",
        "New Laboratory",
        "Bind Familiar",
    ]

    familiar = _page(_saga_with_familiar(), NodeKind.FAMILIAR, familiar_id="fam1")
    assert menu_forms.more_items(familiar) == []
    assert menu_forms.new_items(familiar) == []
    deleted = menu_forms.deletes(familiar)
    assert deleted is not None and deleted.name == "Ashwing"


def test_a_companion_has_no_hermetic_commands():
    saga = _sample_saga_with_covenant()
    saga.characters[0].type = "companion"
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    assert "Lab Texts Read" not in _labels(menu_forms.more_items(page))
    assert "Bind Familiar" not in _labels(menu_forms.new_items(page))


def test_deleting_a_covenant_says_what_happens_and_cancelling_keeps_it():
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    step = menu_forms.command(page, menu_forms.DELETE_RECORD)
    assert isinstance(step, commands.Confirm)
    assert step.question.startswith("Delete Test Covenant?\n\n")
    assert "1 character becomes unassigned." in step.question
    assert saga.covenants  # nothing yet: only Yes deletes
    step.apply()
    assert saga.covenants == []
    assert saga.characters[0].covenant_id is None


def test_deleting_a_familiar_breaks_the_bond():
    saga = _saga_with_familiar()
    page = _page(saga, NodeKind.FAMILIAR, familiar_id="fam1")
    step = menu_forms.command(page, menu_forms.DELETE_RECORD)
    assert isinstance(step, commands.Confirm)
    assert "The bond with Leandro is broken." in step.question
    step.apply()
    assert saga.familiars == []


def test_moving_a_record_to_play_asks_first():
    saga = _sample_saga_with_covenant()
    character = saga.characters[0]
    character.in_creation = True
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    step = menu_forms.command(page, "toggle_mode")
    assert isinstance(step, commands.Confirm)
    assert step.question.startswith("Move Leandro to In Play? Creation checks:")
    step.apply()
    assert not character.in_creation
    step = menu_forms.command(page, "toggle_mode")
    assert isinstance(step, commands.Confirm)
    assert "back to In Creation" in step.question


def test_setting_the_date():
    saga = _sample_saga_with_covenant()
    form = menu_forms.command(_page(saga, NodeKind.SAGA), "set_date")
    assert isinstance(form, commands.Form)
    assert form.title == "Set the Saga's Date"
    unchanged = _answer(form, {})
    assert form.apply(unchanged) is None
    result = form.apply(_answer(form, {"season": "Winter", "year": "1230"}))
    assert result == ["Date set to Winter 1230."]
    assert (saga.current_season, saga.current_year) == ("Winter", 1230)


def test_editing_the_saga_keeps_its_rule_options_apart():
    saga = _sample_saga_with_covenant()
    form = creation_forms.edit_saga_form(saga)
    form.apply(_answer(form, {"name": "Renamed"}))
    assert saga.name == "Renamed"
    assert not any(
        key.startswith(creation_forms.RULE_OPTION_PREFIX) for key in vars(saga)
    )


def test_new_records_are_added_only_once_every_step_is_answered():
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    form = menu_forms.command(page, "create_character")
    assert isinstance(form, commands.Form)
    assert form.title == "Create a New Character"
    assert next(f for f in form.fields() if f.key == "covenant_id").value == "cov1"
    values = _answer(
        form,
        {"name": "Agnes", "type": "magus", "template_magus": "tpl_bonisagus"},
    )
    blanks = form.apply(values)
    # The template's blanks are asked next; nothing is made until then.
    assert isinstance(blanks, commands.Form)
    assert [f.key for f in blanks.fields()] == ["language"]
    assert [c.name for c in saga.characters] == ["Leandro"]
    blanks.apply(_answer(blanks, {"language": "German"}))
    agnes = saga.characters[-1]
    assert (agnes.name, agnes.covenant_id) == ("Agnes", "cov1")

    form = menu_forms.command(page, "create_laboratory")
    assert isinstance(form, commands.Form)
    form.apply(_answer(form, {"name": "Tower", "size": "2"}))
    assert saga.laboratories[-1].name == "Tower"

    form = menu_forms.command(_page(saga, NodeKind.SAGA), "create_covenant")
    assert isinstance(form, commands.Form)
    form.apply(_answer(form, {"name": "Fengheld"}))
    assert saga.covenants[-1].in_creation


def test_binding_a_familiar_starts_with_the_magus_on_show():
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    form = menu_forms.command(page, "create_familiar")
    assert isinstance(form, commands.Form)
    assert next(f for f in form.fields() if f.key == "character_id").value == "char1"
    form.apply(_answer(form, {"name": "Ashwing"}))
    assert [(f.name, f.character_id) for f in saga.familiars] == [("Ashwing", "char1")]


def test_restoring_a_departed_magus():
    saga = _sample_saga_with_covenant()
    covenant = saga.covenants[0]
    covenant.inhabitants.append(
        Inhabitant(id="i1", kind="magus", character_id="char1", departed=True)
    )
    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    assert "Restore" in _labels(menu_forms.more_items(page))
    step = menu_forms.command(page, "restore")
    assert isinstance(step, commands.Choose)
    assert step.title == "Restore which Magus?"
    [choice] = step.choices()
    assert choice.label == "Leandro"
    step.apply(choice.value)
    assert not covenant.inhabitants[0].departed
    assert "Restore" not in _labels(menu_forms.more_items(page))


def test_improving_income_confirms_before_it_changes():
    saga = _sample_saga_with_covenant()
    source = IncomeSource(id="mill", name="Mill", income=10)
    saga.covenants[0].economics.income_sources.append(source)
    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    assert "Improve Income" in _labels(menu_forms.more_items(page))
    form = menu_forms.command(page, "improve")
    assert isinstance(form, commands.Form)
    assert form.title == "Improve Mill"
    effect = next(f for f in form.fields() if f.key == "effect").options[-1][1]
    confirm = form.apply(_answer(form, {"effect": effect}))
    assert isinstance(confirm, commands.Confirm)
    assert source.income == 10
    assert confirm.question.startswith("Update Mill's income from 10 to ")
    confirm.apply()
    assert source.note


def test_sharing_an_invented_spell():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    spell = Spell(id="own1", name="My Flame", technique="Creo", form="Ignem", level=5)
    magus.invented_spells.append(spell)
    magus.spells_known.append(KnownSpell(spell_id="own1"))
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    assert "Share Spell" in _labels(menu_forms.more_items(page))
    confirm = menu_forms.command(page, "share_spell")
    assert isinstance(confirm, commands.Confirm)
    assert confirm.yes_label == "Share"
    confirm.apply()
    assert spell in saga.spells
    assert spell not in magus.invented_spells


def test_lab_texts_read_adds_and_forgets_an_author():
    saga = _sample_saga_with_covenant()
    magus = saga.characters[0]
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    form = menu_forms.command(page, "lab_text_access")
    assert isinstance(form, commands.Form)
    assert form.title == "Lab Texts Leandro reads"
    form.apply(_answer(form, {"name": "Tiberius", "level": "10", "via": "taught"}))
    assert magus.lab_text_access["Tiberius"].level == 10
    form = menu_forms.command(page, "lab_text_access")
    assert isinstance(form, commands.Form)
    values = {f.key: f.value for f in form.fields()} | {"name": "Tiberius"}
    assert form.validate is not None
    assert form.validate(values | {"level": -1}) == "Level can't be negative."
    form.apply(_answer(form, {"name": "Tiberius", "level": "0"}))
    assert "Tiberius" not in magus.lab_text_access


def test_exporting_and_importing_a_character(tmp_path: Path):
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.CHARACTER, character_id="char1")
    form = menu_forms.command(page, "export_record")
    assert isinstance(form, commands.Form)
    target = tmp_path / "leandro"
    result = form.apply(_answer(form, {"file": str(target)}))
    written = tmp_path / "leandro.amm.json"
    assert result == [f"Exported Leandro to {written}."]
    assert written.is_file()

    other = Saga(id="other", name="Other", storyguide="Sam")
    choose = menu_forms.command(_page(other, NodeKind.SAGA), "import_data")
    assert isinstance(choose, commands.Choose)
    assert [c.label for c in choose.choices()] == [
        "Books",
        "Spells",
        "Characters",
        "Covenants",
        "Laboratories",
        "A Whole Saga",
    ]
    wrong = choose.apply("covenants")
    assert isinstance(wrong, commands.ChooseFile)
    refused = wrong.apply(written)
    assert isinstance(refused, commands.Refuse)
    assert "it holds a character, not a covenant" in refused.why
    pick = choose.apply("characters")
    assert isinstance(pick, commands.ChooseFile)
    assert (pick.title, pick.suffix) == ("Import a character", ".json")
    confirm = pick.apply(written)
    assert isinstance(confirm, commands.Confirm)
    assert other.characters == []
    assert confirm.apply() == ["Imported Leandro (character)."]
    assert [c.name for c in other.characters] == ["Leandro"]


def test_importing_books_asks_about_each_duplicate(tmp_path: Path):
    saga = _sample_saga_with_covenant()
    csv = tmp_path / "books.csv"
    csv.write_text(
        "name,type,ability,quality,level\n"
        "On the Theory of Magic,Ability Summa,Magic Theory,5,3\n"
        "New Book,Ability Summa,Magic Theory,5,3\n"
        "On the Theory of Magic,Ability Summa,Magic Theory,5,3\n",
        encoding="utf-8",
    )
    page = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    pick = menu_forms.command(page, "import_data")
    assert isinstance(pick, commands.ChooseFile)
    assert pick.title == "Import books into Test Covenant's library"
    confirm = pick.apply(csv)
    assert isinstance(confirm, commands.Confirm)
    ask = confirm.apply()
    assert isinstance(ask, commands.Choose)
    assert ask.title.startswith("A book named On the Theory of Magic is already")
    assert [c.label for c in ask.choices()] == [
        "Skip",
        "Skip All",
        "Duplicate",
        "Duplicate All",
    ]
    assert len(saga.books) == 2  # nothing until every question is answered
    done = ask.apply("skip_all")
    assert done == [
        "Imported 1 book into Test Covenant's library; skipped 2 duplicates."
    ]
    assert [b.name for b in saga.books][-1] == "New Book"
    assert page.covenant is saga.covenants[0]


def test_spells_come_after_the_csv_help_which_can_save_an_example(tmp_path: Path):
    saga = _sample_saga_with_covenant()
    help_form = import_forms.spell_import_help(saga, tmp_path)
    assert help_form.save_label == "Choose CSV File"
    assert help_form.live is not None
    assert "Columns, in any order" in help_form.live({})
    saved = help_form.apply(_answer(help_form, {"example": True}))
    assert saved == [
        f"Saved spells_example.csv in {tmp_path}. Edit it, then import it."
    ]
    assert (tmp_path / "spells_example.csv").is_file()
    pick = help_form.apply(_answer(help_form, {}))
    assert isinstance(pick, commands.ChooseFile)
    assert pick.suffix == ".csv"
    refused = pick.apply(tmp_path / "none.csv")
    assert isinstance(refused, commands.Refuse)
    assert refused.why.startswith("Couldn't read none.csv")


def test_a_ritual_needs_the_laboratory_to_have_an_owner():
    saga = _sample_saga_with_covenant()
    lab = saga.laboratories[0]
    lab.owner_id = None
    assert isinstance(
        menu_forms.perform_ritual(saga, lab), commands.Refuse
    )  # no texts, and no owner


def test_places_sets_out_where_each_action_is_offered():
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.SAGA)
    assert {
        spot: _labels(menu_forms.placed(page, spot))
        for spot in (
            "Covenants",
            "Unassigned Characters",
            "Unassigned Laboratories",
            "Seasons",
            "Saga Management",
        )
    } == {
        "Covenants": ["New Covenant"],
        "Unassigned Characters": ["New Character"],
        "Unassigned Laboratories": ["New Laboratory"],
        "Seasons": ["Set Date"],
        "Saga Management": ["Edit Saga", "Import", "Export Saga"],
    }
    covenant = _page(saga, NodeKind.COVENANT, covenant_id="cov1")
    assert _labels(menu_forms.placed(covenant, "People")) == ["New Character"]
    assert _labels(menu_forms.placed(covenant, "Laboratories")) == ["New Laboratory"]
    # A covenant's Import brings books into its library.
    assert "Import" in _labels(menu_forms.placed(covenant, "Library"))
    # A familiar is bound on the magus, in a card where it would be shown.
    magus = _page(saga, NodeKind.CHARACTER, character_id="char1")
    assert _labels(menu_forms.placed(magus, "Familiar")) == ["Bind Familiar"]


def test_a_familiar_is_bound_on_the_magus_or_in_their_laboratory():
    saga = _sample_saga_with_covenant()
    magus = _page(saga, NodeKind.CHARACTER, character_id="char1")
    lab = _page(saga, NodeKind.LABORATORY, laboratory_id="lab1")
    assert _labels(menu_forms.placed(lab, "Planning")) == ["Bind Familiar"]
    step = menu_forms.command(lab, "create_familiar")
    assert isinstance(step, commands.Form)
    chosen = {f.key: f.value for f in step.fields()}
    assert chosen["character_id"] == "char1"
    # Not once they have one, nor for a companion or a lab with no owner.
    bound = _saga_with_familiar()
    page = _page(bound, NodeKind.CHARACTER, character_id="char1")
    assert menu_forms.placed(page, "Familiar") == []
    saga.characters[0].type = "companion"
    assert menu_forms.placed(magus, "Familiar") == []
    saga.characters[0].type = "magus"
    saga.laboratories[0].owner_id = None
    assert menu_forms.placed(lab, "Planning") == []


def test_every_new_and_more_action_has_a_place_on_the_page():
    """The desktop has no New or More menu: each action is set out on the
    page, offered by the record's own page, or is a section's button."""
    for item in (*menu_forms.NEW_MENU, *menu_forms.MORE_MENU):
        assert (
            item.action in menu_forms.PLACES
            or item.action in menu_forms.ON_THE_PAGE
            or item.action in menu_forms.NOT_ON_PAGES
        ), item.label


def test_give_silver_is_on_personal_gear_and_wealth():
    for kind, spot in (
        (NodeKind.CHARACTER, "Personal Gear"),
        (NodeKind.COVENANT, "Wealth"),
    ):
        assert menu_forms.lives_at("give_silver", kind, spot)
    assert menu_forms.lives_at("research_bonuses", NodeKind.COVENANT, "Library")


def test_the_actions_moved_to_their_sections_leave_more():
    assert menu_forms.lives_at(
        "lab_text_access", NodeKind.CHARACTER, "Hermetic Background"
    )
    assert menu_forms.lives_at("improve", NodeKind.COVENANT, "Income")
    assert menu_forms.lives_at("perform_ritual", NodeKind.LABORATORY, "Planning")
    # Restore has no place: Add on the Magi and Companions brings them back.
    assert menu_forms.PLACES["restore"] == ()


def test_every_placed_action_is_in_a_menu_and_has_a_command():
    actions = {item.action for item in (*menu_forms.NEW_MENU, *menu_forms.MORE_MENU)}
    for action in menu_forms.PLACES:
        assert action in actions | {menu_forms.EDIT_SAGA.action}
    saga = _sample_saga_with_covenant()
    page = _page(saga, NodeKind.SAGA)
    assert isinstance(
        menu_forms.command(page, menu_forms.EDIT_SAGA.action), commands.Form
    )
