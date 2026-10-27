"""The season form's fields for copying books by magic -- no UI in here:
the book copied, the copying device used if any, how many copies, and
whether they are bound by magic.
The rules and their pages are rules.tme_books's (Transforming Mythic
Europe pp. 98-103); the season is rules.season_work.transforming's."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..form_spec import ChoiceReads, DialogField
from ..markup import escape
from ..models import Character, Saga, SeasonPlan
from ..rules import library
from ..rules import tme_books as tb
from ..rules.season_work import transforming as tw

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]


def fields(
    saga: Saga, character: Character, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """The book copied, the device copying it, the copies made, and
    binding them."""
    ours = plan is not None and plan.activity == tw.COPY_BY_MAGIC
    shown = activity_is(tw.COPY_BY_MAGIC)
    return [
        DialogField(
            "magic_copy_book_id",
            "Book copied",
            "select",
            plan.book_id if plan and ours else None,
            options=[
                (escape(b.name), b.id)
                for b in saga.books
                if b.type in tw.COPYABLE and library.can_read(saga, character, b)
            ],
            allow_blank=True,
            show_if=shown,
            hint=f"Finesse Total {tb.finesse_total(character)} (Perception + "
            "Finesse): 11 at Ease Factor 12 keeps the Quality (TME p. 100).",
        ),
        DialogField(
            "magic_copy_device",
            "Copying device",
            "select",
            plan.device_id if plan and ours else None,
            options=[(escape(d.name), d.id) for d in tw.copy_devices(saga, character)],
            allow_blank=True,
            placeholder="(cast the spells)",
            show_if=shown,
            hint=f"One with {tb.DEVICE_COPY_EFFECT} instilled: a book a use, so "
            "its uses a day cap the copies (TME p. 102).",
        ),
        DialogField(
            "magic_copies",
            "Copies",
            "optint",
            plan.book_level if plan and ours else None,
            placeholder="(one)",
            show_if=shown,
        ),
        DialogField(
            "magic_bind",
            f"Bind them with {tb.BINDING_SPELL}",
            "check",
            bool(plan.quick) if plan and ours else False,
            show_if=shown,
            hint="Needs the spell (or the device's own) and a Finesse Total of "
            "6; unbound copies are loose sheets (TME pp. 101-103).",
        ),
    ]


#: The plan's fields this season sets from the form (as _SEASON_READS).
READS: ChoiceReads = (
    (
        (tw.COPY_BY_MAGIC,),
        lambda v: {
            "book_id": v.get("magic_copy_book_id"),
            "book_level": v.get("magic_copies"),
            "quick": bool(v.get("magic_bind")),
            "device_id": v.get("magic_copy_device"),
        },
    ),
)
