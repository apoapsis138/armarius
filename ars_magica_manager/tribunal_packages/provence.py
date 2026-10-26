"""The Provençal Tribunal's customs (Faith & Flame: The Provençal
Tribunal): any magus may found a covenant, with no leave from the
Tribunal, and residency in the Tribunal is kept by attending its
meetings (p. 22).

Residency (p. 22; the Definitive Edition p. 23 lets each regional
Tribunal set its membership freely): a magus is a resident who attended
one of its last three meetings, or was granted residency by a vote at his
first, or registered on arriving between meetings (with the Redcaps and
the Praeco, or his nearest neighbour). One Gauntleted in the Tribunal is
a resident until three meetings pass without him. A resident stays one
until he claims residency in another Tribunal or votes at its meeting,
and must register his departure first, or breaks the Peripheral Code.

Kept in the package's data: "meetings", the years whose roll call the
residency step recorded; "attended", {magus id: [years]}; "registered",
{magus id: year granted}; "departed", {magus id: {"year", "breach"}}.
The step itself is in provence_meeting.py."""

from __future__ import annotations

from typing import Any

from ..models import Character, Saga, Tribunal
from ..rules.rhine_ranks import gauntlet_year
from . import TribunalPackage, data, register

KEY = "provence"

#: How many of the latest meetings a magus must have attended.
LAST_MEETINGS = 3


def _dict(tribunal: Tribunal, name: str) -> dict[str, Any]:
    found = data(tribunal, KEY).setdefault(name, {})
    if not isinstance(found, dict):
        raise ValueError(f"The Tribunal's {name} should be a mapping, not {found!r}.")
    return found


def meetings(tribunal: Tribunal) -> list[int]:
    """The years whose roll call is recorded, in order."""
    found = data(tribunal, KEY).setdefault("meetings", [])
    if not isinstance(found, list):
        raise ValueError(f"The Tribunal's meetings should be a list, not {found!r}.")
    return found


def attended(tribunal: Tribunal) -> dict[str, list[int]]:
    """The meetings each magus attended, by magus id."""
    return _dict(tribunal, "attended")


def registered(tribunal: Tribunal) -> dict[str, int]:
    """The year each magus was granted residency or registered, by id."""
    return _dict(tribunal, "registered")


def departed(tribunal: Tribunal) -> dict[str, dict[str, Any]]:
    """Each magus who left the Tribunal: the year, and whether he voted
    elsewhere without registering his departure (a breach)."""
    return _dict(tribunal, "departed")


def residency(tribunal: Tribunal, magus: Character) -> tuple[bool, str]:
    """Whether `magus` is a resident of the Tribunal, and why."""
    gone = departed(tribunal).get(magus.id)
    if gone is not None:
        if gone.get("breach"):
            return False, (
                f"voted at another Tribunal in {gone.get('year')} without "
                "registering his departure"
            )
        return False, f"registered his departure in {gone.get('year')}"
    since = registered(tribunal).get(magus.id)
    if since is not None:
        return True, f"registered or granted by vote in {since}"
    held = meetings(tribunal)
    latest = held[-LAST_MEETINGS:]
    seen = [y for y in attended(tribunal).get(magus.id, []) if y in latest]
    if seen:
        return True, f"attended the meeting of {max(seen)}"
    passed = gauntlet_year(magus)
    if passed is not None and sum(1 for y in held if y > passed) < LAST_MEETINGS:
        return True, f"Gauntleted in the Tribunal in {passed}"
    if len(held) < LAST_MEETINGS:
        return True, "presumed: fewer than three meetings are recorded"
    return False, "absent from the last three meetings"


def magus_facts(
    _saga: Saga, tribunal: Tribunal, magus: Character
) -> list[tuple[str, str]]:
    """The magus's residency, for his sheet."""
    resident, why = residency(tribunal, magus)
    return [("Residency", f"{'Resident' if resident else 'Not resident'}: {why}")]


PROVENCE = TribunalPackage(
    KEY,
    "Provence",
    customs="Open founding",
    book="F&F",
    meeting_steps=("residency",),
    magus_facts=magus_facts,
    about="Any magus may found a covenant, with no leave from the Tribunal. "
    "A magus is a resident who attended one of its last three meetings or "
    "was granted residency by vote at his first.",
)

register(PROVENCE)
