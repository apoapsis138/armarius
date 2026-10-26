"""A work of art's choices, kept on the season plan that makes it (Art &
Academe, Chapter Eight: Artists, pp. 123-135): what kind of piece it is,
the bonuses and risks the artist takes, and a maestro's magic instilled
in it. The rules that read them are rules.artistry's."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import REALMS, known_fields

#: A piece's base time to make (A&A p. 124): a season's piece, two small
#: pieces in a season, a year's, a castle or church (a year per Size
#: point) or a cathedral (ten years per Size point).
ARTWORK_BASES: tuple[str, ...] = ("season", "pair", "year", "years", "decades")
#: Life-Linked Art's self-inflicted wound ("" for none).
ART_WOUNDS: tuple[str, ...] = ("", "Light", "Medium", "Heavy")


@dataclass
class ArtworkPlan:
    """What a Create a Work of Art season chose for the piece."""

    base: str = "season"
    #: A castle's, church's or cathedral's Size (bases "years", "decades").
    size: int = 1
    assistants: int = 0
    #: Twice the time for +1; overtime +1 and an Aging roll when done;
    #: a third of Artes Liberales for a piece using a liberal art; half
    #: the time for half the Aesthetic Quality; experimentation.
    double_time: bool = False
    overtime: bool = False
    liberal_arts: bool = False
    rushed: bool = False
    experiment: bool = False
    #: Might a muse sacrificed to the piece (+1 per 5).
    muse_might: int = 0
    wound: str = ""
    #: The realm a maestro or legendary artist is aligned with ("" none),
    #: and the aura where he works (its strength and realm).
    realm: str = ""
    aura: int = 0
    aura_realm: str = ""
    #: A maestro's spell-like effect instilled while he makes it: its
    #: final level (0: none).
    instill_level: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtworkPlan:
        found = cls(**known_fields(cls, data))
        if found.base not in ARTWORK_BASES:
            raise ValueError(f"A work of art's base time {found.base!r} is unknown.")
        if found.wound not in ART_WOUNDS:
            raise ValueError(f"A work of art's wound {found.wound!r} is unknown.")
        for realm in (found.realm, found.aura_realm):
            if realm and realm not in REALMS:
                raise ValueError(f"A work of art's realm {realm!r} is unknown.")
        for name in ("size", "assistants", "muse_might", "aura", "instill_level"):
            value = getattr(found, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"A work of art's {name} must be a number: {value!r}")
        return found
