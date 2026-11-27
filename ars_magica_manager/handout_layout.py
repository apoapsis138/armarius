"""A written Handout laid on its Stationery (ADR 0021): what each
front-end draws, whether a storyguide's Preview or a player's copy.

`lay_out` reads the text into blocks through the one parser
(handout_markup.blocks) and sets each on the page: where it stands
(left, centred, right), the illuminated initial taken off the front of
an initial's paragraph, and each placed picture named. The Stationery
says how its page is made: how tall for its width, its margins, where
the title goes, its edge, whether it is sealed and how often it was
folded. Colours, paper and ornaments are each front-end's own look (ADR
0008): the desktop draws the page from gui/style, the terminal reads it
as lines under the Stationery's name.

Like the blocks, a laid-out Handout never holds a file name or an
address: a placed picture is its number among the Handout's own and the
name it is shown by. Where a picture's file is on this computer is the
storyguide's alone (`Preview`).

Pattern: Bridge, as ADR 0008 splits the look: `Laid` is the one
abstraction, and each front-end's drawing of it an implementation, so a
new Stationery is a row of STATIONERY and a new front-end one more
drawing, neither touching the other."""

from __future__ import annotations

import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from . import handout_markup as hm
from .markup import TAG
from .models import PROCLAMATION, SEALED_LETTER, VELLUM

#: Where a block stands on the page.
LEFT, CENTRE, RIGHT = "left", "centre", "right"

#: Where a Stationery sets the Handout's title: as a heading over the
#: text, in a banner across the head of the page, or small at its top
#: corner, as a letter's docket.
TITLE_HEADING, TITLE_BANNER, TITLE_DOCKET = "heading", "banner", "docket"

#: A Stationery's edge: a scribe's ruled frame, a gilt frame, or none.
EDGE_RULED, EDGE_GILT, EDGE_NONE = "ruled", "gilt", "none"


@dataclass(frozen=True)
class Stationery:
    """How one Stationery's page is made: `label` what it is called,
    `aspect` its height for its width (the least it is: a long text runs
    the page on), `margin` each side's margin as a share of its width,
    `title` where the title goes, `edge` its edge, `seal` whether a seal
    hangs from its foot and `folds` the creases across it."""

    name: str
    label: str
    aspect: float
    margin: float
    title: str
    edge: str
    seal: bool = False
    folds: int = 0


#: Each Stationery, by its name (models.STATIONERY).
STATIONERY: dict[str, Stationery] = {
    found.name: found
    for found in (
        Stationery(VELLUM, "Vellum", 1.4, 0.12, TITLE_HEADING, EDGE_RULED),
        Stationery(
            SEALED_LETTER,
            "A sealed letter",
            1.15,
            0.1,
            TITLE_DOCKET,
            EDGE_NONE,
            seal=True,
            folds=2,
        ),
        Stationery(
            PROCLAMATION,
            "A proclamation",
            1.45,
            0.14,
            TITLE_BANNER,
            EDGE_GILT,
            seal=True,
        ),
    )
}


def stationery(name: str) -> Stationery:
    """The Stationery called `name`; any other reads as vellum."""
    return STATIONERY.get(name, STATIONERY[VELLUM])


#: Where each kind of block stands; an initial's paragraph and plain text
#: run from the left.
_ALIGN: dict[str, str] = {
    hm.HEADING: CENTRE,
    hm.CENTRED: CENTRE,
    hm.RIGHT: RIGHT,
    hm.FLOURISH: CENTRE,
    hm.PICTURE: CENTRE,
}


@dataclass(frozen=True)
class Placed:
    """One block set on the page: its kind (handout_markup's), its words
    as safe markup, where it stands, for an initial's paragraph the
    letter drawn large (taken off the front of `text`; "" when it opens
    on no letter), and for a placed picture its number and the name it is
    shown by."""

    kind: str
    text: str = ""
    align: str = LEFT
    initial: str = ""
    picture: int = 0
    caption: str = ""


@dataclass(frozen=True)
class Laid:
    """A Handout laid on its Stationery: its title (plain text), the
    Stationery and its blocks in order."""

    title: str
    stationery: Stationery
    blocks: tuple[Placed, ...]


def split_initial(text: str) -> tuple[str, str]:
    """The letter an initial's paragraph (markup) opens on, and the
    paragraph without it: the first letter or digit of its words, past
    any opening tags. ("", `text`) when its words open on anything else
    (a quotation mark), so nothing is lost. The letter keeps the accents
    written after it, and stays as written where its capital is more than
    one letter (ß, ﬁ)."""
    at = 0
    while True:
        tag = TAG.match(text, at)
        if tag is None:
            break
        at = tag.end()
    base = text[at : at + 1]
    if not base.isalnum():
        return "", text
    end = at + 1
    while end < len(text) and unicodedata.combining(text[end]):
        end += 1
    capital = base.upper()
    letter = (capital if len(capital) == 1 else base) + text[at + 1 : end]
    return letter, text[:at] + text[end:]


def lay_out(
    title: str, stationery_name: str, text: str, pictures: Sequence[str] = ()
) -> Laid:
    """The Handout titled `title` laid on the Stationery `stationery_name`:
    `text` read into blocks (handout_markup.blocks), `pictures` the names
    its pictures are shown by, in order (a `[picture n]` beyond them is
    text)."""
    placed: list[Placed] = []
    for block in hm.blocks(text, len(pictures)):
        align = _ALIGN.get(block.kind, LEFT)
        if block.kind == hm.INITIAL:
            letter, rest = split_initial(block.text)
            placed.append(Placed(block.kind, rest, align, initial=letter))
        elif block.kind == hm.PICTURE:
            caption = pictures[block.picture - 1]
            placed.append(
                Placed(block.kind, align=align, picture=block.picture, caption=caption)
            )
        else:
            placed.append(Placed(block.kind, block.text, align))
    return Laid(
        title.strip() or "(untitled)", stationery(stationery_name), tuple(placed)
    )


@dataclass(frozen=True)
class Preview:
    """What a storyguide's Preview draws: the laid-out Handout and, by
    picture number less one, where each picture's file is on this
    computer (None when it isn't there: drawn as a placeholder naming
    it). A player's copy never carries this; its pictures come through
    the picture request."""

    laid: Laid
    files: tuple[Path | None, ...] = ()

    def file(self, number: int) -> Path | None:
        """The file of picture `number` (1 for the first), or None."""
        return self.files[number - 1] if 0 < number <= len(self.files) else None


#: What a shown copy's placed picture is captioned: the copy names no
#: file and no record, so nothing the players don't know reaches them.
COPY_CAPTION = "shown with it"


@dataclass(frozen=True)
class Reading:
    """What a player's copy of a shown written Handout draws: the copy laid
    out, and its pictures' bytes as the host sent them, by picture number
    less one (None for one not to hand: drawn as a placeholder). Unlike a
    Preview it names no file on this computer."""

    laid: Laid
    pictures: tuple[bytes | None, ...] = ()
    #: The help page its reading window opens on F1 ("": the Handouts').
    help_id: str = ""


def reading(
    title: str, stationery_name: str, text: str, pictures: Sequence[bytes | None]
) -> Reading:
    """A shown copy (its title, Stationery, text and pictures) laid out
    through the one parser, each placed picture captioned COPY_CAPTION."""
    captions = [COPY_CAPTION] * len(pictures)
    return Reading(lay_out(title, stationery_name, text, captions), tuple(pictures))
