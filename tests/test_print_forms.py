"""Print to PDF's options (forms/printing.py): its fields, what they choose,
and that the last choices are kept in the settings."""

from ars_magica_manager import print_layout as pl
from ars_magica_manager import settings
from ars_magica_manager.forms import printing as pf


def test_the_defaults_are_letter_short_spells_and_parchment():
    assert pf.saved_options() == pl.PrintOptions(pl.LETTER, False, True)
    fields = pf.print_fields(pf.saved_options())
    assert [(f.key, f.value) for f in fields] == [
        ("paper", pl.LETTER),
        ("spells", pf.SHORT),
        ("background", pf.TEXTURED),
    ]


def test_a_record_that_is_not_a_sheet_is_asked_only_its_paper():
    fields = pf.print_fields(pl.DEFAULT_OPTIONS, sheet=False)
    assert [f.key for f in fields] == ["paper"]


def test_the_form_keeps_its_choices_for_next_time():
    chosen = []
    form = pf.print_form(chosen.append)
    form.apply({"paper": pl.A4, "spells": pf.FULL, "background": pf.WHITE})
    assert chosen == [pl.PrintOptions(pl.A4, True, False)]
    assert pf.saved_options() == chosen[0]
    # Printing a covenant keeps the paper, and the sheet's other choices.
    pf.print_form(chosen.append, sheet=False).apply({"paper": pl.LETTER})
    assert pf.saved_options() == pl.PrintOptions(pl.LETTER, True, False)


def test_unknown_saved_choices_fall_back_to_the_defaults():
    settings.update_settings(print_options={"paper": "Foolscap", "spells": 3})
    assert pf.saved_options() == pl.DEFAULT_OPTIONS
    settings.update_settings(print_options="nonsense")
    assert pf.saved_options() == pl.DEFAULT_OPTIONS
