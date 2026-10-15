"""The Provençal Tribunal's customs (Faith & Flame: The Provençal
Tribunal): any magus may found a covenant, with no leave from the
Tribunal. A rule, not data, so the package adds nothing to the sheet
but its note."""

from __future__ import annotations

from . import TribunalPackage, register

PROVENCE = TribunalPackage(
    "provence",
    "Provence",
    customs="Open founding",
    book="F&F",
    about="Any magus may found a covenant, with no leave from the Tribunal.",
)

register(PROVENCE)
