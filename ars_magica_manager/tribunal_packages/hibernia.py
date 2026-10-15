"""The Hibernian Tribunal (The Contested Isle: The Hibernian Tribunal):
the core rules, with its customs noted. It keeps no data of its own
yet."""

from __future__ import annotations

from . import TribunalPackage, register

HIBERNIA = TribunalPackage(
    "hibernia",
    "Hibernia",
    customs="Notes",
    book="TCI",
    about="The core rules, with its customs noted: it meets at the Hill of "
    "Tara, the supernatural ambassadors vote, and in certamen the "
    "aggressor picks the Technique and the defender the Form.",
)

register(HIBERNIA)
