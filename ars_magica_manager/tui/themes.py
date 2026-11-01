"""The Scriptorum themes, from `style.py`. Registered on the app in
app.py; switch between them (and the Textual built-ins) via the command
palette (ctrl+p).
"""

from ..style.palettes import TINCTURES
from .style import (
    SCRIPTORUM,
    SCRIPTORUM_DARK,
    app_variable_defaults,
)

#: What the app's other modules take from style.py through here.
__all__ = [
    "SCRIPTORUM",
    "SCRIPTORUM_DARK",
    "TINCTURES",
    "app_variable_defaults",
]
