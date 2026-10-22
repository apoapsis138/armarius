"""What experimenting left on a creation, as both front-ends show it
(markup): a spell's, an instilled effect's, a bond power's, a familiar's
bond's or a Longevity Ritual's experimental effects."""

from __future__ import annotations

from collections.abc import Sequence

from .markup import escape
from .models import ExperimentalEffect
from .rules import experiment


def effect_lines(
    effects: Sequence[ExperimentalEffect], heading: str = "Experimental effects"
) -> list[str]:
    """A blank line, the heading, and each effect on its own line (none
    without effects); a fatal flaw is marked."""
    if not effects:
        return []
    return ["", f"[b]{escape(heading)}[/]:"] + [
        f"  {'[b]Fatal flaw[/] ' if e.fatal else ''}{escape(experiment.describe(e))}"
        for e in effects
    ]
