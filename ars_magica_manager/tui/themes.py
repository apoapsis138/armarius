"""Scriptorum themes: an illuminated-manuscript palette (light) and its
after-hours counterpart, a single candle in a stone scriptorium (dark).

Registered on the app in app.py; switch between them (and the Textual
built-ins) via the command palette (ctrl+p).

Besides Textual's base colours, the app's CSS uses its own variables, named
for what a colour is *for*: each Scriptorum theme sets them,
and `app_variable_defaults` derives them for any other theme.
"""

from __future__ import annotations

from textual.theme import Theme

#: The light theme's own variables (see the module docstring).
SCRIPTORUM_VARIABLES = {
    # A text field is a well a shade deeper than the parchment, as if pressed
    # into the page, lifting toward the page colour while it's typed in.
    # Not near-white, which breaks the parchment feel.
    "field-background": "#E3D2B1",
    "field-background-focus": "#F6ECD8",
    # Headings (an entity's name, dialog titles, the active
    # tab), labels that recede so values stand out (6:1 on the surface,
    # 4.9:1 on a panel), and the faint rule over each section. Headings
    # share cinnabar with errors, not lapis; a
    # problem also leads with a glyph.
    "heading": "#8B0000",
    "label": "#5F4F44",
    "rule": "#C9B48A",
    # Placeholder text in a field (4.6:1 on a well; Textual's
    # $text-disabled was 2.6:1).
    "placeholder": "#685849",
    # Textual's own variables. Warnings in burnt umber, apart from the gold
    # accent (5.1:1 on a panel; the gold was 4.1:1).
    "text-warning": "#7A4206",
    "text-accent": "#6B4E06",  # gold text, 4.9:1 on a panel (was 4.1:1)
    # The scrollbar was the same tan as the details panel ($panel).
    "scrollbar": "#C9B48A",
    "scrollbar-hover": "#B39C6E",
    "scrollbar-active": "#8C7448",
}

#: The dark theme's: a field is an inkwell, darker than the surface, and warms
#: to candlelight while it's typed in.
SCRIPTORUM_DARK_VARIABLES = {
    "field-background": "#0B0C10",
    "field-background-focus": "#2B2612",
    "heading": "#FCD34D",
    "label": "#A39A84",  # 5.8:1 on the surface, 5.1:1 on a panel
    "rule": "#3A4150",
    "placeholder": "#9A937F",  # 6.4:1 on a well, 4.9:1 on a lifted one
    # Warnings in orange, apart from the amber primary and gold accent;
    # errors a lighter red (5.1:1 on a panel; the crimson was 4.7:1).
    "text-warning": "#F0954A",
    "text-error": "#F87171",
    "scrollbar": "#3A4150",
    "scrollbar-hover": "#4A5366",
    "scrollbar-active": "#D4AF37",
}


def app_variable_defaults(theme: Theme) -> dict[str, str]:
    """The app's own variables for a theme that doesn't set them (Textual's
    built-ins), derived from its colour system. Without a value the app's
    CSS doesn't parse under that theme."""
    colors = theme.to_color_system().generate()
    return {
        "field-background": colors["surface-darken-1"],
        "field-background-focus": colors["surface-lighten-1"],
        "heading": colors["text-primary"],
        "label": colors["text-muted"],
        "rule": colors["panel"],
        "placeholder": colors["text-muted"],
    }


#: Aged parchment, iron gall ink, cinnabar rubrics, gold leaf.
SCRIPTORUM = Theme(
    name="scriptorum",
    primary="#8B0000",  # Cinnabar Red -- headers, active tab, selection
    secondary="#5C4033",  # Walnut Wash -- metadata, secondary text
    accent="#B8860B",  # Burnished Gold -- borders, focus, highlights
    foreground="#2C221E",  # Iron Gall Ink -- body text
    background="#F4EBE1",  # Aged Parchment
    surface="#EDE0CB",
    panel="#E0CBA0",  # a visibly darker card tone, for details panels
    success="#4A6741",  # muted moss green
    warning="#B5651D",  # Burnt Sienna, apart from the gold accent
    error="#8B0000",
    dark=False,
    variables=SCRIPTORUM_VARIABLES,
)

#: Midnight stone, a single candle's amber light, sage and crimson accents.
SCRIPTORUM_DARK = Theme(
    name="scriptorum-dark",
    primary="#FCD34D",  # Candlelight Amber -- headers, active tab, selection
    secondary="#6B9080",  # brightened Velvet Sage -- secondary accents
    accent="#D4AF37",  # gold -- borders, focus, ties back to the light theme
    foreground="#D9CBA3",  # soft parchment cream -- body text (not full amber)
    background="#15171C",  # Midnight Charcoal
    surface="#1D2027",
    panel="#262B35",  # a visibly lighter card tone, for details panels
    success="#6FA287",  # brightened sage, legible against charcoal
    warning="#F0954A",  # orange, apart from the amber primary and gold accent
    error="#DC2626",  # brightened crimson, legible against charcoal
    dark=True,
    variables=SCRIPTORUM_DARK_VARIABLES,
)


#: The colour each heraldic tincture (arms.TINCTURES) is painted in, the
#: same in every theme: arms are the bearer's, not the theme's.
TINCTURES: dict[str, str] = {
    "Or": "#d4a72c",
    "Argent": "#f1ede2",
    "Gules": "#b8282e",
    "Azure": "#2556a8",
    "Vert": "#2e8540",
    "Sable": "#262322",
    "Purpure": "#6b3f9e",
    # A fur is painted as its ground and spots (arms.FURS); this is the
    # ground, for anything that shows one colour for it.
    "Ermine": "#f1ede2",
}
