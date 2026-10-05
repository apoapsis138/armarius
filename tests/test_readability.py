"""STORY-1011: text fields are wells with a background of their own, so a
form shows where to type; the field being typed in lifts. The app's own
theme variables resolve under every theme, Textual's built-ins included."""

import pytest
from textual.color import Color
from textual.widgets import Input

from ars_magica_manager import themes
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.screens.fields import DialogField, FieldsDialog


def _form() -> FieldsDialog:
    return FieldsDialog(
        "Edit",
        [
            DialogField("name", "Name", "text", "Corvinus"),
            DialogField("age", "Age", "int", 25),
            DialogField("notes", "Notes", "text", ""),
        ],
    )


def test_both_scriptorum_themes_set_every_app_variable():
    names = set(themes.app_variable_defaults(themes.SCRIPTORUM))
    assert set(themes.SCRIPTORUM.variables) >= names
    assert set(themes.SCRIPTORUM_DARK.variables) >= names


async def test_every_theme_resolves_the_app_variables():
    """Switching to a built-in theme (which doesn't set the app's
    variables) must not fail to parse the app's CSS."""
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        for theme in sorted(app.available_themes):
            app.theme = theme
            await pilot.pause()
            for name in themes.app_variable_defaults(themes.SCRIPTORUM):
                assert app.theme_variables.get(name), (theme, name)


@pytest.mark.parametrize("theme", ["scriptorum", "scriptorum-dark"])
async def test_a_field_is_a_well_on_its_dialog(theme):
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.theme = theme
        app.push_screen(_form())
        await pilot.pause()
        dialog = app.screen.query_one("#fields-dialog")
        name = app.screen.query_one("#fld-name", Input)
        notes = app.screen.query_one("#fld-notes", Input)
        well = Color.parse(app.theme_variables["field-background"])
        lifted = Color.parse(app.theme_variables["field-background-focus"])
        assert dialog.styles.background != well
        name.focus()
        await pilot.pause()
        assert name.styles.background == lifted
        assert notes.styles.background == well


async def test_number_fields_are_short_wells():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.push_screen(_form())
        await pilot.pause()
        age = app.screen.query_one("#fld-age", Input)
        name = app.screen.query_one("#fld-name", Input)
        assert age.region.width == 10
        assert name.region.width > 10


# -- STORY-1012: a ladder of emphasis -------------------------------------


def test_aligned_labels_recede_and_values_stay_plain():
    from ars_magica_manager.markup import aligned

    text = aligned([("Age", "25"), ("Covenant", "Dammerstein")])
    assert text.splitlines() == [
        "[$label]Age:     [/] 25",
        "[$label]Covenant:[/] Dammerstein",
    ]


def test_inherited_values_are_italic_and_quiet():
    from ars_magica_manager.markup import inherited

    assert inherited("1220") == "[i $label]1220[/]"


async def test_dialog_titles_are_ruled_headings():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.theme = "scriptorum"
        app.push_screen(_form())
        await pilot.pause()
        title = app.screen.query_one("#fields-title")
        assert "dialog-title" in title.classes
        assert title.styles.text_style.bold
        assert title.styles.color == Color.parse(app.theme_variables["heading"])
        assert title.styles.border_bottom[0] == "solid"


# -- STORY-1013: contrast ---------------------------------------------------

#: Text tokens and the backgrounds they're shown on.
_TEXT = (
    "foreground",
    "text-muted",
    "label",
    "heading",
    "text-primary",
    "text-warning",
    "text-error",
    "text-success",
    "text-accent",
)
_GROUNDS = (
    "background",
    "surface",
    "panel",
    "field-background",
    "field-background-focus",
)


def _luminance(color: Color) -> float:
    def channel(value: int) -> float:
        value /= 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    return (
        0.2126 * channel(color.r)
        + 0.7152 * channel(color.g)
        + 0.0722 * channel(color.b)
    )


def _contrast(text: str, ground: str) -> float:
    """WCAG contrast of theme value `text` (a colour, or Textual's "auto
    60%") drawn on colour `ground`."""
    back = Color.parse(ground)
    if text.startswith("auto"):
        alpha = float(text.split()[1].rstrip("%")) / 100
        fore = back.blend(back.get_contrast_text(1.0), alpha)
    else:
        colour = Color.parse(text)
        fore = back.blend(colour, colour.a) if colour.a < 1 else colour
    high, low = sorted((_luminance(fore), _luminance(back)), reverse=True)
    return (high + 0.05) / (low + 0.05)


@pytest.mark.parametrize("theme", ["scriptorum", "scriptorum-dark"])
async def test_text_meets_wcag_aa_on_every_background(theme):
    """Every text colour reads at 4.5:1 or better on every background it can
    sit on; a placeholder only ever sits in a field."""
    app = ArsMagicaManagerApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        app.theme = theme
        await pilot.pause()
        variables = app.theme_variables
        failures = [
            f"{text} on {ground}: {_contrast(variables[text], variables[ground]):.2f}"
            for text in _TEXT
            for ground in _GROUNDS
            if _contrast(variables[text], variables[ground]) < 4.5
        ]
        failures += [
            f"placeholder on {ground}"
            for ground in ("field-background", "field-background-focus")
            if _contrast(variables["placeholder"], variables[ground]) < 4.5
        ]
        assert failures == []


def test_warnings_are_apart_from_the_accent_and_primary():
    for theme in (themes.SCRIPTORUM, themes.SCRIPTORUM_DARK):
        assert theme.warning not in (theme.accent, theme.primary)


@pytest.mark.parametrize("theme", ["scriptorum", "scriptorum-dark"])
async def test_a_focused_entity_name_stays_readable(theme):
    """The entity's name is a heading, but focused it's on the $primary
    cursor bar -- in the light theme the same cinnabar as headings."""
    from textual.containers import Vertical
    from textual.widgets._collapsible import CollapsibleTitle

    from ars_magica_manager.screens.widgets import FocusableSection

    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.theme = theme
        await pilot.pause()
        section = FocusableSection(title="Corvinus")
        await app.screen.mount(Vertical(section, id="char-top-panel"))
        title = section.query_one(CollapsibleTitle)
        title.focus()
        await pilot.pause()
        styles = title.styles
        assert styles.color != Color.parse(app.theme_variables["heading"])
        # "auto" text is black or white, whichever reads on the background
        colour = (
            styles.background.get_contrast_text(styles.color.a)
            if styles.auto_color
            else styles.color
        )
        assert _contrast(colour.hex, styles.background.hex) >= 4.5


# -- STORY-1014: scores in columns ------------------------------------------


def test_ability_scores_and_xp_line_up_in_columns():
    from support import strip_markup

    from ars_magica_manager import sheet_text
    from ars_magica_manager.models import Ability, VirtueFlawInstance
    from ars_magica_manager.rules.xp import ability_xp

    abilities = [
        Ability(name="Brawl", category="Martial", xp=50),
        Ability(name="Charm", category="General", xp=ability_xp(2)),
        Ability(
            name="Magic Theory",
            category="Arcane",
            xp=ability_xp(10),
            specialty="Experimentation",
        ),
        Ability(name="[Odd] Lore", category="General", xp=5),
    ]
    puissant = [
        VirtueFlawInstance(vf_id="vf_puissant_ability", params={"ability": "Brawl"})
    ]
    rows = sheet_text.ability_rows(abilities, puissant)
    plain = [strip_markup(label).replace(r"\[", "[") for _, label in rows]
    header = plain[0]
    scored = [line for (index, _), line in zip(rows, plain) if index is not None]
    # each score's last digit under the end of "Score"; each xp ends under
    # "XP" -- shown, a row has a 2-column marker ("○ ") a header doesn't
    score_end = header.index("Score") + len("Score") - 2
    xp_end = header.index("XP") + len("XP") - 2
    for line in scored:
        assert line[score_end - 1].isdigit() and line[score_end] in " ", line
        assert len(line.rstrip()) == xp_end, line
    assert "4 (6)" in next(line for line in scored if line.startswith("Brawl"))
    # only the first header names the columns
    headers = [line for (index, _), line in zip(rows, plain) if index is None]
    assert all("Score" not in line for line in headers[1:])


# -- STORY-1015: glyphs for problems and to-dos -----------------------------


def test_problems_and_todos_lead_with_their_glyph_and_colour():
    from ars_magica_manager.markup import problem, todo

    assert problem("Over capacity by 1.") == "[$text-error]✘ Over capacity by 1.[/]"
    assert todo("1 point to allocate") == "[$text-warning]☞ 1 point to allocate[/]"
