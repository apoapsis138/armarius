"""The Levant Tribunal's customs (Blood and Sand: The Levant Tribunal):
the Treaty of Baghdad, which keeps its magi out of Crusade and jihad and
must be renewed every ten years. Renewal is an ordinary motion on the
docket, whose ruling the troupe gives a term ending at the last meeting
before the Treaty lapses, so the package adds nothing to the sheet but
its note."""

from __future__ import annotations

from . import TribunalPackage, register

LEVANT = TribunalPackage(
    "levant",
    "Levant",
    customs="The Treaty of Baghdad",
    book="B&S",
    about=(
        "The Treaty of Baghdad bars the Tribunal's magi from Crusade and "
        "jihad, and is renewed every ten years by a vote of the meeting; "
        "a quaesitor of House Guernicus always presides, and the Tribunal "
        "meets every seven years at Domus Pacis."
    ),
)

register(LEVANT)
