"""A Tribunal's treasury reckoned: an entry's amount in words, and what the
treasury holds by silver and each Art. Kept below the sheets and the
Tribunal packages, so both can reckon it."""

from __future__ import annotations

from .models import TreasuryEntry, Tribunal

#: Kinds of entry a Tribunal's customs add to the core's (a package's
#: treasury_kinds): a levy owed to the treasury, counted once paid as a
#: fine is; and a promissory note the Praeco issued against the
#: treasury's income, whose pawns leave it once the note is redeemed
#: (Against the Dark p. 19).
LEVY, NOTE = "levy", "note"


def pounds(amount: float) -> str:
    whole = int(amount) if float(amount).is_integer() else amount
    return f"{whole} pound" if whole in (1, -1) else f"{whole} pounds"


def pawns(amount: float, art: str) -> str:
    whole = int(amount) if float(amount).is_integer() else amount
    noun = "pawn" if whole in (1, -1) else "pawns"
    return f"{whole} {noun} of {art}"


def amount_text(entry: TreasuryEntry) -> str:
    """ "12 pounds", or "3 pawns of Vim" for vis."""
    return pawns(entry.amount, entry.art) if entry.art else pounds(entry.amount)


def balance(tribunal: Tribunal) -> dict[str, float]:
    """What the treasury holds, by "silver" and each Art: its silver and
    vis, with fines and levies paid in, loans not yet repaid out, and
    promissory notes out once redeemed."""
    held: dict[str, float] = {}
    for entry in tribunal.treasury:
        key = entry.art or "silver"
        if entry.kind in ("vis", "silver"):
            sign = 1
        elif entry.kind in ("fine", LEVY):
            sign = 1 if entry.paid else 0
        elif entry.kind == NOTE:
            sign = -1 if entry.paid else 0
        else:
            sign = 0 if entry.paid else -1
        held[key] = held.get(key, 0) + sign * entry.amount
    return held
