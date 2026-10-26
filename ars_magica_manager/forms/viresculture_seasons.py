"""The season form's fields for Hermetic Viresculture's two seasons: the
Stirps' name, its Magic Might (or Lesser Enchantment Vis's level), any
other Stirpes worked on in the same season ("Name: Might; Name: Might")
and, Invigorating, its Form -- no UI in here. Vitalizing also shows the
season form's "Vis from" choice (PAYS_VIS). The rules and their pages are
rules.viresculture's (Legends of Hermes pp. 72-76); the seasons are
rules.season_work.viresculture's."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from ..arts import FORMS
from ..form_spec import ChoiceReads, DialogField
from ..models import SeasonPlan
from ..rules import viresculture as vc

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]

#: The seasons that pay vis, from the pool the form's "Vis from" names.
PAYS_VIS = (vc.VITALIZE,)

#: One other Stirps as typed: its name, then ":" (or a space) and its Might.
_ENTRY = re.compile(r"^(?P<name>.*?)\s*(?::\s*|\s+)(?P<might>\d+)$")


def parse_stirpes(text: str) -> dict[str, int]:
    """The other Stirpes typed as "Name: Might; Name: Might" (a line or a
    semicolon each); a name with no Might typed is kept with -1, which the
    season's checks report."""
    found: dict[str, int] = {}
    for part in re.split(r"[;\n]", text or ""):
        entry = part.strip()
        if not entry:
            continue
        match = _ENTRY.match(entry)
        if match is None or not match.group("name").strip():
            found[entry.rstrip(":").strip()] = -1
        else:
            found[match.group("name").strip()] = int(match.group("might"))
    return found


def stirpes_text(stirpes: dict[str, int]) -> str:
    """The other Stirpes as the form shows them."""
    return "; ".join(
        name if might < 0 else f"{name}: {might}" for name, might in stirpes.items()
    )


def fields(plan: SeasonPlan | None, activity_is: ActivityIs) -> list[DialogField]:
    """The Stirps worked on."""
    ours = plan is not None and plan.activity in (vc.VITALIZE, vc.INVIGORATE)
    return [
        DialogField(
            "stirps_name",
            "Stirps",
            "text",
            plan.title if plan and ours else "",
            placeholder="e.g. Rooster of Virtue",
            show_if=activity_is(vc.VITALIZE, vc.INVIGORATE),
        ),
        DialogField(
            "stirps_might",
            "Its Magic Might",
            "optint",
            plan.book_level if plan and ours else None,
            show_if=activity_is(vc.VITALIZE, vc.INVIGORATE),
            hint="Lesser Enchantment Vis: its effect's level (LoH p. 73).",
        ),
        DialogField(
            "more_stirpes",
            "Other Stirpes",
            "text",
            stirpes_text(plan.more_stirpes) if plan and ours else "",
            placeholder="e.g. Second rooster: 10; Hen of Virtue: 10",
            show_if=activity_is(vc.VITALIZE, vc.INVIGORATE),
            hint="Several in one season (Multiple Laboratory Activities, DE "
            "p. 264): Vitalizing, the Total must finish them all; Invigorating "
            "shares its Total among them, all of the one Form (LoH p. 75).",
        ),
        DialogField(
            "stirps_form",
            "Its Form",
            "select",
            (plan.form if plan and ours else "") or None,
            options=[(form, form) for form in FORMS],
            allow_blank=True,
            show_if=activity_is(vc.INVIGORATE),
            hint="Its Might's Form, or its vis's; Vim is its requisite.",
        ),
    ]


#: The plan's fields these seasons set from the form (as _SEASON_READS).
READS: ChoiceReads = (
    (
        (vc.VITALIZE, vc.INVIGORATE),
        lambda v: {
            "title": (v.get("stirps_name") or "").strip(),
            "book_level": v.get("stirps_might"),
            "form": v.get("stirps_form") or "",
            "more_stirpes": parse_stirpes(v.get("more_stirpes") or ""),
        },
    ),
)
