"""Print to PDF's options (forms/printing.py): its fields, what they choose,
that the last choices are kept in the settings, and that only a reader of
everything is asked who the copy is for."""

from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import print_layout as pl
from ars_magica_manager import settings, viewing
from ars_magica_manager.forms import printing as pf
from ars_magica_manager.models import Player


def test_the_defaults_are_letter_and_parchment():
    assert pf.saved_options() == pl.PrintOptions(pl.LETTER, True)
    fields = pf.print_fields(pf.saved_options())
    assert [(f.key, f.value) for f in fields] == [
        ("sheet", pl.FULL_RECORD),
        ("paper", pl.LETTER),
        ("theme", pl.HOUSE_COLOURS),
        ("background", pf.TEXTURED),
    ]


def test_a_record_that_is_not_a_character_is_asked_paper_theme_and_background():
    fields = pf.print_fields(pl.DEFAULT_OPTIONS, character=False)
    assert [f.key for f in fields] == ["paper", "theme", "background"]


def test_the_theme_is_kept_and_an_unknown_one_falls_back():
    chosen = []
    pf.print_form(chosen.append).apply({"theme": "Tremere"})
    assert chosen[0].theme == "Tremere"
    assert pf.saved_options().theme == "Tremere"
    settings.update_settings(print_options={"theme": "Nowhere"})
    assert pf.saved_options().theme == pl.HOUSE_COLOURS


def test_the_form_keeps_its_choices_for_next_time():
    chosen = []
    form = pf.print_form(chosen.append)
    form.apply({"paper": pl.A4, "background": pf.WHITE, "sheet": "play"})
    assert chosen == [pl.PrintOptions(pl.A4, False, sheet=pl.PLAY_SHEET)]
    assert pf.saved_options() == chosen[0]
    # Printing a covenant keeps its paper and background, and leaves the
    # character's own sheet.
    pf.print_form(chosen.append, character=False).apply(
        {"paper": pl.LETTER, "background": pf.WHITE}
    )
    assert pf.saved_options() == pl.PrintOptions(pl.LETTER, False, sheet=pl.PLAY_SHEET)


def test_unknown_saved_choices_fall_back_to_the_defaults():
    settings.update_settings(
        print_options={"paper": "Foolscap", "spells": 3, "sheet": "poster"}
    )
    assert pf.saved_options() == pl.DEFAULT_OPTIONS
    settings.update_settings(print_options="nonsense")
    assert pf.saved_options() == pl.DEFAULT_OPTIONS


# ---------------------------------------------------------------- the copy


def test_the_copy_is_asked_first_and_starts_at_the_player_copy():
    fields = pf.print_fields(pl.DEFAULT_OPTIONS, asks_copy=True)
    assert [f.key for f in fields][:2] == ["copy", "sheet"]
    assert fields[0].value == pl.PLAYER_COPY


def test_the_copy_is_never_kept_for_next_time():
    chosen = []
    pf.print_form(chosen.append, asks_copy=True).apply({"copy": pl.STORYGUIDE_COPY})
    assert chosen[0].copy == pl.STORYGUIDE_COPY
    assert pf.saved_options().copy == pl.PLAYER_COPY


def test_a_form_that_did_not_ask_never_gives_a_storyguide_copy():
    chosen = []
    pf.print_form(chosen.append).apply({"copy": pl.STORYGUIDE_COPY})
    assert chosen[0].copy == pl.PLAYER_COPY


def test_only_a_reader_of_everything_is_offered_the_copy():
    saga = _sample_saga_with_covenant()
    player = Player(id="pat", name="Pat")
    guide = Player(id="sam", name="Sam", role=viewing.STORYGUIDE)
    saga.players += [player, guide]
    assert pf.offers_copy(saga, viewing.STORYGUIDE_VIEWER)
    assert pf.offers_copy(saga, viewing.viewer_for(guide))
    assert not pf.offers_copy(saga, viewing.viewer_for(player))
    assert not pf.offers_copy(saga, viewing.TABLE_VIEWER)
    # Another storyguide runs a record: the host no longer reads it all.
    viewing.assign(saga.characters[0], guide.id)
    assert not pf.offers_copy(saga, viewing.STORYGUIDE_VIEWER)
