"""The Novgorod Tribunal's customs (The Dragon and the Bear: The
Novgorod Tribunal, a Fourth Edition book): the Tribunal's council holds
formal authority over the settlement of every new covenant in Slavic
lands, and the Royal Embargo forbids any member to reveal himself to the
Russian royal house, and since to the Polish one. Both are rulings of
its Peripheral Code, so the package adds nothing to the sheet but its
note."""

from __future__ import annotations

from . import TribunalPackage, register

NOVGOROD = TribunalPackage(
    "novgorod",
    "Novgorod",
    customs="The Royal Embargo",
    book="D&B",
    about=(
        "Its council decides where any new covenant in Slavic lands may "
        "settle, and the Royal Embargo bars every member from revealing "
        "himself to the Russian and Polish royal houses. It meets every "
        "seven years at Three Lakes."
    ),
)

register(NOVGOROD)
