"""The Scriptorum themes, from armarius_style. Registered on the app in
app.py; switch between them (and the Textual built-ins) via the command
palette (ctrl+p).
"""

from armarius_style.palettes import TINCTURES
from armarius_style.terminal import (
    SCRIPTORUM,
    SCRIPTORUM_DARK,
    app_variable_defaults,
)

#: What the app's other modules take from armarius_style through here.
__all__ = [
    "SCRIPTORUM",
    "SCRIPTORUM_DARK",
    "TINCTURES",
    "app_variable_defaults",
]
