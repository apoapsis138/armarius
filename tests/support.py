"""Helpers shared by several test modules (fixtures live in conftest.py)."""

import re


def strip_markup(markup: str) -> str:
    """`markup` with simple tags like [b], [dim] and [/] removed -- enough to
    check the words and column alignment of a panel's text."""
    return re.sub(r"\[/?[a-z]*\]", "", markup)


async def wait_until(pilot, condition, timeout: float = 2.0, interval: float = 0.02):
    """Poll `condition()` until it's truthy or `timeout` seconds pass, and
    return its last value.

    A bare `pilot.pause()` (wait-for-idle) has occasionally not been enough
    for a heavy sheet view to finish mounting, or a dialog's result callback
    to land, under load; a fixed extra delay only makes that less likely.
    Polling for the actual condition is fast when things are quick and still
    correct when they aren't.
    """
    elapsed = 0.0
    while not condition() and elapsed < timeout:
        await pilot.pause(interval)
        elapsed += interval
    return condition()
