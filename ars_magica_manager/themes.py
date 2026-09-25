"""Scriptorum themes: an illuminated-manuscript palette (light) and its
after-hours counterpart, a single candle in a stone scriptorium (dark).

Registered on the app in app.py; switch between them (and the Textual
built-ins) via the command palette (ctrl+p).
"""

from __future__ import annotations

from textual.theme import Theme

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
    warning="#B8860B",
    error="#8B0000",
    dark=False,
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
    warning="#D4AF37",
    error="#DC2626",  # brightened crimson, legible against charcoal
    dark=True,
)
