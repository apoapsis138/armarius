"""A character's religion: one of a short list, chosen on Biographical
Detail. A blank religion counts as Christian, as most of Mythic Europe is
(rules.faiths reads it so)."""

from __future__ import annotations

CHRISTIAN = "Christian"
MUSLIM = "Muslim"
JEWISH = "Jewish"
MAZDEAN = "Mazdean"
PAGAN = "Pagan"
OTHER = "Other"

#: The religions a character may hold, in the order the form lists them.
RELIGIONS = (CHRISTIAN, MUSLIM, JEWISH, MAZDEAN, PAGAN, OTHER)

#: Words in a religion typed as free text, and the religion each means.
_WORDS: tuple[tuple[str, str], ...] = (
    ("christ", CHRISTIAN),
    ("catholic", CHRISTIAN),
    ("orthodox", CHRISTIAN),
    ("cathar", CHRISTIAN),
    ("muslim", MUSLIM),
    ("islam", MUSLIM),
    ("moslem", MUSLIM),
    ("jew", JEWISH),
    ("judai", JEWISH),
    ("hebrew", JEWISH),
    ("mazdean", MAZDEAN),
    ("zoroastr", MAZDEAN),
    ("magian", MAZDEAN),
    ("pagan", PAGAN),
    ("heathen", PAGAN),
    ("norse", PAGAN),
    ("old gods", PAGAN),
)


def religion_from_text(text: str) -> str:
    """One of RELIGIONS for a religion saved as free text before it was a
    list ("Roman Catholic" is Christian); blank stays blank, and words the
    list doesn't know are Other."""
    plain = text.strip()
    if not plain or plain in RELIGIONS:
        return plain
    folded = plain.casefold()
    return next((faith for word, faith in _WORDS if word in folded), OTHER)
