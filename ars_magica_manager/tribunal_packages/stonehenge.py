"""The Stonehenge Tribunal's customs (Heirs to Merlin: The Stonehenge
Tribunal, a Fourth Edition book): since the void meeting of 1200 the
Tribunal meets a year behind the rest of the Order (1201, 1208, 1215,
1222), always at Blackthorn; each meeting closes and, at the youngest
magus's request, opens again, so one gathering can hold two Tribunals;
its Quaesitores don't vote but have an unGifted Redcap cast their sigils;
and unGifted Redcaps don't count toward the quorum. None of it needs a
list of its own, so the package adds nothing to the sheet but its
note."""

from __future__ import annotations

from . import TribunalPackage, register

STONEHENGE = TribunalPackage(
    "stonehenge",
    "Stonehenge",
    customs="The meeting a year late",
    book="HtM",
    about=(
        "Since 1201 the Tribunal meets a year behind the rest of the Order, "
        "always at Blackthorn. A meeting may close and open again at the "
        "youngest magus's request, holding two Tribunals; the Quaesitores "
        "have an unGifted Redcap cast their sigils, and unGifted Redcaps "
        "don't count toward the quorum."
    ),
)

register(STONEHENGE)
